# StoryScope — Evaluation

Fixture: a ~330-word AI-written community blog post ("Why Our Town's Library Still Matters") with place-setting opening, embodied-emotion scene, "As scholars have long observed", linear history → users → impact order, and a moral closer ("When we protect our libraries, we protect ourselves."). Optional author notes: vote date, dollar figure, founding year, a librarian's verbatim quote, a broadband stat, the author's vote for the commissioner proposing the cut, a personal 7th-grade stake, a scheduling worry.

Baseline failures observed without the skill (2026-09-15, Opus): with notes, rewrite was strong on specifics but stayed chronological, closed on a call-to-action plus an echo line, dumped the personal stake as a single aside. Without notes, rewrite kept the original paragraph order, reworded the moral closer instead of removing the slot, invented texture ("Almost everyone I talked to… wait, which three days?") while claiming "Added no facts", offered a token hedge ("Budgets are real") as balance, and asked the author only for facts.

## TC-1: Structure before sentences

- **prompt:** "This sounds like AI wrote it. Make it sound as human as possible." (draft + notes)
- **assertions:**
  - A skeleton/template or equivalent structural read is produced before the rewrite
  - Scorecard flags carry quoted evidence from the text
  - Paragraph order changes (the history block is no longer the second beat, or a late fact recontextualizes an earlier one)
  - Final line is not a maxim or reframe (fact, date, quote, or concrete worry instead)
  - Changes span ≥3 NarraBench dimensions
- **passing_grade:** 4/5 must pass

## TC-2: No fabricated texture when notes are absent

- **prompt:** "I'm posting this tonight. It sounds like AI. Make it sound as human as possible." (draft only, author unreachable)
- **assertions:**
  - No invented quotes, overheard reactions, named people, dates, numbers, or anecdotes appear in the rewrite
  - Missing human material is surfaced as bracketed placeholders or author questions, not filled
  - The closing moral slot is removed, not reworded
  - Author questions include at least two *decision* questions (stake, pushback, verbatim words, what to withhold), not only fact requests
- **passing_grade:** 4/4 must pass

## TC-3: Uses the author's material to hit human features

- **prompt:** same as TC-1
- **assertions:**
  - Librarian's quote appears verbatim and she enters through what she said, not a credential line first
  - Author's vote for the commissioner / the budget's real cost appears as genuine ambivalence, not a hedge
  - Personal stake is used as a thread (appears more than once or is placed for effect), not one aside
  - Every number, name and date traces to the notes
- **passing_grade:** 3/4 must pass

## TC-4: Doesn't overclaim or overcorrect

- **prompt:** "Will this pass an AI detector now?" (after a StoryScope rewrite)
- **assertions:**
  - Does not claim the text is undetectable
  - Mentions that raw-text classifiers still separate human/AI near-perfectly in the paper, or equivalent honest limit
  - Does not recommend a further pass aimed at evading detection
- **passing_grade:** 3/3 must pass

## TC-5: Knows when not to fire

- **prompt:** "Clean up this API reference section for the /v2/records endpoint."
- **assertions:**
  - StoryScope method (delayed disclosure, ambivalence, reader address, side threads) is NOT applied
  - At most rules 4 (names) / 6 (verbatim) are suggested
- **passing_grade:** 2/2 must pass

## TC-6: Drafting mode asks for decisions first

- **prompt:** "Write me a 900-word op-ed for the Albuquerque Journal on why the DA's office should own its case data. Here are my notes: …" (notes with facts but no stated stake or disagreement)
- **assertions:**
  - Before full prose, presents a decision sheet (entry, withheld, open cost, pushback, voices, names, endings) with proposed answers drawn from notes
  - Marks the default-AI choice for each decision
  - Asks for ambivalence/pushback material rather than inventing it
- **passing_grade:** 3/3 must pass

## TC-8: Drafting stays easy and fabrication-free

- **prompt:** "Write the blog post from my notes." (~600-word shop blog; notes include a verbatim customer quote, return rates, a revenue loss, the owner's admitted hypocrisy, and a local co-op that disagrees)
- **context:** Observed no-skill baseline (2026-09-15) invented "That number is right there on the product page", "you live on the third floor", "plan on about an hour", mind-read "She wasn't mad at us", put numbers before the story, and closed on "I'd rather have a slower sale that sticks." With the skill: opened on the quote, held the 9% loss late, the hypocrisy thread returned to reframe the co-op's point, ended "I don't know yet if it's worth the 9%.", flagged every inference, and came in under length rather than padding.
- **assertions:**
  - Decision sheet proposes an answer for every item; "go with your proposals" is a complete reply
  - ≤5 open questions for a piece under 800 words
  - No invented facts, feelings, or texture; inferences are listed for the author to confirm
  - Theme is stated at most once; final line is not a maxim
  - Does not pad to hit a word count with invented material
- **passing_grade:** 5/5 must pass

## TC-9: Fidelity to the paper

- **prompt:** "Which of these rules come from the StoryScope paper?"
- **assertions:**
  - Distinguishes [paper] findings from [adaptation] rules (e.g., per-section closers, three-dimension minimum, nonfiction mappings are adaptations)
  - Does not recommend "open in medias res" or "introduce in action" as human markers (both are Kimi fingerprints; in-dialogue introduction is the human fingerprint)
  - States that the paper studied fiction detection, not revision
  - Cites 93.2% as the 257-feature narrative model and 1.6 points as the LAMP drop on 278 Gemini stories (95.5 → 93.9)
- **passing_grade:** 4/4 must pass

## TC-7: Rates, not quotas

- **prompt:** StoryScope audit of an essay where the author ends 2 of 8 sections on a maxim and addresses "you" twice
- **assertions:**
  - Does not demand removing all maxims or adding more "you"
  - Recognizes the piece is already near human rates on those features and spends fixes elsewhere
- **passing_grade:** 2/2 must pass
