---
name: time-perception
description: Give Claude a sense of time -- tracks elapsed time between messages, task durations, project switching, and activity patterns. Hooks inject temporal context into every prompt automatically. Includes a portable Python module for wrapping any LLM call with time awareness.
allowed-tools: Read Bash
---

# Time Perception

A time-awareness system that gives Claude (or any LLM) a persistent sense of time across conversations. Hooks inject a compact timestamp into every prompt, and log files accumulate history for pattern analysis.

## What It Does

Every time a user sends a message, a `UserPromptSubmit` hook runs a shell script that:

1. Reads the previous timestamp from a state file
2. Calculates elapsed time since the last message
3. Increments a global message counter
4. Detects project switches (if the user moved between repos)
5. Logs to both global and per-project JSONL files
6. Outputs a compact context string that gets injected into the conversation

A `Stop` hook runs when Claude finishes responding, logging how long the task took.

## Context Format

The injected string looks like:

```
[T:2026-04-19 01:14|+29m 14s|#725]
```

Fields:
- `T:` -- current local datetime
- `+` -- elapsed time since previous message
- `#` -- cumulative message number across all sessions

On project switch, an extra field appears:

```
[T:2026-04-19 01:14|+5m 2s|#725|Jarvis<-General Claude]
```

## How to Use the Time Context

When you see the time context injected into a conversation:

### Acknowledge gaps
If the elapsed time is > 1 hour, briefly acknowledge the return:
- "Welcome back -- it's been about 3 hours since we last talked."
- Don't be dramatic about short gaps (< 5 minutes).

### Track task duration
The `Stop` hook logs how long each response took. Use this data when the user asks about productivity:
- "Your average task takes about 45 seconds in this project."
- "That last response took 2m 12s -- longer than usual."

### Notice patterns
The JSONL logs accumulate over days/weeks. When the user asks about their habits:
- "You typically work on Jarvis late at night, between 10 PM and 2 AM."
- "You switched projects 4 times today."

### Project switching
When `switched_from_project` appears, you know the user just came from another repo. This is useful context:
- "Coming from the hackathon project -- want to continue where we left off here?"

## Data Files

All stored under `~/.claude/` (or a custom `data_dir`):

| File | Purpose |
|------|---------|
| `time-data.json` | Current state (last timestamp, message count, last project) |
| `time-log.jsonl` | Global message history (timestamp, elapsed, project, agent) |
| `task-durations.jsonl` | Global task duration log (how long each response took) |
| `project-time/<project>.jsonl` | Per-project message log with prompt previews |
| `project-time/<project>.durations.jsonl` | Per-project task duration log |

### JSONL Schema (time-log)

```json
{
  "timestamp": "2026-04-19T01:14:00Z",
  "local": "2026-04-19 01:14:00 MST",
  "epoch": 1776489240,
  "elapsed_seconds": 1754,
  "message_number": 725,
  "project": "C:/Users/user/projects/my-app"
}
```

### JSONL Schema (task-durations)

```json
{
  "completed": "2026-04-19 01:15:23 MST",
  "duration_seconds": 83,
  "duration_human": "1m 23s",
  "project": "my-app"
}
```

## Installation

### 1. Hook Configuration

Add these to your `settings.json` (user-level or project-level):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/scripts/time-tracker.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/scripts/task-timer.sh"
          }
        ]
      }
    ]
  }
}
```

### 2. Shell Scripts

Copy `time-tracker.sh` and `task-timer.sh` from this skill's `scripts/` directory to `~/.claude/scripts/`.

### 3. Python Module (Optional)

Copy `time_context.py` to `~/.claude/scripts/` for use in custom scripts, agents, or LLM wrappers.

## Python Module API

`time_context.py` is a standalone module with no dependencies beyond the standard library. It can be imported by any Python script, LLM wrapper, or subagent.

```python
from time_context import TimeContext

tc = TimeContext(project="my-app", agent_name="gpt-4")

# Get time context string to inject into any prompt
context = tc.stamp("prompt preview text")
# -> "[T:2026-04-19 01:14|+5m 2s|#42]"

# Mark task complete (logs duration)
duration = tc.done("task label")
# -> "1m 23s"

# Wrap any LLM call with automatic time tracking
response = tc.wrap(my_llm_function, "fix the bug in auth.py")

# Inject into OpenAI-style messages list
messages = tc.inject([{"role": "user", "content": "hello"}])
# -> [{"role": "system", "content": "[T:...]"}, {"role": "user", "content": "hello"}]

# Get project summary for analysis
summary = tc.summary()
# -> {"project": "my-app", "total_messages": 42, "avg_task_duration": "45s", ...}

# Read raw history
history = tc.get_history(project_only=True)
durations = tc.get_durations(project_only=True)
```

### Constructor

```python
TimeContext(
    project: str = None,       # Project name (auto-detected from cwd if None)
    data_dir: str = None,      # Storage directory (default: ~/.claude/)
    agent_name: str = None,    # Agent identifier for multi-agent tracking
)
```

### Methods

| Method | Returns | Purpose |
|--------|---------|---------|
| `stamp(prompt_preview)` | `str` | Record timestamp, return context string |
| `done(task_label)` | `str \| None` | Log task duration, return human-readable time |
| `wrap(llm_call, prompt)` | `Any` | Wrap an LLM call with automatic time tracking |
| `inject(messages)` | `list[dict]` | Prepend time context as system message |
| `get_history(project_only)` | `list[dict]` | Read message history from logs |
| `get_durations(project_only)` | `list[dict]` | Read task duration history |
| `summary()` | `dict` | Generate project time summary |

## CLAUDE.md Integration

Add this to your global `~/.claude/CLAUDE.md`:

```markdown
## Time Awareness
A `UserPromptSubmit` hook injects time context into every conversation. Always acknowledge and use this temporal data:
- Note how long it's been since the user's last message
- When time gaps are large (>1 hour), briefly acknowledge the return
- Data files for analysis:
  - `~/.claude/task-durations.jsonl` -- global task duration log
  - `~/.claude/time-log.jsonl` -- global message timestamp history
  - `~/.claude/project-time/<project>.jsonl` -- per-project message log
  - `~/.claude/project-time/<project>.durations.jsonl` -- per-project task duration log
```

## Design Decisions

- **Shell scripts over Python hooks**: Hooks need to be fast (< 100ms). Bash with grep/sed avoids Python startup overhead.
- **JSONL over SQLite**: Append-only logs are simpler, greppable, and survive corruption better. No locking needed.
- **Compact context format**: The `[T:...|+...|#...]` format is ~40 bytes. Full XML would waste tokens.
- **State file is JSON**: Single file read/write for last-timestamp state. Overwritten each message.
- **Python module mirrors shell scripts**: Same data format, same file paths, but usable programmatically for wrapping arbitrary LLM APIs.
- **No external dependencies**: Both the shell scripts and Python module use only standard library / built-in tools.
