---
name: task-complete
pattern: sequential
triggers:
  - event: stop
  - event: user_request
    keywords: ["verify this", "check my work", "run completion check"]
on_error: skip
estimated_duration: 5-20 seconds
---

## Purpose

Run post-task verification without needing a subagent. Lighter than `agent-dispatch` — just the "after" stages. Useful for Stop events or whenever Claude claims a task is done.

## Input Contract

```json
{
  "input": {
    "user_request": "<original task>",
    "claude_response": "<what Claude produced>",
    "files_touched": ["<list of paths>"]
  }
}
```

## Stages

### 1. completion-enforcer
- **Skill:** `ghengis-skills:completion-enforcer`
- **Reads:** `input.claude_response`, `input.user_request`
- **Writes:** `completion_enforcer.status`, `completion_enforcer.concerns`
- **Success:** status == "done" AND concerns empty
- **On fail:** don't claim done, flag to user

### 2. hallucination-detector
- **Skill:** `ghengis-skills:hallucination-detector`
- **Reads:** `input.claude_response`
- **Writes:** `hallucination_detector.fabricated_urls`, `hallucination_detector.unsourced_stats`, `hallucination_detector.suspect_claims`
- **Success:** all three lists empty
- **On fail:** flag specific fabrications inline

### 3. audit-ledger
- **Skill:** `ghengis-skills:audit-ledger`
- **Reads:** entire scratchpad
- **Writes:** `audit_ledger.entry_id`, `audit_ledger.hash`
- **Success:** append succeeds
- **On fail:** log error, continue (non-critical)

## Parallel Opportunities

Stages 1 and 2 read the same `input.claude_response` and write to different namespaces — parallel-safe. Enable via:

```yaml
- stage: post-checks
  parallel: true
  skills: [completion-enforcer, hallucination-detector]
```

Keep sequential for v1 until we have confidence.

## Difference from agent-dispatch

| Aspect | agent-dispatch | task-complete |
|--------|---------------|---------------|
| Triggers on | PreToolUse(Agent) | Stop |
| Has pre-stages | Yes (PQL + meta-prompting) | No |
| Scope | Subagent spawns | Any Claude response |
| Cost | Higher (Haiku PQL + meta) | Lower (verification only) |
