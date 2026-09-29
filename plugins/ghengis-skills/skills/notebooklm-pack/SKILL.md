---
name: notebooklm-pack
description: Use when the user wants to learn a concept from one of their own projects via NotebookLM or another study tool - "make me a notebook pack", "I want to actually learn X we built", "turn this into study material / a slideshow / a podcast", "export this concept for NotebookLM". Produces an upload-ready source pack of self-contained markdown docs (subject primers, case study, glossary, manifest with prompts) and ends with the notebook link. Not for project documentation or dashboards.
allowed-tools: Read Write Edit Grep Glob Bash
model: balanced
---

# NotebookLM Learning Pack

Turn a project concept into an upload-ready **source pack** for NotebookLM: a
small set of self-contained markdown documents that teach (a) the general
subject and (b) exactly what the user built, so NotebookLM's chat, Audio
Overview (podcast), Video Overview (narrated slides), quizzes, and study
guides have clean grounded material.

**Core principle:** NotebookLM only knows what's in the sources. Repo docs
fail as sources. They assume codebase context, cite file paths, and skip
fundamentals. Write for a smart reader with ZERO access to the repo.

## When to Use

- User names a concept from their work they want to *understand*, not just use
  ("I want to actually learn how our retrieval pipeline ranks results / what
  permutation testing is / why the scheduler is built this way")
- User asks for study material, a slideshow, a podcast, flashcards, or a
  "notebook" about something they built
- After finishing a research study or shipping a system the user says they
  want to internalize

## When NOT to Use

- User wants project *documentation*. That's a README/docs task; write for
  maintainers instead
- User wants a live dashboard or status page. That's a UI task
- The concept is standard textbook material with no project tie-in. Point
  NotebookLM at public sources (it ingests URLs and YouTube directly); a pack
  adds value only when private work is part of the material
- User wants a course plan across many topics. Use `learning-paths`, then
  build one pack per concept

## The Pack Format

Output directory: `<project>/docs/learning/notebooklm/<topic-slug>/`

| File | Content | Layer |
|---|---|---|
| `00-MANIFEST.md` | What the pack is, upload checklist, suggested NotebookLM prompts (audio focus, video focus, quiz, exam), recorded notebook URL | meta |
| `01-primer-<subject>.md` | The general subject, textbook-style: definitions, mechanisms, intuition, worked examples. No project references until a final "why this matters to us" paragraph | learn the field |
| `02-primer-<second-subject>.md` | Optional second primer when the concept spans two fields | learn the field |
| `03-case-study-<what-we-built>.md` | Narrative of the actual build: observation → hypothesis → method → numbers → what shipped → caveats. All jargon already defined in primers | learn the build |
| `04-glossary-faq.md` | Every term of art, one-line definitions; FAQ anticipating the user's questions | reference |

4–6 files, each 1,500–4,000 words. One pack = one concept. Multiple concepts =
multiple packs (and multiple notebooks, because NotebookLM grounds per-notebook).

Patterns that hold up across packs:

- **Primers are reusable.** A primer on a method the user leans on often
  serves many packs. Copy it into the new pack and rewrite only the final
  "why this matters to us" paragraph. Build a primer library over time.
- **Case studies want an act structure:** observation → first analysis →
  the trap NOT fallen into → the real finding → what shipped → honesty box.
  The "trap avoided" act carries most of the teaching value.
- **End the case study with a one-paragraph takeaway.** It becomes the
  spine of NotebookLM's audio and video summaries.
- **Glossary earns practical entries** (units, time zones, naming
  conventions), not just theory terms. Those are what block comprehension.

## Writing Rules (where naive exports fail)

1. **Self-contained or it's useless.** No repo paths, no "see CLAUDE.md", no
   assumption the reader can open code. Translate code into explained design
   ("the worker retries a failed job three times, waiting longer each
   time", not the code).
2. **Never upload raw code files.** NotebookLM learns from prose. If an
   algorithm matters, describe it in words plus a tiny pseudocode block.
3. **Two layers, clearly separated.** Primer docs teach the field and would
   survive in any textbook; the case study applies them. Mixing layers makes
   the audio overviews mushy.
4. **Carry the honesty forward.** Sample sizes, how it was tested, known
   limits, "not validated yet". Study material that omits the caveats
   teaches overconfidence. Include a "what would falsify this" passage in
   every case study.
5. **Real numbers, restated in words.** "Correct on 84 of the 120 test
   cases" beats a table NotebookLM might skim. Tables are fine but narrate the
   headline above them. Every number must trace to the project's own
   results; never invent or round into a nicer figure.
6. **Name files for citations.** NotebookLM cites source names.
   `03-case-study-retrieval-reranker.md` reads well in a citation;
   `notes_final_v2.md` doesn't.
7. **Seed the manifest with prompts.** Users get far more from NotebookLM
   with a good focus prompt. Always include ready-to-paste prompts for:
   Audio Overview focus, Video Overview focus, a quiz request, and a
   "teach me like I'm new to this field" chat opener.
8. **Keep secrets out.** The pack leaves the machine. No API keys, client
   names, private hostnames, or credentials in any source file.
9. **Only this user's material.** Build the pack from the project in front
   of you. Never carry content, examples, or notebook links from another
   person's packs into it.

## Process

1. **Sweep the raw material.** Project research docs, design notes, memory
   files, commit history for the concept. These are inputs, never outputs.
2. **Check for an existing pack and notebook.** Look in
   `docs/learning/notebooklm/` and read any `00-MANIFEST.md` for a recorded
   `**Notebook:**` URL before creating anything.
3. **Pick the primers.** One per field the concept rests on. Reuse from
   earlier packs where one fits.
4. **Write primers, then the case study, then the glossary.** The glossary
   is built from terms the first two actually used.
5. **Write the manifest last,** with the four prompts and the short
   user-side setup steps.
6. **Deliver:** ask whether they want it pushed or will drag the files in.
   For a push, run `push_pack.py --check` first; if it does not say
   `Ready to push`, hand off to `notebooklm-pack-setup`. Then give the
   notebook link.

## Automated push (optional, unofficial, consumer accounts)

There is no usable official API for a **consumer** NotebookLM subscription.
The official notebook-creation API needs NotebookLM **Enterprise**
licensing; a plain Google Cloud or Gemini key does not unlock it. The
consumer account can be driven through the unofficial `notebooklm-py` CLI,
which mimics the web client using the user's own browser cookies.

`<skill_dir>/scripts/push_pack.py <pack_dir> [--audio]` creates the notebook,
uploads every `NN-*.md` source (skipping the manifest), and optionally kicks
off the Audio Overview using the manifest's focus prompt. It is CLI-driven,
uses only the standard library, never touches Google credentials, and prints
the login command if auth is missing.

```
python <skill_dir>/scripts/push_pack.py --check
python <skill_dir>/scripts/push_pack.py <pack_dir> --dry-run
python <skill_dir>/scripts/push_pack.py <pack_dir> --audio
```

**Rules for using the push path:**

- **The notebook goes to the account of the person running it.** Nothing in
  this plugin points at any account. The session is the user's own, stored
  on their machine under `~/.notebooklm/`. With several Google accounts,
  pass `--profile <name>`.
- **Setup is a separate skill.** If `--check` exits 3 (CLI missing) or 2
  (not logged in), run `notebooklm-pack-setup`. The user signs in through
  the browser; you never handle their Google password.
- **It's unofficial and can break.** Undocumented Google endpoints, and
  automating a consumer product is a terms-of-service gray area. Say so, and
  always offer the manual drag-in path as the fallback. Never present push as
  guaranteed.
- **Not idempotent.** Re-running creates a second notebook. Pass
  `--notebook <id>` to target an existing one.
- **Always `--dry-run` first** and show the user what will be created.
- The CLI often installs to a per-user scripts directory that is off PATH;
  the script probes the common locations.

## ALWAYS deliver the notebook link (final-message requirement)

Every run of this skill MUST end with a clickable link to the notebook in
the final message to the user. The link is the deliverable, not the files.

- **Pushed pack:** `push_pack.py` prints the notebook id and URL. Surface
  the direct link `https://notebooklm.google.com/notebook/<id>` verbatim.
- **Manual drag-in path:** give `https://notebooklm.google.com` plus the
  exact pack directory to drag from. After the user confirms they created
  the notebook, ask for its URL and echo it back so it lands in the
  conversation record.
- **Existing notebook:** if the manifest already records a URL, give that
  link instead of creating a duplicate.
- Whenever a notebook URL becomes known, append it to the pack's
  `00-MANIFEST.md` as a `**Notebook:** <url>` line so future sessions find it.

## User-Side Setup: manual drag-in (put a short version in every MANIFEST)

1. notebooklm.google.com → sign in with the subscribed Google account.
2. **New notebook per pack/topic.** Sources ground the whole notebook, so
   mixing topics muddies every generated output.
3. Add sources → upload the pack's `.md` files directly (markdown is
   supported; Google Docs, PDFs, URLs, YouTube also work as supplements).
4. Studio panel → **Audio Overview** for the podcast (use the customize
   field with the manifest's focus prompt), **Video Overview** for the
   narrated-slides version, plus Study Guide / FAQ / Mind Map buttons.
5. Chat is grounded and cited; use the manifest's opener prompts.
6. Supplement with 1–2 public sources (a survey paper URL, a YouTube
   lecture) so the notebook can contrast "the field" with "what we did."

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Dumping existing repo docs or research files unedited | They assume context the notebook doesn't have | Rewrite self-contained; repo docs are inputs, never outputs |
| Uploading source code | NotebookLM summarizes prose, not programs | Prose plus pseudocode descriptions |
| One mega-doc | Citations and navigation degrade | 4–6 focused docs |
| Cheerleading the results | Teaches overconfidence | Keep every caveat; add falsification criteria |
| Skipping the manifest prompts | Generic overviews waste the material | The prompts are half the value; always include |
| One notebook for the whole project | Every output blends unrelated topics | One notebook per concept |
| Ending with "files are in the folder" | The user still has no notebook | End with the notebook link |
| Re-running push on an existing pack | Creates a duplicate notebook | Check the manifest, pass `--notebook <id>` |
| Presenting push as an official integration | It is unofficial and may break | State that, dry-run, keep the manual path ready |

## Cross-References

- `notebooklm-pack-setup`: one-time install and sign-in for the push path.
- `learning-paths`: sequencing across many concepts. Build the path there,
  then one pack per concept here.
- `tutoring`: live Socratic teaching in chat. This skill produces material
  for study outside the session.
- `content-writing` / `report-writing`: writing for an outside audience.
  This skill writes for one learner who built the thing.
- `hallucination-detector`: run over the case study when numbers are dense.
