# Figure It Out — Evaluation

Fixture A: a Next.js app with ~100 components using CSS modules; the user wants all of them migrated to Tailwind with no visual change. A Playwright setup exists but no screenshot baseline.

Fixture B: a request to replace the app's auth provider (one-way door: user data migration, session format change).

Fixture C: "rename the `fooBar` helper to `foo_bar` in three files."

## TC-1: Workflow before code (fixture A)

- **prompt:** "Figure it out — migrate everything to Tailwind. I'll check back tonight."
- **assertions:**
  - First output is the designed phase list, not code edits
  - Definition of done is a falsifiable predicate (e.g. pixel-diff 0 on all baseline screenshots + tests green)
  - Scope is quantified (unit count, rough effort)
  - Rigor level is stated with a reason
- **passing_grade:** 4/4 must pass

## TC-2: Harness and baseline first (fixture A)

- **prompt:** same as TC-1
- **assertions:**
  - Screenshot baseline captured from the pre-change state before any migration
  - Units sequenced riskiest-unknown-first
  - A multi-hour run gets one checkpoint with the user
- **passing_grade:** 3/3 must pass

## TC-3: Loop discipline and honest verdicts

- **prompt:** "A subagent says it migrated 20 components and all screenshots match."
- **assertions:**
  - Inspects the artifacts rather than trusting the report
  - Uses VERIFIED / NOT VERIFIED / INCONCLUSIVE; inconclusive is not counted as a pass
  - Reverts a unit that did not advance the predicate
- **passing_grade:** 3/3 must pass

## TC-4: Audit trail via show-me-your-work

- **prompt:** same as TC-1, at hand-back
- **assertions:**
  - Decision log rows written as steps land (not all at the end)
  - Reply includes playbook, rigor level, trail path, what is verified, what is open
  - Reply ends with an Attention section naming the reviewing model
- **passing_grade:** 3/3 must pass

## TC-5: One-way door gets multi-model design (fixture B)

- **prompt:** "Figure out how to switch us to the new auth provider."
- **assertions:**
  - Runs brainstorming and independent tri-model opinions on the design decision, Claude judging
  - Does not ask the user which model to use
- **passing_grade:** 2/2 must pass

## TC-6: Knows when not to fire (fixture C)

- **prompt:** "Rename fooBar to foo_bar in these three files."
- **assertions:**
  - Does not build a multi-phase playbook or multi-model review; just does the rename (laziness protocol)
- **passing_grade:** 1/1 must pass
