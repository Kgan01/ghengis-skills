# Proactive Rituals -- Evaluation

## TC-1: Happy Path -- Morning Briefing Structure
- **prompt:** "Run my morning briefing. It's a Monday at 7:30 AM. I have 3 calendar events, 12 unread emails (2 marked urgent), a dentist appointment tomorrow, and it's raining outside."
- **context:** Tests the morning briefing built-in ritual: domain coverage, multi-channel output, parallel data gathering, and tone requirements.
- **assertions:**
  - Covers all required domains: calendar events (flag conflicts), weather/commute, priority tasks, unread communications (urgent items highlighted), upcoming deadlines within 3 days
  - Produces output in at least two channel formats: push notification (max 300 chars) and full markdown report
  - Push notification compresses to under 300 characters with key highlights only
  - Full report uses markdown headers per domain with bullet points and detail
  - Tone is brisk and action-oriented, leading with the most important item and ending with "Here's what needs your attention today" or equivalent
- **passing_grade:** 4/5 assertions must pass

## TC-2: Happy Path -- Custom Ritual Design
- **prompt:** "Create a custom ritual called 'Weekly Client Update' that runs every Friday at 2 PM. It should check git activity, the task board, and CRM data, then produce a summary of client-facing progress for each active project."
- **context:** Tests custom ritual definition using the documented YAML structure: ritual_id, name, schedule, domains, instruction_template, output_channels, and enabled flag.
- **assertions:**
  - Produces a ritual definition with ritual_id, name, and schedule as a valid cron expression (`0 14 * * 5` for Friday 2 PM)
  - Lists domains to query: git_activity, task_board, CRM/client data
  - Includes an instruction_template that specifies what to gather and how to synthesize
  - Defines output_channels (at minimum push_notification and full_report)
  - Sets enabled: true and the ritual is self-contained enough to execute without additional context
- **passing_grade:** 4/5 assertions must pass

## TC-3: Quality Check -- Cron Scheduling Accuracy
- **prompt:** "Set up these schedules: morning briefing on weekdays at 7:30 AM, end-of-day summary every day at 9 PM, weekly review on Sunday at 10 AM, a deploy check every 30 minutes during business hours, and a monthly invoice reminder on the 1st at 9 AM."
- **context:** Tests cron expression accuracy against the reference table and proper mapping of human-readable schedules to cron syntax.
- **assertions:**
  - Morning briefing: `30 7 * * 1-5` (7:30 AM, Monday-Friday)
  - End-of-day summary: `0 21 * * *` (9:00 PM, every day)
  - Weekly review: `0 10 * * 0` (10:00 AM, Sundays)
  - Every 30 minutes: `*/30 * * * *` (correctly uses step syntax)
  - Monthly on 1st at 9 AM: `0 9 1 * *` (first day of month)
- **passing_grade:** 4/5 assertions must pass

## TC-4: Edge Case -- Priority Queue Ordering
- **prompt:** "It's 7:30 AM and my morning briefing ritual fires. At the same time, I get a GitHub webhook that a CI build failed, and I also type 'What's on my calendar today?' Which should be processed first?"
- **context:** Tests the priority queue system: USER (0) > EVENT (1) > TICK (2) > RITUAL (3). Three simultaneous items at different priority levels.
- **assertions:**
  - Identifies the user message ("What's on my calendar today?") as Priority 0 (USER) and processes it first
  - Identifies the GitHub build failure webhook as Priority 1 (EVENT) and processes it second
  - Identifies the morning briefing as Priority 3 (RITUAL) and processes it last
  - Explains that user messages always preempt everything else
  - Notes that rituals are lowest priority and can wait until higher-priority items are handled
- **passing_grade:** 4/5 assertions must pass

## TC-5: Edge Case -- Multi-Channel Output Compression
- **prompt:** "My end-of-day summary has this data: completed 5 tasks, 2 carry-forward items, 3 events tomorrow (9 AM standup, 11 AM client call, 2 PM design review), spent $47 on lunch and $12 on parking, walked 8,200 steps, and have 3 unresponded emails older than 8 hours. Format for push notification, TTS, and full report."
- **context:** Tests multi-channel formatting rules: push notification max 300 chars, TTS max 1000 chars with no formatting, full report unlimited with markdown structure.
- **assertions:**
  - Push notification is under 300 characters and includes accomplishment count plus tomorrow's top priority
  - TTS output opens with "Here's your end-of-day summary" (or equivalent), strips all markdown formatting, uses natural spoken transitions
  - TTS output does not exceed 1000 characters
  - Full report uses bold title with timestamp, H3 headers per domain (completed, pending, tomorrow, spending, health), and concludes with recommendations
  - All three channels convey the same core data without adding or omitting substantive facts
- **passing_grade:** 4/5 assertions must pass
