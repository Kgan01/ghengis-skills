---
name: engineering-principles
description: Use when an engineering judgement call comes up mid-task - choosing types or data structures, placing validation, refactoring or migrating an API, debugging after fixes keep failing, writing or keeping a test, trusting a measured number, declaring work done, designing retries, sharing state between workers, or deciding whether to ask the human. TRIGGER on "what's the principle here", "first principles", "root cause", "prove it works", "is this test real", "make illegal states unrepresentable". Index of 24 principles; read one file per principle that applies.
allowed-tools: Read Grep Glob
---

# Engineering Principles

| Port notes | |
|---|---|
| Source | pstack (`github.com/backnotprop/pstack` clone) - `skills/principle-*/SKILL.md`, 24 skills |
| License | MIT, (c) 2026 Lauren Tan (poteto) |
| What changed | 24 separate skills folded into one index plus `principles/<name>.md`, so only the matching principle costs context. Bodies ported faithfully; links rewritten to sibling files. `laziness-protocol` defers to `ponytail` (canonical) and keeps only its four extra structural rules. `typescript-best-practices` reference replaced by ghengis language skills. |

Each principle is a short rule with a "why", a pattern and a test. Do not load them all. Scan the table, pick the rows whose **When it applies** matches the moment, and read only `principles/<name>.md` for those rows. Usually that is one or two files.

## How to use

1. At a decision point, scan the table below.
2. Read the matching `principles/<name>.md` in full before acting on it. The one-line rule is a pointer, not the principle.
3. When you cite a principle in a plan, review or commit message, apply its own test (each file ends with one). A principle cited with no evidence of its test was not applied.
4. Two principles conflict? Name both and say which one the situation favors. `experience-first` sets the target; `foundational-thinking` sets the order of work.

## Index

| Principle | Group | One-line rule | When it applies |
|---|---|---|---|
| `foundational-thinking` | Design | Get data structures and scaffold right first; downstream code becomes obvious | Choosing core types, sequencing scaffold vs feature, shared state between actors |
| `model-the-domain` | Design | Encode the domain in a structure, not scattered conditionals | Stateful logic, a growing if/else chain, a second boolean kept in sync |
| `type-system-discipline` | Design | Make illegal states unrepresentable; brand primitives; parse at boundaries; exhaust variants | Designing types, reviewing signatures, any typed language |
| `boundary-discipline` | Design | Validate at system edges, trust inside, keep logic pure | Wiring validation, error handling, framework adapters |
| `minimize-reader-load` | Design | Count layers to trace and state to hold; collapse one-caller wrappers | Code that is hard to trace, review of indirection |
| `exhaust-the-design-space` | Design | Build 2-3 real alternatives before committing | Novel UI or architecture with no precedent in the repo |
| `redesign-from-first-principles` | Design | Redesign as if the new requirement were there from day one | Integrating a new requirement into an existing design |
| `experience-first` | Design | Choose user delight over implementation convenience; ship less, better | Product, UX or feature-scope tradeoffs |
| `laziness-protocol` | Change | **Canonical: `ponytail` skill.** File adds flat call hierarchy, consolidated decisions, no signal threading, small leaks | Refactoring, judging diff size, tempted to add a layer |
| `subtract-before-you-add` | Change | Remove dead code and stubs first, then build | Sequencing an addition, refactor or rewrite |
| `migrate-callers-then-delete-legacy-apis` | Change | Migrate callers and delete the old API in the same wave | New internal API while old callers exist, no external users |
| `outcome-oriented-execution` | Change | Converge on the end state; no throwaway compatibility code | Planned rewrites and migrations with explicit phases |
| `sequence-verifiable-units` | Change | Small units, each ending in a checked state; commits ordered as proof | Sweeps, migrations, runs of similar edits, stacking commits/PRs |
| `build-the-lever` | Change | Build the script, codemod or delegate skill instead of hand-editing | Any non-trivial edit, migration, analysis or check |
| `make-operations-idempotent` | Change | Converge to the same end state after crashes, restarts, retries | Commands, lifecycle steps, processing loops |
| `separate-before-serializing-shared-state` | Change | Remove the shared write target first; lock only when one writer is a real invariant | Concurrent actors on one file, branch, key or state object |
| `fix-root-causes` | Verify | Reproduce, ask why until the cause, no silencing guards | Any debugging |
| `attack-the-premise` | Verify | After 2+ fixes on one premise fail, write the premise down and take a census | Repeated fixes failing the same gate |
| `prove-it-works` | Verify | Check the real artifact, not a proxy; script the check | Before declaring any task done |
| `explain-the-number` | Verify | Name the limiter and rule out what else the number measures | Trusting, reporting or acting on a speedup, latency, eval score |
| `test-behavior-not-implementation` | Verify | Assert observed results against literals; delete tests that pass when imports return undefined | Writing, changing or keeping a test |
| `guard-the-context-window` | Agent | Route bulk to subagents; keep summaries in the main thread | Large outputs, long files, fan-out planning |
| `never-block-on-the-human` | Agent | Proceed on reversible work, present, let the human correct; confirm only irreversible actions | Tempted to ask "should I do X?" |
| `encode-lessons-in-structure` | Agent | Turn a repeated instruction into a lint, flag, check or script | Same correction a second time |

