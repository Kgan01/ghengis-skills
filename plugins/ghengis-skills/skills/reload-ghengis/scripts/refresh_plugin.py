#!/usr/bin/env python3
"""
refresh_plugin.py — force-sync the ghengis-skills plugin from GitHub.

Bypasses Claude Code's flaky `/plugin update` logic by doing the filesystem
work directly:
  1. git fetch + reset --hard origin/master on the marketplace clone
  2. Read NEW version from plugin.json
  3. Copy fresh files into ~/.claude/plugins/cache/<mk>/<plugin>/<new-ver>/
  4. Update installed_plugins.json to point at the new version
  5. Leave stale cache versions in place (safe — they're not read)

Run via:
  # As a skill: user invokes /reload-ghengis
  # Standalone: curl -fsSL https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py | python
  # Direct:  python refresh_plugin.py

Stdlib only — no dependencies. Works on Windows, macOS, Linux.
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MARKETPLACE = "ghengis-skills-marketplace"
PLUGIN = "ghengis-skills"
# For first-time installs: if the marketplace clone is missing, bootstrap from GitHub
GITHUB_REPO = "https://github.com/Kgan01/ghengis-skills.git"
CLAUDE_HOME = Path.home() / ".claude"
PLUGINS_ROOT = CLAUDE_HOME / "plugins"


def log(msg: str, level: str = "INFO"):
    prefix = {"INFO": "[refresh]", "WARN": "[refresh WARN]", "ERROR": "[refresh ERROR]"}.get(level, "[refresh]")
    print(f"{prefix} {msg}")


def run_git(*args, cwd: Path) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git", *args], cwd=str(cwd),
        capture_output=True, text=True, check=False,
    )
    return result


def ensure_marketplace_clone() -> Path:
    """Locate or bootstrap the marketplace clone and sync it with origin/master."""
    known = PLUGINS_ROOT / "known_marketplaces.json"
    marketplace_path = None
    if known.exists():
        try:
            registry = json.loads(known.read_text(encoding="utf-8"))
            entry = registry.get(MARKETPLACE)
            if entry:
                install_location = entry.get("installLocation") or entry.get("install_location")
                if install_location:
                    marketplace_path = Path(install_location)
        except (json.JSONDecodeError, OSError) as e:
            log(f"Couldn't parse {known}: {e}", "WARN")

    if not marketplace_path:
        marketplace_path = PLUGINS_ROOT / "marketplaces" / MARKETPLACE

    if not marketplace_path.exists():
        log(f"Marketplace clone missing — bootstrapping at {marketplace_path}")
        marketplace_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "clone", GITHUB_REPO, str(marketplace_path)],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            log(f"git clone failed: {result.stderr.strip()}", "ERROR")
            sys.exit(1)
    else:
        log(f"Marketplace clone found at {marketplace_path}")

    # Force-sync to origin/master
    log("Fetching latest from origin...")
    result = run_git("fetch", "origin", "master", cwd=marketplace_path)
    if result.returncode != 0:
        log(f"git fetch failed: {result.stderr.strip()}", "ERROR")
        sys.exit(1)

    # Check if we're already at origin/master
    local = run_git("rev-parse", "HEAD", cwd=marketplace_path).stdout.strip()
    remote = run_git("rev-parse", "origin/master", cwd=marketplace_path).stdout.strip()
    if local == remote:
        log(f"Marketplace already at {local[:8]} — no fetch-level changes")
    else:
        log(f"Resetting marketplace clone to origin/master ({remote[:8]})")
        result = run_git("reset", "--hard", "origin/master", cwd=marketplace_path)
        if result.returncode != 0:
            log(f"git reset failed: {result.stderr.strip()}", "ERROR")
            sys.exit(1)

    return marketplace_path


def read_new_version(marketplace_path: Path) -> tuple[str, Path]:
    """Read the version from plugin.json and return (version, plugin_source_dir)."""
    plugin_dir = marketplace_path / "plugins" / PLUGIN
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
    if not plugin_json.exists():
        log(f"plugin.json not found at {plugin_json}", "ERROR")
        sys.exit(1)
    try:
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        log(f"plugin.json invalid: {e}", "ERROR")
        sys.exit(1)
    version = data.get("version")
    if not version:
        log("plugin.json missing version field", "ERROR")
        sys.exit(1)
    return version, plugin_dir


def sync_cache(plugin_dir: Path, version: str) -> Path:
    """Copy the fresh plugin dir into the cache for the new version."""
    cache_dir = PLUGINS_ROOT / "cache" / MARKETPLACE / PLUGIN / version
    if cache_dir.exists():
        log(f"Cache already exists at {cache_dir} — refreshing contents")
        shutil.rmtree(cache_dir)
    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(plugin_dir, cache_dir)
    log(f"Copied plugin to cache: {cache_dir}")
    return cache_dir


def update_installed_plugins(version: str, cache_dir: Path, marketplace_path: Path):
    """Update installed_plugins.json to point at the new cached version."""
    installed_file = PLUGINS_ROOT / "installed_plugins.json"
    if not installed_file.exists():
        log(f"installed_plugins.json missing — creating skeleton")
        data = {"version": 2, "plugins": {}}
    else:
        try:
            data = json.loads(installed_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            log(f"installed_plugins.json invalid: {e}", "ERROR")
            sys.exit(1)

    key = f"{PLUGIN}@{MARKETPLACE}"
    plugins = data.setdefault("plugins", {})
    existing = plugins.get(key)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Get current git sha for tracking
    result = run_git("rev-parse", "HEAD", cwd=marketplace_path)
    sha = result.stdout.strip() if result.returncode == 0 else ""

    entry = {
        "scope": "user",
        "installPath": str(cache_dir),
        "version": version,
        "installedAt": (existing[0].get("installedAt") if existing else now_iso),
        "lastUpdated": now_iso,
        "gitCommitSha": sha,
    } if not existing else {
        **existing[0],
        "installPath": str(cache_dir),
        "version": version,
        "lastUpdated": now_iso,
        "gitCommitSha": sha,
    }

    plugins[key] = [entry]
    installed_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    log(f"Updated installed_plugins.json → {version}")


def main() -> int:
    log(f"Starting ghengis-skills refresh")
    marketplace_path = ensure_marketplace_clone()
    version, plugin_dir = read_new_version(marketplace_path)
    log(f"Target version: {version}")
    cache_dir = sync_cache(plugin_dir, version)
    update_installed_plugins(version, cache_dir, marketplace_path)
    log("")
    log(f"Done. Plugin pinned to {version}.")
    log("Next: run /reload-plugins in Claude Code to activate.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("Cancelled", "WARN")
        sys.exit(130)
