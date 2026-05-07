"""
treefile-organizer: planner.

Reads analysis.json from the analyzer, detects project type, computes an ideal
target layout, proposes file moves with computed import rewrites, topologically
sorts the moves, and emits both plan.json (machine-readable) and plan.md
(human-readable) per the schema in plan-format.md.

This is stages 2 (PROPOSE) and 3 (PLAN) of the 7-stage pipeline. It does NOT
move files. It does NOT validate. It produces a deterministic plan that
downstream stages (VALIDATE → CONFIRM → EXECUTE → VERIFY) operate on.

Usage:
    python planner.py <analysis.json> --output-dir <dir>

Output files (written to --output-dir, defaults to ./.claude/treefile-organizer/):
    plan.json   — schema per plan-format.md
    plan.md     — human-readable summary
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

PLANNER_VERSION = "1"

# ---------------------------------------------------------------------------
# Project type detection
# ---------------------------------------------------------------------------


def detect_project_type(analysis: dict) -> str:
    """Heuristic project-type detection from anchor files + source content.

    Important: the analyzer's per-file `imports[]` list excludes external
    imports by default (only resolved-internal imports are kept). So FastAPI /
    Django / Flask CANNOT be detected from there. Instead, scan the actual
    source bytes from the project root for telltale framework imports.

    Returns one of:
        "fastapi-service" | "react-nextjs-app" | "react-app" |
        "python-library" | "typescript-library" | "node-app" | "unknown"
    """
    anchors_set = set(Path(a).name for a in analysis.get("anchors", []))
    files = analysis.get("files", [])
    files_by_path = {f["path"]: f for f in files}
    lang_counts = analysis.get("stats", {}).get("files_by_language", {})
    project_root = Path(analysis.get("project_root", "."))

    has_next = any(
        Path(a).name.startswith("next.config") for a in analysis.get("anchors", [])
    )
    has_pkg = "package.json" in anchors_set
    has_pyproject = "pyproject.toml" in anchors_set or "setup.py" in anchors_set

    # Direct source scan for framework imports — bounded to first 200 Python
    # files for speed. We look for raw `import fastapi`, `from fastapi`,
    # `import django`, `from django`. Not the prettiest signal, but reliable.
    has_fastapi = False
    has_django = False
    has_flask = False
    py_scanned = 0
    for f in files:
        if f["language"] != "python":
            continue
        if py_scanned >= 200:
            break
        py_scanned += 1
        try:
            text = (project_root / f["path"]).read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if re.search(r"^\s*(?:from|import)\s+fastapi\b", text, re.MULTILINE):
            has_fastapi = True
        if re.search(r"^\s*(?:from|import)\s+django\b", text, re.MULTILINE):
            has_django = True
        if re.search(r"^\s*(?:from|import)\s+flask\b", text, re.MULTILINE):
            has_flask = True
        if has_fastapi and has_django and has_flask:
            break

    if has_next and has_pkg:
        return "react-nextjs-app"
    if has_pkg and lang_counts.get("typescript", 0) + lang_counts.get("javascript", 0) > 0:
        return "react-app" if any(p.endswith((".tsx", ".jsx")) for p in files_by_path) else "node-app"
    if has_fastapi or has_flask or has_django:
        return "fastapi-service"  # all three map to API-service shape; specialize later if needed
    if has_pyproject and lang_counts.get("python", 0) > 0:
        return "python-library"
    if lang_counts.get("typescript", 0) > 0:
        return "typescript-library"
    return "unknown"


# ---------------------------------------------------------------------------
# Ideal layout templates per project type
# ---------------------------------------------------------------------------


# Maps layer -> ideal directory (relative to project root). The planner
# proposes moving a file from its current location to <ideal_dir>/<basename>
# only when the file's CURRENT containing dir does not already match the
# ideal pattern for its classified layer.
IDEAL_LAYOUTS: dict[str, dict[str, str]] = {
    "fastapi-service": {
        "api": "src/api",
        "service": "src/services",
        "data": "src/data",
        "infrastructure": "src/infrastructure",
        "utility": "src/utils",
        "ui": "src/ui",  # rare in API services
        "test": "tests",
    },
    "react-nextjs-app": {
        "ui": "src/components",
        "api": "src/app/api",
        "service": "src/services",
        "data": "src/data",
        "infrastructure": "src/lib",
        "utility": "src/utils",
        "test": "tests",
    },
    "react-app": {
        "ui": "src/components",
        "api": "src/api",
        "service": "src/services",
        "data": "src/data",
        "infrastructure": "src/lib",
        "utility": "src/utils",
        "test": "tests",
    },
    "python-library": {
        "api": "src/api",
        "service": "src/services",
        "data": "src/models",
        "infrastructure": "src/infrastructure",
        "utility": "src/utils",
        "ui": "src/ui",
        "test": "tests",
    },
    "typescript-library": {
        "api": "src/api",
        "service": "src/services",
        "data": "src/data",
        "infrastructure": "src/lib",
        "utility": "src/utils",
        "ui": "src/components",
        "test": "tests",
    },
    "node-app": {
        "api": "src/api",
        "service": "src/services",
        "data": "src/data",
        "infrastructure": "src/lib",
        "utility": "src/utils",
        "ui": "src/views",
        "test": "tests",
    },
    "unknown": {
        # Conservative fallback — only move when the layer is unambiguous
        # AND the current location violates a basic expectation.
        "api": "api",
        "service": "services",
        "data": "data",
        "infrastructure": "infrastructure",
        "utility": "utils",
        "ui": "components",
        "test": "tests",
    },
}


# ---------------------------------------------------------------------------
# Move proposal
# ---------------------------------------------------------------------------


@dataclass
class ProposedMove:
    src: str
    dst: str
    language: str
    layer: str
    reason: str
    imports_in: list[dict] = field(default_factory=list)


def file_already_in_ideal_dir(file_path: str, ideal_dir: str) -> bool:
    """Returns True if the file is already inside the ideal_dir (or any subdir of it)."""
    p = Path(file_path).as_posix()
    ideal = Path(ideal_dir).as_posix().rstrip("/")
    if not ideal:
        return False
    # File path starts with ideal/ OR equals ideal+filename pattern
    return p.startswith(ideal + "/") or p == ideal


SCAFFOLD_DIRS = {"src", "app", "lib", "source"}
LAYER_DIRS_FOR_STRIP = {
    "utils", "util", "helpers", "common", "shared",
    "routes", "api", "controllers", "endpoints", "handlers",
    "services", "service", "business", "domain",
    "models", "schemas", "schema", "entities", "repositories", "db", "database",
    "components", "views", "pages", "widgets", "screens", "ui",
    "scripts", "deploy", "config", "infra", "middleware",
    "tests", "test",
}


def propose_target_path(file_path: str, ideal_dir: str) -> str:
    """Compute the proposed target path for a file moving to ideal_dir.

    Strategy:
      1. Drop leading scaffold dirs (src/, app/, lib/, source/).
      2. Drop ALL layer-named components (not just leading) — these are
         redundant under the new ideal_dir which already encodes the layer.
         This avoids the bug where `brain/services/foo.py` -> `src/services`
         produced `src/services/brain/services/foo.py`.
      3. Whatever remains (package prefix + filename) goes under ideal_dir.

    Preserves package context like `brain/foo.py` -> `src/services/brain/foo.py`,
    but strips redundant `services/` segments.
    """
    p = Path(file_path)
    parts = list(p.parts)

    # Drop leading scaffold dirs
    while parts and parts[0] in SCAFFOLD_DIRS:
        parts = parts[1:]

    # Drop ALL layer-name components (preserve the basename always)
    if len(parts) > 1:
        kept = [comp for comp in parts[:-1] if comp not in LAYER_DIRS_FOR_STRIP]
        parts = kept + [parts[-1]]

    if not parts:
        parts = [p.name]
    return str(Path(ideal_dir, *parts)).replace("\\", "/")


def is_anchor(file_path: str, anchors: set[str]) -> bool:
    """A file is an anchor if it's in the anchors set OR inside an anchor directory."""
    if file_path in anchors:
        return True
    p_parts = Path(file_path).parts
    for anchor in anchors:
        a_parts = Path(anchor).parts
        # If anchor is a directory-style entry, check parent containment
        if len(a_parts) <= len(p_parts) and tuple(p_parts[: len(a_parts)]) == tuple(a_parts):
            return True
    return False


