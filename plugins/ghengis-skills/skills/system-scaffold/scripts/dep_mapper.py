"""
system-scaffold Stage 4 — Dependency Mapper (Windows v1).

For each candidate-to-move path from resolved.json, find what references it:
- Registry install paths (HKLM/HKCU Uninstall keys + common install-path values)
- NTFS junctions / reparse-point targets
- .lnk shortcut targets (Desktop, Start Menu, taskbar pinned, quick launch)
- Environment variables (PATH, PYTHONPATH, JAVA_HOME, OLLAMA_MODELS, HF_HOME, etc.)
- OneDrive sync state (any path under %OneDrive%)
- WSL2 distro registrations (HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss)

Output: dependencies.json — per-candidate list of references that would break if
the path moved without coordinating those references.

Pure Python + PowerShell shell-outs. Windows-specific; will move behind OSAdapter
for the Mac port.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
from pathlib import Path

DEP_MAPPER_VERSION = "1"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ps(script: str, timeout: int = 60) -> tuple[int, str, str]:
    """Run a PowerShell script and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, "", str(e)


def _norm(p: str) -> str:
    """Normalize a path for comparison: lowercase, backslash separators, no trailing sep."""
    if not p:
        return ""
    return p.replace("/", "\\").rstrip("\\").lower()


def _path_matches_candidate(ref_path: str, candidates: dict[str, dict]) -> str | None:
    """If ref_path is equal to or under any candidate path, return the candidate's normalized key.
    Otherwise return None."""
    rp = _norm(ref_path)
    if not rp:
        return None
    # Direct match
    if rp in candidates:
        return rp
    # Prefix match (ref is under a candidate)
    for cand in candidates:
        if rp.startswith(cand + "\\"):
            return cand
    return None


# ---------------------------------------------------------------------------
# Reference sources
# ---------------------------------------------------------------------------


def _extract_first_path(raw: str) -> str:
    """Pull the first absolute path out of a registry value that may be
    quoted or followed by args. Handles:
    - `"C:\\Foo\\bar.exe" /args`  → `C:\\Foo\\bar.exe`
    - `C:\\Foo\\bar.exe,0`         → `C:\\Foo\\bar.exe`
    - `C:\\Foo\\bar.exe /args`     → `C:\\Foo\\bar.exe` (truncates at first space NOT inside quotes)
    Returns "" if no drive-letter path is found.
    """
    if not raw:
        return ""
    s = raw.strip()
    # Quoted path
    if s.startswith('"'):
        end = s.find('"', 1)
        if end > 1:
            return s[1:end]
    # Strip trailing ",0" style icon resource refs
    if "," in s:
        before_comma = s.split(",")[0].strip().strip('"')
        if len(before_comma) > 2 and before_comma[1:3] == ":\\":
            s = before_comma
    # Truncate at first space if path looks like exe+args
    if " " in s and s.lower().endswith((".exe", ".dll", ".bat", ".cmd")) is False:
        # Only truncate if a drive-letter precedes (else leave whole)
        space = s.find(" ")
        candidate = s[:space]
        if len(candidate) > 2 and candidate[1:3] == ":\\":
            s = candidate
    return s.strip().strip('"')


def gather_registry_install_paths() -> list[dict]:
    """Pull InstallLocation / Path-style values from common Uninstall keys."""
    # NOTE: cleaning of the raw value (quote/8.3/env expansion) happens Python-side
    # via _extract_first_path + Path.resolve() for correctness across edge cases.
    ps = r"""
$paths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
    'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
)
$results = @()
foreach ($base in $paths) {
    if (-not (Test-Path $base)) { continue }
    Get-ChildItem $base -ErrorAction SilentlyContinue | ForEach-Object {
        $props = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
        if ($props) {
            foreach ($valueName in @('InstallLocation','InstallPath','InstallDir','UninstallString','DisplayIcon','Path')) {
                $val = $props.$valueName
                if ($val) {
                    $expanded = [System.Environment]::ExpandEnvironmentVariables($val)
                    $results += [pscustomobject]@{
                        DisplayName  = "$($props.DisplayName)"
                        Key          = "$($_.Name)"
                        ValueName    = $valueName
                        Value        = "$expanded"
                    }
                }
            }
        }
    }
}
$results | ConvertTo-Json -Compress -Depth 3
"""
    rc, out, err = _ps(ps, timeout=120)
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        # Clean each raw value Python-side via _extract_first_path
        cleaned = []
        for r in data:
            path = _extract_first_path(r.get("Value", "") or "")
            if path and len(path) > 2 and path[1:3] == ":\\":
                r["Value"] = path
                cleaned.append(r)
        return cleaned
    except json.JSONDecodeError:
        return []


