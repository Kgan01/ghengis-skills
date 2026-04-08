# Report Writing -- Evaluation

## TC-1: Happy Path -- Standard Research Output
- **prompt:** "Write a report on the current state of electric vehicle adoption in the US. Audience is our VP of Strategy."
- **context:** Standard request with defined topic and executive audience. Tests full template application.
- **assertions:**
  - Starts with an executive summary (3-5 bullet points, conclusion first)
  - Key findings sections lead with the finding headline, not methodology
  - At least one comparison table is included (not prose where a table works better)
  - Data is included (numbers, percentages, trends -- not vague qualitative statements)
  - Recommendations are numbered, prioritized, and actionable
  - A confidence level is stated (High/Medium/Low)
  - Sources section is present with citations for claims
- **passing_grade:** 6/7 assertions must pass

## TC-2: Edge Case -- Insufficient Data
- **prompt:** "Write a report on the market size of AI-powered pet care products."
- **context:** Niche topic where comprehensive data is likely unavailable.
- **assertions:**
  - Clearly distinguishes known facts from estimates or projections
  - Gaps in data are explicitly stated ("No reliable market size data found for this specific niche")
  - Does NOT fabricate data points or cite non-existent sources
  - A Risks & Uncertainties section is included acknowledging data limitations
  - Recommendations account for uncertainty (e.g., "conduct primary research" as a next step)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Quality Check -- Structure and Formatting
- **prompt:** "Compile a competitive analysis of the top 3 project management tools. Audience is the engineering team lead."
- **context:** Technical audience, comparison-heavy content. Tests table usage, structure, and audience-appropriate depth.
- **assertions:**
  - Follows the template structure (executive summary, key findings, detailed analysis, recommendations, sources)
  - A comparison table is used for the 3-tool comparison (not described in prose)
  - Technical details are included since the audience is an engineering lead (API support, integrations, extensibility)
  - No section exceeds 200 words without a visual break (table, list, or header)
  - Each claim or data point has a source or is explicitly marked as an estimate
  - Recommendations are tied to specific findings (not generic advice)
- **passing_grade:** 5/6 assertions must pass

## TC-4: Edge Case -- Conflicting Sources
- **prompt:** "Write a report on whether remote work increases or decreases productivity. I've seen arguments both ways."
- **context:** Topic with well-known conflicting evidence.
- **assertions:**
  - Both sides of the argument are presented with their supporting evidence
  - The conflict is noted explicitly, not papered over with a false consensus
  - Sources on each side are evaluated for credibility (study size, methodology, recency)
  - Recommends which evidence to trust more and explains why
  - A Risks & Uncertainties section acknowledges the mixed evidence landscape
- **passing_grade:** 4/5 assertions must pass

## TC-5: Edge Case -- Non-Technical Audience
- **prompt:** "Write a report explaining our cloud migration progress for the board of directors."
- **context:** Non-technical audience (board). Tests audience adaptation -- removing jargon, keeping to summary.
- **assertions:**
  - Executive summary is clear and jargon-free (no "Kubernetes", "CI/CD", or "microservices" without plain-English explanation)
  - Technical concepts are explained with analogies where needed
  - Emphasizes business impact (cost savings, timeline, risk) over technical details
  - Recommendations are business-oriented (budget, timeline, staffing) not technical (infra choices)
  - Stays concise -- board members need the bottom line, not deep dives
- **passing_grade:** 4/5 assertions must pass
