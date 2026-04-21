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
    python scratchpad.py path    # show which file is active
"""
import json
import os
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
    if not args:
        print("usage: merge <subkey>  (reads JSON object from stdin)", file=sys.stderr)
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
    state.setdefault(args[0], {})
    if isinstance(state[args[0]], dict):
        state[args[0]].update(payload)
    else:
        state[args[0]] = payload
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


COMMANDS = {
    "read": cmd_read,
    "write": cmd_write,
    "merge": cmd_merge,
    "advance": cmd_advance,
    "dump": cmd_dump,
    "path": cmd_path,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"usage: {sys.argv[0]} <{'|'.join(COMMANDS)}> [args]", file=sys.stderr)
        return 2
    return COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
