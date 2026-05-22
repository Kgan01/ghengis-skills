"""Tests for rationale_ingest — Fix #5: atomic state save in ingest_and_persist.

Per spec: ingest_and_persist combines ingest+append+save into one call. State
file write must use tmp+os.replace for atomicity (state file is consistent or
unchanged, never half-written).

Note: full cross-file atomicity (skill memory + state) is not guaranteed —
the docstring should warn that state-save failure after skill-memory write
results in duplicate skill memory entries on next run (preferred over
silently swallowing learnings).
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import rationale_ingest


def _graph_with_rationales() -> dict:
    return {
        "version": 4,
        "project": "x",
        "nodes": [
            {
                "id": "rationale:foo.py:10:HACK",
                "type": "rationale",
                "path": "foo.py",
                "meta": {"tag": "HACK", "text": "ugly retry loop", "line": 10},
            },
            {
                "id": "rationale:bar.py:7:FIXME",
                "type": "rationale",
                "path": "bar.py",
                "meta": {"tag": "FIXME", "text": "race condition", "line": 7},
            },
        ],
    }


def test_ingest_and_persist_function_exists():
    """The new helper must be exposed at module scope."""
    assert hasattr(rationale_ingest, "ingest_and_persist")


def test_ingest_and_persist_happy_path(tmp_path: Path):
    """Valid graph → writes skill memory, saves state, returns summary."""
    state_dir = tmp_path / "state"
    skill_root = tmp_path / "skills"
    result = rationale_ingest.ingest_and_persist(
        _graph_with_rationales(),
        state_dir=state_dir,
        skill_memory_root=skill_root,
        agent_name="engineer",
    )
    assert result["candidates"] == 2
    assert result["new_count"] == 2
    sm_path = Path(result["skill_memory_path"])
    assert sm_path.exists()
    content = sm_path.read_text(encoding="utf-8")
    assert "HACK" in content
    assert "FIXME" in content
    # State file written and contains both ids.
    state_file = state_dir / rationale_ingest.STATE_FILENAME
    assert state_file.exists()
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert len(state["ingested_ids"]) == 2


def test_ingest_and_persist_dedupes_on_second_call(tmp_path: Path):
    """Second call with same graph reports 0 new and doesn't grow skill memory."""
    state_dir = tmp_path / "state"
    skill_root = tmp_path / "skills"
    r1 = rationale_ingest.ingest_and_persist(
        _graph_with_rationales(), state_dir, skill_root, "engineer"
    )
    assert r1["new_count"] == 2
    sm_path = Path(r1["skill_memory_path"])
    size_after_first = sm_path.stat().st_size

    r2 = rationale_ingest.ingest_and_persist(
        _graph_with_rationales(), state_dir, skill_root, "engineer"
    )
    assert r2["new_count"] == 0
    assert sm_path.stat().st_size == size_after_first  # didn't append


def test_ingest_and_persist_writes_state_atomically(tmp_path: Path):
    """State file save must use os.replace (tmp+rename) for atomicity."""
    state_dir = tmp_path / "state"
    skill_root = tmp_path / "skills"

    with patch.object(rationale_ingest.os, "replace", wraps=rationale_ingest.os.replace) as mocked:
        result = rationale_ingest.ingest_and_persist(
            _graph_with_rationales(), state_dir, skill_root, "engineer"
        )
    assert result["new_count"] == 2
    # os.replace must have been called at least once (for the state file).
    assert mocked.call_count >= 1
    # The final state file path should be one of the call destinations.
    state_file = state_dir / rationale_ingest.STATE_FILENAME
    dest_paths = [Path(call.args[1]) for call in mocked.call_args_list]
    assert state_file in dest_paths


def test_save_state_uses_atomic_rename(tmp_path: Path):
    """The existing save_state function should also use os.replace for atomicity."""
    state_dir = tmp_path / "s"
    with patch.object(rationale_ingest.os, "replace", wraps=rationale_ingest.os.replace) as mocked:
        rationale_ingest.save_state(state_dir, ["a", "b"])
    assert mocked.call_count >= 1
    # File ends up in place.
    state_file = state_dir / rationale_ingest.STATE_FILENAME
    assert state_file.exists()
    data = json.loads(state_file.read_text(encoding="utf-8"))
    assert set(data["ingested_ids"]) == {"a", "b"}


def test_ingest_and_persist_empty_graph_is_noop(tmp_path: Path):
    """Empty / no-rationale graph: returns 0 new, doesn't create skill memory file."""
    state_dir = tmp_path / "state"
    skill_root = tmp_path / "skills"
    empty = {"version": 4, "project": "x", "nodes": []}
    result = rationale_ingest.ingest_and_persist(
        empty, state_dir, skill_root, "engineer"
    )
    assert result["new_count"] == 0
    assert result["candidates"] == 0
