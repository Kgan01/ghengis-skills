# Import Rewriting (Per-Language Rules)

When a file moves, every import that pointed at its old path must be rewritten to point at its new path. Rules differ by language. This file documents the patterns for v1 (Python + TypeScript/JavaScript).

## Python

### Absolute imports

```python
# Before move: src/utils/auth.py
from utils.auth import verify_token

# After move to src/auth/middleware.py
from auth.middleware import verify_token
```

Rewrite the dotted path. Preserve the import-style (`from X import Y` vs `import X.Y`).

### Relative imports

```python
# Before — src/routes/users.py imports from src/utils/auth.py
from ..utils.auth import verify_token

# After — auth.py moved to src/auth/middleware.py, users.py stays put
from ..auth.middleware import verify_token
```

Recompute the relative depth (`.` = same package, `..` = parent, etc.) based on the **new positions of both source and target**. If the source file ALSO moves, recompute based on its new location.

### `__init__.py` re-exports

If a moved file's containing package has an `__init__.py` that re-exports it:

```python
# src/utils/__init__.py before
from .auth import verify_token

# After auth.py moved out of utils/
# REMOVE the re-export line entirely. The new package gets its own __init__.py if needed.
```

Don't leave dead re-exports — they cause confusion and silent failures.

### sys.path-relative imports

If the project uses `sys.path.insert(0, ...)` to enable absolute imports without packages:

```python
# Before
sys.path.insert(0, "src")
from utils.auth import verify_token
```

These rewrites are mechanical IF the sys.path target is stable. If a move would invalidate the sys.path layout (e.g., moving the directory that's on sys.path), refuse the move and surface the conflict.

### `if TYPE_CHECKING:` imports

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from utils.auth import AuthContext  # type-only, but still needs rewrite
```

These are real imports for path-rewrite purposes. Treat them like regular imports.

### Edge cases to handle

- **Star imports** (`from utils.auth import *`): rewrite the module path; the `*` stays.
- **Aliased imports** (`from utils.auth import verify_token as vt`): rewrite the path; alias stays.
- **Multi-line imports** (`from utils.auth import (\n    verify_token,\n    refresh_token,\n)`): rewrite the path on the `from` line; the parenthesized list is unaffected.
- **String-quoted module names** (`importlib.import_module("utils.auth")`): grep for them; flag for manual review. Don't auto-rewrite — the string could be a config value, not a literal.
- **Setup.py / pyproject.toml package paths**: `packages = ["utils", "auth"]` or `[tool.setuptools.packages.find] where = ["src"]` — if the move changes the package layout, the build config needs an update too. Flag in plan.md, don't auto-rewrite.

## TypeScript / JavaScript

### Relative ES module imports

```typescript
// Before — src/routes/users.ts imports src/utils/auth.ts
import { verifyToken } from '../utils/auth';

// After auth.ts moved to src/auth/middleware.ts
import { verifyToken } from '../auth/middleware';
```

Recompute the relative path. Drop the `.ts` extension if absent in the source; preserve it if explicit. Match the project's existing convention (check 5 sample imports in the project to detect).

### Path aliases (tsconfig.json `paths`)

```json
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@auth/*": ["src/auth/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}
```

```typescript
// Before
import { verifyToken } from '@utils/auth';

// After auth.ts moved
import { verifyToken } from '@auth/middleware';
```

Two cases:
1. **Existing alias still points correctly** → rewrite to use the existing alias if it covers the new path
2. **No alias for new path** → use a relative import OR add a new alias to tsconfig.json (flag in plan.md, don't silently mutate config)

NEVER delete or modify existing tsconfig aliases without explicit user consent. They may be used by code outside the moved files.

### `package.json` exports field

```json
{
  "exports": {
    "./auth": "./dist/utils/auth.js"
  }
}
```

If a move changes a path that's referenced in `exports`, that's a package-level change. Flag in plan.md as a high-risk warning. Refuse to auto-rewrite — exports are public API.

### Re-exports (barrel files)

```typescript
// src/utils/index.ts before
export { verifyToken } from './auth';
```

After move:
- If `auth.ts` moved out of `utils/`, REMOVE the re-export line from `utils/index.ts`.
- If a new barrel makes sense at the destination (e.g., `src/auth/index.ts` re-exporting `middleware.ts`), CREATE it (only if there's evidence the project uses barrels — check sibling dirs).

Don't proliferate barrels. If the project doesn't use them elsewhere, don't introduce new ones.

### CommonJS `require()`

```javascript
const { verifyToken } = require('../utils/auth');
```

Treat like ES module imports for rewrite purposes. Pattern matches similarly.

### Dynamic imports

```typescript
const mod = await import('../utils/auth');
```

Static-string dynamic imports CAN be rewritten safely. Variable-based dynamic imports (`import(modulePath)`) cannot — flag for manual review.

### JSX / TSX

Same import rules as their JS/TS siblings. JSX itself doesn't change anything.

### Edge cases to handle

- **Type-only imports** (`import type { X } from '...'`): rewrite the path; keep the `type` keyword.
- **Side-effect imports** (`import './styles.css';`): rewrite the path. If the moved file is a CSS/asset, ensure the new path resolves.
- **Default + named** (`import authMiddleware, { verifyToken } from '../utils/auth';`): rewrite the path; default and named bindings stay.
- **String-quoted module names in tools** (Webpack `require.resolve('utils/auth')`, Jest mock paths): flag for manual review.

## Mixed-Language Projects

If a Python file imports a TypeScript bundle path (rare, but happens with build outputs), or a TypeScript file references a Python script path (also rare):

- These cross-language references are usually in config files (Procfile, Dockerfile, build scripts), not in source code.
- Flag any cross-language path reference for manual review. Don't auto-rewrite across languages.

## Verification

After every batch of rewrites, run a fast check before moving on:

**Python:**
```bash
python -c "import ast; ast.parse(open('<rewritten_file>').read())"
```

**TypeScript:**
```bash
# Cheap syntax check
npx tsc --noEmit --skipLibCheck <rewritten_file>
# OR
node -c '/path/to/rewritten_file.js'  # for plain JS
```

If either fails, halt the move batch and report the exact file + line where the rewrite produced invalid syntax.

## What This Skill Does NOT Do

- **Doesn't rename symbols.** If `verify_token` is a poorly named function, this skill won't suggest renaming. That's a refactor, not a reorg.
- **Doesn't merge files.** If two files belong together, the user has to ask for that explicitly. Treefile-organizer moves; it doesn't combine.
- **Doesn't optimize imports.** Existing unused imports stay unused. Existing import order stays. The skill rewrites paths, not contents beyond the path.
- **Doesn't fix circular imports.** If the project has cycles, the skill detects them and reports — but doesn't try to break them. That's a design decision.
