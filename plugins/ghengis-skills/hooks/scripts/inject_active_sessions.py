#!/usr/bin/env python3
"""
UserPromptSubmit hook — reads active-sessions.json and injects a summary
of what OTHER Claude sessions are currently working on in this project.

Output goes to stdout (hook stdout = injected into user's prompt context).
Only includes sessions OTHER than the current one.
Only shows sessions active in the last 30 minutes.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

STALE_MINUTES = 30


def _normalize_cwd(cwd_str: str) -> Path:
    if not cwd_str:
        return Path(os.getcwd())
    if len(cwd_str) >= 3 and cwd_str[0] == "/" and cwd_str[2] == "/" and cwd_str[1].isalpha():
        return Path(f"{cwd_str[1].upper()}:/{cwd_str[3:]}")
    return Path(cwd_str)


def _parse_iso(iso_str: str) -> float:
    if not iso_str:
        return 0
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.timestamp()
    except (ValueError, TypeError):
        return 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}

    cwd = _normalize_cwd(data.get("cwd") or "")
    my_session = data.get("session_id") or data.get("sessionId") or ""

    sessions_file = cwd / ".claude" / "ghengis-chain" / "active-sessions.json"
    if not sessions_file.exists():
        return 0

    try:
        sessions = json.loads(sessions_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0

    now_ts = datetime.now(timezone.utc).timestamp()
    cutoff = now_ts - (STALE_MINUTES * 60)

    # Other sessions active recently, not me
    others = {
        sid: info for sid, info in sessions.items()
        if sid != my_session and _parse_iso(info.get("last_active", "")) > cutoff
    }

    if not others:
        return 0

    # Build a compact report
    lines = ["## [session-coordination] Other Claude sessions in this project"]
    for sid, info in others.items():
        last_active = info.get("last_active", "unknown")
        files = info.get("recent_files", [])
        # Short session ID
        short_sid = sid[:8] if len(sid) >= 8 else sid
        lines.append(f"- **session {short_sid}** (last active {last_active})")
        if files:
            lines.append(f"  - touching: " + ", ".join(f"`{f}`" for f in files[:5]))

    lines.append("")
    lines.append("_Heads up before editing — avoid colliding with active work above._")
    lines.append("")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
