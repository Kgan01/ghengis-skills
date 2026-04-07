# Task Tracking -- Evaluation

## TC-1: Happy Path -- Task Intake and Prioritization
- **prompt:** "I need to redesign our company website, respond to 3 client emails, fix a production bug, and organize my desk. Help me prioritize."
- **context:** Mixed list of tasks with varying urgency and importance. Tests Eisenhower matrix and priority assignment.
- **assertions:**
  - Tasks are categorized using the Eisenhower matrix (urgent/important quadrants) or P0-P3 priority levels
  - Production bug is identified as highest priority (Q1 / P0 -- urgent and important)
  - Client emails are ranked as high priority (Q1 or Q3 depending on urgency assessment)
  - Website redesign is identified as important but not urgent (Q2 / P1-P2) and flagged for decomposition
  - Desk organization is identified as low priority (Q4 / P3 or eliminate)
  - Website redesign (XL task) is flagged as needing decomposition into smaller tasks
- **passing_grade:** 5/6 assertions must pass

## TC-2: Edge Case -- Vague Task Definition
- **prompt:** "Add 'work on the app' to my task list."
- **context:** Deliberately vague task. Skill methodology says every task needs a clear verb and specific deliverable.
- **assertions:**
  - Response flags "work on the app" as too vague
  - Asks clarifying questions: what specific outcome, what's the next physical action, how long will it take
  - References the vague task pitfall ("Bad: 'Work on website'; Good: 'Update homepage hero image'")
  - Suggests reformulating with a specific verb and deliverable
- **passing_grade:** 3/4 assertions must pass

## TC-3: Happy Path -- Sprint Planning
- **prompt:** "I have 40 hours this week. Here are my tasks: build login page (8h), write API docs (4h), review 5 PRs (5h), team meeting (2h), fix CSS bug (1h), refactor database queries (6h), onboard new hire (3h), design email templates (4h), update dependencies (2h), write unit tests (6h). Plan my week."
- **context:** Total tasks sum to 41 hours. Tests the over-commitment pitfall and sprint planning methodology.
- **assertions:**
  - Response flags that 41 hours of tasks exceeds realistic capacity (should plan for ~24 hours / 60% utilization)
  - Tasks are selected and prioritized, not all crammed into the week
  - Some tasks are deferred to backlog or next week
  - Tasks are distributed across days with consideration for deep work vs light work patterns
  - Buffer time (40% of capacity) is preserved for interruptions and ad-hoc requests
- **passing_grade:** 4/5 assertions must pass

## TC-4: Edge Case -- Blocked Task Handling
- **prompt:** "I can't start the API integration because the backend team hasn't deployed the new endpoints yet. What should I do?"
- **context:** Task is blocked by an external dependency. Tests dependency resolution methodology.
- **assertions:**
  - Response identifies this as a blocked task (Finish-to-Start dependency)
  - Recommends marking the task as "Blocked" with the specific blocker identified
  - Suggests contacting the backend team to get an ETA
  - Recommends finding parallel work that doesn't depend on the blocked endpoints
  - Mentions the escalation rule: escalate if blocker persists more than 2 days
- **passing_grade:** 4/5 assertions must pass

## TC-5: Quality Check -- Task Decomposition
- **prompt:** "I need to build a mobile app for our company. Add it as a task."
- **context:** Massive multi-month effort presented as a single task. Tests decomposition rules.
- **assertions:**
  - Response flags this as an XL task (more than 8 hours) that must be decomposed
  - Breaks it down into epics (1+ week each), stories (1-3 days each), or tasks (2-4 hours each)
  - Follows the hierarchy: Epic -> Stories -> Tasks
  - Each sub-task has a clear verb and specific deliverable
  - Provides effort estimates (S/M/L) for the broken-down tasks
- **passing_grade:** 4/5 assertions must pass
