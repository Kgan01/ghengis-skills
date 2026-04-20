---
name: agent-dispatch
pattern: sequential
triggers:
  - event: pre_tool_use
    tool: Agent
  - event: user_request
    keywords: ["dispatch agent", "spawn subagent", "run full chain on agent"]
on_error: fail_fast
estimated_duration: 15-60 seconds
---

## Purpose

Wraps a subagent dispatch with quality checks before and verification after. Catches bad prompts before they cost money, and catches false "done" claims before they ship.

## Input Contract

Scratchpad keys expected at chain start:

```json
{
  "input": {
    "user_request": "<what the user asked>",
    "target_agent": "<agent type being dispatched, e.g. general-purpose>",
    "prompt_draft": "<the prompt about to be sent>"
  }
}
```

## Stages

### 1. pql-validation
- **Skill:** `ghengis-skills:pql-validation`
- **Reads:** `input.prompt_draft`
- **Writes:** `pql_validation.score` (float 0-1), `pql_validation.anti_patterns` (list), `pql_validation.suggested_fixes` (list)
- **Success:** score >= 0.5 OR auto-fix applied
- **On fail:** route to prompt-autofix (if available) or warn user

### 2. meta-prompting (conditional)
- **Skill:** `ghengis-skills:meta-prompting`
- **When:** `pql_validation.anti_patterns` contains "missing-role" OR "vague-deliverable"
- **Reads:** `input.prompt_draft`, `pql_validation.anti_patterns`
- **Writes:** `meta_prompting.role_selected`, `meta_prompting.enhanced_prompt`
- **Success:** enhanced_prompt passes PQL >= 0.7

### 3. execution
- **Not a skill** — this is where Claude actually invokes the Agent tool with the (possibly enhanced) prompt
- **Writes:** `execution.result` (the subagent's output), `execution.duration_seconds`

### 4. completion-enforcer
- **Skill:** `ghengis-skills:completion-enforcer`
- **Reads:** `execution.result`
- **Writes:** `completion_enforcer.status` ("done" | "partial" | "incomplete"), `completion_enforcer.concerns` (list)
- **Success:** status == "done" OR concerns empty
- **On fail:** flag to user, offer to re-run

### 5. hallucination-detector
- **Skill:** `ghengis-skills:hallucination-detector`
- **Reads:** `execution.result`
- **Writes:** `hallucination_detector.fabricated_urls`, `hallucination_detector.unsourced_stats`, `hallucination_detector.suspect_claims`
- **Success:** all three lists empty
- **On fail:** flag to user, block claims

### 6. audit-ledger
- **Skill:** `ghengis-skills:audit-ledger`
- **Reads:** entire scratchpad
- **Writes:** `audit_ledger.entry_id`, `audit_ledger.hash`
- **Success:** append succeeds

## Parallel Opportunities

Stages 4 and 5 (completion-enforcer and hallucination-detector) read the same `execution.result` and write to different subkeys — they're **parallel-safe**. Future optimization:

```yaml
- stage: post-checks
  parallel: true
  skills: [completion-enforcer, hallucination-detector]
```

Not enabled in v1 — keeping sequential for determinism. Flip when we have confidence.

## Failure Modes

| Stage | Failure | Recovery |
|-------|---------|----------|
| pql-validation | score < 0.5, no autofix available | Warn user, ask to proceed or revise |
| meta-prompting | enhanced_prompt still fails PQL | Fall back to original prompt, flag |
| execution | Agent returns error | Skip remaining stages, surface error |
| completion-enforcer | status == "incomplete" | Tell user, don't claim done |
| hallucination-detector | finds fabrications | Strip/flag in final output |
| audit-ledger | append fails | Log error, proceed (non-critical) |

## Example Scratchpad (Mid-Chain)

After stage 3 completes:

```json
{
  "chain": "agent-dispatch",
  "started_at": "2026-04-20T13:15:22Z",
  "current_stage": "completion-enforcer",
  "stages_completed": ["pql-validation", "meta-prompting", "execution"],
  "stages_remaining": ["completion-enforcer", "hallucination-detector", "audit-ledger"],
  "input": {
    "user_request": "Find all places where we handle user auth",
    "target_agent": "Explore",
    "prompt_draft": "find auth stuff"
  },
  "pql_validation": {
    "score": 0.35,
    "anti_patterns": ["vague-deliverable", "missing-role"],
    "suggested_fixes": ["add role", "specify output format"]
  },
  "meta_prompting": {
    "role_selected": "researcher",
    "enhanced_prompt": "You are a code archaeologist. Find every file that reads/writes authentication credentials. Report: file path, function name, and what auth system it uses. Output as markdown table."
  },
  "execution": {
    "result": "Found 7 files...",
    "duration_seconds": 23
  }
}
```
