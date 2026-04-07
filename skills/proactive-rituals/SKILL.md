---
name: proactive-rituals
description: Use when setting up recurring automated tasks, daily briefings, status checks, or any scheduled agent work -- covers morning briefings, end-of-day summaries, weekly reviews, custom rituals, and event-driven triggers using Claude's native cron scheduling
---

# Proactive Rituals

Design and configure recurring automated tasks that run on a schedule, gather information from multiple sources, synthesize it, and deliver formatted results. This covers daily briefings, end-of-day summaries, weekly reviews, custom rituals, and event-driven triggers.

## Built-in Ritual Patterns

Three foundational rituals that cover the daily and weekly cadence. Use these as templates for custom rituals.

### 1. Morning Briefing

**Schedule**: Weekdays, ~7:30 AM (cron: `30 7 * * 1-5`)

**What to check**:
- Today's calendar events -- flag scheduling conflicts
- Weather forecast and commute conditions (if first event has a location, estimate travel time)
- Priority tasks from the task list -- what's due today, what's overdue
- Unread communications -- email triage (unread counts, urgent items), unread messages
- Upcoming deadlines within the next 3 days
- Anomalies -- anything unusual that needs attention (failed builds, security alerts, unusual spending)

**Data gathering pattern**: Query each domain in parallel, then synthesize:
- Operations: calendar, tasks, reminders
- Communications: email, messages, notifications
- Home: weather, commute, smart home status
- Health: yesterday's activity summary, medication reminders
- Finance: overnight transactions, budget alerts

**Output channels** (same content, different format per channel):

| Channel | Format | Length |
|---------|--------|--------|
| Push notification | Single paragraph, key highlights only | Max 300 characters |
| Voice/TTS | Natural spoken summary, no visual formatting, short sentences | Max 1000 characters |
| Full report | Markdown with headers per domain, bullet points, detail | Unlimited |

**Tone**: Brisk, informative, action-oriented. Lead with the most important item. End with "Here's what needs your attention today."

### 2. End-of-Day Summary

**Schedule**: Daily, ~9:00 PM (cron: `0 21 * * *`)

**What to review**:
- Tasks completed today -- list with completion timestamps
- Unfinished items to carry forward to tomorrow
- Tomorrow's schedule preview (first 3 events)
- Spending summary for today (if financial tracking is enabled)
- Health/wellness check-in -- steps, water, exercise logged today
- Unresponded emails older than 8 hours -- these need attention

**Tone**: Reflective, brief, focused on accomplishments. End with tomorrow's top priorities and a positive note.

**Output channels**:

| Channel | Format | Length |
|---------|--------|--------|
| Push notification | Accomplishment count + tomorrow's top priority | Max 300 characters |
| Voice/TTS | Conversational recap, end with tomorrow's first event | Max 1000 characters |
| Full report | Markdown with completed/pending/tomorrow sections | Unlimited |

### 3. Weekly Review

**Schedule**: Sunday, ~10:00 AM (cron: `0 10 * * 0`)

**What to cover**:
- Week's accomplishments -- tasks completed, milestones hit
- Goal progress -- active goals, stalled items, percentage toward targets
- Financial summary -- spending by category, comparison to previous week, trends
- Health trends -- exercise frequency, activity patterns over the week
- Productivity patterns -- most active days, task completion rate
- Top 3 suggestions for next week based on observed patterns
- Upcoming week preview -- major events, deadlines, appointments

**Tone**: Analytical, longer format. Include trends and recommendations, not just raw data. Use comparisons ("up 15% from last week") to give numbers context.

**Output channels**:

| Channel | Format | Length |
|---------|--------|--------|
| Push notification | 3-line summary: wins, concerns, focus | Max 300 characters |
| Full report | Detailed markdown with data tables, trend arrows, recommendations | Unlimited |

## Custom Ritual Design

### Ritual Definition Structure

Every ritual, built-in or custom, follows this template:

