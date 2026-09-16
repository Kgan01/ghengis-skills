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

[![Skills](https://img.shields.io/badge/skills-62-blue?style=for-the-badge)](./plugins/ghengis-skills/skills/)
[![Evals](https://img.shields.io/badge/evals-51-green?style=for-the-badge)](./plugins/ghengis-skills/evals/)
[![Version](https://img.shields.io/badge/version-1.27.1-lightgrey?style=for-the-badge)](#changelog)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-orange?style=for-the-badge)](https://code.claude.com)
[![License](https://img.shields.io/badge/license-MIT-purple?style=for-the-badge)](#license)

**Make Claude smarter, faster, and more autonomous.**

</div>

62 skills for Claude Code: supervised build / debug / ship chains, a **tri-model harness** that puts Gemini and GPT to work alongside Claude (`/adw`, `/opinion`, `/fusion`, `/auto-validate`, `/gauntlet`), agent-reliability guards, and domain expertise across 20+ fields. Skills load on demand. Unlike MCP servers that add tool schemas to every message, a skill costs nothing until a task matches its trigger, and an autoloader makes sure the right one fires.

---

## Install

In Claude Code, run these four commands one at a time. Each block is one line you can copy and paste.

**1. Register the marketplace**

```
/plugin marketplace add Kgan01/ghengis-skills
```

**2. Install the plugin**

```
/plugin install ghengis-skills@ghengis-skills-marketplace
```

**3. Configure autonomous permissions** (safe dev tools allowed, destructive operations denied)

```
/ghengis-skills:setup
```

**4. Enable the terminal statusline** (model name + color-coded context bar; auto-detects `python3` vs `python`)

```
/ghengis-skills:install-statusline
```

**5. Fully restart Claude Code.** Use `/exit` or Ctrl+C, then run `claude` again. `/reload-plugins` is not enough: the statusline config and newly added skills are only picked up at startup.

All 62 skills are then available in every session (CLI, desktop, and mobile). Claude loads them automatically when a task matches.

### Optional: the tri-model rig

Adds Gemini (via Google's `agy` CLI) and GPT (via OpenAI's `codex` CLI) as extra legs, plus the `/adw` `/opinion` `/fusion` `/auto-validate` `/gauntlet` `/gemini` commands. See [Tri-Model Harness](#tri-model-harness).

```
/ghengis-skills:tri-model-setup
```

### Updating / force refresh

`/plugin update ghengis-skills` sometimes holds on to a cached old version. Any one of these forces a sync to GitHub `master`:

Inside Claude Code:

```
/ghengis-skills:reload-ghengis
```

PowerShell (Windows):

```powershell
irm https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py | python -
```

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/Kgan01/ghengis-skills/master/plugins/ghengis-skills/skills/reload-ghengis/scripts/refresh_plugin.py | python3
```

All three fetch the marketplace clone, reset it to `origin/master`, refresh the plugin cache, and update `installed_plugins.json`. You can run them as often as you like. The in-Claude command always downloads the **latest** refresh script from GitHub first, so an install carrying an old, buggy copy can still update itself. Then **fully restart Claude Code**. New skills, commands, and hooks may not register with `/reload-plugins` alone.

A SessionStart hook also checks GitHub for a newer version every 6 hours and mentions it on your next message if you are behind.

### For teams

Add the marketplace to a project's `.claude/settings.json` so teammates get it automatically:

```json
{
  "extraKnownMarketplaces": {
    "ghengis-skills-marketplace": {
      "source": { "source": "github", "repo": "Kgan01/ghengis-skills" }
    }
  },
  "enabledPlugins": {
    "ghengis-skills@ghengis-skills-marketplace": true
  }
}
```

<details>
<summary><strong>Autonomous permissions JSON</strong> (what <code>/ghengis-skills:setup</code> configures, for manual installs)</summary>

Add to `~/.claude/settings.json`. Claude can then work on safe operations without asking, while destructive ones stay blocked. Anything not on either list still prompts.

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

The allow list covers common dev tools plus the Claude-in-Chrome browser-automation tools. The deny list blocks `rm -rf`, force push, `sudo`, disk formatting, and process killing. `/ghengis-skills:setup` merges a slightly newer version of this list into your existing settings instead of overwriting them.

</details>

---

## Common Workflows

You rarely need to name a skill, because Claude loads them from their trigger descriptions. The **chains** in `skill-chain-supervisor` are the exception worth knowing: each phrase below starts a supervised multi-stage pipeline.

### "I want to build a new feature"

```
You: "let's build a feature for X" / "run feature-build on X"
```

1. **brainstorming** asks clarifying questions one at a time, settles the design with you, then offers three ways to execute: inline, a dispatched subagent, or a build-validate chain.
2. **test-driven-development** writes the failing test first and watches it fail, then writes the minimal code to pass and commits.
3. **build-validate** (nested) has a Validator try to *break* the work. A score below 7 sends it back to the Builder for another round (2 iterations max).

### "I want to fix a bug"

```
You: "fix this bug: X" / "run bug-hunt on X"
```

1. **systematic-debugging** reads the error, reproduces it, and checks recent changes. It proposes no fix until the root cause fits in one sentence with confirming evidence.
2. **test-driven-development** writes a regression test that fails for the *same* reason the user reported.
3. **build-validate** checks that the fix passes that test without breaking the rest of the suite, and rejects fixes that only mask the symptom.

### "Let's add a new skill"

```
You: "add a skill for X" / "port the Y skill from superpowers" / "run skill-port"
```

1. **brainstorming** pins down trigger conditions, anti-patterns, and cross-refs.
2. **writing-skills** runs TDD on documentation: a pressure scenario, a baseline subagent failure, then the SKILL.md, then a re-test.
3. **pql-validation** scores the frontmatter `description` and requires at least 0.7.
4. **build-validate** puts the new skill through adversarial scenarios, with the Validator trying to talk its way past the rules.

### "Ship this branch"

```
You: "ship this branch" / "run finish-line"
```

1. **finishing-a-development-branch** won't proceed while any test fails. It detects whether you're in a normal repo or a worktree, then offers merge / push+PR / keep / discard. Discarding requires an explicit "yes discard", and it never force-pushes to main.
2. **auto-project-sync** updates CLAUDE.md, MEMORY.md, and indexes to match what shipped. It runs only when needed and never blocks.
3. **audit-ledger** records the merge in a hash-chained log.

### "Just review this deliverable"

```
You: "run build-validate on this" / "ping-pong this" / "validate thoroughly"
```

Adversarial review of something that already exists: the Builder produces, the Validator tests and scores it independently, and the loop repeats while the score is below 7. For cross-model review and polish loops, see `/gauntlet` and `/auto-validate` below.

### Forcing a specific skill

```
You: "use the systematic-debugging skill on this"
```

Or invoke by full name, e.g. `/ghengis-skills:deep-research`.

---

## Tri-Model Harness

Claude Code acts as the **host**, and two other model families plug in as **legs**. **You describe the work; the harness picks the models.** It never asks which model to use. It routes by task shape and says in one line what it chose.

### The three legs

| Leg | How it's reached | Role |
|---|---|---|
| **Claude** (host) | this session + the Agent tool | Most of the work at the top tier: Opus / Fable for thinking and review, Sonnet / Haiku for already-specified execution |
| **Gemini** | the `gemini` agent → Google's `agy` (Antigravity) CLI, Google AI Pro subscription | Flash for fast dedicated tasks; Pro for cross-family critique (the default `/gauntlet` critic) |
| **GPT** | OpenAI's `codex` CLI + the first-party `codex@openai-codex` plugin, ChatGPT subscription | Real building work plus adversarial review. It fails in different ways than the other two, so it catches bugs they both miss |

If a leg is down or unauthenticated (`agy models` / `codex login status` errors), work continues on the remaining legs and the gap is noted in one line. A missing leg never blocks work.

### Economics doctrine: quality first

The harness grew out of a real failure: a router with no cost rules sent bulk build work to the metered GPT leg and used up a whole ChatGPT quota in days, while the unmetered Claude leg sat idle. The doctrine that came out of it:

- **All three plans are already paid for.** Quota that expires unused buys nothing, so switching to a cheaper model "to save money" saves nothing. Default to the strongest model that fits.
- **Frontier models for thinking**: design, review, judgment, anything ambiguous.
- **Fast models only for fully specified work** ("just do exactly this"), and always followed by a frontier review.
- **Nothing ships graded only by the model that built it.** Build on one family, review on another.
- **Keep every leg working.** An idle paid leg is waste, so codex gets real building work, not just reviews.
- **Route on evidence.** `python ~/.claude/tri-model/model_advisor.py --days 7` scores models from the harness's own logs (latency, failure rate, token volume, critic yield, overturned verdicts). Rows marked `[thin evidence]` don't have enough data to route on.

Default for a normal change (mode B): Claude builds, then **one** other leg reviews the diff (Gemini Flash, or codex `adversarial-review` when the change is risky).

### What `/ghengis-skills:tri-model-setup` installs

Tested end to end on Windows 11; macOS/Linux use the same manifest host with a different platform slug.

| Piece | Installed to |
|---|---|
| `agy` binary, fetched from Google's manifest with a SHA-512 check (it does **not** run Google's `install.cmd`, which hangs in agent shells), added to PATH through the registry API rather than `setx` | `%LOCALAPPDATA%\agy\bin` |
| `codex` CLI (`npm i -g @openai/codex`) + `codex@openai-codex` Claude Code plugin | global npm / plugins |
| `agy-call.ps1`: the Gemini wrapper (Flash default, `-Model pro`, file relay for long prompts, JSONL usage log) | `~/.claude/scripts/` |
| `gemini` agent | `~/.claude/agents/gemini.md` |
| The six slash commands | `~/.claude/commands/` |
| ADW definitions: `rosters.yaml` + 13 `workflows/*.yaml` | `~/.claude/tri-model/adw/` |
| `dashboard.py` (live ops console on `127.0.0.1:8321`), `model_advisor.py` (routing scorecard), `sync_check.ps1` (detects drift between deployed copies and the skill) | `~/.claude/tri-model/` |

It then runs both sign-ins. **agy**: browser OAuth with a 60-second window, handled by a ConPTY driver plus a clipboard watcher, so you only click *personal Google account → Sign in → Copy to Clipboard*. **codex**: `codex login` with a localhost callback, so nothing needs pasting. Usage logs go to `~/.claude/tri-model/agy-usage.jsonl`, and run artifacts go under `~/.claude/tri-model/*-runs/`.

### `/adw`: plain language → workflow @ roster

The front door for **tasks**. Say what you want, and the router picks a **workflow** (which phases run) and a **roster** (which models fill each role) from the YAML definitions, then runs it. `/adw list` prints both catalogs.

```
/adw the login form accepts empty passwords
→ Routing: bugfix @ balanced — failing behavior, pin with test
```

**Routing table**

| The request sounds like… | workflow | roster |
|---|---|---|
| "what/where/how does X work", recon, "look into" | `scout` | budget |
| something is broken / wrong behavior / failing test | `bugfix` | balanced |
| PRODUCTION IS DOWN / urgent | `hotfix` | frontier |
| architecture-risky, gnarly, "get this right" | `pingpong-plan-build` | pingpong |
| normal feature or change, done properly (default) | `sdlc` | balanced |
| quick feature / spike, no git ceremony | `plan-build-test` | balanced |
| production-critical fix | `plan-build-test` | frontier |
| chore, rename, dep bump, docs/changelog pass | `chore` | budget |
| bulk / private / experiments / "keep it private" | task-appropriate | local |
| "use your best models" / critical quality | task-appropriate | frontier |
| movie / video piece | `storyboard` → `render-cut` | balanced |
| part from a drawing / photo | `cad-part` | budget |
| demand letter (PHI) | `demand-letter` | local (locked) |

An explicit choice from you (a workflow name or `--roster`) is honored, but the router never asks for one.

**Workflows** (`assets/adw/workflows/`)

| Workflow | Phases | Default roster | What it's for |
|---|---|---|---|
| `scout` | scout | budget | Read-only recon: map the code, answer the question, propose options. No changes, no gates |
| `chore` | build → verify | budget | One cheap agent plus gates, for mechanical work |
| `bugfix` | diagnose → fix → verify → review | balanced | Pin the bug with a failing test, fix it, prove it with gates, review. TDD-shaped |
| `hotfix` | fix → verify → commit | frontier | Production is down: one frontier builder, tests only, immediate commit |
| `plan-build-test` | plan → build → verify → review | balanced | Frontier plan, workhorse build, code gates, fresh-eyes review. No git ceremony |
| `sdlc` | plan → build → verify → commit → review → document → commit-docs | balanced | The full cycle, for a normal change done properly |
| `pingpong-plan-build` | plan → critique → reconcile → build → verify → review | pingpong | Two frontier models argue over the plan before a workhorse builds it, for work where the plan is the risk |
| `storyboard` | treatment → shotlist → compile → manifest-check | balanced | Movie idea → style bible → shot list → per-model prompts, checked against a deterministic manifest. No render spend |
| `render-cut` | preflight → render → judge → revise-shots → assemble | balanced | Renders pending shots (**spends money**), has a VLM judge each clip, re-renders failures, assembles the cut |
| `cad-part` | read-drawing → feature-plan → generate → inspect | balanced | Drawing/photo → parametric build123d CAD (STEP), gated by a geometry inspector |
| `champion-gauntlet` | build → wowed → review | frontier | Gauntlet loop run as an ADW: elevate a champion page until a blind critic says WOWED |
| `site-page-gauntlet` | build → release | frontier | Page-by-page site rollout against a champion page, with preservation + WOWED + SHIP gates |
| `demand-letter` | preflight → ingest → extract → draft → judge (→ revise) | local, **locked** | PHI pipeline. The roster can never fall back to a cloud model |

The first seven are generic. Their default gates are `npm run typecheck/lint/test --if-present`, which a repo-root `.adw.yaml` can override. The last six are reference implementations that call project-specific scripts, so adapt their paths before use.

**Rosters** (`assets/adw/rosters.yaml`, the single source of truth for role → model; change models there, never in prose)

| Roster | Planner | Builder | Reviewer | Use |
|---|---|---|---|---|
| `quality` | Claude Fable | GPT-5.6 Sol (codex) | Claude Opus | Quality-first default doctrine |
| `specd` | Claude Haiku | Gemini 3.6 Flash | Claude Opus | Already-specified work: fast typing, frontier verification |
| `frontier` | Claude Fable | GPT-5.6 Sol | Claude Opus | Critical or gnarly work |
| `gpt` | GPT-5.6 Sol (high) | GPT-5.6 Terra | GPT-5.6 Luna | All-OpenAI option |
| `balanced` | GPT-5.6 Sol (high) | Gemini 3.6 Flash | Claude Sonnet | Frontier ends, workhorse middle |
| `budget` | Gemini 3.1 Pro | Gemini 3.6 Flash | Gemini 3.5 Flash | Chores and docs. All-Gemini, no cross-provider dependency |
| `pingpong` | Claude Fable **vs** GPT-5.6 Sol | Gemini 3.6 Flash | Claude Sonnet | Two planners debate |
| `local` | gpt-oss:120b | gpt-oss:120b | qwen3.6:35b | $0 and private, via a local Ollama at `OLLAMA_HOST`. Unavailable when no endpoint is reachable |

**How a run executes:** one visible task per phase (the live progress view) and a run dir at `~/.claude/tri-model/adw-runs/<timestamp>-<slug>/`, with one envelope per phase plus `metrics.jsonl`. `agent` phases go to the leg their roster names (`claude-cli/*` → Agent tool, `google/*` → `gemini` agent, `openai-codex/*` → `codex exec`, which falls back to Sonnet when down). `gate` phases run shell commands, and a repo-root `.adw.yaml` `gates:` list overrides them. When a gate fails, its output goes back to the **same** build agent, up to `max_retries` times. After that the run stops and offers one step up in roster (budget → balanced → frontier).

### `/opinion`: see the disagreement

For **questions**, not tasks. The other legs are dispatched *before* Claude forms its own answer, so nothing anchors on Claude. Every live leg answers independently and decisively. The output is `[claude]`, `[gemini]`, and `[codex]` sections (a dark leg gets one line), plus a short **Consensus & divergence** section saying which answer to act on. Nothing is merged; merging is `/fusion`'s job.

### `/fusion`: one merged answer for high stakes

```
/fusion <task> [-- <fusion instruction>]
```

Every live leg attempts the task independently in parallel, and the raw answers are saved to `~/.claude/tri-model/fusion-runs/<timestamp>/`. Claude then merges them into the single best result, tagging major points `[claude]` / `[gemini]` / `[codex]`, and closes with consensus and divergence. **It costs about 3x for one answer**, and three models rarely beat one on the same coding task, so save it for judgment calls where the stakes are high.

### `/auto-validate`: prove it's done

The definition of done is an **executable script written before any work starts**, by an agent that never touches the code. A blind validator (preferably the Gemini leg) inspects the project read-only and writes `gate.py`, a `uv` single-file script that maps every explicit requirement to an objective check and must **fail** against the current state. Claude then builds and runs `uv run gate.py`, treating the `FAIL:` lines as correction instructions, for up to 3 rounds. Repo `.adw.yaml` gates must pass too. The task is never marked complete while the gate exits non-zero, and if the gate itself is wrong, that gets said openly instead of being quietly edited. Requires `uv`.

### `/gauntlet`: make an existing thing wow

```
/gauntlet <deliverable> [-- <the bar>] [--rounds N]
```

A polish loop for **something that already exists**: a page, module, doc, deck, or CAD part. Round 0 writes a **reference-anchored bar**, which describes the best conceivable version of *this* artifact in named, concrete attributes. The bar must always demand substance, depth, honesty, and craft, not just looks. Then each round:

1. The **worker** (Claude, warm session) improves the deliverable.
2. **Deterministic checks** run first at $0. If any fail, that list becomes the feedback and the critic is skipped.
3. A **blind critic** from a different family (Gemini Pro) gets only the bar and the deliverable, with no history, and returns `VERDICT: WOWED` or `NOT_WOWED` with its differences.
4. The defects go back to the worker framed as *"flaws to REMOVE or RESOLVE — not features to add"*.

The loop stops at WOWED or at the round cap (default 9), which is reported honestly as **PARTIAL**. A fresh-eyes reviewer (codex when live) compares round 1 with the final version, and `report.md` records the convergence.

### `/gemini`: direct line to the Gemini leg

```
/gemini <question>        /gemini --pro <question>        /gemini usage
```

Runs `agy-call.ps1` (Flash by default, `--pro` for Pro) and relays the answer verbatim under `[gemini]`. `/gemini usage` summarizes the local usage log. Exact remaining quota lives in agy's own `/usage`.

### Which one when

| You have… | Use |
|---|---|
| a **task** to get done | `/adw` |
| a **question** where you want independent views | `/opinion` |
| a **high-stakes** call that needs one merged answer | `/fusion` |
| a need to **prove it's done** | `/auto-validate` |
| an existing thing that should **wow** | `/gauntlet` |
| a quick one-off for Gemini | `/gemini` |

Done first, then wow: `/auto-validate` proves a request is complete, and `/gauntlet` takes a finished thing further. With the `tri-model` skill loaded, plain chat follows the same routing without any command.

---

## Chains, Cognition Loop, and a Worked Example

### How chains work

Chains compose skills into supervised pipelines that share a JSON scratchpad at `<project>/.claude/ghengis-chain/context.json`. Each stage reads earlier stages' output, invokes a skill (or a nested chain), and writes its results back under its own key. There are 7 built-in chains: `agent-dispatch`, `task-complete`, `build-validate`, `feature-build`, `bug-hunt`, `skill-port`, `finish-line`. They support sequential, fan-out/merge, conditional, iterative-loop, and nested patterns.

```bash
python scripts/scratchpad.py init feature-build --input-json '{"user_request":"..."}'
python scripts/scratchpad.py finish     # archives to history/, optionally emits a lesson
```

### Cognition loop (opt-in learning)

Set `GHENGIS_COGNITION=true` in your shell or in a project's `.claude/settings.json` `env` block, and chains start learning from outcomes:

- **At init**: past lessons from `<project>/.claude/ghengis-chain/cognition.jsonl` are ranked by UCB1-weighted Jaccard similarity to the current request. The top 5 land in `state.lessons_from_past`, and each one's `hits` count goes up.
- **At finish**: a success adds a `win` to every retrieved lesson, and a new lesson entry is written. The `analyzer` subagent can replace the heuristic lesson with a structured causal one.
- **Maintenance**: `python scripts/scratchpad.py audit` flags lessons with `hits ≥ 5` and `win_rate < 0.4` for retirement.

Turn it on for repeat-structure and long-running projects. Leave it off for one-off spikes, privacy-sensitive work, or when debugging the chain system itself.

<details>
<summary><strong>Worked example: <code>bug-hunt</code> end to end</strong></summary>

A real run fixing a scientific-notation bypass in a banking amount validator:

```
You: "run bug-hunt on this — the banking guard validator accepts 1e-5 as a
      valid amount but should reject it"

Claude: [systematic-debugging]
  Probe: str(0.00001) returns '1e-05' — no '.' — so the decimal-place check
  never triggers. Root cause: string-based validation misses scientific notation.

  [test-driven-development]
  test_amount_scientific_notation_blocked → FAILED as expected. Red confirmed.

  [build-validate — nested]
    [Builder]     Decimal-based validation + NaN/Inf rejection.
    [Validator]   8/10. Four more bypasses: whitespace padding, PEP 515
                  underscores ('1_000'), leading '+1.00', loose NaN assertion.
    [Builder 2]   Regex pre-check + 9 new regression tests.
    [Validator 2] 9/10. Unicode digits still bypass (\d is Unicode) — documented.

  [report] Outcome: fixed. 8 → 9. Full suite 132/132 green.

You: "ship this branch"

Claude: [finish-line] pytest 132 passed ✓ — merge / PR / keep / discard?
You: "2"
Claude: PR #142 opened. [auto-project-sync] docs updated.
        [audit-ledger] entry recorded. Outcome: integrated.
```

The Validator catching cases the Builder missed is the whole point, and the leftover Unicode-digit gap was surfaced openly instead of shipping silently.

Sample `cognition.jsonl` entry:

```json
{
  "id": "01577cb27c7d1386",
  "chain": "bug-hunt",
  "outcome": "fixed",
  "final_score": 9,
  "lesson": "bug-hunt required revision loop; iteration 2 succeeded",
  "causal_factor": "whitespace ' 1.00 '; PEP 515 underscore '1_000'; leading '+1.00'",
  "applies_when": "bug-hunt | banking guard validator accepts 1e-5 scientific notation",
  "iterations_used": 2,
  "hits": 0,
  "wins": 0,
  "audit_status": "unchecked"
}
```

</details>

---

## Skills

All 62, grouped by what they do. Most fire automatically from their trigger descriptions. The rest you run explicitly as `/ghengis-skills:<name>`.

### Tri-Model Harness (2)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **tri-model** | Routing doctrine for the Claude + Gemini + GPT harness: quality-first economics, cross-family review by default, the `/adw` `/opinion` `/fusion` `/auto-validate` `/gauntlet` command family, and till-done execution with visible task lists. The user never picks models. | Auto-fires on non-trivial build/fix/review/decide work when the legs are installed, and on *"get this right"* or *"second opinion"*. See [Tri-Model Harness](#tri-model-harness). |
| **tri-model-setup** | Installs the rig on a bare machine: agy + codex + the codex plugin, then deploys the wrapper, `gemini` agent, six commands, ADW YAMLs, dashboard, and advisor. Handles the agy OAuth steps and known npm/PATH gotchas. | `/ghengis-skills:tri-model-setup`, or *"set up the tri-model rig"*. |

### Plugin & Setup (4)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **setup** | Merges safe-by-default autonomous permissions into `~/.claude/settings.json` (dev tools allowed, destructive operations denied). | `/ghengis-skills:setup` once after install. |
| **install-statusline** | Installs the agent-monitor terminal status bar (model name + color-coded context usage). Auto-detects `python3` vs `python`; safe to re-run. | `/ghengis-skills:install-statusline`, then a full restart. |
| **reload-ghengis** | Force-syncs the plugin from GitHub `master`, bypassing `/plugin update` caching. Always runs the latest refresh script, falling back to the bundled copy only when offline. | `/ghengis-skills:reload-ghengis`, then a full restart. |
| **using-ghengis-skills** | The autoloader, injected at session start, which makes Claude check for and invoke a matching ghengis-skill before responding. | Always on. No invocation needed. |

### Agentic Engineering (8)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **oort-cascade** | Multi-agent orchestration: splits complex tasks into roles (researcher, builder, validator), wires them into dependency DAGs, runs parallel waves, and loops revisions until quality passes. | Auto-fires on complex multi-step requests. Force: *"run a cascade"*. |
| **meta-prompting** | 22 role templates that generate tailored subagent instructions (context injection, deliverable specs, execution boundaries) instead of forwarding raw requests. | Auto-fires when dispatching subagents. Used by the `agent-dispatch` chain. |
| **agent-teams** | Parallel agents with different creative perspectives (Minimalist, Bold, Technical, Playful, Elegant), with the strongest elements combined into one result. | *"give me 3 different takes on X"*, *"parallel perspectives"*. |
| **agent-monitor** | Real-time subagent dashboard and terminal status line, tracking spawns, completions, permissions, and history. | Always on once installed. Browser dashboard at `http://localhost:7685` when 2+ agents run. |
| **pql-validation** | Prompt Quality Layer: 35 anti-pattern checks across task, context, format, scope, reasoning, and agentic categories. | *"check this prompt"*. Wired into `agent-dispatch` (0.5 + autofix) and `skill-port` (0.7). |
| **blueprint-compilation** | Spots repeated multi-step workflows and compiles them into reusable pipelines (trace recording → pattern detection → progressive compilation). | *"I keep doing the same thing, let's automate it"*. |
| **constitutional-ai** | 9 safety rules across Safety, Cost, Privacy, Transparency, and Autonomy. Pre/post execution checks block irreversible actions, PII exposure, and scope creep. | Always-on guardrail. |
| **project-scaffold** | Generates a 4-layer self-documenting project structure: MEMORY.md, CONTEXT.md, per-workspace guidance, and a modular `.claude/` directory. | *"scaffold this project"*, or `/ghengis-skills:project-scaffold`. |

### Agent Reliability (4)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **completion-enforcer** | 70+ signal phrases catch "done" claims that still contain placeholders, TODOs, or unfinished work. Zero cost, instant. | Auto-fires after any "done" / "fixed" claim. Used in the `task-complete` and `agent-dispatch` chains. |
| **hallucination-detector** | Signal-based detection of fabricated URLs, unsourced statistics, fake citations, and impossible future claims, with no LLM verification call. | *"fact-check this"*. Used in the `task-complete` chain. |
| **context-health** | Tracks context usage and task drift, with three recovery strategies (truncate, checkpoint-restart, re-anchor). | *"are we still on track?"* in long sessions. |
| **execution-harness** | Multi-session execution: 3–15 checkpointed tasks, structured state files, pause/resume, and human review gates. | *"this is a multi-session project"*. |

### Agent Learning & Adaptation (8)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **skill-chain-supervisor** | Runs ghengis-skills as supervised chains over a shared JSON scratchpad: 7 built-in chains, nesting, per-stage `on_error`, and cognition emit + UCB1 retrieval. | *"run feature-build on X"*, *"bug-hunt this"*, *"ship this branch"*. See [Common Workflows](#common-workflows). |
| **evolving-cognition** | Pattern for agents that learn from measurable outcomes: fitness signals, cognition store schema, Analyzer prompts, UCB1 retrieval, poison mitigations, and audit loops. | *"learn from outcomes"*, *"agents getting smarter over time"*. |
| **auto-project-sync** | After a major work batch, refreshes code-graph data in MEMORY/CONTEXT/skill memory, appends dated TODO/CHANGELOG/lessons entries, mines cross-project habits, and promotes reusable permissions to global settings. | Auto after big batches, or `/ghengis-skills:sync`. |
| **goal-tracking** | Detects goals from conversation, keeps a parent-child hierarchy, tracks state transitions, and flags stale goals. | *"what was I working on?"* |
| **agent-identity** | Builds an evolving model of your preferences and working style through an observe → extract → synthesize loop. | Always observing. *"remember this preference"*. |
| **skill-memory** | Plain-markdown domain knowledge from past tasks. Searchable with grep, no vector DB, consolidates itself as it grows. | *"remember this for next time"*. |
| **audit-ledger** | Hash-chained (SHA-256) append-only audit trail of what agents did and why, queryable by time/agent/goal. | Used in the `finish-line` chain. *"audit log for today"*. |
| **compute-adaptation** | 4-tier graceful degradation (Normal / Low / Critical / Offline) for rate limits and budget pressure. | Auto-fires on rate limits. *"budget is tight, slow down"*. |

### Workflow Skills (5, ported from superpowers)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **brainstorming** | Turns ideas into designs through inline back-and-forth: one question per message, no plan mode, no picker. Ends with three execution options. | *"let's build X"*. Stage 1 of `feature-build` and `skill-port`. |
| **writing-skills** | TDD for documentation: pressure scenario → watch a subagent fail → write the skill → close loopholes. | *"let's add a skill"*. Used in the `skill-port` chain. |
| **systematic-debugging** | Iron law: no fixes without a root cause. Four phases: investigate, hypothesize, regression test, fix and verify. | *"this is broken"*, *"test is failing"*. Stage 1 of `bug-hunt`. |
| **test-driven-development** | RED-GREEN-REFACTOR in 2–5 minute steps, watching the test fail and then pass, with a commit per cycle. | Auto-fires on any testable behavior change. |
| **finishing-a-development-branch** | Verify tests → detect workspace → merge / PR / keep / discard → clean up. Won't proceed while tests fail. | *"ship this branch"*. Stage 1 of `finish-line`. |

### Research (3)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **deep-research** | 7-phase iterative method (Clarify, Draft, Gap Analysis, Targeted Research, Refine, Red Team, Converge) with confidence levels. | *"deep dive into X"*, *"red-team this"*. |
| **general-research** | One-pass rigorous research: CRAAP source evaluation, structured findings with confidence levels. | *"research X"*. |
| **paper-to-code** | Research paper / technical doc → shipping code: strategic reading, contribution mapping, spec deltas, and "what NOT to adopt". | Auto-fires on arxiv URLs and *"apply this paper"*. |

### Security & Code Analysis (3)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **security-testing** | OWASP Top 10, CVSS scoring, recon methodology, secure coding patterns, hardening checklists, for defensive and authorized testing. | *"security review of this"*, *"OWASP audit"*. |
| **code-intelligence** | 6-layer architectural classification, AST analysis, import graphs, circular dependency detection, structural search. | *"map the architecture"*, *"trace dependencies"*. |
| **treefile-organizer** | Reorganizes a project tree based on its real import graph. Analyzer + planner scripts produce a plan that is adversarially validated before any move. Python + TypeScript. | *"reorganize this project"*. Refuses on a dirty git tree and never moves files without an explicit "yes proceed". |

### Operations (2)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **output-formatting** | 8 destination formatters (chat, email, Slack, TTS, PDF, CSV, JSON, markdown) plus document ingestion and chunking. | *"format this for Slack"*, *"export as CSV"*. |
| **proactive-rituals** | Morning briefings, end-of-day summaries, weekly reviews, and custom rituals mapped to native cron scheduling. | *"set up a morning briefing"*. Pair with `/schedule`. |

### Domain Expertise (19)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **storyscope** | Makes papers, essays, blogs, and speeches read as human-written by fixing *structural* decisions (openings, delayed disclosure, closers, ambivalence, named sources, verbatim quotes), based on StoryScope (COLM 2026). Never invents material. | *"make this sound human"*, *"StoryScope this"*. Run before `humanizer`. |
| **content-writing** | Blog posts, docs, and marketing copy: structure, SEO basics, audience targeting, editorial checklists. | *"write a blog post on X"*. |
| **report-writing** | Executive summaries, data presentation, confidence levels, source citation. | *"write a report on X"*. |
| **data-analysis** | Statistical method, pandas workflows, correlation vs causation, visualization choice, small-sample warnings. | *"analyze this data"*. |
| **bookkeeping** | Double-entry accounting, chart of accounts, IRS categories, reconciliation, month-end close. | *"categorize these expenses"*. |
| **crm-patterns** | Client lifecycle, pipeline management, communication logs, relationship health scoring, follow-ups. | *"track this client"*. |
| **task-tracking** | GTD, Eisenhower matrix, sprint planning, decomposition, blocked-task handling. | *"prioritize this list"*. |
| **scheduling** | Time blocking, priority-based allocation, conflict resolution, calendar optimization. | *"schedule my week"*. |
| **learning-paths** | Bloom's taxonomy, prerequisite mapping, curriculum design, spaced repetition. | *"design a learning path for X"*. |
| **tutoring** | Socratic method, level assessment, scaled worked examples, misconception correction. | *"walk me through X"*. |
| **time-perception** | Time awareness for Claude: tracks elapsed time between messages, task durations, project switching, and activity patterns via hooks. | Always on once installed. |
| **shopping** | Product comparison frameworks, per-unit pricing, deal validation. | *"is this a good deal"*. |
| **file-organization** | 18 manifest types, placement suggestions, naming conventions, duplicate detection, audit trails. | *"organize these files"*. For import-graph restructuring, use `treefile-organizer`. |
| **mcp-patterns** | MCP server config, the meta-tool pattern for context reduction, Context7 two-step lookup. | *"set up an MCP server"*. |
| **devops** | Solo-dev deployment: Docker multi-stage, GitHub Actions, SSL, environments, rollback. | *"set up CI/CD"*. |
| **cad** | Parametric CAD from a description: brackets, enclosures, robot frames, panels. build123d code → STEP/STL/3MF/DXF + topology sidecar, verified by a geometry inspector. Needs the JARVIS pipeline + `build123d`. | *"design a bracket for X"*, requests for `.step` / `.stl`. |
| **3d-modeling** | STL mesh quality, supports, print orientation, tolerances, prompting for 3D generation. | *"prepare this STL for printing"*. |
| **music-curation** | Genre classification, BPM matching, mood mapping, playlist arc design. | *"make a playlist for X"*. |
| **home-lighting** | Color temperature, circadian automation, room profiles, scenes, Philips Hue API. | *"circadian scenes for sleep"*. |

### Framework Skills (4)

| Skill | What It Does | How to Use |
|-------|-------------|-----------|
| **react-nextjs** | Next.js 15 App Router, server/client boundaries, dynamic imports, Zustand, CSS-variable theming. | Auto-fires on Next.js / React work. |
| **fastapi** | Async-first patterns, Pydantic v2, dependency injection, WebSocket auth-before-accept, blocking-code handling. | Auto-fires on FastAPI routes. |
| **flutter-dart** | Widget composition, state management, platform channels, navigation, theming. | Auto-fires on `.dart` edits. |
| **esp32** | PlatformIO, I2S audio, PSRAM, FreeRTOS task pinning, WiFi/BLE, state machines. | Auto-fires on ESP32 firmware work. |

---

## How Skills Work

Each skill is a markdown file with YAML frontmatter:

```yaml
---
name: skill-name
description: When Claude should activate this skill — specific trigger conditions
allowed-tools: Read Write Edit Bash    # optional
disable-model-invocation: true         # optional — user-run only (setup, reload-ghengis…)
---

# Skill Name

Methodology, patterns, examples, checklists...
```

The `description` tells Claude when to load the skill. When a task matches, the skill's content is injected and guides the work. When nothing matches, nothing loads and the context cost is zero.

Some skills ship **supporting docs** (`oort-cascade/handoff-protocol.md`, `pql-validation/anti-patterns.md`, `treefile-organizer/plan-format.md`), **scripts** (`skill-chain-supervisor/scripts/scratchpad.py`, `treefile-organizer/scripts/analyzer.py` + `planner.py`, `reload-ghengis/scripts/refresh_plugin.py`, the tri-model wrapper/dashboard/advisor), or **assets** (the tri-model commands, agent, and ADW YAMLs). The Python scripts use only the standard library.

The plugin also ships **hooks** (`plugins/ghengis-skills/hooks/`) for time tracking, the autoloader, agent monitoring, chain lifecycle, completion checks, and the update notice, plus one command: `/ghengis-skills:sync`.

## Subagents

The plugin ships 7 subagents with isolated context (`plugins/ghengis-skills/agents/`). The tri-model rig adds an 8th, `gemini`, in `~/.claude/agents/`.

| Subagent | Role |
|---|---|
| `ghengis-skills:researcher` | Codebase exploration, doc review, context assembly. Structured findings with sources. Read-only. |
| `ghengis-skills:validator` | Scores deliverables 0–10 across fulfillment, accuracy, completeness, tone, and formatting, with revision feedback. The V in build-validate. |
| `ghengis-skills:fact-checker` | Checks every factual claim and labels it VERIFIED / DISPUTED / UNVERIFIABLE, with an overall accuracy percentage. |
| `ghengis-skills:editor` | Polishes clarity, tone, flow, and grammar. Returns the full edited version with `[EDITED]` markers. |
| `ghengis-skills:analyst` | Metrics, comparisons, trends, anomalies. Precise with numbers. |
| `ghengis-skills:security-reviewer` | PII exposure, injection, credential leaks, OWASP Top 10. APPROVED / FLAGGED with severity. |
| `ghengis-skills:analyzer` | Reads a finished chain's scratchpad and writes a structured causal lesson to `cognition.jsonl`, marking contradicted entries. Haiku-tier by default. |

## Evals

51 skills have evaluation cases in `plugins/ghengis-skills/evals/`: scenarios with specific assertions that check whether a skill produces methodology-driven output rather than a generic response. The 11 without evals are mostly installers and infrastructure (`setup`, `install-statusline`, `reload-ghengis`, `using-ghengis-skills`, `tri-model-setup`, `agent-monitor`, `time-perception`) plus `auto-project-sync`, `cad`, `evolving-cognition`, and `paper-to-code`.

```
evals/{skill-name}.eval.md

## TC-1: Complex Multi-Step Task
- prompt: "Research competitors, write a strategy doc, then review it"
- assertions:
  - Decomposes into researcher, builder, validator roles
  - Creates dependency DAG with parallel waves
  - Runs validation pass with scoring rubric
- passing_grade: 3/3
```

## Contributing

To add a skill (or just say *"let's add a skill"* and the `skill-port` chain walks you through it):

1. Create `plugins/ghengis-skills/skills/{skill-name}/SKILL.md` with YAML frontmatter.
2. Create `plugins/ghengis-skills/evals/{skill-name}.eval.md` with 3–5 test cases.
3. Keep skills focused: one domain, one methodology, with worked examples and checklists.
4. Test that the skill fires on the right triggers and stays quiet otherwise.
5. Bump the version in `plugins/ghengis-skills/.claude-plugin/plugin.json` and `package.json`, update the skill count in this README and `.claude-plugin/marketplace.json`, and add a [Changelog](#changelog) entry.

## License

MIT

---

## Changelog

Newest first.

### v1.27.1 (2026-09-16)

- **Public leak guard (`hooks/scripts/public_leak_guard.py`)**: the commit and push hooks now block when a change headed to a PUBLIC GitHub repo contains private data: your home-folder paths, Tailscale IPs, or anything in your personal denylist at `~/.claude/private-denylist.txt` (literal terms, `regex:` lines, and `folder-names:<dir>` so every "Last, First" client folder is protected automatically). The denylist lives outside every repo. Private repos are skipped; unknown visibility is treated as public. Escape hatch for a verified false positive: `GHENGIS_LEAK_GUARD=off`.
- History rewrite: a real client name that had been copied into an example workflow comment (v1.21.2) was scrubbed from all commits. If you cloned before 2026-09-16, re-clone or run the reload.

### v1.27.0 (2026-09-16)

- **README restructure.** Install moved to the top, with every step a single copy-paste line and separate PowerShell / macOS-Linux refresh commands. Common Workflows now follow install. New **Tri-Model Harness** explainer (legs, economics doctrine, what setup installs, `/adw` routing + all 13 workflows + rosters, `/opinion`, `/fusion`, `/auto-validate`, `/gauntlet`, `/gemini`, which-one-when). Skills tables now list all 62 skills. Counts corrected (62 skills, 51 evals). Changelog moved to the bottom.
- **`reload-ghengis` always runs the latest refresh script.** The skill downloads `refresh_plugin.py` from GitHub `master` and only falls back to the bundled copy when offline, so installs stuck on a buggy script (≤ v1.26.1 crashed on Windows consoles) can update themselves. It has Bash and PowerShell variants and now tells you to **fully restart** Claude Code, because new skills may not register with `/reload-plugins` alone.
- **Personal data scrubbed from shipped assets.** Tri-model commands and agent use `$HOME/.claude/scripts/agy-call.ps1`. Local-model endpoints resolve from `OLLAMA_HOST` (default `127.0.0.1:11434`). Hardcoded user paths, names, and a private network IP were removed from `tri-model`, `tri-model-setup` assets, and `cad`.

### v1.26.2

- `reload-ghengis`: force UTF-8 console output on Windows. Older copies crashed with `UnicodeEncodeError` under cp1252.

### v1.26.1

- `storyscope`: made the skill faithful to the paper line by line.

### v1.26.0

- **StoryScope (`storyscope`).** Human-sounding writing through structure instead of word swaps. Translates the 30 core narrative features from Russell et al. (COLM 2026, arXiv 2604.03136) into nonfiction moves: don't state the lesson in the closing slot, disclose late, keep a real cost of your own position, name sources, quote verbatim. Drafting mode puts the structural decisions to the author first. Revising mode extracts a skeleton, scores it with quoted evidence, and never fabricates texture.

### v1.25.x

- `tri-model`: quality-first routing doctrine + evidence-based `model_advisor.py` (v1.25.0).
- `tri-model-setup`: dashboard + advisor in the deploy table, `sync_check.ps1` (v1.25.1). Windows install no longer runs the hanging `install.cmd`, PATH via registry API, PS 5.1-safe sync check (v1.25.2).

### v1.21 – v1.24

- **Tri-model harness** (v1.21.2): `tri-model` routing doctrine + `tri-model-setup` with agy/codex installs, auth steps, wrapper, agent, and commands.
- **`/gauntlet`** (v1.22.0): the Gauntlet Loop generalized to any deliverable. Critic BLOCKED protocol and an agy file relay for prompts over 25K (v1.22.2).
- Live leg-activity dashboard at `127.0.0.1:8321` (v1.22.3), gauntlet-hardened (v1.23.0), substance-first ops console + permanently high gauntlet bar (v1.24.0).

### v1.15 – v1.20

- `analyzer` subagent for high-quality cognition lessons (v1.15.0), auto-dispatched via hook (v1.16.0).
- `auto-project-sync`: code-graph data refresh (v1.17.0), registry-driven sync (v1.18.0), per-project cognition store (v1.19.0), wildcard synthesis from observed approvals (v1.20.0).
- `cad`: parametric build123d skill via the JARVIS pipeline.

### v1.12 – v1.14

- **Closed cognition loop** (v1.14.0): `GHENGIS_COGNITION=true` makes chain runs emit lessons and retrieve past ones via UCB1-weighted Jaccard similarity.
- **5 workflow skills + 4 chains** (v1.12.0): `brainstorming`, `writing-skills`, `systematic-debugging`, `test-driven-development`, `finishing-a-development-branch`, plus the `feature-build`, `bug-hunt`, `skill-port`, and `finish-line` chains.
- **`treefile-organizer`**: reshapes a project tree from its real import graph.

### v1.7 – v1.9

- **Time Perception** and **Agent Monitor** (v1.8.x): elapsed-time and project-switch awareness, plus the subagent dashboard and statusline.
- **`install-statusline`** with python3/python auto-detection (v1.8.19 / v1.9.3). `/refresh-ghengis` renamed to `/reload-ghengis`.
- **Evolving Cognition** and **Paper to Code** (v1.7.0).

### v1.1 – v1.6

- `using-ghengis-skills` autoloader (v1.4.0), auto-injected at session start (v1.6.0). PreToolUse:Agent prompt-quality hook (v1.6.1).
- `auto-project-sync` + `/sync` command (v1.5.0).
- Subagents + hooks (v1.1.0).
