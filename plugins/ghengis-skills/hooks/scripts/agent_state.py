#!/usr/bin/env python3
"""
Shared state management for agent monitoring.
State is stored in /tmp/claude-agent-monitor/state.json
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Cross-platform file locking
if sys.platform == "win32":
    import msvcrt

    def _lock_file(f, exclusive=True):
        """Lock file on Windows."""
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK if exclusive else msvcrt.LK_NBRLCK, 1)
        except IOError:
            pass  # Already locked, continue anyway for reads

    def _unlock_file(f):
        """Unlock file on Windows."""
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except IOError:
            pass
else:
    import fcntl

    def _lock_file(f, exclusive=True):
        """Lock file on Unix."""
        fcntl.flock(f.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)

    def _unlock_file(f):
        """Unlock file on Unix."""
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
from datetime import datetime
from typing import Dict, List, Optional

TEMP_BASE = Path(tempfile.gettempdir())
STATE_DIR = TEMP_BASE / "claude-agent-monitor"
STATE_FILE = STATE_DIR / "state.json"
DASHBOARD_PID_FILE = STATE_DIR / "dashboard.pid"

def ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)

def load_state() -> Dict:
    """Load the current state, with file locking for safety."""
    ensure_state_dir()
    try:
        with open(STATE_FILE, 'r') as f:
            _lock_file(f, exclusive=False)
            try:
                data = json.load(f)
                # Validate structure
                if not isinstance(data, dict):
                    data = {"agents": {}, "dashboard_pid": None}
                if "agents" not in data or not isinstance(data["agents"], dict):
                    data["agents"] = {}
                return data
            finally:
                _unlock_file(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"agents": {}, "dashboard_pid": None}

def save_state(state: Dict):
    """Save state with file locking."""
    ensure_state_dir()
    with open(STATE_FILE, 'w') as f:
        try:
            _lock_file(f, exclusive=True)
            json.dump(state, f, indent=2, default=str)
        finally:
            _unlock_file(f)

def add_agent(agent_id: str, prompt: str, agent_type: str, model: str = "unknown", project_info: dict | None = None):
    """Register a new agent as running."""
    state = load_state()
    pinfo = project_info or {}
    state["agents"][agent_id] = {
        "prompt": prompt,
        "agent_type": agent_type,
        "model": model,
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "ended_at": None,
        "cwd": pinfo.get("cwd"),
        "git_root": pinfo.get("git_root"),
        "project_name": pinfo.get("project_name"),
        "git_branch": pinfo.get("git_branch"),
        "git_remote": pinfo.get("git_remote"),
    }
    order = state.setdefault("start_order", [])
    if agent_id not in order:
        order.append(agent_id)
    save_state(state)
    return len([a for a in state["agents"].values() if a["status"] == "running"])

def update_agent_field(agent_id: str, field: str, value):
    """Update a single field on an agent in state."""
    state = load_state()
    if agent_id in state["agents"]:
        state["agents"][agent_id][field] = value
        save_state(state)


def complete_agent(agent_id: str):
    """Mark an agent as completed."""
    state = load_state()
    if agent_id in state["agents"]:
        state["agents"][agent_id]["status"] = "completed"
        state["agents"][agent_id]["ended_at"] = datetime.now().isoformat()
    order = state.get("start_order", [])
    if agent_id in order:
        order.remove(agent_id)
    # Clean stale entries
    state["start_order"] = [
        aid for aid in order
        if aid in state["agents"] and state["agents"][aid].get("status") == "running"
    ]
    save_state(state)
    return len([a for a in state["agents"].values() if a["status"] == "running"])

def get_running_count() -> int:
    """Get count of running agents."""
    state = load_state()
    return len([a for a in state["agents"].values() if a["status"] == "running"])

def get_all_agents() -> Dict:
    """Get all agents."""
    state = load_state()
    return state.get("agents", {})

def clear_old_agents():
    """Clear completed agents older than 10 minutes."""
    state = load_state()
    now = datetime.now()
    to_remove = []
    for agent_id, info in state["agents"].items():
        if info["status"] == "completed" and info["ended_at"]:
            ended = datetime.fromisoformat(info["ended_at"])
            if (now - ended).total_seconds() > 600:  # 10 minutes
                to_remove.append(agent_id)
    for agent_id in to_remove:
        del state["agents"][agent_id]
    if to_remove:
        save_state(state)

def set_dashboard_pid(pid: Optional[int]):
    """Store the dashboard PID."""
    state = load_state()
    state["dashboard_pid"] = pid
    save_state(state)

def _is_process_running(pid: int) -> bool:
    """Check if a process is running. Windows-reliable."""
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True, text=True
            )
            return str(pid) in result.stdout
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

def get_dashboard_pid() -> Optional[int]:
    """Get the dashboard PID if running."""
    state = load_state()
    pid = state.get("dashboard_pid")
    if pid:
        if _is_process_running(pid):
            return pid
        state["dashboard_pid"] = None
        save_state(state)
    return None


def pop_oldest_running_id() -> Optional[str]:
    """Return the ID of the oldest running agent, in insertion order."""
    state = load_state()
    agents = state.get("agents", {})
    for agent_id in state.get("start_order", []):
        if agent_id in agents and agents[agent_id].get("status") == "running":
            return agent_id
    return None


def find_running_agent_by_prompt(prompt: str) -> Optional[str]:
    """Find a running agent whose prompt matches the given text."""
    if not prompt:
        return None
    state = load_state()
    agents = state.get("agents", {})
    prompt_prefix = prompt[:200].strip()
    for agent_id in state.get("start_order", []):
        if agent_id in agents and agents[agent_id].get("status") == "running":
            stored_prompt = agents[agent_id].get("prompt", "")[:200].strip()
            if stored_prompt and stored_prompt == prompt_prefix:
                return agent_id
    return None
