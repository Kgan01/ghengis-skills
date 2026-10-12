---
name: benchmark-checklist
description: Use before you trust, report, or act on a performance number you measured - a speedup, a regression, a throughput, a latency, a before/after in a PR, a library or config choice, or an eval result. Vets the limiter, tuning, physical limits, errors, repeatability, relevance, and whether the work happened at all. TRIGGER on "it's X% faster", "benchmark this", "is this a regression", "which is faster", "compare A vs B performance", "measure the speedup", or any perf claim you are about to make.
allowed-tools: Read Bash Grep Glob Write
---

# Benchmark Checklist

A measured number is a claim about a system. Before you trust it, report it, or act on it, find what limits it and rule out that it measured something else.

## Port notes

| | |
|---|---|
| Source | poteto/pstack, `skills/benchmark-checklist/SKILL.md` + `skills/principle-explain-the-number/SKILL.md` |
| License | MIT |
| Credit | poteto (cursor/plugins/pstack; mirror backnotprop/pstack) |
| What changed | The explain-the-number principle is folded in (section below) so this skill stands alone. poteto-mode playbooks (Perf issue, Hillclimb, Opening a PR) mapped to `systematic-debugging`, `figure-it-out`, and `finishing-a-development-branch`. Added When to Use, Anti-Patterns, Cross-References. |

## The Principle: Explain the Number

**Why:** a run that went wrong still prints a plausible number. Requests that failed, a cache that skipped the work, code that never ran, a side left on default settings, and run-to-run noise all produce results that look fine. **If you cannot say why the number is not twice as good, you do not know what you measured.**

- **Ask "why not double?"** Name the resource or code path that bounds the result: a core, a lock, the disk, the network, or the load generator itself. Get it from a profile or system counters taken during a run, then map it to source. A guess from reading the code is not a limiter.
- **List what else the number could be measuring, and rule out each one with evidence.** Usual suspects: errors, skipped or cached work, an untuned side, noise, a piece too small to matter end to end.
- **Keep the evidence with the number.** Run count, spread, and limiter go in the notes or a linked artifact, so a reader can check the claim.

**For an eval result** (not perf), ask the same of the trials: did every run do the task, does the gap hold across trials and models, and does the scenario matter.

**You skipped this** when the evidence behind a number has no run count, no spread, or no named limiter, or when the time saved is larger than the time the changed piece took.

Distinct from `engineering-principles` `principles/prove-it-works.md`, which checks that an output is real. This checks that a measured number means what you say it means.

## When to Use

- You produce a performance number: a PR before/after, a regression claim, a hill-climb harness, a library or config choice.
- **Quick ballpark the user asked for:** one run is enough. Still check questions 4 and 7, and say it is one run. Skip the rest unless the run looks wrong. **A choice between options is never a ballpark.**

## Before You Run Anything

- **Write down the claim** you expect to make, in the words you would ship ("export is 30% faster at p50 on the 60k-row dataset"). The questions test that sentence.
- **Read the measurement script.** Note what it times, what it counts, and what it ignores.
- **Check machine load:** `uptime` and `nproc` (Windows: `Get-CimInstance Win32_Processor | Select NumberOfLogicalProcessors` and Task Manager / `Get-Counter '\Processor(_Total)\% Processor Time'`). If busy, find out what is running. If you cannot stop it, interleave the sides so both see the same noise, and say so in the report.

## The Questions

Answer each with evidence from a run, not from a guess about the code.

