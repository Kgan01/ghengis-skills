"""CLI runner for code-graph tools.

Usage::

    python -m scripts.code_graph.run <action> [args...]

Or, when invoked directly by path (recommended from skills, which don't always
know the right ``python -m`` working directory)::

    python scripts/code_graph/run.py <action> [args...]

Actions:
    memory_map        Refresh the Project Map block in a MEMORY.md file.
    routing_table     Refresh the Workspace Routing block in a CONTEXT.md file.
    rationale_ingest  Push HACK/FIXME/XXX from the code graph into SkillMemory.
    treefile_suggest  Write .jarvis/treefile-suggestions.md from communities.
    learn_patterns    Mine cross-project structural habits from global.json.

All actions read a code-graph sidecar at ``<project_root>/.jarvis/code-graph.json``
(except ``learn_patterns``, which reads a global registry path explicitly).
Every action prints a one-line JSON status to stdout and exits 0 on success,
1 on failure.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

# Make sibling modules importable both as ``python -m`` and ``python <path>``.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from memory_map_writer import update_memory_md, render_project_map  # noqa: E402
from routing_table import compute_routing_rows, render_routing_section, update_context_md  # noqa: E402
from rationale_ingest import (  # noqa: E402
    append_to_skill_memory,
    ingest_rationales,
    save_state,
)
from treefile_advisor import build_suggestions, render_suggestions, write_suggestions  # noqa: E402
from code_pattern_miner import mine_global_registry, write_patterns  # noqa: E402


SIDECAR_RELPATH = Path(".jarvis") / "code-graph.json"


def _load_graph(project_root: Path) -> dict:
    sidecar = project_root / SIDECAR_RELPATH
    if not sidecar.exists():
        raise FileNotFoundError(f"No code-graph sidecar at {sidecar}")
    with sidecar.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _ok(**kw) -> int:
    print(json.dumps({"status": "ok", **kw}))
    return 0


def _err(message: str, **kw) -> int:
    print(json.dumps({"status": "error", "message": message, **kw}))
    return 1


def _action_memory_map(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    memory_path = Path(args.memory_path).resolve()
    graph = _load_graph(project_root)
    md = render_project_map(graph)
    wrote = update_memory_md(memory_path, md)
    return _ok(action="memory_map", wrote_changes=wrote, memory_path=str(memory_path))


def _action_routing_table(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    context_path = Path(args.context_path).resolve()
    graph = _load_graph(project_root)
    rows = compute_routing_rows(graph, top_n=args.top_n)
    md = render_routing_section(rows)
    wrote = update_context_md(context_path, md)
    return _ok(
        action="routing_table",
        wrote_changes=wrote,
        context_path=str(context_path),
        rows=len(rows),
    )


def _action_rationale_ingest(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    skill_memory_root = Path(args.skill_memory_root).expanduser().resolve()
    graph = _load_graph(project_root)
    # State lives under the project's .jarvis/ so it's per-project (matches
    # JARVIS's behavior — global state would re-ingest the same finding across
    # every project).
    state_dir = project_root / ".jarvis"
    result = ingest_rationales(graph, state_dir, include_todo=args.include_todo)
    if result["new_learnings"]:
        sm_path = append_to_skill_memory(
            skill_memory_root, args.agent, result["new_learnings"]
        )
        save_state(state_dir, list(_load_seen(state_dir)) + result["new_ids"])
        wrote_to = str(sm_path)
    else:
        wrote_to = None
    return _ok(
        action="rationale_ingest",
        agent=args.agent,
        candidates=result["candidates"],
        new=len(result["new_learnings"]),
        already_seen=result["already_seen"],
        wrote_to=wrote_to,
    )


def _load_seen(state_dir: Path) -> list:
    """Re-read the state file's ingested_ids so save_state doesn't drop them."""
    from rationale_ingest import load_state
    return load_state(state_dir).get("ingested_ids", [])


def _action_treefile_suggest(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    graph = _load_graph(project_root)
    suggestions = build_suggestions(
        graph.get("nodes", []),
        min_cohesion=args.min_cohesion,
        min_dir_size=args.min_dir_size,
    )
    md = render_suggestions(suggestions)
    out_path = write_suggestions(project_root, md)
    return _ok(
        action="treefile_suggest",
        wrote_to=out_path,
        count=len(suggestions),
    )


def _action_learn_patterns(args: argparse.Namespace) -> int:
    global_json = Path(args.global_json_path).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    if not global_json.exists():
        return _err(f"global.json not found at {global_json}")
    with global_json.open("r", encoding="utf-8") as fh:
        registry = json.load(fh)
    result = mine_global_registry(registry)
    # write_patterns takes a directory containing agent_identity/ — pass the
    # parent so the helper lands code_patterns.json at output_dir/code_patterns.json
    # by treating output_dir itself as the "agent_identity" folder. Simplest:
    # write the JSON directly here so the path is exact.
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "code_patterns.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return _ok(
        action="learn_patterns",
        wrote_to=str(out_path),
        projects_analyzed=result.get("projects_analyzed", 0),
        patterns=len(result.get("patterns", {})),
        note=result.get("note"),
    )


def main(argv: list | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="action", required=True)

    mm = sub.add_parser("memory_map", help="Refresh Project Map block in MEMORY.md")
    mm.add_argument("project_root")
    mm.add_argument("memory_path")

    rt = sub.add_parser("routing_table", help="Refresh Workspace Routing block in CONTEXT.md")
    rt.add_argument("project_root")
    rt.add_argument("context_path")
    rt.add_argument("--top-n", type=int, default=8)

    ri = sub.add_parser("rationale_ingest", help="Push HACK/FIXME/XXX into SkillMemory")
    ri.add_argument("project_root")
    ri.add_argument("skill_memory_root")
    ri.add_argument("--include-todo", action="store_true")
    ri.add_argument("--agent", default="engineer")

    ts = sub.add_parser("treefile_suggest", help="Write treefile-suggestions.md")
    ts.add_argument("project_root")
    ts.add_argument("--min-cohesion", type=float, default=0.5)
    ts.add_argument("--min-dir-size", type=int, default=3)

    lp = sub.add_parser("learn_patterns", help="Mine cross-project structural habits")
    lp.add_argument("global_json_path")
    lp.add_argument("output_dir")

    args = p.parse_args(argv)
    dispatch = {
        "memory_map": _action_memory_map,
        "routing_table": _action_routing_table,
        "rationale_ingest": _action_rationale_ingest,
        "treefile_suggest": _action_treefile_suggest,
        "learn_patterns": _action_learn_patterns,
    }
    fn = dispatch[args.action]
    try:
        return fn(args)
    except FileNotFoundError as e:
        return _err(str(e))
    except Exception as e:  # noqa: BLE001
        return _err(f"{type(e).__name__}: {e}", traceback=traceback.format_exc())


if __name__ == "__main__":
    sys.exit(main())
