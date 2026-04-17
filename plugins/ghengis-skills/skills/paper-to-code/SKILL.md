---
name: paper-to-code
description: Use when the user shares a research paper, arxiv link, or asks how to apply academic research to their codebase -- covers strategic paper reading, contribution mapping, spec delta writing, and the "what NOT to adopt" framing. TRIGGER when message contains arxiv.org, "this paper", "read this paper", "apply this research", or references an academic publication.
---

# Paper to Code

Systematic workflow for turning academic research into shipping code. Not "implement the paper" — instead: extract the transferable ideas, map them to your existing architecture, write a spec delta, and ship what actually applies.

## When to Use

- User shares an arxiv URL or PDF link
- User asks "how do we apply this paper" or "what can we use from this"
- User references a research finding they want to incorporate
- User asks about a new technique from a conference/blog post with a linked paper

## The Workflow

```
Read Paper (strategic, not cover-to-cover)
    │
    ▼
Extract Thesis + Key Contributions + Repo
    │
    ▼
Map Contributions to Existing Architecture
    │
    ▼
Identify What NOT to Adopt (and why)
    │
    ▼
Write Spec Delta (not greenfield — delta on existing work)
    │
    ▼
Plan + Implement
```

## Phase 1: Strategic Paper Reading

Do NOT read the paper cover-to-cover. Read in this order:

### Pass 1: Orientation (~2 minutes)
1. **Title + Abstract** — what's the claim?
2. **Figures/Tables** — scan all of them. The results table tells you if the paper delivered.
3. **Conclusion** — does the conclusion match the abstract, or does it hedge?

### Pass 2: Architecture (~5 minutes)
4. **Method section** — how does it actually work? Focus on:
   - The system architecture (agents, components, data flow)
   - The data structures (schemas, stores, indexes)
   - The evaluation protocol (how did they measure success?)
5. **Related Work** — who did they compare against? This tells you the competitive landscape.

### Pass 3: Depth (~10 minutes)
6. **Results with numbers** — don't just read "outperforms baseline." Read: by how much, on what benchmarks, at what cost?
7. **Ablation studies** — which components actually matter? Ablations tell you what to steal and what to skip.
8. **Limitations section** — what did they NOT solve? (If there's no limitations section, that's a red flag.)
9. **Ethics/Safety section** — what risks did they acknowledge? (If absent, note what they SHOULD have discussed.)

### What to Extract

After reading, you should have:

```
THESIS: one sentence — what the paper actually claims
KEY CONTRIBUTIONS: 3-5 numbered items with specific numbers
OPEN SOURCE: repo URL + license + what's actually implemented vs. aspirational
LIMITATIONS: what they said + what they didn't say but should have
COMPUTE COST: estimated or stated — can you afford to reproduce this?
SAFETY GAPS: what risks exist that the paper didn't address?
```

## Phase 2: Contribution Mapping

Build a table mapping paper concepts to your existing system:

```markdown
| Paper Concept | Your Equivalent | Gap |
|---------------|----------------|-----|
| Researcher agent | ghengis-skills:researcher | none — already exists |
| Cognition Store (FAISS) | brain/ (pgvector) | need embedding retrieval for lessons |
| Experiment Database | session_store.py (JSONL) | need outcome signal, not just events |
| Analyzer agent | *gap* | new — no structured lesson distiller |
```

**Three columns matter:**
1. **Already have** — don't rebuild. Note the mapping.
2. **Gap — need to build** — this is your actual work scope.
3. **Paper has it but we don't need it** — explicitly exclude. Prevents scope creep.

## Phase 3: What NOT to Adopt

This is the most important phase. Every paper has ideas that don't transfer. Be explicit about what you're skipping and why.

Common reasons to skip:

| Reason | Example |
|--------|---------|
| **Compute cost** | "Their architecture search ran 1,773 trials at ~$100k GPU-hours. We're not reproducing that." |
| **Fitness function mismatch** | "Their system optimizes a scalar benchmark score. Our work is open-ended — no single number." |
| **Scale mismatch** | "Their results are at 1.3B parameters. We run on Haiku." |
| **Already solved differently** | "They use FAISS; we already have pgvector with the same embedding model." |
| **Missing safety rails** | "They have no poison mitigation. We need to add our own." |

