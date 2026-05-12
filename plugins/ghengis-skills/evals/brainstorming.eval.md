# Brainstorming — Evaluation

## TC-1: Inline questions, never AskUserQuestion / EnterPlanMode

- **prompt:** "Let's design a notification system for the JARVIS app."
- **context:** User has stated they prefer open conversational format.
- **assertions:**
  - Skill is invoked before any implementation
  - Questions appear as plain text in chat messages
  - `AskUserQuestion` tool is NEVER called
  - `EnterPlanMode` tool is NEVER called
  - Each message contains at most ONE question
- **passing_grade:** 5/5 must pass

## TC-2: Multiple choice with recommended option marked

- **prompt:** "What auth strategy should I use for this FastAPI service?"
- **context:** User is during brainstorming flow.
- **assertions:**
  - Response presents 2-4 options
  - Exactly one option is marked as recommended (e.g., "*recommended*")
  - Each option lists at least one tradeoff
  - There's an explicit "something else — tell me" or equivalent escape
- **passing_grade:** 3/4 must pass

## TC-3: Three execution modes offered at terminal state

- **prompt:** "Sounds good, let's build this." (after design approval)
- **context:** Design has been agreed.
- **assertions:**
  - Three modes are offered: inline, subagent, build-validate
  - One is marked recommended based on project complexity
  - The build-validate option is mentioned explicitly (not just "validate it")
  - User's choice is captured before any implementation starts
- **passing_grade:** 3/4 must pass

## TC-4: Scope decomposition for multi-subsystem requests

- **prompt:** "I want to build a platform with chat, billing, analytics, and an admin dashboard."
- **context:** Request describes 4+ independent subsystems.
- **assertions:**
  - Skill recognizes the scope is too large for one design
  - Surfaces this in the first response (not after 5 questions in)
  - Suggests decomposition into separate specs
  - Asks which sub-project to brainstorm first
  - Does NOT begin detailed questions on the full scope
- **passing_grade:** 4/5 must pass

## TC-5: Hard gate against implementation before design approval

- **prompt:** "Just go ahead and start coding the auth module."
- **context:** Skill is loaded, no design has been agreed.
- **assertions:**
  - Skill refuses to write code without explicit design approval
  - Either: completes a quick design pass first, OR asks "are you sure? we haven't designed this yet" and proceeds only on confirmation
  - Does NOT silently start coding
- **passing_grade:** 3/3 must pass

## TC-6: No default spec doc on disk

- **prompt:** "Let's design a simple JSON-to-CSV converter."
- **context:** Small project, design fits in a short conversation.
- **assertions:**
  - No file is written to `docs/`, `specs/`, or any spec directory by default
  - Skill may OFFER a doc ("want me to write this to a file?") but doesn't impose it
  - Conversational design summary is in chat
- **passing_grade:** 3/3 must pass

## TC-7: No question cap

- **prompt:** "I want to build a real-time collaborative editor with operational transformation and CRDT-based conflict resolution."
- **context:** Genuinely complex project that needs many clarifying questions.
- **assertions:**
  - Skill asks as many questions as needed (10+, 15+, whatever)
  - Does NOT cut off questions to "stay under a limit"
  - Each question advances understanding
- **passing_grade:** 2/3 must pass

## TC-8: One question per message

- **prompt:** any brainstorming flow
- **assertions:**
  - At no point does a single message contain 2+ questions
  - Even on follow-ups, only one question per turn
- **passing_grade:** 1/1 must pass
