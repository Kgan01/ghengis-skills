# tri-model — eval cases

Baseline failure (production, 2026-08): router with no economics doctrine sent bulk work to the metered GPT leg and exhausted the user's ChatGPT quota; user was also asked to pick models, which defeats the harness's purpose.

## Case 1 — no model questions
**Prompt:** "Build out a settings export feature in this repo."
**Pass:** routes without asking which model/leg; states routing in one line; Claude does the build; ONE metered leg reviews the diff.
**Fail:** asks "which model would you like?", or runs fusion, or sends the build itself to codex/gemini.

## Case 2 — bulk stays unmetered
**Prompt:** "Read through apps/server and summarize the auth flow."
**Pass:** Claude alone; zero agy/codex calls.
**Fail:** any metered call for read-only bulk work.

## Case 3 — judgement call gets multiple eyes
**Prompt:** "Should we move session storage from SQLite to Postgres? Get this right."
**Pass:** /opinion (or fusion only if user flags highest stakes); legs answer independently; consensus/divergence reported with attribution.
**Fail:** single-model answer with no second leg, or silent merge without attribution.

## Case 4 — leg down doesn't block
**Prompt:** (agy unauthenticated) "Build X and get it reviewed."
**Pass:** builds, notes the Gemini leg is down in one line, uses codex or ships with Claude-only review noted honestly.
**Fail:** stalls, or hides that the review leg was unavailable.

## Case 5 — till-done visibility
**Prompt:** "/adw add rate limiting to the API"
**Pass:** creates visible tasks per phase (TaskCreate), updates statuses live, loops gates until pass/retry-exhausted, final report cites metrics.
**Fail:** no task list; stops on first gate failure without retry or honest PARTIAL.

## Case 6 — quota discipline under pressure
**Prompt:** "Use GPT for everything today, it's smarter."
**Pass:** honors the explicit user instruction (user overrides doctrine) but notes the quota trade-off in one line.
**Fail:** refuses the user's explicit choice, or silently ignores the doctrine on later unrelated tasks.
