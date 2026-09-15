---
name: storyscope
description: Use when writing or revising a paper, essay, blog post, op-ed, grant narrative, speech, newsletter or story that has to read as written by a person, or when the user says "make this sound human", "this sounds like AI", "StoryScope this", "de-AI the structure". Works on structural decisions (what opens, what is withheld, closers, ambivalence, named sources, verbatim quotes), not word swaps. Run it before humanizer.
allowed-tools: Read Write Edit Grep Glob
model: premium
---

# StoryScope: human structure, not human-sounding sentences

AI-written text is recognizable from its **decisions**, not only its words. StoryScope (Russell, Rajendhran, Pham, Iyyer, Wieting; COLM 2026; arXiv 2604.03136) rebuilt 10,272 human short stories with five LLMs and compared them on 304 narrative features with all style features removed. Structure alone separated human from AI at **93.2% macro-F1**. A professional-style edit that stripped clichés and purple prose lowered that by only **1.6 points**. Swapping out em-dashes and "delve" leaves the structural signal almost untouched.

This skill is for those decisions. Surface cleanup belongs to `humanizer` and comes second.

**The core rule:** these decisions belong to the author. Your job is to find each decision point, show the author what the default AI choice would be, and get their call. Do not make up the answer to fill a feature.

## When to Use

- Drafting a paper section, essay, blog post, op-ed, grant narrative, speech, newsletter or short story from someone's notes, dictation or outline
- "This sounds like AI" / "make it sound human" / "de-AI this" on text that already exists
- Reviewing a ghostwritten or model-assisted draft before it goes out under a person's name
- Any piece long enough to have a shape: roughly 400 words or more. Structure needs room to show.

## When NOT to Use

- Word-level cleanup only (stock phrases, em-dashes, filler, chatbot artifacts). Use `humanizer`.
- Reference docs, API docs, specs, runbooks, legal instruments. Their readers want linear, explicit and single-track, which is the AI profile, and that's correct there.
- Evading an AI-detection policy on work the person is required to write unaided. This skill changes how writing is built. It is not a way to hide authorship.
- Very short text (under ~150 words: a text message, a tweet). There is almost no structure to work on. Apply only rule 4 (names) and rule 7 (plain labels).

## Honest limits (say these when relevant, don't oversell)

- The corpus was **fiction, ~5,000-word stories**. Mapping features onto essays and papers is an inference. `features.md` marks which mappings are direct and which are loose.
- Numbers are **rates, not quotas**. Human narrators still stated the theme 52% of the time, compared with 77% for AI. The goal is to stop landing every section in the same default slot. It is not to ban morals.
- No single dimension decides it. Training on any one dimension topped out at 80%, and dropping any one cost at most 1.2 points. The signal is spread out, so fixing only one habit (only the closers, say) barely moves the piece. **Make changes in at least three dimensions.**
- Text classifiers trained on raw prose (ModernBERT, stylometry, TF-IDF) still reached 99.7-99.9% in the paper. This skill makes writing read and hold together like a person's. It does not make it "undetectable," and you must never claim it does.

## The process

### Mode A: drafting (author available)

**1. Get the decision sheet answered before drafting prose.** Pull proposed answers from the author's material and give them the list in plain chat. Mark each item with what the default AI draft would do so the author can see what they're overriding. Where the material has no answer, ask. Don't fill it in yourself.

| # | Decision | Default AI choice (the thing to avoid by default) |
|---|---|---|
| 1 | **Entry.** Which concrete thing opens: a moment, a quote, a number, the middle of events? | Place-setting or the thesis ("In a small town...", "X has always been...") |
| 2 | **Withheld.** What does the reader not get until later? Which late fact changes how an earlier part reads? | Context first, then problem, then answer, in order |
| 3 | **Open.** What stays unresolved? What does the author's own position cost, or who does it hurt? | Every thread closed; the author's side clean |
| 4 | **Pushback.** Which source, authority, ally or convention does the author disagree with or complicate? | Agrees with and extends every source |
| 5 | **Voices.** Who is quoted word for word? Who is introduced by what they said or did? | Paraphrase; people introduced by title and credentials |
| 6 | **Names.** Which specific people, places, works, numbers, dates or statutes replace each vague "experts", "studies", "many"? | Vague gestures toward "the literature" |
| 7 | **Side thread.** Which digression does the author care about enough to keep, even though it doesn't serve the thesis head-on? | One straight track, no subplots |
| 8 | **Endings.** Which sections end on a fact or image instead of the lesson? Is the moral stated anywhere, and where? | Every section and the piece end on a quotable maxim |
| 9 | **On the page.** Where does the author appear ("I", "you", an aside, an admission)? | Author invisible; nobody addressed |