def propose_moves(
    analysis: dict,
    ideal_layout: dict[str, str],
) -> list[ProposedMove]:
    moves: list[ProposedMove] = []
    anchors = set(analysis.get("anchors", []))
    files = analysis.get("files", [])

    for f in files:
        path = f["path"]
        layer = f["layer"]
        lang = f["language"]

        # Skip anchors entirely
        if is_anchor(path, anchors):
            continue

        # Skip unknown layer — too risky to propose without confidence
        if layer == "unknown":
            continue

        # Skip if there's no ideal location for this layer in this project type
        ideal_dir = ideal_layout.get(layer)
        if not ideal_dir:
            continue

        # Skip if already in the ideal dir
        if file_already_in_ideal_dir(path, ideal_dir):
            continue

        target = propose_target_path(path, ideal_dir)
        # Don't propose a no-op
        if target == path:
            continue

        # Don't propose a "move" that just changes case or whitespace
        if target.lower() == path.lower():
            continue

        moves.append(
            ProposedMove(
                src=path,
                dst=target,
                language=lang,
                layer=layer,
                reason=f"{layer} file currently in non-canonical location",
            )
        )

    return moves


# ---------------------------------------------------------------------------
# Collision detection
# ---------------------------------------------------------------------------


def detect_collisions(moves: list[ProposedMove], existing_files: set[str]) -> list[str]:
    """Surface destinations that collide with each other or with existing files."""
    warnings: list[str] = []
    target_to_srcs: dict[str, list[str]] = defaultdict(list)
    for m in moves:
        target_to_srcs[m.dst].append(m.src)

    for target, srcs in target_to_srcs.items():
        if len(srcs) > 1:
            warnings.append(
                f"COLLISION: {len(srcs)} files would land at {target}: {srcs}"
            )
        elif target in existing_files and target not in [m.src for m in moves]:
            # Target already exists AND no one is moving the existing file out.
            warnings.append(
                f"OVERWRITE: target {target} exists; would clobber unless {target} also moves"
            )
    return warnings


