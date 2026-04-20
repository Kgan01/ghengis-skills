#!/bin/bash
# Stop hook — batch scan all files edited this session for potential secrets.
# Produces a SINGLE summary at end of task, never blocks mid-flow.
# Skips test/demo/example files (where hardcoded values are fine).

EDIT_LOG="$HOME/.claude/edited-files-session.log"
SUMMARY_LOG="$HOME/.claude/secret-scan-history.jsonl"

# Nothing to scan?
if [ ! -f "$EDIT_LOG" ] || [ ! -s "$EDIT_LOG" ]; then
  exit 0
fi

# Dedup file paths
UNIQUE_FILES=$(awk -F'|' '{print $2}' "$EDIT_LOG" | sort -u)

FINDINGS=""
SCANNED_COUNT=0
FINDING_COUNT=0

while IFS= read -r FILE_PATH; do
  # Skip if file doesn't exist anymore
  [ ! -f "$FILE_PATH" ] && continue

  # Skip test/demo/example files — hardcoded values are fine there
  if echo "$FILE_PATH" | grep -qiE '/(test|tests|__tests__|__mocks__|demo|demos|example|examples|fixture|fixtures|sample|samples)/'; then
    continue
  fi
  if echo "$FILE_PATH" | grep -qiE '\.(test|spec|demo|example)\.(js|ts|jsx|tsx|py|rb|go)$'; then
    continue
  fi

  SCANNED_COUNT=$((SCANNED_COUNT + 1))

  # Simple pattern-based scan (no LLM call — fast, deterministic, no interruption)
  HITS=""

  # AWS keys
  if grep -qE 'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}' "$FILE_PATH" 2>/dev/null; then
    HITS="${HITS}  - AWS access key\n"
  fi
  # GitHub tokens
  if grep -qE 'ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}' "$FILE_PATH" 2>/dev/null; then
    HITS="${HITS}  - GitHub token\n"
  fi
  # Stripe live keys
  if grep -qE 'sk_live_[A-Za-z0-9]{24,}|rk_live_[A-Za-z0-9]{24,}' "$FILE_PATH" 2>/dev/null; then
    HITS="${HITS}  - Stripe live key\n"
  fi
  # Private keys
  if grep -q "BEGIN.*PRIVATE KEY" "$FILE_PATH" 2>/dev/null; then
    HITS="${HITS}  - Private key PEM\n"
  fi
  # Connection strings with password
  if grep -qE '(postgres|mysql|mongodb(\+srv)?)://[^:]+:[^@]+@' "$FILE_PATH" 2>/dev/null; then
    HITS="${HITS}  - Connection string with password\n"
  fi

  if [ -n "$HITS" ]; then
    FINDING_COUNT=$((FINDING_COUNT + 1))
    FINDINGS="${FINDINGS}\n${FILE_PATH}:\n${HITS}"
  fi
done <<< "$UNIQUE_FILES"

# Clear the session log regardless
> "$EDIT_LOG"

# Report only if findings
if [ "$FINDING_COUNT" -gt 0 ]; then
  NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "{\"timestamp\":\"${NOW_ISO}\",\"scanned\":${SCANNED_COUNT},\"findings\":${FINDING_COUNT}}" >> "$SUMMARY_LOG"

  echo "" >&2
  echo "[secret-scan] End-of-task review — scanned ${SCANNED_COUNT} files, found potential secrets in ${FINDING_COUNT}:" >&2
  echo -e "$FINDINGS" >&2
  echo "" >&2
  echo "[secret-scan] These may be fine (test fixtures, dev defaults) or may need to move to env vars before production." >&2
fi

exit 0
