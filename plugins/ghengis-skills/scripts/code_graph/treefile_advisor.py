"""Suggest file-tree moves based on code-graph community structure.

Advisory only — never moves files. The output is a markdown report that a
human (or another agent under explicit instruction) can act on.

Heuristic:
  1. For each directory, find the dominant community (most-common community_id
     among module nodes in that dir).
  2. A module is "misplaced" if its community differs from its directory's
     dominant community AND the directory's dominant share is high enough
     to be meaningful (default >= 50%) AND the directory has enough modules
     to be statistically interesting (default >= 3).
  3. For each misplaced module, suggest moving it to whichever directory IS
     dominated by its community (if any).
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

DEFAULT_MIN_COHESION = 0.5
DEFAULT_MIN_DIR_SIZE = 3
SUGGESTIONS_FILENAME = "treefile-suggestions.md"


def _dirname(path: str) -> str:
    """Return the POSIX directory portion of *path*, or '' for top-level."""
    if "/" not in path:
        return ""
    return path.rsplit("/", 1)[0]


def compute_directory_cohesion(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """For every directory containing module nodes, compute its dominant
    community + the share of modules in that community.
    """
    by_dir: Dict[str, List[int]] = {}
    for n in nodes:
        if n.get("type") != "module":
            continue
        cid = n.get("community_id")
        if cid is None:
            continue
        d = _dirname(n.get("path") or "")
        by_dir.setdefault(d, []).append(int(cid))

    cohesion: Dict[str, Dict[str, Any]] = {}
    for d, cids in by_dir.items():
        counts = Counter(cids)
        dom_cid, dom_count = counts.most_common(1)[0]
        cohesion[d] = {
            "dominant": dom_cid,
            "dominant_count": dom_count,
            "size": len(cids),
            "dominant_share": dom_count / len(cids),
        }
    return cohesion


def find_misplaced_modules(
    nodes: List[Dict[str, Any]],
    min_cohesion: float = DEFAULT_MIN_COHESION,
    min_dir_size: int = DEFAULT_MIN_DIR_SIZE,
) -> List[Dict[str, Any]]:
    """Return module nodes whose community differs from their directory's
    dominant community, in directories that pass the cohesion / size gates.
    """
    cohesion = compute_directory_cohesion(nodes)
    out: List[Dict[str, Any]] = []
    for n in nodes:
        if n.get("type") != "module":
            continue
        cid = n.get("community_id")
        if cid is None:
            continue
        path = n.get("path") or ""
        d = _dirname(path)
        info = cohesion.get(d)
        if not info:
            continue
        if info["size"] < min_dir_size:
            continue
        if info["dominant_share"] < min_cohesion:
            continue
        if int(cid) == int(info["dominant"]):
            continue
        out.append({
            "path": path,
            "community_id": int(cid),
            "current_dir": d,
            "current_dir_dominant": info["dominant"],
            "current_dir_share": info["dominant_share"],
        })
    return out


def suggest_destination(
    community_id: int,
    cohesion: Dict[str, Dict[str, Any]],
    current_dir: str,
) -> Optional[str]:
    """Find the directory dominated by *community_id* (other than *current_dir*).
    Returns None if no clear home exists.
    """
    candidates: List[tuple] = []
    for d, info in cohesion.items():
        if d == current_dir:
            continue
        if int(info["dominant"]) == int(community_id):
            candidates.append((info["dominant_share"], info["size"], d))
    if not candidates:
        return None
    # Strongest match = highest dominant_share, ties broken by larger size.
    candidates.sort(key=lambda t: (-t[0], -t[1], t[2]))
    return candidates[0][2]


def build_suggestions(
    nodes: List[Dict[str, Any]],
    min_cohesion: float = DEFAULT_MIN_COHESION,
    min_dir_size: int = DEFAULT_MIN_DIR_SIZE,
) -> List[Dict[str, Any]]:
    """Top-level entry: produce final suggestion records ready to render."""
    cohesion = compute_directory_cohesion(nodes)
    misplaced = find_misplaced_modules(nodes, min_cohesion, min_dir_size)
    out: List[Dict[str, Any]] = []
    for m in misplaced:
        dest = suggest_destination(m["community_id"], cohesion, m["current_dir"])
        if not dest:
            continue  # no clear home -> don't suggest a move
        out.append({**m, "suggested_dir": dest})
    out.sort(key=lambda s: s["path"])
    return out


def render_suggestions(suggestions: List[Dict[str, Any]]) -> str:
    """Render move suggestions as markdown."""
    lines: List[str] = []
    lines.append("# Treefile Suggestions")
    lines.append("")
    lines.append(
        "Derived from `.jarvis/code-graph.json` communities. Each row "
        "lists a file whose graph community disagrees with its directory's "
        "dominant community. Advisory only — review before moving."
    )
    lines.append("")
    if not suggestions:
        lines.append("_No misplacements detected._")
        return "\n".join(lines) + "\n"
    lines.append("| File | Community | Currently in | Dir dominant | Suggested |")
    lines.append("|------|----------:|--------------|-------------:|-----------|")
    for s in suggestions:
        share_pct = int(round(s["current_dir_share"] * 100))
        lines.append(
            f"| `{s['path']}` | community {s['community_id']} | "
            f"`{s['current_dir'] or '(root)'}` | "
            f"{s['current_dir_dominant']} ({share_pct}%) | "
            f"`{s['suggested_dir']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def write_suggestions(project_root, suggestions_md: str) -> str:
    """Write the report to .jarvis/treefile-suggestions.md."""
    from pathlib import Path
    out_dir = Path(project_root) / ".jarvis"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / SUGGESTIONS_FILENAME
    out_path.write_text(suggestions_md, encoding="utf-8")
    return str(out_path)
