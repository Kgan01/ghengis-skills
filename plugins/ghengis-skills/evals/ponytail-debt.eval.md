# Ponytail Debt — Evaluation

Fixture: a repo with
- `api/rate.py:12` `# shortcut: in-memory limiter, single process; move to Redis at 2+ replicas`
- `web/cache.ts:30` `// shortcut: no eviction, fine under 10k keys`
- `jobs/sync.go:88` `// ponytail: polling every 60s, switch to webhooks when the vendor ships them`
- `docs/keys.md` prose: "Press Ctrl+K, the search shortcut: opens the palette"
- `app/ui.tsx:5` `// keyboard shortcut: Ctrl+K opens search`
- `node_modules/x/index.js` with `// shortcut: vendor hack`
- `src/db.py:40` `# TODO: add retry`

## TC-1: Ledger rows and no-trigger tag

- **prompt:** "ponytail debt"
- **assertions:**
  - Exactly three rows: `api/rate.py:12`, `web/cache.ts:30`, `jobs/sync.go:88`
  - `web/cache.ts:30` is tagged `no-trigger` (it names a ceiling but no upgrade trigger)
  - Each row's ceiling and upgrade come from the comment, not invented
  - Ends with `3 markers, 1 with no trigger.`
- **passing_grade:** 4/4 must pass

## TC-2: Excludes noise

- **prompt:** "List the shortcuts we took."
- **assertions:**
  - `docs/keys.md` prose not listed
  - The keyboard-shortcut comment in `app/ui.tsx` not listed
  - The `node_modules` hit not listed
- **passing_grade:** 3/3 must pass

## TC-3: Custom marker word

- **prompt:** "ponytail debt TODO"
- **assertions:**
  - Greps for `TODO` instead and lists `src/db.py:40`
  - Tags it `no-trigger`
- **passing_grade:** 2/2 must pass

## TC-4: Persist only when asked

- **prompt:** first "ponytail debt", then "save that to a file"
- **assertions:**
  - The first turn writes no file
  - The second turn writes a ledger file (for example `docs/SHORTCUT-DEBT.md`) with the date and summary line
  - Source comments are not edited
- **passing_grade:** 3/3 must pass

## TC-5: Clean repo

- **prompt:** "ponytail debt" on a repo with no markers
- **assertions:**
  - Outputs `No shortcut debt. Clean ledger.`
- **passing_grade:** 1/1 must pass
