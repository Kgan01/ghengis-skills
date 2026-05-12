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

## What's New (v1.14.0)

- **Closed cognition loop (`skill-chain-supervisor`)** — Chain runs now learn from each other. Set `GHENGIS_COGNITION=true` and every `finish` emits a structured lesson to `cognition.jsonl`; every `init` retrieves the most relevant past lessons via UCB1-weighted Jaccard similarity, bumps `hits`, and bumps `wins` on success. Audit command surfaces entries to retire (high hits, low win-rate). Stdlib-only, opt-in.
- **5 new workflow skills + 4 new chains (v1.12.0)** — `brainstorming` (inline conversational design, never uses plan mode), `writing-skills` (TDD on documentation), `systematic-debugging` (iron law: no fixes without root cause), `test-driven-development` (RED-GREEN-REFACTOR with bite-sized steps), `finishing-a-development-branch` (verify-tests gate before merge/PR). Plus chains `feature-build`, `bug-hunt`, `skill-port`, `finish-line`.
- **`treefile-organizer` (v1.11.0)** — Reshape an existing project's file tree based on its actual import graph. Analyzer + planner Python scripts produce a plan.json the build-validate chain validates adversarially before any file moves.

## Previous (v1.8.1)

- **Time Perception (`time-perception`)** — Gives Claude a persistent sense of time. `UserPromptSubmit` hook injects elapsed time, message count, and project-switch detection. Includes a portable Python module for wrapping any LLM API with time awareness.
- **Agent Monitor (`agent-monitor`)** — Real-time subagent dashboard and terminal status line. Auto-opens browser dashboard on ports 7685/7686 when 2+ agents run.

## Previous (v1.7.0)

- **Evolving Cognition (`evolving-cognition`)** — ASI-Evolve-inspired pattern for agents that learn from measurable outcomes. Now wired end-to-end via skill-chain-supervisor's cognition commands (see v1.14.0 above).
- **Paper to Code (`paper-to-code`)** — Turn any research paper or technical doc into shipping code. Auto-fires on arxiv URLs, paper links, "apply this research".

## Why Use This

- **Better agentic work** — Claude learns how to decompose complex tasks, dispatch specialized subagents, validate output quality, and self-correct through revision loops
- **Agent reliability** — Completion verification catches premature "done" claims, hallucination detection flags fabricated content, context health monitoring prevents session degradation, and constitutional safety rules block dangerous actions
- **Multi-session execution** — The execution harness breaks large projects into checkpointed tasks that survive session boundaries, with resume capability and human review gates
- **Prompt quality enforcement** — 35 anti-pattern checks catch vague, unsafe, or wasteful prompts before they run
- **Project structure** — Auto-scaffolds any new project with a self-documenting 4-layer structure and modular `.claude/` configuration
- **Adaptive behavior** — Agent identity learns your preferences over time, skill memory accumulates domain knowledge from past tasks, compute adaptation degrades gracefully under resource pressure
- **Domain expertise on demand** — From double-entry accounting to circadian lighting to 3D print optimization, Claude gets expert-level methodology loaded exactly when needed
- **More autonomous sessions** — Skills include permission patterns, hook configurations, and structured workflows that let Claude work more independently with fewer interruptions

## Common Workflows

Most usage doesn't require thinking about which skill to invoke — Claude loads them automatically based on the description triggers. But the **chains** in `skill-chain-supervisor` are the highest-leverage entry points and deserve explicit knowledge. Say one of these phrases and a supervised multi-stage pipeline fires.

### "I want to build a new feature"

```
You: "let's build a feature for X" / "build a feature: X" / "run feature-build on X"
```

What happens:
1. **brainstorming** activates — asks clarifying questions one at a time in chat. Picks design with you. Offers 3 execution modes: inline (you watch me code), subagent (dispatch a Builder, sleep), or build-validate chain (Builder + adversarial Validator + revision loop).
2. **test-driven-development** writes the failing test first; you watch it fail; minimal code to pass; commit.
3. **build-validate** runs as a nested chain. The Validator's job is to *break* the work — find bypass cases, missing edge handling, broken cross-refs. Score < 7 → loops back to Builder for one revision (cap is 2 iterations).

### "I want to fix a bug"

```
You: "fix this bug: X" / "track down a bug" / "run bug-hunt on X"
```

