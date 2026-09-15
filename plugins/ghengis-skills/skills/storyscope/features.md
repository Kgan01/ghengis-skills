# StoryScope core features, fingerprints and method

Source: Russell et al., *StoryScope: Investigating idiosyncrasies in AI fiction*, COLM 2026, arXiv 2604.03136v6.
- Feature questions and answer options: Tables 14–15.
- Human/AI values: Table 16. The AI value averages all five models.
- Fingerprints: Table 17.

Everything in the **Nonfiction reading** and **Fit** columns is **[adaptation]**. The paper only studied fiction.

## How to read the values

- **s**: 1–5 Likert scale. The value is the mean.
- **o**: ordinal scale. The value is the mean "over integer codes". It is **not** a 1–5 scale. The paper gives the answer options but not the codes. Reader address (never / occasional / frequent) is presumably coded 0/1/2, but that's inferred. Fourth-Wall Permeability is labeled "1 (no breaking)–4", yet its means are 0.67 and 0.39, below the scale's minimum, so the paper is inconsistent there. Use these values as relative (human > AI), not absolute.
- **→ option**: a categorical, binary or multi-select option. The value is the % of stories with that option.
- **Gap** = Human − AI.
- **Dimension codes** (NarraBench): SIT situatedness, PLT plot, EVT events, SET setting, AGENT agents, PER perspective, REV revelation, TMP temporal structure.

The paper counts **30 core features**. Reference explicitness, emotional expression and subplot integration each have one option elevated for AI and another for humans, so the tables below have 33 rows.

To qualify as core, a feature had to be stable and important in bootstrap SHAP (B = 50), have a mean human–AI gap of at least 0.20, and show a cross-model AI spread of at most 0.35. In other words, the gap holds for all five models.

**Fit** [adaptation] means how directly the paper's question can be asked of an essay or blog post:
- **close**: ask it almost word for word
- **loose**: the nonfiction reading stretches the feature; weigh it less

**Scoring procedure** [paper]: read the full text, then answer one dimension's questions per pass. Don't score from a summary.

---

## AI-elevated: thematic over-determination

| Feature | Paper question | Dim | Options | Human | AI | Nonfiction reading | Fit |
|---|---|---|---|---|---|---|---|
| Thematic Explicitness & Moralizing | How explicitly does the story articulate its themes or morals? | SIT | s 1–5 | 3.28 | 3.94 | How openly the piece spells out what its examples mean | close |
| Moral / Philosophical Weighting | How heavily does the story foreground moral or philosophical questions? | SIT | s 1–5 | 3.26 | 3.68 | Turning a practical question into a values question | close |
| Thematic Unity | To what extent do subplots and flourishes serve a central thematic concern? | PLT | s 1–5 | 4.41 | 4.74 | Every paragraph serving one thesis | close |
| Narratorial Thematic Commentary → yes | Does the narrator explicitly comment on themes beyond characters' perspectives? | SIT | binary | 52% | 77% | The author states the lesson outright anywhere in the piece (a yes/no for the whole piece) | close |
| Dialogue Function → philosophical debate | What main functions does dialogue serve? | PER | multi: advance plot, reveal character, worldbuilding, philosophical, comic | 34% | 59% | Quotes used to argue ideas, not to move events or show a person | loose |
| Reference Explicitness → implicit echoes | Are intertextual gestures primarily explicit or diffuse? | SIT | cat: none, explicit named, implicit echoes, balanced mix | 50% | 72% | References to other works that stay allusive and unnamed | close for works; loose for "research shows" |

## AI-elevated: sensory and embodied performativity

| Feature | Paper question | Dim | Options | Human | AI | Nonfiction reading | Fit |
|---|---|---|---|---|---|---|---|
| Dominant Emotional Expression → embodied | How are characters' emotions most commonly conveyed? | AGENT | cat: explicit labels, embodied metaphors, behavioral cues, ambiguous | 38% | 81% | Feelings shown through the body ("a knot in the stomach") | close |
| Setting as Psychological Mirror | To what degree does physical environment mirror characters' inner states? | SET | s 1–5 | 3.58 | 4.07 | Weather and rooms that mirror the mood | close when a scene is described |
| Environmental & Ecological Emphasis | How prominent is the natural environment or ecology in the narrative? | SET | s 1–5 | 2.83 | 3.21 | Nature description | loose |
| Dominant Sensory Modalities → olfactory | Which sensory modalities does the story most frequently engage? | SET | multi: visual, auditory, olfactory, tactile, gustatory, kinesthetic | 57% | 82% | Smell among the senses the piece leans on most | loose |
| Sensory Density | How dense is sensory description across the narrative? | SET | s minimal–lush | 3.66 | 3.93 | Stacked sensory description | close |
| Depth of Interior Access | How deep into characters' inner life does narration go? | PER | s 1–5 | 3.67 | 3.93 | Narrating what other people feel inside | close |

