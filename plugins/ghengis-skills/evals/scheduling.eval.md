# Scheduling -- Evaluation

## TC-1: Happy Path -- Schedule a Meeting with Constraints
- **prompt:** "Schedule a 1-hour team meeting this week. I have focus time blocked 9-11am daily and lunch at noon. My afternoons are mostly free."
- **context:** User has existing calendar constraints. Tests optimal meeting placement and preference conflict avoidance.
- **assertions:**
  - Proposed time respects the 9-11am focus block (does not schedule during it)
  - Proposed time avoids the 12-1pm lunch hour
  - Meeting is placed in an optimal afternoon slot (2-4pm recommended for team meetings)
  - Buffer time is accounted for (10 min buffer for a 60-min meeting)
  - Response confirms the proposed time and asks for approval before finalizing
- **passing_grade:** 4/5 assertions must pass

## TC-2: Edge Case -- Hard Calendar Conflict
- **prompt:** "I have a customer demo at 2pm and my manager just scheduled a 1-on-1 at 2pm too. Both are important. What do I do?"
- **context:** Two overlapping meetings at the same time. Tests conflict resolution algorithm and priority comparison.
- **assertions:**
  - Conflict is identified as a hard conflict (two events at the same time)
  - Priority levels are compared (customer demo = P0/P1, manager 1-on-1 = P0/P1)
  - The conflict resolution algorithm is applied (check priority, then older event, then attendee count)
  - 2-3 alternative time slots are proposed for the lower-priority or more flexible meeting
  - Response asks for explicit approval before moving either event (especially P0/P1 events)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Edge Case -- Timezone Scheduling
- **prompt:** "I need to schedule a call with someone in Tokyo. I'm in San Francisco. What times work for both of us?"
- **context:** Cross-timezone scheduling. Tests timezone handling rules and international scheduling best practices.
- **assertions:**
  - Both timezones are displayed for proposed times (e.g., "5pm PST / 10am JST next day")
  - IANA timezone names or standard abbreviations are used (not bare UTC offsets)
  - Proposed times avoid early morning (before 9am) and late evening (after 7pm) for both parties
  - The 16-17 hour difference between PST and JST is correctly calculated
  - Realistic overlap windows are identified (typically early morning SF / evening Tokyo or vice versa)
- **passing_grade:** 4/5 assertions must pass

## TC-4: Quality Check -- Over-Scheduling Prevention
- **prompt:** "I already have meetings at 9am, 10am, 11am, 1pm, 2pm, and 3pm tomorrow. Can you fit in one more at 4pm?"
- **context:** User is already over-scheduled with 6 hours of meetings. Tests the over-scheduling pitfall detection.
- **assertions:**
  - Response flags that 6+ hours of meetings exceeds the 50% rule (max 4 hours of meetings per 8-hour day)
  - Notes that the user has no focus time blocks remaining
  - If adding the 4pm meeting, warns about back-to-back fatigue and suggests buffer time
  - Recommends declining or rescheduling lower-priority meetings to free up focus time
  - Does not blindly add the meeting without raising the over-scheduling concern
- **passing_grade:** 4/5 assertions must pass

## TC-5: Happy Path -- Recurring Event Setup
- **prompt:** "Set up a biweekly 1-on-1 with my direct report starting next Thursday at 3pm."
- **context:** Standard recurring event creation. Tests recurring event best practices and checklist.
- **assertions:**
  - Recurrence pattern is correctly set to biweekly (every 2 weeks)
  - Response checks for conflicts across the next 4 weeks (not just the first instance)
  - An end date or review date is recommended (not an infinite series)
  - Standard meeting length for 1-on-1 is applied (30 min as default, or confirms with user)
  - Buffer time before/after is considered
  - Skip/reschedule rules are mentioned (e.g., what to do on holidays)
- **passing_grade:** 4/6 assertions must pass
