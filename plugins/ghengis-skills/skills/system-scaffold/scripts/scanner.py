"""
system-scaffold Stage 1 — Scanner.

Walks all connected fixed drives on a Windows computer and emits a per-directory
inventory with size, file count, file-type breakdown, project markers, and
modtime. Smart-walks: always descends dirs above a size threshold up to a max
depth; smaller dirs are recorded but not entered. Skips system reserved paths
and NTFS junction/reparse points.

Output: inventory.json suitable for Stage 2 (Classify) to consume.

Pure Python stdlib. Windows-specific drive metadata is gathered via a small
PowerShell shell-out; the rest is portable.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCANNER_VERSION = "1"

# Top-level paths to skip on every drive (compared case-insensitively).
SKIP_DIR_NAMES_LOWER = {
    "$recycle.bin",
    "system volume information",
    "config.msi",
    "recovery",
    "$winreagent",
    "$sysreset",
    "onedrivetemp",
    "perflogs",
}

# Project / scaffold marker files (presence recorded, not interpreted at this stage)
PROJECT_MARKER_FILES = {
    ".git",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "CLAUDE.md",
    "README.md",
    "requirements.txt",
    "Pipfile",
    "composer.json",
    ".gitignore",
    "Dockerfile",
    "docker-compose.yml",
}

# Reparse point attribute (Windows). Fallback to literal value if stat lacks it.
FILE_ATTRIBUTE_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)

# Defaults
DEFAULT_MAX_DEPTH = 8
DEFAULT_SIZE_THRESHOLD_BYTES = 100 * 1024 * 1024  # 100 MB
DEFAULT_OUTPUT_DIR = Path.home() / ".system" / "runs"


# ---------------------------------------------------------------------------
# Drive enumeration (Windows-specific; will move to OSAdapter in a later stage)
# ---------------------------------------------------------------------------


def list_fixed_drives() -> list[str]:
    """Return drive letters of currently mounted fixed/removable filesystems."""
    if os.name != "nt":
        return []
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        root = f"{letter}:\\"
        if os.path.exists(root):
            drives.append(letter)
    return drives


def get_drive_hardware_metadata() -> dict[str, dict]:
    """Map drive letter -> {media_type, bus_type, friendly_name, fs_type, label}.

    Falls back to empty dict if PowerShell call fails. Best-effort only.
    """
    ps_script = r"""
