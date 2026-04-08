# PQL Anti-Pattern Reference

35 anti-patterns across 6 categories. Each pattern describes a common prompt quality issue, its severity, and an actionable fix.

**Severity levels:**
- **warn** -- The prompt will likely work, but output quality or clarity could be improved.
- **critical** -- The prompt is likely to produce poor output, unsafe behavior, or runaway execution. Fix before sending.

---

## Task (7 patterns)

Patterns that detect problems with how the task itself is described.

### 1. vague_task_verb
**Severity:** warn

**What it catches:** Prompts that use weak, non-specific verbs like "handle", "deal with", "take care of", "work on", "look at", "look into", "figure out", "sort out", "manage", "address", "tackle", or "process". These verbs do not tell the model what action to take.

**Fix:** Replace vague verbs with specific ones: "parse", "refactor", "create", "delete", "validate", "extract", "migrate", "deploy", etc.

---

### 2. dual_task
**Severity:** warn

**What it catches:** Prompts that combine multiple unrelated tasks using phrases like "and also", "and then also", "plus also", or that chain three or more "and" clauses together. Cramming tasks reduces quality on all of them.

**Fix:** Split into separate prompts -- one task per prompt produces better results.

---

### 3. no_success_criteria
**Severity:** warn

**What it catches:** Prompts that use subjective quality words without measurable criteria: "looks better", "improve", "make it good", "make it better", "make it nicer", "make it cleaner", "make it faster". The model cannot optimize for a target it cannot measure.

**Fix:** Define measurable success criteria: "response time under 200ms", "all tests pass", "score above 0.9", "fewer than 5 linter warnings".

---

### 4. over_permissive
**Severity:** critical

**What it catches:** Prompts that delegate decision-making entirely to the model: "do whatever", "whatever you think", "whatever you want", "up to you", "your call", "your choice", "feel free to", "use your best judgment". This produces unpredictable and inconsistent results.

**Fix:** Provide explicit constraints instead of open-ended delegation. Tell the model exactly what to do, what not to do, and what boundaries to respect.

---

### 5. emotional_description
**Severity:** warn

**What it catches:** Prompts that use emotionally charged language instead of technical descriptions: "terrible", "disgusting", "awful", "horrible", "worst", "stupid", "idiotic", "dumb", "garbage", "trash", "useless", "pathetic". Emotional language wastes tokens and provides no actionable information.

**Fix:** Replace emotional language with specific technical observations: "the function returns None instead of a list", "the API response takes 8 seconds", "the CSS layout breaks at viewports under 768px".

---

### 6. scope_too_large
**Severity:** critical

**What it catches:** Prompts that request full rewrites or rebuilds: "rewrite the entire", "from scratch", "complete overhaul", "rebuild the whole", "redo everything", "start over", "start fresh", "replace everything". Full rewrites in a single prompt almost always produce worse results than incremental changes.

**Fix:** Break large rewrites into incremental steps. Start with the most critical component. Migrate one module at a time.

---

### 7. implicit_reference
**Severity:** warn

**What it catches:** Prompts that reference prior work without specifics: "like last time", "like before", "the same thing", "the usual way", "the same approach", "fix it again", "do it like before", "you already know which one". The model has no memory of prior conversations unless you provide context.

**Fix:** Reference specific prior context: "like the auth refactor in PR #42" instead of "like last time". Include the relevant code, output, or decision you are referencing.

---

## Context (6 patterns)

Patterns that detect missing or assumed context.

### 8. assumed_knowledge
**Severity:** warn

**What it catches:** Prompts that assume the model remembers prior context or possesses shared knowledge: "you know what I mean", "you know the drill", "obviously", "as you already know", "it's obvious", "it's clear", "goes without saying", "needless to say".

**Fix:** State context explicitly -- the model has no memory of prior conversations unless provided. Spell out what "it" refers to, what the current state is, and what background is relevant.

---

### 9. no_project_context
**Severity:** warn

**What it catches:** Prompts longer than 15 characters that contain no reference to a specific project, directory, file path, file extension, framework, or codebase. Generic prompts produce generic answers.

