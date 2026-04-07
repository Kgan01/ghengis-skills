# Tutoring -- Evaluation

## TC-1: Happy Path -- Beginner Concept Explanation
- **prompt:** "What is a database? I'm not technical at all."
- **context:** Non-technical learner asking a foundational question. Tests level assessment and analogy use.
- **assertions:**
  - Level is assessed as beginner (explicitly or inferred from "not technical at all")
  - Explanation uses at least one real-world analogy (e.g., filing cabinet, spreadsheet, phone contacts)
  - No technical jargon is used without explanation (no raw SQL, no "relational model" without context)
  - A concrete example is included showing a database in action (e.g., how a contacts app stores data)
  - A check-understanding question is posed (answerable from the explanation given)
  - A next step for continued learning is suggested
- **passing_grade:** 5/6 assertions must pass

## TC-2: Happy Path -- Intermediate Worked Example
- **prompt:** "I know basic JavaScript. Can you explain how promises work?"
- **context:** Intermediate learner with stated prior knowledge. Tests incremental teaching and worked examples.
- **assertions:**
  - Level is assessed as intermediate based on stated JS knowledge
  - Explanation starts with "why" -- what problem promises solve (callback hell, async operations)
  - A concrete code example is provided showing a promise in action
  - The example builds incrementally (simple promise first, then chaining or async/await)
  - A check-understanding question or exercise is included
  - A common misconception is addressed (e.g., "promises make code synchronous" or forgetting error handling)
- **passing_grade:** 5/6 assertions must pass

## TC-3: Edge Case -- Frustrated Learner
- **prompt:** "I've been trying to understand recursion for hours and I just can't get it. I give up."
- **context:** Learner is frustrated and about to quit. Tests the emotional handling edge case.
- **assertions:**
  - Response acknowledges the difficulty first ("This IS hard", "Most people struggle here")
  - Tone is encouraging and empathetic, not condescending
  - Explanation is simplified compared to a standard recursion explanation -- starts with the absolute simplest analogy
  - Uses an example-before-definition approach (show it working, then explain the theory)
  - Does NOT say "you're wrong" or imply the learner should have understood by now
  - A manageable next step is provided (not "now go implement a binary tree")
- **passing_grade:** 5/6 assertions must pass

## TC-4: Edge Case -- Wrong Mental Model
- **prompt:** "So an array is basically just a variable that holds multiple values at once, right? Like a variable but bigger?"
- **context:** Learner has a partially correct but incomplete mental model. Tests misconception handling.
- **assertions:**
  - Response does NOT say "you're wrong" or dismiss the mental model
  - Acknowledges what IS correct about the model (arrays do hold multiple values)
  - Gently shows where the model breaks down (indexing, ordered nature, type constraints in some languages)
  - Provides a better analogy or refinement (e.g., numbered mailboxes, a row of lockers)
  - Includes a concrete example demonstrating the aspects the original model missed
- **passing_grade:** 4/5 assertions must pass

## TC-5: Quality Check -- Teaching Response Structure
- **prompt:** "Explain how CSS flexbox works. I know HTML and basic CSS but flexbox confuses me."
- **context:** Tests whether the full tutoring response structure is applied (level, explanation, example, check, next step, misconception).
- **assertions:**
  - Level assessment is present (intermediate -- knows HTML/CSS basics)
  - Main explanation uses an analogy or visual description (e.g., items in a row on a shelf)
  - A concrete example is included (actual CSS code with flex properties demonstrated)
  - A check-understanding question is included (answerable from the explanation)
  - A next step is provided (e.g., CSS Grid as the logical follow-up)
  - A common misconception is addressed (e.g., confusing `justify-content` vs `align-items`)
- **passing_grade:** 5/6 assertions must pass
