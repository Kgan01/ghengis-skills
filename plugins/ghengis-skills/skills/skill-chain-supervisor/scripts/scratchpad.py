#!/usr/bin/env python3
"""
scratchpad.py — shared-state helper for skill-chain-supervisor chains.

Per-project state at: <project>/.claude/ghengis-chain/context.json

Project root resolution order:
1. GHENGIS_CHAIN_PROJECT_ROOT env var (explicit override)
2. Walk up from $PWD looking for .claude/ghengis-chain/
3. Walk up from $PWD looking for .claude/
4. Fallback: $PWD itself (chain dir will be created there)

Usage (from any skill's Bash context):

    python scratchpad.py read pql_validation.score
    python scratchpad.py write pql_validation.score 0.85
    echo '{"score":0.85}' | python scratchpad.py merge pql_validation
    python scratchpad.py advance
    python scratchpad.py dump
    python scratchpad.py path                    # show which file is active

    # Chain lifecycle:
    python scratchpad.py init <chain_name> [--input-json '{"user_request":"..."}']
    python scratchpad.py finish                  # archive + (optionally) emit cognition

    # Nested chain support (chain-as-stage):
    python scratchpad.py nested-start <chain_name>     # allocate <chain_name>.* subkey
    python scratchpad.py nested-finish <chain_name>    # mark nested chain complete

    # Cognition (gated by GHENGIS_COGNITION=true):
    python scratchpad.py cognition-emit          # explicit emit; finish does this automatically
    python scratchpad.py retrieve --query "..."  # UCB1+similarity ranked entries; default reads input.user_request
    python scratchpad.py audit                   # surface entries with hits>=5 and win_rate<0.4
    echo '<JSON>' | python scratchpad.py cognition-replace-last --require-id <id>
                                                  # replace last entry (used by analyzer subagent flow)

UCB1 retrieval formula (within similarity-filtered candidates):
    score = jaccard_similarity(applies_when, query) * (0.7 + 0.3 * ucb1)
    ucb1  = win_rate + sqrt(2 * ln(total_retrievals) / max(hits, 1))
    win_rate = wins / hits  (or 0.5 prior when hits=0)
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path


def resolve_project_root() -> Path:
    override = os.environ.get("GHENGIS_CHAIN_PROJECT_ROOT")
    if override:
        return Path(override)
    cwd = Path.cwd().resolve()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".claude" / "ghengis-chain").is_dir():
            return parent
        if (parent / ".claude").is_dir():
            return parent
    return cwd


def scratchpad_path() -> Path:
    return resolve_project_root() / ".claude" / "ghengis-chain" / "context.json"


def chain_dir() -> Path:
    return resolve_project_root() / ".claude" / "ghengis-chain"


def history_dir() -> Path:
    return chain_dir() / "history"


def cognition_path() -> Path:
    """Back-compat alias. Returns the per-project cognition path (default scope).

    Kept so external callers / older tests that imported this name keep working.
    New code should call `_resolve_cognition_path(scope=...)` directly.
    """
    return _resolve_cognition_path(scope="project")


_VALID_SCOPES = ("project", "global", "merged")


def _resolve_cognition_path(scope: str | None = None) -> Path:
    """Return the cognition.jsonl path for the requested scope.

    Scope precedence (highest first):
      1. Explicit `scope` arg ("project" or "global")
      2. GHENGIS_COGNITION_SCOPE env var
      3. Default: "project"

    Paths:
      project → <resolved_project_root>/.claude/cognition.jsonl
      global  → <home>/.claude/cognition.jsonl

    Creates the parent directory if missing. Does NOT create the file.
    "merged" is a retrieval-only mode and has no single file — callers must
    handle it themselves; passing "merged" to this function raises ValueError.
    """
    if scope is None:
        scope = os.environ.get("GHENGIS_COGNITION_SCOPE", "project").strip().lower()
    else:
        scope = scope.strip().lower()
    if scope == "merged":
        raise ValueError("merged is a retrieval mode, not a single file path")
    if scope not in ("project", "global"):
        raise ValueError(f"invalid scope {scope!r}; expected 'project' or 'global'")
    if scope == "global":
        path = Path.home() / ".claude" / "cognition.jsonl"
    else:
        path = resolve_project_root() / ".claude" / "cognition.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load() -> dict:
    path = scratchpad_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save(state: dict):
    path = scratchpad_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_path(state, dotted):
    parts = dotted.split(".")
    node = state
    for p in parts:
        if not isinstance(node, dict) or p not in node:
            return None
        node = node[p]
    return node


def set_path(state, dotted, value):
    parts = dotted.split(".")
    node = state
    for p in parts[:-1]:
        if p not in node or not isinstance(node[p], dict):
            node[p] = {}
        node = node[p]
    node[parts[-1]] = value


def parse_value(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def cmd_read(args):
    if not args:
        print(json.dumps(load(), indent=2))
        return 0
    value = get_path(load(), args[0])
    if value is None:
        return 1
    if isinstance(value, (dict, list)):
        print(json.dumps(value, indent=2))
    else:
        print(value)
    return 0


def cmd_write(args):
    if len(args) < 2:
        print("usage: write <dotted.key> <value>", file=sys.stderr)
        return 2
    state = load()
    set_path(state, args[0], parse_value(args[1]))
    save(state)
    return 0


def cmd_merge(args):
    """Merge a JSON object (from stdin) into a (possibly nested) subkey.

    Dotted keys are walked through to the leaf; existing keys at the leaf
    are dict-merged. Used for nested chain output: `merge build_validate.validate`
    puts the payload at state["build_validate"]["validate"].
    """
    if not args:
        print("usage: merge <dotted.subkey>  (reads JSON object from stdin)", file=sys.stderr)
        return 2
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"stdin not valid JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("stdin must be a JSON object", file=sys.stderr)
        return 2
    state = load()
    existing = get_path(state, args[0])
    if isinstance(existing, dict):
        existing.update(payload)
        set_path(state, args[0], existing)
    else:
        set_path(state, args[0], payload)
    save(state)
    return 0


def cmd_advance(args):
    state = load()
    remaining = state.get("stages_remaining", [])
    completed = state.get("stages_completed", [])
    if not remaining:
        print("no stages remaining", file=sys.stderr)
        return 1
    next_stage = remaining.pop(0)
    completed.append(state.get("current_stage", ""))
    state["stages_completed"] = [s for s in completed if s]
    state["current_stage"] = next_stage
    state["stages_remaining"] = remaining
    save(state)
    print(next_stage)
    return 0


def cmd_dump(args):
    print(json.dumps(load(), indent=2))
    return 0


def cmd_path(args):
    print(scratchpad_path())
    return 0


def cmd_init(args):
    """Bootstrap a fresh chain scratchpad. Refuses to clobber an in-flight chain."""
    parser = argparse.ArgumentParser(prog="scratchpad.py init")
    parser.add_argument("chain_name")
    parser.add_argument("--input-json", default="{}", help="JSON object for input contract")
    parser.add_argument("--force", action="store_true", help="Overwrite existing in-flight chain")
    parser.add_argument(
        "--scope", choices=["project", "global", "merged"], default=None,
        help="Cognition retrieval scope. Default: GHENGIS_COGNITION_SCOPE env or 'merged' (search project, fall back to global).",
    )
    ns = parser.parse_args(args)

    existing = scratchpad_path()
    if existing.exists() and not ns.force:
        prior = load()
        if prior.get("current_stage") and prior.get("current_stage") != "report":
            print(
                f"in-flight chain detected (current_stage={prior['current_stage']}); "
                f"archive it first with `finish` or pass --force",
                file=sys.stderr,
            )
            return 1

    try:
        input_payload = json.loads(ns.input_json)
    except json.JSONDecodeError as e:
        print(f"--input-json not valid JSON: {e}", file=sys.stderr)
        return 2

    state = {
        "chain": ns.chain_name,
        "started_at": now_iso(),
        "current_stage": "init",
        "stages_completed": [],
        "stages_remaining": [],
        "input": input_payload,
    }
    save(state)

    # Auto-retrieve relevant past lessons when cognition is enabled.
    if os.environ.get("GHENGIS_COGNITION", "").lower() in ("true", "1", "yes"):
        query = input_payload.get("user_request", "") if isinstance(input_payload, dict) else ""
        # Retrieval scope: CLI arg > env var > default "merged"
        retrieval_scope = ns.scope or os.environ.get("GHENGIS_COGNITION_SCOPE", "merged")
        if query:
            lessons = retrieve_lessons(query, top_k=5, scope=retrieval_scope)
            if lessons:
                # Bump hits in whichever store(s) the lessons came from. Group
                # ids by origin scope so we don't scan the wrong file.
                by_scope: dict[str, list[str]] = {}
                for l in lessons:
                    by_scope.setdefault(l.get("_origin_scope", "project"), []).append(l["id"])
                for sc, ids in by_scope.items():
                    _bump_counters(ids, hits_delta=1, scopes=[sc])
                state["lessons_from_past"] = lessons
                save(state)
                # Surface to stderr so the running chain operator notices
                print(
                    f"retrieved {len(lessons)} past lesson(s) into lessons_from_past "
                    f"(scope={retrieval_scope})",
                    file=sys.stderr,
                )

    print(scratchpad_path())
    return 0


def cmd_finish(args):
    """Archive scratchpad to history/ and (if enabled) emit a cognition entry."""
    parser = argparse.ArgumentParser(prog="scratchpad.py finish")
    parser.add_argument("--no-cognition", action="store_true", help="Skip cognition emission even if enabled")
    parser.add_argument("--no-archive", action="store_true", help="Skip moving to history/")
    parser.add_argument(
        "--scope", choices=["project", "global"], default=None,
        help="Where to write the cognition entry. Default: GHENGIS_COGNITION_SCOPE env or 'project'.",
    )
    ns = parser.parse_args(args)

    state = load()
    if not state:
        print("no scratchpad to finish", file=sys.stderr)
        return 1

    state["completed_at"] = now_iso()
    state["current_stage"] = "report"
    save(state)

    cognition_enabled = os.environ.get("GHENGIS_COGNITION", "").lower() in ("true", "1", "yes")
    if cognition_enabled and not ns.no_cognition:
        emit_cognition_entry(state, scope=ns.scope)
        # If the chain succeeded, bump wins on the lessons we retrieved at init.
        report = state.get("report", {}) or {}
        outcome = report.get("outcome", "")
        success_outcomes = {
            "shipped", "shipped-with-notes", "revised-and-shipped",
            "fixed", "fixed-with-notes",
            "skill-shipped", "skill-shipped-with-notes",
            "integrated", "integrated-with-notes",
        }
        if outcome in success_outcomes:
            retrieved = state.get("lessons_from_past", []) or []
            # Bump wins back in the origin scope of each retrieved lesson so
            # cross-project boosts settle in the right store.
            by_scope: dict[str, list[str]] = {}
            for r in retrieved:
                rid = r.get("id")
                if not rid:
                    continue
                by_scope.setdefault(r.get("_origin_scope", "project"), []).append(rid)
            for sc, ids in by_scope.items():
                _bump_counters(ids, wins_delta=1, scopes=[sc])

    if not ns.no_archive:
        history_dir().mkdir(parents=True, exist_ok=True)
        ts = state["completed_at"].replace(":", "").replace("-", "")[:15]
        archive = history_dir() / f"{state.get('chain', 'chain')}-{ts}.json"
        shutil.copy2(scratchpad_path(), archive)
        scratchpad_path().unlink()
        print(archive)
    else:
        print(scratchpad_path())
    return 0


def cmd_nested_start(args):
    """Allocate a top-level <chain_name> subkey for a nested chain's output."""
    if not args:
        print("usage: nested-start <chain_name>", file=sys.stderr)
        return 2
    chain_name = args[0].replace("-", "_")
    state = load()
    if chain_name in state and isinstance(state[chain_name], dict) and state[chain_name].get("_nested_status") == "running":
        print(f"nested chain {chain_name} already running", file=sys.stderr)
        return 1
    state[chain_name] = {
        "_nested_status": "running",
        "_nested_started_at": now_iso(),
    }
    save(state)
    print(chain_name)
    return 0


