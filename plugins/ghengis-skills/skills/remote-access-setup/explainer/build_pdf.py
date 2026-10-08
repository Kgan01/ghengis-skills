"""Build remote-access-explained.pdf from remote-access-explained.md.

    python build_pdf.py

Needs the `markdown` package and Microsoft Edge or Google Chrome (headless print).
Edit the .md, never the .html or .pdf: both are generated.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
SRC = HERE / "remote-access-explained.md"
HTML = Path(tempfile.gettempdir()) / "remote-access-explained.html"  # build artifact, not committed
PDF = HERE / "remote-access-explained.pdf"

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome",
    "chromium",
    "msedge",
]

DIAGRAM = """
<figure class="diagram">
<svg viewBox="0 0 720 300" role="img" aria-label="Moonlight on the client connects to Sunshine on the host through an encrypted Tailscale connection">
  <defs>
    <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#0f766e"/>
    </marker>
    <marker id="ahg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#8a94a6"/>
    </marker>
  </defs>

  <!-- client -->
  <rect x="20" y="110" width="190" height="120" rx="14" fill="#f1f5f9" stroke="#334155" stroke-width="1.5"/>
  <text x="115" y="140" text-anchor="middle" class="t-h">CLIENT</text>
  <text x="115" y="162" text-anchor="middle" class="t-s">the device in front of you</text>
  <rect x="45" y="178" width="140" height="34" rx="8" fill="#ffffff" stroke="#0f766e" stroke-width="1.5"/>
  <text x="115" y="200" text-anchor="middle" class="t-app">Moonlight</text>

  <!-- host -->
  <rect x="510" y="110" width="190" height="120" rx="14" fill="#f1f5f9" stroke="#334155" stroke-width="1.5"/>
  <text x="605" y="140" text-anchor="middle" class="t-h">HOST</text>
  <text x="605" y="162" text-anchor="middle" class="t-s">the computer you control</text>
  <rect x="535" y="178" width="140" height="34" rx="8" fill="#ffffff" stroke="#0f766e" stroke-width="1.5"/>
  <text x="605" y="200" text-anchor="middle" class="t-app">Sunshine</text>

  <!-- tunnel -->
  <rect x="222" y="146" width="276" height="82" rx="30" fill="#ccfbf1" stroke="#0f766e" stroke-width="1.5" stroke-dasharray="0"/>
  <text x="360" y="138" text-anchor="middle" class="t-tun">Tailscale: encrypted connection (WireGuard)</text>
  <line x1="236" y1="174" x2="484" y2="174" stroke="#0f766e" stroke-width="2" marker-start="url(#ah)"/>
  <text x="360" y="166" text-anchor="middle" class="t-flow">video stream (host to client)</text>
  <line x1="236" y1="200" x2="484" y2="200" stroke="#0f766e" stroke-width="2" marker-end="url(#ah)"/>
  <text x="360" y="217" text-anchor="middle" class="t-flow">keyboard and mouse input (client to host)</text>

  <!-- coordination server -->
  <rect x="270" y="18" width="180" height="56" rx="10" fill="#ffffff" stroke="#8a94a6" stroke-width="1.2" stroke-dasharray="5 4"/>
  <text x="360" y="42" text-anchor="middle" class="t-h2">Coordination server</text>
  <text x="360" y="60" text-anchor="middle" class="t-s">public keys only, no traffic</text>
  <line x1="300" y1="76" x2="150" y2="108" stroke="#8a94a6" stroke-width="1.2" stroke-dasharray="4 4" marker-end="url(#ahg)"/>
  <line x1="420" y1="76" x2="570" y2="108" stroke="#8a94a6" stroke-width="1.2" stroke-dasharray="4 4" marker-end="url(#ahg)"/>

  <!-- relay -->
  <text x="360" y="262" text-anchor="middle" class="t-s">When a direct path is not possible, a relay server forwards the encrypted data.</text>
  <text x="360" y="280" text-anchor="middle" class="t-s">The relay cannot decrypt it. No router ports are open on either side.</text>
