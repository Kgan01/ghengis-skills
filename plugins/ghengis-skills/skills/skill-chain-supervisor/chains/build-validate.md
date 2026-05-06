---
name: build-validate
pattern: loop
triggers:
  - event: user_request
    keywords: ["build and validate", "build-validate", "with validation", "ping-pong this", "round-trip", "validate thoroughly"]
on_error: fail_fast
estimated_duration: 1-5 minutes
loop:
  max_iterations: 2
  until: "validate.score >= 7"
---

## Purpose

Enforces the oort-cascade Builder ↔ Validator loop as a hard gate. Builder produces the deliverable, Validator functionally tests it (not just reads), and if the score is too low the issues bounce back to Builder for one revision pass. Caps at 2 round-trips so the loop terminates.

This is the minimum-viable cascade — exactly two roles going back and forth — promoted from "recipe in SKILL.md" to "supervised stages with shared state."

## When to Use

- Deliverable matters enough to justify a validation pass (production code, client work, anything that ships)
- A single focused pass *might* be wrong in ways the builder can't see in their own work
- User explicitly invokes: "run build-validate", "ping-pong this", "validate thoroughly"

## When NOT to Use

- Trivial single-step tasks (one grep, one config tweak, one-line fix) — the triage stage will skip these
- Pure research / lookup tasks with no artifact to validate — use a different chain
- Throwaway drafts where speed beats quality — overhead isn't worth it

## Input Contract

Scratchpad keys expected at chain start:

```json
{
  "input": {
    "user_request": "<what the user asked>",
    "deliverable_type": "<code | document | config | design | other>",
    "scope_notes": "<optional: known constraints or files in scope>"
  }
}
```

## Stages

### 1. triage
- **Skill:** none — Claude evaluates directly
- **Reads:** `input.user_request`, `input.deliverable_type`
- **Writes:** `triage.proceed` (bool), `triage.reason` (string)
- **Decision rules:**
  - `proceed = false` if the task is a single-step lookup, sub-2-minute edit, or has no testable artifact
  - `proceed = true` otherwise
- **On `proceed = false`:** exit chain immediately, report "task too small for build-validate, handling directly"
- **On `proceed = true`:** continue to build stage

### 2. build (loop body)
- **Skill:** none — Claude (or a dispatched Builder subagent) produces the deliverable
- **Reads:** `input.user_request`, `input.scope_notes`, on iteration 2 also `validate.issues`, `validate.feedback`
- **Writes:** `build.artifacts` (list of file paths or content blocks), `build.summary` (what was built/changed), `build.iteration` (1 or 2)
- **On iteration 2:** Builder MUST address every item in `validate.issues` from the previous pass. The summary should map fixes → issues.

### 3. validate (loop body)
- **Not a skill** — dispatch the `ghengis-skills:validator` subagent via the Agent tool, following the pattern used by `agent-dispatch.md` stage 3 (`execution`)
- **Reads:** `input.user_request`, `build.artifacts`, `build.summary`
- **Writes:**
  - `validate.score` (int 0-10, average of dimensions)
  - `validate.dimensions` `{accuracy, completeness, quality, format}` each 0-10
  - `validate.issues` (list, each with file:line or section reference)
  - `validate.revision_needed` (bool)
  - `validate.feedback` (string — single most-impactful fix)
  - `validate.functional_test_run` (bool — was code executed / endpoint hit / UI clicked)
- **Validator prompt MUST instruct:** "Your job is to BREAK this, not approve it. Run code if there is code. Test it functionally. Score what works, not what looks right."
- **Success:** `score >= 7`
- **On `score < 7` and `iteration < 2`:** loop back to build stage with issues + feedback