def cmd_nested_finish(args):
    """Mark a nested chain complete. Its output stays under <chain_name>.*"""
    if not args:
        print("usage: nested-finish <chain_name>", file=sys.stderr)
        return 2
    chain_name = args[0].replace("-", "_")
    state = load()
    if chain_name not in state or not isinstance(state[chain_name], dict):
        print(f"no nested chain {chain_name} found", file=sys.stderr)
        return 1
    state[chain_name]["_nested_status"] = "completed"
    state[chain_name]["_nested_completed_at"] = now_iso()
    save(state)
    print(chain_name)
    return 0


# ---------------------------------------------------------------------------
# Cognition retrieval (UCB1 + Jaccard relevance)
# ---------------------------------------------------------------------------

import math
import re

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have", "in", "is",
    "it", "its", "of", "on", "or", "that", "the", "this", "to", "was", "were", "will", "with",
    "i", "you", "we", "they", "he", "she", "let", "lets", "want", "need", "make", "build",
    "do", "does", "did", "what", "how", "why", "when", "use", "using", "would", "should",
}


def _tokens(text: str) -> set:
    if not text:
        return set()
    raw = re.findall(r"[a-z0-9_]+", text.lower())
    return {t for t in raw if t not in _STOPWORDS and len(t) > 2}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _read_cognition_entries(scope: str | None = None) -> list:
    """Read entries from a single scope ('project' or 'global').

    Returns [] if the file does not exist or cannot be read. Each entry is
    returned as a plain dict — no scope annotation is added here.
    """
    if scope == "merged":
        raise ValueError("_read_cognition_entries does not accept 'merged'; "
                         "use retrieve_lessons(scope='merged') instead")
    path = _resolve_cognition_path(scope=scope)
    if not path.exists():
        return []
    entries = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        return []
    return entries


