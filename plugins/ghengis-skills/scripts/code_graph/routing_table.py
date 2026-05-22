"""Compute Van-Clief Layer-1 workspace-routing rows from code-graph communities."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

START_MARKER = "<!-- AUTO:routing-table:start -->"
END_MARKER = "<!-- AUTO:routing-table:end -->"
DEFAULT_TOP_N = 8
SAMPLE_PATHS_PER_ROW = 3


def compute_routing_rows(
    graph: Dict[str, Any],
    top_n: int = DEFAULT_TOP_N,
) -> List[Dict[str, Any]]:
    """For each top-N community by size, return ``{community_id, label,
    size, dominant_layer, sample_modules}``.

    label = basename of the highest-degree module node in the community
    (its "god node"). Communities with no module nodes are dropped.
    """
    nodes: List[Dict[str, Any]] = graph.get("nodes", [])
    edges: List[Dict[str, Any]] = graph.get("edges", [])

    # Degree per node id
    degree: Dict[str, int] = {}
    for e in edges:
        s = e.get("source", "")
        t = e.get("target", "")
        if s:
            degree[s] = degree.get(s, 0) + 1
        if t:
            degree[t] = degree.get(t, 0) + 1

    # Group nodes by community
    members: Dict[int, List[Dict[str, Any]]] = {}
    for n in nodes:
        cid = n.get("community_id")
        if cid is None:
            continue
        members.setdefault(int(cid), []).append(n)

    rows: List[Dict[str, Any]] = []
    for cid, group in members.items():
        modules = [n for n in group if n.get("type") == "module"]
        if not modules:
            continue
        # God node = highest-degree module
        modules.sort(key=lambda n: -degree.get(n.get("id", ""), 0))
        # Prefer a more descriptive label than __init__.py if possible.
        for candidate in modules:
            basename = (candidate.get("path") or "").rsplit("/", 1)[-1]
            if basename and basename != "__init__.py":
                god = candidate
                break
        else:
            god = modules[0]
        label = (god.get("path") or "?").rsplit("/", 1)[-1] or "?"
        # Dominant layer = most common layer label among modules
        layer_counts = Counter(m.get("layer", "?") for m in modules)
        dominant_layer = layer_counts.most_common(1)[0][0]
        # Sample paths (modules first, then everything else)
        sample_modules = [m.get("path", "") for m in modules[:SAMPLE_PATHS_PER_ROW]]
        rows.append({
            "community_id": cid,
            "label": label,
            "size": len(group),
            "dominant_layer": dominant_layer,
            "sample_modules": sample_modules,
        })

    rows.sort(key=lambda r: (-r["size"], r["community_id"]))
    return rows[:top_n]


def render_routing_section(rows: List[Dict[str, Any]]) -> str:
    """Render the Workspace Routing markdown section."""
    lines: List[str] = []
    lines.append("## Workspace Routing")
    lines.append("")
    lines.append(
        "Auto-derived from `.jarvis/code-graph.json` communities. "
        "Each row groups files that import each other heavily — when a task "
        "matches the label, start in those workspaces."
    )
    lines.append("")
    lines.append("| Community | Label | Size | Layer | Workspaces |")
    lines.append("|-----------|-------|-----:|-------|------------|")
    if not rows:
        lines.append("| _(empty)_ | — | 0 | — | _no communities detected_ |")
    else:
        for r in rows:
            samples = ", ".join(f"`{p}`" for p in r["sample_modules"][:SAMPLE_PATHS_PER_ROW])
            lines.append(
                f"| {r['community_id']} | `{r['label']}` | {r['size']} | "
                f"{r['dominant_layer']} | {samples} |"
            )
    lines.append("")
    return "\n".join(lines)


def update_context_md(context_path, section_md: str) -> bool:
    """Insert / replace the routing block in CONTEXT.md. Returns True if written."""
    from pathlib import Path
    p = Path(context_path)
    block = f"{START_MARKER}\n{section_md}\n{END_MARKER}\n"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(block, encoding="utf-8")
        return True
    current = p.read_text(encoding="utf-8")
    if START_MARKER in current and END_MARKER in current:
        before = current.split(START_MARKER, 1)[0]
        after = current.split(END_MARKER, 1)[1]
        new_content = before + block + after.lstrip("\n")
    else:
        sep = "\n\n" if current and not current.endswith("\n") else "\n"
        new_content = current + sep + block
    if new_content == current:
        return False
    p.write_text(new_content, encoding="utf-8")
    return True
