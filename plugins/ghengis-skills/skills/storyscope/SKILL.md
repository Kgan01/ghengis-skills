---
name: storyscope
description: Use when writing or revising a paper, essay, blog post, op-ed, grant narrative, speech, newsletter or story that has to read as written by a person, or when the user says "make this sound human", "this sounds like AI", "StoryScope this", "de-AI the structure". Works on structural decisions (what opens, what is withheld, closers, ambivalence, named sources, verbatim quotes), not word swaps. Run it before humanizer.
allowed-tools: Read Write Edit Grep Glob
model: premium
---

# StoryScope: human structure, not human-sounding sentences

This skill applies Russell, Rajendhran, Pham, Iyyer & Wieting, *StoryScope: Investigating idiosyncrasies in AI fiction* (COLM 2026, arXiv 2604.03136v6) to everyday writing.

Every claim is tagged:
- **[paper]**: the paper found or did this. Numbers are the paper's.
- **[adaptation]**: this skill's own rule for applying the paper to nonfiction. The paper did not test it.

Keep the tags straight when you explain the method to anyone.

## What the paper found [paper]

- **Setup.** Gemini 2.5 Flash reverse-engineered a writing prompt from each of 10,272 human short stories (Books3). Claude Sonnet 4.6, GPT-5.4, Gemini 3 Flash, DeepSeek V3.2 and Kimi K2.5 each wrote a story from that prompt, giving 61,608 stories. A pipeline found **304 interpretable features** across 10 NarraBench dimensions. Gemini 3 Flash scored each story, reading the full text one dimension per call. XGBoost classifiers did the classifying, and SHAP measured each feature's importance.
- **Structure alone separates human from AI.** Removing the 47 style or style-related features leaves **257 narrative features**, which reach **93.2% macro-F1**, against 96.0% with all 304 features.
- **30 core features** reach 84.8% alone. To qualify as core, a feature needed a human–AI gap of at least 0.20 that held across all five models (AI spread ≤ 0.35).
- **Surface editing barely moves it.** LAMP rewrote 278 Gemini stories to remove seven categories of AI artifacts (cliché, redundant exposition, purple prose…), with Gemini as the rewriter and 25 few-shot examples from professional writers. The narrative classifier went from 95.5 to 93.9 macro-F1, a drop of 1.6 points.
- **Why structure matters.** The authors call AI style "increasingly fleeting". GPT-5.4 cut back its em-dashes, and "fine-tuning to mimic human style drops AI detection rates on creative writing from 97% to 3%" (citing Chakrabarty et al., 2026). They argue narrative features are harder to "humanize", since "changing them requires significant structural rewrites rather than simple post-hoc edits" (citing Namuduri et al., 2025).
- **The core pattern.** AI over-explains themes and prefers tidy, single-track plots. Human writing frames choices as morally ambiguous, has more complex timelines, names outside works, addresses the reader, and describes feelings with explicit labels more often.
- **Convergence.** The five models cluster together. Human stories are rarer (mean rarity percentile 0.71 vs 0.49), but the two distributions "overlap substantially".
- **Claude** is the most distinctive model: the flattest escalation, the most uniform narrative voice, reverent/continuist toward literary tradition (62% of stories vs 39–56% for the other sources), and a preference for epilogues and quiet endings.
- **No single dimension decides it.** The best single dimension (Agents) reaches 80.2%, and removing any one costs at most 1.2 points. The signal is spread across correlated dimensions.

## What the paper did NOT show (say this; don't oversell)

- Everything was **fiction**. Human stories averaged ~6,400 words; Gemini, DeepSeek and Kimi stories ran ~3,000. Nothing was tested on essays, blogs or papers. Every nonfiction mapping here is **[adaptation]**.
- The paper **detected** AI text. It did not test whether revising a piece to match human values makes it read as human. This skill's rewriting method is **[adaptation]**.
- Raw-text classifiers (ModernBERT, stylometry, TF-IDF) scored **99.7–99.9%**. Never claim a result is "undetectable".
- The rates are averages across stories, not targets. Human narrators commented on the theme in 52% of stories.

## When to Use

