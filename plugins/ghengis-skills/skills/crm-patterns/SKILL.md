---
name: crm-patterns
description: Use when managing client relationships, freelance projects, or any work involving multiple clients — covers client tracking, project lifecycle, communication logging, pipeline management, and relationship health
allowed-tools: Read Write Edit Glob
---

# CRM Patterns

## When to Use
When managing client relationships, tracking freelance or consulting projects, logging communications, monitoring pipeline health, generating client summaries, or organizing any multi-client workflow. Applies to freelancing, consulting, agency work, and any scenario where you juggle multiple clients and projects simultaneously.

## Core Data Models

### Client Record

Every client gets a structured record. Store as a markdown file or YAML frontmatter document in a `clients/` directory.

**Required Fields**
```yaml
id: acme-corp              # Slug, unique identifier
name: Acme Corp
status: active             # lead | active | inactive | archived
created_at: 2024-03-15
updated_at: 2024-06-01
```

**Recommended Fields**
```yaml
email: hello@acme.com
phone: +1-555-0100
company: Acme Corporation
contact_person: Jane Smith
tags: [saas, react, recurring]
notes: |
  Referred by Dave. Prefers async communication.
  Decision-maker is CTO (Jane).
```

**Client Statuses**
| Status | Meaning |
|--------|---------|
| `lead` | Initial contact, no commitment yet |
| `active` | Ongoing work or active contract |
| `inactive` | Paused or between projects |
| `archived` | Relationship ended, soft-deleted |

### Project Record

Projects are always tied to a client. Store alongside or nested under the client.

```yaml
id: acme-dashboard
client_id: acme-corp
name: Analytics Dashboard
description: Real-time analytics dashboard with D3 visualizations
status: active              # planning | active | completed | on_hold
hourly_rate: 150.00
budget: 12000.00
started_at: 2024-04-01
created_at: 2024-04-01
updated_at: 2024-06-01
```

**Project Statuses & Lifecycle**
```
lead --> proposal --> planning --> active --> completed
                        |                       |
                        +---> on_hold           +---> archived
                        |
                        +---> cancelled
```

| Stage | What Happens |
|-------|-------------|
| `planning` | Scoping, proposal writing, contract negotiation |
| `active` | Work in progress, deliverables being produced |
| `completed` | All deliverables shipped, awaiting final payment |
| `on_hold` | Paused by client or mutual agreement |

### Communication Log

Every interaction with a client gets logged. This is the heartbeat of relationship health.

```yaml
id: comm-20240601-001
client_id: acme-corp
channel: email               # email | call | meeting | slack | sms
direction: outbound           # inbound | outbound
summary: Sent weekly progress update with dashboard screenshots
timestamp: 2024-06-01T14:30:00Z
follow_up: Schedule demo for Friday
```

**Valid Channels**: email, call, meeting, slack, sms
**Valid Directions**: inbound (they contacted you), outbound (you contacted them)

## File-Based CRM Structure

For Claude Code projects, use a markdown/YAML file-based approach rather than a database.

```
crm/
  clients/
    acme-corp.md              # Client record + notes
    beta-labs.md
    gamma-inc.md
  projects/
    acme-corp/
      analytics-dashboard.md  # Project details + deliverables
      api-redesign.md
    beta-labs/
      mobile-app.md
  comms/
    2024-06.md                # Monthly communication log (append-only)
    2024-05.md
  pipeline.md                 # Pipeline overview / active deals
  README.md                   # CRM conventions and field definitions
```

### Client File Template

```markdown
---
id: acme-corp
name: Acme Corp
email: hello@acme.com
phone: +1-555-0100
company: Acme Corporation
contact_person: Jane Smith (CTO)
status: active
tags: [saas, react, recurring]
created_at: 2024-03-15
updated_at: 2024-06-01
---

# Acme Corp

## Notes
- Referred by Dave from TechMeetup
- Prefers async communication (Slack + email)
- Decision-maker: Jane Smith (CTO)
- Budget cycle: quarterly approvals

## Active Projects
- [Analytics Dashboard](../projects/acme-corp/analytics-dashboard.md) — active
- [API Redesign](../projects/acme-corp/api-redesign.md) — planning

## Key Dates
- 2024-03-15: Initial contact (inbound via website)
- 2024-04-01: Dashboard project kicked off
- 2024-05-15: Proposal sent for API redesign
```

