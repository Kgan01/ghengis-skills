"""
system-scaffold Stage 5 — Move Plan.

Reads resolved.json + dependencies.json + taxonomy.yaml. Produces:
- plan.json: structured list of operations (move/delete/special) with risk
- plan.md: human-readable review document

Operations are proposed but NOT executed. Stage 7 (Execute) is opt-in.

Planning rules:
1. Each node with resolved_class != current-drive's role-implied class is a
   move candidate (target drive = first drive that accepts that class).
2. If user-resolved action=delete → delete op.
3. Class to target-drive mapping driven by taxonomy.yaml drive accept_classes.
4. Risk tiering:
   - safe: no dependencies in dependencies.json
   - with-care: deps that can be auto-handled (env vars, shortcuts)
   - blocked: deps requiring manual intervention (services, app paths,
     scheduled tasks, WSL, Docker, COM CLSID)
5. Special procedures: dev-vm (WSL --export), Docker (settings.json),
   recognized via class/path.
6. Plan never proposes a move whose target == source.
7. Nested candidates collapse: if both A and A/B are candidates with the
   same target drive, only A is moved.

Pure Python stdlib + PyYAML.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path
from collections import defaultdict

import yaml

PLANNER_VERSION = "2"  # this is the system-wide planner, distinct from treefile-organizer/scripts/planner.py


# Risk-tier mapping for reference types
REF_TYPE_RISK = {
    # auto-handleable
    "env_var": "with-care",
    "shortcut": "with-care",
    "registry": "with-care",
    "reparse_point": "with-care",
    "onedrive_sync": "with-care",
    "autorun": "with-care",
    "app_path": "with-care",
    "defender_exclusion": "with-care",
    "file_association": "with-care",
    # require manual intervention
    "service": "blocked",
    "scheduled_task": "blocked",
    "com_class": "blocked",
    "wsl_distro": "blocked",
    "docker_settings": "blocked",
}


# Special procedure classes
SPECIAL_PROCEDURE_CLASSES = {"dev-vm"}


def _norm(p: str) -> str:
    if not p:
        return ""
    return p.replace("/", "\\").rstrip("\\").lower()


def _max_risk(refs: list[dict]) -> str:
    """Worst risk across a reference list. 'blocked' > 'with-care' > 'safe'."""
    order = {"safe": 0, "with-care": 1, "blocked": 2}
    worst = "safe"
    for r in refs:
        rt = r.get("type", "")
        rr = REF_TYPE_RISK.get(rt, "with-care")
        if order[rr] > order[worst]:
            worst = rr
    return worst


def _accept_matches(accepts: list, cls: str, custom_cat: str | None) -> bool:
    """True if an accept_classes entry matches this class/category.

    Prefix match: 'media-video' in accepts matches 'media-video', 'media-video-cold',
    'media-video-active', etc. (suffix variants).
    Custom category exact match too.
    """
    if custom_cat and custom_cat in accepts:
        return True
    for a in accepts:
        if cls == a or cls.startswith(a + "-"):
            return True
    return False


def find_target_drive(resolved_class: str, custom_cat: str | None, taxonomy: dict) -> str | None:
    """First non-excluded drive whose accept_classes accepts this class/category.

    Drives with handling=untouched-by-default are excluded as targets unless
    the move is for their declared custom category (so e.g. aaron-boland items
    can still land on I, but generic 'documents' won't).
    """
    drives = taxonomy.get("drives", {})

    def is_disqualified(cfg: dict, for_custom_cat: str | None) -> bool:
        if cfg.get("excluded_from_scaffold"):
            return True
        if cfg.get("handling") == "untouched-by-default":
            # Only matchable when targeting the drive's own custom category
            accept_cats = [a for a in (cfg.get("accept_classes") or []) if a == for_custom_cat]
            if not accept_cats:
                return True
        return False

    # First pass: custom_category exact match
    if custom_cat:
        for letter, cfg in drives.items():
            if is_disqualified(cfg, custom_cat):
                continue
            if custom_cat in (cfg.get("accept_classes") or []):
                return letter

    # Prefer the MOST SPECIFIC class match (longer accept entry wins) so
    # 'media-video-cold' picks Z (has 'media-video-cold') over E (has 'media-video').
    best: tuple[int, str] | None = None
    for letter, cfg in drives.items():
        if is_disqualified(cfg, custom_cat):
            continue
        for a in (cfg.get("accept_classes") or []):
            if resolved_class == a or resolved_class.startswith(a + "-"):
                score = (1 if resolved_class == a else 0) * 1000 + len(a)
                if best is None or score > best[0]:
                    best = (score, letter)
    return best[1] if best else None


def collapse_nested(candidates: list[dict]) -> list[dict]:
    """Resolve parent/child move conflicts:

    - Parent and child move to the SAME drive → drop child (parent move handles it).
    - Parent and child move to DIFFERENT drives:
        - If parent is user-resolved → drop child (user's intent wins).
        - If child is user-resolved → drop parent (preserve explicit child move,
          parent stays in place so the child can be removed cleanly first).
        - Otherwise → drop child, KEEP parent. The parent move covers the
          whole tree including the child; the classifier-derived child
          target is treated as advisory rather than overriding the parent.
          Without this rule, dropping the parent leaves most of the content
          stranded on the source drive (e.g., ccxt parent → Y was dropped
          because ccxt/python child → Z; net effect: nothing moved).
    """
    by_path = {_norm(c["path"]): c for c in candidates}
    paths_sorted = sorted(by_path.keys(), key=lambda p: (len(p), p))
    dropped: set[str] = set()

    for p in paths_sorted:
        if p in dropped:
            continue
        parent = by_path[p]
        parent_target = parent.get("_target_drive")
        parent_is_user = parent.get("resolution_source") == "user"

        for q in paths_sorted:
            if q == p or q in dropped:
                continue
            if not q.startswith(p + "\\"):
                continue
            child = by_path[q]
            child_target = child.get("_target_drive")
            child_is_user = child.get("resolution_source") == "user"
            if child_target == parent_target:
                dropped.add(q)
            elif parent_is_user:
                dropped.add(q)
            elif child_is_user:
                dropped.add(p)
                break
            else:
                # Both classifier-derived, conflicting targets: parent wins.
                dropped.add(q)

    return [by_path[p] for p in paths_sorted if p not in dropped]


def plan_operations(
    resolved: dict,
    dependencies: dict,
    taxonomy: dict,
) -> dict:
    nodes = resolved.get("nodes", [])
    deps_by_path = {_norm(d["path"]): d for d in dependencies.get("dependencies", [])}

    # Build candidate list — anything with a non-trivial resolved class that's
    # not on a drive that already accepts it.
    drives = taxonomy.get("drives", {})

    def drive_accepts(letter: str, cls: str, custom_cat: str | None) -> bool:
        cfg = drives.get(letter, {})
        if cfg.get("excluded_from_scaffold"):
            return False
        accepts = cfg.get("accept_classes") or []
        return _accept_matches(accepts, cls, custom_cat)

    candidates = []
    deletes = []

    for n in nodes:
        cls = n.get("resolved_class")
        if not cls:
            continue

        # Never plan operations on drive roots — they represent the whole drive,
        # not a movable item.
        if cls == "drive-root" or n.get("depth", 0) == 0:
            continue

        path = n["path"]
        current_drive = n.get("drive")
        custom_cat = n.get("resolved_custom_category")
        action = n.get("resolved_action")

        # Honor per-drive handling rule "untouched-by-default" — no moves FROM
        # such drives unless the user explicitly overrode via a per-path resolution.
        src_cfg = drives.get(current_drive, {})
        if src_cfg.get("handling") == "untouched-by-default":
            if n.get("resolution_source") != "user" and action != "delete":
                continue

        # Explicit delete from user interview
        if action == "delete":
            deletes.append(n)
            continue

        # Drives that EXPLICITLY accept this class as a target
        target_drive_from_user = n.get("resolved_target_drive")
        if target_drive_from_user:
            target = target_drive_from_user
        else:
            target = find_target_drive(cls, custom_cat, taxonomy)

        # Skip if no target found, or current drive already accepts it
        if not target:
            continue
        if drive_accepts(current_drive, cls, custom_cat) and target != current_drive:
            # Current drive accepts it AND user didn't override — leave in place.
            continue
        if target == current_drive:
            continue

        n2 = dict(n)
        n2["_target_drive"] = target
        candidates.append(n2)

    # Collapse nested same-target moves
    candidates = collapse_nested(candidates)

    # Build operations
    operations = []
    op_id_counter = {"del": 0, "mv": 0, "special": 0}

    # Deletes first
    delete_total_bytes = 0
    for n in deletes:
        op_id_counter["del"] += 1
        delete_total_bytes += n.get("size_bytes", 0)
        operations.append(
            {
                "op_id": f"del-{op_id_counter['del']:03d}",
                "type": "delete",
                "path": n["path"],
                "drive": n.get("drive"),
                "size_bytes": n.get("size_bytes", 0),
                "class": n.get("resolved_class"),
                "risk": "safe",
                "reason": n.get("resolved_action") or "user-resolved-delete",
            }
        )

    # Moves
    for cand in candidates:
        cls = cand["resolved_class"]
        from_path = cand["path"]
        target = cand["_target_drive"]
        custom_cat = cand.get("resolved_custom_category")

        # Compute destination path: <target>:\<category-folder>\<basename>
        basename = from_path.rstrip("\\").split("\\")[-1]
        category_folder = _category_subdir(cls, custom_cat, taxonomy)
        to_path = f"{target}:\\{category_folder}\\{basename}" if category_folder else f"{target}:\\{basename}"

        # Dependencies for this candidate (or any ancestor candidate)
        refs = deps_by_path.get(_norm(from_path), {}).get("references", [])
        risk = _max_risk(refs) if refs else "safe"

        # Special procedure?
        is_special = cls in SPECIAL_PROCEDURE_CLASSES
        op_type = "special" if is_special else "move"

        procedure = "copy-verify-delete"
        if cls == "dev-vm":
            procedure = "wsl-export-import"

        # Build the op
        if op_type == "special":
            op_id_counter["special"] += 1
            op_id = f"special-{op_id_counter['special']:03d}"
        else:
            op_id_counter["mv"] += 1
            op_id = f"mv-{op_id_counter['mv']:03d}"

        operations.append(
            {
                "op_id": op_id,
                "type": op_type,
                "from": from_path,
                "to": to_path,
                "drive_from": cand.get("drive"),
                "drive_to": target,
                "size_bytes": cand.get("size_bytes", 0),
                "class": cls,
                "custom_category": custom_cat,
                "procedure": procedure,
                "risk": risk,
                "last_touched_days": cand.get("last_touched_days"),
                "references": refs,
            }
        )

    # Drive impact summary
    drive_impact = compute_drive_impact(operations, resolved, taxonomy)

    # Summary
    total_moves = sum(1 for o in operations if o["type"] in ("move", "special"))
    total_deletes = sum(1 for o in operations if o["type"] == "delete")
    risk_distribution = defaultdict(int)
    for o in operations:
        risk_distribution[o["risk"]] += 1

    return {
        "version": PLANNER_VERSION,
        "planner": "system-scaffold/planner.py",
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": {
            "resolved_ran_at": resolved.get("ran_at"),
            "dependencies_ran_at": dependencies.get("ran_at"),
            "taxonomy_generated_at": taxonomy.get("generated_at"),
        },
        "summary": {
            "total_operations": len(operations),
            "total_moves": total_moves,
            "total_deletes": total_deletes,
            "delete_bytes": delete_total_bytes,
            "risk_distribution": dict(risk_distribution),
        },
        "drive_impact": drive_impact,
        "operations": operations,
    }


def _category_subdir(cls: str, custom_cat: str | None, taxonomy: dict) -> str:
    """Subdirectory under the target drive root for this class."""
    # Custom categories sometimes pin a specific subdir via locations_target
    if custom_cat:
        cats = taxonomy.get("custom_categories", {})
        cat_cfg = cats.get(custom_cat, {})
        targets = cat_cfg.get("locations_target", [])
        if targets:
            t = targets[0]
            # Strip drive letter prefix to get the relative path
            if len(t) > 3 and t[1:3] == ":\\":
                return t[3:].rstrip("\\")
            return t.lstrip("\\")
    # Dev-tool convention
    if cls == "dev-tool":
        return "tools"
    if cls == "tools-archive":
        return "tools-archive"
    if cls.startswith("media-video"):
        return "media\\video"
    if cls.startswith("media-photo"):
        return "media\\photo"
    if cls.startswith("media-audio"):
        return "media\\audio"
    if cls in ("archive",):
        return "archive"
    if cls in ("project-active", "project-stale"):
        return "projects"
    if cls == "dev-models":
        return "dev-models"
    if cls == "documents":
        return "documents"
    return ""  # drive root


def compute_drive_impact(operations: list[dict], resolved: dict, taxonomy: dict) -> dict:
    """For each known drive, approximate the change in used/free bytes."""
    # Per-drive baseline from inventory (resolved doesn't carry it; we approximate
    # by summing all resolved node sizes per drive — close enough for planning).
    impact: dict[str, dict] = {}
    drives = list(taxonomy.get("drives", {}).keys())
    for d in drives:
        impact[d] = {"bytes_removed": 0, "bytes_added": 0, "operations_affecting": 0}

    for op in operations:
        if op["type"] == "delete":
            d = op.get("drive")
            if d in impact:
                impact[d]["bytes_removed"] += op.get("size_bytes", 0)
                impact[d]["operations_affecting"] += 1
        else:
            df = op.get("drive_from")
            dt = op.get("drive_to")
            sz = op.get("size_bytes", 0)
            if df in impact:
                impact[df]["bytes_removed"] += sz
                impact[df]["operations_affecting"] += 1
            if dt in impact:
                impact[dt]["bytes_added"] += sz
                impact[dt]["operations_affecting"] += 1
    return impact


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_markdown(plan: dict) -> str:
    s = plan["summary"]
    lines = [
        "# system-scaffold — Move Plan",
        "",
        f"_Generated: {plan['generated_at']}_",
        "",
        "## Summary",
        "",
        f"- **Total operations**: {s['total_operations']}",
        f"- **Moves**: {s['total_moves']}",
        f"- **Deletes**: {s['total_deletes']} ({s['delete_bytes']/1e9:.2f} GB)",
        f"- **Risk distribution**: {dict(s['risk_distribution'])}",
        "",
        "## Drive impact (estimated)",
        "",
        "| Drive | Bytes removed | Bytes added | Ops |",
        "|---|---|---|---|",
    ]
    for d, im in plan["drive_impact"].items():
        lines.append(
            f"| {d} | {im['bytes_removed']/1e9:7.2f} GB | {im['bytes_added']/1e9:7.2f} GB | {im['operations_affecting']} |"
        )

    # Operations grouped by risk + type
    by_group: dict[str, list[dict]] = defaultdict(list)
    for op in plan["operations"]:
        key = f"{op['risk']} / {op['type']}"
        by_group[key].append(op)

    risk_order = ["safe", "with-care", "blocked"]
    type_order = ["delete", "move", "special"]
    ordered = []
    for r in risk_order:
        for t in type_order:
            k = f"{r} / {t}"
            if by_group.get(k):
                ordered.append((r, t, by_group[k]))

    for r, t, ops in ordered:
        lines.append("")
        lines.append(f"## {r.upper()} — {t} ({len(ops)} ops, {sum(o.get('size_bytes',0) for o in ops)/1e9:.2f} GB)")
        lines.append("")
        for o in sorted(ops, key=lambda x: -x.get("size_bytes", 0)):
            gb = o.get("size_bytes", 0) / 1e9
            if t == "delete":
                lines.append(f"- `{o['op_id']}` **delete** `{o['path']}` — {gb:.2f} GB ({o.get('reason','')})")
            else:
                refs_summary = ""
                if o.get("references"):
                    refs_summary = f"  - **{len(o['references'])} dependencies**: {', '.join(set(r['type'] for r in o['references']))}"
                lines.append(f"- `{o['op_id']}` **{t}** `{o['from']}` → `{o['to']}` — {gb:.2f} GB, {o.get('procedure','')}")
                if refs_summary:
                    lines.append(refs_summary)
                if o.get("class"):
                    lines.append(f"  - class: {o['class']}  custom: {o.get('custom_category') or '-'}  last_touched: {o.get('last_touched_days')}d")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="system-scaffold Stage 5 move planner")
    parser.add_argument("run_dir", help="path to run dir with resolved.json + dependencies.json")
    parser.add_argument("taxonomy", help="path to taxonomy.yaml")
    parser.add_argument("--output-dir", help="output dir (default: run_dir)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    resolved_path = run_dir / "resolved.json"
    dep_path = run_dir / "dependencies.json"
    tax_path = Path(args.taxonomy)

    for p in (resolved_path, dep_path, tax_path):
        if not p.exists():
            print(f"[planner] error: missing {p}", file=sys.stderr)
            return 1

    resolved = json.load(open(resolved_path, "r", encoding="utf-8"))
    dependencies = json.load(open(dep_path, "r", encoding="utf-8"))
    with open(tax_path, "r", encoding="utf-8") as f:
        taxonomy = yaml.safe_load(f)

    out_dir = Path(args.output_dir) if args.output_dir else run_dir

    plan = plan_operations(resolved, dependencies, taxonomy)

    with open(out_dir / "plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    with open(out_dir / "plan.md", "w", encoding="utf-8") as f:
        f.write(render_markdown(plan))

    if not args.quiet:
        s = plan["summary"]
        print(f"[planner] total operations: {s['total_operations']}", file=sys.stderr)
        print(f"[planner]   moves: {s['total_moves']}", file=sys.stderr)
        print(f"[planner]   deletes: {s['total_deletes']} ({s['delete_bytes']/1e9:.2f} GB)", file=sys.stderr)
        print(f"[planner]   risk distribution: {s['risk_distribution']}", file=sys.stderr)
        print("[planner] drive impact (GB):", file=sys.stderr)
        for d, im in plan["drive_impact"].items():
            print(f"  {d}: removed={im['bytes_removed']/1e9:6.2f}  added={im['bytes_added']/1e9:6.2f}  ops={im['operations_affecting']}", file=sys.stderr)
        print(f"[planner] wrote {out_dir / 'plan.json'}", file=sys.stderr)
        print(f"[planner] wrote {out_dir / 'plan.md'}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
