# Goal Tracking -- Evaluation

## TC-1: Detects Explicit Goal From User Request
- **prompt:** "Build a REST API for user management with CRUD endpoints"
- **context:** Fresh session, no existing goals. User message contains a direct request with clear deliverable.
- **assertions:**
  - A new top-level goal is created: "[G1] Build a REST API for user management"
  - Goal state is ACTIVE
  - Sub-goals are decomposed (e.g., G1.1 design endpoints, G1.2 implement handlers, G1.3 write tests)
  - Maximum depth does not exceed 3 levels
  - One-off question detection rule does NOT fire (this is clearly a task, not a question)
- **passing_grade:** 4/5 assertions must pass

## TC-2: Links Related Request to Existing Goal via Fuzzy Matching
- **prompt:** "Fix the token refresh endpoint" (said after earlier work on authentication)
- **context:** Active goal exists: "[G1] Implement JWT authentication with refresh tokens". No other active goals.
- **assertions:**
  - Fuzzy matching fires -- word overlap on "token" and "refresh" against G1 yields score >= 0.4
  - New work is linked as a sub-goal of G1, not created as a new top-level goal
  - Match is logged with the computed score (e.g., "Linked to existing goal [G1] (score: 0.50)")
  - If two goals scored similarly, the skill would ask the user which one (ambiguity handling)
- **passing_grade:** 3/4 assertions must pass

## TC-3: Tracks State Transitions Correctly
- **prompt:** "The auth middleware is done, let's move on to the API endpoints"
- **context:** Active goals: G1 (parent), G1.1 (auth middleware -- ACTIVE), G1.2 (API endpoints -- BLOCKED by G1.1), G1.3 (tests -- BLOCKED by G1.2).
- **assertions:**
  - G1.1 transitions from ACTIVE to COMPLETED
  - G1.2 transitions from BLOCKED to ACTIVE (blocker G1.1 resolved)
  - G1.3 remains BLOCKED (still depends on G1.2)
  - G1 (parent) remains ACTIVE -- not all children are COMPLETED
  - Terminal state rule is respected -- G1.1 COMPLETED is never reopened; if rework needed, a new goal is created
- **passing_grade:** 4/5 assertions must pass

## TC-4: Detects Goal Staleness
- **prompt:** "What should we work on next?" (asked after a long pause)
- **context:** Two active goals: G1 (last activity 4 hours ago, no sub-goal completions in that time), G2 (last activity 30 minutes ago with recent progress). Session has been running with no state changes on G1.
- **assertions:**
  - G1 is flagged as stale (ACTIVE for 3+ hours without state change or sub-goal completion)
  - G2 is NOT flagged as stale (recent activity)
  - Staleness response lists G1 with last activity timestamp
  - Suggestion options are presented: continue, re-scope, or abandon G1
  - If user does not respond, G1 stays ACTIVE but is deprioritized
- **passing_grade:** 4/5 assertions must pass

## TC-5: Does Not Create Goals for Simple Questions
- **prompt:** "What does the `__post_init__` method do in Python dataclasses?"
- **context:** Active goals exist for an ongoing project. User asks a standalone informational question.
- **assertions:**
  - No new goal is created (detection rule 4: do NOT create goals for simple one-off questions)
  - Existing goals are not modified
  - Fuzzy matching may run but does not link this to an existing goal (low overlap score)
  - Goal tracker state remains unchanged after answering
- **passing_grade:** 3/4 assertions must pass
