---
name: deep-research
description: Use when a research task requires iterative depth -- goes beyond single-pass research with a 7-phase methodology that includes gap analysis, targeted follow-up, adversarial review, and convergence checking
---

# Deep Research

TTD-DR (Test-Time Deepen -- Deep Research). An iterative research methodology that goes beyond "search and summarize" by adding gap analysis, targeted follow-up, adversarial critique, and convergence scoring. Seven phases, repeated until the research is deep enough or the iteration budget runs out.

This is a research methodology, not a search tool. Apply it by structuring how you approach complex questions -- decomposing them, identifying gaps in your knowledge, filling those gaps, and stress-testing your conclusions before delivering.

## When to Use Deep Research

- **High-stakes questions** where being wrong matters (client advice, architecture decisions, medical/legal research)
- **Complex questions** that span multiple domains or have no single authoritative answer
- **Ambiguous questions** where "done" is not obvious and the user needs comprehensive coverage
- **Contradictory topics** where different sources disagree and you need to reconcile or present both sides
- **Research deliverables** -- reports, analyses, white papers, literature reviews

## When NOT to Use Deep Research

- **Simple factual lookups** -- "What is the capital of France?" does not need 7 phases
- **Quick questions** with clear, well-known answers
- **Time-sensitive requests** where speed matters more than depth
- **Opinion requests** where the user wants YOUR perspective, not exhaustive coverage
- **Tasks under ~40 words** that have a single-pass answer

**Threshold rule:** If you can answer confidently and comprehensively in a single pass, do that. Deep research adds value only when the question genuinely benefits from iteration.

## The 7-Phase Methodology

```
Phase 1: CLARIFY     -->  Decompose question, define "done"
Phase 2: DRAFT       -->  Initial broad research pass
Phase 3: GAP ANALYSIS -->  Identify what's missing or uncertain
Phase 4: TARGETED RESEARCH -->  Go deep on specific gaps
Phase 5: REFINE      -->  Synthesize all findings into coherent narrative
Phase 6: RED TEAM    -->  Adversarial review -- challenge every claim
Phase 7: CONVERGE    -->  Final synthesis with confidence levels
         |
         +---> Score quality 0-10
         |     Score >= target? --> Deliver
         |     Score < target?  --> Loop back to Phase 3
         +---> Max iterations reached? --> Deliver with quality notes
```

### Phase 1: Clarify

Decompose the question before researching. Do not start gathering information until you know what you are looking for.

**Produce a research brief:**

1. **Core question** -- Refine the user's question for clarity and precision
2. **Sub-questions** (3-5) -- Break the core question into answerable parts
3. **Key search terms** -- What to look for across sources
4. **Expected sections** -- What the final report should contain
5. **Completion criteria** -- What makes the answer "done" vs. "incomplete"

**Example:**

```
User question: "Should we migrate from REST to GraphQL?"

Research brief:
  Core question: What are the technical and organizational trade-offs of
                 migrating an existing REST API to GraphQL for our use case?

  Sub-questions:
    1. What performance differences exist (latency, payload size, caching)?
    2. What is the migration cost (developer time, tooling, training)?
    3. What operational risks exist (monitoring, debugging, security)?
    4. What do teams who have done this migration report in retrospect?
    5. Are there hybrid approaches that capture benefits without full migration?

  Completion criteria:
    - Each sub-question has at least 2 supporting sources
    - Contradicting viewpoints are presented for trade-offs
    - A clear recommendation framework (not just "it depends")
```

### Phase 2: Draft

Initial research pass. Cast a wide net across available sources.

**Sources to use (adapt to your context):**
- Web search for current information
- File/codebase reading for project-specific context
- API calls to data services
- Documentation and reference materials
- Prior knowledge (with explicit confidence markers)

**Rules for the draft:**
- Cover all sub-questions from the brief, even shallowly
- Mark uncertain claims with `[NEEDS VERIFICATION]`
- Note gaps explicitly: "No data found on X"
- Include source references for every factual claim
- Structure with clear sections matching the brief's expected sections

### Phase 3: Gap Analysis

Read the draft critically against the research brief. Identify what is missing, uncertain, or contradictory.

**Produce a gap list (max 5 gaps per iteration):**

```json
[
  {
    "question": "What is the P99 latency difference between REST and GraphQL for nested queries?",
    "importance": "high",
    "section": "Performance Comparison"
  },
  {
    "question": "How does GraphQL affect API caching strategies (CDN, HTTP cache)?",
    "importance": "high",
    "section": "Operational Considerations"
  },
  {
    "question": "What percentage of teams report regretting the migration?",
    "importance": "medium",
    "section": "Industry Experience"
  }
]
```

**Importance levels:**
- **high** -- Core to answering the main question; report is incomplete without it
- **medium** -- Adds significant depth; worth filling if resources allow
- **low** -- Nice to have; skip if constrained

**If no gaps are found**, the research has converged -- skip to Phase 7.

### Phase 4: Targeted Research

