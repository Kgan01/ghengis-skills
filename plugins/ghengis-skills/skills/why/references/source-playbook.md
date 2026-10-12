# Source playbooks

The why skill dispatches one investigator per **reachable** evidence category. Each investigator reads the single playbook for its category. Run the probe first; a failed probe means the category is a gap, recorded in Sources Consulted.

| # | Category | Playbook | Probe (do this before dispatch) |
|---|---|---|---|
| 1 | Source control | [`code-archaeology.md`](./sources/code-archaeology.md) | Always available (git). `gh auth status` decides whether PR bodies/reviews are reachable. |
| 2 | Task / issue tracker | [`task-tracker.md`](./sources/task-tracker.md) | `docs/TODO.md` (or any `TODO.md`) exists; `gh issue list -L 1` succeeds; a tracker MCP is in the tool list. |
| 3 | In-repo long-form docs | [`project-docs.md`](./sources/project-docs.md) | Glob `docs/**/*.md`, `.claude/docs/*.md`, `CHANGELOG.md`, `MEMORY.md`, `CONTEXT.md`, `**/adr/**`. |
| 4 | Agent memory | [`agent-memory.md`](./sources/agent-memory.md) | pi: `brain_recall` tool listed. Otherwise a JARVIS host answers `GET /brain/recall?query=ping&limit=1`. `~/.claude/projects/*/memory/` exists. |
| 5 | Cloud documents | [`google-workspace.md`](./sources/google-workspace.md) | A Drive (or other docs) MCP is in the tool list and a trivial search succeeds. |
| 6 | Conversation record | [`google-workspace.md`](./sources/google-workspace.md) for Gmail; [`generic-mcp.md`](./sources/generic-mcp.md) for chat MCPs | A Gmail / Slack / Discord MCP is listed and authenticates. |
| 7 | Runtime evidence | [`generic-mcp.md`](./sources/generic-mcp.md) | An observability, error-tracking, deploy-log, or warehouse MCP is listed. |

Cross-cutting:

- [`incident-postmortem.md`](./sources/incident-postmortem.md). Append it to every investigator's prompt when the target looks defensive (null checks, retry, timeout, rate limit, feature flag, egress guard, OOM handler).

Rules for every category:

- An MCP that needs auth and fails auth is a gap. Do not make up findings.
- Never chase a lead into another category. Record it under Additional Leads.
- Apply the secrets rule from `SKILL.md`: never copy credentials into findings.
