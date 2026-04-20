#!/bin/bash
# Stop hook — batch scan all files edited this session for potential secrets.
# Cross-platform: matches both / and \ as path separators.

EDIT_LOG="$HOME/.claude/edited-files-session.log"
SUMMARY_LOG="$HOME/.claude/secret-scan-history.jsonl"

if [ ! -f "$EDIT_LOG" ] || [ ! -s "$EDIT_LOG" ]; then
  exit 0
fi

UNIQUE_FILES=$(awk -F'|' '{print $2}' "$EDIT_LOG" | sort -u)

# Build findings via Python — avoids bash echo -e mangling Windows paths (\t)
python3 - "$EDIT_LOG" "$SUMMARY_LOG" << 'PYEOF'
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

edit_log = Path(sys.argv[1])
summary_log = Path(sys.argv[2])

# Dedup
files = sorted({line.split("|", 1)[1].strip()
                for line in edit_log.read_text().splitlines()
                if "|" in line})

# Skip patterns — match both / and \ as separators
SKIP_DIR_PATTERN = re.compile(
    r"[/\](test|tests|__tests__|__mocks__|demo|demos|example|examples|fixture|fixtures|sample|samples)[/\]",
    re.IGNORECASE,
)
SKIP_FILE_PATTERN = re.compile(r"\.(test|spec|demo|example)\.(js|ts|jsx|tsx|py|rb|go)$", re.IGNORECASE)

# Secret detection patterns
DETECTORS = [
    (re.compile(r"AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}"), "GitHub token"),
    (re.compile(r"sk_live_[A-Za-z0-9]{24,}|rk_live_[A-Za-z0-9]{24,}"), "Stripe live key"),
    (re.compile(r"BEGIN.*PRIVATE KEY"), "Private key PEM"),
    (re.compile(r"(postgres|mysql|mongodb(\+srv)?)://[^:]+:[^@]+@"), "Connection string with password"),
]

scanned = 0
findings = {}

for file_path in files:
    p = Path(file_path)
    if not p.is_file():
        continue
    if SKIP_DIR_PATTERN.search(file_path) or SKIP_FILE_PATTERN.search(file_path):
        continue
    scanned += 1
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    hits = [label for regex, label in DETECTORS if regex.search(content)]
    if hits:
        findings[file_path] = hits

# Clear session log
edit_log.write_text("")

# Report
if findings:
    summary_log.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_log, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "scanned": scanned,
            "findings": len(findings),
        }) + "\n")

    print(f"\n[secret-scan] End-of-task review — scanned {scanned} files, "
          f"found potential secrets in {len(findings)}:\n", file=sys.stderr)
    for path, hits in findings.items():
        print(f"  {path}", file=sys.stderr)
        for hit in hits:
            print(f"    - {hit}", file=sys.stderr)
    print("\n[secret-scan] These may be fine (test fixtures, dev defaults) or may need to move to env vars before production.\n",
          file=sys.stderr)
PYEOF

exit 0
