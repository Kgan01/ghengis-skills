#!/usr/bin/env python3
"""
SubagentStop hook for skill-chain-supervisor.

Advances the scratchpad from pre-execution stages (pql-validation,
meta-prompting, execution) to post-execution stages.

current_stage after this runs: "completion-enforcer"
stages_remaining after this runs: ["hallucination-detector", "audit-ledger"]
(current_stage is NOT in stages_remaining — avoids the double-append bug.)
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
SCRATCHPAD = HOME / ".claude" / "ghengis-chain-context.json"
LOG = HOME / ".claude" / "ghengis-chain-log.jsonl"


def main() -> int:
    if not SCRATCHPAD.exists():
        return 0

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        state = json.loads(SCRATCHPAD.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0

    # Only act on in-flight agent-dispatch chains
    if state.get("chain") != "agent-dispatch":
        return 0

    state["current_stage"] = "completion-enforcer"
    state["stages_completed"] = ["pql-validation", "meta-prompting", "execution"]
    state["stages_remaining"] = ["hallucination-detector", "audit-ledger"]
    state["subagent_stopped_at"] = now_iso

    SCRATCHPAD.write_text(json.dumps(state, indent=2), encoding="utf-8")

    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "event": "subagent_stop",
            "chain": "agent-dispatch",
            "timestamp": now_iso,
        }) + "\n")

    print(
        "[skill-chain-supervisor] Subagent finished. Post-stages pending: "
        "completion-enforcer, hallucination-detector, audit-ledger. "
        "Invoke ghengis-skills:skill-chain-supervisor to complete.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
