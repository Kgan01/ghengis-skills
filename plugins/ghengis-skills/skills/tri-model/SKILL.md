---
name: tri-model
description: Use when building, fixing, reviewing, or deciding anything non-trivial on a machine with the tri-model harness (Claude Code host + agy Gemini leg + codex GPT leg). TRIGGER when the user describes work without naming a model, when a deliverable is about to ship with only one model's eyes on it, or on phrases like "build this out", "get this right", "second opinion", "run it through the legs". The user NEVER picks models — this skill does.
---

# Tri-Model Harness — Routing Doctrine

One rule above all: **the user talks about the work; the harness picks the models.** Never ask "which model should I use?" or "want me to run fusion?" — route by the table below and say what you routed in one line.

Baseline failure this skill exists to prevent (observed in production, 2026-08): a router with no economics doctrine sent bulk build work to the metered GPT leg and burned the user's entire ChatGPT quota in days, while the unmetered Claude leg sat idle. Model choice is an economics problem first, a capability problem second.

## The Legs

| Leg | Metering | Role |
|---|---|---|
| **Claude** (this session + Agent tool) | unmetered (Max sub) | ALL bulk labor: reading, building, editing, testing |
| **Gemini** (`gemini` agent → `agy`, Flash default) | metered, cheap (AI Pro) | second eyes: review, critique, tie-breaks. Pro only for deep judgement |
| **GPT** (`codex` CLI + plugin) | metered (ChatGPT sub) | adversarial review of finished work; rescue when Claude is stuck |

Availability check (only when in doubt): `agy models` / `codex login status` errors → leg is down; proceed without it and say so in one line. A missing leg never blocks work.

## Routing by Task Shape

| The work is… | Route |
|---|---|
| Reading, exploring, mechanical edits, docs | Claude alone. No metered tokens. |
| A normal feature/fix, done properly | Claude builds → ONE metered leg reviews the diff (default Gemini Flash; codex `adversarial-review` if the change is risky). This is mode B — the default. |
| A judgement call, architecture choice, "get this right" | /opinion (side-by-side, no merge) or, for the highest stakes only, /fusion (3x cost). |
| "Is it actually done?" / acceptance matters | /auto-validate — blind validator (prefer the gemini agent) writes the gate BEFORE the build. |
| A whole plain-language request to run end-to-end | /adw — router picks workflow + roster, phases run as agents, deterministic gates decide. |
| An EXISTING deliverable that should be elevated until it wows — "make this great", "polish this", long-horizon quality push | /gauntlet — worker + blind cross-family critic rounds against a reference-anchored bar (`VERDICT: WOWED`), deterministic checks first, defects loop back verbatim, caps → honest PARTIAL. Works on any artifact: page, module, doc, deck, CAD part. |
| Claude stuck after 2 real attempts | codex rescue (delegation, mode A). Note the handoff explicitly. |

## Till-Done Execution

The user wants to fire a request and watch it finish, not shepherd it:

1. **Make the work visible**: TaskCreate one task per phase/gate up front; mark `in_progress`/`completed` as you go. The task list IS the progress UI.
2. **Run until done**: a failing gate feeds its failure tail back to the builder (same agent, max 3 retries), then escalates roster or reports PARTIAL honestly. Never stop at "I ran into an issue" with tasks still open.
3. **Leave evidence**: every agy call auto-logs to `~/.claude/tri-model/agy-usage.jsonl`; ADW runs write envelopes + `metrics.jsonl`. Cite them in the final report.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Asking the user which model/leg to use | The whole point is that they don't choose | Route by table, state routing in one line |
| Bulk work on a metered leg | Burns quota that buys nothing (the observed failure) | Claude does bulk; metered legs get review-sized prompts |
| Fusion as the default for normal work | 3x cost, and three models rarely beat one at the same coding task | Fusion is for judgement calls the user flagged as high-stakes |
| Builder grading its own work | Self-review misses what a different model family catches | Cross-model review: builder on one leg, reviewer on another |
| Skipping the second leg to "save tokens" on a shipping deliverable | One Flash review costs ~nothing and catches real bugs | Mode B is the default, not an upgrade |
| Blocking because a leg is down | Availability ≠ permission to stall | Proceed with remaining legs, note the gap |
| Invisible progress on long runs | User can't see till-done momentum | TaskCreate per phase, update statuses live |

## Cross-References

- **`tri-model-setup`** — installs this rig on a machine that lacks it (agy, codex, wrapper, commands).
- Commands (global `~/.claude/commands/`): `/gemini`, `/opinion`, `/fusion`, `/auto-validate`, `/adw`, `/gauntlet`.
- **Gauntlet Loop lineage**: JARVIS `agents/gauntlet.py` (worker+blind-critic dyads, perception adapters) and the ADW wowed gates (deterministic-first, agy-preferred critic). The loop's two load-bearing framings: the critic is BLIND (fresh judgement every round, no history), and feedback is "flaws to REMOVE or RESOLVE — not features to add" (prevents rounds from bloating the deliverable).
- **`oort-cascade`** / **`agent-teams`** — Claude-internal orchestration; this skill decides which MODEL FAMILY, those decide which Claude agents.
- **`skill-chain-supervisor`** — chains may name a validator; prefer a cross-model one when the harness is present.
- Decision record: `~/.claude/tri-model/README.md` (why the harness is shaped this way).
- **Canonical routing catalog**: the "ADW Factory — Mix & Match Catalog" artifact + `~/.claude/tri-model/adw/` (`rosters.yaml`, `workflows/*.yaml`). Those YAMLs are the single source of truth for role→model assignments — when this skill and the YAMLs disagree, the YAMLs win. Edit models there, never in prose.
