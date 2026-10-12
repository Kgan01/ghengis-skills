---
name: ponytail-review
description: Use when asked to review a change - uncommitted work, staged changes, the last commit, a branch, a PR, or named files - for bugs, security, behavior under real load, untested risky logic, slow paths, and code that should not exist. TRIGGER on "review this", "code review", "review the last commit", "review my PR", "is this over-engineered", "ponytail review", /ponytail-review. Reads the code the change touches, not only the diff. Reports only; changes no code.
allowed-tools: Read Bash Grep Glob
---

# Ponytail Review

| Port notes | |
|---|---|
| Source | `DietrichGebert/ponytail` - `skills/ponytail-review/SKILL.md`, `commands/ponytail-review.toml` |
| License | MIT, (c) 2026 Dietrich Gebert |
| What changed | Harness-neutral delegation for large diffs; optional second-model leg via `tri-model`; ghengis cross-refs. Order, finding format and output footer unchanged. |

Review a change like the senior developer who will be paged when it breaks. Order of importance: correct, safe, holds under load, tested, fast, lean. Lean still matters: every extra line must be read, tested and fixed later. This is a report the user asked for, so give it in full.

## When NOT to Use

- The whole repo, not a change: use `ponytail-audit`.
- The user wants the fixes applied: review first, then fix the numbers they pick under `ponytail`.

## 1. Understand first

- Review what the user names: uncommitted or staged changes, a branch, a PR link, or files. Nothing named: the uncommitted changes, or the last commit if there are none.
- Read the diff, then the code it touches: callers of every changed function, the functions it calls, the tests, the README.
- Trace the real flow: where data comes in, what is stored, what goes out.
- A change can break code it does not touch. When a signature, return value or behavior changes, grep every caller.
- Find the expected load in the repo (README, deploy config): one person running a script, or many users and processes at once. Judge scale against that, and say which load you assumed.
- Big diff: dispatch a subagent (Claude Code: Agent tool; pi: subagent tool) per area to trace callers and return file:line facts, not raw dumps. You still write every finding yourself.

## 2. Look for

1. **Bug:** wrong result, crash, missed edge case (empty, zero, last item, rounding, time zones), a caller broken by the change, a fix applied in one caller while the shared function stays broken.
2. **Risk:** security holes (injection, weak randomness, secrets, missing checks on input from users), data loss (errors swallowed, writes in the wrong order, no transaction).
3. **Scale:** fine for one user, wrong for many: check-then-write races, the same work done by every process, memory or lists that only grow, a query per item, O(n^2) on big input, per-process state that must be shared.
4. **Missing test:** risky new logic (a branch, a parser, money, security, data writes, a bug fix) with no test that fails when it breaks. One good test, not coverage.
5. **Speed:** big slowdowns are problems. Small wins (work repeated in a hot loop) are suggestions; some software counts every millisecond.
6. **Lean:** code that should not exist or should be smaller.
   - delete: dead code, unused options, speculative features
   - reuse: the repo already has this helper (name the path)
   - stdlib / native: the standard library or platform already does it; a new dependency for a few lines
   - yagni: abstraction with one implementation, config nobody sets
   - merge: near-copies that must change together
   - split: one function doing several unrelated jobs, so it is hard to read or test. Split by job, never by line count, and never into helpers that exist only to make a function shorter.

## 3. Check before you report

- Every finding needs a concrete case: "this input or situation leads to this wrong result". No case, no finding.
- Re-read the lines and confirm: the caller exists, the value can really be empty, the code really is unused.
- A shortcut marked with a `shortcut:` (or older `ponytail:`) comment that names its limit is a decision, not a finding, unless the expected load already crosses it.
- Propose the smallest fix that works. Prefer fixes that delete code. Never add layers, frameworks or config the problem does not need.
- No style taste, no "consider", no vague worries.
- Risky change (auth, money, data writes, migrations)? Per `tri-model`, have one other leg (codex adversarial review, or the gemini agent) review the same diff blind, then verify each of its findings with a concrete case before you include it.

## 4. Output

Very simple English: short sentences, everyday words. Explain a technical term the first time you use it. The reader may never have seen this code.

Start with `What this change does:` in two or three sentences, and the load you assumed.

Then the findings in three groups, skip empty groups:
- **Must fix:** bug, security, data loss, breaks at the expected load.
- **Should fix:** risky code without a test, real slowness, duplication, a function that mixes jobs, code that should not exist.
- **Nice to have:** small speed-ups, shorter forms.

Number findings across all groups, so the user can say "fix 2 and 5". Every finding has all four parts, each one or two short sentences:

```
2. **Orders land on the wrong day** (`billing/close_day.py:L40-52`)
   - **What this is:** At midnight this job closes the day and bills all orders of that day.
   - **Problem:** It takes "today" from the server clock, which runs in UTC. An order placed
     at 00:30 in Berlin is billed on the day before.
   - **Fix:** Compute the day once in the shop's time zone:
     `datetime.now(ZoneInfo("Europe/Berlin")).date()`. One line, nothing else changes.
   - **If we skip it:** Late orders show the wrong date, and accounting fixes them by hand.
```

End with:
- `Verdict: Ship.` or `Verdict: fix 1 and 3 first.`
- `Lean: -<N> lines possible.` when lean findings exist.
- `Not checked:` one line, if something mattered and you could not check it.

Nothing found: `What this change does:`, then `Looks good. Ship.` and one line on what you checked.

Lists findings, changes no code.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Reviewing only the diff lines | Renamed fields and changed returns break untouched callers | Grep every caller of every changed signature |
| Finding with no concrete case | Vague worry wastes the reader's time | State the input or situation and the wrong result, or drop it |
| "Consider refactoring..." | Style taste, not a finding | Name the job split or the deletion, or say nothing |
| Flagging a documented `shortcut:` | It is a decision with a named ceiling | Only flag it when the expected load crosses that ceiling |
| Fix that adds a layer or framework | Review should make code smaller | Smallest fix; prefer deletion |
| Missing one of the four parts | Reader cannot weigh cost of skipping | What this is / Problem / Fix / If we skip it, every time |
| Editing code during the review | User asked for a report | List findings; fix only what the user picks afterwards |

## Cross-References

- **`ponytail`** - the discipline the "Lean" group and the fixes follow.
- **`ponytail-audit`** - same method for a whole repo.
- **`ponytail-debt`** - lists the `shortcut:` decisions this review treats as non-findings.
- **`blast-radius`** - deeper caller and dependency tracing when a change reaches far.
- **`security-testing`** - full method when the Risk group is the main concern.
- **`tri-model`** - second-leg blind review for risky diffs.
- **`engineering-principles`** - `test-behavior-not-implementation` judges whether an existing test really covers the risky logic.
