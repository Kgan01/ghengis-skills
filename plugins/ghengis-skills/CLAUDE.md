# Ghengis Skills

> Claude Code skills plugin — 42 skills covering agentic engineering, agent reliability, learning/adaptation, and domain expertise.

## Structure

```
skills/           # 42 skill directories, each with SKILL.md
evals/            # Evaluation test cases per skill
hooks/            # Claude Code hooks configuration
agents/           # Subagent prompt templates
docs/             # Plans, architecture
.claude-plugin/   # Plugin metadata for marketplace
```

## Skill Categories

| Category | Count | Skills |
|----------|-------|--------|
| Agentic Engineering | 7 | oort-cascade, meta-prompting, agent-teams, pql-validation, blueprint-compilation, constitutional-ai, project-scaffold |
| Agent Reliability | 4 | completion-enforcer, hallucination-detector, context-health, execution-harness |
| Agent Learning | 5 | goal-tracking, agent-identity, skill-memory, audit-ledger, compute-adaptation |
| Deep Research | 1 | deep-research |
| Domain - Everyone | 10 | general-research, bookkeeping, task-tracking, learning-paths, tutoring, shopping, report-writing, scheduling, crm-patterns, file-organization |
| Domain - Developers | 4 | mcp-patterns, data-analysis, content-writing, devops |
| Domain - Unique | 3 | music-curation, home-lighting, 3d-modeling |
| Domain - Operations | 2 | output-formatting, proactive-rituals |
| Domain - Security | 2 | security-testing, code-intelligence |
| Frameworks | 4 | react-nextjs, fastapi, flutter-dart, esp32 |
