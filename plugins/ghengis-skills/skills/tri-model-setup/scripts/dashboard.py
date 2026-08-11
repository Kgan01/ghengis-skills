#!/usr/bin/env python3
"""Tri-model harness — live leg-activity dashboard.

Single stdlib file. Serves http://127.0.0.1:8321 with a dark ops view of which
model leg is doing what, fed from the harness's own logs:
  - ~/.claude/tri-model/agy-usage.jsonl      (Gemini leg, every call)
  - ~/.codex/sessions/**                     (GPT leg rollouts)
  - ~/.claude/projects/*/                    (Claude sessions, transcript mtimes)
  - ~/.claude/tri-model/{gauntlet,adw}-runs  (run metrics)

Launch:  python %USERPROFILE%\\.claude\\tri-model\\dashboard.py
"""
import json
import re
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOME = Path.home()
TRI = HOME / ".claude" / "tri-model"
AGY_LOG = TRI / "agy-usage.jsonl"
CODEX_SESSIONS = HOME / ".codex" / "sessions"
PROJECTS = HOME / ".claude" / "projects"
PORT = 8321


def _age(ts: float) -> str:
    s = max(0, int(time.time() - ts))
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m"
    if s < 86400:
        return f"{s // 3600}h {s % 3600 // 60}m"
    return f"{s // 86400}d"


def read_agy(limit: int = 40) -> list[dict]:
    if not AGY_LOG.exists():
        return []
    rows = []
    for line in AGY_LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-200:]:
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            ts = datetime.fromisoformat(j.get("ts", "")).timestamp()
        except ValueError:
            continue
        ok = j.get("exit") == 0
        rows.append({
            "leg": "gemini", "ts": ts, "model": j.get("model", "?"),
            "where": (j.get("cwd") or "").split("\\")[-1] or "(global)",
            "detail": f"{j.get('prompt_chars', 0):,}→{j.get('output_chars', 0):,}ch"
                      + (" ·file" if j.get("via_file") else ""),
            "secs": j.get("seconds"), "ok": ok,
            "head": (j.get("output_head") or "")[:90],
        })
    return sorted(rows, key=lambda r: -r["ts"])[:limit]


def read_codex(limit: int = 15) -> list[dict]:
    if not CODEX_SESSIONS.exists():
        return []
    rows = []
    for f in CODEX_SESSIONS.rglob("*.jsonl"):
        st = f.stat()
        cwd = ""
        try:
            first = f.open(encoding="utf-8", errors="replace").readline()
            cwd = (json.loads(first).get("payload", {}) or {}).get("cwd", "")
        except Exception:
            pass
        rows.append({
            "leg": "codex", "ts": st.st_mtime, "model": "codex",
            "where": cwd.split("\\")[-1] if cwd else f.name[8:24],
            "detail": f"{st.st_size // 1024}KB rollout", "secs": None,
            "ok": True, "head": "",
        })
    return sorted(rows, key=lambda r: -r["ts"])[:limit]


