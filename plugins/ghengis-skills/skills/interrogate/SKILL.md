---
name: interrogate
description: Use when the user wants a diff, branch, PR, or set of files stress-tested by several model families before it ships - "interrogate this", "tear this apart", "adversarial review", "multi-model review", "challenge this", "find blind spots", "stress test this code". Sends the same rubric to a Claude subagent, the codex (GPT) leg, and the agy (Gemini) leg, then the host judges the findings into Act On / Consider / Noted / Dismissed. Produces a verdict only; never auto-applies fixes.
allowed-tools: Read Grep Glob Bash Agent
---

# Interrogate

Dispatch one reviewer per model family to adversarially review code changes. Every reviewer gets the same prompt and rubric. The adversarial signal comes from **model diversity**, not from assigned personas.

The deliverable is a synthesized verdict. **Do NOT auto-apply changes.**

## Port notes

| | |
|---|---|
| Source | `cursor/plugins/pstack` → `skills/interrogate/` (mirror: `backnotprop/pstack`) |
| License | MIT |
| Credit | poteto |
| What changed | The Cursor `Task` reviewers and the pstack settings file (opus / grok slugs, slug-fallback rules) are replaced by the three tri-model legs: Claude subagent, codex (GPT), agy (Gemini), invoked exactly as `tri-model` and the `gemini` agent do. Leg-down handling added. Rubric, code-quality lens, reviewer prompt, lead-judgment framework, and output format kept. |

## When to Use

- Before merging a non-trivial branch or PR, when the user asks for a hard review
- After a risky change (concurrency, auth, migrations, money, data loss paths)
- When one model built it and nobody else has looked (`tri-model`: never graded only by the builder)

## When NOT to Use

- Iterating a deliverable until it is excellent → `gauntlet` (worker + blind critic rounds)
- A quick single-leg review of a normal change → `tri-model` mode B (one Flash review)
- No diff exists yet → `brainstorming` or `how`
- The user wants the fixes made → run this first, then fix only what they approve

## Step 1. Determine scope

- User points at files or a diff → use that
- On a feature branch → `git diff main...HEAD` (or the right base) for the whole changeset
- Recent work referenced → gather the relevant files

Package the diff plus the surrounding context files a reviewer needs (callers, types, tests). Write the bundle to a scratch file (e.g. `<scratch>/interrogate/bundle.md`); the external legs read prompts from files.

## Step 2. State the intent

One clear paragraph from the user's message, commit messages, PR description, and the code. Unsure of the intent → ask before proceeding. Reviewers challenge the execution, never the intent.

## Step 3. Dispatch the reviewers

Build ONE prompt from `references/reviewer-prompt.md`, filled with: (1) the intent, (2) the diff or files, (3) `references/rubric.md`, (4) `references/code-quality-review.md`. Save it as `<scratch>/interrogate/prompt.md`. **Every leg gets this identical file.**

Check legs only when in doubt: `agy models` and `codex login status`. A leg that errors is **dark**: proceed with the others and record it. With only one leg live, say plainly that the review is single-model and the consensus signal is absent.

Launch all live reviewers **in one message** so they run concurrently:

| Reviewer | Leg | Claude Code | pi |
|---|---|---|---|
| A | Claude | Agent tool, `subagent_type: general-purpose`, top tier, prompt = the file contents, plus "Read-only: do not edit files or run mutating commands." | Bash: `claude -p < <scratch>/interrogate/prompt.md > <scratch>/interrogate/claude.md` (real `claude` binary on the Max plan) |
| B | GPT (codex) | Agent tool, `subagent_type: codex:codex-rescue`, prompt = the file contents prefixed with "Read-only review. Do not edit files." (the runtime then omits `--write`) | Bash, below |
| C | Gemini (agy) | Agent tool, `subagent_type: gemini`, with "use `-Model flash-high` (adversarial review) and `-Cwd <repo>`; return the answer verbatim" | Bash, below |

Direct Bash forms (work in both harnesses; use them when the agent types are absent):

