---
name: python-fastapi
description: FastAPI is a modern Python web framework for building fast, type-safe REST APIs with automatic OpenAPI documentation. Uses async/await, Pydantic v2 validation, SQLAlchemy ORM, dependency injection, and WebSocket support. Use this skill when FastAPI, REST API, Pydantic, async def, @router, SQLAlchemy, async database, dependency injection, WebSocket, uvicorn. Also triggers on Python API development, OpenAPI docs, async validation, or structured error handling.
---

# Python FastAPI Development

Modern async Python web framework with type-safe validation and automatic OpenAPI docs.

## Quick Router

| Need | Reference |
|------|-----------|
| **Async patterns, background tasks, lifespan** | `references/async-patterns.md` |
| **SQLAlchemy models, sessions, migrations, repository** | `references/sqlalchemy-patterns.md` |
| **Testing, pytest, fixtures, factories** | `references/testing-patterns.md` |

## Why FastAPI

- **Type-safe** with Pydantic v2 validation
- **Async-first** with native `async`/`await`
- **Auto-generated docs** at `/docs` (OpenAPI/Swagger)
- **Dependency injection** built-in (`Depends()`)
- **3-5× faster** than Flask/Django
- **Python 3.12+** support, zero legacy baggage

## Project Structure

```
project/
├── app/
│   ├── main.py              # FastAPI app, lifespan
│   ├── config.py            # Settings (pydantic-settings)
│   ├── dependencies.py      # Reusable Depends()
│   ├── database.py          # SQLAlchemy engine, sessions
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response
│   ├── routers/             # Route handlers (HTTP only)
│   └── services/            # Business logic
├── tests/
│   ├── conftest.py
│   └── test_users.py
├── pyproject.toml
└── Dockerfile
```

## Quick Start

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}

@app.post("/items/")
async def create_item(name: str, price: float):
    return {"name": name, "price": price}
```

Run with: `uvicorn app.main:app --reload`

## Pydantic v2 Schemas

```python
# app/schemas/user.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    created_at: datetime
```

## Dependency Injection

```python
# app/dependencies.py
from typing import Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

DbSession = Annotated[AsyncSession, Depends(get_db)]

async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    token = authorization.removeprefix("Bearer ")
    user = await verify_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
```

## Router Pattern

```python
# app/routers/users.py
from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import DbSession, CurrentUser
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserResponse])
async def list_users(db: DbSession, skip: int = Query(0, ge=0)):
    users = await db.query(User).offset(skip).limit(20).all()
    return users

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, db: DbSession):
    user = User(**data.model_dump())
    db.add(user)
    await db.flush()
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: DbSession):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user
```

## App Setup with Lifespan

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.routers import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/v1")
```

## Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, detail: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": exc.detail},
    )
```

## Middleware Example

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        print(f"{request.method} {request.url.path} → {response.status_code} ({elapsed:.3f}s)")
        return response

app.add_middleware(LoggingMiddleware)
```

## Background Tasks

```python
from fastapi import BackgroundTasks

@app.post("/send-email/")
async def send_email(email: str, bg: BackgroundTasks):
    bg.add_task(send_welcome_email, email)
    return {"status": "email queued"}

async def send_welcome_email(email: str):
    # Runs after response is sent
    await email_client.send(to=email, subject="Welcome!")
```

## WebSocket Endpoint

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.active[user_id] = ws

    async def broadcast(self, data: dict):
        for ws in self.active.values():
            await ws.send_json(data)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(ws: WebSocket, user_id: str):
    await manager.connect(user_id, ws)
    try:
        while True:
            data = await ws.receive_json()
            await manager.broadcast({"user": user_id, "msg": data})
    except WebSocketDisconnect:
        manager.active.pop(user_id, None)
```

## Deployment

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production (gunicorn + uvicorn workers)
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000
```

## Key Dependencies

```toml
[project]
dependencies = [
    "fastapi>=0.129",
    "uvicorn[standard]>=0.30",
    "pydantic>=2.7",
    "pydantic-settings>=2.5",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "httpx>=0.27",
    "factory-boy>=3.3",
]
```

## Reference Files

- `references/async-patterns.md` — Async database, background tasks, lifespan
- `references/sqlalchemy-patterns.md` — Models, sessions, repository patterns
- `references/testing-patterns.md` — pytest, TestClient, fixtures, factories
