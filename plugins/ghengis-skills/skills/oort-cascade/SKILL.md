---
name: oort-cascade
description: Use when facing complex tasks that need multiple specialized agents working in sequence or parallel — task decomposition, role assignment, dependency DAGs, revision loops, and quality validation
allowed-tools: Agent Read Grep Glob
---

# OORT Cascade

Task-Oriented Orchestrated Relay Topology. When a task is too complex for a single pass, decompose it into specialized roles, wire them into a dependency graph, execute in parallel waves, and validate output quality before delivering.

This is orchestration methodology, not a framework or library. Apply it by structuring how you use the Agent tool, subagents, and parallel execution within Claude Code.

## When to Use

- Multi-step tasks that produce a deliverable (report, codebase, design, campaign)
- Tasks requiring different specializations (research + build + validate)
- Work where quality matters enough to justify a validation pass
- Requests with explicit multi-department scope ("research X, then build Y, then review Z")
- Tasks where getting it wrong is expensive (proposals, client deliverables, production code)

## When NOT to Use

- Simple lookups, single-action commands, quick questions
- Tasks under ~40 words that have a clear single-step answer
- Pure factual retrieval (just answer the question)
- Tasks where speed matters more than quality (quick drafts, brainstorming)
- Anything you can do well in a single focused pass -- cascading adds overhead

**Threshold rule:** If you can deliver a high-quality result in one pass, do that. Cascade only when decomposition genuinely improves the outcome.

## The 4 Layers

OORT has four layers. You will use layers 1-3 directly. Layer 4 is about output formatting.

| Layer | Purpose | What You Do |
|-------|---------|-------------|
| **1. Task Cascade** | Decompose request into parallel specialized roles | Break the task into a DAG of roles |
| **2. Meta-Prompting** | Generate tailored instructions per role | Write specific prompts for each subagent |
| **3. Handoff Protocol** | Structured data transfer between roles | Pass findings as structured data, not prose |
| **4. Output Formatting** | Format result for the target audience | Deliver in the format the user requested |

## Task Decomposition

When you receive a complex task, follow this sequence:

### Step 1: Identify the Deliverable

What does the user want produced? A report? A codebase? A plan? A refactored module? Name it concretely.

### Step 2: Map Required Capabilities

What skills and knowledge are needed? List them:
- Does it need research or external information gathering?
- Does it need building/creating/writing?
- Does it need validation or quality checking?
- Does it need documentation or archival?
- Does it need specialized domain expertise?

### Step 3: Assign Roles

Each capability maps to a role. The four core roles are:

| Role | Responsibility | Delivers |
|------|---------------|----------|
| **Researcher** | Gather data, context, background info | Bullet-point findings with sources |
| **Builder** | Create the main deliverable | The artifact (code, document, design) |
| **Validator** | Quality-check the output, score 0-10 | Score + actionable feedback |
| **Documenter** | Archive results, update project docs | Structured summary for memory |

Add specialist roles only when they provide clear value:
- **Analyst** -- when raw data needs interpretation before the builder can use it
- **Architect** -- when structural decisions precede implementation
- **Reviewer** -- when domain-specific review differs from general validation
- **Editor** -- when tone/style polish is a distinct concern from content accuracy

### Step 4: Define the Dependency DAG

Which roles need output from others? Independent roles run in parallel.

```
Wave 1 (parallel):  Researcher, Analyst
Wave 2 (needs W1):  Builder
Wave 3 (needs W2):  Validator
Wave 4 (needs W3):  Documenter
```

### Step 5: Execute in Waves

Use the Agent tool to dispatch subagents. Independent roles within a wave run in parallel. Dependent roles wait for their inputs.

## Decomposition Rules

- **Minimum viable cascade:** Builder + Validator. Every cascade needs at least these two.
- **Add Researcher only if** external information, codebase exploration, or context gathering is required.
- **Add Documenter only if** the results need to be archived or project docs need updating.
- **Add specialists only when** they provide clear value over combining responsibilities.
- **Max 6 roles per cascade.** Beyond 6, you get diminishing returns and coordination overhead.
- **Lean is better.** Fewer roles = faster execution, less handoff noise, lower cost.

## Meta-Prompting: Tailored Instructions Per Role

Every role gets a purpose-built prompt. Never dispatch a subagent with generic instructions.

