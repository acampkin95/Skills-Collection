# Async Patterns for FastAPI

## Async Database Access

```python
# app/database.py
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

## Background Tasks

```python
from fastapi import BackgroundTasks

async def send_welcome_email(email: str, name: str):
    """Runs after response is sent."""
    # async email sending logic
    ...

@router.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    db: DbSession,
    background_tasks: BackgroundTasks,
):
    service = UserService(db)
    user = await service.create_user(data)
    background_tasks.add_task(send_welcome_email, user.email, user.name)
    return user
```

## Lifespan Events (Startup/Shutdown)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import redis.asyncio as aioredis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    app.state.redis = aioredis.from_url(settings.redis_url)
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    yield
    # SHUTDOWN
    await app.state.redis.close()
    await app.state.http_client.aclose()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

## Async Generators for Streaming

```python
from fastapi.responses import StreamingResponse
import asyncio

async def generate_report(query: str):
    """Stream large dataset row by row."""
    async with async_session_factory() as session:
        result = await session.stream(select(Record).where(...))
        async for row in result.scalars():
            yield f"{row.to_csv_line()}\n"
            await asyncio.sleep(0)  # yield control

@router.get("/reports/export")
async def export_report(query: str = ""):
    return StreamingResponse(
        generate_report(query),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=report.csv"},
    )
```

## httpx Async Client

```python
import httpx
from fastapi import Depends, Request

async def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

@router.get("/external-data")
async def fetch_external(
    client: httpx.AsyncClient = Depends(get_http_client),
):
    response = await client.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

## Async Context Manager for Transactions

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def transaction(session: AsyncSession):
    """Explicit transaction boundary."""
    async with session.begin():
        yield session
    # auto-commits on exit, rolls back on exception

async def transfer_funds(db: AsyncSession, from_id: int, to_id: int, amount: float):
    async with transaction(db):
        sender = await db.get(Account, from_id)
        receiver = await db.get(Account, to_id)
        sender.balance -= amount
        receiver.balance += amount
```

## Concurrency with asyncio.gather

```python
import asyncio

@router.get("/dashboard")
async def dashboard(db: DbSession, client: httpx.AsyncClient = Depends(get_http_client)):
    users_task = UserService(db).count_active()
    orders_task = OrderService(db).revenue_today()
    weather_task = client.get("https://api.weather.com/current")

    users, revenue, weather_resp = await asyncio.gather(
        users_task, orders_task, weather_task
    )
    return {
        "active_users": users,
        "revenue_today": revenue,
        "weather": weather_resp.json(),
    }
```

## Rate Limiting with Redis

```python
from fastapi import Request, HTTPException
import redis.asyncio as aioredis

async def rate_limit(request: Request, limit: int = 100, window: int = 60):
    redis: aioredis.Redis = request.app.state.redis
    key = f"rate:{request.client.host}:{request.url.path}"
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window)
    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
```
