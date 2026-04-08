# Deep Research -- Evaluation

## TC-1: Follows the 7-Phase Methodology
- **prompt:** "Research the security implications of using WebAssembly in production web applications"
- **context:** High-stakes research question spanning multiple domains (security, web development, runtime environments). Clearly benefits from iterative depth.
- **assertions:**
  - Phase 1 (Clarify) produces a research brief with: core question, 3-5 sub-questions, key search terms, expected sections, completion criteria
  - Phase 2 (Draft) covers all sub-questions from the brief, even shallowly, with `[NEEDS VERIFICATION]` markers on uncertain claims
  - Phase 3 (Gap Analysis) produces a gap list with max 5 gaps, each with question, importance level, and target section
  - Phase 4 (Targeted Research) researches gaps individually with confidence levels and source tracking
  - Phase 5 (Refine) integrates findings into the draft, removes `[NEEDS VERIFICATION]` tags, and resolves contradictions
  - Phase 6 (Red Team) produces a critique list with severity levels (critical/major/medium/minor)
  - Phase 7 (Converge) scores on 5 dimensions (completeness, accuracy, depth, structure, balance) out of 10
- **passing_grade:** 6/7 assertions must pass

## TC-2: Performs Gap Analysis That Drives Depth
- **prompt:** "Compare GraphQL vs REST for our existing microservices architecture"
- **context:** After Phase 2 draft, the agent has broad coverage but lacks specific performance benchmarks, migration cost data, and production case studies.
- **assertions:**
  - Gap analysis identifies specific, answerable questions (not vague themes)
  - Each gap has an importance level: high, medium, or low
  - High-importance gaps are about core question requirements (e.g., "P99 latency difference for nested queries")
  - Medium-importance gaps add depth but are not essential (e.g., "team migration regret percentage")
  - If no gaps are found, the process skips directly to Phase 7 (convergence)
  - Gap questions are distinct from Phase 2 content -- they identify what is MISSING, not what was already found
- **passing_grade:** 5/6 assertions must pass

## TC-3: Knows When to Converge vs Keep Iterating
- **prompt:** "What are the trade-offs of moving from monolith to microservices?"
- **context:** After 2 iterations, the quality score is 6.5/10. Completeness and accuracy are strong (2/2 each) but depth is 1/2 and balance is 1.5/2. Max iterations is 4.
- **assertions:**
  - Score 6.5 is below target (7.0) -- iteration continues
  - Next iteration focuses on the lowest-scoring dimension (depth at 1/2)
  - If the score does not improve between iterations (plateau), convergence is triggered via diminishing returns rule
  - After reaching max iterations (4), the report is delivered with a quality note explaining remaining gaps
  - Convergence note includes: current score, remaining gaps, what additional iteration would improve
- **passing_grade:** 4/5 assertions must pass

## TC-4: Routes Simple Questions Away From Deep Research
- **prompt:** "What is the default port for PostgreSQL?"
- **context:** Simple factual lookup with a well-known, single-pass answer. No ambiguity, no contradicting sources, no need for iteration.
- **assertions:**
  - Deep research is NOT triggered (fails the "When NOT to Use" criteria: simple factual lookup)
  - The question is answered directly without 7-phase treatment
  - Threshold rule is applied: the question can be answered confidently in a single pass
  - No research brief, gap analysis, or red team phase is invoked
- **passing_grade:** 3/4 assertions must pass

## TC-5: Produces Structured Output With Confidence Assessment
- **prompt:** "What are the best practices for securing a Kubernetes cluster in production?"
- **context:** Research completed after 3 iterations. Score: 8/10. Multiple sources consulted including official docs, industry case studies, and security benchmarks. Some findings have contradictory sources.
- **assertions:**
  - Final output includes all required sections: Summary, Findings (with sub-sections matching the brief), Confidence Assessment, Sources, Remaining Uncertainties, Methodology
  - Confidence assessment table includes per-finding confidence levels (High/Medium/Low) with basis
  - Sources are real (from tool results) with descriptions of what each supported
  - Remaining Uncertainties section lists areas where research could not fully resolve the question
  - Methodology section reports: iteration count, final quality score, phases completed, total sources consulted
  - Contradictory findings are presented with both positions and their evidence, not hidden
- **passing_grade:** 5/6 assertions must pass
