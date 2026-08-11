"""
system-scaffold Stage 6 — Scaffold Writer.

Generates the distributed CONTEXT.md files at drive roots + qualifying folders,
plus the master INDEX.md at C:\\Users\\<user>\\.system\\INDEX.md.

Reads: resolved.json, plan.json, taxonomy.yaml
Writes:
- staging mode (default): all output to <run_dir>/scaffold-preview/<mirrored-path>/CONTEXT.md
- commit mode (--commit): writes to actual drive roots and folder locations
- master INDEX.md (always): goes to ~/.system/INDEX.md

Qualifying folders for their own CONTEXT.md:
- All drive roots (C:\\, Y:\\, etc.)
- Custom-category roots from taxonomy.yaml (Y:\\aaron-boland, Y:\\knowstudio, etc.)
- Top-level (depth <= 3) project folders (resolved_class starts with 'project-')
- Top-level dev-models / dev-tool / dev-toolchain folders >= 1 GB
- Top-level media folders >= 5 GB with a meaningful name
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

WRITER_VERSION = "1"

QUALIFIES_MIN_GB_DEV = 1.0
QUALIFIES_MIN_GB_MEDIA = 5.0
QUALIFIES_MAX_DEPTH = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _norm(p: str) -> str:
    return p.replace("/", "\\").rstrip("\\")


def _human_gb(b: int) -> str:
    if b >= 1024**3:
        return f"{b/1024**3:.2f} GB"
    if b >= 1024**2:
        return f"{b/1024**2:.1f} MB"
    return f"{b/1024:.1f} KB"


def _last_used_date(days_ago: int | None) -> str:
    """Convert 'days ago' into an absolute date string + relative phrasing."""
    if days_ago is None:
        return "_(unknown)_"
    when = (_dt.datetime.now() - _dt.timedelta(days=days_ago)).date()
    if days_ago == 0:
        rel = "today"
    elif days_ago == 1:
        rel = "yesterday"
    elif days_ago < 30:
        rel = f"{days_ago} days ago"
    elif days_ago < 365:
        rel = f"~{days_ago // 30} months ago"
    else:
        rel = f"~{days_ago / 365:.1f} years ago"
    return f"{when.isoformat()} ({rel})"


def _drive_letter_of(path: str) -> str | None:
    p = _norm(path)
    if len(p) >= 2 and p[1] == ":":
        return p[0].upper()
    return None


# ---------------------------------------------------------------------------
# Qualification
# ---------------------------------------------------------------------------


def qualifying_folders(resolved: dict, taxonomy: dict) -> list[dict]:
    """Return the list of folder paths that should get their own CONTEXT.md."""
    nodes = resolved.get("nodes", [])
    drives_cfg = taxonomy.get("drives", {})
    custom_cats = taxonomy.get("custom_categories", {})

    # Index nodes by path
    by_path: dict[str, dict] = {_norm(n["path"]): n for n in nodes}

    # Always-include: drive roots
    qualifying: dict[str, dict] = {}
    for letter, cfg in drives_cfg.items():
        if cfg.get("excluded_from_scaffold"):
            continue
        root = f"{letter}:\\"
        node = by_path.get(_norm(root))
        if node:
            qualifying[_norm(root)] = node

    # Custom-category root paths declared in taxonomy
    for cat_name, cat_cfg in custom_cats.items():
        for loc in (cat_cfg.get("locations") or []):
            if isinstance(loc, dict):
                # Schema variant from taxonomy.yaml — dict of sub-roles
                continue
            path = _norm(str(loc).split(" ")[0])  # strip trailing parenthetical
            n = by_path.get(path)
            if n:
                qualifying[path] = n
        # locations_target — future homes (may not exist yet)
        for loc in (cat_cfg.get("locations_target") or []):
            path = _norm(str(loc))
            n = by_path.get(path)
            if n:
                qualifying[path] = n

    # Top-level (depth <= 3) project / dev-models / dev-tool folders
    for n in nodes:
        if n.get("depth", 0) > QUALIFIES_MAX_DEPTH:
            continue
        cls = n.get("resolved_class", "")
        size_gb = n.get("size_bytes", 0) / 1024**3
        path = _norm(n["path"])

        is_project = cls.startswith("project-")
        is_dev_infra = cls in ("dev-models", "dev-toolchain", "dev-vm", "dev-tool")
        is_media_collection = cls.startswith("media-")
        is_custom_category_match = n.get("resolved_custom_category") is not None

        if is_project and size_gb >= 0.05:
            qualifying[path] = n
        elif is_dev_infra and size_gb >= QUALIFIES_MIN_GB_DEV:
            qualifying[path] = n
        elif is_media_collection and size_gb >= QUALIFIES_MIN_GB_MEDIA:
            qualifying[path] = n
        elif is_custom_category_match and size_gb >= 0.1:
            qualifying[path] = n

    return list(qualifying.values())


# ---------------------------------------------------------------------------
# CONTEXT.md rendering
# ---------------------------------------------------------------------------


def render_drive_root_context(
    letter: str,
    drives_cfg: dict,
    nodes_on_drive: list[dict],
    custom_cats_on_drive: dict[str, list[str]],
    taxonomy: dict,
) -> str:
    cfg = drives_cfg.get(letter, {})
    role = cfg.get("role", "(unspecified)")
    purpose = (cfg.get("purpose") or "").strip()
    hardware = cfg.get("hardware", "")
    handling = cfg.get("handling", "")
    accepts = cfg.get("accept_classes", [])
    stable_id = cfg.get("stable_identifier", {})

    # Top-level structure
    depth1 = [n for n in nodes_on_drive if n.get("depth") == 1]
    depth1.sort(key=lambda n: -n.get("size_bytes", 0))

    # Class distribution
    class_dist: dict[str, int] = defaultdict(int)
    class_size: dict[str, int] = defaultdict(int)
    for n in nodes_on_drive:
        cls = n.get("resolved_class", "unknown")
        class_dist[cls] += 1
        class_size[cls] += n.get("size_bytes", 0)

    lines = [
        f"# Drive {letter}: — {role}",
        "",
        f"_Auto-generated by `system-scaffold` on {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}. Hand-edits welcome — re-running will preserve user-edited sections marked `<!-- user -->` ... `<!-- /user -->`._",
        "",
        "## Purpose",
        "",
        purpose or "_(not declared in taxonomy.yaml)_",
        "",
        "## Hardware",
        "",
        f"- {hardware}" if hardware else "- _(unknown)_",
    ]
    if stable_id:
        lines.append(f"- Stable identifier: label `{stable_id.get('label')}`, fs `{stable_id.get('filesystem')}`, {stable_id.get('size_gb')} GB")
    if handling:
        lines.append(f"- Handling policy: **{handling}**")
    if accepts:
        lines.append("- Accepts classes: " + ", ".join(f"`{a}`" for a in accepts))

    lines += [
        "",
        "## Top-level contents",
        "",
    ]
    if not depth1:
        lines.append("_(empty / not yet scanned)_")
    else:
        lines.append("| Folder | Size | Class | Last used |")
        lines.append("|---|---|---|---|")
        for n in depth1[:25]:
            size = _human_gb(n.get("size_bytes", 0))
            cls = n.get("resolved_class") or "?"
            lt_str = _last_used_date(n.get("last_touched_days"))
            name = _norm(n["path"]).split("\\")[-1]
            lines.append(f"| `{name}` | {size} | `{cls}` | {lt_str} |")
        if len(depth1) > 25:
            lines.append(f"| _… {len(depth1)-25} more …_ | | | |")

    if custom_cats_on_drive:
        lines += ["", "## Custom categories present", ""]
        for cat, paths in custom_cats_on_drive.items():
            lines.append(f"- **{cat}** — {len(paths)} location(s)")
            for p in paths[:5]:
                lines.append(f"  - `{p}`")
            if len(paths) > 5:
                lines.append(f"  - _… {len(paths)-5} more …_")

    lines += ["", "## Class distribution", "", "| Class | Count | Total size |", "|---|---|---|"]
    for cls in sorted(class_dist.keys(), key=lambda c: -class_size[c])[:20]:
        lines.append(f"| `{cls}` | {class_dist[cls]} | {_human_gb(class_size[cls])} |")

    lines += [
        "",
        "## Master index",
        "",
        f"- `C:\\Users\\krist\\.system\\INDEX.md`",
        "",
        "<!-- user -->",
        "_Add any hand-written notes here. This section is preserved across regenerations._",
        "<!-- /user -->",
    ]

    return "\n".join(lines)


def render_folder_context(node: dict, drives_cfg: dict, taxonomy: dict, child_nodes: list[dict]) -> str:
    path = node["path"]
    cls = node.get("resolved_class", "?")
    custom = node.get("resolved_custom_category")
    size = _human_gb(node.get("size_bytes", 0))
    lt = node.get("last_touched_days")
    drive = _drive_letter_of(path)

    lines = [
        f"# `{path}`",
        "",
        f"_Auto-generated by `system-scaffold`. Drive {drive}._",
        "",
        f"- **Class**: `{cls}`",
        f"- **Custom category**: `{custom}`" if custom else "- **Custom category**: _(none)_",
        f"- **Size**: {size}",
        f"- **Last used**: {_last_used_date(lt)}",
    ]

    markers = node.get("markers") or []
    if markers:
        lines.append(f"- **Project markers**: {', '.join(f'`{m}`' for m in markers)}")

    # Brief description per class
    descriptions = {
        "project-active": "Active project. Keep on hot storage; preserve git state if moved.",
        "project-stale": "Stale project (touched > 120 days ago). Candidate for cold archive.",
        "dev-models": "AI model cache (HuggingFace, Ollama, etc.). Movable; configure via env var.",
        "dev-toolchain": "Language toolchain. Moving requires PATH / env updates.",
        "dev-vm": "Virtual machine image. Use vendor-specific procedure to relocate.",
        "dev-tool": "Utility called from other projects. Lives in Y:\\tools\\.",
        "media-video-active": "Active video edit. Keep on fast storage.",
        "media-video-cold": "Cold video. Candidate for Z archive.",
        "documents": "Document collection. Keep accessible.",
        "aaron-boland": "Aaron Boland client work. Drive I is untouched-by-default.",
    }
    desc = descriptions.get(cls)
    if desc:
        lines += ["", desc]

    # Immediate children (top by size)
    sub = sorted([c for c in child_nodes if c["depth"] == node["depth"] + 1], key=lambda n: -n.get("size_bytes", 0))[:10]
    if sub:
        lines += ["", "## Top contents", "", "| Name | Size | Class |", "|---|---|---|"]
        for n in sub:
            name = _norm(n["path"]).split("\\")[-1]
            lines.append(f"| `{name}` | {_human_gb(n['size_bytes'])} | `{n.get('resolved_class','?')}` |")

    lines += [
        "",
        "<!-- user -->",
        "_Hand-written notes preserved across regenerations._",
        "<!-- /user -->",
    ]
    return "\n".join(lines)


def render_master_index(
    resolved: dict,
    taxonomy: dict,
    qualifying: list[dict],
    plan: dict,
    written_files: list[tuple[str, str]],
) -> str:
    drives_cfg = taxonomy.get("drives", {})
    custom_cats = taxonomy.get("custom_categories", {})

    lines = [
        "# System Index — `system-scaffold` master view",
        "",
        f"_Auto-generated by `system-scaffold` on {_dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')}._",
        "",
        "## Drives",
        "",
        "| Drive | Role | Hardware | Notes |",
        "|---|---|---|---|",
    ]
    for letter, cfg in sorted(drives_cfg.items()):
        role = cfg.get("role", "?")
        hw = cfg.get("hardware", "?")
        notes = (cfg.get("purpose") or "").split(".")[0]
        lines.append(f"| **{letter}:** | {role} | {hw} | {notes} |")

    lines += ["", "## Custom categories", ""]
    if not custom_cats:
        lines.append("_(none declared)_")
    else:
        for cat, cfg in custom_cats.items():
            primary = cfg.get("primary_drives") or []
            desc = (cfg.get("description") or "").split(".")[0]
            lines.append(f"- **`{cat}`** ({' / '.join(primary) if primary else 'no primary'}) — {desc}")
            for loc in (cfg.get("locations") or []):
                if isinstance(loc, dict):
                    for k, v in loc.items():
                        if isinstance(v, dict):
                            lines.append(f"  - {k}: `{v.get('path','?')}`")
                else:
                    lines.append(f"  - `{loc}`")

    lines += ["", "## Distributed CONTEXT.md files", ""]
    by_drive: dict[str, list[str]] = defaultdict(list)
    for path, target in written_files:
        letter = _drive_letter_of(path) or "?"
        by_drive[letter].append(target)
    for letter in sorted(by_drive.keys()):
        lines.append(f"### {letter}:")
        for t in sorted(by_drive[letter]):
            lines.append(f"- `{t}`")

    lines += [
        "",
        "## Pending move plan",
        "",
        f"- Total operations: **{plan.get('summary', {}).get('total_operations', '?')}**",
        f"- Moves: {plan.get('summary', {}).get('total_moves', '?')}",
        f"- Deletes: {plan.get('summary', {}).get('total_deletes', '?')}",
        f"- Risk distribution: `{plan.get('summary', {}).get('risk_distribution', {})}`",
        f"- Plan file: `<run_dir>/plan.md`",
        "",
        "_To execute the plan: re-run `system-scaffold` with `--execute` once you've reviewed `plan.md`._",
        "",
        "<!-- user -->",
        "_Add any system-level notes here. Preserved across regenerations._",
        "<!-- /user -->",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def write_scaffold(
    resolved: dict,
    plan: dict,
    taxonomy: dict,
    output_root: Path,
    commit: bool,
) -> dict:
    drives_cfg = taxonomy.get("drives", {})
    nodes = resolved.get("nodes", [])

    nodes_by_drive: dict[str, list[dict]] = defaultdict(list)
    for n in nodes:
        d = n.get("drive")
        if d:
            nodes_by_drive[d].append(n)

    # Custom categories present on each drive
    custom_cats_on_drive: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for n in nodes:
        cat = n.get("resolved_custom_category")
        d = n.get("drive")
        if cat and d:
            custom_cats_on_drive[d][cat].append(n["path"])

    qualifying = qualifying_folders(resolved, taxonomy)

    written: list[tuple[str, str]] = []

    skipped: list[tuple[str, str]] = []

    # 1. Drive root CONTEXT.md
    for letter in sorted(nodes_by_drive.keys()):
        cfg = drives_cfg.get(letter, {})
        if cfg.get("excluded_from_scaffold"):
            continue
        body = render_drive_root_context(
            letter=letter,
            drives_cfg=drives_cfg,
            nodes_on_drive=nodes_by_drive[letter],
            custom_cats_on_drive=custom_cats_on_drive.get(letter, {}),
            taxonomy=taxonomy,
        )
        if commit:
            target = Path(f"{letter}:\\CONTEXT.md")
            try:
                target.write_text(body, encoding="utf-8")
                written.append((f"{letter}:\\", str(target)))
            except (PermissionError, OSError) as e:
                # Drive root often needs admin. Fall back to per-drive .system\ subdir.
                fallback = Path(f"{letter}:\\.system\\CONTEXT.md")
                try:
                    fallback.parent.mkdir(parents=True, exist_ok=True)
                    fallback.write_text(body, encoding="utf-8")
                    written.append((f"{letter}:\\", str(fallback)))
                    skipped.append((str(target), f"drive root not writable; wrote to {fallback}"))
                except (PermissionError, OSError) as e2:
                    skipped.append((str(target), f"{e}; fallback also failed: {e2}"))
        else:
            target = output_root / "scaffold-preview" / letter / "CONTEXT.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
            written.append((f"{letter}:\\", str(target)))

    # 2. Per-folder CONTEXT.md for qualifying folders
    by_path = {_norm(n["path"]): n for n in nodes}
    qualifying_paths = {_norm(q["path"]) for q in qualifying}
    for q in qualifying:
        qpath = _norm(q["path"])
        # Skip drive roots — already handled above
        if len(qpath) <= 3:
            continue
        # Children (depth = q.depth + 1) for the top-contents table
        children = [n for n in nodes if _norm(n["path"]).startswith(qpath + "\\") and n["depth"] == q["depth"] + 1]
        body = render_folder_context(q, drives_cfg, taxonomy, children)
        if commit:
            target = Path(qpath) / "CONTEXT.md"
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding="utf-8")
            except (PermissionError, OSError) as e:
                print(f"[scaffold_writer] WARN: could not write {target}: {e}", file=sys.stderr)
                continue
        else:
            # Mirror under staging
            letter = _drive_letter_of(qpath)
            sub = qpath[3:].replace("\\", "/")  # strip "X:\"
            target = output_root / "scaffold-preview" / letter / sub / "CONTEXT.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        written.append((qpath, str(target)))

    # 3. Master INDEX.md — always to ~/.system/INDEX.md
    index_body = render_master_index(resolved, taxonomy, qualifying, plan, written)
    if commit:
        index_target = Path.home() / ".system" / "INDEX.md"
    else:
        index_target = output_root / "scaffold-preview" / "INDEX.md"
    index_target.parent.mkdir(parents=True, exist_ok=True)
    index_target.write_text(index_body, encoding="utf-8")

    return {
        "version": WRITER_VERSION,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "commit_mode": commit,
        "qualifying_folder_count": len(qualifying),
        "files_written_count": len(written) + 1,
        "files_skipped_count": len(skipped),
        "files_written": written + [(str(Path.home() / ".system" / "INDEX.md" if commit else "preview"), str(index_target))],
        "files_skipped": skipped,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="system-scaffold Stage 6 scaffold writer")
    parser.add_argument("run_dir", help="path to run directory (resolved.json, plan.json)")
    parser.add_argument("taxonomy", help="path to taxonomy.yaml")
    parser.add_argument("--commit", action="store_true", help="write to actual drive locations; default is staging preview")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    for f in ("resolved.json", "plan.json"):
        if not (run_dir / f).exists():
            print(f"[scaffold_writer] error: missing {run_dir / f}", file=sys.stderr)
            return 1

    resolved = json.load(open(run_dir / "resolved.json", "r", encoding="utf-8"))
    plan = json.load(open(run_dir / "plan.json", "r", encoding="utf-8"))
    with open(args.taxonomy, "r", encoding="utf-8") as f:
        taxonomy = yaml.safe_load(f)

    summary = write_scaffold(resolved, plan, taxonomy, run_dir, commit=args.commit)

    if not args.quiet:
        mode = "COMMIT (live drives)" if args.commit else "PREVIEW (staging)"
        print(f"[scaffold_writer] mode: {mode}", file=sys.stderr)
        print(f"[scaffold_writer] qualifying folders: {summary['qualifying_folder_count']}", file=sys.stderr)
        print(f"[scaffold_writer] files written: {summary['files_written_count']}", file=sys.stderr)
        if summary.get("files_skipped_count"):
            print(f"[scaffold_writer] files skipped or relocated: {summary['files_skipped_count']}", file=sys.stderr)
            for orig, reason in summary.get("files_skipped", []):
                print(f"  - {orig}: {reason}", file=sys.stderr)
        if not args.commit:
            print(f"[scaffold_writer] preview root: {run_dir / 'scaffold-preview'}", file=sys.stderr)
        else:
            print(f"[scaffold_writer] master INDEX: {Path.home() / '.system' / 'INDEX.md'}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
