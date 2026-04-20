---
name: hallucination-detector
description: Use when reviewing agent output for factual accuracy -- detects fabricated URLs, unsourced statistics, fake citations, impossible future claims, and confident assertions without evidence
---

# Hallucination Detector

Signal-based detection of fabricated content in LLM output. Catches the four most common hallucination types: fabricated URLs, unsourced statistics, fake citations, and impossible future claims. Zero LLM cost, sub-millisecond latency -- pure regex pattern matching.

## When to Apply

- **Before delivering any agent output** that claims to contain facts, data, or references
- **After research tasks** -- LLMs frequently fabricate sources when asked to "find" information
- **When output contains URLs** that were not returned by a tool (search, browse, API call)
- **When output contains statistics** with decimal precision (73.4%, 2.7x, etc.)
- **When output references academic papers** or cites specific authors
- **When output makes claims about future events** with definitive language
- **More aggressively when context health is degraded** -- hallucination frequency increases with context pressure

## The 4 Hallucination Signal Types

### 1. Fabricated URLs (Severity: Warn)

LLMs generate plausible-looking URLs from training data patterns. These URLs often look real but point to nonexistent pages, expired content, or entirely made-up domains.

**Detection pattern:**
```
Any URL (https?://...) in agent-generated text
```

**Key distinction:** URLs returned by tools (search results, API responses, browser navigation) are legitimate. URLs that the agent wrote from its own knowledge are suspect.

- Flag URLs in agent-generated output
- Skip URL checks in tool results (tool output is grounded)

**Common fabrication patterns:**
- `https://docs.{product}.com/{plausible-path}` -- documentation links that look right but 404
- `https://github.com/{user}/{repo}` -- repositories that do not exist
- `https://arxiv.org/abs/{number}` -- paper IDs that are fabricated
- `https://{company}.com/blog/{date}/{slug}` -- blog posts that were never written
- `https://www.{news-site}.com/{year}/{month}/{headline}` -- news articles that do not exist

**Recovery:**
1. Verify the URL with a tool (browse, fetch, or search for the page title)
2. If verification is not possible, remove the URL and note "URL not verified"
3. Replace with a search suggestion: "Search for: {topic}" instead of a fabricated link

### 2. Unsourced Precise Statistics (Severity: Warn)

LLMs generate precise-looking numbers to sound authoritative. Decimal percentages without a citation are a strong hallucination signal.

**Detection pattern:**
```
Any decimal percentage: \b(\d{1,3}\.\d+)\s*%
Examples: 73.4%, 2.7%, 94.2%, 156.8%
```

**What this catches:**
- "Studies show that 73.4% of developers prefer..." (fabricated statistic)
- "Performance improved by 94.2% compared to..." (made-up benchmark)
- "The market grew 156.8% year over year..." (invented data)

**What this does NOT catch (intentionally):**
- Round numbers: "about 70% of users" -- these are often reasonable estimates
- Statistics with citations: "73.4% (Source: 2024 Stack Overflow Survey)" -- cited data is grounded
- Statistics from tool results: data returned by APIs or searches is grounded

**Recovery:**
1. If a precise statistic is important to the output, verify it with a search tool
2. If unverifiable, replace with a hedged round number: "approximately 70%" instead of "73.4%"
3. If the statistic is incidental, remove it entirely

### 3. Fabricated Academic Citations (Severity: Warn)

LLMs commonly fabricate academic citations, including author names, publication years, and paper titles. These look highly credible but often reference papers that do not exist.

**Detection patterns:**

Pattern A -- Attribution phrases:
```
"according to [Author]"
"as shown/demonstrated/reported/found by [Author]"
"as shown by Dr. [Author] et al."
"as reported by [Author] and colleagues"
"as found by [Author] (2024)"
```

Pattern B -- Inline citations:
```
[Author] et al. (2024)
[Author] et al. [2024]
```

Pattern C -- Study references:
```
"a 2024 study by [Author]"
"a 2023 study by [Author]"
```

Where `[Author]` is a capitalized name (e.g., "Smith", "Johnson", "Zhang").

**What this catches:**
- "According to Dr. Smith et al. (2024), transformer architectures..."
- "Zhang et al. [2023] demonstrated that..."
- "A 2024 study by Johnson found that..."

**Recovery:**
1. Search for the specific paper using author name + topic keywords
2. If the paper cannot be found, remove the citation entirely
3. Replace with verifiable sources: tool-retrieved search results, official documentation, or "research in this area suggests..." without a fabricated attribution

### 4. Future Certainty (Severity: Warn)

LLMs cannot predict the future but sometimes make definitive claims about upcoming events, release dates, or outcomes.

**Detection patterns:**

Definitive future language:
```
"will definitely..."
"will certainly..."
"will absolutely..."
"will guaranteed..."
"is guaranteed to..."
```

