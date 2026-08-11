#!/usr/bin/env python3
"""Tri-model harness — live ops console.

Single stdlib file. http://127.0.0.1:8321 — what every model leg is doing,
through time, per project folder, WITH the numbers that let you act on it:
real token accounting, list-price-equivalent cost, codex quota burn, cache
efficiency, and a click-through inspector on every event.

Sources (the harness's own logs — nothing synthetic):
  ~/.claude/tri-model/agy-usage.jsonl   Gemini leg: call, duration, i/o chars, output head
  ~/.claude/projects/*/*.jsonl          Claude turns: per-turn token usage + model
  ~/.codex/sessions/**                  GPT leg: total token usage + rate-limit burn
  ~/.claude/tri-model/{gauntlet,adw}-runs  run metrics

Launch:  python %USERPROFILE%\\.claude\\tri-model\\dashboard.py
"""
import json
import re
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOME = Path.home()
TRI = HOME / ".claude" / "tri-model"
AGY_LOG = TRI / "agy-usage.jsonl"
CODEX_SESSIONS = HOME / ".codex" / "sessions"
PROJECTS = HOME / ".claude" / "projects"
PORT = 8321

# List price per 1M tokens (in, out). The subscriptions make marginal cost $0 —
# these exist to answer "what would this have cost on the API", and every
# surface that shows them says so. Cache reads bill at 0.1x in, writes 1.25x.
PRICES = {
    "claude-opus": (15.0, 75.0), "claude-fable": (15.0, 75.0),
    "claude-sonnet": (3.0, 15.0), "claude-haiku": (0.80, 4.0),
    "gpt-5": (1.25, 10.0), "codex": (1.25, 10.0),
    "gemini-3.1-pro": (1.25, 10.0), "gemini-3.6-flash": (0.30, 2.50),
    "gemini-3.5-flash": (0.30, 2.50),
}
CHARS_PER_TOKEN = 4  # only used for the Gemini leg, always labelled "est."

_cache: dict = {}
_TS = re.compile(r'"timestamp":"([^"]+)"')
TRUNCATED = [False]  # transcripts stream in full; kept for the coverage flag
SPAN_GAP = 30   # A Claude "work span" is bracketed by REAL logged events at
                # both ends; only events closer together than this are treated
                # as one continuous run, so a bar never spans idle time. A
                # single logged event has no measurable duration and renders
                # as a point mark, not a widened bar.


def price_for(model: str) -> tuple[float, float] | None:
    """None = no published price for this model. Never fall back to zero:
    a $0 that means 'unknown' is a fabricated number."""
    m = (model or "").lower()
    for key, p in PRICES.items():
        if m.startswith(key) or key in m:
            return p
    return None


def cost_of(model: str, tin: int, tout: int, cache_read: int = 0, cache_write: int = 0) -> float | None:
    p = price_for(model)
    if p is None:
        return None
    pin, pout = p
    return (tin * pin + tout * pout + cache_read * pin * 0.1
            + cache_write * pin * 1.25) / 1_000_000


def _slug(cwd: str) -> str:
    return re.sub(r"[:\\/ ]", "-", cwd or "")


def _pretty(project: str) -> str:
    name = re.sub(r"^[A-Z]--", "", project)
    name = re.sub(r"^Users-[^-]+-(?:OneDrive-)?(?:Desktop-)?", "", name)
    if re.match(r"^Users-[^-]+$", name):
        return "home"
    if "AppData" in name:
        return "temp-" + name.split("-")[-1]
    return name or project


def _project_for(cwd: str, names: list[str]) -> str | None:
    s, best = _slug(cwd), None
    for p in names:
        if s == p or s.startswith(p):
            if best is None or len(p) > len(best):
                best = p
    return best


