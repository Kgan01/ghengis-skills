---
name: tri-model-setup
description: Use when installing or repairing the tri-model harness on a machine that lacks it — "set up the tri-model rig", "install the legs", "wire Gemini and GPT into Claude Code" — or when the tri-model skill fires but agy or codex is missing or unauthenticated. Installs agy (Antigravity CLI) + codex CLI + first-party plugin, deploys the wrapper, agent, and commands bundled in this skill's assets, and runs the auth dances.
allowed-tools: Read Write Edit Bash PowerShell WebFetch
---

# Tri-Model Harness — Setup

Turns a bare Claude Code machine into the three-leg rig: Claude host (unmetered), Gemini leg via `agy` (AI Pro sub), GPT leg via `codex` (ChatGPT sub). Everything needed ships in this skill's `scripts/` and `assets/` — deploy, don't re-derive. Tested end-to-end on Windows 11, 2026-08-10.

## Steps

### 1. Install agy (Gemini leg binary)

Windows: `curl.exe -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && cmd /c install.cmd` (macOS/Linux: `install.sh` from the same host). Binary lands at `%LOCALAPPDATA%\agy\bin\agy.exe`; PATH updates in the registry but NOT in already-open shells — use the full path until restart.

### 2. Install codex (GPT leg) + first-party plugin

```
npm install -g @openai/codex@latest
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex        # marketplace registers as "openai-codex"
```

**GOTCHA (observed):** if global npm config has `os` pinned (e.g. `npm config get os` → `linux`), npm silently skips the platform binary and `codex` dies with "Missing optional dependency @openai/codex-win32-x64". Fix per-install, don't touch the global config: `$env:npm_config_os='win32'; $env:npm_config_cpu='x64'; npm install -g @openai/codex@latest --force`.

The plugin's Stop-hook review gate is opt-in — leave it off initially.

### 3. Deploy the harness files

From this skill's directory to the user's global `~/.claude/`:

| Source | Destination |
|---|---|
| `scripts/agy-call.ps1` | `~/.claude/scripts/agy-call.ps1` — the Gemini wrapper (Flash default, JSONL usage log) |
| `assets/gemini-agent.md` | `~/.claude/agents/gemini.md` |
| `assets/commands/*.md` | `~/.claude/commands/` — /gemini /opinion /fusion /auto-validate /adw |
| `assets/adw/` (rosters.yaml + 14 workflows) | `~/.claude/tri-model/adw/` — the CANONICAL role→model + phase definitions /adw interprets. Ported verbatim from the pi-workbench ADW factory; edit models in rosters.yaml, never in command prose |

Check the wrapper's model shorthand map against `agy models` after auth (step 4) — ids drift as Google ships new versions; update the `switch` block if `flash`/`pro` no longer resolve.

### 4. Auth agy — the hard part

`agy` auth is browser OAuth with a **60-second window** and a paste-back code. Two facts make naive automation fail (both observed): the paste prompt reads the raw console, so piped stdin is ignored — you need a real ConPTY; and `proc.read()` on the pty **blocks**, so the code-feed must run on its own thread (already fixed in `scripts/agy_pty_auth.py`).

The dance that works (~10s of user time):

1. Run `scripts/agy_pty_auth.py` (needs `pip install pywinpty`) hidden — it spawns agy under a pty, writes the OAuth URL to `url.txt`, and feeds `code.txt` to the pty the moment it appears.
2. Open the URL from `url.txt` in the user's browser (`Start-Process $url`).
3. Tell the user: click the **personal** Google account (the one holding AI Pro — a Workspace account charges the wrong entitlement and fails quietly), then **Sign in**, then **Copy to Clipboard** on the code page.
4. Poll the clipboard for `^4/0A\S+` (via `powershell -STA -NoProfile -Command Get-Clipboard`, ~1s interval, 55s budget) and write the hit to `code.txt`. The pty driver does the rest.
5. Success = the pty log ends with the prompt's answer and agy exits 0. Credentials persist in the OS keyring — one-time dance.

Verify: `agy models` lists models; `agy-call.ps1 -Prompt "say ok"` exits 0 and appends to `~/.claude/tri-model/agy-usage.jsonl`.

### 5. Auth codex — the easy one

`codex login` runs a localhost callback server — no code paste. Start it hidden with output redirected (it's an npm shim, launch via `cmd /c codex login > out 2> err`), extract the `https://auth.openai.com/...` URL from the output, open it in the user's browser, and the sign-in completes itself. Verify: `codex login status` → "Logged in using ChatGPT", then a live round-trip: `codex exec --skip-git-repo-check "say ok"`.

### 6. Record the install

Write/refresh `~/.claude/tri-model/README.md` (legs, auth state, model-id map, usage-log path) so future sessions and the `tri-model` skill have ground truth.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Asking the user to paste the OAuth code into chat | Chat round-trip exceeds agy's 60s window (observed: ~70s, repeatedly) | Clipboard poll — the user only clicks "Copy to Clipboard" |
| Feeding the code via redirected stdin | agy reads the console, not the pipe (observed: code silently ignored) | ConPTY via pywinpty, threaded feeder |
| Driving the Google consent UI with browser automation | Per-click round-trips + re-appearing interstitials blow the window (observed: 4 failed rounds) | Human clicks (fast), automation only opens the URL and watches the clipboard |
| Letting the user auth agy with a Workspace account | Wrong entitlement, fails quietly or bills wrong | Say "personal account" out loud before the browser opens |
| Assuming `npm i -g` produced a working codex | Platform-pin config silently skips the binary | Run `codex --version` before calling install done |
| Hardcoding Gemini model ids without checking | agy model ids rotate (3.5 → 3.6 …) | Verify against `agy models`, update the wrapper map |

## Cross-References

- **`tri-model`** — the routing doctrine this setup enables; read it after installing.
- Local decision record template: `~/.claude/tri-model/README.md`.
- First-party codex plugin docs: `claude plugin details codex@openai-codex`.
