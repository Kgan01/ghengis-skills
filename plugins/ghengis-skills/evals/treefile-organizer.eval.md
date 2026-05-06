# Treefile Organizer — Evaluation

## TC-1: Plan-First, No Premature Moves

- **prompt:** "Reorganize this Python project. The auth code is scattered."
- **context:** Clean git working tree. Project has Python files in inconsistent layout.
- **assertions:**
  - Skill performs ANALYZE + PROPOSE + PLAN before any file move
  - Writes both `plan.md` and `plan.json` to `<project>/.claude/treefile-organizer/`
  - Does NOT call `git mv` or `mv` before user confirmation
  - Surfaces the plan summary to the user with an explicit "proceed?" question
- **passing_grade:** 4/4 assertions must pass

## TC-2: Refuses on Dirty Working Tree

- **prompt:** "Reorganize the file tree."
- **context:** `git status --porcelain` shows uncommitted changes.
- **assertions:**
  - Skill detects dirty working tree
  - Refuses to operate without committing or stashing first
  - Surfaces the specific blocker (which files are dirty)
  - Suggests `git stash` or `git commit` as the next step
- **passing_grade:** 3/4 assertions must pass

## TC-3: Validator Catches Plan Defects Before Execute

- **prompt:** "Run the treefile-organizer on this monorepo."
- **context:** Project has a circular import that the proposed plan would expose.
- **assertions:**
  - Stage 4 invokes the build-validate chain on `plan.json` (NOT direct execution)
  - Validator's score reflects the circular-dep risk (< 7 if it would break)
  - On low score, plan is regenerated (loop back to PROPOSE), NOT silently executed
  - User sees the validator's specific issues, not just a score
- **passing_grade:** 3/4 assertions must pass

## TC-4: Refuses Unsupported Languages

- **prompt:** "Reorganize this Go project."
- **context:** Project is 100% Go files. No Python or TypeScript.
- **assertions:**
  - Skill detects Go-only and recognizes it's outside v1 scope
  - Refuses to operate
  - Suggests manual reorg OR waits for v2 support
  - Does NOT try to "make it work" by treating Go like Python
- **passing_grade:** 3/4 assertions must pass

## TC-5: Atomic Rollback on Mid-Execute Failure

- **prompt:** "Proceed with the plan." (user has already confirmed)
- **context:** Plan is valid; mid-way through execution, an import rewrite produces invalid Python (rare edge case in user's code).
- **assertions:**
  - Skill detects the syntax error before continuing the batch
  - Runs `git reset --hard <pre_checkpoint_sha>` to restore exactly the pre-execute state
  - Surfaces the failure with the file and line that broke
  - Does NOT proceed to move additional files after the failure
  - Does NOT attempt to "fix forward" — restores cleanly
- **passing_grade:** 4/5 assertions must pass

## TC-6: Imports Rewritten Atomically with Move

- **prompt:** "Yes proceed with the reorganization."
- **context:** Plan says move `src/utils/auth.py` → `src/auth/middleware.py` and rewrite 4 imports across 3 files.
- **assertions:**
  - Single git commit contains BOTH the file move AND the import rewrites
  - No intermediate commit exists where the file moved but imports still point at the old path
  - Commit message identifies treefile-organizer as the source
  - Post-execute: `python -c "import ast; ast.parse(...)"` succeeds for every Python file
- **passing_grade:** 3/4 assertions must pass

## TC-7: Distinguishes Reorg From Surface Cleanup

- **prompt:** "Fix the file structure."
- **context:** Ambiguous — could mean naming conventions OR tree restructuring.
- **assertions:**
  - Skill recognizes ambiguity and asks the user to clarify
  - Mentions both `file-organization` (naming/manifests) and `treefile-organizer` (tree/imports)
  - Does NOT silently pick one and proceed
- **passing_grade:** 3/3 assertions must pass

## TC-8: Anchors Are Respected

- **prompt:** "Reorganize this Next.js project."
- **context:** Project has `package.json`, `tsconfig.json`, `.github/workflows/`, `next.config.js` at root.
- **assertions:**
  - Plan does NOT propose moving any of those anchors
  - `plan.json.anchors` lists them explicitly
  - `plan.md` mentions the anchors as not-moving
  - If a proposed move WOULD invalidate `tsconfig.json` paths, plan flags it as high risk
- **passing_grade:** 3/4 assertions must pass
