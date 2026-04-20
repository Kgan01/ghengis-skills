#!/usr/bin/env python3
"""
Stop hook for task-complete chain.

Writes a minimal state marker so the supervisor (or any participant skill)
knows a task just completed. Doesn't invoke anything — command hooks can't
make their output visible in the transcript. The UserPromptSubmit injector
surfaces post-task review on the next turn.

Only fires if files were edited this session (something material happened).
Skips pure-chat responses to avoid noise.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
EDIT_LOG = HOME / ".claude" / "edited-files-session.log"
CHAIN_STATE = HOME / ".claude" / "ghengis-chain-context.json"
TASK_COMPLETE_LOG = HOME / ".claude" / "ghengis-task-complete-log.jsonl"


def main() -> int:
    # Only act if there's material work to verify
    if not EDIT_LOG.exists() or EDIT_LOG.stat().st_size == 0:
        return 0

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # If an agent-dispatch chain is in-flight, don't clobber — that chain's
    # post-stages will handle verification. Only fire task-complete if the
    # scratchpad is empty or from a different chain.
    if CHAIN_STATE.exists():
        try:
            state = json.loads(CHAIN_STATE.read_text())
            if state.get("chain") == "agent-dispatch" and state.get("stages_remaining"):
                # agent-dispatch will handle it
                return 0
        except (json.JSONDecodeError, OSError):
            pass

    # Count files edited this turn
    edited = set()
    try:
        for line in EDIT_LOG.read_text().splitlines():
            if "|" in line:
                edited.add(line.split("|", 1)[1].strip())
    except OSError:
        return 0

    if not edited:
        return 0

    # Log task-complete event (for history)
    TASK_COMPLETE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(TASK_COMPLETE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": now_iso,
            "chain": "task-complete",
            "files_edited": len(edited),
        }) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
