---
name: blueprint-compilation
description: Use when you notice repeated multi-step workflows that could be automated — teaches how to observe execution patterns, detect structure, and compile them into reusable pipelines
---

# Blueprint Compilation

Self-compiling agent methodology. Agents observe their own execution, detect repeated patterns, and compile them into reusable deterministic pipelines. The core insight: **if you have done a workflow 3+ times with the same structure, it is time to make it a repeatable pipeline.**

## The Self-Compiling Agent Concept

Most agent work follows patterns. A developer asks "run tests, check coverage, update the badge" repeatedly. A deployment sequence always follows the same steps. A code review always checks the same categories.

Self-compiling agents treat this as an optimization opportunity:
1. **Record** what you do (execution traces)
2. **Detect** when you keep doing the same thing (pattern detection)
3. **Compile** the repeated workflow into a reusable pipeline (blueprint generation)
4. **Validate** the compiled pipeline produces the same results (regression testing)
5. **Execute** the pipeline instead of reasoning from scratch next time

This turns expensive, token-heavy LLM reasoning into fast, deterministic execution for known workflows.

## Execution Traces

An execution trace records every step of an agent run. Each step has one of four types:

| Step Type | What It Captures | Example |
|-----------|-----------------|---------|
| **thought** | The agent's reasoning before acting | "I need to check if tests pass before deploying" |
| **tool_call** | A tool invocation with name and arguments | `run_tests(path="src/", coverage=true)` |
| **tool_result** | The output returned by a tool | `{"passed": 47, "failed": 0, "coverage": 92.3}` |
| **output** | The final response delivered to the user | "All 47 tests pass with 92.3% coverage" |

A complete trace also records:
- The original instruction that triggered the run
- Total token consumption and cost
- Whether the execution succeeded
- Total duration

**Key property:** each step is marked as **deterministic** or not. A tool call with identical arguments every time is deterministic. A thought step that varies based on input context is not.

### Example Trace

```
Instruction: "Run the test suite and report results"

Step 0: thought    -> "I need to run pytest on the project"
Step 1: tool_call  -> run_command(cmd="pytest tests/ -v --tb=short")
Step 2: tool_result -> "47 passed, 0 failed, 92.3% coverage"
Step 3: thought    -> "All tests passed, I should format the results"
Step 4: output     -> "Test suite passed: 47/47 tests, 92.3% coverage"
```

## Pattern Detection

Pattern detection groups traces by their **structural signature** -- the sequence of step types and tool names, ignoring variable content.

Two traces match structurally if they follow the same sequence:
```
Trace A: thought -> tool_call:run_command -> tool_result -> thought -> output
Trace B: thought -> tool_call:run_command -> tool_result -> thought -> output
```

These match even if the commands, results, and output text differ, because the *shape* is the same.

### Detection Algorithm

1. **Filter** to successful traces only (failed traces should not become blueprints)
2. **Hash** each trace's structural signature (step types + tool names, ignoring content)
3. **Group** traces by signature hash
4. **Threshold** -- groups with 3+ traces become candidate patterns
5. **Classify** each step position as deterministic or parameterized by comparing values across all matching traces

### Determinism Classification

For each step position across matching traces:

| If the values across traces are... | Classification | Meaning |
|-------------------------------------|---------------|---------|
| Identical every time | **deterministic** | Can be hardcoded |
| Same tool, different arguments | **parameterized** | Can be templated with variable inputs |
| Different tools or different reasoning | **variable** | Needs LLM reasoning |

### Trigger Pattern Generation

From a group of similar instructions, generate a pattern that matches future similar requests:

```
Traces:
  "run tests for the auth module"
  "run tests for the payment module"
  "run tests for the user module"

Generated trigger: "run tests for .+"
```

The algorithm finds common prefix/suffix tokens and inserts wildcards for the varying middle parts.

## Blueprint Structure

A blueprint is a compiled pipeline of sequential steps with dependency tracking.

### Blueprint Metadata

| Field | Purpose |
|-------|---------|
| **name** | Human-readable identifier derived from common instruction words |
| **description** | Auto-generated summary of what the pipeline does |
| **trigger_pattern** | Regex that activates this blueprint on matching instructions |
| **steps** | Ordered list of pipeline steps |
| **version** | Incremented on recompilation |
| **usage_count** | How many times this blueprint has been executed |
| **success_rate** | Rolling success percentage (used to decide when to disable) |

