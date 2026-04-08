---
name: compute-adaptation
description: Use when building resilient agent workflows -- provides graceful degradation strategies across 4 compute tiers, adapting agent behavior when hitting rate limits, budget constraints, or resource limitations
---

# Compute Adaptation

Graceful degradation for agent workflows. When you hit rate limits, blow your budget, or lose access to a provider, do not fail -- adapt. Four tiers define what capabilities are available at each resource level, so workflows degrade smoothly instead of crashing.

This is a resilience methodology, not a runtime library. Apply it by checking your resource state before making decisions, adjusting your approach when constrained, and recovering when resources return.

## The 4 Tiers

| Tier | State | What You Can Do | What You Cannot Do |
|------|-------|----------------|--------------------|
| **NORMAL** | Full capacity | Everything -- premium models, parallel agents, cascades, validation loops | Nothing restricted |
| **LOW** | Approaching limits | Balanced models, reduced parallelism, skip non-essential validation | Premium models, E2E validation, self-validation loops |
| **CRITICAL** | Near exhaustion | Fast models only, single-agent execution, cached results preferred | Cascades, parallel teams, revision loops, documentation |
| **OFFLINE** | No API access | Local models only, cached results, queue work for later | Any API call, any cloud model, any external tool |

## Tier Policies

Each tier defines explicit feature flags. Before executing any capability, check whether it is allowed at the current tier.

### NORMAL -- Full Capabilities

```
max_model_tier:     premium (Opus, GPT-4, etc.)
cascade_enabled:    true
team_enabled:       true    (parallel agent teams)
self_validation:    true    (builder-validator loops)
e2e_validation:     true    (end-to-end integration checks)
max_revision_loops: 2
max_tool_calls:     10      (per execution)
prefer_cached:      false
```

This is the default. Use the best tools for the job without constraint.

### LOW -- Conserve Resources

```
max_model_tier:     balanced (Sonnet, GPT-4o-mini, etc.)
cascade_enabled:    true
team_enabled:       true
self_validation:    false   (skip to save tokens)
e2e_validation:     false   (skip expensive final validation)
max_revision_loops: 1
max_tool_calls:     8
prefer_cached:      false
```

Still capable, but leaner. Key adaptations:
- Downgrade model requests: if an agent requests premium, serve balanced instead
- Cut revision loops from 2 to 1 -- get it right the first time or ship with notes
- Skip self-validation -- trust the builder's output unless a human reviewer catches issues
- Skip E2E validation -- unit-level checks only

### CRITICAL -- Survival Mode

```
max_model_tier:     fast (Haiku, GPT-4o-mini, etc.)
cascade_enabled:    false   (no cascades -- direct routing only)
team_enabled:       false   (no parallel teams)
self_validation:    false
e2e_validation:     false
max_revision_loops: 0
max_tool_calls:     5
prefer_cached:      true    (use cached results when available)
```

Bare minimum execution. Key adaptations:
- Single-agent execution only -- no cascades, no teams, no delegation
- Fast models only -- every request goes to the cheapest capable model
- Zero revision loops -- output ships as-is
- Prefer cached results -- if you have a recent answer, use it instead of calling the API
- Reduce tool calls -- only the essential ones

### OFFLINE -- Local Only

```
max_model_tier:     local (Ollama, local inference only)
cascade_enabled:    false
team_enabled:       false
self_validation:    false
e2e_validation:     false
max_revision_loops: 0
max_tool_calls:     3
prefer_cached:      true
```

No external API access at all. Key adaptations:
- Local models only -- Ollama, llama.cpp, or whatever runs on the machine
- Cached results are primary -- only generate new content if cache misses
- Queue work for later -- record what needs to be done and execute when connectivity returns
- Limit tool calls to local-only tools (file operations, shell commands, local search)

## What Triggers Tier Changes

### Rate Limit Signals

Monitor remaining capacity as a percentage of the limit:

| Remaining Capacity | Tier |
|-------------------|------|
| > 30% | NORMAL |
| 10% - 30% | LOW |
| < 10% | CRITICAL |
| 0% or provider unreachable | OFFLINE |

