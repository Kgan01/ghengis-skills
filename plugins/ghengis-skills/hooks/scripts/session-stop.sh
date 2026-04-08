#!/bin/bash
# session-stop.sh — Archive session state on exit

LOG_DIR=".claude/session-logs"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/session-$TIMESTAMP.md"

{
    echo "# Session Log — $TIMESTAMP"
    echo ""

    if command -v git &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
        echo "## Commits This Session"
        git log --oneline --since="8 hours ago" 2>/dev/null || echo "None"
        echo ""

        CHANGES=$(git status --porcelain 2>/dev/null)
        if [ -n "$CHANGES" ]; then
            echo "## Uncommitted Changes"
            echo '```'
            echo "$CHANGES"
            echo '```'
        fi
    fi
} > "$LOG_FILE"

echo "Session archived to $LOG_FILE"
