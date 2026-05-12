#!/usr/bin/env python3
"""
scratchpad.py — shared-state helper for skill-chain-supervisor chains.

Per-project state at: <project>/.claude/ghengis-chain/context.json

Project root resolution order:
1. GHENGIS_CHAIN_PROJECT_ROOT env var (explicit override)
2. Walk up from $PWD looking for .claude/ghengis-chain/
3. Walk up from $PWD looking for .claude/
4. Fallback: $PWD itself (chain dir will be created there)

Usage (from any skill's Bash context):

    python scratchpad.py read pql_validation.score
    python scratchpad.py write pql_validation.score 0.85
    echo '{"score":0.85}' | python scratchpad.py merge pql_validation
    python scratchpad.py advance
    python scratchpad.py dump
    python scratchpad.py path                    # show which file is active

    # Chain lifecycle:
    python scratchpad.py init <chain_name> [--input-json '{"user_request":"..."}']
    python scratchpad.py finish                  # archive + (optionally) emit cognition

    # Nested chain support (chain-as-stage):
    python scratchpad.py nested-start <chain_name>     # allocate <chain_name>.* subkey
    python scratchpad.py nested-finish <chain_name>    # mark nested chain complete

    # Cognition integration (gated by GHENGIS_COGNITION=true):
    python scratchpad.py cognition-emit          # explicit emit; finish does this automatically
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path


def resolve_project_root() -> Path:
    override = os.environ.get("GHENGIS_CHAIN_PROJECT_ROOT")
    if override:
        return Path(override)
    cwd = Path.cwd().resolve()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".claude" / "ghengis-chain").is_dir():
            return parent
        if (parent / ".claude").is_dir():
            return parent
    return cwd


def scratchpad_path() -> Path:
    return resolve_project_root() / ".claude" / "ghengis-chain" / "context.json"


def chain_dir() -> Path:
    return resolve_project_root() / ".claude" / "ghengis-chain"


def history_dir() -> Path:
    return chain_dir() / "history"


def cognition_path() -> Path:
    return chain_dir() / "cognition.jsonl"


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load() -> dict:
    path = scratchpad_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save(state: dict):
    path = scratchpad_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_path(state, dotted):
    parts = dotted.split(".")
    node = state
    for p in parts:
        if not isinstance(node, dict) or p not in node:
            return None
        node = node[p]
    return node


def set_path(state, dotted, value):
    parts = dotted.split(".")
    node = state
    for p in parts[:-1]:
        if p not in node or not isinstance(node[p], dict):
            node[p] = {}
        node = node[p]
    node[parts[-1]] = value


def parse_value(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def cmd_read(args):
    if not args:
        print(json.dumps(load(), indent=2))
        return 0
    value = get_path(load(), args[0])
    if value is None:
        return 1
    if isinstance(value, (dict, list)):
        print(json.dumps(value, indent=2))
    else:
        print(value)
    return 0


def cmd_write(args):
    if len(args) < 2:
        print("usage: write <dotted.key> <value>", file=sys.stderr)
        return 2
    state = load()
    set_path(state, args[0], parse_value(args[1]))
    save(state)
    return 0


def cmd_merge(args):
    """Merge a JSON object (from stdin) into a (possibly nested) subkey.

    Dotted keys are walked through to the leaf; existing keys at the leaf
    are dict-merged. Used for nested chain output: `merge build_validate.validate`
    puts the payload at state["build_validate"]["validate"].
    """
    if not args:
        print("usage: merge <dotted.subkey>  (reads JSON object from stdin)", file=sys.stderr)
        return 2
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"stdin not valid JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("stdin must be a JSON object", file=sys.stderr)
        return 2
    state = load()
    existing = get_path(state, args[0])
    if isinstance(existing, dict):
        existing.update(payload)
        set_path(state, args[0], existing)
    else:
        set_path(state, args[0], payload)
    save(state)
    return 0


def cmd_advance(args):
    state = load()
    remaining = state.get("stages_remaining", [])
    completed = state.get("stages_completed", [])
    if not remaining:
        print("no stages remaining", file=sys.stderr)
        return 1
    next_stage = remaining.pop(0)
    completed.append(state.get("current_stage", ""))
    state["stages_completed"] = [s for s in completed if s]
    state["current_stage"] = next_stage
    state["stages_remaining"] = remaining
    save(state)
    print(next_stage)
    return 0


def cmd_dump(args):
    print(json.dumps(load(), indent=2))
    return 0


def cmd_path(args):
    print(scratchpad_path())
    return 0


def cmd_init(args):
    """Bootstrap a fresh chain scratchpad. Refuses to clobber an in-flight chain."""
    parser = argparse.ArgumentParser(prog="scratchpad.py init")
    parser.add_argument("chain_name")
    parser.add_argument("--input-json", default="{}", help="JSON object for input contract")
    parser.add_argument("--force", action="store_true", help="Overwrite existing in-flight chain")
    ns = parser.parse_args(args)

    existing = scratchpad_path()
    if existing.exists() and not ns.force:
        prior = load()
        if prior.get("current_stage") and prior.get("current_stage") != "report":
            print(
                f"in-flight chain detected (current_stage={prior['current_stage']}); "
                f"archive it first with `finish` or pass --force",
                file=sys.stderr,
            )
            return 1

    try:
        input_payload = json.loads(ns.input_json)
    except json.JSONDecodeError as e:
        print(f"--input-json not valid JSON: {e}", file=sys.stderr)
        return 2

    state = {
        "chain": ns.chain_name,
        "started_at": now_iso(),
        "current_stage": "init",
        "stages_completed": [],
        "stages_remaining": [],
        "input": input_payload,
    }
    save(state)
    print(scratchpad_path())
    return 0


def cmd_finish(args):
    """Archive scratchpad to history/ and (if enabled) emit a cognition entry."""
    parser = argparse.ArgumentParser(prog="scratchpad.py finish")
    parser.add_argument("--no-cognition", action="store_true", help="Skip cognition emission even if enabled")
    parser.add_argument("--no-archive", action="store_true", help="Skip moving to history/")
    ns = parser.parse_args(args)

    state = load()
    if not state:
        print("no scratchpad to finish", file=sys.stderr)
        return 1

    state["completed_at"] = now_iso()
    state["current_stage"] = "report"
    save(state)

    cognition_enabled = os.environ.get("GHENGIS_COGNITION", "").lower() in ("true", "1", "yes")
    if cognition_enabled and not ns.no_cognition:
        emit_cognition_entry(state)

    if not ns.no_archive:
        history_dir().mkdir(parents=True, exist_ok=True)
        ts = state["completed_at"].replace(":", "").replace("-", "")[:15]
        archive = history_dir() / f"{state.get('chain', 'chain')}-{ts}.json"
        shutil.copy2(scratchpad_path(), archive)
        scratchpad_path().unlink()
        print(archive)
    else:
        print(scratchpad_path())
    return 0


def cmd_nested_start(args):
    """Allocate a top-level <chain_name> subkey for a nested chain's output."""
    if not args:
        print("usage: nested-start <chain_name>", file=sys.stderr)
        return 2
    chain_name = args[0].replace("-", "_")
    state = load()
    if chain_name in state and isinstance(state[chain_name], dict) and state[chain_name].get("_nested_status") == "running":
        print(f"nested chain {chain_name} already running", file=sys.stderr)
        return 1
    state[chain_name] = {
        "_nested_status": "running",
        "_nested_started_at": now_iso(),
    }
    save(state)
    print(chain_name)
    return 0