Specific future dates with product claims:
```
"will be released on/in/by [Month] [Year]"
"will launch on/in/by [Month] [Year]"
"will ship on/in/by [Month] [Year]"
```

**What this catches:**
- "GPT-5 will definitely be released in March 2027"
- "Apple will certainly launch the iPhone 18 by September 2026"
- "This framework is guaranteed to become the industry standard"
- "The API will ship by January 2027"

**What this does NOT catch (intentionally):**
- Hedged predictions: "GPT-5 may be released in 2027" -- hedging is honest
- Past events: "was released in 2024" -- historical claims are separately verifiable
- Tool-sourced dates: dates from search results or API responses are grounded

**Recovery:**
1. Replace definitive language with hedged language: "may", "is expected to", "is rumored to"
2. Add a caveat: "as of [current date], this has not been confirmed"
3. If the claim is central to the output, verify with a search tool

## Severity Classification

All four signal types default to "warn" severity. Escalate to "block" in these contexts:

| Context | Severity | Reason |
|---------|----------|--------|
| Medical or health advice with fabricated statistics | Block | Could cause real harm |
| Legal citations that are fabricated | Block | Could lead to legal consequences |
| Financial data with made-up numbers | Block | Could lead to financial loss |
| URLs in output intended for end users | Block | Users will click broken links |
| Academic citations in research deliverables | Block | Destroys credibility |
| Casual conversation or brainstorming | Warn | Lower stakes, hallucinations are less harmful |
| Internal planning or reasoning | Warn | Not user-facing |

## Common Hallucination Triggers

These request patterns are most likely to produce hallucinated content. Apply extra scrutiny to output generated from these prompts:

| Trigger Request | Why It Causes Hallucination |
|----------------|---------------------------|
| "Give me the exact statistics on..." | LLMs generate precise numbers to satisfy the "exact" requirement |
| "Find me 10 sources for..." | LLMs fabricate sources to fill the requested count |
| "What's the current data on..." | LLMs confuse training data with current data |
| "List the top 10 tools for..." | LLMs invent entries to complete the list |
| "According to research, what..." | LLMs fabricate citations to sound authoritative |
| "What will happen when..." | LLMs make definitive future claims to sound confident |
| "Give me a comprehensive list of..." | LLMs pad lists with fabricated entries to appear thorough |
| "What's the URL for..." | LLMs construct plausible URLs from patterns rather than admitting uncertainty |
| "Cite your sources" | LLMs fabricate citations retroactively to justify their output |

**Mitigation for trigger requests:** When you recognize a trigger pattern in the original instruction, proactively use tools (search, browse) to ground your output in verifiable data. Prefer "I don't have current data on this -- let me search" over fabricating an answer.

## Integration with Other Skills

- **constitutional-ai** includes rule #8 `no_hallucination` which provides the prompt-level instruction "Never fabricate URLs, citations, or statistics." Hallucination detector is the enforcement layer -- it checks whether the output actually followed that instruction.
- **completion-enforcer** catches missing content. Hallucination detector catches fabricated content. They complement each other: one detects gaps, the other detects fill.
- **context-health** detects context degradation, which correlates with increased hallucination frequency. When context health is in the compact zone or beyond, hallucination detection should be applied more aggressively.

## Source Distinction Rule

The most important principle: **tool results are grounded, agent-generated text is not.**

- A URL from a search result or API response = legitimate
- A URL the agent wrote from memory = suspect
- A statistic from a data API or search result = legitimate
- A statistic the agent produced from training data = suspect

When in doubt about whether content came from a tool or from the agent's own generation, treat it as agent-generated and flag it.

## Cost

$0. Zero LLM calls. All checks are regex pattern matching against the output text. Apply to every agent response, every subagent result, and every output before it reaches the user.

## Chain Integration

This skill participates in `skill-chain-supervisor` chains via the shared scratchpad at `~/.claude/ghengis-chain-context.json`.

**Role in chain:** Output scanner. Runs after any content-generating skill or agent.

**Scratchpad subkey (namespaced writes):** `hallucination_detector.*`

**Reads (input scratchpad keys):**
- `execution.result`

**Writes (output scratchpad keys):**
- `hallucination_detector.fabricated_urls` — list of URLs that look fake or uncheckable
- `hallucination_detector.unsourced_stats` — list of specific claims with no citation
- `hallucination_detector.suspect_claims` — list of confident assertions without evidence

**Success criteria:** all three lists empty OR claims verified against sources

When invoked as part of a chain, this skill MUST:
1. Read prior scratchpad state before starting
2. Write outputs to the `hallucination_detector.*` namespace only — never overwrite another skill's subkey
3. Report failure via its own subkey (e.g. `hallucination_detector.error`) rather than raising

When invoked standalone (not in a chain), scratchpad writes are optional but recommended for auditability.
