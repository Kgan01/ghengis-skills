# Hallucination Detector -- Evaluation

## TC-1: Catches Fabricated URLs in Agent Output
- **prompt:** "Find documentation for configuring Prisma with SQLite"
- **context:** Agent generates text containing `https://docs.prisma.io/guides/database/sqlite-setup-2024` and `https://github.com/prisma/prisma-examples/tree/main/databases/sqlite-quickstart`. Neither URL came from a tool result -- both are agent-generated from memory.
- **assertions:**
  - Both URLs are flagged as fabricated (present in agent-generated text, not in tool results)
  - Severity is "warn" (not a medical/legal/financial context)
  - Recovery suggests verifying via browse/search tool or replacing with "Search for: Prisma SQLite configuration"
  - URLs that appear in tool result blocks are NOT flagged (source distinction rule applied)
- **passing_grade:** 3/4 assertions must pass

## TC-2: Flags Unsourced Precise Statistics
- **prompt:** "What percentage of companies have adopted microservices?"
- **context:** Agent responds: "According to recent industry data, 73.4% of enterprise companies have adopted microservices, with adoption growing 24.7% year over year. About 80% of startups use some form of distributed architecture."
- **assertions:**
  - "73.4%" is flagged -- decimal percentage without citation
  - "24.7%" is flagged -- decimal percentage without citation
  - "About 80%" is NOT flagged -- round number with hedging language
  - Recovery suggests replacing with hedged round numbers or verifying via search
- **passing_grade:** 3/4 assertions must pass

## TC-3: Detects Fabricated Academic Citations
- **prompt:** "What research exists on the effectiveness of pair programming?"
- **context:** Agent responds: "According to Dr. Williams et al. (2024), pair programming increases code quality by 15%. A 2023 study by Johnson and Chen found that pair programmers produce 40% fewer defects. As shown by Kumar (2022), the productivity impact depends on task complexity."
- **assertions:**
  - "Dr. Williams et al. (2024)" is flagged (Pattern A + Pattern B: attribution phrase with inline citation)
  - "A 2023 study by Johnson and Chen" is flagged (Pattern C: study reference with author names)
  - "As shown by Kumar (2022)" is flagged (Pattern A: attribution phrase)
  - Recovery suggests searching for actual papers or replacing with "research in this area suggests..." without fabricated attribution
  - All three associated statistics ("15%", "40%", "depends on") are evaluated -- "15%" and "40%" may also trigger the unsourced statistics check
- **passing_grade:** 4/5 assertions must pass

## TC-4: Catches Future Certainty Claims
- **prompt:** "When will Python 4.0 be released?"
- **context:** Agent responds: "Python 4.0 will definitely be released by January 2028. The Python Steering Council is guaranteed to approve the new type system. It will certainly include a new GIL-free mode. Python 3.x may continue receiving updates after 4.0 launches."
- **assertions:**
  - "will definitely be released by January 2028" is flagged (definitive future language + specific future date)
  - "is guaranteed to approve" is flagged (definitive future language)
  - "will certainly include" is flagged (definitive future language)
  - "may continue receiving" is NOT flagged (hedged prediction with "may")
  - Recovery suggests replacing definitive language with "may", "is expected to", or "is rumored to"
- **passing_grade:** 4/5 assertions must pass

## TC-5: Passes Grounded Content From Tool Results
- **prompt:** "Search for the latest React release notes"
- **context:** Agent ran a web search tool that returned URLs and statistics. Agent output includes: a URL from the search results (`https://react.dev/blog/2026/03/react-20`), a statistic from the search snippet ("React 20 reduced bundle size by 18.3%"), and a tool-sourced citation. All factual claims trace back to tool results.
- **assertions:**
  - No URLs are flagged (all came from tool results, not agent memory)
  - No statistics are flagged (all came from tool result snippets)
  - Source distinction rule is correctly applied -- tool output is treated as grounded
  - Severity escalation does NOT trigger (no medical/legal/financial context)
  - Zero hallucination signals detected in the output
- **passing_grade:** 4/5 assertions must pass
