#!/usr/bin/env python3
"""
One-shot installer for the agent-monitor statusline.

Run once per machine. Copies statusline-bar.py to ~/.claude/ and merges
the statusLine entry into ~/.claude/settings.json (preserving all other
keys). Idempotent — safe to re-run.
"""
import json
import shutil
import sys
from pathlib import Path

CLAUDE_HOME = Path.home() / ".claude"
TARGET_SCRIPT = CLAUDE_HOME / "statusline-bar.py"
SETTINGS = CLAUDE_HOME / "settings.json"
# Script is bundled alongside this installer
SOURCE_SCRIPT = Path(__file__).parent / "statusline-bar.py"


def resolve_python() -> str:
    """Pick a Python interpreter that exists on this machine.

    Many systems (modern macOS, most Linux) ship `python3` but not `python`.
    Windows and some distros ship `python` but not `python3`. Prefer `python3`
    because it's the explicit name; fall back to `python`; last resort, hand
    back the literal `python3` and hope it's on PATH at statusline time.
    """
    for name in ("python3", "python"):
        found = shutil.which(name)
        if found:
            return found
    return "python3"


def main() -> int:
    if not SOURCE_SCRIPT.exists():
        print(f"ERROR: statusline-bar.py not found at {SOURCE_SCRIPT}", file=sys.stderr)
        print("Plugin may be corrupted. Reinstall ghengis-skills.", file=sys.stderr)
        return 1

    CLAUDE_HOME.mkdir(parents=True, exist_ok=True)

    # 1. Copy the script
    shutil.copy2(SOURCE_SCRIPT, TARGET_SCRIPT)
    print(f"[install-statusline] Copied statusline-bar.py to {TARGET_SCRIPT}")

    # 2. Merge statusLine into settings.json
    python_cmd = resolve_python()
    cmd = f"{python_cmd} {TARGET_SCRIPT.as_posix()}"
    status_entry = {"type": "command", "command": cmd}

    if SETTINGS.exists():
        try:
            settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"ERROR: {SETTINGS} is not valid JSON: {e}", file=sys.stderr)
            print("Fix the file manually first, then re-run.", file=sys.stderr)
            return 1
    else:
        settings = {}

    existing = settings.get("statusLine")
    if existing == status_entry:
        print(f"[install-statusline] settings.json already configured, nothing to change")
    else:
        if existing:
            print(f"[install-statusline] Replacing existing statusLine: {existing}")
        settings["statusLine"] = status_entry
        SETTINGS.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        print(f"[install-statusline] Updated {SETTINGS} with statusLine config")

    print()
    print("Done. Restart Claude Code (not /reload-plugins — a full exit and relaunch)")
    print("to see the status bar below your prompt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
