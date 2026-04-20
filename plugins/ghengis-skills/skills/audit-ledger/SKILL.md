---
name: audit-ledger
description: Use when building autonomous workflows that need accountability -- provides an immutable hash-chained audit trail pattern for tracking what agents did, when, and why, with tamper detection
---

# Audit Ledger

Immutable, hash-chained audit trail for agent workflows. Every significant action gets a ticket. Each entry includes the hash of the previous entry, creating a tamper-proof chain. If anyone modifies or deletes an entry, the chain breaks and verification detects it.

This is an accountability methodology, not a library. Apply it by maintaining structured log files alongside your work in Claude Code sessions, multi-agent workflows, or any autonomous pipeline where you need to answer: what happened, who did it, and why.

## When to Record

Record every action that changes state or has external consequences:

- **Tool calls** -- file writes, API calls, shell commands, deployments
- **Decisions** -- routing choices, model selections, delegation to subagents
- **State changes** -- configuration updates, permission grants, mode transitions
- **Completions** -- task finished, goal reached, deliverable produced
- **Failures** -- errors, timeouts, rejected outputs, retries that succeeded

## When NOT to Record

Skip entries for internal processing noise that does not affect outcomes:

- Intermediate reasoning steps (chain-of-thought)
- Retries that are transparent to the caller (record the final result only)
- Internal variable assignments or prompt construction
- Read-only operations with no side effects (file reads, searches)
- Heartbeat/keepalive signals with no payload

**Rule of thumb:** If you would want to know about it during a post-mortem, record it. If it is implementation plumbing, skip it.

## The Hash-Chain Pattern

Every entry includes `prev_hash` -- the SHA-256 hash of the previous entry. This creates an append-only chain where modifying or removing any entry breaks all subsequent hashes.

```
Entry 1:  prev_hash = "0000...0000" (genesis)  -->  hash(entry1) = "a1b2..."
Entry 2:  prev_hash = "a1b2..."                 -->  hash(entry2) = "c3d4..."
Entry 3:  prev_hash = "c3d4..."                 -->  hash(entry3) = "e5f6..."
```

If Entry 2 is modified after the fact, its hash changes, which means Entry 3's `prev_hash` no longer matches -- the chain is broken. Verification walks the chain and detects the first break point.

### Computing the Hash

Hash the full JSON representation of each entry with deterministic key ordering:

```
hash = SHA-256(JSON.stringify(entry, sorted_keys=true))
```

The genesis entry (first entry in the ledger) uses a prev_hash of 64 zeros: `"0000000000000000000000000000000000000000000000000000000000000000"`.

## Entry Format

Each ledger entry is a single JSON object with these fields:

```jsonl
{
  "ticket_id": "uuid-v4",
  "prev_hash": "sha256-of-previous-entry",
  "timestamp": "2026-04-07T14:32:01.123Z",
  "chain_id": "session-or-workflow-id",
  "goal_id": "optional-goal-or-task-id",
  "agent_name": "builder",
  "action": "tool_call",
  "detail": "Wrote 47 lines to src/auth.ts implementing JWT validation",
  "tool_name": "write_file",
  "cost_usd": 0.003,
  "tokens": 1240,
  "status": "success",
  "duration_ms": 342
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticket_id` | string (UUID) | yes | Unique identifier for this entry |
| `prev_hash` | string (hex) | yes | SHA-256 hash of the previous entry (64 zeros for genesis) |
| `timestamp` | string (ISO 8601) | yes | When the action occurred, UTC |
| `chain_id` | string | yes | Groups entries by session, workflow, or conversation |
| `goal_id` | string | no | Links entry to a specific goal or task |
| `agent_name` | string | yes | Which agent or role performed the action |
| `action` | string | yes | Action type (see Action Types below) |
| `detail` | string | yes | Human-readable description, max 500 chars |
| `tool_name` | string | no | Name of tool invoked, if applicable |
| `cost_usd` | number | no | Cost of the operation in USD |
| `tokens` | integer | no | Tokens consumed by the operation |
| `status` | string | no | Outcome: success, error, partial, skipped |
| `duration_ms` | integer | no | Wall-clock duration in milliseconds |

### Action Types

| Action | Use For |
|--------|---------|
| `route` | Request routed to a department or agent |
| `tool_call` | Tool executed (file write, API call, shell command) |
| `delegate` | Work delegated to a subagent |
| `complete` | Task or goal completed |
| `fail` | Task or step failed |
| `decision` | Routing or strategy decision made |
| `state_change` | Configuration or mode transition |

## Daily Rollover

Start a new file each day. Name files by date in ISO format:

```
ledger/
  2026-04-05.jsonl
  2026-04-06.jsonl
  2026-04-07.jsonl
```

Each file contains one JSON entry per line (JSONL format). The hash chain spans across files -- the first entry of a new day references the last entry of the previous day.

## Chain Verification

Walk the chain from the beginning and verify each entry's `prev_hash` matches the computed hash of the preceding entry.

### Verification Algorithm

```
prev_hash = "0000...0000"  (64 zeros)
total = 0
valid = 0
first_break = null

for each file in sorted(ledger/*.jsonl):
    for each line in file:
        entry = parse_json(line)
        total += 1

        expected_prev = prev_hash
        if entry.prev_hash == expected_prev:
            valid += 1
        else if first_break is null:
            first_break = { file, line_number, entry_number: total }

        prev_hash = SHA-256(JSON.stringify(entry, sorted_keys=true))

result = {
    valid: first_break is null AND total > 0,
    entries_checked: total,
    valid_links: valid,
    first_break: first_break
}
```

