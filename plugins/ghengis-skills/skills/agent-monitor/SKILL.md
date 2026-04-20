---
name: agent-monitor
description: Real-time subagent monitoring dashboard and status line -- tracks agent spawning, completion, permissions, and history via hooks. Auto-opens a browser dashboard when agents are active. Includes a terminal status line showing model name and context window usage.
allowed-tools: Read Bash
---

# Agent Monitor & Status Line

Two tools for Claude Code power users: a real-time agent monitoring dashboard and a terminal status line.

## Agent Monitor Dashboard

When you spawn subagents (via the Task/Agent tool), hooks automatically:

1. Register each agent with an in-memory state store
2. Launch a local web dashboard (ports 7685/7686) when 2+ agents are running
3. Show real-time status, project grouping, and agent history
4. Auto-shutdown 10 seconds after all agents finish
5. Persist history across sessions in `~/.claude/agent-history.json`

### What the Dashboard Shows

- **Live Monitor** -- real-time agent status (running, completed, failed)
- **Agent Timeline** -- visual timeline of agent execution
- **Project View** -- agents grouped by project/workspace
- **Stats** -- completion rates, average durations, agent counts
- **History** -- searchable history across all sessions
- **Permissions** -- permission request tracking

### Architecture

```
PreToolUse (Task matcher)
    └── on_task_start.py
        ├── Register agent in state
        ├── Launch dashboard server (if 2+ agents)
        └── Open browser tab (reuse existing)

SubagentStop
    └── on_task_stop.py
        ├── Update agent status (completed/failed)
        └── Auto-shutdown dashboard (after 10s idle)

Dashboard Server (agent_web_dashboard.py)
    ├── HTTP API on :7685 (REST endpoints for agent state)
    ├── WebSocket on :7686 (real-time updates)
    ├── Serves React frontend (dashboard-react/dist/)
    └── Fallback to vanilla HTML if React not built
```

### Hook Scripts

| Script | Purpose |
|--------|---------|
| `on_task_start.py` | Registers agent, launches dashboard |
| `on_task_stop.py` | Updates status, triggers shutdown |
| `agent_web_dashboard.py` | HTTP/WS server for the dashboard |
| `agent_state.py` | In-memory + on-disk agent state |
| `agent_history.py` | Persistent cross-session history |
| `agent_permissions.py` | Permission handling utilities |
| `browser_utils.py` | Cross-platform browser launch |
| `on_project_detect.py` | Project context detection |

### Data Files

| File | Purpose |
|------|---------|
| `~/.claude/agent-history.json` | Persistent agent history across sessions |
| `~/.claude/agent-state.json` | Current session agent state |

## Status Line

A Python script that reads Claude Code's status JSON from stdin and displays:

```
Claude Opus 4.6 ████████░░ 78%
/.../my-project
```

- **Model name** in orange
- **Context usage bar** -- green (<50%), yellow (50-80%), red (>80%)
- **Abbreviated working directory** in cyan

### Calibrated Accuracy

The status line applies a linear correction to Claude Code's reported context percentage, calibrated from observed data points. This gives a more accurate reading of actual context pressure.

## Installation

### Auto-install (via plugin)

When installed as a ghengis-skills plugin, the hooks are automatically wired. The dashboard server starts silently when agents spawn and prints the URL (`http://localhost:7685`) to stderr.

### Browser Auto-Open (Opt-In)

By default, the dashboard does **not** open a browser tab � it just starts the server and logs the URL. If you want the old behavior where a browser tab opens every time agents spawn, set this environment variable:

```bash
export GHENGIS_AGENT_MONITOR_AUTO_OPEN=true
```

Accepted truthy values: `true`, `1`, `yes` (case-insensitive). Any other value or unset = silent mode.

For the status line, add this to your `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python ~/.claude/statusline-bar.py"
  }
}
```

Copy `statusline-bar.py` from this skill's `scripts/` directory to `~/.claude/`.

### Manual install

1. Copy all `.py` files from `scripts/hooks/` to `~/.claude/hooks/`
2. Copy `dashboard-react/` and `dashboard-vanilla/` to `~/.claude/hooks/`
3. Copy `statusline-bar.py` to `~/.claude/`
4. Add hooks to `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Task",
      "hooks": [{
        "type": "command",
        "command": "python ~/.claude/hooks/on_task_start.py"
      }]
    }],
    "SubagentStop": [{
      "hooks": [{
        "type": "command",
        "command": "python ~/.claude/hooks/on_task_stop.py"
      }]
    }]
  }
}
```

## Troubleshooting

- **Dashboard doesn't open**: Check ports 7685/7686 are available
- **Status line missing**: Verify Python is in PATH and the path in `settings.json` is correct
- **Windows paths**: Use forward slashes in all `settings.json` paths
- **Import errors**: Requires Python 3.8+
- **React dashboard blank**: The `dist/` folder is pre-built. If missing, run `npm install && npm run build` in `dashboard-react/`
