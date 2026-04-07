# Compute Adaptation -- Evaluation

## TC-1: Degrades Gracefully on Rate Limit
- **prompt:** "Continue building the API endpoints" (while rate limited)
- **context:** API provider returns 429 errors. Remaining capacity is 8% (below 10% threshold). Current tier is NORMAL. Budget is at 40% (well within budget).
- **assertions:**
  - Tier transitions from NORMAL to CRITICAL (remaining capacity < 10%)
  - Rate limit signal is the determining factor (most constrained dimension wins)
  - CRITICAL tier policies activate: no cascades, no parallel teams, fast models only, zero revision loops, max 5 tool calls
  - Model tier downgrade applies: any PREMIUM or BALANCED request is served as FAST
  - Budget signal does not override -- rate limit is more constrained
- **passing_grade:** 4/5 assertions must pass

## TC-2: Adapts Behavior Per Tier Correctly
- **prompt:** "Run the full OORT cascade for this refactoring task"
- **context:** Current tier is LOW (budget at 75% used). User requests a full cascade with builder-validator loops.
- **assertions:**
  - Cascade is still allowed at LOW tier (cascade_enabled: true)
  - Self-validation is disabled (self_validation: false at LOW)
  - E2E validation is disabled (e2e_validation: false at LOW)
  - Revision loops are reduced from 2 to 1
  - Model requests for PREMIUM are downgraded to BALANCED
  - If the same request came at CRITICAL tier, the cascade would be denied entirely
- **passing_grade:** 5/6 assertions must pass

## TC-3: Recovers Cautiously With Hysteresis
- **prompt:** "Check if we can upgrade back to normal operations"
- **context:** Tier is currently LOW. Last 3 consecutive health checks show: remaining capacity at 35%, 38%, 42%. Error rate is 2%. Budget at 55%.
- **assertions:**
  - Upgrade is allowed only after 2+ consecutive favorable checks (hysteresis rule)
  - All 3 checks show capacity > 30% -- sustained improvement confirmed
  - Tier upgrades from LOW to NORMAL
  - Immediate degradation rule contrast: if capacity dropped below 10% on a single check, downgrade would be instant (no hysteresis for degradation)
  - Re-evaluation interval is 10-30 seconds during active work
- **passing_grade:** 4/5 assertions must pass

## TC-4: Handles OFFLINE Tier Correctly
- **prompt:** "The API provider is completely unreachable -- continue working on the project"
- **context:** All API calls are failing (100% error rate). Provider is unreachable. Some cached results exist from earlier in the session.
- **assertions:**
  - Tier transitions to OFFLINE (100% error rate or provider unreachable)
  - Only local models are available (Ollama, llama.cpp)
  - Cached results are the primary source of information (prefer_cached: true)
  - API-dependent work is queued in a backlog file for later execution
  - Tool calls limited to 3 max and restricted to local-only tools (file operations, shell commands)
  - Complex work is NOT attempted with local models -- it is deferred
- **passing_grade:** 5/6 assertions must pass

## TC-5: Prevents Tier Flapping
- **prompt:** "Keep working on the data pipeline"
- **context:** Over the last 60 seconds, remaining capacity has oscillated: 28% (LOW), 32% (NORMAL), 29% (LOW), 33% (NORMAL), 27% (LOW). Five rapid tier transitions.
- **assertions:**
  - Hysteresis prevents rapid oscillation -- degradation to LOW happens immediately on first drop below 30%
  - Upgrade back to NORMAL requires 2+ consecutive checks above 30% (not just one)
  - The system settles at LOW rather than flapping between NORMAL and LOW
  - The anti-pattern "tier flaps between NORMAL and LOW every 30 seconds" is avoided
  - If the user forces a manual override, hysteresis is bypassed
- **passing_grade:** 4/5 assertions must pass
