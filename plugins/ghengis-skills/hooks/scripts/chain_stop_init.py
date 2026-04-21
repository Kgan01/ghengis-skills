#!/usr/bin/env python3
"""
Stop hook for task-complete chain.

State location: <cwd>/.claude/ghengis-chain/
Per-project. Logs task-complete events when files were edited this turn.
Skips when agent-dispatch chain is in-flight (that chain handles verification).
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
    edit_log = chain_dir / "edited-files.log"
    scratchpad = chain_dir / "context.json"
    task_complete_log = chain_dir / "task-complete-log.jsonl"

    if not edit_log.exists() or edit_log.stat().st_size == 0:
        return 0

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Don't clobber an in-flight agent-dispatch chain
    if scratchpad.exists():
        try:
            state = json.loads(scratchpad.read_text(encoding="utf-8"))
            if state.get("chain") == "agent-dispatch" and state.get("stages_remaining"):
                return 0
        except (json.JSONDecodeError, OSError):
            pass

    edited = set()
    try:
        for line in edit_log.read_text(encoding="utf-8", errors="replace").splitlines():
            if "|" in line:
                edited.add(line.split("|", 1)[1].strip())
    except OSError:
        return 0

    if not edited:
        return 0

    task_complete_log.parent.mkdir(parents=True, exist_ok=True)
    with open(task_complete_log, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": now_iso,
            "chain": "task-complete",
            "files_edited": len(edited),
        }) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
