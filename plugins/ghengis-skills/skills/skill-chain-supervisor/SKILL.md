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
- **Starting research** — run the `deep-research` chain (deep-research → fact-check → report-writing)
- **User explicitly asks** — "run the full chain on this" / "validate thoroughly" / "use the pipeline"

## Core Model

```
Event or user request
    ↓
Supervisor reads chain spec (chains/<name>.md)
    ↓
Writes initial state to ~/.claude/ghengis-chain-context.json
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

Single JSON file at `~/.claude/ghengis-chain-context.json`:

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

1. **Identify the chain name** (`agent-dispatch`, `task-complete`, `deep-research`, etc.)
2. **Read the chain spec** at `chains/<name>.md` inside this skill's directory
3. **Initialize scratchpad** — write `chain`, `started_at`, `input`, `current_stage`, `stages_remaining`
4. **Execute each stage:**
   - Read scratchpad to see prior stages' output
   - Invoke the stage's skill (via Skill tool) with scratchpad context
   - After skill returns, update scratchpad: move stage from `stages_remaining` to `stages_completed`, advance `current_stage`
5. **At chain end** — write `completed_at`, optionally archive scratchpad to `~/.claude/ghengis-chain-history/<timestamp>.json`

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

See `chains/` directory. As of v1.8.3:

- **agent-dispatch** — wraps a subagent spawn with PQL → meta-prompting → execution → completion → hallucination → audit

More chains coming in v1.9.0+.

## Debugging

- Print `current_stage` and recent scratchpad updates to stderr
- Preserve scratchpad on failure (`~/.claude/ghengis-chain-errors/<timestamp>.json`)
- Chain execution log at `~/.claude/ghengis-chain-log.jsonl` (one line per stage completion)

## Design Notes

- **Why a file, not in-memory?** Claude sessions are ephemeral. File persists across subagent forks and session restarts.
- **Why namespaced subkeys, not nested stages?** Flat namespaces are easier to query ("what did hallucination-detector find?") and don't require tree traversal.
- **Why sync by default?** Determinism beats speed for a v1. Parallelism is an opt-in per-chain choice.
- **Why not use Anthropic's `hooks` frontmatter field directly?** Hooks fire deterministically but can't express "run skill X, wait for result, then pass result to skill Y". Hooks are for pre/post events; chains are for multi-step workflows with data passing.