1. **Why not double?** Name the limiter. Profile in a run you do **not** report (profilers slow the work). Use CPU per process (`top`, `pidstat`), a runtime profiler (`node --cpu-prof`, `py-spy`, `perf`), I/O wait, and syscall counts (`strace -c` on Linux). Map the hot spot to source. Watch the load generator too: if it saturates first, you measured the load generator. If a change did not move the number, the limiter explains why - find it before calling the change useless.
2. **Was it tuned?** Run every side the way production runs it: release builds, production flags and env, batching and transaction settings, connection pools, caches as warm or cold as production sees them, same versions and data. If one side runs on defaults, you compared configurations, not implementations. A limiter that is a setting (a commit per row, a debug build, a missing index) means that side is untuned: tune it and measure again before picking a winner. If you cannot tune it, do not pick a winner from that run. Narrowing the claim to "the code as it ships today" does not fix this when the user is choosing what to adopt - they adopt the option, not today's settings.
3. **Did it break limits?** Do the arithmetic. Bytes/second vs disk and network bandwidth; ops/second x cost per op vs available cores. Compare time saved with the time the changed piece took: removing a piece that takes 10% of the run can make it at most ~11% faster. A result past a limit means the run measured something other than the work (a cache, a no-op, a bug).
4. **Did it error?** Count failures and non-success responses, and check outputs are **correct**, not just present. Rejections are often fast; timeouts and retries are slow. If the script does not count errors, add the count.
5. **Does it reproduce?** Run each side **at least 5 times**, alternating (A, B, A, B...) so warmup, lazy init, caches, and drift do not favor one side. Report **median and range**. A gap smaller than run-to-run variation is **no measurable difference**. When close, use a rank-sum test (e.g. `scipy.stats.mannwhitneyu`) or the harness's own statistics.
6. **Does it matter?** Next to any micro result, measure the end-to-end path a user waits on, with realistic data sizes and concurrency. Report the micro result as a share of the whole. A helper that takes 1% of a request can make the request at most 1% faster.
7. **Did it even happen?** Confirm the work ran inside the timed region: the request reached the server, rows were written, bytes were read, the code used the result. Lazy code (generators nobody iterates, promises nobody awaits, results the JIT discards) and timeouts all produce numbers for work that never happened.

## Report

- **Lead with the verdict:** faster, slower, no measurable difference, or inconclusive.
- **Number with unit, run count, range, limiter.** E.g. "p50 41 ms -> 33 ms, median of 7 runs per side, range 32 to 35 ms after, bound by JSON parsing on one core."
- **Call it inconclusive** when you claim a difference but cannot name the limiter, when a side ran untuned, or when you could not check questions 4 and 7. Name the gap.
- **PR body: one primary number.** Runs, range, and limiter evidence go in a linked artifact or notes file (see `finishing-a-development-branch`).

## How This Fits Other Perf Work

- **Finding and fixing slowness** (`systematic-debugging`, performance branch): this skill vets the baseline before you plan from it, and every number after that.
- **Hill-climbing one metric** (`figure-it-out` Phase C loop, or `gauntlet`): vet the harness with this checklist **before** freezing it. Make the frozen harness print error and work counts, so every keep-or-revert checks questions 4 and 7 for free.
- Long runs log each measurement row via `show-me-your-work`.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Reporting a number with no limiter | You do not know what was measured | Profile an unreported run; name the bound |
| Guessing the limiter from reading code | Code reading is not a measurement | Profile or counters during a run |
| One side on defaults | Compared configs, not implementations | Tune both to production settings, re-measure |
| Single run for an A-vs-B choice | Noise decides the winner | >= 5 alternating runs, median + range |
| Running all A then all B | Warmup/drift favors one side | Interleave A, B, A, B |
| Speedup larger than the changed piece's share | Physically impossible; measured something else | Do the arithmetic (Q3) |
| Ignoring error counts | Fast failures look like speedups | Count failures, verify outputs correct |
| Micro-benchmark only | Irrelevant to what the user waits on | Report as share of end-to-end path |
| Timed region contains un-awaited / lazy work | Number for work that never happened | Confirm side effects inside the timer (Q7) |
| "No difference" when gap < noise is called "slightly faster" | Overclaims | Say no measurable difference |

## Cross-References

- **`engineering-principles`** - `principles/explain-the-number.md` (same principle, shared form) and `principles/prove-it-works.md`.
- **`systematic-debugging`** - root-causing a slowness.
- **`figure-it-out`** - hill-climb loop and harness-before-work discipline.
- **`blast-radius`** - when a perf change could break behavior elsewhere.
- **`show-me-your-work`** - decision log for measurement runs.
- **`finishing-a-development-branch`** - PR body with one primary number.
- **`data-analysis`** - statistics for close calls.
