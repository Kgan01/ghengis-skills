---
name: fastapi
description: Use when building or modifying FastAPI applications — covers async patterns, Pydantic v2 models, dependency injection, WebSocket auth, middleware, and blocking code handling
allowed-tools: Read Write Edit Glob Grep Bash(python *) Bash(pip *)
---

# FastAPI Python Async

## When This Applies

Working on any FastAPI application — routes, middleware, dependencies, WebSocket handlers, background tasks, Pydantic models, or lifespan events.

## Key Concepts

FastAPI is **async-first**: every route handler should be `async def` and must never call blocking I/O directly — any blocking call stalls the entire event loop. Pydantic v2 is the validation layer; its API differs meaningfully from v1. Dependencies are injected via `Depends()` — this is the canonical pattern for DB sessions, settings, and reusable logic. WebSocket connections must be authenticated *before* `websocket.accept()` is called — rejecting after accept sends a close frame, but the client already considers the connection open.

## Common Patterns

**Async route (standard):**
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["resource"])

@router.get("/items/{item_id}")
async def get_item(item_id: int) -> dict:
    result = await db.fetch_one(item_id)   # async DB call
    return result
```

**Pydantic v2 model:**
```python
from pydantic import BaseModel, model_validator

class CommandRequest(BaseModel):
    text: str
    context: dict = {}

    @model_validator(mode="after")
    def validate_text(self) -> "CommandRequest":
        if not self.text.strip():
            raise ValueError("text must not be blank")
        return self

    def to_dict(self) -> dict:
        return self.model_dump()   # not .dict()
```

**Dependency injection with Depends():**
```python
from fastapi import Depends
from app.db import AsyncSession, get_session

async def get_current_user(session: AsyncSession = Depends(get_session)) -> User:
    # resolve from request state set by auth middleware
    ...

@router.get("/profile")
async def profile(user: User = Depends(get_current_user)):
    return user.model_dump()
```

**Lifespan events (replaces on_event):**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await db.connect()
    await cache.ping()
    yield
    # shutdown
    await db.disconnect()

app = FastAPI(lifespan=lifespan)
```

**Auth middleware:**
```python
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        if not await verify_token(token):
            return Response(status_code=401)
        return await call_next(request)

app.add_middleware(AuthMiddleware)
```

**WebSocket auth before accept:**
```python
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not await verify_token(token):
        await websocket.close(code=1008)   # close before accept
        return
    await websocket.accept()
    # handle messages...
```

**Running blocking code without blocking the loop:**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

async def run_blocking(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, fn, *args)
```

## Anti-Patterns

**`requests` library in async def** — `requests.get()` blocks the entire event loop. Use `httpx.AsyncClient` with `async with` instead.

**`time.sleep()` in async code** — blocks the loop. Replace with `await asyncio.sleep(duration)`.

**`@app.on_event("startup")` / `@app.on_event("shutdown")`** — deprecated in FastAPI 0.93+. Use the `lifespan` context manager shown above.

**Routes registered directly on `app` instead of `APIRouter`** — makes the codebase monolithic and prevents prefix/tag grouping. All routes belong in `APIRouter` instances that are `include_router()`'d onto `app`.

**Accepting WebSocket before verifying auth** — once `accept()` is called the HTTP upgrade is complete; a subsequent `close()` is a protocol-level disconnect, not a rejection. Always check the token before `accept()`.

## Validation

- `python -c "from main import app"` — validates imports, router registration, and startup without running a server; any misconfiguration raises immediately
- `pytest` — run the test suite; async tests require `pytest-asyncio` with `asyncio_mode = "auto"` in `pyproject.toml`
- `uvicorn main:app --reload` — interactive dev server; watch for startup errors and Pydantic validation warnings in the log output
