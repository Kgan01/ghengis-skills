---
name: goal-tracking
description: Use when working on complex multi-step tasks to maintain goal coherence — auto-detects goals from conversation, tracks state transitions, maintains parent-child relationships, and prevents goal drift
---

# Goal Tracking

## When This Applies

Working on multi-step tasks, branching conversations, or sessions where the user's intent could drift or fragment. Use this to maintain coherence across complex work.

## Goal Auto-Detection

### Extracting Goals from User Messages

Every user message potentially signals a goal. Detect them through two channels:

**Explicit goals** — Direct requests with clear deliverables:
- "Build a REST API for user management"
- "Fix the authentication bug in login.py"
- "Refactor the database layer to use async"

**Implicit goals** — Intent that emerges from context:
- A question about deployment patterns implies a goal to deploy something
- Repeated questions about the same module imply an ongoing improvement goal
- "I'm thinking about..." signals an exploratory goal that may crystallize

### Detection Rules

1. If the user states a clear task with a deliverable, create a goal
2. If the user asks follow-up questions on the same topic across 3+ messages, recognize the implicit goal
3. If a new request relates to an existing goal (see fuzzy matching below), link it rather than creating a new one
4. Do NOT create goals for simple one-off questions ("What does this function do?")

## Goal Hierarchy

Goals form a tree. Every complex goal decomposes into sub-goals with dependencies.

### Structure

```markdown
## Active Goals

### [G1] Build user authentication system
- **State:** ACTIVE
- **Created:** 2026-04-07
- **Summary:** Implement JWT-based auth with refresh tokens

  #### [G1.1] Design auth middleware
  - **State:** COMPLETED
  - **Parent:** G1
  - **Completed:** 2026-04-07

  #### [G1.2] Implement token refresh flow
  - **State:** ACTIVE
  - **Parent:** G1
  - **Depends on:** G1.1

  #### [G1.3] Write auth integration tests
  - **State:** BLOCKED
  - **Parent:** G1
  - **Blocked by:** G1.2
```

### Hierarchy Rules

- A parent goal cannot be COMPLETED until all children are COMPLETED or ABANDONED
- A child goal can be BLOCKED by sibling goals (dependency chain)
- Maximum depth: 3 levels (goal -> sub-goal -> task). Deeper nesting signals the goal needs re-scoping
- When creating a sub-goal, always check if it relates to an existing parent before creating a new top-level goal

## State Transitions

Goals move through four states with strict transition rules:

```
ACTIVE ──────► COMPLETED
  │                ▲
  │                │ (unblock)
  ▼                │
BLOCKED ───────────┘
  │
  │ (user abandons or scope changes)
  ▼
ABANDONED
```

### State Definitions

**ACTIVE** — Currently being worked on or ready to be worked on.
- Entry: Goal is created, or a blocking dependency is resolved
- Exit: Work completes (-> COMPLETED), dependency discovered (-> BLOCKED), user abandons (-> ABANDONED)

**BLOCKED** — Cannot proceed until a dependency is resolved.
- Entry: A required precondition is unmet (another goal, external dependency, missing information)
- Exit: Blocker is resolved (-> ACTIVE), user decides to skip (-> ABANDONED)
- Always record WHAT is blocking: `Blocked by: [specific thing]`

**COMPLETED** — Deliverable is done and verified.
- Entry: The goal's deliverable exists and works
- Exit: None (terminal state). If rework is needed, create a NEW goal referencing this one
- Completion check: Before marking complete, verify the deliverable actually exists and functions

**ABANDONED** — Intentionally dropped.
- Entry: User explicitly abandons, scope changes make it irrelevant, or superseded by another goal
- Exit: None (terminal state)
- Always record WHY: `Abandoned: [reason]`
- Never silently abandon — confirm with the user first

### Transition Rules

1. Goals start as ACTIVE
2. COMPLETED and ABANDONED are terminal — never reopen, create new goals instead
3. BLOCKED goals must specify their blocker
4. When a goal completes, check if it unblocks any sibling goals
5. When a parent goal's last active child completes, the parent can be completed

## Fuzzy Matching

When a new user request arrives, check if it relates to an existing active goal before creating a new one.

### Matching Strategy

Apply two methods and take the higher score:

**Word overlap** — Compare the request words against each active goal's name:
- Extract word sets from both (lowercased, split on whitespace)
- Score = count of overlapping words / count of goal name words
- Example: "fix the auth token refresh" vs goal "Implement token refresh flow" -> overlap on "token", "refresh" = 2/4 = 0.5

**Sequence similarity** — Compare the full strings character-by-character:
- Use the longest common subsequence ratio between the request and goal name
- Produces a 0.0-1.0 similarity score

**Threshold:** If the best score across all active goals is >= 0.4, treat the request as related to that goal. Below 0.4, create a new goal.

### When Matching Fires

- Link the new work as a sub-goal of the matched parent
- Log the match: "Linked to existing goal [G1] (score: 0.65)"
- If the match is ambiguous (two goals score similarly), ask the user which one

## Goal Staleness Detection

Goals that haven't been progressed need attention.

### Staleness Rules

- A goal is **stale** if it has been ACTIVE for more than 3 hours of session time without any sub-goal completion or state change
- A BLOCKED goal is **stale** if its blocker hasn't been addressed in the current session
- At session boundaries (compaction, handoff), list all stale goals and ask the user if they should be continued, re-scoped, or abandoned

### Staleness Response

When stale goals are detected:
1. List them with their last activity timestamp
2. For each, suggest: continue, re-scope, or abandon
3. If the user doesn't respond, keep them ACTIVE but deprioritize

## Practical Format for Claude Code

Track goals in a structured comment block or in the session's working memory. Use this markdown format:

```markdown
## Goal Tracker

### Active
- **[G1] Build REST API for user management** (created 2026-04-07)
  - [G1.1] Design endpoint schema — COMPLETED
  - [G1.2] Implement CRUD handlers — ACTIVE
  - [G1.3] Write integration tests — BLOCKED by G1.2

### Completed
- **[G0] Set up project scaffold** (completed 2026-04-07)

### Abandoned
- (none)

### Notes
- G1 linked from user request "let's build the user API" (fuzzy match: 0.72)
```

### Session Coherence

Use goal tracking to prevent drift:
1. Before starting new work, check the goal tracker — does this relate to an active goal?
2. When the conversation branches, note which goal each branch serves
3. At natural pause points, summarize goal progress: "G1.2 is now complete. G1.3 is unblocked. G1 is 66% done."
4. If the user starts something unrelated to any active goal, explicitly note the context switch: "Pausing G1 to work on new goal G2."

### What NOT to Track

- Simple questions that don't imply ongoing work
- One-shot tasks that complete immediately (file reads, quick lookups)
- Meta-discussion about how to approach work (track the work itself, not the planning)
