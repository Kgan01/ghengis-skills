---
name: report-writing
description: Use when creating reports, summaries, or structured documents — covers storytelling structure, data presentation, executive summaries, and audience-appropriate formatting
---

# Report Writing

## When to Use
When synthesizing research findings into reports, writing executive summaries, creating competitive analyses, building market reports, drafting research briefs, or structuring any document that decision-makers need to act on.

## Core Instructions

1. **Start with the executive summary** -- conclusion first, details after
2. **Structure with clear sections** -- use headers, not walls of text
3. **Lead every section with the key finding** -- not the methodology
4. **Include data** -- numbers, percentages, comparisons, trends
5. **Cite sources** -- URL or document reference for every claim
6. **Flag uncertainty** -- distinguish facts from estimates, mark confidence levels
7. **End with recommendations** -- numbered, prioritized, actionable
8. **Use tables for comparisons** -- never describe in prose what a table shows better

## Report Template

```markdown
# [Report Title]
*Prepared: [Date] | Confidence: [High/Medium/Low]*

## Executive Summary
[3-5 bullet points -- the entire report in 30 seconds]

## Key Findings
### Finding 1: [Headline]
[Data + analysis + source]

### Finding 2: [Headline]
[Data + analysis + source]

## Detailed Analysis
[Deep dive with tables, charts references, comparisons]

## Risks & Uncertainties
[What could be wrong, data gaps, assumptions made]

## Recommendations
1. [Action] -- [Why] -- [Expected impact]
2. [Action] -- [Why] -- [Expected impact]
3. [Action] -- [Why] -- [Expected impact]

## Sources
- [Source 1](url)
- [Source 2](url)
```

## Worked Examples

### Example -- Competitive Analysis

**Input**: Research 3 AI assistant competitors. Audience: CEO.
**Approach**: CEO wants the bottom line fast. Lead with who's winning and why. Use a comparison table.

**Output**:
```markdown
# Competitive Analysis: AI Assistants Market
*Prepared: 2026-02-08 | Confidence: High*

## Executive Summary
- **Market leader**: Competitor A ($2.1B revenue, 45% market share)
- **Fastest growing**: Competitor C (312% YoY, targeting enterprise)
- **Our gap**: No voice integration -- both A and C have it, we don't
- **Opportunity**: B2B vertical focus is underserved by all three
- **Recommendation**: Ship voice in Q2, target B2B vertical in Q3

## Key Findings

### Finding 1: Voice is table stakes
All top 3 competitors launched voice features in 2025. Users with voice
enabled retain at 2.3x the rate of text-only users (Source: Competitor A's
investor deck, Jan 2026).

### Finding 2: Enterprise is the revenue driver
| Metric | Comp A | Comp B | Comp C |
|--------|--------|--------|--------|
| Revenue | $2.1B | $890M | $340M |
| Enterprise % | 62% | 41% | 78% |
| Growth YoY | 48% | 22% | 312% |
| Voice support | Yes | No | Yes |

### Finding 3: Pricing convergence
All three converge around $20-30/seat/month for business plans.
Competing on price is not viable.

## Recommendations
1. **Ship voice integration by Q2** -- it's blocking enterprise deals (High priority)
2. **Target B2B verticals** -- healthcare and legal are underserved (Medium priority)
3. **Don't compete on price** -- differentiate on customization and privacy (Strategic)

## Sources
- Competitor A Investor Deck (Jan 2026)
- Crunchbase market data
- G2 comparison reviews (487 reviews analyzed)
```

## Edge Cases

- **Insufficient data**: State what's known vs unknown. Never fabricate data points.
- **Conflicting sources**: Present both, note the conflict, recommend which to trust and why.
- **Audience is technical**: Include methodology section, raw data references.
- **Audience is non-technical**: Remove jargon, use analogies, keep to executive summary + recommendations.
- **Time-sensitive**: Mark the report with "Valid as of [date]" -- data expires.

## Quality Checklist

- [ ] Executive summary exists and is under 5 bullet points
- [ ] Every claim has a source or is marked as an estimate
- [ ] At least one comparison table is included
- [ ] Recommendations are numbered and prioritized
- [ ] Confidence level is stated
- [ ] No section exceeds 200 words without a visual break (table, list, header)
- [ ] Risks/uncertainties section is included
