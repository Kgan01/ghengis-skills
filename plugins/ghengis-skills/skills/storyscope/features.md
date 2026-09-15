# StoryScope core features, translated for nonfiction

Source: Russell et al., *StoryScope: Investigating idiosyncrasies in AI fiction*, COLM 2026, arXiv 2604.03136v6, Tables 14–17. Human and AI numbers are the paper's (the AI figure averages Claude Sonnet 4.6, GPT-5.4, Gemini 3 Flash, DeepSeek V3.2 and Kimi K2.5). Scale features are 1–5 means. Percentages are prevalence.

The paper counts **30 core features**. Three of them (reference explicitness, emotional expression, subplot integration) have one option elevated on each side, so they appear twice below, giving 33 rows.

**Mapping column:** *direct* means the feature measures the same decision in an essay as in a story. *loose* means the essay equivalent is our inference. Weigh loose rows less.

---

## A. What AI does more: spelling out the meaning ("over-determination")

| Feature | Human | AI | In nonfiction this is… | Mapping | Move |
|---|---|---|---|---|---|
| Thematic explicitness & moralizing | 3.28 | 3.94 | Spelling out what the example means instead of letting it stand | direct | Cut the explanation sentence after a strong example |
| Narrator states the theme (narratorial thematic commentary) | 52% | **77%** | The quotable maxim closing a paragraph or section ("That is the gate.") | direct | End at least half the sections on the fact. State the moral at most once, and not in the final line |
| Moral / philosophical weighting | 3.26 | 3.68 | Turning a practical question into a values question ("Ultimately it's about what kind of community we want to be") | direct | Keep the stakes concrete: dates, dollars, people |
| Thematic unity | 4.41 | 4.74 | Every paragraph serves the one thesis. Nothing wanders | direct | Keep one digression that matters to the author (see C) |
| Dialogue used for philosophical debate | 34% | 59% | Quotes brought in to argue the thesis for you | loose | Use quotes that report what happened or show who the person is |
| References as vague echoes | 50% | **72%** | "Scholars have long observed", "research shows", "the literature" | direct | Name the source or cut the claim |

## B. What AI does more: dramatizing through body and senses

| Feature | Human | AI | In nonfiction this is… | Mapping | Move |
|---|---|---|---|---|---|
| Emotion rendered through the body | 38% | **81%** | "Shoulders loosening", "a knot in the stomach", "the news landed like a stone" | direct | Say the feeling ("I was relieved") or show a behavior |
| Setting mirrors a mood | 3.58 | 4.07 | Weather and rooms that reflect the argument's mood | direct | Cut it, or keep the setting only if it's a fact the reader needs |
| Environmental / ecological emphasis | 2.83 | 3.21 | Atmospheric nature scene-setting as a lead-in | loose | Cut the lead-in |
| Smell and other senses (olfactory) | 57% | 82% | Sensory detail used as texture ("the smell of old paper") | direct | Keep one sense only if it was actually witnessed |
| Sensory density | 3.66 | 3.93 | Stacked imagery | direct | Thin it out |
| Depth of interior access | 3.67 | 3.93 | Narrating what readers, users or subjects feel inside ("each carries a quiet hope") | direct | Report only what people said or did, or what the author felt |

## C. What AI does more: streamlining the structure

| Feature | Human | AI | In nonfiction this is… | Mapping | Move |
|---|---|---|---|---|---|
| Unbroken main causal chain | 3.92 | 4.20 | Background → problem → cause → solution, each step leading to the next | direct | Break in with a counterexample, a side thread or a jump in time |
| Fine-grained space | 2.27 | 2.53 | Room-by-room description | loose | Cut |
| Resolution by the protagonist's choice | 46% | **69%** | The author's position wins purely on its merits | loose | Let outside facts, other people or luck share the ending, or leave it undecided |
| People introduced by external description | 30% | 52% | "Dr. Jane Roe, a renowned expert with 20 years of…" | direct | Bring them in through what they said (this is the human fingerprint: introduction in dialogue) or did |
| No subplots | 57% | **79%** | One straight track | direct | Keep one parallel thread that doesn't get wrapped up |
| Resolution by internal understanding | 27% | 47% | Ending on a reframe or acceptance ("The question isn't X, it's Y") | direct | End on an action, a date, an open question, or the concrete worry |
| Opening grounded in a place | 2.12 | 2.33 | "In a small town nestled…" | direct | Open on a moment, a line someone said, or a number |
| Investment built before the threat | 2.76 | 2.99 | A long wind-up of background before the problem shows up | direct | Put the problem in the first paragraph and bring history in later |

## D. What humans do more: engaging the outside world

