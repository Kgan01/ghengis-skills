# Ponytail Review — Evaluation

Fixture A: a Node repo; the last commit renames `post.body` to `post.content` in `src/models/post.js` and `src/routes/posts.js`. `src/routes/feed.js` (untouched by the commit) still reads `post.body` for the Atom feed.

Fixture B: a staged diff adding `POST /import` that builds SQL with string concatenation from `req.body.table`, swallows errors with an empty `catch {}`, and adds a 40-line `ImporterFactory` with one product. README says "internal tool, ~5 users".

Fixture C: a diff adding a correct 6-line `slugify(s)` plus the test `expect(slugify("Hello World")).toBe("hello-world")`. Nothing wrong.

Fixture D: a diff containing `// shortcut: in-memory rate limit, single process only; move to Redis when we scale out`. Deploy config shows one replica.

## TC-1: Finds the break outside the diff (fixture A)

- **prompt:** "Review the last commit."
- **assertions:**
  - Reports that `src/routes/feed.js` breaks (reads the old field) although it is not in the diff
  - Classifies it as Must fix
  - The finding has all four parts: What this is / Problem / Fix / If we skip it
  - Output starts with `What this change does:`
- **passing_grade:** 4/4 must pass

## TC-2: Security and data loss ranked above lean (fixture B)

- **prompt:** "ponytail review the staged changes."
- **assertions:**
  - SQL injection via `req.body.table` reported as Must fix with a concrete input
  - The swallowed error reported as a data-loss risk
  - `ImporterFactory` reported as a lean/yagni finding below the Must-fix items
  - States the assumed load (~5 users) and judges scale against it
  - Ends with `Verdict:` and `Lean: -<N> lines possible.`
- **passing_grade:** 5/5 must pass

## TC-3: Clean diff gets a short pass (fixture C)

- **prompt:** "Code review please."
- **assertions:**
  - Outputs `Looks good. Ship.` (or equivalent) plus one line on what was checked
  - No invented findings, no "consider" suggestions
- **passing_grade:** 2/2 must pass

## TC-4: Documented shortcut is a decision (fixture D)

- **prompt:** "Review my PR."
- **assertions:**
  - Does not report the in-memory rate limit as a finding, because the load (one replica) is under the named ceiling
  - Mentions it only as a known decision, if at all
- **passing_grade:** 2/2 must pass

## TC-5: Report only (fixture B)

- **prompt:** "Review this and tell me what's wrong."
- **assertions:**
  - Makes no file edits
  - Findings are numbered across groups so the user can say "fix 1 and 3"
- **passing_grade:** 2/2 must pass
