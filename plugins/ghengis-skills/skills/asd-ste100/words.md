# Words: part of speech, dictionary rulings, and dictionary access

Adapted from `references/pos-analysis.md`, `references/dictionary.md`, and `references/dictionary-access.md` in [nuelcyoung/asd-ste100](https://github.com/nuelcyoung/asd-ste100) (MIT).

**This file finds violations. It does not choose replacements.** Every replacement must pass substitution safety in `fidelity.md` (Pass 2). Never use this file without `fidelity.md`.

## Copyright and accuracy limits

- The Part 2 dictionary (about 900 approved words and about 1,200 non-approved words) is copyrighted by ASD. Do not reproduce it in a deliverable or in this repo. Quote single rulings only.
- The standard is free, but you must ask for it with a form at [asd-ste100.org/STE_downloads.html](https://www.asd-ste100.org/STE_downloads.html). The site sends a link by email.
- Do not use unofficial copies from other websites. They are often old issues with different rulings.
- No tool can guarantee STE compliance. The human writer gives final approval.

## Dictionary access, in order of preference

1. **The user's official PDF.** Ask: "Do you have a copy of ASD-STE100 Issue 9? It is free from asd-ste100.org after a short request form." If the user gives a path, search Part 2 with the part-of-speech marker as printed (`install (v)`, `check (n)`). Reading the user's own copy to check words is normal use. Do not bulk-extract Part 2.
2. **The website.** Use it only to confirm the current issue and to give the user the request page. The dictionary is behind the form.
3. **The fallback.** Use the rulings and patterns in this file. Put this line in the deliverable notes: *"Vocabulary was checked against known rulings and high-risk patterns only, not against the official ASD-STE100 Part 2 dictionary. Full compliance needs verification against the official standard."*

## Dictionary format (when you have the PDF)

| Column | Content | Convention |
|---|---|---|
| 1 | Word and its part of speech | UPPERCASE = approved. lowercase = not approved. |
| 2 | The one approved meaning, or the approved alternatives | UPPERCASE |
| 3 | STE example | |
| 4 | Non-STE example | |

An entry approves a word **for its listed part of speech only**. A word can be in the dictionary and still be a violation in your sentence.

## The rule: three matches

A word passes only if all three match the entry:

1. The form is listed, or it is a declared technical noun or verb.
2. The part of speech as used matches the entry.
3. The meaning as used matches the one approved meaning.

Record every ruling as *word + POS*: "`check` (v): not approved". A finding of "`check`: approved" is not usable.

## Procedure

1. **Build the terminology table first.** List every name used for each thing. Choose one. Record it in `docs/ste-glossary.md`.
2. **Extract content words as occurrences, not unique strings.** One word in two sentences can have two parts of speech.
3. **Tag each occurrence with its POS in context.** Look out for:

   | In context | POS | Why it is easy to miss |
   |---|---|---|
   | "**Check** the valve." | verb (imperative) | First word of a sentence looks like a noun in a list |
   | "Do a **check** of the valve." | noun | Same string, different ruling |
   | "the **required** parts" | adjective (past participle) | Takes the ruling of `require` (v) |
   | "the **operating** pressure" | modifier in a technical noun | Legal only inside a declared technical noun |
   | "**Torque** the bolt." | noun used as verb | Invisible to a word-list check |
   | "before the **installation**" | noun (nominalization) | Needs its own ruling |

4. **Reduce derived forms to the base and rule on the base first.**
   - Past participle as adjective: legal only if the base verb is approved or declared. `install` (v) is approved, so "the installed component" passes. `require` is not approved, so "the required parts" fails.
   - `-ing` form: never a verb. Legal as a technical noun ("the opening") or inside one.
   - Nominalization: approval of the verb does not approve the noun. `install` (v) does not approve `installation` (n).
   - Noun used as verb: fails if the entry lists the noun only.
5. **Look up each occurrence with its POS marker.**
6. **Scan the high-risk patterns below.** They fail reviews even in short, active sentences.
7. **Fix or justify each failure** with the four moves in `fidelity.md`. Report each failure with POS, ruling, and ruling source (official dictionary or fallback).

## Known rulings (Issue 9, from public sources)

| Word | Ruling | Use instead |
|---|---|---|
| `start` (v) | Approved. `begin`, `commence`, `initiate` are not. | `start` |
| `check` | Approved as a noun only | `make sure that`, `examine`, or `do a check of` |
| `require` | Not approved, so `required` fails too | `necessary` (adj), or "you must have" |
| `fall` (v) | "Move down by gravity" only | `decrease` for a value |
| `about` (prep) | "Concerned with" only | Give the number, not "approximately" |
| `close` (v) | Two meanings: move together to stop passage, and operate a circuit breaker | Not for "close a ticket" |
| `can` (v) | Approved: ability or possibility | Replaces may/might/could only when the meaning is ability or possibility, not uncertainty |
| `must` (v) | Approved: obligation | Replaces shall. Replaces should only if the author confirms obligation. |
| may, might, could, should, would, shall | Not approved | See the modal table in `SKILL.md` |

Do not treat `can` and `must` as banned. They carry meaning. Do not delete them from a source sentence.

## High-risk patterns (skill guidance, not dictionary text)

| Pattern | Examples | Handling |
|---|---|---|
| Vague quantifiers | many, much, several, some, various, numerous, few, most | Give the number, delete, or use "more than one" when the count changes by design. Never invent the number. |
| Subjective words | appropriate, relevant, regular, normal, large, low-traffic, important, critical | Give a measurable condition from the source, or flag it |
| Judgment instructions | "use your judgment", "depends on", "if possible" | Give an "If X, do Y" rule. If the source has no rule, flag it. |
| Vague predicates | "have value", "cause a change", "have an effect" | Subject-verb-object: who does what, under which condition |
| Collocations | "sudden increase", "data loss", "an increase in latency" | Keep the pairing and its preposition, or declare it a technical noun |
| Abstract nominalizations | optimization, configuration, installation, identification | Verb phrase with an agent from the source, or a declared technical noun |
| Multi-meaning verbs | run, apply, review, change, check, close | One meaning only. If you need a different meaning, choose a different word. |

## Technical nouns and technical verbs

STE permits terms from the subject field that are not in the dictionary, for example "hydraulic pump assembly", "to ream", `pgvector`, "HNSW index", "snapshot". Acceptable sources: official documentation, drawings, glossaries, terminology databases. A non-approved word inside a technical noun becomes part of that term. Keep non-approved words in technical terms to a minimum. One person should approve new glossary entries.

## Spelling

American English (Merriam-Webster). colour to color, centre to center, organise to organize.