What happens:
1. **systematic-debugging** Phase 1 — read error, reproduce, check changes. Cannot propose fixes until root cause is stated in one no-hedge sentence with confirming evidence.
2. **test-driven-development** writes a regression test that fails for the *same* reason the user reported.
3. **build-validate** verifies the fix passes the regression test AND no other tests broke. Refuses symptom fixes.

### "Let's add a new skill"

```
You: "add a skill for X" / "port the Y skill from superpowers" / "run skill-port"
```

What happens:
1. **brainstorming** clarifies trigger conditions, anti-patterns, cross-refs.
2. **writing-skills** runs the TDD-on-documentation cycle: pressure scenario → baseline subagent failure → write SKILL.md → re-test.
3. **pql-validation** gates the frontmatter `description` (score ≥ 0.7 required; vague triggers, process summaries, underscores in `name` all rejected).
4. **build-validate** stress-tests the new skill against adversarial scenarios. The Validator tries to rationalize past the rules to find loopholes.

### "Ship this branch"

```
You: "ship this branch" / "wrap up and ship" / "run finish-line"
```

What happens:
1. **finishing-a-development-branch** verifies tests pass first (refuses to proceed if any fail). Detects workspace shape (normal repo / worktree). Presents 4-option menu: merge locally / push+PR / keep / discard. Requires explicit "yes discard" for option 4. Refuses force-push to main.
2. **auto-project-sync** (conditional, non-blocking) updates CLAUDE.md, MEMORY.md, indexes to reflect what shipped.
3. **audit-ledger** records the integration event with hash-chained provenance.

### "Just review this deliverable"

```
You: "run build-validate on this" / "ping-pong this" / "validate thoroughly"
```

When you don't need the whole feature/bug pipeline — just an adversarial check on an existing artifact. Builder produces → Validator independently tests + scores → loops if score < 7.

### Cognition Loop (Opt-In Learning)

The chain system learns from outcomes when `GHENGIS_COGNITION=true`:

```bash
# Per-session
export GHENGIS_COGNITION=true

# Per-project — add to .claude/settings.json env block
{ "env": { "GHENGIS_COGNITION": "true" } }

# Globally — add to ~/.zshrc
export GHENGIS_COGNITION=true
```

When enabled:
- **At chain init:** reads `<project>/.claude/ghengis-chain/cognition.jsonl`, ranks past lessons by UCB1-weighted Jaccard similarity to your current `user_request`, surfaces top 5 as `state.lessons_from_past`. Each surfaced entry's `hits` counter bumps.
- **At chain finish:** if the outcome was a success (shipped / fixed / revised-and-shipped), `wins` bumps on every previously-retrieved lesson. A new entry is emitted for this run.
- **Monthly maintenance:** `python scripts/scratchpad.py audit` flags entries with `hits ≥ 5` and `win_rate < 0.4` for retirement. Set `audit_status: "retired"` to exclude from future retrievals without deleting history.

