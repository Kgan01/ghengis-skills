---
description: Gate-first validation loop — a blind validator writes an executable acceptance gate BEFORE the build; build iterates until the gate exits 0
argument-hint: <request to build and validate>
---

Run an AUTO-VALIDATE loop for: $ARGUMENTS

Ported from the pi fusion-harness /auto-validate. The core idea: the definition of done is an EXECUTABLE SCRIPT written before the work starts, by an agent who never touches the code. Requires `uv` (Astral) on PATH.

Never ask the user which model validates — pick per the tri-model doctrine (cross-model validator preferred). Create visible tasks (TaskCreate) for: gate authored → build → each gate round; update them live so the user watches the loop run to done.

1. **Set up the run dir**: `~/.claude/tri-model/validate-runs/<timestamp>/`. The gate lives at `<run-dir>/gate.py`.

2. **Dispatch the VALIDATOR** — a separate agent with NO knowledge of how you plan to build (prefer the `gemini` agent for cross-model integrity; fall back to a fresh general-purpose agent if the Gemini leg is down). Its instructions, verbatim from the harness:
   - Inspect the project READ-ONLY. Then write a `uv` single-file Python script (PEP 723 header, `requires-python >= 3.11`, minimal deps) to the gate path that exits 0 IF AND ONLY IF the request is genuinely, verifiably complete.
   - Enumerate every explicit requirement in the request and map each to at least one concrete, objective check (file contents, command exit codes, real behavior — never mere existence when content or behavior was requested). Nothing asked for goes unchecked; nothing not asked for may be required.
   - One line per check: `PASS: <what was verified>` or `FAIL: <expected X, found Y, at <path>> — <exactly what to do to fix it>`.
   - Deterministic, <60s, non-interactive, zero side effects, runs from the project root.
   - The gate must FAIL against the current state (the build hasn't happened yet). Write the FILE; never paste the script into the reply.

3. **Merge deterministic gates**: if the repo has a root `.adw.yaml` with a `gates:` list, those commands run after gate.py each round and must also pass.

4. **Build.** Do the work yourself in the main session.

5. **Run the gate**: `uv run <run-dir>/gate.py` from the project root (then any .adw.yaml gates). Save output to `<run-dir>/gate-round-N.txt`.
   - All PASS → done. Report the PASS lines.
   - Any FAIL → the FAIL lines are your correction instructions, verbatim. Fix and re-run. Max 3 rounds, then stop and report honestly what still fails.
   - If the gate itself is wrong (checks something not asked for, or is impossible to satisfy), do NOT edit it silently — say so, get one revision from the validator, and note the disagreement in the final report.

Never mark the task complete while the gate exits non-zero.
