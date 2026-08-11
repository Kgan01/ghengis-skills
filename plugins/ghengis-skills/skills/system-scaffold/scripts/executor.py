"""
system-scaffold Stage 7 — Executor (dry-run capable).

Reads plan.json from Stage 5. In --dry-run mode (default), simulates each
operation and reports what would happen: source/target validity, free space
checks, locked-handle warnings, time estimates. No filesystem writes.

In --execute mode (NOT yet implemented), would perform copy → verify → delete
per operation with per-batch rollback. v1 ships dry-run only.

Pure Python stdlib + PyYAML.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

EXECUTOR_VERSION = "1"


# Throughput estimates by drive media/bus (MB/s)
THROUGHPUT_MBS = {
    ("SSD", "NVMe"): 1500,
    ("SSD", "SATA"): 400,
    ("HDD", "SATA"): 120,
    ("HDD", "USB"): 80,
    ("HDD", None): 90,
    ("SSD", "USB"): 250,
}


def _norm(p: str) -> str:
    return p.replace("/", "\\").rstrip("\\")


def _human_gb(b: int) -> str:
    if b >= 1024**3:
        return f"{b/1024**3:.2f} GB"
    if b >= 1024**2:
        return f"{b/1024**2:.1f} MB"
    return f"{b/1024:.1f} KB"


def _human_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds/60:.1f}m"
    return f"{seconds/3600:.1f}h"


def get_drive_throughput_mbs(media: str | None, bus: str | None) -> int:
    return THROUGHPUT_MBS.get((media, bus)) or THROUGHPUT_MBS.get((media, None), 100)


def get_drive_metadata() -> dict[str, dict]:
    """Map drive letter -> {media_type, bus_type, free_bytes, total_bytes}."""
    out: dict[str, dict] = {}
    for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        root = f"{letter}:\\"
        if not Path(root).exists():
            continue
        try:
            usage = shutil.disk_usage(root)
            out[letter] = {
                "free_bytes": usage.free,
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "media_type": None,
                "bus_type": None,
            }
        except OSError:
            continue

    # Enrich with media/bus via PowerShell
    ps = r"""
$partitions = Get-Partition | Where-Object { $_.DriveLetter }
$result = @()
foreach ($p in $partitions) {
    $physical = Get-PhysicalDisk -DeviceNumber $p.DiskNumber -ErrorAction SilentlyContinue
    $result += [pscustomobject]@{
        Letter    = "$($p.DriveLetter)"
        MediaType = "$($physical.MediaType)"
        BusType   = "$($physical.BusType)"
    }
}
$result | ConvertTo-Json -Compress
"""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, text=True, timeout=30, check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            if isinstance(data, dict):
                data = [data]
            for r in data:
                letter = r.get("Letter", "").strip().upper()
                if letter in out:
                    out[letter]["media_type"] = r.get("MediaType") or None
                    out[letter]["bus_type"] = r.get("BusType") or None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return out


def check_locked_handles(paths: list[str], timeout: int = 60) -> dict[str, str]:
    """Lightweight check: which paths likely have open handles?

    Uses PowerShell to look for any process whose modules or working dir
    overlap with each path. False positives possible; false negatives common.
    Sufficient as a 'warn before move' guard but NOT proof a path is free.
    """
    if not paths:
        return {}
    ps_paths = ",".join(f"'{p.replace(chr(39), chr(39)+chr(39))}'" for p in paths)
    ps = rf"""
