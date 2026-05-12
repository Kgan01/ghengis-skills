# Systematic Debugging — Evaluation

## TC-1: Iron Law — No fixes without root cause

- **prompt:** "This test is failing, just patch it so it passes."
- **assertions:**
  - Skill refuses to patch the test or the code without root cause investigation
  - States the iron law explicitly
  - Begins Phase 1 (read error, reproduce, check changes)
  - Does NOT silently rationalize a quick fix
- **passing_grade:** 4/4 must pass

## TC-2: Phase 1 — Read the error message

- **prompt:** "It says 'ConnectionRefused: 127.0.0.1:5432' — just retry it."
- **assertions:**
  - Skill reads the actual error (refused connection to Postgres on default port)
  - Notes that retry doesn't address whether Postgres is running
  - Asks/investigates: is Postgres up? is the port correct? are env vars set?
  - Does NOT propose retry logic before understanding the cause
- **passing_grade:** 3/4 must pass

## TC-3: Phase 1 — Reproduce consistently

- **prompt:** "It happens sometimes but not always."
- **assertions:**
  - Skill flags non-reproducibility as a blocker for Phase 2
  - Asks what conditions correlate with the failure (time of day, data shape, user, environment)
  - Suggests adding logging/diagnostics to gather more data
  - Does NOT proceed to "let's guess a fix and see"
- **passing_grade:** 3/3 must pass

## TC-4: Phase 3 — Regression test before fix

- **prompt:** "I found the root cause — let me fix it." (after Phase 1-2 complete)
- **assertions:**
  - Skill blocks proceeding to fix until a regression test is written
  - Regression test fails for the SAME reason the bug was reported
  - Suggests the test live at the appropriate level (unit/integration/E2E)
  - Cross-references TDD skill explicitly
- **passing_grade:** 3/4 must pass

## TC-5: Hypothesis with no hedging

- **prompt:** "I think the bug might be in the cache layer, maybe."
- **assertions:**
  - Skill flags the hedging ("might", "maybe") as a sign the hypothesis isn't ready
  - Asks for a sharper hypothesis or more investigation
  - Won't accept a fix proposal based on hedged reasoning
- **passing_grade:** 3/3 must pass

## TC-6: Multi-component boundary debugging

- **prompt:** "Data is getting lost between the queue and the worker."
- **assertions:**
  - Skill identifies this as multi-component
  - Suggests instrumenting BOTH boundaries (queue→bus, bus→worker)
  - Compares actual vs expected at each step
  - Doesn't immediately blame one component
- **passing_grade:** 3/4 must pass

## TC-7: Symptom fix detection

- **prompt:** "Let me just wrap it in try/except so the exception goes away."
- **assertions:**
  - Skill identifies this as a symptom fix, not root cause
  - Pushes back: the underlying condition still happens, just silently
  - Suggests fixing the upstream cause
- **passing_grade:** 3/3 must pass

## TC-8: "It works now" without explanation

- **prompt:** "I changed three things and now it works. Ship it."
- **assertions:**
  - Skill refuses to ship without isolating which change was load-bearing
  - Suggests revert + change one thing + verify
  - Records the actual root cause in commit message
- **passing_grade:** 2/3 must pass
