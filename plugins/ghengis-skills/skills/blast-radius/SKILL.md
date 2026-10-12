---
name: blast-radius
description: Use when a change is about to ship and you need to know what it could break somewhere else, beyond the diff - and prove the one fact it is safe because of by running real code instead of writing an essay. TRIGGER on "blast radius of X", "what could this break", "is this safe to merge", "what else does this touch", "I don't trust this small diff", or before merging a change to shared state, a wire format, a library pin, or a teardown path.
allowed-tools: Read Grep Glob Bash Write
---

# Blast Radius

Find what a change breaks somewhere else, before it ships.

## Port notes

| | |
|---|---|
| Source | poteto/pstack, `skills/blast-radius/SKILL.md` |
| License | MIT |
| Credit | poteto (cursor/plugins/pstack; mirror backnotprop/pstack) |
| What changed | `arena` multi-model step now uses the tri-model legs (Claude judges, codex + agy review independently). `unslop` replaced by `storyscope` then `humanizer`. Added When to Use, Anti-Patterns, Cross-References. Harness-neutral wording (Claude Code and pi). |

Companion to `how` and `why`. `how` tells you what the code does. `why` tells you why it is shaped that way. Blast radius tells you what it breaks somewhere else.

Listing the callers is not the job. Grep finds those in a second. **The job is the breakage grep will not show you.**

## When to Use

- "Blast radius of X", "what could this break", "is this safe to merge".
- Reviewing a small diff you do not trust yet.
- Any change to shared state, a serialized format, a DB column, a feature flag, a library version or local patch, lifecycle/teardown ordering, or code read by another language.

## When NOT to Use

- You need to know what the code does today: use `how`.
- You need to know why it is shaped this way: use `why`.
- A bug already happened: use `systematic-debugging`.

## Do Not Trust Your Own Writeup

A blast-radius writeup that sounds right is worthless. It reads as convincing whether or not it is true. Do not hand back the writeup alone. Find the one or two facts the whole thing depends on, and prove them by running code.

### How sure are you

For each fact the change's safety depends on, push it as far down this ladder as is cheap, and say where it stopped.

1. **You said so.** Worthless on its own.
2. **You pointed at the line.** A real `file:line`, or the library's own source.
3. **You showed the bad case cannot happen.** You walked the failure step by step and it does not reach.
4. **You ran it.** A script or test that calls the real code and fails loud if you are wrong.
5. **You reproduced it in the running app.**

Step 4 is usually one small script that imports the same library the app ships and calls the exact function you are worried about.

## Steps

1. **Read the change.** The diff, the symbols it adds, changes, and deletes, and what it now does differently, including the part the diff does not spell out. Use `why` (its step 2) to pull the PR and commits.
2. **Find the one fact it is safe because of.** Most changes that look risky are safe because of a single fact, like "this call only drops already-dead cache entries and does nothing else". Find that fact. If it holds, most risky cases clear at once. Spend your time here, not on a long list of maybes.
3. **Look where grep stops.** Read the source of the library you call, and check its pinned version and any local patch. Work out *when* things run: microtasks, unmount and teardown, framework scheduling differences (Solid versus React, sync versus async). Follow what a symbol search misses: the JSON an API returns, a DB column, a wire format, another language reading the same bytes, a feature flag, code three hops downstream.
4. **Be honest about each risk.** Give it a real chance of happening and a real cost if it does. Keep the risks you confirmed. List the ones you checked and cleared separately. Same rules as `why`: cite a real `file:line`; a search that finds nothing is still an answer; never make up a caller or an API.
5. **Prove the one fact.** Write a script or test that runs the real code, run it, and paste what happened.
6. **For a big or wide change, get more than one model on it.** Ask the same question to independent legs per `tri-model`: dispatch the Gemini leg (Claude Code: the `gemini` subagent; pi: shell `agy`) and the GPT leg (`codex exec`, or the codex plugin's adversarial review) with the diff and the question "what does this break outside the diff?". Claude merges and judges. Different models catch different real bugs. For a very wide change, fan out by seam with `agent-teams`.

When you delegate any of this, dispatch a subagent (Claude Code: Agent tool; pi: subagent tool) and require it to return `file:line` evidence and the ladder step it reached, never a bare summary.

## What to Hand Back

- **What it does.** What changed, including the part that is not obvious.
- **The one fact it is safe because of.** State it, say which ladder step you got it to, and show the proof. If you could not prove it, write **unproven**.
- **Risks.** Each names how it breaks, the `file:line`, how likely and how bad, and how to check. Paste the proof for the ones that matter.
- **Cleared.** What you checked and why it is fine.
- **Before you merge.** The cheapest test or repro that catches the real bug, including the script you wrote.

Write it through `storyscope` then `humanizer`, cite real code, and strip anything private before it goes anywhere public.

**Reply:** the writeup above, with the one safety fact either proven or marked unproven.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Handing back a list of callers | Grep does that in a second; it is not the breakage | Look where grep stops: runtime order, wire formats, other languages, flags |
| A long list of "maybe" risks | Spreads effort thin; hides the one fact that matters | Find the single safety fact and prove it |
| Stopping at ladder step 1-2 for the load-bearing fact | Convincing prose reads the same whether true or false | Get it to step 4: a script that calls the real code |
| Reasoning about a library from memory | Pinned version or local patch may differ | Read the installed source and the patch |
| Inventing a caller or API to make a risk sound real | Fabricated evidence poisons the review | Cite a real `file:line`; "search found nothing" is an answer |
| Mixing confirmed risks with cleared ones | Reader cannot tell what to act on | Separate Risks and Cleared sections |
| Calling it safe when the proof did not run | False confidence ships the bug | Mark the fact **unproven** |
| One model reviewing a wide change alone | Same blind spots as the author | Independent tri-model legs, Claude judges |

## Cross-References

- **`how`** / **`why`** - companions: what the code does, and why it is shaped this way. `why` step 2 pulls PR and commit history.
- **`systematic-debugging`** - when the breakage already happened.
- **`test-driven-development`** - turn the "Before you merge" repro into a committed regression test.
- **`tri-model`** - which legs review a wide change; **`agent-teams`** - fan-out by seam.
- **`show-me-your-work`** - log the proof script and verdict when this is part of a long run.
- **`engineering-principles`** - `principles/prove-it-works.md` for the falsifiable-proof standard.
- **`storyscope`** then **`humanizer`** - final pass on the writeup.
