---
name: reload-ghengis
description: Force-refresh the ghengis-skills plugin from GitHub, bypassing Claude Code's `/plugin update` caching. Use when `/plugin update` claims you're on an old version even after running it, or when you want to guarantee you're on the latest. Idempotent and safe.
disable-model-invocation: true
allowed-tools: Bash
---

# Reload ghengis-skills

Bypass Claude Code's `/plugin update` caching and force-sync the plugin
from GitHub. Safe to run any time — idempotent, only fixes things if
they're out of sync.

## When to use

- `/plugin update ghengis-skills` claims you're on an old version
- You pushed a new version to GitHub but `/reload-plugins` doesn't pick it up
- Plugin state looks confused on a new machine
- "It should be updated but it isn't"

## What it does

1. Finds your marketplace clone at `~/.claude/plugins/marketplaces/ghengis-skills-marketplace/`
2. `git fetch + reset --hard origin/master` to force-sync from GitHub
3. Reads the new version number from `plugin.json`
4. Copies fresh files into the plugin cache
5. Updates `installed_plugins.json` to point at the new version
6. Tells you to run `/reload-plugins`

## Run it

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/refresh_plugin.py" \
  || python "${CLAUDE_SKILL_DIR}/scripts/refresh_plugin.py"
```

After the script finishes, run `/reload-plugins` in Claude Code to activate.

## Safety

- Idempotent — running twice has no extra effect
- Preserves `installedAt` timestamp across refreshes
- Doesn't delete old cache versions (they're harmless, just unused)
- Exits non-zero with a clear error if anything fails

## Bootstrap on a fresh machine (no plugin installed yet)

The script also handles the no-marketplace case by git-cloning the
repo from `https://github.com/Kgan01/ghengis-skills.git`. So you can
run it on a brand-new machine with zero Claude Code plugin state.

If you can't invoke this skill (because the plugin isn't installed),
use the standalone one-liner:

```bash
curl -fsSL https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py | python3
```