# ---------------------------------------------------------------------------
# Additional reference sources (validator-flagged gaps)
# ---------------------------------------------------------------------------


def gather_services() -> list[dict]:
    """Windows Services — ImagePath points at the executable."""
    ps = r"""
$base = 'HKLM:\SYSTEM\CurrentControlSet\Services'
if (-not (Test-Path $base)) { '[]' | Write-Output; exit }
$results = @()
Get-ChildItem $base -ErrorAction SilentlyContinue | ForEach-Object {
    $props = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
    if ($props -and $props.ImagePath) {
        $expanded = [System.Environment]::ExpandEnvironmentVariables($props.ImagePath)
        $results += [pscustomobject]@{
            ServiceName = "$($_.PSChildName)"
            ImagePath   = "$expanded"
        }
    }
}
$results | ConvertTo-Json -Compress -Depth 3
"""
    rc, out, _ = _ps(ps, timeout=60)
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        cleaned = []
        for r in data:
            path = _extract_first_path(r.get("ImagePath", "") or "")
            if path and len(path) > 2 and path[1:3] == ":\\":
                r["ImagePath"] = path
                cleaned.append(r)
        return cleaned
    except json.JSONDecodeError:
        return []


def gather_scheduled_tasks() -> list[dict]:
    """Scheduled Tasks — Execute path on each task action."""
    ps = r"""
$results = @()
try {
    Get-ScheduledTask -ErrorAction SilentlyContinue | ForEach-Object {
        $task = $_
        foreach ($action in $task.Actions) {
            if ($action.Execute) {
                $expanded = [System.Environment]::ExpandEnvironmentVariables($action.Execute)
                $results += [pscustomobject]@{
                    TaskName = "$($task.TaskName)"
                    TaskPath = "$($task.TaskPath)"
                    Execute  = "$expanded"
                }
            }
        }
    }
} catch { }
$results | ConvertTo-Json -Compress -Depth 3
"""
    rc, out, _ = _ps(ps, timeout=90)
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        cleaned = []
        for r in data:
            path = _extract_first_path(r.get("Execute", "") or "")
            if path and len(path) > 2 and path[1:3] == ":\\":
                r["Execute"] = path
                cleaned.append(r)
        return cleaned
    except json.JSONDecodeError:
        return []


def gather_app_paths() -> list[dict]:
    """App Paths — shell uses these for `start <appname>`."""
    ps = r"""
$paths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths',
    'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths'
)
$results = @()
foreach ($base in $paths) {
    if (-not (Test-Path $base)) { continue }
    Get-ChildItem $base -ErrorAction SilentlyContinue | ForEach-Object {
        $props = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
        if ($props) {
            foreach ($valueName in @('(default)','Path')) {
                $val = $props.$valueName
                if ($val) {
                    $expanded = [System.Environment]::ExpandEnvironmentVariables($val)
                    $results += [pscustomobject]@{
                        AppName   = "$($_.PSChildName)"
                        ValueName = $valueName
                        Value     = "$expanded"
                    }
                }
            }
        }
    }
}
$results | ConvertTo-Json -Compress -Depth 3
"""
    rc, out, _ = _ps(ps, timeout=60)
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        cleaned = []
        for r in data:
            path = _extract_first_path(r.get("Value", "") or "")
            if path and len(path) > 2 and path[1:3] == ":\\":
                r["Value"] = path
                cleaned.append(r)
        return cleaned
    except json.JSONDecodeError:
        return []


