# Skeleton template (Mode B step 2: planning the rewrite)

**What the paper did.** The pipeline extracted a structured template per story using a zero-shot JSON schema organized by NarraBench dimension (Figure 8). Those templates were used to **discover** features by comparing sources, because comparing raw text surfaced style features while comparing templates surfaced structural ones. **Scoring** was done differently: the model read the full text, one dimension per call.

**[adaptation]** This skill does **not** score from the skeleton. Score the full text first (Mode B step 1, `features.md`). Then fill in this skeleton to see the piece's structure and plan what to move.

The field names follow Figure 8. Nonfiction notes are in comments. Paper instructions carried over:
- be objective and don't interpret beyond what the text conveys
- use `null` when something isn't present
- write trajectories and sequences with arrows ("state1 -> state2"), complete even when nonlinear
- GLOBAL fields describe the whole piece; LOCAL fields name the paragraph or section

Quote evidence wherever a field allows it.

```yaml
piece:                     # [adaptation] header
  title:
  genre:                   # essay | blog | op-ed | paper section | grant narrative | speech | story
  words:
  author_material:         # notes/transcript/sources beyond the draft, or "none"

agents:
  major_characters:        # nonfiction: the author and the central people in the piece
    - name:                # [GLOBAL] full name as it appears
      role:                # [GLOBAL] max 2 short clauses
      attributes:          # [GLOBAL]
      emotion_trajectory:  # [GLOBAL] initial -> progression -> final
      motivation_trajectory: # [GLOBAL]
      trope:               # [GLOBAL] archetype, if any ("wise mentor", "faceless bureaucracy")
      introduced_by:       # [adaptation, for the core feature] external_desc | in-action | in-dialogue | inner_thought | others_reports
      voice:               # [adaptation] verbatim | paraphrase | none
  supporting_characters:
    - name:
      description:         # one line

social_network:
  relationships:           # [GLOBAL] "A-B: relationship type and quality"

events:
  sequence:                # [LOCAL] ordered beats: who, where, what, when (by paragraph)
  causality:               # [GLOBAL] "event1 -> event2: explanation"
  narrative_schema:        # [GLOBAL] Figure 8: "such as quest, revenge, or coming-of-age". Table 6's schema options: quest/journey, investigation/mystery, transformation/redemption, siege/ordeal, slice_of_life, trial/test/game, heist/caper, frame_confession/memoir

plot:
  themes:                  # [GLOBAL]
  summary:                 # [GLOBAL] 2-3 sentences
  moral:                   # [GLOBAL] one sentence if signaled; else null. Quote where the text states it
  central_obstacle:        # [GLOBAL]
  central_conflict:        # [GLOBAL]
  narrative_archetype:     # [GLOBAL]
  plot_arc:                # [GLOBAL] e.g. "rising action -> climax -> falling action"
  subplots:                # [adaptation, for Subplot Integration] each: thematically parallel | contrasting | independent

setting:
  locations:               # [LOCAL/GLOBAL] with scope
  time_period:             # [GLOBAL]
  atmosphere:              # [GLOBAL]

discourse:
  revelation:
    suspense:              # [GLOBAL] what key information is withheld?
    curiosity:             # [GLOBAL] what causal antecedents are withheld?
    surprises:             # [GLOBAL] what was revealed, and when (paragraph)?
  temporal_order:
    structure:             # [GLOBAL] linear | nonlinear | mixed
    duration:              # [GLOBAL] overall time span
    flashbacks:            # [LOCAL] which paragraphs
    time_jumps:            # [LOCAL] ellipses or leaps in time/place, by paragraph
    scene_duration:        # [LOCAL] approximate duration of major scenes

narration:
  perspective:
    point_of_view:         # [GLOBAL] 1st person | 2nd person | 3rd person limited | 3rd person omniscient
    focalization:          # [LOCAL] whose perspective, by section
    dialogue_speakers:     # [LOCAL] who is quoted, by section
  style:                   # recorded for completeness; style belongs to humanizer, not this skill
    allusions:             # [LOCAL]
    figurative_language:   # [LOCAL]
    imagery:               # [LOCAL]
    sentence_complexity:   # [GLOBAL]
    evaluative_language:   # [LOCAL]

planning:                  # [adaptation] used to rank fixes
  theme_statements:        # every sentence where the author states the lesson, quoted, with paragraph
  resolution:              # how it ends: resolved externally | resolved internally | unresolved; final line quoted
  reader_address:          # quoted instances of "you"/asides, with count
  references:              # named works/people/places vs vague allusions, quoted
```

## From skeleton to moves [adaptation]

| Skeleton field | What to look for | Core features it informs |
|---|---|---|
| `events.sequence`, `temporal_order.*` | Is the order strictly chronological? Where could a fact move later? | Chronological Discontinuity, Anachrony (TMP); Nonlinear Framing (REV) |
| `revelation.suspense/curiosity/surprises` | Is anything withheld? Does a late reveal change an earlier paragraph? | Recontextualization After Surprise, Pre-Threat Investment (REV) |
| `plot.moral`, `planning.theme_statements` | How many times is the lesson stated? | Narratorial Thematic Commentary, Thematic Explicitness (SIT) |
| `events.causality` | One unbroken chain? | Continuity of Main Causal Chain (EVT) |
| `planning.resolution` | Does it end on an internal reframe or on the protagonist's choice? | Mode of Resolution (EVT); Agency in Resolution (PLT) |
| `plot.subplots` | Any thread parallel to the theme? | Subplot Integration (PLT) |
| `agents.*.introduced_by`, `voice` | Credentials first? Paraphrase only? | Character Introduction (AGENT); Dialogue-to-Narration (PER) |
| `agents.*.emotion_trajectory` + evidence | Body metaphors, or named feelings? | Dominant Emotional Expression (AGENT) |
| `setting.*` | Opening grounded in place? Mood mirrored in setting? | Opening Spatial Grounding, Setting as Psychological Mirror (SET) |
| `planning.references` | Named, or vague echoes? | Intertextual Strategy, Reference Explicitness (SIT) |
| `planning.reader_address` | Never, occasional, or constant? | Direct Reader Address (PER), Fourth-Wall Permeability (SIT) |
| `agents.major_characters` (author) | Is the author's own position framed as clearly positive? | Moral Polarity Toward Protagonist (PLT) |

The dimensions the core features span, for the "changes in at least three dimensions" check [adaptation]: **SIT, PLT, EVT, SET, AGENT, PER, REV, TMP** (Social networks has no core feature).
