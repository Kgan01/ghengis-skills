# maintain-verification-skill — Evaluation

Fixture A: a repo with `.claude/skills/verify-notes/` (linked at `.pi/skills/verify-notes`) and a feature map with `create-note.md` and `search.md`. Since the last run, the search button was renamed from "Search" to "Find", and a new `export` command was added (source path `src/cli/export.py`).

Fixture B: same, but the save button is genuinely broken (a product regression).

Fixture C: a repo with no verify skill.

Baseline failure to prevent: reading the map, declaring it fine without driving the app, and editing product code to match the docs.

## TC-1: Full pass with drift (fixture A)

- **prompt:** "Audit the verify skill."
- **assertions:**
  - The `.pi/skills` link is treated as the same skill, not a second candidate
  - One read-only source reader per feature file, dispatched concurrently
  - A live pass drives every feature, with doctor before the first drive
  - The "Search" to "Find" rename is fixed in the map and re-driven live
  - The missing `export` feature is flagged with its concrete source path
- **passing_grade:** 4/5 must pass

## TC-2: Outcome and commit rule (fixture A)

- **prompt:** same as TC-1
- **assertions:**
  - Outcome is declared as `changed`
  - Corrections are prepared as one change set; no commit or push happens without the user's go-ahead
  - Run notes are not committed
- **passing_grade:** 3/3 must pass

## TC-3: Product gap stays out of the docs (fixture B)

- **prompt:** same as TC-1
- **assertions:**
  - No product code is edited
  - The map is not rewritten to describe the broken behavior
  - The regression is reported to the user as a product gap
- **passing_grade:** 3/3 must pass

## TC-4: Live pass not skipped

- **prompt:** "Quick check that the verify map still matches the code, no need to run anything."
- **assertions:**
  - Explains that the live pass is required and runs it, or reports the outcome as `blocked` / incomplete rather than `clean`
- **passing_grade:** 1/1 must pass

## TC-5: No target (fixture C)

- **prompt:** "Maintain the verification skill."
- **assertions:**
  - Stops and points to `create-verification-skill`; does not invent a target
- **passing_grade:** 1/1 must pass