```bash
# B — codex, read-only sandbox, repo as working root, last message to a file
codex exec --sandbox read-only --ephemeral -C <repo> \
  -o <scratch>/interrogate/codex.md - < <scratch>/interrogate/prompt.md

# C — Gemini via the agy wrapper (auto-logs to ~/.claude/tri-model/agy-usage.jsonl)
powershell -NoProfile -File "C:/Users/krist/.claude/scripts/agy-call.ps1" \
  -PromptFile <scratch>/interrogate/prompt.md -Model flash-high -Cwd <repo>
```

Gemini tier: `flash-high` is the default for adversarial review; use `-Model pro` only if `flash-high` already failed on this task or the user asks for Pro. Codex model: leave unset (plan default). Auth errors: Gemini → "run `agy` once and sign in with the PERSONAL Google account"; codex → "run `codex login`". Report the leg as dark and continue.

Never ask the user which legs to use. Route and state it in one line.

## Step 4. Synthesize

1. **Parse** every reviewer's findings.
2. **Consensus.** Findings raised by 2+ legs independently are highest signal.
3. **Lone-leg findings.** Still read them; weight accordingly.
4. **Deduplicate.** Merge the same issue described differently; record which legs raised it.
5. **Disagreements.** One leg flags it, another says the opposite: keep both for the verdict.

## Step 5. Lead judgment

You are the lead reviewer, a pragmatic senior engineer, not a neutral aggregator. Read `references/lead-judgment.md`. You have the conversation context the reviewers lacked; use it. Trace call sites before accepting a "what if null" finding. Be slow to dismiss security and correctness findings, even from one leg.

Categorize every finding:

- **Act on** — real correctness, security, or maintainability issues given the actual goals. Would block a real PR. Keep it to about 5; more means you are not filtering.
- **Consider** — legitimate, but the cost/benefit is unclear now.
- **Noted** — technically valid, not actionable at this stage.
- **Dismissed** — wrong, nitpicky, or missing context. One-line reason each.

Each finding carries: which leg(s) raised it, the bucket, and a one-line rationale.

## Output Format

### Intent
> [the Step 2 paragraph]

### Reviewers
- Reviewer A: claude/<model>, N findings
- Reviewer B: codex/<model>, N findings (or "dark — <reason>")
- Reviewer C: gemini/<tier>, N findings (or "dark — <reason>")

### Act On
[Description, legs that raised it, why it matters.]

### Consider
[Description, legs, the tradeoff.]

### Noted
[Brief list.]

### Dismissed
[Rejected findings with brief rationale. This is a trust mechanism: the user can override you.]

### Agreement Map
[Where legs agreed, where they diverged, and what the pattern says.]

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Different prompts per leg | Diversity signal is confounded by prompt differences | One prompt file, sent unchanged to every leg |
| Personas ("you are the security reviewer") | Replaces model diversity with role-play | Same rubric for all; diversity comes from families |
| Auto-applying the findings | The verdict is the deliverable; the user decides | Stop after the verdict |
| Aggregating instead of judging | Nitpick gravity floods the user | Filter with `lead-judgment.md`; ~5 Act On max |
| Hiding dismissed findings | User can't override your judgment | Always list Dismissed with reasons |
| Blocking because a leg is dark | Availability is not permission to stall | Proceed, mark the leg dark, note lost consensus |
| Reviewers sequentially | Slow; later legs can be anchored by earlier output | One message, all legs concurrently |
| Giving the codex leg write access | A review run must not mutate the repo | `--sandbox read-only` / "Read-only review" prefix |
| Questioning the intent | Out of scope; reviewers judge execution | State intent up front; ask the user if unsure |

## Cross-References

- **`tri-model`** — leg economics and availability rules; this skill is its "adversarial review" route for a whole changeset.
- **`gauntlet`** — iterative polish loop when the goal is "make it great", not a one-shot verdict.
- **`how`** — when a finding depends on behavior you have not traced.
- **`blast-radius`** — size the impact of an Act On fix before making it.
- **`ponytail-review`** — sibling review skill; use for its own lens, not as a substitute for cross-family review.
- **`engineering-principles`** — the principles the code-quality lens leans on (`principles/<x>.md`).
- **`test-driven-development`** — every Act On correctness finding gets a failing test first.
- **`security-testing`** — deep follow-up when a security finding is accepted.