## Harness notes

- Delegation in any principle (`build-the-lever`, `guard-the-context-window`): dispatch a subagent (Claude Code: Agent tool; pi: subagent tool). Write the shared recipe as a skill or file outside the delegates' write scope.
- `exhaust-the-design-space` with real stakes: build the alternatives in parallel with `agent-teams`, or get independent designs from the tri-model legs via `/opinion` (see `tri-model`). Talk the options through with `brainstorming` first if the intent is unclear.
- `encode-lessons-in-structure` routing: one-off lessons go to `skill-memory` or `evolving-cognition`; recurring fixes become a skill (`writing-skills`) or a lint.
- `never-block-on-the-human` never overrides the harness permission system or a confirm gate a skill sets for irreversible or paid actions.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Reading all 24 files up front | Burns context for rules that do not apply (violates `guard-the-context-window`) | Read only the rows that match |
| Acting on the one-line rule alone | Loses the "when it doesn't apply" and the test | Open the principle file before applying it |
| Citing a principle as a label ("per build-the-lever") with no artifact | Name-dropping is not applying | Show the test result or the artifact (script, census, profile) |
| Copying ponytail's rules into laziness-protocol work | Two sources drift | `ponytail` is canonical; the file only adds the four structural rules |
| `exhaust-the-design-space` on a bug fix with a clear target | Wastes effort where one approach is dictated | Check its "when it doesn't" list |
| `never-block-on-the-human` used to skip a confirm on push, delete or send | Irreversible actions still need confirmation | Proceed only on reversible work |

## Cross-References

- **`ponytail`** - canonical smallest-change discipline; owns `laziness-protocol`.
- **`test-driven-development`** - practice behind `sequence-verifiable-units` (failing test first) and `test-behavior-not-implementation`.
- **`systematic-debugging`** - method for `fix-root-causes`; escalate to `attack-the-premise` after repeated failures.
- **`completion-enforcer`** - enforces `prove-it-works` before "done".
- **`benchmark-checklist`** - full procedure behind `explain-the-number`.
- **`show-me-your-work`** - committed audit trail for `prove-it-works` on big ports and migrations.
- **`blast-radius`**, **`correct`**, **`figure-it-out`**, **`interrogate`**, **`how`**, **`why`** - pstack workflow skills that apply these principles.
- **`create-verification-skill`** / **`maintain-verification-skill`** - the lever form of `prove-it-works` and `encode-lessons-in-structure`.
- **`oort-cascade`** / **`agent-teams`** - fan-out structures for `build-the-lever` and `exhaust-the-design-space`.
- **`brainstorming`** - before `redesign-from-first-principles` on unclear intent.
- **`evolving-cognition`** - where lessons from `encode-lessons-in-structure` land.
