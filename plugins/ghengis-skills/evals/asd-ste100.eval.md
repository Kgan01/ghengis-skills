# ASD-STE100 — Evaluation

Fixture A: a ~140-word restore runbook section ("Restoring the Brain Database") with marketing adjectives, a semicolon, "may be retained ... depending on disk pressure", "data that can be lost", "kicking off", "check all required dependencies", "should be performed during low-traffic windows because ... could return stale results", a WARNING with "unless ... otherwise ... may be corrupted", and a 33-word passive sequence ending "several minutes on large brains".

Fixture B: a client pump-controller setup doc with YAML frontmatter, "utilizes a cutting-edge PID loop which should generally be tuned on-site; various parameters may need adjustment", a numbered list with an inline `pio` command, "Verify ... confirm ... check" rotation, "Torque the mounting bolts appropriately", and "CAUTION: The impeller could be damaged if the pump is run dry for more than 30 seconds."

Baseline failures observed without the skill (2026-10-06, Sonnet, fixture A): output read cleanly but "stale" became "old" (meaning change), "should be performed" became a bare imperative, "could"/"may" silently became "can", "check all required dependencies" vanished from the body (only mentioned in notes), "several minutes" kept and "not much traffic" introduced (vague), claimed "STE allows them" with no dictionary-verification disclaimer, no glossary, no lint pass, notes suggested an inferred "24 hours" figure.

## TC-1: Meaning fidelity on a runbook (fixture A)

- **prompt:** "Rewrite this runbook section in ASD-STE100 STE so it's ready to commit."
- **assertions:**
  - "stale" is not replaced by "old" (or any word meaning merely "aged"); a phrase meaning "not current" or a flag is used
  - "should" is kept, stated as a recommendation, or flagged — not silently turned into an imperative
  - "could"/"may" (uncertainty) are not silently converted to "can"
  - The dependency instruction survives in the body or is flagged — not deleted
  - No invented numbers (no "24 hours", no "5 minutes", no time window)
  - Vague words ("several", "low-traffic", "large") are flagged
- **passing_grade:** 5/6 must pass

## TC-2: Structural rules applied

- **prompt:** same as TC-1
- **assertions:**
  - No semicolons; no "robust"/"seamlessly"; no "kicking off"
  - WARNING starts with a command or condition and sits before the step it guards
  - The 33-word restore sequence becomes a numbered list or ≤25-word sentences
  - Linter was run on the output (or its findings are reported)
- **passing_grade:** 4/4 must pass

## TC-3: Refuses to certify compliance without the dictionary (fixture B)

- **prompt:** "Client needs this ASD-STE100 compliant for their contract. I don't have the spec PDF. Make it compliant and confirm it's compliant so I can send it today. Fill missing numbers with sensible defaults."
- **assertions:**
  - Does not state the document "is compliant" / "STE-compliant"
  - Includes the fallback disclaimer (checked against known rulings only, not the official Part 2 dictionary)
  - Includes an AI-assistance note with the "reviewed and approved" part left for the human
  - Does not invent the torque value or tuning parameters — flags them for the author
  - Tells the user how to get the free spec (asd-ste100.org request form)
- **passing_grade:** 5/5 must pass

## TC-4: Do-not-touch zones (fixture B)

- **prompt:** same as TC-3
- **assertions:**
  - Frontmatter keys and values unchanged (`retry_backoff_ms: 250`)
  - `pio run -t upload --upload-port COM3` unchanged
  - "30 seconds" kept exactly
- **passing_grade:** 3/3 must pass

## TC-5: Certified-mode word rules

- **prompt:** same as TC-3
- **assertions:**
  - "check" is not used as a verb (or is flagged)
  - "Torque" used as a verb is flagged or replaced
  - Verify/confirm/check rotation collapsed to one verb
  - "could be damaged" handled per the Certified modal row (condition restatement or flag), not deleted
- **passing_grade:** 3/4 must pass

## TC-6: Docs mode stays light

- **prompt:** "Tighten up this README paragraph a bit" with a paragraph containing "may", a semicolon, and "seamlessly"
- **assertions:**
  - "may" is kept as written
  - Semicolon and "seamlessly" removed
  - Output is the rewritten text only (no rule table, no mode announcement)
  - No `docs/ste-glossary.md` is created
- **passing_grade:** 4/4 must pass

## TC-7: Knows when not to fire

- **prompt:** "Punch up this landing-page hero copy so it sells harder."
- **assertions:**
  - STE rules are not applied; points to storyscope/humanizer or just does the copy task
- **passing_grade:** 1/1 must pass
