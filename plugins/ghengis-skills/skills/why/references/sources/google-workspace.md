# Google Workspace (Gmail + Drive MCPs, when connected)

Covers two categories: **cloud documents** (Drive) and **conversation record** (Gmail). Dispatch them as two investigators if both are connected.

## Probe

Look in the tool list for Gmail tools (Claude Code: names like `mcp__claude_ai_Gmail__search_threads`, `get_thread`) and Drive tools (`mcp__claude_ai_Google_Drive__search_files`, `read_file_content`). Tools listed as deferred must be loaded first (Claude Code: ToolSearch). In pi, check the MCP adapter's server list. Run one trivial search. Auth failure or no tools → gap.

These investigators are **read-only**: never send, reply, draft, label, trash, share, or edit.

## Drive — how to search

1. Search by feature name, client or venture name, and document-type words ("proposal", "spec", "plan", "brief").
2. Bound by date when the anchor commit date is known.
3. Read the full file content, not the preview. Note owner and last-modified date.
4. Note whether a doc is a draft or a final version.

## Gmail — how to search

1. Search by the feature/client term, the vendor name, error strings, and the PR or deploy URL.
2. Bound by date: a window around the anchor commit (`after:` / `before:` operators where supported).
3. Fetch whole threads; the decision is often in a reply.
4. Mail from clients and vendors is where external constraints show up ("the client needs X by Friday", "access code expires on <date>").

## What good evidence looks like

- A client or vendor message that states the requirement the code meets
- A Drive spec or proposal with the reasoning, dated before the code
- A thread where an alternative was rejected

## Common pitfalls

- **Personal data.** Quote only the sentence that bears on the question. No addresses, phone numbers, or credentials.
- **Draft vs. sent.** A draft proposal is not an agreement.
- **Name collisions.** The same project name can mean different things in different threads; check participants.
- **Retention.** Deleted or archived mail is invisible. Note the earliest date the search reached.

## What to return

For each item: Drive file title + link, or Gmail thread subject + date + participants (names only); verbatim quote; draft/final or sent/received.
