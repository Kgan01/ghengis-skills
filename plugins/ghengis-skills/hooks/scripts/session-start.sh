#!/usr/bin/env bash
# session-start.sh — Load project context + inject using-ghengis-skills at session start

set -euo pipefail

# Determine plugin root directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Read using-ghengis-skills content
using_ghengis_content=$(cat "${PLUGIN_ROOT}/skills/using-ghengis-skills/SKILL.md" 2>/dev/null || echo "Error reading using-ghengis-skills skill")

# Build project context diagnostics
project_context=""
if command -v git &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    RECENT=$(git log --oneline -3 2>/dev/null || true)
    CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    project_context="Branch: ${BRANCH}. Recent: ${RECENT}. Uncommitted: ${CHANGES} files."
fi

# Check for pending sync
pending_sync=""
if [ -f ".claude/pending_sync.md" ]; then
    pending_sync=$(cat .claude/pending_sync.md 2>/dev/null || true)
fi

# Escape string for JSON embedding
escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

using_ghengis_escaped=$(escape_for_json "$using_ghengis_content")
project_escaped=$(escape_for_json "$project_context")
pending_escaped=$(escape_for_json "$pending_sync")

session_context="<EXTREMELY_IMPORTANT>\nYou have ghengis-skills installed.\n\n**Below is the full content of your 'ghengis-skills:using-ghengis-skills' skill. For all ghengis skills, use the 'Skill' tool with the ghengis-skills: prefix:**\n\n${using_ghengis_escaped}\n\n"

# Add project context
if [ -n "$project_context" ]; then
    session_context="${session_context}Project context: ${project_escaped}\n"
fi

# Add pending sync notice
if [ -n "$pending_sync" ]; then
    session_context="${session_context}\n${pending_escaped}\nRun /sync to update project docs.\n"
fi

session_context="${session_context}</EXTREMELY_IMPORTANT>"

# Output context injection as JSON — matching the platform-specific format.
if [ -n "${CURSOR_PLUGIN_ROOT:-}" ]; then
    printf '{\n  "additional_context": "%s"\n}\n' "$session_context"
elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -z "${COPILOT_CLI:-}" ]; then
    printf '{\n  "hookSpecificOutput": {\n    "hookEventName": "SessionStart",\n    "additionalContext": "%s"\n  }\n}\n' "$session_context"
else
    printf '{\n  "additionalContext": "%s"\n}\n' "$session_context"
fi

exit 0
