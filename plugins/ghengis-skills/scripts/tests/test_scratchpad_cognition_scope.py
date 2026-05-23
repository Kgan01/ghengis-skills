"""Tests for v1.19.0 per-project cognition scope feature.

Covers:
- `_resolve_cognition_path(scope)` — explicit scope > env var > default 'project'
- `cognition-emit --scope` — writes land in the right file
- `retrieve --scope merged` — searches both stores, dedupes, project boost
- `cognition-promote <entry_id>` — moves entry from project to global with audit trail
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import scratchpad  # type: ignore  # imported via conftest sys.path injection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    """Build a sandbox with separate project + home dirs.

    Returns a dict with the project root, fake home, and resolved paths.
    Patches scratchpad's project-root resolver and Path.home() to keep tests
    away from the real ~/.claude/ directory.
    """
    project_root = tmp_path / "project"
    (project_root / ".claude" / "ghengis-chain").mkdir(parents=True)
    fake_home = tmp_path / "home"
    (fake_home / ".claude").mkdir(parents=True)

    # Make the scratchpad module think this is the project root.
    monkeypatch.setattr(scratchpad, "resolve_project_root", lambda: project_root)
    # Redirect Path.home() to our fake home so global writes stay sandboxed.
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    # Drop env vars from the host shell so the tests see a clean slate.
    monkeypatch.delenv("GHENGIS_COGNITION_SCOPE", raising=False)
    monkeypatch.delenv("GHENGIS_COGNITION", raising=False)
    monkeypatch.delenv("GHENGIS_CHAIN_PROJECT_ROOT", raising=False)

    return {
        "project_root": project_root,
        "home": fake_home,
        "project_cognition": project_root / ".claude" / "cognition.jsonl",
        "global_cognition": fake_home / ".claude" / "cognition.jsonl",
    }


def _make_entry(entry_id: str, applies_when: str, **overrides) -> dict:
    base = {
        "id": entry_id,
        "created_at": "2026-05-20T00:00:00+00:00",
        "chain": "build-validate",
        "outcome": "shipped",
        "final_score": 9,
        "fitness": 0.9,
        "lesson": f"lesson for {entry_id}",
        "causal_factor": "test factor",
        "applies_when": applies_when,
        "started_at": "2026-05-20T00:00:00+00:00",
        "completed_at": "2026-05-20T00:00:00+00:00",
        "iterations_used": 1,
        "hits": 0,
        "wins": 0,
        "audit_status": "unchecked",
    }
    base.update(overrides)
    return base


def _seed(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


def test_resolve_path_defaults_to_project(isolated_env):
    p = scratchpad._resolve_cognition_path()
    assert p == isolated_env["project_cognition"]


def test_resolve_path_respects_env_var(isolated_env, monkeypatch):
    monkeypatch.setenv("GHENGIS_COGNITION_SCOPE", "global")
    p = scratchpad._resolve_cognition_path()
    assert p == isolated_env["global_cognition"]


def test_resolve_path_explicit_scope_overrides_env(isolated_env, monkeypatch):
    monkeypatch.setenv("GHENGIS_COGNITION_SCOPE", "global")
    p = scratchpad._resolve_cognition_path(scope="project")
    assert p == isolated_env["project_cognition"]


def test_resolve_path_rejects_invalid_scope(isolated_env):
    with pytest.raises(ValueError):
        scratchpad._resolve_cognition_path(scope="bogus")


def test_resolve_path_creates_parent_dir(isolated_env, tmp_path):
    # Clear out the pre-created .claude dir to confirm the function creates it.
    project_root = tmp_path / "fresh_project"
    project_root.mkdir()
    import scratchpad as sp
    # Re-bind the resolver for this test only.
    original = sp.resolve_project_root
    sp.resolve_project_root = lambda: project_root
    try:
        p = sp._resolve_cognition_path(scope="project")
        assert p.parent.is_dir()
        assert not p.exists()  # path returned but file NOT created
    finally:
        sp.resolve_project_root = original


# ---------------------------------------------------------------------------
# emit_cognition_entry with scope
# ---------------------------------------------------------------------------


def test_emit_writes_to_project_by_default(isolated_env):
    state = {
        "chain": "build-validate",
        "started_at": "2026-05-20T00:00:00+00:00",
        "completed_at": "2026-05-20T00:01:00+00:00",
        "report": {"outcome": "shipped", "score_progression": [9]},
        "input": {"user_request": "ship it"},
    }
    entry = scratchpad.emit_cognition_entry(state)
    assert isolated_env["project_cognition"].exists()
    assert not isolated_env["global_cognition"].exists()
    body = isolated_env["project_cognition"].read_text(encoding="utf-8")
    assert entry["id"] in body


def test_emit_with_scope_global_writes_to_global(isolated_env):
    state = {
        "chain": "build-validate",
        "started_at": "2026-05-20T00:00:00+00:00",
        "completed_at": "2026-05-20T00:01:00+00:00",
        "report": {"outcome": "shipped", "score_progression": [9]},
        "input": {"user_request": "ship it"},
    }
    entry = scratchpad.emit_cognition_entry(state, scope="global")
    assert isolated_env["global_cognition"].exists()
    assert not isolated_env["project_cognition"].exists()
    body = isolated_env["global_cognition"].read_text(encoding="utf-8")
    assert entry["id"] in body


# ---------------------------------------------------------------------------
# retrieve_lessons (tiered + boost)
# ---------------------------------------------------------------------------


def test_retrieve_merges_project_and_global(isolated_env):
    # Project has 2 lessons about banking, global has 2 lessons about banking.
    _seed(
        isolated_env["project_cognition"],
        [
            _make_entry("proj_a", "banking amount validation decimal"),
            _make_entry("proj_b", "banking transfer limit verification"),
        ],
    )
    _seed(
        isolated_env["global_cognition"],
        [
            _make_entry("glob_a", "banking amount precision rounding"),
            _make_entry("glob_b", "banking webhook signature verification"),
        ],
    )

    lessons = scratchpad.retrieve_lessons(
        "banking amount validation", top_k=5, scope="merged"
    )
    ids = {l["id"] for l in lessons}
    assert "proj_a" in ids
    # Should pull from both stores since project alone had < 5 hits.
    assert any(i.startswith("glob_") for i in ids)
    # Each entry should be annotated with its origin scope.
    for l in lessons:
        assert l.get("_origin_scope") in ("project", "global")


def test_retrieve_project_boost(isolated_env):
    # Two entries with identical applies_when text — project entry should rank first.
    text = "deploy server validate health check"
    _seed(isolated_env["project_cognition"], [_make_entry("proj_x", text)])
    _seed(isolated_env["global_cognition"], [_make_entry("glob_x", text)])

    lessons = scratchpad.retrieve_lessons(text, top_k=5, scope="merged")
    assert len(lessons) == 2
    assert lessons[0]["id"] == "proj_x"
    assert lessons[0]["_origin_scope"] == "project"


def test_retrieve_project_only_does_not_search_global(isolated_env):
    _seed(isolated_env["project_cognition"], [_make_entry("proj_a", "banking validation")])
    _seed(isolated_env["global_cognition"], [_make_entry("glob_a", "banking validation")])

    lessons = scratchpad.retrieve_lessons("banking validation", top_k=5, scope="project")
    ids = {l["id"] for l in lessons}
    assert "proj_a" in ids
    assert "glob_a" not in ids


# ---------------------------------------------------------------------------
# cognition-promote
# ---------------------------------------------------------------------------


def test_promote_moves_entry_to_global(isolated_env):
    entry = _make_entry("promote_me", "general api retry policy")
    _seed(isolated_env["project_cognition"], [entry])

    rc = scratchpad.cmd_cognition_promote(["promote_me"])
    assert rc == 0

    # Global file should have the entry.
    global_lines = [
        json.loads(l)
        for l in isolated_env["global_cognition"].read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    assert len(global_lines) == 1
    promoted = global_lines[0]
    assert promoted["id"] == "promote_me"
    assert "promoted_from_project" in promoted
    assert "promoted_at" in promoted

    # Project entry should be marked as promoted.
    project_lines = [
        json.loads(l)
        for l in isolated_env["project_cognition"].read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    assert project_lines[0]["promoted_to_global"] is True


def test_promote_errors_if_already_promoted(isolated_env):
    entry = _make_entry("already", "foo bar")
    entry["promoted_to_global"] = True
    _seed(isolated_env["project_cognition"], [entry])

    rc = scratchpad.cmd_cognition_promote(["already"])
    assert rc != 0


def test_promote_errors_if_entry_not_found(isolated_env):
    _seed(isolated_env["project_cognition"], [_make_entry("real_id", "foo")])
    rc = scratchpad.cmd_cognition_promote(["bogus_id"])
    assert rc != 0


# ---------------------------------------------------------------------------
# Backward compat: GHENGIS_COGNITION env still gates the loop
# ---------------------------------------------------------------------------


def test_existing_cognition_enable_flag_still_works(isolated_env, monkeypatch):
    """The _enabled check is separate from the _scope check — make sure
    GHENGIS_COGNITION=true still gates the auto-retrieval-on-init code path.
    """
    monkeypatch.setenv("GHENGIS_COGNITION", "true")
    # Seed a project cognition entry so init has something to retrieve.
    _seed(
        isolated_env["project_cognition"],
        [_make_entry("seed1", "ship a new endpoint")],
    )
    rc = scratchpad.cmd_init(
        ["test-chain", "--input-json", json.dumps({"user_request": "ship a new endpoint"})]
    )
    assert rc == 0
    # init should have surfaced the seeded entry.
    state = scratchpad.load()
    lessons = state.get("lessons_from_past", [])
    assert any(l.get("id") == "seed1" for l in lessons)
