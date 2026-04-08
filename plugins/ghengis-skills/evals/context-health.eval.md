# Context Health -- Evaluation

## TC-1: Detects Token Threshold Crossing for Full Tier Model
- **prompt:** "Continue working on the refactoring task" (session is at ~130,000 tokens with a Sonnet model)
- **context:** Full Tier model (Sonnet). Token estimate: 130,000. Zero prior truncations. No task drift detected. No tool failures.
- **assertions:**
  - Decision tree reaches step 5 -- tokens >= compact zone (120,000) for Full Tier
  - Action returned is "truncate", not "restart" (zero prior truncations)
  - Checkpoint summary is generated containing: original task, tools used, key findings, last progress
  - Checkpoint is between 300-500 tokens (~1200-2000 characters)
- **passing_grade:** 3/4 assertions must pass

## TC-2: Detects Task Drift and Re-Anchors
- **prompt:** "Refactor the authentication module to use JWT tokens" (session is at 90,000 tokens with Opus)
- **context:** Full Tier model. Token estimate: 90,000 (above 80,000 sweet spot). Recent 2000 characters of output discuss CSS styling for a dashboard, with zero overlap on "authentication", "JWT", "refactor", or "tokens". Drift score: 0.05.
- **assertions:**
  - Decision tree reaches step 6 -- tokens >= sweet spot AND drift score < 0.15
  - Action is "warn" with drift detection
  - Re-anchor message is generated containing the verbatim original instruction
  - Re-anchor message includes the computed similarity score and token count
  - No truncation or restart is triggered (drift is a lighter intervention)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Creates Proper Checkpoint on Restart
- **prompt:** "Keep going on the data pipeline build" (session is at 200,000 tokens with Opus)
- **context:** Full Tier model. Token estimate: 200,000 (above 180,000 hard limit). Two prior truncations already performed. Restart counter at 1.
- **assertions:**
  - Decision tree reaches step 3 -- tokens >= hard limit
  - Action is "restart" (checkpoint restart, not truncate)
  - Fresh context includes: system prompt, original instruction, checkpoint summary, continuation directive
  - Cooldown of 3 iterations is activated post-restart
  - Restart counter increments to 2
- **passing_grade:** 4/5 assertions must pass

## TC-4: Circuit Breaker Prevents Restart Loop
- **prompt:** "Continue building the API" (session is at 190,000 tokens with Opus)
- **context:** Full Tier model. Token estimate: 190,000 (above hard limit). Restart counter already at 3 (maximum reached).
- **assertions:**
  - Circuit breaker activates -- 3 restarts already performed
  - "Restart" action is downgraded to "truncate" instead
  - User warning is surfaced: task may be too large for a single session
  - No restart counter increment beyond 3
- **passing_grade:** 3/4 assertions must pass

## TC-5: Handles Tool Failure Spiral
- **prompt:** "Search for the configuration file and update the database URL"
- **context:** Any tier model. 10 tool calls made, 5 failed (50% failure rate). Token count is low (15,000 on Full Tier -- well within sweet spot).
- **assertions:**
  - Decision tree reaches step 2 -- tool failure rate > 40% with 4+ tool calls
  - Action is "restart" despite low token count (tool failure trumps token checks)
  - Restart rationale cites "agent confusion" or "corrupted context" from tool failure rate
  - If cooldown is active from a recent restart, the check is skipped (step 1 takes precedence)
- **passing_grade:** 3/4 assertions must pass
