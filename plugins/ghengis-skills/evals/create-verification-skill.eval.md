# create-verification-skill — Evaluation

Fixture A: a Next.js + FastAPI repo with `npm run dev` (port 3000), `uvicorn main:app` (port 8000), a Playwright config, no `.claude/skills/` folder, no `.pi/` folder.

Fixture B: a Python CLI repo (`notes create`, `notes search`) with a README quickstart and no browser surface.

Fixture C: fixture A, but the dev server fails to start because a `static/` directory the API mounts is missing.

Baseline failure to prevent: a skill full of `<your-selector>` placeholders, written but never run, saved only where one harness can see it.

## TC-1: Repo interview before questions (fixture A)

- **prompt:** "Make a verify skill for this repo."
- **assertions:**
  - Launch commands and ports come from package.json / README, not from asking the user
  - The existing Playwright setup is reused as the drive harness
  - The user is asked only what the repo cannot answer (e.g. test credentials), if anything
- **passing_grade:** 3/3 must pass

## TC-2: Location works in both harnesses (fixture A)

- **prompt:** same as TC-1
- **assertions:**
  - Canonical copy at `.claude/skills/verify-<app>/SKILL.md` with `name:` and `description:` frontmatter
  - pi exposure via a `.pi/skills/verify-<app>` link/junction or a `.pi/settings.json` `skills` entry
  - Only one real copy of the files exists
- **passing_grade:** 3/3 must pass

## TC-3: Required sections, no placeholders

- **prompt:** same as TC-1
- **assertions:**
  - Launch, Doctor, Drive, Evidence, Cleanup sections exist
  - No `<placeholder>` selectors or commands remain
  - Cleanup kills tracked PIDs, not processes by name
  - `features/README.md` plus 3-5 feature files with the four required H2s in order
- **passing_grade:** 4/4 must pass

## TC-4: Proven before hand-over

- **prompt:** same as TC-1
- **assertions:**
  - The generated skill is executed once: launch, doctor, drive one feature, capture evidence, cleanup
  - Evidence is confirmed to exist after cleanup
  - The report names the evidence location
- **passing_grade:** 3/3 must pass

## TC-5: CLI surface (fixture B)

- **prompt:** "We need a scripted way to prove the notes CLI works."
- **assertions:**
  - Launch is "build/install once, isolated session per drive" (no fake long-lived server)
  - Evidence includes command, stdout, stderr, exit code
- **passing_grade:** 2/2 must pass

## TC-6: Broken base first (fixture C)

- **prompt:** same as TC-1
- **assertions:**
  - The startup failure is fixed or reported precisely before the skill is generated
  - Any created `static/` scaffolding is marked as verification scaffolding and removed in cleanup
- **passing_grade:** 2/2 must pass
