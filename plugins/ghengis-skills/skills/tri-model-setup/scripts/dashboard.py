#!/usr/bin/env python3
"""Tri-model harness — live leg-activity dashboard with swim-lane timeline.

Single stdlib file. Serves http://127.0.0.1:8321 — a dark ops view of which
model leg is doing what, THROUGH TIME, per project folder. Lineage: IndyDevDan's
software-factory visualizer / pi-workbench adw-viz.mjs, rebuilt live.

Data sources (the harness's own logs — nothing synthetic):
  - ~/.claude/tri-model/agy-usage.jsonl      Gemini leg: every call, real durations
  - ~/.codex/sessions/**                     GPT leg rollouts (event marks)
  - ~/.claude/projects/*/<newest>.jsonl      Claude activity spans from transcript timestamps
  - ~/.claude/tri-model/{gauntlet,adw}-runs  run metrics

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

_TS_RE = re.compile(r'"timestamp"\s*:\s*"([^"]+)"')
_span_cache: dict = {}


def _slug(cwd: str) -> str:
    return re.sub(r"[:\\/ ]", "-", cwd or "")


def _project_for(cwd: str, project_names: list[str]) -> str | None:
    """Map a working directory to the Claude project dir that owns it."""
    s = _slug(cwd)
    best = None
    for p in project_names:
        if s == p or s.startswith(p + "-") or s.startswith(p):
            if best is None or len(p) > len(best):
                best = p
    return best


def _pretty(project: str) -> str:
    """Human folder name from a Claude project-dir slug."""
    name = re.sub(r"^[A-Z]--", "", project)
    name = re.sub(r"^Users-[^-]+-(?:OneDrive-)?(?:Desktop-)?", "", name)
    if re.match(r"^Users-[^-]+$", name):
        return "home"
    if "AppData" in name:
        return "temp-" + name.split("-")[-1]
    return name or project


def read_agy(limit: int = 400) -> list[dict]:
    if not AGY_LOG.exists():
        return []
    rows = []
    for line in AGY_LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
        try:
            j = json.loads(line)
            ts = datetime.fromisoformat(j["ts"]).timestamp()
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
        rows.append({
            "leg": "gemini", "ts": ts, "secs": j.get("seconds") or 0,
            "model": j.get("model", "?"), "cwd": j.get("cwd") or "",
            "ok": j.get("exit") == 0,
            "detail": f"{j.get('prompt_chars', 0):,} in / {j.get('output_chars', 0):,} out"
                      + (" / via file" if j.get("via_file") else ""),
            "head": (j.get("output_head") or "")[:110],
        })
    return rows


def read_codex() -> list[dict]:
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
        rows.append({"leg": "codex", "ts": st.st_mtime, "secs": 0, "model": "codex",
                     "cwd": cwd, "ok": True,
                     "detail": f"rollout {st.st_size // 1024}KB", "head": ""})
    return rows


def claude_spans(project_dir: Path, t0: float) -> list[list[float]]:
    """Merge transcript line timestamps into [start, end] activity spans.
    Honest data: spans come from real event timestamps; gaps > 3min split."""
    newest, mt = None, 0.0
    for f in project_dir.glob("*.jsonl"):
        m = f.stat().st_mtime
        if m > mt:
            newest, mt = f, m
    if not newest or mt < t0:
        return []
    key = (str(newest), mt, int(t0 // 60))
    if key in _span_cache:
        return _span_cache[key]
    try:
        with newest.open("rb") as fh:
            fh.seek(max(0, newest.stat().st_size - 3_000_000))
            text = fh.read().decode("utf-8", errors="replace")
    except OSError:
        return []
    stamps = []
    for m in _TS_RE.finditer(text):
        try:
            stamps.append(datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).timestamp())
        except ValueError:
            continue
    stamps = sorted(s for s in set(stamps) if s >= t0)
    spans: list[list[float]] = []
    for s in stamps:
        if spans and s - spans[-1][1] <= 180:
            spans[-1][1] = s
        else:
            spans.append([s, s])
    _span_cache[key] = spans
    if len(_span_cache) > 200:
        _span_cache.pop(next(iter(_span_cache)))
    return spans


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
            out.append({"kind": kind.split("-")[0], "name": run.name,
                        "ts": m.stat().st_mtime, "events": len(lines),
                        "last": str(last.get("verdict") or last.get("gate") or last.get("phase") or "")})
    return sorted(out, key=lambda r: -r["ts"])[:12]


def build_data(window: int) -> dict:
    now = time.time()
    t0 = now - window
    project_dirs = [d for d in PROJECTS.iterdir() if d.is_dir()] if PROJECTS.exists() else []
    project_names = [d.name for d in project_dirs]

    agy = read_agy()
    codex = read_codex()
    for r in agy + codex:
        p = _project_for(r["cwd"], project_names)
        r["project"] = _pretty(p) if p else (r["cwd"].split("\\")[-1] or "global")

    lanes = {}
    for d in project_dirs:
        spans = claude_spans(d, t0)
        if spans:
            lanes.setdefault(_pretty(d.name), {"claude": [], "events": []})["claude"] = spans
    for r in agy + codex:
        if r["ts"] >= t0:
            lanes.setdefault(r["project"], {"claude": [], "events": []})["events"].append(r)

    lane_list = []
    for name, v in lanes.items():
        last = max([s[1] for s in v["claude"]] + [e["ts"] for e in v["events"]] or [0])
        lane_list.append({"name": name, "claude": v["claude"], "events": v["events"], "last": last})
    lane_list.sort(key=lambda x: -x["last"])

    hour, day = now - 3600, now - 86400
    score: dict = {}
    for r in agy:
        if r["ts"] > day:
            s = score.setdefault(r["model"], {"n": 0, "secs": 0.0, "ok": 0})
            s["n"] += 1
            s["secs"] += r["secs"] or 0
            s["ok"] += 1 if r["ok"] else 0
    feed = sorted([r for r in agy + codex if r["ts"] >= t0], key=lambda r: -r["ts"])[:400]
    return {
        "now": now, "window": window,
        "lanes": lane_list[:12],
        # Deep enough that a per-folder filter never starves (frontend slices).
        "feed": feed,
        "runs": read_runs(),
        "score": [{"model": k, **v} for k, v in sorted(score.items(), key=lambda kv: -kv[1]["n"])],
        "summary": {
            "gemini_1h": sum(1 for r in agy if r["ts"] > hour),
            "gemini_24h": sum(1 for r in agy if r["ts"] > day),
            "fails_24h": sum(1 for r in agy if r["ts"] > day and not r["ok"]),
            "codex_24h": sum(1 for r in codex if r["ts"] > day),
            "sessions_live": sum(1 for ln in lane_list if now - ln["last"] < 900),
        },
    }


PAGE = r"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>tri-model ops</title><style>
:root{--page:#0a0d12;--card:#12161d;--card2:#161b24;--line:#1f2733;--line2:#2a3442;
--text:#c7d0dc;--dim:#5c6878;--bright:#e8edf4;
--claude:#d97757;--gemini:#9ece6a;--codex:#7aa2f7;--dgx:#bb9af7;
--good:#56d364;--warn:#e3b341;--bad:#f85149;
--mono:"Cascadia Code",Consolas,ui-monospace,monospace;--sans:"Segoe UI",system-ui,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--text);font:14px/1.5 var(--sans);padding:1.3rem 1.2rem 3rem}
.wrap{max-width:1180px;margin:0 auto}
header{display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap;margin-bottom:1rem}
h1{font:600 1.02rem var(--mono);color:var(--bright);margin:0;letter-spacing:.05em}
.live{display:inline-flex;align-items:center;gap:.4rem;font:.68rem var(--mono);color:var(--bright)}
.live .p{width:.5rem;height:.5rem;border-radius:99px;background:var(--bright);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
.legend{font:.7rem var(--mono);color:var(--dim);margin-left:auto}
.legend b{color:var(--text);font-weight:500}
.dot{display:inline-block;width:.55rem;height:.55rem;border-radius:99px;margin:0 .3rem 0 .8rem;vertical-align:baseline}
.controls{display:flex;gap:.6rem;align-items:center;margin-bottom:1rem;flex-wrap:wrap}
select{background:var(--card);color:var(--text);border:1px solid var(--line2);border-radius:6px;
padding:.32rem .6rem;font:.78rem var(--sans);cursor:pointer}
select:hover{border-color:var(--dim);background:var(--card2)}
select:focus-visible{outline:2px solid var(--bright);outline-offset:1px}
.upd{font:.68rem var(--mono);font-variant-numeric:tabular-nums;color:var(--dim);margin-left:auto}
.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.6rem;margin-bottom:1.5rem}
.sc{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--line2);border-radius:8px;padding:.55rem .8rem}
.sc .k{font:.64rem var(--sans);text-transform:uppercase;letter-spacing:.07em;color:var(--dim)}
.sc .v{font:600 1.4rem var(--mono);font-variant-numeric:tabular-nums;color:var(--bright)}
.sc.cla{border-left-color:var(--claude)}.sc.gem{border-left-color:var(--gemini)}
.sc.cdx{border-left-color:var(--codex)}.sc.bad{border-left-color:var(--bad)}.sc.bad .v{color:var(--bad)}
h2{font:600 .7rem var(--mono);text-transform:uppercase;letter-spacing:.09em;color:var(--dim);
margin:1.7rem 0 .55rem;border-bottom:1px solid var(--line);padding-bottom:.3rem}
.tl{background:var(--card);border:1px solid var(--line);border-radius:10px;padding: .7rem .9rem 1rem;overflow-x:auto}
.tlin{min-width:740px}
.axisrow{display:flex;align-items:flex-start}
.axismask{width:170px;min-width:170px;height:1.1rem;position:sticky;left:0;z-index:3;background:var(--card)}
.axis{position:relative;flex:1;height:1.1rem;font:.62rem var(--mono);font-variant-numeric:tabular-nums;color:var(--dim)}
.axis .tick{position:absolute;top:0;transform:translateX(-50%)}
.axis .tick.last{transform:translateX(-100%)}
.lane{display:flex;align-items:center;min-height:2.1rem;border-top:1px solid var(--line)}
.lane:first-of-type{border-top:0}
.lname{width:170px;min-width:170px;font:.74rem var(--sans);color:var(--bright);
overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding-right:.7rem;
position:sticky;left:0;z-index:2;background:var(--card)}
.lname .a{display:block;font:.62rem var(--mono);font-variant-numeric:tabular-nums;color:var(--dim)}
.track{position:relative;flex:1;height:1.5rem;overflow:hidden}
#lanes{position:relative}
#lanes .nowline{position:absolute;right:0;top:0;bottom:0;width:1px;background:var(--line2)}
.seg{position:absolute;top:.42rem;height:.62rem;border-radius:3px;background:var(--claude);opacity:.42}
.seg:hover{opacity:.75}
.ev{position:absolute;top:.18rem;height:1.1rem;border-radius:3px;min-width:5px;background:var(--gemini);opacity:.95;cursor:default}
.ev.fail{outline:1.5px solid var(--bad)}
.ev.codex{background:var(--codex);width:7px;top:.3rem;height:.9rem;border-radius:2px}
.ev.mark{width:6px;top:.3rem;height:.9rem;border-radius:2px}
.seg.mark{width:4px;border-radius:2px}
.ev:hover{filter:brightness(1.25)}
table{border-collapse:collapse;width:100%;font:.76rem var(--mono);font-variant-numeric:tabular-nums}
td,th{padding:.32rem .55rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;white-space:nowrap}
th{font:500 .62rem var(--sans);text-transform:uppercase;letter-spacing:.06em;color:var(--dim)}
td.num,th.num{text-align:right}
td.head{white-space:normal;color:var(--dim);max-width:380px;font-size:.72rem}
.pill{font:.62rem var(--mono);padding:.05em .5em;border-radius:99px;letter-spacing:.03em}
.pill.ok{background:#12351f;color:var(--good)}.pill.bad{background:#3d1512;color:var(--bad)}
.dim{color:var(--dim)}.tw{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.2rem .4rem}
.empty{color:var(--dim);font:.78rem var(--mono);padding:.6rem}
</style></head><body><div class="wrap">
<header><h1>TRI-MODEL OPS</h1><span class="live"><span class="p"></span>LIVE</span>
<span class="legend">legs<b><span class="dot" style="background:var(--claude)"></span>claude</b><b><span class="dot" style="background:var(--gemini)"></span>gemini</b><b><span class="dot" style="background:var(--codex)"></span>codex</b></span></header>
<div class="controls">
<select id="proj" title="folder filter"><option value="">all folders</option></select>
<select id="win" title="time window">
<option value="3600">last hour</option><option value="10800" selected>last three hours</option>
<option value="21600">last six hours</option><option value="86400">last day</option></select>
<span class="upd" id="upd"></span></div>
<div class="strip" id="strip"></div>
<h2>Timeline — who worked when</h2><div class="tl"><div class="tlin"><div class="axisrow"><div class="axismask"></div><div class="axis" id="axis"></div></div><div id="lanes"></div></div></div>
<h2>Leg call feed</h2><div class="tw"><table id="feed"></table></div>
<h2>Scoreboard — gemini models, 24h</h2><div class="tw"><table id="score"></table></div>
<h2>Runs — gauntlet / adw</h2><div class="tw"><table id="runs"></table></div>
</div><script>
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const age=(now,ts)=>{const s=Math.max(0,Math.round(now-ts));
if(s<60)return s+"s";if(s<3600)return Math.floor(s/60)+"m";
if(s<86400)return Math.floor(s/3600)+"h"+String(Math.floor(s%3600/60)).padStart(2,"0")+"m";
return Math.floor(s/86400)+"d"+String(Math.floor(s%86400/3600)).padStart(2,"0")+"h"};
const hm=ts=>{const d=new Date(ts*1000);return String(d.getHours()).padStart(2,"0")+":"+String(d.getMinutes()).padStart(2,"0")};
let cur=null;
function render(){if(!cur)return;const d=cur,now=d.now,W=d.window,t0=now-W;
const pf=document.getElementById("proj").value;
const lanes=d.lanes.filter(l=>!pf||l.name===pf);
const s=d.summary;
document.getElementById("strip").innerHTML=
`<div class="sc"><div class="k">sessions live</div><div class="v">${s.sessions_live}</div></div>`+
`<div class="sc gem"><div class="k">gemini · past hour</div><div class="v">${s.gemini_1h}</div></div>`+
`<div class="sc gem"><div class="k">gemini · past day</div><div class="v">${s.gemini_24h}</div></div>`+
`<div class="sc cdx"><div class="k">codex · past day</div><div class="v">${s.codex_24h}</div></div>`+
`<div class="sc ${s.fails_24h?"bad":""}"><div class="k">leg failures · past day</div><div class="v">${s.fails_24h}</div></div>`;
const X=ts=>Math.min(100,Math.max(0,(ts-t0)/W*100));
let ticks="";for(let i=0;i<=6;i++){ticks+=`<div class="tick${i===6?" last":""}" style="left:${(i/6*100).toFixed(1)}%">${hm(t0+W*i/6)}</div>`}
document.getElementById("axis").innerHTML=ticks;
document.getElementById("lanes").innerHTML='<div class="nowline"></div>'+(lanes.length?lanes.map(l=>{
// MIN_W is the smallest width that renders as a scaled duration. Anything
// shorter becomes a point MARK — never a widened bar, which would overstate
// how long the work took. Exact seconds always live in the tooltip.
const MIN_W=0.4;
const segs=l.claude.map(sp=>{const w=X(sp[1])-X(sp[0]);
const t=`claude active ${hm(sp[0])}–${hm(sp[1])} · ${Math.round(sp[1]-sp[0])}s`;
return w>=MIN_W?`<div class="seg" style="left:${X(sp[0]).toFixed(2)}%;width:${w.toFixed(2)}%" title="${t}"></div>`
:`<div class="seg mark" style="left:min(${X(sp[0]).toFixed(2)}%,calc(100% - 4px))" title="${t} (too brief to scale)"></div>`}).join("");
const evs=l.events.map(e=>{
// The call is LOGGED on completion, so a duration bar ends at e.ts and
// starts e.secs earlier — drawing it forward would plot the future.
const dur=e.leg==="gemini"&&e.secs?e.secs:0;
const x0=X(e.ts-dur),w=dur?X(e.ts)-x0:0;
const scaled=w>=MIN_W;
const cls=e.leg==="codex"?"codex":(scaled?"":"mark");
const dtxt=e.secs?`${e.secs}s`:(e.leg==="codex"?"point event":"duration not recorded");
// Marks are clamped inside the track so an event at "now" is never clipped.
const pos=scaled?`${x0.toFixed(2)}%`:`min(${X(e.ts).toFixed(2)}%,calc(100% - 7px))`;
return `<div class="ev ${cls}${e.ok?"":" fail"}" style="left:${pos}${scaled?`;width:${w.toFixed(2)}%`:""}" title="${esc(e.model)} · ${hm(e.ts)} · ${esc(e.detail)} · ${dtxt}${e.ok?"":" · FAILED"}${e.head?`&#10;${esc(e.head)}`:""}"></div>`}).join("");
return `<div class="lane"><div class="lname">${esc(l.name)}<span class="a">last ${age(now,l.last)} ago</span></div><div class="track">${segs}${evs}</div></div>`}).join("")
:'<div class="empty">no activity in this window</div>');
// Filter FIRST, then cap — so a quiet folder still shows its own history.
const feed=d.feed.filter(e=>!pf||e.project===pf).slice(0,40);
document.getElementById("feed").innerHTML="<tr><th>age</th><th>leg / model</th><th>folder</th><th>i/o</th><th class=\"num\">time</th><th>ok</th><th>said</th></tr>"+
(feed.length?feed.map(r=>`<tr><td class="dim">${age(now,r.ts)}</td>`+
`<td><span class="dot" style="background:var(--${r.leg})"></span>${esc(r.model)}</td>`+
`<td>${esc(r.project)}</td><td class="dim">${esc(r.detail)}</td>`+
`<td class="num">${r.secs?r.secs+"s":"—"}</td>`+
`<td><span class="pill ${r.ok?"ok":"bad"}">${r.ok?"ok":"FAIL"}</span></td>`+
`<td class="head">${esc(r.head)}</td></tr>`).join(""):'<tr><td class="empty" colspan="7">no leg calls in this window</td></tr>');
document.getElementById("score").innerHTML="<tr><th>model</th><th class=\"num\">calls</th><th class=\"num\">avg</th><th class=\"num\">ok</th></tr>"+
(d.score.length?d.score.map(m=>`<tr><td><span class="dot" style="background:var(--gemini)"></span>${esc(m.model)}</td>`+
`<td class="num">${m.n}</td><td class="num">${(m.secs/m.n).toFixed(1)}s</td><td class="num">${m.ok}/${m.n}</td></tr>`).join(""):'<tr><td class="empty" colspan="4">no calls yet</td></tr>');
document.getElementById("runs").innerHTML="<tr><th>age</th><th>kind</th><th>run</th><th class=\"num\">events</th><th>last</th></tr>"+
(d.runs.length?d.runs.map(r=>`<tr><td class="dim">${age(now,r.ts)}</td><td>${esc(r.kind)}</td>`+
`<td>${esc(r.name)}</td><td class="num">${r.events}</td><td>${esc(r.last)}</td></tr>`).join("")
:'<tr><td class="empty" colspan="5">no runs yet — fire /gauntlet or /adw</td></tr>');
document.getElementById("upd").textContent="updated "+new Date().toLocaleTimeString();}
async function tick(){const W=document.getElementById("win").value;
try{cur=await(await fetch("/data?window="+W)).json()}catch(e){return}
// Rebuild the folder list ONLY when it actually changed — blindly rewriting
// innerHTML every 5s slams a native dropdown shut under the operator's cursor.
const sel=document.getElementById("proj"),had=sel.value;
const names=[...new Set(cur.lanes.map(l=>l.name))];
if(sel.dataset.names!==names.join("")){sel.dataset.names=names.join("");
sel.innerHTML='<option value="">all folders</option>'+names.map(n=>`<option${n===had?" selected":""}>${esc(n)}</option>`).join("");}
render();}
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
