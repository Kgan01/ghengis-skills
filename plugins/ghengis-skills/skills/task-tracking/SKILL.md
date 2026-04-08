---
name: task-tracking
description: Use when helping organize tasks, projects, or priorities — covers GTD methodology, Eisenhower matrix, project breakdown, and systematic task management
---

# Task Tracking & Management

## When to Use
When helping organize tasks, manage projects, set priorities, break down large initiatives, plan sprints, track progress, or design productivity systems.

## Core Concepts

### GTD (Getting Things Done) Phases
1. **Capture**: Collect all tasks in inbox (brain dump)
2. **Clarify**: Is it actionable? If yes, define next action. If no, trash/reference/someday
3. **Organize**: Categorize by context (@home, @work, @computer, @phone)
4. **Reflect**: Weekly review of all lists
5. **Engage**: Do tasks based on context, time, energy, priority

### Eisenhower Matrix
```
                Urgent          Not Urgent
Important    | DO NOW (Q1)    | SCHEDULE (Q2)  |
             | Crises         | Planning       |
             | Deadlines      | Learning       |
             |----------------|----------------|
Not Important| DELEGATE (Q3)  | ELIMINATE (Q4) |
             | Interruptions  | Time wasters   |
             | Busy work      | Distractions   |
```
**Goal**: Minimize Q1 (crises), maximize Q2 (proactive), eliminate Q4.

### Task States
- **Backlog**: Not started, not scheduled
- **Todo**: Ready to work, in current sprint/week
- **In Progress**: Actively being worked on
- **Blocked**: Waiting on dependency or external input
- **Review**: Done, needs validation/testing
- **Done**: Completed and verified
- **Archived**: Completed or canceled (removed from active views)

### Task Decomposition Rules
```
Large task (>2 hours) -> Break into subtasks (<1 hour each)
Epic (>1 week) -> Break into stories (1-3 days each)
Story -> Break into tasks (2-4 hours each)

Example:
Epic: "Launch website" (2 weeks)
|- Story: "Design homepage" (2 days)
|  |- Task: "Wireframe layout" (2h)
|  |- Task: "Choose color palette" (1h)
|  |- Task: "Create Figma mockup" (3h)
|- Story: "Implement backend API" (3 days)
|  |- Task: "Set up database schema" (4h)
```

### Dependency Types
- **Finish-to-Start (FS)**: Task B starts when Task A finishes (most common)
- **Start-to-Start (SS)**: Task B starts when Task A starts (parallel work)
- **Finish-to-Finish (FF)**: Task B finishes when Task A finishes (coordinated delivery)
- **Start-to-Finish (SF)**: Task B finishes when Task A starts (rare, shift handoffs)

## Patterns & Procedures

### Task Intake Process
```
1. User says: "I need to [do something]"
2. Clarify:
   - Is it actionable? (Yes/No)
   - If no -> Trash, Reference, or Someday list
   - If yes -> Continue
3. Define:
   - What's the desired outcome?
   - What's the very next physical action?
   - How long will it take? (<2 min -> do now, else -> queue)
4. Categorize:
   - Context: @home, @work, @computer, @calls, @errands
   - Priority: P0 (critical), P1 (high), P2 (medium), P3 (low)
   - Effort: S (small <1h), M (medium 1-4h), L (large 4-8h), XL (>8h -> decompose)
5. Organize:
   - If urgent+important (Q1) -> Do today
   - If important+not urgent (Q2) -> Schedule this week
   - If urgent+not important (Q3) -> Delegate or batch
   - If not important+not urgent (Q4) -> Eliminate or someday
```

### Sprint Planning (Weekly)
```
Every Monday (or Friday for next week):
1. Review last week's completion rate (aim for 70-80%)
2. Pull incomplete tasks from last week (if still relevant)
3. Select new tasks from backlog:
   - Max capacity: 20-25 hours (not 40 -> buffer for interrupts)
   - Mix of P0/P1 (urgent) and P2 (important but not urgent)
   - Balance: 60% planned work, 40% buffer for ad-hoc requests
4. Assign tasks to days:
   - Monday: Lighter load (email catchup, planning)
   - Tue-Thu: Heavy lifting (deep work)
   - Friday: Wrap-ups, reviews, planning next week
5. Identify blockers early (dependencies not yet complete)
```

### Daily Standup Structure
```
For each person or project:
1. What did you complete yesterday?
2. What will you work on today?
3. Any blockers? (dependencies, waiting on others, unclear requirements)

Signals to watch:
- Tasks in progress >2 days (may be stuck)
- Blocked tasks (need unblocking action)
- Sprint >80% through with <50% completion
```

### Dependency Resolution
```
When a task is blocked:
1. Identify the blocker (task ID or external dependency)
2. Check blocker status:
   - If in progress -> Estimate completion, notify assignee
   - If not started -> Escalate (why hasn't it started?)
   - If external -> Create follow-up task to check status
3. Mark task as "Blocked" (don't count toward sprint capacity)
4. Find parallel work (other tasks that don't depend on blocker)
```

