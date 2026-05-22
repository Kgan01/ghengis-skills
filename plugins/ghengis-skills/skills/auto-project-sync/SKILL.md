---
name: auto-project-sync
description: Use after completing a major work batch (plan execution, feature build, multi-task subagent run) to refresh code-graph-derived data in MEMORY.md/CONTEXT.md/SKILL_MEMORY, append dated narrative entries to TODO/CHANGELOG/lessons-learned, mine cross-project structural habits, and ratchet reusable permissions to global settings. Keeps project DNS in sync with reality.
allowed-tools: Read Write Edit Glob Grep Bash
---

# Auto Project Sync — The Umbrella

Refresh every memory artifact in the project after a significant work batch, so the next session starts with current context. Runs in 4 phases: discover what to update, refresh the mechanical (code-graph-derived) bits, append the narrative (human judgment) bits, and finally ratchet permissions to global. The "project DNS keeps drifting from the code" problem — solved.

## When to Invoke

**Mandatory triggers:**
- After `superpowers:subagent-driven-development` finishes all tasks
- After `superpowers:finishing-a-development-branch` is invoked
- When user types `/sync` slash command
- When SessionEnd hook detects unsynced commits beyond threshold (5+ commits since last sync)

**Do NOT invoke:**
- Mid-task (creates noise; sync is terminal)
- After trivial commits (typo fixes, formatting)
- Inside a subagent

## Phase 0 — Discovery (only on first run in a project)

If `.jarvis/memory-files.json` doesn't exist, create it by scanning the project. This file is the project's **memory file registry** — auto-project-sync consults it on every subsequent run to know which files to touch.

**Required entries** (always add if file present; create empty if missing):

| Path | Role | `auto_block` | `append_dated` |
|---|---|---|---|
| `MEMORY.md` | `project_dns` | true | false |
| `CONTEXT.md` | `routing` | true | false |
| `CLAUDE.md` | `instructions` | false | false |
| `TODO.md` or `docs/TODO.md` | `todo` | false | true |
| `CHANGELOG.md` | `changelog` | false | true |

**Discovered entries** (case-insensitive globs; add only what exists):

| Glob | Role | `append_dated` |
|---|---|---|
| `**/LESSONS*.md`, `**/NOTES*.md`, `**/PROBLEMS*.md`, `**/JOURNAL*.md` | `lessons` | true |
| `**/TODO*.md`, `**/BACKLOG*.md`, `**/PLANS*.md` (excluding `docs/plans/`) | `todo` | true |
| `**/CHANGELOG*.md` | `changelog` | true |
| `docs/plans/` (directory) | `plans_dir` | n/a |

**If `.jarvis/code-graph.json` is present**, also register a synthetic entry:
```json
{"path": "<skill_memory_root>", "role": "skill_memory_feed", "agent": "engineer"}
```
This tells Phase 1 to run `rationale_ingest` for the engineer agent.

**Registry file shape:**

```json
{
  "version": 1,
  "memory_files": [
    {"path": "MEMORY.md", "role": "project_dns", "auto_block": true},
    {"path": "CONTEXT.md", "role": "routing", "auto_block": true},
    {"path": "CLAUDE.md", "role": "instructions", "auto_block": false},
    {"path": "TODO.md", "role": "todo", "append_dated": true},
    {"path": "CHANGELOG.md", "role": "changelog", "append_dated": true},
    {"path": "docs/lessons-learned.md", "role": "lessons", "append_dated": true}
  ]
}
```

Once written, future runs skip discovery and just read this file.

## Phase 1 — Mechanical (deterministic, every run)

Run only if `.jarvis/code-graph.json` exists. If absent: **skip silently with one-line notice** (`"No code graph present — skipping mechanical refresh"`) and proceed to Phase 2. This skill does NOT require JARVIS to be installed.

