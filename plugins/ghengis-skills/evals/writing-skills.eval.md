# Writing Skills — Evaluation

## TC-1: TDD-on-Documentation flow

- **prompt:** "Create a new skill for managing PostgreSQL migrations."
- **assertions:**
  - Skill identifies a baseline failure scenario BEFORE writing SKILL.md
  - Dispatches a subagent (or simulates) without the skill loaded
  - Documents what the subagent did wrong as the "failing test"
  - Then writes the SKILL.md addressing those specific failures
  - Re-tests with skill loaded to confirm behavior changed
- **passing_grade:** 4/5 must pass

## TC-2: Description rules enforced

- **prompt:** "Write a description for this new skill."
- **assertions:**
  - Description starts with "Use when..." or "TRIGGER when..."
  - Includes specific symptoms/contexts/user phrasings, not generic statements
  - No underscores or parentheses in `name`
  - Under 1024 characters total frontmatter
  - Does NOT summarize the skill's process ("This skill teaches X...")
- **passing_grade:** 4/5 must pass

## TC-3: Anti-pattern section required

- **prompt:** "I've drafted a skill, can you review it?" (skill missing anti-patterns section)
- **assertions:**
  - Skill flags the missing anti-patterns section as a gap
  - Suggests at least 3-5 anti-patterns based on the skill's domain
  - Each anti-pattern has Why-it-fails + Fix
- **passing_grade:** 3/3 must pass

## TC-4: Refusal for project-specific guidance

- **prompt:** "Let's write a skill that says 'always use our internal logger called foobar_logger in this codebase'."
- **assertions:**
  - Skill recognizes this is project-specific, not reusable
  - Suggests putting it in `CLAUDE.md` instead
  - Refuses to create the skill (or strongly pushes back before creating)
- **passing_grade:** 2/3 must pass

## TC-5: Cross-references to existing ghengis-skills

- **prompt:** "Create a new debugging skill."
- **context:** Ghengis-skills already has `systematic-debugging`.
- **assertions:**
  - Skill flags the existing systematic-debugging skill
  - Asks whether the new skill is complementary, replacement, or duplicate
  - If complementary, ensures the new skill has explicit cross-refs to systematic-debugging
  - Does NOT create a duplicate skill silently
- **passing_grade:** 3/4 must pass

## TC-6: PQL validation handoff

- **prompt:** "I'm done writing the SKILL.md."
- **assertions:**
  - Skill suggests running pql-validation on the frontmatter description
  - Mentions the `skill-port` chain as the canonical pipeline
  - Does not declare done without quality check
- **passing_grade:** 2/3 must pass

## TC-7: Eval file alongside SKILL.md

- **prompt:** "Write the new skill for me."
- **assertions:**
  - Skill creates `plugins/ghengis-skills/skills/<name>/SKILL.md`
  - ALSO creates `plugins/ghengis-skills/evals/<name>.eval.md`
  - Eval has 4-8 test cases
  - Each test case has assertions and a passing grade
- **passing_grade:** 3/4 must pass

## TC-8: Porting adaptations table

- **prompt:** "Port the X skill from superpowers into ghengis-skills."
- **assertions:**
  - Ghengis version includes a table at the top showing what's different from the source
  - Cross-references the source skill as inspiration, not authority
  - Doesn't blindly copy file paths or skill names that don't exist in ghengis-skills
- **passing_grade:** 3/3 must pass
