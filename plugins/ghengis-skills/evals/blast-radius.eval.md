# Blast Radius — Evaluation

Fixture A: a small Python repo. `cache.py` adds `prune()` that calls `self._store.evict(expired_only=True)` from a vendored library `vendor/kvstore/` pinned at 2.1 with a local patch `patches/kvstore-evict.patch` that makes `expired_only` also drop entries with `ttl=None`. `session.py` stores sessions with `ttl=None`. A 6-line diff adds `prune()` to the hourly scheduler.

Fixture B: a TypeScript change renaming JSON response field `user_id` -> `userId` in `api/users.ts`. A Python job `jobs/export.py` reads the same endpoint's JSON with `row["user_id"]`. No TS file references the old name after the change.

Fixture C: a one-line CSS color change in a single component file with no shared tokens.

## TC-1: Finds the breakage grep will not show (fixture A)

- **prompt:** "What's the blast radius of this prune() change? It's tiny, I think it's fine."
- **assertions:**
  - Reads the vendored library source and the local patch, not only the diff
  - Identifies that sessions with `ttl=None` get evicted (the real risk)
  - Cites a real `file:line` for the patch behavior
  - Does not return a bare caller list as the main output
- **passing_grade:** 4/4 must pass

## TC-2: Proves the safety fact by running code (fixture A)

- **prompt:** same as TC-1
- **assertions:**
  - Names the one fact the change's safety depends on
  - Writes and runs a script/test that calls the real `evict` and pastes the output
  - States the ladder step reached (1-5), or marks the fact **unproven**
  - "Before you merge" section contains a concrete repro or test
- **passing_grade:** 4/4 must pass

## TC-3: Cross-language wire format (fixture B)

- **prompt:** "Blast radius of renaming user_id to userId? tsc is green."
- **assertions:**
  - Finds `jobs/export.py` reading `user_id` from the JSON (another language, same bytes)
  - Does not conclude "safe" from the TypeScript compiler alone
  - Separates confirmed risks from cleared checks
- **passing_grade:** 3/3 must pass

## TC-4: Wide change uses independent legs

- **prompt:** "This PR touches 40 files across the auth layer — what could it break?"
- **assertions:**
  - Proposes or dispatches independent model legs (gemini/agy and/or codex) per tri-model, with Claude merging
  - Delegation instructions require `file:line` evidence and ladder step from each subagent
  - Does not ask the user which model to use
- **passing_grade:** 3/3 must pass

## TC-5: No fabrication on a trivial change (fixture C)

- **prompt:** "What could this color change break?"
- **assertions:**
  - Reports few or no risks honestly; does not invent callers or APIs
  - A search that found nothing is stated as a result
- **passing_grade:** 2/2 must pass
