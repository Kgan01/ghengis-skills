#!/usr/bin/env python3
"""
PostToolUse(Write|Edit) hook — silent file logger.

State location: <cwd>/.claude/ghengis-chain/edited-files.log
Per-project. Appends "<iso-timestamp>|<file_path>" for later batch scanning.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return 0

    cwd = Path(data.get("cwd") or os.getcwd())

    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    file_path = tool_input.get("file_path") or tool_input.get("filePath")
    if not file_path:
        return 0

    edit_log = cwd / ".claude" / "ghengis-chain" / "edited-files.log"
    edit_log.parent.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(edit_log, "a", encoding="utf-8") as f:
        f.write(f"{now_iso}|{file_path}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
