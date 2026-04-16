---
name: using-ghengis-skills
description: Use when starting any conversation - establishes how to find and use ghengis-skills, requiring Skill tool invocation before ANY response when a ghengis-skill applies (mirrors superpowers:using-superpowers pattern)
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a ghengis-skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Why This Skill Exists

Ghengis skills are domain expertise and operational reliability tools that complement (not replace) workflow skills like superpowers. Without an autoloader, they get crowded out by skills that DO autoload. This skill ensures ghengis skills get equal priority treatment.

## Instruction Priority

Ghengis skills override default system prompt behavior, but **user instructions always take precedence**:

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **Ghengis skills** — override default system behavior where they conflict
3. **Other autoloaded skill systems** (e.g., superpowers) — coexist; both should be checked
4. **Default system prompt** — lowest priority

If both ghengis-skills and superpowers offer skills for the same task, prefer the more specific one. If user says "don't use X," follow the user.

## How to Access Skills

Use the `Skill` tool. Invoke with the qualified name: `ghengis-skills:<skill-name>`. When invoked, the skill content loads — follow it directly. Never use Read on skill files.

# When to Invoke Ghengis Skills

## The Rule

**Invoke relevant or requested skills BEFORE any response or action.** Even a 1% chance a skill might apply means invoke it. If the skill turns out to be wrong, drop it.

## Decision Flow

```dot
digraph ghengis_skill_flow {
    "User message received" [shape=doublecircle];
    "About to dispatch a subagent?" [shape=diamond];
    "Use meta-prompting + pql-validation" [shape=box];
    "Subagent claims done?" [shape=diamond];
    "Use completion-enforcer" [shape=box];
    "Doing complex/iterative research?" [shape=diamond];
    "Use deep-research" [shape=box];
    "Working with FastAPI/React/Flutter/ESP32?" [shape=diamond];
    "Use the matching domain skill" [shape=box];
    "Long session or context drift suspected?" [shape=diamond];
    "Use context-health" [shape=box];
    "Multiple parallel agents needed?" [shape=diamond];
    "Use agent-teams or oort-cascade" [shape=box];
    "Reviewing AI output for accuracy?" [shape=diamond];
    "Use hallucination-detector" [shape=box];
    "Other ghengis-skill might apply?" [shape=diamond];
    "Invoke it" [shape=box];
    "Respond" [shape=doublecircle];

    "User message received" -> "About to dispatch a subagent?";
    "About to dispatch a subagent?" -> "Use meta-prompting + pql-validation" [label="yes"];
    "About to dispatch a subagent?" -> "Subagent claims done?" [label="no"];
    "Use meta-prompting + pql-validation" -> "Subagent claims done?";
    "Subagent claims done?" -> "Use completion-enforcer" [label="yes"];
    "Subagent claims done?" -> "Doing complex/iterative research?" [label="no"];
    "Use completion-enforcer" -> "Doing complex/iterative research?";
    "Doing complex/iterative research?" -> "Use deep-research" [label="yes"];
    "Doing complex/iterative research?" -> "Working with FastAPI/React/Flutter/ESP32?" [label="no"];
    "Use deep-research" -> "Working with FastAPI/React/Flutter/ESP32?";
    "Working with FastAPI/React/Flutter/ESP32?" -> "Use the matching domain skill" [label="yes"];
    "Working with FastAPI/React/Flutter/ESP32?" -> "Long session or context drift suspected?" [label="no"];
    "Use the matching domain skill" -> "Long session or context drift suspected?";
    "Long session or context drift suspected?" -> "Use context-health" [label="yes"];
    "Long session or context drift suspected?" -> "Multiple parallel agents needed?" [label="no"];
    "Use context-health" -> "Multiple parallel agents needed?";
    "Multiple parallel agents needed?" -> "Use agent-teams or oort-cascade" [label="yes"];
    "Multiple parallel agents needed?" -> "Reviewing AI output for accuracy?" [label="no"];
    "Use agent-teams or oort-cascade" -> "Reviewing AI output for accuracy?";
    "Reviewing AI output for accuracy?" -> "Use hallucination-detector" [label="yes"];
    "Reviewing AI output for accuracy?" -> "Other ghengis-skill might apply?" [label="no"];
    "Use hallucination-detector" -> "Other ghengis-skill might apply?";
    "Other ghengis-skill might apply?" -> "Invoke it" [label="yes, even 1%"];
    "Other ghengis-skill might apply?" -> "Respond" [label="no"];
    "Invoke it" -> "Respond";
}
```

## Mandatory Trigger Map

These situations ALWAYS require the listed skill — no exceptions:

