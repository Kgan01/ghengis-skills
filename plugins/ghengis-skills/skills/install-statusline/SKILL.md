---
name: install-statusline
description: One-shot installer for the agent-monitor terminal status line. Copies statusline-bar.py to ~/.claude/ and adds the statusLine config to settings.json. Run once per machine. Idempotent and safe.
disable-model-invocation: true
allowed-tools: Bash
---

# Install Statusline

Run this skill once per machine to enable the agent-monitor terminal status bar
(model name + color-coded context usage bar, shown below your Claude Code prompt).

## What it does

1. Copies `statusline-bar.py` from this plugin to `~/.claude/statusline-bar.py`
2. Merges `"statusLine"` config into `~/.claude/settings.json` (preserves all other keys)
3. Prints a confirmation

## After running

**Fully restart Claude Code** — not `/reload-plugins`. The `statusLine` config is
only read at startup. Press Ctrl+C or `/exit`, then run `claude` again.

## Why it's not automatic

Plugins cannot modify user `settings.json` or install files into `~/.claude/`
directly. The statusline config has to be opted in via this skill.

## Safety

- Idempotent — safe to run multiple times
- Preserves all existing `settings.json` keys
- Fails cleanly if `settings.json` is not valid JSON (won't corrupt your config)

## Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/install_statusline.py" \
  || python "${CLAUDE_SKILL_DIR}/scripts/install_statusline.py"
```

Use whichever Python binary exists on the system — modern macOS and most Linux
ship `python3` only; Windows and some distros ship `python` only. The installer
itself then auto-detects the right binary when wiring up `settings.json`.

Scripts are self-contained inside this skill's `scripts/` directory so the
skill doesn't depend on sibling skills or cross-directory path traversal.
