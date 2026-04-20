#!/usr/bin/env python3
"""End-of-task batch secret scanner. Runs from Stop hook."""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

EDIT_LOG = Path.home() / ".claude" / "edited-files-session.log"
SUMMARY_LOG = Path.home() / ".claude" / "secret-scan-history.jsonl"


# Comment-stripping regexes (applied before secret detection).
# Heuristic — not a full parser. Handles common comment styles.
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)  # /* ... */
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)  # <!-- ... -->
_TRIPLE_DOUBLE = re.compile(r'"""[\s\S]*?"""')  # Python docstrings
_TRIPLE_SINGLE = re.compile(r"'''[\s\S]*?'''")
_LINE_SLASHSLASH = re.compile(r"//[^\n]*", re.MULTILINE)  # // ... EOL
# For `#`, only strip when it's clearly a line comment (preceded only by whitespace
# or after code). Skip inside URLs (http://host#frag) which are usually on the same
# line as actual URL text, and skip `#!` shebangs.
_LINE_HASH = re.compile(r"(?m)(?<!:)(?<!#)#(?!!)[^\n]*")


def _strip_comments(text: str) -> str:
    """Remove common comment syntax before secret scanning.

    Reduces false positives from doc examples, regex patterns in comments,
    and other non-secret strings that happen to match credential regexes.
    """
    text = _BLOCK_COMMENT.sub(" ", text)
    text = _HTML_COMMENT.sub(" ", text)
    text = _TRIPLE_DOUBLE.sub(" ", text)
    text = _TRIPLE_SINGLE.sub(" ", text)
    text = _LINE_SLASHSLASH.sub("", text)
    text = _LINE_HASH.sub("", text)
    return text


def main():
    if not EDIT_LOG.exists() or EDIT_LOG.stat().st_size == 0:
        return 0

    # Dedup file paths from "timestamp|path" lines.
    # Explicit UTF-8 — paths may contain unicode (emoji, CJK, accents).
    # Default encoding on Windows is cp1252 which crashes on UTF-8 bytes.
    files = sorted({
        line.split("|", 1)[1].strip()
        for line in EDIT_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
        if "|" in line
    })

    # Skip test/demo/example paths — match both / and \ separators
    skip_dir = re.compile(
        r"[/\\](test|tests|__tests__|__mocks__|demo|demos|example|examples|fixture|fixtures|sample|samples)[/\\]",
        re.IGNORECASE,
    )
    skip_file = re.compile(r"\.(test|spec|demo|example)\.(js|ts|jsx|tsx|py|rb|go)$", re.IGNORECASE)

    detectors = [
        (re.compile(r"AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}"), "AWS access key"),
        (re.compile(r"ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}"), "GitHub token"),
        (re.compile(r"sk_live_[A-Za-z0-9]{24,}|rk_live_[A-Za-z0-9]{24,}"), "Stripe live key"),
        # Require PEM dashes — prevents matching regex definitions of the pattern itself
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
        # Strip comments before scanning to reduce false positives
        # (doc examples, regex patterns in comments, etc.)
        content = _strip_comments(content)
        hits = [label for regex, label in detectors if regex.search(content)]
        if hits:
            findings[file_path] = hits

    # Clear session log regardless of findings
    EDIT_LOG.write_text("", encoding="utf-8")

    if not findings:
        return 0

    SUMMARY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_LOG, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "scanned": scanned,
            "findings": len(findings),
        }) + "\n")

    # Also write a human-readable report to pending-scan-report.md.
    # A UserPromptSubmit hook picks this up on the NEXT turn and injects
    # it into Claude's context so the user can actually see it.
    # Command-type hook stderr is not surfaced to the Claude Code transcript;
    # the pending-report mechanism routes around that limitation.
    pending_report = Path.home() / ".claude" / "pending-scan-report.md"
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

    # Also print to stderr for logs/debugging (not visible in transcript)
    out = sys.stderr
    print(f"\n[secret-scan] End-of-task review — scanned {scanned} files, "
          f"found potential secrets in {len(findings)}:\n", file=out)
    for path, hits in findings.items():
        print(f"  {path}", file=out)
        for hit in hits:
            print(f"    - {hit}", file=out)
    print("\n[secret-scan] These may be fine (test fixtures, dev defaults) or may need to move to env vars before production.\n",
          file=out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