- Drafting a paper section, essay, blog post, op-ed, grant narrative, speech, newsletter or short story from someone's notes, dictation or outline
- "This sounds like AI" / "make it sound human" on existing text
- Reviewing a model-assisted draft before it goes out under a person's name
- Pieces with enough length to have a shape (roughly 400+ words)

## When NOT to Use

- Word-level cleanup only. Use `humanizer`.
- Reference docs, API docs, specs, runbooks, legal instruments. Linear, explicit and single-track is what their readers need.
- Hiding authorship where someone is required to write unaided. This skill shapes how writing is built. It isn't for evading a policy.
- Text under ~150 words. There's too little structure. Use only rule 4 (names).

## The process

### Mode A: drafting (author available)

**1. Get the decision sheet answered before drafting prose.** [adaptation] Each decision targets core features from `features.md`. Propose an answer for every item from the author's notes, so "go with your proposals" is a complete reply. Mark each item with the AI-elevated default it avoids. Ask only what the notes truly can't answer, ranked: **at most 5 questions under ~800 words**, at most 10 for longer pieces. Never fill a gap with invented material.

| # | Decision | Core features it targets [paper] | AI-elevated default to avoid |
|---|---|---|---|
| 1 | **Entry.** What does the reader get first, and what do they not get yet? | Opening spatial grounding (AI ↑), pre-threat investment (AI ↑), nonlinear framing for delayed disclosure (human ↑) | Place-setting, or a long build-up of background before the problem |
| 2 | **Withheld.** Which fact arrives late and changes how an earlier part reads? | Recontextualization after surprise (human ↑), chronological discontinuity and anachrony (human ↑) | Chronological order, every fact in sequence |
| 3 | **Ambivalence.** Where is the author's own position morally mixed: a real cost, doubt or contradiction? | Moral polarity → ambivalent/mixed (human 59% vs AI 38%) | The author's side framed as clearly good |
| 4 | **Resolution.** What settles the piece: outside events, nothing (left open), or the author's insight? | Agency in resolution → protagonist choice (AI ↑), mode of resolution → internal understanding (AI ↑) | Ending on a realization or acceptance ("the real question is…") |
| 5 | **Voices.** Who speaks in their own words, and is the central person introduced through what they said? | Dialogue-to-narration proportion (human ↑), character introduction → in-dialogue (human fingerprint) vs external description (AI ↑) | Paraphrase; introducing someone with a credential line |
| 6 | **Names.** Which specific works, people and places are named? | Intertextual strategy → explicit named reference (human 47% vs AI 24%), reference explicitness → balanced mix (human ↑) vs implicit echoes (AI ↑) | "Scholars have long observed", vague allusion |
| 7 | **Parallel thread.** Is there a second thread that echoes the main theme from another angle? | Subplot integration → thematically parallel (human 42% vs AI 21%); no subplots (AI 79% vs 57%) | One straight track |
| 8 | **Theme statement.** Is the lesson stated outright, and if so, how many times and where? | Narratorial thematic commentary (AI 77% vs human 52%), thematic explicitness & moralizing (AI ↑) | Lesson stated, and restated to close sections [adaptation: the section-closer slot] |
| 9 | **Reader.** Is the reader addressed anywhere? | Direct reader address and fourth-wall permeability (human ↑; body text 28% vs 7%, 67% vs 39%) | No address at all. But most human stories don't address the reader either, and "no direct address" is also a human fingerprint (Table 17). When a human does, it's occasional. |

For a short piece, the sheet only has to cover 1, 3, 5 or 6, and 8.

**2. Draft to the sheet.** Name feelings with explicit labels where the author's feeling is stated (explicit labels: human 29% vs AI 8%; embodied metaphor: AI 81% vs 38%) [paper].

**3. Audit the draft blind.** [paper protocol, adapted] The paper hid which source wrote a story in every LLM-facing prompt. When you can, give the draft to a fresh subagent to score, with no mention of who wrote it. When you can't, score it yourself using Mode B step 2 exactly.

### Mode B: auditing or revising existing text