Check across multiple dimensions: request count, token count, and per-model limits. The most constrained dimension determines the tier.

### Budget Thresholds

Track cumulative spend against a daily or session budget:

| Budget Used | Tier |
|------------|------|
| < 70% | NORMAL |
| 70% - 90% | LOW |
| > 90% | CRITICAL |
| 100% (hard cap) | OFFLINE |

Default daily budget: $5.00. Adjust based on your context.

### Error Rate Signals

Track API call success rates over a sliding window:

| Error Rate | Signal |
|-----------|--------|
| < 5% | NORMAL |
| 5% - 20% | Downgrade one tier |
| > 20% | Downgrade two tiers |
| 100% (all calls failing) | OFFLINE |

### Latency Spikes

Track response times relative to baseline:

| Latency vs. Baseline | Signal |
|---------------------|--------|
| < 2x baseline | NORMAL |
| 2x - 5x baseline | Consider LOW |
| > 5x baseline | Consider CRITICAL |
| Timeouts | OFFLINE |

### Manual Override

Force a specific tier when you know your constraints:

- Testing with limited budget: force LOW
- Demo mode with no API access: force OFFLINE
- Known rate limit window: force CRITICAL during the window

## Model Tier Downgrade

When a task requests a model tier higher than what the current compute tier allows, downgrade automatically.

```
Model tier ordering: LOCAL < FAST < BALANCED < PREMIUM

Example at LOW tier:
  Request PREMIUM  -->  Serve BALANCED (downgraded)
  Request BALANCED -->  Serve BALANCED (no change)
  Request FAST     -->  Serve FAST     (no change)
  Request LOCAL    -->  Serve LOCAL    (no change)

Example at CRITICAL tier:
  Request PREMIUM  -->  Serve FAST (downgraded)
  Request BALANCED -->  Serve FAST (downgraded)
  Request FAST     -->  Serve FAST (no change)
```

The caller does not need to know about the downgrade -- it gets the best available model within the current tier's constraints.

## Per-Tier Behavior Guide

### What to Do at Each Tier

**NORMAL:**
- Use the full OORT cascade pattern when tasks warrant it
- Spawn parallel agent teams for multi-perspective work
- Run builder-validator loops with up to 2 revisions
- Use premium models for complex reasoning
- Run E2E validation on deliverables

**LOW:**
- Simplify cascades: Builder + Validator minimum, skip Documenter
- Reduce team size from N agents to N/2
- Cut revision loops to 1 -- if the first revision does not pass, ship with notes
- Use balanced models -- they handle most tasks well
- Skip E2E validation -- unit-level checks are sufficient

**CRITICAL:**
- No cascades -- single-agent direct execution
- No teams -- one agent handles the entire task
- No revision loops -- output ships as-is
- Use fast models -- optimize for speed and cost, not quality ceiling
- Check cache before every API call
- Skip documentation and archival tasks -- focus on the primary deliverable

**OFFLINE:**
- Use local models (Ollama) for any generation tasks
- Serve cached results wherever possible
- Queue API-dependent work in a backlog file for later execution
- Limit scope to what can be accomplished with local tools
- Record what you cannot do and why, so recovery can pick it up

## Cost Tracking

Track cumulative cost to drive tier transitions. At minimum, track:

```jsonl
{"timestamp": "2026-04-07T14:00:00Z", "model": "claude-sonnet", "tokens_in": 1200, "tokens_out": 800, "cost_usd": 0.006}
{"timestamp": "2026-04-07T14:01:00Z", "model": "claude-haiku", "tokens_in": 500, "tokens_out": 200, "cost_usd": 0.0003}
```

Aggregate by time window (hourly, daily) and compare against budget thresholds to determine tier.

### Estimating Cost

When exact cost is not available, estimate from token counts:

| Model Tier | Approximate Cost per 1K Tokens |
|-----------|-------------------------------|
| Premium (Opus) | $0.015 input / $0.075 output |
| Balanced (Sonnet) | $0.003 input / $0.015 output |
| Fast (Haiku) | $0.00025 input / $0.00125 output |
| Local | $0 (electricity only) |