$paths = @({ps_paths})
$results = @{{}}
$procs = Get-Process -ErrorAction SilentlyContinue
foreach ($p in $paths) {{
    $hit = $null
    foreach ($proc in $procs) {{
        try {{
            $exe = $proc.Path
            if ($exe -and $exe.StartsWith($p, [System.StringComparison]::OrdinalIgnoreCase)) {{
                $hit = "process: $($proc.ProcessName) (PID $($proc.Id))"
                break
            }}
        }} catch {{ }}
    }}
    if ($hit) {{ $results[$p] = $hit }}
}}
$results | ConvertTo-Json -Compress -Depth 2
"""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            if isinstance(data, dict):
                return data
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return {}


def simulate_op(op: dict, drive_meta: dict, locked: dict) -> dict:
    """Return simulation result for a single operation."""
    result = {
        "op_id": op["op_id"],
        "type": op["type"],
        "size_bytes": op.get("size_bytes", 0),
        "would_proceed": True,
        "warnings": [],
        "blockers": [],
        "estimated_seconds": 0,
    }

    if op["type"] == "delete":
        src = op["path"]
        if not Path(src).exists():
            result["blockers"].append(f"source does not exist: {src}")
            result["would_proceed"] = False
        return result

    # Move / special
    src = op["from"]
    dst = op["to"]

    # Source exists?
    if not Path(src).exists():
        result["blockers"].append(f"source does not exist: {src}")
        result["would_proceed"] = False
        return result

    # Target path collision?
    if Path(dst).exists():
        result["blockers"].append(f"target already exists: {dst}")
        result["would_proceed"] = False

    # Target drive free space?
    target_drive = op.get("drive_to") or _drive_from(dst)
    src_drive = op.get("drive_from") or _drive_from(src)
    size = op.get("size_bytes", 0)
    if target_drive:
        td_meta = drive_meta.get(target_drive, {})
        free = td_meta.get("free_bytes", 0)
        if size > free:
            result["blockers"].append(
                f"target drive {target_drive}: only has {_human_gb(free)} free, op needs {_human_gb(size)}"
            )
            result["would_proceed"] = False
        elif size > free * 0.9:
            result["warnings"].append(
                f"target drive {target_drive}: would use {size/free*100:.0f}% of free space"
            )

    # Locked handles
    if src in locked:
        result["warnings"].append(f"source path has open handles: {locked[src]}")

    # Time estimate — slowest of source-read or target-write throughput
    src_meta = drive_meta.get(src_drive, {}) if src_drive else {}
    tgt_meta = drive_meta.get(target_drive, {}) if target_drive else {}
    src_mbs = get_drive_throughput_mbs(src_meta.get("media_type"), src_meta.get("bus_type"))
    tgt_mbs = get_drive_throughput_mbs(tgt_meta.get("media_type"), tgt_meta.get("bus_type"))
    bottleneck = min(src_mbs, tgt_mbs)
    result["estimated_seconds"] = size / (bottleneck * 1024 * 1024) if bottleneck else 0

    # Procedure-specific notes
    if op.get("procedure") == "wsl-export-import":
        result["warnings"].append("WSL distro — manual wsl --export / --import procedure required")
        result["would_proceed"] = False  # not auto-handleable

    # Refs that would need manual fixing
    if op.get("references"):
        result["warnings"].append(
            f"{len(op['references'])} dependencies need handling: " + ", ".join(set(r["type"] for r in op["references"]))
        )

    return result


def _drive_from(path: str) -> str | None:
    p = _norm(path)
    if len(p) >= 2 and p[1] == ":":
        return p[0].upper()
    return None


def simulate_plan(plan: dict, taxonomy: dict, check_locks: bool) -> dict:
    drive_meta = get_drive_metadata()
    ops = plan.get("operations", [])

    # Pre-check locks (single batched PowerShell call)
    if check_locks:
        src_paths = []
        for op in ops:
            p = op.get("from") or op.get("path")
            if p:
                src_paths.append(p)
        locked = check_locked_handles(src_paths)
    else:
        locked = {}

    results = []
    for op in ops:
        r = simulate_op(op, drive_meta, locked)
        results.append(r)

    # Aggregate
    proceed = [r for r in results if r["would_proceed"]]
    blocked = [r for r in results if not r["would_proceed"]]
    with_warnings = [r for r in results if r["warnings"] and r["would_proceed"]]

    total_bytes_proceed = sum(r["size_bytes"] for r in proceed)
    total_seconds = sum(r["estimated_seconds"] for r in proceed)

    # Per-drive impact (estimated)
    by_drive: dict[str, dict] = defaultdict(lambda: {"removed_bytes": 0, "added_bytes": 0, "ops": 0})
    for op, r in zip(ops, results):
        if not r["would_proceed"]:
            continue
        if op["type"] == "delete":
            d = _drive_from(op["path"])
            if d:
                by_drive[d]["removed_bytes"] += op.get("size_bytes", 0)
                by_drive[d]["ops"] += 1
        else:
            df = op.get("drive_from")
            dt = op.get("drive_to")
            sz = op.get("size_bytes", 0)
            if df:
                by_drive[df]["removed_bytes"] += sz
                by_drive[df]["ops"] += 1
            if dt:
                by_drive[dt]["added_bytes"] += sz

    # Resulting free space per drive
    for d, impact in by_drive.items():
        meta = drive_meta.get(d, {})
        free_before = meta.get("free_bytes", 0)
        impact["free_before"] = free_before
        impact["free_after_estimated"] = free_before + impact["removed_bytes"] - impact["added_bytes"]

    return {
        "version": EXECUTOR_VERSION,
        "mode": "dry-run",
        "ran_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "summary": {
            "total_ops": len(ops),
            "would_proceed": len(proceed),
            "blocked": len(blocked),
            "with_warnings": len(with_warnings),
            "total_bytes_proceed": total_bytes_proceed,
            "estimated_total_seconds": total_seconds,
            "locked_paths_found": len(locked),
        },
        "drive_impact": dict(by_drive),
        "per_op": [
            {
                "op_id": r["op_id"],
                "type": r["type"],
                "size_bytes": r["size_bytes"],
                "would_proceed": r["would_proceed"],
                "warnings": r["warnings"],
                "blockers": r["blockers"],
                "estimated_seconds": r["estimated_seconds"],
            }
            for r in results
        ],
    }


def render_dry_run_md(plan: dict, sim: dict) -> str:
    s = sim["summary"]
    lines = [
        "# system-scaffold — Stage 7 dry run",
        "",
        f"_Generated: {sim['ran_at']}_  ",
        f"_Source plan: {plan.get('generated_at')}_",
        "",
        "## Outcome",
        "",
        f"- **Would proceed**: {s['would_proceed']} / {s['total_ops']} ops",
        f"- **Blocked**: {s['blocked']}",
        f"- **With warnings**: {s['with_warnings']}",
        f"- **Bytes that would move/delete**: {_human_gb(s['total_bytes_proceed'])}",
        f"- **Estimated total time** (if executed sequentially): {_human_time(s['estimated_total_seconds'])}",
        f"- **Paths with open handles detected**: {s['locked_paths_found']}",
        "",
        "## Per-drive impact (estimated)",
        "",
        "| Drive | Free before | Removed | Added | Free after | Ops |",
        "|---|---|---|---|---|---|",
    ]
    for d, im in sim["drive_impact"].items():
        lines.append(
            f"| {d} | {_human_gb(im['free_before'])} | {_human_gb(im['removed_bytes'])} | {_human_gb(im['added_bytes'])} | {_human_gb(im['free_after_estimated'])} | {im['ops']} |"
        )

    # Blockers
    blockers = [r for r in sim["per_op"] if not r["would_proceed"]]
    if blockers:
        lines += ["", f"## Blocked ops ({len(blockers)})", ""]
        for r in blockers[:30]:
            blockers_str = "; ".join(r["blockers"])
            lines.append(f"- `{r['op_id']}` ({r['type']}, {_human_gb(r['size_bytes'])}): {blockers_str}")
        if len(blockers) > 30:
            lines.append(f"_… {len(blockers)-30} more …_")

    # Warnings
    warn_ops = [r for r in sim["per_op"] if r["warnings"] and r["would_proceed"]]
    if warn_ops:
        lines += ["", f"## Ops with warnings ({len(warn_ops)})", ""]
        for r in warn_ops[:30]:
            w = "; ".join(r["warnings"])
            lines.append(f"- `{r['op_id']}` ({r['type']}, {_human_gb(r['size_bytes'])}): {w}")
        if len(warn_ops) > 30:
            lines.append(f"_… {len(warn_ops)-30} more …_")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Real execution (Stage 7 v1) — per-op safe execute
# ---------------------------------------------------------------------------


def _dir_size_and_count(path: Path) -> tuple[int, int]:
    """Return (total_bytes, file_count) for a directory tree."""
    total = 0
    count = 0
    try:
        for entry in path.rglob("*"):
            try:
                st = entry.lstat()
                # Skip symlinks/junctions
                import stat as _stat
                if _stat.S_ISREG(st.st_mode):
                    total += st.st_size
                    count += 1
            except OSError:
                pass
    except OSError:
        pass
    return total, count


def execute_op(op: dict, drive_meta: dict, audit_log: Path) -> dict:
    """Execute a single op (move or delete). Returns result dict.

    Uses robocopy /MOVE for cross-drive moves (handles reserved names like nul),
    shutil.move for same-drive (atomic rename), and shutil.rmtree for deletes.
    Verifies post-move by comparing source-pre size+count to target post.
    """
    result = {
        "op_id": op["op_id"],
        "type": op["type"],
        "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "status": "pending",
        "errors": [],
        "size_bytes": op.get("size_bytes", 0),
    }

    def _log(entry: dict) -> None:
        try:
            with open(audit_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError as e:
            print(f"[executor] WARN: could not write audit log: {e}", file=sys.stderr)

    # ----- DELETE -----
    if op["type"] == "delete":
        src = Path(op["path"])
        result["from"] = str(src)
        if not src.exists():
            result["status"] = "skipped"
            result["errors"].append("source already absent")
            result["finished_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            _log(result)
            return result
        try:
            import shutil
            if src.is_dir():
                shutil.rmtree(src)
            else:
                src.unlink()
            result["status"] = "succeeded"
        except OSError as e:
            result["status"] = "failed"
            result["errors"].append(f"delete failed: {e}")
        result["finished_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        _log(result)
        return result

    # ----- MOVE / SPECIAL -----
    src = Path(op["from"])
    dst = Path(op["to"])
    result["from"] = str(src)
    result["to"] = str(dst)

    # Pre-flight
    if not src.exists():
        result["status"] = "skipped"
        result["errors"].append(f"source does not exist: {src}")
        _log(result | {"finished_at": result["started_at"]})
        return result
    if dst.exists():
        result["status"] = "skipped"
        result["errors"].append(f"target already exists: {dst}")
        _log(result | {"finished_at": result["started_at"]})
        return result

    drive_from = op.get("drive_from") or _drive_from(str(src))
    drive_to = op.get("drive_to") or _drive_from(str(dst))
    sz = op.get("size_bytes", 0)
    tgt_free = drive_meta.get(drive_to, {}).get("free_bytes", 0)
    if sz > tgt_free:
        result["status"] = "blocked"
        result["errors"].append(f"target drive {drive_to} only has {_human_gb(tgt_free)} free, need {_human_gb(sz)}")
        _log(result | {"finished_at": result["started_at"]})
        return result

    # Special procedure
    if op.get("procedure") == "wsl-export-import":
        result["status"] = "blocked"
        result["errors"].append("WSL distro — requires manual wsl --export / wsl --import; not auto-executable")
        _log(result | {"finished_at": result["started_at"]})
        return result

    # Snapshot source for verification
    pre_size, pre_count = _dir_size_and_count(src) if src.is_dir() else (src.stat().st_size, 1)

    # Ensure target parent exists
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        result["status"] = "failed"
        result["errors"].append(f"could not create target parent: {e}")
        result["finished_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        _log(result)
        return result

    # Execute the move
    if drive_from == drive_to and src.is_dir():
        # Same-drive directory: atomic rename
        try:
            import shutil
            shutil.move(str(src), str(dst))
            result["method"] = "same-drive-rename"
        except OSError as e:
            result["status"] = "failed"
            result["errors"].append(f"shutil.move failed: {e}")
            result["finished_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            _log(result)
            return result
    elif src.is_dir():
        # Cross-drive directory: robocopy /MOVE handles edge cases (nul, long paths)
        result["method"] = "robocopy-move"
        rc = subprocess.run(
            ["robocopy", str(src), str(dst), "/MOVE", "/E", "/R:1", "/W:1", "/NP", "/NFL", "/NDL", "/NJH", "/NJS"],
            capture_output=True, text=True, timeout=3600, check=False,
        )
        # robocopy exit codes: <8 means success (1-7 indicate copies happened);
        # >=8 means failures
        if rc.returncode >= 8:
            result["status"] = "failed"
            result["errors"].append(f"robocopy exit {rc.returncode}: {rc.stderr.strip()[:200]}")
            result["finished_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            _log(result)
            return result
    else:
        # Single file
        try:
            import shutil
            shutil.move(str(src), str(dst))
            result["method"] = "shutil-file-move"
        except OSError as e:
            result["status"] = "failed"
            result["errors"].append(f"shutil.move (file) failed: {e}")
            result["finished_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            _log(result)
            return result

    # Verify
    post_size, post_count = _dir_size_and_count(dst) if dst.is_dir() else (dst.stat().st_size if dst.exists() else 0, 1 if dst.exists() else 0)
    result["pre_size"] = pre_size
    result["pre_count"] = pre_count
    result["post_size"] = post_size
    result["post_count"] = post_count
    if post_size < pre_size * 0.95 or post_count < pre_count:
        result["status"] = "failed"
        result["errors"].append(
            f"verify failed: pre {pre_count} files / {_human_gb(pre_size)}, post {post_count} files / {_human_gb(post_size)}"
        )
    else:
        result["status"] = "succeeded"

    result["finished_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    _log(result)
    return result


def select_ops_to_run(plan: dict, op_ids: list[str] | None, batch: str | None) -> list[dict]:
    """Filter plan operations by explicit op_id list or by batch spec."""
    all_ops = plan.get("operations", [])
    if op_ids:
        wanted = set(op_ids)
        return [o for o in all_ops if o["op_id"] in wanted]
    if batch:
        # Format: "C-to-Z" or "from-C" or "to-Y" or "class:project-stale"
        if batch.startswith("class:"):
            cls = batch[len("class:"):]
            return [o for o in all_ops if o.get("class") == cls]
        if batch.startswith("from-"):
            d = batch[len("from-"):].upper()
            return [o for o in all_ops if o.get("drive_from") == d]
        if batch.startswith("to-"):
            d = batch[len("to-"):].upper()
            return [o for o in all_ops if o.get("drive_to") == d]
        if "-to-" in batch:
            a, b = batch.upper().split("-TO-")
            return [o for o in all_ops if o.get("drive_from") == a and o.get("drive_to") == b]
    return []


def execute_plan(plan: dict, ops: list[dict], audit_log: Path, stop_on_failure: bool) -> dict:
    drive_meta = get_drive_metadata()
    results = []
    for op in ops:
        # Refresh free space between ops since previous ops affect it
        if op.get("drive_to"):
            drive_meta = get_drive_metadata()
        r = execute_op(op, drive_meta, audit_log)
        results.append(r)
        if r["status"] in ("failed", "blocked") and stop_on_failure:
            print(f"[executor] STOPPING — op {r['op_id']} {r['status']}: {'; '.join(r['errors'])}", file=sys.stderr)
            break
    succeeded = [r for r in results if r["status"] == "succeeded"]
    failed = [r for r in results if r["status"] == "failed"]
    blocked = [r for r in results if r["status"] == "blocked"]
    skipped = [r for r in results if r["status"] == "skipped"]
    return {
        "version": EXECUTOR_VERSION,
        "mode": "execute",
        "ran_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "summary": {
            "requested": len(ops),
            "executed": len(results),
            "succeeded": len(succeeded),
            "failed": len(failed),
            "blocked": len(blocked),
            "skipped": len(skipped),
            "bytes_succeeded": sum(r.get("size_bytes", 0) for r in succeeded),
        },
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="system-scaffold Stage 7 executor")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_dry = sub.add_parser("dry-run", help="simulate the plan against live drive state")
    p_dry.add_argument("run_dir")
    p_dry.add_argument("taxonomy")
    p_dry.add_argument("--check-locks", action="store_true")
    p_dry.add_argument("--output")
    p_dry.add_argument("--quiet", action="store_true")

    p_run = sub.add_parser("run", help="execute selected ops (cherry-pick by id or batch)")
    p_run.add_argument("run_dir")
    p_run.add_argument("taxonomy")
    p_run.add_argument("--op", action="append", default=[], help="explicit op_id to run (can repeat)")
    p_run.add_argument("--batch", help='batch selector: "C-to-Z", "from-C", "to-Y", "class:project-stale"')
    p_run.add_argument("--continue-on-failure", action="store_true", help="keep going past failed ops (default: stop)")
    p_run.add_argument("--quiet", action="store_true")

    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)
    plan_path = run_dir / "plan.json"
    if not plan_path.exists():
        print(f"[executor] error: missing {plan_path}", file=sys.stderr)
        return 1
    plan = json.load(open(plan_path, "r", encoding="utf-8"))
    with open(args.taxonomy, "r", encoding="utf-8") as f:
        taxonomy = yaml.safe_load(f)

    if args.mode == "dry-run":
        sim = simulate_plan(plan, taxonomy, check_locks=args.check_locks)
        out_json = Path(args.output) if args.output else run_dir / "dry-run.json"
        out_md = run_dir / "dry-run.md"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(sim, f, indent=2)
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(render_dry_run_md(plan, sim))
        if not args.quiet:
            s = sim["summary"]
            print(f"[executor] dry-run: would proceed on {s['would_proceed']} / {s['total_ops']} ops", file=sys.stderr)
            print(f"[executor]   blocked: {s['blocked']}, with-warnings: {s['with_warnings']}", file=sys.stderr)
            print(f"[executor]   bytes: {_human_gb(s['total_bytes_proceed'])}, est time: {_human_time(s['estimated_total_seconds'])}", file=sys.stderr)
            print(f"[executor] wrote {out_json} + {out_md}", file=sys.stderr)
        return 0

    # mode == "run"
    if not args.op and not args.batch:
        print("[executor] error: --op or --batch required for run mode", file=sys.stderr)
        return 2
    ops = select_ops_to_run(plan, args.op, args.batch)
    if not ops:
        print("[executor] no ops match selection — nothing to do", file=sys.stderr)
        return 0
    audit_log = run_dir / "execute-log.jsonl"
    if not args.quiet:
        total_bytes = sum(o.get("size_bytes", 0) for o in ops)
        print(f"[executor] selected {len(ops)} ops ({_human_gb(total_bytes)})", file=sys.stderr)
        for o in ops[:10]:
            kind = "delete" if o["type"] == "delete" else f"{o.get('drive_from')}→{o.get('drive_to')}"
            print(f"  {o['op_id']:14s} {kind:10s} {_human_gb(o.get('size_bytes', 0)):>10s}  {o.get('from') or o.get('path')}", file=sys.stderr)
        if len(ops) > 10:
            print(f"  … {len(ops)-10} more", file=sys.stderr)

    result = execute_plan(plan, ops, audit_log, stop_on_failure=not args.continue_on_failure)
    out_json = run_dir / "execute-result.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    if not args.quiet:
        s = result["summary"]
        print(f"[executor] executed: {s['executed']}/{s['requested']}", file=sys.stderr)
        print(f"  succeeded: {s['succeeded']} ({_human_gb(s['bytes_succeeded'])})", file=sys.stderr)
        print(f"  failed: {s['failed']}, blocked: {s['blocked']}, skipped: {s['skipped']}", file=sys.stderr)
        print(f"[executor] audit log: {audit_log}", file=sys.stderr)
    return 0 if result["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
