---
name: scheduling
description: Use when helping with time management, calendar organization, or routine design — covers time blocking, ritual scheduling, priority-based allocation, and calendar optimization
---

# Calendar Scheduling & Time Management

## When to Use
When helping with calendar management, meeting scheduling, time blocking, routine design, conflict resolution, timezone handling, or optimizing how someone spends their time.

## Core Concepts

### Calendar Conflict Types
- **Hard Conflict**: Two meetings overlap in time (same person cannot attend both)
- **Soft Conflict**: Back-to-back meetings with no travel/break time
- **Resource Conflict**: Meeting room or shared resource double-booked
- **Preference Conflict**: Meeting violates working hours or focus time blocks

### Time Block Categories
- **Focus Time**: 90-120 min blocks for deep work (protect aggressively)
- **Meeting Time**: 9am-5pm (or user's working hours), exclude lunch
- **Buffer Time**: 5-15 min between meetings (scale with meeting length)
- **Commute Time**: Travel buffer for location changes
- **Prep Time**: Pre-meeting review (5-10 min before important meetings)

### Priority Levels
1. **P0 (Critical)**: One-on-ones with manager, customer meetings, deadlines
2. **P1 (High)**: Team meetings, project check-ins, interviews
3. **P2 (Medium)**: Standups, recurring syncs, optional attendee meetings
4. **P3 (Low)**: Social events, optional trainings, informational sessions

### Timezone Handling Rules
- Always store in UTC internally, display in user's local timezone
- When scheduling across timezones, show both times: "10am PST (1pm EST)"
- Avoid 7-9am or 5-7pm slots for international calls (likely early/late for someone)
- Use IANA timezone names (`America/Los_Angeles`), not bare offsets (`UTC-8`)
- Daylight Saving Time: Re-calculate recurring events during DST transitions

## Patterns & Procedures

### Conflict Resolution Algorithm
```
1. Detect conflict type (hard vs soft vs resource)
2. Check priority levels (P0 > P1 > P2 > P3)
3. If equal priority:
   - Prefer keeping older event (first to schedule wins)
   - Unless newer event has more attendees (bigger impact)
4. Propose alternative slots:
   - Same day, different time
   - Next available day with similar time
   - Batch with related meetings
5. If moving P0/P1 events, require explicit approval
```

### Optimal Meeting Placement
```
Best times by meeting type:
- Deep focus work: 9-11am (peak cognitive hours)
- One-on-ones: 2-4pm (post-lunch, before end-of-day fatigue)
- Standups: 10am or 2pm (after email check, not first thing)
- Creative brainstorms: 10am-12pm (high energy, collaborative mood)
- Status updates: 4-5pm (summary/wrap-up time)

Avoid:
- 12-1pm (lunch)
- 8-9am on Mondays (email catchup)
- 4-5pm on Fridays (focus drops)
```

### Buffer Time Calculation
```
Meeting length -> Buffer needed:
- 15-30 min meeting -> 5 min buffer
- 30-60 min meeting -> 10 min buffer
- 60+ min meeting -> 15 min buffer
- Different locations -> Add travel time (10-30 min)
- Important meetings -> Add 5-10 min prep time before
```

### Recurring Event Patterns
```
Daily: Standups (15 min, 10am)
Weekly: Team sync (60 min, Tuesdays 2pm)
Biweekly: One-on-ones (30 min, alternating Thursdays)
Monthly: All-hands (90 min, first Friday 11am)
Quarterly: Planning sessions (4 hours, full morning block)

Rules:
- Recurring events have lower priority than one-off critical meetings
- Can skip/move individual instances without breaking series
- Always check for conflicts 2 weeks ahead when creating recurring events
```

### Meeting Batch Optimization
```
If scheduling multiple meetings in one day:
1. Group by location (minimize travel)
2. Batch related topics (context switching cost)
3. Alternate high-energy (presentations) with low-energy (status updates)
4. Never schedule more than 4 hours of meetings in one day
5. Ensure at least one 90-min focus block remains
```

## Common Pitfalls

### Timezone Mistakes
- **Wrong**: "Let's meet at 3pm" (whose timezone?)
- **Right**: "3pm PST (6pm EST)" or "3pm your local time"
- **Trap**: Forgetting DST transitions (recurring events shift by 1 hour twice a year)
- **Fix**: Always use IANA timezone names (`America/Los_Angeles`), not offsets (`UTC-8`)

### Over-Scheduling
- **Symptom**: Back-to-back meetings all day, no focus time
- **Cause**: Accepting all meeting requests without calendar review
- **Fix**: Block 2-4 hours per day as "Focus Time" (decline conflicts)
- **Rule**: Max 50% of workday in meetings (4 hours out of 8)

### Buffer Neglect
- **Problem**: Scheduling meetings back-to-back across buildings
- **Reality**: Takes 5-10 min to wrap up, 5-10 min to walk, 5 min to settle in
- **Solution**: Automatic 15-min buffer between meetings at different locations

### Priority Confusion
- **Mistake**: Treating all meetings equally
- **Impact**: Moving critical customer call to fit in team standup
- **Fix**: Always tag meetings with P0-P3, never move P0 without explicit ask

### Recurring Event Bloat
- **Issue**: 10 weekly recurring meetings from 2 years ago still on calendar
- **Audit**: Quarterly review of all recurring events (decline/cancel unused ones)
- **Guideline**: If you've skipped 3+ instances, delete the series

## Quick Reference

### Timezone Abbreviations
```
PST/PDT: Pacific (UTC-8/-7)
MST/MDT: Mountain (UTC-7/-6)
CST/CDT: Central (UTC-6/-5)
EST/EDT: Eastern (UTC-5/-4)
GMT/BST: London (UTC+0/+1)
CET/CEST: Central Europe (UTC+1/+2)
IST: India (UTC+5:30)
JST: Japan (UTC+9)
```

### Standard Meeting Lengths
```
15 min: Quick sync, standup
30 min: One-on-one, focused discussion
60 min: Team meeting, workshop
90 min: Deep dive, training
2-4 hours: Planning, offsite
```

### Conflict Resolution Phrases
```
"I see a conflict with [existing meeting]. Would you prefer to:
 a) Move [new meeting] to [alternate time]
 b) Reschedule [existing meeting] to [alternate time]
 c) Decline [lower priority meeting]"

"This creates back-to-back meetings from 10am-1pm. I recommend:
 - Adding a 15-min buffer at 12:00pm
 - Moving [meeting] to 2pm for breathing room"
```

## Checklists

### Before Scheduling a Meeting
- [ ] Check all attendees' availability (not just organizer)
- [ ] Verify timezone (convert if attendees in different zones)
- [ ] Calculate required buffer time
- [ ] Confirm meeting room/resource availability
- [ ] Ensure at least one focus block remains that day
- [ ] Check priority level (can it bump existing meetings?)

### When Detecting Conflicts
- [ ] Identify conflict type (hard/soft/resource/preference)
- [ ] Compare priority levels
- [ ] Propose 2-3 alternative times
- [ ] Calculate buffer/travel time if suggesting new slots
- [ ] Get explicit approval before moving P0/P1 events

### For Recurring Events
- [ ] Check conflicts for next 4 weeks (not just first instance)
- [ ] Set appropriate recurrence pattern (daily/weekly/biweekly/monthly)
- [ ] Document skip/reschedule rules (e.g., "skip on holidays")
- [ ] Set end date or review date (don't create infinite series)
- [ ] Send recurring event summary to attendees

### Weekly Calendar Maintenance
- [ ] Audit upcoming week on Friday afternoon
- [ ] Ensure max 50% meeting time (4 hrs/day)
- [ ] Confirm at least one 90-min focus block per day
- [ ] Review and decline low-priority conflicts
- [ ] Block focus time for next week
- [ ] Check for timezone issues (DST transitions, international calls)
