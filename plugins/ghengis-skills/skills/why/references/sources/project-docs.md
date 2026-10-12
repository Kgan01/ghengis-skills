# In-Repo Long-Form Docs

## What this source contains

- `docs/plans/` — dated design and implementation plans (e.g. `2026-08-07-gauntlet-loop-implementation.md`). Often hold "alternatives considered" and "what NOT to adopt".
- `docs/research/` — analyses that preceded a build (gap tables, ranked lifts)
- `docs/INDEX.md`, `docs/STATUS.md`, `docs/architecture/`, `docs/concepts/`
- `.claude/docs/*.md` — module docs, incl. `current-status.md` with dated completion notes and "build-validate caught…" bug stories
- `CHANGELOG.md`, `MEMORY.md`, `CONTEXT.md` (and per-folder `CONTEXT.md`)
- ADRs anywhere (`**/adr/**`, "Decision record")
- READMEs inside the target's folder

## How to search it

1. **Keyword sweep** across all doc roots for the feature name, symbols, config keys, the threshold value itself:
   ```bash
   rg -n -i '<term>' docs .claude/docs CHANGELOG.md MEMORY.md CONTEXT.md --glob '*.md'
   ```
2. **Date-bound the plans.** Plans are named by date. List those within a few weeks before the anchor commit date and read the candidates in full; rationale is often mid-document.
3. **Read the whole doc**, including "Alternatives", "Non-goals", "Risks", "What not to adopt".
4. **Doc history.** Docs that were edited after the code shipped may record a change of plan:
   ```bash
   git log --oneline --follow -- <doc>
   ```
5. **Follow in-repo links** between docs. Links out to Drive, mail, or the brain go to Additional Leads.

## What good evidence looks like

- A plan section stating the problem and the chosen approach, with rejected alternatives
- A `current-status.md` or CHANGELOG line naming the target and why it was added
- A research doc whose recommendation matches the code

## Common pitfalls

- **Plan vs. reality drift.** Plans are written before the build. Flag divergence; don't present the plan as what shipped.
- **Multiple drafts.** Prefer the most recent finalized doc, but report earlier ones that disagree.
- **Counts and claims in docs go stale.** Treat numbers in docs as dated claims, not facts.

## What to return

For each relevant doc: path, section heading, last-modified commit and date, verbatim motivation quote with line numbers, and whether it is a plan (pre-build) or a record (post-build).
