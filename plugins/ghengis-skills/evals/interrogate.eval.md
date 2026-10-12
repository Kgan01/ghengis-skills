# interrogate — Evaluation

Fixture A: a feature branch adding a retry wrapper around an HTTP client. The diff has a real bug (retries on non-idempotent POST), one file pushed from under 1000 lines to over 1000 lines, and several style nits.

Fixture B: same branch, session where `codex login status` fails (codex leg dark) and agy works.

Fixture C: a tiny 3-line typo fix.

Baseline failure to prevent: one model reviews, every nit is listed as a blocker, and fixes are applied without being asked.

## TC-1: Three legs, one prompt (fixture A)

- **prompt:** "Interrogate this branch before I merge."
- **assertions:**
  - States the intent in one paragraph before dispatch
  - One prompt file built from reviewer-prompt + rubric + code-quality lens
  - Claude subagent, codex leg, and Gemini leg all receive that same prompt, dispatched concurrently
  - codex runs read-only (`--sandbox read-only`, or codex-rescue with a read-only instruction); Gemini runs via the `gemini` agent or `agy-call.ps1` with `-Model flash-high`
  - Does not ask the user which models to use
- **passing_grade:** 5/5 must pass

## TC-2: Lead judgment filters (fixture A)

- **prompt:** same as TC-1
- **assertions:**
  - The non-idempotent POST retry is in Act On
  - Pure style nits are in Noted or Dismissed, not Act On
  - Act On has 5 or fewer items
  - Every finding names the leg(s) that raised it
  - A Dismissed section exists with one-line reasons
- **passing_grade:** 4/5 must pass

## TC-3: Never auto-applies (fixture A)

- **prompt:** "Tear this apart."
- **assertions:**
  - No file in the repo is modified by the review
  - Output ends with the verdict (and at most an offer to fix), not with applied changes
- **passing_grade:** 2/2 must pass

## TC-4: Dark leg does not block (fixture B)

- **prompt:** same as TC-1
- **assertions:**
  - Review proceeds with Claude + Gemini
  - Reviewers section shows codex as "dark" with the reason
  - Agreement Map notes the reduced consensus signal
- **passing_grade:** 3/3 must pass

## TC-5: Right-sizing (fixture C)

- **prompt:** "Can you just glance at this typo fix?"
- **assertions:**
  - Does not run a three-leg interrogation unprompted; a direct look or single-leg review is used, or the user is told interrogate is overkill
- **passing_grade:** 1/1 must pass

## TC-6: Points to gauntlet for polish loops

- **prompt:** "Keep reviewing and improving this module until it is excellent."
- **assertions:**
  - Routes to `gauntlet` (iterative worker + blind critic) rather than a one-shot interrogate verdict
- **passing_grade:** 1/1 must pass
