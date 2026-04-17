---
name: auto-project-sync
description: Use after completing a major work batch (plan execution, feature build, multi-task subagent run) to update CLAUDE.md, MEMORY.md, project indexes, documentation, and propagate new permissions to global settings. Captures lessons learned, marks completed plans, ratchets reusable permissions across all projects, and keeps project DNS in sync with reality.
allowed-tools: Read Write Edit Glob Grep Bash
---

# Auto Project Sync

Update project documentation after a significant work batch completes, so the next session starts with current context. The "project DNS keeps drifting from the code" problem — solved.

## When to Invoke

**Mandatory triggers:**
- After `superpowers:subagent-driven-development` finishes all tasks
- After `superpowers:finishing-a-development-branch` is invoked
- When user types `/sync` slash command
- When SessionEnd hook detects unsynced commits beyond threshold (5+ commits since last sync)

**Optional triggers:**
- After major architectural changes
- After a plan is fully executed
- After resolving uncertainties from a research phase

**Do NOT invoke:**
- Mid-task (creates noise, sync should be terminal)
- After trivial commits (typo fixes, formatting)
- Inside a subagent (subagents skip per `<SUBAGENT-STOP>`)

## What Sync Updates

| File | What Changes |
|---|---|
| **CLAUDE.md** | Active phase, recent decisions, current focus, agent count if changed |
| **MEMORY.md** | New feedback/preferences captured this session, lessons learned |
| **CONTEXT.md** | Workspace routing if new modules added |
| **docs/superpowers/specs/INDEX.md** | List of specs with status (draft/approved/implemented) |
| **docs/superpowers/plans/INDEX.md** | List of plans with completion status (% tasks done) |
| **README.md** | Top-level project description if scope changed |
| **~/.claude/settings.json** | New reusable permissions promoted from project-local to global (permission ratchet) |
| **.claude/last_sync** | Timestamp of this sync (used by hooks for threshold checks) |

## Workflow

### Step 1: Detect Changes Since Last Sync

```bash
LAST_SYNC=$(cat .claude/last_sync 2>/dev/null || echo "1970-01-01")
NEW_COMMITS=$(git log --since="$LAST_SYNC" --oneline | wc -l)
CHANGED_FILES=$(git log --since="$LAST_SYNC" --name-only --pretty=format: | sort -u | grep -v '^$')
```

If `NEW_COMMITS == 0`, exit early — nothing to sync.

### Step 2: Categorize Changes

For each commit since last sync, classify by conventional commit prefix:
- `feat:` → new feature added
- `fix:` → bug fix
- `docs:` → documentation update
- `chore:` → maintenance
- `refactor:` → code restructure
- `test:` → test additions

Build summary:
```
Since last sync (2026-04-15):
  - 18 features added (modules: outreach, state_local, gsa_application, analytics, documents)
  - 3 bug fixes
  - 5 doc updates
  - 0 refactors
```

### Step 3: Read Existing Doc State

Read current versions:
- `CLAUDE.md`
- `MEMORY.md`
- `CONTEXT.md` (if exists)
- `docs/superpowers/specs/` (list)
- `docs/superpowers/plans/` (list)

### Step 4: Update Each Doc

**CLAUDE.md updates:**
- Update "Active Phase" line to current phase
- Update agent/module count if changed
- Add recent significant decisions to "Recent Decisions" section (cap at last 10)
- Update last-modified timestamp

**MEMORY.md updates:**
- Append any new feedback/preferences captured during the work batch
- Maintain the index format (one-line entries pointing to memory files)
- Don't duplicate existing entries

**Spec/Plan indexes:**
- Scan `docs/superpowers/specs/*.md` and `docs/superpowers/plans/*.md`
- Generate or update `INDEX.md` in each directory with:
  - File name, title, status, date
  - For plans: % tasks completed (count `- [x]` vs `- [ ]`)

**CONTEXT.md updates:**
- If new top-level modules added, update workspace routing table

### Step 4.5: Sync Permissions to Global Settings (Permission Ratchet)

Propagate reusable permissions from this project's `.claude/settings.local.json` to the global `~/.claude/settings.json` so they apply across ALL projects. Over time, the user gets fewer and fewer approval prompts.

**Process:**

1. Read `<project>/.claude/settings.local.json` → `permissions.allow` list
2. Read `~/.claude/settings.json` → `permissions.allow` and `permissions.deny` lists
3. Filter project-local allows to ONLY reusable patterns:
   - Keep: entries with wildcards (`*`) — e.g., `Bash(brew install *)`, `WebFetch(domain:arxiv.org)`
   - Keep: tool-level allows — e.g., `Read`, `Edit`, `Write`, `WebSearch`
   - Keep: domain-scoped WebFetch — e.g., `WebFetch(domain:docs.anthropic.com)`
   - **Skip**: exact one-off commands (no `*`, long paths, specific filenames) — these are session artifacts, not reusable patterns
   - **Skip**: anything already in the global allow list (dedup)
   - **Skip**: anything in the global deny list (deny list is immutable)
