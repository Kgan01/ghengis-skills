# Audit Ledger -- Evaluation

## TC-1: Uses Hash Chaining Correctly
- **prompt:** "Start a new audit trail for the auth refactor project"
- **context:** Fresh session, no existing ledger. Agent creates the genesis entry and two subsequent entries.
- **assertions:**
  - Genesis entry has `prev_hash` set to 64 zeros (`"0000000000000000000000000000000000000000000000000000000000000000"`)
  - Entry 2 has `prev_hash` equal to SHA-256 of the full JSON of Entry 1 (deterministic key ordering)
  - Entry 3 has `prev_hash` equal to SHA-256 of the full JSON of Entry 2
  - All required fields are present: ticket_id, prev_hash, timestamp, chain_id, agent_name, action, detail
  - Hash is computed using `SHA-256(JSON.stringify(entry, sorted_keys=true))`
- **passing_grade:** 4/5 assertions must pass

## TC-2: Records the Right Actions, Skips Noise
- **prompt:** "Refactor the auth module -- read the existing code, plan the approach, write new files, run tests"
- **context:** Agent performs: (1) reads 3 files, (2) reasons about approach, (3) writes 2 new files, (4) runs test command, (5) test fails, (6) fixes and retries, (7) tests pass.
- **assertions:**
  - File reads (step 1) are NOT recorded (read-only operations with no side effects)
  - Internal reasoning (step 2) is NOT recorded (intermediate reasoning steps)
  - File writes (step 3) ARE recorded with action `tool_call` and tool_name
  - Test execution (step 4) IS recorded with action `tool_call`
  - Test failure (step 5) IS recorded with action `fail` and error context in detail
  - The transparent retry (step 6 fix) is recorded as its own entry -- the final success (step 7) IS recorded
  - At most 4-5 entries are created, not 7 (noise filtered)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Supports Chain Verification and Tamper Detection
- **prompt:** "Verify the audit trail integrity for today's session"
- **context:** Ledger file has 10 entries. Entry 5 was manually edited after creation (simulating tampering). Entries 1-4 are intact. Entries 6-10 were appended normally after the tamper.
- **assertions:**
  - Verification walks the chain from genesis forward
  - First break is detected at Entry 6 (its prev_hash no longer matches the hash of tampered Entry 5)
  - Entries 1-4 are reported as valid
  - Entry 5's modification is identified as the root cause
  - Verification result includes: `valid: false`, `entries_checked: 10`, `valid_links: 5`, `first_break: {entry 6}`
- **passing_grade:** 4/5 assertions must pass

## TC-4: Handles Daily Rollover With Cross-File Chain
- **prompt:** "Continue work from yesterday's session"
- **context:** Yesterday's ledger file `2026-04-06.jsonl` has 8 entries. Today's file `2026-04-07.jsonl` needs to start. The last entry in yesterday's file has a known hash.
- **assertions:**
  - Today's first entry has `prev_hash` matching the SHA-256 hash of yesterday's last entry
  - The chain spans across files -- no break at the file boundary
  - New file is named in ISO date format: `2026-04-07.jsonl`
  - JSONL format is used -- one JSON object per line
  - Verification across both files reports a continuous valid chain
- **passing_grade:** 4/5 assertions must pass

## TC-5: Records Meaningful Detail, Not Templates
- **prompt:** "Deploy the API to staging, then update the database schema"
- **context:** Agent performs a deployment and a migration. Both succeed.
- **assertions:**
  - Deployment entry `detail` field is specific: "Deployed auth-api v2.3 to staging via Docker Compose" not "Task completed"
  - Migration entry `detail` field is specific: "Applied migration 003_add_refresh_tokens adding refresh_tokens table" not "Database updated"
  - Both entries have `status: "success"`
  - Both entries include `duration_ms` (wall-clock time tracked)
  - The anti-pattern of identical template detail text is avoided
- **passing_grade:** 4/5 assertions must pass