def read_sessions() -> list[dict]:
    if not PROJECTS.exists():
        return []
    agy_by_slug: dict[str, int] = {}
    for r in read_agy(200):
        agy_by_slug[r["where"]] = agy_by_slug.get(r["where"], 0) + 1
    out = []
    for d in PROJECTS.iterdir():
        if not d.is_dir():
            continue
        newest = 0.0
        for f in d.glob("*.jsonl"):
            newest = max(newest, f.stat().st_mtime)
        if newest and time.time() - newest < 6 * 3600:
            name = re.sub(r"^[A-Z]--", "", d.name)
            out.append({"name": name, "ts": newest,
                        "active": time.time() - newest < 900})
    return sorted(out, key=lambda r: -r["ts"])[:14]


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
            lines = [ln for ln in m.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
            last = {}
            try:
                last = json.loads(lines[-1]) if lines else {}
            except json.JSONDecodeError:
                pass
            out.append({
                "kind": kind.split("-")[0], "name": run.name,
                "ts": m.stat().st_mtime, "events": len(lines),
                "last": last.get("verdict") or last.get("gate") or last.get("phase") or "",
            })
    return sorted(out, key=lambda r: -r["ts"])[:10]


def build_data() -> dict:
    feed = sorted(read_agy() + read_codex(), key=lambda r: -r["ts"])[:35]
    hour = time.time() - 3600
    day = time.time() - 86400
    agy_all = read_agy(200)
    return {
        "now": time.time(),
        "feed": feed,
        "sessions": read_sessions(),
        "runs": read_runs(),
        "summary": {
            "gemini_1h": sum(1 for r in agy_all if r["ts"] > hour),
            "gemini_24h": sum(1 for r in agy_all if r["ts"] > day),
            "gemini_fail_24h": sum(1 for r in agy_all if r["ts"] > day and not r["ok"]),
            "codex_24h": sum(1 for r in read_codex(100) if r["ts"] > day),
            "sessions_live": sum(1 for s in read_sessions() if s["active"]),
        },
    }


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>tri-model — leg activity</title><style>
:root{--page:#0a0d12;--card:#12161d;--line:#1f2733;--text:#c7d0dc;--dim:#5c6878;
--bright:#e8edf4;--claude:#d97757;--gemini:#9ece6a;--codex:#7aa2f7;--dgx:#bb9af7;
--good:#56d364;--warn:#e3b341;--bad:#f85149;
--mono:"Cascadia Code",Consolas,ui-monospace,monospace;--sans:"Segoe UI",system-ui,sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--text);
font:14px/1.5 var(--sans);padding:1.4rem 1.2rem 3rem}
.wrap{max-width:1100px;margin:0 auto}
h1{font:600 1.05rem var(--mono);color:var(--bright);margin:0 0 .2rem;letter-spacing:.04em}
.sub{color:var(--dim);font-size:.8rem;margin:0 0 1.1rem}
.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.6rem;margin-bottom:1.4rem}
.sc{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--line);
border-radius:8px;padding:.6rem .8rem}
.sc .k{font:.66rem var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--dim)}
.sc .v{font:600 1.35rem var(--mono);font-variant-numeric:tabular-nums;color:var(--bright)}
.sc.gem{border-left-color:var(--gemini)}.sc.cdx{border-left-color:var(--codex)}
.sc.cla{border-left-color:var(--claude)}.sc.bad{border-left-color:var(--bad)}
.sc.bad .v{color:var(--bad)}
h2{font:600 .72rem var(--mono);text-transform:uppercase;letter-spacing:.08em;
color:var(--dim);margin:1.6rem 0 .5rem;border-bottom:1px solid var(--line);padding-bottom:.3rem}
table{border-collapse:collapse;width:100%;font:.78rem var(--mono);font-variant-numeric:tabular-nums}
td{padding:.32rem .55rem;border-bottom:1px solid var(--line);vertical-align:top;white-space:nowrap}
td.head{white-space:normal;color:var(--dim);max-width:340px}
.dot{display:inline-block;width:.55rem;height:.55rem;border-radius:99px;margin-right:.4rem;vertical-align:baseline}
.pill{font:.64rem var(--mono);padding:.06em .55em;border-radius:99px;letter-spacing:.03em}
.pill.ok{background:#12351f;color:var(--good)}.pill.bad{background:#3d1512;color:var(--bad)}
.pill.live{background:#12351f;color:var(--good)}.pill.idle{background:#1a212c;color:var(--dim)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:.6rem}
.card{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--claude);
border-radius:8px;padding:.55rem .8rem;font:.8rem var(--mono)}
.card .n{color:var(--bright)}.card .a{color:var(--dim);font-size:.72rem}
.dim{color:var(--dim)}.tw{overflow-x:auto}
.age{color:var(--dim);font-size:.7rem}
</style></head><body><div class="wrap">
<h1>TRI-MODEL — LEG ACTIVITY</h1>
<p class="sub">claude <span class="dot" style="background:var(--claude)"></span>·
gemini <span class="dot" style="background:var(--gemini)"></span>·
codex <span class="dot" style="background:var(--codex)"></span>
&nbsp; refreshes every 5s · <span id="upd" class="age"></span></p>
<div class="strip" id="strip"></div>
<h2>Leg call feed — newest first</h2><div class="tw"><table id="feed"></table></div>
<h2>Claude sessions (last 6h)</h2><div class="grid" id="sess"></div>
<h2>Runs (gauntlet / adw)</h2><div class="tw"><table id="runs"></table></div>
</div><script>
const esc=s=>String(s??"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const age=(now,ts)=>{const s=Math.max(0,Math.round(now-ts));
if(s<60)return s+"s";if(s<3600)return Math.floor(s/60)+"m";
if(s<86400)return Math.floor(s/3600)+"h "+Math.floor(s%3600/60)+"m";return Math.floor(s/86400)+"d"};
async function tick(){let d;try{d=await(await fetch("/data")).json()}catch(e){return}
const s=d.summary;
document.getElementById("strip").innerHTML=
`<div class="sc cla"><div class="k">sessions live now</div><div class="v">${s.sessions_live}</div></div>`+
`<div class="sc gem"><div class="k">gemini calls · 1h</div><div class="v">${s.gemini_1h}</div></div>`+
`<div class="sc gem"><div class="k">gemini calls · 24h</div><div class="v">${s.gemini_24h}</div></div>`+
`<div class="sc cdx"><div class="k">codex rollouts · 24h</div><div class="v">${s.codex_24h}</div></div>`+
`<div class="sc ${s.gemini_fail_24h?"bad":""}"><div class="k">leg failures · 24h</div><div class="v">${s.gemini_fail_24h}</div></div>`;
document.getElementById("feed").innerHTML=d.feed.map(r=>
`<tr><td class="age">${age(d.now,r.ts)}</td>`+
`<td><span class="dot" style="background:var(--${r.leg})"></span>${esc(r.model)}</td>`+
`<td>${esc(r.where)}</td><td class="dim">${esc(r.detail)}${r.secs?` · ${r.secs}s`:""}</td>`+
`<td><span class="pill ${r.ok?"ok":"bad"}">${r.ok?"ok":"FAIL"}</span></td>`+
`<td class="head">${esc(r.head)}</td></tr>`).join("");
document.getElementById("sess").innerHTML=d.sessions.map(x=>
`<div class="card"><span class="n">${esc(x.name)}</span> `+
`<span class="pill ${x.active?"live":"idle"}">${x.active?"active":"idle"}</span>`+
`<div class="a">last activity ${age(d.now,x.ts)} ago</div></div>`).join("");
document.getElementById("runs").innerHTML=d.runs.length?d.runs.map(r=>
`<tr><td class="age">${age(d.now,r.ts)}</td><td>${esc(r.kind)}</td>`+
`<td>${esc(r.name)}</td><td class="dim">${r.events} events</td><td>${esc(r.last)}</td></tr>`).join("")
:'<tr><td class="dim">no runs yet — fire /gauntlet or /adw</td></tr>';
document.getElementById("upd").textContent="updated "+new Date().toLocaleTimeString();}
tick();setInterval(tick,5000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            body = json.dumps(build_data()).encode()
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
