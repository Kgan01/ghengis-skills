---
name: pql-validation
description: Use when writing, reviewing, or improving prompts for agents, subagents, or LLM calls — detects anti-patterns, suggests fixes, and enforces prompt quality principles
---

# PQL Validation

Prompt Quality Layer for Claude Code. Validates prompts before execution, catches anti-patterns, and auto-fixes common issues. Zero cost, instant feedback.

## When to Validate

- Before dispatching subagents or spawning parallel agents
- Before any LLM call where the prompt was constructed dynamically
- When prompts are generating poor, off-topic, or verbose output
- When reviewing prompt templates or system instructions
- Before committing prompt changes to a codebase

## 7 Core Principles

1. **Be specific** -- "Analyze the auth middleware for SQL injection" not "check the code"
2. **Include context** -- What files, what problem, what the expected outcome is
3. **Set boundaries** -- What to do AND what NOT to do
4. **Specify output format** -- JSON, markdown, table, code block -- never leave it ambiguous
5. **One task per prompt** -- Don't combine unrelated asks
6. **Avoid filler** -- No "please", "basically", "essentially", "very" -- they waste tokens
7. **Use XML tags for Claude** -- `<task>`, `<context>`, `<constraints>` structure

## 6 Anti-Pattern Categories

All 35 anti-patterns are documented in `anti-patterns.md`. Here is the category overview:

| Category | Count | What It Catches |
|----------|-------|-----------------|
| **Task** | 7 | Vague verbs, dual tasks, no success criteria, over-permissive delegation, emotional language, scope too large, implicit references |
| **Context** | 6 | Assumed knowledge, missing project context, hallucination invitations, undefined audience, no failure context, missing constraints |
| **Format** | 6 | Missing output format, implicit length, vague aesthetics, no examples, ambiguous lists, no tone specified |
| **Scope** | 6 | No scope boundary, no stack constraints, unbounded iteration, no error handling spec, no performance target, no backward compat |
| **Reasoning** | 5 | CoT on reasoning models, contradictory instructions, roleplay without purpose, prompt injection risk, negative framing |
| **Agentic** | 5 | No starting state, no target state, no stop condition, unlocked filesystem, no human review step |

**Severity levels:**
- `warn` -- Informational. Prompt will likely work but could be improved.
- `critical` -- Likely to cause poor output, unsafe behavior, or runaway execution.

## Auto-Fix Patterns

These are common fixes you can apply without an LLM call:

| Problem | Fix |
|---------|-----|
| Vague verb ("handle", "deal with") | Replace with specific action: "parse", "validate", "refactor", "delete" |
| Filler words ("basically", "essentially", "just", "very", "really") | Remove them. They add zero information. |
| Preamble ("Sure!", "I'd be happy to help", "Let me explain") | Strip from LLM output before passing to next stage |
| "Think step by step" on reasoning models | Remove. Models like o1, o3, DeepSeek R1, Qwen3 reason internally. |
| "Do whatever you think is best" | Replace with explicit constraints and boundaries |
| "Keep going until it's perfect" | Set a fixed iteration limit: "try 3 approaches, pick the best" |
| Emotional language ("terrible", "garbage") | Replace with specific technical observations |
| Negative framing ("don't make it ugly") | Reframe positively: "make it readable with consistent spacing" |
| Implicit length ("keep it short") | Specify exact length: "200 words", "5 bullet points", "3 paragraphs" |
| "You know what I mean" | State context explicitly -- the model has no memory unless you provide it |

## Prompt Framework Quick Reference

Use these when structuring prompts for different task types.

### RTF -- Simple One-Shot Tasks
```
Role:   Who the AI should act as
Task:   What the AI should do
Format: How the output should be structured
```
Best for: Quick questions, single-step tasks, code generation with clear specs.

### CO-STAR -- Business Writing
```
Context:  Background and situation
Objective: The goal of the task
Style:    Writing style to adopt
Tone:     Emotional register (formal, casual, empathetic)
Audience: Who will read this
Response: Expected format of the response
```
Best for: Emails, reports, proposals, documentation aimed at a specific audience.

### RISEN -- Complex Multi-Step Tasks
```
Role:        Who the AI should act as
Instructions: High-level directives
Steps:       Ordered list of actions to perform
End Goal:    What success looks like
Narrowing:   Constraints and scope limits
```
Best for: Multi-step tasks, implementation plans, refactoring workflows.

### ReAct + Stop -- Autonomous Agents
```
Objective:         The agent's mission
Starting State:    Initial conditions and context
Target State:      Desired end state
Allowed Actions:   Tools and actions the agent may use
Forbidden Actions: Actions the agent must not take
Stop Conditions:   When to halt execution
Checkpoints:       Intermediate verification points
```
Best for: Agentic workflows, autonomous execution, Claude Code subagents.

### File-Scope -- Code Editing
```
File:             Path to the file being edited
Function:         Target function or method
Current Behavior: What the code does now
Desired Change:   What should change
Scope:            Boundaries of the edit
Constraints:      Rules the edit must follow
Done When:        Acceptance criteria
```
Best for: Targeted code changes, bug fixes, feature additions in specific files.

## Token Efficiency

Wasted tokens = wasted money and context window. Apply these rules to all prompts and handoffs:

**Filler words to remove:**
basically, essentially, actually, literally, obviously, clearly, simply, just, really, very, quite, rather, pretty much, kind of, sort of, in order to, due to the fact that, at this point in time, it should be noted that, it is important to note that, as a matter of fact, in terms of

**Preamble patterns to strip from LLM output before passing downstream:**
"Sure!", "Okay!", "I'd be happy to help.", "Here is the result:", "Let me help...", "Let me explain...", "Let me show...", "Let me provide...", "I found that", "I discovered that", "I noticed that"

**Structured handoffs:** When passing data between agents or stages, use structured formats (JSON, XML tags) instead of prose. A 10-line natural language handoff can often be a 3-line structured block.

## Red Flags Table

Thoughts that mean your prompt needs work:

| If you're thinking... | The problem is... | Fix it by... |
|----------------------|-------------------|-------------|
| "The model should know what I mean" | Assumed knowledge | Stating context explicitly |
| "It keeps giving me the wrong thing" | Missing constraints or format spec | Adding boundaries and output format |
| "Just make it better" | No success criteria | Defining measurable outcomes |
| "Do this and also that and also..." | Multiple tasks in one prompt | Splitting into separate prompts |
| "I'll know it when I see it" | Vague aesthetic requirements | Specifying exact visual properties |
| "Keep going until it's perfect" | Unbounded iteration | Setting a fixed iteration limit |
| "Use your best judgment" | Over-permissive delegation | Providing explicit constraints |
| "Fix it again, it still doesn't work" | No failure context | Including error messages and what you tried |
| "Write a blog post" (no audience) | Undefined audience | Specifying who will read it |
| "Make the API fast" | No performance target | Setting a measurable target (e.g., "under 200ms") |
