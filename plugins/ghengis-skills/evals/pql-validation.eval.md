# PQL Validation — Evaluation

## TC-1: Detects Vague Verb Anti-Pattern
- **prompt:** "Review this prompt: 'Handle the user data and deal with any issues.'"
- **context:** The prompt under review uses vague verbs ("handle", "deal with") which are Task category anti-patterns.
- **assertions:**
  - Identifies "handle" and "deal with" as vague verbs (Task anti-pattern category)
  - Suggests specific replacements (e.g., "parse", "validate", "transform" instead of "handle")
  - References the correct anti-pattern category (Task)
  - Provides a rewritten version of the prompt with specific verbs
  - Does NOT just say "be more specific" -- gives concrete alternatives
- **passing_grade:** 4/5 assertions must pass

## TC-2: Catches Multiple Anti-Pattern Categories
- **prompt:** "Check this agent prompt: 'Please basically just check the code and make it better. You know what I mean. Keep going until it's perfect.'"
- **context:** This prompt has anti-patterns across at least 4 categories: filler words (Format), vague verbs (Task), assumed knowledge (Context), unbounded iteration (Scope).
- **assertions:**
  - Identifies filler words: "please", "basically", "just" (Format/Token efficiency)
  - Identifies vague verb: "check", "make it better" (Task)
  - Identifies assumed knowledge: "You know what I mean" (Context)
  - Identifies unbounded iteration: "Keep going until it's perfect" (Scope)
  - Suggests specific fixes for each category, not just flagging them
  - Correctly classifies severity (e.g., unbounded iteration as critical, filler words as warn)
- **passing_grade:** 5/6 assertions must pass

## TC-3: Knows All 6 Anti-Pattern Categories
- **prompt:** "What are the PQL anti-pattern categories and give me an example of each?"
- **context:** Testing whether Claude knows the full taxonomy, not just a subset.
- **assertions:**
  - Lists all 6 categories: Task, Context, Format, Scope, Reasoning, Agentic
  - Provides at least one concrete anti-pattern example per category
  - Includes severity levels (warn vs. critical)
  - Examples are specific (not generic descriptions) and match the documented anti-patterns
- **passing_grade:** 3/4 assertions must pass

## TC-4: Suggests Appropriate Prompt Framework
- **prompt:** "I need to write a prompt for an autonomous agent that deploys code to staging. What framework should I use?"
- **context:** Autonomous agent task with real-world side effects. Should map to ReAct + Stop framework.
- **assertions:**
  - Recommends ReAct + Stop framework (not RTF or CO-STAR)
  - Includes required elements: Objective, Starting State, Target State, Allowed Actions, Forbidden Actions, Stop Conditions
  - Adds Checkpoints for intermediate verification
  - Warns about the Agentic anti-pattern category (no starting state, no stop condition, unlocked filesystem)
- **passing_grade:** 3/4 assertions must pass

## TC-5: Good Prompt Passes Validation
- **prompt:** "Validate this prompt: 'You are a Python code reviewer. Analyze src/auth/middleware.py for SQL injection vulnerabilities. Output a JSON array of findings, each with {line_number, severity, description, fix}. Check only this file -- do not modify it. If no vulnerabilities found, return an empty array.'"
- **context:** A well-structured prompt that follows PQL principles: specific verb, context, format, boundaries, single task.
- **assertions:**
  - Recognizes the prompt as high quality (no critical anti-patterns)
  - Identifies specific strengths: clear role, specific task, defined output format, explicit scope boundary
  - Does NOT invent problems that are not there
  - May suggest minor improvements (e.g., specifying the audience or adding error handling) but rates overall quality highly
- **passing_grade:** 3/4 assertions must pass
