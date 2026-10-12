---
name: ponytail-audit
description: Use when asked to audit a whole repo, folder, or package - not a single change - for bugs, security holes, what breaks under real load, risky code without tests, slow paths, and what to delete, merge or split. TRIGGER on "audit this codebase", "review the whole repo", "find bloat", "what can I delete", "what should I fix first", "ponytail audit", /ponytail-audit. Maps entry points and data flow first; ranked one-shot report; changes nothing.
allowed-tools: Read Bash Grep Glob
---

# Ponytail Audit

| Port notes | |
|---|---|
| Source | `DietrichGebert/ponytail` - `skills/ponytail-audit/SKILL.md`, `commands/ponytail-audit.toml` |
| License | MIT, (c) 2026 Dietrich Gebert |
| What changed | Big-repo fan-out uses harness-neutral subagents; optional code-graph shortcut via `code-intelligence`; ghengis cross-refs. Map-first order, finding format, 20-finding cap and footer unchanged. |

Audit the whole repo like the senior developer who just inherited it and will be paged when it breaks. Order of importance: correct, safe, holds under load, tested, fast, lean. Lean still matters: every extra line must be read, tested and fixed later. This is a report the user asked for, so give it in full.

## When NOT to Use

- One change, commit, branch or PR: use `ponytail-review`.
- Only the deferred shortcuts: use `ponytail-debt`.
- Pure security assessment with CVSS scoring: use `security-testing`.

## 1. Map first

- Audit what the user names: a folder, a package, or the whole repo. Nothing named: the whole repo.
- Read the README, the deploy and build config, the dependency list, the entry points (main, routes, handlers, jobs, CLI commands) and the tests.
- Find the expected load: one person running a script, or many users and processes at once. Judge scale against that, and say which load you assumed.
- Trace the main flows end to end: where data comes in, what is stored, what goes out. Read those paths fully: input from users, money, auth, data writes, background jobs, anything shared between processes.
- Big repo: go deep where a mistake costs the most, not file by file. Say which parts you did not read. A code graph (`code-intelligence`, or an existing `code-graph.json`) speeds up the entry-point and caller map.
- Fan-out is allowed for reading, not judging: dispatch a subagent (Claude Code: Agent tool; pi: subagent tool) per high-risk flow to return file:line facts. You confirm every finding yourself before it goes in the report.

## 2. Look for

1. **Bug:** wrong result, crash, missed edge case (empty, zero, last item, rounding, time zones), callers that disagree with what a function returns, the same rule applied differently in two places.
2. **Risk:** security holes (injection, weak randomness, secrets in code, missing checks on input from users), data loss (errors swallowed, writes in the wrong order, no transaction).
3. **Scale:** fine for one user, wrong for many: check-then-write races, the same work done by every process, memory or lists that only grow, a query per item, O(n^2) on big input, per-process state that must be shared.
4. **Missing test:** risky logic (a branch, a parser, money, security, data writes) with no test that fails when it breaks. One good test, not coverage.
5. **Speed:** big slowdowns are problems. Small wins (work repeated in a hot loop) are suggestions; some software counts every millisecond.
6. **Lean:** code that should not exist or should be smaller.
   - delete: dead code, unused options, flags and config, speculative features
   - reuse: two helpers doing the same thing (keep one, name the path)
   - stdlib / native: the standard library or platform already does it; a dependency doing what a few lines or the platform can do
   - yagni: interface with one implementation, factory with one product, wrapper that only passes calls through
   - merge: near-copies that must change together
   - split: one function or class doing several unrelated jobs, so it is hard to read or test. Split by job, never by line count, and never into helpers that exist only to make a function shorter.

## 3. Check before you report

- Every finding needs a concrete case: "this input or situation leads to this wrong result". No case, no finding.
- Before calling code unused, grep the whole tree for it, including tests, fixtures, config, and string or dynamic references.
- A shortcut marked with a `shortcut:` (or older `ponytail:`) comment that names its limit is a decision, not a finding, unless the expected load already crosses it.
- Propose the smallest fix that works. Prefer fixes that delete code. Never add layers, frameworks or config the problem does not need.
- No style taste, no "consider", no vague worries.

## 4. Output

Very simple English: short sentences, everyday words. Explain a technical term the first time you use it. The reader may never have seen this code.

Start with `What this repo does:` in two or three sentences, and the load you assumed.

Then the findings in three groups, most important first, skip empty groups:
- **Must fix:** bug, security, data loss, breaks at the expected load.
- **Should fix:** risky code without a test, real slowness, duplication, a function that mixes jobs, code that should not exist.
- **Nice to have:** small speed-ups, shorter forms.

Number findings across all groups, so the user can say "fix 2 and 5". At most 20 findings; if you left smaller ones out, say how many. Every finding has all four parts, each one or two short sentences: **What this is**, **Problem**, **Fix**, **If we skip it** - same shape as the example in `ponytail-review`, headed by a bold title and `file:lines`.

End with:
- `Verdict:` one line: healthy, or what to fix first.
- `Lean: -<N> lines, -<M> dependencies possible.` when lean findings exist.
- `Not checked:` the parts you did not read or could not run.

Nothing found: `What this repo does:`, then `Healthy. Nothing to fix.` and one line on what you checked.

One-shot report, changes no code.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Walking the repo file by file | Spends the budget on low-cost code; misses the money and auth paths | Map entry points and data flow, go deep where mistakes cost most |
| No stated load | Scale findings have no yardstick | Name the load you assumed in the opening |
| "Unused" without a full-tree grep | Dynamic, string, config or test references make it live | Grep everything, including fixtures and config |
| Silent coverage gaps | Reader assumes the whole repo was read | `Not checked:` lists every part skipped |
| 60 findings | The top three drown | Cap at 20, rank, count the left-outs |
| Trusting a subagent's finding unchecked | Fan-out reads are evidence, not verdicts | Re-read the lines and build the concrete case yourself |
| Fixing while auditing | One-shot report was asked for | Report; fix later under `ponytail` |

## Cross-References

- **`ponytail-review`** - the per-change version and the full finding example.
- **`ponytail`** - the discipline used to fix whatever the user picks.
- **`ponytail-debt`** - ledger of the `shortcut:` decisions this audit skips.
- **`code-intelligence`** - code graph for entry points, callers and god nodes.
- **`security-testing`** - deep pass when the Risk group dominates.
- **`blast-radius`** - tracing how far one finding's fix will reach.
- **`benchmark-checklist`** - before any Speed finding quotes a measured number.
