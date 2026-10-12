# Ponytail Audit — Evaluation

Fixture A: a warehouse-stock FastAPI repo (~2k lines). `routes/batch.py` runs one DB query per row. `importer.py` uses `except Exception: continue`, which silently skips bad CSV rows. `utils/dates.py` and `helpers/time_utils.py` hold near-identical `parse_day()`. `legacy/export_v1.py` is referenced only by a string in `jobs.yaml`. `importer.py` has no tests. README: "used by 3 offices, batches up to 1,200 items".

Fixture B: a 50k-line monorepo; the user names `packages/billing/` only.

## TC-1: Maps before judging (fixture A)

- **prompt:** "Audit this codebase."
- **assertions:**
  - Opens with `What this repo does:` and the assumed load (3 offices, batches to 1,200)
  - Shows it read the entry points / routes and the import flow before the findings
  - Silent row skipping in `importer.py` reported as Must fix (data loss)
  - Query-per-row in the batch route reported as a scale finding tied to 1,200-item batches
- **passing_grade:** 4/4 must pass

## TC-2: "Unused" needs a full-tree grep (fixture A)

- **prompt:** "What can I delete?"
- **assertions:**
  - Does NOT call `legacy/export_v1.py` dead without noting the `jobs.yaml` string reference
  - Reports the duplicate `parse_day()` as a merge finding and names which path to keep
  - Ends with `Lean: -<N> lines, -<M> dependencies possible.`
- **passing_grade:** 3/3 must pass

## TC-3: Output contract (fixture A)

- **prompt:** "ponytail audit"
- **assertions:**
  - Findings grouped Must fix / Should fix / Nice to have, numbered across groups
  - Every finding has What this is / Problem / Fix / If we skip it
  - At most 20 findings; the left-out count is stated if any
  - Ends with `Verdict:` and `Not checked:`
  - Makes no file edits
- **passing_grade:** 5/5 must pass

## TC-4: Scope respected (fixture B)

- **prompt:** "Audit packages/billing for me."
- **assertions:**
  - Findings stay inside `packages/billing/` (outside callers cited as evidence only)
  - `Not checked:` names what was not read
- **passing_grade:** 2/2 must pass

## TC-5: Knows when not to fire

- **prompt:** "Review my last commit."
- **assertions:**
  - Routes to the per-change review (`ponytail-review`), not a whole-repo audit
- **passing_grade:** 1/1 must pass
