---
name: reload-ghengis
description: Force-refresh the ghengis-skills plugin from GitHub, bypassing Claude Code's `/plugin update` caching. Use when `/plugin update` claims you're on an old version even after running it, or when you want to guarantee you're on the latest. Idempotent and safe.
disable-model-invocation: true
allowed-tools: Bash PowerShell
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

1. Downloads the **latest** `refresh_plugin.py` from GitHub `master` and runs it
   (falls back to the copy bundled with this skill only if GitHub is unreachable)
2. Finds your marketplace clone at `~/.claude/plugins/marketplaces/ghengis-skills-marketplace/`
3. `git fetch + reset --hard origin/master` to force-sync from GitHub
4. Reads the new version number from `plugin.json`
5. Copies fresh files into the plugin cache
6. Updates `installed_plugins.json` to point at the new version
7. Tells you to fully restart Claude Code

**Why step 1 matters:** the bundled script is whatever version you already have
installed. If that copy has a bug (e.g. ≤ v1.26.1 crashed on Windows consoles with
`UnicodeEncodeError`), running it locally can never update you past the bug.
Fetching from `master` means every install always runs the newest fixes.

## Run it

Use exactly ONE of the two blocks — whichever shell tool you have. Both do the
same thing: fetch the latest script, fall back to the bundled copy if offline,
run it with the first working Python 3.

**Bash (macOS, Linux, Git Bash on Windows):**

```bash
URL="https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py"
LOCAL="${CLAUDE_SKILL_DIR}/scripts/refresh_plugin.py"
PY=""
for c in python3 python py; do
  "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >/dev/null 2>&1 && PY="$c" && break
done
[ -n "$PY" ] || { echo "[refresh ERROR] no Python 3.9+ found on PATH"; exit 1; }
"$PY" - "$URL" "$LOCAL" <<'PYEOF'
import sys, urllib.request
try:
    src = urllib.request.urlopen(sys.argv[1], timeout=20).read()
    print("[refresh] running latest refresh_plugin.py from GitHub master")
except Exception as e:
    src = open(sys.argv[2], "rb").read()
    print("[refresh WARN] GitHub unreachable (%s) - using bundled copy" % e)
exec(compile(src, "refresh_plugin.py", "exec"))
PYEOF
```

**PowerShell (Windows without Git Bash):**

```powershell
$url   = 'https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py'
$local = "${CLAUDE_SKILL_DIR}/scripts/refresh_plugin.py"
$py = @('python', 'python3', 'py') | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
if (-not $py) { Write-Output '[refresh ERROR] no Python found on PATH'; exit 1 }
$code = @'
import sys, urllib.request
try:
    src = urllib.request.urlopen(sys.argv[1], timeout=20).read()
    print("[refresh] running latest refresh_plugin.py from GitHub master")
except Exception as e:
    src = open(sys.argv[2], "rb").read()
    print("[refresh WARN] GitHub unreachable (%s) - using bundled copy" % e)
exec(compile(src, "refresh_plugin.py", "exec"))
'@
$code | & $py - $url $local
```

Do not "simplify" these back to `python "${CLAUDE_SKILL_DIR}/scripts/refresh_plugin.py"` —
that reintroduces the can't-update-past-a-bug trap described above.

## After it finishes

**Fully restart Claude Code** — `/exit` (or Ctrl+C), then run `claude` again.
`/reload-plugins` refreshes existing skills, but NEW skills, commands, and hooks
added in the update may not register until a full restart. Tell the user this
explicitly; do not just say "run /reload-plugins".

## Safety

- Idempotent — running twice has no extra effect
- Preserves `installedAt` timestamp across refreshes
- Doesn't delete old cache versions (they're harmless, just unused)
- Exits non-zero with a clear error if anything fails
- The remote script comes only from this repo's `master` branch over HTTPS

## Bootstrap on a fresh machine (no plugin installed yet)

The script also handles the no-marketplace case by git-cloning the
repo from `https://github.com/Kgan01/ghengis-skills.git`. So you can
run it on a brand-new machine with zero Claude Code plugin state.

If you can't invoke this skill (because the plugin isn't installed),
use the standalone one-liner for your shell:

PowerShell:

```powershell
irm https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py | python -
```

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py | python3
```

Then fully restart Claude Code.
