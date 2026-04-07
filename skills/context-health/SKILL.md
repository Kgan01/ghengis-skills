---
name: context-health
description: Use during long-running sessions or complex multi-step tasks -- detects context window degradation, task drift from original request, and offers recovery strategies including checkpoint restart and re-anchoring
---

# Context Health

Detects when a long conversation or multi-step task is degrading due to context window pressure, task drift, or tool failure spirals. Provides recovery strategies: truncate, checkpoint-restart, re-anchor, or warn. Zero LLM cost, sub-millisecond latency -- pure heuristics and token estimation.

## When to Check Context Health

- **After every N tool calls** (every 5-10 is a good interval for complex tasks)
- **After producing long outputs** (each long output eats significant context)
- **After encountering errors** -- errors compound; 2+ consecutive failures is a signal
- **When your output starts feeling repetitive or off-topic** -- you may have drifted
- **At the start of each major step** in a multi-step task
- **When the user says "you already did that"** or "that's not what I asked" -- you have drifted

## Model-Aware Token Thresholds

Different models degrade at different context utilization levels. These thresholds are based on empirical quality degradation curves.

### Full Tier (resilient, less than 5% quality loss across wide range)
**Models:** opus, sonnet, gpt-4o, gpt-4, gpt-5, gemini-pro, gemini-2.5-pro, gemini-3-pro, claude-4, claude-3.5-sonnet, o1, o3

| Zone | Token Threshold | Action |
|------|----------------|--------|
| Sweet spot | 0 -- 80,000 | Continue normally |
| Approaching limit | 80,000 -- 120,000 | Check for drift, warn if detected |
| Compact zone | 120,000 -- 180,000 | Truncate old context |
| Hard limit | 180,000+ | Must restart with checkpoint |

### Compact Tier (degrades earlier, ~50% quality drop at upper range)
**Models:** haiku, gpt-4o-mini, gemini-flash, deepseek, codestral, grok, mistral-small, mistral-medium, gemini-2.0-flash, gemini-2.5-flash, gemini-3-flash, perplexity-sonar, groq-llama, claude-3.5-haiku

| Zone | Token Threshold | Action |
|------|----------------|--------|
| Sweet spot | 0 -- 20,000 | Continue normally |
| Approaching limit | 20,000 -- 30,000 | Check for drift, warn if detected |
| Compact zone | 30,000 -- 50,000 | Truncate old context |
| Hard limit | 50,000+ | Must restart with checkpoint |

### Local Tier (small context windows, aggressive thresholds)
**Models:** llama, mistral-7b, codellama, phi-, qwen-

| Zone | Token Threshold | Action |
|------|----------------|--------|
| Sweet spot | 0 -- 8,000 | Continue normally |
| Approaching limit | 8,000 -- 16,000 | Check for drift, warn if detected |
| Compact zone | 16,000 -- 32,000 | Truncate old context |
| Hard limit | 32,000+ | Must restart with checkpoint |

**Unknown models default to Compact Tier** -- conservative is safer than optimistic.

## Token Estimation

Quick heuristic: ~4 characters per token. Count the total characters in all messages and divide by 4. This is accurate within ~10% for English text and is sufficient for threshold decisions.

For messages with tool use blocks, also count `JSON.stringify(input)` content and tool result text.

## The Decision Tree

This is the core logic. Evaluate in order -- first match wins.

```
1. Cooldown active?
   YES --> continue (prevent restart spam after recent restart)

2. Tool failure rate > 40% (with at least 4 tool calls)?
   YES --> restart (agent is confused, context is likely corrupted)

3. Tokens >= hard limit?
   YES --> restart (severe degradation, output quality is collapsing)

4. Tokens >= compact zone AND 2+ prior truncations?
   YES --> restart (truncation has diminishing returns, start fresh)

5. Tokens >= compact zone?
   YES --> truncate (remove old messages, keep recent work)

6. Tokens >= sweet spot AND task drift < 0.15?
   YES --> warn (agent has drifted from original request)

7. Otherwise --> continue
```

### Circuit Breaker: Maximum 3 Restarts

To prevent infinite restart loops, cap restarts at 3 per session. After 3 restarts, downgrade all "restart" actions to "truncate" instead. If truncation also fails to help, warn the user that the task may be too large for a single session.

## Task Drift Detection

Drift detection measures how much your current output relates to the original request.

**Method: Asymmetric word overlap**

Compare the words in the original instruction against the words in the last ~2000 characters of output.

```
drift_score = |instruction_words INTERSECT recent_output_words| / |instruction_words|
```