def gather_com_classes() -> list[dict]:
    """HKCR\\CLSID\\*\\{InprocServer32,LocalServer32} default values.

    Implemented via winreg (stdlib) instead of PowerShell — PS over 7800+
    CLSID keys exceeded our 300s budget. winreg is ~30x faster.
    """
    try:
        import winreg
    except ImportError:
        # Non-Windows — gracefully skip
        return []

    results: list[dict] = []
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "CLSID") as clsid_root:
            i = 0
            while True:
                try:
                    clsid = winreg.EnumKey(clsid_root, i)
                    i += 1
                except OSError:
                    break
                for server_kind in ("InprocServer32", "LocalServer32"):
                    try:
                        with winreg.OpenKey(clsid_root, rf"{clsid}\{server_kind}") as sk:
                            val, _ = winreg.QueryValueEx(sk, None)
                            if val:
                                expanded = os.path.expandvars(val)
                                results.append(
                                    {
                                        "CLSID": clsid,
                                        "ServerKind": server_kind,
                                        "Value": expanded,
                                    }
                                )
                    except OSError:
                        # Subkey doesn't exist or has no default value
                        continue
    except OSError as e:
        print(f"[dep_mapper] WARN: winreg HKCR\\CLSID open failed: {e}", file=sys.stderr)
        return []

    cleaned = []
    for r in results:
        path = _extract_first_path(r["Value"])
        if path and len(path) > 2 and path[1:3] == ":\\":
            r["Value"] = path
            cleaned.append(r)
    return cleaned


def gather_file_associations() -> list[dict]:
    """HKCR\\<ext>\\shell\\open\\command default value."""
    ps = r"""
$base = 'Registry::HKEY_CLASSES_ROOT'
$results = @()
Get-ChildItem -Path $base -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -match '^\.[a-z0-9]+$' -or $_.PSChildName -match 'file$' } | ForEach-Object {
    $cmd = Join-Path $_.PSPath 'shell\open\command'
    if (Test-Path $cmd) {
        $val = (Get-ItemProperty $cmd -ErrorAction SilentlyContinue).'(default)'
        if ($val) {
            $expanded = [System.Environment]::ExpandEnvironmentVariables($val)
            $results += [pscustomobject]@{
                Ext   = "$($_.PSChildName)"
                Value = "$expanded"
            }
        }
    }
}
$results | ConvertTo-Json -Compress -Depth 3
"""
    rc, out, err = _ps(ps, timeout=300)
    if rc != 0:
        print(f"[dep_mapper] WARN: file associations walk failed (rc={rc}): {err.strip()[:200]}", file=sys.stderr)
        return []
    if not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        cleaned = []
        for r in data:
            path = _extract_first_path(r.get("Value", "") or "")
            if path and len(path) > 2 and path[1:3] == ":\\":
                r["Value"] = path
                cleaned.append(r)
        return cleaned
    except json.JSONDecodeError:
        return []


def gather_autorun() -> list[dict]:
    """Run / RunOnce keys (HKCU + HKLM, both 64 and 32-bit views)."""
    ps = r"""
$bases = @(
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce'
)
$results = @()
foreach ($b in $bases) {
    if (-not (Test-Path $b)) { continue }
    $props = Get-ItemProperty $b -ErrorAction SilentlyContinue
    if ($props) {
        $props.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
            $expanded = [System.Environment]::ExpandEnvironmentVariables($_.Value)
            $results += [pscustomobject]@{
                Hive    = $b
                Name    = "$($_.Name)"
                Value   = "$expanded"
            }
        }
    }
}
$results | ConvertTo-Json -Compress -Depth 3
"""
    rc, out, _ = _ps(ps, timeout=30)
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        cleaned = []
        for r in data:
            path = _extract_first_path(r.get("Value", "") or "")
            if path and len(path) > 2 and path[1:3] == ":\\":
                r["Value"] = path
                cleaned.append(r)
        return cleaned
    except json.JSONDecodeError:
        return []


def gather_defender_exclusions() -> list[str]:
    """Windows Defender path exclusions."""
    ps = r"""
$base = 'HKLM:\SOFTWARE\Microsoft\Windows Defender\Exclusions\Paths'
if (-not (Test-Path $base)) { '[]' | Write-Output; exit }
$props = Get-ItemProperty $base -ErrorAction SilentlyContinue
if (-not $props) { '[]' | Write-Output; exit }
$results = @()
$props.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
    $expanded = [System.Environment]::ExpandEnvironmentVariables($_.Name)
    $results += "$expanded"
}
$results | ConvertTo-Json -Compress
"""
    rc, out, _ = _ps(ps, timeout=30)
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, str):
            data = [data]
        return [p for p in data if p and len(p) > 2 and p[1:3] == ":\\"]
    except json.JSONDecodeError:
        return []


