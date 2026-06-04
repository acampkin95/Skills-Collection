---
name: python-fastapi
description: FastAPI for type-safe async Python REST APIs with Pydantic v2, SQLAlchemy, dependency injection, and auto-generated OpenAPI docs.
version: 2.0.0
reviewed: "2026-06-04"
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

## Reference Files

- `references/async-patterns.md` — Async database, background tasks, lifespan
- `references/sqlalchemy-patterns.md` — Models, sessions, repository patterns
- `references/testing-patterns.md` — pytest, TestClient, fixtures, factories


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.