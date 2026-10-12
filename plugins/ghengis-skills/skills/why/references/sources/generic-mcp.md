# Any Other Connected MCP (chat, observability, errors, deploy logs, warehouse)

Use this playbook when discovery finds an MCP that fits category 6 (conversation record: Slack, Discord, Teams) or category 7 (runtime evidence: observability, error tracking, deploy/runtime logs such as Vercel, database or warehouse such as Supabase). It condenses the upstream pstack playbooks for Slack, Datadog, Sentry, and Databricks into one adaptable recipe. Do not assume any of these exist. The probe decides.

## Probe

1. Find the server's tools in the tool list (Claude Code: `mcp__<server>__*`; load deferred tools first). Read the server instructions and tool schemas before calling anything.
2. Call one cheap read tool (list projects / orgs / channels). Auth failure → stop, report the gap. Never invent findings.
3. Use **read-only** tools only. No writes, no posts, no config changes, no reruns.

## What each kind uniquely surfaces

| Kind | The "why" it holds |
|---|---|
| Team chat | Real-time deliberation that never reached a doc. Incident channels. |
| Observability / logs | The infra reality the code reacts to: timeouts, latency, rate limits, saturation |
| Error tracking | The exceptions whose first-seen / last-seen windows bracket a defensive change |
| Deploy logs | Which release shipped the change, and what broke around it |
| Warehouse / database | The data reality behind a threshold, flag, or migration ("where did 100 come from") |

## How to search

1. **Anchor on time.** The anchor commit and PR merge dates define the window. Look before (what motivated it) and after (did the signal change).
2. **Anchor on terms.** Symbol names, error strings the target handles, endpoint paths, the threshold value.
3. **Temporal correlation is the strongest signal.** "Error X peaked at N/day, first seen D1, stopped after the release on D2 that shipped the guard." Report the numbers and timestamps, not adjectives.
4. **Chat: fetch whole threads.** A single message out of context misleads. Author-bounded search (PR author around the merge date) and PR-URL search hit most often.
5. **Warehouse: read-only queries, bounded windows.** Report fully-qualified table names, the query, and the numeric summary. Never run a write or an unbounded scan.

## Common pitfalls

- **Retention cliffs.** Logs, errors, and chat expire. Report the earliest date the source reached.
- **Correlation is not cause.** A metric change after a deploy is circumstantial. Classify it as such.
- **Casual chat as decision.** "lol just ship it" is not a considered decision.
- **Noisy dashboards.** Name the exact metric, filter, and window, or the finding can't be checked.

## What to return

Server and tool names used; exact queries and windows; verbatim quotes or numeric summaries with timestamps; permalinks or IDs; whether each item is direct or circumstantial.
