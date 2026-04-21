#!/usr/bin/env python3
"""End-of-task batch secret scanner. Runs from Stop hook.

State location: <cwd>/.claude/ghengis-chain/
Reads edited-files.log, writes pending-scan-report.md + scan-history.jsonl.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# Comment-stripping regexes (applied before secret detection).
# Heuristic — not a full parser. Handles common comment styles.
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_TRIPLE_DOUBLE = re.compile(r'"""[\s\S]*?"""')
_TRIPLE_SINGLE = re.compile(r"'''[\s\S]*?'''")
_LINE_SLASHSLASH = re.compile(r"//[^\n]*", re.MULTILINE)
_LINE_HASH = re.compile(r"(?m)(?<!:)(?<!#)#(?!!)[^\n]*")


def _strip_comments(text: str) -> str:
    text = _BLOCK_COMMENT.sub(" ", text)
    text = _HTML_COMMENT.sub(" ", text)
    text = _TRIPLE_DOUBLE.sub(" ", text)
    text = _TRIPLE_SINGLE.sub(" ", text)
    text = _LINE_SLASHSLASH.sub("", text)
    text = _LINE_HASH.sub("", text)
    return text


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}

    cwd = Path(data.get("cwd") or os.getcwd())
    chain_dir = cwd / ".claude" / "ghengis-chain"
    edit_log = chain_dir / "edited-files.log"
    summary_log = chain_dir / "scan-history.jsonl"
    pending_report = chain_dir / "pending-scan-report.md"

    if not edit_log.exists() or edit_log.stat().st_size == 0:
        return 0

    files = sorted({
        line.split("|", 1)[1].strip()
        for line in edit_log.read_text(encoding="utf-8", errors="replace").splitlines()
        if "|" in line
    })

    skip_dir = re.compile(
        r"[/\\](test|tests|__tests__|__mocks__|demo|demos|example|examples|fixture|fixtures|sample|samples)[/\\]",
        re.IGNORECASE,
    )
    skip_file = re.compile(r"\.(test|spec|demo|example)\.(js|ts|jsx|tsx|py|rb|go)$", re.IGNORECASE)

    detectors = [
        (re.compile(r"AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}"), "AWS access key"),
        (re.compile(r"ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}"), "GitHub token"),
        (re.compile(r"sk_live_[A-Za-z0-9]{24,}|rk_live_[A-Za-z0-9]{24,}"), "Stripe live key"),
        (re.compile(r"-----BEGIN[A-Z ]*PRIVATE KEY-----"), "Private key PEM"),
        (re.compile(r"(postgres|mysql|mongodb(\+srv)?)://[^:]+:[^@]+@"), "Connection string with password"),
    ]

    scanned = 0
    findings = {}

    for file_path in files:
        p = Path(file_path)
        if not p.is_file():
            continue
        if skip_dir.search(file_path) or skip_file.search(file_path):
            continue
        scanned += 1
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        content = _strip_comments(content)
        hits = [label for regex, label in detectors if regex.search(content)]
        if hits:
            findings[file_path] = hits

    # Clear session log after scanning
    edit_log.write_text("", encoding="utf-8")

    # Clear stale pending report if the current scan is clean
    if pending_report.exists() and not findings:
        try:
            pending_report.unlink()
        except OSError:
            pass

    if not findings:
        return 0

    summary_log.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_log, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "scanned": scanned,
            "findings": len(findings),
        }) + "\n")

    lines = [
        f"## [secret-scan] End-of-task review",
        f"",
        f"Scanned **{scanned}** file(s), found potential secrets in **{len(findings)}**:",
        f"",
    ]
    for path, hits in findings.items():
        lines.append(f"- `{path}`")
        for hit in hits:
            lines.append(f"  - {hit}")
    lines.append("")
    lines.append("_These may be fine (test fixtures, dev defaults) or may need to move to env vars before production._")
    lines.append("")
    pending_report.write_text("\n".join(lines), encoding="utf-8")

    # Also stderr for logs (not visible to user transcript)
    out = sys.stderr
    print(f"\n[secret-scan] End-of-task review — scanned {scanned} files, "
          f"found potential secrets in {len(findings)}:\n", file=out)
    for path, hits in findings.items():
        print(f"  {path}", file=out)
        for hit in hits:
            print(f"    - {hit}", file=out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