def _write_cognition_entries(entries: list, scope: str | None = None):
    """Rewrite cognition.jsonl atomically (used to update hits/wins counters)."""
    path = _resolve_cognition_path(scope=scope)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, sort_keys=False) + "\n")
    tmp.replace(path)


def _ucb1_score(entry: dict, total_retrievals: int) -> float:
    """UCB1 = win_rate + sqrt(2 * ln(N) / hits). 0.5 prior when hits=0."""
    hits = max(entry.get("hits", 0), 0)
    wins = max(entry.get("wins", 0), 0)
    win_rate = (wins / hits) if hits > 0 else 0.5
    n = max(total_retrievals, 1)
    exploration = math.sqrt(2.0 * math.log(n) / max(hits, 1))
    return win_rate + exploration


def retrieve_lessons(
    query: str,
    top_k: int = 5,
    min_relevance: float = 0.08,
    scope: str | None = None,
    project_boost: float = 1.1,
) -> list:
    """Return top_k cognition entries ranked by relevance * UCB1.

    Excludes retired entries (audit_status='retired') and superseded ones.

    Scope semantics:
      - "project": search only the project cognition store
      - "global":  search only the global cognition store
      - "merged":  search project first; if it yields < top_k candidates,
                   also pull from global. Project entries get a small UCB1
                   multiplier (project_boost, default 1.1×) so they outrank
                   equal-similarity global entries.
      - None: defaults to merged behavior (the v1.19.0 default).

    Each returned entry carries an `_origin_scope` annotation ("project" or
    "global") in addition to the existing `_retrieval` block.
    """
    effective = (scope or "merged").strip().lower()
    if effective not in ("project", "global", "merged"):
        raise ValueError(f"invalid scope {effective!r}")

    if effective in ("project", "global"):
        entries = _read_cognition_entries(scope=effective)
        return _rank_entries(
            entries,
            query=query,
            top_k=top_k,
            min_relevance=min_relevance,
            origin_scope=effective,
            score_multiplier=1.0,
        )

    # Merged: project first (with boost), then global as fallback if project
    # didn't fill top_k. Dedupe by entry id (project wins on collision).
    project_entries = _read_cognition_entries(scope="project")
    project_ranked = _rank_entries(
        project_entries,
        query=query,
        top_k=max(top_k, 1) * 4,  # over-pull so we can re-rank against global
        min_relevance=min_relevance,
        origin_scope="project",
        score_multiplier=project_boost,
    )
    if len(project_ranked) >= top_k:
        return project_ranked[:top_k]

    global_entries = _read_cognition_entries(scope="global")
    global_ranked = _rank_entries(
        global_entries,
        query=query,
        top_k=max(top_k, 1) * 4,
        min_relevance=min_relevance,
        origin_scope="global",
        score_multiplier=1.0,
    )

    # Merge by score; project entries already carry the boost, so a simple
    # sort by stored _retrieval.score is correct.
    seen_ids: set[str] = set()
    merged: list[dict] = []
    for entry in (*project_ranked, *global_ranked):
        eid = entry.get("id")
        if eid in seen_ids:
            continue
        seen_ids.add(eid)
        merged.append(entry)
    merged.sort(key=lambda e: -e["_retrieval"]["score"])
    return merged[:top_k]


