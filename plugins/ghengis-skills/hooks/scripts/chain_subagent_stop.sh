#!/bin/bash
# SubagentStop hook for skill-chain-supervisor.
# WARN-ONLY: updates chain state in scratchpad, nudges Claude to run post-stages.

SCRATCHPAD="$HOME/.claude/ghengis-chain-context.json"
LOG="$HOME/.claude/ghengis-chain-log.jsonl"

NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Check if scratchpad has an in-flight chain
if [ ! -f "$SCRATCHPAD" ]; then
  exit 0
fi

# Check if chain is agent-dispatch and still in-progress
if ! grep -q '"chain": *"agent-dispatch"' "$SCRATCHPAD" 2>/dev/null; then
  exit 0
fi

# Update scratchpad — mark execution done, move to post-stages
# (Simple jq-free update: rewrite relevant fields)
python3 - << PYEOF
import json, os
path = os.path.expanduser("$SCRATCHPAD")
try:
    with open(path) as f:
        state = json.load(f)
except Exception:
    sys.exit(0)

state["current_stage"] = "completion-enforcer"
state["stages_completed"] = ["pql-validation", "meta-prompting", "execution"]
state["stages_remaining"] = ["completion-enforcer", "hallucination-detector", "audit-ledger"]
state["subagent_stopped_at"] = "${NOW_ISO}"

with open(path, "w") as f:
    json.dump(state, f, indent=2)
PYEOF

echo "{\"event\":\"subagent_stop\",\"chain\":\"agent-dispatch\",\"timestamp\":\"${NOW_ISO}\"}" >> "$LOG"

# Stderr: nudge Claude to finish the chain
echo "[skill-chain-supervisor] Subagent finished. Post-stages pending: completion-enforcer, hallucination-detector, audit-ledger. Invoke ghengis-skills:skill-chain-supervisor to complete." >&2

exit 0
