---
name: why
description: Use when the user asks why code, a config, or a design has its current shape - "why is it like this", "why did we pick Y", "what was this for", "is this still needed", "where did this number come from", regressions and postmortems. Discovers which evidence sources exist at run time (git and gh, docs/ and docs/plans, TODO.md, the JARVIS brain, Claude memory dirs, Gmail or Drive when connected), dispatches one investigator per source, and returns a confidence-tiered, cited answer. For runtime behavior use how.
allowed-tools: Read Grep Glob Bash Agent WebFetch
---

# Why

Investigate the motivation and intent behind code. Companion to `how`: `how` answers what the code does; `why` answers what forces led to its shape.

## Port notes

| | |
|---|---|
| Source | `cursor/plugins/pstack` → `skills/why/` (mirror: `backnotprop/pstack`) |
| License | MIT |
| Credit | poteto |
| What changed | Cursor `Task`/readonly flags and the pstack model-settings file removed. The 7 enterprise evidence categories (Linear, Notion, Slack, Datadog, Sentry, Databricks) are remapped to this user's sources: git + `gh`, repo docs, TODO/issues, JARVIS brain, Claude memory dirs, Google Workspace MCPs, plus a generic playbook for any other MCP that happens to be connected. Discover-then-query shape, epistemics, and synthesizer contract kept verbatim. Added a secrets rule for memory sources. |

## When to Use

- "Why does X work this way?", "why did we pick Y over Z?", "what is this check for?"
- "Is this still needed?" / dead-code questions before deleting something
- "Where did this threshold/number come from?"
- Regressions and postmortems: what change introduced a behavior, and with what intent
- Before changing code whose purpose is unclear (output converts to Preserve / Change / Avoid / Risk)

## When NOT to Use

- How the code runs now → `how`
- A live bug with symptoms to fix → `systematic-debugging`
- The answer is in one commit message you already have open → quote it, answer inline (see the skip bar in Step 3)

## Operating Posture

Operate as a **careful, cautious, precise investigator**. Separate what you know from what you infer. Read `references/epistemics.md`; the synthesizer must follow it. The value of the output is its honesty, not its authority.

## Dispatch convention

"Dispatch a subagent" means: Claude Code: Agent tool (`subagent_type: general-purpose`); pi: the subagent tool. Investigators and the synthesizer must **not** be restricted to a read-only/plan mode that strips MCP tools, because MCP-backed investigators need them. They still must not write files, send mail, comment, or change external state. With no subagent tool, run each investigator yourself, one after another.

## Step 1. Understand the target and the question

The **target** is a chunk of code, a pattern, a feature, a config value, or a named decision. The **question** is a rationale, a tradeoff, a motivating edge case, an external constraint, dead code, or a history sweep. If the target is vague, guess from conversation context (open files, recent edits, what was just discussed), state your reading in one line, and proceed.

## Step 2. Establish the code anchor

Build it inline before any dispatch:

```bash
git blame -L <start>,<end> <file>          # last-touch commits for the target lines
git log --follow --oneline -20 -- <file>   # recent history through renames, PR numbers visible
git log --follow -p -- <file>              # full history with patches
git log -1 --format=%B <commit>            # PR numbers / ticket IDs in a message
gh pr view <n> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews
```

Capture: file paths and line ranges, key symbols, commit list, PR numbers, issue/TODO IDs (e.g. `#277`). This is the seed for every investigator.

## Step 3. Discover sources, then dispatch investigators

### Discovery (run every time; never assume)

Classify what is actually reachable this session into these categories. See `references/source-playbook.md` for the probe for each.

| # | Category | This user's sources | Probe |
|---|---|---|---|
| 1 | Source control | git, `gh` PRs/reviews, code comments, tests | Always available |
| 2 | Task / issue tracker | `docs/TODO.md`, `gh issue`, any tracker MCP | File exists? `gh auth status`? |
| 3 | In-repo long-form docs | `docs/`, `docs/plans/`, `docs/research/`, `.claude/docs/`, `CHANGELOG.md`, `MEMORY.md`, `CONTEXT.md`, ADRs | Glob for them |
| 4 | Agent memory | JARVIS brain (pi `brain_recall` tool, or `GET /brain/recall` on the JARVIS server), Claude memory dirs `~/.claude/projects/*/memory/`, `SKILL_MEMORY.md` | Tool in list? Host answers? Dir exists? |
| 5 | Cloud documents | Google Drive MCP, other doc MCPs | `mcp__*Drive*`-style tools in the tool list |
| 6 | Conversation record | Gmail MCP; Slack/Discord MCPs if ever connected | Tools in the tool list, auth succeeds |
| 7 | Runtime evidence | Any connected observability, error-tracking, deploy-log, or warehouse MCP (e.g. Vercel runtime logs, Supabase) | Tools in the tool list |

