---
name: asd-ste100
description: Use when writing, rewriting, or reviewing documentation that a reader must not misread - runbooks, procedures, READMEs, CLAUDE.md/CONTEXT.md, WARNING text, error messages, tool descriptions, agent prompts - or when the user says "STE", "Simplified Technical English", "ASD-STE100", "controlled language", "make this unambiguous", "plain technical English", "check STE compliance". Not for marketing, fiction, or voice-driven prose (use storyscope / humanizer there).
allowed-tools: Read Write Edit Grep Glob Bash
model: balanced
---

# ASD-STE100 Simplified Technical English for documentation

ASD-STE100 is the controlled-language standard that the aerospace industry uses so that a maintenance technician cannot misread an instruction. It removes two causes of misreading: words with more than one meaning, and sentences with more than one possible structure. Current edition: Issue 9 (January 2025). It has 53 writing rules in 9 sections and a dictionary of about 900 approved words.

This skill applies that discipline to documentation and to text that agents read. The reader of a runbook at 2 a.m., a non-native reader, a translation pipeline, and a downstream agent have the same problem as the technician: no author to ask.

**Core principle:** STE removes ambiguity. It does not remove content. A rewrite that is short and compliant but says something different from the source is a failed rewrite.

## Sources and what this skill takes from each

| Source | What is load-bearing here |
|---|---|
| [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) (MIT) | Modes by text type. Split between structural rules (checkable) and lexical rules (need the dictionary). Hedges are content. AI-habit scan. Text-only default output. The linter in `scripts/ste_lint.py`. |
| [nuelcyoung/asd-ste100](https://github.com/nuelcyoung/asd-ste100) (MIT) | Rule 0 (meaning outranks vocabulary) and the five fidelity passes. Procedure vs description. Part-of-speech discipline. Terminology table. Dictionary access tiers and copyright limits. |
| [STEMG white paper, *ASD-STE100 and AI*](https://www.asd-ste100.org/assets/files/WhitePaper-ASD-STE100_and_AI.pdf) (June 2026) | AI assists, the human author is accountable. Disclose AI assistance. Keep content decisions traceable. Protect confidential content. The standard outranks the tool. |
| ghengis additions | Three modes (adds Certified). Do-not-touch zones for docs. Project glossary file. Change log. Explicit modal-strength table. Eval file. |

This skill is not affiliated with or endorsed by ASD or STEMG. ASD-STE100 is a registered trademark of ASD. STEMG does not endorse any AI tool.

## When to Use

- Write or rewrite a runbook, setup guide, procedure, or troubleshooting section.
- Rewrite WARNING, CAUTION, and NOTE text.
- Write error messages, log messages, tool or function descriptions, and agent or system prompts.
- Clean up READMEs, CLAUDE.md, CONTEXT.md, architecture docs, PR descriptions, and changelogs that read as dense or hedged.
- Review a document for STE compliance and report violations.
- The user must deliver a document that complies with ASD-STE100 (contract, aerospace, defense, regulated manual).

## When NOT to Use

- Marketing, persuasive, or fiction text. Voice is the point there. Use `storyscope` or `humanizer`.
- Legal text, license text, and contract clauses. Flag them. Do not rewrite them.
- Code, identifiers, and generated reference output.
- Content that is wrong or empty. STE fixes form, not substance. A hollow paragraph becomes a short hollow paragraph. Say so instead of polishing it.

## Step 1: Pick the mode

If the user does not name a mode, infer it from the text type. State the mode only when you show the change log.

| Mode | Use for | Enforce |
|---|---|---|
| **Docs** (default) | README, CLAUDE.md, CONTEXT.md, architecture docs, PR text, changelogs, explanations | All structural rules. Lexical rules as a direction only. Keep every hedge as written. |
| **Strict** | Runbooks, procedures, setup steps, WARNING/CAUTION/NOTE, error messages, tool descriptions, agent prompts | All structural rules. One word for one meaning across the document. Modal table below. Change log. |
| **Certified** | The user says the text must comply with ASD-STE100 | Everything in Strict, plus part-of-speech tagging and a word-by-word check against the official dictionary (`words.md`). Verification disclaimer. AI-assist note. |

Never claim Certified-level compliance from Docs or Strict work. Without the official dictionary, you cannot verify the lexical rules.

## Step 2: Mark the do-not-touch zones

Before you change a word, mark what stays exactly as it is:

- Fenced code blocks, inline code, commands, flags, file paths, URLs, and environment variables.
- Identifiers and API field names, even if they contain non-approved words (`retry_backoff`, `/search`).
- YAML or TOML frontmatter keys and values that tools parse.
- Product and proper names.
- Direct quotes and legal or license text.
- Numbers, units, and limits. Never round them and never invent them.

If a do-not-touch item makes a sentence non-compliant, restructure the words around it.

## Step 3: Inventory the propositions (Rule 0)

Before you rewrite a passage, list each fact, relation, condition, and qualifier in it. This list is the test that the output must pass in Step 6. The full procedure and the trap tables are in `fidelity.md`. **Read `fidelity.md` before every Strict or Certified rewrite.**

The four moves when no plain word carries the meaning, in this order:

1. Restructure the sentence.
2. Use an approved verb phrase (`get access to`, `make sure that`, `find the cause of`).
3. Declare a technical noun or technical verb in the project glossary.
4. Keep the accurate word and flag it.

Never take the nearest plain word if it changes the meaning. "Stale" is not "old". "Lose" is not "decrease". "Fail" is not "stop".

## Step 4: Classify each passage

| | Procedure (tells the reader what to do) | Description (tells how something works) |
|---|---|---|
| Voice | Imperative, active only | Active where possible. Passive is permitted when the agent is unknown or not important. |
| Sentence limit | 20 words | 25 words |
| Structure | One instruction per sentence. Numbered steps. | One topic per paragraph. Vary sentence length and construction. |

Do not mix the two in one passage. **Never invent an agent to escape the passive.** If every sentence needs an agent that the source does not name, the passage is a procedure. Write it in the imperative.

## Step 5: Apply the rules

### Structural rules (apply with confidence in all modes)

| Rule | Do | Do not |
|---|---|---|
| Active voice | "The script deletes the file." | "The file is deleted." (unless the agent is unknown) |
| No phrasal verbs (Rule 9.3) | "Start the job." "Remove the panel." | "Kick off the job." "Spin up." "Reach out." |
| One instruction per sentence | "Stop the service. Run the restore." | "Stop the service and run the restore, then check it." |
| Sentence length | 20 words or fewer (procedure), 25 or fewer (description) | Long chains of clauses |
| Split, never delete | Give each proposition its own sentence | Cut a condition or object to fit the limit |
| No semicolons (Rule 8.1) | Two sentences | Any semicolon |
| Condition first | "If the API service runs, do not start the restore." | "Do not start the restore if the API service runs." |
| Noun clusters | 3 words or fewer. 3 is a ceiling, not a target. Keep legal 2- and 3-word clusters. | 4+ stacked nouns, or `of`-chains built from a legal cluster |
| No omitted words | Keep subject, verb, and article | "Files not backed up will be lost." |
| Correct articles | "high CPU use" | "a high CPU use" (uncountable) |
| Paragraphs | One topic, 6 sentences or fewer, topic sentence first | Mixed topics |
| Lists | A numbered list for 3+ steps or conditions | A sequence hidden in one sentence |
| Simple tenses | "We received the report." | "We have received the report." Exception: keep a compound form that carries a hedge or current relevance, and flag it. |
| Safety text | WARNING/CAUTION/NOTE starts with a clear command or condition. Put it before the step it applies to. | A hazard in the middle of a sentence |

### Lexical rules (direction in Docs, enforced in Strict, verified in Certified)

- **One word, one meaning.** One name for one thing and one verb for one action in the whole document. Do not rotate check/verify/confirm or user/customer/client.
- **One part of speech.** `check` is approved as a noun only: "do a check of the valve", not "check the valve". Rules and the tagging procedure are in `words.md`.
- **Verb, not noun (Rule 3.7).** "Analyze the log", not "Perform an analysis of the log".
- **No vague quantifiers.** Replace many, several, some, various, and few with the number. Delete the word if the number is not important. Use "more than one" if the count changes by design.
- **No judgment words.** Replace appropriate, relevant, regular, normal, low-traffic, and large with a measurable condition. If the source gives no number, flag it. Do not invent one.
- **American spelling.**

### Modals: keep the strength of the claim

A hedge is content. A shorter sentence that makes a hedge into a fact states a different claim. This is the most frequent error in STE rewrites.

| Source | Docs | Strict | Certified (only `can`, `must`, `will`) |
|---|---|---|---|
| may / might / could (uncertain) | Keep | Keep. Do not change to "can". | Restate as a condition: "If X, Y can occur." If that changes the claim, keep the source word and flag it. |
| can / may (ability, permission) | Keep | "can" | "can" |
| must / shall (obligation) | Keep | "must" or imperative | "must" or imperative |
| should (recommendation) | Keep | Keep "should", or write "We recommend that you..." Do not change to an imperative. | Flag it. Ask the author: obligation (`must`) or recommendation? |
| may have / could have (past uncertainty) | Keep | Keep and flag the compound tense | Flag it |

The source author decides the strength of a claim. Do not decide it for them.

## Step 6: Verify

1. **Fidelity pass.** Compare the Step 3 proposition list with the output. Every proposition must be present and unchanged. Nothing is added. Every hedge, condition, number, and object of a transitive verb is still there.
2. **Mechanical pass.** Run the linter on the output:
   ```bash
   python scripts/ste_lint.py FILE.md            # Docs
   python scripts/ste_lint.py --strict FILE.md   # Strict / Certified: also flags non-approved modals
   python scripts/ste_lint.py --max-words 20 FILE.md   # procedure-only file
   ```
   The linter is a heuristic. It skips code and frontmatter. It never fails on hedges. If the linter and the standard disagree, the standard wins.
3. **Prose pass.** Read the output as a document. Look for the same sentence opener more than twice in a row, paragraphs of equal length, and `of`-chains.
4. **Glossary pass.** Make sure each term agrees with the project glossary (Step 7).

## Step 7: Keep the project glossary

STE permits project technical nouns and verbs beyond the base dictionary. Use one name for one thing across the whole project, not only across one file.

- Use `docs/ste-glossary.md` in the project. Create it the first time you choose a term in Strict or Certified mode. In Docs mode, read it if it exists. Do not create it.
- Format: `| Term (POS) | Meaning in this project | Names to avoid | Source |`
- Before you name something, look it up. If the glossary has a term, use it.

## Step 8: Output and traceability

The STEMG white paper asks that AI-assisted content decisions stay traceable and that the human author stays accountable.

- **Text the user pasted:** return the rewritten text and nothing else. After the text, add these lines only if they apply:
  - `Kept as-is:` a phrase you did not shorten, and the precision that a shorter version would lose.
  - `Flagged:` a word or claim that the author must decide (unverified word, `should` strength, a missing number).
- **A file in the repo:** edit the file. Then report in one short block: mode, flags, and glossary terms added.
- **Change log (Strict and Certified, or when the user asks for "before/after", "diff", or "which rules"):**

  | Rule | Original | Rewrite |
  |---|---|---|
  | Condition first | "Do not run X unless Y" | "If Y is not true, do not run X." |

- **Certified mode:** add both lines to the deliverable notes, not to the body text:
  - *"Vocabulary was checked against [the official ASD-STE100 Issue 9 dictionary supplied by the user | known rulings and high-risk patterns only]. Full compliance needs verification by a qualified human writer."*
  - *"AI assistance: [scope of the AI work]. The author reviewed and approved the content."* Leave "reviewed and approved" for the human to confirm. Do not mark it as done.

## AI-use guardrails (from the STEMG white paper)

1. **Assist, do not replace.** The author approves the final text. Never say that a document "is STE-compliant". Say what you checked and against what.
2. **Disclose.** For documents that leave the user's own projects (client, contract, regulated), include the AI-assist note.
3. **Traceable.** Every substitution that is not obvious goes in the change log or the flag list.
4. **Confidential.** Do not paste proprietary or client documents into third-party checkers or web tools. If you delegate the work to another model, prefer a local model.
5. **Unusual or safety-critical content.** Model reliability is lowest here. Flag WARNING text and safety limits for human review, even when the rewrite looks correct.

## Scan for AI-writing habits (all modes)

These habits are mechanical to find and frequent in model output:

1. Synonym rotation: one thing with several names.
2. Hedge stacking: "it is important to note that this may potentially help". State the claim at its real strength, or delete it.
3. Nominalization: "perform an analysis of", "provide assistance to".
4. Marketing adjectives: seamless, robust, powerful, cutting-edge, effortless, blazing-fast. Delete them, or replace them with the measurement.
5. Run-on sentences joined by semicolons or dashes.
6. Soft phrasal verbs: spin up, reach out, dive into, kick off.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Nearest-word substitution ("stale" to "old", "lost" to "decrease") | The output is compliant and false | Run the substitution check in `fidelity.md` (Pass 2). Use the four moves. |
| Change "could"/"should" to "can"/imperative to look simpler | The strength of the claim changes | Use the modal table. Flag "should". |
| Delete a condition or a vague instruction to meet the length limit | Information is lost and nobody sees it | Split the sentence. Flag vague content. Do not drop it. |
| Invent an agent ("The team must...") to remove a passive | Fabricated obligation | Reclassify as a procedure and use the imperative |
| Invent a number to replace a vague word ("several minutes" to "5 minutes") | Fabricated fact | Flag it. Ask the author. |
| "This document is now STE-compliant" | No tool can verify that. STEMG endorses no tool. | State what you checked and the dictionary source |
| Rewrite inside code, flags, paths, or identifiers | The commands break | Do-not-touch zones (Step 2) |
| Break every 2-word noun cluster into an `of`-chain | Heavier text than the source | 3 words is a ceiling |
| Rewrite a document in Certified mode with `words.md` but without `fidelity.md` | Substitution without a limit damages content | Always load `fidelity.md` first |
| Polish a paragraph that says nothing | STE fixes form, not substance | Say that it has no content |

## Reference files

- `fidelity.md`: Rule 0 in full. The five fidelity passes, the antonym trap table, articles, noun clusters, and a worked example. **Read for every Strict or Certified rewrite.**
- `words.md`: part-of-speech tagging, derived forms, known dictionary rulings, high-risk word patterns, how to get and use the official dictionary, and copyright limits. **Read for Certified mode and for any word-level ruling.**
- `scripts/ste_lint.py`: deterministic linter for the structural rules (stdlib only). Run `--selftest` after any change to it.

## Cross-References

- **`storyscope`, `humanizer`**: the opposite direction. They give prose a human voice. STE removes voice to remove ambiguity. Do not run both on one passage.
- **`pql-validation`**: run it on agent prompts after the STE pass. STE fixes ambiguity. PQL fixes prompt structure.
- **`writing-skills`**: use Strict mode on SKILL.md bodies and tool descriptions. Do not apply it to frontmatter `description` triggers, because they need the user's phrasing.
- **`report-writing`, `output-formatting`**: STE applies to the procedure and finding text inside a report.
- **`auto-project-sync`**: when it updates CONTEXT.md or MEMORY.md, keep terms in agreement with `docs/ste-glossary.md`.
