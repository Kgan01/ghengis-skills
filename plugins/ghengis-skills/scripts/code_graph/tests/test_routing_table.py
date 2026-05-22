"""Tests for routing_table — malformed marker handling for update_context_md."""
from __future__ import annotations

from pathlib import Path

import pytest

from routing_table import (
    END_MARKER,
    START_MARKER,
    compute_routing_rows,
    render_routing_section,
    update_context_md,
)


def _sample_graph():
    return {
        "version": 4,
        "project": "demo",
        "nodes": [
            {"id": "module:a.py:a.py", "type": "module", "path": "a.py",
             "layer": "api", "community_id": 0},
            {"id": "module:b.py:b.py", "type": "module", "path": "b.py",
             "layer": "api", "community_id": 0},
        ],
        "edges": [
            {"source": "module:a.py:a.py", "target": "module:b.py:b.py",
             "type": "imports"},
        ],
    }


def _rendered_section():
    g = _sample_graph()
    rows = compute_routing_rows(g)
    return render_routing_section(rows)


# ---- Existing behavior ----

def test_update_context_md_creates_file_when_missing(tmp_path: Path):
    ctx = tmp_path / "CONTEXT.md"
    section = _rendered_section()
    assert update_context_md(ctx, section) is True
    text = ctx.read_text(encoding="utf-8")
    assert START_MARKER in text
    assert END_MARKER in text


def test_update_context_md_replaces_existing_block(tmp_path: Path):
    ctx = tmp_path / "CONTEXT.md"
    ctx.write_text(
        f"# Header\n\n{START_MARKER}\nold\n{END_MARKER}\n\n## Tail\n",
        encoding="utf-8",
    )
    section = _rendered_section()
    assert update_context_md(ctx, section) is True
    text = ctx.read_text(encoding="utf-8")
    assert "old" not in text
    assert text.count(START_MARKER) == 1
    assert text.count(END_MARKER) == 1


# ---- Fix #1: malformed marker handling (mirror tests from memory_map_writer) ----

def test_malformed_orphan_start_marker_raises(tmp_path: Path):
    ctx = tmp_path / "CONTEXT.md"
    ctx.write_text(f"# Doc\n\n{START_MARKER}\ndangling\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed"):
        update_context_md(ctx, _rendered_section())


def test_malformed_orphan_end_marker_raises(tmp_path: Path):
    ctx = tmp_path / "CONTEXT.md"
    ctx.write_text(f"# Doc\n\nstuff\n{END_MARKER}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed"):
        update_context_md(ctx, _rendered_section())


def test_malformed_end_before_start_raises(tmp_path: Path):
    ctx = tmp_path / "CONTEXT.md"
    ctx.write_text(
        f"# Doc\n\n{END_MARKER}\nstuff\n{START_MARKER}\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Malformed"):
        update_context_md(ctx, _rendered_section())


def test_malformed_two_start_markers_raises(tmp_path: Path):
    ctx = tmp_path / "CONTEXT.md"
    ctx.write_text(
        f"# Doc\n\n{START_MARKER}\nfirst\n{START_MARKER}\nsecond\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Malformed"):
        update_context_md(ctx, _rendered_section())


def test_malformed_error_message_names_file(tmp_path: Path):
    ctx = tmp_path / "CONTEXT.md"
    ctx.write_text(f"{START_MARKER}\nno end\n", encoding="utf-8")
    with pytest.raises(ValueError) as exc_info:
        update_context_md(ctx, _rendered_section())
    msg = str(exc_info.value)
    assert "CONTEXT.md" in msg
    assert "Refusing to write" in msg
