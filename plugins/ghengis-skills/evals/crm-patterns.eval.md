# CRM Patterns -- Evaluation

## TC-1: Happy Path -- New Client Onboarding
- **prompt:** "I just had a discovery call with Sarah Chen, CTO at NovaTech Solutions. They found us through our blog. They're interested in a React dashboard project, budget around $20k. Set them up in the CRM."
- **context:** Full onboarding flow from initial contact to lead creation. Tests client record creation, communication logging, pipeline entry, and follow-up scheduling.
- **assertions:**
  - Creates a client file with YAML frontmatter including id (slug format), name, status set to `lead`, contact_person, tags, and created_at
  - Logs the initial communication entry with channel (call), direction (inbound), summary of the discovery call, and a follow-up action
  - Adds the lead to pipeline.md under the Leads section with source, first contact date, and notes
  - Sets a follow-up reminder within 3 days (the defined threshold for leads)
  - Creates a project directory under `projects/novatech-solutions/` or equivalent slug
- **passing_grade:** 4/5 assertions must pass

## TC-2: Edge Case -- Detecting Stale Relationships
- **prompt:** "Review my active clients and tell me which relationships are going stale. Here's the situation: Acme Corp last contacted 2 days ago, Beta Labs last contacted 10 days ago (active project), Gamma Inc last contacted 4 days ago (lead stage), and Delta Corp last contacted 35 days ago (inactive)."
- **context:** Tests staleness detection against the defined thresholds: active clients stale after 7 days, leads after 3 days, inactive after 30 days. Multiple clients at different statuses.
- **assertions:**
  - Flags Beta Labs as stale (10 days > 7-day threshold for active clients)
  - Flags Gamma Inc as stale (4 days > 3-day threshold for leads)
  - Flags Delta Corp as stale (35 days > 30-day threshold for inactive clients)
  - Does NOT flag Acme Corp (2 days is within the 7-day active threshold)
  - Generates a follow-up list sorted by urgency with recommended actions per client
- **passing_grade:** 4/5 assertions must pass

## TC-3: Happy Path -- Communication Logging with Follow-Up
- **prompt:** "Log this: I had a Slack message from Marcus at Beta Labs today. He asked about the timeline for mobile app phase 2 and wants to start in July. I need to send him a revised SOW by Wednesday."
- **context:** Tests communication log entry creation with all required fields and follow-up tracking.
- **assertions:**
  - Creates a communication log entry with channel set to `slack` and direction set to `inbound`
  - Includes client_id referencing Beta Labs
  - Summary captures the substance (timeline question for phase 2, July start preference)
  - Sets a follow-up action ("Send revised SOW") with a specific follow-up date (Wednesday)
  - Entry follows the documented format with timestamp and unique id
- **passing_grade:** 4/5 assertions must pass

## TC-4: Quality Check -- Pipeline Revenue Tracking
- **prompt:** "Give me a pipeline overview. Active: Acme Corp dashboard at $12k budget with $6k billed, Beta Labs mobile app at $18k with $12k billed. Proposal: Gamma Inc e-commerce rebuild at $25k, sent 15 days ago. One lead: Delta Corp, cold email about React migration last week."
- **context:** Tests pipeline view generation with leads, proposals, active work, and revenue tracking. Also tests the 14-day proposal follow-up threshold.
- **assertions:**
  - Generates a structured pipeline view with separate sections for Leads, Proposals, Active Work
  - Shows accurate revenue data: total billed ($18k), total paid figures, outstanding amounts
  - Flags the Gamma Inc proposal as overdue for follow-up (15 days > 14-day threshold)
  - Includes budget progress for active projects (e.g., 50% for Acme Corp)
  - Revenue summary table totals are arithmetically correct
- **passing_grade:** 4/5 assertions must pass

## TC-5: Edge Case -- Relationship Health Score Red Flags
- **prompt:** "Assess the health of my relationship with Acme Corp. Details: last communication was 16 days ago, they have an active dashboard project, all 5 recent communications were outbound (I contacted them every time), they have $3,500 outstanding for over 35 days, and the API redesign project has been on_hold with no follow-up scheduled."
- **context:** Tests the relationship health heuristic with multiple simultaneous red flags as defined in the skill.
- **assertions:**
  - Flags "No communication in 14+ days with active project" red flag (16 days)
  - Flags "All communication is outbound" red flag (one-directional relationship)
  - Flags "Outstanding payment > 30 days" red flag ($3,500 at 35 days)
  - Flags "Project on_hold with no follow-up scheduled" red flag (API redesign)
  - Provides specific recommended actions for each red flag, not just identification
- **passing_grade:** 4/5 assertions must pass
