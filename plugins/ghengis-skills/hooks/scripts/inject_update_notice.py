#!/usr/bin/env python3
"""
UserPromptSubmit hook — surfaces ~/.claude/ghengis-update-available.md
if present (not deleted on read — persists until user actually updates).

Runs alongside the other UserPromptSubmit hooks. Prints to stdout which
gets injected into Claude's context.

Unlike inject_pending_reports (which deletes the file after read), this
one leaves the notice in place so it keeps reminding the user until
they actually update. The version check hook will delete it when
installed version catches up.
"""
import sys
from pathlib import Path

NOTICE = Path.home() / ".claude" / "ghengis-update-available.md"


def main() -> int:
    if not NOTICE.exists():
        return 0
    try:
        content = NOTICE.read_text(encoding="utf-8")
    except OSError:
        return 0
    if content.strip():
        print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
