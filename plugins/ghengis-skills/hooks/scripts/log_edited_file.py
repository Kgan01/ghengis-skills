#!/usr/bin/env python3
"""
PostToolUse(Write|Edit) hook — silent file logger.

Appends `<iso-timestamp>|<file_path>` to ~/.claude/edited-files-session.log.
Never blocks, no Haiku call, no user-visible output.

Uses proper UTF-8 JSON parsing so unicode paths (emoji, CJK chars, etc.)
are handled correctly — the previous bash+grep version silently dropped
unicode paths.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EDIT_LOG = Path.home() / ".claude" / "edited-files-session.log"


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0  # silent fail, don't break the tool

    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    file_path = tool_input.get("file_path") or tool_input.get("filePath")
    if not file_path:
        return 0

    EDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(EDIT_LOG, "a", encoding="utf-8") as f:
        f.write(f"{now_iso}|{file_path}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
