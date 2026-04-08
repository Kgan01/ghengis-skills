# FastAPI -- Evaluation

## TC-1: Async Route with Database
- **prompt:** "Create a FastAPI endpoint that fetches a user by ID from the database"
- **context:** Standard async route pattern. Should use async def, dependency injection for DB session.
- **assertions:**
  - Route handler is `async def` (not plain `def`)
  - Uses `Depends()` for database session injection (not manual instantiation)
  - Route is defined on an `APIRouter` (not directly on `app`)
  - APIRouter has a prefix and tags defined
  - Database call uses `await` (async DB driver, not synchronous)
- **passing_grade:** 4/5 assertions must pass

## TC-2: Pydantic v2 Model
- **prompt:** "Create a request model for a command that has a text field (required, non-blank) and an optional context dict"
- **context:** User needs a Pydantic model with validation. Must use v2 API, not v1.
- **assertions:**
  - Inherits from `BaseModel`
  - Uses `model_validator` (not `@validator` which is v1)
  - Validates that `text` is not blank
  - Uses `.model_dump()` (not `.dict()` which is v1)
  - `context` field has a default value of `{}` or is `Optional[dict]`
- **passing_grade:** 4/5 assertions must pass

## TC-3: WebSocket Auth Before Accept
- **prompt:** "Create a WebSocket endpoint that requires a token for authentication"
- **context:** WebSocket handler that must authenticate before accepting the connection.
- **assertions:**
  - Extracts token from query params or headers BEFORE calling `websocket.accept()`
  - Calls `websocket.close(code=1008)` if auth fails (before accept, not after)
  - Only calls `websocket.accept()` after successful token verification
  - Does not accept the connection and then try to reject it
  - Includes a return statement after close to prevent further processing
- **passing_grade:** 4/5 assertions must pass

## TC-4: Anti-Pattern Detection -- Blocking Code in Async
- **prompt:** "Here's my endpoint. Is there a problem?\n```python\nimport requests\n\n@router.get('/proxy')\nasync def proxy_endpoint():\n    response = requests.get('https://api.example.com/data')\n    return response.json()\n```"
- **context:** User has `requests` (blocking) in an async handler. Classic anti-pattern.
- **assertions:**
  - Identifies `requests.get()` as a blocking call that stalls the event loop
  - Recommends replacing with `httpx.AsyncClient` using `async with`
  - Refactored code uses `await` for the HTTP call
  - Does not suggest wrapping `requests` in `run_in_executor` as the primary solution (httpx is preferred)
  - Explains why blocking the event loop is a problem (all other requests stall)
- **passing_grade:** 4/5 assertions must pass

## TC-5: Lifespan Events (Not on_event)
- **prompt:** "I need to connect to my database on startup and disconnect on shutdown in FastAPI"
- **context:** User needs lifecycle management. Should use lifespan, not deprecated on_event.
- **assertions:**
  - Uses `@asynccontextmanager` with a `lifespan` function (not `@app.on_event("startup")`)
  - Startup logic (db connect) runs before `yield`
  - Shutdown logic (db disconnect) runs after `yield`
  - Lifespan is passed to `FastAPI(lifespan=lifespan)`
  - Mentions that `on_event` is deprecated in FastAPI 0.93+
- **passing_grade:** 4/5 assertions must pass