def _rank_entries(
    entries: list,
    *,
    query: str,
    top_k: int,
    min_relevance: float,
    origin_scope: str,
    score_multiplier: float = 1.0,
) -> list:
    """Internal: rank a single-scope entry list and annotate with origin."""
    if not entries:
        return []
    superseded_ids = set()
    for e in entries:
        for sid in e.get("supersedes", []) or []:
            superseded_ids.add(sid)
    candidates = [
        e for e in entries
        if e.get("audit_status") != "retired" and e.get("id") not in superseded_ids
    ]
    if not candidates:
        return []

    query_tokens = _tokens(query)
    total_retrievals = sum(max(e.get("hits", 0), 0) for e in entries) or 1

    ranked = []
    for e in candidates:
        applies = e.get("applies_when", "")
        relevance = _jaccard(query_tokens, _tokens(applies))
        if relevance < min_relevance:
            continue
        ucb = _ucb1_score(e, total_retrievals)
        score = relevance * (0.7 + 0.3 * ucb) * score_multiplier
        ranked.append((score, relevance, ucb, e))

    ranked.sort(key=lambda t: -t[0])
    return [
        {
            **e,
            "_retrieval": {
                "score": round(s, 4),
                "relevance": round(r, 4),
                "ucb1": round(u, 4),
            },
            "_origin_scope": origin_scope,
        }
        for s, r, u, e in ranked[:top_k]
    ]


