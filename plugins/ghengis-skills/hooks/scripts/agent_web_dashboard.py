#!/usr/bin/env python3
"""
Web-based dashboard for monitoring Claude Code subagents.
Serves two ports: React on 7685, Vanilla on 7686.
"""

import sys
import os
import json
import glob
import time
import signal
import atexit
import threading
import subprocess
import mimetypes
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).parent))
import agent_state
import agent_history
import agent_permissions

REACT_PORT = 7685
VANILLA_PORT = 7686
HOOKS_DIR = Path(__file__).parent
REACT_DIST = HOOKS_DIR / "dashboard-react" / "dist"
VANILLA_HTML = HOOKS_DIR / "dashboard-vanilla" / "index.html"

should_exit = False

# Cross-platform shutdown handling
if sys.platform == "win32":
    def signal_handler(signum=None, frame=None):
        global should_exit
        should_exit = True
    atexit.register(signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
else:
    def signal_handler(signum, frame):
        global should_exit
        should_exit = True
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def find_agent_transcripts():
    """Find recent agent transcript files.

    Claude Code writes session transcripts as UUID-named JSONL files under
    ~/.claude/projects/<encoded-cwd>/<uuid>.jsonl. The old pattern 'agent-*.jsonl'
    never matched; the correct pattern is '*.jsonl'.
    """
    project_dirs = glob.glob(os.path.expanduser("~/.claude/projects/*"))
    candidates = []
    for pdir in project_dirs:
        for f in glob.glob(os.path.join(pdir, "*.jsonl")):
            mtime = os.path.getmtime(f)
            if time.time() - mtime < 600:
                candidates.append((f, mtime))
    candidates.sort(key=lambda x: x[1], reverse=True)
    return [c[0] for c in candidates[:40]]


def _extract_user_prompt(content) -> str:
    """Extract a real user prompt from message content.

    Claude Code injects wrappers as string-type content. Real prompts come as
    list-type content with type=text items. We prefer list-type and filter
    known injected string patterns.
    """
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                text = c.get("text", "")
                if text and not text.startswith("<local-command-caveat>"):
                    return text
    elif isinstance(content, str):
        # String content = almost always an injected wrapper; skip known patterns
        if not content.startswith("<local-command-caveat>") and \
           not content.startswith("<command-name>") and \
           not content.startswith("<command-message>"):
            return content
    return ""


def parse_agent_file(filepath: str) -> dict:
    """Parse agent JSONL file to extract full info.

    The first line is often a 'file-history-snapshot' record, not a user message.
    We scan all lines to find the first real user prompt, then collect all
    assistant tool_calls and tool_results.
    """
    info = {
        "agent_id": Path(filepath).stem,
        "session_id": Path(filepath).stem,  # UUID filename = session_id
        "model": "unknown",
        "prompt": "",
        "status": "running",
        "started_at": None,
        "ended_at": None,
        "last_activity": "",
        "tool_calls": [],
        "messages": [],
        "filepath": filepath
    }
    prompt_found = False
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            try:
                data = json.loads(line.strip())
                msg = data.get("message", {})
                msg_type = data.get("type", "")
                timestamp = data.get("timestamp", "")

                # Extract session_id from outer record if present
                if not info.get("_session_from_record") and data.get("sessionId"):
                    info["session_id"] = data["sessionId"]
                    info["_session_from_record"] = True

                # Find first real user prompt
                if msg_type == "user" and not prompt_found:
                    extracted = _extract_user_prompt(msg.get("content", ""))
                    if extracted:
                        info["prompt"] = extracted
                        info["started_at"] = timestamp
                        prompt_found = True

                if msg_type == "assistant":
                    if msg.get("model"):
                        info["model"] = msg["model"]
                    if msg.get("stop_reason") == "end_turn":
                        info["status"] = "completed"
                        info["ended_at"] = timestamp
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for c in content:
                            if c.get("type") == "text":
                                text = c.get("text", "")
                                if text:
                                    info["last_activity"] = text
                                    info["messages"].append({
                                        "type": "text",
                                        "content": text,
                                        "timestamp": timestamp
                                    })
                            elif c.get("type") == "tool_use":
                                tool_name = c.get("name", "unknown")
                                tool_input = c.get("input", {})
                                info["tool_calls"].append({
                                    "name": tool_name,
                                    "input": tool_input,
                                    "timestamp": timestamp
                                })
                                info["last_activity"] = f"Using: {tool_name}"

                if msg_type == "user" and i > 0:
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for c in content:
                            if c.get("type") == "tool_result":
                                tool_id = c.get("tool_use_id", "")
                                result = c.get("content", "")
                                if isinstance(result, list):
                                    result = "\n".join([r.get("text", str(r)) for r in result if isinstance(r, dict)])
                                info["messages"].append({
                                    "type": "tool_result",
                                    "tool_id": tool_id,
                                    "content": str(result)[:2000],
                                    "timestamp": timestamp
                                })
            except json.JSONDecodeError:
                continue
    except Exception as e:
        info["last_activity"] = f"Error reading: {str(e)}"

    # Clean up internal tracking key
    info.pop("_session_from_record", None)

    if info["started_at"] and info["ended_at"]:
        try:
            s = datetime.fromisoformat(info["started_at"])
            e = datetime.fromisoformat(info["ended_at"])
            info["duration_seconds"] = round((e - s).total_seconds(), 1)
        except (ValueError, TypeError):
            pass
    return info


import re as _re

def _normalize_prompt(text: str) -> str:
    """Normalize a prompt for flexible comparison: strip and collapse whitespace."""
    if not text:
        return ""
    return _re.sub(r'\s+', ' ', text.strip())


def _prompts_match(state_prompt: str, transcript_prompt: str) -> bool:
    """Check if a tracked agent's prompt matches a transcript prompt.

    Claude Code wraps/transforms the original prompt before writing to the
    transcript JSONL, so exact prefix matching rarely works. This uses
    progressively looser strategies:
      1. Normalized 200-char prefix equality
      2. Substring containment (shorter inside longer)
      3. Normalized 50-char prefix equality (very loose fallback)
    """
    if not state_prompt or not transcript_prompt:
        return False

    sp = _normalize_prompt(state_prompt)
    tp = _normalize_prompt(transcript_prompt)

    if not sp or not tp:
        return False

    # Strategy 1: normalized 200-char prefix
    if sp[:200] == tp[:200]:
        return True

    # Strategy 2: substring containment
    shorter, longer = (sp, tp) if len(sp) <= len(tp) else (tp, sp)
    if len(shorter) >= 20 and shorter in longer:
        return True

    # Strategy 3: loose 50-char prefix
    if len(sp) >= 50 and len(tp) >= 50 and sp[:50] == tp[:50]:
        return True

    return False


def _parse_iso_timestamp(ts: str):
    """Parse an ISO timestamp string, returning a naive UTC datetime or None."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
        # Normalize to naive UTC so all comparisons work
        if dt.tzinfo is not None:
            from datetime import timezone
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except (ValueError, TypeError):
        return None


def get_all_agent_data():
    """Get comprehensive agent data from state and transcripts.

    Matching strategy (in priority order):
      1. Direct transcript_path from state data (set by stop hook)
      2. Flexible prompt matching with normalization and substring checks
      3. Closest started_at timestamp for remaining unmatched pairs
    """
    agent_state.clear_old_agents()
    tracked = agent_state.get_all_agents()
    transcript_files = find_agent_transcripts()
    transcript_data = {}
    for f in transcript_files:
        parsed = parse_agent_file(f)
        transcript_data[parsed["session_id"]] = parsed

    agents = []
    matched_transcripts = set()

    def _enrich_agent(agent, tdata, tid):
        """Merge transcript activity data into a tracked agent dict."""
        agent["id"] = tid
        agent["model"] = tdata["model"]
        agent["prompt"] = tdata["prompt"] or agent["prompt"]
        agent["tool_calls"] = tdata["tool_calls"]
        agent["messages"] = tdata["messages"]
        agent["last_activity"] = tdata["last_activity"]
        agent["status"] = tdata["status"]
        if tdata.get("ended_at"):
            agent["ended_at"] = tdata["ended_at"]
        if tdata.get("started_at"):
            agent["started_at"] = tdata["started_at"]
        matched_transcripts.add(tid)

    # --- Pass 1: Direct transcript_path lookup (primary method) ---
    agents_needing_match = []  # (agent_dict, state_info) pairs without activity

    for agent_hash, state_info in tracked.items():
        agent = {
            "id": agent_hash,
            "type": state_info.get("agent_type", "unknown"),
            "model": state_info.get("model", "unknown"),
            "prompt": state_info.get("prompt", ""),
            "status": state_info.get("status", "running"),
            "started_at": state_info.get("started_at"),
            "ended_at": state_info.get("ended_at"),
            "tool_calls": [],
            "messages": [],
            "last_activity": ""
        }

        transcript_path = state_info.get("transcript_path")
        if transcript_path and os.path.isfile(transcript_path):
            tdata = parse_agent_file(transcript_path)
            tid = tdata["session_id"]
            _enrich_agent(agent, tdata, tid)
        else:
            agents_needing_match.append((agent, state_info))

        agents.append(agent)

    # --- Pass 2: Flexible prompt matching for unmatched agents ---
    still_unmatched = []

    for agent, state_info in agents_needing_match:
        prompt = agent["prompt"]
        matched_tid = None
        for tid, tdata in transcript_data.items():
            if tid in matched_transcripts:
                continue
            if _prompts_match(prompt, tdata["prompt"]):
                matched_tid = tid
                break

        if matched_tid:
            _enrich_agent(agent, transcript_data[matched_tid], matched_tid)
        else:
            still_unmatched.append(agent)

    # --- Pass 3: Timestamp-based matching for remaining unmatched agents ---
    # For agents that have no activity yet, try to find the closest unmatched
    # transcript by started_at time.
    if still_unmatched:
        available_tids = [
            tid for tid in transcript_data
            if tid not in matched_transcripts
        ]
        for agent in still_unmatched:
            if not available_tids:
                break
            agent_ts = _parse_iso_timestamp(agent.get("started_at"))
            if not agent_ts:
                continue

            best_tid = None
            best_diff = None
            for tid in available_tids:
                tdata = transcript_data[tid]
                t_ts = _parse_iso_timestamp(tdata.get("started_at"))
                if not t_ts:
                    continue
                diff = abs((agent_ts - t_ts).total_seconds())
                # Only consider transcripts within 30 seconds of the agent start
                if diff <= 30 and (best_diff is None or diff < best_diff):
                    best_diff = diff
                    best_tid = tid

            if best_tid:
                _enrich_agent(agent, transcript_data[best_tid], best_tid)
                available_tids.remove(best_tid)

    # --- Pass 4: Enrich tracked agents from unmatched running transcripts ---
    # Instead of creating duplicate "unknown" entries, try to pair remaining
    # running transcripts with tracked agents that still lack activity data.
    unenriched = [a for a in agents if not a["tool_calls"] and not a["messages"]]
    for tid, tdata in transcript_data.items():
        if tid in matched_transcripts:
            continue
        if tdata["status"] != "running":
            continue

        # Try to pair with an unenriched tracked agent
        paired = False
        for agent in unenriched:
            if agent.get("tool_calls") or agent.get("messages"):
                continue  # already enriched by an earlier iteration
            _enrich_agent(agent, tdata, tid)
            paired = True
            break

        # Only create an unknown entry if no tracked agent could be paired
        if not paired:
            agents.append({
                "id": tid,
                "type": "unknown",
                "model": tdata["model"],
                "prompt": tdata["prompt"],
                "status": tdata["status"],
                "started_at": tdata["started_at"],
                "ended_at": tdata["ended_at"],
                "tool_calls": tdata["tool_calls"],
                "messages": tdata["messages"],
                "last_activity": tdata["last_activity"]
            })

    agents.sort(key=lambda x: x.get("started_at") or "", reverse=True)
    return {
        "agents": agents,
        "running_count": len([a for a in agents if a["status"] == "running"]),
        "total_count": len(agents),
        "timestamp": datetime.now().isoformat()
    }


# --- Shared API logic ---

def handle_api_agents():
    return get_all_agent_data()


def handle_api_history(params):
    q = params.get("q", [""])[0]
    date_from = params.get("date_from", [None])[0]
    date_to = params.get("date_to", [None])[0]
    atype = params.get("type", [None])[0]
    model = params.get("model", [None])[0]
    status = params.get("status", [None])[0]
    limit = int(params.get("limit", ["100"])[0])
    offset = int(params.get("offset", ["0"])[0])
    if q or date_from or date_to or atype or model or status:
        agents = agent_history.search_agents(q, date_from, date_to, atype, model, status_filter=status)
        total = len(agents)
        agents = agents[offset: offset + limit]
        return {"agents": agents, "total": total, "limit": limit, "offset": offset}
    else:
        return agent_history.get_all_agents(limit=limit, offset=offset)


def handle_api_history_id(agent_id):
    return agent_history.get_agent(agent_id)


def handle_api_stats():
    return agent_history.get_stats()


def handle_api_projects(params: dict) -> dict:
    """Return all projects with aggregated stats."""
    projects = agent_history.get_projects()
    return {"projects": projects}


def handle_api_project_agents(project_name: str, params: dict) -> dict:
    """Return agents for a specific project."""
    agents = agent_history.get_project_agents(project_name)
    return {"agents": agents, "total": len(agents)}


def handle_api_project_settings(project_name: str, body: dict) -> dict:
    """Update project settings (display_name, color, pinned)."""
    projects = agent_history.get_projects()
    git_root = None
    for p in projects:
        if p["project_name"] == project_name:
            git_root = p["git_root"]
            break
    if not git_root:
        return {"error": "Project not found"}

    allowed_keys = {"display_name", "color", "pinned"}
    filtered = {k: v for k, v in body.items() if k in allowed_keys}
    agent_history.save_project_settings(git_root, filtered)
    return {"ok": True}


def handle_api_permissions():
    pending = agent_permissions.get_pending()
    # Convert timestamps for JSON serialization
    for p in pending:
        p["created_at"] = datetime.fromtimestamp(p["created_at"]).isoformat()
        p["expires_at"] = datetime.fromtimestamp(p["expires_at"]).isoformat()
    return {"permissions": pending}


def handle_api_permissions_decide(request_id, body):
    approved = body.get("approved", False)
    ok = agent_permissions.decide(request_id, approved)
    return {"success": ok, "request_id": request_id}


# --- Auto-build React ---

def _maybe_build_react():
    dist_index = REACT_DIST / "index.html"
    if not dist_index.exists():
        react_dir = HOOKS_DIR / "dashboard-react"
        if (react_dir / "package.json").exists():
            try:
                print("Building React dashboard...")
                subprocess.run(["npm", "run", "build"], cwd=str(react_dir),
                               capture_output=True, timeout=120)
            except Exception as e:
                print(f"React build skipped: {e}")


# --- Shared handler mixin ---

class _ApiMixin:
    def log_message(self, format, *args):
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html, status=200):
        body = html.encode() if isinstance(html, str) else html
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_not_found(self):
        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/api/agents":
            self.send_json(handle_api_agents())
        elif path == "/api/history":
            self.send_json(handle_api_history(params))
        elif path.startswith("/api/history/"):
            agent_id = path[len("/api/history/"):]
            record = handle_api_history_id(agent_id)
            if record is None:
                self.send_json({"error": "not found"}, status=404)
            else:
                self.send_json(record)
        elif path == "/api/stats":
            self.send_json(handle_api_stats())
        elif path == "/api/projects":
            self.send_json(handle_api_projects(params))
        elif path.startswith("/api/projects/") and path.endswith("/agents"):
            parts = path.split("/")
            project_name = parts[3] if len(parts) >= 5 else ""
            from urllib.parse import unquote
            project_name = unquote(project_name)
            self.send_json(handle_api_project_agents(project_name, params))
        elif path == "/api/permissions":
            self.send_json(handle_api_permissions())
        else:
            self._serve_static(path)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = {}
        if content_length:
            try:
                body = json.loads(self.rfile.read(content_length))
            except json.JSONDecodeError:
                pass

        if path.startswith("/api/permissions/") and path.endswith("/decide"):
            parts = path.split("/")
            request_id = parts[-2]
            self.send_json(handle_api_permissions_decide(request_id, body))
        elif path.startswith("/api/projects/") and path.endswith("/settings"):
            parts = path.split("/")
            project_name = parts[3] if len(parts) >= 5 else ""
            from urllib.parse import unquote
            project_name = unquote(project_name)
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length)) if content_length else {}
            self.send_json(handle_api_project_settings(project_name, body))
        else:
            self.send_not_found()


class ReactHandler(_ApiMixin, BaseHTTPRequestHandler):
    def _serve_static(self, path):
        if not REACT_DIST.exists():
            self.send_html("<html><body style='background:#0a0a0f;color:#e2e8f0;font-family:sans-serif;padding:40px'>"
                          "<h2>React dashboard not built yet</h2>"
                          "<p>Run: <code>cd ~/.claude/hooks/dashboard-react && npm install && npm run build</code></p>"
                          "</body></html>")
            return
        file_path = REACT_DIST / path.lstrip("/")
        if not file_path.exists() or file_path.is_dir():
            file_path = REACT_DIST / "index.html"
        # Security: ensure path is within dist
        try:
            file_path.resolve().relative_to(REACT_DIST.resolve())
        except ValueError:
            self.send_not_found()
            return
        try:
            content = file_path.read_bytes()
            content_type, _ = mimetypes.guess_type(str(file_path))
            content_type = content_type or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.send_not_found()


class VanillaHandler(_ApiMixin, BaseHTTPRequestHandler):
    def _serve_static(self, path):
        if path == "/" or path == "/index.html":
            if VANILLA_HTML.exists():
                content = VANILLA_HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_html("<html><body style='background:#0a0a0f;color:#e2e8f0;font-family:sans-serif;padding:40px'>"
                              "<h2>Vanilla dashboard not found</h2>"
                              "<p>Expected at: dashboard-vanilla/index.html</p>"
                              "</body></html>")
        else:
            self.send_not_found()


def run_server():
    global should_exit
    agent_state.set_dashboard_pid(os.getpid())
    _maybe_build_react()

    react_server = ThreadingHTTPServer(("127.0.0.1", REACT_PORT), ReactHandler)
    react_server.allow_reuse_address = True
    vanilla_server = ThreadingHTTPServer(("127.0.0.1", VANILLA_PORT), VanillaHandler)
    vanilla_server.allow_reuse_address = True

    react_thread = threading.Thread(target=react_server.serve_forever, daemon=True)
    react_thread.start()
    vanilla_thread = threading.Thread(target=vanilla_server.serve_forever, daemon=True)
    vanilla_thread.start()

    print(f"Agent Monitor (React)   -> http://localhost:{REACT_PORT}")
    print(f"Agent Monitor (Vanilla) -> http://localhost:{VANILLA_PORT}")

    no_running_count = 0
    try:
        while not should_exit:
            time.sleep(1)
            data = get_all_agent_data()
            if data["running_count"] == 0 and data["total_count"] > 0:
                no_running_count += 1
                if no_running_count >= 10:
                    break
            else:
                no_running_count = 0
    except KeyboardInterrupt:
        pass
    finally:
        agent_state.set_dashboard_pid(None)
        react_server.shutdown()
        vanilla_server.shutdown()
        print("Agent Monitor stopped.")


if __name__ == "__main__":
    run_server()
