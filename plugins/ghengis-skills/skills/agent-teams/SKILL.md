---
name: agent-teams
description: Use when a task benefits from multiple creative perspectives -- spawns parallel agents with different viewpoints, then synthesizes the best elements into a final output
---

# Agent Teams

Spawn parallel agents with the same task but different creative perspectives. Each produces a variation, then a synthesis step combines the best elements into a final output that is stronger than any individual variation.

## Core Concept

Instead of asking one agent to produce one answer, ask N agents to approach the same task through different creative lenses. The diversity of perspectives surfaces ideas that a single agent would miss.

```
                    +--> [Minimalist] --+
                    |                   |
User Request ------+--> [Bold]      ---+--> [Synthesizer] --> Final Output
                    |                   |
                    +--> [Technical] ---+
                    |                   |
                    +--> [Playful]   ---+
                    |                   |
                    +--> [Elegant]   ---+
```

## 5 Default Perspectives

Each perspective is a creative constraint injected into the agent's prompt alongside the original task instructions.

| Perspective | Description | Constraints |
|-------------|-------------|-------------|
| **Minimalist** | Clean, simple, less is more. Focus on essential elements only. | Max 3 key elements. No decorative flourishes. White space is your friend. |
| **Bold** | Provocative, attention-grabbing, breaks conventions. | Challenge assumptions. Use unexpected angles. Be memorable above all. |
| **Technical** | Precise, data-driven, appeals to experts and practitioners. | Include specifics, numbers, technical depth. Avoid fluff. |
| **Playful** | Fun, engaging, uses humor and personality. | Light tone, conversational, surprising. Make people smile. |
| **Elegant** | Sophisticated, refined, premium feel. | Polished language, aspirational tone, luxury aesthetic. |

### Injecting a Perspective

Each team member receives the full task plus a perspective block:

```
CREATIVE CONSTRAINT: Bold
Provocative, attention-grabbing, breaks conventions.
Constraints: Challenge assumptions. Use unexpected angles. Be memorable above all.

Apply this perspective consistently throughout your work.
All other task requirements remain the same.
```

## Execution Flow

### Step 1: Spawn Parallel Agents

Create one subagent per perspective. Each gets the same instruction but a different creative constraint.

```
For each perspective in [Minimalist, Bold, Technical, Playful, Elegant]:
    Spawn subagent with:
        - System prompt: "You are a creative team member. {perspective_injection}"
        - Instruction: "{original_user_request}"
    Run all agents in parallel (not sequential)
```

### Step 2: Collect Variations

Gather the output from each agent. Failed agents are logged but do not block the others.

### Step 3: Synthesize

A synthesis agent reviews all successful variations and combines the best elements:

```
You are a synthesis agent reviewing {N} creative variations for this task:
{original_instruction}

Here are all variations:

## Variation: Minimalist
{minimalist_output}

---

## Variation: Bold
{bold_output}

---

(etc.)

Your job:
1. Identify the STRONGEST element from each variation
2. Note which perspective contributed what
3. Combine the best elements into ONE cohesive final output
4. The synthesis should be better than any individual variation

Output your synthesized result.
```

## When to Use Agent Teams

**Good use cases:**
- Content generation (taglines, headlines, copy, descriptions)
- Brainstorming (product names, feature ideas, marketing angles)
- Creative writing (blog posts, social media, presentations)
- Design direction (visual concepts, layout approaches)
- Problem-solving where multiple approaches are valid
- Any task where "there's more than one right answer"

**Bad use cases -- use a single agent instead:**
- Factual lookup (there is one correct answer)
- Code that must follow a specific pattern (consistency matters more than creativity)
- Data analysis (numbers don't benefit from creative lenses)
- Single-answer questions ("What is the capital of France?")
- Tasks where the user already knows exactly what they want

## Controlling Team Size

Not every task needs 5 perspectives. Adjust based on the task:

| Scenario | Team Size | Perspectives to Use |
|----------|-----------|-------------------|
| Quick brainstorm | 3 | Minimalist, Bold, Technical |
| Full creative exploration | 5 | All five defaults |
| Tone-sensitive writing | 3 | Technical, Playful, Elegant |
| Marketing copy | 4 | Bold, Playful, Elegant, Minimalist |
| Technical documentation | 2 | Minimalist, Technical |

## Custom Perspectives

Create task-specific perspectives when the defaults don't fit:

```
Perspective:   "User Advocate"
Description:   "Thinks from the end-user's point of view. Prioritizes clarity and ease of use."
Constraints:   "No jargon. Every sentence should pass the 'would my mom understand this?' test."
```

```
Perspective:   "Devil's Advocate"
Description:   "Deliberately challenges the premise. Looks for flaws and counterarguments."
Constraints:   "Find at least 3 problems with the approach. Be constructive, not destructive."
```

## Fallback: Single Agent

When resources are constrained or the task is time-sensitive, fall back to a single agent using the most relevant perspective:

- For marketing tasks: **Bold**
- For technical tasks: **Technical**
- For executive communication: **Elegant**
- For general use: **Minimalist**
- For casual/social content: **Playful**

## Synthesis Best Practices

The synthesis step is what makes teams valuable. A poor synthesis just picks one variation; a good synthesis creates something new.

**Good synthesis identifies:**
- The clearest structure (often from Minimalist)
- The most memorable hook (often from Bold)
- The most credible supporting detail (often from Technical)
- The most engaging tone (often from Playful)
- The most polished language (often from Elegant)

**Good synthesis avoids:**
- Averaging all variations into bland mush
- Picking one variation and ignoring the rest
- Making the output longer than any individual variation
- Losing coherence by mixing incompatible tones

## Example: Tagline Generation

**Task:** "Write a tagline for a developer productivity tool"

| Perspective | Variation |
|-------------|-----------|
| Minimalist | "Ship faster." |
| Bold | "Your code doesn't need more coffee. It needs this." |
| Technical | "40% fewer context switches. Measurable flow state." |
| Playful | "Finally, a tool your IDE won't be jealous of." |
| Elegant | "The art of effortless engineering." |

**Synthesis:** "Ship faster. 40% fewer context switches -- because your best code happens in flow state."

The synthesis took the directness of Minimalist, the specificity of Technical, and the aspiration of Elegant.
