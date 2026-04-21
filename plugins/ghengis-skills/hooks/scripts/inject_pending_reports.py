#!/usr/bin/env python3
"""
UserPromptSubmit hook — reads <cwd>/.claude/ghengis-chain/pending-scan-report.md
(if it exists) and prints its contents to stdout. Hook stdout is injected
into the user's prompt context, so Claude sees the report and surfaces
it to the user.

After printing, the report file is deleted so it doesn't re-surface
every turn.
"""
import json
import os
import sys
from pathlib import Path


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}

    cwd = Path(data.get("cwd") or os.getcwd())
    pending = cwd / ".claude" / "ghengis-chain" / "pending-scan-report.md"

    if not pending.exists():
        return 0
    try:
        content = pending.read_text(encoding="utf-8")
    except OSError:
        return 0
    if content.strip():
        print(content)
    try:
        pending.unlink()
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
