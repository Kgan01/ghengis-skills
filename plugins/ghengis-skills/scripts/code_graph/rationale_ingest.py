"""Pipe code-graph rationale nodes into SkillMemory as searchable learnings.

Only debt markers (HACK / FIXME / XXX) are ingested by default — they signal
risk or compromise that an engineering agent should remember. TODO / NOTE /
WHY are intentional design notes; including them tends to flood skill memory.

Portable version: includes a small ``append_to_skill_memory`` helper so this
module doesn't depend on the JARVIS ``agents.skill_memory`` package.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def append_to_skill_memory(skill_memory_root: Path, agent_name: str, learnings: list[str]) -> Path:
    """Append timestamped bullets to <root>/<agent_name>/SKILL_MEMORY.md. Returns the file path."""
    agent_dir = Path(skill_memory_root) / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)
    sm = agent_dir / "SKILL_MEMORY.md"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [f"- [{ts}] {l}" for l in learnings]
    # Touch first so stat() doesn't blow up.
    if not sm.exists():
        sm.write_text("", encoding="utf-8")
    with sm.open("a", encoding="utf-8") as fh:
        if sm.stat().st_size > 0:
            fh.write("\n")
        fh.write("\n".join(lines) + "\n")
    return sm


# Default tag set — debt markers only.
DEFAULT_DEBT_TAGS: Set[str] = {"HACK", "FIXME", "XXX"}
OPTIONAL_TAGS: Set[str] = {"TODO", "NOTE", "WHY"}

STATE_FILENAME = "rationale_ingest_state.json"


def select_rationales(
    nodes: List[Dict[str, Any]],
    include_todo: bool = False,
    extra_tags: Optional[Set[str]] = None,
) -> List[Dict[str, Any]]:
    """Filter graph nodes down to debt rationale entries."""
    accepted = set(DEFAULT_DEBT_TAGS)
    if include_todo:
        accepted.add("TODO")
    if extra_tags:
        accepted.update(extra_tags)
    out: List[Dict[str, Any]] = []
    for n in nodes:
        if n.get("type") != "rationale":
            continue
        tag = (n.get("meta") or {}).get("tag", "")
        if tag in accepted:
            out.append(n)
    return out


def format_rationale_learning(node: Dict[str, Any]) -> str:
    """Render one rationale node as a single-line SkillMemory bullet."""
    meta = node.get("meta") or {}
    tag = meta.get("tag", "?")
    text = (meta.get("text") or "").strip()
    line = meta.get("line", "?")
    path = node.get("path", "?")
    return f"{tag} at {path}:{line} — {text}"


def _state_path(state_dir: Path) -> Path:
    return state_dir / STATE_FILENAME


def load_state(state_dir: Path) -> Dict[str, Any]:
    p = _state_path(state_dir)
    if not p.exists():
        return {"version": 1, "ingested_ids": []}
    try:
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            if "ingested_ids" not in data:
                data["ingested_ids"] = []
            return data
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "ingested_ids": []}


def save_state(state_dir: Path, ingested_ids: List[str]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    p = _state_path(state_dir)
    p.write_text(
        json.dumps({
            "version": 1,
            "ingested_ids": sorted(set(ingested_ids)),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }),
        encoding="utf-8",
    )


def ingest_rationales(
    graph: Dict[str, Any],
    state_dir: Path,
    include_todo: bool = False,
) -> Dict[str, Any]:
    """Compute the set of new (not-yet-ingested) learnings.

    Returns ``{"new_learnings": [str, ...], "new_ids": [str, ...],
    "already_seen": int, "candidates": int}``. The caller is responsible
    for actually writing to SkillMemory and saving state.
    """
    candidates = select_rationales(graph.get("nodes", []), include_todo=include_todo)
    state = load_state(state_dir)
    seen: Set[str] = set(state.get("ingested_ids", []))
    new_learnings: List[str] = []
    new_ids: List[str] = []
    for node in candidates:
        nid = node.get("id", "")
        if not nid or nid in seen:
            continue
        new_learnings.append(format_rationale_learning(node))
        new_ids.append(nid)
    return {
        "candidates": len(candidates),
        "already_seen": len(candidates) - len(new_learnings),
        "new_learnings": new_learnings,
        "new_ids": new_ids,
    }
