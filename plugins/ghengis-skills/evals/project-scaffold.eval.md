# Project Scaffold — Evaluation

## TC-1: New Code Project Gets Full 4-Layer Structure
- **prompt:** "Scaffold a new TypeScript API project called 'pulse-api'. It is a REST API for health metrics tracking."
- **context:** Greenfield project. Type: code (or service). Language: TypeScript. No existing files.
- **assertions:**
  - Creates MEMORY.md with project name, type, stage (IDEA), goal, and creation date
  - Creates root CONTEXT.md as a routing table mapping tasks to workspaces
  - Creates workspace CONTEXT.md files for each workspace directory (src/, tests/, docs/)
  - Creates .claude/CLAUDE.md under 150 lines with @ includes for detailed content
  - Creates .claude/rules/typescript.md with TypeScript-specific rules (strict mode, interfaces, const defaults)
  - Creates .claude/rules/tests.md with test conventions
  - MEMORY.md folder map matches the generated directory structure
- **passing_grade:** 5/7 assertions must pass

## TC-2: Existing Project Gets Cautious Retrofit
- **prompt:** "Add Claude Code structure to my existing Python project. It already has src/ and tests/ directories and a README.md."
- **context:** Existing project with some structure. Has src/, tests/, README.md. Does NOT have MEMORY.md, CONTEXT.md, or .claude/.
- **assertions:**
  - Scans for existing files before creating anything
  - Does NOT overwrite existing files (src/, tests/, README.md are preserved)
  - Creates only missing files: MEMORY.md, CONTEXT.md, workspace CONTEXT.md files, .claude/ directory
  - Reports what was created vs. what was skipped (with reasons for skips)
  - May suggest improvements to existing files (like README.md) without modifying them
- **passing_grade:** 4/5 assertions must pass

## TC-3: MEMORY.md Follows Token Budget
- **prompt:** "Scaffold a client project called 'acme-dashboard' for Acme Corp. It is a React dashboard for their internal metrics."
- **context:** Client project type. Client: Acme Corp. Framework: React.
- **assertions:**
  - MEMORY.md includes all required fields: project name, type (Client Project), stage, goal, client name, created date
  - MEMORY.md includes a Folder Map section listing all workspaces
  - MEMORY.md includes Conventions section with project slug and canonical source rules
  - MEMORY.md includes Current State section with stage, blockers, next action
  - MEMORY.md stays within approximately 800 token budget (not excessively long)
  - Client-specific workspaces are included: client/, deliverables/
- **passing_grade:** 5/6 assertions must pass

## TC-4: CONTEXT.md is Pure Routing (No Work)
- **prompt:** "Scaffold a research project called 'llm-benchmarks' for evaluating LLM performance across tasks."
- **context:** Research type project. Workspaces: research/, experiments/, docs/.
- **assertions:**
  - Root CONTEXT.md contains ONLY task-to-workspace routing (no actual work or content)
  - CONTEXT.md includes the routing table mapping task types to workspace directories
  - CONTEXT.md includes the canonical source rule ("Every fact lives in ONE file")
  - CONTEXT.md includes the one-way dependency rule
  - CONTEXT.md stays within approximately 300 token budget
  - Research-specific workspaces appear in routing: research/, experiments/, docs/
- **passing_grade:** 4/6 assertions must pass

## TC-5: Language-Specific Rules Generation
- **prompt:** "Scaffold a Flutter mobile app project called 'fittrack' for fitness tracking."
- **context:** Dart/Flutter project. Should generate Flutter-specific rules, not Python or TypeScript rules.
- **assertions:**
  - Creates .claude/rules/ directory with language-appropriate files
  - Generates a Flutter/Dart rules file (not Python or TypeScript rules)
  - Flutter rules cover relevant conventions (widget patterns, state management, platform channels)
  - Creates .claude/rules/tests.md (generated for ALL project types)
  - Does NOT generate irrelevant language rules (no python.md, no typescript.md)
- **passing_grade:** 4/5 assertions must pass
