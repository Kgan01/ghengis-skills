"""Drive agy auth under a real ConPTY so its console-read paste prompt works.

Writes the OAuth URL to url.txt as soon as it appears; polls code.txt and
types the code + Enter into the pty when the file shows up; mirrors all pty
output to pty.log. Exits when agy exits (or 5 min hard cap).
"""
import os
import re
import sys
import threading
import time
from pathlib import Path

from winpty import PtyProcess

d = Path(__file__).parent
url_file = d / "url.txt"
code_file = d / "code.txt"
log_file = d / "pty.log"
for f in (url_file, code_file, log_file):
    if f.exists():
        f.unlink()

agy = os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe")
proc = PtyProcess.spawn([agy, "--print", "say ok", "--print-timeout", "10m"], dimensions=(50, 500))

buf = ""
deadline = time.time() + 300
log = open(log_file, "a", encoding="utf-8")


def feeder():
    """proc.read() blocks, so the code feed runs on its own thread."""
    while proc.isalive():
        if code_file.exists():
            time.sleep(0.3)
            code = code_file.read_text(encoding="utf-8").strip()
            if code:
                proc.write(code + "\r\n")
                (d / "fed.marker").write_text(code[:12], encoding="utf-8")
                return
        time.sleep(0.2)


threading.Thread(target=feeder, daemon=True).start()

while proc.isalive() and time.time() < deadline:
    try:
        chunk = proc.read(4096)
    except (EOFError, ConnectionAbortedError):
        break
    if chunk:
        log.write(chunk)
        log.flush()
        buf += chunk
        if not url_file.exists():
            m = re.search(r"https://accounts\.google\.com/o/oauth2/auth\S+", buf)
            if m:
                url_file.write_text(m.group(0).rstrip('"\x1b[]0;'), encoding="utf-8")

log.write(f"\n[PTY-DRIVER] agy alive={proc.isalive()} — done\n")
log.close()
sys.exit(0)
