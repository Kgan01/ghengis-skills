# Code Intelligence -- Evaluation

## TC-1: Happy Path -- 6-Layer Architectural Classification
- **prompt:** "Classify these files into architectural layers: `src/routes/user.py`, `src/services/auth_service.py`, `src/models/user.py`, `src/components/Dashboard.tsx`, `deploy/Dockerfile`, `src/utils/validators.py`, `src/config/settings.py`, `src/agents/email_agent.py`."
- **context:** Tests the 6-layer classification system with files that match different layer patterns. Each file should map to exactly one layer based on path pattern matching with priority rules.
- **assertions:**
  - Classifies `src/routes/user.py` as API layer (matches `*/routes/*.py` pattern)
  - Classifies `src/services/auth_service.py` as Service layer and `src/agents/email_agent.py` as Service layer (matches `*/services/*.py` and `*/agents/*.py`)
  - Classifies `src/models/user.py` as Data layer (matches `*/models/*.py`)
  - Classifies `src/components/Dashboard.tsx` as UI layer (matches `*/components/*.tsx`)
  - Classifies `deploy/Dockerfile` as Infrastructure layer and `src/utils/validators.py` as Utility layer
- **passing_grade:** 4/5 assertions must pass

## TC-2: Happy Path -- Import Graph and Dependency Analysis
- **prompt:** "Analyze the imports in this Python project. `routes/user.py` imports from `services/user_service.py`. `services/user_service.py` imports from `models/user.py`. `models/user.py` imports from `routes/user.py` (to get a request type). `utils/helpers.py` imports from `services/auth_service.py`. Which dependency rules are violated?"
- **context:** Tests import graph analysis for circular dependencies and layer violations. The model importing from routes is both a circular dep and a layer violation (Data -> API). The utility importing from services is also a layer violation.
- **assertions:**
  - Detects the circular dependency: routes/user.py -> services/user_service.py -> models/user.py -> routes/user.py
  - Flags the Data -> API layer violation: models/user.py importing from routes/user.py (Data layer must not import from API layer)
  - Flags the Utility -> Service layer violation: utils/helpers.py importing from services/auth_service.py
  - References the allowed dependency directions: API -> Service -> Data is valid, reverse is not
  - Recommends specific fixes (e.g., extract the request type to a shared schema/types module to break the cycle)
- **passing_grade:** 4/5 assertions must pass

## TC-3: Quality Check -- Codebase Understanding Methodology
- **prompt:** "I just joined a new team and need to understand their Python backend. The repo has 200+ files. Walk me through how to build a mental model of this codebase."
- **context:** Tests the 5-step codebase understanding methodology: identify entry points, map layer structure, trace key flows, identify patterns, find anomalies. Must prescribe the correct tool strategy.
- **assertions:**
  - Step 1: Identify entry points by searching for `main.py`, `index.*`, server startup patterns (`uvicorn`, `app.run`), Dockerfile CMD/ENTRYPOINT
  - Step 2: Map the layer structure by globbing all source files, classifying directories into the 6 layers, and verifying by reading sample files
  - Step 3: Trace 2-3 key flows end-to-end (e.g., user login) from route handler through service to data access
  - Step 4: Identify recurring patterns (auth pattern, data access pattern, error handling, config, testing)
  - Step 5: Find anomalies (files not fitting layer patterns, circular deps, god objects with 500+ lines, dead code, missing tests)
- **passing_grade:** 4/5 assertions must pass

## TC-4: Edge Case -- Anomaly Detection
- **prompt:** "Here's what I found in our codebase: `utils/payment_handler.py` is 800 lines with 25 functions and handles Stripe webhooks, invoice generation, and refund processing. `models/report_generator.py` contains route handlers and HTML rendering. `services/database.py` is imported by 15 other files. `tests/` has 10 test files but `services/` has 20 service files."
- **context:** Tests the anomaly detection capability: god objects, misplaced files, high-connectivity modules, and missing test coverage.
- **assertions:**
  - Flags `utils/payment_handler.py` as a god object (800 lines, 25 functions, multiple concerns) that belongs in Service layer, not Utility
  - Flags `models/report_generator.py` as misplaced (route handlers belong in API layer, not Data layer -- violates layer classification)
  - Flags `services/database.py` as a high-connectivity module (imported by 15+ files makes it an architectural pillar to examine carefully)
  - Flags the test coverage gap (10 test files for 20 service files suggests core modules lack corresponding tests)
  - Recommends splitting the god object into separate single-concern modules (payment, invoicing, refunds)
- **passing_grade:** 4/5 assertions must pass

## TC-5: Happy Path -- Structural Code Search Strategy
- **prompt:** "I need to find all API endpoints in a FastAPI app, determine which ones require authentication, and identify which ones accept file uploads. Show me the search strategy."
- **context:** Tests structural code search using the documented patterns for route handlers, auth decorators, and input types. Must use Glob and Grep strategically per the tool strategy section.
- **assertions:**
  - Searches for route handlers using decorator patterns: `@app.get`, `@app.post`, `@router.get`, `@router.post`, etc.
  - Searches for auth requirements using dependency patterns: `Depends(require_auth)`, `dependencies=[Depends(...)]`
  - Searches for file upload indicators: `UploadFile`, `File(...)`, `multipart/form-data`
  - Uses the correct tool order: Glob first for broad discovery (`**/*routes*.py`, `**/*api*.py`), then Grep for pattern matching within discovered files
  - Classifies each endpoint as protected or public based on auth mapping results
- **passing_grade:** 4/5 assertions must pass

## TC-6: Quality Check -- Code Graph Output
- **prompt:** "Generate a code graph for a small project with these files: `src/routes/auth.py` (functions: login, logout), `src/services/auth_service.py` (functions: verify_token, create_session), `src/models/user.py` (class: UserModel). Auth routes import auth_service, auth_service imports user model."
- **context:** Tests the code graph JSON output format with files, layers, symbols, imports, and dependency edges as documented.
- **assertions:**
  - Produces a JSON structure with `files`, `layers`, and `dependency_edges` top-level keys
  - Each file entry includes path, layer classification, language, symbols (with name, type, and line range), and imports list
  - Layer map groups files correctly: API for routes, Service for auth_service, Data for user model
  - Dependency edges are directed: `routes/auth.py -> services/auth_service.py` and `services/auth_service.py -> models/user.py`
  - All dependency directions are valid (API -> Service -> Data) with no layer violations
- **passing_grade:** 4/5 assertions must pass