def cmd_nested_finish(args):
    """Mark a nested chain complete. Its output stays under <chain_name>.*"""
    if not args:
        print("usage: nested-finish <chain_name>", file=sys.stderr)
        return 2
    chain_name = args[0].replace("-", "_")
    state = load()
    if chain_name not in state or not isinstance(state[chain_name], dict):
        print(f"no nested chain {chain_name} found", file=sys.stderr)
        return 1
    state[chain_name]["_nested_status"] = "completed"
    state[chain_name]["_nested_completed_at"] = now_iso()
    save(state)
    print(chain_name)
    return 0


def emit_cognition_entry(state: dict) -> dict:
    """Build a cognition entry from chain state and append to cognition.jsonl."""
    chain_name = state.get("chain", "unknown")
    started = state.get("started_at", "")
    completed = state.get("completed_at", now_iso())
    report = state.get("report", {}) or {}
    outcome = report.get("outcome", "unknown")
    score = report.get("score_progression", [])
    final_score = score[-1] if isinstance(score, list) and score else None

    # Heuristic lesson extraction: outcome string + any issues from validate stage(s)
    validate = state.get("validate", {}) or state.get("build_validate", {}).get("validate", {}) or {}
    issues = validate.get("issues", []) if isinstance(validate, dict) else []
    issues_text = "; ".join(issues[:3]) if issues else "no issues raised"

    # Stable id from chain name + completed_at
    raw_id = f"{chain_name}|{completed}"
    entry_id = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]

    fitness = None
    if isinstance(final_score, (int, float)):
        fitness = float(final_score) / 10.0

    entry = {
        "id": entry_id,
        "created_at": now_iso(),
        "chain": chain_name,
        "outcome": outcome,
        "final_score": final_score,
        "fitness": fitness,
        "lesson": _derive_lesson(chain_name, outcome, issues),
        "causal_factor": issues_text,
        "applies_when": _derive_applies_when(chain_name, state),
        "started_at": started,
        "completed_at": completed,
        "iterations_used": state.get("iterations_used"),
        "hits": 0,
        "wins": 0,
        "audit_status": "unchecked",
    }
    path = cognition_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=False) + "\n")
    return entry


