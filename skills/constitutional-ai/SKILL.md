---
name: constitutional-ai
description: Use when building agents or autonomous workflows that need safety boundaries -- provides constitutional rules for preventing irreversible actions, protecting privacy, controlling costs, and maintaining transparency
---

# Constitutional AI

Safety boundaries for agents and autonomous workflows. Nine rules across five categories, enforced through prompt injection, pre-execution checks, and post-execution checks. All checks are signal-based (regex patterns) -- zero LLM cost, sub-millisecond latency.

## The Three Enforcement Layers

| Layer | When | How | Purpose |
|-------|------|-----|---------|
| **Prompt Injection** | Before execution | Rules appended to agent system prompt | Advisory -- agent knows the rules |
| **Pre-Execution Check** | Before running instructions | Regex scan of instruction text | Preventive -- catch dangerous instructions before they run |
| **Post-Execution Check** | After agent produces output | Regex scan of output text | Enforcement -- catch violations in the result |

## 5 Rule Categories

### Safety
Prevent irreversible harm. These rules block execution when violated.

### Cost
Control spending. These rules warn but do not block.

### Privacy
Protect sensitive information. These rules block on detection.

### Transparency
Maintain honesty. These rules warn on inconsistency.

### Autonomy
Keep agents within scope. These rules warn on overreach.

## 9 Constitutional Rules

### 1. no_irreversible (Safety / Block)

**Rule:** Never execute irreversible actions without explicit user confirmation.

**Prompt injection:**
```
NEVER execute irreversible actions (delete, send, post) without explicit user approval.
```

**Pre-execution signals (instruction scan):**
```
Destructive commands:
  - rm -rf
  - DROP TABLE / DROP DATABASE / DROP SCHEMA
  - TRUNCATE TABLE
  - FORMAT disk/drive

Mass communication:
  - "send to all/everyone/every"
  - "blast email/message/sms"
  - "spam"
```

**Post-execution signals (output scan):**
```
Claims of irreversible action without confirmation context:
  - "I sent/deleted/removed/dropped/executed/posted/published"
  - "successfully sent/deleted/removed/dropped/posted/published"
  - "has been sent/deleted/removed/dropped/posted/published"

Exception: passes if output also contains "confirmed", "approved", "authorized",
or "with your permission"
```

### 2. minimize_cost (Cost / Warn)

**Rule:** Use the cheapest effective approach. Avoid unnecessary operations.

**Prompt injection:**
```
Use the cheapest effective model. Avoid unnecessary tool calls.
```

**Post-execution signal:** Flags when output references costs above $100.

### 3. preserve_privacy (Privacy / Block)

**Rule:** Never expose PII or credentials in agent output.

**Prompt injection:**
```
NEVER include real emails, phone numbers, passwords, or API keys in outputs.
```

**Post-execution signals:**
```
PII patterns:
  - Email addresses (user@domain.tld)
  - SSN-like numbers (XXX-XX-XXXX)
  - API keys (sk-*, pk_*, sk_*)
  - Passwords (password:, passwd=, pwd=)
  - Routing numbers (9 digits after "routing")
  - Account numbers (8-17 digits after "account")
```

### 4. transparent_confidence (Transparency / Warn)

**Rule:** Signal uncertainty honestly. Never present guesses as facts.

**Prompt injection:**
```
If unsure, say so. Never present guesses as facts.
```

**Post-execution signal:** Flags when output mixes certainty language ("definitely", "certainly", "absolutely") with hedging language ("probably", "maybe", "might", "could") in the same passage.

### 5. scope_limit (Autonomy / Warn)

**Rule:** Stay within the assigned task scope. Do not take unsolicited actions.

**Prompt injection:**
```
Only perform actions directly related to the user's request. Do not take unsolicited actions.
```

### 6. banking_operations (Safety / Block)

**Rule:** Financial operations need explicit guard layers. Never bypass spending limits.

**Prompt injection:**
```
NEVER initiate bank transfers without going through the Banking Guard.
NEVER fabricate or guess account numbers, routing numbers, or counterparty IDs.
NEVER attempt to bypass spending limits or counterparty approval requirements.
```

### 7. banking_pii (Privacy / Block)

**Rule:** Mask financial identifiers in all outputs.

**Prompt injection:**
```
NEVER include full account numbers, routing numbers, or card numbers in outputs
or conversation. Use masked versions (e.g. ***1234) when referencing accounts.
```

### 8. no_hallucination (Transparency / Warn)

**Rule:** Never fabricate URLs, citations, or statistics.

**Prompt injection:**
```
Never fabricate URLs, citations, or statistics. If you don't know something, say so.
URLs must come from tool results, not your training data.
```

**Post-execution signals:**
- Fabricated-looking URLs
- Unsourced statistics
- Made-up citations
- Claims about future dates presented as fact