Find the plugin runner once:
```bash
PLUGIN_DIR="$(dirname "$(dirname "$(readlink -f .)")")/plugins/ghengis-skills"
# Or use the absolute path of this skill's parent — see Hook Integration below.
RUNNER="$PLUGIN_DIR/scripts/code_graph/run.py"
```

Then iterate `memory_files`:

```bash
# For each entry with role == "project_dns":
python "$RUNNER" memory_map "$PROJECT_ROOT" "$PROJECT_ROOT/$ENTRY_PATH"

# For each entry with role == "routing":
python "$RUNNER" routing_table "$PROJECT_ROOT" "$PROJECT_ROOT/$ENTRY_PATH"

# For each entry with role == "skill_memory_feed":
python "$RUNNER" rationale_ingest "$PROJECT_ROOT" "$ENTRY_PATH" --agent "$ENTRY_AGENT"
```

Each invocation prints one JSON line. Parse `wrote_changes` / `new` / `count` and roll into the final summary. The mechanical step is idempotent — repeated runs only change MEMORY.md/CONTEXT.md when the graph actually changed.

## Phase 2 — Narrative (your judgment — Claude reasoning, dated appends only)

**Critical rule: never overwrite history. Always append. Always include a `[YYYY-MM-DD]` prefix.**

Read each entry in `memory_files` and act based on `role`:

### `role: project_dns` (MEMORY.md)
- Append a dated session-summary bullet **above** the `<!-- AUTO:project-map:start -->` marker (the hand-written section is everything before the AUTO block).
- Form: `- [YYYY-MM-DD] <one-line summary of what shifted this session>`
- If the file is empty (Phase 0 just created it), seed it with a `# <Project Name>` header and a `## Project Memory` section, then add your bullet, then leave a blank line for Phase 1 to drop the AUTO block.

### `role: routing` (CONTEXT.md)
- The AUTO block is owned by Phase 1. The hand-written section above it can hold workspace-specific routing intent. Append dated bullets there only when a new workspace was introduced this session.

### `role: instructions` (CLAUDE.md)
- Look for a `Last Updated:` line and bump it to today's date.
- Do NOT add session summaries here — CLAUDE.md is for *instructions*, not history.

### `role: todo`
- Append new items as `- [ ] [YYYY-MM-DD] <item>` to the end of the file (or under the appropriate section if the file has them).
- For items completed this session: find the existing `- [ ] [...] <item>` line and replace it with `- [x] [YYYY-MM-DD-completed] ~~<item>~~`. Never delete — strike through.

### `role: lessons`
- Append per session as:
  ```markdown
  ### [YYYY-MM-DD] <topic — 5-8 words>

  <2-4 sentences of takeaway>
  ```
- One block per distinct lesson, not one block per session.

### `role: changelog`
- Append per **batch** (one entry per sync run, multiple bullets):
  ```markdown
  ## [YYYY-MM-DD]
  - <change 1>
  - <change 2>
  ```
- If today's date already has a `## [YYYY-MM-DD]` heading, append bullets under it instead of starting a new section.

### `role: plans_dir`
- For each plan file referenced as completed this session (e.g., user said "shipped X plan" or all checkboxes in the plan are now `[x]`), append a single line at the file's end:
  ```markdown

  **Completed**: YYYY-MM-DD
  ```
- Skip plans that already have a `**Completed**:` line.

## Phase 3 — Cross-project (only if global registry exists)

If `~/.claude/code-graph/global.json` exists:

```bash
python "$RUNNER" learn_patterns "$HOME/.claude/code-graph/global.json" "$HOME/.claude/agent_identity"
```

This refreshes `~/.claude/agent_identity/code_patterns.json` with the user's structural habits across all registered projects. The `agent-identity` skill reads this file when suggesting where new code should go.

If the registry doesn't exist, **skip silently**. Don't create it — that's `analyze_codebase`'s job (or whatever tool the user uses to register projects).

## Phase 4 — Permissions ratchet (existing behavior — keep as-is)

Propagate reusable permissions from this project's `.claude/settings.local.json` to the global `~/.claude/settings.json` so they apply across ALL projects.

