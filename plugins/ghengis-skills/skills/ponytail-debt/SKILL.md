---
name: ponytail-debt
description: Use when the user wants to see the deliberate shortcuts in a codebase as a debt ledger - every `shortcut:` comment (and older `ponytail:` ones) with its ceiling and upgrade trigger. TRIGGER on "ponytail debt", "what did ponytail defer", "list the shortcuts", "shortcut ledger", "what corners did we cut", /ponytail-debt. Also when the user names their own marker word ("ponytail debt TODO"). Reports; writes a ledger file only when asked.
allowed-tools: Read Write Bash Grep Glob
model: fast
---

# Ponytail Debt

| Port notes | |
|---|---|
| Source | `DietrichGebert/ponytail` - `skills/ponytail-debt/SKILL.md`, `commands/ponytail-debt.toml` |
| License | MIT, (c) 2026 Dietrich Gebert |
| What changed | Ledger file defaults to `docs/SHORTCUT-DEBT.md` when asked to persist (source suggested `PONYTAIL-DEBT.md`; either is fine if the repo already has one). PowerShell fallback for Windows hosts. ghengis cross-refs. |

Every deliberate ponytail shortcut is marked with a `shortcut:` comment naming its ceiling and upgrade path (older code may say `ponytail:`). This collects them into one ledger so a deferral can't quietly become permanent.

## When NOT to Use

- General TODO/FIXME hunting with ranking: use `ponytail-audit` (or the code graph's rationale nodes in `code-intelligence`).
- The user wants the shortcuts upgraded: list first, then fix the rows they pick under `ponytail`.

## Scan

Grep the repo for comment markers, skipping `node_modules`, `.git`, and build output:

```bash
grep -rnE --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build '(#|//|/[*]) ?(shortcut|ponytail):' .
```

Add other comment prefixes if the stack uses them (`--` for SQL/Lua, `;` for Lisp/asm, `<!--` for HTML). Prefer the harness Grep tool when it exists; on Windows without a POSIX shell use `rg -n "(#|//|/\*) ?(shortcut|ponytail):"`.

If the user names their own marker word (`ponytail debt TODO`), grep for that word instead.

Each hit is one ledger row. The comment prefix keeps prose that merely mentions the convention out of the ledger. Skip hits that are not a deferral, like a note about a keyboard shortcut.

## Output

One row per marker, grouped by file:

```
<file>:<line>, <what was simplified>. ceiling: <the limit named>. upgrade: <the trigger to revisit>.
```

The convention is `shortcut: <ceiling>, <upgrade path>`, so pull the ceiling and the trigger straight from the comment. Want an owner per row too? add `git blame -L<line>,<line> <file>`.

Flag the rot risk: any marker comment that names no upgrade path or trigger gets a `no-trigger` tag, those are the ones that silently rot.

End with `<N> markers, <M> with no trigger.` Nothing found: `No shortcut debt. Clean ledger.`

## Persisting the ledger

Reads and reports only by default, changes nothing. When the user asks to save it, write the ledger to a file (`docs/SHORTCUT-DEBT.md`, or the existing ledger file if the repo has one), with the date and the summary line at the top. Rewrite the whole file each run so it never holds rows for markers that are gone. Do not edit the source comments.

One-shot. "stop ponytail-debt" or "normal mode" to revert.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Grepping the bare word `shortcut` | Pulls in keyboard-shortcut prose and docs | Require the comment prefix before the marker |
| Inventing a ceiling or trigger the comment does not state | The ledger lies about the decision | Copy from the comment; tag `no-trigger` when absent |
| Dropping `no-trigger` rows as "incomplete" | Those are exactly the ones that rot | Keep them, tag them, count them |
| Appending to an old ledger file | Resolved shortcuts linger as phantom debt | Regenerate the whole file each run |
| Fixing the shortcuts during the scan | One-shot report was asked for | List; upgrade later under `ponytail` |
| Scanning `node_modules` / build output | Vendor noise | Exclude `.git`, `node_modules`, `dist`, `build`, vendored dirs |

## Cross-References

- **`ponytail`** - writes the `shortcut: <limit>, <when to upgrade>` comments this skill harvests.
- **`ponytail-review`** / **`ponytail-audit`** - treat these markers as decisions, not findings, unless load crosses the ceiling.
- **`task-tracking`** - move a row whose trigger has fired into `docs/TODO.md`.
- **`code-intelligence`** - rationale nodes (HACK/FIXME/TODO) cover the untagged debt.
