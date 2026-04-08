# Output Formatting -- Evaluation

## TC-1: Happy Path -- Same Content Adapted for Email
- **prompt:** "Draft an email to jane.doe@example.com about the Q2 dashboard project update. We finished the data pipeline, visualization layer is 80% done, and we're on track for the June 15 deadline."
- **context:** Tests email format output rules: subject line extraction, greeting derived from email address, body without markdown headers, professional sign-off, and metadata extraction via regex.
- **assertions:**
  - Includes a subject line under 60 characters related to the Q2 dashboard update
  - Greeting derives name from email address: "Hi Jane," (from jane.doe@example.com)
  - Body uses short paragraphs (2-4 sentences) with plain bold for emphasis, no markdown headers
  - Ends with a professional sign-off ("Best regards," or equivalent)
  - Extracts recipient email using the documented regex pattern
- **passing_grade:** 4/5 assertions must pass

## TC-2: Edge Case -- Slack Format with Truncation
- **prompt:** "Post this project status to Slack: We completed the authentication system overhaul including OAuth2 integration with Google, GitHub, and Microsoft providers. Session management now uses HttpOnly secure cookies with 15-minute access tokens and 7-day refresh tokens. Rate limiting is enforced at 100 requests per minute per user on auth endpoints. CORS is locked down to our three production domains. We also added comprehensive audit logging for all auth events, integrated with our SIEM platform for real-time alerting. Password reset flows now use time-limited tokens with automatic expiry after 1 hour. Two-factor authentication via TOTP is available for all users. [imagine this continues well past 2000 characters]"
- **context:** Tests Slack formatting rules: mrkdwn syntax (bold with asterisks not markdown headers), 2000 character hard cap with truncation at 1950 chars, and thread-friendly structure with key point first.
- **assertions:**
  - Converts any markdown headers to Slack bold format (`*Header*` not `# Header`)
  - Leads with the key point (auth system overhaul completed) before supporting details
  - If content exceeds 2000 characters, truncates at 1950 and appends the documented truncation message
  - Uses Slack-compatible mrkdwn syntax throughout (not standard markdown)
  - Suggests splitting long content into thread replies at paragraph boundaries
- **passing_grade:** 4/5 assertions must pass

## TC-3: Happy Path -- TTS Voice Output
- **prompt:** "Read this aloud: The Q2 revenue was $45,000 (up 15% from Q1). Our top client Acme Corp contributed 40% of revenue. See the breakdown in the table below. Three key metrics: NPS score of 72, churn rate at 2.1%, and MRR growth of $3,200/month."
- **context:** Tests TTS format rules: strip all visual formatting, spell out abbreviations, no visual references, short sentences, phonetic awareness for symbols and percentages.
- **assertions:**
  - Replaces "$45,000" with "forty-five thousand dollars" or "45 thousand dollars" (spells out currency symbol)
  - Replaces "15%" with "fifteen percent" or "15 percent" (spells out percent symbol)
  - Removes or rephrases "See the breakdown in the table below" (no visual references in TTS)
  - Spells out abbreviations on first use: NPS (Net Promoter Score), MRR (Monthly Recurring Revenue)
  - Uses natural speech transitions instead of bullet/list structure
- **passing_grade:** 4/5 assertions must pass

## TC-4: Quality Check -- Format Selection from Keywords
- **prompt:** "Take this project summary and give me versions for: 1) a Slack post to the team channel, 2) a PDF report for the client, 3) a JSON payload for our API. Summary: Project Alpha completed on time. 12 features delivered, 3 bugs found and fixed during QA. Total cost was $15,000 against a $16,000 budget."
- **context:** Tests the ability to produce three distinct formats from the same source content. The substance must remain identical while packaging changes per destination.
- **assertions:**
  - Slack version uses mrkdwn syntax, respects 2000 char limit, leads with key point
  - PDF version includes a title (H1), date stamp, section structure with heading hierarchy, and horizontal rule separators between sections
  - JSON version uses proper types (numbers as numbers not strings, null for absent values), 2-space indent, and nested structure for related fields
  - All three versions convey the same facts: on-time completion, 12 features, 3 bugs, $15k cost, $16k budget
  - Each format follows its specific rules from the skill (no cross-contamination of formatting conventions)
- **passing_grade:** 4/5 assertions must pass

## TC-5: Edge Case -- Document Chunking for Large Content
- **prompt:** "I have a 50-page technical specification document in markdown. It has 8 major sections with H2 headers. How should I chunk it for storage and retrieval?"
- **context:** Tests document ingestion and chunking methodology: semantic boundary splitting, chunk configuration defaults, overlap handling, and metadata extraction.
- **assertions:**
  - Recommends splitting at heading boundaries (H2 sections) rather than arbitrary character counts
  - Uses the default chunk size of ~1000 tokens with ~100 token overlap between chunks
  - Includes contextual prefix for each chunk (what document, which section, what came before)
  - Recommends metadata extraction: title, section headers, document type, source path
  - Applies the quality check rules: no empty chunks, no oversized chunks (>2x target), overlap regions contain meaningful content
- **passing_grade:** 4/5 assertions must pass
