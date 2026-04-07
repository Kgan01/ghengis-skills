# Ghengis Skills

Agentic engineering patterns and domain expertise for Claude Code. 26 skills extracted from the [JARVIS](https://github.com/kgan) personal AI assistant system.

Install this plugin and every Claude session gets access to multi-agent orchestration, prompt quality validation, project scaffolding, and deep domain expertise across 15+ fields.

## What's Inside

### Agentic Engineering (7 skills)

The core differentiator. These teach Claude **how to be a better agent**.

| Skill | What It Does |
|-------|-------------|
| **oort-cascade** | Multi-agent orchestration — task decomposition, dependency DAGs, parallel waves, revision loops |
| **meta-prompting** | 22 role templates for dispatching specialized subagents (researcher, builder, validator, etc.) |
| **agent-teams** | Parallel agents with perspective diversity — Minimalist, Bold, Technical, Playful, Elegant |
| **pql-validation** | 35 prompt anti-pattern checks across 6 categories — catches bad prompts before they waste tokens |
| **blueprint-compilation** | Self-compiling workflows — observe repeated patterns, compile into reusable pipelines |
| **constitutional-ai** | 9 safety rules across 5 categories — prevents irreversible actions, PII exposure, cost overruns |
| **project-scaffold** | Van Clief 4-layer project structure — auto-generates MEMORY.md, CONTEXT.md, modular .claude/ config |

### Domain Expertise — Everyone (8 skills)

Practical knowledge that makes Claude dramatically better at everyday tasks. Great for non-technical users too.

| Skill | What It Does |
|-------|-------------|
| **general-research** | Systematic research methodology — source evaluation, iterative refinement, structured findings |
| **bookkeeping** | Double-entry accounting, IRS expense categories, reconciliation, financial reports |
| **task-tracking** | GTD + Eisenhower matrix, project breakdown, priority management |
| **learning-paths** | Bloom's taxonomy, prerequisite mapping, curriculum design, personalized progression |
| **tutoring** | Socratic method, level assessment, worked examples, misconception handling |
| **shopping** | Price comparison frameworks, evaluation criteria, tier-based recommendations |
| **report-writing** | Storytelling structure, data presentation, executive summaries |
| **scheduling** | Time blocking, ritual design, priority-based allocation, calendar optimization |

### Domain Expertise — Developers (4 skills)

| Skill | What It Does |
|-------|-------------|
| **mcp-patterns** | MCP server types, meta-tool pattern (14x context reduction), Context7 integration, anti-patterns |
| **data-analysis** | Statistical methodology, pandas patterns, visualization best practices, insight presentation |
| **content-writing** | Blog posts, docs, marketing copy — structure, audience targeting, editorial quality |
| **devops** | Solo-dev deployment — Docker, GitHub Actions, SSL, environment management, rollback |

### Domain Expertise — Unique (3 skills)

The fun ones. These make people tell their friends.

| Skill | What It Does |
|-------|-------------|
| **music-curation** | Genre theory, BPM matching, mood mapping, playlist arc design, Spotify patterns |
| **home-lighting** | Color theory, circadian rhythms, room profiles, scene design, Philips Hue |
| **3d-modeling** | STL quality, support structures, print orientation, mesh optimization |

### Framework Skills (4 skills)

| Skill | What It Does |
|-------|-------------|
| **react-nextjs** | App Router, server/client components, Zustand, data fetching patterns |
| **fastapi** | Async patterns, Pydantic v2, dependency injection, WebSocket auth |
| **flutter-dart** | Widget patterns, state management, platform channels, navigation |
| **esp32** | PlatformIO, I2S audio, WiFi/BLE, memory management, state machines |

## Installation

### Claude Code CLI / Desktop

```bash
# Via plugin marketplace (when published)
/plugin install ghengis-skills

# Manual install (clone into plugins directory)
git clone https://github.com/kgan/ghengis-skills.git ~/.claude/plugins/ghengis-skills
```

### How Skills Work

Skills are loaded on-demand — they don't bloat your context window. When Claude detects a task that matches a skill's description, the skill is loaded and its guidance shapes the response.

Unlike MCP servers that add tool schemas to every message, skills are **zero overhead until activated**.

## Evals

Each skill has evaluation test cases in the `evals/` directory. These define scenarios with assertions to verify the skill is producing correct output.

```
evals/
  oort-cascade.eval.md      # 5 test cases
  pql-validation.eval.md    # 5 test cases
  bookkeeping.eval.md       # 4 test cases
  ...
```

## Origin

These skills are extracted from [JARVIS](https://github.com/kgan), a personal AI assistant with 72 specialized agents, ~200 tools, and 50+ domain skills. The agentic engineering patterns (OORT, PQL, Blueprint, Constitutional AI) power JARVIS's multi-agent orchestration system.

Ghengis Skills packages the **portable knowledge** — the methodology and domain expertise that works in any Claude session, without requiring the JARVIS server.

## Contributing

Skills follow the [superpowers](https://github.com/obra/superpowers) plugin format:

```
skills/{skill-name}/
  SKILL.md           # Main skill (YAML frontmatter + markdown)
  supporting-doc.md  # Optional supporting documents
evals/
  {skill-name}.eval.md  # Test cases
```

### Skill Format

```yaml
---
name: skill-name
description: When Claude should activate this skill — be specific about triggers
---

# Skill Name

Content here...
```

## License

MIT