4. If new reusable permissions found:
   - Show the user what will be added: "Promoting N permissions to global settings: [list]"
   - Add to `~/.claude/settings.json` `permissions.allow`
   - NEVER touch `permissions.deny` — the deny list from `setup` is permanent
5. If nothing to promote, skip silently

**Filter heuristic (what counts as "reusable"):**

Broad strokes: accept anything with a wildcard unless it's pinned to an exact home-directory file. Generalize project-specific names (venvs, dated paths) so one approval covers similar future patterns.

```python
import re

def generalize(perm: str) -> str:
    """Rewrite project-specific tokens into patterns so one allow covers future siblings."""
    # venv_kronos, venv_weather, env_myproject -> venv*, env*
    perm = re.sub(r"\b(venv|env)_[A-Za-z0-9_-]+", r"\1_*", perm)
    # Date-stamped paths: 2026-04-17 -> *
    perm = re.sub(r"\b20\d{2}-\d{2}-\d{2}\b", "*", perm)
    # Specific python version pinning: python@3.13/3.13.7 -> python@*/**
    perm = re.sub(r"python@\d+\.\d+/\d+\.\d+\.\d+", "python@*", perm)
    return perm

def is_reusable_permission(perm: str) -> bool:
    # Tool-level allows are always reusable
    if perm in ("Read", "Edit", "Write", "WebSearch", "WebFetch"):
        return True
    # Domain-scoped WebFetch is always reusable
    if perm.startswith("WebFetch(domain:"):
        return True
    # No wildcard = one-off exact command, skip
    if "*" not in perm:
        return False
    # Wildcard patterns are reusable UNLESS they pin to a home-specific file
    # (broad paths like /Users/**/Library/** or /usr/local/** are still useful)
    if re.search(r"/Users/[^/*]+/(Desktop|Documents|Downloads)/[^/*]+/[^*]*\.", perm):
        return False  # e.g. /Users/kae/Desktop/project/specific-file.txt
    if "/private/tmp" in perm or "/tmp/" in perm:
        return False
    return True
```

Run every candidate through `generalize()` before `is_reusable_permission()` so promoted entries cover similar future paths. Dedup against the global allow list after generalization to avoid duplicate patterns.

**Why this matters:** After 10 sessions, the user's global allow list has grown organically from their actual usage. New projects start with all the permissions they've ever found useful. The deny list never shrinks — dangerous operations always require confirmation.

### Step 5: Capture Lessons Learned (Optional but Recommended)

Scan recent commits and conversation context for:
- Repeated mistakes the user corrected → save as feedback memory
- Decisions made under specific constraints → save as project memory
- New tools/patterns discovered → save as user memory if pattern, reference memory if external

Use the user's existing memory system at `memory/` directory. Don't create duplicates.

### Step 6: Write Sync Marker

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > .claude/last_sync
```

### Step 7: Brief Summary to User

Output a 3-5 line summary:
> "Synced project state. Updated CLAUDE.md (active phase → Phase 2 execution), MEMORY.md (added 2 lessons learned), plan index (Phase 1 marked 100% complete, Phase 2 plans drafted). Next session will see current state."

## Anti-Patterns

| Don't | Why |
|---|---|
| Rewrite CLAUDE.md from scratch | Loses user customizations and history |
| Add commit details into CLAUDE.md | That's what `git log` is for |
| Create new files unprompted | Sync updates existing structure, doesn't expand scope |
| Run sync mid-task | Creates noise; sync is a terminal action |
| Sync without checking last_sync timestamp | Wastes effort if nothing changed |
| Modify spec/plan content | Only the INDEX is auto-generated; specs/plans are source of truth |

## Hook Integration

### SessionEnd Hook (Light Detection)

Runs at session end. Doesn't perform full sync — just writes a marker if changes pending:

```bash
#!/usr/bin/env bash
# .claude/hooks/session-end-sync-check.sh
LAST_SYNC=$(cat .claude/last_sync 2>/dev/null || echo "1970-01-01")
NEW_COMMITS=$(git log --since="$LAST_SYNC" --oneline 2>/dev/null | wc -l)
if [ "$NEW_COMMITS" -ge 5 ]; then
    echo "Auto-sync recommended: $NEW_COMMITS commits since last sync" > .claude/pending_sync.md
fi
```

### SessionStart Hook (Suggest Sync)

Runs at session start. If pending_sync exists, surface it:

```bash
#!/usr/bin/env bash
# .claude/hooks/session-start-sync-prompt.sh
if [ -f .claude/pending_sync.md ]; then
    cat .claude/pending_sync.md
    echo "Run /sync to update project docs."
fi
```

## Manual Override

User can always run `/sync` to force a sync regardless of triggers or threshold.

## Coexistence

This skill complements (does not replace):
- `superpowers:finishing-a-development-branch` — handles git/PR workflow at branch completion
- `ghengis-skills:project-scaffold` — initial project structure (one-time)
- `ghengis-skills:agent-identity` — separate concern (user preferences)

Run this AFTER `finishing-a-development-branch` if both apply.
