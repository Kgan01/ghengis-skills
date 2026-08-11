---
description: Ask the Gemini leg directly (agy, Flash by default). "/gemini usage" shows quota evidence.
argument-hint: <question> | --pro <question> | usage
---

Gemini leg request: $ARGUMENTS

- If the argument is `usage`: read `~/.claude/tri-model/agy-usage.jsonl`, summarize calls/day, model split, total prompt+output chars this week, then remind: exact remaining quota lives in the agy TUI under `/usage`. Stop.
- Otherwise: strip a leading `--pro` flag (sets `-Model pro`; default is `-Model flash`), then run via PowerShell:
  `powershell -NoProfile -File "C:/Users/krist/.claude/scripts/agy-call.ps1" -Prompt "<the question>" -Model <flash|pro>`
  For questions longer than one line or containing quotes, write the prompt to a temp file in the scratchpad and use `-PromptFile` instead.
- Present Gemini's answer under a `[gemini]` header, verbatim. Add your own commentary only if the answer conflicts with something you know from this session — and label it as yours.
- If auth fails: tell Kaegan to run `agy` once in a terminal and sign in with the PERSONAL Google account (AI Pro), not Workspace.
