# Testing Patterns for FastAPI

## conftest.py — Core Fixtures

```python
# tests/conftest.py
import asyncio
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.database import get_db
from app.main import app
from app.models.base import Base

TEST_DATABASE_URL = settings.database_url + "_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Create tables once per test session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Each test gets its own rolled-back transaction."""
    async with TestSessionFactory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client with overridden DB dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

## Basic CRUD Tests

```python
# tests/test_users.py
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_create_user(client: AsyncClient):
    response = await client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "securepass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "password" not in data  # never expose password


async def test_create_user_duplicate_email(client: AsyncClient):
    payload = {"email": "dupe@example.com", "name": "First", "password": "pass12345"}
    await client.post("/api/v1/users/", json=payload)
    response = await client.post("/api/v1/users/", json=payload)
    assert response.status_code == 409


async def test_get_user(client: AsyncClient):
    create = await client.post("/api/v1/users/", json={
        "email": "get@example.com", "name": "Get Me", "password": "pass12345",
    })
    user_id = create.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "get@example.com"


async def test_get_user_not_found(client: AsyncClient):
    response = await client.get("/api/v1/users/99999")
    assert response.status_code == 404


async def test_list_users_pagination(client: AsyncClient):
    for i in range(5):
        await client.post("/api/v1/users/", json={
            "email": f"page{i}@example.com", "name": f"User {i}", "password": "pass12345",
        })
    response = await client.get("/api/v1/users/?page=1&per_page=2")
    data = response.json()
    assert len(data["items"]) == 2
    assert data["per_page"] == 2


async def test_create_user_validation(client: AsyncClient):
    response = await client.post("/api/v1/users/", json={
        "email": "not-an-email",
        "name": "",
        "password": "short",
    })
    assert response.status_code == 422
```

## Mocking Dependencies

```python
# tests/test_with_mocks.py
from unittest.mock import AsyncMock, patch

async def test_external_api_call(client: AsyncClient):
    mock_response = AsyncMock()
    mock_response.json.return_value = {"data": "mocked"}
    mock_response.raise_for_status = AsyncMock()

    with patch("app.routers.external.httpx.AsyncClient.get", return_value=mock_response):
        response = await client.get("/api/v1/external-data")
        assert response.status_code == 200
        assert response.json()["data"] == "mocked"
```

## Factory Boy for Test Data

```python
# tests/factories.py
import factory
from factory import fuzzy
from app.models.user import User

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    email = factory.LazyAttribute(lambda o: f"user{o.id}@example.com")
    name = factory.Faker("name")
    hashed_password = "hashed_test_password"
    is_active = True
```

```python
# Using in tests
from tests.factories import UserFactory

async def test_with_factory(db_session):
    user = UserFactory.build()
    db_session.add(user)
    await db_session.flush()

    result = await db_session.get(User, user.id)
    assert result.email == user.email
```

## Testing Authentication

```python
# tests/conftest.py (add)
from app.dependencies import get_current_user
from tests.factories import UserFactory

@pytest.fixture
def auth_user():
    return UserFactory.build(id=1, email="auth@test.com", name="Auth User")

@pytest.fixture
async def auth_client(client: AsyncClient, auth_user):
    """Client with authentication mocked."""
    app.dependency_overrides[get_current_user] = lambda: auth_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)
```

```python
async def test_protected_route(auth_client: AsyncClient):
    response = await auth_client.delete("/api/v1/users/1")
    assert response.status_code != 401  # auth is mocked
```

## pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
filterwarnings = ["ignore::DeprecationWarning"]

[tool.coverage.run]
source = ["app"]
omit = ["app/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_users.py -v

# Run tests matching pattern
pytest -k "test_create_user"

# Parallel execution
pytest -n auto  # requires pytest-xdist
```
