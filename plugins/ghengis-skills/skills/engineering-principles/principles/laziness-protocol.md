# Laziness Protocol

> Ported from pstack `skills/principle-laziness-protocol/SKILL.md` (MIT, Lauren Tan / poteto). Index: `../SKILL.md`.

**Canonical source: the `ponytail` skill.** Load it and follow it. Ponytail owns the smallest-complete-change ladder, "prefer deletion", "minimize the diff", the never-cut list and the `shortcut:` convention. This file does not repeat those rules.

Aim for the most result with the least code and complexity.

pstack's protocol adds four structural rules that ponytail does not spell out. Apply them together with ponytail:

- **Maintain a flat call hierarchy.** Avoid deep call chains. A rich interface that hides substantial work is not a deep call chain. If answering a question requires tracing through more than 3 files or layers, flatten it.
- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple flag.
- **Question the threading.** If a task asks you to pass a new signal through types, schemas, pipelines, or similar layers, stop and look for a more direct path.
- **Sweat the small leaks.** Remove tiny pass-throughs, representation leaks, and duplicated choices before they spread. Small leaks compound into permanent coordination costs.

**The test:** If a human developer would find the code exhausting to maintain, it is a bad solution.

Other principles that cite this one ([build-the-lever](build-the-lever.md), [attack-the-premise](attack-the-premise.md)) mean: build or change the smallest thing that does the job, per `ponytail`.