**1. Score the full text, one dimension at a time.** [paper] Answer the paper's exact questions in `features.md`, reading the whole piece, **one NarraBench dimension per pass**. The paper found single-call application covered only 68.4% of features, with "broad systematic dropout, especially in revelation and temporal-structure features". Per-dimension calls covered 95.4%. [adaptation] Only the 8 dimensions that contain core features need a pass: Situatedness, Plot, Events, Setting, Agents, Perspective, Revelation, Temporal structure. Quote evidence from the text for every answer; the paper's scoring step didn't require that, but this skill does.

**2. Draw the skeleton to plan the rewrite.** [adaptation] Fill in `template.md`, adapted from the paper's Figure 8 extraction schema. The paper used templates to *discover* features, not to score them. Here the skeleton is a planning map: it shows the order of disclosure, the threads and the resolution, so you can see what to move.

**3. Rank fixes by effect per word changed.** [adaptation] Moving a paragraph or removing a theme statement usually beats rewriting a section. For each fix, name the core feature and say whether it needs **author material** (ambivalence, quotes, named references and personal stakes almost always do).

**4. Get author material before rewriting.** If a fix needs a fact, quote, doubt or name that isn't in the source, list it as a question. When the author can't be reached, make only the moves that need no new facts, and return the rest as bracketed questions.

**5. Rewrite structurally, then re-score (step 1 again).** [adaptation] Change features in at least three dimensions. This rule is ours: the paper showed the signal is redundant across dimensions (removing any one cost ≤ 1.2 points). The only edits it tested were LAMP's surface rewrites, never structural edits or edits aimed at human feature values. Then read the piece straight through: the argument is still made, the paragraphs connect, and the length is within ~25% of the original unless the removed text was invented.

**6. Optional surface pass:** `humanizer`.

### Scorecard format

```
STORYSCOPE AUDIT: <title> (<words> words, <genre>)
Dimension      Core feature (paper question)             Answer            Leans   Evidence
Situatedness   Narratorial thematic commentary           yes               AI      "When we protect our libraries, we protect ourselves."
Situatedness   Reference explicitness                    implicit echoes   AI      "As scholars have long observed"
Agents         Dominant emotional expression             embodied metaphors AI     "their shoulders loosening"
Revelation     Nonlinear framing for delayed disclosure  1 (linear)        AI      history → users → impact → moral
Plot           Moral polarity toward protagonist         clearly positive  not the human-elevated option (ambivalent)  no cost of the author's position stated
...
Dimensions leaning AI: 5 of 8   Needs author material: 3 items
Top fixes (effect per word): 1. ... 2. ... 3. ...
Questions for the author: ...
```

## Rules (each traced to a core feature)