# ---------------------------------------------------------------------------
# Import rewrite computation
# ---------------------------------------------------------------------------


def python_module_path(rel_path: str) -> str:
    """Convert src/foo/bar.py -> foo.bar (best-effort dotted module path).

    This strips the leading 'src/' if present and the .py extension, replaces
    slashes with dots. Used for rewriting absolute Python imports.
    """
    p = rel_path.replace("\\", "/")
    if p.startswith("src/"):
        p = p[4:]
    if p.endswith("/__init__.py"):
        p = p[: -len("/__init__.py")]
    elif p.endswith(".py"):
        p = p[:-3]
    return p.replace("/", ".")


def python_relative_to_absolute(import_module: str, source_path: str) -> tuple[str, str] | None:
    """Try to resolve a Python relative import to an absolute module path.

    Returns (absolute_module_path, original_module_str) or None if can't compute.
    """
    leading = len(import_module) - len(import_module.lstrip("."))
    if leading == 0:
        return None
    rest = import_module[leading:]
    src_parts = list(Path(source_path).parts[:-1])  # drop filename
    if src_parts and src_parts[0] == "src":
        src_parts = src_parts[1:]
    up = leading - 1
    if up > len(src_parts):
        return None
    base = src_parts[: len(src_parts) - up] if up > 0 else src_parts
    rest_parts = rest.split(".") if rest else []
    full_parts = [p for p in base + rest_parts if p]
    return (".".join(full_parts), import_module)


def ts_compute_relative(from_path: str, to_path: str) -> str:
    """Compute a TS-style relative import specifier from one file to another.

    Both paths are project-relative POSIX. Result has no extension and is
    always prefixed with ./ or ../ so it's recognized as relative.
    """
    import os
    from_dir = Path(from_path).parent
    target_no_ext = Path(to_path).with_suffix("")
    rel = os.path.relpath(target_no_ext, from_dir).replace("\\", "/")
    if not rel.startswith("."):
        rel = "./" + rel
    return rel


