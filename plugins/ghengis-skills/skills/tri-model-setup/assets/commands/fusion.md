---
description: High-stakes only — all legs attempt independently, then merge with attribution (3x cost for one answer)
argument-hint: <task> [-- <fusion instruction>]
---

Run a FUSION round on: $ARGUMENTS

Ported from the pi fusion-harness /fusion, reimplemented on the native Workflow tool (which already does parallel fan-out + synthesis). Reserve this for judgement calls — three models rarely beat one at the same coding task. Never ask which legs to include — use every leg that's up.

1. **Split arguments**: text after ` -- ` is the fusion instruction; default instruction: "produce the single best merged answer".
2. **Fan out via the Workflow tool** (the user opted into orchestration by invoking /fusion): one agent per available leg, each answering the ORIGINAL task independently and decisively —
   - claude leg: a general-purpose agent (inherits session model)
   - gemini leg: the `gemini` agent (agentType), Flash unless the task is a deep judgement call, then Pro
   - codex leg: only if live; otherwise note it as dark
   Save each leg's full raw answer to `~/.claude/tri-model/fusion-runs/<timestamp>/<leg>.md`.
3. **Merge** (you are the fusion agent): produce the definitive merged result per the instruction. Where a major point comes from one leg, attribute it inline as [claude], [gemini], or [codex]. If the instruction calls for producing/rendering/running something, DO it — never describe commands for the user to run.
4. **Close with "Consensus & divergence"** — SHORT: where legs agreed, where they disagreed (cite legs and model names), and anything you discarded and why.
5. Name any created files after the pair/trio of legs (e.g. `fused-report-claude-gemini.md`) — a fused result is the product of all contributors, never just the merger.
