# Agent Memory (JARVIS brain + Claude memory dirs)

## What this source contains

- **JARVIS brain** — pgvector semantic memories + Neo4j graph facts: past decisions, preferences, project facts, prior work, stored across harnesses.
- **Claude Code auto-memory** — `~/.claude/projects/<project-slug>/memory/MEMORY.md` (an index) plus one `.md` per topic. Written during past sessions; often records *why* a setup is the way it is ("DISABLED after it closed all windows").
- **Skill memory** — per-agent `SKILL_MEMORY.md` files (see the `skill-memory` skill) and lessons logs.
- **Repo-local session notes** if present (e.g. `.claude/session-logs/`).

Memory is second-hand: an agent's summary of what happened. It is strong for "what did we decide and when", weaker as proof of the original reason.

## Probe and access

1. **JARVIS brain**
   - In pi: call the `brain_recall` tool (`query`, `limit`).
   - Elsewhere: query the server directly. Hosts in order: `$JARVIS_URL` if set, the hosts in `~/.pi/agent/kit.json` → `brain.hosts`, then `http://localhost:8000`. Auth header `X-API-Key: $JARVIS_API_KEY` (or kit.json `brain.apiKey`).
     ```bash
     curl -s -G "$HOST/brain/recall" -H "X-API-Key: $KEY" \
       --data-urlencode "query=<feature or decision>" -d limit=10 -d include_graph=true
     ```
     (`POST /brain/recall` with JSON `{query, limit, include_graph}` also works.)
   - No host answers → the brain is a gap. Say which hosts were tried.
2. **Claude memory dirs**
   ```bash
   ls ~/.claude/projects/                      # find the slug for this repo (e.g. Y--Jarvis)
   rg -n -i '<term>' ~/.claude/projects/*/memory/ --glob '*.md'
   ```
   Read `MEMORY.md` for the index line, then the full topic file.
3. **Skill memory**: `rg -n -i '<term>' --glob 'SKILL_MEMORY.md' ~ ~/.jarvis 2>/dev/null` (narrow the roots if slow).

## How to search it

- Several phrasings: the feature name, the symptom, the tool or vendor name, the person's name, the date range.
- For the brain, run 3+ queries; semantic recall misses exact terms and graph facts miss paraphrase.
- Read memory files whole; dates and "superseded" notes are usually at the top or bottom.

## What good evidence looks like

- A dated memory line that names the decision and its cause ("2026-09-07 fixed … count-based check broken by a mid-stream reconnect")
- A brain memory whose `created_at` precedes the code and states intent
- Two memories from different harnesses that agree

## Common pitfalls

- **Memory is a summary.** Mark it as such; prefer the primary source it points at, and list that source as a lead.
- **Stale memory.** Memories are not auto-corrected. Check the date and whether a later memory supersedes it.
- **Secrets.** Memory files can contain passwords and keys. Never quote them. Write "[credential redacted]".
- **Cross-project bleed.** A memory in another project's dir may describe a different system with the same name.

## What to return

For each item: store (brain / memory file path / SKILL_MEMORY path), verbatim quote, date (`created_at` or file date / blame), importance or tags if present, and the primary source it cites.
