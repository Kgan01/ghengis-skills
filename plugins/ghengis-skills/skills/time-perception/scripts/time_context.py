"""
time_context - Give any LLM a sense of time.

Portable time-awareness module that can be used with any LLM API.
Tracks message timestamps, elapsed time, task durations, and per-project logs.

Usage:
    from time_context import TimeContext

    tc = TimeContext(project="my-app")

    # Get time context string to inject into any LLM prompt
    context = tc.stamp()
    # -> "<time-context>current_time: 2026-03-06 22:55:00 MST | previous: 5m ago | messages: 42</time-context>"

    # Use as middleware for any LLM call
    response = tc.wrap(llm_call, prompt="fix the bug")

    # Mark task complete (logs duration)
    tc.done()

    # Read logs for analysis
    history = tc.get_history()
    durations = tc.get_durations()
    summary = tc.summary()
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


class TimeContext:
    def __init__(
        self,
        project: Optional[str] = None,
        data_dir: Optional[str] = None,
        agent_name: Optional[str] = None,
    ):
        """
        Initialize time context tracker.

        Args:
            project: Project name for per-project logging. Auto-detected from cwd if None.
            data_dir: Directory for storing time data. Defaults to ~/.claude/
            agent_name: Name of the agent/LLM using this (e.g., "gpt-4", "claude-subagent-1")
        """
        self.data_dir = Path(data_dir or os.path.expanduser("~/.claude"))
        self.project = project or Path.cwd().name
        self.agent_name = agent_name or "default"
        self._task_start: Optional[float] = None

        # File paths
        self.state_file = self.data_dir / "time-data.json"
        self.global_log = self.data_dir / "time-log.jsonl"
        self.global_durations = self.data_dir / "task-durations.jsonl"
        self.project_dir = self.data_dir / "project-time"
        self.project_log = self.project_dir / f"{self._safe_name(self.project)}.jsonl"
        self.project_durations = self.project_dir / f"{self._safe_name(self.project)}.durations.jsonl"

        self.project_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_name(name: str) -> str:
        return name.replace("/", "_").replace("\\", "_").replace(":", "_").strip("_")

    @staticmethod
    def _format_elapsed(seconds: int) -> str:
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        elif seconds < 86400:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
        else:
            return f"{seconds // 86400}d {(seconds % 86400) // 3600}h"

    def _read_state(self) -> dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _write_state(self, state: dict):
        self.state_file.write_text(json.dumps(state, indent=2))

    def _append_log(self, path: Path, entry: dict):
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def stamp(self, prompt_preview: str = "") -> str:
        """
        Record a timestamp and return time context string.
        Call this before sending a prompt to any LLM.

        Returns a <time-context> string suitable for injection into any prompt.
        """
        now_epoch = int(time.time())
        now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        state = self._read_state()
        prev_epoch = state.get("last_message_epoch", 0)
        prev_local = state.get("last_message_local", "none")
        prev_project = state.get("last_project", "")
        msg_count = state.get("message_count", 0)

        if prev_epoch > 0:
            elapsed = now_epoch - prev_epoch
            elapsed_str = self._format_elapsed(elapsed)
        else:
            elapsed = 0
            elapsed_str = "N/A"

        msg_count += 1
        self._task_start = now_epoch

        # Update state
        new_state = {
            "last_message_epoch": now_epoch,
            "last_message_iso": now_iso,
            "last_message_local": now_local,
            "last_project": self.project,
            "message_count": msg_count,
        }
        self._write_state(new_state)

        # Global log
        self._append_log(self.global_log, {
            "timestamp": now_iso,
            "local": now_local,
            "epoch": now_epoch,
            "elapsed_seconds": elapsed,
            "message_number": msg_count,
            "project": self.project,
            "agent": self.agent_name,
        })

        # Per-project log
        self._append_log(self.project_log, {
            "timestamp": now_iso,
            "local": now_local,
            "epoch": now_epoch,
            "elapsed_seconds": elapsed,
            "agent": self.agent_name,
            "prompt_preview": prompt_preview[:100] if prompt_preview else "",
        })

        # Build compact context string
        # Format: [T:YYYY-MM-DD HH:MM|+elapsed|#count] or with project on switch
        now_short = datetime.now().strftime("%Y-%m-%d %H:%M")
        parts = [f"T:{now_short}", f"+{elapsed_str}", f"#{msg_count}"]
        if prev_project and prev_project != self.project:
            parts.append(f"{self.project}<-{prev_project}")
        if self.agent_name != "default":
            parts.append(f"@{self.agent_name}")

        context = "[" + "|".join(parts) + "]"
        return context

    def done(self, task_label: str = "") -> Optional[str]:
        """
        Mark current task as complete and log duration.
        Call this after the LLM finishes responding.

        Returns human-readable duration string, or None if no task was started.
        """
        if not self._task_start:
            state = self._read_state()
            self._task_start = state.get("last_message_epoch", 0)

        if not self._task_start:
            return None

        now_epoch = int(time.time())
        now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
        duration = now_epoch - self._task_start
        duration_str = self._format_elapsed(duration)

        entry = {
            "completed": now_local,
            "duration_seconds": duration,
            "duration_human": duration_str,
            "project": self.project,
            "agent": self.agent_name,
        }
        if task_label:
            entry["task"] = task_label

        self._append_log(self.global_durations, entry)
        self._append_log(self.project_durations, entry)

        self._task_start = None
        return duration_str

    def wrap(self, llm_call: Callable, prompt: str, **kwargs) -> Any:
        """
        Wrap any LLM call with time tracking.

        Injects time context, calls the LLM, logs duration, returns response.

        Args:
            llm_call: Function that takes (prompt, **kwargs) and returns a response
            prompt: The prompt to send
            **kwargs: Additional arguments passed to llm_call

        Returns:
            The LLM's response
        """
        context = self.stamp(prompt_preview=prompt)
        augmented_prompt = f"{context}\n\n{prompt}"

        response = llm_call(augmented_prompt, **kwargs)

        self.done(task_label=prompt[:50])
        return response

    def inject(self, messages: list[dict], prompt_preview: str = "") -> list[dict]:
        """
        Inject time context into an OpenAI-style messages list.
        Adds a system message with time context.

        Args:
            messages: List of {"role": ..., "content": ...} dicts
            prompt_preview: Short description of the task for logging

        Returns:
            New messages list with time context prepended as system message
        """
        context = self.stamp(prompt_preview=prompt_preview)
        time_msg = {"role": "system", "content": context}
        return [time_msg] + messages

    def get_history(self, project_only: bool = False) -> list[dict]:
        """Read message history from log files."""
        log_file = self.project_log if project_only else self.global_log
        if not log_file.exists():
            return []
        entries = []
        for line in log_file.read_text().strip().split("\n"):
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return entries

    def get_durations(self, project_only: bool = False) -> list[dict]:
        """Read task duration history."""
        log_file = self.project_durations if project_only else self.global_durations
        if not log_file.exists():
            return []
        entries = []
        for line in log_file.read_text().strip().split("\n"):
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return entries

    def summary(self) -> dict:
        """
        Generate a summary of time data for this project.
        Useful for injecting into LLM context as a behavioral overview.
        """
        history = self.get_history(project_only=True)
        durations = self.get_durations(project_only=True)

        if not history:
            return {"project": self.project, "total_messages": 0}

        gaps = [e["elapsed_seconds"] for e in history if e.get("elapsed_seconds", 0) > 0]
        task_times = [e["duration_seconds"] for e in durations if e.get("duration_seconds", 0) > 0]

        summary = {
            "project": self.project,
            "total_messages": len(history),
            "total_tasks_completed": len(durations),
            "first_interaction": history[0].get("local", ""),
            "last_interaction": history[-1].get("local", ""),
        }

        if gaps:
            summary["avg_time_between_messages"] = self._format_elapsed(sum(gaps) // len(gaps))
            summary["longest_gap"] = self._format_elapsed(max(gaps))

        if task_times:
            summary["avg_task_duration"] = self._format_elapsed(sum(task_times) // len(task_times))
            summary["longest_task"] = self._format_elapsed(max(task_times))
            summary["shortest_task"] = self._format_elapsed(min(task_times))

        # Agent breakdown
        agents = {}
        for e in history:
            agent = e.get("agent", "default")
            agents[agent] = agents.get(agent, 0) + 1
        if len(agents) > 1 or "default" not in agents:
            summary["agents"] = agents

        return summary
