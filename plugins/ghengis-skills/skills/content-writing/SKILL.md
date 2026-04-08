---
name: content-writing
description: Use when creating written content -- blog posts, documentation, marketing copy, technical writing -- covers structure, audience targeting, SEO basics, and editorial quality
allowed-tools: Read Write Edit
---

# Content Writing

When helping with written content -- blog posts, articles, newsletters, thought leadership, documentation -- follow these principles for well-structured, engaging, and audience-appropriate writing.

## Core Instructions

1. **Hook in the first sentence** -- start with a surprising stat, bold claim, or relatable problem
2. **Use the inverted pyramid** -- most important info first, details later
3. **Structure for scanning** -- short paragraphs (2-3 sentences), headers every 200-300 words, bullet lists for key points
4. **Write at 8th-grade reading level** -- clear, simple language wins over clever vocabulary
5. **Include one concrete example per major point** -- abstract advice is forgettable
6. **SEO basics**: Target keyword in title, first paragraph, and 2-3 headers. Use related terms naturally
7. **End with a takeaway or CTA** -- never trail off
8. **Word count targets**: Blog post 800-1500 words, newsletter 400-600, article 1500-2500

## Output Structure

When producing content, use this format:

```markdown
# [Title -- includes keyword, under 60 chars]

*[Subtitle or meta description -- 150-160 chars]*

[Hook paragraph]

## [Section 1 Header]
[Content with examples]

## [Section 2 Header]
[Content with examples]

## [Section 3+ Headers]
[Content]

## Key Takeaways
- [Point 1]
- [Point 2]
- [Point 3]

---
*[CTA or closing line]*
```

## Worked Examples

### Example 1 -- Blog Post

**Input**: Topic: "Why most AI projects fail". Audience: tech managers. Tone: authoritative but accessible. Keyword: "AI project failure".

**Reasoning**: Tech managers have seen failed projects. Start with a stat that validates their experience. Structure as a listicle for easy scanning.

**Output**:
```markdown
# Why 85% of AI Projects Fail (And How to Beat the Odds)

*Most AI initiatives never make it to production. Here's what the survivors do differently.*

You've seen it before: a team spends six months building an AI model, demos it to leadership, gets applause -- and then nothing happens. The model sits in a notebook, never deployed, slowly becoming irrelevant.

You're not alone. According to Gartner, 85% of AI projects fail to deliver business value. But the 15% that succeed share three patterns.

## 1. They Start With the Problem, Not the Tech

The most common mistake is building a model and then looking for a use case. Successful teams flip this: they identify a $1M+ problem first, then ask whether AI is the right solution.

**Example**: A logistics company didn't start with "let's use ML." They started with "we lose $3M/year to misrouted packages." The AI solution was obvious once the problem was clear.

## 2. They Ship a Crappy V1 in 4 Weeks

Perfectionism kills AI projects. The winning teams deploy a minimal model fast -- even if it's only 70% accurate -- and improve in production with real data.

## 3. They Have an Ops Plan From Day One

Model accuracy is 20% of the work. Monitoring, retraining, data pipelines, and incident response are the other 80%.

## Key Takeaways
- Start with the business problem, not the technology
- Ship fast, iterate with real data
- Budget 80% of effort for operations, not modeling

---
*Building an AI project? Start with an AI Readiness Checklist -- it takes 10 minutes and saves months.*
```

### Example 2 -- Newsletter

**Input**: Topic: weekly tech digest. Audience: developers. Tone: casual, insider voice. Length: 500 words.

**Reasoning**: Developers want signal, not noise. Lead with the most impactful news. Use informal language.

**Output**:
```markdown
# This Week in Dev: Claude Gets Agents, React 20 Ships

*Your 3-minute developer news roundup*

Happy Friday. Three things you should know:

**Claude's agent SDK is wild.** Anthropic shipped a framework for building autonomous agents that can use tools, maintain context across sessions, and self-correct. Early reviews say it's significantly less janky than LangChain. Worth trying this weekend.

**React 20 is official.** The big change: Server Components are now the default. If you're still client-rendering everything, this is your nudge to learn RSC. Migration guide is actually good for once.

**GitHub Copilot got expensive.** New pricing: $19/mo individual, $39/seat for teams. The free tier now limits completions to 50/day. Cursor and Cody are looking more attractive.

## Quick Links
- [Claude Agent SDK docs](link)
- [React 20 migration guide](link)
- [Copilot pricing comparison spreadsheet](link)

---
*Reply to this email if you want us to cover something next week.*
```

## Edge Cases

- **No keyword provided**: Focus on readability and value; skip SEO optimization
- **Highly technical topic**: Include code snippets or diagrams. Define acronyms on first use
- **Controversial topic**: Present multiple perspectives. Take a clear position but acknowledge counterarguments
- **Very short request** (<200 words): Format as a LinkedIn post or tweet thread instead

## Quality Checklist

- [ ] Hook in the first sentence (not "In this article, we will...")
- [ ] Headers every 200-300 words
- [ ] No paragraph longer than 4 sentences
- [ ] At least one concrete example included
- [ ] Keyword appears in title and first paragraph (if SEO)
- [ ] Ends with a takeaway or CTA
- [ ] Reading level is 8th grade or below (no unnecessary jargon)
- [ ] Word count matches the target range