In Claude Code, MCP tools appear as `mcp__<server>__<tool>`; in pi, check the tool list and the MCP adapter's servers. Record ambiguous classifications in the coverage map. A category with no reachable source is a **gap**, written down, not silently dropped.

### Dispatch

Dispatch one investigator per reachable category, **all in one message**. One investigator owns exactly one category; never ask one agent to cover several. Each gets:

1. `references/investigator-prompt.md` (base prompt)
2. The single matching playbook from `references/sources/`
3. `references/sources/incident-postmortem.md` **if the target looks defensive** (null guards, retries, timeouts, rate limits, feature flags, egress guards, OOM handlers)
4. The code anchor from Step 2
5. The user's original question

### Skipping a category

Only with a written justification that appears in Sources Consulted. Two valid reasons: **no reachable source** (a gap, not a choice), or **provably irrelevant** (high bar, e.g. runtime evidence for a build-time script). A trivial single-commit target whose PR already holds the complete answer may be answered inline only after you state why every other category would be redundant. This should be rare.

## Step 4. Synthesize

Dispatch one synthesizer (frontier tier per `tri-model`). It gets all investigator findings including nulls and skips, the code anchor, the question, `references/epistemics.md`, and `references/synthesizer-prompt.md`. It may spot-check citations with tools; it must not write anything.

## Step 5. Present

Present the synthesizer's output. Light edits are fine; **do not rewrite the confidence language**. If the question precedes a change, convert the findings into a **Preserve / Change / Avoid / Risk** constraint set after Sources Consulted.

## Output Format

From `references/synthesizer-prompt.md`: The Question, The Code in Question, What We Found, What We Can Reasonably Infer, Competing Hypotheses, What We Don't Know, Sources Consulted (one line per category, including empty and skipped ones with the reason), Confidence Summary.

## Secrets rule

Memory dirs, the brain, and mail can hold credentials and personal data. Investigators quote only what bears on the question and never copy passwords, keys, tokens, or addresses into findings. Write "[credential redacted]" where a quote would carry one.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Recency bias: the last commit is "the reason" | Shape is an accretion of older decisions | Trace back with `--follow`, `-S`, `-G` |
| Citing code as evidence of its own intent | Code is mechanics, not motivation | Cite messages, PRs, docs, notes, memories |
| Hardcoding a source that isn't connected | Investigator fabricates or errors | Discover first; absent = gap |
| Skipping a category without writing why | User can't judge coverage | Every category gets a Sources Consulted line |
| One investigator covering several sources | Shallow, scope confusion | One investigator per category |
| Confirming the user's embedded hypothesis | Sycophancy trap | Treat it as one candidate; check independently |
| Picking the tidier of two contradicting sources | Hides the most useful finding | Surface both with citations |
| Filling a gap with a plausible guess | User acts on the guess | "We searched A, B, C and found nothing" |
| Copying a secret out of a memory file | Leaks credentials into chat/logs | Apply the secrets rule |

## Cross-References

- **`how`** — run first, or alongside, when the code's runtime behavior is itself unclear.
- **`blast-radius`** — consumes the Preserve / Change / Avoid / Risk set before a change.
- **`skill-memory`** — per-agent `SKILL_MEMORY.md`, one of the agent-memory sources.
- **`evolving-cognition`** — after the answer, record a durable lesson if the history taught one.
- **`hallucination-detector`** — useful check on the synthesizer's claims when evidence is thin.
- **`deep-research`** — when the "why" lives outside the repo (papers, vendor docs) rather than in its history.
- **`tri-model`** — tier choice for investigators (fast) and synthesizer (frontier).
