---
name: create-verification-skill
description: Use when a repo has no scripted way to drive the real app and prove that a UI, CLI, TUI, service, or device feature works the way a user would see it - "make a verify skill for this repo", "make a control skill", "how do we prove this actually works", "/create-verification-skill". Generates a project-local verify-<app> skill (launch, doctor, drive, evidence, cleanup) plus a feature map, visible to both Claude Code and pi, and runs it once end to end before handing it over.
allowed-tools: Read Write Edit Bash Grep Glob Agent
---

# Create a verification skill

Every serious project needs a scripted way to drive the real app and prove behavior: launch it, exercise a feature the way a user would, and capture evidence. This skill generates that as a project-local skill, `verify-<app>/`, tailored to the repo. You write it for the **next agent**, not for a human: it will be read cold, mid-task, by an agent that has never seen the app.

## Port notes

| | |
|---|---|
| Source | `cursor/plugins/pstack` → `skills/create-verification-skill/` (mirror: `backnotprop/pstack`) |
| License | MIT |
| Credit | poteto |
| What changed | Output location made concrete for Claude Code and pi (canonical folder + pi exposure step). Drive options mapped to this user's tools (Playwright, claude-in-chrome, the `run` skill, Bash/tmux, serial for firmware). Added When NOT to Use, Anti-Patterns, Cross-References. Generation steps, proof standards, and the feature-map contract kept. |

## When to Use

- A repo where "it works" has only ever meant "the tests pass"
- Before a long autonomous run (`adw`, `auto-validate`, `gauntlet`) that needs a real proof step
- When verification keeps being improvised per session

## When NOT to Use

- A `verify-*` skill already exists → `maintain-verification-skill`
- One-off "does this run?" → the `run` skill
- Unit-level behavior → `test-driven-development`

## Where the skill goes (both harnesses)

1. If the repo already keeps project skills in `.claude/skills/`, `.pi/skills/`, or `.agents/skills/`, use that folder.
2. Otherwise write the canonical copy to **`.claude/skills/verify-<app>/`** (Claude Code loads it).
3. Expose the same folder to **pi**, which discovers project skills in `.pi/skills/` and `.agents/skills/`:
   - preferred: a directory link `.pi/skills/verify-<app>` → `.claude/skills/verify-<app>` (Windows: `cmd /c mklink /J .pi\skills\verify-<app> .claude\skills\verify-<app>`; POSIX: `ln -s ../../.claude/skills/verify-<app> .pi/skills/verify-<app>`). pi dedupes linked aliases by canonical path.
   - or: add the folder's path to the `skills` array in the project's `.pi/settings.json`.
4. Confirm both harnesses list `verify-<app>` (Claude Code: the skill list; pi: `pi config` or the startup skill list). One copy, two loaders. Never maintain two diverging copies.

## 1. Interview the repo, not the user

Answer from the codebase; ask the user only what you cannot observe:

- **Surface:** what does a user touch? Web UI, CLI/TUI, desktop app, API, mobile app, firmware over serial/BLE, library. Pick the primary one; note the rest.
- **Run:** how does it start locally? Prefer the repo's own documented command (package scripts, Makefile, README, `CONTEXT.md`). Note ports, env vars, seed data, auth.
- **Drive:** how can an agent interact with it programmatically? Existing harnesses first: Playwright/Cypress specs, expect scripts, PTY helpers, curl-able endpoints, a debug port. Then a generic recipe: Playwright or browser automation (claude-in-chrome) for web and Electron; a tmux/PTY session via Bash for CLI/TUI; plain HTTP for services; serial commands for devices.
- **Observe:** screenshots, ARIA snapshots, terminal transcripts, response bodies, logs, exit codes, DB rows.
- **Isolate:** can two instances run side by side (ports, data dirs, profiles)? If not, say so in the generated skill. Refusing to double-drive a shared instance beats corrupting the user's session.

