---
name: code-intelligence
description: Use when analyzing codebases, understanding architecture, tracing dependencies, or building mental models of unfamiliar code -- covers AST parsing patterns, 6-layer architectural classification, import graph analysis, and structural code search
allowed-tools: Read Grep Glob
---

# Code Intelligence

Methodology for understanding codebases structurally -- classifying files into architectural layers, tracing dependencies through import graphs, and using AST-level analysis to extract meaningful code structure. This skill transforms an unfamiliar codebase from "a pile of files" into a navigable mental model.

This is a codebase analysis methodology, not a specific tool. Apply it by structuring how you explore, classify, and reason about code -- using Glob, Grep, and Read strategically rather than reading files at random.

## When to Use

- **Onboarding to an unfamiliar codebase** -- building a mental model from scratch
- **Architecture review** -- understanding how a system is organized before making changes
- **Dependency analysis** -- tracing what depends on what, finding circular dependencies
- **Impact analysis** -- before modifying a function, understanding who calls it and what it calls
- **Code review** -- understanding the structural context of a change
- **Refactoring planning** -- identifying architectural boundaries, god objects, misplaced code

## When NOT to Use

- **Single-file edits** where you already know the file and its context
- **Simple bug fixes** where the scope is obvious
- **Writing new code from scratch** (no existing codebase to analyze)

## 6-Layer Architectural Classification

Every codebase, regardless of language or framework, can be classified into 6 architectural layers. This classification tells you WHERE a file fits in the system and WHAT role it plays.

### The Layers

| Layer | Role | Contains |
|-------|------|----------|
| **API** | External interface | Routes, endpoints, controllers, request handlers |
| **Service** | Business logic | Orchestration, domain logic, agents, engines |
| **Data** | Persistence | Models, repositories, database access, stores, schemas |
| **UI** | Presentation | Components, views, templates, screens, widgets |
| **Infrastructure** | Configuration | Config files, middleware, Docker, CI/CD, env files |
| **Utility** | Shared helpers | Utils, helpers, shared functions, core libraries |

### Classification by Path Patterns

Files are classified by matching their path against glob patterns. First match wins, evaluated in layer priority order (API > Service > Data > UI > Infrastructure > Utility). Unmatched files default to Utility.

**API layer patterns:**
- `*_routes.py`, `*/routes/*.py`, `*/api/*.py`, `*/endpoints/*.py`
- `*routes*`, `*endpoint*`, `*/api*`
- `*controller*`, `*handler*` (common in Express/Spring)

**Service layer patterns:**
- `*/agents/*.py`, `*agent*.py`, `*/services/*.py`, `*_service.py`
- `*service*`, `*_engine.py`, `*engine*`
- `*/orchestration/*.py`, `*orchestrat*`

**Data layer patterns:**
- `*/models/*.py`, `*model*.py`, `*/stores/*.py`, `*_store.py`
- `*/graph/*.py`, `*graph*`, `*/memory/*.py`, `*memory*`
- `*/vectors*.py`, `*vector*`, `*/schema*.py`
- `*/repositories/*.py`, `*_repository.py`

**UI layer patterns:**
- `*/components/*.tsx`, `*/components/**/*.tsx`
- `*/screens/*.dart`, `*/screens/**/*.dart`
- `*/features/*.dart`, `*/features/**/*.dart`
- `*.tsx` (React components), `*/ui/*.py`

**Infrastructure layer patterns:**
- `deploy/*`, `*deploy*`, `*Dockerfile*`, `*docker-compose*`
- `*/config/*.py`, `*config*.py`
- `*.yaml`, `*.yml`, `*.env`, `*.env.*`, `*.toml`, `*.cfg`, `*.conf`
- `Caddyfile`, `*infra*`

**Utility layer patterns:**
- `*/utils/*.py`, `*utils*`, `*/helpers/*.py`, `*helper*`
- `*/lib/*.py`, `*lib*`, `*/core/*.py`, `*core*`

### Layer Classification in Practice

To classify files in a codebase using Claude Code tools:

