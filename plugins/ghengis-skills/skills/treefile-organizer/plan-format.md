# Plan Format

The treefile-organizer pipeline produces two artifacts at stage 3:

- `<project>/.claude/treefile-organizer/plan.md` — human-readable, the user's primary view
- `<project>/.claude/treefile-organizer/plan.json` — machine-readable, the validator's input

This file specifies the schema for `plan.json` and the structure expected in `plan.md`.

## plan.json Schema

```json
{
  "version": "1",
  "created_at": "ISO 8601 timestamp",
  "project_root": "absolute path",
  "project_type": "fastapi-service | react-nextjs-app | flutter-app | python-library | typescript-library | unknown",
  "language_mix": {
    "python": "<file count>",
    "typescript": "<file count>",
    "javascript": "<file count>"
  },
  "anchors": [
    "list of paths NOT to move (relative to project_root)"
  ],
  "moves": [
    {
      "from": "relative path",
      "to": "relative path",
      "language": "python | typescript | javascript",
      "layer": "api | service | data | ui | infrastructure | utility",
      "reason": "one-line explanation",
      "imports_in": [
        {
          "file": "relative path of the file containing the import",
          "line": "<line number>",
          "old": "the exact text being replaced",
          "new": "the replacement text"
        }
      ]
    }
  ],
  "topo_order": [
    "moves[].from in dependency-safe execution order"
  ],
  "estimated_imports_to_rewrite": "<integer>",
  "risk": "low | medium | high",
  "warnings": [
    "any non-blocking concerns surfaced during proposal"
  ]
}
```

### Field Rules

- `from` and `to` are relative to `project_root`. Always use forward slashes regardless of OS.
- Every entry in `topo_order` MUST appear in `moves[].from`.
- `topo_order` MUST be a valid topological sort: if file A imports file B, and both are moving, B comes before A.
- `imports_in[].old` MUST match the exact substring at `file:line` so the rewrite is unambiguous.
- `imports_in[].new` MUST be valid for the target language (Python: dotted-path or relative; TypeScript: ES module specifier).
- `anchors` contains both files (e.g., `pyproject.toml`) and directories (e.g., `.github/workflows/`).

### Example

```json
{
  "version": "1",
  "created_at": "2026-05-06T00:30:00Z",
  "project_root": "/Users/kgan/Desktop/myproject",
  "project_type": "fastapi-service",
  "language_mix": {"python": 47, "typescript": 0, "javascript": 0},
  "anchors": ["pyproject.toml", ".github/workflows/", "scripts/deploy.sh"],
  "moves": [
    {
      "from": "src/utils/auth.py",
      "to": "src/auth/middleware.py",
      "language": "python",
      "layer": "service",
      "reason": "auth code belongs in auth/, not utils/; consumed by 4 files in routes/",
      "imports_in": [
        {"file": "src/main.py", "line": 12, "old": "from utils.auth import verify_token", "new": "from auth.middleware import verify_token"},
        {"file": "src/routes/users.py", "line": 5, "old": "from ..utils.auth import verify_token", "new": "from ..auth.middleware import verify_token"}
      ]
    }
  ],
  "topo_order": ["src/utils/auth.py"],
  "estimated_imports_to_rewrite": 2,
  "risk": "low",
  "warnings": []
}
```

## plan.md Structure

The human-readable plan should answer four questions in this order:

1. **What's the project, and what's drifted?** — One paragraph: project type, what the layout looks like now, and what's wrong.
2. **What's the proposed shape?** — A tree diagram showing the target layout. Use indentation, not box-drawing characters (easier to copy).
3. **What moves and why?** — A grouped list: moves grouped by source-dir → target-dir, with the count and one-line rationale per group.
4. **What's the risk?** — Risk level + the top 3 things that could go wrong + the recovery plan if they do.

Do NOT dump the raw JSON in plan.md. The validator reads plan.json; the user reads plan.md.

### Example plan.md skeleton

```markdown
# Reorganization Plan — myproject

**Project type:** FastAPI service
**Generated:** 2026-05-06 00:30 UTC
**Risk:** low

## What's drifted

Auth code lives in `src/utils/`, mixed with unrelated helpers. 4 route files import
from `utils.auth`, which makes the auth boundary invisible to anyone reading the
import graph. Tests follow the source structure (good); models are in `src/data/`
(good).

## Proposed shape

src/
  auth/
    middleware.py        ← from utils/auth.py
  data/                  (unchanged)
  routes/                (unchanged)
  utils/
    helpers.py           (unchanged — actually generic)

## Moves

**utils/ → auth/** (1 file, low risk)
- `utils/auth.py` → `auth/middleware.py` — auth concern, consumed by 4 files

## Anchors (not moving)

- pyproject.toml, package.json, .github/workflows/, scripts/deploy.sh

## Risk

Low. 2 import statements need rewrite across 2 files. No circular dependency
risk. If anything fails, rollback is `git reset --hard <sha>`. Recommend tagging
the pre-state for easy reference.

## Proceed?

Reply "yes proceed" to execute, or describe what to change and I'll re-plan.
```

## Why Two Files

The split is intentional:

- **Validator can't reliably parse free-form markdown.** A structured JSON is what the build-validate chain's Validator stage operates on.
- **User shouldn't have to read JSON.** Markdown is for human review; the user shouldn't be asked to validate path strings or topo order.
- **Audit trail.** plan.json is the canonical record of what was attempted; plan.md is the human-friendly diff. Both go into `report-<timestamp>.md` after execution.