Research each gap individually. This is where depth comes from -- focused investigation of specific unknowns rather than broad surveys.

**For each gap:**
1. Search specifically for that question
2. Look for primary sources (benchmarks, studies, official docs) not just blog posts
3. If sources contradict, record both positions with their evidence
4. Assign a confidence level to the findings

**Parallel execution:** Gaps are independent -- research them in parallel when possible (use subagents or multiple search passes).

**Track facts as you go:**

```json
{
  "content": "GraphQL queries with 3+ levels of nesting show 15-40% higher latency than equivalent REST calls",
  "source": "https://engineering.shopify.com/blogs/engineering/...",
  "confidence": 0.8,
  "is_disputed": true,
  "supporting_facts": ["Netflix benchmark showed similar results"],
  "contradicting_facts": ["Apollo team claims <5% difference with DataLoader"]
}
```

### Phase 5: Refine

Integrate new findings from Phase 4 into the draft.

**Refinement rules:**
1. Integrate new information into the appropriate sections
2. Remove `[NEEDS VERIFICATION]` tags where findings provide answers
3. Resolve contradictions -- note them explicitly if unresolvable
4. Improve structure and flow for readability
5. Ensure all claims have supporting evidence
6. Keep the draft comprehensive but well-organized

Do not just append findings -- weave them into the narrative so the final output reads as a cohesive document.

### Phase 6: Red Team

Adversarial critique of the refined draft. Deliberately try to break your own work.

**Challenge the draft on:**
1. **Unsupported claims** -- Is every factual statement backed by evidence?
2. **Logical contradictions** -- Does the analysis contradict itself anywhere?
3. **Missing perspectives** -- Are important viewpoints absent?
4. **Factual errors** -- Can any claim be disproven?
5. **Bias** -- Is the analysis one-sided or missing counterarguments?

**Produce a critique list (max 5 issues):**

```json
[
  {
    "issue": "Performance comparison relies entirely on synthetic benchmarks, no production data cited",
    "severity": "major",
    "suggestion": "Add real-world migration case studies with production metrics"
  },
  {
    "issue": "Security section does not address GraphQL-specific attack vectors (query complexity, batching)",
    "severity": "critical",
    "suggestion": "Add subsection on GraphQL security considerations: depth limiting, query cost analysis"
  }
]
```

**Severity levels:**
- **critical** -- Undermines the core conclusion; must fix before delivery
- **major** -- Significant gap or error; should fix if possible
- **medium** -- Noticeable weakness; fix if iterating, note if shipping
- **minor** -- Polish issue; fix opportunistically

### Phase 7: Converge

Score the draft and decide whether to iterate or deliver.

**Scoring rubric (0-10):**

| Dimension | Weight | What to Check |
|-----------|--------|---------------|
| **Completeness** | 0-2 | Does it answer all sub-questions from the brief? |
| **Accuracy** | 0-2 | Are claims well-supported with credible sources? |
| **Depth** | 0-2 | Is the analysis thorough beyond surface-level? |
| **Structure** | 0-2 | Is it well-organized and readable? |
| **Balance** | 0-2 | Are multiple perspectives and counterarguments covered? |

**Total: 0-10**

**Convergence rules:**
- Score >= 7: Deliver. Research is solid.
- Score 5-6: Iterate if budget allows. Address critical/major critiques from Phase 6.
- Score < 5: Iterate. Loop back to Phase 3 with a focus on the lowest-scoring dimensions.
- Max iterations reached: Deliver with a quality note explaining remaining gaps.

**Default settings:**
- Target score: 7.0
- Max iterations: 4
- If no gaps found in Phase 3: converged regardless of score

## Convergence Detection

Research is "deep enough" when any of these conditions is met:

1. **Score target reached** -- Quality score >= target (default 7.0)
2. **No gaps found** -- Phase 3 produces an empty gap list
3. **Diminishing returns** -- Score does not improve between iterations (plateau)
4. **Budget exhausted** -- Max iterations reached or compute tier drops to CRITICAL+

When delivering before full convergence, always note:
- Current quality score
- Remaining gaps or uncertainties
- What additional iteration would improve

## Output Format

The final deliverable is a structured report:

```markdown
# [Research Question]

## Summary
[2-3 sentence executive summary with the key finding/recommendation]

## Findings

### [Section 1 from brief]
[Content with inline source citations]

### [Section 2 from brief]
[Content with inline source citations]

...

## Confidence Assessment

| Finding | Confidence | Basis |
|---------|-----------|-------|
| [Key finding 1] | High (0.9) | Multiple concordant sources |
| [Key finding 2] | Medium (0.6) | Limited data, single source |
| [Key finding 3] | Low (0.4) | Contradictory sources, no consensus |

## Sources
1. [Source title](url) -- Used for: [what it supported]
2. [Source title](url) -- Used for: [what it supported]

## Remaining Uncertainties
- [Question that could not be fully resolved]
- [Area where more research would help]

## Methodology
- Iterations: [N]
- Final quality score: [X]/10
- Phases completed: [list]
- Total sources consulted: [N]
```