def _bump_counters(ids: list, hits_delta: int = 0, wins_delta: int = 0,
                   scopes: list | None = None):
    """Increment hits and/or wins on cognition entries by id.

    Scopes is an optional list of ("project", "global", ...) to update. When
    omitted, both scopes are checked — bumps land wherever the id lives.
    """
    if not ids:
        return
    target = set(ids)
    scopes_to_check = scopes if scopes else ["project", "global"]
    for sc in scopes_to_check:
        entries = _read_cognition_entries(scope=sc)
        if not entries:
            continue
        changed = False
        for e in entries:
            if e.get("id") in target:
                if hits_delta:
                    e["hits"] = max(e.get("hits", 0), 0) + hits_delta
                if wins_delta:
                    e["wins"] = max(e.get("wins", 0), 0) + wins_delta
                changed = True
        if changed:
            _write_cognition_entries(entries, scope=sc)


def cmd_retrieve(args):
    """Surface relevant past lessons by UCB1 + Jaccard similarity."""
    parser = argparse.ArgumentParser(prog="scratchpad.py retrieve")
    parser.add_argument("--query", default=None, help="Query text. Default: reads input.user_request from scratchpad")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-relevance", type=float, default=0.08)
    parser.add_argument("--no-bump", action="store_true", help="Skip incrementing hits on retrieved entries")
    parser.add_argument("--write-to-scratchpad", action="store_true", help="Save retrieved entries under lessons_from_past")
    parser.add_argument(
        "--scope", choices=["project", "global", "merged"], default=None,
        help="Search scope. Default: GHENGIS_COGNITION_SCOPE env or 'merged'.",
    )
    ns = parser.parse_args(args)

    query = ns.query
    if query is None:
        state = load()
        query = (state.get("input", {}) or {}).get("user_request", "")
    if not query:
        print("no query (pass --query or set input.user_request via init)", file=sys.stderr)
        return 2

    retrieval_scope = ns.scope or os.environ.get("GHENGIS_COGNITION_SCOPE", "merged")
    lessons = retrieve_lessons(
        query, top_k=ns.top_k, min_relevance=ns.min_relevance, scope=retrieval_scope
    )
    if not lessons and ns.write_to_scratchpad:
        state = load()
        state["lessons_from_past"] = []
        save(state)

    if lessons and not ns.no_bump:
        # Bump in each lesson's origin scope.
        by_scope: dict[str, list[str]] = {}
        for l in lessons:
            by_scope.setdefault(l.get("_origin_scope", "project"), []).append(l["id"])
        for sc, ids in by_scope.items():
            _bump_counters(ids, hits_delta=1, scopes=[sc])

    if ns.write_to_scratchpad:
        state = load()
        state["lessons_from_past"] = lessons
        save(state)

    print(json.dumps(lessons, indent=2))
    return 0


