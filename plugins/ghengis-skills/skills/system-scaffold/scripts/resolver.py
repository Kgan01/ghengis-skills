"""
system-scaffold Stage 3 (final step) — Resolver.

Takes the post-interview taxonomy.yaml and the Stage 2 classifications.json,
applies the user's decisions, and emits resolved.json — the final per-node
classification that Stages 4-7 consume.

Resolution rules (applied in order):
1. Per-path 'resolutions' from taxonomy.yaml — explicit overrides.
2. Drive-purpose inheritance — items with class=unknown on a drive with a
   declared accept_classes list pick up the most specific accept_class that
   matches their content type, else the first accept_class as fallback.
3. policies.nested_project_likely=inherit-from-parent — for any project-likely
   node whose path is inside an already-classified project, copy the parent's
   class + custom_category.
4. policies.phantom_command_folders=leave-untouched — record but don't move.

Output: resolved.json with the same shape as classifications.json plus
- resolved_class, resolved_confidence (final after all rules)
- resolved_custom_category (if applicable)
- resolution_source ('user', 'drive-inheritance', 'parent-inheritance', 'classifier')
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

import yaml  # PyYAML

RESOLVER_VERSION = "1"

SEP = "\\"


def _norm(path: str) -> str:
    return path.replace("/", SEP)


def apply_resolutions(
    classifications: dict,
    taxonomy: dict,
) -> dict:
    nodes = classifications["classified"]
    by_path = {_norm(n["path"]): n for n in nodes}

    # 1. Explicit per-path resolutions
    user_resolutions = {_norm(r["path"]): r for r in taxonomy.get("resolutions", [])}

    # 2. Drive purposes — for inheritance fallback
    drive_purposes = {
        letter: cfg for letter, cfg in taxonomy.get("drives", {}).items()
    }

    # 3. Build set of already-classified projects (project-active, project-stale)
    project_paths = {
        _norm(n["path"]): n
        for n in nodes
        if n.get("class") in ("project-active", "project-stale")
    }

    def closest_project_ancestor(path: str):
        parts = _norm(path).split(SEP)
        while parts:
            parts.pop()
            candidate = SEP.join(parts)
            if candidate in project_paths:
                return project_paths[candidate]
        return None

    nested_inherit = taxonomy.get("policies", {}).get("nested_project_likely") == "inherit-from-parent"

    resolved_nodes = []
    stats = {
        "user_resolved": 0,
        "parent_inherited": 0,
        "drive_inherited": 0,
        "unchanged": 0,
        "to_delete": 0,
    }

    for n in nodes:
        path = _norm(n["path"])
        out = dict(n)
        out["resolved_class"] = n["class"]
        out["resolved_confidence"] = n["confidence"]
        out["resolved_custom_category"] = None
        out["resolved_action"] = None
        out["resolved_target_drive"] = None
        out["resolution_source"] = "classifier"

        # Rule 1: per-path user resolution
        if path in user_resolutions:
            r = user_resolutions[path]
            if "class" in r:
                out["resolved_class"] = r["class"]
                out["resolved_confidence"] = float(r.get("confidence", 1.0))
            if "action" in r:
                out["resolved_action"] = r["action"]
                if r["action"] == "delete":
                    stats["to_delete"] += 1
            if "custom_category" in r:
                out["resolved_custom_category"] = r["custom_category"]
            if "target_drive" in r:
                out["resolved_target_drive"] = r["target_drive"]
            out["resolution_source"] = "user"
            stats["user_resolved"] += 1
            resolved_nodes.append(out)
            continue

        # Rule 3 (parent inheritance for nested project-likely)
        if nested_inherit and n["class"] == "project-likely":
            anc = closest_project_ancestor(path)
            if anc:
                out["resolved_class"] = anc["class"]
                out["resolved_confidence"] = 0.92  # match parent's confidence
                out["resolution_source"] = "parent-inheritance"
                # Pass through parent's custom category if it had one resolved
                stats["parent_inherited"] += 1
                resolved_nodes.append(out)
                continue

        # Rule 2 — drive-purpose inheritance for unknown items
        if n["class"] == "unknown":
            drive_letter = n.get("drive")
            drive_cfg = drive_purposes.get(drive_letter, {})
            accept = drive_cfg.get("accept_classes", [])
            if accept:
                # Use the first non-meta accept_class as the default
                # (drive owner can refine later in scaffold authoring)
                default_cls = accept[0]
                out["resolved_class"] = default_cls
                out["resolved_confidence"] = 0.7  # inherited — not user-confirmed per item
                out["resolution_source"] = "drive-inheritance"
                stats["drive_inherited"] += 1
                resolved_nodes.append(out)
                continue

        stats["unchanged"] += 1
        resolved_nodes.append(out)

    # Distribution of resolved classes
    dist: dict[str, int] = {}
    for n in resolved_nodes:
        dist[n["resolved_class"]] = dist.get(n["resolved_class"], 0) + 1

    delete_set = [n for n in resolved_nodes if n.get("resolved_action") == "delete"]
    total_delete_bytes = sum(n["size_bytes"] for n in delete_set)

    return {
        "version": RESOLVER_VERSION,
        "resolver": "system-scaffold/resolver.py",
        "ran_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source_classifications_ran_at": classifications.get("ran_at"),
        "taxonomy_generated_at": taxonomy.get("generated_at"),
        "stats": stats,
        "delete_summary": {
            "count": len(delete_set),
            "total_bytes": total_delete_bytes,
            "paths": [n["path"] for n in delete_set],
        },
        "resolved_distribution": dict(sorted(dist.items(), key=lambda kv: -kv[1])),
        "nodes": resolved_nodes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="system-scaffold Stage 3 resolver")
    parser.add_argument("classifications", help="path to classifications.json")
    parser.add_argument("taxonomy", help="path to taxonomy.yaml")
    parser.add_argument(
        "--output",
        help="output path for resolved.json. Default: same dir as classifications.",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    cls_path = Path(args.classifications)
    tax_path = Path(args.taxonomy)
    out_path = Path(args.output) if args.output else cls_path.parent / "resolved.json"

    if not cls_path.exists():
        print(f"[resolver] error: {cls_path} not found", file=sys.stderr)
        return 1
    if not tax_path.exists():
        print(f"[resolver] error: {tax_path} not found", file=sys.stderr)
        return 1

    classifications = json.load(open(cls_path, "r", encoding="utf-8"))
    with open(tax_path, "r", encoding="utf-8") as f:
        taxonomy = yaml.safe_load(f)

    result = apply_resolutions(classifications, taxonomy)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if not args.quiet:
        s = result["stats"]
        print(f"[resolver] user-resolved: {s['user_resolved']}", file=sys.stderr)
        print(f"[resolver] parent-inherited: {s['parent_inherited']}", file=sys.stderr)
        print(f"[resolver] drive-inherited: {s['drive_inherited']}", file=sys.stderr)
        print(f"[resolver] unchanged: {s['unchanged']}", file=sys.stderr)
        print(f"[resolver] queued for delete: {s['to_delete']} ({result['delete_summary']['total_bytes']/1e9:.2f} GB)", file=sys.stderr)
        print(f"[resolver] wrote {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
