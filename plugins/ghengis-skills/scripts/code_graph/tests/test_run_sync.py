"""Tests for the new `sync` action in run.py — consumes .jarvis/memory-files.json.

Covers Fix #2: the registry was decorative pre-v1.18 (project-scaffold/SKILL.md
told users to write memory-files.json but no helper read it). The sync action
dispatches each entry to the right writer based on `role`.
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from typing import Dict, Any

import pytest

import run  # type: ignore  # imported via conftest sys.path injection


def _write_graph(project_root: Path, graph: Dict[str, Any]) -> None:
    jarvis = project_root / ".jarvis"
    jarvis.mkdir(parents=True, exist_ok=True)
    (jarvis / "code-graph.json").write_text(json.dumps(graph), encoding="utf-8")


def _write_registry(project_root: Path, entries: list) -> None:
    jarvis = project_root / ".jarvis"
    jarvis.mkdir(parents=True, exist_ok=True)
    (jarvis / "memory-files.json").write_text(json.dumps(entries), encoding="utf-8")


def _sample_graph() -> Dict[str, Any]:
    return {
        "version": 4,
        "project": "demo",
        "generated_at": "2026-05-20T00:00:00+00:00",
        "nodes": [
            {"id": "module:a.py:a.py", "type": "module", "path": "a.py",
             "layer": "api", "community_id": 0, "name": "a.py"},
            {"id": "module:b.py:b.py", "type": "module", "path": "b.py",
             "layer": "service", "community_id": 0, "name": "b.py"},
        ],
        "edges": [
            {"source": "module:a.py:a.py", "target": "module:b.py:b.py",
             "type": "imports"},
        ],
        "layers": {"api": ["a.py"], "service": ["b.py"]},
    }


def _run_sync(project_root: Path) -> tuple[int, dict]:
    """Call run.main(['sync', <root>]) and capture the printed JSON."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = run.main(["sync", str(project_root)])
    out = buf.getvalue().strip().splitlines()
    # Last line is the JSON status (others may be log lines if we added any).
    payload = json.loads(out[-1])
    return code, payload


def test_sync_with_valid_registry_and_graph(tmp_path: Path):
    """With a valid registry + graph, both MEMORY.md and CONTEXT.md get populated."""
    _write_graph(tmp_path, _sample_graph())
    _write_registry(tmp_path, [
        {
            "path": "MEMORY.md",
            "role": "project_dns",
            "auto_block": True,
            "append_dated": False,
        },
        {
            "path": "CONTEXT.md",
            "role": "routing",
            "auto_block": True,
            "append_dated": False,
        },
    ])
    code, payload = _run_sync(tmp_path)
    assert code == 0, payload
    assert payload["status"] == "ok"
    assert payload["files_processed"] == 2
    assert payload["files_changed"] == 2
    # Both target files exist with AUTO blocks.
    mem = (tmp_path / "MEMORY.md").read_text(encoding="utf-8")
    ctx = (tmp_path / "CONTEXT.md").read_text(encoding="utf-8")
    assert "AUTO:project-map:start" in mem
    assert "AUTO:routing-table:start" in ctx


def test_sync_with_missing_registry_returns_error(tmp_path: Path):
    """No memory-files.json → exit 1 with clean message naming the missing file."""
    # No registry file at all.
    code, payload = _run_sync(tmp_path)
    assert code == 1
    assert payload["status"] == "error"
    assert "memory-files.json" in payload["message"]
    assert "traceback" not in payload  # clean one-line, no stack


def test_sync_with_invalid_registry_json(tmp_path: Path):
    """Malformed JSON → exit 1, clean error."""
    jarvis = tmp_path / ".jarvis"
    jarvis.mkdir(parents=True)
    (jarvis / "memory-files.json").write_text("{not json,,", encoding="utf-8")
    code, payload = _run_sync(tmp_path)
    assert code == 1
    assert payload["status"] == "error"
    assert "memory-files.json" in payload["message"]


def test_sync_with_missing_graph_returns_ok_with_noops(tmp_path: Path):
    """Registry valid, no graph sidecar → exit 0, all entries report no sidecar."""
    _write_registry(tmp_path, [
        {"path": "MEMORY.md", "role": "project_dns", "auto_block": True},
        {"path": "CONTEXT.md", "role": "routing", "auto_block": True},
    ])
    code, payload = _run_sync(tmp_path)
    assert code == 0
    assert payload["status"] == "ok"
    assert payload["files_processed"] == 2
    assert payload["files_changed"] == 0
    for detail in payload["details"]:
        assert detail["wrote_changes"] is False
        assert detail.get("error") == "no sidecar"


def test_sync_skips_unknown_roles(tmp_path: Path):
    """Roles we don't yet handle are reported in details but not treated as errors."""
    _write_graph(tmp_path, _sample_graph())
    _write_registry(tmp_path, [
        {"path": "MEMORY.md", "role": "project_dns", "auto_block": True},
        {"path": "SKILL_MEMORY.md", "role": "lessons", "auto_block": False},
    ])
    code, payload = _run_sync(tmp_path)
    assert code == 0
    assert payload["files_processed"] == 2
    # MEMORY.md changed; lessons row skipped (wrote_changes=False, not an error)
    roles_seen = {d["role"] for d in payload["details"]}
    assert "project_dns" in roles_seen
    assert "lessons" in roles_seen
    lessons = next(d for d in payload["details"] if d["role"] == "lessons")
    assert lessons["wrote_changes"] is False
    # SKILL_MEMORY.md should not have been touched.
    assert not (tmp_path / "SKILL_MEMORY.md").exists()


def test_sync_registry_not_a_list_returns_error(tmp_path: Path):
    """Registry must be a JSON list at the top level — anything else is an error."""
    jarvis = tmp_path / ".jarvis"
    jarvis.mkdir(parents=True)
    (jarvis / "memory-files.json").write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    code, payload = _run_sync(tmp_path)
    assert code == 1
    assert payload["status"] == "error"