### Step Types

Every step in a blueprint is one of two types:

**Code steps** -- Deterministic execution. No LLM call, no token cost, fast.
```yaml
step:
  type: code
  name: run_project_tests
  description: "Execute pytest on the project test suite"
  input: { path: "string", flags: "string" }
  output: { passed: "int", failed: "int", coverage: "float" }
  timeout: 30s
  retry: 1
```

Use code steps when:
- The tool and arguments are the same every time (static)
- The tool is the same but arguments are derived from input (parameterized)
- The transformation is pure data manipulation (parsing, formatting, filtering)

**Agent steps** -- LLM-powered reasoning. Costs tokens but handles variability.
```yaml
step:
  type: agent
  name: analyze_test_failures
  description: "Examine failed tests and suggest fixes"
  prompt: "Given test failures, identify root causes and suggest fixes"
  model_tier: FAST
  tools: [read_file, grep]
  timeout: 30s
```

Use agent steps when:
- The reasoning varies significantly based on input
- The step requires judgment, creativity, or interpretation
- The output structure is unpredictable

### Dependencies

Steps can declare dependencies on previous steps:
```yaml
steps:
  - index: 0, type: code, name: fetch_data        # runs first
  - index: 1, type: code, name: transform_data     # depends_on: [0]
  - index: 2, type: agent, name: analyze_results   # depends_on: [1]
  - index: 3, type: code, name: format_output      # depends_on: [2]
```

### Fallback Behavior

When a code step fails at runtime, it automatically falls back to an agent step for that position. This means blueprints degrade gracefully -- a compiled pipeline never produces worse results than running the agent from scratch. The system tracks how often fallbacks occur per step to decide whether to recompile.

## Compilation Flow

The full pipeline from raw traces to executable blueprint:

```
1. RECORD TRACES
   Agent executes normally, recording each step
   ↓
2. DETECT PATTERNS
   Group traces by structural signature
   Filter to groups with 3+ matches
   ↓
3. CLASSIFY STEPS
   For each step position, compare across traces:
   - Identical values → "code" (static)
   - Same tool, varying args → "code" (parameterized)
   - Varying reasoning → "agent"
   ↓
4. GENERATE STEPS
   Code steps: generate deterministic function
   Agent steps: extract prompt template from example reasoning
   ↓
5. VALIDATE
   AST safety checks on generated code (no dangerous imports, no eval/exec)
   Run against original trace inputs as regression tests
   ↓
6. ASSEMBLE BLUEPRINT
   Combine steps + metadata + trigger pattern
   Save test cases from original traces
   ↓
7. ITERATE
   Track usage count and success rate
   Recompile when success rate drops below threshold
   Disable when consistently failing
```

### Step Classification in Detail

The classifier examines each step position across all matching traces:

**For tool_call steps:**
- Are all tool names identical? If no, classify as "agent"
- Are all arguments identical? If yes, classify as "code" (static)
- Arguments differ? Classify as "code" (parameterized) -- find which args are constant and which vary

**For thought/output steps:**
- Is the content identical every time? If yes, classify as "code" (static template)
- Content varies? Classify as "agent" (needs LLM reasoning)

**For tool_result steps:**
- Results from code steps are pass-through (handled by the tool_call step)
- Not generated as separate blueprint steps

### Code Generation Examples

**Static step** (same tool + same args every time):
```
# Generated from traces where every run called the same command
execute(input):
  return tool_call("run_command", { cmd: "pytest tests/ -v" })
```

**Parameterized step** (same tool, varying args):
```
# Generated from traces where the path argument varied
execute(input):
  args = { flags: "-v --tb=short" }       # constant across traces
  args["path"] = input.get("path")        # varied across traces
  return tool_call("run_command", args)
```

**Agent step** (extracted prompt template):
```
# Generated from traces where reasoning varied
prompt: "Given the test results, analyze failures and suggest fixes.
         Example reasoning: [extracted from first trace]"
model_tier: FAST
```