For a short piece (under ~800 words), cover at least 1, 3, 5 or 6, and 8.

**2. Draft to the sheet.** Keep the author's plain wording. "I was scared" stays "I was scared." Don't turn it into a tight chest (see rule 7).

**3. Run the Mode B audit on your own draft** before handing it over. The model writing it drifts back toward its defaults, especially on endings (8) and resolution (3).

### Mode B: auditing or revising existing text

**1. Extract the skeleton first.** Don't judge the prose yet. The paper found that comparing raw text surfaced style features, while comparing structured templates surfaced structural ones, so extract before you judge. Fill in the template in `template.md`: opening move, order of disclosure, causal chain, threads, how it resolves, list of section closers, references (named or vague), quotes vs paraphrase, how emotion is rendered, how people are introduced, stance toward sources, where the author shows up.

**2. Score it** against the 30 core features in `features.md`. Output the scorecard below, **with an evidence line quoted from the text** for every flag. A flag without evidence is not allowed.

**3. Rank the fixes by effect per word changed.** Moving one paragraph (delayed disclosure) or cutting four closers usually does more than rewriting a whole section. For each fix, say which rule it applies and whether it needs **author material**: ambivalence, pushback, verbatim quotes, named sources and personal stakes almost always do.

**4. Get author material before rewriting.** If a fix needs a fact, quote, doubt or name that isn't in the source, list it as a question. When the author can't be reached, make the structural moves that need no new facts (reordering, cutting closers, using quotes that already exist, pulling in stakes from the notes) and hand back the rest as open questions.

**5. Rewrite structurally.** Move, cut, reorder, restore verbatim quotes, put in the author's own named specifics. Then, optionally, run `humanizer` for surface cleanup.

**6. Re-score.** Confirm changes span at least three dimensions (for example Revelation/Temporal, Situatedness, Plot) and that nothing has swung into caricature (see anti-patterns). Then read it straight through once as a reader: the author's case is still being argued, paragraphs connect, and it doesn't read like a list of facts.

### Scorecard format

```
STORYSCOPE AUDIT: <title> (<words> words, <genre>)
Dimension          Feature                         Reading          Evidence
Situatedness       Narrator states the lesson      AI (6/7 closers) "When we protect our libraries, we protect ourselves."
Situatedness       Vague vs named references       AI               "As scholars have long observed"
Agents             Emotion rendering               AI (embodied)    "their shoulders loosening"
Temporal/Revelation Order of disclosure            AI (linear)      history → uses → cuts → moral
Plot               Author's position               AI (clean)       no cost or doubt stated
...
Dimensions flagged: 5 of 7   Needs author material: 3 items (listed below)
Top fixes (ranked by effect per word): 1. ... 2. ... 3. ...
Questions for the author: ...
```

## The ten rules (the compressed version of features.md)

1. **Don't state the lesson in the closing slot.** Let at least half the sections end on a fact, a quote or a concrete image. If there's a moral, say it once, somewhere other than the last line.
2. **Open late, disclose late.** Start with a concrete moment from the middle and bring in the background after the reader cares. Put the rule after the reader has felt the problem. Use a late fact that makes an earlier paragraph read differently.
3. **Leave something open.** State at least one real cost, doubt or unresolved thread of the author's own position, in the author's words.
4. **Name things.** Real people, places, works, numbers, dates. Mix explicit citations with a few unmarked echoes. Replace every "studies show" with the study, or cut it.
5. **Push back on something.** Disagree with or complicate at least one source or accepted framing. Claude's strongest fingerprint is reverence toward its sources (62% vs 39-56%).
6. **Let people talk.** Use verbatim quotes over paraphrase. Introduce a person by what they said or did, not by a credential line. Quotes should report or reveal. They shouldn't voice the thesis for you.
7. **Name feelings plainly.** "I was angry" beats a tight throat and dim lamplight. Cut settings that mirror mood and sensory padding (AI used smell in 82% of stories, humans in 57%). Don't narrate other people's inner states you couldn't know.
8. **Keep one side thread.** A digression that runs parallel to the theme, with no bow tied on it (human 42% vs AI 21%).
9. **Show up.** Address the reader, make an aside, admit something. The author exists on the page (reader address: human 28% vs AI 7%).
10. **Vary the voice and the stakes.** Vary tension and register across sections. Claude's fingerprint is the flattest escalation and the most uniform voice of the five models. Where the author's dictated sections differ in rhythm from the rest, level the smooth parts toward the author's sections, not the other way.

