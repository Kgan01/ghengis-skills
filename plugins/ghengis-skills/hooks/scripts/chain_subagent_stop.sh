#!/bin/bash
# SubagentStop hook for skill-chain-supervisor.
# WARN-ONLY: updates chain state in scratchpad, nudges Claude to run post-stages.

LOG="$HOME/.claude/ghengis-chain-log.jsonl"
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Use Python for everything scratchpad-related — avoids cross-platform path issues
# where bash gives /c/Users/... and Python on Windows can't open that form.
python3 - "$NOW_ISO" << 'PYEOF'
import json
import os
import sys
from pathlib import Path

now_iso = sys.argv[1] if len(sys.argv) > 1 else ""
scratchpad = Path.home() / ".claude" / "ghengis-chain-context.json"

if not scratchpad.exists():
    sys.exit(0)

try:
    state = json.loads(scratchpad.read_text())
except (json.JSONDecodeError, OSError):
    sys.exit(0)

# Only advance if this is an agent-dispatch chain in-flight
if state.get("chain") != "agent-dispatch":
    sys.exit(0)

state["current_stage"] = "completion-enforcer"
state["stages_completed"] = ["pql-validation", "meta-prompting", "execution"]
state["stages_remaining"] = ["completion-enforcer", "hallucination-detector", "audit-ledger"]
state["subagent_stopped_at"] = now_iso

scratchpad.write_text(json.dumps(state, indent=2))
PYEOF

# Append to chain log (bash handles its own paths fine)
echo "{\"event\":\"subagent_stop\",\"chain\":\"agent-dispatch\",\"timestamp\":\"${NOW_ISO}\"}" >> "$LOG"

# Nudge Claude
echo "[skill-chain-supervisor] Subagent finished. Post-stages pending: completion-enforcer, hallucination-detector, audit-ledger. Invoke ghengis-skills:skill-chain-supervisor to complete." >&2

exit 0