## Recovery: Upgrading Tiers

Tier degradation should not be permanent. Monitor for recovery signals:

| Signal | Recovery Action |
|--------|----------------|
| Rate limit window resets | Re-evaluate, upgrade if capacity > 30% |
| New billing period starts | Reset budget tracking, upgrade to NORMAL |
| Error rate drops below 5% | Upgrade one tier |
| Provider comes back online | Re-evaluate all checks, upgrade accordingly |

### Re-Evaluation Interval

Check conditions every 10-30 seconds during active work. Do not check on every single API call -- that adds overhead. Do not wait minutes between checks -- that delays recovery.

### Hysteresis

Avoid tier flapping by requiring sustained improvement before upgrading:

- Degrade immediately when thresholds are crossed (fail fast)
- Upgrade only after conditions remain favorable for 2+ consecutive checks (recover cautiously)

## Practical Application in Claude Code

### When Rate-Limited

Claude Code sessions hit rate limits during intensive work. When you notice slower responses or 429 errors:

1. Switch to CRITICAL tier mentally -- simplify your approach
2. Batch related questions into fewer, more comprehensive prompts
3. Use cached context from earlier in the session instead of re-reading files
4. Skip nice-to-have validation passes
5. Focus on the highest-priority deliverable

### When Context Is Running Low

As context window fills up:

1. Switch to LOW or CRITICAL tier for the remaining work
2. Summarize accumulated context instead of referencing raw sources
3. Skip exploratory research -- use what you already know
4. Produce the deliverable directly instead of iterating on drafts
5. Record what you would do with more context for a follow-up session

### When a Session Is Getting Expensive

If token usage is high and you want to control costs:

1. Track approximate token usage mentally across the conversation
2. Switch to simpler approaches: direct answers over multi-step analysis
3. Skip optional documentation and polish passes
4. Use existing code patterns instead of researching new approaches
5. Deliver the minimum viable output and note what could be improved

## Integration with Other Patterns

| Pattern | How It Uses Compute Adaptation |
|---------|-------------------------------|
| **OORT Cascade** | Cascades are disabled at CRITICAL+; at LOW, reduce team size and revision loops |
| **Audit Ledger** | Record tier changes as `state_change` entries with old/new tier |
| **Constitutional AI** | `minimize_cost` rule reinforces tier-appropriate model selection |
| **Deep Research** | Reduce max iterations at LOW; skip red-team phase at CRITICAL |
| **Goal Tracking** | Mark goals as "deferred" when OFFLINE prevents completion |

## Decision Quick Reference

```
Can I use a cascade?
  NORMAL/LOW: yes    CRITICAL/OFFLINE: no

Can I spawn parallel agents?
  NORMAL/LOW: yes    CRITICAL/OFFLINE: no

Can I use a premium model?
  NORMAL: yes    LOW/CRITICAL/OFFLINE: no

Should I check cache first?
  NORMAL/LOW: optional    CRITICAL/OFFLINE: yes

Can I run revision loops?
  NORMAL: 2 loops    LOW: 1 loop    CRITICAL/OFFLINE: 0 loops
```

## Anti-Patterns

| If you notice... | The problem is... | Fix it by... |
|-----------------|-------------------|-------------|
| Session crashes on rate limit | No degradation strategy | Checking rate limit headers and adapting before hitting the wall |
| Tier stuck at CRITICAL forever | No recovery monitoring | Re-evaluating conditions periodically and upgrading when resources return |
| NORMAL tier burns through budget in 10 minutes | No cost tracking | Tracking cumulative cost and triggering LOW at 70% budget |
| Tier flaps between NORMAL and LOW every 30 seconds | No hysteresis | Requiring 2+ consecutive favorable checks before upgrading |
| OFFLINE tier produces garbage from local models | Expecting too much from local inference | Queuing complex work for later and only doing simple tasks locally |
| Every task runs at NORMAL regardless of constraints | Tier checks not wired in | Checking the tier before every model call and capability decision |
