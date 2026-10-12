# Benchmark Checklist — Evaluation

Fixture A: `bench.py` times an async `export_rows()` call 1 time per side. Side A uses the new code; side B uses the old code with `DEBUG=1` and `commit_per_row=True`. Output: A 0.8s, B 4.1s. The script does not await `export_rows()` on side A (returns a coroutine) and does not count errors.

Fixture B: a micro-benchmark shows `slugify()` 3x faster after a change; a profile of the `/posts` request shows `slugify` at 0.5% of request time.

Fixture C: 7 alternating runs per side, p50 A 41-44 ms, B 40-45 ms.

## TC-1: Catches work that never happened (fixture A)

- **prompt:** "New export is 5x faster, write the PR description."
- **assertions:**
  - Spots the un-awaited coroutine (question 7) before reporting any speedup
  - Flags missing error counting (question 4)
  - Does not ship "5x faster"
- **passing_grade:** 3/3 must pass

## TC-2: Catches the untuned side (fixture A)

- **prompt:** same as TC-1
- **assertions:**
  - Identifies side B running with debug build / commit-per-row as untuned (question 2)
  - Refuses to pick a winner until both sides are tuned and re-measured
  - Requires >= 5 alternating runs with median and range
- **passing_grade:** 3/3 must pass

## TC-3: Relevance end to end (fixture B)

- **prompt:** "slugify is 3x faster now, huge win for page loads."
- **assertions:**
  - Reports the micro result as a share of the end-to-end request (at most ~0.5% gain)
  - Corrects the "huge win for page loads" framing
- **passing_grade:** 2/2 must pass

## TC-4: Noise is no difference (fixture C)

- **prompt:** "Is A faster than B?"
- **assertions:**
  - Verdict is "no measurable difference" (gap within run-to-run range)
  - Mentions rank-sum test or equivalent for close calls
  - Report gives run count and range
- **passing_grade:** 3/3 must pass

## TC-5: Explain the number standalone

- **prompt:** "Throughput went from 2k to 9k req/s after switching JSON libraries. Report it."
- **assertions:**
  - Asks "why not double?" and requires a named limiter from a profile or counters
  - Does the limits arithmetic (gain vs JSON's share of the run) and flags a gain larger than the changed piece allows
  - Verdict is inconclusive until the limiter is named
- **passing_grade:** 3/3 must pass

## TC-6: Ballpark mode stays light

- **prompt:** "Roughly how long does the test suite take? Just a ballpark."
- **assertions:**
  - One run is acceptable and is labeled as one run
  - Still confirms the run did not error and the tests actually executed (questions 4 and 7)
  - Does not demand 5 alternating runs
- **passing_grade:** 3/3 must pass
