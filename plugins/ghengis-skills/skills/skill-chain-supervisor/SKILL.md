---
name: skill-chain-supervisor
description: Use when orchestrating multiple ghengis-skills across a single task -- coordinates pre-action validation, execution, post-action verification, and lesson extraction via a shared JSON scratchpad. TRIGGER when dispatching a subagent, finishing a major task, or when the user mentions "run the full chain", "validate this", "fire the pipeline", or explicitly invokes a chain by name.
allowed-tools: Read Write Edit Bash
---

# Skill Chain Supervisor

Orchestrates ghengis-skills into reliable workflows. Instead of invoking one skill at a time, you run a pre-defined **chain** — a sequence of skills that share state through a JSON scratchpad, enforce dependencies, and produce verifiable results.

## When to Use This Skill

- **Dispatching a subagent** — run the `agent-dispatch` chain for PQL validation, completion enforcement, and hallucination checking
- **Finishing a major task** — run the `task-complete` chain to verify + record + learn
- **Producing a deliverable that needs to actually work** — run the `build-validate` chain for a hard-gated Builder ↔ Validator round-trip
- **Shipping a new feature** — run the `feature-build` chain (brainstorming → TDD → build-validate)
- **Fixing a bug responsibly** — run the `bug-hunt` chain (systematic-debugging → TDD → build-validate)
- **Creating or porting a skill** — run the `skill-port` chain (brainstorming → writing-skills → pql-validation → build-validate)
- **Wrapping up implementation work** — run the `finish-line` chain (finishing-a-development-branch → auto-project-sync → audit-ledger)
- **Starting research** — run the `deep-research` chain (deep-research → fact-check → report-writing)
- **User explicitly asks** — "run the full chain on this" / "validate thoroughly" / "use the pipeline"

## Core Model

```
Event or user request
    ↓
Supervisor reads chain spec (chains/<name>.md)
    ↓
Writes initial state to <project>/.claude/ghengis-chain/context.json
    ↓
For each stage in chain:
    → Invoke skill (via Skill tool)
    → Skill reads scratchpad, does work, writes namespaced output
    → Supervisor advances stage marker
    ↓
Report final state
```

## Execution Rules

1. **Sync, blocking.** Each stage completes before next begins — except where `parallel: true`.
2. **DAG only.** No cycles. A chain that needs iteration must declare `pattern: loop` with a `max_iterations` cap.
3. **Rules authoritative at chain-entry.** If a skill learns something mid-chain (e.g. `evolving-cognition` extracts a new rule), it writes to the rule file. The NEXT chain invocation sees it — not the current one.
4. **Parallel-safe when:**
   - No two parallel skills write to the same scratchpad key
   - No parallel skill reads a key another parallel skill is still writing
5. **Fail-fast** unless chain declares `on_error: skip`. If a skill's output indicates failure, stop and report.

## Scratchpad Schema

Single JSON file at `<project>/.claude/ghengis-chain/context.json`:

```json
{
  "chain": "agent-dispatch",
  "started_at": "2026-04-20T13:00:00Z",
  "current_stage": "completion-enforcer",
  "stages_completed": ["pql-validation", "meta-prompting", "<execution>", "completion-enforcer"],
  "stages_remaining": ["hallucination-detector", "audit-ledger"],
  "input": {
    "user_request": "...",
    "target_agent": "general-purpose"
  },
  "pql_validation": {
    "score": 0.78,
    "anti_patterns_found": [],
    "fixes_applied": ["added role", "added deliverable"]
  },
  "meta_prompting": {
    "role_selected": "builder",
    "template_applied": "..."
  },
  "completion_enforcer": {
    "status": "done",
    "concerns": []
  },
  "hallucination_detector": {
    "fabricated_urls": [],
    "unsourced_stats": []
  },
  "audit_ledger": {
    "entry_id": "abc123",
    "hash": "sha256:..."
  }
}
```

**Namespacing rule:** Each skill writes to a subkey matching its own name (underscores, not hyphens). Never overwrite another skill's subkey.

**Read rules:** Any skill may read any subkey. Read freely.

