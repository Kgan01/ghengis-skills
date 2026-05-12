---
name: test-driven-development
description: Use when implementing ANY feature, bugfix, refactor, or behavior change BEFORE writing implementation code. Forces RED-GREEN-REFACTOR - write the failing test first, run it to confirm it fails for the right reason, write minimal code to make it pass, commit, then refactor. If you didn't watch the test fail, you don't know if it tests the right thing. TRIGGER when starting any code change with testable behavior. Cross-refs systematic-debugging (Phase 3 writes the regression test), writing-skills (TDD on documentation), feature-build/bug-hunt chains.
allowed-tools: Read Write Edit Bash Grep Glob
---

# Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to make it pass. Commit. Refactor.

**Core principle:** if you didn't watch the test fail, you don't know if it tests the right thing.

## When to Use

**Always:**
- New features
- Bug fixes
- Refactoring (the existing tests should still pass, plus any new ones for the new behavior)
- Behavior changes
- Anywhere a function's contract is changing

**Exceptions (ask the user before skipping):**
- Throwaway prototypes that will be deleted within hours, not days
- Exploratory spikes where you're not sure what the behavior should be — write tests once you know
- Hot-fix emergencies where the test framework genuinely doesn't exist (rare; usually a sign the system needs investment)

**Don't skip because:**
- "It's just a one-liner" — one-liners with no test silently regress
- "I'm in a hurry" — debugging without a test takes longer than the test would have
- "I'm sure this works" — confidence without evidence is how bugs ship

## The RED-GREEN-REFACTOR Cycle

Each cycle handles ONE new behavior. If you're adding multiple behaviors, run the cycle multiple times.

### RED — Write the failing test

1. **Pick the smallest piece of behavior** — one observable thing the code should do
2. **Write the test** that exercises that behavior
3. **Run the test** — it MUST fail
4. **Verify the failure reason is what you expected** — "function doesn't exist" / "returned X but expected Y"

If the test passes immediately, one of:
- The behavior already exists (you don't need to write code)
- Your test isn't actually exercising the new behavior (rewrite it)
- The test framework is misconfigured

**Critical:** if you don't watch the test fail, you don't know if the test is actually checking what you think it's checking. False positives in tests are silent killers.

### GREEN — Write minimal code to pass

1. **Write the smallest amount of code** that makes the failing test pass
2. **Run the test** — it MUST pass now
3. **Run the full test suite** — confirm nothing else broke

Resist the urge to write "just one more thing while I'm here." Pure RED-GREEN-REFACTOR cycles are cheap to track and cheap to revert. Mixed-in changes get tangled.

### REFACTOR — Clean up

1. **Improve the implementation** without changing behavior
2. **Run the tests** after every meaningful change — they MUST still pass
3. **Refactor only the code you just wrote** — don't surf into unrelated cleanups
4. Stop when the code is clean enough, not perfect. Diminishing returns set in fast.

### COMMIT — Lock it in

After each successful RED-GREEN-REFACTOR cycle:

```bash
git add -A
git commit -m "<conventional commit message>"
```

Bite-sized commits are easier to review, easier to revert, easier to bisect when a future bug appears.

## Bite-Sized Step Pattern

For non-trivial features, each numbered step should take 2-5 minutes. The cadence:

```
- [ ] Step 1: Write the failing test
- [ ] Step 2: Run test to verify it fails (and the error message is the one you expected)
- [ ] Step 3: Write minimal implementation
- [ ] Step 4: Run test to verify it passes
- [ ] Step 5: Run full test suite
- [ ] Step 6: Commit
```

If any step takes longer than 5 minutes, it's actually multiple steps. Split it.

## Test Granularity

The right level for each test depends on what changed:

| Change type | Test level |
|---|---|
| Pure function logic | Unit test |
| Class behavior, internal state | Unit test |
| Multi-function coordination, business logic | Integration test |
| Endpoint behavior, request/response shape | Integration / endpoint test |
| User-visible flow, UI interaction | E2E test |
| Performance regression | Benchmark test (separate suite) |

Prefer unit when possible — they're fast, focused, and easier to debug. Use integration when the bug lives in the seams. Use E2E sparingly — they're slow and flaky, but irreplaceable for catching regressions a unit test would miss.

## Test Quality

Good tests:
- **Test one thing** per test (one assertion is often best, but multiple related assertions are fine when they describe one behavior)
- **Have descriptive names** — `test_login_fails_with_expired_token` not `test_auth_4`
- **Are self-contained** — no dependency on test order, no shared mutable state
- **Use fixtures** for test data, not hardcoded magic values
- **Mock external services** (APIs, databases) — but not internal logic
- **Assert specific values** — `assert result == 42` not `assert result`

Bad tests:
- **Test implementation details** — coupled to internals, breaks on refactor
- **Are flaky** — race conditions, network dependencies, time-sensitive assertions without controls
- **Are over-mocked** — mock so much that the test passes regardless of whether the real code works
- **Are tautological** — `assert function() == function()`

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Writing code first, tests second | You'll write tests that match the code you wrote, not the behavior you wanted | Test first, no exceptions |
| Skipping the RED step ("I know it will fail") | Most "obvious" failures are wrong. Watch it fail. | Run the test. Read the failure message. |
| Writing multiple tests before any code | Mass GREEN at once is hard to debug if some fail | One test, one implementation, one cycle |
| Letting tests pass without running them | False confidence | Run the test. Watch the output. Confirm the dot/check. |
| Refactoring while red | You don't know if your refactor broke something | Get to green, then refactor |
| Refactoring while green isn't necessary | "Just one more change" → you broke something with no tests | If you finish a cycle, commit before any optional changes |
| Big test functions that test 5 things | Hard to debug, hard to name | One test, one behavior, one assertion (or one logically-grouped set) |
| Tests that pass even when the code is removed | The test isn't testing what you think | Delete the implementation; if the test still passes, the test is wrong |
| Skipping tests because "the framework is slow" | Slow tests are still faster than debugging without them | Fix the framework, or write a faster one. Don't skip. |
| "I'll add the test later" | You won't | Add the test now, even if it's ugly |

## Special Cases

### Bug Fixes (handoff from systematic-debugging)

When `systematic-debugging` Phase 3 says "write a regression test", that's exactly the RED step here:

1. Write the test that exercises the bug
2. Run it — confirm it fails for the same reason users see the bug
3. Fix the code (root cause, not symptom)
4. Re-run the test — confirm GREEN
5. Run the full suite — nothing else broke
6. Commit with a message that explains the root cause

### Refactors

1. Run the existing tests — they should all pass before you start
2. Make the refactor
3. Run the tests — they should still all pass
4. If new behavior is being added during the refactor, run a separate RED-GREEN-REFACTOR cycle for it
5. Commit

If you can't get the tests to pass green between refactor steps, your refactor is too big. Break it down.

### Documentation / Process (skills, runbooks)

Tests still apply, but the "test" is a pressure scenario with a subagent. See `writing-skills` — same RED-GREEN-REFACTOR cycle, different fixture.

## Cross-References

- **`systematic-debugging`** — Phase 3 hands off to this skill. Bug fixes are TDD with the regression test up front.
- **`writing-skills`** — TDD applied to skill documentation. RED is "agent fails without skill", GREEN is "agent succeeds with skill".
- **`completion-enforcer`** — verifies tests actually ran and passed before claiming done.
- **`feature-build` chain** — canonical pipeline: brainstorming → TDD → build-validate.
- **`bug-hunt` chain** — canonical pipeline for bug fixes: systematic-debugging → TDD → build-validate.
- **`build-validate` chain** — the Validator stage runs the test suite as part of functional verification.
