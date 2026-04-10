# Ghengis Skills

A Claude Code plugin that makes Claude smarter, faster, and more autonomous. 43 skills covering multi-agent orchestration, prompt quality validation, agent reliability, session management, project scaffolding, security testing, code intelligence, and deep domain expertise across 20+ fields.

Skills are lightweight — they load on-demand and don't bloat your context window. Unlike MCP servers that inject tool schemas into every message, skills activate only when relevant, adding zero overhead the rest of the time.

### v1.4.0 — Opus 4.6 Optimizations

Updated for Claude Opus 4.6 based on [Anthropic's prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), [harness design patterns](https://www.anthropic.com/engineering/harness-design-long-running-apps), and [Managed Agents architecture](https://www.anthropic.com/engineering/managed-agents):

- **Functional testing in OORT** — Validators now run the output (execute tests, call endpoints, load in browser) instead of just scoring it. Tuned to skepticism.
- **Subagent guardrails** — oort-cascade, agent-teams, and meta-prompting include dispatch guardrails for Opus 4.6, which has a strong native tendency to spawn subagents. Prevents over-spawning.
- **Native context awareness** — context-health updated for models that track their own context window. Shift from detection to leveraging native awareness. Fresh-start guidance over compaction.
- **State management patterns** — execution-harness now includes structured state files (tests.json, progress.txt), setup scripts, and git-as-state-tracking for multi-window workflows.
- **Model tier updates** — context-health model tiers updated for opus-4.6, sonnet-4.6, haiku-4.5.

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

### Step 1: Clone the repo

```bash
git clone https://github.com/Kgan01/ghengis-skills.git ~/ghengis-skills
```

### Step 2: Add the marketplace

In Claude Code, run:

```
/plugin marketplace add ~/ghengis-skills
```

### Step 3: Install the plugin

```
/plugin install ghengis-skills@ghengis-skills-marketplace
```

Or use the `/plugin` UI to browse and install.

### Step 4: Activate

```
/reload-plugins
```

That's it. Skills are now available in every Claude Code session — CLI, desktop app, and mobile (via desktop).

### Short Commands (Recommended)

By default, plugin skills are namespaced (`/ghengis-skills:project-scaffold`). To use short names like `/project-scaffold`, symlink the skills to your personal skills directory:

```bash
mkdir -p ~/.claude/skills
for skill in ~/ghengis-skills/plugins/ghengis-skills/skills/*/; do
  ln -sf "$skill" ~/.claude/skills/$(basename "$skill")
done
```

Now you can use skills directly:

```
/project-scaffold    # Scaffold a new project
/oort-cascade        # Multi-agent orchestration
/pql-validation      # Check prompt quality
/deep-research       # 7-phase iterative research
```

Claude also loads skills automatically when it detects a matching task — you don't always need to invoke them manually. Just work normally and the relevant skill activates when needed.

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

### Hooks & Permissions

Skills like `project-scaffold` and `constitutional-ai` define permission boundaries and safety checks that help Claude operate more autonomously while staying within safe limits.

## Skills

### Agentic Engineering (7 skills)

These change how Claude approaches complex work — orchestration patterns extracted from a production multi-agent system.

| Skill | What It Does |
|-------|-------------|
| **oort-cascade** | Multi-agent orchestration — breaks complex tasks into specialized roles (researcher, builder, validator), wires them into dependency DAGs, executes in parallel waves, and runs functional testing + revision loops. Includes subagent dispatch guardrails for Opus 4.6 |
| **meta-prompting** | 22 role templates for dispatching subagents. Instead of forwarding raw requests, generates tailored instructions per role with context injection, deliverable specs, and execution boundaries |
| **agent-teams** | Spawns parallel agents with different creative perspectives (Minimalist, Bold, Technical, Playful, Elegant), then synthesizes the strongest elements from each into a final output |
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
| **context-health** | Monitors context window usage mid-session, detects degradation and task drift, offers three recovery strategies (truncate, checkpoint-restart, re-anchor). Updated for Opus 4.6 native context awareness — leverages the model's own tracking while still catching drift and failure spirals. |
| **execution-harness** | Multi-session orchestration for large projects. Decomposes work into 3-15 checkpointed tasks, tracks progress across session boundaries with structured state files (tests.json, progress.txt), supports fresh-start-over-compact strategy, git-as-state-tracking, and human review gates. |
| **constitutional-ai** | *(also listed in Agentic Engineering)* Pre/post execution safety checks that prevent irreversible actions before they happen. |

### Agent Learning & Adaptation (5 skills)

These help Claude learn, remember, and adapt — building intelligence over time rather than starting fresh every session.

| Skill | What It Does |
|-------|-------------|
| **goal-tracking** | Auto-detects goals from conversation, maintains parent-child hierarchy, tracks state transitions (active/blocked/completed/abandoned), and catches goal staleness with fuzzy matching for related requests |
| **agent-identity** | Builds an evolving understanding of user preferences, communication style, and working patterns through an observe-extract-synthesize loop. Adapts behavior over time. |
| **skill-memory** | Accumulates domain knowledge from past tasks in a grepable plain-text format. No vector database needed — plain markdown, searchable via grep, with auto-consolidation when it grows too large. |
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
| **shopping** | Multi-tier product comparison, evaluation frameworks, per-unit pricing analysis, deal validation |
| **report-writing** | Executive summary structure, data presentation, audience-appropriate formatting, confidence levels, source citation |
| **scheduling** | Time blocking, ritual design, priority-based allocation, conflict resolution, calendar optimization |
| **crm-patterns** | Client lifecycle management, project tracking, communication logging, pipeline management, relationship health scoring, and follow-up automation for freelancers and consultants |
| **file-organization** | 18 manifest types for file categorization, intelligent placement suggestions, naming conventions, directory structure patterns, duplicate detection, and audit trails for file operations |
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