- Score of 1.0 = all instruction keywords present in recent output (on-topic)
- Score of 0.15 or below = significant drift (most instruction keywords absent from recent output)
- Only the last 2000 characters of recent output are checked (not diluted by long history)

This is asymmetric on purpose: a 500-word response to a 4-word instruction scores high as long as it mentions the key words. Unlike Jaccard similarity, long outputs do not dilute the score.

**Drift only triggers a warning when tokens exceed the sweet spot threshold.** Short conversations do not need drift checks.

## Recovery Strategy 1: Truncate

Remove old messages while preserving the ability to continue.

**What to keep:**
1. System prompt (always)
2. Original user instruction (always)
3. Checkpoint summary (injected after instruction)
4. Last 2 message pairs (most recent context)

**Checkpoint summary captures:**
- Original task (first 300 characters of instruction)
- Tools used so far (up to 10 tool names)
- Key findings from tool results (last 5, truncated to 200 chars each)
- Last progress (most recent assistant output, first 500 chars)
- Target: 300-500 tokens (~1200-2000 characters)

**Checkpoint message format:**
```
[CONTEXT CHECKPOINT -- PREVIOUS PROGRESS]
Original task: {instruction}
Tools used: {tool_names}
Key findings:
  - {finding_1}
  - {finding_2}
Last progress: {last_assistant_output}
[END CHECKPOINT]

Continue from where you left off. Do not repeat completed work.
```

Track truncation count. After 2 truncations, the next compact-zone trigger escalates to restart (diminishing returns).

## Recovery Strategy 2: Checkpoint Restart

A complete context reset with full knowledge carry-forward. Used when truncation is no longer effective.

**Fresh context structure:**
1. System prompt (original)
2. User message containing: original instruction + checkpoint + continuation directive

**Restart message format:**
```
{original_instruction}

[CONTEXT CHECKPOINT -- PREVIOUS PROGRESS]
{checkpoint_summary}
[END CHECKPOINT]

Continue from where the previous execution left off.
Do not repeat completed work. Pick up at the next step.
```

**After restart:**
- Activate a 3-iteration cooldown (no health checks for 3 cycles to let the fresh context stabilize)
- Increment restart counter (toward the 3-restart circuit breaker)
- Reset step counter to 0

## Recovery Strategy 3: Re-Anchoring

Lighter than truncate or restart. Injects the original request back into context when drift is detected, without removing any messages.

**When to re-anchor:**
- Health check returns "warn" with task drift detected
- User feedback indicates you have gone off-topic
- You notice your own output diverging from the original request

**Re-anchor message format:**
```
[RE-ANCHOR -- Context drift detected]

Your recent output has drifted from the original request.
Reason: Task drift detected (similarity=0.12) at 85,000 tokens

ORIGINAL REQUEST (verbatim):
{original_instruction}

Refocus on satisfying this specific request.
Do not repeat completed work -- continue from where you are,
but ensure your output addresses the original request above.
```

## Recovery Strategy 4: Warn User

When context health is degrading but not yet critical, surface the concern:

- "This task is approaching context limits. Consider breaking remaining work into a follow-up session."
- "Tool failure rate is high (40%+). The remaining context may be unreliable."
- "Output appears to have drifted from the original request."

## Tool Failure Tracking

Track tool calls and failures across the session:

| Metric | Threshold | Signal |
|--------|-----------|--------|
| Failure rate > 40% | Minimum 4 tool calls | Agent is confused or context is corrupted |
| Consecutive failures 3+ | Any count | Likely a systematic issue, not transient |
| Same tool failing repeatedly | 2+ failures of same tool | Tool-specific problem, try alternative approach |

High tool failure rates often indicate the agent's context has degraded enough that it is generating malformed tool calls, wrong parameters, or calling tools inappropriately.

## Checkpoint Format Reference

When you need to capture state before a restart or at a manual checkpoint:

```
## Checkpoint: {task_name}
**Status:** {percentage or step X of Y}
**Completed:**
- {what was done}
- {what was done}
**Key decisions:**
- {why you chose approach X over Y}
- {important findings that affect remaining work}
**Remaining work:**
- {next step}
- {remaining steps}
**Blockers:**
- {anything that prevented progress}
```

## Integration with Other Skills

- **completion-enforcer** checks whether the final output is complete. Context health checks whether the environment can still produce quality output.
- **constitutional-ai** enforces safety rules regardless of context health. Even degraded contexts must respect constitutional boundaries.
- **hallucination-detector** catches fabricated content, which becomes more likely as context degrades. Run hallucination detection more aggressively when context health is in the compact zone or beyond.

## Cost

$0. Zero LLM calls. All checks are character counting, word overlap computation, and threshold comparison. Apply on every iteration of long-running tasks.