def compute_import_rewrites(
    moves: list[ProposedMove],
    files: list[dict],
    edges: list[dict],
) -> list[ProposedMove]:
    """For each move, find all files importing it and produce import_in entries.

    Mutates moves in place by populating their imports_in lists, then returns the
    same list for convenience.
    """
    # Index moves by src for fast lookup
    move_src_to_dst: dict[str, str] = {m.src: m.dst for m in moves}
    move_src_to_lang: dict[str, str] = {m.src: m.language for m in moves}
    files_by_path: dict[str, dict] = {f["path"]: f for f in files}

    # Index edges: for each (src->dst), we know src imports dst.
    # We need: for each "moved file", who imports it?
    importers: dict[str, list[dict]] = defaultdict(list)  # imported_path -> [edge dicts]
    for e in edges:
        importers[e["dst"]].append(e)

    for m in moves:
        consumers = importers.get(m.src, [])
        for edge in consumers:
            consumer_path = edge["src"]
            consumer = files_by_path.get(consumer_path)
            if not consumer:
                continue

            # Find the actual import line in the consumer file
            line = edge["line"]
            old_module = None
            for imp in consumer.get("imports", []):
                if imp.get("line") == line and imp.get("resolves_to") == m.src:
                    old_module = imp.get("module")
                    break
            if old_module is None:
                # Unable to find the exact import — surface as a warning rather than silently skipping
                m.imports_in.append({
                    "file": consumer_path,
                    "line": line,
                    "old": "<unresolved — manual review needed>",
                    "new": "<unresolved — manual review needed>",
                })
                continue

            # Compute the new import string
            new_module = _rewrite_import(
                old_module=old_module,
                language=m.language,
                consumer_path=consumer_path,
                old_target=m.src,
                new_target=m.dst,
                consumer_after_move=move_src_to_dst.get(consumer_path, consumer_path),
            )

            m.imports_in.append({
                "file": consumer_path,
                "line": line,
                "old": old_module,
                "new": new_module,
            })

    return moves


def _rewrite_import(
    old_module: str,
    language: str,
    consumer_path: str,
    old_target: str,
    new_target: str,
    consumer_after_move: str,
) -> str:
    """Rewrite a single import statement to point at the new target location."""
    if language == "python":
        # If old_module starts with '.', it's relative — convert to absolute or recompute
        if old_module.startswith("."):
            # Resolve old relative -> absolute, then rewrite to new absolute path
            new_abs = python_module_path(new_target)
            return new_abs
        # Absolute: rewrite the dotted path
        new_abs = python_module_path(new_target)
        return new_abs
    elif language in ("typescript", "javascript"):
        if old_module.startswith("./") or old_module.startswith("../"):
            return ts_compute_relative(consumer_after_move, new_target)
        # Path alias or external — flag for manual review
        return f"<rewrite needed; was {old_module} — manual review>"
    return old_module


# ---------------------------------------------------------------------------
# Topological sort
# ---------------------------------------------------------------------------


def topo_sort(moves: list[ProposedMove], edges: list[dict]) -> list[str]:
    """Return move sources in topo order: a file is moved AFTER any file it depends on.

    Analyzer edges are (src=consumer, dst=imported), meaning src imports dst.
    For the move plan, the IMPORTED file (dst) must move BEFORE the IMPORTING
    file (src) so that intermediate states are valid. So in our DAG:
        - dst (the dependency) has no incoming edges from its consumers
        - src (the dependent) gets an incoming edge from its dependency
    Kahn's then pops dependencies first.

    Conservative: if cycles exist among moved files, falls back to source order.
    """
    move_set = {m.src for m in moves}
    adj: dict[str, set[str]] = defaultdict(set)
    indeg: dict[str, int] = {s: 0 for s in move_set}
    for e in edges:
        consumer, imported = e["src"], e["dst"]
        if consumer in move_set and imported in move_set:
            # Edge points from imported (dependency) -> consumer (dependent).
            # Consumer gains an indegree because it depends on imported.
            if consumer not in adj[imported]:
                adj[imported].add(consumer)
                indeg[consumer] += 1

    queue = [s for s, d in indeg.items() if d == 0]
    order: list[str] = []
    while queue:
        queue.sort()
        node = queue.pop(0)
        order.append(node)
        for child in sorted(adj[node]):
            indeg[child] -= 1
            if indeg[child] == 0:
                queue.append(child)

    if len(order) < len(move_set):
        # Cycle detected — fall back to sorted source order
        order = sorted(move_set)
    return order


# ---------------------------------------------------------------------------
# Risk assessment
# ---------------------------------------------------------------------------


def assess_risk(moves: list[ProposedMove], analysis: dict) -> tuple[str, list[str]]:
    """Return (risk_level, list_of_warning_strings)."""
    n_moves = len(moves)
    n_imports = sum(len(m.imports_in) for m in moves)
    n_files = analysis.get("stats", {}).get("files_total", 0)
    n_cycles = analysis.get("stats", {}).get("cycles_detected", 0)

    risk_warnings: list[str] = []
    if n_cycles > 0:
        risk_warnings.append(
            f"Project contains {n_cycles} import cycle(s); moves involving cyclic files "
            "may produce unstable intermediate states. Validator should flag these."
        )

    if n_moves == 0:
        return "low", risk_warnings
    move_ratio = n_moves / max(n_files, 1)
    if move_ratio > 0.5 or n_cycles > 5 or n_imports > 200:
        return "high", risk_warnings
    if move_ratio > 0.2 or n_cycles > 0 or n_imports > 50:
        return "medium", risk_warnings
    return "low", risk_warnings


