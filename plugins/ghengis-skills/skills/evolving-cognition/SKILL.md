---
name: evolving-cognition
description: Use when building agents or workflows that should learn from their own measurable outcomes -- covers fitness signal design, cognition store schema, Analyzer prompts, UCB1 retrieval, poison mitigations, and audit loops. TRIGGER when user mentions "learn from outcomes", "agent memory", "feedback loop", "lesson store", "cognition", or "agents getting smarter over time".
---

# Evolving Cognition

Pattern for building agent systems that get sharper over time by distilling causal lessons from measurable outcomes and feeding them back into future prompts. Inspired by ASI-Evolve (GAIR-NLP, arxiv 2603.29640).

The core insight: **most agent work produces measurable outcomes (tests pass/fail, deploys succeed/fail, transactions match/mismatch). Those outcomes are currently discarded. Capture them, analyze why they happened, and retrieve the lessons into future prompts — agents improve without anyone editing their prompts.**

## When to Use

- Building an agent system that does measurable work (code, deploys, data pipelines, transactions)
- Adding a feedback loop so agents learn from past successes and failures
- Designing a knowledge store that grows from agent activity (not just user input)
- Implementing retrieval-augmented generation where the corpus is self-generated lessons
- Any "agents should get better at this over time" requirement

## The Learn-Design-Experiment-Analyze Loop

ASI-Evolve's thesis: prior work evolves candidate solutions; this pattern **evolves cognition itself**. Accumulated experience and distilled insights are continuously stored and retrieved to inform future exploration.

```
┌─────────────────────────────────────────────────┐
│                                                  │
│   Agent does work ──► Outcome measured           │
│         ▲                    │                   │
│         │                    ▼                   │
│   Lessons injected    Analyzer distills          │
│   into prompt         causal lesson              │
│         ▲                    │                   │
│         │                    ▼                   │
│   UCB1 retrieval ◄── Cognition Store             │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Step 1: Define Fitness Signals

Every department/domain needs a measurable outcome. If you can't define one, the domain is excluded from the loop — that's fine.

| Domain | Signal Source | Fitness Type |
|--------|-------------|--------------|
| Code/Engineering | tests pass/fail, lint, type-check | scalar (pass_count / total) |
| Deployment | deploy success, rollback count | binary |
| Data pipelines | rows processed, error rate | scalar |
| Financial | reconciliation match, P&L delta | scalar |
| IoT/Hardware | device responded, print succeeded | binary |
| Research | fact-checker agreement, source freshness | scalar |

**Key rule:** fitness must be computable WITHOUT human judgment. If it requires a human to score, it's not a fitness signal — it's a review task. Open-ended conversation has no fitness signal; exclude it.

Emit outcomes as structured events:
```python
emit_outcome_measured(
    session_id=session_id,
    agent="engineering.coder",
    task="Add user login endpoint",
    fitness=0.85,                    # 17/20 tests passed
    artifacts={"test_output": "..."}, # raw evidence
    tool_names=["PytestRun"],
    department="engineering",
)
```

## Step 2: Design the Cognition Entry Schema

Each lesson is a structured record, not free-form text. The schema forces the Analyzer to be specific.

```
CognitionEntry:
  id: str                    # sortable unique id
  created_at: datetime
  lesson: str                # <= 280 chars, imperative mood, one sentence
  causal_factor: str         # <= 500 chars, WHY it worked/failed
  applies_when: str          # <= 280 chars, embedding target for retrieval
  confidence: float          # 0.0-1.0
  source_event_ids: list     # pointers to raw outcome events
  department: str
  agent: str
  tool_names: list
  outcome_score: float       # the fitness from the trial
  supersedes: list[str]      # older entry ids this replaces
  contradicts: list[str]     # entry ids this conflicts with
  audit_status: str          # unchecked | verified | flagged | retired
  hits: int                  # retrieval count
  wins: int                  # task-succeeded-after-retrieval count
```

**Critical field: `applies_when`** — this is what you embed and retrieve by. It describes the SITUATION, not the lesson itself. "Sandboxed pytest retry after source edit" retrieves differently than "Always use --no-cache on pytest retry."

## Step 3: Write the Analyzer Prompt

The Analyzer is a cheap model (Haiku-tier) that reads the outcome event + tool trace and writes a structured lesson. Escalate to a stronger model only when the outcome contradicts 3+ existing lessons.

Template structure:
```
You are the ANALYZER in the cognition loop.

TASK ATTEMPTED: {task_description}
OUTCOME SCORE: {outcome_score}
DEPARTMENT: {department}
TOOL-CALL TRACE: {trace}
RAW OUTCOME: {outcome_artifacts}
PRIOR LESSONS THAT MAY CONFLICT: {prior_lessons}

RULES:
1. Focus on WHY, not WHAT
2. If contradicting a prior lesson, list its id
3. Never store PII or credentials
4. CONFIDENCE: 0.3-0.5 speculative, 0.6-0.8 supported, 0.9+ unambiguous

