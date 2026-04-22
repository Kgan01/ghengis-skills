#!/usr/bin/env python3
"""
SessionStart hook — check if ghengis-skills has an update available on GitHub.

Writes a notice to ~/.claude/ghengis-update-available.md if stale.
The UserPromptSubmit hook (inject_update_notice.py) picks it up on the
user's next message and surfaces via Claude's reply.

Caching: only hits the network once every 6 hours. Cache file at
~/.claude/ghengis-version-check.json stores last_checked + remote_version.

Runs async (non-blocking). Silent failure if network is down or GitHub
is unreachable — not worth annoying the user about.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

CLAUDE_HOME = Path.home() / ".claude"
CACHE_FILE = CLAUDE_HOME / "ghengis-version-check.json"
NOTICE_FILE = CLAUDE_HOME / "ghengis-update-available.md"
REMOTE_PLUGIN_JSON = "https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/.claude-plugin/plugin.json"
CHECK_INTERVAL_HOURS = 6
TIMEOUT_SECONDS = 4


def get_installed_version() -> str:
    installed_file = CLAUDE_HOME / "plugins" / "installed_plugins.json"
    if not installed_file.exists():
        return ""
    try:
        data = json.loads(installed_file.read_text(encoding="utf-8"))
        entry = data.get("plugins", {}).get("ghengis-skills@ghengis-skills-marketplace")
        if entry and len(entry) > 0:
            return entry[0].get("version", "")
    except (json.JSONDecodeError, OSError):
        pass
    return ""


def should_check() -> bool:
    if not CACHE_FILE.exists():
        return True
    try:
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        last_iso = cache.get("last_checked", "")
        last = datetime.fromisoformat(last_iso.replace("Z", "+00:00"))
        age_hours = (datetime.now(timezone.utc) - last).total_seconds() / 3600
        return age_hours >= CHECK_INTERVAL_HOURS
    except (json.JSONDecodeError, ValueError, OSError):
        return True


def fetch_remote_version() -> str:
    try:
        req = urllib.request.Request(REMOTE_PLUGIN_JSON, headers={"User-Agent": "ghengis-skills-version-check/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("version", "")
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, OSError):
        return ""


def version_tuple(v: str) -> tuple:
    """Parse '1.9.4' -> (1, 9, 4). Handles missing/weird values gracefully."""
    try:
        return tuple(int(p) for p in v.split("."))
    except (ValueError, AttributeError):
        return (0,)


def main() -> int:
    if not should_check():
        return 0

    installed = get_installed_version()
    if not installed:
        # Plugin not installed or unparseable — nothing to compare
        return 0

    remote = fetch_remote_version()
    if not remote:
        # Network unreachable, silent
        return 0

    # Update cache regardless of result
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({
        "last_checked": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "installed_version": installed,
        "remote_version": remote,
    }, indent=2), encoding="utf-8")

    # If remote is newer, write notice. If not, remove any stale notice.
    if version_tuple(remote) > version_tuple(installed):
        NOTICE_FILE.write_text(
            f"## [ghengis-skills] Update available: {installed} → {remote}\n"
            f"\n"
            f"A newer version of ghengis-skills is on GitHub. "
            f"Run `/reload-ghengis` (or `/plugin update ghengis-skills`) to upgrade, "
            f"then `/reload-plugins`.\n",
            encoding="utf-8",
        )
    else:
        # No update needed — clear any stale notice
        if NOTICE_FILE.exists():
            try:
                NOTICE_FILE.unlink()
            except OSError:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