# ---------------------------------------------------------------------------
# plan.json + plan.md generation
# ---------------------------------------------------------------------------


def build_plan_json(
    analysis: dict,
    project_type: str,
    moves: list[ProposedMove],
    topo_order: list[str],
    warnings_list: list[str],
) -> dict:
    risk, risk_warnings = assess_risk(moves, analysis)
    all_warnings = warnings_list + risk_warnings
    return {
        "version": PLANNER_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_root": analysis["project_root"],
        "project_type": project_type,
        "language_mix": analysis.get("stats", {}).get("files_by_language", {}),
        "anchors": analysis.get("anchors", []),
        "moves": [
            {
                "from": m.src,
                "to": m.dst,
                "language": m.language,
                "layer": m.layer,
                "reason": m.reason,
                "imports_in": m.imports_in,
            }
            for m in moves
        ],
        "topo_order": topo_order,
        "estimated_imports_to_rewrite": sum(len(m.imports_in) for m in moves),
        "risk": risk,
        "warnings": all_warnings,
    }


def _pluralize(n: int, singular: str, plural: str | None = None) -> str:
    return singular if n == 1 else (plural or singular + "s")


def _build_proposed_tree(plan: dict) -> str:
    """Render an indented preview of the proposed top-level shape after moves."""
    if not plan["moves"]:
        return "(no moves; tree unchanged)"
    target_dirs: dict[str, set[str]] = defaultdict(set)
    for m in plan["moves"]:
        top = Path(m["to"]).parts[0] if Path(m["to"]).parts else "."
        rest_dir = str(Path(*Path(m["to"]).parts[1:-1])) if len(Path(m["to"]).parts) > 2 else "(root)"
        target_dirs[top].add(rest_dir)
    out: list[str] = []
    for top in sorted(target_dirs):
        subdirs = sorted(d for d in target_dirs[top] if d != "(root)")
        out.append(f"{top}/")
        if "(root)" in target_dirs[top]:
            out.append(f"  *.{{py,ts,…}}")
        for sub in subdirs[:8]:
            out.append(f"  {sub}/")
        if len(subdirs) > 8:
            out.append(f"  …and {len(subdirs) - 8} more subdirs")
    return "\n".join(out)


