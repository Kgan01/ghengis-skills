# Meta-Prompting — Evaluation

## TC-1: Role-Specific Prompt Generation
- **prompt:** "I need to build a landing page for our new SaaS product. Research the market, write the copy, and review it for quality."
- **context:** Product is a developer productivity tool. Target audience is engineering managers. The task maps to researcher -> builder -> validator.
- **assertions:**
  - Generates distinct meta-prompts for each role (researcher, builder, validator)
  - Each meta-prompt includes: role identity, original request context, specific deliverable, output format
  - Researcher prompt specifies focus areas and "Do NOT create the final deliverable"
  - Builder prompt references upstream researcher findings in structured format
  - Validator prompt includes a scoring rubric (fulfillment, accuracy, completeness, tone, formatting)
- **passing_grade:** 4/5 assertions must pass

## TC-2: Dependency Context Injection
- **prompt:** "Analyze our API response times from the logs, then build a performance report with recommendations."
- **context:** Logs in `logs/api_access.log`. Two-stage task: analyst first, builder second. Builder depends on analyst output.
- **assertions:**
  - Builder meta-prompt contains an `[INPUT from analyst]` or equivalent structured dependency block
  - Dependency context uses key-value format (not prose paragraphs)
  - Each input block is labeled with the source role name
  - Dependency context is truncated to a reasonable size (300-600 tokens per role)
- **passing_grade:** 3/4 assertions must pass

## TC-3: Correct Role Selection for Task Type
- **prompt:** "Draft an email to our investors updating them on Q1 progress, and have it reviewed for security before sending."
- **context:** Investor relations email. Sensitive content. Maps to the "Email or message draft" task type in the role selection guide.
- **assertions:**
  - Selects communicator role (not generic builder) for email drafting
  - Includes editor role for polish
  - Includes security role for sensitive content review
  - Does NOT select engineer, fabricator, or other irrelevant specialist roles
  - Role selection matches or closely follows the guide: researcher -> communicator -> editor -> security
- **passing_grade:** 4/5 assertions must pass

## TC-4: Revision Loop with Specific Feedback
- **prompt:** "The validator scored the report 5/10. Missing pricing comparison and tone is too casual. Revise it."
- **context:** A builder has produced output that failed validation. This tests whether revision context is injected properly.
- **assertions:**
  - Revision prompt includes the score (5/10)
  - Revision prompt lists ALL specific issues (missing pricing comparison, tone too casual)
  - Includes "Fix ALL listed issues. Do not introduce new problems." or equivalent constraint
  - Labels the revision attempt number (e.g., "Attempt 2")
- **passing_grade:** 3/4 assertions must pass

## TC-5: Execution Boundaries for Agentic Roles
- **prompt:** "Have the engineer implement the new payment endpoint in src/api/payments.ts."
- **context:** Active codebase. The engineer role takes real-world actions (writes files). Needs explicit boundaries.
- **assertions:**
  - Engineer meta-prompt includes an ALLOWED ACTIONS section
  - Engineer meta-prompt includes a FORBIDDEN ACTIONS section
  - Specifies STOP CONDITIONS (when to pause and ask for human review)
  - Boundaries are specific to the task (mentions relevant paths like src/api/)
- **passing_grade:** 3/4 assertions must pass
