---
name: figure-it-out
description: Use when a task is large, ambiguous, or long-running and no narrower skill fits - a big migration, an ambitious multi-part change, or work the user will review after stepping away. Designs an auditable playbook first, scales rigor to the stakes, runs a hypothesis loop, and logs decisions via show-me-your-work. TRIGGER on "/figure-it-out", "figure it out", "just handle it", "migrate all of X", "I'll check back later", "do the whole thing", or when no other skill's trigger matches the job.
allowed-tools: Read Write Edit Bash Grep Glob
---

# Figure It Out

When the task matches no playbook, design one. **The deliverable before any code is the workflow itself:** a sequence of phases that scales rigor to the task, runs the scientific method, and leaves a decision trail a human can audit after stepping away.

## Port notes

| | |
|---|---|
| Source | poteto/pstack, `skills/figure-it-out/SKILL.md` |
| License | MIT |
| Credit | poteto (cursor/plugins/pstack; mirror backnotprop/pstack) |
| What changed | "Read poteto-mode Principles" replaced by `engineering-principles`; principle skills mapped to `engineering-principles/principles/<x>.md`. `architect`/`arena` replaced by `brainstorming` + tri-model legs (`/opinion`). Fan-out via `agent-teams` / `oort-cascade`. Harness-neutral wording. Added When to Use, Anti-Patterns, Cross-References. |

## When to Use

- A large migration ("move all 100 components to the new styling system").
- An ambitious multi-part change with unknowns.
- Work the user reviews after stepping away (unattended or overnight runs).
- Nothing narrower fits. If `systematic-debugging`, `test-driven-development`, `blast-radius`, or `benchmark-checklist` covers the job, use that instead.

## Start

Open a todo list (Claude Code: TaskCreate; pi: its todo tool or a `TODO` section in the log). The **first item** is to read `engineering-principles` (its SKILL.md and the principles named below). Then add phases A-E as todos.

## Phase A: Frame

Ground first, then commit. Do not start the run until you can state:

- **Definition of done as a falsifiable predicate** (`principles/prove-it-works.md`).
- **Scope, quantified:** rough units and effort, plus the blockers grounding surfaced.
- **Rigor level, biased high.** One-way doors and high blast radius get more. Reversible low-stakes steps get less. **Rigor is gates and artifacts, not "try harder".**

Present the framing and tradeoffs before committing to a long run. Reversible work proceeds without waiting (`principles/never-block-on-the-human.md`), but **a multi-hour run earns one checkpoint** with the user.

## Phase B: Design the Workflow

Decompose into atomic, independently-landable units. **Sequence riskiest-unknown-first.** Scaffold and verification come before features (`principles/foundational-thinking.md`).

- **Build the verification harness before the work**, with the baseline captured from the pre-change state, so each check reads "old value vs new value". If the harness measures performance, vet it with `benchmark-checklist` first.
- **One-way-door design decisions:** run `brainstorming`, and get independent opinions from the tri-model legs (`/opinion`, or dispatch the `gemini` subagent and `codex exec` per `tri-model`; Claude judges). Skip this for mechanical work whose shape is already concrete. A second multi-model round over a settled design is over-engineering (`principles/laziness-protocol.md`).
- **Decide what fans out.** Parallelize only across seams, and give each worker its own worktree or branch (`principles/separate-before-serializing-shared-state.md`). Do not over-fan. Use `agent-teams` for parallel peers or `oort-cascade` for a dependency DAG.
- **Write the designed phase list down.** That list is what the human reviews.

Then execute the design: add its steps to the todo list as concrete items, after the Phase C entry and before Phase D. Run each under the Phase C loop discipline, and weave the Phase D log through them - **a row as each step lands**, not the whole trail at the end.

## Phase C: Run the Loop

Each unit is an experiment. **State the hypothesis, make the smallest change, measure against the predicate on the real artifact, keep it if it advanced, revert it if it did not.** Verify each unit before starting the next instead of batching checks at the end (`principles/sequence-verifiable-units.md`).

- **Verify by inspecting the artifact, never a self-report.** When something passes too easily, suspect the observation method before the system.
- **Pair delegated work with a judge.** When you dispatch a subagent (Claude Code: Agent tool; pi: subagent tool), a separate judge (ideally another model family per `tri-model`) checks its output. If a worker games the gate, reset and harden the contract. If the gate itself is wrong, fix the gate in its own change rather than routing around it.
- **A verdict is VERIFIED, NOT VERIFIED, or INCONCLUSIVE.** Inconclusive is not a pass. Do not hide a negative.

## Phase D: Keep the Audit Trail

Log the run via `show-me-your-work`. figure-it-out's work is usually ambitious enough to **commit the trail** so the reviewer can read it in the PR. The trail plus the diff is what lets the human come back and trust the work.

## Phase E: Verify and Hand Back

Check the whole against the Phase A predicate **on the real product, not just the harness.** Encode any recurring correction as a gate, lint rule, check, or script (`principles/encode-lessons-in-structure.md`; use `correct` for repeat mistakes).

**Reply:** the playbook you designed, the rigor level and why, the decision-trail path, what is verified against the predicate, and what is still open. Include the `show-me-your-work` Attention section.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Writing code before the workflow exists | No plan for the human to review; rigor not chosen | Phase A + B output first |
| Done defined as "looks good" | Not falsifiable; any end state passes | Predicate that can fail |
| "Rigor" meaning "try harder" | Nothing checkable changes | Rigor = gates and artifacts |
| Easy units first | Riskiest unknown surfaces late and sinks the plan | Riskiest-unknown-first |
| Harness built after the change | No baseline; cannot compare old vs new | Capture baseline before changing anything |
| Fanning out across shared state | Workers collide | Parallelize only across seams; one worktree each |
| Trusting a worker's summary | Self-reports lie | Inspect the artifact; separate judge |
| Routing around a wrong gate | Gate rots, next run is blind | Fix the gate in its own change |
| Treating INCONCLUSIVE as pass | Hides a negative | Report it as open |
| Logging the trail at the very end | Reconstructed history, gaps | Row as each step lands |
| Multi-model review of a settled, mechanical design | Waste | Reserve for one-way doors |

## Cross-References

- **`engineering-principles`** - read first; the principles cited above.
- **`show-me-your-work`** - owns the decision-trail format (Phase D).
- **`brainstorming`** + **`tri-model`** - one-way-door design decisions.
- **`agent-teams`** / **`oort-cascade`** - fan-out mechanics.
- **`benchmark-checklist`** - vet any perf harness before freezing it.
- **`blast-radius`** - before landing a wide unit.
- **`correct`** - turn recurring corrections into enforcement.
- **`test-driven-development`** / **`systematic-debugging`** - narrower skills to prefer when they fit.
