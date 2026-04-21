---
name: completion-enforcer
description: Use after any agent or subagent claims a task is complete -- verifies completion through signal detection, catching premature "done" claims, partial outputs, and unfinished work before it ships
---

# Completion Enforcer

Signal-based verification that work is actually finished. Catches premature "done" claims, placeholder content, failure masking, and missing deliverables. Zero LLM cost, sub-millisecond latency -- pure pattern matching.

## When to Apply

- **Before claiming completion** -- scan your own output for incompleteness signals
- **Before committing** -- check that generated code, docs, or content is actually complete
- **Before responding to the user** -- verify the output matches the complexity of the request
- **After subagent execution** -- validate that delegated work came back whole
- **After any multi-step task** -- confirm all steps were addressed, not just the first one

## The 5 Heuristic Checks

Run all five checks on every "completed" output. If any check fails, the work is PARTIAL, not COMPLETED.

### Check 1: Maximum Steps Reached

If the agent hit its step/iteration limit before finishing, the output is truncated by definition. This is the strongest incompleteness signal -- it means the agent ran out of room.

**Detection:** The agent reached max tool calls, max iterations, or max tokens.
**Recovery:** Continue from where you stopped. Do not claim completion.

### Check 2: Output Length vs. Instruction Complexity

Short output for a complex instruction is suspicious. A request to "write, create, build, design, draft, prepare, generate, develop, implement, code, analyze, research, report, proposal, plan, or strategy" something expects a substantial deliverable.

**Complex instruction signals (2+ present or 40+ words in the instruction):**
```
write, create, build, design, draft, prepare,
generate, develop, implement, code, analyze,
research, report, proposal, plan, strategy
```

**Thresholds:**
- Any output under 30 characters is suspiciously short
- Complex instruction output under 100 characters is almost certainly incomplete

**Recovery:** Expand the output to match the instruction's complexity.

### Check 3: Incompleteness Signal Phrases

Scan the output (case-insensitive) for phrases that indicate unfinished work. These are the most common ways agents say "done" when they are not done.

**Admission of inability (agent hit a wall):**
```
i'll need to
i would need to
i haven't been able to
i wasn't able to
i couldn't
i can't
unfortunately i
i don't have access
i'm unable to
this is beyond
```

**Deferred work (agent is passing the buck):**
```
i'll get back to you
i'll follow up
to be continued
work in progress
not yet complete
partially done
still working on
haven't finished
need more time
need more information
```

**Placeholder content (agent left blanks):**
```
placeholder
todo
tbd
[insert
[add
[fill in
lorem ipsum
```

**Additional patterns to watch for:**
```
as an exercise
left as an exercise
i'll leave that to you
you'll need to
you should be able to
the rest is similar
and so on
etc (at the end of incomplete lists)
...  (trailing ellipsis as content, not punctuation)
skeleton
stub
boilerplate (when it IS the deliverable, not describing it)
# TODO
// TODO
/* TODO
FIXME
HACK
XXX
PLACEHOLDER
NotImplementedError
raise NotImplementedError
pass  (as the only content of a function body)
```

**Recovery:** Complete the work. Replace every placeholder, finish every deferred item.

### Check 4: Failure Masking

The agent claims success but the output contains error evidence. This happens when an agent encounters an error mid-execution, catches it internally, and reports "done" anyway.

**Error phrases (only flagged when output is under 300 characters -- short error-only responses):**
```
error occurred
exception was raised
failed to execute
could not connect
permission denied
timed out
rate limit
api error
500 internal
404 not found
connection refused
```

**Recovery:** Acknowledge the failure. Retry, use a fallback approach, or report the error honestly to the user.

### Check 5: Missing Expected Deliverables

For complex instructions, check that the output contains the expected deliverable types.