$ErrorActionPreference = 'SilentlyContinue'
$partitions = Get-Partition | Where-Object { $_.DriveLetter }
$result = @()
foreach ($p in $partitions) {
    $disk = Get-Disk -Number $p.DiskNumber
    $physical = Get-PhysicalDisk -DeviceNumber $p.DiskNumber
    $vol = Get-Volume -DriveLetter $p.DriveLetter
    $result += [pscustomobject]@{
        Letter        = "$($p.DriveLetter)"
        MediaType     = "$($physical.MediaType)"
        BusType       = "$($physical.BusType)"
        FriendlyName  = "$($physical.FriendlyName)"
        FileSystem    = "$($vol.FileSystem)"
        Label         = "$($vol.FileSystemLabel)"
    }
}
$result | ConvertTo-Json -Compress
"""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return {}
        data = json.loads(proc.stdout)
        if isinstance(data, dict):
            data = [data]
        out = {}
        for row in data:
            letter = row.get("Letter", "").strip()
            if letter:
                out[letter] = {
                    "media_type": row.get("MediaType", "") or "",
                    "bus_type": row.get("BusType", "") or "",
                    "friendly_name": row.get("FriendlyName", "") or "",
                    "fs_type": row.get("FileSystem", "") or "",
                    "label": row.get("Label", "") or "",
                }
        return out
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return {}


# ---------------------------------------------------------------------------
# Reparse point detection
# ---------------------------------------------------------------------------


def is_reparse_point(entry_or_stat) -> bool:
    """True if the entry is a junction, symlink, or other reparse point."""
    try:
        if hasattr(entry_or_stat, "stat"):
            st = entry_or_stat.stat(follow_symlinks=False)
        else:
            st = entry_or_stat
        attrs = getattr(st, "st_file_attributes", 0)
        return bool(attrs & FILE_ATTRIBUTE_REPARSE_POINT)
    except (OSError, AttributeError):
        return False


# ---------------------------------------------------------------------------
# Per-directory walk
# ---------------------------------------------------------------------------


class WalkStats:
    """Mutable counters for the whole scan."""

    def __init__(self) -> None:
        self.nodes_recorded = 0
        self.files_seen = 0
        self.dirs_seen = 0
        self.reparse_points_skipped = 0
        self.permission_errors = 0
        self.other_errors = 0
        self.skipped: list[dict] = []


def _record_skip(stats: WalkStats, path: str, reason: str) -> None:
    if len(stats.skipped) < 1000:  # cap to keep JSON sane
        stats.skipped.append({"path": path, "reason": reason})


def walk_directory(
    root_path: Path,
    drive_letter: str,
    max_depth: int,
    size_threshold: int,
    stats: WalkStats,
    nodes_out: list[dict],
) -> int:
    """Walk root_path with smart-descent rules. Returns total size in bytes.

    A node is recorded for every directory visited. Descent stops when:
    - depth >= max_depth
    - dir total_size < size_threshold AND no project markers present
    """

    def _walk(path: Path, depth: int) -> tuple[int, int, int, dict[str, dict], float]:
        """Walk path, record nodes. Returns:
        (total_size, file_count, subdir_count, type_breakdown, max_descendant_mtime).

        max_descendant_mtime is the most recent file/dir mtime anywhere in the
        subtree — the real "last touched" signal for a folder, since a dir's
        own mtime only updates when its direct entries change.
        """

        stats.dirs_seen += 1
        total_size = 0
        file_count = 0
        subdir_count = 0
        type_breakdown: dict[str, dict] = {}
        markers_found: set[str] = set()
        subdirs: list[str] = []
        immediate_subdir_paths: list[Path] = []
        max_descendant_mtime: float = 0.0

        try:
            entries = list(os.scandir(path))
        except PermissionError:
            stats.permission_errors += 1
            _record_skip(stats, str(path), "permission_denied")
            entries = []
        except OSError as e:
            stats.other_errors += 1
            _record_skip(stats, str(path), f"os_error:{e.errno}")
            entries = []

        for entry in entries:
            name = entry.name

            if name in PROJECT_MARKER_FILES:
                markers_found.add(name)

            # Skip reparse points entirely (don't follow, don't size)
            if is_reparse_point(entry):
                stats.reparse_points_skipped += 1
                continue

            try:
                if entry.is_file(follow_symlinks=False):
                    try:
                        st = entry.stat(follow_symlinks=False)
                        size = st.st_size
                        if st.st_mtime > max_descendant_mtime:
                            max_descendant_mtime = st.st_mtime
                    except OSError:
                        size = 0
                    total_size += size
                    file_count += 1
                    stats.files_seen += 1
                    ext = os.path.splitext(name)[1].lower() or "(no_ext)"
                    bucket = type_breakdown.setdefault(ext, {"count": 0, "size_bytes": 0})
                    bucket["count"] += 1
                    bucket["size_bytes"] += size
                elif entry.is_dir(follow_symlinks=False):
                    # Top-level skips
                    if depth == 0 and name.lower() in SKIP_DIR_NAMES_LOWER:
                        _record_skip(stats, str(Path(entry.path)), "system_reserved")
                        continue
                    subdir_count += 1
                    subdirs.append(name)
                    immediate_subdir_paths.append(Path(entry.path))
            except OSError:
                stats.other_errors += 1
                continue

        # Decide descent into subdirs. Always descend at depth < 2 (we want
        # full picture of drive root + first level). Below that, descend only
        # if there's something interesting.
        descend = depth < max_depth - 1

        # We want to recurse to gather child rollups even when we won't record
        # individual leaf nodes — so the parent's size is accurate. But we
        # avoid creating *node entries* for deep small dirs.
        for sub in immediate_subdir_paths:
            sub_total, sub_files, sub_subs, sub_breakdown, sub_max_mtime = (0, 0, 0, {}, 0.0)
            if descend:
                sub_total, sub_files, sub_subs, sub_breakdown, sub_max_mtime = _walk(sub, depth + 1)
            # Roll up into parent regardless of whether we recorded it
            total_size += sub_total
            if sub_max_mtime > max_descendant_mtime:
                max_descendant_mtime = sub_max_mtime
            for ext, agg in sub_breakdown.items():
                bucket = type_breakdown.setdefault(ext, {"count": 0, "size_bytes": 0})
                bucket["count"] += agg["count"]
                bucket["size_bytes"] += agg["size_bytes"]

        # Record this directory as a node
        try:
            st_self = path.stat()
            modtime = _dt.datetime.fromtimestamp(st_self.st_mtime).isoformat(timespec="seconds")
            if st_self.st_mtime > max_descendant_mtime:
                max_descendant_mtime = st_self.st_mtime
        except OSError:
            modtime = None

        max_desc_iso = (
            _dt.datetime.fromtimestamp(max_descendant_mtime).isoformat(timespec="seconds")
            if max_descendant_mtime > 0
            else None
        )

        # Determine whether to record this node based on relevance
        should_record = (
            depth < 2  # always record root and first-level
            or total_size >= size_threshold
            or markers_found
        )

        if should_record:
            stop_reason = None
            descended = descend
            if not descend:
                stop_reason = "max_depth"
            elif total_size < size_threshold and depth >= 2:
                # We descended but found little; still recorded the node
                stop_reason = None

            nodes_out.append(
                {
                    "path": str(path),
                    "drive": drive_letter,
                    "depth": depth,
                    "size_bytes": total_size,
                    "file_count": file_count,
                    "subdir_count": subdir_count,
                    "modtime": modtime,
                    "max_descendant_mtime": max_desc_iso,
                    "markers": sorted(markers_found),
                    "type_breakdown": type_breakdown,
                    "subdirs": sorted(subdirs)[:50],  # cap for readability
                    "descended": descended,
                    "stop_reason": stop_reason,
                }
            )
            stats.nodes_recorded += 1

        return total_size, file_count, subdir_count, type_breakdown, max_descendant_mtime

    total, _, _, _, _ = _walk(root_path, depth=0)
    return total


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------


def scan(drives: list[str], max_depth: int, size_threshold: int) -> dict:
    started_at = time.time()
    started_iso = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    if not drives:
        drives = list_fixed_drives()

    hw = get_drive_hardware_metadata()

    drive_records = []
    all_nodes: list[dict] = []
    stats = WalkStats()

    for letter in drives:
        root = Path(f"{letter}:\\")
        if not root.exists():
            _record_skip(stats, str(root), "drive_not_mounted")
            continue
        try:
            usage = shutil.disk_usage(str(root))
            total_bytes = usage.total
            used_bytes = usage.used
            free_bytes = usage.free
        except OSError as e:
            total_bytes = used_bytes = free_bytes = 0
            _record_skip(stats, str(root), f"disk_usage_error:{e.errno}")

        meta = hw.get(letter, {})
        drive_records.append(
            {
                "letter": letter,
                "label": meta.get("label", ""),
                "fs_type": meta.get("fs_type", ""),
                "media_type": meta.get("media_type", ""),
                "bus_type": meta.get("bus_type", ""),
                "friendly_name": meta.get("friendly_name", ""),
                "size_bytes": total_bytes,
                "used_bytes": used_bytes,
                "free_bytes": free_bytes,
            }
        )

        walk_directory(
            root_path=root,
            drive_letter=letter,
            max_depth=max_depth,
            size_threshold=size_threshold,
            stats=stats,
            nodes_out=all_nodes,
        )

    duration = round(time.time() - started_at, 2)

    return {
        "version": SCANNER_VERSION,
        "scanner": "system-scaffold/scanner.py",
        "run_started_at": started_iso,
        "host": {
            "computer_name": os.environ.get("COMPUTERNAME", ""),
            "user": os.environ.get("USERNAME", ""),
            "os": sys.platform,
        },
        "config": {
            "drives_requested": drives,
            "max_depth": max_depth,
            "size_threshold_bytes": size_threshold,
        },
        "drives": drive_records,
        "nodes": all_nodes,
        "skipped": stats.skipped,
        "stats": {
            "scan_duration_seconds": duration,
            "nodes_recorded": stats.nodes_recorded,
            "files_seen": stats.files_seen,
            "dirs_seen": stats.dirs_seen,
            "reparse_points_skipped": stats.reparse_points_skipped,
            "permission_errors": stats.permission_errors,
            "other_errors": stats.other_errors,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="system-scaffold Stage 1 scanner")
    parser.add_argument(
        "--drives",
        help="comma-separated drive letters (e.g., C,Y,Z). Default: all mounted fixed drives.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=f"maximum directory depth to descend (default: {DEFAULT_MAX_DEPTH})",
    )
    parser.add_argument(
        "--size-threshold",
        type=int,
        default=DEFAULT_SIZE_THRESHOLD_BYTES,
        help=f"min dir size (bytes) to record beyond depth 2 (default: {DEFAULT_SIZE_THRESHOLD_BYTES})",
    )
    parser.add_argument(
        "--output",
        help="output JSON path. Default: ~/.system/runs/<timestamp>/inventory.json",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress progress output",
    )

    args = parser.parse_args(argv)

    drives = (
        [d.strip().upper() for d in args.drives.split(",") if d.strip()]
        if args.drives
        else []
    )

    if args.output:
        out_path = Path(args.output)
    else:
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = DEFAULT_OUTPUT_DIR / stamp / "inventory.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not args.quiet:
        print(f"[scanner] starting; drives={drives or 'auto'} max_depth={args.max_depth}", file=sys.stderr)

    result = scan(
        drives=drives,
        max_depth=args.max_depth,
        size_threshold=args.size_threshold,
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if not args.quiet:
        print(
            f"[scanner] done in {result['stats']['scan_duration_seconds']}s "
            f"(nodes={result['stats']['nodes_recorded']}, files={result['stats']['files_seen']}, "
            f"dirs={result['stats']['dirs_seen']})",
            file=sys.stderr,
        )
        print(f"[scanner] wrote {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
