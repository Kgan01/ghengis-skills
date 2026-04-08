---
name: skill-memory
description: Use to accumulate and retrieve domain knowledge from past tasks — builds a grepable plain-text knowledge base that grows over time, enabling agents to learn from experience without vector databases
---

# Skill Memory (Grepable Knowledge Base)

## When This Applies

After completing non-trivial tasks, discovering non-obvious patterns, or encountering pitfalls that future sessions should avoid. This skill defines how to accumulate, organize, retrieve, and maintain a plain-text knowledge base that grows over time.

## The Core Insight

Plain text beats infrastructure for agent knowledge. A well-structured markdown file is:
- **Free** to query (grep, not vector search)
- **Instant** to read (< 1ms, not network round-trip)
- **Offline-capable** (no database, no API)
- **Already in context** (the file IS the knowledge)
- **Auditable** (human-readable, git-trackable)

No vector database. No embeddings. No RAG pipeline. Just structured markdown files searchable via grep.

## What to Record

### Record These (Transferable Knowledge)

**Lessons learned** — Things that went wrong and how they were fixed:
- "SQLite WAL mode must be enabled before concurrent reads work"
- "FastAPI dependency injection doesn't work with classmethods"

**Patterns discovered** — Reusable approaches that worked:
- "For large file processing, streaming chunks through a generator avoids OOM"
- "TypeScript discriminated unions eliminate the need for type guards in switch statements"

**Pitfalls encountered** — Traps to avoid next time:
- "Don't use `datetime.now()` without timezone — always use `datetime.now(timezone.utc)`"
- "React useEffect with empty deps still runs on mount — not truly 'never'"

**Successful approaches** — What worked and why:
- "Using dataclasses with `__post_init__` for validation keeps models clean"
- "Parallel tool execution via asyncio.gather cut response time 3x"

**Environment specifics** — Setup details that took effort to discover:
- "macOS Ventura requires explicit camera permission even for CLI tools"
- "Node 20 changed the default fetch implementation — check for subtle differences"

### Do NOT Record These

