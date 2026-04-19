#!/usr/bin/env python3
"""Cross-platform browser opening utility."""

import os
import sys
import subprocess
import platform

def get_platform() -> str:
    """Detect current platform: 'windows', 'macos', 'wsl', or 'linux'."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    return "wsl"
        except (FileNotFoundError, PermissionError):
            pass
        return "linux"
    return "linux"

def open_browser(url: str) -> bool:
    """Open URL in default browser. Works on Windows, macOS, Linux, and WSL."""
    plat = get_platform()

    try:
        if plat == "windows":
            os.startfile(url)
            return True

        elif plat == "wsl":
            subprocess.Popen(
                ["cmd.exe", "/c", "start", "", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True

        elif plat == "macos":
            subprocess.Popen(
                ["open", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True

        else:  # linux
            for cmd in ["xdg-open", "sensible-browser", "x-www-browser", "gnome-open"]:
                try:
                    subprocess.Popen([cmd, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                except FileNotFoundError:
                    continue

        return False
    except Exception:
        return False

CURRENT_PLATFORM = get_platform()