| Situation | Required Skill |
|---|---|
| About to write a prompt for a subagent | `ghengis-skills:meta-prompting` (use a role template) |
| About to dispatch a subagent with a custom prompt | `ghengis-skills:pql-validation` (verify prompt quality FIRST) |
| Subagent reports DONE / completes | `ghengis-skills:completion-enforcer` (verify it actually finished) |
| User asks for research that needs depth/iteration | `ghengis-skills:deep-research` |
| User asks for quick lookup | `ghengis-skills:general-research` |
| Working with FastAPI code | `ghengis-skills:fastapi` |
| Working with React/Next.js code | `ghengis-skills:react-nextjs` |
| Working with Flutter/Dart code | `ghengis-skills:flutter-dart` |
| Working with ESP32/IoT firmware | `ghengis-skills:esp32` |
| Working with 3D models / STL files | `ghengis-skills:3d-modeling` |
| Working with MCP servers | `ghengis-skills:mcp-patterns` |
| Setting up DevOps / CI/CD / Docker | `ghengis-skills:devops` |
| Security review / vulnerability assessment | `ghengis-skills:security-testing` |
| Data analysis / visualization | `ghengis-skills:data-analysis` |
| Writing reports / structured docs | `ghengis-skills:report-writing` |
| Writing content / blog posts / docs | `ghengis-skills:content-writing` |
| Need multiple creative perspectives | `ghengis-skills:agent-teams` |
| Multi-step pipeline with role decomposition | `ghengis-skills:oort-cascade` |
| Reviewing AI/agent output for hallucinations | `ghengis-skills:hallucination-detector` |
| Building agentic workflow | `ghengis-skills:constitutional-ai` (safety boundaries) |
| Long-running session, context degradation | `ghengis-skills:context-health` |
| Task too large for one session | `ghengis-skills:execution-harness` |
| Repeated workflow you might want to automate | `ghengis-skills:blueprint-compilation` |
| Setting up scheduled/cron tasks | `ghengis-skills:proactive-rituals` |
| Need to learn from past tasks | `ghengis-skills:skill-memory` |
| Building agent that needs accountability | `ghengis-skills:audit-ledger` |
| Hitting rate limits / cost ceilings | `ghengis-skills:compute-adaptation` |
| Starting new project | `ghengis-skills:project-scaffold` |
| Organizing files / cleanup | `ghengis-skills:file-organization` |
| Tracking goals across multi-step work | `ghengis-skills:goal-tracking` |
| Tracking tasks/projects/priorities | `ghengis-skills:task-tracking` |
| Adapting agent behavior to user style | `ghengis-skills:agent-identity` |
| Codebase exploration / architecture analysis | `ghengis-skills:code-intelligence` |
| Formatting output for specific destination | `ghengis-skills:output-formatting` |
| Teaching / explaining concepts | `ghengis-skills:tutoring` |
| Building learning curriculum | `ghengis-skills:learning-paths` |
| Time/calendar/routine design | `ghengis-skills:scheduling` |
| Smart light/ambiance design | `ghengis-skills:home-lighting` |
| Music discovery / playlist creation | `ghengis-skills:music-curation` |
| Purchase decisions / product research | `ghengis-skills:shopping` |
| Financial record-keeping / tax prep | `ghengis-skills:bookkeeping` |
| Client/freelance project management | `ghengis-skills:crm-patterns` |

## Red Flags

These thoughts mean STOP — you're rationalizing:

| Thought | Reality |
|---|---|
| "Superpowers handled this" | Both systems coexist. Check ghengis too. |
| "I know how to do this" | Skills evolve. Read current version. |
| "This is too quick to need a skill" | Quick tasks are where errors slip through. Use the skill. |
| "I'll just write the prompt myself" | meta-prompting + pql-validation prevent stuck/wrong agents. |
| "The agent finished, looks good" | completion-enforcer catches premature/false completions. |
| "I'll do shallow research" | If complex, use deep-research. Don't skip the methodology. |
| "FastAPI is just web code" | The fastapi skill has patterns specific to async/Pydantic v2/dependency injection. Use it. |

## Coexistence with Superpowers

Both autoload systems are valid. They overlap intentionally — pick the more specific skill:

| Task | Pick |
|---|---|
| Brainstorming a feature | `superpowers:brainstorming` (workflow skill) |
| Writing a sub-agent prompt during brainstorming | `ghengis-skills:meta-prompting` (specific tool) |
| Writing implementation plans | `superpowers:writing-plans` |
| Building FastAPI endpoints in that plan | `ghengis-skills:fastapi` (domain expertise) |
| Executing plans with subagents | `superpowers:subagent-driven-development` |
| Verifying each subagent's completion | `ghengis-skills:completion-enforcer` |
| Researching a library | `ghengis-skills:deep-research` (or `general-research` for quick) |
| TDD discipline | `superpowers:test-driven-development` |
| Reviewing finished work | `superpowers:requesting-code-review` |
| Checking for hallucinations in agent output | `ghengis-skills:hallucination-detector` |

## When NOT to Invoke

- During subagent execution (`<SUBAGENT-STOP>` above)
- When the user has explicitly told you not to use skills for this task
- When invoking would create infinite recursion (skill calling itself)

## How to Announce Use

When invoking a ghengis skill, announce briefly:
> "Using `ghengis-skills:meta-prompting` to write the subagent prompt."

This keeps the user informed without verbose explanation.
