"""Render the auto-managed Project Map section for MEMORY.md from a code graph.

The output sits between HTML-comment markers so MEMORY.md can mix hand-written
prose with this auto-generated block. The writer is idempotent: running it
twice on the same graph produces the same output.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

START_MARKER = "<!-- AUTO:project-map:start -->"
END_MARKER = "<!-- AUTO:project-map:end -->"
TOP_MODULES = 5
TOP_COMMUNITIES = 5


def render_project_map(graph: Dict[str, Any]) -> str:
    """Render the Project Map markdown section from a parsed code-graph dict."""
    nodes: List[Dict[str, Any]] = graph.get("nodes", [])
    edges: List[Dict[str, Any]] = graph.get("edges", [])
    layers: Dict[str, List[str]] = graph.get("layers", {})
    project = graph.get("project", "(unknown)")
    generated_at = graph.get("generated_at", "")

    # Module degree counts (in + out)
    degree: Dict[str, int] = {}
    for e in edges:
        s = e.get("source", "")
        t = e.get("target", "")
        if s.startswith("module:"):
            degree[s] = degree.get(s, 0) + 1
        if t.startswith("module:"):
            degree[t] = degree.get(t, 0) + 1

    id_to_node = {n["id"]: n for n in nodes if "id" in n}
    top_modules = sorted(
        (
            {
                "path": id_to_node.get(nid, {}).get("path", nid),
                "layer": id_to_node.get(nid, {}).get("layer", "?"),
                "community": id_to_node.get(nid, {}).get("community_id", -1),
                "degree": deg,
            }
            for nid, deg in degree.items()
        ),
        key=lambda x: -x["degree"],
    )[:TOP_MODULES]

    # Community sizing
    community_sizes: Dict[int, int] = {}
    community_sample: Dict[int, List[str]] = {}
    for n in nodes:
        cid = n.get("community_id")
        if cid is None:
            continue
        community_sizes[cid] = community_sizes.get(cid, 0) + 1
        if n.get("type") == "module":
            community_sample.setdefault(cid, []).append(n.get("path", ""))
    top_communities = sorted(
        community_sizes.items(),
        key=lambda kv: -kv[1],
    )[:TOP_COMMUNITIES]

    # Node-type counts
    node_type_counts: Dict[str, int] = {}
    for n in nodes:
        t = n.get("type", "?")
        node_type_counts[t] = node_type_counts.get(t, 0) + 1

    lines: List[str] = []
    lines.append("## Project Map")
    lines.append("")
    lines.append(f"**Project**: `{project}` · **Generated**: {generated_at}")
    lines.append(
        f"**Nodes**: {len(nodes)} · **Edges**: {len(edges)} · "
        f"**Communities**: {len(community_sizes)}"
    )
    lines.append("")

    lines.append(f"### Top Modules (top {TOP_MODULES} by total degree)")
    lines.append("")
    if top_modules:
        for i, m in enumerate(top_modules, start=1):
            lines.append(
                f"{i}. `{m['path']}` *(layer: {m['layer']}, "
                f"community: {m['community']}, degree: {m['degree']})*"
            )
    else:
        lines.append("_No module edges yet._")
    lines.append("")

    lines.append("### Layers")
    lines.append("")
    for layer_name in sorted(layers.keys()):
        members = layers.get(layer_name) or []
        count = len(members) if isinstance(members, list) else int(members)
        lines.append(f"- **{layer_name}**: {count}")
    lines.append("")

    lines.append("### Communities (top by size)")
    lines.append("")
    if top_communities:
        for cid, size in top_communities:
            samples = community_sample.get(cid, [])[:3]
            sample_txt = ", ".join(f"`{s}`" for s in samples) if samples else "_(no module samples)_"
            lines.append(f"- **#{cid}** ({size} nodes) — {sample_txt}")
    else:
        lines.append("_No communities detected._")
    lines.append("")
    return "\n".join(lines)


def update_memory_md(memory_path: Path, project_map_md: str) -> bool:
    """Insert or replace the project-map block in *memory_path*.

    Returns True if the file was written, False if no change needed.
    Creates the file if it doesn't exist.
    """
    block = f"{START_MARKER}\n{project_map_md}\n{END_MARKER}\n"
    if not memory_path.exists():
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text(block, encoding="utf-8")
        return True
    current = memory_path.read_text(encoding="utf-8")
    if START_MARKER in current and END_MARKER in current:
        before = current.split(START_MARKER, 1)[0]
        after = current.split(END_MARKER, 1)[1]
        new_content = before + block + after.lstrip("\n")
    else:
        sep = "\n\n" if current and not current.endswith("\n") else "\n"
        new_content = current + sep + block
    if new_content == current:
        return False
    memory_path.write_text(new_content, encoding="utf-8")
    return True


def update_from_graph_file(memory_path: Path, graph_json_path: Path) -> bool:
    """Convenience: load graph json, render map, update memory.md. Returns True if written."""
    with open(graph_json_path, "r", encoding="utf-8") as fh:
        graph = json.load(fh)
    md = render_project_map(graph)
    return update_memory_md(memory_path, md)
