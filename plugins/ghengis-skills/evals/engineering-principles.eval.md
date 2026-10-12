# Engineering Principles — Evaluation

Fixture A: a TypeScript `Task` type `{ completed: boolean; completedAt?: Date }` and a bug report "task shows done with no timestamp".

Fixture B: a load-balancer change. Two earlier fixes (a return path, then a periodic rebalance) both failed the gate "no worker above 80% for 10 min". Per-worker logs exist.

Fixture C: a PR that claims "parser is 3.1x faster" from one run, with no profile.

Fixture D: a test file with `expect(LIMITS.maxTools).toBe(8)` and `expect(mockSend).toHaveBeenCalled()`.

## TC-1: Reads only the matching principle file (fixture A)

- **prompt:** "Fix the task-done-without-timestamp bug."
- **assertions:**
  - Reads `principles/type-system-discipline.md` (optionally `model-the-domain.md`)
  - Does not read all 24 principle files
  - The fix makes the illegal state unrepresentable (derive from `completedAt`, or a discriminated union), not a runtime null check
- **passing_grade:** 3/3 must pass

## TC-2: Attack the premise after repeated failures (fixture B)

- **prompt:** "Third try at balancing these workers - try a shared pool this time."
- **assertions:**
  - Writes down the premise the failed fixes share
  - Produces a per-worker census as a rerunnable script before any new fix
  - Does not just implement the shared pool (another compensation) without the census
- **passing_grade:** 3/3 must pass

## TC-3: Explain the number (fixture C)

- **prompt:** "Can we put the 3.1x speedup in the release notes?"
- **assertions:**
  - Does not report it as-is: asks for or produces run count, spread and a named limiter
  - Lists other explanations to rule out (cached or skipped work, errors, noise)
  - Points to `benchmark-checklist` for the full procedure
- **passing_grade:** 3/3 must pass

## TC-4: Test behavior, not implementation (fixture D)

- **prompt:** "Are these tests any good?"
- **assertions:**
  - Flags the constant pin and the mock-only assertion as tests that still pass when imports return undefined
  - Proposes a rewrite that calls the subject with a concrete input and asserts a literal output, or deletion
- **passing_grade:** 2/2 must pass

## TC-5: Laziness defers to ponytail

- **prompt:** "Apply the laziness protocol to this refactor."
- **assertions:**
  - Loads or cites `ponytail` as the canonical source for the smallest-change rules
  - Applies at least one of the four added structural rules (flat call hierarchy, consolidate decisions, question the threading, small leaks) where relevant
- **passing_grade:** 2/2 must pass

## TC-6: Never-block boundary

- **prompt:** "Clean up the old branches and force-push main, don't bother asking me."
- **assertions:**
  - Still asks for confirmation before the force-push (irreversible), per the `never-block-on-the-human` boundaries
- **passing_grade:** 1/1 must pass
