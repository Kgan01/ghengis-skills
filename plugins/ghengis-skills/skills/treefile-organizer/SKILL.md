---
name: treefile-organizer
description: Use when reorganizing an existing project's file tree based on what actually connects to what — analyzes import graph, classifies layers, proposes an ideal target tree, validates the plan adversarially, then executes file moves with atomic per-language import rewrites. Always plan-first; never moves a file before the user confirms. TRIGGER on "reorganize this project", "clean up the file tree", "the structure is a mess", "make this match a real project layout", or after project-scaffold detects layout drift.
allowed-tools: Read Write Edit Bash Glob Grep
---

# Treefile Organizer

Reshape a project's file tree to match how its code actually connects, not how files happened to land. Plan-first, validate-before-execute, never move a file without explicit user confirmation.

This skill differs from `file-organization` (naming, manifest types, surface categorization) and `project-scaffold` (greenfield 4-layer setup). Treefile-organizer operates on **existing** projects with **existing** import graphs and reorganizes the leaves AND the branches.

## When to Use

- A project's file tree has drifted from its architecture (auth code in `utils/`, components scattered across the repo, tests next to nothing they test)
- The user says "this is a mess" or "I want to reorganize this"
- After `project-scaffold` detects layout drift on an existing project
- Onboarding to a codebase where the structure obscures the design

## When NOT to Use

- Greenfield projects — use `project-scaffold` instead
- Projects under active feature work where moving files breaks open PRs (advise pausing the reorg until merged)
- Languages outside the v1 scope (see Scope below) — surface a warning and bail
- Trivial cleanups (renaming 2-3 files) — just do them directly with Edit/Bash

## Scope (v1)

| Language | Import-rewrite support | Notes |
|----------|----------------------|-------|
| **Python** | Full | `from x.y import z`, relative imports, `__init__.py` re-exports, sys.path-relative imports |
| **TypeScript** / JavaScript | Full | ES module imports, `tsconfig.json` path aliases, `package.json` exports field |
| Go, Rust, Java, Flutter | NOT supported | Will refuse to operate; recommend manual reorg |
| Mixed-language repos | Partial | Operates only on Python + TS files; non-supported files stay put |

A v2 may extend to Go modules and Flutter packages. Don't pretend to support what's not implemented.

## Hard Requirements

1. **Project must be a git repo with a clean working tree.** Refuse to operate on dirty repos — the user could lose work. Suggest `git stash` first.
2. **Always run plan-then-confirm-then-execute.** Never skip the confirm step, even when the user is impatient.
3. **Move atomically per file group.** If any move fails or any import becomes unresolvable, hard-revert the entire batch via `git reset --hard <pre-checkpoint-sha>`.
4. **Rewrite imports in the SAME commit as the move.** A commit must never be in a state where files moved but imports still point at old paths.

## The 7-Stage Pipeline

### 1. ANALYZE — what connects to what

Build the dependency graph of the project. Run `scripts/analyzer.py` (Python stdlib only, no deps):

```bash
python <skill_dir>/scripts/analyzer.py <project_root> --output .claude/treefile-organizer/analysis.json
```

Output (analysis.json):
- **files**: every code file in scope with relative path, language, layer classification (api / service / data / ui / infrastructure / utility / test / unknown), loc, and import list
- **edges**: every internal import resolved to a project file (source path, target path, line number)
- **anchors**: files that should NOT move (pyproject.toml, package.json, tsconfig.json, .github/, scripts/, README.md, lockfiles, build configs, CI configs)
- **stats**: total counts including cycles_detected (graph health proxy)

The analyzer uses Python's `ast` module for Python imports (precise) and regex for TypeScript/JavaScript (~99% accurate; handles `import`, `export from`, `require`, dynamic `import()` with literal strings). External imports are counted but excluded from the per-file `imports` list by default unless `--include-external` is passed.

Cross-reference: `code-intelligence` skill provides the broader 6-layer classification methodology this script implements.

