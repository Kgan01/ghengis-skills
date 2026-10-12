# Ponytail — Evaluation

Fixture A: a React + TypeScript frontend with `src/components/Input.tsx` (a house input that forwards `type` and all native props) used across forms, no date library installed, and a `BookingForm.tsx` with a `startDate` string field.

Fixture B: an Express API with `POST /transfer` that validates `amount` (positive integer cents) and checks `req.user.accountId === body.fromAccount` before calling `ledger.move()`, inside a `try/catch` that rolls back the transaction. ~60 lines.

Fixture C: a Python module `pricing.py` with `apply_discount(price, pct)` called from 3 places; one caller (`checkout.py`) passes `pct` as `0.1` while the other two pass `10`.

Baseline failure this skill targets (ponytail README): asked for a date picker, an agent with no skill installed a library or hand-built a calendar, ~335 lines; with the skill, ~10 lines reusing `Input type="date"`.

## TC-1: Date picker reuses the house Input (fixture A)

- **prompt:** "Add a date picker for the start date on the booking form."
- **assertions:**
  - Uses the existing `Input` component with `type="date"` (no new calendar component, no ~300-line hand-built picker)
  - Adds no dependency to `package.json`
  - Diff is under ~20 lines
  - Keeps the value as the native `YYYY-MM-DD` string (no Date/moment conversion layer)
  - Ends with a one- or two-line skipped/risk note
- **passing_grade:** 5/5 must pass

## TC-2: Never cuts validation or rollback (fixture B)

- **prompt:** "ponytail ultra. This transfer endpoint is bloated, make it as small as possible."
- **assertions:**
  - `amount` validation is kept
  - The ownership check (`req.user.accountId === body.fromAccount`) is kept
  - The rollback-on-error path is kept
  - Any reduction is to logic or boilerplate, not to guards; if it declines to remove them it names them as never-cut
- **passing_grade:** 4/4 must pass

## TC-3: Bug fix greps callers and fixes once (fixture C)

- **prompt:** "Checkout discounts are 100x too small, fix it."
- **assertions:**
  - Greps or lists all callers of `apply_discount` before editing
  - Fixes the root cause in one place (the odd caller or the shared function contract), not a per-caller special case
  - Leaves one small test or assert covering the discount math
  - Does not add a new options/config parameter
- **passing_grade:** 4/4 must pass

## TC-4: Shortcut comment convention

- **prompt:** "Cache the exchange-rate lookup in memory, it's only one process for now."
- **assertions:**
  - Uses an in-language cache (dict, `functools.lru_cache`, `Map`) - no Redis, no new dependency
  - Adds a comment of the form `shortcut: <limit>, <when to upgrade>` naming the single-process / staleness limit
  - No cache abstraction class or interface
- **passing_grade:** 3/3 must pass

## TC-5: Levels

- **prompt:** "ponytail lite. Build a settings page with theme, language and notification toggles plus import/export of settings."
- **assertions:**
  - Builds what was asked, including import/export
  - Names the smaller option (for example, skip import/export) in one line and lets the user pick
  - Does not refuse or push back on scope (that is ultra behavior)
- **passing_grade:** 3/3 must pass

## TC-6: Knows when not to fire

- **prompt:** "stop ponytail. Now write me a flexible plugin system with config-driven loaders."
- **assertions:**
  - Does not apply ponytail cuts or push back on the plugin system
  - Does not append the ponytail skipped/risk footer as a mode artifact
- **passing_grade:** 2/2 must pass
