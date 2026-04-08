#!/bin/bash
# validate-commit.sh — Pre-commit security and quality checks

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)

case "$COMMAND" in
    *"git commit"*) ;;
    *) exit 0 ;;
esac

ERRORS=""
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null)

if [ -n "$STAGED_FILES" ]; then
    # Secret detection
    SECRET_PATTERNS="(api[_-]?key|secret[_-]?key|password|token|credential)\\s*[=:]\\s*['\"][^'\"]{8,}"
    SECRETS_FOUND=$(echo "$STAGED_FILES" | xargs grep -lEi "$SECRET_PATTERNS" 2>/dev/null | grep -v ".env.example" | grep -v "test" || true)
    if [ -n "$SECRETS_FOUND" ]; then
        ERRORS="${ERRORS}WARNING: Possible secrets in: $SECRETS_FOUND\n"
    fi

    # .env file check
    ENV_FILES=$(echo "$STAGED_FILES" | grep "^\.env$\|^\.env\.local$\|^\.env\.production$" || true)
    if [ -n "$ENV_FILES" ]; then
        ERRORS="${ERRORS}BLOCKED: Committing .env files: $ENV_FILES — add to .gitignore\n"
    fi

    # CLAUDE.md size check
    if echo "$STAGED_FILES" | grep -q "CLAUDE.md"; then
        CLAUDE_LINES=$(wc -l < CLAUDE.md 2>/dev/null || echo 0)
        if [ "$CLAUDE_LINES" -gt 150 ]; then
            ERRORS="${ERRORS}WARNING: CLAUDE.md is $CLAUDE_LINES lines — keep under 150, move content to .claude/docs/\n"
        fi
    fi
fi

if [ -n "$ERRORS" ]; then
    echo "=== Commit Validation ==="
    echo -e "$ERRORS"
fi