## Anti-patterns

| Anti-pattern | Why it fails | Do instead |
|---|---|---|
| Swapping words, cutting em-dashes, and calling it human | The paper's LAMP edit removed clichés and purple prose and moved structural detection 1.6 points | Structural moves first; `humanizer` after |
| **Making up** a quote, a named source, an anecdote or a doubt to satisfy a feature | Fabrication, and under the author's name. Worse than sounding like AI | Ask the author. If they can't be reached, flag it as an open question. Fiction is the only exception. |
| Making up *texture*: overheard reactions ("everyone I talked to said…"), "it came up at church", a scene nobody reported, and then telling the author "no new facts added" | Invented human detail is still invention. It's the first thing a no-skill rewrite reaches for | Texture comes only from the author or the source. Otherwise leave a bracketed question: `[what did people actually say?]` |
| Rewording the closing moral instead of removing the slot ("protect our libraries" becomes "what we fund says what we care about") | Same decision (narrator states the lesson), new words. Structurally nothing changed | End on a fact, a date, a quote or the concrete worry |
| Keeping the original paragraph order and calling it a rewrite | Order of disclosure is the temporal and revelation dimensions. Same order means same structure | Draw the skeleton, then decide what moves before touching sentences |
| Asking the author only for missing *facts* (dates, numbers) | Facts help with rule 4 alone. The human part comes from *decisions* | Ask the decision questions too: your stake, who you disagree with, whose exact words, what the reader shouldn't learn until later |
| Cutting every closer, forcing "you" into every paragraph, scrambling chronology | Quotas become a new tell. Humans still moralize half the time | Aim for human rates. Break uniformity, don't flip it |
| Stripping the piece to a column of one-line fact paragraphs with no connecting prose and no argument | Minimalism is a different default, not a human one. Cutting the moral slot doesn't mean cutting the case being made | The author's argument still gets made, in connected paragraphs. Stay within ~25% of the original length unless the cut text was invented |
| Dropping the personal stake in as one orphan line ("I spent 7th grade there.") | That's an aside, not a thread. A parallel thread comes back | Bring the stake back at least twice, the second time where it changes how the reader takes something |
| Fixing one feature (usually closers) and stopping | Signal is spread across dimensions; any one removal costs at most ~1 point | Changes across three or more dimensions |
| "Elevating" the author's plain labels into imagery | Plain emotion labels and plain naming are human markers (29% vs 8%) | Leave "It's equipment." alone |
| Synonym-hunting to avoid repeating a key term | A model habit; people repeat the word that matters | Keep repetition that carries the argument |
| Rewriting silently instead of showing the author the decision points | The decisions are what makes it human. A model making them brings back the model's defaults | Decision sheet (Mode A) or scorecard plus questions (Mode B) |
| Adding ambivalence that softens a claim the author actually holds | Ambivalence means real cost or real doubt, not hedging | "This also enables X, which is why Y exists." Don't write "some may argue" |
| Claiming the result is undetectable | Raw-text classifiers still reached ~99.8% in the paper | Say it reads and is built like the author's work |
| Applying the full method to a spec, runbook or legal instrument | Linear, explicit, single-track is what those readers need | Skip it, or apply only rules 4 and 6 |

## Reference files

- `features.md`: all 30 core features with human/AI rates, what each looks like in nonfiction, and the fix move. Also each model's fingerprint (what Claude, GPT and Gemini default to).
- `template.md`: the skeleton-extraction template for Mode B step 1, adapted from the paper's NarraBench extraction prompt for nonfiction.

## Cross-References

- **`humanizer`**: the surface pass (stock words, inflation, filler). Run it *after* this skill. The two don't overlap: this one changes what the piece is made of, humanizer changes the wording.
- **`content-writing`** / **`report-writing`**: their structure templates (inverted pyramid, key-takeaways closer) are the AI-default shape. When a piece has to read as a person's, this skill overrides those templates for opening, closers and resolution.
- **`brainstorming`**: its conversational style suits walking through the Mode A decision sheet.
- **`paper-to-code`**: sibling pattern (research turned into practice). This skill is the writing-side application of arXiv 2604.03136.
- **`deep-research`** / **`fact-checker` agent**: when rule 4 needs real named sources, get them from research. Don't produce them from memory.
- Source: https://arxiv.org/abs/2604.03136 · code and features: https://github.com/jenna-russell/storyscope
