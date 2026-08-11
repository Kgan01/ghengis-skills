"""
system-scaffold Stage 2 — Classifier.

Reads inventory.json from Stage 1, applies an ordered rule cascade to label
each node with a class + confidence, attaches universal freshness signals
(last_touched_days), and emits:
- classifications.json: every node with its final classification
- uncertain.json: subset whose class is uncertain (confidence below threshold
  or in *-likely / *-uncertain / unknown) for Stage 3 (Interview) to ask the
  user about.

Pure Python stdlib. Designed to be re-runnable on a fresh inventory without
state from prior runs.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

CLASSIFIER_VERSION = "1"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Default confidence threshold — below this, node escalates to Interview.
# 0.85 = ask more questions, guess less. Tuned for use on stranger's computer.
DEFAULT_CONFIDENCE_THRESHOLD = 0.85

# Stale threshold for project-active vs project-stale (days).
DEFAULT_STALE_DAYS = 120

# Classes that always escalate to Interview regardless of confidence score.
ALWAYS_ESCALATE_CLASSES = {
    "project-likely",
    "media-video-uncertain",
    "media-photo-uncertain",
    "media-audio-uncertain",
    "unknown",
}

# Primary project markers — definitive signal that a directory IS a project.
PRIMARY_PROJECT_MARKERS = {
    ".git",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "composer.json",
    "Pipfile",
    "Makefile",
    "Dockerfile",
    "requirements.txt",
}

# Secondary markers — suggestive but not definitive on their own.
SECONDARY_PROJECT_MARKERS = {".gitignore", "README.md", "docker-compose.yml"}

# Path substrings that signal "I'm inside a vendor bundle, not a real project".
# Each fragment is the literal substring as it appears in a lowercased,
# backslash-normalized path. Non-raw strings: "\\" is one literal backslash.
VENDOR_PATH_FRAGMENTS = (
    "\\node_modules\\",
    "\\.vscode\\extensions\\",
    "\\.cursor\\extensions\\",
    "\\.cursor-server\\",
    "\\.vscode-server\\",
    "\\.platformio\\packages\\",
    "\\.cargo\\registry\\",
    "\\.gradle\\caches\\",
    "\\.pnpm-store\\",
    "\\bower_components\\",
    # Package-manager and tool caches (each contains many vendored copies)
    "\\.bun\\install\\cache\\",
    "\\.npm\\_cacache\\",
    "\\.yarn\\cache\\",
    "\\appdata\\local\\pip\\cache\\",
    "\\appdata\\local\\npm-cache\\",
    "\\appdata\\local\\yarn\\cache\\",
    "\\appdata\\roaming\\npm-cache\\",
    "\\adobetemp\\",  # Adobe installer scratch
)

# Media extensions
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".wmv", ".flv", ".webm", ".m4v", ".braw", ".r3d"}
PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".cr2", ".arw", ".nef", ".dng", ".raw", ".tiff", ".tif", ".heic", ".gif", ".bmp"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma"}
ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".7z", ".rar", ".xz", ".tar.gz"}

# Editor / NLE project file signatures — presence indicates active editing.
EDITOR_PROJECT_EXTS = {
    ".aep",       # After Effects
    ".prproj",    # Premiere Pro
    ".drp",       # DaVinci Resolve
    ".fcpbundle", # Final Cut Pro
    ".blend",     # Blender
    ".psd",       # Photoshop
    ".ai",        # Illustrator
    ".indd",      # InDesign
    ".xcf",       # GIMP
    ".kra",       # Krita
    ".als",       # Ableton Live
    ".flp",       # FL Studio
    ".ptx",       # Pro Tools
    ".logicx",    # Logic Pro
    ".reaproject", # Reaper
}

# Document-y types that suggest user personal content.
DOCUMENT_EXTS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".odt", ".rtf"}

MEDIA_DOMINANT_THRESHOLD = 0.80  # 80% of bytes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize(path: str) -> str:
    return path.replace("/", "\\").lower()


def _type_breakdown_share(type_breakdown: dict, exts: set) -> float:
    """Fraction of total bytes accounted for by the given extensions."""
    total = sum(v["size_bytes"] for v in type_breakdown.values()) or 1
    matched = sum(
        v["size_bytes"] for k, v in type_breakdown.items() if k.lower() in exts
    )
    return matched / total


def _has_editor_project(type_breakdown: dict) -> bool:
    return any(ext.lower() in EDITOR_PROJECT_EXTS for ext in type_breakdown.keys())


def _is_vendor_path(path_norm: str) -> bool:
    """True if path is inside a vendor/cache bundle (or IS one)."""
    for frag in VENDOR_PATH_FRAGMENTS:
        if frag in path_norm:
            return True
        # Also match when the path ENDS with the vendor dir (no trailing sep)
        if path_norm.endswith(frag.rstrip("\\")):
            return True
    return False


def _has_primary_marker(markers: list[str]) -> bool:
    return any(m in PRIMARY_PROJECT_MARKERS for m in markers)


def _has_secondary_marker(markers: list[str]) -> bool:
    return any(m in SECONDARY_PROJECT_MARKERS for m in markers)


def _days_since(iso_ts: str | None, now_ts: float) -> int | None:
    if not iso_ts:
        return None
    try:
        dt = _dt.datetime.fromisoformat(iso_ts)
        seconds = now_ts - dt.timestamp()
        return max(0, int(seconds / 86400))
    except (ValueError, OSError):
        return None


# ---------------------------------------------------------------------------
# Rule cascade
# ---------------------------------------------------------------------------


def classify_node(node: dict, now_ts: float, stale_days: int) -> dict:
    """Return classification dict: class, confidence, signals[], movability, action_hint."""

    path = node["path"]
    path_norm = _normalize(path)
    markers = node.get("markers", [])
    type_breakdown = node.get("type_breakdown", {})
    size_bytes = node.get("size_bytes", 0)
    depth = node.get("depth", 0)
    last_touched_days = _days_since(node.get("max_descendant_mtime"), now_ts)

    signals: list[str] = []
    if last_touched_days is not None:
        signals.append(f"last_touched_days={last_touched_days}")

    # ----- Tier A: drive-/path-prefix rules (high confidence, very specific) -----

    # User-profile container rules — must come BEFORE project detection so a
    # stray package.json under a profile root doesn't promote the whole home
    # dir to "project-active".
    if re.match(r"^[a-z]:\\users$", path_norm):
        return _result("user-profile-parent", 0.99, signals + ["path:users-root"], "never", "Windows user profiles container", last_touched_days, size_bytes)
    if re.match(r"^[a-z]:\\users\\[^\\]+$", path_norm):
        return _result("user-profile", 0.99, signals + ["path:user-home"], "never", "user home directory — describe in CONTEXT.md but do not move", last_touched_days, size_bytes)
    if re.match(r"^[a-z]:\\users\\[^\\]+\\appdata$", path_norm):
        return _result("app-data", 0.95, signals + ["path:appdata-root"], "never", "AppData root container", last_touched_days, size_bytes)
    if re.match(r"^[a-z]:\\users\\[^\\]+\\onedrive$", path_norm):
        return _result("cloud-synced", 0.97, signals + ["path:onedrive-root"], "never", "OneDrive sync root; manage in OneDrive settings", last_touched_days, size_bytes)
    if re.match(r"^[a-z]:\\users\\[^\\]+\\(onedrive\\)?documents$", path_norm):
        return _result("documents", 0.92, signals + ["path:user-documents"], "with-care", "user Documents folder; check contents before moving", last_touched_days, size_bytes)
    if re.match(r"^[a-z]:\\users\\[^\\]+\\\.cache$", path_norm):
        return _result("cache-rebuildable", 0.90, signals + ["path:user-cache-root"], "delete", "user-level cache root", last_touched_days, size_bytes)

    # Windows system
    if re.match(r"^[a-z]:\\windows(\\|$)", path_norm):
        return _result("system", 0.99, signals + ["path:windows-system"], "never", "do not move", last_touched_days, size_bytes)

    # Program Files
    if re.match(r"^[a-z]:\\program files( \(x86\))?(\\|$)", path_norm):
        return _result("installed-app", 0.99, signals + ["path:program-files"], "never", "uninstall via OS, do not move files", last_touched_days, size_bytes)

    # ProgramData
    if re.match(r"^[a-z]:\\programdata(\\|$)", path_norm):
        return _result("installed-app", 0.95, signals + ["path:programdata"], "never", "system-wide app data; do not move", last_touched_days, size_bytes)

    # WSL VHDX
    if re.search(r"\\appdata\\local\\wsl(\\|$)", path_norm):
        return _result("dev-vm", 0.98, signals + ["path:wsl"], "special", "use 'wsl --export' / '--import' to relocate, not file copy", last_touched_days, size_bytes)

    # Docker
    if re.search(r"\\programdata\\docker(\\|$)", path_norm):
        return _result("dev-vm", 0.97, signals + ["path:docker"], "special", "use Docker Desktop settings to relocate image store", last_touched_days, size_bytes)

    # AppData Roaming = app config
    if re.search(r"\\appdata\\roaming(\\|$)", path_norm):
        return _result("app-config", 0.92, signals + ["path:appdata-roaming"], "never", "app reads from this path; do not move", last_touched_days, size_bytes)

    # AppData Local Temp = cache-tmp
    if re.search(r"\\appdata\\local\\temp(\\|$)", path_norm):
        return _result("cache-tmp", 0.97, signals + ["path:appdata-temp"], "delete", "safe to delete", last_touched_days, size_bytes)

    # AppData Local *\Cache = cache-app
    if re.search(r"\\appdata\\local\\[^\\]+\\cache(\\|$)", path_norm):
        return _result("cache-app", 0.90, signals + ["path:appdata-cache"], "delete", "safe to delete; app will rebuild", last_touched_days, size_bytes)

    # AppData LocalLow / AppData Local = app-data
    if re.search(r"\\appdata\\(local|locallow)(\\|$)", path_norm):
        return _result("app-data", 0.85, signals + ["path:appdata-local"], "with-care", "movable via app settings only; do not move via filesystem", last_touched_days, size_bytes)

    # Google Drive File Stream
    if re.match(r"^[a-z]:\\(my drive|shared drives|\.shortcut-targets-by-id|\.encrypted)", path_norm):
        return _result("cloud-synced", 0.98, signals + ["cloud:google-drive"], "never", "Google Drive content; manage in Drive UI", last_touched_days, size_bytes)

    # ----- Tier B: vendor bundles / rebuildable caches -----

    # Inside a known vendor path
    if _is_vendor_path(path_norm):
        return _result("vendor-bundle", 0.95, signals + ["path:vendor-fragment"], "delete", "rebuildable from lockfile (npm/pnpm install, etc.)", last_touched_days, size_bytes)

    # __pycache__
    if path_norm.endswith(r"\__pycache__") or r"\__pycache__\\" in path_norm:
        return _result("cache-rebuildable", 0.99, signals + ["path:pycache"], "delete", "Python bytecode cache; auto-regenerates", last_touched_days, size_bytes)

    # Project-local virtualenvs
    if re.search(r"\\(venv|\.venv|env)$", path_norm):
        return _result("cache-rebuildable", 0.92, signals + ["path:virtualenv"], "delete", "rebuildable from requirements.txt / pyproject.toml", last_touched_days, size_bytes)

    # Other build-artifact caches
    if re.search(r"\\(\.pytest_cache|\.ruff_cache|\.mypy_cache|\.next|\.turbo|\.svelte-kit|\.nuxt|\.parcel-cache)(\\|$)", path_norm):
        return _result("cache-rebuildable", 0.97, signals + ["path:build-cache"], "delete", "build cache; auto-regenerates", last_touched_days, size_bytes)

    # ----- Tier C: dev infrastructure -----

    # HuggingFace / model caches
    if re.search(r"\\\.cache\\huggingface(\\|$)", path_norm):
        return _result("dev-models", 0.97, signals + ["path:huggingface"], "safe-to-move", "AI model cache; large but movable", last_touched_days, size_bytes)

    if "ollama-models" in path_norm or "ollama_models" in path_norm:
        return _result("dev-models", 0.95, signals + ["path:ollama-models"], "safe-to-move", "Ollama model cache; configurable via OLLAMA_MODELS env", last_touched_days, size_bytes)

    if "sentence-transformers" in path_norm or "transformers_cache" in path_norm:
        return _result("dev-models", 0.95, signals + ["path:transformers-cache"], "safe-to-move", "transformers model cache", last_touched_days, size_bytes)

    # System-wide Python installs
    if re.match(r"^[a-z]:\\python\d+(\\|$)", path_norm):
        return _result("dev-toolchain", 0.95, signals + ["path:python-install"], "with-care", "system Python install; relocation requires re-pointing PATH", last_touched_days, size_bytes)

    # PlatformIO toolchain
    if re.search(r"\\\.platformio(\\|$)", path_norm):
        return _result("dev-toolchain", 0.93, signals + ["path:platformio"], "with-care", "PlatformIO toolchain; relocatable via env var", last_touched_days, size_bytes)

    # Other dev toolchain managers
    if re.search(r"\\(\.pyenv|\.rustup|\.nvm|\.fnm|\.volta|\.cargo|\.bun|\.deno)(\\|$)", path_norm):
        return _result("dev-toolchain", 0.93, signals + ["path:toolchain-manager"], "with-care", "language version manager; relocation needs config update", last_touched_days, size_bytes)

    # Conda / Anaconda / Miniconda distributions
    if re.search(r"\\(anaconda3|miniconda3|miniforge3)(\\|$)", path_norm):
        return _result("dev-toolchain", 0.93, signals + ["path:conda-distribution"], "with-care", "Conda Python distribution; relocation needs config update", last_touched_days, size_bytes)

    # ----- Tier D: standard Windows user folders -----

    if re.search(r"\\users\\[^\\]+\\downloads(\\|$)", path_norm):
        return _result("downloads", 0.92, signals + ["path:downloads"], "review", "review individually; often disposable", last_touched_days, size_bytes)

    if re.search(r"\\users\\[^\\]+\\(onedrive\\)?desktop$", path_norm):
        # The desktop ROOT — not a single item on the desktop.
        # Loose items would be at depth+1; we tag the root differently.
        return _result("desktop-scratch", 0.80, signals + ["path:desktop-root"], "review", "loose desktop items; review individually", last_touched_days, size_bytes)

    if re.search(r"\\users\\[^\\]+\\(onedrive\\)?pictures(\\|$)", path_norm):
        # Default to photo-uncertain; later type breakdown may narrow.
        return _result("media-photo-uncertain", 0.78, signals + ["path:user-pictures"], "with-care", "personal photo collection; archive candidate when cold", last_touched_days, size_bytes)

    if re.search(r"\\users\\[^\\]+\\(onedrive\\)?videos(\\|$)", path_norm):
        return _result("media-video-uncertain", 0.78, signals + ["path:user-videos"], "with-care", "personal video collection; check for active editing projects", last_touched_days, size_bytes)

    if re.search(r"\\users\\[^\\]+\\(onedrive\\)?music(\\|$)", path_norm):
        return _result("media-audio", 0.85, signals + ["path:user-music"], "safe-to-move", "personal music collection; cold storage candidate", last_touched_days, size_bytes)

    if re.search(r"\\(saved games|my games)(\\|$)", path_norm):
        return _result("game-save-data", 0.90, signals + ["path:game-saves"], "with-care", "game save data; do not move without checking each game", last_touched_days, size_bytes)

    # ----- Tier E: project detection (vendor already excluded above) -----

    has_primary = _has_primary_marker(markers)
    has_secondary = _has_secondary_marker(markers)
    project_modtime_days = last_touched_days  # uses max descendant — actual activity

    if has_primary:
        # Real project
        if project_modtime_days is not None and project_modtime_days > stale_days:
            return _result(
                "project-stale",
                0.92,
                signals + [f"markers:{sorted(set(markers) & PRIMARY_PROJECT_MARKERS)}", f"stale>{stale_days}d"],
                "safe-to-move",
                "old project; candidate for cold storage on Z",
                last_touched_days,
                size_bytes,
            )
        return _result(
            "project-active",
            0.92,
            signals + [f"markers:{sorted(set(markers) & PRIMARY_PROJECT_MARKERS)}"],
            "with-care",
            "active project; keep on hot storage (Y), preserve git state on move",
            last_touched_days,
            size_bytes,
        )

    if has_secondary and not has_primary:
        # Possibly a project — escalate.
        return _result(
            "project-likely",
            0.55,
            signals + [f"secondary-only:{sorted(set(markers) & SECONDARY_PROJECT_MARKERS)}"],
            "with-care",
            "may be a project without standard markers — ask user",
            last_touched_days,
            size_bytes,
        )

    # ----- Tier F: media classification by content -----

    video_share = _type_breakdown_share(type_breakdown, VIDEO_EXTS)
    photo_share = _type_breakdown_share(type_breakdown, PHOTO_EXTS)
    audio_share = _type_breakdown_share(type_breakdown, AUDIO_EXTS)
    archive_share = _type_breakdown_share(type_breakdown, ARCHIVE_EXTS)
    has_editor = _has_editor_project(type_breakdown)

    if video_share >= MEDIA_DOMINANT_THRESHOLD:
        if has_editor:
            return _result("media-video-active", 0.88, signals + [f"video_share={video_share:.2f}", "editor-project-files-present"], "with-care", "active video editing project; keep on hot storage", last_touched_days, size_bytes)
        if last_touched_days is not None and last_touched_days > stale_days:
            return _result("media-video-cold", 0.88, signals + [f"video_share={video_share:.2f}", f"stale>{stale_days}d"], "safe-to-move", "old video; cold storage (Z) candidate", last_touched_days, size_bytes)
        return _result("media-video-uncertain", 0.55, signals + [f"video_share={video_share:.2f}", "signals-conflict"], "with-care", "video collection with mixed signals — ask user", last_touched_days, size_bytes)

    if photo_share >= MEDIA_DOMINANT_THRESHOLD:
        if has_editor:
            return _result("media-photo-active", 0.85, signals + [f"photo_share={photo_share:.2f}", "editor-project-files-present"], "with-care", "active photo editing project", last_touched_days, size_bytes)
        if last_touched_days is not None and last_touched_days > stale_days:
            return _result("media-photo-cold", 0.85, signals + [f"photo_share={photo_share:.2f}", f"stale>{stale_days}d"], "safe-to-move", "old photo collection; cold storage candidate", last_touched_days, size_bytes)
        return _result("media-photo-uncertain", 0.55, signals + [f"photo_share={photo_share:.2f}"], "with-care", "photo collection with mixed signals — ask user", last_touched_days, size_bytes)

    if audio_share >= MEDIA_DOMINANT_THRESHOLD:
        if has_editor:
            return _result("media-audio-active", 0.85, signals + [f"audio_share={audio_share:.2f}", "editor-project-files-present"], "with-care", "active audio project", last_touched_days, size_bytes)
        if last_touched_days is not None and last_touched_days > stale_days:
            return _result("media-audio", 0.85, signals + [f"audio_share={audio_share:.2f}", f"stale>{stale_days}d"], "safe-to-move", "audio collection; cold storage candidate", last_touched_days, size_bytes)
        return _result("media-audio-uncertain", 0.55, signals + [f"audio_share={audio_share:.2f}"], "with-care", "audio collection with mixed signals — ask user", last_touched_days, size_bytes)

    if archive_share >= MEDIA_DOMINANT_THRESHOLD:
        return _result("archive", 0.90, signals + [f"archive_share={archive_share:.2f}"], "safe-to-move", "archives; cold storage candidate", last_touched_days, size_bytes)

    document_share = _type_breakdown_share(type_breakdown, DOCUMENT_EXTS)
    if document_share >= MEDIA_DOMINANT_THRESHOLD:
        return _result("documents", 0.85, signals + [f"document_share={document_share:.2f}"], "with-care", "document collection; keep accessible (Y) unless stale", last_touched_days, size_bytes)

    # ----- Tier G: fallback by depth/heuristic -----

    # Drive root
    if depth == 0:
        return _result("drive-root", 1.0, signals + ["depth=0"], "never", "drive root — describe in CONTEXT.md", last_touched_days, size_bytes)

    return _result(
        "unknown",
        0.0,
        signals + ["no-rule-matched"],
        "with-care",
        "needs user input — Stage 3 will ask",
        last_touched_days,
        size_bytes,
    )


def _result(
    cls: str,
    confidence: float,
    signals: list[str],
    movability: str,
    action_hint: str,
    last_touched_days: int | None,
    size_bytes: int,
) -> dict:
    return {
        "class": cls,
        "confidence": round(confidence, 3),
        "movability": movability,
        "action_hint": action_hint,
        "signals": signals,
        "last_touched_days": last_touched_days,
        "size_bytes": size_bytes,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def classify_inventory(inventory: dict, stale_days: int, confidence_threshold: float) -> tuple[dict, dict]:
    now_ts = _dt.datetime.now().timestamp()

    classified_nodes = []
    uncertain_nodes = []

    for node in inventory.get("nodes", []):
        result = classify_node(node, now_ts, stale_days)
        out = {
            "path": node["path"],
            "drive": node.get("drive"),
            "depth": node.get("depth"),
            **result,
        }
        classified_nodes.append(out)

        if result["class"] in ALWAYS_ESCALATE_CLASSES or result["confidence"] < confidence_threshold:
            uncertain_nodes.append(out)

    # Class distribution
    distribution: dict[str, int] = {}
    for c in classified_nodes:
        distribution[c["class"]] = distribution.get(c["class"], 0) + 1

    summary = {
        "version": CLASSIFIER_VERSION,
        "classifier": "system-scaffold/classifier.py",
        "ran_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "config": {
            "stale_days": stale_days,
            "confidence_threshold": confidence_threshold,
        },
        "source_inventory": {
            "run_started_at": inventory.get("run_started_at"),
            "node_count": len(inventory.get("nodes", [])),
        },
        "distribution": dict(sorted(distribution.items(), key=lambda kv: -kv[1])),
        "classified": classified_nodes,
    }

    uncertain_summary = {
        "version": CLASSIFIER_VERSION,
        "ran_at": summary["ran_at"],
        "config": summary["config"],
        "uncertain_count": len(uncertain_nodes),
        "nodes": uncertain_nodes,
    }

    return summary, uncertain_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="system-scaffold Stage 2 classifier")
    parser.add_argument("inventory", help="path to inventory.json from Stage 1")
    parser.add_argument(
        "--output-dir",
        help="output directory. Default: same as inventory file's parent.",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=DEFAULT_STALE_DAYS,
        help=f"days after which a project is stale (default: {DEFAULT_STALE_DAYS})",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=DEFAULT_CONFIDENCE_THRESHOLD,
        help=f"confidence below which a node escalates to Interview (default: {DEFAULT_CONFIDENCE_THRESHOLD})",
    )
    parser.add_argument("--quiet", action="store_true")

    args = parser.parse_args(argv)

    inv_path = Path(args.inventory)
    if not inv_path.exists():
        print(f"[classifier] error: inventory not found at {inv_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.output_dir) if args.output_dir else inv_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(inv_path, "r", encoding="utf-8") as f:
        inventory = json.load(f)

    summary, uncertain = classify_inventory(
        inventory,
        stale_days=args.stale_days,
        confidence_threshold=args.confidence_threshold,
    )

    classifications_path = out_dir / "classifications.json"
    uncertain_path = out_dir / "uncertain.json"

    with open(classifications_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    with open(uncertain_path, "w", encoding="utf-8") as f:
        json.dump(uncertain, f, indent=2)

    if not args.quiet:
        print(f"[classifier] classified {len(summary['classified'])} nodes", file=sys.stderr)
        print(f"[classifier] uncertain: {uncertain['uncertain_count']} (escalates to Interview)", file=sys.stderr)
        print(f"[classifier] wrote {classifications_path}", file=sys.stderr)
        print(f"[classifier] wrote {uncertain_path}", file=sys.stderr)
        top = list(summary["distribution"].items())[:10]
        print("[classifier] top classes:", file=sys.stderr)
        for cls, count in top:
            print(f"  {cls}: {count}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
