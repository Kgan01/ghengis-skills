# Ghengis Skills

> 42 skills for Claude Code — agentic engineering, agent reliability, domain expertise.

## Structure

- `skills/` — Each subdirectory has a `SKILL.md` with frontmatter describing when to activate
- `evals/` — Test cases per skill
- `hooks/` — Hook configurations
- `agents/` — Subagent templates

Skills are self-describing. Claude discovers and loads them from frontmatter — no manual routing needed.
