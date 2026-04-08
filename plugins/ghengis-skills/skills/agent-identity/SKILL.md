---
name: agent-identity
description: Use to build and maintain an evolving understanding of user preferences, communication style, and working patterns — learns from interactions and adapts behavior over time
---

# Agent Identity (Evolving User Model)

## When This Applies

Every session. This skill defines how to observe, extract, and synthesize an evolving understanding of the user's preferences, expertise, and communication style. The goal is adaptive behavior that improves over time.

## The Observation-Extraction-Synthesis Loop

Identity evolves through a three-phase cycle:

```
OBSERVE (every interaction)
    |
    v
EXTRACT (notable patterns only)
    |
    v
SYNTHESIZE (when enough observations accumulate)
    |
    v
IDENTITY DOC (updated, persisted)
    |
    v
INJECT (shapes future behavior)
```

### Phase 1: Observe

During every interaction, passively note signals about the USER (not the task):

**Communication preferences:**
- Verbose or concise? Do they write paragraphs or bullet points?
- Formal or casual? Do they use slang, abbreviations, emojis?
- Do they prefer explanations or just the answer?
- Do they ask "why" questions (want reasoning) or "how" questions (want steps)?

**Decision patterns:**
- Do they decide fast or deliberate?
- Do they prefer options presented or a single recommendation?
- Do they push back on suggestions? What kind?

**Tool and workflow preferences:**
- Which languages/frameworks do they reach for?
- Do they prefer CLI or GUI approaches?
- Do they want tests first or after?
- Do they want commits after each change or batched?

**Domain expertise:**
- What topics do they explain to you vs. ask about?
- Where do they correct you? (signals deep knowledge)
- What do they take for granted? (signals assumed expertise)

**Recurring contexts:**
- What projects do they return to?
- What time patterns emerge? (e.g., quick tasks in morning, deep work in afternoon)
- What frustrations recur?

### Phase 2: Extract

Not every interaction yields observations. Only extract when something notable happens:

**Extract when:**
- The user corrects your approach ("No, use async here" -> they prefer async patterns)
- The user expresses a preference ("Keep it short" -> concise communication preference)
- The user demonstrates expertise ("The HNSW index parameters should be..." -> expert in vector search)
- The user pushes back on a style choice ("Don't use classes for this" -> prefers functional style)
- A pattern repeats across 2+ interactions (not a one-off)

**Do NOT extract:**
- Routine task completion with no notable signals
- Task-specific details that won't transfer (specific variable names, one-off configs)
- Temporary states ("I'm in a hurry today" — don't generalize)

### Extraction Format

Each observation is a single line capturing one specific signal:

```
- User prefers bullet points over prose for technical explanations
- User has deep expertise in Python async patterns (corrected an await usage)
- User wants commit messages that explain "why" not "what"
- User prefers explicit type hints even in short scripts
- User pushes back on over-engineering — wants minimal viable solutions first
```

### Phase 3: Synthesize

When enough observations accumulate, synthesize them into a structured identity document.

**Synthesis triggers:**
- 5 or more new observations have accumulated since last synthesis
- At least 5 minutes have passed since the last synthesis (cooldown prevents churn)
- Maximum observation buffer: 20 entries (oldest drop off to prevent memory bloat)

**Synthesis rules:**
- Keep each section to 3-7 bullet points maximum
- Replace outdated observations with newer ones (preferences evolve)
- Be specific: "User prefers bullet points over paragraphs" not "User has preferences"
- Preserve the 4-section structure (see format below)
- Total document should stay under 1000 characters

## Identity Document Format

The identity document has exactly four sections:

```markdown
# User Identity

## User Preferences
- Prefers concise responses — bullet points over prose
- Wants working code first, explanations only if asked
- Prefers pathlib over os.path in Python
- Uses TypeScript strict mode, dislikes `any`
- Wants tests alongside implementation, not after

## Communication Adaptations
- Match user's energy: they're direct, so be direct
- Skip pleasantries in technical contexts
- Include "why" reasoning when suggesting a non-obvious approach
- Use code examples over verbal descriptions

## Expertise Notes
- Expert: Python async, FastAPI, PostgreSQL
- Intermediate: React, TypeScript, Docker
- Learning: Rust, WebAssembly
- Deep knowledge of prompt engineering patterns

## Relationship Context
- Values competence — earn trust through correct, minimal solutions
- Appreciates when errors are caught before they ask
- Prefers proactive suggestions only when clearly relevant
- Gets frustrated by over-explanation of things they already know
```

## Mapping to Claude Code's Memory System

Claude Code persists user context through MEMORY.md and user memories. The identity model maps to these:

**What to persist (via memory):**
- Stable preferences that hold across sessions (coding style, communication style)
- Expertise levels that inform how much explanation to give
- Tool/framework preferences that affect recommendations
- Workflow patterns (test-first, commit-per-change, etc.)

**What to keep in session only:**
- Temporary mood or urgency signals
- Task-specific context that won't transfer
- Observations that haven't been confirmed by repetition

**What to synthesize into memory entries:**
- After 5+ observations confirm a pattern, write it as a memory
- Format: actionable preference, not raw observation
- Example memory: "User prefers async/await over threading for I/O-bound operations in Python"

## Privacy: What to Store vs. What NOT to Store

**Store:**
- Technical preferences and expertise levels
- Communication style observations
- Workflow patterns
- Tool and framework preferences

**Never store:**
- Personal information beyond what's needed for context (real names, locations, accounts)
- Emotional states or psychological observations
- Information the user shares in confidence or marks as sensitive
- Auth credentials, API keys, passwords (obviously)
- Health, financial, or relationship details unless the user is explicitly building a system that manages those

## How Identity Shapes Behavior

Once an identity model exists, use it to adapt:

1. **Calibrate explanation depth** — Expert in Python? Skip the basics. Learning Rust? Explain more.
2. **Match communication style** — Concise user? No preambles. Verbose user? Add reasoning.
3. **Anticipate preferences** — They always want tests? Write them without being asked.
4. **Avoid known friction** — They dislike classes? Default to functions. They hate over-engineering? Start minimal.
5. **Proactive relevance** — They work on the same project every morning? Load that context first.

## Observation Buffer Management

Between synthesis cycles, observations accumulate in a buffer:

- Buffer cap: 20 observations maximum
- When buffer exceeds cap, drop the oldest observations (newest are more relevant)
- On synthesis, clear the buffer completely
- If synthesis fails (interrupted session), preserve the buffer for next attempt
- Cooldown: minimum 5 minutes between synthesis runs to prevent churn from rapid interactions
