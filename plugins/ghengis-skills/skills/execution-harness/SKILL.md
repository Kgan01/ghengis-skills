---
name: execution-harness
description: Use when a task is too large for a single session — provides multi-session execution with checkpoints, progress tracking, and resume capability so complex projects survive context resets and session boundaries
allowed-tools: Agent Read Write Edit Glob Grep
---

# Execution Harness

Multi-session orchestration for tasks that exceed what one conversation can handle. The harness decomposes a project into ordered tasks, executes them one at a time with checkpoints between each, and enables any future session to pick up exactly where the last one stopped.

This is the pattern for: "Build me a complete X" where X takes hours, not minutes.

## When to Use

- Projects with 3-15 discrete implementation steps
- Work that will span multiple Claude Code sessions
- Tasks where losing progress to a context reset would be costly
- Any plan where you need to track completed vs remaining work
- Projects requiring human review gates between phases

## When NOT to Use

- Tasks completable in a single session (just do them)
- Pure research or conversation (no persistent state needed)
- Work where every step depends on reviewing the previous step's output interactively

## The Initializer-Executor Pattern

**Session 1 (Initializer):** Decompose the project, create the task list, save the first checkpoint.

**Session 2..N (Executors):** Load the latest checkpoint, pick the next pending task, execute it, save a new checkpoint.

Any session can be an executor. The checkpoint carries all state.

## Checkpoint Structure

After each task, capture this state:

```markdown
## Checkpoint — {project-name}
**Session:** {N}
**Timestamp:** {ISO-8601}
**Status:** running | paused | completed | failed

### Completed Tasks
- [x] Set up project structure
- [x] Implement user model
- [x] Add authentication middleware

### Pending Tasks
- [ ] Build API endpoints
- [ ] Write integration tests
- [ ] Add documentation

### Current Task
None (between tasks)

### Artifacts
**Files created:** src/models/user.py, src/middleware/auth.py, tests/conftest.py
**Files modified:** src/main.py, requirements.txt
**Git commit:** a1b2c3d

### Context Summary
{OM-compressed summary of what was done, key decisions made, and anything
the next session needs to know to continue without reading all prior work}

### Metrics
**Cost so far:** $0.12
**Sessions used:** 3
**Confidence:** 0.85
```

## Step-by-Step Process

### Phase 1: Initialize (Session 1)

1. **Receive the project spec** — what the user wants built
2. **Decompose into tasks** — 3-15 ordered steps, each completable in one session:
   - Each task is a single sentence starting with a verb
   - Order by dependency (foundational first)
   - Include setup, implementation, testing, and documentation
   - Not too granular (avoid "create file X"), not too broad (avoid "build the backend")
3. **Present the task list** to the user for review and adjustment
4. **Save the initial checkpoint** with all tasks in pending, none completed

### Phase 2: Execute (Session 2..N)

1. **Load the latest checkpoint** — read the checkpoint file or memory
2. **Identify the next pending task** — first item in the pending list
3. **Execute the task** — do the actual work (write code, research, create files)
4. **Record artifacts** — what files were created/modified, any git commits
5. **Compress context** — summarize what was done and key decisions for future sessions
6. **Save the new checkpoint** — move the task from pending to completed, update metrics
7. **Check for human review gates** — if the next task is risky or a phase boundary, pause

### Phase 3: Resume (After Interruption)

When a new session starts and needs to continue:

1. **Load the checkpoint** — find the latest checkpoint for this project
2. **Read the context summary** — understand what's been done without replaying history
3. **Check artifacts** — verify files exist, git state is clean
4. **Continue from the next pending task** — no need to redo anything

### Fresh Start vs. Compaction

**Prefer starting fresh** over compacting when context has degraded. Opus 4.6 is extremely effective at rediscovering state from the filesystem. A fresh context with good state files often outperforms a compacted context with degraded history.

**When to start fresh:**
- After 2+ compactions in the same session (diminishing returns)
- When output quality has visibly degraded (repetition, drift, errors)
- At natural phase boundaries (setup complete, moving to implementation)

**When to compact instead:**
- Mid-task where you need the immediate conversation context
- When the state is too complex to capture in files (intricate debugging session)
- When checkpoint files don't exist yet

**For the first context window**, use a different prompt: set up the framework (write tests, create setup scripts, save initial state). Future windows iterate on the task list.

### State Management Patterns

Use structured files + git to carry state across sessions.

