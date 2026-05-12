---
name: finish-line
pattern: sequential
triggers:
  - event: user_request
    keywords: ["finish-line", "ship this branch", "wrap up and ship", "ready to integrate", "integrate this branch", "merge this branch", "run finish-line"]
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

### 1. finishing_a_development_branch
- **Skill:** `ghengis-skills:finishing-a-development-branch`
- **Reads:** project filesystem, git state
- **Writes:**
  - `finishing_a_development_branch.tests_passed` (bool — gate)
  - `finishing_a_development_branch.workspace_state` ("normal-repo" | "worktree-named" | "worktree-detached")
  - `finishing_a_development_branch.base_branch` (e.g. "main")
  - `finishing_a_development_branch.option_chosen` (1=merge | 2=pr | 3=keep | 4=discard)
  - `finishing_a_development_branch.merge_sha` or `finishing_a_development_branch.pr_url` (depending on option)
  - `finishing_a_development_branch.branch_disposition` ("merged" | "pr-opened" | "kept-as-is" | "discarded")
  - `finishing_a_development_branch.force_push_attempted` (bool — flag if user requested it; chain refuses)
- **Success:** chosen option executed cleanly
- **On fail:** tests don't pass → exit chain with `outcome: tests-failing`; user must fix before re-running

### 2. auto_project_sync (conditional, non-blocking)
- **Skill:** `ghengis-skills:auto-project-sync`
- **on_error:** `skip` (per-stage override; non-blocking per supervisor SKILL.md "Per-Stage on_error Override")
- **When:** `finishing_a_development_branch.branch_disposition` is "merged" or "pr-opened" (skip if kept-as-is or discarded)
- **Reads:** entire scratchpad, project files (CLAUDE.md, MEMORY.md, indexes, docs)
- **Writes:**
  - `auto_project_sync.claude_md_updated` (bool)
  - `auto_project_sync.memory_md_updated` (bool)
  - `auto_project_sync.indexes_refreshed` (list of files)
  - `auto_project_sync.permissions_propagated` (list — any reusable Bash perms ratcheted to global settings)
  - `auto_project_sync.lessons_captured` (list — entries written to skill memory or evolving-cognition)
- **Success:** docs reflect what just shipped
- **On fail:** record what couldn't be auto-synced and surface to user; proceed to stage 3

### 3. audit_ledger (non-blocking)
- **Skill:** `ghengis-skills:audit-ledger`
- **on_error:** `skip` (per-stage override; audit gaps shouldn't block shipping)
- **Reads:** entire scratchpad
- **Writes:**
  - `audit_ledger.entry_id` (unique id)
  - `audit_ledger.hash` (sha256 chain hash)
  - `audit_ledger.summary` (one line: what shipped, when, where)
- **Success:** entry appended to immutable log
- **On fail:** record but proceed

### 4. report
- **Not a skill** — supervisor writes final summary
- **Reads:** entire scratchpad
- **Writes:**
  - `report.outcome` ("integrated" | "integrated-with-notes" | "kept-as-is" | "discarded")
  - `report.what_shipped` (one paragraph)
  - `report.pr_url` (if option 2)
  - `report.next_session_hint` (what the next session should know about this)
- **Terminate chain via:** `python scripts/scratchpad.py finish` — this archives the scratchpad to `history/<chain>-<ts>.json` AND, if `GHENGIS_COGNITION=true`, emits a structured cognition entry to `cognition.jsonl` (see `evolving-cognition` skill for the schema). Cognition entries from `finish-line` runs are particularly valuable because they capture the WHOLE feature/bug cycle outcome, not just one chain's verdict.

## Failure Modes

| Stage | Failure | Recovery |
|---|---|---|
| finishing_a_development_branch | Tests failing | Exit `tests-failing`; do NOT proceed to docs/audit (would lie about what shipped) |
| finishing_a_development_branch | Force push to main attempted | Set `force_push_attempted=true`; refuse hard; require manual confirmation or different option |
| finishing_a_development_branch | Discard chosen without explicit "yes discard" | Refuse; require unambiguous consent |
| auto_project_sync | CLAUDE.md update conflicts with manual edits | Non-blocking (on_error: skip); record conflict, ask user later |
| audit_ledger | Hash chain check fails | Surface immediately; this is a tamper signal — still propagate because non-blocking but surface prominently |

## Skip-Stage Rules

- **Option 3 "Keep as-is"**: skip stages 2 and 3 (nothing shipped to record)
- **Option 4 "Discard"**: skip stage 2 (nothing to document); DO write audit entry that the branch was discarded
- **No git remote configured**: option 2 (PR) is unavailable; menu adjusts automatically

## Example Scratchpad (After Successful Merge + Sync + Audit)

```json
{
  "chain": "finish-line",
  "stages_completed": ["finishing_a_development_branch", "auto_project_sync", "audit_ledger", "report"],
  "input": {
    "user_request": "Ship the JWT refactor"
  },
  "finishing_a_development_branch": {
    "tests_passed": true,
    "workspace_state": "normal-repo",
    "base_branch": "main",
    "option_chosen": 1,
    "merge_sha": "ab12c3d",
    "branch_disposition": "merged",
    "force_push_attempted": false
  },
  "auto_project_sync": {
    "claude_md_updated": true,
    "memory_md_updated": true,
    "indexes_refreshed": ["docs/INDEX.md"],
    "permissions_propagated": [],
    "lessons_captured": ["JWT migration required handling existing session cookies during cutover"]
  },
  "audit_ledger": {
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
