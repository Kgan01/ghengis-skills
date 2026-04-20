#!/usr/bin/env python3
"""
scratchpad.py — shared-state helper for skill-chain-supervisor chains.

Usage (from any skill's Bash context):

    # Read a subkey
    python ~/.claude/plugins/cache/.../scripts/scratchpad.py read pql_validation
    python ~/.claude/plugins/.../scripts/scratchpad.py read pql_validation.score

    # Write a namespaced value (JSON string or primitive)
    python scratchpad.py write pql_validation.score 0.85
    python scratchpad.py write pql_validation.anti_patterns '["vague-deliverable","missing-role"]'

    # Update multiple keys at once (JSON on stdin)
    echo '{"score":0.85,"anti_patterns":[]}' | python scratchpad.py merge pql_validation

    # Advance chain stage
    python scratchpad.py advance

    # Full dump
    python scratchpad.py dump
"""
import json
import os
import sys
from pathlib import Path

SCRATCHPAD = Path(os.environ.get("GHENGIS_CHAIN_SCRATCHPAD",
                                 os.path.expanduser("~/.claude/ghengis-chain-context.json")))


def load():
    if not SCRATCHPAD.exists():
        return {}
    try:
        return json.loads(SCRATCHPAD.read_text())
    except json.JSONDecodeError:
        return {}


def save(state):
    SCRATCHPAD.parent.mkdir(parents=True, exist_ok=True)
    SCRATCHPAD.write_text(json.dumps(state, indent=2))


def get_path(state, dotted):
    """Traverse dotted path: 'pql_validation.score' -> state['pql_validation']['score']."""
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
    """Try JSON parse, fall back to string."""
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


COMMANDS = {
    "read": cmd_read,
    "write": cmd_write,
    "merge": cmd_merge,
    "advance": cmd_advance,
    "dump": cmd_dump,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"usage: {sys.argv[0]} <{'|'.join(COMMANDS)}> [args]", file=sys.stderr)
        return 2
    return COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