## How to Run a Chain

1. **Identify the chain name** (`agent-dispatch`, `task-complete`, `feature-build`, etc.)
2. **Read the chain spec** at `chains/<name>.md` inside this skill's directory
3. **Cognition opt-in (inline prompt)** — BEFORE initializing the scratchpad:
   - If `GHENGIS_COGNITION=true` is already set in the environment, **skip this step** (always-on mode). Treat cognition as enabled for the rest of the chain.
   - Otherwise, ask the user inline, in chat: **`Run cognition on this chain? [y/N]`** — one short line, no preamble.
     - If they answer `y` / `yes` (case-insensitive): treat cognition as enabled for this chain run.
     - If they answer `n` / `no` / Enter (default) / anything else: treat cognition as disabled for this chain run.
   - Whichever way the decision lands, propagate it to every `scratchpad.py` invocation in this chain by prefixing the command with `GHENGIS_COGNITION=true` (when enabled) or `GHENGIS_COGNITION=false` (when disabled). Don't rely on the user's shell environment — set it explicitly per-call so the answer follows the chain.
   - Persist the choice into the scratchpad as `state["cognition_optin"]` so subagents reading the scratchpad can see whether to expect lessons / write contributions.
4. **Initialize scratchpad** — `GHENGIS_COGNITION=<cognition_flag> python scripts/scratchpad.py init <chain_name> --input-json '{...}'`. When cognition is enabled, init also performs UCB1 retrieval and populates `state["lessons_from_past"]`.
5. **Execute each stage:**
   - Read scratchpad to see prior stages' output: `python scripts/scratchpad.py read <dotted.path>`
   - Invoke the stage's skill (via Skill tool) with scratchpad context
   - After skill returns, update scratchpad: `merge`, `write`, or `advance` as appropriate (see Scratchpad Helper section)
6. **For nested chain stages** (e.g., `feature-build` → `build-validate`): wrap the nested run with `python scripts/scratchpad.py nested-start <nested>` and `nested-finish <nested>`. The nested chain's output stays namespaced under `<nested>.*` in the parent scratchpad. The cognition opt-in is **inherited from the parent** — do NOT re-prompt for nested chains.
7. **At chain end** — call `GHENGIS_COGNITION=<cognition_flag> python scripts/scratchpad.py finish`. This writes `completed_at`, archives to `<project>/.claude/ghengis-chain/history/<chain>-<ts>.json`, and (if cognition is enabled) emits a structured cognition entry to `cognition.jsonl` derived from the chain's outcome, score, and issues. **The cognition write defaults to project scope** (`<project>/.claude/cognition.jsonl`) — that's almost always what you want. Pass `--scope global` only when you know up front the lesson generalizes across projects. If cognition is enabled, dispatch the `ghengis-skills:analyzer` subagent next to replace the heuristic entry with a high-quality causal lesson (see "The Analyzer Subagent" section).

## Built-in Patterns

Chains declare their execution pattern. Four supported:

### Sequential
Each stage runs strictly after the previous. Simplest, safest.

### Fan-Out / Merge
Multiple skills run in parallel, then a merge step collates their outputs.
```yaml
- stage: parallel-checks
  parallel: true
  skills: [hallucination-detector, pql-validation, context-health]
- stage: merge
  skill: chain-merger
```

### Conditional Routing
Next stage depends on prior output.
```yaml
- stage: pql-validation
- stage: auto-fix-or-proceed
  if:
    "pql_validation.score < 0.5": invoke prompt-autofix
    else: skip
```

### Iterative Loop
Repeat a stage until condition or cap.
```yaml
- stage: refine
  loop:
    max_iterations: 3
    until: "pql_validation.score >= 0.8"
```

### Nested Chain

A stage can invoke another chain instead of a single skill. The nested chain's scratchpad output is **namespaced under the nested chain's name (underscored)** so it doesn't collide with the parent chain's own subkeys.

```yaml
- stage: validate-via-build-validate
  chain: build-validate   # invokes the build-validate chain
  # Nested writes go under `build_validate.*` in the parent scratchpad:
  #   build_validate.triage
  #   build_validate.build
  #   build_validate.validate
  #   build_validate.report
```

