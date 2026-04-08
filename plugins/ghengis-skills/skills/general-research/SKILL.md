---
name: general-research
description: Use when the user needs deep research on any topic — teaches systematic research methodology including source evaluation, iterative refinement, fact-checking, and structured findings
allowed-tools: Read Grep Glob WebSearch WebFetch
---

# General Research

## When to Use
When helping with any research task: finding information, evaluating claims, comparing options, building literature reviews, investigating topics, or answering complex questions that require multiple sources.

## Core Methodology

### Search Operator Mastery

**Google Search Operators**
- `site:` -- Search within specific domain
  - Example: `site:nytimes.com climate change`
- `filetype:` -- Find specific file types
  - Example: `budget template filetype:xlsx`
- `intitle:` -- Search in page titles
  - Example: `intitle:"annual report" tesla`
- `inurl:` -- Search in URL
  - Example: `inurl:blog marketing strategy`
- `related:` -- Find similar websites
  - Example: `related:techcrunch.com`
- `"exact phrase"` -- Search exact match
  - Example: `"climate change is real"`
- `-exclude` -- Exclude terms
  - Example: `python -snake -snake oil`
- `OR` -- Either term (use CAPS)
  - Example: `marketing OR advertising`
- `*` -- Wildcard
  - Example: `"best * for productivity"`
- `..` -- Number range
  - Example: `laptop $500..$1000`

**Combining Operators**
```
Research question: "Find academic papers on AI ethics from .edu domains published 2022-2024"

Search query:
site:edu filetype:pdf "artificial intelligence" ethics 2022..2024
```

### Source Credibility Assessment

**CRAAP Test** (Currency, Relevance, Authority, Accuracy, Purpose)
- **Currency**: When was it published? (Updated recently = more credible for news/tech)
- **Relevance**: Does it answer your research question? (Not just keyword match)
- **Authority**: Who wrote it? (Credentials? Affiliated institution?)
- **Accuracy**: Can you verify claims? (Sources cited? External validation?)
- **Purpose**: Why was it written? (Inform, sell, persuade, entertain?)

**Source Hierarchy** (Most to Least Credible)
1. **Peer-reviewed journals** (Nature, Science, JAMA)
2. **Government/Institutional reports** (.gov, .edu, WHO, World Bank)
3. **Established news organizations** (Reuters, AP, NYT, WSJ)
4. **Industry reports** (Gartner, Forrester, McKinsey)
5. **Expert blogs** (Verified credentials, transparent methodology)
6. **Wikipedia** (Good starting point, but verify via citations)
7. **Random blogs/forums** (Use with extreme caution, verify heavily)
8. **Social media** (Lowest credibility, requires corroboration)

**Red Flags**
- No author listed (anonymous = suspicious)
- No date (old info presented as new?)
- Sensational headlines ("You won't believe...")
- No citations (claims without evidence)
- Bias/agenda (political site, company selling product)
- Spelling/grammar errors (unprofessional = less credible)

### Multi-Source Triangulation