- Routine operations (standard CRUD, simple file reads)
- Temporary state (current branch name, in-progress variable names)
- User-specific secrets or credentials
- Task-specific details that won't transfer to future tasks
- Information already well-documented in official docs (don't duplicate MDN or Python docs)

## Entry Format

Each knowledge entry follows a consistent structure for grepability:

```markdown
### 2026-04-07 14:30
- [python/async] asyncio.gather swallows exceptions by default — use return_exceptions=True to surface them
- [react/hooks] useCallback with object dependencies triggers infinite re-renders — memoize the object first
```

### Format Rules

1. **Timestamp header** — `### YYYY-MM-DD HH:MM` (UTC). Enables chronological grep and staleness detection
2. **Tag prefix** — `[domain/topic]` at the start of each bullet. Enables scoped grep (e.g., grep for `[python/` to find all Python learnings)
3. **One line per learning** — Complete thought in a single line. No multi-line entries (breaks grep)
4. **Dash prefix** — Every learning starts with `- `. Consistent format for parsing
5. **Actionable language** — State what to DO or AVOID, not what happened. "Use X" or "Avoid Y", not "We encountered an issue with Z"

### Tag Taxonomy

Use two-level tags: `[domain/topic]`

Common domains:
- `[python/...]` `[typescript/...]` `[rust/...]` — Language-specific
- `[react/...]` `[fastapi/...]` `[nextjs/...]` — Framework-specific
- `[git/...]` `[docker/...]` `[ci/...]` — Tooling
- `[architecture/...]` — Design patterns and system design
- `[debugging/...]` — Diagnostic techniques
- `[performance/...]` — Optimization insights
- `[security/...]` — Security-relevant findings

## File Structure

Knowledge lives in a single markdown file per domain or project:

```markdown
# Skill Memory: {domain or project name}

Learned knowledge from past tasks.

### Consolidated Learnings (auto-summarized)
- [python/async] Always use return_exceptions=True with asyncio.gather
- [react/state] Avoid derived state in useState — compute in render instead
- [git/workflow] Rebase before merge to keep history linear

### 2026-04-07 14:30
- [python/pathlib] Path.is_relative_to() was added in Python 3.9 — check version before using
- [fastapi/deps] Dependency overrides only work in the same event loop — test fixtures need async

### 2026-04-06 10:15
- [docker/build] Multi-stage builds with --target cut image size 60% for Python apps
```

## When to Write

**Write after:**
- Completing a task that required non-obvious problem-solving
- Discovering a pitfall that cost significant debugging time
- Finding an approach that was notably more effective than the obvious one
- Encountering a version-specific behavior or breaking change
- Resolving an error that had a non-obvious root cause

**Do NOT write after:**
- Routine operations that went smoothly
- Tasks that followed well-known patterns
- Simple lookups or one-off answers
- Mid-task (wait until the task completes to know what actually mattered)

### Write Trigger Checklist

Before writing a knowledge entry, it must pass at least one:
- [ ] Would this save 10+ minutes if encountered again?
- [ ] Is this NOT in the first page of official documentation?
- [ ] Did this require multiple attempts or debugging cycles to discover?
- [ ] Would a different approach have been significantly better?

## Auto-Consolidation

When the knowledge base grows too large, compress old entries while preserving value.

### Size Thresholds

- **Under 10KB** — No action needed
- **10-50KB** — Deduplicate similar entries (see below)
- **Over 50KB** — Summarize old entries, keep recent ones verbatim

### Deduplication

When entries are similar (85%+ text similarity), keep only the more recent version:

1. Compare all bullet points pairwise within the file
2. If two entries are 85%+ similar by character sequence matching, drop the older one
3. Log what was removed so nothing is silently lost

### Summarization

When the file exceeds 50KB:

1. Split into header + timestamped sections
2. Keep the 5 most recent sections verbatim (freshest knowledge)
3. Summarize all older sections into 5-10 key bullet points
4. Write the summary as a "Consolidated Learnings (auto-summarized)" section
5. Remove the original old sections

### Staleness

Entries older than 90 days with no consolidated summary are candidates for removal. Technology moves fast — a Python 3.9 workaround may not apply to 3.12.

## Cross-Domain Search

The grepable format enables searching across multiple knowledge files without infrastructure:

### Search Patterns

**Find all knowledge about a topic:**
Search for the tag prefix across all skill memory files.
Example: Search for `[python/async]` finds every async-related learning regardless of which project generated it.

**Find knowledge relevant to a current error:**
Search for key terms from the error message.
Example: An error mentioning "event loop" — search for `event.loop` or `asyncio` across all files.

**Find knowledge from a specific time period:**
Search for the date prefix.
Example: Search for `### 2026-04` finds all April 2026 learnings.

### Search Priority

When looking for relevant knowledge:
1. Search the current project's skill memory first
2. Search related domain files second (same language/framework)
3. Search all files last (broadest, may include noise)

## Mapping to Claude Code's Memory System

Skill memory maps to Claude Code's persistent memory:

**For high-value learnings (save 30+ minutes if forgotten):**
Write as a Claude Code user memory. These persist across all sessions.
Example: "In this codebase, the auth middleware must be registered before route handlers or 401s are silent"

**For project-specific knowledge:**
Store in the project's MEMORY.md or a dedicated knowledge section.
These persist for anyone working on the project.

**For domain knowledge (transferable across projects):**
Store in a domain-level skill memory file.
Example: `~/.claude/skill-memory/python.md` for Python-specific learnings.

**For session-specific findings (not yet confirmed as durable):**
Hold in working memory during the session. Only persist after confirming the finding held up.

## Practical Example

After debugging a complex async issue:

```markdown
### 2026-04-07 16:45
- [python/async] When using asyncio.TaskGroup, unhandled exceptions in one task cancel ALL sibling tasks — wrap each task in try/except if partial failure is acceptable
- [python/async] TaskGroup.__aexit__ re-raises the first exception as ExceptionGroup — use except* (PEP 654) to handle individual exceptions from the group
- [debugging/async] When async tests hang, check for unawaited coroutines — pytest-asyncio strict mode catches these at collection time
```

Each entry is: tagged, one-line, actionable, and grepable. Six months from now, searching for `[python/async]` or `TaskGroup` surfaces exactly this knowledge.
