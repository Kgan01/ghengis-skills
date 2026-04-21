#!/usr/bin/env python3
"""
One-shot installer for the agent-monitor statusline.

Run once per machine. Copies statusline-bar.py to ~/.claude/ and merges
the statusLine entry into ~/.claude/settings.json (preserving all other
keys). Idempotent — safe to re-run.
"""
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

CLAUDE_HOME = Path.home() / ".claude"
TARGET_SCRIPT = CLAUDE_HOME / "statusline-bar.py"
SETTINGS = CLAUDE_HOME / "settings.json"
# Script is bundled alongside this installer
SOURCE_SCRIPT = Path(__file__).parent / "statusline-bar.py"


def _is_windowsapps_stub(path: str) -> bool:
    # Microsoft Store "App Execution Alias" stubs live at
    # %LOCALAPPDATA%\Microsoft\WindowsApps and pretend to be python/python3
    # on PATH. Running one exits 49 with a Store-install prompt.
    return "microsoft\\windowsapps" in path.lower().replace("/", "\\")


def _probe(argv):
    # Actually execute `<argv> --version` and confirm it's a working Python.
    # Catches Store-alias stubs, Xcode CLT prompt stubs, and any other
    # non-Python binary that happens to sit on PATH under the same name.
    try:
        r = subprocess.run(
            list(argv) + ["--version"],
            capture_output=True, text=True, timeout=5,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False
    return r.returncode == 0 and "Python" in (r.stdout + r.stderr)


def resolve_python():
    """Return argv list for a working Python 3 interpreter.

    Works across Windows, macOS, and Linux:
      - Windows: prefer `py -3` (Python Launcher, bundled with every
        python.org installer, immune to Store-alias collision). Fall back
        to `python`/`python3` with WindowsApps stubs filtered out.
      - macOS/Linux: `python3` is canonical; `python` is a rare fallback.

    Every candidate is probed with `--version` before we accept it.
    """
    is_windows = platform.system() == "Windows"

    if is_windows:
        candidates = [["py", "-3"], ["python"], ["python3"]]
    else:
        candidates = [["python3"], ["python"]]

    for parts in candidates:
        exe = shutil.which(parts[0])
        if not exe:
            continue
        if is_windows and _is_windowsapps_stub(exe):
            continue
        resolved = [exe] + parts[1:]
        if _probe(resolved):
            return resolved

    return ["python3"]


def _shell_quote(part, force=False):
    # Quote argv pieces containing whitespace so the whole command
    # round-trips through a single-string statusLine.command field.
    # `force=True` wraps every part in quotes (used on Windows so drive-letter
    # paths survive bash parsing regardless of special chars).
    if force or any(c.isspace() for c in part):
        return '"' + part + '"'
    return part


def main() -> int:
    if not SOURCE_SCRIPT.exists():
        print(f"ERROR: statusline-bar.py not found at {SOURCE_SCRIPT}", file=sys.stderr)
        print("Plugin may be corrupted. Reinstall ghengis-skills.", file=sys.stderr)
        return 1

    CLAUDE_HOME.mkdir(parents=True, exist_ok=True)

    # 1. Copy the script
    shutil.copy2(SOURCE_SCRIPT, TARGET_SCRIPT)
    print(f"[install-statusline] Copied statusline-bar.py to {TARGET_SCRIPT}")

    # 2. Merge statusLine into settings.json
    python_parts = resolve_python()
    cmd_parts = python_parts + [TARGET_SCRIPT.as_posix()]
    # Claude Code runs statusLine.command through a shell (bash on Windows via
    # Git Bash). Backslashes in Windows paths get eaten by bash -- e.g.
    # C:\WINDOWS\py.EXE becomes C:WINDOWSpy.EXE. Normalize every part to
    # forward slashes on Windows and always double-quote so paths with spaces
    # and drive letters survive shell parsing.
    is_windows = platform.system() == "Windows"
    if is_windows:
        cmd_parts = [p.replace("\\", "/") for p in cmd_parts]
    cmd = " ".join(_shell_quote(p, force=is_windows) for p in cmd_parts)
    status_entry = {"type": "command", "command": cmd}

    if SETTINGS.exists():
        try:
            settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"ERROR: {SETTINGS} is not valid JSON: {e}", file=sys.stderr)
            print("Fix the file manually first, then re-run.", file=sys.stderr)
            return 1
    else:
        settings = {}

    existing = settings.get("statusLine")
    if existing == status_entry:
        print(f"[install-statusline] settings.json already configured, nothing to change")
    else:
        if existing:
            print(f"[install-statusline] Replacing existing statusLine: {existing}")
        settings["statusLine"] = status_entry
        SETTINGS.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        print(f"[install-statusline] Updated {SETTINGS} with statusLine config")

    print()
    print("Done. Restart Claude Code (not /reload-plugins — a full exit and relaunch)")
    print("to see the status bar below your prompt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