**Fix:** Specify the project, directory, or file: "In apps/server/agents/base.py, ...", "using FastAPI with Pydantic", "in the React frontend under src/components/".

---

### 10. hallucination_invite
**Severity:** warn

**What it catches:** Prompts that ask the model for specific statistics, data, numbers, or facts it likely does not have: "top 10 statistics", "best data", "latest trends", "what percentage of", "give me exact numbers". Models confabulate statistics when they do not know the answer.

**Fix:** Ask the model to search for current data or explicitly say "cite sources". Better yet, provide the data yourself and ask the model to analyze it.

---

### 11. undefined_audience
**Severity:** warn

**What it catches:** Prompts that request written content (blog posts, articles, guides, tutorials, docs, reports, summaries) without specifying who the audience is. Content quality depends heavily on audience calibration.

**Fix:** Define the target audience: "for senior Python developers", "for non-technical stakeholders", "for junior engineers with 0-2 years experience".

---

### 12. no_prior_failure_context
**Severity:** warn

**What it catches:** Prompts that reference a recurring failure without providing failure details: "still doesn't work", "fix it again", "tried everything", "keeps failing", "keeps breaking", "keeps crashing". Without the error message and what you already tried, the model will repeat the same suggestions.

**Fix:** Include the error message, stack trace, and what you already tried. "I tried X and got error Y. The relevant code is Z."

---

### 13. missing_constraints
**Severity:** warn

**What it catches:** Prompts that contain no constraint language whatsoever -- no "must", "should", "require", "only", "never", "always", "do not", "avoid", "ensure", "within", "at most", "at least", "maximum", "minimum". Unconstrained prompts give the model too much freedom.

**Fix:** Add explicit constraints: "must not exceed 100 lines", "only use stdlib", "avoid external dependencies", "must be backward compatible", "do not modify the public API".

---

## Format (6 patterns)

Patterns that detect missing or vague output format specifications.

### 14. missing_output_format
**Severity:** warn

**What it catches:** Prompts longer than 20 characters that do not specify an output format -- no mention of JSON, YAML, markdown, table, list, code block, or any format directive. Without a format spec, the model picks one at random.

**Fix:** Specify the output format: "as JSON", "as a markdown table", "as a Python code block", "as a numbered list with explanations".

---

### 15. implicit_length
**Severity:** warn

**What it catches:** Prompts that use vague length words: "short", "brief", "concise", "long", "detailed", "comprehensive", "thorough". These words mean different things to different people and different models.

**Fix:** Specify exact length: "200 words", "3 paragraphs", "10 bullet points", "under 50 lines of code" instead of "short" or "detailed".

---

### 16. vague_aesthetic
**Severity:** warn

**What it catches:** Prompts that use subjective visual descriptions: "looks nice", "looks good", "make it pretty", "make it beautiful", "clean looking", "modern design", "sleek", "cool", "professional looking". These are not actionable.

**Fix:** Define specific visual requirements: "use 16px padding, blue #3B82F6 buttons, rounded-lg corners", "follow the existing design system", "match the Figma mockup at [URL]".

---

### 17. no_example_provided
**Severity:** warn

**What it catches:** Prompts that do not include any example of the desired output -- no "for example", "e.g.", "such as", "like this", "here's", "sample", "template", "pattern", "similar to", or code blocks. Examples dramatically reduce ambiguity.

**Fix:** Include an example of the desired output. Even a partial or simplified example helps the model understand what you want.

---

### 18. ambiguous_list_request
**Severity:** warn

**What it catches:** Prompts that ask for a list without specifying how many items: "list the things", "give me some options", "enumerate all ideas", "provide suggestions", "list some ways". Without a count, you might get 3 items or 30.

**Fix:** Specify how many items: "list 5 options" instead of "list some options", "give me the top 3 recommendations", "enumerate exactly 10 steps".

---

### 19. no_tone_specified
**Severity:** warn

**What it catches:** Prompts that ask for written communication (email, message, letter, announcement, memo, reply) without specifying the tone. Tone mismatches are the most common complaint about AI-written communications.

