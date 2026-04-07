# Quality Gates

Validation scoring, revision triggers, and quality checks for OORT cascades. Every deliverable gets scored; low scores trigger revision with specific feedback.

## Self-Validation Checklist

Before returning ANY output from any role, verify these four dimensions:

### Completeness
- Does the output address every part of the request?
- Are there unanswered questions that should have been answered?
- Is the output the right depth for the task (not too shallow, not over-detailed)?

### Accuracy
- Are all facts verifiable against the codebase or source material?
- Are file paths, line numbers, function names, and variable names correct?
- Are sources cited where applicable?

### Format
- Does it match the requested output format?
- Is it structured with sections, bullets, and headers?
- Is it concise -- no filler words, no unnecessary preamble?

### Actionability
- Can the next role (or the user) act on this immediately?
- Are next steps clearly stated?
- Are blockers and dependencies identified?

## The Builder-Validator Loop

This is the core quality mechanism. Every cascade should have it.

```
Builder produces output
    |
Validator scores 0-10 on rubric
    |
Score >= 7?  -->  Accept, continue pipeline
Score < 7?   -->  Send structured feedback to Builder
    |
Builder revises, addressing ALL listed issues
    |
Validator re-scores
    |
Max 2 revision loops -- then accept with quality note
```

### Why 2 Revisions Max

- Revision 1 catches most issues (typically raises score by 2-3 points)
- Revision 2 catches remaining issues (typically raises score by 1 point)
- Revision 3+ rarely improves score meaningfully and wastes execution time
- If score does not improve after 2 revisions, the problem is usually in the approach, not the execution -- flag this to the user rather than looping further

## Scoring Rubric

Rate every output on four dimensions, 0-10 each:

| Dimension | 0-2 | 3-4 | 5-6 | 7-8 | 9-10 |
|-----------|-----|-----|-----|-----|------|
| **Accuracy** | Major factual errors, broken code | Some errors, partially incorrect | Mostly correct, minor issues | Correct with edge cases handled | Verified, bulletproof |
| **Completeness** | Most requirements missed | Some requirements addressed | Core requirements met, gaps remain | All requirements met | All requirements met + edge cases |
| **Quality** | Unstructured, hard to follow | Readable but rough | Decent structure, some polish needed | Well-structured, professional | Publication-ready |
| **Format** | Wrong format entirely | Partially matches spec | Mostly matches spec | Matches spec with minor deviations | Exact match to spec |

**Overall score** = average of the four dimensions, rounded to nearest integer.

## Score Thresholds and Actions

| Score | Meaning | Action |
|-------|---------|--------|
| 9-10 | Excellent | Ship immediately. No changes needed. |
| 7-8 | Good | Ship. Note minor improvements for future reference. |
| 5-6 | Acceptable | Revise if time allows. Ship only if deadline-pressured. |
| 3-4 | Below standard | Must revise before shipping. Do not deliver at this quality. |
| 0-2 | Failed | Restart the role from scratch with a revised approach. |

## Feedback Format

When the validator scores below 7, feedback must be structured and actionable:

```
SCORE: 5
DIMENSION_SCORES:
  accuracy: 7
  completeness: 4
  quality: 6
  format: 3

ISSUES:
- Missing error handling for token expiration (auth/jwt.ts:45 -- no catch block)
- No tests for the refresh token endpoint (required by original spec)
- Response format uses snake_case but spec requires camelCase

REVISION_NEEDED: true
FEEDBACK: Add the missing refresh token tests first -- that will address
completeness and catch any accuracy issues in the refresh flow simultaneously.
```

### Feedback Rules

- **Be specific.** "This is incomplete" is useless. "Missing tests for refresh endpoint" is actionable.
- **Reference locations.** File paths, line numbers, section names -- the builder should not have to search.
- **Prioritize.** The FEEDBACK field should name the single change that would raise the score the most.
- **Track progression.** If this is revision 2, note whether the previous issues were resolved.

## Revision Tracking

Track scores across revision loops to verify improvement:

```
Revision 0 (initial): Score 4 (accuracy:6, completeness:2, quality:5, format:3)
Revision 1:           Score 6 (accuracy:7, completeness:5, quality:6, format:6)
Revision 2:           Score 8 (accuracy:8, completeness:8, quality:7, format:7)
  --> Accept
```

**Red flags in progression:**
- Score decreases between revisions -- builder introduced new problems while fixing old ones
- Score stays flat -- builder did not address the listed issues, or the issues were symptoms of a deeper problem
- Single dimension stays low while others improve -- that dimension may need a fundamentally different approach

## End-to-End Validation

For cascades with 3+ roles, add a holistic validation pass after all waves complete. This catches integration issues that per-role validation misses.

### What E2E Validation Checks

- **Coherence:** Do all role outputs tell a consistent story? Are there contradictions between what the researcher found and what the builder produced?
- **Traceability:** Can every builder decision be traced back to a researcher finding or user requirement?
- **Integration:** Do the pieces fit together? If the builder created code and the documenter wrote docs, do the docs match the actual code?
- **Original request alignment:** Step back and compare the final output against the user's original request word by word. Did anything get lost or added that was not asked for?

### E2E Scoring

Same 0-10 scale, focused on integration:

| Dimension | What to Check |
|-----------|---------------|
| **Coherence** | No contradictions between role outputs |
| **Traceability** | Every output element traces to a requirement |
| **Integration** | Pieces fit together without gaps |
| **Request alignment** | Final output matches what the user actually asked for |

## Escalation Patterns

When validation reveals problems that revision cannot fix:

| Situation | Response |
|-----------|----------|
| Score stuck below 5 after 2 revisions | Flag to user: "The current approach is not producing quality results. Here is what I tried and where it falls short. Recommend changing the approach to [alternative]." |
| Contradictory requirements discovered | Flag to user: "The requirements contain a contradiction: [X] conflicts with [Y]. Which takes priority?" |
| Scope larger than estimated | Flag to user: "This task is larger than initially assessed. Breaking it into [N] separate cascades would produce better results." |
| Critical quality issue (security, data loss) | Block output entirely. Do not deliver. Explain the issue and the risk. |

## Common Validator Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Rubber-stamping (always 9-10) | Validator prompt too generic | Add specific checkpoints: "verify X exists in file Y" |
| Scoring too harshly (always 3-4) | Validator applying impossible standards | Calibrate: 7 means "good enough to ship," not "perfect" |
| Vague feedback | Validator not referencing specific locations | Require file:line references in every issue |
| Only checking surface quality | Validator not testing functionality | Include "run the tests" or "verify the function handles edge case X" |
| Ignoring the original request | Validator checking quality in isolation | Always re-read the user's original request as part of validation |