### 4. report
- **Skill:** none — chain summary written by supervisor
- **Reads:** entire scratchpad
- **Writes:** `report.outcome` ("shipped" | "shipped-with-notes" | "revised-and-shipped" | "quality-gap-flagged")
- **Outcome rules:**
  - `score >= 9` after iteration 1 → `shipped`
  - `score 7-8` after iteration 1 → `shipped-with-notes`
  - `score >= 7` after iteration 2 → `revised-and-shipped` (include score progression)
  - `score < 7` after iteration 2 → `quality-gap-flagged` (deliver anyway, but warn user explicitly)

## Loop Control

The frontmatter `loop:` block is authoritative. Per `SKILL.md` lines 128-134, the supervisor's `pattern: loop` schema accepts exactly two fields: `max_iterations` (the cap) and `until` (the success condition). This chain uses:

- `max_iterations: 2` — hard cap; supervisor terminates the loop after 2 build+validate cycles regardless of score
- `until: "validate.score >= 7"` — success condition; satisfied after iteration 1 → exit early

**Loop body:** stages `build` and `validate` (in that order) repeat together. Each iteration runs both stages.

**On cap reached without success** (iterations == 2 AND `validate.score < 7`): the supervisor proceeds to the `report` stage, which writes `outcome: quality-gap-flagged`. The deliverable is NOT silently shipped — the user sees the gap.

The supervisor enforces the cap. The validator cannot extend it. The builder cannot skip the validator.

## Failure Modes

| Stage | Failure | Recovery |
|-------|---------|----------|
| triage | Ambiguous — can't tell if task is trivial | Default to `proceed = true` (overhead is cheaper than missed validation) |
| build | Builder produces no artifact | Stop chain, report "no deliverable to validate" |
| validate | Validator skips functional test | `functional_test_run = false` → reduce score ceiling to 6, force iteration 2 |
| validate | Validator scores 9-10 with no issues listed | Likely rubber-stamp — flag and surface validator's reasoning to user |
| loop | Score doesn't improve between iterations | Accept and flag — fundamental approach problem, surfacing it beats infinite loops |

## Anti-Patterns This Prevents

- **"Builder rates own work"** — separate validator context with skeptical prompt
- **"Validator reads but doesn't test"** — `functional_test_run` is a tracked field
- **"Endless revision spiral"** — hard cap at 2 iterations
- **"Silent quality gap"** — `quality-gap-flagged` outcome forces an explicit warning
- **"Trivial task got cascaded"** — triage stage exits early for sub-2-minute work

## Example Scratchpad (After Iteration 2)

```json
{
  "chain": "build-validate",
  "started_at": "2026-05-05T21:40:00Z",
  "current_stage": "report",
  "stages_completed": ["triage", "build:1", "validate:1", "build:2", "validate:2"],
  "iteration": 2,
  "input": {
    "user_request": "Add JWT refresh endpoint",
    "deliverable_type": "code"
  },
  "triage": {
    "proceed": true,
    "reason": "auth code, security-sensitive, needs functional test"
  },
  "build": {
    "iteration": 2,
    "artifacts": ["auth/refresh.ts", "auth/__tests__/refresh.test.ts"],
    "summary": "Added POST /auth/refresh; rotates refresh token; rejects expired tokens. Iter 2 fix: added rate-limit per validator issue #1."
  },
  "validate": {
    "score": 8,
    "dimensions": {"accuracy": 9, "completeness": 8, "quality": 8, "format": 8},
    "issues": ["minor: error message leaks token expiry timestamp (refresh.ts:42)"],
    "revision_needed": false,
    "feedback": "Generic error message would close the timing-leak nit",
    "functional_test_run": true
  },
  "report": {
    "outcome": "revised-and-shipped",
    "score_progression": [5, 8]
  }
}
```

## Relationship to Other Chains

- **agent-dispatch** wraps a single subagent dispatch with PQL + completion + hallucination checks. **build-validate** wraps a deliverable with a revision loop. They compose: you can dispatch a Builder via `agent-dispatch` and then validate the result via `build-validate`.
- **task-complete** runs after work is done to verify + record + learn. **build-validate** runs *during* the work to enforce the round-trip. Use both for high-stakes deliverables.
