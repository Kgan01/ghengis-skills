# Incident & Postmortem Context

Not a separate source, a **cross-cutting angle**. Incidents often motivate defensive code ("we added this check after the X outage"). If the target looks defensive (null checks, retry logic, timeout handling, rate limiting, feature flags, egress guards, OOM handlers), each investigator hunts for incident history **inside its own source**:

- **Git / `gh`**: messages like "fix for", "hotfix", "add defensive check", "revert" followed by "re-apply with…"; same-day merges; PRs labelled bug/incident.
- **Task tracker**: `docs/TODO.md` entries that name an outage, a "caught a production bug" note, or a "security hardening" item; `gh issue` with incident/bug labels.
- **Project docs**: `.claude/docs/current-status.md` and CHANGELOG lines like "build-validate caught…", "real-world stress test caught N production bugs"; `docs/plans/` written right after a failure; any postmortem doc.
- **Agent memory**: dated memory lines like "fixed week-long silent failure", "DISABLED after it closed all windows"; brain memories tagged with a failure.
- **Gmail / Drive** (if connected): vendor or client messages reporting a failure around the anchor date.
- **Runtime MCPs** (if connected): error issues whose first-seen / last-seen window brackets the ship date; log spikes before the change and their drop after.

If you find an incident reference, fetch the full record. Postmortem-style notes often list action items that map directly to code changes. When several sources corroborate (a memory line names the failure, a TODO item tracks the fix, the PR links the TODO, and the error count drops after the release), the evidence is especially strong.

Worth the time when the code's defensive character makes an incident-driven origin plausible. Skip it for code that doesn't look defensive.
