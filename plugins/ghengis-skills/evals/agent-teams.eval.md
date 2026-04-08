# Agent Teams — Evaluation

## TC-1: Creative Task Spawns Parallel Perspectives
- **prompt:** "Write a tagline for our new developer productivity CLI tool."
- **context:** The tool helps developers reduce context-switching. Target audience: individual contributors and tech leads. Classic creative task where multiple perspectives add value.
- **assertions:**
  - Spawns at least 3 parallel agents with distinct creative perspectives
  - Each agent receives the same core task but a different creative constraint (e.g., Minimalist, Bold, Technical)
  - Agents run in parallel (not sequential)
  - A synthesis step combines the best elements from all variations
  - Synthesis output identifies which perspective contributed which element
- **passing_grade:** 4/5 assertions must pass

## TC-2: Factual Task Does NOT Trigger Teams
- **prompt:** "How many bytes are in a kilobyte?"
- **context:** Single correct answer. No creative variation possible. Teams would be overkill.
- **assertions:**
  - Does NOT spawn multiple agents with different perspectives
  - Answers directly with a single response
  - Does NOT mention perspectives, variations, or synthesis
  - Response is concise and factual
- **passing_grade:** 4/4 assertions must pass

## TC-3: Synthesis Quality — Not Bland Averaging
- **prompt:** "Write a product description for a premium noise-cancelling headphone aimed at remote workers."
- **context:** Marketing copy task. Should use 4-5 perspectives. The synthesis is the critical quality check.
- **assertions:**
  - Synthesis creates a new combined output (not just picking one variation)
  - Synthesis does NOT average all variations into generic mush
  - Synthesis output is not longer than the longest individual variation
  - Synthesis identifies the strongest element from each perspective (e.g., "structure from Minimalist, hook from Bold")
  - Final output maintains a coherent, consistent tone (not jarring tone shifts)
- **passing_grade:** 4/5 assertions must pass

## TC-4: Appropriate Team Size Selection
- **prompt:** "Write API documentation for the /users endpoint."
- **context:** Technical documentation task. Creativity matters less than precision. Full 5-perspective team is overkill.
- **assertions:**
  - Uses a reduced team size (2-3 perspectives, not all 5)
  - Selects Minimalist and/or Technical perspectives as primary (most relevant for docs)
  - Does NOT use Playful or Bold perspectives for technical documentation
  - Justifies the team size selection based on the task type
- **passing_grade:** 3/4 assertions must pass

## TC-5: Custom Perspectives for Domain-Specific Tasks
- **prompt:** "Generate 5 name ideas for a cozy neighborhood coffee shop that also sells used books."
- **context:** Brand naming task. The default 5 perspectives may not all fit. Custom perspectives (e.g., "Nostalgic", "Literary", "Neighborhood Local") would add more value than generic Technical or Minimalist.
- **assertions:**
  - Considers creating custom perspectives tailored to the domain (coffee shop + bookstore)
  - Custom perspectives have a name, description, and constraints (matching the template format)
  - Does not force-fit all 5 default perspectives when some are clearly irrelevant
  - Synthesis step still follows the standard process (collect, identify strengths, combine)
- **passing_grade:** 3/4 assertions must pass