### What Breaks Tell You

| Break Pattern | Likely Cause |
|---------------|-------------|
| Single break at entry N, rest valid | Entry N-1 was modified after the fact |
| Break at entry N, all subsequent broken | Entry N or earlier was deleted or inserted |
| Multiple scattered breaks | File was manually edited or entries were reordered |
| First entry breaks | Genesis entry was modified or prev_hash was not set to zeros |

## Querying the Ledger

The JSONL format supports grep-based querying for quick lookups. For structured queries across large ledgers, maintain a parallel index.

### By Time Range

```bash
# All entries from today
cat ledger/2026-04-07.jsonl

# Entries between specific times
grep '"timestamp":"2026-04-07T1[4-6]' ledger/2026-04-07.jsonl
```

### By Agent

```bash
grep '"agent_name":"builder"' ledger/*.jsonl
```

### By Goal

```bash
grep '"goal_id":"refactor-auth-module"' ledger/*.jsonl
```

### By Action Type

```bash
grep '"action":"fail"' ledger/*.jsonl
```

### Cost Summary

```bash
# Extract all cost values and sum them
grep -o '"cost_usd":[0-9.]*' ledger/2026-04-07.jsonl
```

For more complex queries (aggregations, joins, time-series), load the JSONL into a SQLite table or use `jq`:

```bash
# Total cost per agent today
cat ledger/2026-04-07.jsonl | jq -s 'group_by(.agent_name) | map({agent: .[0].agent_name, total_cost: (map(.cost_usd) | add)})'

# All failed actions with their details
cat ledger/2026-04-07.jsonl | jq 'select(.status == "error")'
```

## Practical Usage in Claude Code

### Starting a Session

At the beginning of a multi-step task or autonomous workflow, create a ledger file and record the genesis entry:

```jsonl
{"ticket_id":"a1b2c3d4","prev_hash":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":"2026-04-07T14:00:00Z","chain_id":"session-001","goal_id":"refactor-auth","agent_name":"orchestrator","action":"route","detail":"Starting auth module refactor -- decomposed into research, build, validate","tool_name":null,"cost_usd":0,"tokens":0,"status":"success","duration_ms":0}
```

### Recording as You Work

After each significant action, append an entry. In multi-agent cascades, each agent appends its own entries with the same `chain_id`.

### Post-Mortem

When something goes wrong, the ledger answers:
- **What happened?** -- Read entries in timestamp order
- **Who did it?** -- Filter by `agent_name`
- **Why?** -- Read the `detail` field for context
- **How much did it cost?** -- Sum `cost_usd` across entries
- **Was the trail tampered with?** -- Run chain verification

### Cost Tracking

Sum `cost_usd` and `tokens` across entries to understand where budget went:

```
Total session cost:  $0.47
  researcher:        $0.12 (25%)
  builder:           $0.28 (60%)
  validator:         $0.07 (15%)
```

## Integration with Other Patterns

| Pattern | How It Uses the Ledger |
|---------|----------------------|
| **OORT Cascade** | Each role appends entries; validator checks the chain before accepting |
| **Compute Adaptation** | Tier changes are recorded as `state_change` entries |
| **Constitutional AI** | Violations are recorded with `action: "fail"` and the rule ID in detail |
| **Goal Tracking** | Goals reference `goal_id`; completion entries mark goal resolution |
| **Deep Research** | Each research phase appends entries; iteration count tracked via chain |

## Anti-Patterns

| If you notice... | The problem is... | Fix it by... |
|-----------------|-------------------|-------------|
| Hundreds of entries per minute | Recording too granularly | Only recording state-changing actions |
| All entries have `cost_usd: 0` | Not tracking costs | Estimating cost from token counts and model tier |
| `detail` field is always the same template | Not providing useful context | Writing specific descriptions of what changed and why |
| No `fail` entries in a long session | Not recording failures | Recording errors, timeouts, and retries |
| Chain verification never runs | Ledger exists but is not trusted | Running verification at session end or before audits |
| Entries have no `goal_id` | Cannot trace actions to objectives | Assigning goal IDs when goals are created |

## Chain Integration

This skill participates in `skill-chain-supervisor` chains via the shared scratchpad at `~/.claude/ghengis-chain-context.json`.

**Role in chain:** Final recorder. Runs last, persists the full chain outcome.

**Scratchpad subkey (namespaced writes):** `audit_ledger.*`

**Reads (input scratchpad keys):**
- `entire scratchpad`

**Writes (output scratchpad keys):**
- `audit_ledger.entry_id` — UUID of the ledger entry appended
- `audit_ledger.hash` — SHA-256 of the entry (for chain integrity)
- `audit_ledger.prev_hash` — hash of previous ledger entry (hash chain)

**Success criteria:** append succeeds and returns non-empty entry_id + hash

When invoked as part of a chain, this skill MUST:
1. Read prior scratchpad state before starting
2. Write outputs to the `audit_ledger.*` namespace only — never overwrite another skill's subkey
3. Report failure via its own subkey (e.g. `audit_ledger.error`) rather than raising

When invoked standalone (not in a chain), scratchpad writes are optional but recommended for auditability.
