#!/bin/bash
# session-start.sh — Load project context at session start

echo "=== Session Context ==="

# Git context
if command -v git &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    echo "Branch: $BRANCH"
    echo ""
    echo "Recent commits:"
    git log --oneline -5 2>/dev/null || true
    echo ""

    CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [ "$CHANGES" -gt 0 ]; then
        echo "Uncommitted changes: $CHANGES files"
        git status --short 2>/dev/null
        echo ""
    fi
fi

# Session state recovery (execution-harness checkpoints)
for f in CHECKPOINT.md docs/harness/*.md; do
    if [ -f "$f" ]; then
        echo "==============================="
        echo "ACTIVE CHECKPOINT DETECTED: $f"
        echo "==============================="
        head -20 "$f"
        echo ""
        echo "Read full file to resume."
        break
    fi
done

# In-progress work detection
if [ -f "docs/TODO.md" ]; then
    IN_PROGRESS=$(grep -c "In Progress\|in.progress\|\bWIP\b" "docs/TODO.md" 2>/dev/null || echo 0)
    if [ "$IN_PROGRESS" -gt 0 ]; then
        echo "TODO: $IN_PROGRESS in-progress items — read docs/TODO.md"
    fi
fi

# Code health
SRC_DIRS="src apps lib"
for dir in $SRC_DIRS; do
    if [ -d "$dir" ]; then
        TODO_COUNT=$(grep -rn "TODO\|FIXME\|HACK\|XXX" "$dir" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$TODO_COUNT" -gt 0 ]; then
            echo "Code health: $TODO_COUNT TODO/FIXME markers in $dir/"
        fi
        break
    fi
done
