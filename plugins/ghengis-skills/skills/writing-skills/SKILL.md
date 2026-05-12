---
name: writing-skills
description: TRIGGER when user says "let's add a skill", "make a skill for X", "port the Y skill from superpowers", "I keep repeating this instruction", "this should be a skill", "create a skill"; OR when noticing a repeated multi-message instruction pattern that would benefit from being captured once. Use to create or edit any SKILL.md file in plugins/ghengis-skills/skills/.
allowed-tools: Read Write Edit Bash Grep Glob
---

# Writing Skills

Skills are reference guides for techniques, patterns, or tools that future Claude instances should apply when the trigger conditions match. They are *not* narratives about how you solved a problem once. A good skill is reusable, specific in its trigger conditions, and provably better than baseline behavior.

**Core principle:** if you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

This is TDD applied to documentation:

| TDD step | Skill creation step |
|---|---|
| Write the failing test | Write a pressure scenario the skill should change |
| Run it, watch it fail | Dispatch a subagent on the scenario without the skill; document the failure |
| Write minimal code | Draft the SKILL.md addressing exactly those failure modes |
| Run it, watch it pass | Dispatch a subagent WITH the skill loaded; verify it now succeeds |
| Refactor | Tighten language, close loopholes, remove unnecessary content |

## When to Use

- Creating a brand-new skill
- Porting an existing skill from `superpowers`, `anthropic-skills`, or another skill system into ghengis-skills
- Editing an existing skill because it's not actually changing agent behavior
- After noticing yourself repeat the same instructions across 3+ sessions ("just one more time I have to remind Claude to X...")

## When NOT to Use

- One-off solutions that won't apply elsewhere
- Project-specific conventions — put those in `CLAUDE.md`, not a skill
- Mechanical constraints enforceable with code (regex check, lint rule, hook) — automate instead of documenting
- Documentation of how something works — that's a README, not a skill
- Stuff already well-documented in official docs

## What Makes a Skill

A skill is:
- A **trigger** in the frontmatter `description` — the conditions under which Claude should load it
- **Instructions** in the body — what to do when those conditions match
- **Anti-patterns** — what NOT to do
- **Cross-references** — related skills and their natural sequencing

A skill is NOT:
- A retelling of a recent debugging session
- A copy-paste of API docs
- A general advice essay
- Anything that can't be exercised against a test scenario

## Directory Structure

```
plugins/ghengis-skills/skills/
  <skill-name>/
    SKILL.md                # required, the entry point
    <topic>.md              # optional reference doc, e.g. plan-format.md
    scripts/                # optional executable code
      <script>.py
```

**Flat namespace** — all skills are siblings under `skills/`. No nesting. Names use lowercase-hyphens. Pick names that future-you will type without thinking ("test-driven-development" not "tdd-methodology-v2").

Add an eval file alongside: `plugins/ghengis-skills/evals/<skill-name>.eval.md` with 4-8 test cases.

## Frontmatter Rules

```yaml
---
name: skill-name
description: <single string, see rules below>
allowed-tools: <space-separated tool names, e.g. Read Write Edit Bash>
---
```

**Description rules** (the trigger):
- Third-person, focused on WHEN to use (not WHAT it does)
- Start with "Use when..." or "TRIGGER when..."
- Include specific symptoms, situations, examples of phrasing users employ
- Under 500 characters if possible, max 1024
- Use letters, numbers, hyphens in `name` only — no parens, no underscores

**Bad description:**
> "A skill for testing things."

**Good description:**
> "Use when implementing any feature or bugfix, before writing implementation code. Forces RED-GREEN-REFACTOR: write the failing test first, run it to confirm it fails for the right reason, write minimal code to make it pass, commit, then refactor."

The description is what Claude scans to decide whether to load the skill. If it's vague, the skill doesn't fire. Treat it as the most important sentence in the file.

**Run `pql-validation` on the description** before shipping. It catches 35+ anti-patterns including vague triggers, missing scope, and prompt-quality issues. The `skill-port` chain wires this in automatically.

## SKILL.md Body Structure

There's no rigid template, but most skills have these sections:

