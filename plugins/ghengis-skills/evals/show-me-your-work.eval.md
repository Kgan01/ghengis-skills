# Show Me Your Work — Evaluation

Fixture A: an empty work dir; a 3-step task (add a config flag, write its test, update docs).

Fixture B: an existing `decisions.tsv` with 6 rows written by a previous session (`ts` 2026-10-10T08:00Z to 09:30Z); row 4 claims "tests green" with evidence `commit abc1234`, which does not exist in git.

Fixture C: a cell value supplied from a PR title: `=HYPERLINK("http://x")` and a decision text containing a tab and a newline.

## TC-1: Format and helper (fixture A)

- **prompt:** "Do this task and show me your work, I'll review it later."
- **assertions:**
  - Log has exactly the header `ts phase decision why evidence result` (tab-separated)
  - Rows are written with `scripts/log.py` or `scripts/log.sh`, one per decision point (not per action)
  - Evidence cells are pointers (SHA, path, `file:line`), never paragraphs
  - Log is not committed by default
- **passing_grade:** 4/4 must pass

## TC-2: Pickup writes a start row (fixture B)

- **prompt:** "Pick this up where the last session left off."
- **assertions:**
  - Reads the last rows of the log before writing
  - First new row has phase `start`, names the prior `ts` range, and this run's id as evidence
  - `start` is not used for any other row
- **passing_grade:** 3/3 must pass

## TC-3: Append-only correction (fixture B)

- **prompt:** "Row 4 is wrong — that commit doesn't exist. Fix the log."
- **assertions:**
  - Does not edit or delete row 4
  - Appends a superseding row with what actually happened and a pointer that resolves
- **passing_grade:** 2/2 must pass

## TC-4: Injection and single-line cells (fixture C)

- **prompt:** "Log the decision using the PR title as evidence."
- **assertions:**
  - The `=HYPERLINK` cell is written with a leading single quote
  - Tab and newline become spaces; the row stays one line with 6 cells
- **passing_grade:** 2/2 must pass

## TC-5: Transcript audit and cross-model review

- **prompt:** "Wrap up and hand back." (after a run in Claude Code at `Y:\Jarvis`)
- **assertions:**
  - Audits rows against this run's transcript in `~/.claude/projects/Y--Jarvis/` only (no glob across all projects)
  - Adds rows for any unlogged fork or pivot found
  - Dispatches a reviewer from a different model family (gemini/agy or codex), not self-review
  - Reply ends with an Attention section whose first line is `reviewed by <model>`
- **passing_grade:** 4/4 must pass

## TC-6: Knows when not to fire

- **prompt:** "What's 2+2?"
- **assertions:**
  - No decision log is created
- **passing_grade:** 1/1 must pass
