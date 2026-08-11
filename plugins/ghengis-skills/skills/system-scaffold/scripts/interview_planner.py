"""
system-scaffold Stage 3 — Interview Planner.

Reads inventory.json + classifications.json + uncertain.json from prior stages.
Groups questions into batches by priority. Writes:
- questions.md: human-readable script the Claude session uses to drive the interview
- questions.json: machine-readable batch structure for reproducibility

This script does NOT conduct the interview — that happens in the Claude session
itself (the interview is conversational). This planner just decides WHAT to ask.

Pure Python stdlib.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

PLANNER_VERSION = "1"

# Thresholds (in bytes)
LARGE_UNCERTAIN_THRESHOLD = 10 * 1024**3   # 10 GB
PROJECT_LIKELY_TOP_N = 15
LARGE_UNCERTAIN_TOP_N = 20


def _gb(b: int) -> float:
    return b / 1024**3


def plan(
    inventory: dict,
    classifications: dict,
    uncertain: dict,
) -> dict:
    """Produce the question batch list."""

    drives = inventory.get("drives", [])
    classified = classifications.get("classified", [])
    uncertain_nodes = uncertain.get("nodes", [])

    batches: list[dict] = []

    # --- Batch 1: drive purposes ---
    drive_qs = []
    for d in drives:
        letter = d["letter"]
        used_gb = _gb(d["used_bytes"])
        free_gb = _gb(d["free_bytes"])
        hardware = d.get("friendly_name") or "(unknown)"
        media = f"{d.get('media_type','?')}/{d.get('bus_type','?')}"
        label = d.get("label", "") or "(no label)"
        drive_qs.append(
            {
                "id": f"drive-{letter}",
                "drive": letter,
                "hardware": hardware,
                "media": media,
                "label": label,
                "used_gb": round(used_gb, 1),
                "free_gb": round(free_gb, 1),
                "prompt": f"What is {letter}: drive for? (e.g., system, hot-storage, cold-archive, client-project, media, cloud)",
                "needs": ["role", "purpose", "custom_category (optional)"],
            }
        )
    batches.append(
        {
            "batch_id": "drives",
            "title": "Drive purposes",
            "description": "Establish what each drive is for. Many uncertain items below resolve automatically once drives are tagged.",
            "questions": drive_qs,
        }
    )

    # --- Batch 2: drive-inheritance preview ---
    # Group uncertain nodes by which drive they're on, so user can see how many
    # items each drive-purpose declaration would resolve.
    uncertain_by_drive: dict[str, list[dict]] = {}
    for n in uncertain_nodes:
        uncertain_by_drive.setdefault(n.get("drive", "?"), []).append(n)
    inheritance_preview = []
    for letter in sorted(uncertain_by_drive.keys()):
        items = uncertain_by_drive[letter]
        total_gb = sum(_gb(n["size_bytes"]) for n in items)
        # Find top distinct top-level uncertain ancestors on this drive
        top_paths = sorted(items, key=lambda n: -n["size_bytes"])[:5]
        inheritance_preview.append(
            {
                "drive": letter,
                "uncertain_count": len(items),
                "uncertain_total_gb": round(total_gb, 1),
                "sample_paths": [
                    {"path": n["path"], "size_gb": round(_gb(n["size_bytes"]), 2), "class": n["class"]}
                    for n in top_paths
                ],
            }
        )
    batches.append(
        {
            "batch_id": "drive-inheritance",
            "title": "Drive-purpose inheritance preview",
            "description": "After drive purposes are set in Batch 1, the following uncertain items will inherit their drive's role unless individually overridden.",
            "preview": inheritance_preview,
        }
    )

    # --- Batch 3: large uncertain items (>10 GB) ---
    large = sorted(
        [n for n in uncertain_nodes if n["size_bytes"] >= LARGE_UNCERTAIN_THRESHOLD],
        key=lambda n: -n["size_bytes"],
    )[:LARGE_UNCERTAIN_TOP_N]
    large_qs = [
        {
            "id": f"large-{i}",
            "path": n["path"],
            "drive": n["drive"],
            "size_gb": round(_gb(n["size_bytes"]), 2),
            "current_class": n["class"],
            "current_confidence": n["confidence"],
            "last_touched_days": n["last_touched_days"],
            "signals": n["signals"],
            "prompt": f"What is this? (current best guess: {n['class']}, confidence {n['confidence']})",
            "options": [
                "confirm current class",
                "different class (specify)",
                "inherit from drive purpose",
                "exclude from scaffold",
            ],
        }
        for i, n in enumerate(large)
    ]
    batches.append(
        {
            "batch_id": "large-uncertain",
            "title": f"Large uncertain items (>{LARGE_UNCERTAIN_THRESHOLD//1024**3} GB)",
            "description": "Individual review of the biggest uncertain items. These deserve direct user input because misclassifying them affects gigabytes.",
            "questions": large_qs,
        }
    )

    # --- Batch 4: project-likely batch ---
    project_likely = [
        c for c in classified
        if c["class"] == "project-likely"
    ]
    project_likely.sort(key=lambda c: -c["size_bytes"])
    project_likely_qs = [
        {
            "id": f"plikely-{i}",
            "path": c["path"],
            "size_gb": round(_gb(c["size_bytes"]), 3),
            "last_touched_days": c["last_touched_days"],
            "signals": c["signals"],
            "prompt": "Treat as project, or just scratch?",
            "options": ["project (active)", "project (stale)", "scratch / documents", "exclude"],
        }
        for i, c in enumerate(project_likely[:PROJECT_LIKELY_TOP_N])
    ]
    batches.append(
        {
            "batch_id": "project-likely",
            "title": f"Project-likely items (top {PROJECT_LIKELY_TOP_N} by size; {len(project_likely)} total)",
            "description": "Folders with secondary signals (README, .editorconfig, etc.) but no .git/package.json/etc. Could be projects without standard markers, or just collections of files.",
            "questions": project_likely_qs,
            "bulk_action_after_top_n": True,
            "remaining_count": max(0, len(project_likely) - PROJECT_LIKELY_TOP_N),
        }
    )

    # --- Batch 5: custom categories ---
    batches.append(
        {
            "batch_id": "custom-categories",
            "title": "Custom personal categories",
            "description": "Declare any personal categories beyond the built-in taxonomy (e.g., 'aaron-boland' for law firm work, 'knowstudio' for company projects, 'virgil-videos' for active video editing series).",
            "prompt": "List any personal category names you want to track, with a brief description of what counts and which drive(s) they live on.",
            "free_form": True,
        }
    )

    return {
        "version": PLANNER_VERSION,
        "planner": "system-scaffold/interview_planner.py",
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": {
            "inventory_run_started_at": inventory.get("run_started_at"),
            "classified_count": len(classified),
            "uncertain_count": uncertain.get("uncertain_count", len(uncertain_nodes)),
        },
        "batches": batches,
    }


def render_markdown(plan_doc: dict) -> str:
    """Render the question plan as a markdown interview script."""
    lines = [
        "# system-scaffold — Interview Questions",
        "",
        f"_Generated: {plan_doc['generated_at']}_  ",
        f"_Source classifications: {plan_doc['source']['classified_count']} nodes ({plan_doc['source']['uncertain_count']} uncertain)_",
        "",
        "The Claude session conducting the interview reads this file and asks the user the questions below, one batch at a time. Skip any batch the user has already answered in conversation.",
        "",
    ]

    for batch in plan_doc["batches"]:
        lines.append(f"## {batch['title']}")
        lines.append("")
        lines.append(batch.get("description", ""))
        lines.append("")

        if batch["batch_id"] == "drives":
            for q in batch["questions"]:
                lines.append(f"- **{q['drive']}: drive** — {q['hardware']} ({q['media']}), label `{q['label']}`, {q['used_gb']:.1f} GB used / {q['free_gb']:.1f} GB free")
                lines.append(f"  - Q: {q['prompt']}")
            lines.append("")

        elif batch["batch_id"] == "drive-inheritance":
            for row in batch["preview"]:
                lines.append(f"- **{row['drive']}:** {row['uncertain_count']} uncertain items ({row['uncertain_total_gb']:.1f} GB total)")
                for s in row["sample_paths"]:
                    lines.append(f"  - `{s['path']}` ({s['size_gb']} GB, current class: {s['class']})")
            lines.append("")

        elif batch["batch_id"] == "large-uncertain":
            for q in batch["questions"]:
                lines.append(f"- `{q['path']}` — {q['size_gb']} GB, last touched {q['last_touched_days']}d ago")
                lines.append(f"  - current: **{q['current_class']}** (conf {q['current_confidence']})")
                lines.append(f"  - signals: {', '.join(str(s) for s in q['signals'][:4])}")
                lines.append(f"  - Q: {q['prompt']}")
            lines.append("")

        elif batch["batch_id"] == "project-likely":
            for q in batch["questions"]:
                lines.append(f"- `{q['path']}` — {q['size_gb']} GB, last touched {q['last_touched_days']}d ago")
                lines.append(f"  - signals: {', '.join(str(s) for s in q['signals'][:3])}")
                lines.append(f"  - Q: {q['prompt']}")
            if batch.get("remaining_count"):
                lines.append(f"")
                lines.append(f"_{batch['remaining_count']} more project-likely items not shown. Bulk action: treat-all-as-X or skip._")
            lines.append("")

        elif batch["batch_id"] == "custom-categories":
            lines.append(batch["prompt"])
            lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="system-scaffold Stage 3 interview planner")
    parser.add_argument("run_dir", help="path to the run directory (contains inventory.json + classifications.json + uncertain.json)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir)
    inv_path = run_dir / "inventory.json"
    cls_path = run_dir / "classifications.json"
    unc_path = run_dir / "uncertain.json"

    for p in (inv_path, cls_path, unc_path):
        if not p.exists():
            print(f"[interview_planner] error: missing {p}", file=sys.stderr)
            return 1

    inventory = json.load(open(inv_path, "r", encoding="utf-8"))
    classifications = json.load(open(cls_path, "r", encoding="utf-8"))
    uncertain = json.load(open(unc_path, "r", encoding="utf-8"))

    plan_doc = plan(inventory, classifications, uncertain)

    questions_json = run_dir / "questions.json"
    questions_md = run_dir / "questions.md"

    with open(questions_json, "w", encoding="utf-8") as f:
        json.dump(plan_doc, f, indent=2)
    with open(questions_md, "w", encoding="utf-8") as f:
        f.write(render_markdown(plan_doc))

    if not args.quiet:
        total_qs = sum(
            len(b.get("questions", []))
            for b in plan_doc["batches"]
        )
        print(f"[interview_planner] {len(plan_doc['batches'])} batches, {total_qs} structured questions", file=sys.stderr)
        print(f"[interview_planner] wrote {questions_json}", file=sys.stderr)
        print(f"[interview_planner] wrote {questions_md}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
