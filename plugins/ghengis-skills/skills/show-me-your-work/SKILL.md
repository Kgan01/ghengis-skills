---
name: show-me-your-work
description: Use when running long, unattended, autonomous, or multi-phase work that a human will review after stepping away, and the result needs a reviewable decision trail - a TSV log with one row per decision (what, why, evidence, result), audited against the transcript and reviewed by a second model family before hand-back. TRIGGER on "/show-me-your-work", "show your work", "keep a decision log", "audit trail", "I'll review it when I'm back", or when figure-it-out or another skill routes its trail here.
allowed-tools: Read Write Edit Bash Grep Glob
---

# Show Me Your Work

Keep one canonical decision log per run, prove it tells the truth, and get a second model family to flag what the user should look at.

## Port notes

| | |
|---|---|
| Source | poteto/pstack, `skills/show-me-your-work/` (SKILL.md, `scripts/log.sh`, `references/decision-log-template.tsv`) |
| License | MIT |
| Credit | poteto (cursor/plugins/pstack; mirror backnotprop/pstack) |
| What changed | Added `scripts/log.py`, a stdlib Python port of `log.sh` with identical output, so the helper runs on Windows without bash. Cursor transcript path removed; Claude Code, pi, and Codex paths kept. Cross-model review uses the tri-model legs. `unslop` replaced by `storyscope` then `humanizer`. Added When to Use, Anti-Patterns, Cross-References. |

## When to Use

- Autonomous, overnight, or multi-phase runs; work the user reviews later.
- Any skill that needs an audit trail (`figure-it-out` Phase D, `benchmark-checklist` measurement runs). **Other skills route their trail here instead of inventing one.** Reference this skill by name and let it own the format; do not restate the columns.

## When NOT to Use

- A short interactive task where the user watched every step.

## The Format

A single TSV file, one row per decision. **Cells stay single-line. Evidence is a pointer, not prose.** Copy `references/decision-log-template.tsv` (the header row) to start a clean log.

- **ts** - ISO8601 timestamp.
- **phase** - the phase or workstream.
- **decision** - what was chosen or done, one line.
- **why** - the reason in plain words. If a principle drove it, say it plainly, not as a jargon tag.
- **evidence** - a link or path that proves it: commit SHA, PR number, `file:line`, or an artifact, trace, or screenshot path. **Never a paragraph.**
- **result** - outcome or predicate state: `tests green`, `reverted`, `pixel-diff 0`, `INCONCLUSIVE`, `open`.

Example, plain-spoken so a reviewer reads it at a glance:

```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted the work first, about 100 components and roughly 75 hours	wanted to know the size before starting a long run	commit 3a9f1c2	found 5 things to sort out before starting
2026-05-24T09:40:00Z	harness	took screenshots of the old version before changing anything	so we can compare old against new and catch any visual change	scripts/snapshot.sh, baseline/	saved 120 reference screenshots
2026-05-24T11:15:00Z	widget	moved the widget styles over without changing how it looks	keep the change small and the result identical	commit 7c21e0a, pixel-diff 0	looks identical, tests pass
2026-05-24T12:30:00Z	widget	threw out a helper's work because its screenshots were blank	checked the real files instead of trusting its summary	worktree reset	reverted, tightened the instructions for next time
```

## Logging a Row

Write each entry the way you would tell a teammate what you did. Plain words, concrete actions, no AI speak or abstract jargon (`storyscope` / `humanizer` apply to log text too).

Use the helper (both produce identical rows):

```bash
python scripts/log.py <logfile> <phase> <decision> <why> <evidence> <result>   # any OS
bash   scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>   # POSIX / Git Bash
```

It stamps `ts`, writes the header on first use, creates the parent directory, strips stray tabs/newlines/CRs, and prefixes any cell starting with `=`, `+`, `-`, or `@` with a single quote (spreadsheet formula-injection guard). A bare `printf` append works too, but mind those same bytes if cells come from generated or user-supplied text.

**Log decision points and checkpoints, not every action:** a fork chosen, a unit completed with its verification result, a pivot or revert with its trigger, a blocker surfaced, a gate fixed. For loop runs, one row per iteration. Skip the trivial and self-evident.

### Runs and `start` rows

A **run** is one agent conversation, including its later turns and any summary of it. A pickup, a replacement agent, or a new chat starts a new run.

- When a run adds to a log that already has rows, its first row has phase `start` - and so does its first row after another run's `start` row.
- So a run that comes back to a log in a later turn **first reads the log's last rows** to see whether another run wrote since.
- A `start` row names the `ts` range of the rows before it that this run did not write, and its evidence names this run (e.g. its agent or session id).
- Use phase `start` for nothing else.