### Status Reporting
```
Weekly Report Format:
- Sprint Goal: [What we planned to achieve]
- Completion Rate: X/Y tasks done (Z%)
- Key Accomplishments: [3-5 bullet points]
- Blockers: [List with owner and ETA]
- Next Week Focus: [Top 3 priorities]

Monthly Report Format:
- Total tasks completed: X
- On-time delivery rate: Y%
- Average cycle time: Z days (from Todo -> Done)
- Backlog size: N tasks (growing/stable/shrinking?)
- Top categories: [e.g., 40% bugs, 30% features, 20% tech debt]
```

## Common Pitfalls

### Over-Commitment
- **Symptom**: Sprint with 40 hours of work for 40-hour workweek
- **Reality**: Meetings, emails, interruptions take 30-40% of time
- **Fix**: Plan for 60% utilization (24 hours of tasks for 40-hour week)

### Vague Tasks
- **Bad**: "Work on website"
- **Good**: "Update homepage hero image with new photo from /assets folder"
- **Rule**: Every task needs a clear verb and specific deliverable

### Skipping Decomposition
- **Problem**: "Build mobile app" as single task (2-month effort)
- **Impact**: Task stuck in progress for weeks, no visible progress
- **Fix**: Break into epics -> stories -> tasks (nothing >1 day)

### Ignoring Blockers
- **Mistake**: Leaving task in "Blocked" state for weeks without action
- **Reality**: Blocked = progress stopped, needs immediate attention
- **Fix**: Daily review of blocked tasks, escalate after 2 days

### Priority Inflation
- **Issue**: Everything marked as P0 (critical)
- **Result**: No way to distinguish actual urgency
- **Fix**: Max 20% of tasks can be P0, force rank the rest

### Zombie Tasks
- **Symptom**: Tasks in backlog for 6+ months, never prioritized
- **Solution**: Quarterly backlog grooming (delete/archive anything not done in 3 months)

## Quick Reference

### Task Estimation Guidelines
```
S (Small):    <1 hour  (bug fix, copy change, config tweak)
M (Medium):   1-4 hours (small feature, refactor, integration)
L (Large):    4-8 hours (complex feature, requires research)
XL (X-Large): >8 hours  (DECOMPOSE INTO SMALLER TASKS)
```

### Priority Assignment
```
P0: Production down, security issue, blocking deadline today
P1: Important deadline this week, customer-facing bug, key feature
P2: Nice to have, quality improvements, non-urgent bugs
P3: Backlog, future ideas, low-impact enhancements
```

### Context Tags
```
@computer: Requires laptop (coding, writing, design)
@phone: Calls, texts, mobile-only tasks
@home: Chores, personal errands, home office work
@work: Office-only tasks (meetings, in-person collab)
@errands: Outside tasks (shopping, post office, bank)
@low-energy: Easy tasks for tired moments (email, admin)
@high-energy: Deep work for peak focus (coding, writing, strategy)
```

### Common Task Patterns
```
Bug Report -> Reproduce -> Fix -> Test -> Deploy -> Close
Feature Request -> Spec -> Design -> Implement -> Test -> Ship
Research Task -> Define question -> Gather info -> Synthesize -> Report
Content Task -> Outline -> Draft -> Edit -> Review -> Publish
```

### Velocity Calculation
```
Velocity = (Total points completed) / (Number of sprints)

Example:
Sprint 1: 20 points completed
Sprint 2: 25 points completed
Sprint 3: 22 points completed
Velocity = (20+25+22)/3 = 22.3 points/sprint

Use velocity to plan future sprints (don't overcommit).
```

## Checklists

### Daily Task Review (Morning)
- [ ] Review tasks assigned for today
- [ ] Check for new urgent/critical tasks (P0)
- [ ] Identify blockers (mark as blocked, notify owner)
- [ ] Prioritize 3 MITs (Most Important Tasks)
- [ ] Time-block focus time for deep work
- [ ] Clear quick wins (<15 min tasks) first

### Daily Task Review (Evening)
- [ ] Mark completed tasks as Done
- [ ] Update in-progress tasks (add notes/blockers)
- [ ] Move incomplete tasks to tomorrow or backlog
- [ ] Log time spent (optional, for velocity tracking)
- [ ] Identify tomorrow's top 3 MITs

### Weekly Sprint Planning
- [ ] Review last week's completion rate
- [ ] Groom backlog (archive old, reprioritize)
- [ ] Select tasks for upcoming week (60% capacity)
- [ ] Check dependencies (ensure blockers are resolved)
- [ ] Balance priorities (mix of Q1 and Q2)
- [ ] Assign tasks to specific days
- [ ] Communicate sprint goal to team

### Monthly Backlog Grooming
- [ ] Archive tasks >3 months old (not started)
- [ ] Reprioritize based on changed goals
- [ ] Decompose large tasks (break down epics)
- [ ] Remove duplicate/obsolete tasks
- [ ] Update task descriptions (clarify vague ones)
- [ ] Check dependency chains (are they still valid?)

### Blocking a Task
- [ ] Identify blocker (task ID or external dependency)
- [ ] Assign blocker owner (who can resolve it?)
- [ ] Set expected resolution date
- [ ] Notify assignee (don't let it sit silently)
- [ ] Find alternative work (parallel tasks)
- [ ] Escalate if blocker persists >2 days