**Turn on for:** repeat-structure projects, long-running work, multi-session contexts where lessons across runs matter.
**Leave off for:** one-off projects, fast spikes, debugging the chain system itself (don't poison the journal), privacy-sensitive work.

### Direct Skill Invocation

You don't usually need this — skills auto-fire on triggers — but if you want to force one:

```
You: "use the systematic-debugging skill on this"
You: "I want brainstorming for this"
You: "run pql-validation on this prompt"
```

Or use the Skill tool's exact name from the table below.

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

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **oort-cascade** | Multi-agent orchestration — breaks complex tasks into specialized roles (researcher, builder, validator), wires them into dependency DAGs, executes in parallel waves, and runs revision loops until quality passes | Auto-fires on complex multi-step requests. Force: *"use oort-cascade on this"*, *"run a cascade"*. Often nested inside `feature-build` and `build-validate` chains. |
| **meta-prompting** | 22 role templates for dispatching subagents. Instead of forwarding raw requests, generates tailored instructions per role with context injection, deliverable specs, and execution boundaries | Auto-fires when dispatching subagents. Force: *"use meta-prompting for the subagent prompt"*. The `agent-dispatch` chain calls this automatically. |
| **agent-teams** | Spawns parallel agents with different creative perspectives (Minimalist, Bold, Technical, Playful, Elegant), then synthesizes the strongest elements from each into a final output | Trigger: *"give me 3 different takes on X"*, *"agent teams for this design"*, *"parallel perspectives"*. |
| **agent-monitor** | Real-time subagent monitoring dashboard and terminal status line — tracks agent spawning, completion, permissions, and history. Auto-opens browser dashboard when agents are active. | Always-on once installed. Browser dashboard at `http://localhost:7685` when 2+ agents run. |
| **pql-validation** | Prompt Quality Layer — 35 anti-pattern checks across 6 categories (task, context, format, scope, reasoning, agentic). Catches vague verbs, missing constraints, hallucination invitations, and unsafe delegation before execution | Trigger: *"check this prompt"*, *"validate this prompt"*. Wired into `agent-dispatch` (threshold 0.5 + autofix) and `skill-port` chains (threshold 0.7). |
| **blueprint-compilation** | Recognizes repeated multi-step workflows and compiles them into reusable pipelines. Trace recording, pattern detection, and progressive compilation from ad-hoc to automated | Trigger: *"I keep doing the same thing, let's automate it"*, *"compile this workflow"*. |
| **constitutional-ai** | 9 safety rules across 5 categories (Safety, Cost, Privacy, Transparency, Autonomy). Signal-based pre/post execution checks that prevent irreversible actions, PII exposure, and scope creep | Always-on guardrail. Doesn't need invocation. Refuses irreversible operations, flags PII before sending to external services. |
| **project-scaffold** | Auto-generates a 4-layer project structure: MEMORY.md (project identity), CONTEXT.md (workspace routing), per-workspace guidance, and a modular `.claude/` directory with rules, docs, and settings | Trigger: *"scaffold this project"*, *"set up project structure"*, *"new FastAPI service"*. Run `/scaffold-project` slash command. |

### Agent Reliability (5 skills)

These keep agents honest, healthy, and on track — catching failures that normally go unnoticed until the user finds them.

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **completion-enforcer** | 70+ signal phrases detect when an agent claims "done" but left placeholders, TODOs, or unfinished work. Five heuristic checks verify structural completeness. Zero cost, instant. | Auto-fires after any "done" / "complete" / "fixed" claim. Force: *"verify this is actually done"*. Built into the `task-complete` and `agent-dispatch` chains. |
| **hallucination-detector** | Signal-based detection of fabricated URLs, unsourced statistics, fake citations, and impossible future claims. Catches confabulation without an LLM verification call. | Trigger: *"fact-check this"*, *"look for fabrications"*. Wired into `task-complete` chain. |
| **context-health** | Monitors context window usage mid-session, detects degradation and task drift, offers three recovery strategies (truncate, checkpoint-restart, re-anchor). Prevents the silent quality collapse that happens in long sessions. | Trigger: *"feeling lost"*, *"are we still on track?"*, *"context health check"*. Useful when the conversation has run long. |
| **execution-harness** | Multi-session orchestration for large projects. Decomposes work into 3-15 checkpointed tasks, tracks progress across session boundaries, supports pause/resume, and includes human review gates between phases. | Trigger: *"this is a multi-session project"*, *"set up the execution harness"*, *"checkpoint this work"*. |
| **constitutional-ai** | *(also listed in Agentic Engineering)* Pre/post execution safety checks that prevent irreversible actions before they happen. | Always-on; no invocation needed. |

### Agent Learning & Adaptation (5 skills)

These help Claude learn, remember, and adapt — building intelligence over time rather than starting fresh every session.

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **goal-tracking** | Auto-detects goals from conversation, maintains parent-child hierarchy, tracks state transitions (active/blocked/completed/abandoned), and catches goal staleness with fuzzy matching for related requests | Auto-fires when you describe a goal. Trigger: *"what was I working on?"*, *"goal status"*. |
| **agent-identity** | Builds an evolving understanding of user preferences, communication style, and working patterns through an observe-extract-synthesize loop. Adapts behavior over time. | Always-on observation. Trigger explicit update: *"remember this preference"*, *"update my profile"*. |
| **skill-memory** | Accumulates domain knowledge from past tasks in a grepable plain-text format. No vector database needed — plain markdown, searchable via grep, with auto-consolidation when it grows too large. | Trigger: *"remember this for next time"*, *"what did we learn last time about X?"*. Searchable via grep over `~/.claude/skill-memory/`. |
| **skill-chain-supervisor** | Orchestrates multiple ghengis-skills into reliable workflows via a shared JSON scratchpad. **7 built-in chains:** `agent-dispatch`, `task-complete`, `build-validate`, `feature-build`, `bug-hunt`, `skill-port`, `finish-line`. Continuous execution principle — no "should I continue?" pauses between stages. Nested chain support. Per-stage `on_error` overrides. Cognition emission + UCB1 retrieval when `GHENGIS_COGNITION=true`. | See **Common Workflows** section above. Trigger phrases: *"run feature-build on X"*, *"bug-hunt this"*, *"port the Y skill"*, *"ship this branch"*, *"validate thoroughly"*. Helper at `scripts/scratchpad.py` exposes `init`, `finish`, `nested-start`, `nested-finish`, `retrieve`, `audit`, `cognition-emit`. |
| **audit-ledger** | Hash-chained append-only audit trail for what agents did, when, and why. Tamper-proof via SHA-256 chain, queryable by time/agent/goal, daily rollover. | Wired into `finish-line` chain. Trigger explicit query: *"audit log for today"*, *"what did the agents do yesterday?"*. |
| **compute-adaptation** | 4-tier graceful degradation (Normal, Low, Critical, Offline). Adapts agent behavior when hitting rate limits, budget constraints, or resource pressure — reduces parallelism, downgrades models, queues non-essential work. | Auto-fires when hitting rate limits or budget caps. Trigger: *"we're rate-limited"*, *"budget is tight, slow down"*. |

### Deep Research (2 skills)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **deep-research** | 7-phase iterative research methodology (Clarify, Draft, Gap Analysis, Targeted Research, Refine, Red Team, Converge). Goes beyond single-pass research with adversarial review, convergence detection, and structured confidence levels. | Trigger: *"deep dive into X"*, *"thorough research on Y"*, *"red-team this"*. Auto-fires when a research question needs more than one pass. |
| **general-research** | Systematic research methodology — CRAAP test source evaluation, iterative refinement, structured findings with confidence levels. Lighter than deep-research; one-pass with rigor. | Trigger: *"research X"*, *"what do we know about Y"*. |

### Operations (2 skills)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **output-formatting** | 8 destination formatters (chat, email, Slack, TTS, PDF, CSV, JSON, markdown) plus document ingestion and chunking patterns. Same content, adapted per target audience and channel. | Trigger: *"format this for Slack"*, *"make this an email"*, *"export as CSV"*, *"ingest this PDF"*. |
| **proactive-rituals** | Morning briefings, end-of-day summaries, weekly reviews, and custom ritual design. Maps directly to Claude's native cron scheduling. Includes priority queues, sensitivity levels, and event-driven triggers. | Trigger: *"set up a morning briefing"*, *"daily check-in"*, *"weekly review ritual"*. Pair with `/schedule` slash command. |

### Security & Code Analysis (2 skills)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **security-testing** | OWASP Top 10 coverage, CVSS scoring, reconnaissance methodology, secure coding patterns, vulnerability analysis, exploit proof format, and hardening checklists. Defensive security and authorized testing. | Trigger: *"security review of this"*, *"check for vulnerabilities"*, *"OWASP audit"*. Also fires on `/security-review` slash command. |
| **code-intelligence** | 6-layer architectural classification, AST-based analysis patterns, import graph construction, circular dependency detection, structural code search, and a 5-step codebase understanding methodology. | Trigger: *"map the architecture"*, *"trace dependencies"*, *"understand this codebase"*. The `treefile-organizer` analyzer uses this layer classification. |

### Workflow Skills (5 skills, ported from superpowers)

The development discipline skills. Mostly auto-fire when triggered, but also wire into the chains.

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **brainstorming** | Turn ideas into shippable designs through inline conversational dialogue. No plan mode, no `AskUserQuestion` picker — just back-and-forth in chat. One question per message, multiple-choice with recommended option marked, no question cap. Ends by offering 3 execution modes: inline / subagent / build-validate chain. | Auto-fires on *"let's build X"*, *"design Y for me"*, *"add a feature: Z"*. Used as stage 1 of `feature-build` and `skill-port` chains. |
| **writing-skills** | Test-driven development applied to documentation. Write a pressure scenario, watch a subagent fail without the skill, write the skill that makes it pass, then close loopholes. | Trigger: *"let's add a skill"*, *"port the X skill from superpowers"*, *"I keep repeating this instruction"*. Wired into `skill-port` chain. |
| **systematic-debugging** | Iron law: no fixes without root cause investigation. 4-phase methodology — investigate, hypothesize, write regression test, fix and verify. Refuses symptom fixes. | Auto-fires on *"this is broken"*, *"test is failing"*, *"why is X doing Y"*. Stage 1 of `bug-hunt` chain. |
| **test-driven-development** | RED-GREEN-REFACTOR discipline with bite-sized 2-5 minute steps. Watch the test fail before writing code. Watch it pass after. Commit at every cycle boundary. | Auto-fires when implementing any new behavior. Stages 2 of `feature-build` and `bug-hunt` chains. Override only for true throwaway code or 30-min spikes. |
| **finishing-a-development-branch** | Verify tests → detect workspace shape → present 4-option menu (merge / PR / keep / discard) → execute → cleanup. Refuses to proceed if tests fail. | Trigger: *"ship this branch"*, *"merge this branch"*, *"wrap up and ship"*. Stage 1 of `finish-line` chain. |

### Domain Expertise (16 skills)

Expert-level methodology that loads when Claude encounters matching tasks. Each skill contains the actual knowledge — frameworks, formulas, checklists, worked examples — not just generic guidance.

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **bookkeeping** | Double-entry accounting, chart of accounts, IRS expense categories, bank reconciliation, cash vs accrual basis, month-end close procedures | Trigger: *"categorize these expenses"*, *"reconcile this account"*, *"close the books"*. |
| **task-tracking** | GTD methodology, Eisenhower matrix, sprint planning, task decomposition, blocked task handling | Trigger: *"organize my tasks"*, *"prioritize this list"*, *"break this down"*. |
| **learning-paths** | Bloom's taxonomy, prerequisite mapping, curriculum design, spaced repetition scheduling, progress tracking | Trigger: *"teach me X"*, *"design a learning path for Y"*, *"prerequisites for Z"*. |
| **tutoring** | Socratic method, level assessment, worked examples scaled by difficulty, misconception detection and correction | Trigger: *"explain X like I'm a beginner"*, *"walk me through Y"*. |
| **time-perception** | Time awareness for Claude — tracks elapsed time between messages, task durations, project switching, and activity patterns via hooks. | Always-on once installed. No invocation needed. |
| **shopping** | Multi-tier product comparison, evaluation frameworks, per-unit pricing analysis, deal validation | Trigger: *"should I buy X"*, *"compare these products"*, *"is this a good deal"*. |
| **report-writing** | Executive summary structure, data presentation, audience-appropriate formatting, confidence levels, source citation | Trigger: *"write a report on X"*, *"executive summary of Y"*. |
| **scheduling** | Time blocking, ritual design, priority-based allocation, conflict resolution, calendar optimization | Trigger: *"schedule my week"*, *"optimize my calendar"*. Pair with `/schedule`. |
| **crm-patterns** | Client lifecycle management, project tracking, communication logging, pipeline management, relationship health scoring, follow-up automation | Trigger: *"track this client"*, *"my pipeline status"*, *"follow up with X"*. |
| **file-organization** | 18 manifest types for file categorization, intelligent placement suggestions, naming conventions, directory structure patterns, duplicate detection, audit trails | Trigger: *"organize these files"*, *"clean up this directory"*. For deep tree restructuring use `treefile-organizer` instead. |
| **treefile-organizer** | Reshape an existing project's file tree based on its actual import graph. Analyzer + planner Python scripts produce a plan.json the build-validate chain validates adversarially before any file moves. Python + TypeScript v1. | Trigger: *"reorganize this project"*, *"the structure is a mess"*. Refuses on dirty git tree. Always plan-first; never moves files without explicit "yes proceed". |
| **mcp-patterns** | MCP server configuration, the meta-tool pattern for context reduction, Context7 two-step lookup, registration anti-patterns | Trigger: *"set up an MCP server"*, *"how do I use the meta-tool pattern"*. |
| **data-analysis** | Statistical methodology, pandas workflows, correlation vs causation, visualization selection, small sample warnings | Trigger: *"analyze this data"*, *"what does this CSV tell us"*, *"visualize X vs Y"*. |
| **content-writing** | Blog posts, documentation, marketing copy — structure, SEO basics, audience targeting, editorial checklists | Trigger: *"write a blog post on X"*, *"draft marketing copy for Y"*. |
| **devops** | Solo-dev deployment patterns — Docker multi-stage builds, GitHub Actions CI/CD, SSL, environment management, rollback procedures | Trigger: *"deploy this"*, *"set up CI/CD"*, *"Docker for this project"*. |
| **music-curation** | Genre classification, BPM matching and transitions, mood-to-genre mapping, playlist arc design, Spotify audio features | Trigger: *"make a playlist for X"*, *"music for a Y mood"*. |
| **home-lighting** | Color temperature science, circadian rhythm automation, room profiles, scene composition, Philips Hue API patterns | Trigger: *"design lighting for X room"*, *"circadian scenes for sleep"*, *"Hue automation"*. |
| **3d-modeling** | STL mesh quality, support structure planning, print orientation optimization, dimensional tolerances, prompt engineering for 3D generation | Trigger: *"3D print this"*, *"prepare this STL for printing"*, *"print orientation for X"*. |
| **paper-to-code** | Strategic reading, contribution mapping, spec delta writing, "what NOT to adopt" framing for translating research papers into code | Auto-fires on arxiv URLs, *"apply this paper"*, *"read this paper and tell me what's useful"*. |

### Framework Skills (4 skills)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **react-nextjs** | Next.js 15 App Router, server/client component boundaries, dynamic imports, Zustand state management, CSS variable theming | Auto-fires on Next.js / React file edits. Trigger: *"add a server component for X"*, *"client-side hook in Y"*. |
| **fastapi** | Async-first patterns, Pydantic v2 (model_dump not dict), dependency injection, WebSocket auth-before-accept, blocking code handling | Auto-fires on FastAPI imports / routes. Trigger: *"add an endpoint for X"*, *"FastAPI middleware for Y"*. |
| **flutter-dart** | Widget composition, state management patterns, platform channels (MethodChannel/EventChannel), navigation, theme system | Auto-fires on `.dart` file edits. Trigger: *"add a widget for X"*, *"platform channel for Y"*. |
| **esp32** | PlatformIO build system, I2S audio configuration, PSRAM allocation, FreeRTOS task pinning, WiFi/BLE patterns, state machine design | Auto-fires on ESP32 firmware work. Trigger: *"flash this firmware"*, *"I2S audio for X"*, *"BLE service for Y"*. |

## How Skills Work

Each skill is a markdown file with YAML frontmatter:

```yaml
---
name: skill-name
description: When Claude should activate this skill — specific trigger conditions
allowed-tools: Read Write Edit Bash    # optional
model: fast | balanced | premium       # optional tier hint for subagent dispatch
---

# Skill Name

Methodology, patterns, examples, checklists...
```

The `description` field tells Claude when to load the skill. When a task matches, the skill content is injected into the session and guides Claude's approach. When no skills match, nothing is loaded — zero context cost.

**Some skills include supporting docs** (e.g., `oort-cascade/handoff-protocol.md`, `treefile-organizer/plan-format.md`, `pql-validation/anti-patterns.md`) that provide deeper reference material.

**Some skills include executable scripts:**
- `skill-chain-supervisor/scripts/scratchpad.py` — chain lifecycle helper (init, finish, nested-start, nested-finish, retrieve, audit, cognition-emit)
- `treefile-organizer/scripts/analyzer.py` — walks a project, extracts import graph, classifies layers, emits analysis JSON
- `treefile-organizer/scripts/planner.py` — reads analysis, proposes moves with import rewrites, emits plan.json + plan.md

All scripts are stdlib-only Python — no dependencies.

## How Chains Work

Chains compose multiple skills into supervised pipelines via a shared JSON scratchpad at `<project>/.claude/ghengis-chain/context.json`. Each stage:

1. Reads prior stages' output from the scratchpad
2. Invokes a skill (or another chain, for nesting) with that context
3. Writes its results back, namespaced under its own underscored subkey

Lifecycle:
```bash
# Bootstrap a fresh chain
python scripts/scratchpad.py init feature-build --input-json '{"user_request":"..."}'

# At chain end — archives to history/, optionally emits cognition entry
python scripts/scratchpad.py finish
```

Patterns supported: sequential, fan-out/merge, conditional, iterative loop, **nested chain**. See `skill-chain-supervisor/SKILL.md` for the full schema, per-stage `on_error` overrides, and trigger precedence rules.

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
