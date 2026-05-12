---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work. Guides completion through structured options - merge locally, push and open PR, keep as-is, or discard. Verifies tests before presenting options; refuses to proceed if any test fails. TRIGGER on "let's wrap this up", "ship it", "merge this", "ready to ship", "done coding", or after build-validate chain ends with revised-and-shipped outcome.
allowed-tools: Read Bash Grep Glob
---

# Finishing a Development Branch

Closes out development work by verifying tests, detecting the workspace shape, presenting structured integration options, and executing the choice with sensible cleanup.

**Core principle:** Verify tests → Detect environment → Present options → Execute choice → Clean up.

## When to Use

- Implementation is finished and you believe it's ready to integrate
- `build-validate` chain has completed with `shipped` or `revised-and-shipped`
- User says "let's wrap this up", "ship it", "merge this", "ready to ship"
- All planned work for this branch is done

## When NOT to Use

- Mid-implementation — finish the code first
- Tests are failing — fix them, don't skip this skill
- The work isn't actually ready (skip-trying-to-finish-too-early is half the value of this skill)

## The 6-Step Process

### Step 1: Verify tests pass

Before showing any options, run the test suite:

```bash
# Try the project's test command in order
pytest 2>/dev/null || npm test 2>/dev/null || cargo test 2>/dev/null || go test ./... 2>/dev/null || python -m pytest 2>/dev/null
```

If you can't find a test command, check the project for `Makefile`, `package.json` scripts, `pyproject.toml`, or `CLAUDE.md` for hints. Ask the user only as a last resort.

**If tests fail:**
> Tests failing (N failures). Must fix before completing:
>
> [show first few failures]
>
> Cannot proceed with merge/PR until tests pass.

Stop. Don't proceed to Step 2. This is a hard refusal — the integration options assume green tests.

**If tests pass OR project genuinely has no tests** (rare, document why): continue to Step 2.

### Step 2: Detect workspace shape

Different states get different menus:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
HEAD_STATE=$(git symbolic-ref HEAD 2>/dev/null && echo "named" || echo "detached")
```

| State | Menu options |
|---|---|
| Normal repo (`GIT_DIR == GIT_COMMON`) | All 4 options |
| Worktree with named branch | All 4 options + worktree cleanup |
| Worktree with detached HEAD | 3 options (no local merge — externally managed) |

### Step 3: Determine base branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

If neither works, ask the user: "This branch diverged from <best-guess> — is that the base you want to merge into?"

### Step 4: Present options

**Normal repo / named-branch worktree:**

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (you'll handle it later)
4. Discard this work

Which option?
```

**Detached HEAD worktree:**

```
Implementation complete. You're on a detached HEAD (externally managed workspace).

1. Push as new branch and create a Pull Request
2. Keep as-is (you'll handle it later)
3. Discard this work

Which option?
```

Keep options concise. Don't pre-explain consequences — wait for the user to ask.

### Step 5: Execute the choice

#### Option 1: Merge locally

```bash
# Sanity: ensure working tree is clean
git status --porcelain | grep -v '^??' && echo "Working tree dirty — commit or stash first" && exit 1

# Switch to base, fast-forward if possible, otherwise create a merge commit
git checkout <base-branch>
git pull --ff-only origin <base-branch> 2>/dev/null
git merge --no-ff <feature-branch>
```

Confirm the merge with `git log --oneline -5`. Don't push yet — that's a separate decision.

#### Option 2: Push and open a Pull Request

```bash
# Push the branch
git push -u origin <feature-branch>

# Open PR via gh CLI
gh pr create --title "<title>" --body "<body>" --base <base-branch>
```

Body should include:
- Summary (1-3 bullets)
- Test plan (what you ran, what passed)
- Anything reviewers should look at twice

Return the PR URL.

#### Option 3: Keep as-is

Confirm:
> Branch `<branch>` left as-is. To pick it back up: `git checkout <branch>`.

If you're in a worktree, surface its path so the user can find it.

#### Option 4: Discard

Destructive — require explicit confirmation:

> This will permanently delete the branch and its commits. Are you sure? Type "yes discard" to confirm.

Only proceed on "yes discard" or equivalent unambiguous consent. Then:

```bash
git checkout <base-branch>
git branch -D <feature-branch>
# If worktree, remove it too
git worktree remove <path> 2>/dev/null
```

### Step 6: Cleanup

After merge or PR creation, offer cleanup:

- Delete local branch if merged
- Remove worktree if applicable
- Surface any stale state worth noting (untracked files, ignored artifacts)

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Presenting options without verifying tests first | User merges broken code | Run tests; refuse to proceed on red |
| Bundling multiple options into one "smart" action | User can't tell what's happening or revert one part | One option, one action |
| Auto-pushing without asking | Pushes are publicly visible; some users want to review locally first | Ask. Always. |
| `--no-verify` or skipping hooks during finish | Hides real issues, breaks team conventions | Investigate hook failures, don't bypass |
| Force push to a shared branch | Destroys other people's work | Refuse. Suggest a rebase + new branch instead |
| Deleting a branch without confirmation | Can't be undone | Require explicit consent for option 4 |
| Pre-explaining all 4 options at length | User just wants to pick | Keep menu terse; explain only if asked |
| Skipping cleanup | Stale branches and worktrees accumulate | Offer cleanup as part of step 6 |

## Cross-References

- **`build-validate` chain** — natural predecessor. Once it outputs `revised-and-shipped`, use this skill to integrate.
- **`finish-line` chain** (in `skill-chain-supervisor`) — wraps this skill plus `auto-project-sync` (update CLAUDE.md/MEMORY.md) plus `audit-ledger` (record in immutable log).
- **`auto-project-sync`** — natural successor after merge. Update docs to reflect what was just shipped.
- **`audit-ledger`** — record the integration event with hash-chained provenance.
- **`test-driven-development`** — predecessor. If tests aren't passing, this skill refuses; go back to TDD.
