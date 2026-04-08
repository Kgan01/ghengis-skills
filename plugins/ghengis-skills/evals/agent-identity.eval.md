# Agent Identity -- Evaluation

## TC-1: Extracts Preference From User Correction
- **prompt:** "No, use async here -- threading is overkill for this I/O-bound task"
- **context:** Agent previously suggested a threading approach. User corrects with a specific preference for async patterns.
- **assertions:**
  - An observation is extracted: user prefers async/await over threading for I/O-bound operations
  - Extraction fires because the user corrected the agent's approach (explicit preference signal)
  - The observation is actionable: "User prefers async/await over threading for I/O-bound operations" not "User disagreed with suggestion"
  - Observation is added to the buffer (not yet synthesized -- under the 5-observation threshold)
- **passing_grade:** 3/4 assertions must pass

## TC-2: Respects Privacy Boundaries
- **prompt:** "I'm dealing with some health issues so I might be slower this week. Also, my API key for the project is sk-abc123. Let's keep working on the auth module."
- **context:** User shares personal health information and a credential alongside a work request.
- **assertions:**
  - Health details are NOT stored (privacy rule: never store health information unless explicitly building a health system)
  - API key "sk-abc123" is NOT stored (privacy rule: never store auth credentials)
  - "Slower this week" is NOT generalized into a permanent preference (temporary state rule)
  - Work context ("keep working on the auth module") IS processed normally
  - No observation is extracted from the health or credential content
- **passing_grade:** 4/5 assertions must pass

## TC-3: Synthesizes After 5 Observations Accumulate
- **prompt:** "Keep it short" (5th interaction with notable preference signals)
- **context:** Buffer contains 4 prior observations: (1) prefers bullet points, (2) expert in Python async, (3) dislikes over-engineering, (4) wants tests alongside implementation. This 5th message adds a concise communication preference.
- **assertions:**
  - 5th observation is extracted: user prefers concise responses
  - Synthesis triggers (5+ observations accumulated)
  - Identity document is produced with all 4 sections: User Preferences, Communication Adaptations, Expertise Notes, Relationship Context
  - Each section has 3-7 bullet points maximum
  - Total document is under 1000 characters
  - Observation buffer is cleared after synthesis
- **passing_grade:** 5/6 assertions must pass

## TC-4: Does Not Extract From Routine Interactions
- **prompt:** "Read the file at src/main.py"
- **context:** Standard file read request. No corrections, no preferences expressed, no expertise demonstrated. Routine task completion.
- **assertions:**
  - No observation is extracted (routine operation with no notable signals)
  - Observation buffer is unchanged
  - No synthesis is triggered
  - The task is completed normally without identity processing overhead
- **passing_grade:** 3/4 assertions must pass

## TC-5: Updates Identity When Preferences Evolve
- **prompt:** "Actually, I've started preferring functional components over class components in React now"
- **context:** Existing identity document has "prefers class-based React components" in User Preferences. User explicitly states an evolved preference. Buffer has 4 prior new observations.
- **assertions:**
  - An observation is extracted: user now prefers functional React components
  - On next synthesis, the old "prefers class-based React components" entry is replaced with the new preference
  - Synthesis rule applied: newer observations replace outdated ones (preferences evolve)
  - The identity document does not contain contradictory entries about React component style
  - Specificity is maintained: "Prefers functional components over class components in React" not "User has React preferences"
- **passing_grade:** 4/5 assertions must pass
