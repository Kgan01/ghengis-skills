#!/usr/bin/env python3
"""
public_leak_guard.py — block commits/pushes that would put private data in a PUBLIC repo.

Called from validate-commit.sh / validate-push.sh (PreToolUse on Bash). Reads the hook
JSON on stdin. Exit 2 + stderr = block (Claude Code shows the reason to the model).

What counts as private:
  1. Built-in: this user's home-folder paths (C:\\Users\\<you>, /Users/<you>, /home/<you>)
     and Tailscale IPs (the CGNAT range 100.64/10).
  2. The personal denylist at ~/.claude/private-denylist.txt — kept OUTSIDE every repo:
       Some Literal Term          case-insensitive substring
       regex:<pattern>            case-insensitive regex
       folder-names:<dir>         every subfolder named "Last, First" (e.g. one per client)
                                  becomes "Last, First" and "First Last" — new clients are
                                  covered automatically, no names copied into the list
       # comment

Only lines ADDED by the staged diff (commit) or outgoing commits (push) are scanned.
Repos whose GitHub visibility is PRIVATE/INTERNAL are skipped. Unknown visibility
(no gh, non-GitHub remote) is treated as public.

Escape hatch for a verified false positive: GHENGIS_LEAK_GUARD=off in the environment.
Stdlib only.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
DENYLIST = Path(os.environ.get("GHENGIS_LEAK_DENYLIST", HOME / ".claude" / "private-denylist.txt"))
VIS_CACHE = HOME / ".claude" / "cache" / "repo-visibility.json"
VIS_TTL = 24 * 3600
TAILSCALE_IP = r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}\b"


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, r.stdout


def parse_command(command):
    """Return (repo_dir_or_None, push_target_or_None) from a git command line."""
    try:
        parts = shlex.split(command, posix=True)
    except ValueError:
        parts = command.split()
    repo, target = None, None
    for i, p in enumerate(parts):
        if p == "-C" and i + 1 < len(parts):
            repo = parts[i + 1]
        if p == "push":
            rest = [a for a in parts[i + 1:] if not a.startswith("-")]
            if rest:
                target = rest[0]
            break
    return repo, target


def github_slug(url):
    m = re.search(r"github\.com[:/]+([^/]+)/([^/\s]+?)(?:\.git)?/?$", url or "")
    return f"{m.group(1)}/{m.group(2)}" if m else None


def visibility(repo, target):
    url = target if target and ("://" in target or "@" in target) else None
    if not url:
        _, out = git(repo, "remote", "get-url", target or "origin")
        url = out.strip()
    slug = github_slug(url)
    if not slug:
        return "UNKNOWN", url or "(no remote)"
    cache = {}
    try:
        cache = json.loads(VIS_CACHE.read_text(encoding="utf-8"))
        hit = cache.get(slug)
        if hit and time.time() - hit["at"] < VIS_TTL:
            return hit["v"], slug
    except (OSError, ValueError, KeyError):
        pass
    try:
        r = subprocess.run(["gh", "repo", "view", slug, "--json", "visibility", "-q", ".visibility"],
                           capture_output=True, text=True, timeout=15)
        v = r.stdout.strip().upper() if r.returncode == 0 else "UNKNOWN"
    except (OSError, subprocess.TimeoutExpired):
        v = "UNKNOWN"
    if v != "UNKNOWN":
        cache[slug] = {"v": v, "at": time.time()}
        try:
            VIS_CACHE.parent.mkdir(parents=True, exist_ok=True)
            VIS_CACHE.write_text(json.dumps(cache), encoding="utf-8")
        except OSError:
            pass
    return v, slug


def load_patterns():
    pats = []  # (label, compiled regex)
    user = re.escape(HOME.name)
    pats.append(("home path", re.compile(rf"(?i)[a-z]:[\\/]+users[\\/]+{user}\b|/(?:Users|home)/{user}\b")))
    pats.append(("tailscale IP", re.compile(TAILSCALE_IP)))
    if not DENYLIST.exists():
        return pats
    for raw in DENYLIST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("regex:"):
            pats.append(("denylist regex", re.compile(line[6:], re.I)))
        elif line.startswith("folder-names:"):
            d = Path(line[13:].strip())
            if not d.is_dir():
                continue
            for child in d.iterdir():
                if not child.is_dir() or "," not in child.name:
                    continue
                last, first = [s.strip() for s in child.name.split(",", 1)]
                if not last or not first:
                    continue
                full = rf"\b{re.escape(last)}\s*,\s*{re.escape(first)}\b|\b{re.escape(first)}\s+{re.escape(last)}\b"
                pats.append(("private name", re.compile(full, re.I)))
        else:
            pats.append(("denylist term", re.compile(re.escape(line), re.I)))
    return pats


def added_lines(repo, mode, target=None):
    """Yield (file, text) for every added line headed out."""
    if mode == "commit":
        _, out = git(repo, "diff", "--cached", "-U0", "--no-color")
    else:
        rng = None
        if target:
            # Compare against what the remote actually has, so pushes by URL or to a
            # remote with no upstream set only scan the outgoing commits.
            code, out = git(repo, "ls-remote", target, "HEAD", "refs/heads/*")
            shas = {l.split()[0] for l in out.splitlines() if l.strip()} if code == 0 else set()
            known = [s for s in shas if git(repo, "cat-file", "-e", s + "^{commit}")[0] == 0]
            if known:
                rng = ["HEAD", "--not", *known]
        if rng is None:
            code, _ = git(repo, "rev-parse", "--abbrev-ref", "@{u}")
            rng = ["@{u}..HEAD"] if code == 0 else ["HEAD", "--not", "--remotes"]
        _, out = git(repo, "log", "-p", "-U0", "--no-color", "--format=", *rng)
    current = "?"
    for line in out.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("+") and not line.startswith("+++"):
            yield current, line[1:]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "push"
    if os.environ.get("GHENGIS_LEAK_GUARD", "").lower() == "off":
        return 0
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    command = data.get("tool_input", {}).get("command", "")
    if "git" not in command or mode not in command:
        return 0
    repo_arg, target = parse_command(command)
    repo = repo_arg or data.get("cwd") or os.getcwd()
    code, _ = git(repo, "rev-parse", "--git-dir")
    if code != 0:
        return 0

    forced = os.environ.get("GHENGIS_LEAK_GUARD_ASSUME", "").upper()
    vis, where = (forced, "(assumed)") if forced else visibility(repo, target)
    if vis in ("PRIVATE", "INTERNAL"):
        return 0

    pats = load_patterns()
    hits = []
    for f, text in added_lines(repo, mode, target):
        for label, rx in pats:
            if rx.search(text):
                hits.append((f, label))
    if not hits:
        return 0

    seen = sorted(set(hits))
    print(f"BLOCKED by public_leak_guard: this {mode} would put private data in "
          f"{where} (visibility: {vis}).", file=sys.stderr)
    for f, label in seen[:25]:
        print(f"  - {f}: {label}", file=sys.stderr)
    if len(seen) > 25:
        print(f"  ... and {len(seen) - 25} more", file=sys.stderr)
    print("Scrub these (genericize names, use ~ / env vars instead of paths and IPs), "
          "then retry. If it is a verified false positive, the user can push it "
          "themselves or set GHENGIS_LEAK_GUARD=off.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