**Structured state file** (`tests.json`):
```json
{
  "tests": [
    {"id": 1, "name": "auth_flow", "status": "passing"},
    {"id": 2, "name": "user_crud", "status": "failing"},
    {"id": 3, "name": "api_endpoints", "status": "not_started"}
  ],
  "total": 15, "passing": 10, "failing": 3, "not_started": 2
}
```

**Progress notes** (`progress.txt`):
```
Session 3 progress:
- Fixed auth token validation
- Updated user model for edge cases
- Next: investigate user_crud test failures (test #2)
- Note: Do not remove tests — this could mask bugs
```

**Setup script** (`init.sh`):
```bash
#!/bin/bash
# Run this at the start of each session
cd project_root && pip install -r requirements.txt
python -m pytest tests/ --tb=short -q
cat progress.txt
```

**Git as state tracking:** Commit after each completed task. Git log provides a natural audit trail. Tag phase boundaries (`git tag phase-1-complete`).

**Key principle:** Write tests in the first session, track them in a structured format, and remind future sessions: "Do not remove or edit tests — this could lead to missing or buggy functionality."

## Task Decomposition Rules

Good decomposition:
```
1. Set up project structure and dependencies
2. Implement the data model with migrations
3. Build the authentication system
4. Create CRUD API endpoints
5. Add input validation and error handling
6. Write integration tests
7. Add API documentation
8. Deploy to staging
```

Bad decomposition (too granular):
```
1. Create src/ directory
2. Create requirements.txt
3. Add FastAPI to requirements
4. Create main.py
...
```

Bad decomposition (too broad):
```
1. Build the backend
2. Build the frontend
```

**Target:** Each task takes 5-20 minutes of focused execution. 3-15 tasks total.

## Human Review Gates

Some transitions should pause for human review:

| Gate | When to Pause |
|------|--------------|
| **Architecture decisions** | After initial setup, before building on the foundation |
| **External integrations** | Before connecting to APIs, databases, or third-party services |
| **Destructive operations** | Before migrations, data changes, or deployment |
| **Phase boundaries** | Between major project phases (setup → build → test → deploy) |
| **Low confidence** | When the executor is uncertain about the approach |

When paused, the checkpoint status changes to `paused` and records a review message explaining what needs human input.

## Failure Handling

- **Task fails:** Don't remove from pending. Save checkpoint with error context. Next session can retry with the error information.
- **Session crashes:** Last saved checkpoint is the recovery point. No work lost beyond the current unsaved task.
- **Wrong approach:** Human can edit the pending task list in the checkpoint to adjust course.
- **Too many failures:** After 3 failures on the same task, pause and request human review.

## Context Compression Between Sessions

The `Context Summary` field in the checkpoint is critical. It must contain everything a fresh session needs to continue without reading all prior conversation:

**Include:**
- What was built and where (file paths, architecture decisions)
- Key technical decisions and why they were made
- Current state of the codebase (what works, what's stubbed)
- Any gotchas or constraints discovered during execution

**Exclude:**
- Step-by-step replay of what happened
- Error messages from resolved issues
- Intermediate attempts that were abandoned
- Conversation context that isn't relevant to future work

**Target:** 500-1000 words. Enough to brief a new session, short enough to fit in context.

## Checkpoint Storage in Claude Code

Store checkpoints where future sessions can find them:

- **Primary:** Project's `docs/harness/` directory (committed to git)
- **Alternative:** Claude Code memory system (for cross-project harnesses)
- **Naming:** `checkpoint-{session-number}.md` or a single `CHECKPOINT.md` that gets updated

The checkpoint file IS the state. Anyone (human or agent) can read it and understand exactly where the project stands.

## Metrics Tracking

Track across sessions:
- **Total cost** — cumulative across all sessions
- **Sessions used** — how many sessions the project has consumed
- **Task completion rate** — completed / total
- **Average task duration** — helps estimate remaining time
- **Confidence** — executor's confidence that the project is on track (0.0-1.0)

## Checklist

### Before Starting a Harness
- [ ] Project spec is clear enough to decompose into tasks
- [ ] User has reviewed and approved the task list
- [ ] Initial checkpoint is saved
- [ ] Checkpoint storage location is established

### After Each Task
- [ ] Task moved from pending to completed
- [ ] Artifacts recorded (files created/modified)
- [ ] Context summary updated for next session
- [ ] Checkpoint saved
- [ ] Check if human review gate applies before next task

### When Resuming
- [ ] Latest checkpoint loaded
- [ ] Context summary read and understood
- [ ] Artifacts verified (files exist, git clean)
- [ ] Next pending task identified
- [ ] Ready to execute without replaying history
