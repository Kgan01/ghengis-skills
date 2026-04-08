---
name: output-formatting
description: Use when content needs to be formatted for a specific destination or when ingesting documents -- covers 8 output formats (chat, email, Slack, PDF, CSV, JSON, markdown, TTS), document chunking for digestion, and audience-appropriate adaptation of the same content
---

# Output Formatting

Format the same content differently depending on where it will be delivered. The substance never changes -- only the packaging. This skill also covers document ingestion: splitting source material into meaningful chunks for processing, summarization, or storage.

## Core Principle

One piece of content, eight possible formats. Choose the format based on the destination channel and the audience consuming it. Never rewrite the substance -- adapt the structure, length, and syntax.

## 8 Destination Formats

### 1. Chat (Default)

Conversational markdown for interactive sessions.

- Concise, scannable paragraphs
- Markdown-friendly: headers, bold, bullet points, code fences
- Light emoji use (only when it aids scannability, never decorative)
- No formal greeting or sign-off
- Keep responses under ~800 words unless the user asked for depth

### 2. Email

Professional message with structural elements.

- **Subject line**: Extract from the first meaningful sentence or the user's stated topic. Keep under 60 characters.
- **Greeting**: "Hi {Name}," -- derive name from email address if not provided (e.g., jane.doe@example.com -> "Hi Jane,")
- **Body**: Strip markdown headers (they look wrong in email). Keep paragraphs short (2-4 sentences). Use plain bold for emphasis, not headers.
- **Sign-off**: "Best regards," followed by sender name
- **Formality**: Match the relationship. Business contacts get professional tone. Known contacts can be warmer.
- **Metadata to extract**: recipient email (regex: `[\w.+-]+@[\w-]+\.[\w.]+`), subject (look for "about", "regarding", "re:", "subject:" patterns)

### 3. Slack / Discord

Platform messaging with character limits and platform syntax.

- **Slack**: Convert markdown headers to bold (`*Header*` not `# Header`). Slack uses mrkdwn, not standard markdown.
- **Discord**: Standard markdown works, but use `**bold**` for emphasis.
- **Character limit**: Hard cap at 2000 characters. If content exceeds this, truncate at 1950 chars and append: `\n\n_...truncated. Full version available on request._`
- **Thread-friendly**: Lead with the key point. Supporting detail goes in thread replies.
- **Chunking for long content**: Split at paragraph boundaries, not mid-sentence. Each chunk should stand alone.
- **Reactions**: Suggest appropriate emoji reactions for status updates (checkmark for done, eyes for review needed).

### 4. TTS / Voice

Spoken output -- optimized for listening, not reading.

- **Strip all visual formatting**: Remove markdown headers, bold, italic, code fences, code blocks, links (keep link text, drop URL), bullet markers, numbered list markers, tables, horizontal rules.
- **Short sentences**: Break complex sentences at natural speech boundaries.
- **No visual references**: Never say "as shown above" or "in the table below" -- there is no visual.
- **Phonetic awareness**: Spell out abbreviations on first use. Use "dollars" not "$". Use "percent" not "%".
- **Conciseness**: Cap at ~1000 characters. Find a sentence boundary near the limit (look for a period after the 500-char mark). If no good boundary, hard cut at 1000.
- **Natural flow**: Use transitional phrases ("Next,", "Also worth noting,") instead of bullet structures.

### 5. PDF / Document

Structured report with clear hierarchy.

- **Title**: Ensure content starts with a top-level header. If missing, generate one from the original request (first 60 chars).
- **Date stamp**: Add generation date at the top: `*Report generated: {date}*`
- **Section structure**: Use heading hierarchy (H1 for title, H2 for sections, H3 for subsections). Never skip levels.
- **Page-break awareness**: Insert `---` horizontal rules between major sections (these become page breaks in PDF renderers).
- **Table of contents**: For documents with 4+ sections, include a TOC after the title.
- **Footer**: Add generation metadata at the bottom with a horizontal rule separator.

### 6. CSV / Data

Tabular data export with consistent structure.

- **Headers**: Always include a header row. Use snake_case for column names.
- **Delimiters**: Use commas. If field values contain commas, wrap in double quotes.
- **Escaping**: Double quotes inside quoted fields become `""`. Newlines inside fields get quoted.
- **Type consistency**: Every value in a column should be the same type. Don't mix numbers and strings. Use empty string for null, not "N/A" or "null".
- **Date format**: ISO 8601 (`2026-04-07T14:30:00Z`). Be consistent -- don't mix formats.
- **Encoding**: UTF-8 with BOM for Excel compatibility when the user mentions Excel.

### 7. JSON / API

Structured data for programmatic consumption.

