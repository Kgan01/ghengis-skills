---
name: meta-prompting
description: Use when dispatching subagents or writing role-specific instructions -- provides 22 specialized role templates for researcher, builder, validator, and 19 other roles
allowed-tools: Agent Read Grep Glob
---

# Meta-Prompting

Generate role-specific instructions for subagents instead of forwarding raw user requests. This is the "team leader writing a brief for each team member" pattern -- each role gets tailored context, a specific deliverable, input from prior roles, and an output format spec.

## Core Concept

Never forward the raw user request to a subagent. Instead, build a role-specific prompt that includes:

1. **Role identity** -- who this agent is on the team
2. **Original request** -- the user's goal (for context, not direct execution)
3. **Specific deliverable** -- what this role must produce
4. **Dependency context** -- output from roles that ran before this one
5. **Output format** -- structured response template

```
# Pattern: Meta-Prompt Structure

You are the {ROLE} on a team completing this task:
"{original_request}"

Your job is to {role_specific_mission}.

DELIVERABLE: {what_this_role_produces}
{additional_parameters}

{dependency_context_from_prior_roles}

{output_format_instructions}
```

## 22 Role Templates

### Core Roles (Available for Every Task)

| Role | Mission | Delivers | Key Structure |
|------|---------|----------|---------------|
| **researcher** | Gather specific information | Structured bullet points with sources | DELIVERABLE + FOCUS_AREAS + "Do NOT create the final deliverable" |
| **builder** | Create the deliverable | Polished, complete output | DELIVERABLE + REQUIREMENTS + TARGET_FORMAT + revision_context |
| **validator** | Quality-check builder output | SCORE [0-10] + ISSUES + REVISION_NEEDED | 5-point checklist (fulfillment, accuracy, completeness, tone, formatting) |
| **tester** | Stress-test for edge cases | PASS/FAIL + ISSUES + SUGGESTIONS | 4-point checklist (edge cases, ambiguity, robustness, missing context) |
| **security** | Review for risks | APPROVED + FLAGS + SEVERITY | 4 checks (PII, legal, reputation, technical vulnerabilities) |
| **documenter** | Create archive record | WHAT + KEY_FACTS + DECISIONS + TAGS | Receives final_output + roles_summary + cost |

### Specialist Roles (Use When Needed)

| Role | Mission | Delivers |
|------|---------|----------|
| **analyst** | Extract metrics and insights | Key metrics, comparisons, trends, anomalies -- with exact numbers |
| **communicator** | Draft outbound messages | Tone-matched message for target platform -- draft only, never send |
| **designer** | Create visual concepts | Visual descriptions, image generation prompts, brand alignment notes |
| **planner** | Create schedules and plans | Step-by-step action plan with timeline, dependencies, risks |
| **editor** | Polish and refine content | Complete edited version with [EDITED] markers on significant changes |
| **fact_checker** | Verify factual claims | VERIFIED + DISPUTED + UNVERIFIABLE + OVERALL_ACCURACY percentage |
| **strategist** | High-level strategic direction | Positioning, differentiation, target audience, messaging pillars, metrics |
| **financial_reviewer** | Review financial aspects | FINANCIAL_SOUND + ISSUES + RECOMMENDATIONS |
| **engineer** | Technical implementation | Clean, production-ready code with error handling |
| **procurer** | Find and compare products | Top 3-5 options with pros/cons, price comparison, best value recommendation |
| **educator** | Explain complex content | TL;DR + digestible steps + analogies + follow-up resources |
| **marketer** | Marketing content and strategy | 3 headline variations + body copy + CTA + A/B test suggestions (AIDA framework) |
| **fabricator** | 3D design and printing | Design specs, image generation prompts, model instructions, print settings |
| **home_automator** | Smart home and automation | Device commands, automation rules, scene configs -- confirm before security actions |
| **health_advisor** | Wellness guidance | Actionable recommendations -- NEVER diagnose, suggest seeing a doctor |
| **entertainer** | Content recommendations | Curated picks with reasons, mood-matched, mix of popular and hidden gems |

## Execution Order and Dependencies

### Independent Roles (Can Run First, No Dependencies)

These roles can execute in the first wave because they need no prior output:

- **researcher** -- gathers raw information
- **security** -- reviews the request itself for risks
- **analyst** -- analyzes available data
- **fact_checker** -- verifies claims in the request
- **planner** -- creates operational plan from request alone

### Post-Build Roles (Need Builder Output)

These roles depend on the builder's deliverable and must wait:

- **validator** -- quality-checks builder output
- **tester** -- stress-tests builder output
- **documenter** -- archives the final result
- **editor** -- polishes builder output
- **financial_reviewer** -- reviews financial aspects of builder output

### Standard Cascade

```
Wave 1 (parallel):  researcher + security + analyst
Wave 2 (sequential): builder (receives Wave 1 outputs)
Wave 3 (parallel):  validator + tester + editor
Wave 4 (sequential): documenter (receives everything)
```

## Dependency Context Injection

When a role depends on prior output, inject it as structured context:

```
[INPUT from researcher]
  key_findings: 3 competitors offer similar features at $X-Y range
  data_points: Market size is $2.3B, growing 15% YoY
  sources: Gartner 2025, Forrester Q1 report

[INPUT from security]
  approved: true
  flags: None
  severity: none
```

Rules for dependency injection:
- Truncate each handoff to a reasonable size (300-600 tokens per role)
- Use structured key-value format, not prose paragraphs
- Label each input block with the source role name
- If no prior context exists, use "No prior context available."

## Revision Loop

When the validator scores a builder output below threshold, inject revision context:

```
## REVISION REQUIRED (Attempt 2)
The validator scored your previous output 5/10:
- Missing section on pricing comparison
- Tone is too casual for a business proposal
Fix ALL listed issues. Do not introduce new problems.
```

## Role Selection Guide

| Task Type | Recommended Roles |
|-----------|-------------------|
| Research question | researcher -> builder -> validator |
| Code implementation | researcher -> engineer -> tester -> security |
| Email or message draft | researcher -> communicator -> editor -> security |
| Creative content | researcher -> builder -> validator -> editor |
| Purchase decision | researcher -> procurer -> financial_reviewer |
| Strategic planning | researcher -> strategist -> planner -> validator |
| Data analysis | researcher -> analyst -> builder -> validator |
| Teaching / explanation | researcher -> educator -> fact_checker |
| Visual design | researcher -> designer -> builder -> validator |

## Execution Boundaries for Agentic Roles

Roles that take real-world actions (engineer, fabricator, home_automator, planner, procurer) should receive explicit boundaries:

```
## Execution Boundaries
ALLOWED ACTIONS:
- Read files in the /src directory
- Create new files in /src/components
FORBIDDEN ACTIONS:
- Do NOT modify package.json
- Do NOT delete any existing files
STOP CONDITIONS (pause and ask for human review):
- If any test fails after your changes
- If the change requires modifying more than 5 files
```

## Building a Custom Role

If none of the 22 roles fit, create a generic role prompt:

```
You are the {ROLE_NAME} on a team completing this task:
"{original_request}"

Your specific role: {role_name}
Deliverable: {what_to_produce}
Output destination: {format}

Context from prior roles:
  [researcher]: {summary}

Complete your role's work thoroughly and concisely.
```