### 2. PROPOSE — what does an "ideal" tree look like
### 3. PLAN — produce both human-readable and machine-readable artifacts

Stages 2 and 3 are implemented together in `scripts/planner.py`:

```bash
python <skill_dir>/scripts/planner.py .claude/treefile-organizer/analysis.json \
    --output-dir .claude/treefile-organizer/
```

The planner:
- **Detects project type** from anchors + content (FastAPI service, React/Next.js app, Python library, etc.)
- **Loads the ideal layout** for that project type from a built-in template (layer → ideal directory)
- **Proposes moves** for files whose layer doesn't match their current location, skipping anchors, unknown-layer files, and files already in canonical positions
- **Computes import rewrites** for every move using the analyzer's edge data (per-language: Python dotted-path or relative; TS/JS relative path with `os.path.relpath`)
- **Detects collisions** — two files moving to the same target, or a target that already exists
- **Topo-sorts moves** via Kahn's algorithm so dependent files move after their dependencies
- **Assesses risk** (low / medium / high) based on move ratio, cycle count, and import-rewrite volume

Reference: `plan-format.md` for the full plan.json schema. The planner's output conforms to that exactly.

**Refuses to propose moves for:**
- Files marked as anchors in stage 1
- Files in directories matched by `.gitignore` (excluded from analysis upstream)
- Files classified as `unknown` layer (insufficient confidence)

Generate two files in `<project>/.claude/treefile-organizer/`:

**`plan.md`** — human-readable summary:
- Project type detected
- Files staying put: count
- Files moving: count, grouped by source-dir → target-dir
- Imports needing rewrite: count, with sample
- Anchors respected: list
- Estimated risk: low / medium / high (based on coupling density)

**`plan.json`** — machine-readable for the validator:
```json
{
  "version": "1",
  "project_root": "/abs/path/to/project",
  "language_mix": {"python": 23, "typescript": 47},
  "moves": [
    {
      "from": "src/utils/auth.py",
      "to": "src/auth/middleware.py",
      "language": "python",
      "imports_in": [{"file": "src/main.py", "line": 12, "old": "from utils.auth import ...", "new": "from auth.middleware import ..."}]
    }
  ],
  "anchors": ["pyproject.toml", "package.json", ".github/workflows/ci.yml"],
  "topo_order": ["src/utils/helpers.py", "src/utils/auth.py", "src/main.py"],
  "estimated_imports_to_rewrite": 47
}
```

See `plan-format.md` for the full schema.

### 4. VALIDATE — adversarially break the plan before files move

Invoke the `build-validate` chain via `skill-chain-supervisor`. The plan IS the deliverable; the validator's job is to find what the plan misses.

Validator must check (functional, not visual):
- **Import resolution simulation** — for every move, simulate the new import path; flag any that don't resolve
- **Cyclic dependency detection** — does any move create a cycle?
- **Coverage** — does the plan miss any file that imports something being moved?
- **Anchor violations** — does any move conflict with `pyproject.toml` / `tsconfig.json` package layout config?
- **Topo-order soundness** — can the moves actually execute in the proposed order without breaking intermediate states?
- **Test mirroring** — if `tests/foo.py` tests `src/foo.py`, does the plan move them together?

Validator output: structured issues with file paths, score 0-10. If score < 7 or `revision_needed = true`, loop back to PROPOSE with the issues injected.

### 5. CONFIRM — get explicit user permission before any file moves

Surface to the user:
- Final plan summary from `plan.md`
- Validator score + any remaining flagged issues
- A single yes/no question: "Proceed with this reorganization?"

**Do not interpret silence, "ok", "sure", "looks good" as a green light without an explicit "yes proceed" or equivalent.** This is a destructive operation; require unambiguous consent.

If the user says no or asks to modify, treat the request as input to a fresh PROPOSE pass. Do not execute partial plans.

### 6. EXECUTE — move files in dependency-safe order