## Supervisor/Worker Pattern

For large research tasks, use a supervisor/worker architecture:

**Supervisor (you or the orchestrating agent):**
- Writes the research brief (Phase 1)
- Manages the iteration loop
- Runs gap analysis (Phase 3)
- Runs red team critique (Phase 6)
- Scores quality and decides convergence (Phase 7)

**Workers (subagents or focused research passes):**
- Execute the initial draft (Phase 2)
- Research individual gaps in parallel (Phase 4)
- Refine the draft with new findings (Phase 5)
- Address unresolved critiques

This separation ensures the supervisor maintains the big picture while workers go deep on specifics. Workers do not need to know about the overall iteration state -- they receive focused prompts and return focused results.

## Source Quality Evaluation

Not all sources are equal. Evaluate source quality at each phase:

| Source Type | Reliability | Use For |
|------------|-------------|---------|
| **Primary research** (papers, benchmarks, official docs) | High | Core claims, quantitative data |
| **Industry case studies** (engineering blogs from known companies) | Medium-High | Real-world validation, practical insights |
| **Expert commentary** (conference talks, interviews) | Medium | Perspective, interpretation |
| **General articles** (news, blog posts) | Medium-Low | Background context, trend signals |
| **Forum discussions** (Stack Overflow, Reddit) | Low-Medium | Anecdotal evidence, edge cases |
| **AI-generated content** (other LLM outputs) | Low | Treat as unverified claims |

**Rules:**
- High-confidence claims need at least one primary or industry source
- If only forum/blog sources exist, flag the finding as lower confidence
- When sources conflict, weight by source type and recency
- Always prefer primary sources over commentary about primary sources

## Worked Example: 7-Phase Cycle

**Question:** "What are the security implications of using WebAssembly in production web applications?"

**Phase 1 -- Clarify:**
- Sub-questions: memory safety, sandboxing model, known CVEs, comparison to JavaScript security model, mitigation strategies
- Completion: each sub-question answered with sources, threat model provided

**Phase 2 -- Draft:**
- Broad survey: WebAssembly security model, browser sandbox, known vulnerabilities
- Gaps noted: `[NEEDS VERIFICATION]` on specific CVE counts, no data on server-side Wasm security

**Phase 3 -- Gap Analysis:**
- Gap 1 (high): "What specific CVEs target WebAssembly runtimes?" (section: Known Vulnerabilities)
- Gap 2 (high): "How does Wasm sandboxing compare to V8 isolates for security?" (section: Sandboxing)
- Gap 3 (medium): "What are the security implications of Wasm on the server side (Wasmtime, Wasmer)?" (section: Server-Side Considerations)

**Phase 4 -- Targeted Research:**
- Researched each gap with focused searches
- Found 12 Wasm-related CVEs, sandbox escape research from academic papers, Bytecode Alliance security audits

**Phase 5 -- Refine:**
- Integrated CVE data into vulnerability section
- Added server-side Wasm security subsection
- Removed 3 `[NEEDS VERIFICATION]` tags
- Restructured comparison section for clarity

**Phase 6 -- Red Team:**
- Issue (major): "Analysis assumes browser-only Wasm but server-side usage is growing fast"
- Issue (medium): "No mention of supply chain attacks via Wasm modules"
- Addressed both in a refinement pass

**Phase 7 -- Converge:**
- Completeness: 2/2, Accuracy: 2/2, Depth: 1.5/2, Structure: 2/2, Balance: 1.5/2
- Score: 9/10 -- exceeds target, deliver

## Integration with Other Patterns

| Pattern | How It Uses Deep Research |
|---------|-------------------------|
| **OORT Cascade** | Deep research is the Researcher role's methodology within a cascade |
| **Compute Adaptation** | At LOW tier, reduce max iterations; at CRITICAL, skip red-team phase |
| **Audit Ledger** | Each phase appends a ledger entry; iteration count and score tracked |
| **Constitutional AI** | `no_hallucination` rule reinforces source-backed claims |

## Anti-Patterns

| If you notice... | The problem is... | Fix it by... |
|-----------------|-------------------|-------------|
| Phase 2 draft is 5000 words with no sources | Writing an essay, not researching | Requiring inline citations for every factual claim |
| Phase 3 always finds 5 gaps | Generating gaps to fill the quota | Only listing genuine gaps; empty list means convergence |
| Phase 4 finds the same information as Phase 2 | Gaps are not specific enough | Writing gap questions as precise, answerable queries |
| Phase 6 red team always says "looks good" | Rubber-stamp critique | Requiring the red team to find at least 1 issue or explicitly justify why none exist |
| Score never reaches target after 4 iterations | Target is too high or question is inherently uncertain | Delivering with a quality note; some questions do not have clean answers |
| Every question gets 7-phase treatment | Over-engineering simple lookups | Using the "When NOT to Use" criteria to route simple questions to direct answers |
| Sources are all from the same domain/perspective | Research bias | Explicitly seeking contradicting viewpoints and alternative perspectives |