</svg>
<figcaption>How the three parts connect.</figcaption>
</figure>
"""

CSS = """
@page { size: Letter; margin: 0.75in 0.8in 0.8in; }
:root { --ink:#1e2430; --muted:#5b6474; --rule:#dbe1ea; --accent:#0f766e; --wash:#f1f5f9; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; color: var(--ink);
       font-size: 10.2pt; line-height: 1.5; margin: 0; }
.cover { border-bottom: 3px solid var(--accent); padding-bottom: 18px; margin-bottom: 26px; }
.cover .kicker { font-size: 9pt; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); font-weight: 600; }
.cover h1 { font-size: 26pt; line-height: 1.15; margin: 6px 0 8px; letter-spacing: -.01em; }
.cover .sub { font-size: 12pt; color: var(--muted); margin: 0; }
h1 { display: none; }
h2 { font-size: 14.5pt; margin: 22px 0 8px; padding-top: 4px; color: var(--ink);
     border-top: 1px solid var(--rule); padding-top: 14px; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 18px 0 6px; color: var(--accent); break-after: avoid; }
p { margin: 0 0 9px; }
ul, ol { margin: 0 0 10px; padding-left: 22px; }
li { margin: 0 0 4px; }
strong { color: #0b1220; }
code { font-family: Consolas, "SF Mono", Menlo, monospace; font-size: 9.5pt; background: var(--wash);
       padding: 1px 5px; border-radius: 4px; }
table { width: 100%; border-collapse: collapse; margin: 6px 0 14px; font-size: 10pt; break-inside: avoid; }
th { text-align: left; background: var(--ink); color: #fff; font-weight: 600; padding: 7px 10px; }
td { padding: 7px 10px; border-bottom: 1px solid var(--rule); vertical-align: top; }
tr:nth-child(even) td { background: #f8fafc; }
.diagram { margin: 8px 0 14px; padding: 8px 10px 4px; border: 1px solid var(--rule); border-radius: 12px; break-inside: avoid; }
.diagram svg { width: 86%; height: auto; display: block; margin: 0 auto; }
.diagram figcaption { text-align: center; font-size: 9pt; color: var(--muted); margin-top: 4px; }
.t-h { font: 700 13px "Segoe UI", Arial, sans-serif; fill: #1e2430; letter-spacing: .08em; }
.t-h2 { font: 600 12px "Segoe UI", Arial, sans-serif; fill: #475569; }
.t-s { font: 400 11px "Segoe UI", Arial, sans-serif; fill: #5b6474; }
.t-app { font: 600 13px "Segoe UI", Arial, sans-serif; fill: #0f766e; }
.t-tun { font: 600 11.5px "Segoe UI", Arial, sans-serif; fill: #0f766e; }
.t-flow { font: 400 10.5px "Segoe UI", Arial, sans-serif; fill: #134e4a; }
hr { border: 0; border-top: 1px solid var(--rule); margin: 28px 0 10px; }
hr + p { font-size: 8.5pt; color: var(--muted); break-inside: avoid; }
section.keep { break-inside: avoid; }
"""


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
        text = text[m.end():]

    body = markdown.markdown(text, extensions=["tables", "sane_lists"])
    # Diagram goes after the "three parts" table.
    body = body.replace("<h2>3. Tailscale</h2>", DIAGRAM + "<h2>3. Tailscale</h2>", 1)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{meta.get("title", "Remote access")}</title>
<style>{CSS}</style></head>
<body>
<div class="cover">
  <div class="kicker">Client guide</div>
  <h1 style="display:block">{meta.get("title", "")}</h1>
  <p class="sub">{meta.get("subtitle", "")}</p>
</div>
{body}
</body></html>"""
    HTML.write_text(html, encoding="utf-8")

    browser = next((b for b in BROWSERS if Path(b).exists() or shutil.which(b)), None)
    if not browser:
        print("No Edge/Chrome found. Open the .html and print it to PDF.", file=sys.stderr)
        return 1
    subprocess.run(
        [browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={PDF}", HTML.as_uri()],
        check=True, capture_output=True, timeout=120,
    )
    print(f"wrote {PDF}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
