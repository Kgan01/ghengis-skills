---
name: correct
description: Use when the user keeps correcting agents for the same mistake in a repo and wants it made impossible, not just remembered. Finds repeated mistake classes, then fixes each at the highest level that works - architecture, types, a lint or hook whose error names the fix, a test, and docs/rules last - and proves each check fails on a real past mistake. TRIGGER on "/correct", "you keep doing X", "stop making this mistake", "make this impossible", "I've told you this before", or any repeat correction.
allowed-tools: Read Write Edit Bash Grep Glob
---

# Correct

The user keeps correcting agents in this repo for the same mistakes. Change the repo so the next agent cannot make them.

## Port notes

| | |
|---|---|
| Source | poteto/pstack, `skills/correct/SKILL.md` |
| License | MIT |
| Credit | poteto (cursor/plugins/pstack; mirror backnotprop/pstack) |
| What changed | "Agent instruction file" mapped to this user's real enforcement points (lint, tests, Claude Code hooks in `.claude/settings.json`, pi extensions; docs last = `CLAUDE.md`, `.claude/rules/*.md`, `AGENTS.md`). Added When to Use, Anti-Patterns, Cross-References. Fires on user corrections, not only `/correct`. |

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

## When to Use

- The user says "/correct", "you keep doing X", "I told you this already", "make this impossible".
- **Every time the user corrects you**: fix the mistake, then run the rule-table step below.
- Periodic cleanup of a repo where agents repeat the same review comments.

## When NOT to Use

- A one-off mistake with no second occurrence: just fix it (a class needs two hits).
- A judgment preference with no checkable shape and no history: note it, wait for a repeat.

## 1. Find the mistake classes

Read recent commits, reverts, review comments, agent instruction files (`CLAUDE.md`, `.claude/rules/*.md`, `AGENTS.md`, `MEMORY.md`), session corrections, and comments that explain workarounds. Group the mistakes into classes. **A class counts once it has happened twice.**

## 2. Fix each class at the highest level that works

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete old ways and dead code an agent would copy.
2. **Enforce it with types** so the bad state cannot be written. If bad code still compiles, add a **lint, CI check, or hook** whose error message names the file, type, or function to use instead. If the pattern is already common, fail only when a change *adds more* (ratchet).
   - In this user's setup, a check can live in: the project linter/CI, a pytest test, a pre-commit hook, a Claude Code `PreToolUse`/`PostToolUse` hook in `.claude/settings.json` (use `update-config`), or a pi extension. Prefer the one that runs both locally and in CI.
3. **Test the behavior.** Fix or delete any test that would still pass if every function it calls returned nothing.
4. **Write docs or agent rules last, only for judgment calls.** Nothing fails when an agent skips them. Docs here means `CLAUDE.md`, `.claude/rules/<topic>.md`, or `AGENTS.md`, written per `asd-ste100`.

## 3. Fix and prove

- Fix the most frequent classes now, **one commit each**.
- **Prove each new check fails on a real past mistake** (check out or re-create the bad code, run the check, see it fail with the named fix). Then confirm it passes on the corrected code. This is RED-GREEN from `test-driven-development`.
- Run the same command locally and in CI.
- Exceptions go on the offending line with a **reason, an expiry date, and a human's approval**.

## 4. Keep the rule table

Keep a table in the repo's agent instruction file (`CLAUDE.md` or `.claude/rules/enforcement.md`) that pairs each rule with what enforces it:

```markdown
| Rule | Enforced by |
|---|---|
| Use Path.is_relative_to(), not str.startswith(), for path checks | ruff custom rule `JARVIS001` + tests/test_paths.py |
| Never commit .env | pre-commit hook `block-env` |
| Prefer small PRs | docs only (judgment call) |
```

When the user corrects you: fix the mistake **and** add the rule. If the rule was already there and nothing enforces it, that is a repeat - fix it at the highest level in the same change. **Drop a rule once its mistake cannot happen.**

**Reply:** each class with its evidence, the level you picked, and why a higher level did not work.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Adding a line to CLAUDE.md as the first fix | Nothing fails when an agent skips it | Climb: architecture, types, lint/hook, test; docs last |
| A lint error that says only "not allowed" | Agent guesses the workaround | Error names the file, type, or function to use instead |
| Failing the whole repo on a common pattern | Blocks unrelated work, gets disabled | Ratchet: fail only when a change adds more |
| Shipping a check never seen failing | It may never fire | Prove it fails on a real past mistake |
| Check runs locally but not in CI (or reverse) | Drift; one side ships the mistake | Same command in both |
| Silent exceptions | Rot back into the norm | Inline reason + expiry date + human approval |
| Tests that pass when every call returns nothing | Tests prove nothing | Assert real values; delete hollow tests |
| Rule table entry with no enforcer, on a repeat | The table becomes a wish list | Fix at a higher level in the same change |
| Treating one occurrence as a class | Over-engineering | Wait for the second hit |

## Cross-References

- **`test-driven-development`** - prove each new check fails first.
- **`update-config`** - writing Claude Code hooks into `.claude/settings.json`.
- **`asd-ste100`** - wording for any rule that has to stay a doc.
- **`engineering-principles`** - `principles/encode-lessons-in-structure.md`.
- **`evolving-cognition`** / **`skill-memory`** - record the lesson so future runs recall it.
- **`create-verification-skill`** / **`maintain-verification-skill`** - when the enforcer is itself a verification skill.
- **`blast-radius`** - before a large architecture fix that deletes "old ways".
