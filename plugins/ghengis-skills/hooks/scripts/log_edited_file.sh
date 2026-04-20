#!/bin/bash
# PostToolUse(Write|Edit) hook — NON-BLOCKING.
# Just appends the file path to a session log for later batch scanning.
# No Haiku call, no interruption, no WARN — just silent logging.

EDIT_LOG="$HOME/.claude/edited-files-session.log"

# Read hook input
HOOK_INPUT=""
if read -t 1 LINE; then
  HOOK_INPUT="$LINE"
  while read -t 0.1 LINE; do
    HOOK_INPUT="${HOOK_INPUT}${LINE}"
  done
fi

# Extract file_path from tool_input JSON (simple regex)
FILE_PATH=$(echo "$HOOK_INPUT" | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)"/\1/')

if [ -n "$FILE_PATH" ]; then
  mkdir -p "$(dirname "$EDIT_LOG")"
  NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "${NOW_ISO}|${FILE_PATH}" >> "$EDIT_LOG"
fi

exit 0
