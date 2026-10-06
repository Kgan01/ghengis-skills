# Meaning Fidelity: the gate that outranks the dictionary

Adapted from `references/meaning-fidelity.md` in [nuelcyoung/asd-ste100](https://github.com/nuelcyoung/asd-ste100) (MIT). Additions for this skill: the modal pass, the vague-content pass, and the traps found in the ghengis baseline test.

STE exists to remove ambiguity, not content. A sentence that uses only plain words but states something false, vague, or incomplete is a worse failure than a sentence that keeps one flagged word. The author is responsible for the content. The rules control the wording. They never permit a change to what the text says.

## The four moves

When no plain or approved word carries the meaning, use these moves in this order:

1. **Restructure** the sentence so that different words carry the same idea. Most cases end here.
2. **Use an approved verb phrase**: `get access to` (access), `make sure that` (check), `find the cause of` (diagnose).
3. **Declare a technical noun or verb** in `docs/ste-glossary.md`.
4. **Keep the accurate word and flag it**, with the reason.

Do not take the nearest plain word and accept the change in meaning. That is the most damaging error of an AI rewrite, because the output looks compliant and reads well.

## Pass 1: Proposition inventory (before you rewrite)

List each fact, relation, condition, and qualifier. After the rewrite, check each one:

- [ ] **Present.** Nothing is silently dropped. A vague instruction ("check all required dependencies") is still an instruction. Keep it, make it specific from the source, or flag it.
- [ ] **Unchanged.** No fact is altered to fit a word.
- [ ] **Nothing added.** No invented agents, numbers, causes, durations, frequencies, or obligations.
- [ ] **Hedges intact.** See Pass 3.
- [ ] **Objects intact.** A transitive verb keeps its object: "increase its capacity", not "increase".

## Pass 2: Substitution safety (every replaced word)

1. Write the meaning of the source word in its context.
2. Write the meaning of the candidate word.
3. If the two meanings are different, the substitution is not valid. Go to the four moves.
4. Do not present an unverified word as "approved".

**Trap table.** These pairs are close enough to pass a quick read and wrong enough to matter:

| Do not use | For | Because |
|---|---|---|
| `old` | stale | Stale data is out of date relative to a source. Old data can be current. Write "results that are not current" or "results from before the restore". |
| `decrease` | lose, delete, corrupt | A decrease changes a quantity. A loss removes data. |
| `fall` | decrease | In STE, `fall` means movement down by gravity only. |
| `stop` | fail, crash | A stop can be intentional. A failure is not. |
| `find` | detect, monitor | Finding is one event. Monitoring is continuous. |
| `change` | migrate, convert, update | The source named a specific operation. |
| `make sure that` | test, validate | Use it only for confirmation, not for a formal test procedure. |
| `help` | let, permit, enable | "Help X to Y" means partial help. "Let X Y" means capability. |
| `many`, `multiple`, `several` | each other | Each is a vague quantifier. Swapping one for another fixes nothing. Use the number or "more than one". |
| `that` after a negated verb | whether | "Does not show that X works" asserts X. "Does not show whether X works" questions X. |

## Pass 3: Modal strength

A modal states how sure the author is. Confidence is content.

| Change | Why it is wrong |
|---|---|
| "may be corrupted" to "is corrupted" | Possibility becomes fact |
| "could return stale results" to "can return old results" | "can" states a known capability. "could" states an uncertain risk. Two meanings change in one sentence. |
| "should be performed" to "Do the restore" | A recommendation becomes an order |
| "can be more important" to "is more important" | A qualified claim becomes absolute. `can` is approved, so the deletion was not necessary. |
| "may have failed" to "failed" | The system only suspected the failure |

Use the modal table in `SKILL.md`. When the target mode does not allow the source modal, restate the claim as a condition or flag it. Do not choose a strength for the author.

## Pass 4: Do not invent an agent

Rule 3.5 asks for active voice in descriptions "as much as possible", not at any cost. Passive is permitted when the agent is unknown or not important.

| Source | Fabricated rewrite | Better |
|---|---|---|
| "Backups should be taken frequently." | "The teams must make backups frequently." | Procedure: "Make backups [interval: flag]." Description: "Backups are made at [interval]." |
| "Snapshots are taken nightly." | "The administrator takes snapshots each night." | "The backup job makes a snapshot each night." only if the source names the job. Otherwise keep the passive. |

**Repetition check:** if the same subject opens more than two sentences in a row ("The system...", "The teams must..."), you invented an agent or missed a procedure.

## Pass 5: Do not trade prose quality for compliance

These are rule items (Rules 2, 4, and 6.5), not style preferences.

**Articles.** "Do not omit articles" does not mean "add an article everywhere". No `a`/`an` on uncountable nouns ("high CPU use"). No `the` on a generic class ("application errors increase"). Choose one treatment of `data` (singular or plural) and record it in the glossary.

**Noun clusters.** 3 words is the ceiling. Keep legal clusters.

| Over-corrected | Correct |
|---|---|
| "the times of the database queries" | "the database query times" |
| "the errors of the application" | "the application errors" |
| "main landing gear shock absorber assembly" (5 words) | "the shock absorber assembly of the main landing gear" |

**Chained nominalizations.** "go from the detection of a problem to the diagnosis" becomes "find a problem, find its cause, and then correct it".

**Vary construction (Rule 6.5).** In a description, mix a conditional sentence, a list, and a short sentence after two long ones. A page of "The X must do Y" is a violation.

## Pass 6: Split, do not delete. Flag, do not invent.

Meet the 20/25-word limits by splitting:

| Source (28 words) | Wrong | Right |
|---|---|---|
| "A rollback is a possible step if the last release caused the incident, but it will not help if the cause is a data migration." | "A rollback is a possible step." | "If the last release caused the incident, a rollback is a possible step. If a data migration caused the incident, a rollback does not correct the problem." |

Replace vague content only with information from the source. If the source has no number, the output has no number:

| Source | Wrong (invented) | Right |
|---|---|---|
| "can take several minutes" | "takes 5 minutes" | "can take more than one minute [Flagged: give the measured time]" |
| "during low-traffic windows" | "between 02:00 and 04:00" | "when traffic is low [Flagged: give the request rate or the time window]" |
| "snapshots are taken nightly" | "you can lose 24 hours of data" | Keep "each night". 24 hours is an inference. Flag it as a question for the author. |

## Worked example (from the baseline test)

**Source:** "Restores should be performed during low-traffic windows because the `/search` endpoint could return stale results while the restore is running."

**Baseline rewrite without the skill:** "Do the restore when there is not much traffic. During a restore, the `/search` endpoint can return old results."

Failures: `should` became an order (Pass 3). `could` became `can` (Pass 3). `stale` became `old` (Pass 2). "low-traffic" is still vague and has no flag (Pass 6). The causal link "because" is gone (Pass 1).

**Strict rewrite:**

> We recommend that you do the restore when traffic is low. During the restore, the `/search` endpoint could return results that are not current.
>
> Flagged: "traffic is low": give the request rate or time window. "We recommend": confirm whether this is a recommendation or an obligation (`must`).

The causal link is now carried by the order of the two sentences. If the reader must see the cause, write: "If you do the restore when traffic is high, more requests could get results that are not current."

## Report unresolved words

An honest flag is a deliverable with one open item. A silent bad substitution is an incorrect document.

> `stale` (adj): kept as "not current". No plain single word carries "out of date relative to the source". Declare "stale result" as a technical noun if the project uses it often.
