#!/bin/bash
# Time Tracker for Claude Code
# Runs on every UserPromptSubmit to give Claude a sense of time.
# Reads hook input from stdin (JSON with prompt, cwd, session_id).
# stdout is injected into Claude's context automatically.

TIMESTAMP_FILE="$HOME/.claude/time-data.json"
LOG_FILE="$HOME/.claude/time-log.jsonl"
PROJECT_LOG_DIR="$HOME/.claude/project-time"

NOW_EPOCH=$(date +%s)
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
NOW_LOCAL=$(date +"%Y-%m-%d %H:%M:%S %Z")

# Read hook input from stdin (non-blocking)
HOOK_INPUT=""
if read -t 1 HOOK_INPUT_LINE; then
  HOOK_INPUT="$HOOK_INPUT_LINE"
  while read -t 0.1 HOOK_INPUT_LINE; do
    HOOK_INPUT="${HOOK_INPUT}${HOOK_INPUT_LINE}"
  done
fi

# Parse project path from cwd field using bash
PROJECT=""
PROJECT_SAFE=""
if [ -n "$HOOK_INPUT" ]; then
  # Extract cwd value: "cwd":"/path/to/project"
  PROJECT=$(echo "$HOOK_INPUT" | grep -o '"cwd": *"[^"]*"' | sed 's/.*": *"//;s/"//')
  if [ -n "$PROJECT" ]; then
    # Create safe directory name from project path
    PROJECT_SAFE=$(echo "$PROJECT" | sed 's|[:/\\]|_|g; s|^_*||')
  fi

  # Extract first 100 chars of prompt for task categorization
  PROMPT_PREVIEW=$(echo "$HOOK_INPUT" | grep -o '"prompt": *"[^"]*"' | sed 's/.*": *"//;s/"$//' | head -c 100)
fi

# Read previous timestamp
if [ -f "$TIMESTAMP_FILE" ]; then
  PREV_EPOCH=$(grep -o '"last_message_epoch": *[0-9]*' "$TIMESTAMP_FILE" | grep -o '[0-9]*')
  PREV_LOCAL=$(grep -o '"last_message_local": *"[^"]*"' "$TIMESTAMP_FILE" | sed 's/.*": *"//;s/"//')
  SESSION_COUNT=$(grep -o '"message_count": *[0-9]*' "$TIMESTAMP_FILE" | grep -o '[0-9]*')
  PREV_PROJECT=$(grep -o '"last_project": *"[^"]*"' "$TIMESTAMP_FILE" | sed 's/.*": *"//;s/"//')

  if [ -n "$PREV_EPOCH" ] && [ "$PREV_EPOCH" -gt 0 ] 2>/dev/null; then
    ELAPSED=$((NOW_EPOCH - PREV_EPOCH))

    # Format elapsed time human-readably
    if [ $ELAPSED -lt 60 ]; then
      ELAPSED_STR="${ELAPSED}s"
    elif [ $ELAPSED -lt 3600 ]; then
      MINS=$((ELAPSED / 60))
      SECS=$((ELAPSED % 60))
      ELAPSED_STR="${MINS}m ${SECS}s"
    elif [ $ELAPSED -lt 86400 ]; then
      HOURS=$((ELAPSED / 3600))
      MINS=$(( (ELAPSED % 3600) / 60 ))
      ELAPSED_STR="${HOURS}h ${MINS}m"
    else
      DAYS=$((ELAPSED / 86400))
      HOURS=$(( (ELAPSED % 86400) / 3600 ))
      ELAPSED_STR="${DAYS}d ${HOURS}h"
    fi
  else
    ELAPSED=0
    ELAPSED_STR="N/A"
  fi
else
  ELAPSED=0
  ELAPSED_STR="N/A"
  SESSION_COUNT=0
  PREV_LOCAL="none"
  PREV_PROJECT=""
fi

# Increment message count
SESSION_COUNT=$((SESSION_COUNT + 1))

# Determine project display name (last folder in path)
PROJECT_NAME=""
if [ -n "$PROJECT" ]; then
  PROJECT_NAME=$(basename "$PROJECT")
fi

# Write current timestamp to state file
cat > "$TIMESTAMP_FILE" << EOF
{
  "last_message_epoch": ${NOW_EPOCH},
  "last_message_iso": "${NOW_ISO}",
  "last_message_local": "${NOW_LOCAL}",
  "last_project": "${PROJECT}",
  "message_count": ${SESSION_COUNT}
}
EOF

# Append to global log
echo "{\"timestamp\":\"${NOW_ISO}\",\"local\":\"${NOW_LOCAL}\",\"epoch\":${NOW_EPOCH},\"elapsed_seconds\":${ELAPSED},\"message_number\":${SESSION_COUNT},\"project\":\"${PROJECT}\"}" >> "$LOG_FILE"

# Append to per-project log
if [ -n "$PROJECT_SAFE" ]; then
  mkdir -p "$PROJECT_LOG_DIR"
  echo "{\"timestamp\":\"${NOW_ISO}\",\"local\":\"${NOW_LOCAL}\",\"epoch\":${NOW_EPOCH},\"elapsed_seconds\":${ELAPSED},\"prompt_preview\":\"${PROMPT_PREVIEW}\"}" >> "$PROJECT_LOG_DIR/${PROJECT_SAFE}.jsonl"
fi

# Build compact context output
# Format: [T:YYYY-MM-DD HH:MM|+elapsed|#count] or [T:...|proj<-prev] on switch
NOW_SHORT=$(date +"%Y-%m-%d %H:%M")
OUTPUT="[T:${NOW_SHORT}|+${ELAPSED_STR}|#${SESSION_COUNT}"
if [ -n "$PREV_PROJECT" ] && [ "$PREV_PROJECT" != "$PROJECT" ] && [ -n "$PROJECT_NAME" ]; then
  PREV_PROJECT_NAME=$(basename "$PREV_PROJECT")
  OUTPUT="${OUTPUT}|${PROJECT_NAME}<-${PREV_PROJECT_NAME}"
fi
OUTPUT="${OUTPUT}]"
echo "$OUTPUT"

exit 0
