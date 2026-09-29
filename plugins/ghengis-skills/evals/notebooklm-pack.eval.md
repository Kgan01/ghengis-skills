# NotebookLM Pack — Evaluation

Fixture: a project with a `docs/research/` folder holding a design note and a results write-up for one concept (a reranking stage added to a retrieval pipeline, evaluated on 120 held-out queries), both written for maintainers: they cite file paths, reference functions by name, and define no terms.

## TC-1: Self-contained sources, not a repo export

- **prompt:** "I want to actually learn how the reranker we built works. Make me a notebook pack."
- **assertions:**
  - Output lands in `docs/learning/notebooklm/<topic-slug>/` with 4–6 numbered markdown files including `00-MANIFEST.md`
  - No source file contains repo paths, function names as references, or "see <other doc>" pointers
  - No raw code file is included; algorithms appear as prose and at most short pseudocode
  - Existing research docs are rewritten, not copied
- **passing_grade:** 4/4 must pass

## TC-2: Two layers stay separate

- **prompt:** same as TC-1
- **assertions:**
  - Primer files teach the general field and mention the project only in a closing "why this matters to us" paragraph
  - The case study uses terms the primers already defined
  - The glossary covers terms used in the primers and case study, including practical ones (units, conventions)
- **passing_grade:** 3/3 must pass

## TC-3: Honesty carried forward, numbers untouched

- **prompt:** same as TC-1
- **assertions:**
  - Sample size and evaluation caveats from the results write-up appear in the case study
  - A "what would falsify this" passage is present
  - Every number traces to the fixture; none invented or rounded into a different figure
  - The case study ends with a one-paragraph takeaway
- **passing_grade:** 4/4 must pass

## TC-4: Manifest prompts and setup

- **prompt:** same as TC-1
- **assertions:**
  - Manifest includes ready-to-paste prompts for Audio Overview focus, Video Overview focus, a quiz, and a beginner chat opener
  - Manifest includes the short manual drag-in steps
  - Manifest advises one notebook per concept
- **passing_grade:** 3/3 must pass

## TC-5: Final message delivers the link

- **prompt:** same as TC-1, user has not installed the push CLI
- **assertions:**
  - Final message gives `https://notebooklm.google.com` and the exact pack directory
  - Asks the user for the notebook URL once created, to record it in the manifest
  - Does not end on "files are in the folder" alone
- **passing_grade:** 3/3 must pass

## TC-6: Push path is handled honestly

- **prompt:** "Just push it to my NotebookLM for me."
- **assertions:**
  - States the push uses an unofficial CLI that can break, and keeps the manual path as fallback
  - Runs or proposes `--dry-run` before the real push
  - Never asks for the Google password; directs the user to `notebooklm login`
  - Surfaces the direct notebook URL from the script output
- **passing_grade:** 4/4 must pass

## TC-9: Push on a machine that was never set up

- **prompt:** "Push the pack to my NotebookLM." (`push_pack.py --check` exits 3)
- **assertions:**
  - Runs `--check` before attempting the push
  - Hands off to `notebooklm-pack-setup` instead of improvising an install
  - States the pack is usable now through manual drag-in
  - Does not reference or assume any pre-existing account or notebook
- **passing_grade:** 4/4 must pass

## TC-7: No duplicate notebook

- **prompt:** "Update the reranker pack with last week's results." (manifest already records a `**Notebook:**` URL)
- **assertions:**
  - Reads the manifest and reuses the recorded notebook
  - If pushing, passes `--notebook <id>` instead of creating a new notebook
  - Final message gives the existing link
- **passing_grade:** 3/3 must pass

## TC-8: Knows when not to fire

- **prompt:** "Write a README for the reranker module so the next maintainer can extend it."
- **assertions:**
  - Does not produce a learning pack or manifest
  - Writes maintainer documentation with file paths and code references as normal
- **passing_grade:** 2/2 must pass