def cmd_cognition_replace_last(args):
    """Replace the last line of cognition.jsonl with a JSON object from stdin.

    Used by the Analyzer subagent dispatch flow: analyzer reads scratchpad,
    produces a rewritten entry, orchestrator pipes that JSON into this command.
    Preserves all prior entries unchanged.
    """
    parser = argparse.ArgumentParser(prog="scratchpad.py cognition-replace-last")
    parser.add_argument("--require-id", help="Refuse unless the new entry has this id (safety)")
    parser.add_argument(
        "--scope", choices=["project", "global"], default=None,
        help="Which store to modify. Default: GHENGIS_COGNITION_SCOPE env or 'project'.",
    )
    ns = parser.parse_args(args)

    try:
        new_entry = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(f"stdin not valid JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(new_entry, dict):
        print("stdin must be a JSON object", file=sys.stderr)
        return 2

    path = _resolve_cognition_path(scope=ns.scope)
    if not path.exists():
        print(f"cognition.jsonl does not exist at {path}", file=sys.stderr)
        return 1

    lines = path.read_text(encoding="utf-8").splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        print("cognition.jsonl has no entries to replace", file=sys.stderr)
        return 1

    try:
        existing = json.loads(lines[-1])
    except json.JSONDecodeError:
        print("last line of cognition.jsonl is not valid JSON", file=sys.stderr)
        return 1

    if ns.require_id and existing.get("id") != ns.require_id:
        print(
            f"--require-id mismatch: last entry id is {existing.get('id')}, "
            f"expected {ns.require_id}",
            file=sys.stderr,
        )
        return 1

    # Preserve immutable fields from the existing entry that analyzer must not touch
    immutable = ("id", "created_at", "started_at", "completed_at", "hits", "wins")
    for field in immutable:
        if field in existing:
            new_entry[field] = existing[field]

    lines[-1] = json.dumps(new_entry, sort_keys=False)
    tmp = path.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp.replace(path)
    print(f"replaced last entry (id={existing.get('id')})")
    return 0


def cmd_audit(args):
    """List entries with hits>=5 and win_rate<0.4 (candidates for retirement) +
    stale entries (created>90 days ago and unused)."""
    parser = argparse.ArgumentParser(prog="scratchpad.py audit")
    parser.add_argument("--hits-threshold", type=int, default=5)
    parser.add_argument("--win-rate-threshold", type=float, default=0.4)
    parser.add_argument(
        "--scope", choices=["project", "global"], default=None,
        help="Which store to audit. Default: GHENGIS_COGNITION_SCOPE env or 'project'.",
    )
    ns = parser.parse_args(args)

    entries = _read_cognition_entries(scope=ns.scope)
    if not entries:
        print("no cognition entries", file=sys.stderr)
        return 0

    flagged = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for e in entries:
        hits = max(e.get("hits", 0), 0)
        wins = max(e.get("wins", 0), 0)
        win_rate = (wins / hits) if hits > 0 else None
        try:
            created = datetime.datetime.fromisoformat(e.get("created_at", "").replace("Z", "+00:00"))
            age_days = (now - created).days
        except ValueError:
            age_days = None

        reasons = []
        if hits >= ns.hits_threshold and win_rate is not None and win_rate < ns.win_rate_threshold:
            reasons.append(f"low win_rate ({win_rate:.2f}) after {hits} hits")
        if hits == 0 and age_days is not None and age_days >= 90:
            reasons.append(f"unused for {age_days} days")
        if reasons:
            flagged.append({"id": e.get("id"), "chain": e.get("chain"), "lesson": e.get("lesson"), "reasons": reasons})

    print(json.dumps({"flagged": flagged, "total_entries": len(entries)}, indent=2))
    return 0


def emit_cognition_entry(state: dict, scope: str | None = None) -> dict:
    """Build a cognition entry from chain state and append to cognition.jsonl.

    Scope follows the precedence in `_resolve_cognition_path` — default
    'project', overridable via GHENGIS_COGNITION_SCOPE env var or explicit
    arg. Returns the entry that was written.
    """
    chain_name = state.get("chain", "unknown")
    started = state.get("started_at", "")
    completed = state.get("completed_at", now_iso())
    report = state.get("report", {}) or {}
    outcome = report.get("outcome", "unknown")
    score = report.get("score_progression", [])
    final_score = score[-1] if isinstance(score, list) and score else None

    # Heuristic lesson extraction: outcome string + any issues from validate stage(s)
    validate = state.get("validate", {}) or state.get("build_validate", {}).get("validate", {}) or {}
    issues = validate.get("issues", []) if isinstance(validate, dict) else []
    issues_text = "; ".join(issues[:3]) if issues else "no issues raised"

    # Stable id from chain name + completed_at
    raw_id = f"{chain_name}|{completed}"
    entry_id = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]

    fitness = None
    if isinstance(final_score, (int, float)):
        fitness = float(final_score) / 10.0

    entry = {
        "id": entry_id,
        "created_at": now_iso(),
        "chain": chain_name,
        "outcome": outcome,
        "final_score": final_score,
        "fitness": fitness,
        "lesson": _derive_lesson(chain_name, outcome, issues),
        "causal_factor": issues_text,
        "applies_when": _derive_applies_when(chain_name, state),
        "started_at": started,
        "completed_at": completed,
        "iterations_used": state.get("iterations_used"),
        "hits": 0,
        "wins": 0,
        "audit_status": "unchecked",
    }
    path = _resolve_cognition_path(scope=scope)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=False) + "\n")
    return entry


