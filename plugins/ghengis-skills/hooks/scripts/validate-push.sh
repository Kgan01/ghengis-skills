#!/bin/bash
# validate-push.sh — Pre-push safety checks

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | "${SCRIPT_DIR}/run-python.sh" -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

case "$COMMAND" in
    *"git push"*) ;;
    *) exit 0 ;;
esac

# Block private data (client names, home paths, Tailscale IPs) headed to a PUBLIC repo
echo "$INPUT" | "${SCRIPT_DIR}/run-python.sh" "${SCRIPT_DIR}/public_leak_guard.py" push
[ $? -eq 2 ] && exit 2

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