RESPOND:
LESSON: <one sentence, imperative mood>
CAUSAL_FACTOR: <why it worked/failed>
APPLIES_WHEN: <retrieval condition>
CONFIDENCE: <float>
SUPERSEDES: [<prior ids this replaces>]
CONTRADICTS: [<prior ids that clash>]
```

**Parse the output with regex, not JSON.** LLMs are more reliable with labeled fields than structured formats. Truncate oversize fields and LOG A WARNING — silent truncation hides prompt misbehavior.

## Step 4: UCB1 Retrieval Scoring

Don't retrieve by raw cosine similarity. Use UCB1 (Upper Confidence Bound) which balances exploitation (lessons that worked before) with exploration (lessons that haven't been tried enough).

```
score = cosine_similarity(task_embedding, entry.applies_when_embedding)
      + (entry.wins / max(entry.hits, 1))           # exploitation
      + sqrt(2 * log(total_retrievals) / max(entry.hits, 1))  # exploration
```

**ASI-Evolve finding (Section 5.2.3):** when priors are strong (well-seeded cognition store), UCB1 beats diversity-preserving samplers like MAP-Elites. Strong priors make exploration less valuable — exploit what works.

Inject the top-k (typically 3-5) lessons into the agent prompt:
```
LESSONS FROM PAST ATTEMPTS
1. [conf 0.87, 12 wins / 14 retrievals] Use --no-cache on pytest retry
   Applies when: Sandboxed pytest after source edit
2. [conf 0.72, 5 wins / 8 retrievals] Check bed temp before high-density infill
   Applies when: 3D print with cold chamber
```

**Gate behind an env flag** (e.g., `COGNITION_LIVE=true`) during rollout so you can disable without a deploy.

## Step 5: Poison Mitigations (The Paper Skipped These)

ASI-Evolve has zero safety discussion. These are the rails you need:

### 5a. Contradiction Flag
When the Analyzer writes `CONTRADICTS: [old_id]`, BOTH the new entry AND the old entry get `audit_status = "flagged"`. Flagged entries are excluded from retrieval until resolved.

### 5b. Retrospective Audit (Weekly)
Re-score every entry by its win/hit ratio over the past 14 days:
- `hits >= 5` AND `wins/hits < 0.4` → **retire** (excluded from retrieval forever)
- `hits == 0` AND `age >= 90 days` → **decay confidence** (multiply by 0.9 each audit pass)
- `audit_status == "flagged"` with unresolved contradictions → write to **review queue** for human eyeball

### 5c. Supersede Chain
When the Analyzer writes `SUPERSEDES: [old_id]`, the old entry stays in storage (for audit trail) but is excluded from retrieval. No silent edits — supersession is an explicit, traceable action.

### 5d. Constitution Gate
The Analyzer inherits the same safety rules as every other agent. No storing PII in `causal_factor`. No lessons that would produce irreversible actions if retrieved.

### 5e. Human Review Surface
Write `review_queue.json` listing all flagged contradictions. Surface this in a UI (mobile, web, CLI) with Verify/Retire buttons. The human resolves conflicts the system can't.

## Step 6: Batch Job Design

Run the Analyzer on a schedule (every 15 minutes is a good cadence), not inline with the agent run. This keeps agent latency unaffected.

```
Batch job flow:
1. Scan session event logs for new OUTCOME_MEASURED events
2. Track last-processed sequence per session (marker file)
3. For each new event: dispatch Analyzer (parallel, max 6 concurrent)
4. Append resulting CognitionEntry to store
5. Advance markers (even on failure — prevent infinite retry loops)
6. Log ERROR if all events in a batch failed (Analyzer is broken)
```

**Idempotency:** use a marker file (`{session_id: last_processed_seq}`). Running the job twice produces entries once.

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| Storing raw outcomes as lessons | No causal analysis — "test failed" doesn't tell the next agent WHY |
| Retrieving by lesson text similarity | You want to match SITUATIONS, not ADVICE — embed `applies_when`, not `lesson` |
| Silent truncation of oversize fields | Hides that the Analyzer is ignoring your prompt constraints |
| Inline analysis (during the agent run) | Adds latency; batch is better |
| Global retrieval without department filter | A Fabrication lesson about bed temperature shouldn't dominate a Finance agent's context |
| MAP-Elites when priors are strong | UCB1 converges faster when the cognition store is well-seeded (ASI-Evolve Section 5.2.3) |
| No audit loop | Bad lessons compound — a single wrong high-confidence entry can derail weeks of agent runs |
| No human review surface | Contradictions the system can't resolve need human judgment — hiding them is a time bomb |

## Cross-Domain Synthesis

The most powerful finding from ASI-Evolve: lessons from one domain can inform another. Their drug-target interaction model used Sinkhorn attention — discovered by cross-retrieving optimal transport theory lessons from a different experiment.

Enable this by:
- Storing all lessons in ONE index (not per-department silos)
- Using department as a FILTER, not a partition
- Defaulting to department-filtered retrieval, but allowing cross-department when the `applies_when` similarity is very high (cosine > 0.85)

## Cost Model

At Haiku pricing (~$0.80/1M input, $4/1M output):
- Typical Analyzer pass: ~2k input + ~300 output = ~$0.003 per lesson
- 150 outcomes/day = ~$0.45/day
- Weekly audit: negligible (no LLM calls — pure Python)

## Integration with Other Skills

- **audit-ledger** tracks WHAT agents did. Evolving cognition tracks what they LEARNED from doing it.
- **blueprint-compilation** compiles PROCEDURES (deterministic steps). Evolving cognition compiles INTUITION (when to try what).
- **skill-memory** is hand-authored per-agent notes. Cognition entries are auto-generated cross-agent lessons.
- **completion-enforcer** catches incomplete work NOW. Cognition prevents the same incomplete pattern NEXT TIME.
