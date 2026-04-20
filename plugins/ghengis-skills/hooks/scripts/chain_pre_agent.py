#!/usr/bin/env python3
"""
PreToolUse(Agent) hook for skill-chain-supervisor.

Behavior:
- If scratchpad has an in-flight chain, archive it to history/ before overwriting
- Write fresh chain state for this dispatch
- Append to chain log
- Print status to stderr (non-blocking, warn-only)
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
SCRATCHPAD = HOME / ".claude" / "ghengis-chain-context.json"
LOG = HOME / ".claude" / "ghengis-chain-log.jsonl"
HISTORY_DIR = HOME / ".claude" / "ghengis-chain-history"


def main() -> int:
    now = datetime.now(timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    archive_stamp = now.strftime("%Y%m%dT%H%M%SZ")

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCHPAD.parent.mkdir(parents=True, exist_ok=True)

    # Archive existing in-flight chain before overwriting
    archived = False
    if SCRATCHPAD.exists():
        try:
            prior = json.loads(SCRATCHPAD.read_text())
            if prior.get("stages_remaining"):
                # In-flight chain — archive it
                archive_file = HISTORY_DIR / f"interrupted-{archive_stamp}.json"
                prior["interrupted_at"] = now_iso
                prior["interrupt_reason"] = "new agent dispatched before chain completed"
                archive_file.write_text(json.dumps(prior, indent=2))
                archived = True
        except (json.JSONDecodeError, OSError):
            pass  # corrupt file, just overwrite

    # Fresh chain state.
    # current_stage is what's ABOUT to run; stages_remaining excludes it.
    state = {
        "chain": "agent-dispatch",
        "started_at": now_iso,
        "current_stage": "pql-validation",
        "stages_completed": [],
        "stages_remaining": [
            "meta-prompting",
            "execution",
            "completion-enforcer",
            "hallucination-detector",
            "audit-ledger",
        ],
        "input": {"triggered_by": "PreToolUse(Agent) hook"},
        "hook_triggered": True,
    }
    SCRATCHPAD.write_text(json.dumps(state, indent=2))

    # Append chain log
    log_entry = {
        "event": "chain_start",
        "chain": "agent-dispatch",
        "timestamp": now_iso,
    }
    if archived:
        log_entry["archived_prior"] = True
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Stderr nudge
    msg = f"[skill-chain-supervisor] agent-dispatch chain initiated. State at {SCRATCHPAD}"
    if archived:
        msg += " (prior in-flight chain archived to history/)"
    print(msg, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
