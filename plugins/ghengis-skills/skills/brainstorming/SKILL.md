---
name: brainstorming
description: Use BEFORE any creative or implementation work — creating features, building components, adding functionality, modifying behavior, or porting a skill. Explores user intent, requirements, and design through inline conversational dialogue. Never enters plan mode. Never uses structured question pickers. Inline chat only. TRIGGER when user says "let's build", "I want to make", "add a feature", "design X", or describes a new project; or BEFORE invoking any chain that builds a deliverable.
allowed-tools: Read Grep Glob Bash
---

# Brainstorming

Turn ideas into shippable designs through inline conversational dialogue. No structured question pickers. No plan mode. Just back-and-forth in chat until both sides know what's being built.

This is the ghengis adaptation of `superpowers:brainstorming`. The two skills disagree on three things:

| Superpowers brainstorming | Ghengis brainstorming |
|---|---|
| Ends by invoking `writing-plans` skill | Ends by offering 3 execution modes (inline / subagent / build-validate chain) |
| Writes design doc to `docs/superpowers/specs/YYYY-MM-DD-*.md` | No file. Conversational design summary in chat. |
| Hard 9-step checklist with TodoWrite | Conversational, sequence is a suggestion not a contract |
| Uses `AskUserQuestion` for some prompts | NEVER uses `AskUserQuestion` or `EnterPlanMode` |

If the user explicitly wants a spec doc written to disk, ask first — don't default to it.

## Hard Rules

1. **No implementation, file edits, or scaffolding until the user approves the design.** This applies to every project regardless of perceived simplicity. A todo list, a single-function utility, a config change — all of them.
2. **Never invoke `EnterPlanMode`.** That tool is forbidden in this skill.
3. **Never invoke `AskUserQuestion`.** Structured Q&A pickers break the open-format flow. Ask questions as plain text in your reply.
4. **One question per message.** Don't combine clarifying questions with design proposals or with each other. The user answers one thing at a time.
5. **No question cap.** If a project needs 15 questions, ask 15. The user can always say "just build it" if they want to skip ahead — trust them.

## When to Use

- User says "let's build X", "I want to make Y", "design a feature for Z"
- Before invoking the `feature-build`, `skill-port`, or any chain that produces a deliverable
- After `systematic-debugging` reveals the bug is actually a design problem, not a code bug
- When a request describes multiple independent subsystems — flag the scope and decompose before brainstorming

## When NOT to Use

- The task is purely informational ("how does X work?") — just answer
- The task is a one-line obvious edit — just do it
- User has already given a full spec — go to `writing-skills` or build directly
- User explicitly says "skip the design, just build" — honor that, but flag risks if you see them

## The Process

This is a sequence, not a checklist. You can loop back, skip steps that don't apply, or compress steps for small projects. The end state is "user has approved a design and chosen an execution mode."

### 1. Read the project context

Before the first question, get oriented:

- `ls`, `git log --oneline -10`, look at `CLAUDE.md` / `README.md` if present
- Skim recent commits for what the team has been working on
- Check `MEMORY.md` or memory directory for prior decisions

If the project context is rich, the first message should acknowledge it: "I see this is a FastAPI service with X already in place. For the new feature you mentioned, my first question is..."

If the project is fresh / empty, start with "what's the goal of this?" rather than diving into details.

### 2. Scope check — is this one project or several?

If the user's request describes multiple independent subsystems ("build a platform with chat + billing + analytics + admin"), flag it immediately:

> "This sounds like 3-4 distinct projects. I'd recommend we break this into separate specs and build them one at a time. Which piece is most urgent: chat, billing, analytics, or admin?"

Don't refine details of a project that needs to be decomposed first.

### 3. Ask clarifying questions, one at a time

Each question is its own message. Keep them tight — purpose, constraints, success criteria, edge cases, integration points.

**Multiple choice when possible**, with your recommendation marked:

> What auth strategy?
>
> a) JWT with refresh tokens *(recommended — matches your existing FastAPI middleware)*
> b) Session cookies with Redis store
> c) OAuth2 with external provider
> d) something else — tell me

If open-ended is the right shape, just ask:

> What's the single most important thing this needs to do?

Don't pad questions with context the user already gave you. Don't preface with "great question!" or any filler.

### 4. Propose 2-3 approaches before settling

Once you understand the goal, lay out 2-3 plausible approaches with tradeoffs. Lead with your recommendation:

