---
name: system-scaffold
description: Use when reorganizing a Windows computer system-wide (multiple drives, mixed content) — walks all connected drives, classifies content by tier, lets user correct classifications, and produces a distributed CONTEXT.md scaffold plus a master INDEX.md, plus an opt-in move plan with treefile-organizer-style safety. Plan-first; never moves a file without explicit user confirmation. Status — v0, Stage 1 (scanner) only. TRIGGER on "organize this computer", "clean up my drives", "where does everything live", or "build the system index".
allowed-tools: Read Write Edit Bash Glob Grep
---

# System Scaffold

Reshape a computer's filesystem to match how its content is actually used, not where files happened to land. Plan-first, validate-before-execute, never move a file without explicit user confirmation. Computer-wide analog of `treefile-organizer`.

## Status

**v0 — under construction.** Currently only Stage 1 (Scanner) is implemented. Stages 2-7 are planned. See design doc at `<jarvis-root>/docs/system-scaffold-design.md` for the full architecture.

## When to Use

- Multiple connected drives with no consistent taxonomy
- C drive critically full while other drives sit empty
- User wants Jarvis (or any AI assistant) to know where files live without re-scanning every time
- User asks "where does X live?" or "what's on this drive?"

## When NOT to Use

- Single project file-tree cleanup → use `treefile-organizer`
- Greenfield project layout → use `project-scaffold`
- File naming / surface conventions only → use `file-organization`
- Code-internal reorganization → use `treefile-organizer`

## Scope (v1)

| Platform | Support |
|---|---|
| Windows 10/11 | Full (v1) |
| macOS | Architecture-ready, not implemented |
| Linux | Out of scope |

## 7-Stage Pipeline (planned)

1. **SCAN** — walk drives, build inventory (this stage exists)
2. **CLASSIFY** — apply built-in taxonomy, score confidence (not yet)
3. **INTERVIEW** — ask user only about uncertain items + drive purposes (not yet)
4. **MAP DEPENDENCIES** — Windows-specific: registry, junctions, .lnk targets (not yet)
5. **PLAN** — propose moves based on classifications + drive purposes (not yet)
6. **WRITE SCAFFOLD** — generate distributed CONTEXT.md + master INDEX.md (not yet)
7. **EXECUTE** (opt-in) — copy→verify→delete with per-batch rollback (not yet)

## Stage 1 — Scanner usage

```bash
python <skill_dir>/scripts/scanner.py [--drives C,Y,Z] [--max-depth 8] [--output <path>]
```

Defaults: scan all connected fixed drives, max depth 8 with size-aware descent, output to `C:\Users\<user>\.system\runs\<timestamp>\inventory.json`.

## Refusal Conditions

This skill MUST refuse to proceed when:
- Not running on Windows (until macOS adapter is implemented)
- User asks for moves without first completing Stages 1-6 and reviewing the plan
- Any drive in scope is not currently mounted

## Cross-References

- `treefile-organizer` — project-scoped analog
- `project-scaffold` — per-project layout templates
- `file-organization` — surface naming and manifest concerns
