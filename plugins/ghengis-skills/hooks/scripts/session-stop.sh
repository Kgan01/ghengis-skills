#!/usr/bin/env bash
# session-stop.sh — Archive session state + check for pending sync on exit

set -euo pipefail

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

# Auto-sync check: if 5+ commits since last sync, write pending_sync marker
if command -v git &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
    LAST_SYNC=$(cat .claude/last_sync 2>/dev/null || echo "1970-01-01")
    NEW_COMMITS=$(git log --since="$LAST_SYNC" --oneline 2>/dev/null | wc -l | tr -d ' ')
    if [ "$NEW_COMMITS" -ge 5 ]; then
        mkdir -p .claude
        echo "Auto-sync recommended: $NEW_COMMITS commits since last sync ($LAST_SYNC). Run /sync to update project docs." > .claude/pending_sync.md
    fi
fi

echo "Session archived to $LOG_FILE"