Pre-flight:
- `git status --porcelain` — must be clean
- Tag a checkpoint: `git rev-parse HEAD` saved as `pre_checkpoint_sha`
- Optional backup: `cp -r <project> <project>.treefile-backup-<timestamp>` (off by default; opt-in via `--backup`)

For each file in `topo_order`:
1. `mkdir -p <target_dir>` if needed
2. `git mv <from> <to>` (uses git's rename detection; preserves history)
3. For each import in `imports_in[file]`, rewrite the import line using language-specific rules (see `import-rewriting.md`)
4. After each batch (default: 10 files), run a fast verify probe (next stage)

If ANY step fails:
- `git reset --hard $pre_checkpoint_sha` — restore exactly the state before move began
- Surface the failure to the user with the file that broke and the underlying error
- DO NOT attempt to "fix forward" or move on to the next file

### 7. VERIFY — confirm nothing actually broke

Post-move sanity checks:
- **Python**: `python -c "import ast; [ast.parse(open(f).read()) for f in <all_python_files>]"` — every file still parses
- **TypeScript**: `npx tsc --noEmit` if `tsconfig.json` exists — every file still type-checks (or at least doesn't have NEW errors)
- **Re-run import resolution** — every import statement resolves to an actual file
- **Run tests if a test command is detected** — e.g., `pytest --collect-only` or `npm test --listTests`

If any check fails: `git reset --hard $pre_checkpoint_sha`, restore from `--backup` if used, surface the failure with full output.

If all checks pass:
- Commit the moves with message `treefile-organizer: reorganize <N> files (<from-tree> → <to-tree>)`
- Write a final report to `<project>/.claude/treefile-organizer/report-<timestamp>.md`
- Tell the user what changed and how to revert (`git revert <sha>` or `git reset --hard $pre_checkpoint_sha~1`)

## Failure Modes and Recovery

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Import doesn't resolve after move | step 7 import-resolution check | git reset, surface broken import |
| TypeScript path alias breaks | step 7 tsc check | git reset, suggest manual `tsconfig.json` review |
| Tests fail post-move | step 7 test run | git reset (a passing build is a hard requirement) |
| User Ctrl-C mid-execute | trap signal | git reset to pre_checkpoint_sha immediately |
| Two files have same target name | step 2 propose | refuse to plan; surface collision in plan.md |
| Move would violate anchor | step 2 propose | exclude from move list; note in plan.md |

## Refusal Conditions

This skill MUST refuse to proceed when:
- Project is not a git repo (`git rev-parse --git-dir` fails)
- Working tree is dirty (`git status --porcelain` returns non-empty)
- Any in-scope language is unsupported AND no Python/TS files were detected
- User explicitly says "just move the files" without going through the plan/validate/confirm gates
- Detected an open git rebase / merge / cherry-pick in progress

When refusing, surface the specific blocker and what the user should do (e.g., "commit or stash your changes, then re-run").

## Trigger Words

The skill should activate when the user says:
- "reorganize this project" / "clean up the file tree"
- "the structure is a mess" / "the layout is wrong"
- "make this match a real project layout"
- "treefile" / "tree organizer"
- "move files based on what they import"

Activate cautiously when the user says:
- "fix the file structure" — could mean naming (use `file-organization`) or tree (use this skill); ask
- "refactor the code" — broader than reorg; clarify scope first

## Output to User

After every stage, surface a one-paragraph status with the next decision point. Don't dump JSON. The plan.md is the user's primary view; plan.json is for the validator and for audit.

Final report should answer: what moved, what stayed, what imports were rewritten, what the new top-level shape looks like.

## Cross-References

- `code-intelligence` — provides AST parsing + import graph + layer classification (used in stage 1)
- `project-scaffold` — provides ideal tree templates per project type (used in stage 2)
- `file-organization` — handles surface naming and manifest concerns; complementary, not replacement
- `skill-chain-supervisor` — invokes the build-validate chain at stage 4
- `plan-format.md` (this skill) — full plan.json schema
- `import-rewriting.md` (this skill) — per-language rewrite rules
