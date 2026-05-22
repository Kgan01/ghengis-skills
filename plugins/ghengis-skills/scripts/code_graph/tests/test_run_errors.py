"""Tests for run.py error UX (Fix #3) — clean one-line JSON errors,
no traceback dumps in user-visible output.
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

import run  # type: ignore


def _capture(*argv: str) -> tuple[int, dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run.main(list(argv))
    out = buf.getvalue().strip().splitlines()
    payload = json.loads(out[-1])
    return code, payload


def test_readonly_file_emits_clean_error(tmp_path: Path):
    """Pointing memory_map at a directory triggers IsADirectoryError, which
    must surface as a clean one-line JSON error (no traceback, message short).
    """
    # Set up a valid graph so we get past the load step.
    jarvis = tmp_path / ".jarvis"
    jarvis.mkdir()
    (jarvis / "code-graph.json").write_text(json.dumps({
        "version": 4, "project": "x", "nodes": [], "edges": [], "layers": {},
    }), encoding="utf-8")
    # Use a directory as the memory_path target — open(<dir>, 'w') raises
    # IsADirectoryError on POSIX. On Windows it raises PermissionError. Both
    # are caught explicitly in our handler.
    target_dir = tmp_path / "actually_a_dir"
    target_dir.mkdir()
    code, payload = _capture("memory_map", str(tmp_path), str(target_dir))
    assert code == 1
    assert payload["status"] == "error"
    assert "traceback" not in payload  # one-line, no stack
    # The message should be short and human-readable.
    assert len(payload["message"]) < 200
    # Should NOT contain Python frame markers.
    assert "Traceback" not in payload["message"]
    assert ".py\"" not in payload["message"]


def test_missing_graph_emits_clean_error(tmp_path: Path):
    """FileNotFoundError (no .jarvis/code-graph.json) → clean message."""
    mem = tmp_path / "MEMORY.md"
    code, payload = _capture("memory_map", str(tmp_path), str(mem))
    assert code == 1
    assert payload["status"] == "error"
    assert "code-graph" in payload["message"]
    assert "traceback" not in payload


def test_invalid_graph_json_emits_clean_error(tmp_path: Path):
    """Malformed sidecar JSON → JSONDecodeError → clean message."""
    jarvis = tmp_path / ".jarvis"
    jarvis.mkdir()
    (jarvis / "code-graph.json").write_text("{not valid json", encoding="utf-8")
    mem = tmp_path / "MEMORY.md"
    code, payload = _capture("memory_map", str(tmp_path), str(mem))
    assert code == 1
    assert payload["status"] == "error"
    assert "Invalid JSON" in payload["message"]
    assert "traceback" not in payload


def test_malformed_markers_emit_clean_error(tmp_path: Path):
    """ValueError from malformed markers (Fix #1) → clean message via top-level handler."""
    jarvis = tmp_path / ".jarvis"
    jarvis.mkdir()
    (jarvis / "code-graph.json").write_text(json.dumps({
        "version": 4, "project": "x", "nodes": [], "edges": [], "layers": {},
    }), encoding="utf-8")
    # Pre-corrupt MEMORY.md with an orphan start marker.
    mem = tmp_path / "MEMORY.md"
    mem.write_text(
        "# Doc\n\n<!-- AUTO:project-map:start -->\ndangling\n",
        encoding="utf-8",
    )
    code, payload = _capture("memory_map", str(tmp_path), str(mem))
    assert code == 1
    assert payload["status"] == "error"
    assert "Malformed" in payload["message"]
    assert "traceback" not in payload
