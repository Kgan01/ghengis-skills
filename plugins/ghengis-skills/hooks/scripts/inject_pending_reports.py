#!/usr/bin/env python3
"""
UserPromptSubmit hook — reads ~/.claude/pending-scan-report.md (if it exists)
and prints its contents to stdout. Hook stdout is injected into the user's
prompt context, so Claude sees the report and surfaces it to the user.

After printing, the report file is deleted so it doesn't re-surface every turn.

Runs in PARALLEL with the time-tracker hook (both hooks emit stdout and both
outputs are combined). The time context stamp is NOT affected.
"""
import sys
from pathlib import Path

PENDING = Path.home() / ".claude" / "pending-scan-report.md"


def main() -> int:
    if not PENDING.exists():
        return 0
    try:
        content = PENDING.read_text(encoding="utf-8")
    except OSError:
        return 0
    if content.strip():
        print(content)
    try:
        PENDING.unlink()
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