### Template

```
You are the {ROLE} on a team completing: {TASK}

YOUR SPECIFIC RESPONSIBILITY:
{What this role must deliver -- concrete and measurable}

DELIVERABLE FORMAT:
{Exact structure of expected output}

CONTEXT FROM PREVIOUS ROLES:
{Handoff data from dependencies -- key findings, data points, artifacts}

QUALITY CRITERIA:
{What "good" looks like for this specific output}

CONSTRAINTS:
- Scope: {boundaries of this role's work}
- Length: {target size of output}
- Audience: {who will consume this output}
```

### Role-Specific Guidance

**Researcher prompts should specify:**
- Focus areas and specific questions to answer
- Where to look (codebase paths, file types, documentation)
- Output format: bullet points with citations, not prose

**Builder prompts should specify:**
- Exact deliverable specification
- Style, tone, and structural requirements
- Reference materials from upstream roles
- Output: the actual artifact

**Validator prompts should specify:**
- Scoring rubric (accuracy, completeness, quality, format)
- Specific items to check against the original request
- Output: structured score + issues + revision feedback

**Documenter prompts should specify:**
- What to document and where
- Format and structure expectations
- Output: structured summary ready for project docs

### Worked Example

**Task:** "Refactor the auth module to use JWT tokens instead of session cookies"

- **Researcher prompt:** "Survey the current auth implementation. Identify all files using session cookies, all endpoints that check auth state, and all tests covering auth. Output: file list, dependency map, risk areas as bullet points."
- **Builder prompt:** "Using the researcher's file list and dependency map, refactor auth from session cookies to JWT. Implement token generation, validation middleware, refresh flow. Preserve all existing test coverage."
- **Validator prompt:** "Review the JWT refactor against: (1) all original auth tests still pass, (2) no session cookie references remain, (3) token refresh handles edge cases, (4) no security regressions. Score 0-10 on accuracy, completeness, quality, format."

## Handoff Protocol

Roles pass structured data downstream -- not prose paragraphs. See `handoff-protocol.md` for the full specification.

**Key rules:**
- Max 500 tokens per handoff (forces conciseness)
- Use bullet points, not paragraphs
- Include raw data and numbers, not just interpretations
- Every claim needs a source or confidence qualifier
- When merging multiple upstream handoffs, synthesize -- do not duplicate

**Anti-patterns:**
- "The researcher found many interesting things about the topic" (vague, useless)
- Passing entire previous outputs as handoffs (bloated, unfocused)
- Omitting source references (downstream roles cannot verify)

## Quality Gates and Validation

Every cascade includes validation. See `quality-gates.md` for the full scoring system.

### Functional Testing (Not Just Scoring)

The validator must **use the output like a user would**, not just read and rate it. Scoring without execution catches surface problems; functional testing catches real ones.

| Output Type | Functional Test |
|-------------|----------------|
| Code | Run it. Execute tests. Check imports resolve. Verify the build passes. |
| API endpoints | Call them. Send real requests. Check response shapes and status codes. |
| Web UI / frontend | Load it in a browser (Playwright, puppeteer). Click through flows. Screenshot results. |
| Documents / reports | Check all claims are sourced. Verify data points against inputs. |
| Config / infrastructure | Dry-run or validate syntax (`terraform validate`, `docker compose config`). |
| 3D models | Check mesh integrity, verify printability constraints. |

**Tune the validator to skepticism.** Models praise their own work — a separate validator context with instructions to find problems catches what self-review misses. The validator prompt should say "find what's wrong" not "check if it's good."

```
Validator prompt pattern:
  "Your job is to BREAK this, not approve it.
   Run the code. Hit the endpoints. Click the buttons.
   Score based on what actually works, not what looks right."
```

### The Builder-Validator Loop

```
Builder produces output
    |
Validator RUNS functional tests (not just reads)
    |
Score >= 7?  -->  Accept, continue pipeline
Score < 7?   -->  Send feedback to Builder with specific issues
    |
Builder revises addressing ALL listed issues
    |
Validator re-tests (functional, not just re-reads)
    |
Accept (max 2 revision loops to prevent infinite cycles)
```

### Scoring Rubric

Rate every output on these four dimensions (0-10 each):

