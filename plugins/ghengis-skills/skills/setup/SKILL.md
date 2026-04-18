---
name: setup
description: Run once after installing ghengis-skills to configure autonomous permissions — sets up safe tool access and blocks dangerous operations
disable-model-invocation: true
allowed-tools: Read Write Edit Bash(cat *) Bash(mkdir *)
---

# Ghengis Skills Setup

Configure Claude Code for autonomous operation with safe defaults.

## Process

### Step 1: Read current settings

Read `~/.claude/settings.json` to check what's already configured.

### Step 2: Merge permissions

Add the following permissions to the user's settings, merging with any existing rules (don't overwrite what's already there).

**Allow list** — safe dev tools that Claude can use without asking. Includes process management (`kill`, `pkill`, `lsof`, `ps`) and file removal (`rm`) so Claude can clean up dev servers and ephemeral artifacts without prompting. Catastrophic `rm -rf` targets (`/`, `~`, `$HOME`) stay denied below:

```json
[
  "Bash(git:*)", "Bash(python:*)", "Bash(python3:*)", "Bash(python -m:*)",
  "Bash(pytest:*)", "Bash(pip:*)", "Bash(pip3:*)",
  "Bash(npm:*)", "Bash(npx:*)", "Bash(node:*)",
  "Bash(docker:*)", "Bash(docker compose:*)",
  "Bash(pio:*)", "Bash(gh:*)", "Bash(curl:*)",
  "Bash(make:*)", "Bash(cmake:*)", "Bash(cargo:*)", "Bash(go:*)",
  "Bash(flutter:*)", "Bash(dart:*)",
  "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)",
  "Bash(wc:*)", "Bash(find:*)", "Bash(tree:*)", "Bash(grep:*)",
  "Bash(mkdir:*)", "Bash(chmod:*)", "Bash(echo:*)", "Bash(sort:*)",
  "Bash(xargs:*)", "Bash(basename:*)", "Bash(dirname:*)",
  "Bash(cp:*)", "Bash(mv:*)", "Bash(touch:*)", "Bash(diff:*)",
  "Bash(sed:*)", "Bash(awk:*)", "Bash(cut:*)", "Bash(tr:*)",
  "Bash(tee:*)", "Bash(jq:*)", "Bash(bash:*)",
  "Bash(cd:*)", "Bash(pwd:*)", "Bash(which:*)", "Bash(env:*)",
  "Bash(sudo:*)",
  "Bash(rm:*)",
  "Bash(kill:*)", "Bash(pkill:*)", "Bash(killall:*)",
  "Bash(lsof:*)", "Bash(ps:*)",
  "Read", "Edit", "Write", "WebSearch",
  "WebFetch(domain:github.com)",
  "WebFetch(domain:raw.githubusercontent.com)",
  "WebFetch(domain:docs.anthropic.com)",
  "WebFetch(domain:pypi.org)",
  "WebFetch(domain:npmjs.com)",
  "WebFetch(domain:stackoverflow.com)"
]
```

**Deny list** — irreversible / catastrophic operations that always require confirmation. Note: `rm` and `kill` are allowed broadly above; only the genuinely-cannot-be-undone variants live here:

```json
[
  "Bash(rm -rf /:*)",
  "Bash(rm -rf ~:*)",
  "Bash(rm -rf $HOME:*)",
  "Bash(git push --force:*)", "Bash(git push -f:*)",
  "Bash(git reset --hard:*)", "Bash(git clean -f:*)",
  "Bash(chmod 777:*)",
  "Bash(shutdown:*)", "Bash(reboot:*)", "Bash(halt:*)", "Bash(poweroff:*)",
  "Bash(mkfs:*)", "Bash(dd:*)", "Bash(diskutil erase:*)", "Bash(launchctl:*)"
]
```

### Step 3: Write settings

Read `~/.claude/settings.json`, merge the allow and deny lists (deduplicating), and write back. Preserve all existing settings — only add to `permissions.allow` and `permissions.deny`.

### Step 4: Confirm

Tell the user what was added and that they need to restart Claude Code for the permissions to take effect.

## Rules

- NEVER remove existing permissions — only add
- NEVER overwrite non-permission settings
- Deduplicate — don't add rules that already exist
- Always show the user what changed before writing
- Ask for confirmation before writing to settings.json
