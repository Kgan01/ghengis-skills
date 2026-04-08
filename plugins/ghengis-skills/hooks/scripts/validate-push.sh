#!/bin/bash
# validate-push.sh — Pre-push safety checks

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

case "$COMMAND" in
    *"git push"*) ;;
    *) exit 0 ;;
esac

BRANCH=$(git branch --show-current 2>/dev/null || echo "")

case "$BRANCH" in
    main|master|production|release)
        echo "=== Push Warning ==="
        echo "Pushing to protected branch: $BRANCH"
        ;;
esac

case "$COMMAND" in
    *"--force"*|*" -f "*)
        echo "=== Force Push Warning ==="
        echo "Force pushing to $BRANCH — this overwrites remote history."
        ;;
esac
