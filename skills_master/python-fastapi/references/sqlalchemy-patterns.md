# SQLAlchemy 2.0 Patterns for FastAPI

## Declarative Models

```python
# app/models/base.py
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
```

```python
# app/models/user.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")
```

```python
# app/models/post.py
from sqlalchemy import ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Post(TimestampMixin, Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
```

## Async Session Queries

```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# Get by primary key
user = await session.get(User, user_id)

# Select with filters
stmt = select(User).where(User.is_active == True).order_by(User.created_at.desc())
result = await session.execute(stmt)
users = result.scalars().all()

# Pagination
stmt = (
    select(User)
    .where(User.is_active == True)
    .offset((page - 1) * per_page)
    .limit(per_page)
)
result = await session.execute(stmt)
users = result.scalars().all()

# Count
count_stmt = select(func.count()).select_from(User).where(User.is_active == True)
total = (await session.execute(count_stmt)).scalar_one()

# Search with ILIKE
if search:
    stmt = stmt.where(User.name.ilike(f"%{search}%"))

# Eager loading relationships
from sqlalchemy.orm import selectinload
stmt = select(User).options(selectinload(User.posts)).where(User.id == user_id)
result = await session.execute(stmt)
user = result.scalar_one_or_none()
```

## Repository Pattern

```python
# app/repositories/base.py
from typing import Generic, TypeVar, Type
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)

class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: Type[ModelT]):
        self.session = session
        self.model = model

    async def get(self, id: int) -> ModelT | None:
        return await self.session.get(self.model, id)

    async def list(self, offset: int = 0, limit: int = 20) -> list[ModelT]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        return (await self.session.execute(stmt)).scalar_one()

    async def create(self, **kwargs) -> ModelT:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, id: int, **kwargs) -> ModelT | None:
        instance = await self.get(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def delete(self, id: int) -> bool:
        instance = await self.get(id)
        if not instance:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True
```

```python
# app/repositories/user.py
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
```

## Alembic Async Setup

```python
# migrations/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.models.base import Base
from app.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Common Alembic Commands

```bash
# Initialize (first time only)
alembic init -t async migrations

# Create migration
alembic revision --autogenerate -m "add users table"

# Apply all pending
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history --verbose
```