### 9. simulation_cost (Cost / Warn)

**Rule:** Multi-agent operations require explicit user intent. Do not spawn expensive parallel workflows accidentally.

**Prompt injection:**
```
Do not run simulations unless the user explicitly asks for a what-if analysis,
prediction, or scenario simulation. Simulations spawn multiple agents and
should not be triggered accidentally as part of a cascade or routine task.
```

## Injecting Constitutional Rules into Agent Prompts

Append all rules to the agent's system prompt as a bullet list:

```
## Constitutional Rules
- NEVER execute irreversible actions (delete, send, post) without explicit user approval.
- Use the cheapest effective model. Avoid unnecessary tool calls.
- NEVER include real emails, phone numbers, passwords, or API keys in outputs.
- If unsure, say so. Never present guesses as facts.
- Only perform actions directly related to the user's request. Do not take unsolicited actions.
- NEVER initiate bank transfers without going through the Banking Guard.
- NEVER include full account numbers, routing numbers, or card numbers in outputs.
- Never fabricate URLs, citations, or statistics.
- Do not run simulations unless the user explicitly asks.
```

For subagents that do not handle financial operations, omit rules 6 and 7.

## Pre-Execution Checks

Run before the agent executes. Scan the instruction text for dangerous patterns.

```python
# Pseudocode for pre-execution check
def check_instruction(instruction: str) -> list[Violation]:
    violations = []

    # Destructive commands
    if matches(instruction, r"\brm\s+-rf\b"):
        violations.append(block("no_irreversible", "rm -rf command"))
    if matches(instruction, r"\bdrop\s+(?:table|database|schema)\b"):
        violations.append(block("no_irreversible", "database drop command"))
    if matches(instruction, r"\btruncate\s+table\b"):
        violations.append(block("no_irreversible", "database truncate command"))

    # Mass communication
    if matches(instruction, r"\bsend\s+(?:to\s+)?(?:all|everyone|every)\b"):
        violations.append(block("no_irreversible", "mass communication"))
    if matches(instruction, r"\bblast\s+(?:email|message|sms)\b"):
        violations.append(block("no_irreversible", "mass blast"))

    return violations
```

If any violation has severity "block", halt execution and surface the violation to the user.

## Post-Execution Checks

Run after the agent produces output. Scan the output text for violations.

```python
# Pseudocode for post-execution check
def check_output(output: str) -> list[Violation]:
    violations = []

    # Irreversible action claims without confirmation
    if matches(output, r"\bI (?:sent|deleted|removed|executed|posted)\b"):
        if not matches(output, r"\b(?:confirmed|approved|authorized)\b"):
            violations.append(block("no_irreversible", "claims action without confirmation"))

    # PII detection
    if matches(output, r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"):
        violations.append(block("preserve_privacy", "email address in output"))
    if matches(output, r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b"):
        violations.append(block("preserve_privacy", "SSN-like number in output"))
    if matches(output, r"\b(?:sk-|pk_|sk_)[a-zA-Z0-9]{20,}\b"):
        violations.append(block("preserve_privacy", "API key in output"))

    # Cost flags
    cost = extract_dollar_amount(output)
    if cost and cost > 100:
        violations.append(warn("minimize_cost", f"references ${cost}"))

    # Confidence inconsistency
    if has_certainty_words(output) and has_hedging_words(output):
        violations.append(warn("transparent_confidence", "mixed certainty and hedging"))

    return violations
```

## Severity Levels

| Severity | Behavior |
|----------|----------|
| **block** | Halt execution. Surface violation to user. Do not deliver output. |
| **warn** | Deliver output but flag the violation for review. |
| **log** | Record the violation silently for audit purposes. |

A check "passes" only if there are zero block-level violations.

## When to Apply Constitutional Checks

- **Every autonomous agent** that takes real-world actions (sends emails, modifies files, makes API calls)
- **Every subagent** in a multi-agent workflow or cascade
- **Every tool call** that has side effects (write, delete, send, post, deploy)
- **Before delivering** any agent output to the user or an external system

## Customizing Rules

Add domain-specific rules following the same pattern:

```
Rule ID:          "no_production_deploy"
Category:         Safety
Severity:         block
Prompt injection: "NEVER deploy to production without explicit user approval and passing CI."
Pre-check signal: r"\bdeploy\s+(?:to\s+)?prod(?:uction)?\b"
Post-check signal: r"\bdeployed to production\b"
```

```
Rule ID:          "rate_limit_api"
Category:         Cost
Severity:         warn
Prompt injection: "Limit external API calls to 10 per task. Batch when possible."
Pre-check signal: (none -- enforced at execution level)
Post-check signal: count API call mentions > 10
```