## When to Compile

**Compile when:**
- 3+ similar traces share the same structural signature
- All matching traces were successful
- The pattern appears stable (not still evolving)
- The task is operationally important (high frequency or high cost)

**Do NOT compile when:**
- The task is a one-off (user will not repeat it)
- Inputs are highly variable with no structural pattern
- The task requires creativity (writing, brainstorming, design)
- The workflow is still being iterated on (wait until it stabilizes)
- The agent steps dominate -- if every step needs LLM reasoning, the blueprint adds overhead without benefit

### Compilation Threshold Decision Table

| Signal | Compile? | Reason |
|--------|----------|--------|
| 3+ identical structure, all succeeded | Yes | Clear repeatable pattern |
| 3+ similar structure, mixed success | Wait | Pattern exists but isn't reliable yet |
| 2 matches (below threshold) | No | Not enough evidence |
| All steps are agent-type | Probably not | Blueprint adds overhead without token savings |
| >80% code steps | Definitely | Maximum determinism, minimum cost |
| Task is creative writing | No | Outputs should vary |
| Task is data pipeline | Yes | Pipelines are inherently repeatable |

## Blueprint Validation

Every compiled blueprint must pass validation before deployment:

### Safety Checks
- **AST analysis** on all generated code: no dangerous imports (subprocess, os, sys, socket, pickle), no eval/exec/compile
- **Input/output schema** validation: types match expectations
- **Timeout enforcement**: every step has a max execution time

### Regression Testing
- Save the original traces as test cases (input instruction + expected step outputs)
- Run the compiled blueprint against each saved test case
- Verify outputs match within tolerance
- Track success rate over time

### Success Rate Tracking
- Every blueprint execution updates its success rate
- Blueprints falling below a threshold get flagged for review
- Consistently failing blueprints auto-disable and fall back to full agent execution
- Recompilation triggered when enough new traces accumulate

## Practical Application in Claude Code

When working in Claude Code, apply blueprint thinking to recognize automation opportunities:

### Recognizing Patterns

Ask yourself after completing a multi-step task:
1. Have I done this exact sequence before?
2. Would the steps be the same next time, or do they change?
3. Which steps are pure tool calls vs. reasoning?

### Building Reusable Workflows

When you notice a pattern, document it as a pipeline:

```markdown
## Deploy Feature Branch
Trigger: "deploy <branch> to staging"

1. [code] Run tests: `pytest tests/ -v`
2. [code] Build: `npm run build`
3. [agent] Review build output for warnings (judgment needed)
4. [code] Deploy: `git push staging <branch>`
5. [code] Health check: `curl -s https://staging.example.com/health`
6. [agent] Summarize deployment status (format for human)
```

### Progressive Compilation

Start with fully agent-driven execution. As patterns emerge:

1. **Week 1**: Do everything manually, let traces accumulate
2. **Week 2**: Notice you keep running the same 4-step sequence for deployments
3. **Week 3**: Extract the deterministic steps (build, deploy, health check) into code
4. **Week 4**: Only the "review warnings" and "summarize status" steps still need the LLM

Result: a 6-step workflow drops from ~6 LLM calls to ~2 LLM calls. The 4 code steps execute in milliseconds at zero token cost.

### Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Compiling after 1 execution | No pattern evidence | Wait for 3+ repetitions |
| Compiling creative tasks | Outputs should be unique | Keep these as agent-only workflows |
| Never revalidating | Environments change, blueprints drift | Periodically re-run regression tests |
| All-or-nothing compilation | Some steps are inherently variable | Mix code and agent steps in one pipeline |
| Ignoring fallback data | Frequent fallbacks signal a bad compilation | Recompile when fallback rate exceeds 20% |

## Summary

The blueprint compilation methodology is a loop:

```
OBSERVE  ->  DETECT  ->  COMPILE  ->  VALIDATE  ->  EXECUTE  ->  OBSERVE
   ^                                                                |
   +----------------------------------------------------------------+
```

Every execution feeds back into observation. Patterns that hold get stronger. Patterns that break trigger recompilation. The system converges toward maximum determinism with minimum token spend, while always maintaining the ability to fall back to full LLM reasoning when the unexpected happens.
