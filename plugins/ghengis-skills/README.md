# Ghengis Skills

A Claude Code plugin that makes Claude smarter, faster, and more autonomous. It has **62 skills** (51 with evals): supervised build / debug / ship chains, a **tri-model harness** (Claude + Gemini + GPT: `/adw`, `/opinion`, `/fusion`, `/auto-validate`, `/gauntlet`, `/gemini`), multi-agent orchestration, prompt quality validation, agent reliability, security testing, code intelligence, and domain expertise across 20+ fields.

Skills load on demand. A skill adds nothing to your context until a task matches its trigger.

**The full guide lives in the [root README](../../README.md):** install, common workflows, the tri-model harness explainer, the complete skills tables, and the changelog. This page is only a summary, so it won't drift out of date.

## Install

In Claude Code, run each line separately:

```
/plugin marketplace add Kgan01/ghengis-skills
```

```
/plugin install ghengis-skills@ghengis-skills-marketplace
```

```
/ghengis-skills:setup
```

```
/ghengis-skills:install-statusline
```

Then **fully restart Claude Code** (`/exit`, then `claude`).

Optional tri-model rig:

```
/ghengis-skills:tri-model-setup
```

## Update / force refresh

```
/ghengis-skills:reload-ghengis
```

PowerShell:

```powershell
irm https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py | python -
```

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py | python3
```

Then fully restart Claude Code. New skills may not register with `/reload-plugins` alone.

## What's in this directory

| Path | Contents |
|---|---|
| `skills/` | 62 skills, one folder each (`SKILL.md` + optional docs, scripts, assets) |
| `evals/` | 51 `{skill}.eval.md` files with test cases and assertions |
| `agents/` | 7 subagents: researcher, validator, fact-checker, editor, analyst, security-reviewer, analyzer |
| `hooks/` | time tracking, autoloader injection, agent monitor, chain lifecycle, completion check, update notice |
| `commands/` | `/ghengis-skills:sync` |

## License

MIT