1. **Decide whether to state the theme at all.** [paper: narratorial commentary 77% AI vs 52% human; explicitness 3.94 vs 3.28] If you state it, say it once. [adaptation: don't repeat it as a closer on every section]
2. **Hold something back, and let a late fact reframe what came before.** [paper: recontextualization 3.28 vs 2.95; delayed disclosure 1.96 vs 1.68; chronological discontinuity; anachrony] Don't open with place-setting or a long background wind-up [paper: opening spatial grounding and pre-threat investment are AI-elevated]. A formula "in medias res" opening is not the fix. That's Kimi's fingerprint.
3. **Frame the author's own position as mixed where it really is.** [paper: moral polarity → ambivalent, 59% vs 38%] Ambivalence means a real cost or contradiction from the author, not a hedge.
4. **Name the works, people and places you draw on, and mix explicit citation with a few unmarked echoes.** [paper: explicit named reference 47% vs 24%; balanced mix 37% vs 16%; implicit echoes AI 72% vs 50%]
5. **Don't let the ending be the author's insight winning.** [paper: protagonist-choice resolution 69% AI vs 46%; internal-understanding resolution 47% vs 27%] Let outside events settle it, or leave it unresolved.
6. **Put the words people actually said on the page, and introduce the central person through their words.** [paper: dialogue proportion human ↑; in-dialogue introduction is the top human fingerprint; external description AI 52% vs 30%] Note that "primarily direct speech" is also a Gemini fingerprint, so quote where you have the words. Don't make everything quotes.
7. **Name feelings plainly. Don't render them through the body or the setting.** [paper: explicit labels 29% vs 8%; embodied metaphor 81% vs 38%; setting as psychological mirror 4.07 vs 3.58] Cut sensory padding [paper: sensory density AI ↑; olfactory among the most engaged senses 82% vs 57%]. Don't narrate inner states you couldn't know [paper: depth of interior access AI ↑].
8. **Include a second thread that echoes the theme from another angle.** [paper: thematically parallel subplots 42% vs 21%]
9. **Let one dialogue do more than argue ideas.** [paper: dialogue function → philosophical debate, AI 59% vs 34%] Quotes should move events or show a person.
10. **For a Claude-drafted piece, check Claude's fingerprints:** does the stakes level actually rise, does any section sound different from the others, does it only honor convention and never break one, and does it close on an epilogue? [paper: Claude fingerprints] [adaptation: applying "reverent toward literary tradition" to cited sources and conventions in nonfiction]

## Anti-patterns

| Anti-pattern | Why it fails | Do instead |
|---|---|---|
| Swapping words, cutting em-dashes, and calling it human | [paper] LAMP artifact removal moved narrative detection 1.6 points (95.5 → 93.9, Gemini stories) | Structural moves first; `humanizer` after |
| **Making up** a quote, source, anecdote, doubt or reaction to satisfy a feature | Fabrication under the author's name | Ask, or leave a bracketed question. Fiction is the only exception. |
| Making up *texture*: "everyone I talked to said…", scenes nobody reported, "the number is right there on the page" | Observed in no-skill baselines (see eval), each time claiming "no new facts" | Texture comes only from the author or the source |
| Rewording the theme statement instead of deciding whether to have one | Narratorial commentary is yes/no for the whole piece. New words, same answer | Remove it, or state it once, deliberately |
| Keeping the original paragraph order and calling it a rewrite | Revelation and temporal features measure order | Plan from the skeleton before touching sentences |
| Opening "in medias res" or introducing people "in action" as the human fix | [paper] Both are Kimi fingerprints. Among the top human fingerprints listed, introduction is in-dialogue | Solve the entry with delayed disclosure, not a formula |
| Constant "you", constant flashbacks, all quotes | [paper] Most human stories never address the reader, and "no direct address" is also a human fingerprint. Frequent flashbacks and primarily direct speech are Gemini fingerprints | Use these at human rates, not as quotas |
| Stripping to one-line fact paragraphs with no argument | Observed overcorrection in testing | Keep the case connected; length within ~25% |
| A personal stake dropped in as one orphan line | Not a parallel thread | A thread that comes back and echoes the theme |
| Scoring all 30 features in one pass | [paper] Single-call coverage was 68.4% vs 95.4% per dimension | One dimension per pass |
| Asking the author twenty questions for a short post | Nobody answers them; the skill stops being easy | Propose answers; ≤5 questions under 800 words |
| Claiming the result is undetectable | [paper] Raw-text classifiers hit 99.7–99.9% | Say it's built like the author's work |
| Presenting an [adaptation] rule as a paper finding | The paper studied fiction detection only | Keep the tags |

## Reference files

- `features.md`: the 30 core features with the paper's exact questions, answer options, human/AI values, NarraBench dimension, and a nonfiction reading marked as adaptation. Also per-model fingerprints and the method details.
- `template.md`: the skeleton for Mode B step 2, the paper's Figure 8 schema adapted for nonfiction.

## Cross-References

- **`humanizer`**: the surface pass. Run it after this skill.
- **`content-writing`** / **`report-writing`**: their templates (key-takeaways closer, inverted pyramid) match the AI-elevated profile. When a piece has to read as a person's, this skill overrides them on theme statement, resolution and disclosure order.
- **`brainstorming`**: conversational format for the decision sheet.
- **`deep-research`** / **`fact-checker` agent**: real named sources for rule 4. Never produce them from memory.
- **`paper-to-code`**: the same research-to-practice discipline.
- Source: https://arxiv.org/abs/2604.03136 · code, prompts, features: https://github.com/jenna-russell/storyscope