## AI-elevated: structural streamlining

| Feature | Paper question | Dim | Options | Human | AI | Nonfiction reading | Fit |
|---|---|---|---|---|---|---|---|
| Continuity of Main Causal Chain | How continuous is the single causal chain from inciting incident to ending? | EVT | s 1–5 | 3.92 | 4.20 | One unbroken line from background to solution | close |
| Spatial Granularity Level | How fine-grained is the story's depiction of physical space? | SET | o very_low–high | 2.27 | 2.53 | Detailed description of physical space | loose |
| Agency in Resolution → protagonist choice | Is resolution driven by protagonist's choices or external events? | PLT | cat: protagonist_choice, mixed, external_fate | 46% | 69% | The piece is settled by the author's (or central actor's) own choice | loose |
| Character Introduction → external description | What narrative device primarily introduces the central character? | AGENT | cat: external_desc, in-action, in-dialogue, inner_thought, others_reports | 30% | 52% | The central person introduced by description or credentials | close (central person only) |
| Subplot Integration → no subplots | How directly do subplots echo the central theme? | PLT | cat: no_subplots, thematically_parallel, contrasting, independent | 57% | 79% | A single track | close |
| Mode of Resolution → internal understanding | Is the main event chain resolved through internal acceptance or external action? | EVT | cat: resolved externally, resolved internally, unresolved | 27% | 47% | Ending on a realization, reframe or acceptance | close |
| Opening Spatial Grounding | How clearly does the opening ground the reader in a specific physical setting? | SET | o none/vague, minimal, clear local, clear local+global | 2.12 | 2.33 | Opening by establishing the place | close |
| Pre-Threat Character Investment | How much does the story build investment before major jeopardy? | REV | s 1–5 | 2.76 | 2.99 | Background wind-up before the problem appears | close |

## Human-elevated: intertextual richness

| Feature | Paper question | Dim | Options | Human | AI | Nonfiction reading | Fit |
|---|---|---|---|---|---|---|---|
| Intertextual Strategy Types → explicit named reference | What kinds of intertextual engagement does the story employ? | SIT | multi: explicit named, retelling, pastiche, myth/religion, self referential | 47% | 24% | Naming the specific works, authors and texts drawn on | close |
| Reference Explicitness → balanced mix | Are intertextual gestures explicit or diffuse? | SIT | cat (as above) | 37% | 16% | Named citations mixed with some unmarked echoes | close |

(Body text, §4.1 [paper]: humans "reference specific texts and authors at nearly double the AI rate", while AI "avoids naming real brands, places, or works.")

## Human-elevated: reader engagement

| Feature | Paper question | Dim | Options | Human | AI | Nonfiction reading | Fit |
|---|---|---|---|---|---|---|---|
| Fourth-Wall Permeability | To what extent does the story break the boundary between story-world and reader? | SIT | o 1 (no breaking)–4 (radical violations) | 0.67 | 0.39 | The author stepping outside the piece to comment on it | close |
| Frequency of Direct Reader Address | How often does the text directly address the reader? | PER | o never, occasional asides, frequent/structural | 0.28 | 0.07 | "you" addressed to the reader | close |

(The body text reports these as "67% vs. 39%" and "28% vs. 7%". Table 16 marks them as ordinal means. Both numbers come from the paper. Also, "Narrator address mode → no direct address" is listed as a **human fingerprint** in Table 17, so reader address is human-elevated on average but not universal.)

## Human-elevated: temporal complexity

| Feature | Paper question | Dim | Options | Human | AI | Nonfiction reading | Fit |
|---|---|---|---|---|---|---|---|
| Depth of Recontextualization After Surprise | How extensively does a revelation force reinterpretation of earlier scenes? | REV | s 1 (none)–5 (complete re-reading) | 3.28 | 2.95 | A late fact that changes how earlier paragraphs read | close |
| Degree of Chronological Discontinuity | How often does the narrative jump across time? | TMP | s 1–5 | 2.40 | 2.12 | Moving between now, then and later | close |
| Nonlinear Framing for Delayed Disclosure | To what extent does the story use time jumps to stage revelations? | REV | s 1 (linear)–5 (heavily fragmented) | 1.96 | 1.68 | Arranging time so a key fact is disclosed late | close |
| Anachrony Intensity | How heavily does the narrative rely on flashbacks or flash-forwards? | TMP | s 1 (absent)–5 (dominant anachronic) | 2.58 | 2.31 | Flashbacks or flash-forwards placed mid-piece | close |

(Body text [paper]: "a human mystery might open at the funeral and spiral backward through decades, while AI tells the same story from first clue to the grand reveal.")

## Human-elevated: narrative diversity

| Feature | Paper question | Dim | Options | Human | AI | Nonfiction reading | Fit |
|---|---|---|---|---|---|---|---|
| Location Variety Scope | How many distinct physical locales does the story inhabit? | SET | o single–multiworld | 1.34 | 1.08 | More than one real place | loose |
| Dialogue-to-Narration Proportion | What proportion of text is direct dialogue vs. narration? | PER | s 1 (no dialogue)–5 (dialogue dominates) | 2.95 | 2.70 | Share of people's own words (quotes) vs author narration | loose |
| Subplot Integration → thematically parallel | How directly do subplots echo the central theme? | PLT | cat (as above) | 42% | 21% | A second thread that echoes the theme from another angle | close |
| Moral Polarity Toward Protagonist → ambivalent/mixed | Does the narrative frame the protagonist's choices as morally clear or ambiguous? | PLT | cat: clearly positive, ambivalent/mixed, clearly negative | 59% | 38% | The author's own position (or the central actor's) framed as mixed | loose |
| Dominant Emotional Expression → explicit labels | How are characters' emotions most commonly conveyed? | AGENT | cat (as above) | 29% | 8% | Feelings named plainly ("I was angry") | close |

---

## Fingerprints (Table 17) [paper]

These come from the six-way task: a feature's importance is concentrated in one source. Arrows are the paper's. **Features listed without an arrow have no stated direction. Don't invent one.** Fingerprint counts: Human 32, Claude 26, GPT 11, Gemini 11, DeepSeek 7, Kimi 3.

Core features hold across all five models, and fingerprints belong to one source [paper]. **[adaptation]** When a core feature and a fingerprint point different ways, follow the core feature at human rates and don't turn the fingerprint into a formula.

Don't add up the counts. They sum to 90, but footnote 15 says 75 fingerprint features. The paper doesn't explain the difference.

| Source | Top fingerprints (Table 17, in order) | Also stated in the body text |
|---|---|---|
| **Human** | character introduction → in-dialogue; breadth of focalization → single focal; narrator address mode → no direct address; overall revelation pacing → back-loaded; literary ambition → crossover genre; +27 more (visibility of withholding, atmospheric techniques, subplot density, naming, twist placement…, no directions given) | — |
| **Claude** | strength of event escalation (no arrow in the table; direction comes from the body text); event-type diversity (no direction); ending temporal scope → epilogue/flashforward; dreams/visions as temporal distortion → no; setting mood → uncanny/haunted; +21 more (event density, conflict modality, relationship trajectory, heteroglossia, closure…) | escalates less than any other source; most uniform narrative voice; reverent/continuist approach to literary tradition (62% vs 39–56% across the other sources); favors epilogues; quiet endings over "avalanche" endings |
| **GPT** | role of gossip and rumor → salient; narrator temporal distance → distant retrospective; reader expectation strategy → subverts; iterative/habitual narration → no; reconciliation/forgiveness → partial/ambiguous; +6 more | gossip as a plot mechanism 64% vs 44–55%; subverts expectations 41% vs 27–36%; ensemble social networks at human levels |
| **Gemini** | protagonist social trajectory → expands; balance of speech → primarily direct; global narrative schema → siege/ordeal; naming practice → named personal name; global chronological structure → frequent flashbacks; +6 more | tidiest endings, extended denouements, bleakest settings (88% bleak/oppressive); defaults to external character description (abstract) |
| **DeepSeek** | narrator presence/visibility (no direction); emotional expression → behavioral cues; plot vs. atmosphere orientation (no direction); backstory placement → evenly interleaved; embedded storytelling scenes (no direction); +2 more (seasons/cyclical time…) | front-loads crucial context that other sources leave until later |
| **Kimi** | character introduction → in-action event; narrative entry frame → in medias res; explicit trait labeling → no | fewest fingerprints; the generic center of the AI distribution |

Six-way per-class F1, narrative-only [paper]: Human 0.89 · Claude 0.77 · GPT 0.73 · Gemini 0.60 · DeepSeek 0.57 · Kimi 0.55. Gemini, DeepSeek and Kimi form a more confused cluster. The paper says narrative structure is "less diagnostic for distinguishing among models that make similar storytelling choices", though "each still has individual quirks".

---

## Method details [paper]

- **Data.** 10,272 human stories from Books3. Gemini 2.5 Flash reverse-engineered a writing prompt from each, and each model wrote from that prompt. Mean words: human 6,403; Claude 6,817; GPT 6,651; Gemini 3,155; DeepSeek 2,946; Kimi 3,274.
- **Pipeline.**
  1. GPT-5.1 extracts a structured JSON template per story across 10 NarraBench dimensions (Figure 8).
  2. GPT-5.1 compares the six templates per prompt on a held-out pool of 600 stories (100 prompts).
  3. GPT-5.1 proposes closed-form features per dimension, run 3 times and unioned: 408 candidates.
  4. Embedding dedup (F2LLM-4B, cosine 0.85) leaves 304 features: 124 categorical, 59 ordinal, 45 scale, 44 binary, 32 multi-select.
- **Templates vs raw text.** Discovering features from raw text surfaced style-heavy features (humor, register, allusion types, imagery). Templates surfaced structure-heavy ones (emotional arcs, relationship trajectories, event density, flashbacks). Only 6 of the top 20 overlapped. This applied to *discovery*.
- **Assignment.** Gemini 3 Flash (minimal thinking) read the **full story** with feature definitions, **one dimension per call**. Coverage was 95.4%, against 68.4% when all features went in a single call; the single call "showed broad systematic dropout, especially in revelation and temporal-structure features".
- **Reliability.** Repeat runs gave Krippendorff's α = 0.90. Human–model Cohen's κ was 0.84 on average (0.91 and 0.77 for two annotators, 240 items, 12 stories); human–human κ was 0.74.
- **Blinding.** Source identities were anonymized in every LLM-facing prompt. Within pairwise template comparisons, presentation order was randomized.
- **Style boundary.** A feature is style if it can only be answered from prose texture. Sensory Density, Depth of Interior Access and Chronological Discontinuity count as non-style. 47 features were excluded as style or style-related, leaving 257 narrative features.

## Results worth knowing [paper]

| Model | Binary macro-F1 | Six-way macro-F1 |
|---|---|---|
| Narrative (257) | 93.2 | 68.4 |
| Core only (30) | 84.8 | 46.5 |
| Core + fingerprint (101) | 91.1 | 63.4 |
| Narrative + style (304) | 96.0 | 77.3 |
| Style only (39 LLM-extracted style features) | 85.8 | 60.4 |
| ModernBERT / stylometric / TF-IDF (raw text) | 99.9 / 99.8 / 99.7 | 99.8 / 99.6 / 99.5 |
| Binoculars (zero-shot) | 55.9 | — |

- **LAMP-edited stories** (278 Gemini stories, Gemini as rewriter): the narrative model scored 93.9 on edited stories vs 95.5 on the originals. Only the narrative classifier was tested on edited text.
- **Single dimensions** (binary): Agents 80.2, Situatedness 77.3, Plot 74.5, Perspective 71.3, Setting 70.6, Social networks 67.9, Events 67.8, Revelation 67.2, Temporal structure 62.0. Removing any one dimension changes the score by −1.2 to +0.3.
- **Convergence.** Human–AI centroid distance averages 6.6, against 4.3 for AI–AI pairs (1.6×). The closest human–AI pair (6.2) is farther apart than the most distant AI–AI pair (6.0). The six most-confused pairs in six-way attribution are all AI–AI.
- **Rarity.** Human stories have a mean rarity percentile of 0.71 vs 0.49 (AUC 0.73, Cohen's d = 0.83). The human story is the rarest of its six 57.8% of the time (chance is 16.7%). The distributions still overlap substantially: the rarest 10% of stories includes 340 human and 487 AI.
- **Controls.** Length matching left the narrative model at 93.2. Topic effects were not significant (Kruskal–Wallis p = 0.46), though binary F1 ranged from 90.0 to 96.2 across topics. Filtering memorization-risk prompts barely changed results (93.18 → 93.23).
