# Ghengis Skills V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract and adapt 25 skills from the JARVIS system into a Claude Code plugin package.

**Architecture:** Skills are markdown files with YAML frontmatter. Each skill directory contains a SKILL.md (main skill) and optionally supporting docs. The plugin follows the superpowers pattern (.claude-plugin/, skills/, hooks/, agents/).

**Tech Stack:** Markdown, YAML frontmatter, Claude Code plugin system

---

## Source Mapping

### Agentic Engineering (from Python code — need new SKILL.md creation)
| Skill | Source |
|-------|--------|
| oort-cascade | `agents/oort.py` + `skills/upskill/oort/*.md` (6 files) |
| meta-prompting | `agents/meta_prompts.py` (22 role templates) |
| agent-teams | `agents/agent_teams.py` (parallel perspectives + synthesis) |
| pql-validation | `agents/prompt_validator.py` (35 anti-patterns, 6 categories) |
| blueprint-compilation | `agents/blueprint.py` + `blueprint_engine.py` + `blueprint_compiler.py` |
| constitutional-ai | `agents/constitution.py` (9 rules, 5 categories) |

### Domain Skills (from existing SKILL.md — adapt format)
| Skill | Source |
|-------|--------|
| general-research | `skills/upskill/web-research/SKILL.md` + `brain/deep_research.py` |
| bookkeeping | `skills/upskill/bookkeeping/SKILL.md` |
| task-tracking | `skills/upskill/task-tracking/SKILL.md` |
| learning-paths | `skills/upskill/learning-paths/SKILL.md` |
| tutoring | `skills/upskill/tutoring/SKILL.md` |
| shopping | `skills/upskill/shopping/SKILL.md` |
| report-writing | `skills/upskill/report-writing/SKILL.md` |
| scheduling | `skills/upskill/scheduling/SKILL.md` |
| mcp-patterns | `skills/upskill/tooling/mcp-patterns.md` |
| data-analysis | `skills/upskill/data-analysis/SKILL.md` |
| content-writing | `skills/upskill/content-writing/SKILL.md` |
| devops | `skills/upskill/devops/SKILL.md` |
| music-curation | `skills/upskill/music-curation/SKILL.md` |
| home-lighting | `skills/upskill/home-lighting/SKILL.md` |
| 3d-modeling | `skills/upskill/3d-modeling/SKILL.md` |

### Framework Skills (from existing markdown — adapt format)
| Skill | Source |
|-------|--------|
| react-nextjs | `skills/upskill/frameworks/react-nextjs.md` |
| fastapi | `skills/upskill/frameworks/fastapi.md` |
| flutter-dart | `skills/upskill/frameworks/flutter-dart.md` |
| esp32 | `skills/upskill/frameworks/platformio-esp32.md` |

## Transformation Rules

1. **Frontmatter**: Add `name` and `description` fields that tell Claude WHEN to activate
2. **Reframe**: Change from "teach a cheap model" to "guide Claude Code session behavior"
3. **De-JARVIS**: Replace JARVIS tool references with generic equivalents (e.g., `browse` → "use browser automation", `web_search` → "use WebSearch tool")
4. **Keep knowledge**: The domain expertise, patterns, and anti-patterns are the core value
5. **Add gates**: For rigid skills (OORT, PQL, Constitutional), add enforcement language and red flags tables
6. **Standalone**: Each skill must work without the JARVIS server running

---

## Task 1: Agentic Engineering Core — OORT Cascade

**Files:**
- Create: `skills/oort-cascade/SKILL.md`
- Create: `skills/oort-cascade/handoff-protocol.md`
- Create: `skills/oort-cascade/quality-gates.md`

Extract from: `agents/oort.py`, `skills/upskill/oort/cascade-methodology.md`, `skills/upskill/oort/handoff-protocol.md`, `skills/upskill/oort/quality-gates.md`, `skills/upskill/oort/validation-loops.md`