| Feature | Human | AI | In nonfiction this is… | Mapping | Move |
|---|---|---|---|---|---|
| Explicit named reference | **47%** | 24% | The specific book, statute, study, person, brand or place | direct | Name every source you rely on. Never make one up |
| Balanced mix of explicit and implicit references | 37% | 16% | Mostly named citations, plus a couple of unmarked echoes | direct | Don't footnote every allusion |

## E. What humans do more: engaging the reader

| Feature | Human | AI | In nonfiction this is… | Mapping | Move |
|---|---|---|---|---|---|
| Fourth-wall permeability | 0.67 | 0.39 | The author visible: "I'm saying this up front because…", asides, admissions | direct | At least one moment where the author steps out |
| Direct reader address | 0.28 | 0.07 | "you" | direct | Use it where it's natural. Don't put it in every paragraph |

## F. What humans do more: complexity in time and disclosure

| Feature | Human | AI | In nonfiction this is… | Mapping | Move |
|---|---|---|---|---|---|
| Recontextualization after a surprise | 3.28 | 2.95 | A late fact that changes how an earlier paragraph reads | direct | Hold back one fact (a stake, a conflict of interest, an outcome) until it lands hardest |
| Chronological discontinuity | 2.40 | 2.12 | Jumping between now, then and later | direct | Open in the present crisis, then go back |
| Nonlinear order for delayed disclosure | 1.96 | 1.68 | Putting the rule after the case, the answer after the problem | direct | Scene first, rule second |
| Anachrony (flashback / flash-forward) | 2.58 | 2.31 | "In 1974…" dropped into the middle, "By next spring…" | direct | One flashback placed where it matters, not as a history block at the top |

## G. What humans do more: diversity

| Feature | Human | AI | In nonfiction this is… | Mapping | Move |
|---|---|---|---|---|---|
| Location variety | 1.34 | 1.08 | More than one real place in the piece | loose | Bring in the second place that actually belongs |
| Dialogue-to-narration proportion | 2.95 | 2.70 | Verbatim quotes vs paraphrase | direct | Swap paraphrase for the actual words when you have them |
| Subplot running parallel to the theme | **42%** | 21% | A personal thread running alongside the argument | direct | The author's own stake, told in pieces, not dumped in one aside |
| Ambivalent moral framing of the protagonist | **59%** | 38% | The author's own side has a cost, or the "opponent" has a point | direct | One honest paragraph, in the author's words |
| Emotion named with explicit labels | **29%** | 8% | "I was angry." "It scared me." | direct | Keep plain labels. Never "elevate" them |

---

## Model fingerprints (Table 17)

These are what each model defaults to that the others don't, useful for knowing what your own draft will lean toward.

- **Claude** (most distinct of the five; 26 fingerprints): the flattest event escalation, the lowest diversity of event types, **the most uniform voice**, reverent/continuist toward tradition (62% vs 39–56%), favors **epilogues** and quiet endings, avoids dream or vision sequences. *Checks for a Claude draft:* does the tension actually rise? Does any section sound different from the others? Does it disagree with anything? Does it end with an epilogue that wraps everything up?
- **GPT**: gossip and rumor as a plot device (64%), a distant looking-back narrator ("years later…"), subverts expectations more than other models, leaves reconciliations ambiguous.
- **Gemini**: the tidiest endings with long wind-downs, the bleakest settings (88%), introduces characters by external description, uses more flashbacks.
- **DeepSeek**: **puts crucial context up front** (the rule before the scene), a highly visible narrator, emotion shown through behavior.
- **Kimi**: the generic center of the AI cluster. Opens in medias res and introduces characters in action.
- **Human** (32 fingerprints): introduces characters **through dialogue**, keeps a single point of view, **saves revelations for late in the piece**, crosses genres.

## Other findings worth knowing

- **Convergence.** The distance between the human and AI centers is 1.6 times the distance between AI models (6.6 vs 4.3). Even the closest human–AI pair is farther apart than the most distant AI–AI pair. Models don't just have a narrower range than humans; they sit in a different region.
- **Rarity.** Human stories are rarer in feature space (mean rarity percentile 0.71 vs 0.49; Cohen's d = 0.83), and the human version was the rarest of the six 57.8% of the time. In practice: when a decision point comes up, the first choice that occurs to you is the shared default. Ask what the author would actually do.
- **Length and topic** don't explain the results. The narrative model scored 93.2 both before and after length matching, and there was no significant difference by topic (p = 0.46).
- **Style-only detection** (85.8) is about as strong as the 30 core narrative features (84.8). Style still counts. It's just the part that disappears when someone edits.
- **Human agreement:** the feature extractor agreed with human annotators at Cohen's κ = 0.84, and humans agreed with each other at κ = 0.74. These features are judgment calls. Quote evidence for each one.
