---
name: project-scaffold
description: Use when starting a new project or organizing an existing one — creates self-documenting 4-layer project structure with MEMORY.md, CONTEXT.md, modular CLAUDE.md, and workspace routing
allowed-tools: Read Write Edit Bash(mkdir *) Glob
---

# Project Scaffold (Van Clief 4-Layer Structure)

## When This Applies

Starting a new project from scratch, organizing an existing project that lacks structure, or retrofitting Claude Code configuration into a project missing `.claude/` setup.

## Process

Follow these steps in order when this skill is invoked.

### Step 1 — Gather Requirements

Ask the user:
1. **What type of project?** (code / client / service / hardware / research / business)
2. **Project name and one-line description?**
3. **What is the goal?** (one sentence)
4. **Client name?** (only for client/service types)
5. **Primary languages/frameworks?** (determines which `.claude/rules/` files to generate)

If the user provides enough context to infer these answers, skip the questions and proceed.

### Step 2 — Choose Project Type

Each type defines its workspace directories and canonical files:

| Type | Label | Workspaces | Key Files |
|------|-------|-----------|-----------|
| **code** | Software Project | `src/`, `tests/`, `docs/` | `.env.example` |
| **client** | Client Project | `src/`, `client/`, `deliverables/`, `docs/` | `client/CONTRACT.md`, `client/COMMUNICATION.md` |
| **service** | API/Microservice | `src/`, `infrastructure/`, `client/`, `docs/` | `infrastructure/ARCHITECTURE.md`, `DEPLOYMENT.md`, `RUNBOOK.md`, `docs/HANDOFF.md` |
| **hardware** | Firmware/Electronics | `firmware/`, `schematics/`, `stl/`, `docs/` | `docs/BOM.md` |
| **research** | Research Project | `research/`, `experiments/`, `docs/` | `docs/THESIS.md` |
| **business** | Business/Revenue | `pipeline/`, `operations/`, `finances/`, `docs/` | `pipeline/LEADS.md`, `operations/PRICING.md`, `finances/REVENUE.md` |

### Step 3 — Generate Layer 0 (MEMORY.md)

The "DNS of the project." Always read first by any agent or session. Target ~800 tokens.

```markdown
# {Project Name}

> {One-line description}

**Type:** {Project Type Label}
**Stage:** IDEA
**Goal:** {Goal statement}
**Client:** {Client name, if applicable}
**Created:** {YYYY-MM-DD}

## Folder Map

- `src/` — Source code
- `tests/` — Test suite
- `docs/` — Documentation and plans

## Conventions

- Project slug: `{slugified-name}`
- Canonical sources are marked with `(canonical)` in CONTEXT.md files
- Dependencies flow one way only (see CONTEXT.md for routing)

## Current State

- Stage: IDEA
- Blockers: none
- Next action: Review CONTEXT.md and begin work
```

### Step 4 — Generate Layer 1 (CONTEXT.md)

The "routing table." Pure task-to-workspace mapping. Target ~300 tokens. Does NO work itself.

```markdown
# Project Routing

> This file routes tasks to the right workspace.
> Read this once per session. Do not perform work here.

## Task Routing

| Task related to source code | -> `src/` |
| Task related to test suite | -> `tests/` |
| Task related to documentation | -> `docs/` |

## Rules

1. Every fact lives in ONE file (canonical source). Never duplicate.
2. Dependencies flow one way. If A references B, B must not reference A.
3. Load specific sections, not entire files. See workspace CONTEXT.md for guidance.
```

### Step 5 — Generate Layer 2 (workspace/CONTEXT.md files)

Each workspace gets its own CONTEXT.md (200-500 tokens) specifying:
- When to route here
- What to load when working in this workspace
- Key files with their canonical designations

Example for `src/CONTEXT.md`:
```markdown
## Workspace: src/

Code implementation lives here.

### When to route here
- Writing, reading, or modifying code
- Debugging or fixing bugs
- Adding features

### What to load
- README.md (if exists)
- Relevant source files by task
- tests/ for related test files
```

### Step 6 — Generate .claude/ Directory

Every scaffolded project gets a `.claude/` directory for Claude Code integration.

```
project/
├── MEMORY.md              # Layer 0 — project identity
├── CONTEXT.md             # Layer 1 — workspace routing
├── .claude/
│   ├── CLAUDE.md          # Modular, <150 lines, @ includes
│   ├── docs/              # Referenced documentation
│   ├── rules/             # Language/domain rules
│   └── settings.json      # Permission configuration
└── [workspaces]/
    └── CONTEXT.md         # Layer 2 — per-workspace guidance
```

**CLAUDE.md format rules:**
- Keep under 150 lines total
- Use `@.claude/docs/<topic>.md` includes for detailed content
- Never inline content longer than 3 lines — it belongs in a referenced doc
- One fact, one place — cross-reference instead of duplicating
- Update counts when agents/tools/modules change

Example CLAUDE.md:
```markdown
# {Project Name}

> {One-line description}. **{Language/framework}.**

## Documentation

@.claude/docs/architecture.md
@.claude/docs/conventions.md

## Quick Commands

```bash
# start dev server
npm run dev

# run tests
npm test
```

## Key Files

1. `src/index.ts` — Entry point
2. `MEMORY.md` — Project identity (read first)
3. `CONTEXT.md` — Workspace routing
```

### Step 7 — Generate .claude/rules/ Files

Based on detected or specified languages/frameworks, generate relevant rule files:

- **Python projects:** `.claude/rules/python.md` — type hints, pathlib, async patterns, logging
- **TypeScript projects:** `.claude/rules/typescript.md` — strict mode, interfaces, const defaults, nullish coalescing
- **Dart/Flutter projects:** `.claude/rules/flutter.md` — widget conventions, state management, platform channels
- **C++/Firmware projects:** `.claude/rules/firmware.md` — memory allocation, ISR safety, task pinning
- **All projects:** `.claude/rules/tests.md` — test isolation, descriptive names, specific assertions

### Step 8 — Handle Existing Projects (Cautious Retrofit)

When scaffolding into an existing project:

1. **Scan** for existing MEMORY.md, CONTEXT.md, .claude/ directory
2. **Never overwrite** existing files — only fill gaps
3. **Preserve** any existing structure that already serves the same purpose
4. **Report** what was created vs. what was skipped (with reasons)
5. **Suggest** improvements to existing files without modifying them

## Project Lifecycle Stages

Projects progress through these stages (update MEMORY.md as they advance):

1. **IDEA** — Concept, not started
2. **PLANNING** — Scoping, designing
3. **ACTIVE** — In development / execution
4. **REVIEW** — Client review or QA
5. **DELIVERED** — Handed off to client
6. **MAINTENANCE** — Ongoing support
7. **ARCHIVED** — No longer active

## Key Principles

- **Canonical sources**: every fact lives in ONE place, marked with `(canonical)`
- **One-way dependencies**: A can reference B, but B must never reference A back
- **Selective loading**: load specific sections of files, never dump entire files into context
- **Layer discipline**: MEMORY.md is identity, CONTEXT.md is routing, workspace CONTEXT.md is guidance, content files are the work
- **Token budgets**: Layer 0 ~800 tokens, Layer 1 ~300 tokens, Layer 2 200-500 tokens each