- [ ] Read all OORT source files
- [ ] Create SKILL.md with: cascade decomposition methodology, DAG dependency patterns, wave execution, when to cascade vs handle directly, revision loops, role contracts
- [ ] Create handoff-protocol.md: structured data passing between roles
- [ ] Create quality-gates.md: validation scoring, revision triggers, E2E checks

---

## Task 2: Agentic Engineering Core — Meta-Prompting

**Files:**
- Create: `skills/meta-prompting/SKILL.md`

Extract from: `agents/meta_prompts.py` (22 role templates + MetaPromptBuilder)

- [ ] Read meta_prompts.py
- [ ] Create SKILL.md with: role template system, 22 role definitions (generalized), dependency context injection, revision context, department routing logic
- [ ] Generalize from JARVIS-specific to universal agent orchestration

---

## Task 3: Agentic Engineering Core — Agent Teams

**Files:**
- Create: `skills/agent-teams/SKILL.md`

Extract from: `agents/agent_teams.py` (parallel perspectives + synthesis)

- [ ] Read agent_teams.py
- [ ] Create SKILL.md with: perspective diversity pattern, parallel execution, synthesis methodology, default perspectives (Minimalist/Bold/Technical/Playful/Elegant), when to use teams vs single agent

---

## Task 4: Agentic Engineering Core — PQL Validation

**Files:**
- Create: `skills/pql-validation/SKILL.md`
- Create: `skills/pql-validation/anti-patterns.md`

Extract from: `agents/prompt_validator.py` (35 patterns), `agents/prompt_templates.py` (12 frameworks), `agents/token_auditor.py`

- [ ] Read all PQL source files
- [ ] Create SKILL.md with: prompt quality principles, 6 categories, when to validate, auto-fix patterns
- [ ] Create anti-patterns.md with: all 35 anti-patterns, each with pattern name, category, severity, what it catches, suggestion

---

## Task 5: Agentic Engineering Core — Blueprint Compilation

**Files:**
- Create: `skills/blueprint-compilation/SKILL.md`

Extract from: `agents/blueprint.py`, `agents/blueprint_engine.py`, `agents/blueprint_compiler.py`

- [ ] Read all blueprint source files
- [ ] Create SKILL.md with: trace recording methodology, pattern detection, compilation from trace to reusable pipeline, when to compile vs ad-hoc

---

## Task 6: Agentic Engineering Core — Constitutional AI

**Files:**
- Create: `skills/constitutional-ai/SKILL.md`

Extract from: `agents/constitution.py` (9 rules, 5 categories, pre/post checks)

- [ ] Read constitution.py
- [ ] Create SKILL.md with: 5 rule categories, 9 constitutional rules (generalized), pre-execution checks, post-execution checks, signal-based enforcement patterns

---

## Tasks 7-21: Domain & Framework Skills

Each follows the same pattern:
- [ ] Read source SKILL.md from JARVIS
- [ ] Transform frontmatter (add name + description for Claude Code triggering)
- [ ] Remove JARVIS-specific tool references
- [ ] Keep all domain knowledge intact
- [ ] Write to new location

Skills: general-research, bookkeeping, task-tracking, learning-paths, tutoring, shopping, report-writing, scheduling, mcp-patterns, data-analysis, content-writing, devops, music-curation, home-lighting, 3d-modeling, react-nextjs, fastapi, flutter-dart, esp32

---

## Task 22: Eval System

**Files:**
- Create: `evals/README.md` (eval format specification)
- Create: one eval per skill (25 files)

- [ ] Define eval format (based on JARVIS EVAL.md pattern)
- [ ] Create evals for agentic engineering skills
- [ ] Create evals for domain skills

---

## Task 23: Final Review

- [ ] Verify all 25 skills have SKILL.md
- [ ] Verify all frontmatter has name + description
- [ ] Verify no JARVIS-specific tool references remain
- [ ] Test plugin loads in Claude Code
