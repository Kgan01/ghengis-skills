#!/usr/bin/env python3
"""
SubagentStop hook.
Triggered when a Claude Code subagent finishes.
Updates agent status and closes dashboard if no agents running.
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))

import agent_state
import agent_history


def terminate_process(pid: int) -> bool:
    """Terminate a process by PID, cross-platform."""
    try:
        if sys.platform == "win32":
            import subprocess
            subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                          capture_output=True, check=False)
        else:
            import signal
            os.kill(pid, signal.SIGTERM)
        return True
    except Exception as e:
        print(f"Warning: Failed to terminate process {pid}: {e}", file=sys.stderr)
        return False


def extract_prompt_from_transcript(filepath: str) -> Optional[str]:
    """Read the transcript and find the first real user prompt.

    Claude Code injects wrappers as string-type content. Real user prompts arrive
    as list-type content with type=text items. We prefer list-type and skip known
    injected string patterns.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for line in lines[:30]:  # Scan first 30 lines for the prompt
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("type") != "user":
                continue
            msg = data.get("message", {})
            content = msg.get("content", "")

            if isinstance(content, list):
                # List content = real user prompt (injected wrappers are str)
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        text = c.get("text", "")
                        if text and not text.startswith("<local-command-caveat>"):
                            return text
            elif isinstance(content, str):
                # String content = usually an injected wrapper; skip known patterns
                if content and \
                   not content.startswith("<local-command-caveat>") and \
                   not content.startswith("<command-name>") and \
                   not content.startswith("<command-message>"):
                    return content
        return None
    except Exception:
        return None


def find_and_complete_agent(hook_input: dict):
    """Find the agent that completed and mark it done.

    Matching strategy:
    1. Extract prompt from transcript_path (provided by SubagentStop hook)
    2. Match against running agents by prompt content (200 then 100 char prefix)
    3. Fall back to FIFO (pop_oldest_running_id) if no match
    """
    matched_id = None
    transcript_path = hook_input.get("transcript_path")

    # Strategy 1: Match by transcript prompt
    if transcript_path:
        prompt = extract_prompt_from_transcript(transcript_path)
        if prompt:
            prompt_prefix_200 = prompt[:200].strip()
            prompt_prefix_100 = prompt[:100].strip()

            state = agent_state.load_state()
            agents = state.get("agents", {})

            # Try 200-char prefix first, then 100-char
            for prefix in [prompt_prefix_200, prompt_prefix_100]:
                if not prefix:
                    continue
                for agent_id in state.get("start_order", []):
                    if agent_id in agents and agents[agent_id].get("status") == "running":
                        stored = agents[agent_id].get("prompt", "")
                        stored_prefix = stored[:len(prefix)].strip()
                        if stored_prefix == prefix:
                            matched_id = agent_id
                            break
                if matched_id:
                    break

    # Strategy 2: FIFO fallback
    if matched_id is None:
        matched_id = agent_state.pop_oldest_running_id()

    if matched_id is None:
        return agent_state.get_running_count()

    # Store transcript_path in state before completing
    if transcript_path:
        agent_state.update_agent_field(matched_id, "transcript_path", transcript_path)

    agent_state.complete_agent(matched_id)

    ended_at = datetime.now().isoformat()

    # Enrich history with transcript data
    try:
        if transcript_path:
            from agent_web_dashboard import parse_agent_file
            parsed = parse_agent_file(transcript_path)
            agent_history.complete_agent(
                matched_id, ended_at=ended_at,
                final_tool_calls=parsed.get("tool_calls", []),
                final_messages=parsed.get("messages", []),
                transcript_path=transcript_path,
            )
        else:
            from agent_web_dashboard import parse_agent_file, find_agent_transcripts
            transcripts = find_agent_transcripts()
            agents = agent_state.get_all_agents()
            state_info = agents.get(matched_id, {})
            prompt_prefix = state_info.get("prompt", "")[:200]
            for tf in transcripts:
                parsed = parse_agent_file(tf)
                if parsed["prompt"][:200] == prompt_prefix and prompt_prefix:
                    agent_history.complete_agent(
                        matched_id, ended_at=ended_at,
                        final_tool_calls=parsed.get("tool_calls", []),
                        final_messages=parsed.get("messages", []),
                        transcript_path=tf,
                    )
                    break
            else:
                agent_history.complete_agent(matched_id, ended_at=ended_at)
    except Exception:
        agent_history.complete_agent(matched_id, ended_at=ended_at,
                                     transcript_path=transcript_path)

    return agent_state.get_running_count()


def close_dashboard():
    """Close the dashboard if running."""
    pid = agent_state.get_dashboard_pid()
    if pid:
        if terminate_process(pid):
            agent_state.set_dashboard_pid(None)
        else:
            agent_state.set_dashboard_pid(None)

def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        hook_input = {}

    # Complete the agent
    running_count = find_and_complete_agent(hook_input)

    # If no agents running, close dashboard after a short delay
    # (Dashboard will auto-close itself, but we can also signal it)
    if running_count == 0:
        # Let dashboard close itself gracefully
        pass

    sys.exit(0)

if __name__ == "__main__":
    main()
