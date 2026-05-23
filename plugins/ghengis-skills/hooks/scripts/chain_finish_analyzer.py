#!/usr/bin/env python3
"""
PostToolUse(Bash) hook — auto-dispatch the analyzer subagent after a chain finishes.

Fires when a Bash command containing `scratchpad.py finish` runs successfully AND
GHENGIS_COGNITION is enabled. Prints a system-reminder to stdout that Claude Code
injects into the next turn, instructing the orchestrator to dispatch the
ghengis-skills:analyzer subagent on the freshly-archived scratchpad.

Silent in all other cases — does NOT spam the conversation with reminders
for unrelated Bash commands.

State location: per-project at <cwd>/.claude/
Reads:
- The Bash tool input (command + exit code) from stdin
- <cwd>/.claude/ghengis-chain/history/ for the latest archived scratchpad
- <cwd>/.claude/cognition.jsonl for the last entry's id (v1.19.0+ path)
"""
import json
import os
import sys
from pathlib import Path


def _normalize_cwd(cwd_str: str) -> Path:
    if not cwd_str:
        return Path(os.getcwd())
    if len(cwd_str) >= 3 and cwd_str[0] == "/" and cwd_str[2] == "/" and cwd_str[1].isalpha():
        return Path(f"{cwd_str[1].upper()}:/{cwd_str[3:]}")
    return Path(cwd_str)


def _cognition_enabled() -> bool:
    return os.environ.get("GHENGIS_COGNITION", "").lower() in ("true", "1", "yes")


def _is_finish_command(command: str) -> bool:
    """Detect `scratchpad.py finish` invocations regardless of how python is called."""
    if "scratchpad.py" not in command:
        return False
    # Look for `finish` as a standalone argument (not e.g. `finished`)
    # Cheap match: command contains the literal token after scratchpad.py
    after = command.split("scratchpad.py", 1)[1]
    tokens = after.split()
    return any(t == "finish" for t in tokens[:5])


def _command_succeeded(data: dict) -> bool:
    """Check the tool_response for non-zero exit signals.

    PostToolUse delivers `tool_response` with stdout/stderr/exit_code (or similar)
    depending on Claude Code version. Be defensive: if exit_code is present and
    non-zero, treat as failure. Otherwise default to success.
    """
    resp = data.get("tool_response") or data.get("toolResponse") or {}
    if not isinstance(resp, dict):
        return True
    exit_code = resp.get("exit_code")
    if exit_code is None:
        exit_code = resp.get("exitCode")
    if exit_code is None:
        # No structured exit info — assume success
        return True
    try:
        return int(exit_code) == 0
    except (ValueError, TypeError):
        return True


def _find_latest_history(chain_dir: Path) -> Path | None:
    history = chain_dir / "history"
    if not history.is_dir():
        return None
    candidates = sorted(
        (p for p in history.iterdir() if p.is_file() and p.suffix == ".json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _last_cognition_id(cog_path: Path) -> str | None:
    """Read the id of the last entry in cognition.jsonl.

    v1.19.0+: cognition.jsonl moved from <cwd>/.claude/ghengis-chain/cognition.jsonl
    to <cwd>/.claude/cognition.jsonl (per-project scope). The hook is project-scope-only
    so we don't consult the global library.
    """
    if not cog_path.exists():
        return None
    try:
        lines = [
            ln for ln in cog_path.read_text(encoding="utf-8").splitlines() if ln.strip()
        ]
    except OSError:
        return None
    if not lines:
        return None
    try:
        return json.loads(lines[-1]).get("id")
    except json.JSONDecodeError:
        return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return 0

    if not _cognition_enabled():
        return 0

    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    if not isinstance(command, str) or not _is_finish_command(command):
        return 0

    if not _command_succeeded(data):
        return 0

    cwd = _normalize_cwd(data.get("cwd") or "")
    chain_dir = cwd / ".claude" / "ghengis-chain"
    cognition_path = cwd / ".claude" / "cognition.jsonl"
    history_path = _find_latest_history(chain_dir)
    last_id = _last_cognition_id(cognition_path)

    if history_path is None or last_id is None:
        # No archived scratchpad or no cognition entry yet — nothing to analyze
        return 0

    # Emit a system-reminder. Claude Code injects this into the next turn.
    sys.stdout.write(
        "\n<system-reminder>\n"
        "Chain just finished with GHENGIS_COGNITION enabled. Auto-dispatch the\n"
        "`ghengis-skills:analyzer` subagent to replace the heuristic cognition\n"
        "entry with a high-quality structured lesson.\n\n"
        f"Archived scratchpad: {history_path}\n"
        f"Last cognition entry id (target for replacement): {last_id}\n"
        f"Cognition file: {cognition_path}\n\n"
        "After the analyzer returns its REPLACEMENT: <single-line JSON>, pipe it\n"
        "to the helper:\n"
        f"  echo '<JSON>' | python <scratchpad.py path> cognition-replace-last "
        f"--require-id {last_id}\n\n"
        "If the analyzer responds with ANALYSIS_DECLINED or KEEP_HEURISTIC_ENTRY,\n"
        "leave the existing entry in place — better generic than hallucinated.\n"
        "</system-reminder>\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