def build_plan_md(plan: dict) -> str:
    project = Path(plan["project_root"]).name
    lines: list[str] = []
    lines.append(f"# Reorganization Plan — {project}")
    lines.append("")
    lines.append(f"**Project type:** {plan['project_type']}")
    lines.append(f"**Generated:** {plan['created_at']}")
    lines.append(f"**Risk:** {plan['risk']}")
    lines.append("")

    n_moves = len(plan["moves"])
    n_imports = plan["estimated_imports_to_rewrite"]
    n_anchors = len(plan["anchors"])
    # Use sum of language_mix for "files scanned" — this excludes
    # `unknown`-language files which the analyzer also filters out, so this
    # equals stats.files_total.
    n_files_total = sum(plan["language_mix"].values())

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Files scanned: {n_files_total}")
    lines.append(f"- {_pluralize(n_moves, 'file')} moving: {n_moves}")
    lines.append(f"- Imports to rewrite: {n_imports}")
    lines.append(f"- Anchors (not moving): {n_anchors}")
    if plan["warnings"]:
        lines.append(f"- ⚠ Warnings: {len(plan['warnings'])} (see Risk section)")
    lines.append("")

    # What's drifted (narrative)
    lines.append("## What's drifted")
    lines.append("")
    if n_moves == 0:
        lines.append("Nothing significant. The project layout already matches its detected type.")
        lines.append("")
        lines.append("## Proceed?")
        lines.append("")
        lines.append('No moves to execute. Reply "discard" to dismiss this plan.')
        return "\n".join(lines)

    # Build narrative from move-source distribution
    src_dirs: dict[str, int] = defaultdict(int)
    for m in plan["moves"]:
        src_dirs[str(Path(m["from"]).parts[0]) if Path(m["from"]).parts else "."] += 1
    top_drift = sorted(src_dirs.items(), key=lambda kv: -kv[1])[:3]
    drift_summary = ", ".join(f"`{d}/` ({n} {_pluralize(n, 'file')})" for d, n in top_drift)
    lines.append(
        f"Files classified as architectural layers don't match their current locations. "
        f"Top sources of drift: {drift_summary}. "
        f"The proposed plan moves {n_moves} {_pluralize(n_moves, 'file')} "
        f"and rewrites {n_imports} import {_pluralize(n_imports, 'statement')} "
        f"so that each file lives under the canonical directory for its layer in a "
        f"{plan['project_type']} project."
    )
    lines.append("")

    # Proposed shape
    lines.append("## Proposed shape")
    lines.append("")
    lines.append("```")
    lines.append(_build_proposed_tree(plan))
    lines.append("```")
    lines.append("")

    # Group moves by source-dir → target-dir
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for m in plan["moves"]:
        src_dir = str(Path(m["from"]).parent) or "."
        dst_dir = str(Path(m["to"]).parent) or "."
        grouped[(src_dir, dst_dir)].append(m)

    lines.append("## Moves")
    lines.append("")
    for (src_dir, dst_dir), group in sorted(grouped.items()):
        layers = sorted({m["layer"] for m in group})
        n = len(group)
        lines.append(
            f"**`{src_dir}/` → `{dst_dir}/`** ({n} {_pluralize(n, 'file')}, "
            f"{_pluralize(len(layers), 'layer')}: {', '.join(layers)})"
        )
        for m in group[:5]:
            lines.append(f"  - `{Path(m['from']).name}` — {m['reason']}")
        if n > 5:
            lines.append(f"  - …and {n - 5} more")
        lines.append("")

    lines.append("## Anchors (not moving)")
    lines.append("")
    if plan["anchors"]:
        for a in plan["anchors"][:20]:
            lines.append(f"- `{a}`")
        if len(plan["anchors"]) > 20:
            lines.append(f"- …and {len(plan['anchors']) - 20} more")
    else:
        lines.append("(none detected)")
    lines.append("")

    lines.append("## Risk")
    lines.append("")
    lines.append(f"Overall: **{plan['risk']}**.")
    lines.append("")
    if plan["warnings"]:
        lines.append("### Warnings")
        for w in plan["warnings"]:
            lines.append(f"- {w}")
        lines.append("")
    lines.append(
        "If anything fails mid-execute, recovery is `git reset --hard <pre-checkpoint-sha>`. "
        "The skill tags that SHA before any moves and surfaces it on completion."
    )
    lines.append("")

    lines.append("## Proceed?")
    lines.append("")
    lines.append('Reply **"yes proceed"** to execute, or describe what to change and I will re-plan.')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="treefile-organizer planner (stages 2-3)")
    p.add_argument("analysis_json", help="Path to analysis.json from analyzer.py")
    p.add_argument(
        "--output-dir",
        "-o",
        default=".claude/treefile-organizer",
        help="Where to write plan.json and plan.md (default: .claude/treefile-organizer)",
    )
    args = p.parse_args(argv)

    analysis_path = Path(args.analysis_json)
    if not analysis_path.is_file():
        sys.stderr.write(f"Analysis file not found: {analysis_path}\n")
        return 2

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    project_type = detect_project_type(analysis)
    ideal_layout = IDEAL_LAYOUTS.get(project_type, IDEAL_LAYOUTS["unknown"])

    moves = propose_moves(analysis, ideal_layout)
    existing_files = {f["path"] for f in analysis.get("files", [])}
    warnings_list = detect_collisions(moves, existing_files)
    moves = compute_import_rewrites(moves, analysis.get("files", []), analysis.get("edges", []))
    topo_order = topo_sort(moves, analysis.get("edges", []))

    plan = build_plan_json(analysis, project_type, moves, topo_order, warnings_list)
    plan_md = build_plan_md(plan)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    (output_dir / "plan.md").write_text(plan_md, encoding="utf-8")

    print(f"Wrote {output_dir / 'plan.json'}")
    print(f"Wrote {output_dir / 'plan.md'}")
    print(f"Project type: {project_type}")
    print(f"Moves: {len(moves)}")
    print(f"Imports to rewrite: {sum(len(m.imports_in) for m in moves)}")
    print(f"Risk: {plan['risk']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
