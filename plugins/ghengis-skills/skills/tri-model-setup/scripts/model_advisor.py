#!/usr/bin/env python3
"""Model advisor — evidence-based routing from the harness's own history.

Answers "which model should do this?" with measurements instead of vibes, by
reading the same logs the ops console shows:

  ~/.claude/tri-model/agy-usage.jsonl        gemini calls: latency, failures, sizes
  ~/.codex/sessions/**                       codex: tokens, completion, plan burn
  ~/.claude/projects/*/*.jsonl               claude: per-turn usage by model
  ~/.claude/tri-model/gauntlet-runs/*/       critic yield: defects found per round
  ~/.claude/tri-model/adw-runs/*/            phase outcomes by model

Usage:
  python model_advisor.py                 # scorecard for the last 14 days
  python model_advisor.py --days 3
  python model_advisor.py --json          # machine-readable, for skills to read

Nothing here is fabricated: every column is either measured or reported as
unavailable. Where a signal is thin, the row says so. Corrections applied after
an Opus correctness review (2026-08-10) are marked REVIEW-FIX.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HOME = Path.home()
TRI = HOME / ".claude" / "tri-model"
AGY_LOG = TRI / "agy-usage.jsonl"
CODEX = HOME / ".codex" / "sessions"
PROJECTS = HOME / ".claude" / "projects"
TS = re.compile(r'"timestamp":"([^"]+)"')

# Per-leg thresholds: 5 claude TURNS is nothing, 5 codex SESSIONS is a signal.
THIN = {"claude": 40, "gemini": 5, "codex": 3}
# REVIEW-FIX #13/alias: the wrapper used to log the shorthand before resolving.
ALIASES = {"flash": "gemini-3.6-flash-medium (pre-resolution alias)",
           "pro": "gemini-3.1-pro-high (pre-resolution alias)"}


def _ts(text: str) -> float | None:
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
    except (ValueError, AttributeError):
        return None


def gemini_stats(t0: float) -> dict:
    """Per-call latency and outcome. REVIEW-FIX #11: a missing exit code is
    'unknown', never counted as a failure — fail-rate is the metric that would
    demote a model, so a logging gap must not be able to move it."""
    out: dict = defaultdict(lambda: {"calls": 0, "fails": 0, "unknown": 0, "secs": 0.0,
                                     "timed": 0, "in_chars": 0, "out_chars": 0})
    if not AGY_LOG.exists():
        return out
    for line in AGY_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = _ts(j.get("ts", ""))
        if ts is None or ts < t0:
            continue
        model = j.get("model", "?")
        s = out[ALIASES.get(model, model)]
        s["calls"] += 1
        code = j.get("exit")
        if code is None:
            s["unknown"] += 1
        elif code != 0:
            s["fails"] += 1
        if j.get("seconds") is not None:   # REVIEW-FIX #12: 0s is a measurement
            s["secs"] += j["seconds"]
            s["timed"] += 1
        s["in_chars"] += j.get("prompt_chars") or 0
        s["out_chars"] += j.get("output_chars") or 0
    return out


def codex_stats(t0: float) -> dict:
    """REVIEW-FIX #5/#8: events are filtered by their own timestamps (not just
    file mtime), in-window token usage is summed from per-turn deltas rather
    than the session's cumulative total, and quota is the LATEST reading by
    event time, not whatever the directory walk happened to hit last."""
    out: dict = defaultdict(lambda: {"sessions": 0, "completed": 0, "errored": 0,
                                     "tokens": 0, "secs": 0.0, "timed": 0, "partial": 0})
    quota = None
    quota_at = -1.0
    if not CODEX.exists():
        return {"models": out, "quota": quota}
    for f in CODEX.rglob("*.jsonl"):
        if f.stat().st_mtime < t0:
            continue
        model, complete, errored = "codex", False, False
        first = last = None
        in_window_tokens, saw_out_of_window = 0, False
        try:
            for line in f.open(encoding="utf-8", errors="replace"):
                m = TS.search(line)
                ets = _ts(m.group(1)) if m else None
                if ets is not None and ets < t0:
                    saw_out_of_window = True
                    continue          # event predates the window: ignore it
                if ets is not None:
                    first = ets if first is None else first
                    last = ets
                if '"task_complete"' in line:
                    complete = True
                if '"type":"error"' in line:
                    errored = True
                if '"model"' in line and model == "codex":
                    mm = re.search(r'"model":"([^"]+)"', line)
                    if mm:
                        model = mm.group(1)
                if '"token_count"' in line:
                    try:
                        payload = (json.loads(line).get("payload") or {})
                        info = payload.get("info") or {}          # guard: null info
                        last_use = info.get("last_token_usage") or {}
                        in_window_tokens += last_use.get("total_tokens", 0)
                        prim = ((payload.get("rate_limits") or {}).get("primary") or {})
                        if prim.get("used_percent") is not None and (ets or 0) > quota_at:
                            quota_at = ets or 0
                            quota = {"pct": prim["used_percent"],
                                     "resets_at": prim.get("resets_at"), "read_at": ets}
                    except (json.JSONDecodeError, KeyError, AttributeError, TypeError):
                        pass
        except OSError:
            continue
        if first is None:
            continue                  # nothing from this session is in-window
        s = out[model]
        s["sessions"] += 1
        s["completed"] += 1 if complete else 0
        s["errored"] += 1 if errored else 0
        s["tokens"] += in_window_tokens
        s["partial"] += 1 if saw_out_of_window else 0
        if last > first:
            s["secs"] += last - first
            s["timed"] += 1
    return {"models": out, "quota": quota}


def claude_stats(t0: float) -> dict:
    """REVIEW-FIX #7: cache tokens are the bulk of Claude's real throughput —
    excluding them understated Fable by ~325x and inverted the comparison
    against codex. Fresh, cached and written tokens are all reported."""
    out: dict = defaultdict(lambda: {"turns": 0, "tin": 0, "tout": 0,
                                     "cache_read": 0, "cache_write": 0})
    if not PROJECTS.exists():
        return out
    seen: set = set()
    for d in PROJECTS.iterdir():
        if not d.is_dir():
            continue
        for f in d.glob("*.jsonl"):
            if f.stat().st_mtime < t0:
                continue
            try:
                fh = f.open(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line in fh:
                if '"usage"' not in line or '"output_tokens"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = rec.get("message", {}) or {}
                u = msg.get("usage") or {}
                if not u.get("output_tokens"):
                    continue
                tid = rec.get("requestId") or msg.get("id") or rec.get("uuid")
                if not tid or tid in seen:
                    continue
                ts = _ts(rec.get("timestamp") or "")   # REVIEW-FIX #10
                if ts is None or ts < t0:
                    continue
                seen.add(tid)
                s = out[msg.get("model", "claude")]
                s["turns"] += 1
                s["tin"] += u.get("input_tokens", 0)
                s["tout"] += u.get("output_tokens", 0)
                s["cache_read"] += u.get("cache_read_input_tokens", 0)
                s["cache_write"] += u.get("cache_creation_input_tokens", 0)
            fh.close()
    return out


def adw_stats(t0: float) -> dict:
    """REVIEW-FIX #9: adw-runs was advertised and never read. Phase outcomes
    per model are exactly the 'did this model do the job' signal."""
    out: dict = defaultdict(lambda: {"phases": 0, "secs": 0.0, "gate_fail": 0})
    root = TRI / "adw-runs"
    if not root.exists():
        return out
    for run in root.iterdir():
        m = run / "metrics.jsonl"
        if not m.exists() or m.stat().st_mtime < t0:
            continue
        for line in m.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            model = r.get("model") or r.get("agent_model")
            if not model:
                continue
            s = out[model]
            s["phases"] += 1
            s["secs"] += r.get("seconds") or 0
            if str(r.get("gate", "")).lower() in ("fail", "failed", "retried"):
                s["gate_fail"] += 1
    return out


def critic_yield(t0: float) -> dict:
    """REVIEW-FIX #1/#2/#3/#15. Reads both `defects` and `n_defects`; a round
    with neither is 'unscored' rather than silently zero. Only an exact WOWED
    with no defects counts as a pass. Unattributed rounds get their own bucket
    instead of a default name, and a panel is credited to each member. The
    'overturned' signal only counts inside the SAME bar version — a WOWED
    followed by defects under a rewritten bar is a new standard, not a miss.
    Rows carry no timestamps, so this section is explicitly not windowed."""
    out: dict = defaultdict(lambda: {"rounds": 0, "unscored": 0, "defects": 0,
                                     "wowed": 0, "overturned": 0})
    root = TRI / "gauntlet-runs"
    if not root.exists():
        return out
    for run in root.iterdir():
        m = run / "metrics.jsonl"
        if not m.exists():
            continue
        rows = []
        for line in m.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        # A note mentioning a new bar starts a new standard for overturn checks.
        bar_of, bar = [], 0
        for r in rows:
            if re.search(r"bar v\d|substance-first", str(r.get("note", "")), re.I):
                bar += 1
            bar_of.append(bar)
        for i, r in enumerate(rows):
            raw = r.get("critic") or r.get("critics")
            names = [n.strip() for n in re.split(r"\+", str(raw))] if raw else ["(critic unrecorded)"]
            d = r.get("defects", r.get("n_defects"))
            v = str(r.get("verdict", "")).strip().upper()
            passed = v == "WOWED" and not (d or 0)
            later = [x for j, x in enumerate(rows[i + 1:], start=i + 1)
                     if bar_of[j] == bar_of[i] and (x.get("defects", x.get("n_defects")) or 0) > 0]
            for name in names:
                s = out[name]
                s["rounds"] += 1
                if d is None:
                    s["unscored"] += 1
                else:
                    s["defects"] += d
                if passed:
                    s["wowed"] += 1
                    if later:
                        s["overturned"] += 1
    return out


def build(days: float) -> dict:
    t0 = time.time() - days * 86400
    g, c, cl, adw, cy = (gemini_stats(t0), codex_stats(t0), claude_stats(t0),
                         adw_stats(t0), critic_yield(t0))
    rows = []
    for model, s in cl.items():
        total = s["tin"] + s["tout"] + s["cache_read"] + s["cache_write"]
        rows.append({"leg": "claude", "model": model, "uses": s["turns"], "unit": "turns",
                     "latency": None, "span": None, "fail_rate": None, "unknown": 0,
                     "tokens": total, "cache_read": s["cache_read"],
                     "note": f"{s['tout']:,} out · {s['cache_read']:,} cache-read "
                             f"· outcome not logged"})
    for model, s in g.items():
        scored = s["calls"] - s["unknown"]
        rows.append({"leg": "gemini", "model": model, "uses": s["calls"], "unit": "calls",
                     "latency": round(s["secs"] / s["timed"], 1) if s["timed"] else None,
                     "span": None,
                     "fail_rate": round(s["fails"] / scored, 3) if scored else None,
                     "unknown": s["unknown"], "tokens": None, "cache_read": None,
                     "note": f"{s['in_chars']:,} in / {s['out_chars']:,} out chars"
                             + (f" · {s['unknown']} unknown exit" if s["unknown"] else "")})
    for model, s in c["models"].items():
        rows.append({"leg": "codex", "model": model, "uses": s["sessions"], "unit": "sessions",
                     "latency": None,
                     "span": round(s["secs"] / s["timed"], 1) if s["timed"] else None,
                     "fail_rate": round(s["errored"] / s["sessions"], 3) if s["sessions"] else None,
                     "unknown": 0, "tokens": s["tokens"], "cache_read": None,
                     "note": f"{s['completed']}/{s['sessions']} logged completion"
                             + (f" · {s['partial']} span the window edge" if s["partial"] else "")})
    for r in rows:
        r["thin_evidence"] = r["uses"] < THIN.get(r["leg"], 5)
    # REVIEW-FIX #13: sort within leg — units are not comparable across legs.
    rows.sort(key=lambda r: (r["leg"], -r["uses"]))
    return {"generated": time.time(), "days": days, "models": rows,
            "adw": {k: v for k, v in adw.items()},
            "critics": {k: v for k, v in cy.items()}, "quota": c["quota"]}


def render(d: dict) -> str:
    L = [f"MODEL ADVISOR — last {d['days']:g} day(s)", ""]
    L.append(f"{'leg':<8}{'model':<34}{'uses':>7} {'unit':<9}{'latency':>9}{'span':>8}{'fail':>7}{'tokens':>14}")
    L.append("-" * 104)
    for r in d["models"]:
        lat = f"{r['latency']}s" if r["latency"] is not None else "—"
        span = f"{r['span']}s" if r["span"] is not None else "—"
        fr = f"{r['fail_rate']*100:.0f}%" if r["fail_rate"] is not None else "n/a"
        tok = f"{r['tokens']:,}" if r["tokens"] is not None else "n/a"
        L.append(f"{r['leg']:<8}{r['model']:<34}{r['uses']:>7} {r['unit']:<9}{lat:>9}{span:>8}{fr:>7}{tok:>14}")
        L.append(f"{'':<8}{r['note']}" + ("   [thin evidence]" if r["thin_evidence"] else ""))
    L.append("")
    L.append("latency = per-call wall time (gemini). span = whole-session first→last event")
    L.append("(codex); it includes idle time and is NOT comparable to latency. claude turns")
    L.append("carry no timing or outcome in transcripts. tokens include cache for both legs.")
    if d["adw"]:
        L += ["", "ADW PHASES (workflow work actually completed, by model)", "-" * 104]
        for model, s in sorted(d["adw"].items(), key=lambda kv: -kv[1]["phases"]):
            avg = f"{s['secs']/s['phases']:.0f}s" if s["phases"] else "—"
            L.append(f"  {model:<40} {s['phases']:>3} phases  avg {avg:>7}  {s['gate_fail']} gate failures")
    if d["critics"]:
        L += ["", "CRITIC YIELD — all gauntlet rounds on file (NOT windowed: rounds carry no timestamps)",
              "-" * 104]
        ranked = sorted(d["critics"].items(),
                        key=lambda kv: -(kv[1]["defects"] / kv[1]["rounds"] if kv[1]["rounds"] else 0))
        for name, s in ranked:
            per = s["defects"] / s["rounds"] if s["rounds"] else 0
            extra = f", {s['unscored']} unscored" if s["unscored"] else ""
            L.append(f"  {name:<44} {s['rounds']:>3} rounds  {s['defects']:>3} defects "
                     f"({per:.1f}/round{extra})  {s['wowed']} passed, {s['overturned']} overturned same-bar")
    if d["quota"]:
        q = d["quota"]
        when = datetime.fromtimestamp(q["resets_at"]).strftime("%b %d %H:%M") if q.get("resets_at") else "n/a"
        read = datetime.fromtimestamp(q["read_at"]).strftime("%b %d %H:%M") if q.get("read_at") else "?"
        L += ["", f"CODEX PLAN BURN: {q['pct']}% (resets {when}; latest reading {read})"]
    else:
        L += ["", "CODEX PLAN BURN: unavailable — no rollout in this window reported rate limits"]
    L += ["", "Routing doctrine: quality first. Frontier models think and review;",
          "fast models execute already-specified work and are always verified.",
          "Rows marked [thin evidence] have too few observations to route on."]
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=float, default=14)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    data = build(a.days)
    sys.stdout.write(json.dumps(data, indent=2) if a.json else render(data))
    sys.stdout.write("\n")