```yaml
ritual_id: "daily_standup_prep"        # Unique identifier
name: "Daily Standup Prep"             # Human-readable name
schedule: "0 9 * * 1-5"               # Cron expression
domains:                                # What areas to query
  - "git_activity"
  - "task_board"
  - "calendar"
instruction_template: |                 # What to gather and how
  Prepare standup notes:
  - What I completed yesterday (from git commits and task completions)
  - What I'm working on today (from task board, calendar)
  - Any blockers (overdue items, failed builds, dependency waits)
output_channels:                        # Where to deliver
  - "push_notification"
  - "full_report"
enabled: true
```

### Cron Expression Reference

| Expression | Meaning |
|------------|---------|
| `30 7 * * 1-5` | 7:30 AM, Monday through Friday |
| `0 21 * * *` | 9:00 PM, every day |
| `0 10 * * 0` | 10:00 AM, Sundays only |
| `*/30 * * * *` | Every 30 minutes |
| `0 9 1 * *` | 9:00 AM on the 1st of each month |
| `0 */4 * * *` | Every 4 hours |

Format: `minute hour day_of_month month day_of_week`

### Ritual Execution Flow

Every ritual follows this pipeline:

```
TRIGGER (cron fires or manual invoke)
    |
    v
GATHER (query each domain in parallel)
    |-- Domain A: calendar, tasks
    |-- Domain B: email, messages
    |-- Domain C: finance, health
    |
    v
SYNTHESIZE (merge results into coherent narrative)
    |-- Handle missing data gracefully ("Finance data unavailable")
    |-- Prioritize: lead with actionable items
    |
    v
FORMAT (one synthesis, multiple outputs)
    |-- Push: compress to 300 chars
    |-- TTS: strip formatting, natural speech
    |-- Full: structured markdown report
    |
    v
DELIVER (route to each output channel)
```

### Multi-Channel Output Rules

The same ritual produces different formats per channel. Rules for compression:

**Push notification** (max 300 chars):
- Take the first sentence of each domain's output (max 80 chars each)
- Prefix with ritual name
- If over 300 chars, truncate with "..."
- Pattern: `{Ritual Name}:\n- {domain}: {first_line}\n- {domain}: {first_line}`

**TTS/Voice** (max 1000 chars):
- Open with "Here's your {ritual name}."
- Take first 2 sentences from each domain
- Remove all markdown, formatting, special characters
- Use natural spoken transitions between domains
- Pattern: natural paragraph, no bullet structures

**Full report** (unlimited):
- Bold title with execution timestamp
- H3 header per domain
- Full detail from each domain query
- Conclude with recommendations or next actions

## Proactive Engine Patterns

### Priority Queue

When multiple things compete for attention, process them in this order:

| Priority | Source | Example |
|----------|--------|---------|
| **0 - USER** | Direct user request | "What's on my calendar?" |
| **1 - EVENT** | External trigger | Email arrived, calendar conflict detected, build failed |
| **2 - TICK** | Background check found something | Reminder coming due, sensor anomaly |
| **3 - RITUAL** | Scheduled ritual output | Morning briefing, weekly review |

User messages always preempt everything else. Rituals are lowest priority -- they can wait.

### Sensitivity Levels

Control how aggressively the system checks for actionable items:

| Level | What Gets Checked | When to Use |
|-------|-------------------|-------------|
| **Aggressive** | Everything: notifications, reminders, calendar, messages, sensor data, build status | Active work sessions, deadline crunch |
| **Normal** | Important only: notifications, reminders, calendar events | Default daily operation |
| **Quiet** | Critical only: urgent notifications, overdue reminders | Focus time, meetings, sleep hours |

### Tick Suppression

Pause proactive checks during these conditions:
- User is actively working (detected by recent input activity)
- System is explicitly paused (user toggled pause)
- Current time is outside active hours (e.g., 11 PM - 6 AM)

Resume automatically when the suppression condition clears.

## Event-Driven Triggers

Not everything runs on a schedule. Some rituals fire in response to external events.

### Trigger Pattern

```
EVENT (webhook, file change, API callback)
    |
    v
MATCH (does this event match a registered trigger?)
    |-- Source: "github", "email", "calendar", "build_system"
    |-- Event type: "pull_request.opened", "invoice.received"
    |
    v
VERIFY (is this event authentic?)
    |-- HMAC signature verification
    |-- Source IP allowlist (optional)
    |
    v
ACTION (route to appropriate handler)
    |-- "Auto-review this PR"
    |-- "Categorize this invoice"
    |-- "Check for calendar conflicts"
```