### Communication Log Entry Format

```markdown
## 2024-06-01

### [OUTBOUND] Email to Jane @ Acme Corp
- **Channel**: email
- **Summary**: Sent weekly progress update with dashboard screenshots. Milestone 2 of 4 complete.
- **Follow-up**: Schedule demo for Friday

### [INBOUND] Slack from Marcus @ Beta Labs
- **Channel**: slack
- **Summary**: Asked about timeline for mobile app phase 2. Wants to start July.
- **Follow-up**: Send revised SOW by Wednesday
```

## Pipeline Management

### Pipeline View

Track all opportunities from lead to close.

```markdown
# Pipeline — June 2024

## Leads (not yet proposed)
| Client | Source | First Contact | Notes |
|--------|--------|--------------|-------|
| Delta Corp | Cold email | 2024-05-28 | Interested in React migration |

## Proposals (sent, awaiting response)
| Client | Project | Amount | Sent | Follow-up |
|--------|---------|--------|------|-----------|
| Gamma Inc | E-commerce Rebuild | $25,000 | 2024-05-20 | Follow up June 3 |

## Active Work
| Client | Project | Budget | Billed | Status |
|--------|---------|--------|--------|--------|
| Acme Corp | Dashboard | $12,000 | $6,000 | 50% milestone 2/4 |
| Beta Labs | Mobile App | $18,000 | $12,000 | Phase 1 complete |

## Completed (pending final payment)
| Client | Project | Total | Paid | Due |
|--------|---------|-------|------|-----|
| — | — | — | — | — |
```

### Revenue Tracking

Per-client P&L summary:

```markdown
# Revenue Summary — Q2 2024

| Client | Projects | Billed | Paid | Outstanding |
|--------|----------|--------|------|-------------|
| Acme Corp | 1 active | $6,000 | $4,500 | $1,500 |
| Beta Labs | 1 active | $12,000 | $12,000 | $0 |
| **Total** | **2** | **$18,000** | **$16,500** | **$1,500** |
```

## Relationship Health

### Staleness Detection

A relationship is going stale when there has been no communication logged for a defined period.

**Thresholds**
| Client Status | Stale After | Action |
|---------------|-------------|--------|
| active | 7 days | Send check-in or progress update |
| lead | 3 days | Follow up on initial contact |
| inactive | 30 days | Consider re-engagement or archive |

**How to Check**
1. Look at the latest communication timestamp for each client
2. Compare against today's date
3. Flag clients exceeding the threshold
4. Generate a follow-up list sorted by urgency

### Follow-Up Reminders

When logging a communication, always capture the next action:
```yaml
follow_up: Schedule demo for Friday
follow_up_date: 2024-06-07
```

Review follow-ups daily. A CRM without follow-up tracking is just an address book.

### Relationship Health Score (Heuristic)

```
Score = weighted sum of:
  - Days since last communication (lower is better)
  - Communication frequency (higher is better)
  - Direction balance (mix of inbound + outbound is best)
  - Active project count (more = stronger relationship)
  - Outstanding payments (fewer = healthier)

Red flags:
  - No communication in 14+ days with active project
  - All communication is outbound (they never reach out)
  - Outstanding payment > 30 days
  - Project on_hold with no follow-up scheduled
```

## Search and Retrieval

### Finding Clients

**By status**: List all clients with `status: active`
**By tag**: Find all clients tagged with `react` or `saas`
**By name/company**: Search client files for name or company match
**By project**: Find which client owns a specific project
**By communication**: Search communication logs for a keyword

### Client Summary Generation

When asked for a client overview, assemble:
1. Client record (contact info, status, tags)
2. All associated projects (with status and budget)
3. Recent communications (last 10 entries)
4. Financial summary (total billed, total paid, outstanding)
5. Relationship health (staleness, follow-ups due)

