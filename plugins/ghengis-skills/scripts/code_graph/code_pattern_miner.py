"""Mine cross-project structural patterns from registered code graphs.

Reads each project's sidecar (via the global registry at
~/.jarvis/code-graph/global.json) and computes per-canonical-pattern
summaries — where do auth files live? do services cluster cohesively?

Pure structural mining: no LLM, no embeddings. The output is consumed
by JARVIS's agent-identity layer so cross-project habits surface in new
projects.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Canonical name patterns. Order matters: FIRST MATCH WINS.
# Each pattern matches against the POSIX module path (case-insensitive).
#
# Consequence: files in `tests/` will classify as `test_files` even if their
# basename matches another pattern (e.g. `tests/auth_helpers.py` → test_files,
# not auth_files). This is intentional — test files form their own coherent
# pattern across projects and shouldn't be split across auth/route/etc groups.
PATTERNS: List[tuple] = [
    # (group_name, regex)
    ("test_files",    re.compile(r"(^|/)tests?(/|_)|(^|/)test_[^/]+\.py$|(^|/)[^/]+_test\.py$", re.IGNORECASE)),
    ("auth_files",    re.compile(r"(^|/|_)(auth|oauth|login|session)([._/]|$)", re.IGNORECASE)),
    ("route_files",   re.compile(r"(^|/|_)(routes?|router)([._/]|$)", re.IGNORECASE)),
    ("service_files", re.compile(r"(^|/|_)(services?|svc)([._/]|$)", re.IGNORECASE)),
    ("model_files",   re.compile(r"(^|/|_)(models?|schema)([._/]|$)", re.IGNORECASE)),
    ("db_files",      re.compile(r"(^|/|_)(db|database|postgres|sqlite|redis|mongo)([._/]|$)", re.IGNORECASE)),
]

PATTERNS_FILENAME = "code_patterns.json"
AGENT_IDENTITY_DIR = "agent_identity"
EXEMPLARS_PER_PATTERN = 8


def classify_module(path: str) -> Optional[str]:
    """Return the first canonical pattern *path* matches, or None."""
    if not path:
        return None
    for group, pattern in PATTERNS:
        if pattern.search(path):
            return group
    return None


def analyze_project(graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Compute per-pattern summaries for one project's graph.

    Returns ``{pattern_name: {count, modal_layer, communities, avg_degree, exemplars}}``.
    """
    nodes: List[Dict[str, Any]] = graph.get("nodes", [])
    edges: List[Dict[str, Any]] = graph.get("edges", [])

    # Degree counts per node id.
    degree: Dict[str, int] = {}
    for e in edges:
        s = e.get("source", "")
        t = e.get("target", "")
        if s:
            degree[s] = degree.get(s, 0) + 1
        if t:
            degree[t] = degree.get(t, 0) + 1

    by_group: Dict[str, List[Dict[str, Any]]] = {}
    for n in nodes:
        if n.get("type") != "module":
            continue
        path = n.get("path", "")
        group = classify_module(path)
        if group is None:
            continue
        by_group.setdefault(group, []).append({
            "path": path,
            "layer": n.get("layer", "?"),
            "community_id": n.get("community_id"),
            "degree": degree.get(n.get("id", ""), 0),
        })

    summary: Dict[str, Dict[str, Any]] = {}
    for group, members in by_group.items():
        layers = [m["layer"] for m in members]
        comms = [m["community_id"] for m in members if m["community_id"] is not None]
        degrees = [m["degree"] for m in members]
        modal_layer = Counter(layers).most_common(1)[0][0] if layers else "?"
        summary[group] = {
            "count": len(members),
            "modal_layer": modal_layer,
            "communities": comms,
            "avg_degree": (sum(degrees) / len(degrees)) if degrees else 0.0,
            "exemplars": sorted({m["path"] for m in members})[:EXEMPLARS_PER_PATTERN],
        }
    return summary


def aggregate_patterns(
    per_project: Dict[str, Dict[str, Dict[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    """Roll per-project summaries up into one cross-project view per pattern."""
    all_groups: Set[str] = set()
    for ps in per_project.values():
        all_groups.update(ps.keys())

    out: Dict[str, Dict[str, Any]] = {}
    for group in all_groups:
        projects_with = 0
        all_layers: List[str] = []
        all_communities: List[int] = []
        all_degrees: List[float] = []
        all_exemplars: List[str] = []
        total_count = 0
        for proj_summary in per_project.values():
            ps = proj_summary.get(group)
            if not ps:
                continue
            projects_with += 1
            total_count += ps.get("count", 0)
            all_layers.append(ps.get("modal_layer", "?"))
            all_communities.extend(ps.get("communities", []))
            all_degrees.append(ps.get("avg_degree", 0.0))
            all_exemplars.extend(ps.get("exemplars", []))
        modal_layer = Counter(all_layers).most_common(1)[0][0] if all_layers else "?"
        # High cohesion = the modules in this pattern across projects landed in
        # a small number of communities relative to count.
        unique_comms = len(set(all_communities))
        high_cohesion = (
            unique_comms > 0
            and unique_comms <= max(2, total_count // 3)
        )
        out[group] = {
            "projects_with": projects_with,
            "total_modules": total_count,
            "modal_layer": modal_layer,
            "avg_degree": (sum(all_degrees) / len(all_degrees)) if all_degrees else 0.0,
            "high_cohesion": high_cohesion,
            "exemplars": sorted(set(all_exemplars))[:EXEMPLARS_PER_PATTERN],
        }
    return out


def mine_global_registry(registry: Dict[str, Any]) -> Dict[str, Any]:
    """Walk every registered project, run analyze_project, aggregate.

    Returns:
        {
            "version": 1,
            "generated_at": "...",
            "projects_analyzed": int,
            "patterns": {group_name: aggregated_summary, ...},
            "note": "..." (only if signal is too thin to act on)
        }

    Signal-thinness guard: with < 2 projects, the per-project modal_layer
    trivially equals each project's own dominant layer, so cross-project
    "patterns" are descriptive of a single project, not predictive. We still
    return the aggregated data so consumers can inspect it, but include a
    `note` field they can check before acting on the patterns.
    """
    per_project: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for slug, entry in registry.get("projects", {}).items():
        sidecar = Path(entry.get("sidecar", ""))
        if not sidecar.exists():
            continue
        try:
            with sidecar.open("r", encoding="utf-8") as fh:
                graph = json.load(fh)
        except (json.JSONDecodeError, OSError):
            continue
        per_project[slug] = analyze_project(graph)
    out: Dict[str, Any] = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "projects_analyzed": len(per_project),
        "patterns": aggregate_patterns(per_project),
    }
    if len(per_project) < 2:
        out["note"] = (
            "Signal too thin: needs >=2 registered projects for cross-project "
            "patterns to be meaningful. Output is descriptive of "
            f"{len(per_project)} project(s) only."
        )
    return out


def write_patterns(jarvis_home: Path, result: Dict[str, Any]) -> str:
    """Write the aggregated patterns to ~/.jarvis/agent_identity/code_patterns.json."""
    out_dir = Path(jarvis_home) / AGENT_IDENTITY_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / PATTERNS_FILENAME
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return str(out_path)
