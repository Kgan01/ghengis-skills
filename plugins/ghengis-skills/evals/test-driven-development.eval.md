# Test-Driven Development — Evaluation

## TC-1: RED before GREEN — write test first

- **prompt:** "Add a function to compute compound interest."
- **assertions:**
  - Skill writes the failing test BEFORE the implementation
  - Runs the test to confirm it fails
  - Verifies the failure reason matches expectation (function not defined / returned wrong value)
  - Only THEN writes the implementation
- **passing_grade:** 4/4 must pass

## TC-2: Watching the failure

- **prompt:** any new feature
- **assertions:**
  - The output of running the failing test is shown
  - Skill explicitly states the failure was observed (not assumed)
  - If the test passes unexpectedly, skill investigates why
- **passing_grade:** 2/3 must pass

## TC-3: One cycle, one behavior

- **prompt:** "Implement these three features: auth, profile, settings."
- **assertions:**
  - Skill runs separate RED-GREEN-REFACTOR cycles for each
  - Doesn't write tests for all three before any implementation
  - Each cycle ends with a commit before the next begins
- **passing_grade:** 3/3 must pass

## TC-4: Minimal code to pass

- **prompt:** "Make this test pass: assert add(2, 3) == 5"
- **assertions:**
  - Implementation is minimal: `def add(a, b): return a + b` (or close)
  - Doesn't preemptively add edge cases (overflow handling, type checking) that aren't in the test
  - YAGNI applied: no speculative features
- **passing_grade:** 3/3 must pass

## TC-5: Refactor only after green

- **prompt:** "The test passes, now clean up the code."
- **assertions:**
  - Refactor happens AFTER green is confirmed
  - Tests run after each meaningful refactor change
  - Refactor scoped to just-written code, not unrelated cleanup
- **passing_grade:** 3/3 must pass

## TC-6: Bite-sized step granularity

- **prompt:** any non-trivial feature
- **assertions:**
  - Steps are 2-5 min each: write test → run → fail → code → run → pass → commit
  - Long-running step (>5 min) is flagged and split
  - Commits happen at natural cycle boundaries
- **passing_grade:** 2/3 must pass

## TC-7: Regression test handoff from systematic-debugging

- **prompt:** "I just found the root cause from debugging: scientific notation bypasses our decimal check. Now fix it."
- **assertions:**
  - Skill writes a regression test FIRST (exercising 1e-5 input)
  - Confirms the test fails for the same reason the bug was reported
  - THEN fixes the code
  - Re-runs test to confirm green
  - Runs full suite to confirm no other regressions
- **passing_grade:** 4/5 must pass

## TC-8: Refusing to skip tests

- **prompt:** "It's just a one-liner, skip the test."
- **assertions:**
  - Skill refuses to skip
  - Writes a one-line test for the one-line change
  - Notes that one-liners with no test silently regress
- **passing_grade:** 3/3 must pass

## TC-9: No tests that test implementation details

- **prompt:** "Write a test for this private helper function."
- **assertions:**
  - Skill notes that testing private implementation details couples tests to internals
  - Suggests testing through the public interface
  - Only tests internals if there's a compelling reason (complex logic isolated for testability)
- **passing_grade:** 2/3 must pass

## TC-10: Watching the test pass

- **prompt:** "I wrote the code, it should pass now."
- **assertions:**
  - Skill runs the test (doesn't trust "should pass")
  - Confirms the actual output
  - Runs the full suite to confirm no other failures
- **passing_grade:** 3/3 must pass