**Process:**

1. Read `<project>/.claude/settings.local.json` → `permissions.allow` list
2. Read `~/.claude/settings.json` → `permissions.allow` and `permissions.deny` lists
3. Filter project-local allows to ONLY reusable patterns:
   - Keep: entries with wildcards (`*`) — e.g., `Bash(brew install *)`, `WebFetch(domain:arxiv.org)`
   - Keep: tool-level allows — e.g., `Read`, `Edit`, `Write`, `WebSearch`
   - Keep: domain-scoped WebFetch — e.g., `WebFetch(domain:docs.anthropic.com)`
   - **Skip**: exact one-off commands (no `*`, long paths, specific filenames)
   - **Skip**: anything already in the global allow list (dedup)
   - **Skip**: anything in the global deny list (deny list is immutable)
4. If new reusable permissions found:
   - Show the user what will be added: "Promoting N permissions to global settings: [list]"
   - Add to `~/.claude/settings.json` `permissions.allow`
   - NEVER touch `permissions.deny`
5. If nothing to promote, skip silently

**Filter heuristic:**

```python
import re

def generalize(perm: str) -> str:
    """Rewrite project-specific tokens into patterns so one allow covers future siblings."""
    perm = re.sub(r"\b(venv|env)_[A-Za-z0-9_-]+", r"\1_*", perm)
    perm = re.sub(r"\b20\d{2}-\d{2}-\d{2}\b", "*", perm)
    perm = re.sub(r"python@\d+\.\d+/\d+\.\d+\.\d+", "python@*", perm)
    return perm

def is_reusable_permission(perm: str) -> bool:
    if perm in ("Read", "Edit", "Write", "WebSearch", "WebFetch"):
        return True
    if perm.startswith("WebFetch(domain:"):
        return True
    if "*" not in perm:
        return False
    if re.search(r"/Users/[^/*]+/(Desktop|Documents|Downloads)/[^/*]+/[^*]*\.", perm):
        return False
    if "/private/tmp" in perm or "/tmp/" in perm:
        return False
    return True
```

Run every candidate through `generalize()` before `is_reusable_permission()`. Dedup against the global allow list after generalization.

**Why this matters:** After N sessions, the user's global allow list grows organically from their actual usage. The deny list never shrinks — dangerous operations always require confirmation.

## Final step — Write sync marker + brief summary

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > .claude/last_sync
```

Output a 4-6 line summary:
> "Synced. MEMORY.md project-map refreshed (8 nodes added). CONTEXT.md routing table: 6 communities. TODO.md: 3 items closed, 2 added. lessons-learned.md: 1 new entry. SkillMemory engineer: 4 new HACK/FIXME bullets. Promoted 2 permissions to global."

## Degraded-mode behavior

If `.jarvis/code-graph.json` is missing, Phase 1 prints `"No code graph present — skipping mechanical refresh"` once, then Phase 2 still runs (narrative appends never require a graph). The skill is useful even without any code-graph tooling installed.

## Anti-Patterns

| Don't | Why |
|---|---|
| Rewrite MEMORY.md from scratch | Loses user customizations and history |
| Overwrite the AUTO block by hand | Phase 1 owns it — your changes go above it |
| Delete completed TODO items | Strike-through preserves the audit trail |
| Replace lessons-learned content | Always append new dated sections |
| Run sync mid-task | Sync is terminal |
| Skip Phase 0 on a project that has no `memory-files.json` | Phase 1 won't know what to touch |
| Touch `permissions.deny` in `~/.claude/settings.json` | Deny list is immutable by policy |

## Hook Integration

### SessionEnd Hook (Light Detection)

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
- `ghengis-skills:project-scaffold` — initial project structure + first-time `.jarvis/memory-files.json` (one-time)
- `ghengis-skills:agent-identity` — reads `~/.claude/agent_identity/code_patterns.json` written by Phase 3

Run this AFTER `finishing-a-development-branch` if both apply.
