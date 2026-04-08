# General Research -- Evaluation

## TC-1: Happy Path -- Multi-Source Research Question
- **prompt:** "Research the health effects of intermittent fasting. I need a solid summary with sources."
- **context:** User wants a research synthesis on a health topic with multiple credible sources available.
- **assertions:**
  - Response breaks the research question into sub-questions (e.g., metabolic effects, long-term risks, population-specific outcomes)
  - At least 3 independent sources are cited (triangulation / 3-source rule)
  - Sources are ranked or evaluated using CRAAP-style criteria (currency, authority, accuracy)
  - A source hierarchy is respected -- peer-reviewed or institutional sources prioritized over blogs/social media
  - Response includes an executive summary or key findings section followed by detailed analysis
- **passing_grade:** 4/5 assertions must pass

## TC-2: Edge Case -- Conflicting Sources
- **prompt:** "Is red meat bad for you? I keep seeing contradictory information."
- **context:** User is confused by conflicting claims across sources. Skill should demonstrate conflict resolution methodology.
- **assertions:**
  - Response acknowledges the conflict explicitly rather than picking one side
  - Conflicting sources are compared by credibility (sample size, peer review status, recency, funding/bias)
  - Resolution follows the triangulation process -- identifies which sources are primary vs secondary
  - Red flags are called out if any source exhibits them (no author, sensational headline, no citations)
  - Final conclusion states the weight of evidence with appropriate hedging (not absolute certainty)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Edge Case -- Vague Research Request
- **prompt:** "Research AI for me."
- **context:** User gives an overly broad, non-specific request. Skill methodology says to define a specific question first.
- **assertions:**
  - Response does NOT immediately dump information about AI
  - Response asks clarifying questions or proposes a narrowed research question (e.g., "AI in healthcare risks" vs "research AI")
  - If the assistant proceeds without clarification, it explicitly reframes the vague topic into specific sub-questions
  - The research workflow's step 1 is applied: "Define the question -- Bad: 'Research AI'; Good: 'What are the top 3 risks of AI in healthcare?'"
- **passing_grade:** 3/4 assertions must pass

## TC-4: Quality Check -- Citation and Source Formatting
- **prompt:** "Find me 3 credible sources about the effectiveness of remote work on productivity. Format them properly."
- **context:** User explicitly wants formatted citations. Tests citation formatting methodology.
- **assertions:**
  - At least 3 sources are provided with full citation details (author, date, title, publication, URL where applicable)
  - Citations follow a consistent format (APA or clearly structured)
  - Each source includes a credibility assessment note (why this source is trustworthy)
  - Source types are mixed (not all from the same category -- e.g., not all news articles)
  - In-text citation style is demonstrated or offered (e.g., "According to Smith (2024)...")
- **passing_grade:** 4/5 assertions must pass

## TC-5: Edge Case -- Outdated Information Risk
- **prompt:** "What are the best practices for SEO in 2026?"
- **context:** Fast-changing topic where outdated sources are a major pitfall. Tests date-awareness methodology.
- **assertions:**
  - Response prioritizes recent sources (2025-2026) over older ones
  - If older sources are referenced, the response flags them as potentially outdated
  - The common pitfall "Not Checking Dates" is avoided -- no 2020-era SEO advice presented as current
  - Response acknowledges the fast-changing nature of the topic and recommends re-checking periodically
- **passing_grade:** 3/4 assertions must pass
