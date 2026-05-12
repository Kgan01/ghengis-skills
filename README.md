<div align="center">

```
   ██████╗ ██╗  ██╗███████╗███╗   ██╗ ██████╗ ██╗███████╗
  ██╔════╝ ██║  ██║██╔════╝████╗  ██║██╔════╝ ██║██╔════╝
  ██║  ███╗███████║█████╗  ██╔██╗ ██║██║  ███╗██║███████╗
  ██║   ██║██╔══██║██╔══╝  ██║╚██╗██║██║   ██║██║╚════██║
  ╚██████╔╝██║  ██║███████╗██║ ╚████║╚██████╔╝██║███████║
   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚══════╝
                     S K I L L S
```

[![Skills](https://img.shields.io/badge/skills-55-blue?style=for-the-badge)](./plugins/ghengis-skills/skills/)
[![Evals](https://img.shields.io/badge/evals-42-green?style=for-the-badge)](./plugins/ghengis-skills/evals/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-orange?style=for-the-badge)](https://code.claude.com)
[![License](https://img.shields.io/badge/license-MIT-purple?style=for-the-badge)](./LICENSE)

**Make Claude smarter, faster, and more autonomous.**

*55 skills covering evolving cognition, paper-to-code research translation, multi-agent orchestration, prompt quality validation, agent reliability, security testing, code intelligence, and domain expertise across 20+ fields. Includes an autoloader that forces relevant skills to fire automatically — same pattern as superpowers.*

---

</div>

Skills are lightweight — they load on-demand and don't bloat your context window. Unlike MCP servers that inject tool schemas into every message, skills activate only when relevant, adding zero overhead the rest of the time.

## What's New (v1.8.1)

- **Time Perception (`time-perception`)** — Gives Claude a persistent sense of time. `UserPromptSubmit` hook injects elapsed time, message count, and project-switch detection into every prompt. `Stop` hook logs task durations. Includes a portable Python module (`time_context.py`) for wrapping any LLM API with time awareness.
- **Agent Monitor (`agent-monitor`)** — Real-time subagent dashboard and terminal status line. Auto-opens a browser dashboard (ports 7685/7686) when 2+ agents are running. Tracks agent lifecycle, project grouping, permissions, and cross-session history. Status line shows model name + color-coded context usage bar.

## Previous (v1.7.0)

- **Evolving Cognition (`evolving-cognition`)** — ASI-Evolve-inspired pattern for agents that learn from measurable outcomes. Covers fitness signal design, cognition store schema, UCB1 retrieval, Analyzer prompts, poison mitigations (contradiction flags, confidence decay, retirement thresholds), and audit loops. Auto-fires on "feedback loop", "agents getting smarter", "learn from outcomes".
- **Paper to Code (`paper-to-code`)** — Turn any research paper, engineering blog, or technical doc into shipping code. Strategic reading order, contribution mapping tables, explicit "what NOT to adopt" phase, spec-delta writing. Auto-fires on arxiv URLs, paper links, "apply this research".
- **Multi-Stage Verification (enhanced `completion-enforcer`)** — New Check 6 adds the ASI-Evolve 3-tier evaluation pattern: proxy (lint/type-check) -> functional (tests) -> full (manual/UI verification). Catches "tests pass but I didn't actually try it" false completions.

## Why Use This

- **Better agentic work** — Claude learns how to decompose complex tasks, dispatch specialized subagents, validate output quality, and self-correct through revision loops
- **Agent reliability** — Completion verification catches premature "done" claims, hallucination detection flags fabricated content, context health monitoring prevents session degradation, and constitutional safety rules block dangerous actions
- **Multi-session execution** — The execution harness breaks large projects into checkpointed tasks that survive session boundaries, with resume capability and human review gates
- **Prompt quality enforcement** — 35 anti-pattern checks catch vague, unsafe, or wasteful prompts before they run
- **Project structure** — Auto-scaffolds any new project with a self-documenting 4-layer structure and modular `.claude/` configuration
- **Adaptive behavior** — Agent identity learns your preferences over time, skill memory accumulates domain knowledge from past tasks, compute adaptation degrades gracefully under resource pressure
- **Domain expertise on demand** — From double-entry accounting to circadian lighting to 3D print optimization, Claude gets expert-level methodology loaded exactly when needed
- **More autonomous sessions** — Skills include permission patterns, hook configurations, and structured workflows that let Claude work more independently with fewer interruptions

## Installation

Four commands. Once installed, skills, permissions, and the terminal statusline are set up across all projects forever.

In Claude Code, run:

```
/plugin marketplace add Kgan01/ghengis-skills
/plugin install ghengis-skills@ghengis-skills-marketplace
/ghengis-skills:setup
/ghengis-skills:install-statusline
```

1. `/plugin marketplace add` — register the marketplace
2. `/plugin install` — install the plugin itself
3. `/ghengis-skills:setup` — configure autonomous permissions (safe dev tools auto-allowed, dangerous operations blocked)
4. `/ghengis-skills:install-statusline` — enable the terminal statusline (model name + color-coded context usage bar below your prompt). Auto-detects whether your system uses `python3` or `python`. Idempotent.

Then **fully restart Claude Code** — press Ctrl+C or `/exit`, then run `claude` again. The `statusLine` config is only read at startup; `/reload-plugins` is not enough.

All 55 skills are now available in every session — CLI, desktop app, and mobile. Claude loads them automatically when it detects a matching task.

### Updating / Force Refresh

`/plugin update ghengis-skills` sometimes caches an old version. If the installed version looks stuck, two paths:

**Option 1 — from inside Claude Code:**
```
/ghengis-skills:reload-ghengis
/reload-plugins
```

**Option 2 — from any shell (also works for fresh installs):**
```bash
curl -fsSL https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py | python3
```

Both paths git-fetch the marketplace clone, reset to `origin/master`, refresh the plugin cache, and update `installed_plugins.json`. Idempotent, safe to run repeatedly.

A SessionStart hook also checks for updates every 6 hours and surfaces a notice on your next message if your local version is behind.

### For Teams

Add the marketplace to your project's `.claude/settings.json` so teammates get it automatically:

```json
{
  "extraKnownMarketplaces": {
    "ghengis-skills-marketplace": {
      "source": {
        "source": "github",
        "repo": "Kgan01/ghengis-skills"
      }
    }
  },
  "enabledPlugins": {
    "ghengis-skills@ghengis-skills-marketplace": true
  }
}
```

### Autonomous Permissions (Recommended)

To get the most out of these skills, add this to your `~/.claude/settings.json`. It lets Claude work autonomously on safe operations while blocking dangerous ones.

```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)", "Bash(python:*)", "Bash(python3:*)", "Bash(python -m:*)",
      "Bash(pytest:*)", "Bash(pip:*)", "Bash(pip3:*)",
      "Bash(npm:*)", "Bash(npx:*)", "Bash(node:*)",
      "Bash(docker:*)", "Bash(docker compose:*)",
      "Bash(pio:*)", "Bash(gh:*)", "Bash(curl:*)",
      "Bash(make:*)", "Bash(cmake:*)", "Bash(cargo:*)", "Bash(go:*)",
      "Bash(flutter:*)", "Bash(dart:*)",
      "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)",
      "Bash(wc:*)", "Bash(find:*)", "Bash(tree:*)", "Bash(grep:*)",
      "Bash(mkdir:*)", "Bash(chmod:*)", "Bash(echo:*)", "Bash(sort:*)",
      "Bash(xargs:*)", "Bash(basename:*)", "Bash(dirname:*)",
      "Bash(cp:*)", "Bash(mv:*)", "Bash(touch:*)", "Bash(diff:*)",
      "Bash(sed:*)", "Bash(awk:*)", "Bash(cut:*)", "Bash(tr:*)",
      "Bash(tee:*)", "Bash(jq:*)", "Bash(bash:*)",
      "Bash(cd:*)", "Bash(pwd:*)", "Bash(which:*)", "Bash(env:*)",
      "Read", "Edit", "Write", "WebSearch",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:raw.githubusercontent.com)",
      "WebFetch(domain:docs.anthropic.com)",
      "WebFetch(domain:pypi.org)",
      "WebFetch(domain:npmjs.com)",
      "WebFetch(domain:stackoverflow.com)",
      "mcp__claude-in-chrome__tabs_context_mcp",
      "mcp__claude-in-chrome__tabs_create_mcp",
      "mcp__claude-in-chrome__navigate",
      "mcp__claude-in-chrome__read_page",
      "mcp__claude-in-chrome__get_page_text",
      "mcp__claude-in-chrome__find",
      "mcp__claude-in-chrome__form_input",
      "mcp__claude-in-chrome__read_console_messages",
      "mcp__claude-in-chrome__read_network_requests",
      "mcp__claude-in-chrome__javascript_tool",
      "mcp__claude-in-chrome__shortcuts_list",
      "mcp__claude-in-chrome__shortcuts_execute",
      "mcp__claude-in-chrome__resize_window",
      "mcp__claude-in-chrome__switch_browser",
      "mcp__claude-in-chrome__upload_image",
      "mcp__claude-in-chrome__gif_creator",
      "mcp__claude-in-chrome__update_plan",
      "mcp__claude-in-chrome__computer"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(git push --force:*)", "Bash(git push -f:*)",
      "Bash(git reset --hard:*)", "Bash(git clean -f:*)",
      "Bash(sudo:*)", "Bash(chmod 777:*)",
      "Bash(shutdown:*)", "Bash(reboot:*)", "Bash(halt:*)", "Bash(poweroff:*)",
      "Bash(killall:*)", "Bash(pkill:*)", "Bash(kill -9:*)",
      "Bash(mkfs:*)", "Bash(dd:*)", "Bash(diskutil erase:*)", "Bash(launchctl:*)"
    ]
  }
}
```

The allow list covers all common dev tools plus the Claude-in-Chrome browser-automation MCP tools (navigate, read page, click, type, console/network inspection, screenshots). The deny list blocks destructive operations — `rm -rf`, force push, `sudo`, disk formatting, process killing. Claude still asks before anything not on either list.

## Skills

### Agentic Engineering (7 skills)

These change how Claude approaches complex work — orchestration patterns extracted from a production multi-agent system.

| Skill | What It Does |
|-------|-------------|
| **oort-cascade** | Multi-agent orchestration — breaks complex tasks into specialized roles (researcher, builder, validator), wires them into dependency DAGs, executes in parallel waves, and runs revision loops until quality passes |
| **meta-prompting** | 22 role templates for dispatching subagents. Instead of forwarding raw requests, generates tailored instructions per role with context injection, deliverable specs, and execution boundaries |
| **agent-teams** | Spawns parallel agents with different creative perspectives (Minimalist, Bold, Technical, Playful, Elegant), then synthesizes the strongest elements from each into a final output |
| **agent-monitor** | Real-time subagent monitoring dashboard and terminal status line — tracks agent spawning, completion, permissions, and history. Auto-opens browser dashboard when agents are active. |
| **pql-validation** | Prompt Quality Layer — 35 anti-pattern checks across 6 categories (task, context, format, scope, reasoning, agentic). Catches vague verbs, missing constraints, hallucination invitations, and unsafe delegation before execution |
| **blueprint-compilation** | Recognizes repeated multi-step workflows and compiles them into reusable pipelines. Trace recording, pattern detection, and progressive compilation from ad-hoc to automated |
| **constitutional-ai** | 9 safety rules across 5 categories (Safety, Cost, Privacy, Transparency, Autonomy). Signal-based pre/post execution checks that prevent irreversible actions, PII exposure, and scope creep |
| **project-scaffold** | Auto-generates a 4-layer project structure: MEMORY.md (project identity), CONTEXT.md (workspace routing), per-workspace guidance, and a modular `.claude/` directory with rules, docs, and settings |

### Agent Reliability (5 skills)

These keep agents honest, healthy, and on track — catching failures that normally go unnoticed until the user finds them.

| Skill | What It Does |
|-------|-------------|
| **completion-enforcer** | 70+ signal phrases detect when an agent claims "done" but left placeholders, TODOs, or unfinished work. Five heuristic checks verify structural completeness. Zero cost, instant. |
| **hallucination-detector** | Signal-based detection of fabricated URLs, unsourced statistics, fake citations, and impossible future claims. Catches confabulation without an LLM verification call. |
| **context-health** | Monitors context window usage mid-session, detects degradation and task drift, offers three recovery strategies (truncate, checkpoint-restart, re-anchor). Prevents the silent quality collapse that happens in long sessions. |
| **execution-harness** | Multi-session orchestration for large projects. Decomposes work into 3-15 checkpointed tasks, tracks progress across session boundaries, supports pause/resume, and includes human review gates between phases. |
| **constitutional-ai** | *(also listed in Agentic Engineering)* Pre/post execution safety checks that prevent irreversible actions before they happen. |

### Agent Learning & Adaptation (5 skills)

These help Claude learn, remember, and adapt — building intelligence over time rather than starting fresh every session.

| Skill | What It Does |
|-------|-------------|
| **goal-tracking** | Auto-detects goals from conversation, maintains parent-child hierarchy, tracks state transitions (active/blocked/completed/abandoned), and catches goal staleness with fuzzy matching for related requests |
| **agent-identity** | Builds an evolving understanding of user preferences, communication style, and working patterns through an observe-extract-synthesize loop. Adapts behavior over time. |
| **skill-memory** | Accumulates domain knowledge from past tasks in a grepable plain-text format. No vector database needed — plain markdown, searchable via grep, with auto-consolidation when it grows too large. |
| **skill-chain-supervisor** | Orchestrates multiple ghengis-skills into reliable workflows via a shared JSON scratchpad. Supports sequential, fan-out/merge, conditional, and iterative-loop patterns. **7 built-in chains:** `agent-dispatch` (subagent dispatch with quality gates), `task-complete` (post-task verification), `build-validate` (Builder ↔ Validator round-trip, max 2 iterations), `feature-build` (brainstorming → TDD → build-validate), `bug-hunt` (systematic-debugging → TDD → build-validate), `skill-port` (brainstorming → writing-skills → pql-validation → build-validate), `finish-line` (finishing-a-development-branch → auto-project-sync → audit-ledger). Continuous execution principle — no "should I continue?" pauses between stages. |
| **audit-ledger** | Hash-chained append-only audit trail for what agents did, when, and why. Tamper-proof via SHA-256 chain, queryable by time/agent/goal, daily rollover. |
| **compute-adaptation** | 4-tier graceful degradation (Normal, Low, Critical, Offline). Adapts agent behavior when hitting rate limits, budget constraints, or resource pressure — reduces parallelism, downgrades models, queues non-essential work. |

### Deep Research (1 skill)

| Skill | What It Does |
|-------|-------------|
| **deep-research** | 7-phase iterative research methodology (Clarify, Draft, Gap Analysis, Targeted Research, Refine, Red Team, Converge). Goes beyond single-pass research with adversarial review, convergence detection, and structured confidence levels. |

### Operations (2 skills)

| Skill | What It Does |
|-------|-------------|
| **output-formatting** | 8 destination formatters (chat, email, Slack, TTS, PDF, CSV, JSON, markdown) plus document ingestion and chunking patterns. Same content, adapted per target audience and channel. |
| **proactive-rituals** | Morning briefings, end-of-day summaries, weekly reviews, and custom ritual design. Maps directly to Claude's native cron scheduling. Includes priority queues, sensitivity levels, and event-driven triggers. |

### Security & Code Analysis (2 skills)

| Skill | What It Does |
|-------|-------------|
| **security-testing** | OWASP Top 10 coverage, CVSS scoring, reconnaissance methodology, secure coding patterns, vulnerability analysis, exploit proof format, and hardening checklists. Defensive security and authorized testing. |
| **code-intelligence** | 6-layer architectural classification, AST-based analysis patterns, import graph construction, circular dependency detection, structural code search, and a 5-step codebase understanding methodology. |

### Domain Expertise (17 skills)

Expert-level methodology that loads when Claude encounters matching tasks. Each skill contains the actual knowledge — frameworks, formulas, checklists, worked examples — not just generic guidance.

| Skill | What It Does |
|-------|-------------|
| **general-research** | Systematic research methodology — CRAAP test source evaluation, iterative refinement, structured findings with confidence levels |
| **bookkeeping** | Double-entry accounting, chart of accounts, IRS expense categories, bank reconciliation, cash vs accrual basis, month-end close procedures |
| **task-tracking** | GTD methodology, Eisenhower matrix, sprint planning, task decomposition, blocked task handling |
| **learning-paths** | Bloom's taxonomy, prerequisite mapping, curriculum design, spaced repetition scheduling, progress tracking |
| **tutoring** | Socratic method, level assessment, worked examples scaled by difficulty, misconception detection and correction |
| **time-perception** | Time awareness for Claude — tracks elapsed time between messages, task durations, project switching, and activity patterns via hooks. Includes a portable Python module for wrapping any LLM call with time context. |
| **shopping** | Multi-tier product comparison, evaluation frameworks, per-unit pricing analysis, deal validation |
| **report-writing** | Executive summary structure, data presentation, audience-appropriate formatting, confidence levels, source citation |
| **scheduling** | Time blocking, ritual design, priority-based allocation, conflict resolution, calendar optimization |
| **crm-patterns** | Client lifecycle management, project tracking, communication logging, pipeline management, relationship health scoring, and follow-up automation for freelancers and consultants |
| **file-organization** | 18 manifest types for file categorization, intelligent placement suggestions, naming conventions, directory structure patterns, duplicate detection, and audit trails for file operations |
| **treefile-organizer** | Reshape an existing project's file tree based on its actual import graph — analyzes connections, proposes an ideal target tree, validates the plan adversarially via build-validate, and only moves files after explicit user confirmation. Atomic per-batch rollback via git. Python + TypeScript v1. |
| **brainstorming** | Turn ideas into shippable designs through inline conversational dialogue. No plan mode, no structured Q&A picker — just back-and-forth in chat. One question per message, multiple-choice with recommended option marked, no question cap. Ends by offering 3 execution modes: inline, subagent, or build-validate chain. Adapted from superpowers:brainstorming. |
| **writing-skills** | Test-driven development applied to documentation. Write a pressure scenario, watch a subagent fail without the skill, write the skill that makes it pass, then close loopholes. Required reading before porting any skill. Adapted from superpowers:writing-skills with ghengis pql-validation + build-validate integration. |
| **systematic-debugging** | Iron law: no fixes without root cause investigation. 4-phase methodology — investigate, hypothesize, write regression test (handoff to TDD), fix and verify. Refuses symptom fixes. Adapted from superpowers:systematic-debugging. |
| **test-driven-development** | RED-GREEN-REFACTOR discipline with bite-sized 2-5 minute steps. Watch the test fail before writing code. Watch it pass after. Commit at every cycle boundary. Adapted from superpowers:test-driven-development with the writing-plans bite-sized step pattern baked in. |
| **finishing-a-development-branch** | Verify tests → detect workspace shape → present 4-option menu (merge / PR / keep / discard) → execute → cleanup. Refuses to proceed if tests fail. Requires explicit "yes discard" for destructive option. Adapted from superpowers:finishing-a-development-branch. |
| **mcp-patterns** | MCP server configuration, the meta-tool pattern for context reduction, Context7 two-step lookup, registration anti-patterns |
| **data-analysis** | Statistical methodology, pandas workflows, correlation vs causation, visualization selection, small sample warnings |
| **content-writing** | Blog posts, documentation, marketing copy — structure, SEO basics, audience targeting, editorial checklists |
| **devops** | Solo-dev deployment patterns — Docker multi-stage builds, GitHub Actions CI/CD, SSL, environment management, rollback procedures |
| **music-curation** | Genre classification, BPM matching and transitions, mood-to-genre mapping, playlist arc design, Spotify audio features |
| **home-lighting** | Color temperature science, circadian rhythm automation, room profiles, scene composition, Philips Hue API patterns |
| **3d-modeling** | STL mesh quality, support structure planning, print orientation optimization, dimensional tolerances, prompt engineering for 3D generation |

### Framework Skills (4 skills)

| Skill | What It Does |
|-------|-------------|
| **react-nextjs** | Next.js 15 App Router, server/client component boundaries, dynamic imports, Zustand state management, CSS variable theming |
| **fastapi** | Async-first patterns, Pydantic v2 (model_dump not dict), dependency injection, WebSocket auth-before-accept, blocking code handling |
| **flutter-dart** | Widget composition, state management patterns, platform channels (MethodChannel/EventChannel), navigation, theme system |
| **esp32** | PlatformIO build system, I2S audio configuration, PSRAM allocation, FreeRTOS task pinning, WiFi/BLE patterns, state machine design |

## How Skills Work

Each skill is a markdown file with YAML frontmatter:

```yaml
---
name: skill-name
description: When Claude should activate this skill — specific trigger conditions
---

# Skill Name

Methodology, patterns, examples, checklists...
```

The `description` field tells Claude when to load the skill. When a task matches, the skill content is injected into the session and guides Claude's approach. When no skills match, nothing is loaded — zero context cost.

Some skills include supporting documents (e.g., `oort-cascade/handoff-protocol.md`, `pql-validation/anti-patterns.md`) that provide deeper reference material.

## Evals

Each skill has evaluation test cases in `evals/` — scenarios with specific assertions that verify the skill produces correct, methodology-driven output rather than generic responses.

```
evals/{skill-name}.eval.md

# Example test case format:
## TC-1: Complex Multi-Step Task
- prompt: "Research competitors, write a strategy doc, then review it"
- assertions:
  - Decomposes into researcher, builder, validator roles
  - Creates dependency DAG with parallel waves
  - Runs validation pass with scoring rubric
- passing_grade: 3/3
```

## Contributing

To add a skill:

1. Create `skills/{skill-name}/SKILL.md` with YAML frontmatter
2. Create `evals/{skill-name}.eval.md` with 3-5 test cases
3. Keep skills focused — one domain, one methodology
4. Include worked examples and checklists where possible
5. Test that the skill activates on the right triggers and stays silent otherwise

## License

MIT
