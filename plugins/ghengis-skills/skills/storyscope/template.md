# Skeleton extraction template (Mode B, step 1)

Adapted from the paper's NarraBench extraction prompt (arXiv 2604.03136, Figure 8) for nonfiction. Fill it in **before** judging any sentence. The paper found that comparing raw text surfaced mostly style features (humor, register, imagery), while comparing templates surfaced structural ones (arcs, event density, flashbacks). Only 6 of the top 20 features overlapped. Reduce the piece to its skeleton so you judge its decisions, not its wording.

Quote the text as evidence wherever a field asks for it. Use `null` when the text has nothing.

```yaml
piece:
  title:
  genre:            # essay | blog | op-ed | paper section | grant narrative | speech | story | email
  words:
  author_material:  # what notes, transcript or sources exist beyond the draft? (path or "none")

opening:
  first_move:       # place-setting | thesis | background | scene/moment | quote | number | admission
  evidence:         # first sentence, quoted

disclosure_order:   # paragraph-level sequence, arrows: "announcement -> history -> users -> impact -> moral"
  rule_before_case: # yes/no. Does the principle arrive before the reader has seen the problem?
  withheld_facts:   # anything held back and revealed late (null if nothing)
  late_recontextualization: # a late fact that changes how an earlier paragraph reads (null if none)
  flashbacks:       # where the piece jumps back or forward in time, by paragraph

causal_chain:       # "A -> B -> C", and whether anything breaks into it
threads:
  main:
  side_threads:     # each one with: parallel to the theme? resolved?

people:             # everyone who appears
  - name:
    introduced_by:  # credentials/description | what they said | what they did | others' report
    voice:          # verbatim quote | paraphrase | none
    evidence:

references:
  named:            # specific works, people, statutes, datasets, places
  vague:            # "experts", "studies", "scholars have long observed", quoted

emotion:
  rendering:        # plain labels | embodied metaphor | behavior | setting-as-mirror
  evidence:
  mind_reading:     # inner states given to people the author couldn't know (quoted)

stance:
  toward_sources:   # agrees with all | complicates some | disagrees with some
  toward_own_position: # clean | concedes a cost | genuinely torn
  evidence:

author_on_page:
  first_person:     # none | occasional | throughout
  reader_address:   # count of "you" addressed to the reader
  asides_admissions: # quoted

endings:
  section_closers:  # the last sentence of each section/paragraph block, quoted, marked [maxim] or [fact]
  final_line:       # quoted, marked [maxim] | [reframe] | [call-to-action] | [fact] | [open question]
  resolution_mode:  # author wins on merits | external events | left open | internal reframe/acceptance

voice_uniformity:   # do sections differ in rhythm/register? note any seam between author-dictated and generated parts
escalation:         # does tension or stakes rise, or stay flat?
```

## From skeleton to scorecard

Map the fields to `features.md` sections:

| Skeleton field | features.md rows |
|---|---|
| `endings.*` | A: narrator states the theme, explicitness; C: resolution mode |
| `references.*` | A: vague echoes; D: named, balanced mix |
| `emotion.*` | B: all rows; G: plain labels |
| `disclosure_order.*`, `opening` | C: opening grounding, investment before the threat; F: all rows |
| `threads.*`, `causal_chain` | A: thematic unity; C: causal chain, no subplots; G: parallel subplot |
| `people.*` | C: external-description introduction; G: dialogue proportion |
| `stance.*` | G: ambivalent framing; Claude fingerprint: reverent toward sources |
| `author_on_page.*` | E: both rows |
| `voice_uniformity`, `escalation` | Claude fingerprint: uniform voice, flat escalation |

Seven dimensions to count for the "at least three dimensions changed" check: **Situatedness** (A, D, E), **Agents** (B emotion, people), **Setting** (B sensory, place), **Events** (causal chain, resolution mode), **Plot** (threads, ambivalence, resolution agency), **Temporal/Revelation** (F, opening), **Perspective** (dialogue proportion, reader address).