1. **One-paragraph overview** — core principle in 1-2 sentences
2. **When to Use** — specific symptoms and contexts (mirror and expand the description)
3. **When NOT to Use** — boundaries; what triggers a similar-looking but wrong response
4. **The Process / Methodology** — the actual content; numbered steps for sequential skills, principles for flexible ones
5. **Anti-Patterns** — table or list of what NOT to do, with rationale
6. **Cross-References** — related skills, natural sequencing, the chains this skill participates in

Scale length to the topic. A simple skill is 100 lines. A complex one is 400-600. Don't pad.

## The TDD Cycle for Skills

### RED — Watch the failure

Before writing the skill, prove the failure mode is real:

1. Pick a scenario that should trigger the skill once it exists.
2. Dispatch a fresh subagent (no inherited context) with the scenario.
3. Document exactly what they did wrong: which assumptions they made, what they skipped, what rationalizations they used.
4. This is your failing-test evidence.

If the baseline subagent doesn't fail, you don't need the skill yet — the model already does the right thing.

### GREEN — Write the minimal skill

Write the SKILL.md addressing *those specific failures*. Don't pad with content that addresses problems you didn't observe. Don't generalize beyond what you watched fail.

Re-dispatch a subagent with the new skill loaded and the same scenario. Verify they now succeed.

### REFACTOR — Tighten and close loopholes

Once the skill works on the baseline scenario, try to break it:

1. Construct a similar-but-not-identical scenario where the agent might rationalize around the rule.
2. Dispatch a subagent on the new scenario with the skill loaded.
3. If they rationalize, your skill has a loophole. Add the specific anti-pattern, and re-test.

Repeat until the skill holds against adversarial pressure.

This is exactly what the `build-validate` chain does — it can be invoked on a draft skill where the deliverable is the SKILL.md and the Validator's test scenarios are pressure cases.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Writing a SKILL.md without a baseline failure scenario | You don't know if you're fixing a real problem | Run the scenario without the skill first |
| Description summarizes the process ("This skill teaches the 4-phase debugging method...") | Claude doesn't load skills based on what they do, only when to use them | Start with "Use when..." and describe triggers, not content |
| Description is generic ("Use when debugging") | Doesn't differentiate from other skills, fires too often or never | Specific symptoms, user phrasing, scope boundaries |
| Skill is 1000+ lines | Long skills don't get loaded fully into context; people don't read them | Split: SKILL.md is the entry, reference docs are separate files |
| Skill contains a war story ("Last week I was debugging X and...") | Narrative is not a reference; future-Claude can't apply it | Extract the lesson, write the pattern |
| Skill duplicates content of existing skill | Two skills disagree silently when both load | Cross-reference; one skill is the canonical source |
| Anti-pattern section missing | Loopholes don't get closed | List 3-7 specific failure modes with fixes |
| No cross-references | Skill stands alone, never composes | Name the natural predecessors, successors, and chains |
| Description uses underscores or parens | Won't load reliably on some systems | letters-numbers-hyphens-only |
| Skill describes a project-specific convention | Should be in CLAUDE.md, not a skill | Move it, link from the project |

## Cross-References

- **`test-driven-development`** — required background. Writing skills IS TDD on documentation. Read that first.
- **`pql-validation`** — run on the frontmatter description before shipping. Catches the most common skill-quality issues.
- **`brainstorming`** — natural predecessor for non-trivial skills. Talk through what the skill should do before writing it.
- **`build-validate` chain** — use as the validation step. The Validator's job is to break the skill with adversarial test scenarios.
- **`skill-port` chain** — canonical pipeline for porting skills from other systems: brainstorming → writing-skills → pql-validation → build-validate.
- **`meta-prompting`** — 22 role templates. Use these patterns when designing skill triggers and subagent prompts.

## Porting Skills from Other Systems

When porting a skill (e.g., from `superpowers`, `anthropic-skills`, `agent-skills`):

1. **Read the source** — full text, including any reference docs in the skill's directory
2. **Identify what's load-bearing** — the methodology, the anti-patterns, the cross-refs to skills you have
3. **Identify what doesn't apply** — references to skills you don't have, opinionated patterns you disagree with, file paths from their system
4. **Write the ghengis adaptation** — explicitly note what's different from the source in a small table at the top
5. **Cross-reference the original** as inspiration, not as authority
6. **Test against the same scenario** the source skill was built for
7. **Run pql-validation on the new description** — different system, different conventions
8. **Add to README and bump version** — see the project's release pattern