def read_agy() -> list[dict]:
    """Gemini leg. No token counts are exposed by the CLI, so tokens here are
    a labelled char/4 estimate and are kept separate from measured totals."""
    if not AGY_LOG.exists():
        return []
    rows = []
    # No tail cap: the time window is the only filter, so a busy day can never
    # silently drop calls (and with them tokens, cost and failures).
    for line in AGY_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            j = json.loads(line)
            ts = datetime.fromisoformat(j["ts"]).timestamp()
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
        # Absent size fields mean "not recorded" — not zero.
        pc, oc = j.get("prompt_chars"), j.get("output_chars")
        known = pc is not None and oc is not None
        tin = (pc // CHARS_PER_TOKEN) if pc is not None else None
        tout = (oc // CHARS_PER_TOKEN) if oc is not None else None
        model = j.get("model", "?")
        rows.append({
            "leg": "gemini", "ts": ts, "secs": j.get("seconds"), "model": model,
            "cwd": j.get("cwd") or "", "ok": j.get("exit") == 0, "state": "ok" if j.get("exit") == 0 else "failed",
            "tin": tin, "tout": tout, "est_tokens": True,
            "cost": cost_of(model, tin or 0, tout or 0) if known else None,
            "detail": (f"{pc:,} in / {oc:,} out chars" if known else "sizes not recorded")
                      + (" · via file" if j.get("via_file") else ""),
            "head": (j.get("output_head") or "")[:400],
            "prompt_chars": pc, "output_chars": oc, "via_file": bool(j.get("via_file")),
        })
    return rows


def read_codex() -> list[dict]:
    """GPT leg. Rollouts carry measured token totals and plan rate-limit burn."""
    if not CODEX_SESSIONS.exists():
        return []
    rows = []
    for f in CODEX_SESSIONS.rglob("*.jsonl"):
        st = f.stat()
        key = ("codex", str(f), st.st_mtime)
        if key in _cache:
            rows.append(dict(_cache[key]))
            continue
        cwd, model, usage, limits, started, preview = "", "codex", {}, {}, st.st_mtime, ""
        last_evt, complete, errored = 0.0, False, False
        try:
            for line in f.open(encoding="utf-8", errors="replace"):
                if '"task_complete"' in line:
                    complete = True
                if '"error"' in line and '"type":"error"' in line:
                    errored = True
                if '"cwd"' in line and not cwd:
                    m = re.search(r'"cwd":"((?:[^"\\]|\\.)*)"', line)
                    if m:
                        cwd = m.group(1).replace("\\\\", "\\")
                if '"token_count"' in line:
                    try:
                        p = json.loads(line).get("payload", {})
                        usage = p.get("info", {}).get("total_token_usage", usage) or usage
                        limits = p.get("rate_limits", limits) or limits
                    except json.JSONDecodeError:
                        pass
                if '"model"' in line and model == "codex":
                    m = re.search(r'"model":"([^"]+)"', line)
                    if m:
                        model = m.group(1)
                if '"agent_message"' in line:
                    try:
                        msg = json.loads(line).get("payload", {}).get("message", "")
                        if isinstance(msg, str) and msg.strip():
                            preview = msg.strip()[:400]
                    except json.JSONDecodeError:
                        pass
                if '"timestamp"' in line:
                    m = _TS.search(line)
                    if m:
                        try:
                            et = datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).timestamp()
                        except ValueError:
                            continue
                        if started == st.st_mtime:
                            started = et
                        last_evt = max(last_evt, et)
        except OSError:
            continue
        tin = usage.get("input_tokens", 0)
        cached = usage.get("cached_input_tokens", 0)
        tout = usage.get("output_tokens", 0)
        prim = (limits or {}).get("primary") or {}
        # Times come from LOGGED events. If the rollout logged none, say so —
        # never present a filesystem mtime as an operational timestamp.
        logged = bool(last_evt)
        end = last_evt or st.st_mtime
        state = "errored" if errored else ("completed" if complete else "running")
        row = {
            "leg": "codex", "ts": end, "start": started if logged else None,
            "secs": max(0, end - started) if logged else None,
            "logged_times": logged,
            "time_source": "logged events" if logged else "no events logged — file mtime used only to place it on the timeline",
            "model": model, "cwd": cwd,
            # "ok" is reserved for a rollout that actually logged completion;
            # a running one is neither a success nor a failure.
            "ok": state == "completed", "state": state,
            "status": {"errored": "errored", "completed": "completed",
                       "running": "in progress · no completion logged"}[state],
            "tin": tin - cached, "tout": tout, "cache_read": cached, "est_tokens": False,
            "cost": cost_of(model, tin - cached, tout, cache_read=cached),
            "reasoning": usage.get("reasoning_output_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "quota_pct": prim.get("used_percent"), "quota_reset": prim.get("resets_at"),
            "plan": ((limits or {}).get("credits") or {}).get("balance"),
            "detail": (f"{usage.get('total_tokens', 0):,} tokens" if usage else f"{st.st_size // 1024}KB rollout"),
            "head": preview, "session": f.name[8:24],
        }
        _cache[key] = dict(row)
        rows.append(row)
    return rows


def read_claude(t0: float) -> tuple[dict, list[dict]]:
    """Claude work. Per-turn usage lives in the transcripts: measured tokens,
    model, and timestamps. Returns {project: [spans]} plus turn events."""
    if not PROJECTS.exists():
        return {}, []
    spans_by_proj, turns = {}, []
    seen_turns: set = set()  # dedupe by request/message id — see below
    for d in PROJECTS.iterdir():
        if not d.is_dir():
            continue
        # EVERY transcript touched in the window, not just the newest: a
        # project can have several concurrent sessions and dropping them
        # silently under-reports the fleet.
        files = [f for f in d.glob("*.jsonl") if f.stat().st_mtime >= t0]
        for newest in files:
            mt = newest.stat().st_mtime
            key = ("claude", str(newest), mt, int(t0 // 60))
            spans, tl = _parse_transcript(newest, key, t0)
            name = _pretty(d.name)
            keep = [sp for sp in spans if sp[1] >= t0]
            if keep:
                spans_by_proj.setdefault(name, []).extend(keep)
            for t in tl:
                if t["ts"] < t0 or t["id"] in seen_turns:
                    continue
                seen_turns.add(t["id"])
                    # Transcripts record usage, not outcome — no success signal
                # exists to report, so none is claimed.
                turns.append({**t, "project": name, "leg": "claude",
                              "state": "recorded",
                              "cost": cost_of(t["model"], t["tin"], t["tout"],
                                              t["cache_read"], t["cache_write"])})
    for name, sp in spans_by_proj.items():
        sp.sort()
        merged: list = []
        for a, b in sp:
            if merged and a - merged[-1][1] <= SPAN_GAP:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        spans_by_proj[name] = merged
    return spans_by_proj, turns


def _parse_transcript(newest: Path, key: tuple, t0: float) -> tuple[list, list]:
    """Spans + per-turn usage from one transcript. Turns carry a stable id so
    the caller can drop duplicates (the same assistant turn is written more
    than once across resume/sidechain lines — counting it twice inflates
    every token and cost number downstream)."""
    if key in _cache:
        return _cache[key]
    # Streamed line by line: no byte cap, so no transcript is ever partially
    # read and no in-window turn can go missing.
    try:
        fh = newest.open(encoding="utf-8", errors="replace")
    except OSError:
        return [], []
    tl, stamps, local_seen = [], [], set()
    for line in fh:
        m = _TS.search(line)
        if not m:
            continue
        try:
            ts = datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).timestamp()
        except ValueError:
            continue
        stamps.append(ts)
        if '"usage"' in line and '"output_tokens"' in line:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = rec.get("message", {}) or {}
            u = msg.get("usage") or {}
            if not u.get("output_tokens"):
                continue
            tid = rec.get("requestId") or msg.get("id") or rec.get("uuid")
            if not tid or tid in local_seen:
                continue
            local_seen.add(tid)
            # The assistant's own words for this turn — so a span is never
            # an opaque bar in the inspector.
            say = ""
            content = msg.get("content")
            if isinstance(content, list):
                for blk in content:
                    if isinstance(blk, dict) and blk.get("type") == "text" and blk.get("text", "").strip():
                        say = blk["text"].strip()[:2000]
                        break
            tl.append({
                "id": tid, "ts": ts, "model": msg.get("model", "claude"),
                "tin": u.get("input_tokens", 0), "tout": u.get("output_tokens", 0),
                "cache_read": u.get("cache_read_input_tokens", 0),
                "cache_write": u.get("cache_creation_input_tokens", 0),
                "say": say,
            })
    fh.close()
    spans = []
    for s in sorted(set(stamps)):
        if spans and s - spans[-1][1] <= SPAN_GAP:
            spans[-1][1] = s
        else:
            spans.append([s, s])
    _cache[key] = (spans, tl)
    if len(_cache) > 400:
        _cache.pop(next(iter(_cache)))
    return spans, tl


def read_runs() -> list[dict]:
    out = []
    for kind in ("gauntlet-runs", "adw-runs"):
        root = TRI / kind
        if not root.exists():
            continue
        for run in root.iterdir():
            m = run / "metrics.jsonl"
            if not m.exists():
                continue
            lines = [x for x in m.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
            try:
                last = json.loads(lines[-1]) if lines else {}
            except json.JSONDecodeError:
                last = {}
            out.append({"kind": kind.split("-")[0], "name": run.name, "ts": m.stat().st_mtime,
                        "events": len(lines),
                        "last": str(last.get("verdict") or last.get("gate") or last.get("phase") or "")})
    return sorted(out, key=lambda r: -r["ts"])[:12]


def build_data(window: int) -> dict:
    now = time.time()
    t0 = now - window
    names = [d.name for d in PROJECTS.iterdir() if d.is_dir()] if PROJECTS.exists() else []

    agy, codex = read_agy(), read_codex()
    for r in agy + codex:
        p = _project_for(r["cwd"], names)
        r["project"] = _pretty(p) if p else (r["cwd"].split("\\")[-1] or "global")
    claude_spans, claude_turns = read_claude(t0)

    # IDs must be STABLE across polls — an index-based id re-points a live
    # selection at a different event as the window slides.
    events = []
    for r in sorted([x for x in agy + codex if x["ts"] >= t0], key=lambda x: x["ts"]):
        events.append({**r, "id": f"{r['leg']}-{int(r['ts'] * 1000)}"})

    lanes = {}
    for name, spans in claude_spans.items():
        lanes.setdefault(name, {"claude": [], "events": []})["claude"] = spans
    for e in events:
        lanes.setdefault(e["project"], {"claude": [], "events": []})["events"].append(e)

    lane_list = []
    for name, v in lanes.items():
        turns = [t for t in claude_turns if t["project"] == name]
        last = max([s[1] for s in v["claude"]] + [e["ts"] for e in v["events"]] + [0])
        lane_list.append({
            "name": name, "claude": v["claude"], "events": v["events"], "last": last,
            "claude_tokens": sum(t["tin"] + t["tout"] for t in turns),
            "claude_cache": sum(t["cache_read"] for t in turns),
            "claude_fresh": sum(t["tin"] + t["cache_write"] for t in turns),
            "claude_cost": sum(t["cost"] or 0 for t in turns),
            "leg_cost": sum(e["cost"] or 0 for e in v["events"]),
            "cost_partial": any(t["cost"] is None for t in turns) or any(e["cost"] is None for e in v["events"]),
            "turns": len(turns),
        })
    lane_list.sort(key=lambda x: -x["last"])

    def _blank(leg, est=False):
        return {"leg": leg, "n": 0, "tin": 0, "tout": 0, "cache": 0, "cost": 0.0,
                "priced": True, "secs": 0.0, "timed": 0, "fail": 0, "running": 0, "est": est}

    by_model: dict = {}
    for t in claude_turns:
        s = by_model.setdefault(t["model"], _blank("claude"))
        s["n"] += 1
        s["tin"] += t["tin"]
        s["tout"] += t["tout"]
        s["cache"] += t["cache_read"]
        if t["cost"] is None:
            s["priced"] = False
        else:
            s["cost"] += t["cost"]
    for e in events:
        s = by_model.setdefault(e["model"], _blank(e["leg"], e.get("est_tokens", False)))
        s["n"] += 1
        s["tin"] += e.get("tin") or 0
        s["tout"] += e.get("tout") or 0
        s["cache"] += e.get("cache_read") or 0
        if e["cost"] is None:
            s["priced"] = False
        else:
            s["cost"] += e["cost"]
        # Average latency divides by CALLS THAT WERE TIMED, not all calls.
        if e.get("secs"):
            s["secs"] += e["secs"]
            s["timed"] += 1
        if e.get("state") == "failed" or e.get("state") == "errored":
            s["fail"] += 1
        elif e.get("state") == "running":
            s["running"] += 1
    models = [{"model": k, **v} for k, v in sorted(by_model.items(), key=lambda kv: -kv[1]["cost"])]

    # Quota comes from the newest rollout that reported it — which may predate
    # the window, so name its session and when it was read.
    cq = sorted([c for c in codex if c.get("quota_pct") is not None], key=lambda c: -c["ts"])
    quota = ({"pct": cq[0]["quota_pct"], "resets_at": cq[0]["quota_reset"],
              "from": cq[0]["session"], "read_at": cq[0]["ts"],
              "in_window": cq[0]["ts"] >= t0} if cq else None)

    fresh = sum(l["claude_fresh"] for l in lane_list)
    cached = sum(l["claude_cache"] for l in lane_list)
    return {
        # Every active folder ships — a capped lane list would hide whole
        # projects from both the timeline and the folder filter.
        "now": now, "window": window, "lanes": lane_list, "events": events,
        "turns": claude_turns, "models": models, "runs": read_runs(), "quota": quota,
        "totals": {
            "claude_tokens": sum(l["claude_tokens"] for l in lane_list),
            "cache_pct": round(cached / (cached + fresh) * 100, 1) if (cached + fresh) else 0.0,
            "cost": sum(m["cost"] for m in models),
            "cost_partial": any(not m["priced"] for m in models),
            "sessions_live": sum(1 for l in lane_list if now - l["last"] < 900),
            "fails": sum(1 for e in events if e.get("state") in ("failed", "errored")),
            "truncated": TRUNCATED[0],
        },
    }


PAGE = r"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>tri-model ops</title><style>
:root{--page:#0a0d12;--card:#12161d;--card2:#161b24;--line:#1f2733;--line2:#2a3442;
--text:#c7d0dc;--dim:#5c6878;--bright:#e8edf4;
--claude:#d97757;--gemini:#9ece6a;--codex:#7aa2f7;
--good:#56d364;--warn:#e3b341;--bad:#f85149;
--mono:"Cascadia Code",Consolas,ui-monospace,monospace;--sans:"Segoe UI",system-ui,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--text);font:14px/1.5 var(--sans);padding:1.2rem 1.1rem 3rem}
.wrap{max-width:1240px;margin:0 auto}
header{display:flex;align-items:baseline;gap:.9rem;flex-wrap:wrap;margin-bottom:.9rem}
h1{font:600 1rem var(--sans);color:var(--bright);margin:0;letter-spacing:.09em}
.live{display:inline-flex;align-items:center;gap:.4rem;font:.66rem var(--sans);letter-spacing:.06em;color:var(--bright)}
.live .p{width:.5rem;height:.5rem;border-radius:99px;background:var(--bright);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
.legend{font:.68rem var(--sans);color:var(--dim);margin-left:auto}
.dot{display:inline-block;width:.55rem;height:.55rem;border-radius:99px;margin:0 .3rem 0 .8rem;vertical-align:baseline}
.controls{display:flex;gap:.55rem;align-items:center;margin-bottom:1rem;flex-wrap:wrap}
select{background:var(--card);color:var(--text);border:1px solid var(--line2);border-radius:6px;
padding:.32rem .6rem;font:.78rem var(--sans);cursor:pointer}
select:hover{border-color:var(--dim);background:var(--card2)}
select:focus-visible{outline:2px solid var(--bright);outline-offset:1px}
.scope{font:.7rem var(--sans);color:var(--dim)}
.upd{font:.66rem var(--mono);font-variant-numeric:tabular-nums;color:var(--dim);margin-left:auto}
.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:.55rem;margin-bottom:1.3rem}
.sc{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--line2);border-radius:8px;padding:.5rem .75rem}
.sc .k{font:.62rem var(--sans);text-transform:uppercase;letter-spacing:.07em;color:var(--dim)}
.sc .v{font:600 1.32rem var(--mono);font-variant-numeric:tabular-nums;color:var(--bright)}
.sc .s{font:.62rem var(--mono);font-variant-numeric:tabular-nums;color:var(--dim)}
.sc.cla{border-left-color:var(--claude)}.sc.gem{border-left-color:var(--gemini)}
.sc.cdx{border-left-color:var(--codex)}.sc.bad{border-left-color:var(--bad)}.sc.bad .v{color:var(--bad)}
.sc.warn{border-left-color:var(--warn)}.sc.warn .v{color:var(--warn)}
h2{font:600 .68rem var(--sans);text-transform:uppercase;letter-spacing:.09em;color:var(--dim);
margin:1.5rem 0 .5rem;border-bottom:1px solid var(--line);padding-bottom:.28rem;display:flex;gap:.6rem;align-items:baseline}
h2 .note{font:.62rem var(--sans);letter-spacing:0;text-transform:none;color:var(--dim);opacity:.85}
.split{display:grid;grid-template-columns:1fr 340px;gap:.8rem;align-items:start}
@media (max-width:960px){.split{grid-template-columns:1fr}}
.tl{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.65rem .85rem .9rem;overflow-x:auto}
.tlin{min-width:700px}
.axisrow{display:flex;align-items:flex-start}
.axismask{width:186px;min-width:186px;height:1.1rem;position:sticky;left:0;z-index:7;background:var(--card)}
.axis{position:relative;flex:1;height:1.1rem;font:.62rem var(--mono);font-variant-numeric:tabular-nums;color:var(--dim)}
.axis .tick{position:absolute;top:0;transform:translateX(-50%)}
.axis .tick.first{transform:translateX(0)}
.axis .tick.last{transform:translateX(-100%)}
.lane{display:flex;align-items:center;min-height:2.2rem;border-top:1px solid var(--line)}
.lane:first-of-type{border-top:0}
.lname{width:186px;min-width:186px;padding-right:.7rem;position:sticky;left:0;z-index:6;background:var(--card);
overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lname b{font:500 .74rem var(--sans);color:var(--bright)}
.lname .a{display:block;font:.6rem var(--mono);font-variant-numeric:tabular-nums;color:var(--dim)}
.track{position:relative;flex:1;height:1.6rem;overflow:hidden}
#lanes{position:relative}
#lanes .nowline{position:absolute;right:0;top:0;bottom:0;width:1px;background:var(--line2)}
.seg,.ev{position:absolute;padding:0;border:0;cursor:pointer;background:var(--claude)}
.seg{top:.46rem;height:.62rem;border-radius:3px;opacity:.42}
.seg:hover{opacity:.72}.seg.mark{width:3px;border-radius:1px;opacity:.8}
.ev{top:.22rem;height:1.16rem;border-radius:3px;background:var(--gemini);opacity:.95}
/* A MARK is a point indicator, never a duration claim: 3px hairline, visually
   distinct from a scaled bar, with the true duration in the tooltip. Any leg
   with a measured duration gets a scaled bar instead. */
.ev.mark{width:3px;top:.28rem;height:1.04rem;border-radius:1px}
.ev.legcodex{background:var(--codex)}
.ev:hover,.seg:hover{filter:brightness(1.3)}
.ev.fail{outline:1.5px solid var(--bad)}
.ev.running{outline:1.5px dashed var(--warn)}
.sel{outline:2px solid var(--bright)!important;outline-offset:1px;z-index:4}
.seg:focus-visible,.ev:focus-visible{outline:2px solid var(--bright);outline-offset:1px}
.insp{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.75rem .9rem;
position:sticky;top:.8rem;max-height:82vh;overflow:auto}
.insp h3{font:600 .78rem var(--mono);color:var(--bright);margin:0 0 .1rem}
.insp .who{font:.66rem var(--sans);color:var(--dim);margin-bottom:.6rem}
.kv{display:grid;grid-template-columns:auto 1fr;gap:.18rem .7rem;font:.72rem var(--mono);font-variant-numeric:tabular-nums}
.kv dt{color:var(--dim);font-family:var(--sans);font-size:.68rem}
.kv dd{margin:0;color:var(--text);text-align:right}
.insp .out{margin-top:.7rem;border-top:1px solid var(--line);padding-top:.5rem;
font:.7rem/1.45 var(--mono);color:var(--dim);white-space:pre-wrap;word-break:break-word;max-height:15rem;overflow:auto}
.insp .hint{color:var(--dim);font:.72rem var(--sans)}
table{border-collapse:collapse;width:100%;font:.75rem var(--mono);font-variant-numeric:tabular-nums}
td,th{padding:.3rem .5rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;white-space:nowrap}
th{font:500 .6rem var(--sans);text-transform:uppercase;letter-spacing:.06em;color:var(--dim)}
td.num,th.num{text-align:right}
td.head{white-space:normal;color:var(--dim);max-width:330px;font-size:.7rem}
tr.click{cursor:pointer}tr.click:hover td{background:var(--card2)}
tr.click:focus-visible{outline:2px solid var(--bright);outline-offset:-2px}
.pill{font:.6rem var(--mono);padding:.05em .5em;border-radius:99px}
.pill.ok{background:#12351f;color:var(--good)}.pill.bad{background:#3d1512;color:var(--bad)}
.pill.est{background:#2a2416;color:var(--warn)}
.dim{color:var(--dim)}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.15rem .35rem}
.empty{color:var(--dim);font:.76rem var(--sans);padding:.6rem}
.foot{margin-top:1.6rem;color:var(--dim);font:.68rem var(--sans);border-top:1px solid var(--line);padding-top:.6rem}
.bar{height:.3rem;border-radius:2px;background:var(--line2);overflow:hidden;margin-top:.25rem}
.bar i{display:block;height:100%;background:var(--codex)}
</style></head><body><div class="wrap">
<header><h1>TRI-MODEL OPS</h1><span class="live"><span class="p"></span>LIVE</span>
<span class="legend">legs<span class="dot" style="background:var(--claude)"></span>claude<span class="dot" style="background:var(--gemini)"></span>gemini<span class="dot" style="background:var(--codex)"></span>codex</span></header>
<div class="controls">
<select id="proj" title="folder filter"><option value="">all folders</option></select>
<select id="win" title="time window">
<option value="3600">last hour</option><option value="10800" selected>last three hours</option>
<option value="21600">last six hours</option><option value="86400">last day</option></select>
<span class="scope" id="scope"></span><span class="upd" id="upd"></span></div>
<div class="strip" id="strip"></div>
<h2>Timeline <span class="note">click any bar to inspect · lanes are project folders · hairline marks are point events too brief to scale, never widened bars</span></h2>
<div class="split">
<div class="tl"><div class="tlin"><div class="axisrow"><div class="axismask"></div><div class="axis" id="axis"></div></div><div id="lanes"></div></div></div>
<div class="insp" id="insp"></div></div>
<h2>Models <span class="note">tokens + list-price equivalent · subscriptions make actual marginal cost $0</span></h2>
<div class="tw"><table id="models"></table></div>
<h2>Folders <span class="note">what each project is consuming in this window</span></h2>
<div class="tw"><table id="folders"></table></div>
<h2>Leg call feed <span class="note">click a row to inspect</span></h2><div class="tw"><table id="feed"></table></div>
<h2>Runs</h2><div class="tw"><table id="runs"></table></div>
<p class="foot">Sources: agy-usage.jsonl (gemini), Claude session transcripts (per-turn usage), codex rollouts (token totals + plan burn).
Claude and codex token counts are <b>measured</b> and de-duplicated by request id; gemini has no token API through the CLI so its counts are a labelled estimate (chars/4).
Dollar figures are list-price equivalents, not billed amounts — Fable is priced at the published Opus tier as its nearest equivalent.
Codex start/end come from logged events (not file timestamps) and a rollout is only "ok" once it logs completion.</p>
</div><script>
// Single quotes MUST be escaped: the span payload rides in a single-quoted
// attribute, and one apostrophe in a model's output would truncate the JSON.
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const age=(n,t)=>{const s=Math.max(0,Math.round(n-t));if(s<60)return s+"s";if(s<3600)return Math.floor(s/60)+"m";
if(s<86400)return Math.floor(s/3600)+"h"+String(Math.floor(s%3600/60)).padStart(2,"0")+"m";
return Math.floor(s/86400)+"d"+String(Math.floor(s%86400/3600)).padStart(2,"0")+"h"};
const hm=t=>{const d=new Date(t*1000);return String(d.getHours()).padStart(2,"0")+":"+String(d.getMinutes()).padStart(2,"0")};
// Full wall clock — date + time + zone, so a span is unambiguous across days.
const hms=t=>{const d=new Date(t*1000);
const z=(d.toTimeString().match(/\(([^)]+)\)/)||[,""])[1].split(" ").map(w=>w[0]).join("");
return d.toLocaleDateString(undefined,{month:"short",day:"numeric"})+" "+d.toLocaleTimeString()+(z?" "+z:"")};
const K=n=>n>=1e6?(n/1e6).toFixed(2)+"M":n>=1e3?(n/1e3).toFixed(1)+"k":String(n||0);
// null cost = no published price for that model. Never render it as $0.
const USD=c=>c==null?"price n/a":c>=1?"$"+c.toFixed(2):c>0?"$"+c.toFixed(3):"$0";
const NUM=n=>n==null?"n/r":K(n);  // n/r = not recorded
// Never print "0s" for something we did not measure — say so instead.
const DUR=s=>(s&&s>=1)?Math.round(s)+"s":(s>0?"<1s":"not measured");
let cur=null,sel=null;
function pick(kind,payload){sel={kind,payload};render()}
let inspKey=null;
function inspector(){const el=document.getElementById("insp");
// Re-render ONLY when the selection changes; a blind 5s innerHTML rewrite
// throws away the operator's scroll position mid-read.
// Whether the selection has aged out is part of the render key, or the
// notice would never appear once cached.
const gone=!sel?false:(sel.kind==="claude"
?!cur.lanes.some(l=>l.name===sel.payload.project&&l.claude.some(sp=>Math.round(sp[0])===Math.round(sel.payload.a)))
:sel.kind==="claudeturn"?!cur.turns.some(t=>Math.round(t.ts*1000)===Math.round(sel.payload.ts*1000))
:!cur.events.some(e=>e.id===sel.id));
const key=sel?sel.kind+"|"+sel.id+"|"+gone:"none";
if(key===inspKey)return;inspKey=key;
if(!sel){
el.innerHTML='<div class="hint">Select any bar on the timeline — or a row in the feed — to inspect the call: exact times, model, sizes, tokens, cost equivalent and the model’s own output.</div>';return}
const p=sel.payload;let rows="",out="",title="",who="";
if(sel.kind==="gemini"){title=p.model;who="gemini leg · "+p.project;
rows=[["started",p.secs?hms(p.ts-p.secs):"not recorded"],["finished",hms(p.ts)],["duration",DUR(p.secs)],
["prompt",p.prompt_chars!=null?p.prompt_chars.toLocaleString()+" chars":"not recorded"],
["output",p.output_chars!=null?p.output_chars.toLocaleString()+" chars":"not recorded"],
["tokens (est.)",NUM(p.tin)+" in / "+NUM(p.tout)+" out"],["cost equiv. (list)",USD(p.cost)],
["delivery",p.via_file?"file relay":"inline argv"],["status",p.ok?"ok":"FAILED"]];
out=p.head?"— model output —\n"+p.head:"(no output captured)"}
else if(sel.kind==="codex"){title=p.model;who="gpt leg · "+p.project;
rows=[["session",p.session],
["started",p.logged_times?hms(p.start):"not logged"],
["last logged event",p.logged_times?hms(p.ts):"not logged"],
["duration",DUR(p.secs)],["time source",p.time_source||"logged events"],
["tokens total",K(p.total_tokens)],["fresh in",K(p.tin)],["cached in",K(p.cache_read)],
["output",K(p.tout)],["reasoning",K(p.reasoning)],["cost equiv. (list)",USD(p.cost)],
["plan burn",p.quota_pct!=null?p.quota_pct+"%":"not reported"],
["plan resets",p.quota_reset?hms(p.quota_reset):"not reported"],
["credit balance",p.plan!=null&&p.plan!==""?p.plan:"not reported"],
["status",p.status||(p.ok?"ok":"FAILED")]];
out=p.head?"— codex output —\n"+p.head:"(no agent message captured in this rollout)"}
else if(sel.kind==="claudeturn"){title=p.model;who="claude leg · "+p.project+" · single turn";
rows=[["at",hms(p.ts)],["duration","not measured (per-turn timing not logged)"],
["fresh input",K(p.tin)],["cache read",K(p.cache_read)],["cache write",K(p.cache_write)],
["output",K(p.tout)],["cost equiv. (list)",USD(p.cost)],
["status","usage recorded · transcripts log no success signal"]];
out=p.say?"— assistant output —\n"+p.say:"(no assistant text on this turn — tool use only)"}
else if(sel.kind==="claude"){title="claude work span";who=p.project;
rows=[["from",hms(p.a)],["to",hms(p.b)],
["span length",p.b>p.a?DUR(p.b-p.a)+" (first→last logged event)":"single logged event · no duration"],
["model(s)",p.model||"claude"],["turns in span",p.turns],
["fresh input",K(p.tin)],["output",K(p.tout)],["cache read",K(p.cache)],
["cache write",K(p.cwrite)],["tokens total",K(p.tokens)],
["cache hit",p.cachePct+"%"],
["cost equiv. (list)",USD(p.cost)+(p.costPartial?" + unpriced turns":"")],
["status",p.turns?p.turns+" turns recorded · no success signal in transcripts":"no turns recorded"]];
out=(p.says&&p.says.length)
?p.says.map(s=>`[${hms(s.ts)}] ${s.say}`).join("\n\n")
:"(no assistant text captured in this span)"}
el.innerHTML=`<h3>${esc(title)}</h3><div class="who">${esc(who)}</div>`+
(gone?'<div class="pill est" style="display:inline-block;margin-bottom:.5rem">outside the current window — kept for reference</div>':"")+
`<dl class="kv">`+rows.map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")+`</dl>`+
(out?`<div class="out">${esc(out)}</div>`:"");}
function render(){if(!cur)return;const d=cur,now=d.now,W=d.window,t0=now-W;
// Rebuilding the lanes destroys the focused node; remember it and give the
// keyboard operator their place back after the tick.
const focusId=(document.activeElement&&document.activeElement.dataset)?document.activeElement.dataset.id:null;
const pf=document.getElementById("proj").value;
const lanes=d.lanes.filter(l=>!pf||l.name===pf);
const evs=d.events.filter(e=>!pf||e.project===pf);
const turns=d.turns.filter(t=>!pf||t.project===pf);
const claudeTok=lanes.reduce((a,l)=>a+l.claude_tokens,0);
const cacheR=lanes.reduce((a,l)=>a+l.claude_cache,0),fresh=lanes.reduce((a,l)=>a+l.claude_fresh,0);
const cachePct=(cacheR+fresh)?(cacheR/(cacheR+fresh)*100).toFixed(1):"0.0";
const cost=turns.reduce((a,t)=>a+(t.cost||0),0)+evs.reduce((a,e)=>a+(e.cost||0),0);
const partial=turns.some(t=>t.cost==null)||evs.some(e=>e.cost==null);
const fails=evs.filter(e=>e.state==="failed"||e.state==="errored").length;
const running=evs.filter(e=>e.state==="running").length;
const q=d.quota;
document.getElementById("scope").textContent=pf?`scoped to ${pf}`:"all folders";
document.getElementById("strip").innerHTML=
`<div class="sc"><div class="k">sessions live</div><div class="v">${lanes.filter(l=>now-l.last<900).length}</div><div class="s">${lanes.length} in window</div></div>`+
`<div class="sc cla"><div class="k">claude tokens</div><div class="v">${K(claudeTok)}</div><div class="s">${turns.length} turns measured</div></div>`+
`<div class="sc cla"><div class="k">cache hit</div><div class="v">${cachePct}%</div><div class="s">${K(cacheR)} cached / ${K(fresh)} fresh</div></div>`+
`<div class="sc"><div class="k">cost equivalent</div><div class="v">${USD(cost)}${partial?"+":""}</div><div class="s">list price · $0 billed on subs${partial?" · some models unpriced":""}</div></div>`+
`<div class="sc gem"><div class="k">gemini calls</div><div class="v">${evs.filter(e=>e.leg==="gemini").length}</div><div class="s">${(()=>{const g=evs.filter(e=>e.leg==="gemini");const unk=g.filter(e=>e.tin==null||e.tout==null).length;
return (unk?"≥":"")+K(g.reduce((a,e)=>a+(e.tin||0)+(e.tout||0),0))+" tokens est."+(unk?` · ${unk} unrecorded`:"")})()}</div></div>`+
(q?`<div class="sc cdx ${q.pct>=80?"warn":""}"><div class="k">codex plan burn${pf?" · account-wide":""}</div><div class="v">${q.pct}%</div><div class="s">${pf?"not folder-scoped · ":""}resets ${q.resets_at?hms(q.resets_at):"n/a"}<br>read ${hms(q.read_at)} from rollout ${esc(q.from)} · ${q.in_window?"in window":"outside window"}<div class="bar"><i style="width:${Math.min(100,q.pct)}%"></i></div></div></div>`
:`<div class="sc cdx"><div class="k">codex plan burn</div><div class="v">n/a</div><div class="s">no rollout data</div></div>`)+
`<div class="sc ${fails?"bad":""}"><div class="k">leg failures</div><div class="v">${fails}</div><div class="s">in window${running?` · ${running} still running`:""}</div></div>`+
(d.totals.truncated?`<div class="sc warn"><div class="k">coverage</div><div class="v">partial</div><div class="s">a transcript exceeded the read cap</div></div>`:"");
const X=t=>Math.min(100,Math.max(0,(t-t0)/W*100));
let ticks="";for(let i=0;i<=6;i++)ticks+=`<div class="tick${i===0?" first":i===6?" last":""}" style="left:${(i/6*100).toFixed(1)}%">${hm(t0+W*i/6)}</div>`;
document.getElementById("axis").innerHTML=ticks;
const MIN=0.4;
document.getElementById("lanes").innerHTML='<div class="nowline"></div>'+(lanes.length?lanes.map(l=>{
const lt=d.turns.filter(t=>t.project===l.name);
const segs=l.claude.map((sp,i)=>{const w=X(sp[1])-X(sp[0]);
const inSpan=lt.filter(t=>t.ts>=sp[0]-2&&t.ts<=sp[1]+2);
const tok=inSpan.reduce((a,t)=>a+t.tin+t.tout,0),cr=inSpan.reduce((a,t)=>a+t.cache_read,0);
const fr=inSpan.reduce((a,t)=>a+t.tin+t.cache_write,0);
// Every turn's own words, not just the last — a span groups many turns.
const says=inSpan.filter(t=>t.say).slice(-8).map(t=>({ts:t.ts,say:t.say}));
const pay=JSON.stringify({a:sp[0],b:sp[1],project:l.name,turns:inSpan.length,tokens:tok,cache:cr,
tin:inSpan.reduce((a,t)=>a+t.tin,0),tout:inSpan.reduce((a,t)=>a+t.tout,0),
cwrite:inSpan.reduce((a,t)=>a+t.cache_write,0),
cachePct:((cr+fr)?(cr/(cr+fr)*100).toFixed(1):"0.0"),
cost:inSpan.reduce((a,t)=>a+(t.cost||0),0),costPartial:inSpan.some(t=>t.cost==null),
model:[...new Set(inSpan.map(t=>t.model))].join(", ")||"claude",says});
// Stable across polls: anchored to the span's own start time, not its index.
const id=`c-${l.name}-${Math.round(sp[0])}`;
const t=`claude ${hm(sp[0])}–${hm(sp[1])} · ${inSpan.length} turns · ${K(tok)} tokens · bracketed by logged events (gaps over 30s split the span)`;
return `<button class="seg${w>=MIN?"":" mark"}${sel&&sel.id===id?" sel":""}" data-id="${id}" data-kind="claude" data-p='${esc(pay)}' style="left:${w>=MIN?X(sp[0]).toFixed(2)+"%":`min(${X(sp[0]).toFixed(2)}%,calc(100% - 4px))`}${w>=MIN?`;width:${w.toFixed(2)}%`:""}" title="${t}" aria-label="${t}"></button>`}).join("");
// ANY leg with a measured duration draws a scaled bar — codex included.
const evb=l.events.map(e=>{const dur=e.secs||0;
const x0=X(e.ts-dur),w=dur?X(e.ts)-x0:0,scaled=w>=MIN;
const cls=(e.leg==="codex"?"legcodex ":"")+(scaled?"":"mark");
// A running rollout is neither success nor failure — dashed, never red.
const stateCls=(e.state==="failed"||e.state==="errored")?" fail":(e.state==="running"?" running":"");
const when=(e.leg==="codex"&&!e.logged_times)?`${hm(e.ts)} (file mtime — no timestamps logged)`:hm(e.ts);
const t=`${e.model} · ${when} · ${e.detail}${e.secs?` · ${Math.round(e.secs)}s`:" · duration not measured"}${stateCls===" fail"?" · FAILED":stateCls===" running"?" · running":""}`;
return `<button class="ev ${cls}${stateCls}${sel&&sel.id===e.id?" sel":""}" data-id="${e.id}" data-kind="${e.leg}" style="left:${scaled?x0.toFixed(2)+"%":`min(${X(e.ts).toFixed(2)}%,calc(100% - 8px))`}${scaled?`;width:${w.toFixed(2)}%`:""}" title="${esc(t)}" aria-label="${esc(t)}"></button>`}).join("");
return `<div class="lane"><div class="lname"><b>${esc(l.name)}</b><span class="a">${age(now,l.last)} ago · ${K(l.claude_tokens)} tok · ${USD(l.claude_cost+l.leg_cost)}${l.cost_partial?"+":""}</span></div><div class="track">${segs}${evb}</div></div>`}).join("")
:'<div class="empty">no activity in this window</div>');
// Recomputed from the FILTERED turns+events so the folder selection scopes
// the model table too — server aggregates are global and would lie here.
const mm={};const B=(leg,est)=>({leg,n:0,tin:0,tout:0,cache:0,cost:0,priced:true,secs:0,timed:0,fail:0,running:0,unknown:0,est:!!est});
for(const t of turns){const s=mm[t.model]??(mm[t.model]=B("claude"));
s.n++;s.tin+=t.tin;s.tout+=t.tout;s.cache+=t.cache_read;
if(t.cost==null)s.priced=false;else s.cost+=t.cost}
for(const e of evs){const s=mm[e.model]??(mm[e.model]=B(e.leg,e.est_tokens));
s.n++;
// A call whose sizes were never recorded is COUNTED as unknown, not summed
// as zero — otherwise the total reads as measured when it isn't.
if(e.tin==null||e.tout==null)s.unknown++;else{s.tin+=e.tin;s.tout+=e.tout}
s.cache+=e.cache_read||0;
if(e.cost==null)s.priced=false;else s.cost+=e.cost;
if(e.secs){s.secs+=e.secs;s.timed++}
if(e.state==="failed"||e.state==="errored")s.fail++;else if(e.state==="running")s.running++}
const models=Object.entries(mm).map(([model,v])=>({model,...v})).sort((a,b)=>b.cost-a.cost);
document.getElementById("models").innerHTML="<tr><th>model</th><th>leg</th><th class=num>calls</th><th class=num>in</th><th class=num>out</th><th class=num>cached</th><th class=num>avg</th><th class=num>cost equiv. (list)</th><th>fails</th></tr>"+
(models.length?models.map(m=>`<tr><td><span class="dot" style="background:var(--${m.leg})"></span>${esc(m.model)}${m.est?' <span class="pill est">est</span>':""}</td>`+
`<td class="dim">${m.leg}</td><td class="num">${m.n}</td>`+
`<td class="num">${m.unknown?"≥":""}${K(m.tin)}</td><td class="num">${m.unknown?"≥":""}${K(m.tout)}</td>`+
`<td class="num">${K(m.cache)}</td><td class="num">${m.timed?(m.secs/m.timed).toFixed(1)+"s"+(m.timed<m.n?` <span class="dim">/${m.timed}</span>`:""):'<span class="dim">not timed</span>'}</td>`+
`<td class="num">${m.priced?USD(m.cost):'<span class="dim">price n/a</span>'}</td>`+
`<td>${m.fail?`<span class="pill bad">${m.fail}</span>`:(m.leg==="claude"?'<span class="dim">n/a</span>':'<span class="dim">0</span>')}${m.running?` <span class="pill est">${m.running} running</span>`:""}</td></tr>`).join("")
:'<tr><td class="empty" colspan="9">no model activity in this window</td></tr>');
document.getElementById("folders").innerHTML="<tr><th>folder</th><th class=num>turns</th><th class=num>claude tok</th><th class=num>cache hit</th><th class=num>leg calls</th><th class=num>cost equiv.</th><th class=num>last active</th></tr>"+
(lanes.length?lanes.map(l=>{const cp=(l.claude_cache+l.claude_fresh)?(l.claude_cache/(l.claude_cache+l.claude_fresh)*100).toFixed(0):"0";
return `<tr><td>${esc(l.name)}</td><td class="num">${l.turns}</td><td class="num">${K(l.claude_tokens)}</td>`+
`<td class="num">${cp}%</td><td class="num">${l.events.length}</td>`+
`<td class="num">${USD(l.claude_cost+l.leg_cost)}${l.cost_partial?'<span class="dim">+</span>':""}</td>`+
`<td class="num dim">${age(now,l.last)}</td></tr>`}).join(""):'<tr><td class="empty" colspan="7">no folders active</td></tr>');
// ALL THREE legs in one chronology — Claude turns included, not just the
// metered legs. Each row opens the same inspector the timeline does.
const claudeRows=turns.map(t=>({id:"t-"+Math.round(t.ts*1000),leg:"claude",kind:"claudeturn",
ts:t.ts,model:t.model,project:t.project,secs:null,cost:t.cost,state:"recorded",
detail:`${K(t.tin)} fresh / ${K(t.cache_read)} cached in · ${K(t.tout)} out`,head:t.say||"",turn:t}));
const feed=[...evs.map(e=>({...e,kind:e.leg})),...claudeRows].sort((a,b)=>b.ts-a.ts).slice(0,50);
document.getElementById("feed").innerHTML="<tr><th>age</th><th>leg / model</th><th>folder</th><th>size</th><th class=num>time</th><th class=num>cost equiv. (list)</th><th>ok</th><th>said</th></tr>"+
(feed.length?feed.map(r=>`<tr class="click" tabindex="0" role="button" aria-label="inspect ${esc(r.model)} call in ${esc(r.project)}" data-id="${r.id}" data-kind="${r.kind}"${r.kind==="claudeturn"?` data-p='${esc(JSON.stringify(r.turn))}'`:""}><td class="dim">${age(now,r.ts)}</td>`+
`<td><span class="dot" style="background:var(--${r.leg})"></span>${esc(r.model)}</td><td>${esc(r.project)}</td>`+
`<td class="dim">${esc(r.detail)}</td><td class="num">${r.secs?Math.round(r.secs)+"s":'<span class="dim">not timed</span>'}</td>`+
`<td class="num">${USD(r.cost)}</td><td>${r.state==="recorded"?'<span class="dim">n/a</span>':r.state==="running"?'<span class="pill est">running</span>':`<span class="pill ${r.state==="ok"||r.state==="completed"?"ok":"bad"}">${r.state==="ok"||r.state==="completed"?"ok":"FAIL"}</span>`}</td>`+
`<td class="head">${esc((r.head||"").slice(0,110))}</td></tr>`).join(""):'<tr><td class="empty" colspan="8">no activity in this window</td></tr>');
document.getElementById("runs").innerHTML="<tr><th>age</th><th>kind</th><th>run</th><th class=num>events</th><th>last</th></tr>"+
(d.runs.length?d.runs.map(r=>`<tr><td class="dim">${age(now,r.ts)}</td><td>${esc(r.kind)}</td><td>${esc(r.name)}</td>`+
`<td class="num">${r.events}</td><td>${esc(r.last)}</td></tr>`).join(""):'<tr><td class="empty" colspan="5">no runs yet — fire /gauntlet or /adw</td></tr>');
inspector();
if(focusId){const back=document.querySelector(`[data-id="${CSS.escape(focusId)}"]`);if(back)back.focus({preventScroll:true})}
document.getElementById("upd").textContent="updated "+new Date().toLocaleTimeString();}
function onPick(t){const el=t.closest("[data-kind]");if(!el)return;
const kind=el.dataset.kind,id=el.dataset.id;
if(kind==="claude"||kind==="claudeturn"){sel={kind,id,payload:JSON.parse(el.dataset.p)}}
else{const e=cur.events.find(x=>x.id===id);if(!e)return;sel={kind,id,payload:e}}
render()}
document.addEventListener("click",e=>onPick(e.target));
document.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){if(e.target.dataset&&e.target.dataset.kind){e.preventDefault();onPick(e.target)}}
if(e.key==="Escape"){sel=null;render()}});
async function tick(){const W=document.getElementById("win").value;
try{cur=await(await fetch("/data?window="+W)).json()}catch(e){return}
const s=document.getElementById("proj"),had=s.value;
const names=[...new Set(cur.lanes.map(l=>l.name))];
// Even a legitimate change waits while the operator has the menu open.
if(s.dataset.names!==names.join("")&&document.activeElement!==s){s.dataset.names=names.join("");
s.innerHTML='<option value="">all folders</option>'+names.map(n=>`<option${n===had?" selected":""}>${esc(n)}</option>`).join("")}
render()}
document.getElementById("proj").addEventListener("change",render);
document.getElementById("win").addEventListener("change",tick);
tick();setInterval(tick,5000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/data":
            q = parse_qs(u.query)
            window = max(600, min(86400, int(q.get("window", ["10800"])[0])))
            body = json.dumps(build_data(window)).encode()
            ctype = "application/json"
        else:
            body = PAGE.encode()
            ctype = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"tri-model dashboard: http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
