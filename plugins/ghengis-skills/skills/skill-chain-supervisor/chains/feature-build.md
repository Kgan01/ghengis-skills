---
name: feature-build
pattern: sequential
triggers:
  - event: user_request
    keywords: ["build a feature", "feature-build", "let's build", "add this feature", "implement this", "run feature-build"]
on_error: fail_fast
estimated_duration: 5-30 minutes
---

## Purpose

Canonical pipeline for shipping a new feature. Aligns intent through brainstorming, writes tests first via TDD, validates implementation via the build-validate chain (which has its own internal revision loop).

Replaces the loose "let me brainstorm and then code it" pattern with supervised stages that share state through the scratchpad.

## When To Use

- User says "let's build X", "add a feature to do Y"
- Non-trivial work that benefits from explicit design before implementation
- Code that ships (not throwaway prototypes — those can skip the chain)

## When NOT To Use

- Bug fixes — use `bug-hunt` chain instead (starts with systematic-debugging)
- One-line edits — just do them
- New skills — use `skill-port` chain
- Pure research / questions — answer directly

## Continuous Execution Principle

This chain runs end-to-end without pausing to ask "should I continue?" between stages. Stages have natural decision points built into them (brainstorming asks design questions; build-validate has the revision loop). Outside those, drive forward. The user can interrupt at any moment if they want to redirect.

## Input Contract

Scratchpad keys expected at chain start:

```json
{
  "input": {
    "user_request": "<what the user wants built>",
    "project_root": "<absolute path>",
    "preferred_execution_mode": "<inline | subagent | build-validate>  (set during brainstorming stage 3)"
  }
}
```

## Stages

### 1. brainstorming
- **Skill:** `ghengis-skills:brainstorming`
- **Reads:** `input.user_request`, project context (filesystem)
- **Writes:** `brainstorming.design_summary` (string), `brainstorming.execution_mode` ("inline" | "subagent" | "build-validate"), `brainstorming.scope_decomposed` (bool — true if the request was broken into sub-projects)
- **Success:** user has approved a design AND picked an execution mode
- **On fail:** user declined or scope was too broad to handle in one chain — exit chain with `outcome: needs-decomposition`

### 2. test-driven-development
- **Skill:** `ghengis-skills:test-driven-development`
- **Reads:** `brainstorming.design_summary`, `input.project_root`
- **Writes:** `tdd.test_files` (list of test file paths created), `tdd.red_confirmed` (bool — did we watch the test fail?), `tdd.green_confirmed` (bool — does it now pass?)
- **Success:** `red_confirmed = true` AND `green_confirmed = true`
- **On fail:** user opted out of TDD ("just build it") — skip to stage 3 with warning recorded in `tdd.skip_reason`

### 3. build-validate (nested chain)
- **Chain:** `build-validate`
- **Reads:** entire scratchpad
- **Writes:** `build_validate.score` (int 0-10), `build_validate.outcome` ("shipped" | "shipped-with-notes" | "revised-and-shipped" | "quality-gap-flagged"), `build_validate.iterations_used` (int)
- **Special handling:** if `brainstorming.execution_mode == "inline"`, skip the build-validate chain and let Claude implement inline with the user watching. If `"subagent"`, dispatch a Builder subagent but skip the Validator stage. If `"build-validate"`, run the full chain.
- **Success:** `score >= 7`
- **On fail:** propagate the quality gap to the report stage

### 4. report
- **Not a skill** — supervisor writes the final summary
- **Reads:** entire scratchpad
- **Writes:** `report.outcome` ("shipped" | "shipped-with-notes" | "quality-gap-flagged"), `report.tests_added` (int), `report.files_touched` (list), `report.next_step_suggestion` (string — usually "run finish-line chain to integrate")
- **Recommends:** invoking the `finish-line` chain to verify tests, merge/PR, and update docs

## Failure Modes

| Stage | Failure | Recovery |
|---|---|---|
| brainstorming | User can't decide / keeps changing scope | Pause, ask user to commit; if they can't, exit chain (this isn't ready to build) |
| brainstorming | Scope is multi-subsystem | Exit with `needs-decomposition`; user should rerun chain on one sub-project |
| TDD | User refuses to write tests first | Skip TDD with warning; record `tdd.skip_reason` in scratchpad |
| build-validate | Score stays < 7 after 2 iterations | Outcome becomes `quality-gap-flagged`; do NOT silently ship |
| report | — | This stage doesn't fail; it surfaces what happened |

## Example Scratchpad (After Successful Run)

```json
{
  "chain": "feature-build",
  "started_at": "2026-05-12T00:30:00Z",
  "completed_at": "2026-05-12T00:55:00Z",
  "stages_completed": ["brainstorming", "tdd", "build-validate", "report"],
  "input": {
    "user_request": "Add a /health endpoint that returns DB connectivity status",
    "project_root": "/Users/kgan/code/foo-service"
  },
  "brainstorming": {
    "design_summary": "GET /health → JSON {status: ok|degraded|down, db: <bool>, ts: <iso>}. Use existing db.ping() helper.",
    "execution_mode": "build-validate",
    "scope_decomposed": false
  },
  "tdd": {
    "test_files": ["tests/test_health.py"],
    "red_confirmed": true,
    "green_confirmed": true
  },
  "build_validate": {
    "score": 9,
    "outcome": "shipped",
    "iterations_used": 1
  },
  "report": {
    "outcome": "shipped",
    "tests_added": 3,
    "files_touched": ["src/routes/health.py", "tests/test_health.py"],
    "next_step_suggestion": "Run finish-line chain to integrate"
  }
}
```
