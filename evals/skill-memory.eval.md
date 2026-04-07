# Skill Memory -- Evaluation

## TC-1: Records Lesson in Proper Format After Non-Trivial Task
- **prompt:** "That asyncio.gather issue cost us an hour -- it was swallowing exceptions silently"
- **context:** Agent just finished debugging a complex async issue where `asyncio.gather` was hiding exceptions. The fix was to use `return_exceptions=True`.
- **assertions:**
  - Entry is written with a timestamp header in `### YYYY-MM-DD HH:MM` format
  - Tag prefix is present and correct: `[python/async]`
  - Entry is a single line starting with `- `
  - Language is actionable: "Use return_exceptions=True with asyncio.gather to surface exceptions" not "We found a bug in our code"
  - Write trigger checklist passes: this would save 10+ minutes if encountered again AND required debugging to discover
- **passing_grade:** 4/5 assertions must pass

## TC-2: Skips Recording for Routine Operations
- **prompt:** "Read the config file and tell me what port the server runs on"
- **context:** Agent reads a YAML config file and reports the port number. Standard lookup, no debugging, no surprises.
- **assertions:**
  - No skill memory entry is written
  - Write trigger checklist fails: would NOT save 10+ minutes, IS in standard documentation, did NOT require multiple attempts
  - The task is classified as "routine operation that went smoothly"
  - No modification to any skill memory file
- **passing_grade:** 3/4 assertions must pass

## TC-3: Uses Correct Tag Taxonomy
- **prompt:** "We discovered that Docker multi-stage builds with --target cut our Python image size by 60%"
- **context:** Agent completed a Docker optimization task. The finding is transferable and non-obvious.
- **assertions:**
  - Tag uses two-level format: `[docker/build]` (domain/topic)
  - Tag is NOT single-level like `[docker]` or three-level like `[docker/build/multistage]`
  - Entry content focuses on the actionable pattern: "Use multi-stage builds with --target to reduce Python image size"
  - Entry is placed under the current timestamp section, not under Consolidated Learnings
- **passing_grade:** 3/4 assertions must pass

## TC-4: Consolidates When File Exceeds Size Threshold
- **prompt:** "The skill memory file is getting large -- clean it up"
- **context:** Skill memory file is 55KB (above the 50KB threshold). Contains entries spanning 6 months. Some entries are 85%+ similar to each other.
- **assertions:**
  - Summarization triggers (file exceeds 50KB)
  - 5 most recent timestamp sections are kept verbatim
  - All older sections are summarized into 5-10 key bullet points under "Consolidated Learnings (auto-summarized)"
  - Duplicate entries (85%+ similarity) are deduplicated -- only the more recent version is kept
  - The resulting file is significantly smaller than 50KB
- **passing_grade:** 4/5 assertions must pass

## TC-5: Handles Cross-Domain Search Correctly
- **prompt:** "Have we seen any async event loop issues before?"
- **context:** Multiple skill memory files exist: `python.md`, `fastapi.md`, `typescript.md`. The `python.md` file contains entries tagged `[python/async]` about event loop issues. The `fastapi.md` file also has a `[fastapi/deps]` entry mentioning event loop behavior.
- **assertions:**
  - Search finds entries in `python.md` matching `[python/async]` or `event.loop`
  - Search also finds the `fastapi.md` entry mentioning event loop
  - Search priority is correct: current project first, related domain second, all files last
  - Results include entries from both files, ranked by relevance
  - Grepable format enables the search without any vector database or embedding infrastructure
- **passing_grade:** 4/5 assertions must pass