def _derive_lesson(chain: str, outcome: str, issues: list) -> str:
    """Generate a short lesson string from outcome + issues. Heuristic, not LLM."""
    if outcome in ("shipped", "fixed", "skill-shipped", "integrated"):
        return f"{chain} succeeded cleanly on first or revised iteration"
    if outcome in ("shipped-with-notes", "fixed-with-notes", "skill-shipped-with-notes", "integrated-with-notes"):
        return f"{chain} succeeded but surfaced notes worth tracking"
    if outcome in ("revised-and-shipped",):
        return f"{chain} required revision loop; iteration 2 succeeded"
    if outcome in ("quality-gap-flagged", "fix-incomplete", "skill-incomplete"):
        return f"{chain} hit max iterations without reaching success threshold"
    if outcome in ("cannot-reproduce", "needs-redesign", "needs-decomposition", "tests-failing"):
        return f"{chain} exited early at {outcome}; precondition not satisfied"
    if outcome in ("kept-as-is", "discarded"):
        return f"{chain} ended without integration ({outcome})"
    return f"{chain} ended with outcome {outcome}"


def _derive_applies_when(chain: str, state: dict) -> str:
    """Build an embedding target describing the situation the chain ran in."""
    parts = [chain]
    input_obj = state.get("input", {})
    if isinstance(input_obj, dict):
        req = input_obj.get("user_request", "")
        if req:
            parts.append(str(req)[:160])
        dtype = input_obj.get("deliverable_type", "")
        if dtype:
            parts.append(f"deliverable:{dtype}")
    return " | ".join(parts)


def cmd_cognition_emit(args):
    """Explicitly emit a cognition entry from the current scratchpad."""
    state = load()
    if not state:
        print("no scratchpad to emit from", file=sys.stderr)
        return 1
    entry = emit_cognition_entry(state)
    print(json.dumps(entry, indent=2))
    return 0


COMMANDS = {
    "read": cmd_read,
    "write": cmd_write,
    "merge": cmd_merge,
    "advance": cmd_advance,
    "dump": cmd_dump,
    "path": cmd_path,
    "init": cmd_init,
    "finish": cmd_finish,
    "nested-start": cmd_nested_start,
    "nested-finish": cmd_nested_finish,
    "cognition-emit": cmd_cognition_emit,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"usage: {sys.argv[0]} <{'|'.join(COMMANDS)}> [args]", file=sys.stderr)
        return 2
    return COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
