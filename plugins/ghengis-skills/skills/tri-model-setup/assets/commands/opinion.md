---
description: Two-model side-by-side — Claude and Gemini (and Codex when live) answer the same question independently
argument-hint: <question>
---

Run an OPINION round on: $ARGUMENTS

Ported from the pi fusion-harness /opinion. Never ask which legs to use — dispatch every leg that's up. Rules:

1. **Dispatch the other legs FIRST, before forming your own answer** (so their answers cannot anchor yours, and they run while you work):
   - `gemini` agent with the exact question, prefixed by the opinion contract: "Answer the following directly and completely. Be decisive, do not hedge, do not ask questions."
   - If the Codex leg is live (codex CLI authed, quota available), also dispatch it via the codex plugin's delegation skill with the same contract. If dark, skip and say so in the output.
2. **Answer the question yourself** — directly and completely, decisive, no hedging, no questions back. You may use tools to ground the answer.
3. **Present side-by-side** with clear attribution:
   - `## [claude] <model>` — your answer
   - `## [gemini] <model>` — verbatim
   - `## [codex] <model>` — verbatim (or one line: "dark — quota")
   - `## Consensus & divergence` — SHORT: where answers agree, where they conflict (cite legs), and which answer you'd act on and why.

Do not merge the answers — that's /fusion. Opinion is for seeing the disagreement.
