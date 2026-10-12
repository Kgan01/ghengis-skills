# Task / Issue Tracker (docs/TODO.md + GitHub Issues)

## What this source contains

- `docs/TODO.md` (JARVIS and most of this user's repos): numbered items (`#277`), Ideas Backlog, In Progress, Completed, Archived-with-reason. This is where "we're doing this because…" is usually first written.
- Other `TODO.md` / `tasks.md` files in sub-projects
- GitHub Issues and their comments, labels, milestones, linked PRs (`gh`)
- Any tracker MCP that is connected (Linear, Jira, etc.). Adapt the same steps.

The tracker holds the product or personal forcing function: the request, the incident follow-up, the client ask.

## How to search it

1. **Follow IDs from the anchor first.** Commit messages and PR bodies often cite `#NNN`. Find that item in `docs/TODO.md`:
   ```bash
   rg -n '#277\b' docs/TODO.md
   ```
   Read the whole entry and its neighbours (sub-bullets often carry the reason).
2. **Keyword search** for the feature name, key symbols, user-visible terms. Try several phrasings and the "Archived" section, where superseded ideas keep their reason.
3. **History of the tracker itself.** When an item appeared and how it changed is evidence:
   ```bash
   git log -S '<feature term>' --oneline -- docs/TODO.md
   git log -p --follow -- docs/TODO.md | rg -n -C3 '<term>'
   ```
4. **GitHub Issues** (if `gh` is authed and the repo uses issues):
   ```bash
   gh issue list --state all --search '<term>' --limit 30
   gh issue view <n> --comments
   ```
5. **Follow parent/child and supersession links.** "Superseded by #NNN", "see plan in docs/plans/…" (record doc links as leads for the docs investigator).

## What good evidence looks like

- A TODO entry that states the problem or the requester ("Kaegan wants X because Y")
- An Archived entry with the reason it was dropped or replaced
- An issue comment recording a decision between alternatives
- The commit that added the TODO item, dated before the code it motivated

## Common pitfalls

- **Stale entries.** TODO.md items describe the plan at the time; check the date of the line (`git blame docs/TODO.md`) against the code's ship date.
- **Status lies.** "Completed" sometimes marks a partial ship. Cross-check with the code anchor.
- **Boilerplate.** A generic line ("improve UX") is not a reason.

## What to return

For each relevant item: ID and title, the motivation text quoted verbatim, status and section, date the line was added (from blame), linked PRs/plans, and the file:line or issue URL.
