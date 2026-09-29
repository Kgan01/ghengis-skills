#!/usr/bin/env python3
"""
Push a NotebookLM learning pack to the NotebookLM account of whoever runs it.

Uses the UNOFFICIAL notebooklm-py CLI (mimics the web client via stored
browser cookies). Nothing account-specific ships with this script: it acts on
the Google account the local user logged in with, stored on their machine
under ~/.notebooklm/. One-time setup is the notebooklm-pack-setup skill, or:

    pip install --user "notebooklm-py[browser]"
    notebooklm login            # interactive, the user's own Google account

This script:
  1. reads the pack's 00-MANIFEST.md for a notebook title + audio focus prompt
  2. creates a notebook
  3. uploads every NN-*.md source file (skips the manifest itself)
  4. optionally kicks off the Audio Overview with the manifest's focus prompt

It is deliberately CLI-driven (the documented stable surface) rather than the
async SDK. Idempotency is NOT guaranteed — re-running creates a second
notebook; pass --notebook <id> to target an existing one.

Auth and credentials belong to the user; this script never handles Google
passwords. If auth is missing it prints the login command and exits.

Usage:
    python push_pack.py --check [--profile NAME]
    python push_pack.py <pack_dir> [--audio] [--notebook ID] [--profile NAME] [--dry-run]

Exit codes: 0 ok, 1 upload/create failure, 2 not logged in, 3 CLI not installed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

INSTALL_HINT = 'pip install --user "notebooklm-py[browser]"'


def _candidates() -> list[str]:
    """notebooklm is installed to the per-user scripts dir, often off PATH."""
    found = ["notebooklm"]
    appdata = os.environ.get("APPDATA")
    if appdata:
        found += sorted(
            (str(p) for p in Path(appdata, "Python").glob("Python*/Scripts/notebooklm.exe")),
            reverse=True,
        )
    found.append(str(Path.home() / ".local" / "bin" / "notebooklm"))
    found += sorted(
        (str(p) for p in Path.home().glob("Library/Python/*/bin/notebooklm")),
        reverse=True,
    )
    return found


def _cli() -> str | None:
    for c in _candidates():
        try:
            r = subprocess.run([c, "--version"], capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                return c
        except (FileNotFoundError, OSError):
            continue
    return None


def _base(cli: str, profile: str | None) -> list[str]:
    return [cli, "-p", profile] if profile else [cli]


def _run(base: list[str], args: list, dry: bool, **kw) -> subprocess.CompletedProcess:
    print(f"  $ notebooklm {' '.join(args)}")
    if dry:
        return subprocess.CompletedProcess(args, 0, "", "")
    return subprocess.run([*base, *args], text=True, **kw)


def _auth_ok(base: list[str], test: bool = False) -> bool:
    """Local cookie check; test=True also confirms NotebookLM accepts them."""
    cmd = [*base, "auth", "check", "--json"] + (["--test"] if test else [])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            return r.returncode == 0
        checks = data.get("checks", {})
        if test and checks.get("token_fetch") is not True:
            return False
        return data.get("status") == "ok" or checks.get("cookies_present") is True
    except Exception:
        return False


def check(profile: str | None) -> int:
    """Report whether this machine is ready to push. Prints no account data."""
    cli = _cli()
    if not cli:
        print(f"CLI: not installed\n  Install: {INSTALL_HINT}")
        return 3
    print(f"CLI: {cli}")
    if not _auth_ok(_base(cli, profile), test=True):
        print("Auth: not logged in (or session expired)\n"
              "  Run once, with your own Google account:\n\n    notebooklm login\n")
        return 2
    print(f"Auth: ok (profile: {profile or 'active'})\nReady to push.")
    return 0


def parse_manifest(pack: Path) -> tuple[str, str]:
    """(notebook_title, audio_focus_prompt) from 00-MANIFEST.md."""
    mf = pack / "00-MANIFEST.md"
    title = pack.name.replace("-", " ").title()
    audio = "Give an engaging deep-dive overview of these sources."
    if not mf.exists():
        return title, audio
    text = mf.read_text(encoding="utf-8")
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if m:
        title = m.group(1).replace("Learning Pack:", "").strip()
    # Audio focus prompt: the first blockquote after an "Audio Overview" heading
    am = re.search(r"Audio Overview.*?\n((?:>.*\n?)+)", text)
    if am:
        audio = " ".join(l.lstrip("> ").rstrip()
                         for l in am.group(1).splitlines() if l.strip())
    return title, audio


def main() -> int:
    # Windows consoles default to cp1252; keep non-ASCII titles printable.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack_dir", nargs="?")
    ap.add_argument("--check", action="store_true",
                    help="only report whether the CLI is installed and logged in")
    ap.add_argument("--audio", action="store_true",
                    help="also kick off the Audio Overview (podcast)")
    ap.add_argument("--notebook", help="target an existing notebook ID instead of creating one")
    ap.add_argument("--profile", help="notebooklm profile to use (one per Google account)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.check:
        return check(args.profile)
    if not args.pack_dir:
        ap.error("pack_dir is required unless --check is given")

    pack = Path(args.pack_dir).resolve()
    if not pack.is_dir():
        sys.exit(f"not a directory: {pack}")
    sources = sorted(p for p in pack.glob("[0-9][0-9]-*.md")
                     if not p.name.startswith("00-"))
    if not sources:
        sys.exit(f"no NN-*.md source files in {pack}")

    title, audio_prompt = parse_manifest(pack)
    print(f"Pack: {pack.name}\nTitle: {title}\nSources: {len(sources)}")

    # A dry run must work before the CLI is installed or logged in.
    if args.dry_run:
        base = ["notebooklm"]
    else:
        cli = _cli()
        if not cli:
            print(f"notebooklm CLI not found. Install: {INSTALL_HINT}")
            return 3
        base = _base(cli, args.profile)
        if not _auth_ok(base):
            print("Not logged in to NotebookLM. Run this once (interactive, your "
                  "own Google account):\n\n    notebooklm login\n")
            return 2

    nb_id = args.notebook
    if not nb_id:
        r = _run(base, ["create", title, "--json"], args.dry_run,
                 capture_output=True)
        if not args.dry_run:
            if r.returncode != 0:
                sys.exit(f"create failed: {r.stderr or r.stdout}")
            try:
                j = json.loads(r.stdout)
                nb_id = (j.get("id") or j.get("notebook_id")
                         or j.get("notebook", {}).get("id"))
            except (json.JSONDecodeError, AttributeError):
                nb_id = None
            if not nb_id:
                sys.exit(f"could not parse notebook id from: {r.stdout}")
        else:
            nb_id = "<dry-run-id>"
    print(f"Notebook: {nb_id}")

    failed = 0
    for src in sources:
        r = _run(base, ["source", "add", str(src), "-n", nb_id,
                        "--type", "file", "--title", src.stem], args.dry_run,
                 capture_output=True)
        if not args.dry_run and r.returncode != 0:
            failed += 1
            print(f"  ! failed to add {src.name}: {r.stderr or r.stdout}",
                  file=sys.stderr)

    if args.audio:
        print("Kicking off Audio Overview (this takes a few minutes server-side)...")
        _run(base, ["generate", "audio", audio_prompt, "-n", nb_id],
             args.dry_run)

    print(f"\nDone. Open: https://notebooklm.google.com/notebook/{nb_id}")
    if failed:
        print(f"{failed} of {len(sources)} sources failed to upload.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