**Code-producing instructions** (keywords: code, implement, build, function, class, script, program):
```
Expected signals in output: ```, def , class , function , import
```

**Data/analysis instructions** (keywords: data, json, csv, table, spreadsheet, analyze):
```
Expected signals in output: {, [, ```json, ```csv
```

Missing deliverable types are only flagged when output is under 500 characters -- longer outputs may contain the deliverables in a different format.

**Recovery:** Produce the missing deliverable. If the instruction asked for code, deliver code. If it asked for data, deliver data.

## Confidence Scoring

When incompleteness is detected, confidence in the PARTIAL verdict scales with how many checks failed:

| Checks Failed | Confidence | Auto-Continue? |
|---------------|------------|----------------|
| 1 | 0.80 | Yes -- likely a minor gap |
| 2 | 0.60 | No -- multiple signals indicate real incompleteness |
| 3 | 0.40 | No -- significant incompleteness |
| 4+ | 0.30 | No -- almost certainly unfinished |

## Red Flags: Common False "Done" Patterns

| Pattern | What It Looks Like | What Actually Happened |
|---------|--------------------|----------------------|
| **The Summarizer** | "I've analyzed the codebase and identified 3 key issues..." | Agent described what it would do instead of doing it |
| **The Deferrer** | "You'll need to update the config file with..." | Agent handed the work back to the user |
| **The Skeleton** | Returns function signatures with `pass` or `...` bodies | Agent created structure without implementation |
| **The Error Swallower** | "Task completed successfully" (but output is 2 lines) | Agent hit an error and reported success anyway |
| **The Partial Lister** | "Here are the first 3 items: ... and so on" | Agent got tired and truncated the deliverable |
| **The Planner** | Returns a plan/outline instead of the requested artifact | Agent confused planning with execution |
| **The Promiser** | "I'll implement the rest in the next step" | Agent split work across steps it never took |
| **The Commentator** | Code full of `// TODO: implement this` comments | Agent created a to-do list, not a solution |

## Recovery Actions

When incompleteness is detected, do not just flag it -- fix it:

1. **Identify which checks failed** -- each failed check points to a specific type of incompleteness
2. **Replace placeholders** -- search output for TODO, TBD, placeholder, [insert, and fill them in
3. **Complete deferred work** -- anything described as "you'll need to" or "as an exercise" must be done
4. **Retry on errors** -- if failure masking was detected, retry the failed operation or explain why it cannot be done
5. **Expand short outputs** -- if output is too short for the instruction complexity, expand with actual content
6. **Add missing deliverables** -- if code was expected but not delivered, write the code

## Check 6: Multi-Stage Verification (ASI-Evolve Pattern)

For non-trivial deliverables, a single pass is not enough. ASI-Evolve (arxiv 2603.29640) demonstrated that discoveries validated at small scale (20M parameters) often fail at medium scale (340M) and need re-validation at full scale (1.3B). The same principle applies to code, content, and any agent output.

**Three verification tiers:**

| Tier | What It Checks | Cost | When to Use |
|------|---------------|------|-------------|
| **Proxy** | Lint, type-check, syntax, format | $0, <1s | Every deliverable |
| **Functional** | Unit tests, integration tests, endpoint smoke tests | $0-0.01, <30s | Code changes, API work |
| **Full** | Manual smoke test, cross-validation script, user-facing walkthrough | Variable | Features, UI changes, deployments |

**The rule:** A deliverable that passes Tier 1 but hasn't been Tier 2 tested is NOT complete. A deliverable that passes Tier 2 but involves user-facing changes and hasn't been Tier 3 tested is NOT complete.

**Detection:** Check what tier the implementer actually reached:

```
Tier 1 signals (proxy only):
- "lint passes" / "no type errors" / "compiles cleanly"
- But no test execution mentioned

Tier 2 signals (functional):
- "X tests passing" / "pytest output" / "curl returned 200"
- But no manual verification of the user-facing behavior

Tier 3 signals (full):
- "tested in browser" / "smoke-tested on device" / "verified the UI flow"
- Screenshots, recordings, or specific behavioral descriptions
```

**Recovery by tier gap:**

| Gap | Recovery Action |
|-----|----------------|
| Only Tier 1 claimed | Run the test suite. Report results. |
| Tier 2 passed but Tier 3 skipped on UI work | Start the dev server, test the golden path + one edge case. Report what you see. |
| Tier 2 passed but Tier 3 infeasible (no emulator, no browser) | Explicitly state "Tier 3 not verified â€” [reason]". Do NOT claim full completion. |

**When Tier 3 is infeasible:** It is honest and correct to say "functional tests pass but I cannot verify the UI behavior because [no emulator available / no browser access / etc.]." Claim DONE_WITH_CONCERNS, not DONE. The user decides whether to accept.

**Multi-stage for subagent review:**
When reviewing a subagent's work, check which tier they reached:
1. Did they run any tests at all? (Many subagents claim "done" without running anything)
2. Did they run the RIGHT tests? (Running unrelated tests is not verification)
3. Did they verify the SPECIFIC behavior the task requested? (Running the full suite doesn't prove the new feature works)

## Integration with Other Skills

- **constitutional-ai** catches intent violations (dangerous actions, privacy leaks). Completion enforcer catches output quality (did you actually finish?).
- **hallucination-detector** catches fabricated content. Completion enforcer catches missing content.
- **context-health** detects when context degradation causes declining output quality. Completion enforcer detects when the final output is incomplete regardless of cause.
- **evolving-cognition** prevents the same incompleteness pattern NEXT TIME by distilling lessons from past outcomes. Completion enforcer catches it NOW.

## Cost

$0. Zero LLM calls. All checks are string matching and length comparisons. Apply liberally.

## Chain Integration

This skill participates in `skill-chain-supervisor` chains via the shared scratchpad at `<project>/.claude/ghengis-chain/context.json`.

**Role in chain:** Post-execution verifier. Catches false 'done' claims before they ship.

**Scratchpad subkey (namespaced writes):** `completion_enforcer.*`

**Reads (input scratchpad keys):**
- `execution.result`
- `input.user_request`

**Writes (output scratchpad keys):**
- `completion_enforcer.status` — 'done' | 'partial' | 'incomplete'
- `completion_enforcer.concerns` — list of premature-completion signals detected
- `completion_enforcer.evidence_checks` — what was verified (tests ran, files created, etc.)

**Success criteria:** status == 'done' AND concerns is empty

When invoked as part of a chain, this skill MUST:
1. Read prior scratchpad state before starting
2. Write outputs to the `completion_enforcer.*` namespace only — never overwrite another skill's subkey
3. Report failure via its own subkey (e.g. `completion_enforcer.error`) rather than raising

When invoked standalone (not in a chain), scratchpad writes are optional but recommended for auditability.
