# `scripts/code_graph/` — code-graph data refresh helpers

Five small Python helpers + a single CLI runner. They consume a `.jarvis/code-graph.json` sidecar (produced by JARVIS's `analyze_codebase` tool, or any tool that emits the same shape) and refresh derived data files: MEMORY.md, CONTEXT.md, SkillMemory bullets, treefile suggestions, and cross-project structural patterns.

## Files

| File | Purpose |
|------|---------|
| `memory_map_writer.py` | Render the auto-managed Project Map block for MEMORY.md |
| `routing_table.py` | Render the Workspace Routing block for CONTEXT.md (Van Clief Layer 1) |
| `rationale_ingest.py` | Pull HACK/FIXME/XXX rationale nodes into per-agent SKILL_MEMORY.md |
| `treefile_advisor.py` | Suggest file moves based on community vs. directory mismatch |
| `code_pattern_miner.py` | Mine structural habits (where do auth files live?) across registered projects |
| `run.py` | Single CLI entry point — invoke any of the five from a skill |

All helpers are pure Python stdlib. No JARVIS / agents / brain imports — drop them anywhere.

## CLI usage

From inside the plugin directory:

```
python scripts/code_graph/run.py <action> [args...]
```

### `memory_map`
Refresh the `<!-- AUTO:project-map:start -->` … `<!-- AUTO:project-map:end -->` block in a MEMORY.md.
```
python scripts/code_graph/run.py memory_map <project_root> <memory_path>
```

### `routing_table`
Refresh the `<!-- AUTO:routing-table:start -->` block in a CONTEXT.md.
```
python scripts/code_graph/run.py routing_table <project_root> <context_path> [--top-n 8]
```

### `rationale_ingest`
Append new HACK/FIXME/XXX bullets to `<skill_memory_root>/<agent>/SKILL_MEMORY.md`. State (already-ingested ids) lives in `<project_root>/.jarvis/rationale_ingest_state.json`.
```
python scripts/code_graph/run.py rationale_ingest <project_root> <skill_memory_root> \
    [--include-todo] [--agent engineer]
```

### `treefile_suggest`
Write `<project_root>/.jarvis/treefile-suggestions.md`.
```
python scripts/code_graph/run.py treefile_suggest <project_root> \
    [--min-cohesion 0.5] [--min-dir-size 3]
```

### `learn_patterns`
Mine cross-project habits and write `<output_dir>/code_patterns.json`.
```
python scripts/code_graph/run.py learn_patterns <global_json_path> <output_dir>
```
A reasonable `<output_dir>` is `~/.claude/agent_identity/`. Needs ≥2 registered projects for signal to be meaningful; output includes a `note` field when signal is thin.

## Output format

Every action prints exactly one JSON line to stdout. Success looks like:
```json
{"status": "ok", "action": "memory_map", "wrote_changes": true, "memory_path": "..."}
```
Failure looks like:
```json
{"status": "error", "message": "No code-graph sidecar at ..."}
```
Exit code is `0` on success, `1` on error.

## Calling from a skill

A skill should:
1. Verify `<project_root>/.jarvis/code-graph.json` exists (skip the mechanical step otherwise).
2. Invoke the runner with `Bash`, capturing stdout.
3. Parse the JSON line and surface `wrote_changes`/`count`/etc. to the user.

The runner is self-contained — no PYTHONPATH magic needed when invoked by path.
