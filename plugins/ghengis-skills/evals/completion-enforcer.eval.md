# Completion Enforcer -- Evaluation

## TC-1: Catches Placeholder Code
- **prompt:** "Write a Python class that handles JWT token validation with refresh logic"
- **context:** Agent returns a class with `pass` bodies, `# TODO: implement` comments, and `raise NotImplementedError` in three methods
- **assertions:**
  - Check 3 (incompleteness signal phrases) fires on `pass`, `# TODO`, and `NotImplementedError`
  - Check 5 (missing expected deliverables) does NOT fire because code structure is present
  - Verdict is PARTIAL, not COMPLETED
  - Recovery action instructs the agent to fill in all placeholder method bodies
- **passing_grade:** 3/4 assertions must pass

## TC-2: Catches Premature Completion With Short Output
- **prompt:** "Create a comprehensive deployment guide for our FastAPI app covering Docker, CI/CD, and monitoring"
- **context:** Agent returns a 60-character response: "I've set up the basic deployment configuration for you."
- **assertions:**
  - Check 2 (output length vs instruction complexity) fires -- instruction contains "create", "guide", "covering" and is 40+ words equivalent in complexity, output is under 100 characters
  - The Summarizer red flag pattern is identified -- agent described what it did instead of producing the deliverable
  - Confidence score is 0.60 or lower (2+ checks failed)
  - Auto-continue is NOT recommended
- **passing_grade:** 3/4 assertions must pass

## TC-3: Passes Genuinely Complete Work
- **prompt:** "Write a utility function that converts Celsius to Fahrenheit"
- **context:** Agent returns a 15-line Python function with type hints, docstring, and two usage examples. No placeholders, no TODOs, no error phrases. Output is 400 characters.
- **assertions:**
  - No incompleteness signal phrases are detected
  - Output length is proportional to instruction complexity (simple instruction, moderate output)
  - No failure masking phrases detected
  - Verdict is COMPLETED with confidence >= 0.80
  - Zero checks fail
- **passing_grade:** 4/5 assertions must pass

## TC-4: Detects Failure Masking
- **prompt:** "Connect to the PostgreSQL database and run the migration script"
- **context:** Agent returns a 120-character response: "Migration completed successfully. Error occurred during table creation but the process continued."
- **assertions:**
  - Check 4 (failure masking) fires on "error occurred" in a response under 300 characters
  - Check 2 (output length vs instruction complexity) fires -- short output for a task involving "connect" and "run"
  - Recovery action instructs the agent to acknowledge the failure and retry or explain why the table creation failed
  - Verdict is PARTIAL with 2+ checks failed
- **passing_grade:** 3/4 assertions must pass

## TC-5: Detects The Deferrer Pattern
- **prompt:** "Implement rate limiting middleware for our Express API"
- **context:** Agent returns: "Here's the approach for rate limiting. You'll need to install express-rate-limit, then configure it in your middleware stack. You should be able to set the window and max requests. I'll leave the exact configuration to you since it depends on your traffic patterns."
- **assertions:**
  - Check 3 fires on "you'll need to", "you should be able to", and "I'll leave that to you"
  - Check 5 (missing expected deliverables) fires -- instruction says "implement" but no code block is present in output
  - The Deferrer red flag pattern is identified -- agent handed work back to the user
  - Recovery instructs the agent to produce the actual middleware code, not describe what the user should do
  - Confidence is 0.40 or lower (3+ checks failed)
- **passing_grade:** 4/5 assertions must pass