```markdown
# Client Summary: Acme Corp

**Status**: Active | **Since**: 2024-03-15 | **Contact**: Jane Smith (CTO)
**Tags**: saas, react, recurring

## Projects (2)
- Analytics Dashboard — active ($6,000 / $12,000 billed)
- API Redesign — planning ($0 / $8,000 budget)

## Recent Communications
- 2024-06-01: [OUT] Email — Weekly progress update
- 2024-05-28: [IN] Slack — Jane asked about API timeline
- 2024-05-25: [OUT] Meeting — Sprint review demo

## Financials
- Total Billed: $6,000
- Total Paid: $4,500
- Outstanding: $1,500

## Health
- Last contact: 1 day ago (healthy)
- Follow-up: Schedule demo for Friday (2024-06-07)
- Direction balance: 2 outbound, 1 inbound (acceptable)
```

## Procedures

### Onboarding a New Client
```
1. Create client file in clients/ with all known info
2. Set status to "lead"
3. Log initial communication (how they found you, first contact)
4. Add tags for industry, tech stack, relationship type
5. Create project directory under projects/{client-id}/
6. Draft proposal or SOW
7. Update pipeline.md with the new lead
8. Set follow-up reminder (3 days for leads)
```

### Transitioning Lead to Active
```
1. Update client status: lead -> active
2. Create project file with budget, rate, scope
3. Update pipeline.md (move from Leads to Active)
4. Log communication: contract signed / project kicked off
5. Set up recurring check-in cadence (weekly for active projects)
```

### Closing a Project
```
1. Update project status: active -> completed
2. Log final communication (delivery confirmation)
3. Update pipeline.md (move to Completed)
4. Generate final invoice (if applicable)
5. Request testimonial or referral (7 days after delivery)
6. If no more projects: update client status to inactive
7. Set 30-day re-engagement reminder
```

### Monthly CRM Review
```
1. Check all active clients for staleness (> 7 days no contact)
2. Review pipeline: any proposals > 14 days without response?
3. Check outstanding payments (any > 30 days?)
4. Update revenue summary
5. Archive any dead leads (> 60 days, no response)
6. Review follow-up list (anything overdue?)
```

## Common Pitfalls

### Not Logging Communications
- **Symptom**: "When did I last talk to them?"
- **Impact**: Relationships go stale without noticing, follow-ups missed
- **Fix**: Log every interaction immediately, even brief ones

### No Follow-Up Tracking
- **Symptom**: Proposals sent into the void, no reminder to check back
- **Impact**: Lost revenue, client thinks you forgot about them
- **Fix**: Every communication entry must include a follow-up action and date

### Mixing Personal Notes with Client Data
- **Symptom**: Client file is a dumping ground of unstructured text
- **Impact**: Hard to extract actionable info, can't generate summaries
- **Fix**: Use structured fields (YAML frontmatter) for data, free-text notes section for context

### Ignoring Inactive Clients
- **Symptom**: Client marked inactive and forgotten
- **Impact**: Lost repeat business, they hire someone else
- **Fix**: Set 30-day re-engagement reminders for inactive clients, quarterly review of all inactive

### No Revenue Tracking
- **Symptom**: "Am I making money on this client?"
- **Impact**: Underpricing, scope creep goes unnoticed, unprofitable relationships continue
- **Fix**: Track budget, billed, and paid per project; generate P&L per client monthly

## Checklists

### New Client Onboarding
- [ ] Create client file with contact info and tags
- [ ] Set status to `lead`
- [ ] Log initial communication with source/channel
- [ ] Create project directory
- [ ] Add to pipeline.md
- [ ] Set 3-day follow-up reminder

### Weekly CRM Maintenance
- [ ] Log all communications from the past week
- [ ] Check for stale relationships (active clients > 7 days)
- [ ] Review follow-up list (anything overdue?)
- [ ] Update project statuses if changed
- [ ] Send any overdue progress updates

### Monthly Review
- [ ] Review full pipeline (leads, proposals, active, completed)
- [ ] Update revenue summary
- [ ] Check outstanding payments (flag > 30 days)
- [ ] Archive dead leads (> 60 days no response)
- [ ] Re-engage inactive clients (send check-in)
- [ ] Generate client summaries for active clients

### Project Kickoff
- [ ] Client record exists and is up to date
- [ ] Project file created with scope, budget, rate, timeline
- [ ] Contract or SOW signed and filed
- [ ] Pipeline updated (moved to Active)
- [ ] Communication cadence established (weekly check-in)
- [ ] First communication logged (kickoff meeting/email)
