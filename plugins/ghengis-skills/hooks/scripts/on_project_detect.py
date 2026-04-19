"""Detect project context from the current working directory."""

import os
import subprocess
from pathlib import Path


def detect_project_info() -> dict:
    """Return project info dict from current working directory.

    Walks up from cwd to find .git root, captures branch and remote.
    Returns dict with: cwd, git_root, project_name, git_branch, git_remote
    """
    cwd = os.getcwd()
    git_root = _find_git_root(cwd)
    project_name = Path(git_root).name if git_root else Path(cwd).name
    git_branch = _git_cmd("rev-parse", "--abbrev-ref", "HEAD", cwd=git_root) if git_root else None
    git_remote = _git_cmd("config", "--get", "remote.origin.url", cwd=git_root) if git_root else None

    return {
        "cwd": cwd,
        "git_root": git_root or cwd,
        "project_name": project_name,
        "git_branch": git_branch,
        "git_remote": git_remote,
    }


def _find_git_root(start: str) -> str | None:
    """Walk up from start to find nearest directory containing .git."""
    current = Path(start).resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").exists():
            return str(parent)
    return None


def _git_cmd(*args, cwd: str | None = None) -> str | None:
    """Run a git command and return stripped stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, timeout=5,
            cwd=cwd,
        )
        if result.returncode == 0:
            return result.stdout.strip() or None
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None