**Rules for nesting:**

- The nested chain's top-level subkeys (`triage`, `build`, etc.) are remapped under `<nested_chain_name>.*` in the parent scratchpad — they are NOT promoted to parent top-level.
- The parent chain can read the nested result via `<nested_chain_name>.report.outcome` (or any other nested subkey).
- One level of nesting is supported. Deeper nesting is allowed but discouraged — flatten when reasonable.
- The parent's `pattern` field describes the parent's own execution shape; nested chains inherit their own pattern from their spec.

### Per-Stage on_error Override

The frontmatter `on_error: fail_fast` is the chain default. Individual stages can override it when they are non-blocking (e.g., audit-ledger should not fail-fast the chain if its append fails):

```yaml
- stage: audit-ledger
  skill: ghengis-skills:audit-ledger
  on_error: skip   # non-blocking; record the gap but continue
```

Use this sparingly. Most stages should respect the chain default.

## Trigger Precedence

When a user message matches keywords in multiple chains, resolve in this order:

1. **Exact chain name** (`run build-validate`, `run skill-port`, `feature-build`) — always wins. The user named the chain explicitly.
2. **Specific compound phrase** (`build a feature`, `fix this bug`, `port a skill`, `ship this branch`) — these are deliberately distinctive and unambiguous.
3. **Generic phrase fallback** — if the message says "build" or "ship" or "validate" without context, ask before firing a chain. Generic phrases were removed from the trigger keywords precisely because they fire too often.

If multiple specific matches are still ambiguous (rare), the precedence is:

| Situation | Preferred chain |
|---|---|
| New code that ships | `feature-build` |
| Existing code is broken | `bug-hunt` |
| Existing code is finished and needs integration | `finish-line` |
| New skill being added | `skill-port` |
| Just need an adversarial review of a deliverable | `build-validate` |
| Just need to fire-and-forget verification at session end | `task-complete` |
| Dispatching a subagent | `agent-dispatch` |

When in doubt, ask: "this could be `feature-build` or `bug-hunt` — is it new code or a fix?". Never silently fire the wrong chain.

## Defining a New Chain

Create a file at `chains/<name>.md` with frontmatter + stages:

```yaml
---
name: my-chain
pattern: sequential
triggers:
  - event: user_request
    keywords: ["deploy", "ship it"]
on_error: fail_fast
---

## Purpose
One-sentence description.

## Stages

1. **stage-name** — skill: `ghengis-skills:skill-name`
   - Inputs (scratchpad keys read): [...]
   - Outputs (scratchpad keys written): [...]
   - Success criteria: [...]
```

## Available Chains

See `chains/` directory. As of v1.12.0:

- **agent-dispatch** — wraps a subagent spawn with PQL → meta-prompting → execution → completion → hallucination → audit
- **task-complete** — post-response verification (completion + hallucination + audit). Lighter than agent-dispatch; fires on Stop events.
- **build-validate** — minimum-viable cascade: Builder ↔ Validator round-trip with hard-gated revision loop (max 2 iterations). Triage stage skips trivial tasks. Promotes oort-cascade's revision pattern from recipe to enforced stages.
- **feature-build** — ship a new feature: brainstorming → test-driven-development → build-validate. Brainstorming captures intent + execution mode (inline / subagent / build-validate); TDD writes failing tests first; build-validate runs the full revision loop.
- **bug-hunt** — fix a bug responsibly: systematic-debugging → test-driven-development (regression test) → build-validate. Iron law: no fixes without root cause. Validator confirms regression test passes AND no other tests broke.
- **skill-port** — create or port a skill: brainstorming → writing-skills → pql-validation → build-validate. PQL gates description quality; build-validate stress-tests the skill against pressure scenarios.
- **finish-line** — wrap up integration: finishing-a-development-branch → auto-project-sync → audit-ledger. Verifies tests, presents merge/PR/cleanup options, updates CLAUDE.md/MEMORY.md, records immutable audit entry.

