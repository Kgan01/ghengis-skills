# Content Writing -- Evaluation

## TC-1: Blog Post with SEO
- **prompt:** "Write a blog post about remote work productivity tips. Target keyword: 'remote work productivity'. Audience: managers. Tone: professional but approachable."
- **context:** User wants a full blog post with SEO optimization, proper structure, and audience targeting.
- **assertions:**
  - Title is under 60 characters and includes the keyword "remote work productivity"
  - First paragraph contains a hook (surprising stat, bold claim, or relatable problem) -- not "In this article, we will..."
  - Keyword appears in the title, first paragraph, and at least 2 headers
  - Structure uses headers every 200-300 words with short paragraphs (2-3 sentences max)
  - Includes at least one concrete example per major point
  - Ends with key takeaways or a CTA
  - Word count falls within 800-1500 words
- **passing_grade:** 5/7 assertions must pass

## TC-2: Newsletter Format
- **prompt:** "Write a weekly developer newsletter about three topics: a new React release, a security vulnerability in npm, and a trending open-source project. Casual tone, 500 words."
- **context:** Short-form newsletter for developers. Needs to be scannable and punchy.
- **assertions:**
  - Total word count is approximately 400-600 words
  - Covers all three requested topics
  - Uses casual/insider voice appropriate for developers
  - Includes a quick links section or equivalent for further reading
  - Ends with a CTA (reply, subscribe, share)
- **passing_grade:** 4/5 assertions must pass

## TC-3: No Keyword Provided (Edge Case)
- **prompt:** "Write a short piece about why startups should hire generalists early on."
- **context:** No SEO keyword given. Skill should focus on readability and value, skipping SEO optimization.
- **assertions:**
  - Does not force a keyword into the title or headers unnaturally
  - Still opens with a compelling hook
  - Maintains structure with headers and short paragraphs
  - Includes at least one concrete example
  - Ends with a takeaway or conclusion (not trailing off)
- **passing_grade:** 4/5 assertions must pass

## TC-4: Very Short Request
- **prompt:** "Write something about AI in healthcare, under 200 words."
- **context:** Request is under 200 words target. Skill should adapt format to LinkedIn post or tweet thread.
- **assertions:**
  - Output is under 200 words
  - Format adapts to short-form content (LinkedIn post, tweet thread, or similar)
  - Still includes a hook and a takeaway
  - Does not pad with filler to reach a standard blog length
- **passing_grade:** 3/4 assertions must pass

## TC-5: Quality Checklist Adherence
- **prompt:** "Write a blog post about why most SaaS companies fail in their first year. Keyword: 'SaaS failure'. Audience: founders."
- **context:** Full blog post request. Evaluates adherence to the quality checklist from the skill.
- **assertions:**
  - Hook in the first sentence (not a generic opening)
  - No paragraph longer than 4 sentences
  - Reading level is accessible (8th grade or below, no unnecessary jargon)
  - At least one concrete example or case study included
  - Headers break up content every 200-300 words
  - Meta description or subtitle is 150-160 characters
- **passing_grade:** 4/6 assertions must pass