**The 3-Source Rule**
- Never rely on single source for important facts
- Find 3 independent sources that agree
- If sources conflict, dig deeper (who's right? why do they differ?)

**Triangulation Process**
```
Claim: "70% of businesses use AI"

Source 1: Forbes article (cites McKinsey survey)
Source 2: McKinsey report (primary source, 2024, n=3,000 companies)
Source 3: Gartner report (similar stat: 65%, 2023, n=2,500 companies)

Conclusion: Credible (primary sources, large samples, similar results)
Best citation: McKinsey report (primary source)
```

**Handling Conflicting Sources**
```
Claim: "Coffee is good/bad for health"

Source 1 (pro): Harvard study (2023, n=100k, shows reduced heart disease)
Source 2 (con): Blog post (2020, no study cited, anecdotal)

Resolution:
- Harvard study = peer-reviewed, large sample, recent -> more credible
- Blog = no evidence, older, not authoritative -> disregard
Conclusion: Coffee likely beneficial (based on credible research)
```

### Research Synthesis Patterns

**Bottom-Up Synthesis** (Details -> Big Picture)
1. Collect all relevant facts/data points
2. Group into themes/categories
3. Identify patterns and connections
4. Draw conclusions from patterns

**Top-Down Synthesis** (Question -> Answer)
1. Define research question
2. Break into sub-questions
3. Answer each sub-question
4. Combine answers into overall conclusion

**Comparison Matrix**
```
Question: "What's the best project management tool?"

        | Asana  | Trello | Monday | Jira  |
--------|--------|--------|--------|-------|
Price   | $$     | $      | $$$    | $$    |
Ease    | High   | High   | Medium | Low   |
Features| Medium | Low    | High   | High  |
Best For| Teams  | Simple | Complex| Dev   |
```

## Research Project Workflow

```
1. Define the question:
   - Bad: "Research AI"
   - Good: "What are the top 3 risks of AI in healthcare?"

2. Break into sub-questions:
   - What is AI being used for in healthcare?
   - What risks have been identified?
   - Which risks are most significant?

3. Identify source types needed:
   - Academic papers (for scientific claims)
   - News articles (for current events)
   - Government reports (for regulations)
   - Industry surveys (for adoption stats)

4. Search strategy:
   - Start broad: "AI healthcare risks"
   - Narrow with operators: site:edu filetype:pdf "AI healthcare" risks
   - Follow citations: Find key paper, check its references

5. Collect and organize:
   - Tag by theme (privacy, bias, safety)
   - Rate credibility (high/medium/low)

6. Synthesize findings:
   - Group by sub-question
   - Identify consensus (3+ sources agree)
   - Note conflicting views (explain why)

7. Write report:
   - Executive summary (1 paragraph)
   - Key findings (3-5 bullet points)
   - Detailed analysis (by sub-question)
   - Recommendations (actionable next steps)
   - Citations (full source list)
```

### Citation Formatting

**APA Style** (most common for research)
```
Journal article:
Author, A. A. (Year). Title of article. Journal Name, Volume(Issue), pages. DOI

Example:
Smith, J. (2024). AI in healthcare. Nature Medicine, 30(2), 145-152. https://doi.org/10.1038/nm.2024.01

Website:
Author, A. A. (Year, Month Day). Title of page. Site Name. URL

Example:
Jones, B. (2024, January 15). The future of AI. TechCrunch. https://techcrunch.com/future-ai

Report:
Organization. (Year). Title of report. URL

Example:
McKinsey & Company. (2024). State of AI Report 2024. https://mckinsey.com/ai-report
```

**Quick In-Text Citation**
- First mention: "According to a McKinsey report (2024)..."
- Subsequent: "The report also found..."
- Multiple sources: "Studies show... (Smith, 2024; Jones, 2023)"

## Common Pitfalls

### Confirmation Bias
- **Trap**: Only searching for sources that support your hypothesis
- **Result**: Skewed research, missed counter-evidence
- **Fix**: Actively search for opposing views, steel-man the counter-argument

### Wikipedia as Final Source
- **Mistake**: Citing Wikipedia directly
- **Problem**: Wikipedia is tertiary (summary of summaries), can be edited by anyone
- **Fix**: Use Wikipedia to find original sources (check citations), cite those instead

### Not Checking Dates
- **Issue**: Using 2015 article for 2024 research (tech/medicine changes fast)
- **Result**: Outdated information
- **Fix**: Filter by date range, prioritize recent sources for fast-changing topics

### Trusting First Result
- **Error**: Using top search result without checking credibility
- **Reality**: Top result does not equal most credible (could be SEO-optimized)
- **Fix**: Check 5-10 results, compare sources, use CRAAP test

### Not Following Citations
- **Miss**: Article cites a study but doesn't link to it
- **Problem**: Can't verify claim (broken telephone)
- **Fix**: Find original study (search study title + author), read it directly

### Over-Reliance on One Source Type
- **Symptom**: Only using news articles for scientific claim
- **Issue**: News = simplified/sensationalized, not peer-reviewed
- **Fix**: Mix source types (academic papers + news + expert analysis)

## Quick Reference

### Common Research Scenarios

**Academic Research**
```
Search: site:edu OR site:org filetype:pdf [topic] [year range]
Sources: Google Scholar, PubMed, JSTOR
Cite: APA or MLA format
```

**Market Research**
```
Search: [industry] market size OR trends OR forecast
Sources: Statista, IBISWorld, Gartner, CB Insights
Cite: Organization, report title, year
```

**News/Current Events**
```
Search: [topic] site:reuters.com OR site:apnews.com
Sources: Reuters, AP, Bloomberg, NPR
Cite: Author, date, publication, URL
```

**Technical/How-To**
```
Search: [technology] documentation OR tutorial OR "best practices"
Sources: Official docs, Stack Overflow, GitHub
Cite: Project documentation, version, date
```

### Credibility Quick Check
```
Good signs:
- Author name + credentials visible
- Date published/updated shown
- Sources cited (links/references)
- Neutral tone (factual, not sensational)
- Domain: .edu, .gov, .org (non-profit)
- Grammar/spelling correct

Red flags:
- Anonymous author
- No date (or very old)
- No citations
- Sensational headline ("shocking", "you won't believe")
- Commercial site selling related product
- Typos/poor grammar
```

## Checklists

### Starting a Research Project
- [ ] Define specific research question (not vague topic)
- [ ] Break into 3-5 sub-questions
- [ ] Identify required source types (academic, news, industry)
- [ ] Set time box (1 hour? 1 day? 1 week?)
- [ ] Create structure to organize findings

### Evaluating a Source
- [ ] Check author (credentials? affiliated institution?)
- [ ] Check date (published/updated recently?)
- [ ] Check citations (claims supported by evidence?)
- [ ] Check bias (neutral reporting or agenda?)
- [ ] Check domain (.edu/.gov more credible than .com)
- [ ] Cross-reference (do other credible sources agree?)

### During Research
- [ ] Save URLs + key excerpts in organized structure
- [ ] Tag sources by theme/sub-question
- [ ] Rate credibility (high/medium/low)
- [ ] Note conflicting information (dig deeper)
- [ ] Follow citations to original sources
- [ ] Track time (don't rabbit-hole indefinitely)

### Synthesizing Findings
- [ ] Group sources by sub-question
- [ ] Identify consensus (3+ credible sources agree)
- [ ] Note disagreements (explain conflicting views)
- [ ] Draw evidence-based conclusions
- [ ] Identify gaps (what's still unknown?)
- [ ] Formulate recommendations (actionable next steps)

### Writing Research Report
- [ ] Executive summary (1 paragraph, key takeaways)
- [ ] Methodology (how you researched, what sources used)
- [ ] Key findings (3-5 bullet points with evidence)
- [ ] Detailed analysis (by sub-question, cite sources)
- [ ] Limitations (what you couldn't find/verify)
- [ ] Recommendations (actionable based on findings)
- [ ] Full citation list (APA format, alphabetical)

### Final Quality Check
- [ ] All claims cited (no unsupported statements)
- [ ] 3+ sources for key facts (triangulation)
- [ ] Primary sources used where possible (not secondary)
- [ ] Dates checked (no outdated info for fast-changing topics)
- [ ] Conflicting sources addressed (not ignored)
- [ ] Bias acknowledged (recognize limitations of sources)
