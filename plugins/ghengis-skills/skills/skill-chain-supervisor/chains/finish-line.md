---
name: finish-line
pattern: sequential
triggers:
  - event: user_request
    keywords: ["finish-line", "ship it", "let's wrap this up", "ready to ship", "integrate this work", "run finish-line"]
on_error: fail_fast
estimated_duration: 2-15 minutes
---

## Purpose

Canonical pipeline for finishing a development branch responsibly. Verify tests, present integration options, execute the choice, then update documentation and audit logs so the next session knows what shipped.

## When To Use

- Implementation is complete and tests pass
- `feature-build` or `bug-hunt` or `skill-port` chain just ended with `shipped` / `revised-and-shipped`
- User says "let's wrap up", "ship it", "ready to integrate", "merge this"

## When NOT To Use

- Mid-implementation
- Tests are failing — fix them first
- Work that's been abandoned (use the `discard` option inside finishing-a-development-branch directly)

## Continuous Execution Principle

Drive through stages. The natural decision point is in stage 1 (which integration option). After that, the supervisor doesn't pause — it executes the choice, updates docs, records the audit entry, and reports.

## Input Contract

```json
{
  "input": {
    "user_request": "<optional context — e.g., 'ship the JWT refactor'>",
    "project_root": "<absolute path>",
    "base_branch": "<optional; defaults to detection via git merge-base>"
  }
}
```

## Stages

### 1. finishing-a-development-branch
- **Skill:** `ghengis-skills:finishing-a-development-branch`
- **Reads:** project filesystem, git state
- **Writes:**
  - `finishing.tests_passed` (bool — gate)
  - `finishing.workspace_state` ("normal-repo" | "worktree-named" | "worktree-detached")
  - `finishing.base_branch` (e.g. "main")
  - `finishing.option_chosen` (1 | 2 | 3 | 4)
  - `finishing.merge_sha` or `finishing.pr_url` (depending on option)
  - `finishing.branch_disposition` ("merged" | "pr-opened" | "kept-as-is" | "discarded")
- **Success:** chosen option executed cleanly
- **On fail:** tests don't pass → exit chain with `outcome: tests-failing`; user must fix before re-running

### 2. auto-project-sync (conditional)
- **Skill:** `ghengis-skills:auto-project-sync`
- **When:** `finishing.branch_disposition` is "merged" or "pr-opened" (skip if kept-as-is or discarded)
- **Reads:** entire scratchpad, project files (CLAUDE.md, MEMORY.md, indexes, docs)
- **Writes:**
  - `sync.claude_md_updated` (bool)
  - `sync.memory_md_updated` (bool)
  - `sync.indexes_refreshed` (list of files)
  - `sync.permissions_propagated` (list — any reusable Bash perms ratcheted to global settings)
  - `sync.lessons_captured` (list — entries written to skill memory or evolving-cognition)
- **Success:** docs reflect what just shipped
- **On fail:** non-blocking; record what couldn't be auto-synced and surface to user

### 3. audit-ledger
- **Skill:** `ghengis-skills:audit-ledger`
- **Reads:** entire scratchpad
- **Writes:**
  - `audit.entry_id` (unique id)
  - `audit.hash` (sha256 chain hash)
  - `audit.summary` (one line: what shipped, when, where)
- **Success:** entry appended to immutable log
- **On fail:** non-blocking; record but proceed (audit gaps shouldn't block shipping)

### 4. report
- **Not a skill** — supervisor writes final summary
- **Reads:** entire scratchpad
- **Writes:**
  - `report.outcome` ("integrated" | "integrated-with-notes" | "kept-as-is" | "discarded")
  - `report.what_shipped` (one paragraph)
  - `report.pr_url` (if option 2)
  - `report.next_session_hint` (what the next session should know about this)

## Failure Modes

| Stage | Failure | Recovery |
|---|---|---|
| finishing | Tests failing | Exit `tests-failing`; do NOT proceed to docs/audit (would lie about what shipped) |
| finishing | Force push to main attempted | Refuse hard; require manual confirmation or different option |
| finishing | Discard chosen without explicit "yes discard" | Refuse; require unambiguous consent |
| auto-project-sync | CLAUDE.md update conflicts with manual edits | Non-blocking; record conflict, ask user later |
| audit-ledger | Hash chain check fails | Surface immediately; this is a tamper signal |

## Skip-Stage Rules

- **Option 3 "Keep as-is"**: skip stages 2 and 3 (nothing shipped to record)
- **Option 4 "Discard"**: skip stage 2 (nothing to document); DO write audit entry that the branch was discarded
- **No git remote configured**: option 2 (PR) is unavailable; menu adjusts automatically

## Example Scratchpad (After Successful Merge + Sync + Audit)

```json
{
  "chain": "finish-line",
  "stages_completed": ["finishing", "auto-project-sync", "audit-ledger", "report"],
  "input": {
    "user_request": "Ship the JWT refactor"
  },
  "finishing": {
    "tests_passed": true,
    "workspace_state": "normal-repo",
    "base_branch": "main",
    "option_chosen": 1,
    "merge_sha": "ab12c3d",
    "branch_disposition": "merged"
  },
  "sync": {
    "claude_md_updated": true,
    "memory_md_updated": true,
    "indexes_refreshed": ["docs/INDEX.md"],
    "permissions_propagated": [],
    "lessons_captured": ["JWT migration required handling existing session cookies during cutover"]
  },
  "audit": {
    "entry_id": "2026-05-12-7f3a",
    "hash": "sha256:abcd...",
    "summary": "Merged JWT auth refactor (ab12c3d) into main; 23 tests, all green"
  },
  "report": {
    "outcome": "integrated",
    "what_shipped": "JWT-based auth replacing session cookies; all 23 auth tests pass; CLAUDE.md auth section updated",
    "next_session_hint": "Watch for cookie-related session bugs in legacy frontend if not yet updated"
  }
}
```
