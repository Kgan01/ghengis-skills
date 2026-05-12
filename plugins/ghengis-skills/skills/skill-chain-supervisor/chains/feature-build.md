---
name: feature-build
pattern: sequential
triggers:
  - event: user_request
    keywords: ["build a feature", "feature-build", "let's build a feature", "add a new feature", "implement a feature", "run feature-build"]
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
- User has chosen the **build-validate execution mode** in brainstorming. The chain is purpose-built for the high-rigor path. If brainstorming returns `execution_mode = "inline"` or `"subagent"`, the chain exits at stage 1 with `outcome: design-only-handoff` — the design is the deliverable and the user implements outside the chain.

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

### 2. test_driven_development
- **Skill:** `ghengis-skills:test-driven-development`
- **Reads:** `brainstorming.design_summary`, `input.project_root`
- **Writes:** `test_driven_development.test_files` (list of test file paths created), `test_driven_development.red_confirmed` (bool — did we watch the test fail?), `test_driven_development.green_confirmed` (bool — does it now pass?)
- **Success:** `red_confirmed = true` AND `green_confirmed = true`
- **On fail:** user opted out of TDD ("just build it") — skip to stage 3 with warning recorded in `test_driven_development.skip_reason`

### 3. build_validate (nested chain)
- **Chain:** `build-validate`
- **Nested chain output:** namespaced under `build_validate.*` per supervisor SKILL.md "Nested Chain" pattern. Parent reads `build_validate.report.outcome`, `build_validate.report.score_progression`, etc.
- **Reads:** entire scratchpad
- **The chain itself produces:** `build_validate.triage`, `build_validate.build`, `build_validate.validate`, `build_validate.report` (full structure of the nested chain's scratchpad)
- **Success:** `build_validate.report.outcome` in {"shipped", "shipped-with-notes", "revised-and-shipped"}
- **On fail:** `build_validate.report.outcome == "quality-gap-flagged"` — propagate the quality gap to the parent report stage

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
| test_driven_development | User refuses to write tests first | Skip TDD with warning; record `test_driven_development.skip_reason` in scratchpad |
| build-validate | Score stays < 7 after 2 iterations | Outcome becomes `quality-gap-flagged`; do NOT silently ship |
| report | — | This stage doesn't fail; it surfaces what happened |

## Example Scratchpad (After Successful Run)

```json
{
  "chain": "feature-build",
  "started_at": "2026-05-12T00:30:00Z",
  "completed_at": "2026-05-12T00:55:00Z",
  "stages_completed": ["brainstorming", "test_driven_development", "build_validate", "report"],
  "input": {
    "user_request": "Add a /health endpoint that returns DB connectivity status",
    "project_root": "/Users/kgan/code/foo-service"
  },
  "brainstorming": {
    "design_summary": "GET /health → JSON {status: ok|degraded|down, db: <bool>, ts: <iso>}. Use existing db.ping() helper.",
    "execution_mode": "build-validate",
    "scope_decomposed": false
  },
  "test_driven_development": {
    "test_files": ["tests/test_health.py"],
    "red_confirmed": true,
    "green_confirmed": true
  },
  "build_validate": {
    "triage": {"proceed": true, "reason": "Real deliverable with functional test"},
    "build": {"iteration": 1, "summary": "Added /health route + 3 tests"},
    "validate": {"score": 9, "functional_test_run": true, "issues": []},
    "report": {"outcome": "shipped", "score_progression": [9]}
  },
  "report": {
    "outcome": "shipped",
    "tests_added": 3,
    "files_touched": ["src/routes/health.py", "tests/test_health.py"],
    "next_step_suggestion": "Run finish-line chain to integrate"
  }
}
```
