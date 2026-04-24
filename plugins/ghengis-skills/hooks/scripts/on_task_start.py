#!/usr/bin/env python3
"""
PreToolUse hook for Task tool.
Triggered when Claude Code is about to spawn a subagent.
Registers the agent and launches dashboard if 2+ agents running.
"""

import sys
import os
import json
import socket
import subprocess
import time
import tempfile
import contextlib
from datetime import datetime
from pathlib import Path

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))

import agent_state
import agent_history
from browser_utils import open_browser, get_platform
from on_project_detect import detect_project_info

TEMP_BASE = Path(tempfile.gettempdir())
DASHBOARD_PORT = 7685

@contextlib.contextmanager
def _acquire_launch_lock():
    """Acquire an OS-level lock for dashboard launching.
    Yields True if lock acquired, False if another process holds it.
    """
    monitor_dir = Path(tempfile.gettempdir()) / "claude-agent-monitor"
    monitor_dir.mkdir(exist_ok=True)
    lock_path = monitor_dir / "launching.lock"

    f = None
    acquired = False
    try:
        f = open(lock_path, 'w')
        if sys.platform == "win32":
            import msvcrt
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                acquired = True
            except (IOError, OSError):
                acquired = False
        else:
            import fcntl
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except (IOError, OSError):
                acquired = False
        yield acquired
    finally:
        if f:
            if acquired:
                try:
                    if sys.platform == "win32":
                        import msvcrt
                        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
            f.close()

def _is_port_bound(port: int) -> bool:
    """Check if a port is already in use."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except (ConnectionRefusedError, OSError):
        return False

def _find_pid_for_port(port: int) -> int | None:
    """Find the PID owning a port using netstat. Windows-compatible."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if parts:
                    try:
                        return int(parts[-1])
                    except ValueError:
                        pass
    except Exception:
        pass
    return None

def extract_agent_info(hook_input: dict) -> tuple:
    """Extract agent info from hook input."""
    tool_input = hook_input.get("tool_input", {})

    prompt = tool_input.get("prompt", "")
    agent_type = tool_input.get("subagent_type", "unknown")
    description = tool_input.get("description", "")
    model = tool_input.get("model", "inherit")

    import secrets
    agent_id = f"{int(time.time()*1000)}_{secrets.token_hex(4)}"

    return agent_id, prompt, agent_type, model, description

def _get_terminal_id() -> str:
    """Get a stable identifier for the current terminal/session.
    Uses CLAUDE_SESSION_ID env var if available, otherwise falls back to parent PID.
    """
    return os.environ.get("CLAUDE_SESSION_ID", str(os.getppid()))


