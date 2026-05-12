---
name: skill-port
pattern: sequential
triggers:
  - event: user_request
    keywords: ["port a skill", "skill-port", "add a new skill", "port this skill", "create a new skill", "run skill-port"]
on_error: fail_fast
estimated_duration: 10-60 minutes
---

## Purpose

Canonical pipeline for creating a new skill or porting one from another skill system (superpowers, anthropic-skills, etc.) into ghengis-skills. Aligns on what the skill should do, writes it TDD-style on documentation, validates the description with pql-validation, and stress-tests via build-validate.

This is exactly the workflow we've been running manually for `brainstorming`, `writing-skills`, `systematic-debugging`, `test-driven-development`, and `finishing-a-development-branch` ports.

## When To Use

- "Let's add a new skill for X"
- "Port the Y skill from superpowers"
- "Take this anthropic-skills template and make it ours"
- After noticing a 3rd time you've repeated the same instruction to Claude

## When NOT To Use

- Editing an existing skill in-place — just edit it (no chain needed)
- Project-specific guidance — put it in `CLAUDE.md`, not a skill
- One-off solutions you won't reuse

## Continuous Execution Principle

Drive through stages. The natural decision point is at brainstorming (does the skill make sense, what should it do); after that, the pipeline runs end-to-end.

## Input Contract

```json
{
  "input": {
    "user_request": "<what the skill should do, or which existing skill to port>",
    "source_skill_path": "<optional: absolute path to the source SKILL.md if porting>",
    "project_root": "/Users/kelemcdaniel/Desktop/ghengis-skills"
  }
}
```

## Stages

### 1. brainstorming
- **Skill:** `ghengis-skills:brainstorming`
- **Reads:** `input.user_request`, optionally `input.source_skill_path`
- **Writes:**
  - `brainstorming.skill_name` (lowercase-hyphens)
  - `brainstorming.purpose` (one sentence: what the skill does)
  - `brainstorming.trigger_conditions` (list — when should it load)
  - `brainstorming.anti_patterns` (list — what would the skill prevent)
  - `brainstorming.cross_refs` (list — related ghengis-skills)
  - `brainstorming.adaptations_from_source` (only if porting — table of differences)
- **Success:** trigger conditions are specific (not "use when working"), anti-patterns are observable, cross-refs point to real skills
- **On fail:** scope unclear; user should clarify before proceeding

### 2. writing-skills (TDD on documentation)
- **Skill:** `ghengis-skills:writing-skills`
- **Reads:** entire scratchpad
- **Writes:**
  - `writing.skill_md_path` (absolute path to new SKILL.md)
  - `writing.eval_path` (absolute path to new eval file)
  - `writing.baseline_failure_scenario` (one paragraph describing what an agent does wrong WITHOUT the skill)
  - `writing.with_skill_scenario` (what they should do WITH it)
- **Success:** SKILL.md exists, frontmatter valid, baseline failure documented

### 3. pql-validation
- **Skill:** `ghengis-skills:pql-validation`
- **Reads:** `writing.skill_md_path` (specifically the frontmatter `description`)
- **Writes:**
  - `pql.score` (0-1)
  - `pql.anti_patterns_found` (list)
  - `pql.suggested_fixes` (list)
- **Success:** `score >= 0.7`. Description has specific triggers, no vague phrasing, no missing scope, no underscores in name.
- **On fail:** loop back to writing-skills with fixes applied — re-validate

### 4. build-validate (adversarial scenario testing)
- **Chain:** `build-validate`
- **Reads:** entire scratchpad
- **The "deliverable" is the new SKILL.md.** Validator's job is to construct pressure scenarios that should trigger the skill, dispatch a subagent on them, and verify:
  - The skill loads when expected (description triggers fire)
  - The skill changes agent behavior in the predicted direction
  - The skill doesn't fire on similar-but-distinct scenarios (no over-matching)
  - Anti-patterns the skill documents are actually closed (try to rationalize past them)
- **Success:** `score >= 7`
- **On fail:** revision loop adds anti-pattern entries to close the loopholes the Validator found

### 5. report
- **Not a skill** — supervisor writes summary
- **Reads:** entire scratchpad
- **Writes:**
  - `report.outcome` ("skill-shipped" | "skill-shipped-with-notes" | "skill-incomplete")
  - `report.files_created` (SKILL.md + eval + maybe supporting docs)
  - `report.cross_refs_updated` (list — other skills that should cross-reference this new one)
  - `report.next_steps` (typically: bump version in package.json + plugin.json, update README.md, mirror to marketplace, commit + push — or invoke `finish-line` chain to do that)

## Failure Modes

| Stage | Failure | Recovery |
|---|---|---|
| brainstorming | Trigger conditions are vague | Force specific symptoms / user phrasings before proceeding |
| writing-skills | Can't articulate baseline failure | Skill probably isn't needed; the model already does the right thing |
| pql-validation | Score < 0.7 | Loop back to writing-skills with autofix applied |
| build-validate | Subagent ignores the skill even when loaded | Description trigger is too vague — rewrite |
| build-validate | Subagent rationalizes past the skill's rules | Add anti-pattern entries; re-test |
| build-validate | Score < 7 after 2 iterations | Outcome `skill-incomplete`; surface the failure modes to user |

## Example Scratchpad (After Successful Run)

```json
{
  "chain": "skill-port",
  "stages_completed": ["brainstorming", "writing-skills", "pql-validation", "build-validate", "report"],
  "input": {
    "user_request": "Port systematic-debugging from superpowers, adapt to ghengis conventions",
    "source_skill_path": "~/.claude/plugins/cache/.../superpowers/5.1.0/skills/systematic-debugging/SKILL.md"
  },
  "brainstorming": {
    "skill_name": "systematic-debugging",
    "purpose": "Force root-cause investigation before any fix",
    "trigger_conditions": ["test failure", "unexpected behavior", "error message", "performance issue"],
    "anti_patterns": ["multiple fixes in parallel", "catching exceptions to silence them", "trusting 'it works now'"],
    "cross_refs": ["test-driven-development", "completion-enforcer", "bug-hunt chain"],
    "adaptations_from_source": [
      "Added Phase 3 (regression test) as explicit handoff to TDD",
      "Cross-refs hallucination-detector for error-message verification"
    ]
  },
  "writing": {
    "skill_md_path": "plugins/ghengis-skills/skills/systematic-debugging/SKILL.md",
    "eval_path": "plugins/ghengis-skills/evals/systematic-debugging.eval.md"
  },
  "pql": {
    "score": 0.85,
    "anti_patterns_found": [],
    "suggested_fixes": []
  },
  "build_validate": {
    "score": 9,
    "outcome": "shipped",
    "iterations_used": 1
  },
  "report": {
    "outcome": "skill-shipped",
    "files_created": ["SKILL.md", "systematic-debugging.eval.md"],
    "cross_refs_updated": ["test-driven-development", "bug-hunt chain"],
    "next_steps": "bump version, update README, run finish-line chain"
  }
}
```