> Three ways to do this:
>
> **A. Embedded SQLite (recommended)** — simplest, no external service, fine for <10k records/day. Tradeoff: not great if you later want multi-instance.
>
> **B. Postgres via Supabase** — production-grade, you already have a Supabase account. Tradeoff: more setup.
>
> **C. Pure in-memory dict with JSONL backup** — fastest, smallest. Tradeoff: loses everything between restarts unless you handle persistence carefully.
>
> Which fits?

The user picks or pushes back. Either is fine.

### 5. Present the design conversationally

When you have enough to design, write it inline. Sections should be scaled to their actual complexity — a few sentences for simple projects, 200-300 words for nuanced ones. Cover:

- **What this is** (one sentence)
- **Architecture** (the shape of it — components, files, data flow)
- **Key decisions** (the things we just talked through)
- **What's NOT in scope** (YAGNI ruthlessly — name what we're explicitly NOT building)
- **How we'll know it works** (the functional test)

After each major section, ask "does this match what you had in mind?" — don't dump the whole design then wait for a verdict.

### 6. Offer 3 execution modes

When the user approves the design, offer three ways to build it:

> Three ways to build this:
>
> **A. Inline (recommended for small features)** — you watch me code it here in chat, step by step. Fastest feedback, you can redirect at any moment.
>
> **B. Subagent-driven** — I dispatch a Builder subagent to implement, then verify the result. You step away, come back to a finished deliverable. Good for medium-effort work where you don't need to babysit.
>
> **C. `build-validate` chain** — Builder + adversarial Validator + revision loop (max 2 iterations). The Validator's job is to *break* the Builder's work, not approve it. Slower but highest quality. Use for production code, security-sensitive changes, or anything where getting it wrong is expensive.
>
> Which mode?

Honor their choice. If they say "just build it" without picking, default to inline.

### 7. Optional: spec doc on disk

If the project is large enough that the user will want to reference the design later (or share it with someone), offer to write a short doc:

> Want me to write this design to `docs/<project>-design.md` so you have it for reference? Otherwise it lives only in our chat.

Default is **no doc** unless they ask. Avoid bureaucracy on small projects.

## Working in existing codebases

- Explore the current structure before proposing changes. Follow existing patterns.
- If existing code has a problem that directly affects this work (a 2000-line file you're about to edit, tangled responsibilities in a module you're touching), include targeted improvements as part of the design — the way a careful developer fixes adjacent rot they're working in.
- Don't propose unrelated refactoring. Stay focused.

## Design for isolation and clarity

Smaller, well-bounded units are easier to reason about and easier to test. For each piece of the design, you should be able to answer:

- What does it do?
- How do you use it?
- What does it depend on?

If a unit's internals leak into its consumers — or you can't change the internals without breaking callers — the boundaries need work.

## Anti-Patterns

| Anti-pattern | Why it's bad | Do instead |
|---|---|---|
| Asking 3 questions in one message | Overwhelms the user, hides which one matters | One question per message |
| Using `AskUserQuestion` | Structured popup breaks the open chat flow | Inline text questions |
| Using `EnterPlanMode` | Forces UI mode change, loses conversational thread | Just talk |
| "This is too simple to need design" | Simple projects are where unexamined assumptions cause the most wasted work | Even one-line fixes get a 2-sentence design |
| Combining design with clarifying question | User has to context-switch between approving and answering | Separate messages |
| Defaulting to a spec doc on disk | Bureaucracy, slow, dies stale | Conversational design; offer the doc, don't impose it |
| "Should I continue?" check-ins between steps | Wastes the user's time | Just keep going — they'll redirect if needed |
| Skipping scope check on multi-subsystem requests | Burns tokens refining a project that needs to be decomposed | Flag immediately, decompose first |

## Cross-References

- **`writing-skills`** — natural next step when brainstorming a new skill
- **`test-driven-development`** — natural next step for code projects; write the test first, then implement
- **`systematic-debugging`** — if "I want to build" turns out to be "I have a bug I need to fix", switch to debugging mode
- **`build-validate` chain** (in `skill-chain-supervisor`) — execution mode C
- **`feature-build` chain** (in `skill-chain-supervisor`) — the canonical pipeline for new features (brainstorming → TDD → build-validate)
- **`skill-port` chain** (in `skill-chain-supervisor`) — the canonical pipeline for new skills (brainstorming → writing-skills → pql-validation → build-validate)
