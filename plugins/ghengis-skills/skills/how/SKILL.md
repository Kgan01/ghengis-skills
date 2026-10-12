---
name: how
description: Use when the user asks a question about how existing code behaves and wants a written explanation back - "how does X work", "walk me through Y before I change it", "where should this live", "which module owns this", "is this the right layer". Dispatches read-only explorer subagents, then one explainer, and returns an onboarding-grade answer. Not for motivation or history (use why). Not for a full structural map, layer classification, or dependency graph (use code-intelligence).
allowed-tools: Read Grep Glob Bash Agent
---

# How

Explore the codebase to answer "how does X work?" questions. Produce an architectural explanation at the level of a senior engineer onboarding onto a subsystem: enough to build a working mental model, not so much that it reads like annotated source code.

## Port notes

| | |
|---|---|
| Source | `cursor/plugins/pstack` → `skills/how/` (mirror: `backnotprop/pstack`) |
| License | MIT |
| Credit | poteto |
| What changed | Cursor `Task` tool and the pstack model-settings file removed. Model slugs (grok, opus-xhigh) replaced by harness-neutral subagent dispatch. Added When to Use / When NOT to Use, the split against `code-intelligence`, Anti-Patterns, Cross-References. Prompt templates kept, tool names made harness-neutral. |

## When to Use

- "How does X work?", "walk me through the flow of Y", "what happens when Z is called"
- Before changing unfamiliar code, to get the mental model first
- Placement and ownership questions: "where should this live", "which package owns this", "is this the right layer"
- Onboarding a reader onto one subsystem

## When NOT to Use

- **Why** the code has its shape (history, rationale, tradeoffs) → `why`
- A whole-repo structural map, 6-layer classification, import graph, god-node ranking → `code-intelligence`
- A bug to find and fix → `systematic-debugging`
- A one-line fact you can answer with one grep → answer directly

## Dispatch convention

"Dispatch a subagent" means: Claude Code: Agent tool (`subagent_type: general-purpose`, or `Explore` for explorers); pi: the subagent tool. Tell every subagent it is **read-only**: no file writes, no commits. If the harness has no subagent tool, run each role yourself, one after another, and keep the same prompts.

Model choice follows `tri-model`: explorers can run on a fast tier because their job is fact-gathering; the explainer runs on the frontier tier because synthesis is judgement.

## Step 1. Assess complexity

If the scope is ambiguous, state your interpretation in one line and explore. The user can redirect.

- **Simple** (one module, a small utility, "how does function X work"): no explorers. One explainer explores and explains in one pass. Go to Step 2b.
- **Complex** (a subsystem across several files or services, a cross-cutting feature, an architectural overview): parallel explorers first, then the explainer. Go to Step 2a.

When in doubt, take the simple path.

## Step 2a. Explore (complex only)

Decompose the question into 2 to 4 exploration angles, each a distinct slice of the subsystem (for example: entry point and request path, data model and persistence, background jobs, external boundaries). Dispatch all explorers **in one message** so they run concurrently.

Each explorer gets `references/explorer-prompt.md` with `{QUESTION}` and `{EXPLORATION_ANGLE}` filled in. Then go to Step 3.

## Step 2b. Direct explain (simple only)

Dispatch one explainer subagent. Build its prompt from `references/explainer-prompt.md` and delete the Explorer Findings section. Go to Step 4.

## Step 3. Synthesize (complex only)

When every explorer has returned, dispatch one explainer subagent. Build its prompt from `references/explainer-prompt.md` with every explorer's findings pasted into `{EXPLORER_FINDINGS_ALL}`. The explainer reconciles overlaps, resolves contradictions by reading the code itself, and keeps open questions visible.

## Step 4. Present

Present the explainer's output. Light edits for clarity or for context from the conversation are fine. Do not substantially rewrite it, and do not delete its open questions.

## Output Format

The sections from `references/explainer-prompt.md`, dropping any that do not apply: **Overview, Key Concepts, How It Works, Where Things Live, Gotchas.** Prose over pseudocode. Concrete file and function names. A diagram (mermaid or ASCII) only when the flow crosses several components.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Guessing behavior from file and function names | Names lie; the explanation becomes fiction | Explorers must read the implementation, not infer it |
| Spawning explorers for a one-function question | Cost and latency for no gain | Simple path: one explainer, one pass |
| Explorers with overlapping angles | Duplicate work, contradictory findings | Give each explorer a distinct slice |
| Dispatching explorers one at a time | Serial latency | Launch all explorers in one message |
| Rewriting the explainer's output heavily | Loses the reconciled facts and citations | Light edits only |
| Hiding gaps ("I couldn't trace X") | Reader acts on a false-complete model | Keep Open Questions in the answer |
| Answering a "why" question with "how" | Mechanics are not motivation | Hand off to `why` |
| Letting a subagent edit files | `how` is read-only by contract | State read-only in every prompt |

## Cross-References

- **`why`** — companion. `how` explains what the code does; `why` explains what forces shaped it. `why` often runs `how` first to anchor the code.
- **`code-intelligence`** — structural methodology (layers, import graph, AST). Use it for a repo-wide map; use `how` to answer one question in prose.
- **`blast-radius`** — run after `how` when the next step is a change and you need its impact.
- **`interrogate`** — review of a diff once the change exists.
- **`tutoring`** — when the user wants to be taught the subsystem step by step, not handed an explanation.
- **`tri-model`** — decides which model tier runs explorers and the explainer.
- **`agent-teams`** — general parallel fan-out pattern that Step 2a is an instance of.
