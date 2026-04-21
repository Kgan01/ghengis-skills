#!/usr/bin/env python3
"""
SubagentStop hook for skill-chain-supervisor.

State location: <cwd>/.claude/ghengis-chain/
Advances the scratchpad from pre-execution stages to post-execution stages.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _normalize_cwd(cwd_str: str) -> Path:
    if not cwd_str:
        return Path(os.getcwd())
    if len(cwd_str) >= 3 and cwd_str[0] == "/" and cwd_str[2] == "/" and cwd_str[1].isalpha():
        return Path(f"{cwd_str[1].upper()}:/{cwd_str[3:]}")
    return Path(cwd_str)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}

    cwd = _normalize_cwd(data.get("cwd") or "")
    chain_dir = cwd / ".claude" / "ghengis-chain"
    scratchpad = chain_dir / "context.json"
    log = chain_dir / "log.jsonl"

    if not scratchpad.exists():
        return 0

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        state = json.loads(scratchpad.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0

    if state.get("chain") != "agent-dispatch":
        return 0

    state["current_stage"] = "completion-enforcer"
    state["stages_completed"] = ["pql-validation", "meta-prompting", "execution"]
    state["stages_remaining"] = ["hallucination-detector", "audit-ledger"]
    state["subagent_stopped_at"] = now_iso

    scratchpad.write_text(json.dumps(state, indent=2), encoding="utf-8")

    with open(log, "a", encoding="utf-8") as f:
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
