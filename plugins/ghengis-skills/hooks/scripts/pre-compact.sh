#!/bin/bash
# pre-compact.sh — Dump critical state before context compaction

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

echo "=== Pre-Compaction State Dump ==="
echo "Timestamp: $TIMESTAMP"
echo ""

# In-progress items
if [ -f "docs/TODO.md" ]; then
    echo "--- In-Progress Items ---"
    grep -n "In Progress\|in.progress\|\bWIP\b\|\[ \]" "docs/TODO.md" 2>/dev/null | head -10 || echo "None"
    echo ""
fi

# Recently modified source files (last 2 hours)
echo "--- Recently Modified Files (last 2h) ---"
SRC_DIRS="src apps lib"
for dir in $SRC_DIRS; do
    if [ -d "$dir" ]; then
        find "$dir" -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.go" -o -name "*.rs" \) -mmin -120 2>/dev/null | head -20
        break
    fi
done
echo ""

# Git state
if command -v git &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
    STAGED=$(git diff --cached --stat 2>/dev/null)
    UNSTAGED=$(git diff --stat 2>/dev/null)
    UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | head -10)

    if [ -n "$STAGED" ]; then
        echo "--- Staged Changes ---"
        echo "$STAGED"
        echo ""
    fi
    if [ -n "$UNSTAGED" ]; then
        echo "--- Unstaged Changes ---"
        echo "$UNSTAGED"
        echo ""
    fi
    if [ -n "$UNTRACKED" ]; then
        echo "--- New Untracked Files ---"
        echo "$UNTRACKED"
        echo ""
    fi
fi

# Checkpoint recovery hint
echo "After compaction, read CLAUDE.md and any CHECKPOINT.md to recover context."
