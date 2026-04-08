# OORT Cascade — Evaluation

## TC-1: Complex Multi-Department Task Triggers Cascade
- **prompt:** "Research our top 3 competitors, build a comparison report, and validate the findings before sending to the leadership team."
- **context:** User has a project with competitor data in `docs/competitors/`. The task spans research, building, and validation -- classic cascade territory.
- **assertions:**
  - Decomposes into at least 3 roles (Researcher, Builder, Validator)
  - Defines a dependency DAG with waves (Researcher in Wave 1, Builder in Wave 2, Validator in Wave 3)
  - Generates role-specific meta-prompts (not generic forwarding of the user request)
  - Identifies the deliverable concretely ("comparison report")
  - Plans parallel execution for independent roles within the same wave
- **passing_grade:** 4/5 assertions must pass

## TC-2: Simple Task Does NOT Trigger Cascade
- **prompt:** "What is the default port for PostgreSQL?"
- **context:** A factual lookup question with a single correct answer. No decomposition needed.
- **assertions:**
  - Does NOT decompose into multiple roles
  - Does NOT create a dependency DAG or mention waves
  - Answers directly in a single pass
  - Response is concise (under 100 words)
- **passing_grade:** 4/4 assertions must pass

## TC-3: Builder-Validator Revision Loop
- **prompt:** "Refactor the auth module from session cookies to JWT tokens. The refactor must pass all existing tests and have no security regressions."
- **context:** Codebase has `src/auth/` with session-based auth, `tests/auth/` with 23 tests. Quality bar is high -- production code with security implications.
- **assertions:**
  - Includes a Validator role that scores output on a rubric (accuracy, completeness, quality, format)
  - Specifies a score threshold (>= 7) for acceptance
  - Plans a revision loop if score is below threshold
  - Caps revision loops at max 2 iterations
  - Builder meta-prompt references researcher findings (not just the raw user request)
- **passing_grade:** 4/5 assertions must pass

## TC-4: Lean Cascade — Minimum Viable Roles
- **prompt:** "Write a Python script that converts CSV files to JSON format."
- **context:** A building task that benefits from validation but does not require research or documentation. Should trigger a lean cascade.
- **assertions:**
  - Uses at minimum Builder + Validator (the minimum viable cascade)
  - Does NOT add Researcher role (no external information needed)
  - Does NOT add Documenter role (not requested)
  - Total roles stay at 4 or fewer
  - Recognizes this as a build-then-validate pattern, not a full 6-role cascade
- **passing_grade:** 4/5 assertions must pass

## TC-5: Handoff Protocol Compliance
- **prompt:** "Analyze our Q1 sales data, identify trends, build a board-ready presentation, and archive the results in our project docs."
- **context:** Sales data in `data/q1_sales.csv`. Project uses MEMORY.md/CONTEXT.md structure. Task needs Researcher, Analyst, Builder, Validator, Documenter.
- **assertions:**
  - Handoffs between roles use structured bullet points (not prose paragraphs)
  - Handoff data includes raw numbers and sources, not just interpretations
  - Total cascade stays at 6 roles or fewer (max limit)
  - Roles are grouped into parallel waves where possible (Researcher + Analyst in Wave 1)
  - Documenter role is included because archiving was explicitly requested
- **passing_grade:** 4/5 assertions must pass