```
Step 1: Glob for all source files
  Glob("**/*.py") or Glob("**/*.ts") etc.

Step 2: Classify each file by matching its path against layer patterns
  - First check API patterns (routes, endpoints, controllers)
  - Then Service patterns (services, agents, engines)
  - Then Data patterns (models, stores, repositories)
  - Then UI patterns (components, screens)
  - Then Infrastructure patterns (config, deploy, docker)
  - Default: Utility

Step 3: Group results into a layer map
  API: [list of files]
  Service: [list of files]
  Data: [list of files]
  ...
```

### Layer Resolution Priority

When a file matches multiple layers, the first match in priority order wins:

1. API (highest priority -- if it handles HTTP requests, it is an API file)
2. Service
3. Data
4. UI
5. Infrastructure
6. Utility (default/catch-all)

## AST-Based Code Analysis

Abstract Syntax Tree (AST) parsing extracts structural information from source code without executing it. This gives you function definitions, class hierarchies, imports, and exports -- the skeleton of the code.

### What AST Parsing Provides

| Information | What It Tells You |
|-------------|-------------------|
| **Function definitions** | Every function/method, its name, line span |
| **Class definitions** | Every class, its methods, its inheritance |
| **Import statements** | What each file depends on |
| **Export statements** | What each file exposes to others |
| **Decorators** | Metadata like `@app.get("/path")`, `@login_required` |

### Language-Agnostic AST Node Types

Tree-sitter (the most common AST engine) uses language-specific node types that map to universal concepts:

**Functions:**
- Python: `function_definition`
- TypeScript/JavaScript: `function_declaration`, `method_definition`
- Dart: `function_signature` + `function_body`
- Kotlin: `function_declaration`

**Classes:**
- Python: `class_definition`
- TypeScript/JavaScript: `class_declaration`
- Dart: `class_definition`
- Kotlin: `class_declaration`, `object_declaration`

**Imports:**
- Python: `import_statement`, `import_from_statement`
- TypeScript/JavaScript: `import_statement`
- Dart: `import_or_export`
- Kotlin: `import_header`

### Supported File Types

| Extension | Language |
|-----------|----------|
| `.py` | Python |
| `.ts`, `.tsx` | TypeScript |
| `.js`, `.jsx` | JavaScript |
| `.dart` | Dart |
| `.kt`, `.kts` | Kotlin |

### When AST Is Unavailable

If tree-sitter or equivalent parsing is not available, fall back to character-based chunking: split source files into overlapping windows (~1000 chars with ~100 char overlap). This loses structural awareness but still allows content-based search and analysis.

## Import Graph Analysis

Import statements define the dependency structure of a codebase. Extracting and analyzing them reveals architecture, coupling, and potential problems.

### Building the Dependency Graph

For each source file:
1. Parse import statements (via AST or regex)
2. Resolve relative imports to file paths
3. Record directed edges: `source_file -> imported_file`

**Python imports to resolve:**
```python
import os                          # stdlib, skip
from pathlib import Path           # stdlib, skip
from myapp.services import UserService  # local, resolve to file
from .utils import helper          # relative, resolve from current package
```

**TypeScript/JavaScript imports to resolve:**
```typescript
import React from 'react'              // external package, skip
import { UserService } from './services/user'  // local, resolve
import type { Config } from '../config'        // local type import
```

### What the Import Graph Reveals

**Circular dependencies:** File A imports B, B imports C, C imports A. These create fragile coupling and make testing difficult. Search for cycles in the directed graph.

**High-connectivity modules (potential god objects):** Files that are imported by many others are central to the system. If they are also large, they may be doing too much.

**Orphan modules:** Files that are not imported by anything and do not serve as entry points. These may be dead code.

**Layer violations:** A Data layer file importing from the API layer, or a Utility file importing a Service -- these indicate architectural boundary violations.

### Detecting Import Issues with Claude Code

```
Find circular deps:
  1. Grep for import statements in all source files
  2. Build a map: file -> list of files it imports
  3. Walk the graph looking for cycles

Find high-connectivity modules:
  1. Count how many files import each module
  2. Sort by count descending
  3. Files imported by 10+ others are architectural pillars -- examine carefully

Find layer violations:
  1. Classify all files into layers
  2. Check import edges against allowed directions:
     API -> Service -> Data (ok)
     Data -> API (violation)
     Utility -> Service (violation)
```

