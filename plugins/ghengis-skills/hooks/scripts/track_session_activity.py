#!/usr/bin/env python3
"""
PostToolUse(Write|Edit) hook — tracks what each session is working on.

Writes to <cwd>/.claude/ghengis-chain/active-sessions.json:

  {
    "abc123": {
      "last_active": "2026-04-21T00:03:12Z",
      "cwd": "/path/to/project",
      "recent_files": ["apps/server/foo.py", "apps/web/bar.tsx"]
    },
    ...
  }

Entries older than STALE_MINUTES are pruned on every write.
Read by inject_active_sessions.py on UserPromptSubmit to show Claude
what OTHER sessions are doing in the same project.

This runs ALONGSIDE log_edited_file.py (they do different things):
- log_edited_file.py: tracks files edited this turn for the scanner
- track_session_activity.py: tracks what each session is working on
  for cross-session visibility
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

STALE_MINUTES = 30
MAX_RECENT_FILES = 10


def _normalize_cwd(cwd_str: str) -> Path:
    if not cwd_str:
        return Path(os.getcwd())
    if len(cwd_str) >= 3 and cwd_str[0] == "/" and cwd_str[2] == "/" and cwd_str[1].isalpha():
        return Path(f"{cwd_str[1].upper()}:/{cwd_str[3:]}")
    return Path(cwd_str)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return 0

    cwd = _normalize_cwd(data.get("cwd") or "")
    session_id = data.get("session_id") or data.get("sessionId") or "unknown"

    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    file_path = tool_input.get("file_path") or tool_input.get("filePath")
    if not file_path:
        return 0

    sessions_file = cwd / ".claude" / "ghengis-chain" / "active-sessions.json"
    sessions_file.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Load existing state
    try:
        sessions = json.loads(sessions_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        sessions = {}

    # Prune stale sessions
    cutoff = now.timestamp() - (STALE_MINUTES * 60)
    sessions = {
        sid: info for sid, info in sessions.items()
        if _parse_iso(info.get("last_active", "")) > cutoff
    }

    # Upsert my session
    me = sessions.setdefault(session_id, {"recent_files": []})
    me["last_active"] = now_iso
    me["cwd"] = str(cwd)
    recent = me.get("recent_files", [])
    # Move file to front, dedup, cap
    recent = [file_path] + [f for f in recent if f != file_path]
    me["recent_files"] = recent[:MAX_RECENT_FILES]

    sessions_file.write_text(json.dumps(sessions, indent=2), encoding="utf-8")
    return 0


def _parse_iso(iso_str: str) -> float:
    """Parse ISO-8601 string to epoch seconds. Returns 0 on failure."""
    if not iso_str:
        return 0
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.timestamp()
    except (ValueError, TypeError):
        return 0


if __name__ == "__main__":
    sys.exit(main())
