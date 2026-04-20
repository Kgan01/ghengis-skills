#!/bin/bash
# PreToolUse(Agent) hook for skill-chain-supervisor.
# WARN-ONLY: writes chain state to scratchpad, prints status to stderr.
# Never blocks, never modifies the prompt.

SCRATCHPAD="$HOME/.claude/ghengis-chain-context.json"
LOG="$HOME/.claude/ghengis-chain-log.jsonl"

NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Read hook input (contains prompt, tool_input, etc.)
HOOK_INPUT=""
if read -t 1 LINE; then
  HOOK_INPUT="$LINE"
  while read -t 0.1 LINE; do
    HOOK_INPUT="${HOOK_INPUT}${LINE}"
  done
fi

# Write chain initiation to scratchpad (minimal — supervisor populates the rest)
mkdir -p "$(dirname "$SCRATCHPAD")"
cat > "$SCRATCHPAD" << EOF
{
  "chain": "agent-dispatch",
  "started_at": "${NOW_ISO}",
  "current_stage": "pre-validation",
  "stages_completed": [],
  "stages_remaining": ["pql-validation", "meta-prompting", "execution", "completion-enforcer", "hallucination-detector", "audit-ledger"],
  "input": {
    "triggered_by": "PreToolUse(Agent) hook"
  },
  "hook_triggered": true
}
EOF

echo "{\"event\":\"chain_start\",\"chain\":\"agent-dispatch\",\"timestamp\":\"${NOW_ISO}\"}" >> "$LOG"

# Stderr: visible to Claude, acts as a nudge to invoke the supervisor
echo "[skill-chain-supervisor] agent-dispatch chain initiated. State tracked at ${SCRATCHPAD}" >&2

exit 0
