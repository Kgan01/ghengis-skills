#!/usr/bin/env python3
"""
PreToolUse(Agent) hook for skill-chain-supervisor.

State location: <cwd>/.claude/ghengis-chain/
Per-project isolation — sessions in the same folder share state,
sessions in different folders do not.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ARCHIVE_RETENTION_COUNT = 50


def chain_paths(cwd: Path):
    chain_dir = cwd / ".claude" / "ghengis-chain"
    chain_dir.mkdir(parents=True, exist_ok=True)
    history_dir = chain_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    return {
        "scratchpad": chain_dir / "context.json",
        "log": chain_dir / "log.jsonl",
        "history": history_dir,
    }


def prune_archive(history_dir: Path) -> int:
    files = sorted(history_dir.glob("interrupted-*.json"), key=lambda p: p.stat().st_mtime)
    excess = len(files) - ARCHIVE_RETENTION_COUNT
    deleted = 0
    for f in files[:excess] if excess > 0 else []:
        try:
            f.unlink()
            deleted += 1
        except OSError:
            pass
    return deleted


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}

    cwd = Path(data.get("cwd") or os.getcwd())
    paths = chain_paths(cwd)

    now = datetime.now(timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    archive_stamp = now.strftime("%Y%m%dT%H%M%SZ")

    # Archive existing in-flight chain — but only if some stages actually ran.
    # Phantoms (PQL-blocked dispatches) have empty stages_completed and are
    # silently overwritten rather than cluttering history/.
    archived = False
    if paths["scratchpad"].exists():
        try:
            prior = json.loads(paths["scratchpad"].read_text(encoding="utf-8"))
            prior_completed = prior.get("stages_completed") or []
            prior_remaining = prior.get("stages_remaining") or []
            if prior_remaining and prior_completed:
                archive_file = paths["history"] / f"interrupted-{archive_stamp}.json"
                prior["interrupted_at"] = now_iso
                prior["interrupt_reason"] = "new agent dispatched before chain completed"
                archive_file.write_text(json.dumps(prior, indent=2), encoding="utf-8")
                archived = True
        except (json.JSONDecodeError, OSError):
            pass

    prune_archive(paths["history"])

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
        "input": {"triggered_by": "PreToolUse(Agent) hook", "cwd": str(cwd)},
        "hook_triggered": True,
    }
    paths["scratchpad"].write_text(json.dumps(state, indent=2), encoding="utf-8")

    log_entry = {
        "event": "chain_start",
        "chain": "agent-dispatch",
        "timestamp": now_iso,
    }
    if archived:
        log_entry["archived_prior"] = True
    with open(paths["log"], "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    msg = f"[skill-chain-supervisor] agent-dispatch chain initiated at {paths['scratchpad']}"
    if archived:
        msg += " (prior in-flight chain archived)"
    print(msg, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
