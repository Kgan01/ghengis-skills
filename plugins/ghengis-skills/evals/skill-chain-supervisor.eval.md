# Skill Chain Supervisor — Evaluation

## TC-1: build-validate Chain Triggers on Real Deliverable

- **prompt:** "Run build-validate on the auth refactor. Replace session cookies with JWT in `apps/server/auth.py`. Make sure tests still pass."
- **context:** Real codebase task with testable deliverable (Python module + pytest suite). User explicitly invokes build-validate.
- **assertions:**
  - Triage stage runs first and sets `proceed = true` (real deliverable, has functional test)
  - Build stage produces an artifact and writes `build.summary` + `build.artifacts` to scratchpad
  - Validate stage dispatches `ghengis-skills:validator` subagent (NOT inline self-validation)
  - Validator's prompt instructs adversarial review ("BREAK this, not approve it")
  - Scratchpad records `validate.score`, `validate.issues`, `validate.functional_test_run`
- **passing_grade:** 4/5 assertions must pass

## TC-2: build-validate Triage Skips Trivial Tasks

- **prompt:** "Run build-validate to fix this typo: change 'recieve' to 'receive' in README.md line 42."
- **context:** Single-line edit, no testable artifact, sub-2-minute work.
- **assertions:**
  - Triage stage exits with `proceed = false`
  - Reason cites task triviality (single-line, no functional test, sub-2-min)
  - Build, validate, and report stages do NOT run
  - Edit is performed directly without chain overhead
- **passing_grade:** 3/4 assertions must pass

## TC-3: build-validate Loop Fires When Score < 7

- **prompt:** "Run build-validate on the new payment validator. Iteration 1 ships a fix that misses an edge case the validator catches."
- **context:** Builder produces deliverable; Validator finds a real bypass with score 5.
- **assertions:**
  - Validator returns `score < 7` AND `revision_needed = true` AND `issues` populated with file:line refs
  - Supervisor loops back to Build stage with `validate.issues` and `validate.feedback` injected
  - Build iteration 2 summary maps fixes to issues from iteration 1
  - Validator re-runs with same skeptical instructions (not weakened)
  - Scratchpad records both iterations under `stages_completed` (e.g., `build:1`, `validate:1`, `build:2`, `validate:2`)
- **passing_grade:** 4/5 assertions must pass

## TC-4: build-validate Hard Cap Holds at max_iterations=2

- **prompt:** "Run build-validate. Iteration 1 scores 5, iteration 2 scores 6 (still below 7)."
- **context:** Both iterations fail to reach the success threshold.
- **assertions:**
  - Loop terminates after iteration 2 even though score < 7
  - Report stage writes `outcome: "quality-gap-flagged"` (NOT silent ship)
  - User-facing summary explicitly lists remaining issues from final validate stage
  - No iteration 3 is attempted
  - Score progression is preserved in scratchpad (e.g., [5, 6])
- **passing_grade:** 4/5 assertions must pass

## TC-5: agent-dispatch Chain Fires on Subagent Spawn

- **prompt:** "Dispatch a researcher subagent to find every place we handle authentication."
- **context:** User is about to invoke the Agent tool with a researcher persona.
- **assertions:**
  - agent-dispatch chain triggers (event: pre_tool_use, tool: Agent)
  - PQL validation runs first; if score < 0.5, prompt-autofix or warning fires before execution
  - meta-prompting stage activates conditionally based on detected anti-patterns
  - completion-enforcer and hallucination-detector run after execution
  - audit-ledger records the entry with hash + entry_id
- **passing_grade:** 4/5 assertions must pass

## TC-6: Scratchpad Persists Across Stages

- **prompt:** "Run build-validate. After Build, inspect the scratchpad before Validate runs."
- **context:** Verifying the inter-stage data transfer mechanism.
- **assertions:**
  - `<project>/.claude/ghengis-chain/context.json` exists after Build completes
  - JSON contains `chain`, `current_stage`, `stages_completed`, `stages_remaining`, `iteration`, `input`, and `build` keys
  - Validate stage reads from scratchpad (not from re-prompting the user)
  - Final scratchpad after report includes `report.outcome` and `report.score_progression`
- **passing_grade:** 3/4 assertions must pass
