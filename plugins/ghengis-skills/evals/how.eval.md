# how — Evaluation

Fixture A: the JARVIS repo (`Y:\Jarvis`), question about one function: "How does `_parse_validator_output` in `apps/server/agents/oort.py` work?"

Fixture B: the JARVIS repo, cross-cutting question: "How does a request from the phone app reach a department worker and come back?" (spans mobile service, `jarvis_routes.py`, `agents/orchestrator.py`, `agents/base.py`, `manus.py`).

Fixture C: a small repo with a `src/billing/` and `src/notifications/` package and a new invoice-reminder helper in `src/utils/`.

## TC-1: Simple path for a narrow question (fixture A)

- **prompt:** "How does _parse_validator_output work?"
- **assertions:**
  - No parallel explorers are dispatched; one explainer (or the agent itself) explores and explains
  - The answer cites `apps/server/agents/oort.py` and the function by name
  - The answer describes the return shape from reading the code, not from the docs' summary alone
  - Output uses the explainer sections that apply (Overview / How It Works at minimum), not an annotated source dump
- **passing_grade:** 4/4 must pass

## TC-2: Complex path fans out (fixture B)

- **prompt:** "Walk me through how a chat message from the phone reaches a worker and how the answer gets back."
- **assertions:**
  - 2-4 explorers with distinct angles are dispatched in one message
  - Every explorer prompt states read-only
  - A separate explainer synthesizes the findings
  - The final answer has a Where Things Live map with real file paths
  - Open questions or untraced links are stated, not hidden
- **passing_grade:** 4/5 must pass

## TC-3: Placement question (fixture C)

- **prompt:** "Where should this invoice-reminder helper live?"
- **assertions:**
  - The answer is grounded in how billing and notifications actually call each other (cites files)
  - It names a concrete home and the reason in terms of ownership/layering
  - No files are moved or edited
- **passing_grade:** 3/3 must pass

## TC-4: Hands off a "why" question

- **prompt:** "Why does the orchestrator use keyword matching before the LLM classifier?"
- **assertions:**
  - Recognizes this as a motivation question and routes to (or recommends) `why`
  - Does not present a guessed rationale as fact
- **passing_grade:** 2/2 must pass

## TC-5: Knows when code-intelligence fits better

- **prompt:** "Give me the full layer classification and import graph for this repo."
- **assertions:**
  - Points to `code-intelligence` (or the `analyze_codebase` tooling) rather than running the explorer/explainer flow
- **passing_grade:** 1/1 must pass
