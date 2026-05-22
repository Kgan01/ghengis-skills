"""Tests for memory_map_writer — auto-maintained section in MEMORY.md.

Covers:
- Fix #1 — malformed marker detection (orphan start, orphan end, end-before-start, double start)
- Fix #4 — unified EMPTY_STATE_NOTE wording across empty sections
- Existing render & write behavior (sanity checks)
"""
from __future__ import annotations

from pathlib import Path

import pytest

from memory_map_writer import (
    END_MARKER,
    START_MARKER,
    EMPTY_STATE_NOTE,
    render_project_map,
    update_memory_md,
)


def _sample_graph():
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
             "type": "imports", "confidence": "EXTRACTED"},
        ],
        "layers": {"api": ["a.py"], "service": ["b.py"]},
    }


def _empty_graph():
    return {
        "version": 4,
        "project": "empty",
        "generated_at": "2026-05-20T00:00:00+00:00",
        "nodes": [],
        "edges": [],
        "layers": {},
    }


# ---- Existing behavior ----

def test_update_memory_md_creates_file_when_missing(tmp_path: Path):
    mem = tmp_path / "MEMORY.md"
    md = render_project_map(_sample_graph())
    assert update_memory_md(mem, md) is True
    text = mem.read_text(encoding="utf-8")
    assert START_MARKER in text
    assert END_MARKER in text


def test_update_memory_md_replaces_existing_block(tmp_path: Path):
    mem = tmp_path / "MEMORY.md"
    mem.write_text(
        f"# Header\n\n{START_MARKER}\nold content\n{END_MARKER}\n\n## Tail\n",
        encoding="utf-8",
    )
    md = render_project_map(_sample_graph())
    wrote = update_memory_md(mem, md)
    assert wrote is True
    text = mem.read_text(encoding="utf-8")
    assert "old content" not in text
    assert "# Header" in text
    assert "## Tail" in text
    # Exactly one start and one end marker.
    assert text.count(START_MARKER) == 1
    assert text.count(END_MARKER) == 1


def test_update_memory_md_appends_when_neither_marker_present(tmp_path: Path):
    mem = tmp_path / "MEMORY.md"
    mem.write_text("# Just a header\n", encoding="utf-8")
    md = render_project_map(_sample_graph())
    assert update_memory_md(mem, md) is True
    text = mem.read_text(encoding="utf-8")
    assert "# Just a header" in text
    assert START_MARKER in text


# ---- Fix #1: malformed marker handling ----

def test_malformed_orphan_start_marker_raises(tmp_path: Path):
    mem = tmp_path / "MEMORY.md"
    mem.write_text(
        f"# Doc\n\n{START_MARKER}\nsome dangling content\n",
        encoding="utf-8",
    )
    md = render_project_map(_sample_graph())
    with pytest.raises(ValueError, match="Malformed"):
        update_memory_md(mem, md)


def test_malformed_orphan_end_marker_raises(tmp_path: Path):
    mem = tmp_path / "MEMORY.md"
    mem.write_text(
        f"# Doc\n\nsome content\n{END_MARKER}\n",
        encoding="utf-8",
    )
    md = render_project_map(_sample_graph())
    with pytest.raises(ValueError, match="Malformed"):
        update_memory_md(mem, md)


def test_malformed_end_before_start_raises(tmp_path: Path):
    mem = tmp_path / "MEMORY.md"
    mem.write_text(
        f"# Doc\n\n{END_MARKER}\nstuff\n{START_MARKER}\n",
        encoding="utf-8",
    )
    md = render_project_map(_sample_graph())
    with pytest.raises(ValueError, match="Malformed"):
        update_memory_md(mem, md)


def test_malformed_two_start_markers_raises(tmp_path: Path):
    mem = tmp_path / "MEMORY.md"
    mem.write_text(
        f"# Doc\n\n{START_MARKER}\nfirst\n{START_MARKER}\nsecond\n",
        encoding="utf-8",
    )
    md = render_project_map(_sample_graph())
    with pytest.raises(ValueError, match="Malformed"):
        update_memory_md(mem, md)


def test_malformed_error_message_names_file(tmp_path: Path):
    mem = tmp_path / "MEMORY.md"
    mem.write_text(f"{START_MARKER}\nno end\n", encoding="utf-8")
    md = render_project_map(_sample_graph())
    with pytest.raises(ValueError) as exc_info:
        update_memory_md(mem, md)
    msg = str(exc_info.value)
    assert "MEMORY.md" in msg
    assert "Refusing to write" in msg


# ---- Fix #4: unified empty-state wording ----

def test_render_uses_unified_empty_state_marker():
    """All three empty sections must use the same EMPTY_STATE_NOTE constant."""
    md = render_project_map(_empty_graph())
    # Top modules section must have it
    assert "### Top Modules" in md
    # Communities section must have it
    assert "### Communities" in md
    # Layers section must have it
    assert "### Layers" in md
    # All three sections produce the unified note.
    occurrences = md.count(EMPTY_STATE_NOTE)
    assert occurrences >= 3, (
        f"Expected unified empty marker {EMPTY_STATE_NOTE!r} in all 3 sections, "
        f"got {occurrences} occurrences. Render output:\n{md}"
    )


def test_empty_state_note_constant_is_defined():
    """The constant must be present at module scope."""
    assert isinstance(EMPTY_STATE_NOTE, str)
    assert EMPTY_STATE_NOTE.strip()  # non-empty
