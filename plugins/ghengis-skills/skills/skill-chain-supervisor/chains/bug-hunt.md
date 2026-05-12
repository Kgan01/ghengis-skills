---
name: bug-hunt
pattern: sequential
triggers:
  - event: user_request
    keywords: ["bug-hunt", "fix this bug", "find this bug", "this is broken", "track down a bug", "debug this thoroughly", "run bug-hunt"]
on_error: fail_fast
estimated_duration: 5-45 minutes
---

## Purpose

Canonical pipeline for fixing a bug responsibly. Forces root-cause analysis before any code change, writes a regression test before the fix, and validates the fix via build-validate so the bug doesn't quietly come back.

## When To Use

- "Test X is failing"
- "Production is reporting Y error"
- "Why is this returning the wrong value"
- "It works locally but not in CI"
- Any unexpected behavior in code that previously worked

## When NOT To Use

- Building something new — use `feature-build` chain
- Refactoring without a known bug — that's a design task, not a debug task
- Performance optimization without a specific regression — that's design + benchmarking
- One-line obvious typos — just fix them

## Continuous Execution Principle

Drive through phases. Don't pause to ask "should I keep debugging?" after every probe. The user can interrupt if they want to redirect. The systematic-debugging skill itself has the natural decision point ("hypothesis confirmed / wrong, loop back").

## Input Contract

```json
{
  "input": {
    "user_request": "<the bug report — symptoms, repro steps if any, observed behavior>",
    "project_root": "<absolute path>",
    "error_messages": "<optional: stack traces, log excerpts>"
  }
}
```

## Stages

### 1. systematic_debugging
- **Skill:** `ghengis-skills:systematic-debugging`
- **Reads:** `input.user_request`, `input.error_messages`, project files
- **Writes:**
  - `systematic_debugging.reproduction_confirmed` (bool — can we trigger the bug deterministically?)
  - `systematic_debugging.root_cause` (one-sentence statement)
  - `systematic_debugging.root_cause_evidence` (what experiment confirmed it)
  - `systematic_debugging.affected_files` (list)
- **Success:** root cause stated in one sentence, with no hedging, AND a confirming experiment was run
- **On fail:** can't reproduce — exit chain with `outcome: cannot-reproduce`; user should gather more data. The chain refuses to skip this stage — that's the iron law.

### 2. test_driven_development (regression test mode)
- **Skill:** `ghengis-skills:test-driven-development`
- **Reads:** `systematic_debugging.root_cause`, `systematic_debugging.affected_files`
- **Writes:**
  - `test_driven_development.regression_test_file` (path)
  - `test_driven_development.red_confirmed` (bool — test fails for the same reason the user reported)
  - `test_driven_development.green_after_fix` (bool — test passes after stage 3 fix)
- **Success:** `red_confirmed = true` AND eventually `green_after_fix = true` (after stage 3)
- **On fail:** test fails for a different reason — investigation isn't done; loop back to systematic_debugging

### 3. build_validate (fix + verify, nested chain)
- **Chain:** `build-validate`
- **Nested chain output:** namespaced under `build_validate.*` per supervisor SKILL.md "Nested Chain" pattern.
- **Reads:** entire scratchpad
- **Builder writes:** the fix
- **Validator MUST verify:**
  - The regression test from stage 2 now passes (Validator updates `test_driven_development.green_after_fix = true`)
  - The full test suite still passes (no other regressions)
  - The fix addresses root cause, not symptom (check the change against `systematic_debugging.root_cause`)
- **Success:** `build_validate.report.outcome` in {"shipped", "shipped-with-notes", "revised-and-shipped"} AND `test_driven_development.green_after_fix = true`

### 4. report
- **Not a skill** — supervisor writes summary
- **Reads:** entire scratchpad
- **Writes:**
  - `report.outcome` ("fixed" | "fixed-with-notes" | "fix-incomplete")
  - `report.root_cause_summary`
  - `report.regression_test_added` (path)
  - `report.suggest_documenting` (bool — did we learn something non-obvious that should go in CLAUDE.md or a skill?)

## Special Handling

**"It's a one-liner, can we skip debugging?"** — No. The iron law of systematic-debugging says no fixes without root cause. The chain refuses to skip stage 1.

**"The test framework doesn't exist"** — TDD stage will skip with warning recorded. Document the gap so a future cycle can fix it.

**"Root cause is a design problem, not a code defect"** — Exit chain at stage 1 with `outcome: needs-redesign`; user should invoke `feature-build` instead.

## Failure Modes

| Stage | Failure | Recovery |
|---|---|---|
| systematic-debugging | Can't reproduce | Exit `cannot-reproduce`; ask user for more repro data |
| systematic-debugging | Root cause is design problem | Exit `needs-redesign`; suggest `feature-build` chain |
| TDD regression test | Test fails for different reason than user's bug | Loop back to debugging — root cause was wrong |
| build-validate | Fix passes regression test but breaks other tests | Validator flags; Builder revises; or fix is genuinely incompatible with existing behavior (signal design conflict) |
| build-validate | Score < 7 after 2 iterations | Outcome `fix-incomplete`; surface gaps to user |

## Example Scratchpad (After Successful Run)

```json
{
  "chain": "bug-hunt",
  "stages_completed": ["systematic_debugging", "test_driven_development", "build_validate", "report"],
  "input": {
    "user_request": "BankingGuard accepts 1e-5 as valid amount; should reject"
  },
  "systematic_debugging": {
    "reproduction_confirmed": true,
    "root_cause": "str(amount) returns '1e-05' for 0.00001, which has no '.', so the decimal-place check at line 462 doesn't trigger",
    "root_cause_evidence": "Probe: str(1e-5)='1e-5', no dot, current check returns False",
    "affected_files": ["apps/server/banking_guard.py"]
  },
  "test_driven_development": {
    "regression_test_file": "tests/test_banking_guard.py::test_amount_scientific_notation_blocked",
    "red_confirmed": true,
    "green_after_fix": true
  },
  "build_validate": {
    "triage": {"proceed": true, "reason": "Security-sensitive code, has clear functional test"},
    "build": {"iteration": 2, "summary": "Decimal-based validation; regex pre-check for string inputs"},
    "validate": {"score": 9, "functional_test_run": true, "issues": []},
    "report": {"outcome": "revised-and-shipped", "score_progression": [8, 9]}
  },
  "report": {
    "outcome": "fixed",
    "root_cause_summary": "String-based decimal check missed scientific notation; replaced with Decimal-based validation",
    "regression_test_added": "tests/test_banking_guard.py",
    "suggest_documenting": false
  }
}
```