def gather_docker_data_folder() -> str | None:
    """Read Docker Desktop settings.json for the dataFolder (VHDX location)."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    settings = Path(appdata) / "Docker" / "settings.json"
    if not settings.exists():
        return None
    try:
        with open(settings, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg.get("dataFolder")
    except (json.JSONDecodeError, OSError):
        return None


def gather_env_var_refs() -> dict[str, list[str]]:
    """Return dict of var_name -> list of path fragments (PATH and friends split)."""
    interesting_vars = [
        "PATH", "PYTHONPATH", "JAVA_HOME", "GOPATH", "GOROOT", "CARGO_HOME",
        "RUSTUP_HOME", "ANDROID_HOME", "ANDROID_SDK_ROOT", "NDK_HOME",
        "VCPKG_ROOT", "CONDA_PREFIX", "OLLAMA_MODELS", "HF_HOME",
        "TRANSFORMERS_CACHE", "HUGGINGFACE_HUB_CACHE", "OneDrive", "OneDriveConsumer",
        "USERPROFILE", "LOCALAPPDATA", "APPDATA", "ProgramFiles", "ProgramFiles(x86)",
        "ProgramData", "TEMP", "TMP",
    ]
    out = {}
    for v in interesting_vars:
        val = os.environ.get(v)
        if not val:
            continue
        # PATH-like vars use ; on Windows
        if v in ("PATH", "PYTHONPATH"):
            entries = [p.strip() for p in val.split(";") if p.strip()]
            out[v] = entries
        else:
            out[v] = [val]
    return out


def gather_shortcut_targets() -> list[dict]:
    """Walk standard shortcut locations and read .lnk targets via WScript.Shell COM."""
    ps = r"""
$locations = @(
    "$env:USERPROFILE\Desktop",
    "$env:PUBLIC\Desktop",
    "$env:APPDATA\Microsoft\Windows\Start Menu",
    "$env:ProgramData\Microsoft\Windows\Start Menu",
    "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch",
    "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar",
    "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch\User Pinned\StartMenu"
)
$shell = New-Object -ComObject WScript.Shell
$results = @()
foreach ($loc in $locations) {
    if (-not (Test-Path $loc)) { continue }
    Get-ChildItem -Path $loc -Recurse -Filter *.lnk -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $sc = $shell.CreateShortcut($_.FullName)
            if ($sc.TargetPath) {
                $results += [pscustomobject]@{
                    LnkPath = "$($_.FullName)"
                    Target  = "$($sc.TargetPath)"
                    WorkDir = "$($sc.WorkingDirectory)"
                }
            }
        } catch { }
    }
}
$results | ConvertTo-Json -Compress -Depth 3
"""
    rc, out, err = _ps(ps, timeout=180)
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        return data
    except json.JSONDecodeError:
        return []


def gather_wsl_distros() -> list[dict]:
    """Read registered WSL2 distros + their BasePath (where the VHDX lives)."""
    ps = r"""
$base = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss'
if (-not (Test-Path $base)) { @() | ConvertTo-Json; exit }
$results = @()
Get-ChildItem $base -ErrorAction SilentlyContinue | ForEach-Object {
    $props = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
    if ($props -and $props.BasePath) {
        $results += [pscustomobject]@{
            DistroName = "$($props.DistributionName)"
            BasePath   = "$($props.BasePath)" -replace '^\\\\\?\\',''
            State      = "$($props.State)"
            Version    = "$($props.Version)"
        }
    }
}
$results | ConvertTo-Json -Compress -Depth 3
"""
    rc, out, err = _ps(ps, timeout=30)
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        return data
    except json.JSONDecodeError:
        return []


def gather_reparse_targets(root_paths: list[str]) -> list[dict]:
    """Find every NTFS reparse point under the given roots and capture its target.

    Uses PowerShell's Get-Item .Target / .LinkTarget. Slower than necessary but
    correct. Restricted to known relevant roots to avoid scanning whole disks.
    """
    if not root_paths:
        return []
    ps_paths = ",".join(f"'{p}'" for p in root_paths)
    ps = f"""