**Fix:** Specify the tone: "professional", "casual", "empathetic", "assertive", "formal but warm", "direct and concise".

---

## Scope (6 patterns)

Patterns that detect missing boundaries and constraints on what the model should touch.

### 20. no_scope_boundary
**Severity:** warn

**What it catches:** Prompts longer than 15 characters that contain no reference to a specific file, module, function, class, method, component, route, endpoint, table, schema, or line range. Without scope, the model may make changes in unexpected places.

**Fix:** Specify scope: "in agents/orchestrator.py", "the `route()` method", "lines 45-60", "only the login component".

---

### 21. no_stack_constraints
**Severity:** warn

**What it catches:** Prompts that request building an application, API, service, server, frontend, backend, dashboard, or system without specifying the technology stack. The model will pick a stack for you, and it may not be what you want.

**Fix:** Specify the tech stack: "using FastAPI with Pydantic", "in TypeScript with Express", "React with Next.js and Tailwind CSS".

---

### 22. unbounded_iteration
**Severity:** critical

**What it catches:** Prompts that set no limit on repetition: "keep going", "keep trying", "keep improving", "keep optimizing", "do this until", "don't stop until", "iterate until", "infinitely improve", "forever refine". Unbounded loops waste resources and can run indefinitely in agentic systems.

**Fix:** Set a fixed iteration limit: "try 3 approaches", "iterate at most 5 times", "spend no more than 10 minutes on this".

---

### 23. no_error_handling_spec
**Severity:** warn

**What it catches:** Prompts that request building a function, method, endpoint, handler, service, parser, or processor without mentioning error handling, edge cases, validation, fallback behavior, or what to do when things go wrong.

**Fix:** Specify error handling: "raise ValueError on invalid input", "return None on failure", "retry 3 times with exponential backoff", "log the error and return a default value".

---

### 24. no_performance_constraint
**Severity:** warn

**What it catches:** Prompts that ask for performance optimization without a measurable target: "optimize", "speed up", "make it fast", "make it faster", "improve performance", "improve speed", "improve throughput". Without a target, the model cannot know when to stop optimizing.

**Fix:** Set a measurable target: "response time under 200ms", "process 1000 items/second", "reduce memory usage below 512MB", "cold start under 3 seconds".

---

### 25. no_backward_compat
**Severity:** warn

**What it catches:** Prompts that ask to refactor, migrate, upgrade, update, change, modify, or replace an API, interface, schema, database, model, protocol, format, or contract without specifying whether backward compatibility is required. This is the source of most breaking-change incidents.

**Fix:** Specify backward compatibility: "must remain backward compatible", "breaking change is acceptable with a migration path", "add v2 endpoint alongside v1".

---

## Reasoning (5 patterns)

Patterns that detect logical issues, contradictions, or reasoning anti-patterns.

### 26. cot_on_reasoning_model
**Severity:** warn

**What it catches:** Prompts that include chain-of-thought instructions: "think step by step", "reason through this", "work step by step", "explain your reasoning", "show your thought process", "let's think carefully". These are unnecessary with modern reasoning models (o1, o3, DeepSeek R1, Qwen3) that reason internally.

**Fix:** Remove chain-of-thought instructions when using reasoning models. They already do it. Adding explicit CoT instructions can actually degrade performance by conflicting with internal reasoning.

---

### 27. contradictory_instructions
**Severity:** critical

**What it catches:** Prompts that contain directly contradictory directives: asking to "be brief" and "be detailed" in the same prompt, or saying "don't use X" and "make sure to use X". Contradictions cause unpredictable output as the model tries to satisfy both requirements.

**Fix:** Remove contradictory instructions. Pick one direction and be consistent. If you need both brevity and detail, specify which sections should be brief and which should be detailed.

---

### 28. roleplay_without_purpose
**Severity:** warn

**What it catches:** Prompts that assign an inflated persona without practical purpose: "you are an expert", "act as a genius", "pretend you're a world-class developer", "behave as a 10x engineer", "play the role of a legendary architect". With capable models, this adds no value and wastes tokens.