If the checkout does not build or start as-is, fix that first or report it precisely. A skill written against a broken base teaches wrong steps. When an irrelevant missing asset blocks startup, the generated skill may create it, clearly marked as verification scaffolding, and remove it in cleanup.

## 2. Generate the skill

Write `verify-<app>/SKILL.md` with YAML frontmatter (`name: verify-<app>`, and a `description` that names the app, the surface, and when to reach for it; without frontmatter the skill never registers). Sections, each grounded in what the interview found, **no placeholders left**:

- **Launch:** the exact command and the readiness signal (log line, port answering, prompt). Include teardown. For a short-lived CLI/TUI: build or install once, then start each drive in its own isolated PTY or tmux session.
- **Doctor:** one read-only check for "is this instance worth driving?": process up, right build, port owned by us, auth valid. Run first, and whenever anything looks off.
- **Drive:** the harness recipe with this repo's real selectors and commands. Prefer stable handles (ARIA roles and names, data attributes, prompt strings, route paths) over coordinates and tab order.
- **Evidence:** what to capture and where it goes. Proof standards: exercise the real user path, not internal setters or test-only endpoints; capture the action **and** the resulting state; verify side effects (files written, rows inserted, messages sent) alongside what is visible; mocks only where a production boundary already isolates the external system. When the safe path is a dry-run or test mode, verify what it actually skips by observing (files, network, git refs), not by trusting its name.
- **Cleanup:** tear down what the run created. Never kill by process name; kill what you started. Cleanup removes instances and scratch state, **never the evidence**: proof artifacts survive teardown in a location the skill names.
- **Helpers:** every shipped script is executable and its invocation is shown in the skill body.

## 3. Seed the feature map

Create `verify-<app>/features/README.md` plus one file per user-facing feature (start with the top 3-5 from routes, commands, menus, docs). Follow `references/feature-map-example/` (a README index plus one file per feature). Each feature file has an H1, one paragraph of user-visible behavior, then exactly four H2s in order: `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, `Gotchas`. The map is the repo's maintained verification source: a proof that drives one convenient entry point is incomplete when the map lists others.

## 4. Prove the generated skill before handing it over

Run its own instructions end to end once: launch, doctor, drive ONE mapped feature, capture evidence, clean up. After cleanup, confirm the evidence still exists at the named location; a cleanup that eats the proof fails this step. Fix what fails, and run the generated cleanup after every failed iteration so broken attempts don't strand processes and ports. **A generated skill that was never executed is a draft, not a deliverable.**

## 5. Offer the maintenance loop

Point the user at `maintain-verification-skill` for keeping the map honest as the app changes. Suggest a cadence only if asked.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Asking the user how the app runs before reading the repo | Wastes their time; the answer is in scripts/README | Interview the repo first |
| Placeholder selectors or `<command>` left in the skill | Next agent fails cold | Every command is real and was run |
| Handing over without a live run | Untested instructions rot instantly | Step 4 is mandatory |
| Cleanup that deletes proof artifacts | Nothing left to show | Evidence lives outside the scratch state |
| `pkill node` / kill by name | Kills the user's own sessions | Track and kill PIDs you started |
| Two copies for Claude Code and pi | They drift apart | One canonical folder, linked or listed for pi |
| Driving through test-only endpoints | Proves the test path, not the user path | Real user entry points only |
| Implementation details in the feature map | Map rots with every refactor | User paths, handles, commands, observable proof |

## Cross-References

- **`maintain-verification-skill`** — the upkeep loop for what this skill generates.
- **`run`** — one-off launch-and-look; this skill makes that repeatable.
- **`claude-in-chrome`** — browser driving and screenshots for web surfaces.
- **`auto-validate`** / **`adw`** / **`gauntlet`** — consumers: their gates can call the verify skill for real proof.
- **`completion-enforcer`** — "done" requires the evidence this skill captures.
- **`how`** — to understand a feature's entry points before mapping it.
- **`writing-skills`** — frontmatter and description rules for the generated SKILL.md.
- **`show-me-your-work`** — evidence standards when reporting the proof run.
