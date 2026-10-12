# Correct — Evaluation

Fixture A: a Python repo whose git log shows three reverts titled "fix: use Path.is_relative_to not startswith" across `tools/files.py`, `tools/upload.py`, `routes/static.py`; `CLAUDE.md` already contains "Use Path.is_relative_to() for path validation"; no lint rule or test enforces it. CI runs `ruff` and `pytest`.

Fixture B: same repo plus two review comments "don't import from brain._internal, use brain.UnifiedBrain" and one occurrence of "prefer small PRs".

## TC-1: Climbs above docs (fixture A)

- **prompt:** "/correct — agents keep using str.startswith for path checks."
- **assertions:**
  - Cites the three reverts as evidence the class happened at least twice
  - Notes the CLAUDE.md rule already exists with nothing enforcing it, so this is a repeat
  - Fixes at lint/test/hook level or higher, not by adding/rewording a CLAUDE.md line
  - Lint/check error message names the function to use instead (`Path.is_relative_to`)
- **passing_grade:** 4/4 must pass

## TC-2: Proves the check fails on a real past mistake (fixture A)

- **prompt:** same as TC-1
- **assertions:**
  - Runs the new check against a re-created past bad version and shows it failing
  - Shows it passing on the corrected code
  - Same command runs locally and in CI
- **passing_grade:** 3/3 must pass

## TC-3: Architecture first where possible (fixture B)

- **prompt:** "Make it impossible for agents to import brain internals."
- **assertions:**
  - Considers hiding internals (e.g. `__all__`, module privacy, import-linter rule) so the wrong import fails
  - Explains why a higher level did or did not work
  - One commit per class
- **passing_grade:** 3/3 must pass

## TC-4: Rule table and judgment calls (fixture B)

- **prompt:** "/correct everything you can find."
- **assertions:**
  - Maintains a table pairing each rule with its enforcer, in CLAUDE.md or `.claude/rules/*.md`
  - "Prefer small PRs" (one occurrence, judgment) is not turned into a hard check; it is docs-only or deferred
  - Any exception is inline with reason, expiry date, and human approval
- **passing_grade:** 3/3 must pass

## TC-5: Fires on a plain correction

- **prompt:** "You did it again — you used print() instead of logging. I've told you this before."
- **assertions:**
  - Fixes the immediate mistake
  - Checks whether a rule exists and whether anything enforces it
  - Proposes or adds an enforcement (lint rule such as ruff `T20`) rather than only an apology
- **passing_grade:** 3/3 must pass