def _derive_lesson(chain: str, outcome: str, issues: list) -> str:
    """Generate a short lesson string from outcome + issues. Heuristic, not LLM."""
    if outcome in ("shipped", "fixed", "skill-shipped", "integrated"):
        return f"{chain} succeeded cleanly on first or revised iteration"
    if outcome in ("shipped-with-notes", "fixed-with-notes", "skill-shipped-with-notes", "integrated-with-notes"):
        return f"{chain} succeeded but surfaced notes worth tracking"
    if outcome in ("revised-and-shipped",):
        return f"{chain} required revision loop; iteration 2 succeeded"
    if outcome in ("quality-gap-flagged", "fix-incomplete", "skill-incomplete"):
        return f"{chain} hit max iterations without reaching success threshold"
    if outcome in ("cannot-reproduce", "needs-redesign", "needs-decomposition", "tests-failing"):
        return f"{chain} exited early at {outcome}; precondition not satisfied"
    if outcome in ("kept-as-is", "discarded"):
        return f"{chain} ended without integration ({outcome})"
    return f"{chain} ended with outcome {outcome}"


def _derive_applies_when(chain: str, state: dict) -> str:
    """Build an embedding target describing the situation the chain ran in."""
    parts = [chain]
    input_obj = state.get("input", {})
    if isinstance(input_obj, dict):
        req = input_obj.get("user_request", "")
        if req:
            parts.append(str(req)[:160])
        dtype = input_obj.get("deliverable_type", "")
        if dtype:
            parts.append(f"deliverable:{dtype}")
    return " | ".join(parts)


