---
name: systematic-debugging
description: Use when encountering ANY bug, test failure, error message, performance issue, or unexpected behavior, BEFORE proposing fixes. Forces root-cause investigation before any code change. Iron law - no fixes without evidence. TRIGGER on "this is broken", "test is failing", "why is X doing Y", "it crashed", "production issue", or any unexpected output. Cross-refs test-driven-development for writing the regression test, bug-hunt chain for the canonical fix pipeline.
allowed-tools: Read Grep Glob Bash Edit Write
---

# Systematic Debugging

Random fixes waste time and create new bugs. Quick patches mask underlying issues and the same bug returns wearing a different hat next week.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes. "It works now" without explanation is not debugging — it's luck.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production or local dev
- Unexpected behavior
- Performance problems (slow response, memory creep, CPU spikes)
- Build failures
- Integration issues
- "It works on my machine"

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting; systematic is *faster* than thrashing)
- "Just one quick fix" seems obvious — that voice is the symptom of the trap
- You've already tried multiple fixes that didn't work
- The previous fix made it different but not better
- You don't fully understand the issue but feel pressure to ship

**Don't skip when:**
- Issue seems simple — simple bugs have root causes too
- You're in a hurry — rushing guarantees rework
- Someone wants it fixed NOW — explain, don't capitulate

## The 4-Phase Process

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**Before attempting ANY fix:**

1. **Read error messages carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely — line numbers, file paths, error codes
   - If you don't understand a phrase in the error, look it up before guessing

2. **Reproduce consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time, or only under specific conditions (time of day, data, user role)?
   - If not reproducible → gather more data; don't guess

3. **Check recent changes**
   - `git log --oneline -20`, `git diff HEAD~5`
   - New dependencies, config changes, env differences
   - What was the last known-good state?

4. **Add diagnostic instrumentation in multi-component systems**

   When the system has multiple components (CI → build → signing, API → service → DB, frontend → API → worker), add logs at component boundaries BEFORE proposing fixes:

   ```
   For each component boundary:
     - Log what data enters component
     - Log what data exits component
     - Compare actual vs expected at each step
   ```

   Don't assume the boundaries are intact. Verify each one. Most multi-component bugs live in the seams.

5. **Form a hypothesis and state it explicitly**
   - "I think X is happening because Y, and I can verify this by Z"
   - If you can't write that sentence, you don't have a hypothesis — keep investigating
   - One hypothesis at a time. Don't try to debug 3 theories in parallel.

### Phase 2: Test the Hypothesis

1. **Design a single experiment that confirms or rules out your hypothesis**
   - What's the minimal probe that would distinguish "yes, this is the cause" from "no, look elsewhere"?
   - Run the probe — read the output carefully
   - Update your hypothesis based on what you observed

2. **If the hypothesis is wrong, go back to Phase 1**
   - Don't bend evidence to fit your theory
   - "Mostly right" is wrong — keep investigating

3. **If the hypothesis is right, you have root cause**
   - State it in one sentence
   - Confirm: "The bug is caused by X, which produces Y, which manifests as Z"
   - If the sentence has hedging ("might", "maybe", "could be"), keep investigating

### Phase 3: Write a Regression Test

**Before fixing — write a test that fails because of the bug.**

This is the critical handoff to `test-driven-development`:

1. Pick the level the test should live at (unit, integration, end-to-end) based on where root cause lives
2. Write the test
3. Run it and confirm it fails for the same reason the user-reported bug fails
4. If the test fails for a *different* reason, your test is wrong — fix the test, not the bug yet

The regression test proves:
- You actually understand the bug
- The fix you're about to write addresses what users saw
- A future change won't silently re-introduce the same bug

Skip this only if:
- You're in a non-code system (debugging infra, config, deployment)
- The test framework genuinely doesn't exist (and you're not in a position to add one)

### Phase 4: Fix and Verify

1. **Write the fix targeted at root cause, not symptom**
   - "This catches the exception" — that's a symptom fix
   - "This prevents the exception from being raised by handling the actual upstream condition" — that's a root-cause fix
   - If the fix is in a different file than you expected, that's a sign you found the actual root, not a proxy

2. **Run the regression test from Phase 3 — confirm it now passes**

3. **Run the full test suite — confirm nothing else broke**
   - If something else broke, the fix has unintended consequences
   - Often this means the bug was masking a different bug; investigate

4. **Document what you learned**
   - Commit message explains the root cause, not just "fixed bug"
   - If the bug taught you something non-obvious, write it down in CLAUDE.md or a relevant skill

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Trying multiple fixes in parallel | Can't tell which one worked, can't tell which made things worse | One hypothesis, one experiment, one fix at a time |
| "It works now, ship it" | The bug is still there; you just changed the surface enough to hide it | Find the root cause even if the symptom is gone |
| Catching exceptions to make the error go away | Symptom fix; the condition still happens, just silently | Fix the upstream cause; only catch exceptions that are genuinely expected |
| Adding `try/except` then re-raising with no behavior change | Adds noise without adding signal | Don't catch unless you handle |
| "I changed three things and now it works" | You have no idea which change was load-bearing | Revert, change one thing, verify, repeat |
| Skipping the regression test | The bug returns in three months wearing a different hat | Write the test even if it slows the fix by 5 minutes |
| Reading the error message diagonally | The exact answer is often in the stack trace | Read every line, every file path, every line number |
| "Random race condition" | Almost no bugs are actually random; you just haven't found the trigger | Find the trigger. Run it 1000 times in a loop if you have to. |
| Fixing the wrong layer | The fix masks the real bug, which surfaces elsewhere later | Trace the chain back to the actual cause, not the proximate symptom |
| Trusting "fixed in the latest version" without verification | Often the fix doesn't apply to your specific case | Verify against your exact scenario |

## Multi-Component Debugging Patterns

When the bug involves multiple systems (CI/CD, distributed services, async pipelines):

1. **Bisect the boundaries** — narrow down which seam is failing
2. **Each component is innocent until proven guilty** — assume it works correctly until evidence shows otherwise
3. **Log data shape at every boundary** — what type, what shape, what fields
4. **Time-stamp everything** — race conditions and ordering bugs are invisible without timestamps
5. **Check for silent data loss** — payloads getting truncated, batches getting dropped, retries swallowing errors

## Cross-References

- **`test-driven-development`** — Phase 3 is a handoff to TDD. Write the regression test before the fix.
- **`completion-enforcer`** — verify the fix actually addressed the issue before claiming done.
- **`bug-hunt` chain** (in `skill-chain-supervisor`) — canonical pipeline: systematic-debugging → TDD → build-validate. Use this when the bug is non-trivial.
- **`hallucination-detector`** — if the error message references something you can't find, the model may have hallucinated. Verify the symbol/file/version exists before debugging it.
- **`brainstorming`** — if Phase 1 reveals the bug is actually a design problem (not a code defect), switch to brainstorming mode.