**Fix:** Provide domain context and constraints instead of role inflation. "You have access to our FastAPI codebase and should follow PEP 8" is more useful than "you are a world-class Python expert".

---

### 29. prompt_injection_risk
**Severity:** critical

**What it catches:** Prompts that contain patterns resembling prompt injection attacks: "ignore all previous instructions", "disregard your rules", "override your safety", "pretend you have no restrictions", "jailbreak", "DAN mode", "developer mode override". Whether intentional or accidental, these patterns cause unpredictable behavior.

**Fix:** Remove injection-like patterns. If you need to override a specific behavior, use the proper configuration mechanism (system prompt, tool permissions, etc.) rather than instructing the model to ignore its own rules.

---

### 30. negative_framing
**Severity:** warn

**What it catches:** Prompts that frame instructions negatively: "don't make it bad", "don't mess it up", "don't forget", "don't miss", "don't skip", "avoid being slow", "not too complicated". Negative framing forces the model to reason about what NOT to do, which is less effective than stating what TO do.

**Fix:** Frame instructions positively: "make it readable" instead of "don't make it ugly", "include error handling" instead of "don't forget error handling", "keep it under 100 lines" instead of "don't make it too long".

---

## Agentic (5 patterns)

Patterns specific to agentic workflows -- autonomous agents, subagent dispatch, multi-step execution. These are only relevant when the prompt drives an agent that will take actions autonomously.

### 31. no_starting_state
**Severity:** critical

**What it catches:** Agentic prompts that do not specify the starting state -- no mention of the current branch, commit, version, existing code state, or initial conditions. Without a starting state, the agent cannot reason about what has already been done.

**Fix:** Specify the starting state: "starting from the main branch", "given the current code in base.py", "the database currently has schema v3", "the test suite currently passes with 42 tests".

---

### 32. no_target_state
**Severity:** critical

**What it catches:** Agentic prompts that do not specify what the end result should look like -- no mention of target state, goal, desired result, expected outcome, or deliverable. Without a target state, the agent has no way to know when it has succeeded.

**Fix:** Define the target state: "the result should be a working login page with tests passing", "the API should return paginated results with cursor-based navigation", "all 3 migration scripts should run without errors".

---

### 33. no_stop_condition
**Severity:** critical

**What it catches:** Agentic prompts that have no stop condition -- no mention of when to stop, what signals completion, iteration limits, time bounds, or success criteria that terminate execution. Without a stop condition, an agent can loop indefinitely.

**Fix:** Set a stop condition: "stop after all tests pass", "at most 5 iterations", "complete when CI is green", "deadline: 10 minutes", "stop if the error persists after 3 attempts".

---

### 34. unlocked_filesystem
**Severity:** critical

**What it catches:** Agentic prompts that grant unrestricted filesystem access: "edit any file", "modify all files", "whatever files you need", "free rein", "carte blanche", "full access", "unrestricted access". Unrestricted filesystem access is the most common cause of agents making unintended changes.

**Fix:** Restrict filesystem scope: "only modify files in apps/web/src/app/login/", "do not touch configuration files", "changes limited to the agents/ directory".

---

### 35. no_human_review
**Severity:** critical

**What it catches:** Agentic prompts that skip human review before consequential actions: "automatically merge", "directly deploy", "push without review", "skip review", "bypass approval", "straight to production", "directly to main". Autonomous deployment without review is the fastest path to production incidents.

**Fix:** Include a human review step: "create a PR for review", "wait for approval before deploying", "stage the changes and notify me", "run in dry-run mode first".

---

## Quick Scoring Reference

The PQL scoring system deducts from a perfect 1.0:
- Each **warn** deducts 0.04
- Each **critical** deducts 0.10
- Score is clamped to [0.0, 1.0]

| Score Range | Interpretation |
|-------------|---------------|
| 0.9 - 1.0 | Good. Minor improvements possible. |
| 0.7 - 0.89 | Fair. Several issues worth fixing. |
| 0.5 - 0.69 | Poor. Multiple anti-patterns detected. Rewrite recommended. |
| Below 0.5 | Bad. Fundamental issues. Do not send this prompt without a rewrite. |