def cmd_cognition_emit(args):
    """Explicitly emit a cognition entry from the current scratchpad."""
    parser = argparse.ArgumentParser(prog="scratchpad.py cognition-emit")
    parser.add_argument("--scope", choices=["project", "global"], default=None,
                        help="Where to write. Default: GHENGIS_COGNITION_SCOPE env or 'project'.")
    ns = parser.parse_args(args)
    state = load()
    if not state:
        print("no scratchpad to emit from", file=sys.stderr)
        return 1
    entry = emit_cognition_entry(state, scope=ns.scope)
    print(json.dumps(entry, indent=2))
    return 0


def cmd_cognition_promote(args):
    """Move a cognition entry from the project store to the global library.

    The project entry is NOT deleted — it's marked with `promoted_to_global: true`
    to preserve the local audit trail. The global copy gains
    `promoted_from_project: <project_root>` and `promoted_at: <iso8601>` stamps.

    Errors:
      - entry_id not found in project store
      - entry already has `promoted_to_global: true`
    """
    parser = argparse.ArgumentParser(prog="scratchpad.py cognition-promote")
    parser.add_argument("entry_id")
    ns = parser.parse_args(args)

    project_path = _resolve_cognition_path(scope="project")
    if not project_path.exists():
        print(f"no project cognition store at {project_path}", file=sys.stderr)
        return 1

    project_entries = _read_cognition_entries(scope="project")
    target = None
    for e in project_entries:
        if e.get("id") == ns.entry_id:
            target = e
            break
    if target is None:
        print(
            f"entry_id {ns.entry_id!r} not found in project store ({project_path})",
            file=sys.stderr,
        )
        return 1
    if target.get("promoted_to_global") is True:
        print(
            f"entry_id {ns.entry_id!r} already has promoted_to_global=true",
            file=sys.stderr,
        )
        return 1

    # Build the global copy. Use a fresh dict so we don't mutate the project entry.
    promoted = dict(target)
    promoted["promoted_from_project"] = str(resolve_project_root())
    promoted["promoted_at"] = now_iso()

    global_path = _resolve_cognition_path(scope="global")
    global_path.parent.mkdir(parents=True, exist_ok=True)
    with global_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(promoted, sort_keys=False) + "\n")

    # Mark the project entry. Atomic rewrite via _write_cognition_entries.
    for e in project_entries:
        if e.get("id") == ns.entry_id:
            e["promoted_to_global"] = True
            e["promoted_at"] = promoted["promoted_at"]
            break
    _write_cognition_entries(project_entries, scope="project")

    print(json.dumps({
        "promoted": ns.entry_id,
        "project_path": str(project_path),
        "global_path": str(global_path),
    }, indent=2))
    return 0


COMMANDS = {
    "read": cmd_read,
    "write": cmd_write,
    "merge": cmd_merge,
    "advance": cmd_advance,
    "dump": cmd_dump,
    "path": cmd_path,
    "init": cmd_init,
    "finish": cmd_finish,
    "nested-start": cmd_nested_start,
    "nested-finish": cmd_nested_finish,
    "cognition-emit": cmd_cognition_emit,
    "cognition-promote": cmd_cognition_promote,
    "cognition-replace-last": cmd_cognition_replace_last,
    "retrieve": cmd_retrieve,
    "audit": cmd_audit,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"usage: {sys.argv[0]} <{'|'.join(COMMANDS)}> [args]", file=sys.stderr)
        return 2
    return COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