### Common Event Triggers

| Source | Event | Suggested Action |
|--------|-------|------------------|
| GitHub | PR opened | Auto-review, check CI status |
| GitHub | Workflow failed | Create issue, notify with failure details |
| GitHub | Issue assigned to you | Add to task list, check deadline |
| Email | Invoice received | Route to finance, auto-categorize |
| Email | Meeting invite | Check calendar conflicts, suggest response |
| Calendar | Event in 15 minutes | Push notification with location/join link |
| Build system | Deploy completed | Run smoke tests, notify team |
| File system | Config file changed | Validate syntax, diff against previous |

### Webhook Security (HMAC Verification)

For any external webhook, verify authenticity before processing:

| Source | Signature Header | How to Verify |
|--------|-----------------|---------------|
| GitHub | `X-Hub-Signature-256` | HMAC-SHA256 of body with webhook secret |
| Slack | `X-Slack-Signature` | HMAC-SHA256 of `v0:timestamp:body` |
| Generic | `X-Webhook-Signature` | HMAC-SHA256 of body with source-specific secret |

**Verification pattern**:
1. Extract signature from header
2. Compute HMAC-SHA256 of the raw request body using the shared secret
3. Compare using constant-time comparison (prevents timing attacks)
4. Reject if signature doesn't match -- log the attempt but don't process

Store secrets in environment variables, never in code: `WEBHOOK_SECRET_GITHUB`, `WEBHOOK_SECRET_SLACK`, etc.

## Setting Up with Claude Code Scheduling

### Using `/schedule` for Recurring Rituals

Map ritual definitions to Claude's native scheduling:

```
/schedule "Morning Briefing" --cron "30 7 * * 1-5" --prompt "Run the morning briefing ritual: check calendar, tasks, email, weather. Format as push notification (300 chars max) and full markdown report."
```

### Defining a Custom Ritual via Scheduling

1. Write the ritual instruction as a clear, self-contained prompt
2. Specify the cron schedule
3. Define the output format in the prompt itself
4. Set up the delivery channel (file output, notification, etc.)

```
/schedule "Weekly Code Review" --cron "0 14 * * 5" --prompt "Review all PRs merged this week. For each: summarize changes, note any patterns (repeated refactors, growing tech debt, test coverage changes). Output as markdown with a summary section and per-PR detail."
```

### Event-Driven Agents via Webhooks

For event-triggered rituals, set up webhook receivers:

1. Register a webhook endpoint with the event source (GitHub, Slack, etc.)
2. Configure the webhook secret for HMAC verification
3. Define the handler: what to do when the event fires
4. Route the event through the priority queue

### Agent Self-Scheduling

Agents can schedule their own follow-ups:

- **Duration**: 1 second to 24 hours maximum
- **Concurrency limit**: Max 5 concurrent scheduled wake-ups per agent (prevents infinite loops)
- **Use cases**: "Check back on this deploy in 10 minutes", "Remind me about this PR tomorrow morning"
- **Cancellation**: Scheduled wake-ups can be cancelled by ID before they fire

## Designing Your Own Ritual

### Step-by-step

1. **Name it**: What is this ritual? ("Weekly Client Update", "Deploy Readiness Check")
2. **Schedule it**: When should it run? (cron expression)
3. **Define domains**: What data sources does it need? (calendar, git, email, tasks, metrics)
4. **Write the instruction**: What should the agent gather and how should it synthesize?
5. **Choose output channels**: Where does the result go? (push, voice, full report, Slack channel)
6. **Set enabled/disabled**: Start enabled, disable during vacations or off-periods

### Ritual Hygiene

- **Keep instructions specific**: "Check email for unread messages" not "check communications"
- **Handle missing data**: Always include fallback text when a data source is unavailable
- **Cap output length per channel**: Push notifications over 300 chars get truncated badly
- **Test with manual trigger first**: Run the ritual once manually before scheduling
- **Review execution history**: Check that rituals are actually running and producing useful output
- **Disable during downtime**: Turn off rituals during vacations, system maintenance, or focus periods