### Allowed Dependency Directions

```
API  -->  Service  -->  Data
 |          |            |
 +----------+------------+--->  Utility
 |          |            |
 +----------+------------+--->  Infrastructure (config only)

UI  -->  Service  (via API calls or direct import)
UI  -->  Utility
```

**Red flags:**
- Data layer importing API layer
- Utility importing Service or API
- Infrastructure importing Service directly
- Circular dependencies at any level

## Structural Code Search

Go beyond text search to search by code structure -- finding all functions that match a pattern, all classes that inherit from a base, all files that follow a convention.

### Search Strategies

**Find all route handlers:**
```
Grep for decorator patterns: @app.get, @router.post, app.use, @Route
```

**Find all classes inheriting from a base:**
```
Grep for: class \w+\(BaseModel\), class \w+ extends Component, class \w+ implements Interface
```

**Find all functions that return a specific type:**
```
Grep for: -> List\[, -> Optional\[, -> Dict\[, : Promise<
```

**Find call chains (who calls this function):**
```
Step 1: Grep for the function name across the codebase
Step 2: For each caller, grep for who calls THAT function
Step 3: Build a call tree up to the entry point
```

**Find all files matching a structural pattern:**
```
Glob for route files: **/*routes*.py, **/*controller*.ts
Glob for test files: **/test_*.py, **/*.test.ts, **/*.spec.ts
Glob for config files: **/*.yaml, **/*.toml, **/.env*
```

### Identifying Architectural Boundaries

Architectural boundaries separate subsystems. Look for:

1. **Directory structure** -- Top-level directories often represent major boundaries
2. **Import patterns** -- Groups of files that only import each other form a module boundary
3. **Shared interfaces** -- Files that define types/interfaces used across boundaries
4. **Entry points** -- Files that serve as the "front door" to a subsystem

## Codebase Understanding Methodology

A 5-step process for building a mental model of any codebase. Execute these steps in order, using Claude Code tools strategically.

### Step 1: Identify Entry Points

Entry points are where execution begins or where external requests arrive.

**What to search for:**
- `main.py`, `index.ts`, `main.dart`, `main.go` -- application entry points
- Route registration files -- where HTTP endpoints are wired up
- `package.json` scripts -- `"start"`, `"dev"`, `"build"` reveal entry commands
- `Dockerfile` CMD/ENTRYPOINT -- what actually runs in production

**Tools to use:**
- `Glob("**/main.*")` -- find main files
- `Glob("**/index.*")` -- find index files
- `Grep("app.listen|app.run|uvicorn|createServer")` -- find server startup

### Step 2: Map the Layer Structure

Classify the codebase into the 6 layers.

**How to do it:**
1. `Glob("**/*.py")` (or appropriate extension) to get all source files
2. Look at the directory structure -- `ls` the top-level directories
3. Classify directories into layers based on naming conventions
4. Verify by reading a sample file from each directory

**Output:** A layer map showing which directories/files belong to which layer.

### Step 3: Trace Key Flows

Pick 2-3 important operations (e.g., "user logs in", "data is saved", "a report is generated") and trace them end-to-end.

**How to trace a flow:**
1. Start at the entry point (route handler, API endpoint)
2. Read the handler to see what it calls
3. Follow the call chain: handler -> service -> data access -> response
4. Note: where is input validated? where is auth checked? where does data persist?

**Tools to use:**
- `Read` the route handler file
- `Grep` for function names to find their definitions
- `Grep` for function calls to find who invokes them
- Follow imports to navigate between files

### Step 4: Identify Patterns

After tracing 2-3 flows, patterns emerge. Document them.

**Common patterns to identify:**
- **Auth pattern**: How is authentication enforced? Middleware? Per-route decorators?
- **Data access pattern**: ORM? Raw SQL? Repository pattern? Direct database calls?
- **Error handling pattern**: Try/catch at boundaries? Global error handler? Custom exceptions?
- **Config pattern**: Env vars? Config files? Dependency injection?
- **Testing pattern**: Unit tests? Integration tests? What is mocked?

### Step 5: Find Anomalies

Anomalies are files or patterns that do not fit the established conventions. They are often the source of bugs, tech debt, or security issues.

