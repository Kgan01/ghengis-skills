#!/bin/bash
# Task Timer for Claude Code
# Runs on Stop hook to track how long Claude took to respond.
# Reads hook input from stdin for project context.

TIMESTAMP_FILE="$HOME/.claude/time-data.json"
TASK_LOG="$HOME/.claude/task-durations.jsonl"
PROJECT_LOG_DIR="$HOME/.claude/project-time"

NOW_EPOCH=$(date +%s)
NOW_LOCAL=$(date +"%Y-%m-%d %H:%M:%S %Z")

# Read hook input from stdin (non-blocking)
HOOK_INPUT=""
if read -t 1 HOOK_INPUT_LINE; then
  HOOK_INPUT="$HOOK_INPUT_LINE"
  while read -t 0.1 HOOK_INPUT_LINE; do
    HOOK_INPUT="${HOOK_INPUT}${HOOK_INPUT_LINE}"
  done
fi

# Parse project path from cwd
PROJECT=""
PROJECT_SAFE=""
if [ -n "$HOOK_INPUT" ]; then
  PROJECT=$(echo "$HOOK_INPUT" | grep -o '"cwd": *"[^"]*"' | sed 's/.*": *"//;s/"//')
  if [ -n "$PROJECT" ]; then
    PROJECT_SAFE=$(echo "$PROJECT" | sed 's|[:/\\]|_|g; s|^_*||')
  fi
fi

# Fall back to project from timestamp file if stdin had nothing
if [ -z "$PROJECT" ] && [ -f "$TIMESTAMP_FILE" ]; then
  PROJECT=$(grep -o '"last_project": *"[^"]*"' "$TIMESTAMP_FILE" | sed 's/.*": *"//;s/"//')
  if [ -n "$PROJECT" ]; then
    PROJECT_SAFE=$(echo "$PROJECT" | sed 's|[:/\\]|_|g; s|^_*||')
  fi
fi

PROJECT_NAME=""
if [ -n "$PROJECT" ]; then
  PROJECT_NAME=$(basename "$PROJECT")
fi

# Format duration helper
format_duration() {
  local SECS=$1
  if [ $SECS -lt 60 ]; then
    echo "${SECS}s"
  elif [ $SECS -lt 3600 ]; then
    echo "$((SECS / 60))m $((SECS % 60))s"
  else
    echo "$((SECS / 3600))h $(( (SECS % 3600) / 60 ))m"
  fi
}

if [ -f "$TIMESTAMP_FILE" ]; then
  PREV_EPOCH=$(grep -o '"last_message_epoch": *[0-9]*' "$TIMESTAMP_FILE" | grep -o '[0-9]*')

  if [ -n "$PREV_EPOCH" ] && [ "$PREV_EPOCH" -gt 0 ] 2>/dev/null; then
    DURATION=$((NOW_EPOCH - PREV_EPOCH))
    DURATION_STR=$(format_duration $DURATION)

    # Global task log
    echo "{\"completed\":\"${NOW_LOCAL}\",\"duration_seconds\":${DURATION},\"duration_human\":\"${DURATION_STR}\",\"project\":\"${PROJECT_NAME}\"}" >> "$TASK_LOG"

    # Per-project task duration log
    if [ -n "$PROJECT_SAFE" ]; then
      mkdir -p "$PROJECT_LOG_DIR"
      PROJ_DURATION_FILE="$PROJECT_LOG_DIR/${PROJECT_SAFE}.durations.jsonl"
      echo "{\"completed\":\"${NOW_LOCAL}\",\"duration_seconds\":${DURATION},\"duration_human\":\"${DURATION_STR}\"}" >> "$PROJ_DURATION_FILE"
    fi
  fi
fi

exit 0