## Continuous Execution Principle

Chains beyond v1.8.x respect the **continuous execution principle**: the supervisor does NOT pause between stages to ask "should I continue?" Each chain has natural decision points built into its stages (brainstorming asks design questions; build-validate has the revision loop; finishing-a-development-branch presents integration options). Outside those, drive forward. The user can interrupt at any moment to redirect.

## Scratchpad Helper

Skills participating in a chain should use `scripts/scratchpad.py` for reliable reads/writes. Stdlib-only; no deps.

### Chain Lifecycle

```bash
# Bootstrap a fresh chain (refuses to clobber an in-flight chain unless --force)
python scripts/scratchpad.py init feature-build --input-json '{"user_request":"add /health endpoint"}'

# Archive scratchpad to history/ and (if GHENGIS_COGNITION=true) emit a cognition entry
python scripts/scratchpad.py finish
```

### Read / Write / Advance

```bash
# Read a subkey (supports dotted paths)
python scripts/scratchpad.py read pql_validation.score
python scripts/scratchpad.py read build_validate.report.outcome

# Write a value at a dotted path
python scripts/scratchpad.py write pql_validation.score 0.85

# Merge a JSON object into a (possibly nested) subkey — stdin = JSON object
echo '{"score":0.85,"anti_patterns":[]}' | python scripts/scratchpad.py merge pql_validation
echo '{"score":9}' | python scripts/scratchpad.py merge build_validate.validate

# Advance the chain stage pointer
python scripts/scratchpad.py advance

# Full dump or path inspection
python scripts/scratchpad.py dump
python scripts/scratchpad.py path
```

### Nested Chain Support

When a chain invokes another chain as a stage, use these helpers to namespace correctly:

```bash
# Allocate the nested chain's subkey (creates state["build_validate"] = {_nested_status: running})
python scripts/scratchpad.py nested-start build-validate

# After the nested chain's stages run (writing to build_validate.triage, .build, .validate, .report)
python scripts/scratchpad.py nested-finish build-validate
```

The nested chain's own scratchpad commands write to `state["build_validate"]["..."]` — never colliding with the parent's top-level subkeys.

### Cognition: emit, retrieve, audit

The cognition loop is **opt-in** per-chain. Two ways to enable it:

- **Inline prompt (default UX, recommended for ad-hoc decisions):** the chain's entry sequence asks `Run cognition on this chain? [y/N]` before init (see step 3 of "How to Run a Chain"). The user's answer is propagated as the `GHENGIS_COGNITION` env var to every `scratchpad.py` invocation for that chain run, and persisted as `state["cognition_optin"]` in the scratchpad.
- **Always-on env var:** export `GHENGIS_COGNITION=true` in the shell environment to skip the inline prompt and always emit/retrieve. Useful once a user has decided cognition is worth it everywhere.

Whichever path enables it, three things happen automatically:

1. **Init reads** — `scratchpad.py init` finds relevant past lessons in `cognition.jsonl` using **UCB1-weighted Jaccard similarity** (balances exploitation of proven entries with exploration of untested ones). Top 5 lessons land at `state["lessons_from_past"]` for stages to consult. Bumps each surfaced entry's `hits` counter.
2. **Finish writes** — emits a new structured entry to `cognition.jsonl` describing this run (chain, outcome, lesson, applies_when target, fitness=score/10).
3. **Finish bumps wins** — if the chain's outcome was a success (`shipped`, `fixed`, `revised-and-shipped`, etc.), increments `wins` on every lesson that was retrieved at init. The win_rate (`wins/hits`) thus reflects whether surfaced lessons actually helped subsequent runs succeed.

```bash
# Explicit emission (rare; finish does this for you)
GHENGIS_COGNITION=true python scripts/scratchpad.py cognition-emit

# Explicit retrieval (also rare; init does this for you)
python scripts/scratchpad.py retrieve --query "banking amount validation" --top-k 5

# Audit: surface entries to retire (hits>=5 + win_rate<0.4) or unused (90+ days, hits=0)
python scripts/scratchpad.py audit
```