- **Schema adherence**: If the user specifies a schema, match it exactly. Field names, nesting, types.
- **Proper types**: Numbers as numbers (not strings). Booleans as `true`/`false` (not "yes"/"no"). Use `null` for absent values (not empty string).
- **Nested structure**: Group related fields into objects. Don't flatten everything to top-level.
- **Arrays**: Use arrays for lists of items, even if there's only one item.
- **Indentation**: 2-space indent for human-readable output. Minified only when explicitly requested.
- **Content type**: `application/json` -- note this in metadata when relevant.

### 8. Markdown

GitHub-Flavored Markdown for documentation and files.

- **GFM compliance**: Use fenced code blocks with language identifiers (` ```python `, not ` ``` `).
- **Heading hierarchy**: Start at H1, never skip levels. One H1 per document.
- **Link formatting**: `[text](url)` -- descriptive text, not "click here".
- **Tables**: Use GFM table syntax with alignment. Include header separator row.
- **Lists**: Use `-` for unordered, `1.` for ordered. Indent nested lists by 2 or 4 spaces consistently.
- **Line breaks**: Use blank lines between blocks. Don't rely on trailing spaces for line breaks.

## Format Selection Guide

| Audience / Channel | Format | Why |
|--------------------|--------|-----|
| Interactive conversation | Chat | Conversational, scannable |
| Sending to a person | Email | Professional structure, greeting/sign-off |
| Team channel / group chat | Slack/Discord | Platform syntax, character limits |
| Hands-free / driving / walking | TTS | No visual formatting, natural speech |
| Stakeholder or client deliverable | PDF | Professional, printable, structured |
| Data export / spreadsheet | CSV | Parseable, importable |
| API response / programmatic use | JSON | Typed, structured, machine-readable |
| Documentation / README | Markdown | GFM, version-control friendly |

### Inferring the Destination

Look for keyword signals in the user's request:

| Keywords | Inferred Destination |
|----------|---------------------|
| "email", "mail to", "send to", "reply to", "draft", "compose", "cc", "bcc" | Email |
| "document", "write a doc", "create a document", "word doc", "google doc" | PDF/Document |
| "slack", "post to slack", "channel", "discord", "post to discord" | Slack/Discord |
| "read aloud", "speak this", "say it out loud", "voice" | TTS |
| "pdf", "report", "printable", "print this" | PDF |
| "csv", "spreadsheet", "export data", "table export" | CSV |
| "json", "api response", "structured data" | JSON |

If no signals are present, default to Chat.

## Document Ingestion and Chunking

When processing source documents (for summarization, storage, or retrieval), chunk them into meaningful segments.

### Contextual Chunking

Split documents at semantic boundaries, not arbitrary character counts.

- **Markdown/code**: Split at heading boundaries (H1, H2, H3). Keep a heading with its content.
- **Prose**: Split at paragraph boundaries. Keep related paragraphs together when they discuss the same topic.
- **Code files**: Split at function/class boundaries. Keep imports with the first chunk.
- **PDF**: Split at section headers or page boundaries. Preserve section context.

### Chunk Configuration

| Parameter | Default | Purpose |
|-----------|---------|---------|
| **Chunk size** | ~1000 tokens | Target size per chunk. Semantic boundaries take priority over exact size. |
| **Chunk overlap** | ~100 tokens | Repeat the last ~100 tokens of the previous chunk at the start of the next. Preserves context across boundaries. |
| **Contextual prefix** | Enabled | Prepend a short LLM-generated summary of the chunk's context (what document, which section, what came before). |

### Metadata Extraction

For every ingested document, extract and preserve:

- **Title**: First heading or filename
- **Author**: If present in frontmatter or document metadata
- **Date**: Creation or modification date
- **Section headers**: Full hierarchy for navigation
- **Document type**: PDF, markdown, code, plain text -- determines chunking strategy
- **Source path**: Original file location for reference

### When to Chunk vs. Process Whole

| Document Size | Strategy |
|---------------|----------|
| Under 500 tokens | Process whole -- chunking adds overhead with no benefit |
| 500-4000 tokens | Process whole if within context window; chunk if storing for retrieval |
| Over 4000 tokens | Always chunk. Use overlap for context preservation. |

### Summarization Levels

When summarizing chunked content, offer the appropriate level of compression:

| Level | Ratio | Use Case |
|-------|-------|----------|
| **Sentence** | ~20:1 | Push notifications, TTS previews, chat previews |
| **Paragraph** | ~5:1 | Email summaries, briefing bullets |
| **Section** | ~3:1 | Document overviews, table of contents with summaries |
| **Document** | ~10:1 | Archive records, search index entries |

### Chunk Quality Checks

After chunking, verify:

1. No chunk is empty or contains only whitespace
2. No chunk exceeds 2x the target size (split oversized chunks)
3. Overlap regions don't contain only formatting (headers, separators)
4. Metadata is attached to every chunk (source, position, section)
