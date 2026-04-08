# Blueprint Compilation — Evaluation

## TC-1: Recognizes Repeated Workflow Pattern
- **prompt:** "I keep running the same sequence: run pytest, check coverage, update the badge in README, then commit. I do this every time I finish a feature. Can this be automated?"
- **context:** User describes a 4-step workflow they repeat frequently. Classic blueprint compilation candidate -- 3+ repetitions implied, all steps are deterministic.
- **assertions:**
  - Identifies this as a compilation candidate (repeated structured workflow)
  - Recognizes the trace-detect-compile flow applies here
  - Classifies most steps as "code" type (deterministic tool calls: pytest, coverage check, badge update, git commit)
  - Proposes a trigger pattern (e.g., "run post-feature checks" or similar)
  - Includes a blueprint structure with ordered steps, types, and dependencies
- **passing_grade:** 4/5 assertions must pass

## TC-2: Correctly Classifies Step Types (Code vs. Agent)
- **prompt:** "Here is my deployment workflow: 1) run tests, 2) build the project, 3) review build output for warnings, 4) deploy to staging, 5) run health check, 6) write a summary of what changed."
- **context:** 6-step workflow. Steps 1, 2, 4, 5 are deterministic tool calls. Steps 3 and 6 require LLM judgment.
- **assertions:**
  - Classifies steps 1, 2, 4, 5 as "code" type (deterministic, same tool + args pattern)
  - Classifies step 3 (review warnings) as "agent" type (requires judgment)
  - Classifies step 6 (write summary) as "agent" type (requires interpretation)
  - Notes the token savings: 4 code steps at zero token cost, only 2 LLM calls needed
  - Defines dependencies between steps (e.g., step 2 depends on step 1 passing)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Knows When NOT to Compile
- **prompt:** "I wrote a blog post yesterday and might write another one next month. Should I create a blueprint for blog writing?"
- **context:** Creative task, done infrequently (not 3+ repetitions), outputs should vary each time.
- **assertions:**
  - Advises against compilation for this workflow
  - Cites at least 2 valid reasons: creative tasks should produce varied output, insufficient repetitions (below 3+ threshold), or task is not yet stable
  - Does NOT generate a blueprint structure
  - May suggest when compilation would become appropriate (e.g., "if you develop a consistent editorial process with fixed review steps")
- **passing_grade:** 3/4 assertions must pass

## TC-4: Compilation Threshold and Validation
- **prompt:** "I have run the same data import pipeline 5 times with identical structure. All succeeded. 4 of the 5 steps use the same tools with the same arguments. Should I compile this?"
- **context:** Strong compilation signal: 5 matches (above 3+ threshold), all succeeded, >80% code steps.
- **assertions:**
  - Strongly recommends compilation (clear pattern with high confidence)
  - References the threshold: 3+ traces with matching structural signature, all successful
  - Notes the >80% code steps ratio as a strong positive signal
  - Mentions validation requirements: AST safety checks, regression testing against original traces
  - Includes success rate tracking and fallback behavior (code step fails -> falls back to agent)
- **passing_grade:** 4/5 assertions must pass

## TC-5: Progressive Compilation Awareness
- **prompt:** "We just started a new deployment process last week. We have done it twice so far and the steps are still changing. Should we compile?"
- **context:** Below threshold (only 2 executions), workflow still evolving. Should NOT compile yet.
- **assertions:**
  - Advises waiting before compilation
  - Cites below-threshold count (2 < 3 minimum)
  - Notes the workflow is still being iterated on (not yet stable)
  - Suggests continuing to record traces and revisiting after 3+ successful executions with stable structure
- **passing_grade:** 3/4 assertions must pass