$roots = @({ps_paths})
$results = @()
foreach ($r in $roots) {{
    if (-not (Test-Path $r)) {{ continue }}
    Get-ChildItem -Path $r -Recurse -Force -ErrorAction SilentlyContinue -Attributes ReparsePoint |
        ForEach-Object {{
            try {{
                $target = $_.Target
                if ($null -eq $target) {{ $target = $_.LinkTarget }}
                if ($target) {{
                    $results += [pscustomobject]@{{
                        ReparsePath = "$($_.FullName)"
                        Target      = "$target"
                        Kind        = "$($_.LinkType)"
                    }}
                }}
            }} catch {{ }}
        }}
}}
$results | ConvertTo-Json -Compress -Depth 3
"""
    rc, out, err = _ps(ps, timeout=300)
    if rc != 0 or not out.strip():
        return []
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]
        return data
    except json.JSONDecodeError:
        return []


# ---------------------------------------------------------------------------
# Candidate selection
# ---------------------------------------------------------------------------


# Classes that are candidates to be moved (worth checking dependencies for)
MOVABLE_CLASSES = {
    "project-active",
    "project-stale",
    "project-likely",
    "media-video-active",
    "media-video-cold",
    "media-video-uncertain",
    "media-photo-active",
    "media-photo-cold",
    "media-photo-uncertain",
    "media-audio",
    "media-audio-active",
    "media-audio-uncertain",
    "documents",
    "archive",
    "downloads",
    "desktop-scratch",
    "dev-models",
    "dev-toolchain",
    "dev-vm",
    "dev-tool",
    "tools-archive",
    "app-data",
    "virgil-videos",
    "aaron-boland",
}


def select_candidates(resolved: dict, min_size_bytes: int = 50 * 1024**2) -> dict[str, dict]:
    """Return dict of normalized_path -> candidate node. Filters by class + size."""
    out = {}
    for n in resolved.get("nodes", []):
        cls = n.get("resolved_class")
        size = n.get("size_bytes", 0)
        if cls in MOVABLE_CLASSES and size >= min_size_bytes:
            out[_norm(n["path"])] = n
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def map_dependencies(resolved: dict, min_candidate_mb: int) -> dict:
    started_at = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    candidates = select_candidates(resolved, min_size_bytes=min_candidate_mb * 1024**2)

    # Index references
    deps_by_path: dict[str, list[dict]] = {p: [] for p in candidates}

    # 1) Registry install paths
    reg_refs = gather_registry_install_paths()
    for r in reg_refs:
        val = r.get("Value", "")
        match = _path_matches_candidate(val, candidates)
        if match:
            deps_by_path[match].append(
                {
                    "type": "registry",
                    "key": r.get("Key", ""),
                    "value_name": r.get("ValueName", ""),
                    "display_name": r.get("DisplayName", ""),
                    "raw_value": val,
                }
            )

    # 2) Environment variables
    env_refs = gather_env_var_refs()
    for var, entries in env_refs.items():
        for entry in entries:
            match = _path_matches_candidate(entry, candidates)
            if match:
                deps_by_path[match].append(
                    {
                        "type": "env_var",
                        "var": var,
                        "fragment": entry,
                    }
                )

    # 3) Shortcuts
    shortcuts = gather_shortcut_targets()
    for s in shortcuts:
        target = s.get("Target", "")
        match = _path_matches_candidate(target, candidates)
        if match:
            deps_by_path[match].append(
                {
                    "type": "shortcut",
                    "lnk_path": s.get("LnkPath", ""),
                    "target": target,
                    "workdir": s.get("WorkDir", ""),
                }
            )

    # 4) WSL distros
    wsl_distros = gather_wsl_distros()
    for d in wsl_distros:
        base = d.get("BasePath", "")
        match = _path_matches_candidate(base, candidates)
        if match:
            deps_by_path[match].append(
                {
                    "type": "wsl_distro",
                    "distro_name": d.get("DistroName", ""),
                    "base_path": base,
                    "state": d.get("State", ""),
                }
            )

    # 5) Reparse points — scan known reparse-prone roots. Restricted to
    # standard system locations because recursive scans of full drive roots
    # on multi-TB drives explode (e.g., E:\ 6.3 TB times out PowerShell).
    # v2: extend cross-drive scanning to top-N levels only or use index APIs.
    reparse_roots = [
        os.environ.get("USERPROFILE", "C:\\Users\\krist"),
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\ProgramData",
    ]
    reparse_roots = [r for r in reparse_roots if r and Path(r).exists()]
    reparse_refs = gather_reparse_targets(reparse_roots)
    for r in reparse_refs:
        target = r.get("Target", "")
        match = _path_matches_candidate(target, candidates)
        if match:
            deps_by_path[match].append(
                {
                    "type": "reparse_point",
                    "reparse_path": r.get("ReparsePath", ""),
                    "target": target,
                    "kind": r.get("Kind", ""),
                }
            )

    # 6) Services
    services = gather_services()
    for s in services:
        match = _path_matches_candidate(s.get("ImagePath", ""), candidates)
        if match:
            deps_by_path[match].append(
                {"type": "service", "service_name": s.get("ServiceName"), "image_path": s.get("ImagePath")}
            )

    # 7) Scheduled tasks
    tasks = gather_scheduled_tasks()
    for t in tasks:
        match = _path_matches_candidate(t.get("Execute", ""), candidates)
        if match:
            deps_by_path[match].append(
                {"type": "scheduled_task", "task_name": t.get("TaskName"), "task_path": t.get("TaskPath"), "execute": t.get("Execute")}
            )

    # 8) App Paths
    app_paths = gather_app_paths()
    for a in app_paths:
        match = _path_matches_candidate(a.get("Value", ""), candidates)
        if match:
            deps_by_path[match].append(
                {"type": "app_path", "app_name": a.get("AppName"), "value_name": a.get("ValueName"), "value": a.get("Value")}
            )

    # 9) COM CLSID registrations
    com_classes = gather_com_classes()
    for c in com_classes:
        match = _path_matches_candidate(c.get("Value", ""), candidates)
        if match:
            deps_by_path[match].append(
                {"type": "com_class", "clsid": c.get("CLSID"), "server_kind": c.get("ServerKind"), "value": c.get("Value")}
            )

    # 10) File associations
    file_assocs = gather_file_associations()
    for fa in file_assocs:
        match = _path_matches_candidate(fa.get("Value", ""), candidates)
        if match:
            deps_by_path[match].append(
                {"type": "file_association", "ext": fa.get("Ext"), "value": fa.get("Value")}
            )

    # 11) AutoRun
    autoruns = gather_autorun()
    for ar in autoruns:
        match = _path_matches_candidate(ar.get("Value", ""), candidates)
        if match:
            deps_by_path[match].append(
                {"type": "autorun", "hive": ar.get("Hive"), "name": ar.get("Name"), "value": ar.get("Value")}
            )

    # 12) Defender exclusions
    defender_excl = gather_defender_exclusions()
    for excl in defender_excl:
        match = _path_matches_candidate(excl, candidates)
        if match:
            deps_by_path[match].append(
                {"type": "defender_exclusion", "path": excl, "note": "moving this loses Defender exclusion; rescan may quarantine"}
            )

    # 13) Docker dataFolder
    docker_data = gather_docker_data_folder()
    if docker_data:
        match = _path_matches_candidate(docker_data, candidates)
        if match:
            deps_by_path[match].append(
                {"type": "docker_settings", "data_folder": docker_data, "note": "Docker Desktop reads from this path; relocate via Docker settings"}
            )

    # 14) OneDrive sync flag — any candidate under %OneDrive%
    onedrive_root = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
    if onedrive_root:
        od_norm = _norm(onedrive_root)
        for cand in candidates:
            if cand == od_norm or cand.startswith(od_norm + "\\"):
                deps_by_path[cand].append(
                    {
                        "type": "onedrive_sync",
                        "onedrive_root": onedrive_root,
                        "note": "moving this path affects OneDrive sync state",
                    }
                )

    # Stats
    with_deps = sum(1 for v in deps_by_path.values() if v)
    total_refs = sum(len(v) for v in deps_by_path.values())

    return {
        "version": DEP_MAPPER_VERSION,
        "mapper": "system-scaffold/dep_mapper.py",
        "ran_at": started_at,
        "config": {
            "min_candidate_mb": min_candidate_mb,
            "reparse_scan_roots": reparse_roots,
        },
        "stats": {
            "candidates_checked": len(candidates),
            "candidates_with_dependencies": with_deps,
            "total_references_found": total_refs,
            "registry_refs": len(reg_refs),
            "env_var_buckets_found": len(env_refs),
            "shortcuts_walked": len(shortcuts),
            "wsl_distros_found": len(wsl_distros),
            "reparse_points_walked": len(reparse_refs),
            "services_scanned": len(services),
            "scheduled_tasks_scanned": len(tasks),
            "app_paths_scanned": len(app_paths),
            "com_classes_scanned": len(com_classes),
            "file_associations_scanned": len(file_assocs),
            "autoruns_scanned": len(autoruns),
            "defender_exclusions_scanned": len(defender_excl),
            "docker_data_folder_found": bool(docker_data),
        },
        "dependencies": [
            {
                "path": candidates[p]["path"],
                "drive": candidates[p].get("drive"),
                "resolved_class": candidates[p].get("resolved_class"),
                "size_bytes": candidates[p].get("size_bytes", 0),
                "references": refs,
            }
            for p, refs in deps_by_path.items()
            if refs
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="system-scaffold Stage 4 dependency mapper")
    parser.add_argument("resolved", help="path to resolved.json from Stage 3")
    parser.add_argument(
        "--output",
        help="output path for dependencies.json. Default: same dir as resolved.",
    )
    parser.add_argument(
        "--min-candidate-mb",
        type=int,
        default=50,
        help="min size (MB) for a node to be considered a movable candidate (default: 50)",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    res_path = Path(args.resolved)
    if not res_path.exists():
        print(f"[dep_mapper] error: {res_path} not found", file=sys.stderr)
        return 1
    out_path = Path(args.output) if args.output else res_path.parent / "dependencies.json"

    resolved = json.load(open(res_path, "r", encoding="utf-8"))

    if not args.quiet:
        print(f"[dep_mapper] gathering references — this may take ~1-3 min...", file=sys.stderr)

    result = map_dependencies(resolved, min_candidate_mb=args.min_candidate_mb)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if not args.quiet:
        s = result["stats"]
        print(f"[dep_mapper] candidates checked: {s['candidates_checked']}", file=sys.stderr)
        print(f"[dep_mapper] candidates with refs: {s['candidates_with_dependencies']}", file=sys.stderr)
        print(f"[dep_mapper] total references found: {s['total_references_found']}", file=sys.stderr)
        print(f"[dep_mapper]   registry refs scanned: {s['registry_refs']}", file=sys.stderr)
        print(f"[dep_mapper]   env vars considered: {s['env_var_buckets_found']}", file=sys.stderr)
        print(f"[dep_mapper]   .lnk shortcuts walked: {s['shortcuts_walked']}", file=sys.stderr)
        print(f"[dep_mapper]   WSL distros found: {s['wsl_distros_found']}", file=sys.stderr)
        print(f"[dep_mapper]   reparse points walked: {s['reparse_points_walked']}", file=sys.stderr)
        print(f"[dep_mapper]   services scanned: {s['services_scanned']}", file=sys.stderr)
        print(f"[dep_mapper]   scheduled tasks scanned: {s['scheduled_tasks_scanned']}", file=sys.stderr)
        print(f"[dep_mapper]   app paths scanned: {s['app_paths_scanned']}", file=sys.stderr)
        print(f"[dep_mapper]   COM classes scanned: {s['com_classes_scanned']}", file=sys.stderr)
        print(f"[dep_mapper]   file associations scanned: {s['file_associations_scanned']}", file=sys.stderr)
        print(f"[dep_mapper]   autoruns scanned: {s['autoruns_scanned']}", file=sys.stderr)
        print(f"[dep_mapper]   defender exclusions scanned: {s['defender_exclusions_scanned']}", file=sys.stderr)
        print(f"[dep_mapper]   docker data folder found: {s['docker_data_folder_found']}", file=sys.stderr)
        print(f"[dep_mapper] wrote {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
