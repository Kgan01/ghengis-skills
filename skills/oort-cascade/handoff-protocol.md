# Handoff Protocol

Structured data transfer between roles in an OORT cascade. Handoffs carry key findings and artifacts -- not prose paragraphs. This is the inter-agent language that prevents information loss and bloat between cascade stages.

## Handoff Format

Every role outputs a structured handoff for downstream roles:

```
KEY_FINDINGS:
- [Finding 1: concise, factual, actionable]
- [Finding 2: with specific data or file reference]
- [Finding 3: with source or confidence qualifier]

DATA_POINTS:
- [Metric or data point with source]
- [Metric or data point with source]

ARTIFACTS:
- [File path or resource identifier]
- [Generated content snippet if relevant]

CONFIDENCE: [0.0-1.0]
```

## Rules

1. **Max 500 tokens per handoff.** This forces conciseness. If you cannot fit it in 500 tokens, you are passing too much.
2. **Use bullet points, not paragraphs.** Every item should be scannable.
3. **Include raw data and numbers, not just interpretations.** The downstream role needs facts it can verify and build on.
4. **Every claim needs a source or confidence qualifier.** "Auth module uses sessions (auth/middleware.py:42)" not "the auth module uses sessions."
5. **Merge multiple dependency handoffs cleanly.** No duplication between upstream sources.

## Good vs. Bad Handoffs

### Bad (vague, prose, no data)

```
The researcher found many interesting things about the authentication
system. It appears to use session-based auth with cookies, and there
are several files involved. The tests seem comprehensive but could
use some improvement. Overall the codebase is well-structured.
```

**Problems:** No file paths, no line numbers, no metrics, vague qualifiers ("many", "several", "seems"), reads like a book report.

### Good (structured, specific, actionable)

```
KEY_FINDINGS:
- Session auth via express-session in auth/middleware.ts:15-48
- Cookie config: httpOnly=true, secure=false (security gap), maxAge=24h
- 3 middleware functions: requireAuth, optionalAuth, requireRole
- 14 endpoints check auth state (see ARTIFACTS for full list)

DATA_POINTS:
- Test coverage: 87% on auth/ directory (23 tests in auth/__tests__/)
- 2 tests mock session directly — will break on JWT migration
- No refresh token tests exist

ARTIFACTS:
- auth/middleware.ts (core session logic)
- auth/__tests__/middleware.test.ts (23 tests)
- routes/protected.ts (8 endpoints using requireAuth)
- routes/admin.ts (6 endpoints using requireRole)

CONFIDENCE: 0.95
```

## Merging Multiple Dependencies

When a role depends on 2+ upstream roles, merge their handoffs into a unified context block:

```
FROM researcher:
  - Session auth in auth/middleware.ts:15-48
  - 14 protected endpoints across 2 route files
  - 87% test coverage, 2 fragile mocks

FROM analyst:
  - JWT migration affects 3 downstream services
  - Token refresh adds ~200ms latency per expired token
  - Cookie-to-header migration requires client-side changes

MERGED CONTEXT FOR BUILDER:
  Scope: auth/middleware.ts + 2 route files + 23 tests
  Key risk: 2 tests mock sessions directly — rewrite first
  Performance constraint: refresh flow must stay under 200ms
  Client impact: Authorization header replaces cookie — coordinate with frontend
```

### Merge Rules

- Deduplicate overlapping findings between sources
- Resolve contradictions explicitly ("researcher says X, analyst says Y -- using Y because [reason]")
- Synthesize a combined implication when upstream findings interact
- Preserve the most specific data point when two sources cover the same topic

## Handoff by Role Type

### Researcher Handoff

Focus on: facts, file paths, metrics, citations. Avoid: opinions, recommendations, architectural suggestions.

```
KEY_FINDINGS:
- [Factual finding with file:line reference]
- [Factual finding with file:line reference]

DATA_POINTS:
- [Metric with measurement method]

ARTIFACTS:
- [List of relevant files discovered]

CONFIDENCE: [0.0-1.0]
```

### Builder Handoff (to Validator)

Focus on: what was built, what changed, what was not changed and why.

```
KEY_FINDINGS:
- [What was created/modified]
- [Key design decisions and why]
- [Known limitations or tradeoffs]

ARTIFACTS:
- [Files created or modified with brief description of changes]

TESTS:
- [New tests added]
- [Existing tests modified]
- [Tests intentionally not modified and why]
```

### Validator Handoff (feedback to Builder on revision)

Focus on: specific issues with locations, what would raise the score.

```
SCORE: [0-10]
DIMENSION_SCORES:
  accuracy: [0-10]
  completeness: [0-10]
  quality: [0-10]
  format: [0-10]

ISSUES:
- [Specific issue 1 with file:line or section reference]
- [Specific issue 2 with file:line or section reference]

REVISION_NEEDED: [true/false]
FEEDBACK: [One concrete improvement that would raise the score the most]
```

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Prose paragraphs | Downstream role has to parse natural language to find facts | Use structured bullet format |
| "Many files were found" | No specificity, cannot be acted on | List the actual files |
| Passing entire previous output | Bloated context, buries signal in noise | Extract the 3-5 most relevant points |
| Opinions without data | Downstream role cannot verify or challenge | Include the measurement or source |
| Missing confidence | Downstream role treats uncertain info as certain | Always include CONFIDENCE score |
| Duplicated info across merged handoffs | Wastes tokens, creates confusion when versions differ | Deduplicate and resolve contradictions |
