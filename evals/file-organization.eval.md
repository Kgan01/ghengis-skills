# File Organization -- Evaluation

## TC-1: Happy Path -- Manifest Type Detection and Project Discovery
- **prompt:** "Scan my ~/code directory and tell me what projects are in there. I see package.json, pyproject.toml, Cargo.toml, and go.mod files scattered around."
- **context:** Tests project auto-discovery using the 18 manifest types. Must correctly identify project roots, skip build artifact directories, and stop descending into discovered project subdirectories.
- **assertions:**
  - Identifies each manifest file and maps it to the correct project type (node, python, rust, go)
  - Skips directories like node_modules, __pycache__, target, build, dist, .git, venv during scanning
  - Reports collected information per project: path, name, project_type, manifest_file
  - Does not descend into a discovered project's subdirectories to avoid false matches in nested dependencies
  - Limits scan depth to 5 levels by default as specified in the skill
- **passing_grade:** 4/5 assertions must pass

## TC-2: Happy Path -- File Naming Convention Enforcement
- **prompt:** "I have these files that need renaming: 'My Final Report (v3) - Copy.pdf', 'Meeting Notes Jan 2024.docx', 'project_proposal.MD', 'CLIENT-INVOICE-042.xlsx'. Apply your naming conventions."
- **context:** Tests naming convention rules: lowercase with hyphens, no spaces, date-prefixed when temporal, descriptive names, consistent extensions.
- **assertions:**
  - Renames to lowercase with hyphens: no spaces, no uppercase, no special characters like parentheses
  - Date-prefixes the meeting notes file (temporal content) with YYYY-MM-DD or YYYY-MM format
  - Date-prefixes the invoice (financial document with temporal relevance)
  - Does NOT date-prefix the project proposal (reusable document, not time-series)
  - Removes version suffixes and "Copy" indicators, preferring a single source of truth
- **passing_grade:** 4/5 assertions must pass

## TC-3: Quality Check -- Audit Trail on File Moves
- **prompt:** "Move contract-draft.docx from my Downloads folder to the Acme Corp contracts directory, and move the meeting-notes.md to their communications folder."
- **context:** Tests the safe file move procedure and audit trail logging. Every move must be logged with source, destination, timestamp, and metadata.
- **assertions:**
  - Verifies source files exist before moving (step 1 of safe file move)
  - Resolves to absolute paths, not relative paths
  - Checks that destination does not already exist (refuses to overwrite)
  - Logs each move as an audit entry in JSONL format with id, action (move), src, dst, client_id, timestamp, and metadata including reason
  - Creates parent directories as needed before the move
- **passing_grade:** 4/5 assertions must pass

## TC-4: Edge Case -- Cleanup Patterns for Duplicates and Orphans
- **prompt:** "Clean up my project directory. I see report-v1.pdf, report-v2.pdf, report-v3.pdf, report-final.pdf, report-final-final.pdf. Also there are .DS_Store files everywhere, a few .tmp and .bak files, and a 'budget (1).xlsx' that looks like an accidental duplicate."
- **context:** Tests duplicate identification, orphan file detection, version cleanup, and OS metadata removal. Tests multiple cleanup patterns simultaneously.
- **assertions:**
  - Identifies report-v1.pdf through report-final-final.pdf as a versioning problem and recommends keeping only the latest
  - Flags .DS_Store as OS metadata files to remove
  - Flags .tmp and .bak files as temporary/backup orphans to remove
  - Identifies "budget (1).xlsx" as an accidental duplicate (matches the `* (1).*` orphan pattern)
  - Recommends moving older versions to archive/ with date prefix rather than immediate deletion
- **passing_grade:** 4/5 assertions must pass

## TC-5: Happy Path -- Intelligent File Categorization
- **prompt:** "I have a pile of unsorted files: nda-signed-acme.pdf, weekly-standup-notes.md, q2-revenue-report.xlsx, auth-middleware.py, client-meeting-recording.mp3. Sort these into the canonical client folder structure."
- **context:** Tests heuristic classification rules with confidence scoring. Files should be categorized into projects/, contracts/, deliverables/, or communications/ based on keyword matching.
- **assertions:**
  - Categorizes nda-signed-acme.pdf into contracts/ (keyword "nda" matches contract pattern, confidence 0.7)
  - Categorizes weekly-standup-notes.md into communications/ (keyword "notes" and "meeting" match communication pattern)
  - Categorizes q2-revenue-report.xlsx into deliverables/ (keyword "report" and .xlsx extension match deliverable pattern)
  - Categorizes auth-middleware.py into projects/ (source code, default fallback at confidence 0.4)
  - Categorizes client-meeting-recording.mp3 into communications/ (keyword "meeting" matches communication pattern)
- **passing_grade:** 4/5 assertions must pass