**What to look for:**
- **Files that do not fit the layer pattern** -- a utility file with route handlers, a model file with business logic
- **Circular dependencies** -- modules that import each other
- **God objects** -- files with 20+ functions or 500+ lines that do too many things
- **Dead code** -- files not imported by anything and not entry points
- **Inconsistent patterns** -- one module uses raw SQL while others use the ORM
- **Missing tests** -- core modules without corresponding test files

**Tools to use:**
- `Grep` for files imported by many others (high fan-in)
- `Glob("**/test_*.py")` vs `Glob("**/*.py")` to find untested modules
- Read anomalous files to understand why they deviate

## Practical Tool Strategy for Claude Code

When analyzing unfamiliar codebases, use tools in this order for maximum efficiency:

### Broad Discovery (minutes 0-2)

```
Glob("**/*.py")           -- or *.ts, *.go, etc. -- get the full file list
Glob("**/package.json")   -- find project boundaries
Glob("**/*.md")           -- find documentation
Read the README or CLAUDE.md if present
```

### Structure Mapping (minutes 2-5)

```
ls on top-level directories to understand organization
Glob("**/*routes*")       -- find API layer
Glob("**/*service*")      -- find service layer
Glob("**/*model*")        -- find data layer
Glob("**/test*")          -- find test layer
```

### Targeted Investigation (minutes 5+)

```
Grep("pattern")           -- search for specific code patterns
Read(specific_file)       -- deep-read files identified as important
Grep("function_name")     -- trace call chains
Grep("import.*module")    -- trace dependencies
```

### Key Principle

Start broad, narrow down. Never start by reading a random file. Always establish the big picture (entry points, layer structure, major directories) before diving into specifics. This prevents wasting time on peripheral code when the core architecture is elsewhere.

## Directories to Skip During Analysis

When walking a codebase, skip these directories to avoid noise:

- `__pycache__`, `.mypy_cache`, `.pytest_cache` -- Python caches
- `node_modules` -- npm dependencies (thousands of files)
- `.git` -- version control internals
- `.venv`, `venv`, `env` -- Python virtual environments
- `dist`, `build`, `.next` -- build output
- `.dart_tool`, `.idea`, `.gradle` -- IDE/build caches
- `coverage` -- test coverage output

## Code Graph Output

The result of a full codebase analysis can be structured as a code graph:

```json
{
  "files": [
    {
      "path": "src/routes/user.py",
      "layer": "api",
      "language": "python",
      "symbols": [
        {"name": "get_user", "type": "function", "lines": [10, 25]},
        {"name": "create_user", "type": "function", "lines": [28, 50]}
      ],
      "imports": ["src/services/user_service.py", "src/models/user.py"],
      "hash": "a1b2c3d4"
    }
  ],
  "layers": {
    "api": ["src/routes/user.py", "src/routes/auth.py"],
    "service": ["src/services/user_service.py"],
    "data": ["src/models/user.py"],
    "utility": ["src/utils/validators.py"]
  },
  "dependency_edges": [
    {"source": "src/routes/user.py", "target": "src/services/user_service.py"},
    {"source": "src/services/user_service.py", "target": "src/models/user.py"}
  ]
}
```

This graph enables:
- Visualizing architecture at a glance
- Detecting layer violations automatically
- Finding circular dependencies
- Measuring coupling between modules
- Tracking changes over time (via file hashes)

## Anti-Patterns

| If you notice... | The problem is... | Fix it by... |
|-----------------|-------------------|-------------|
| Reading files one by one without a plan | No discovery phase | Starting with Glob to map the full file set, then classifying into layers |
| Spending 10 minutes in utility files | Bottom-up analysis trap | Starting from entry points and tracing top-down through key flows |
| Cannot explain how a request flows through the system | Missing flow tracing | Picking a specific operation and tracing it from route handler to database and back |
| Every file seems equally important | No layer classification | Classifying files into layers; API and Service files are usually most important |
| Modifying code without understanding callers | Missing impact analysis | Grepping for the function/class name to find all call sites before changing it |
| Assuming directory names match their contents | Path-only classification | Reading a sample file from each directory to verify the classification |