| Dimension | What to Check |
|-----------|---------------|
| **Accuracy** | Are facts correct? Claims supported? Code functional? |
| **Completeness** | Does it address every part of the request? |
| **Quality** | Is it well-structured, polished, professional? |
| **Format** | Does it match the requested output format? |

**Overall score** = average of dimensions, rounded.

### Score Thresholds

| Score | Action |
|-------|--------|
| 9-10 | Ship immediately |
| 7-8 | Ship with minor notes |
| 5-6 | Revise if time allows |
| 3-4 | Must revise before shipping |
| 0-2 | Restart the role from scratch |

### Revision Rules

- Max 2 revision loops per role (prevents infinite cycles)
- Each revision must address ALL listed issues
- Track score progression -- it should improve each iteration
- If score does not improve after revision, accept and note the quality gap to the user

## Self-Validation Checklist

Before returning ANY output from any role, verify:

- [ ] **Completeness** -- Does it address every part of the request?
- [ ] **Accuracy** -- Are all facts verifiable? Code tested?
- [ ] **Format** -- Does it match the requested output structure?
- [ ] **Actionability** -- Can the next role (or the user) act on this immediately?

## Red Flags Table

| If you notice... | The problem is... | Fix it by... |
|-----------------|-------------------|-------------|
| A role's output is >2000 tokens | Scope creep or missing constraints | Tightening the meta-prompt with explicit length limits |
| Validator always scores 9-10 | Rubber-stamp validation | Adding specific checkpoints to the validator prompt |
| Builder ignores researcher findings | Weak handoff | Restructuring handoff as explicit requirements, not background info |
| Cascade has 7+ roles | Over-decomposition | Merging roles with overlapping responsibilities |
| Revision loop hits max without improving | Fundamental approach problem | Restarting the role with a different strategy |
| Handoff is prose paragraphs | Handoff protocol violation | Converting to structured KEY_FINDINGS / DATA_POINTS format |
| User's request was simple but you cascaded | Over-engineering | Handling it directly in a single pass |

## Cascade vs. Direct: Decision Guide

Ask yourself these questions:

1. **Does this need multiple distinct skills?** (research AND build AND validate) -- If yes, cascade.
2. **Is the deliverable complex enough to benefit from a validation pass?** -- If yes, at least Builder + Validator.
3. **Would I naturally break this into phases if doing it myself?** -- If yes, those phases are your roles.
4. **Can I do this well in a single focused pass?** -- If yes, skip the cascade entirely.

## Putting It All Together

Here is the full execution flow for a cascade:

```
1. Receive complex task
2. Identify deliverable and required capabilities
3. Assign roles (min: Builder + Validator, max: 6)
4. Build dependency DAG and group into waves
5. Write meta-prompts for each role (tailored, not generic)
6. Execute Wave 1 (parallel where possible)
7. Collect outputs, build structured handoffs
8. Execute Wave 2 with handoff context
9. ... continue through all waves ...
10. Validator scores final output
11. If score < 7 and revisions remain, loop back to Builder
12. Deliver final output to user
```

The power of OORT is not in the framework -- it is in the discipline of decomposition, structured handoffs, and closed-loop validation. Apply the pattern; skip the ceremony when the task does not warrant it.

## Subagent Dispatch Guardrails

Opus 4.6 has a strong native tendency to spawn subagents. Combined with OORT's cascade pattern, this can cause over-spawning — subagents spawning subagents, coordination overhead exceeding the work itself.

**Use subagents (cascade) when:**
- Tasks can genuinely run in parallel with no shared state
- Different specializations are required (research vs build vs validate)
- The deliverable benefits from isolated contexts (independent perspectives)
- Work is substantial enough that coordination overhead is worth it

**Work directly (no cascade) when:**
- A single grep, file read, or lookup answers the question
- The task is a sequential chain where each step needs the previous result immediately
- Single-file edits or small focused changes
- The task takes less than 2 minutes of focused work
- You already have the context you need — don't delegate understanding

**Anti-patterns to avoid:**
- Spawning a Researcher subagent when you could just grep the codebase yourself
- Creating a Validator subagent for a 10-line code change — just run the tests directly
- Cascading a task that has one obvious approach — cascading adds overhead, not quality
- Nesting cascades — if a subagent needs its own cascade, the decomposition is wrong
