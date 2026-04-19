#!/usr/bin/env python3
"""
Persistent agent history storage for Claude Agent Monitor.
Stores agent records in ~/.claude/agent-history.json with file locking.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Cross-platform file locking - same pattern as agent_state.py
if sys.platform == "win32":
    import msvcrt

    def _lock_file(f, exclusive=True):
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK if exclusive else msvcrt.LK_NBRLCK, 1)
        except IOError:
            pass

    def _unlock_file(f):
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        except IOError:
            pass
else:
    import fcntl

    def _lock_file(f, exclusive=True):
        fcntl.flock(f.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)

    def _unlock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


HISTORY_FILE = Path.home() / ".claude" / "agent-history.json"


def _load_history() -> Dict:
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            _lock_file(f, exclusive=False)
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    return {"sessions": {}, "agents": {}}
                data.setdefault("sessions", {})
                data.setdefault("agents", {})
                return data
            finally:
                _unlock_file(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"sessions": {}, "agents": {}}


def _save_history(data: Dict):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        _lock_file(f, exclusive=True)
        try:
            json.dump(data, f, indent=2, default=str)
        finally:
            _unlock_file(f)


def _now_iso() -> str:
    return datetime.now().isoformat()


def upsert_agent(agent_id: str, data: Dict):
    """Create or update an agent record. Merges tool_calls and messages lists."""
    history = _load_history()
    agents = history["agents"]
    sessions = history["sessions"]

    if agent_id in agents:
        existing = agents[agent_id]
        existing_tc_ts = {tc.get("timestamp") for tc in existing.get("tool_calls", [])}
        existing_msg_ts = {m.get("timestamp") for m in existing.get("messages", [])}

        for tc in data.get("tool_calls", []):
            if tc.get("timestamp") not in existing_tc_ts:
                existing.setdefault("tool_calls", []).append(tc)

        for msg in data.get("messages", []):
            if msg.get("timestamp") not in existing_msg_ts:
                existing.setdefault("messages", []).append(msg)

        for key in ("status", "ended_at", "last_activity", "model", "type", "prompt",
                    "cwd", "git_root", "project_name", "git_branch", "git_remote",
                    "transcript_path"):
            if key in data and data[key] is not None:
                existing[key] = data[key]
    else:
        agents[agent_id] = {
            "id": agent_id,
            "session_id": data.get("session_id", ""),
            "type": data.get("type", "unknown"),
            "model": data.get("model", "unknown"),
            "prompt": data.get("prompt", ""),
            "status": data.get("status", "running"),
            "started_at": data.get("started_at", _now_iso()),
            "ended_at": data.get("ended_at", None),
            "tool_calls": data.get("tool_calls", []),
            "messages": data.get("messages", []),
            "last_activity": data.get("last_activity", ""),
            "cwd": data.get("cwd"),
            "git_root": data.get("git_root"),
            "project_name": data.get("project_name"),
            "git_branch": data.get("git_branch"),
            "git_remote": data.get("git_remote"),
            "transcript_path": data.get("transcript_path"),
        }

    session_id = data.get("session_id") or agents[agent_id].get("session_id")
    if session_id:
        if session_id not in sessions:
            sessions[session_id] = {
                "started_at": data.get("started_at", _now_iso()),
                "agents": [],
            }
        if agent_id not in sessions[session_id]["agents"]:
            sessions[session_id]["agents"].append(agent_id)

    _save_history(history)


def complete_agent(agent_id: str, ended_at: Optional[str] = None,
                   final_tool_calls: Optional[List] = None,
                   final_messages: Optional[List] = None,
                   transcript_path: Optional[str] = None):
    """Mark agent completed and write full transcript data."""
    history = _load_history()
    agents = history["agents"]

    if agent_id not in agents:
        agents[agent_id] = {
            "id": agent_id,
            "session_id": "",
            "type": "unknown",
            "model": "unknown",
            "prompt": "",
            "status": "completed",
            "started_at": _now_iso(),
            "ended_at": ended_at or _now_iso(),
            "tool_calls": final_tool_calls or [],
            "messages": final_messages or [],
            "last_activity": "",
            "transcript_path": transcript_path,
        }
    else:
        record = agents[agent_id]
        record["status"] = "completed"
        record["ended_at"] = ended_at or _now_iso()
        if final_tool_calls is not None:
            record["tool_calls"] = final_tool_calls
        if final_messages is not None:
            record["messages"] = final_messages
        if transcript_path is not None:
            record["transcript_path"] = transcript_path

    _save_history(history)


def get_agent(agent_id: str) -> Optional[Dict]:
    """Return full agent record including tool_calls and messages."""
    history = _load_history()
    return history["agents"].get(agent_id)


def get_all_agents(limit: int = 100, offset: int = 0) -> Dict:
    """Return metadata-only records (no tool_calls/messages), newest first."""
    history = _load_history()
    records = []

    for agent_id, agent in history["agents"].items():
        records.append({
            "id": agent.get("id", agent_id),
            "session_id": agent.get("session_id", ""),
            "type": agent.get("type", "unknown"),
            "model": agent.get("model", "unknown"),
            "prompt": agent.get("prompt", ""),
            "status": agent.get("status", "unknown"),
            "started_at": agent.get("started_at"),
            "ended_at": agent.get("ended_at"),
            "last_activity": agent.get("last_activity", ""),
            "tool_call_count": len(agent.get("tool_calls", [])),
            "message_count": len(agent.get("messages", [])),
            "cwd": agent.get("cwd"),
            "git_root": agent.get("git_root"),
            "project_name": agent.get("project_name"),
            "git_branch": agent.get("git_branch"),
            "git_remote": agent.get("git_remote"),
            "transcript_path": agent.get("transcript_path"),
        })

    records.sort(key=lambda x: x.get("started_at") or "", reverse=True)
    total = len(records)
    return {"agents": records[offset: offset + limit], "total": total, "limit": limit, "offset": offset}


def search_agents(query: str, date_from: Optional[str] = None,
                  date_to: Optional[str] = None,
                  type_filter: Optional[str] = None,
                  model_filter: Optional[str] = None,
                  status_filter: Optional[str] = None) -> List[Dict]:
    """Search agents by substring match on prompt and message content."""
    history = _load_history()
    query_lower = query.lower() if query else ""
    results = []

    for agent_id, agent in history["agents"].items():
        started = agent.get("started_at", "")
        if date_from and started and started < date_from:
            continue
        if date_to and started and started > date_to:
            continue
        if type_filter and agent.get("type", "").lower() != type_filter.lower():
            continue
        if model_filter and model_filter.lower() not in agent.get("model", "").lower():
            continue
        if status_filter and agent.get("status", "") != status_filter:
            continue
        if query_lower:
            prompt_match = query_lower in agent.get("prompt", "").lower()
            msg_match = any(query_lower in m.get("content", "").lower()
                            for m in agent.get("messages", []))
            if not prompt_match and not msg_match:
                continue

        results.append({
            "id": agent.get("id", agent_id),
            "session_id": agent.get("session_id", ""),
            "type": agent.get("type", "unknown"),
            "model": agent.get("model", "unknown"),
            "prompt": agent.get("prompt", ""),
            "status": agent.get("status", "unknown"),
            "started_at": agent.get("started_at"),
            "ended_at": agent.get("ended_at"),
            "last_activity": agent.get("last_activity", ""),
            "tool_call_count": len(agent.get("tool_calls", [])),
            "message_count": len(agent.get("messages", [])),
            "cwd": agent.get("cwd"),
            "git_root": agent.get("git_root"),
            "project_name": agent.get("project_name"),
            "git_branch": agent.get("git_branch"),
            "git_remote": agent.get("git_remote"),
            "transcript_path": agent.get("transcript_path"),
        })

    results.sort(key=lambda x: x.get("started_at") or "", reverse=True)
    return results


def get_stats() -> Dict:
    """Return aggregate statistics over all history."""
    history = _load_history()
    agents = history["agents"]
    by_model: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    by_date: Dict[str, int] = {}
    durations = []
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()

    for agent in agents.values():
        model = agent.get("model", "unknown")
        atype = agent.get("type", "unknown")
        started = agent.get("started_at", "")
        ended = agent.get("ended_at")

        by_model[model] = by_model.get(model, 0) + 1
        by_type[atype] = by_type.get(atype, 0) + 1

        if started and started >= cutoff:
            date_key = started[:10]
            by_date[date_key] = by_date.get(date_key, 0) + 1

        if started and ended:
            try:
                s = datetime.fromisoformat(started)
                e = datetime.fromisoformat(ended)
                durations.append((e - s).total_seconds())
            except (ValueError, TypeError):
                pass

    avg_duration = sum(durations) / len(durations) if durations else 0
    return {
        "total": len(agents),
        "by_model": by_model,
        "by_type": by_type,
        "by_date": dict(sorted(by_date.items())),
        "avg_duration_seconds": round(avg_duration, 1),
    }


SETTINGS_FILE = Path.home() / ".claude" / "project-settings.json"


def _load_project_settings() -> dict:
    """Load project settings from disk."""
    try:
        if SETTINGS_FILE.exists():
            return json.loads(SETTINGS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        pass
    return {"projects": {}}


def save_project_settings(git_root: str, settings: dict) -> None:
    """Update settings for a project."""
    all_settings = _load_project_settings()
    if "projects" not in all_settings:
        all_settings["projects"] = {}
    existing = all_settings["projects"].get(git_root, {})
    existing.update(settings)
    all_settings["projects"][git_root] = existing
    SETTINGS_FILE.write_text(json.dumps(all_settings, indent=2))


def get_projects() -> list:
    """Aggregate agents by project, return project summaries."""
    history = _load_history()
    agents = history.get("agents", {})
    settings = _load_project_settings()

    projects = {}
    for a in agents.values():
        git_root = a.get("git_root") or "unknown"
        project_name = a.get("project_name") or "Unknown Project"

        if git_root not in projects:
            proj_settings = settings.get("projects", {}).get(git_root, {})
            projects[git_root] = {
                "git_root": git_root,
                "project_name": project_name,
                "display_name": proj_settings.get("display_name", project_name),
                "color": proj_settings.get("color", "#6b7fff"),
                "pinned": proj_settings.get("pinned", False),
                "git_remote": a.get("git_remote"),
                "agent_count": 0,
                "session_count": 0,
                "last_active": None,
                "branches_seen": [],
                "agent_types": {},
                "status_summary": {},
                "_sessions": set(),
            }

        p = projects[git_root]
        p["agent_count"] += 1

        session_id = a.get("session_id")
        if session_id:
            p["_sessions"].add(session_id)

        ended = a.get("ended_at") or a.get("started_at")
        if ended and (not p["last_active"] or ended > p["last_active"]):
            p["last_active"] = ended

        branch = a.get("git_branch")
        if branch and branch not in p["branches_seen"]:
            p["branches_seen"].append(branch)

        atype = a.get("type", "unknown")
        p["agent_types"][atype] = p["agent_types"].get(atype, 0) + 1

        status = a.get("status", "unknown")
        p["status_summary"][status] = p["status_summary"].get(status, 0) + 1

    result = []
    for p in projects.values():
        p["session_count"] = len(p.pop("_sessions"))
        result.append(p)

    # Pinned first, then by last_active descending within each group.
    # Two stable sorts: first by last_active desc, then by pinned group.
    result.sort(key=lambda x: x.get("last_active") or "", reverse=True)
    result.sort(key=lambda x: not x["pinned"])

    return result


def get_project_agents(project_name: str) -> list:
    """Get all agents for a specific project by name."""
    history = _load_history()
    agents = history.get("agents", {})
    result = []
    for a in agents.values():
        pname = a.get("project_name") or "Unknown Project"
        if pname == project_name:
            result.append(a)
    result.sort(key=lambda x: x.get("started_at", ""), reverse=True)
    return result
