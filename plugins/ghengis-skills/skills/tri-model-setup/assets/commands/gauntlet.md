---
description: Gauntlet Loop — long-horizon polish of ANY existing deliverable through worker + blind-critic rounds until a reference-anchored bar is met (VERDICT WOWED)
argument-hint: <deliverable path or description> [-- <the bar>] [--rounds N]
---

Run a GAUNTLET LOOP on: $ARGUMENTS

The general topology (from JARVIS `agents/gauntlet.py` + the ADW wowed gates): a worker improves a deliverable, a **blind critic from a different model family** judges it against a **reference-anchored bar**, defects loop back verbatim, until WOWED or caps. Point it at anything — a web page, a module, a doc, a deck, a CAD part, a paragraph. This is a POLISH pass on something that exists; if nothing exists yet, build the MVP first (normal work or /adw), then gauntlet it.

## Setup (round 0)

1. **Identify the deliverable** — file path(s) preferred. Slug it; run dir `~/.claude/tri-model/gauntlet-runs/<slug>/`.
2. **Write the bar** (unless given after `--`): anchor to the best conceivable version of the SAME artifact, in concrete named attributes — "a $50,000 design-agency build of THIS site: commanding hero, Playfair over Inter, aged-paper #faf3df ground…" not "high quality". Include any hard truth/constraint rules (things that are an automatic fail). Save as `bar.md` in the run dir.
3. **Author deterministic checks** where the domain allows (existence, completeness/size, forbidden patterns, palette/lint/tests) as a small script in the run dir. They run FIRST each round, cost $0, and catch the class of bug a model critic shouldn't be spent on.
4. **TaskCreate**: one task for setup, one per round (created as you go), one for the final review. Statuses updated live.
5. Caps: default **9 rounds** (override via `--rounds N`). Never ask which models — worker is Claude (warm session or agent); critic is the `gemini` agent on **Pro** (`-Model pro`), a different family from the worker by construction; final reviewer prefers a third family (codex) when live.

## The loop (each round)

1. **Worker** improves the deliverable in place (same warm session each round so feedback compounds).
2. **Deterministic checks** via Bash. Any failure → the failure list IS the round's feedback; skip the critic (don't spend a critic call on a page that fails code checks).
3. **Blind critic** — the `gemini` agent, `-Model pro`, with ONLY: the bar + the WOWED protocol + the deliverable (as file path(s) via `-Cwd`/`--add-dir` — agy reads workspace files in print mode, so never inline large content). The critic is BLIND: no build history, no prior critiques, no round number — every round is a fresh judgement. Protocol, verbatim:
   > "You are a ruthless blind critic. FIRST read the deliverable in full; if you cannot fully read it, reply `VERDICT: BLOCKED` with the reason and stop — never judge an artifact you could not perceive. Judge against the bar: [bar]. Reply `VERDICT: WOWED` only if you can name ZERO material differences from that bar. Otherwise reply `VERDICT: NOT_WOWED` followed by `DIFFERENCES:` with one '- ' bullet per concrete, actionable flaw."

   `VERDICT: BLOCKED` (or no VERDICT line at all) is a **harness error, not a round**: fix the critic's perception (path, workspace dir, prompt size) and re-dispatch — don't count it against the round cap, and never fail over to a different critic family without saying so.
4. **Archive the round**: copy the deliverable to `round-N.<ext>` in the run dir; append `{round, verdict, n_defects, seconds}` to `metrics.jsonl`.
5. **WOWED** → exit loop. **NOT_WOWED** → feed the bullets back to the worker framed exactly as: "The blind critic found these DEFECTS in your previous version. They are flaws to REMOVE or RESOLVE — not features to add. Fix every one." (This framing prevents rounds from bloating the deliverable.)
6. Caps hit → stop honestly as **PARTIAL**: report the last defect list, never soften the verdict.

## Close-out

- **Fresh-eyes reviewer** (third family if live, else a fresh agent): compare round-1 vs final, verdict ship / don't-ship, anything that regressed. The reviewer never saw the loop.
- **Convergence report** `report.md` in the run dir: rounds table (verdict, defect count, what changed), the final defect list if PARTIAL, and the reviewer's read-out.
- Final message: outcome (WOWED at round N / PARTIAL), what materially improved, link to the run dir.

## Composes with

- `/adw` — gauntlet-shaped workflows (champion-gauntlet, site-page-gauntlet) run their loop as an ADW gate; this command is the free-standing general form.
- `/auto-validate` — gates prove a request is DONE; the gauntlet pushes a done thing until it WOWS. Done-ness first, then wow.