## Where It Lives

By default the log is a **working artifact, not committed.** Keep it at `decisions.tsv` in the work dir, or `.audit/<task-slug>.tsv` when several efforts run at once, and leave it out of git. **Commit it only** when the work is ambitious enough that a reviewer needs the trail to trust the result.

## Rules

- **Append-only.** A wrong call gets a new row that supersedes it. Never edit or delete history.
- Prefer evidence produced by committed scripts over hand-made one-offs (`engineering-principles` `principles/encode-lessons-in-structure.md`).

## Audit the Log Against the Transcript

At the end of the run, before handing back, check the log told the truth. Read **this run's** transcript from the active workspace's session directory:

- **Claude Code:** `~/.claude/projects/<slug>/` (workspace path with every non-letter, non-digit character turned into `-`; e.g. `Y:\Jarvis` -> `Y--Jarvis`).
- **pi:** `~/.pi/agent/sessions/--<slug>--/`.
- **Codex:** the `~/.codex/sessions/` file whose first line has `payload.cwd` equal to the workspace path.

**Do not glob across every project's directory** - that reads unrelated private chats.

Walk this run's rows against what actually happened. Each stretch begins at one of this run's `start` rows (or the first row, if this run created the log) and ends at the next `start` row of another run:

- Every row maps to a real decision or action.
- Each row's evidence resolves and shows what the row claims.
- A fork, pivot, or abandoned approach that shaped the work but is not logged is a gap. Add it.

**Correct the log, not the story.** The audit never edits or removes a row, even an invented one. When a row records neither a real decision nor a real action, or its claim or evidence is wrong, add a row that supersedes it with what actually happened and a pointer that resolves. The audit does not check rows outside this run's stretches; if this run's own work shows one is wrong, supersede it like any wrong call.

## Cross-Model Review of the Trail

Before handing back, dispatch a reviewer on a **different model family** from the one that did the work. **Self-review is not a substitute.** Per `tri-model`: if Claude did the work, use the Gemini leg (Claude Code: `gemini` subagent; pi: shell `agy`) or the GPT leg (`codex exec`). If another leg did the work, Claude reviews. The reviewer reads the trail and the run's transcript and flags what the user should pay attention to - not a redo of the work, a scan for what is suboptimal or risky:

- Decisions logged with weak or absent evidence.
- Verification steps skipped or claimed without proof in the transcript.
- Choices that look risky in hindsight (premature, scope-creeping, papering over a symptom).
- Gaps the user would miss on a casual skim.

**Every reply for a run that produced a trail ends with an "Attention" section.** Lead with the reviewer's model on its own line (`reviewed by <model>`), then list each flag pointing to specific rows or moments. "No flags" is a valid value. The model name is not optional. If no other leg is available, say `reviewed by: none available (<leg> down)` - never substitute self-review silently.

## Reviewing the Trail

Read top to bottom, follow the evidence pointers, spot-check. GitHub renders a committed TSV as a table. In a terminal: `column -s$'\t' -t decisions.tsv`; in PowerShell: `Import-Csv decisions.tsv -Delimiter "`t" | Format-Table`.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Paragraphs in the evidence cell | Unverifiable, breaks the table | A SHA, PR, `file:line`, or path |
| Logging every action | Signal drowns | Decision points and checkpoints only |
| Editing or deleting a wrong row | Destroys the audit | Append a superseding row |
| Writing the whole log at the end | Reconstructed, gaps | Row as each step lands |
| Skipping the `start` row on pickup | Rows from two runs blur | `start` row with prior `ts` range + this run's id |
| Globbing all session directories | Reads unrelated private chats | Only this workspace's directory |
| Same model reviewing its own trail | Shares its blind spots | Different model family via tri-model legs |
| Omitting the Attention section or reviewer name | User cannot tell it was reviewed | Always end with it; "No flags" is fine |
| Committing every log by default | Noise in git | Commit only when the reviewer needs it |
| Raw `printf` of untrusted text | Tabs break rows; `=` cells run as formulas | Use `log.py` / `log.sh` |

## Cross-References

- **`figure-it-out`** - routes its Phase D audit trail here.
- **`benchmark-checklist`** - measurement runs log one row each.
- **`tri-model`** - which leg reviews the trail.
- **`audit-ledger`** - hash-chained ledger for JARVIS agents; this skill is the human-readable trail for coding runs.
- **`engineering-principles`** - `principles/encode-lessons-in-structure.md`.
- **`storyscope`** then **`humanizer`** - plain log text.