**Frame as "what we take, what we leave, what we add":**
- **Take**: the loop structure, the schema, the retrieval pattern
- **Leave**: the specific experiments, the compute-heavy validation, the benchmark chasing
- **Add**: safety rails, env-flag gating, human review surface, audit loop

## Phase 4: Write a Spec Delta

Don't write a greenfield spec. Write a DELTA on your existing architecture docs.

Structure:
```markdown
# [Feature Name] — Spec Delta on [Existing Spec]

**Inspired by:** [Paper title, arxiv URL, repo URL]

## Relationship to Existing Work
- What already exists
- What this adds
- Dependency map

## Problem (in plain language)
Why the current system doesn't have this capability

## Solution (in plain language)
What the paper taught us, adapted to our constraints

## Architecture Changes
- New modules/files
- Modified files (with line-number targets)
- New data models

## What Counts as Success
- Measurable acceptance criteria
- What "done" looks like

## Explicit Non-Goals
- What we're NOT building from the paper
- Why

## Decisions
- Resolved design questions (don't leave them open)

## Open Questions (if any)
- With a PROPOSAL for each (never leave a question without a default answer)
```

## Phase 5: Plan + Implement

Use your standard planning skill (`writing-plans` or equivalent). The spec delta IS the input to the planner.

Key principle: **the plan should reference the paper's concepts by name** so future developers can trace decisions back to the source. "UCB1 retrieval (ASI-Evolve Section 5.2.3)" is better than "bandit-based scoring."

## Anti-Patterns

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| "Let's implement the paper" | Papers are research artifacts, not product specs. Extract ideas, don't clone. |
| Skipping the limitations section | You'll rediscover their unsolved problems the hard way |
| Ignoring compute cost | A technique that requires 1,773 GPU-hour trials is not viable at $0 budget |
| No "what NOT to adopt" phase | Scope creeps to include everything the paper mentions |
| Greenfield spec instead of delta | Ignores everything you already built. Deltas are cheaper and safer. |
| Reading the full paper before checking the repo | The repo tells you what's actually implemented vs. aspirational |
| Trusting the abstract | Abstracts oversell. Read the results table and the conclusion's hedging language. |
| No safety analysis | If the paper has no ethics/safety section, that's YOUR problem to solve, not a feature to copy |

## When the Paper Has an Open-Source Repo

Check the repo BEFORE deep-reading the paper:

1. **License** — can you use it? (Apache-2.0, MIT = yes. No license = ask.)
2. **README vs. paper** — does the repo implement everything the paper claims? Often it doesn't.
3. **Stars/activity** — is it maintained or abandoned?
4. **Dependencies** — can you install it? Heavy deps (CUDA, specific framework versions) may be a barrier.
5. **Code quality** — is it research code (works once) or production code (works reliably)?

**Don't fork the repo.** Extract the PATTERN and reimplement in your stack. Research code has different quality standards than production code.

## Cost of This Workflow

- Phase 1 (reading): 1 WebFetch + 1-2 targeted reads = ~$0.01 in API calls
- Phase 2 (mapping): pure reasoning, no tools
- Phase 3 (exclusions): pure reasoning
- Phase 4 (spec delta): 1 file write
- Phase 5 (planning): standard planning skill cost

Total: negligible. The value is in the structured thinking, not the tool calls.

## Integration with Other Skills

- **evolving-cognition** is the most common OUTPUT of this skill — "read ASI-Evolve paper, build a cognition loop"
- **deep-research** covers the 7-phase research methodology for broader topics. Paper-to-code is specifically for "I have ONE paper and want to ship code from it."
- **writing-plans** takes the spec delta as input for implementation planning.
- **general-research** covers source evaluation. Paper-to-code assumes you already have the paper.