UCB1 formula (within similarity-filtered candidates):
```
score    = jaccard(applies_when_tokens, query_tokens) * (0.7 + 0.3 * ucb1)
ucb1     = win_rate + sqrt(2 * ln(total_retrievals) / max(hits, 1))
win_rate = wins / hits, or 0.5 prior when hits=0
```

The exploration bonus pulls in untested entries occasionally even when they don't have a win track record yet. Over time, the ones that genuinely help accumulate wins; the ones that mislead accumulate hits without wins. The audit command surfaces the latter for retirement.

### Cognition store: project vs global (v1.19.0+)

Cognition is **per-project by default**. Each project keeps its own JSONL at `<project>/.claude/cognition.jsonl`, and there is also a shared cross-project library at `~/.claude/cognition.jsonl`. The two are independent files; nothing leaks between them automatically.

**Where things land:**

- `scratchpad.py finish` writes to **project** by default — `<project>/.claude/cognition.jsonl`.
- `scratchpad.py cognition-emit`, `audit`, and `cognition-replace-last` all default to **project**.
- `scratchpad.py retrieve` (and `init`'s auto-retrieve) default to **merged** — search project first, fall back to global if project has < `top_k` hits. Project entries get a small UCB1 boost (1.1×) so they outrank equal-similarity global entries.

**Choosing a scope:**

- `--scope project` (default for writes) — store this lesson with this project only.
- `--scope global` — store this lesson in the cross-project library. Use sparingly; lessons that show up out of context waste prompt budget.
- `--scope merged` (default for reads) — pull from both. Project results outrank equal global results.

**Override precedence:** explicit `--scope` arg > `GHENGIS_COGNITION_SCOPE` env var > default. Set the env var per-project (e.g. in `.claude/settings.json`) when you want a project to always write or always read in a non-default scope.

```bash
# Per-project (default): writes land in <project>/.claude/cognition.jsonl
python scripts/scratchpad.py cognition-emit

# Cross-project: writes land in ~/.claude/cognition.jsonl
python scripts/scratchpad.py cognition-emit --scope global

# Retrieve from only this project (skip the global library)
python scripts/scratchpad.py retrieve --query "..." --scope project

# Retrieve from the global library only
python scripts/scratchpad.py retrieve --query "..." --scope global
```

**Promoting a project lesson to global:**

When a project lesson clearly generalizes (a language API gotcha, a framework footgun, a debugging technique — *not* a project-specific config quirk), promote it:

```bash
python scripts/scratchpad.py cognition-promote <entry_id>
```

This appends a copy to `~/.claude/cognition.jsonl` with `promoted_from_project: <project_root>` and `promoted_at: <iso8601>` stamps. The project entry is **not deleted** — it's marked `promoted_to_global: true` so the local audit trail stays intact. A second promote on the same id is rejected.

**When NOT to promote:** project-specific configs, hardcoded paths, secrets, team conventions, codebase-specific architecture choices. If the lesson would confuse you in an unrelated project, it doesn't belong in the global library.

### The Analyzer Subagent

The `scratchpad.py finish` command writes a HEURISTIC cognition entry by default — strings like "bug-hunt required revision loop; iteration 2 succeeded". These work as a fallback but are too generic to retrieve usefully.

The **`ghengis-skills:analyzer` subagent** (defined in `agents/analyzer.md`) reads the archived scratchpad after `finish` and produces a structured causal lesson that REPLACES the heuristic entry. Lessons like:

> *"When validating amount strings, use Decimal + regex pre-check — Decimal() alone silently accepts whitespace, PEP 515 underscores, and leading +"*

vs the heuristic:

> *"bug-hunt required revision loop; iteration 2 succeeded"*

The analyzer reads the scratchpad's validator findings, iteration history, and outcome to write specific lessons that name the actual technique / API / edge case that mattered. It also detects contradictions with prior entries and marks superseded entries.

**When to dispatch the analyzer:**

After `finish` writes the heuristic entry, AND when `GHENGIS_COGNITION=true`:

```
Agent tool with subagent_type=ghengis-skills:analyzer
Prompt: "The most recent chain finished. Archived scratchpad at:
        <project>/.claude/ghengis-chain/history/<chain>-<ts>.json
        Read it, read the last entry of cognition.jsonl, and produce
        a better lesson + causal_factor + applies_when. Return the
        REPLACE_LAST_LINE_OF: ... WITH: ... directive so I can update
        the file."
```

The analyzer outputs structured guidance; the orchestrator (you) executes the file replacement via Bash. Analyzer is `disallowedTools: Write, Edit` to keep the dispatch clean.

**Cost:** runs on Haiku-tier by default. Most analyses complete in <200 output tokens. Escalates to Sonnet/Opus only when contradicting 3+ existing lessons or scratchpad is unusually large.

**Refusal:** the analyzer declines when scratchpad evidence is too thin to support a non-generic lesson (typical for `cannot-reproduce`, `design-only-handoff` outcomes). In that case the heuristic entry stays — better a generic lesson than a hallucinated one.

### When to Turn Cognition On / Off

`GHENGIS_COGNITION` is environment-scoped — set it where you want the loop active, leave it unset where you don't.

**Turn it ON when:**

- **Repeat structure.** You're going to run similar work many times — debugging similar bug classes, building similar features, porting more skills. The loop only pays off when patterns recur.
- **Long-running project.** Cognition.jsonl grows from your actual work. A 2-day project doesn't generate enough entries; a 6-month project does.
- **Multi-session work.** Lessons from a session you ran 3 weeks ago show up in today's chain start. That's the whole point.
- **You're OK with the small overhead.** Reading and writing JSONL on init/finish adds maybe 50ms. Negligible for chains that take minutes.

**Turn it OFF when:**

- **One-off projects** with no repeat structure. Spike work, throwaway prototypes, hackathons.
- **Debugging the chain system itself.** Cognition entries from broken runs can poison future retrievals. Disable while iterating on chain logic.
- **Fast spikes.** Adding 50ms to each chain matters when you're running 100 chains in a tight loop. (Not the normal case but worth flagging.)
- **You're skeptical of feedback loops** and prefer manually curated guidance (CLAUDE.md, project notes). Cognition complements those — it doesn't replace them.
- **Privacy concerns.** Cognition entries include the `applies_when` field which contains a snippet of `user_request`. Per-project storage limits exposure, but if you're doing sensitive work in a project, consider whether the journal is appropriate.

**Setting it:**

```bash
# Per-session (works for current shell only)
export GHENGIS_COGNITION=true

# Per-project (add to project's .claude/settings.json env block)
{
  "env": {
    "GHENGIS_COGNITION": "true"
  }
}

# Globally for all sessions (add to ~/.zshrc or ~/.bashrc)
export GHENGIS_COGNITION=true
```

**Maintenance cadence:** run `python scripts/scratchpad.py audit` monthly (or after every 50+ entries). Mark flagged entries with `audit_status: "retired"` in the JSONL to exclude them from future retrievals without deleting history.

The helper handles JSON parsing, dotted paths, atomic writes, archiving, cognition emission, UCB1 retrieval, and audit so participant skills don't need to re-implement state management.

## Debugging

- Print `current_stage` and recent scratchpad updates to stderr
- Preserve scratchpad on failure (`<project>/.claude/ghengis-chain/errors/<timestamp>.json`)
- Chain execution log at `<project>/.claude/ghengis-chain/log.jsonl` (one line per stage completion)

## Design Notes

- **Why a file, not in-memory?** Claude sessions are ephemeral. File persists across subagent forks and session restarts.
- **Why namespaced subkeys, not nested stages?** Flat namespaces are easier to query ("what did hallucination-detector find?") and don't require tree traversal.
- **Why sync by default?** Determinism beats speed for a v1. Parallelism is an opt-in per-chain choice.
- **Why not use Anthropic's `hooks` frontmatter field directly?** Hooks fire deterministically but can't express "run skill X, wait for result, then pass result to skill Y". Hooks are for pre/post events; chains are for multi-step workflows with data passing.