def _is_process_running(pid: int) -> bool:
    """Check if a process with the given PID is still running."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True, text=True, timeout=5
            )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.TimeoutExpired):
        return False


def _cleanup_stale_flags(sessions_dir: Path):
    """Remove flag files whose terminal PID is no longer running."""
    try:
        for flag_file in sessions_dir.iterdir():
            if not flag_file.suffix == ".flag":
                continue
            terminal_pid_str = flag_file.stem
            try:
                terminal_pid = int(terminal_pid_str)
            except ValueError:
                continue
            if not _is_process_running(terminal_pid):
                try:
                    flag_file.unlink()
                except OSError:
                    pass
    except OSError:
        pass


def launch_dashboard():
    """Launch the web dashboard and open browser (reusing existing tab).

    Browser tab reuse strategy (per-terminal):
    - Each terminal tracks its own browser-open state via a flag file
      in browser_opened_sessions/<terminal_id>.flag
    - The flag file stores the dashboard PID that the browser was opened for
    - If dashboard restarts (new PID), each terminal opens exactly one new tab
    - Stale flag files from dead terminals are cleaned up automatically
    """
    dashboard_script = Path(__file__).parent / "agent_web_dashboard.py"
    monitor_dir = TEMP_BASE / "claude-agent-monitor"
    sessions_dir = monitor_dir / "browser_opened_sessions"
    terminal_id = _get_terminal_id()
    terminal_flag = sessions_dir / f"{terminal_id}.flag"

    # Ensure directories exist
    monitor_dir.mkdir(exist_ok=True)
    sessions_dir.mkdir(exist_ok=True)

    # Clean up stale flag files from dead terminal processes
    _cleanup_stale_flags(sessions_dir)

    # Fix 1: Port probe - check if dashboard is already bound before trusting state.json
    port_in_use = _is_port_bound(DASHBOARD_PORT)

    # Check if dashboard is already running
    current_dashboard_pid = agent_state.get_dashboard_pid()
    dashboard_running = current_dashboard_pid is not None

    # Fix 3: Self-healing - port bound but state.json has null PID
    if port_in_use and not dashboard_running:
        discovered_pid = _find_pid_for_port(DASHBOARD_PORT)
        if discovered_pid:
            agent_state.set_dashboard_pid(discovered_pid)
            current_dashboard_pid = discovered_pid
            dashboard_running = True
        else:
            # Port is bound but can't find PID - still treat as running to avoid crash loop
            dashboard_running = True

    # Per-terminal check: has THIS terminal already opened a browser for the current dashboard?
    browser_already_opened = False
    if terminal_flag.exists():
        try:
            stored_pid = terminal_flag.read_text().strip()
            if stored_pid == str(current_dashboard_pid):
                browser_already_opened = True
        except Exception as e:
            print(f"Warning: Failed to read terminal flag file: {e}", file=sys.stderr)

    if dashboard_running and browser_already_opened:
        return True  # Dashboard running and this terminal already opened a tab

    with _acquire_launch_lock() as got_lock:
        if not got_lock:
            return True  # Another process is launching

        # Re-check per-terminal flag after acquiring lock (TOCTOU prevention)
        if terminal_flag.exists():
            try:
                stored_pid = terminal_flag.read_text().strip()
                # Re-read dashboard PID in case it changed while waiting for lock
                fresh_pid = agent_state.get_dashboard_pid()
                if stored_pid == str(fresh_pid):
                    return True  # Another invocation in this terminal beat us to it
            except Exception:
                pass

        # Launch the web server in background (only if not already running and port is free)
        new_dashboard_started = False
        if not dashboard_running and not port_in_use:
            try:
                popen_kwargs = {
                    "stdout": subprocess.DEVNULL,
                    "stderr": subprocess.DEVNULL,
                }
                if sys.platform == "win32":
                    popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                else:
                    popen_kwargs["start_new_session"] = True
                subprocess.Popen([sys.executable, str(dashboard_script)], **popen_kwargs)
                time.sleep(0.5)  # Give server time to start
                new_dashboard_started = True
                # Get the new dashboard PID
                current_dashboard_pid = agent_state.get_dashboard_pid()
            except Exception as e:
                notify_file = TEMP_BASE / "claude-agent-monitor" / "launch-failed"
                notify_file.write_text(f"Dashboard launch failed: {e}\nRun manually:\npython3 {dashboard_script}\n")
                return False

        # Only open browser if:
        # 1. A new dashboard just started, OR
        # 2. Dashboard was already running but this terminal never opened a tab for it
        if browser_already_opened and not new_dashboard_started:
            return True

        # Write per-terminal flag with the dashboard PID
        try:
            terminal_flag.write_text(str(current_dashboard_pid or ""))
        except OSError as e:
            print(f"Warning: Failed to write terminal flag: {e}", file=sys.stderr)

        # Open browser using cross-platform utility
        # Respects GHENGIS_AGENT_MONITOR_AUTO_OPEN env var (default: false)
        url = "http://localhost:7685"
        auto_open = os.environ.get("GHENGIS_AGENT_MONITOR_AUTO_OPEN", "false").lower()
        if auto_open in ("true", "1", "yes"):
            open_browser(url)
        else:
            # Silent mode: print URL to stderr so user can open manually
            print(f"[agent-monitor] Dashboard running at {url}", file=sys.stderr)

    return True

def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Extract agent info
    agent_id, prompt, agent_type, model, description = extract_agent_info(hook_input)

    # Detect project context
    project_info = detect_project_info()

    # Register the agent
    running_count = agent_state.add_agent(agent_id, prompt, agent_type, model, project_info=project_info)

    # Write to persistent history
    import uuid
    _state = agent_state.load_state()
    if "session_id" not in _state or not _state.get("session_id"):
        _state["session_id"] = uuid.uuid4().hex[:12]
        agent_state.save_state(_state)
    session_id = _state.get("session_id", "unknown")

    agent_history.upsert_agent(agent_id, {
        "session_id": session_id,
        "type": agent_type,
        "model": model,
        "prompt": prompt,
        "status": "running",
        "started_at": datetime.now().isoformat(),
        **project_info,
    })

    # Launch dashboard on first agent (or if 2+ running)
    if running_count >= 1 and not agent_state.get_dashboard_pid():
        launch_dashboard()

    # Always allow the tool to proceed
    sys.exit(0)

if __name__ == "__main__":
    main()
