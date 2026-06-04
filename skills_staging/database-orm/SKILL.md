---
name: database-orm
description: PostgreSQL with Prisma and Drizzle ORM for TypeScript/Next.js. Use for schema design, migrations, N+1 optimization, connection pooling, and zero-downtime deploys.
version: 2.0.0
reviewed: "2026-06-04"
---
# Database & ORM Skill

**Read the relevant reference file before starting work.**

## Quick Navigation

| Task | Reference |
|------|-----------|
| Prisma schema, relations, extensions | `references/prisma-patterns.md` |
| Drizzle schema, queries, joins | `references/drizzle-patterns.md` |
| PostgreSQL indexes, EXPLAIN, tuning | `references/postgresql-optimization.md` |
| Migrations, rollbacks, seeding | `references/migration-strategies.md` |

---

## PostgreSQL Fundamentals

### Essential Data Types

```sql
-- Prefer these types
id            BIGSERIAL PRIMARY KEY          -- or UUID
created_at    TIMESTAMPTZ DEFAULT now() NOT NULL
updated_at    TIMESTAMPTZ DEFAULT now() NOT NULL
email         TEXT NOT NULL                -- not VARCHAR
price         NUMERIC(10,2)               -- not FLOAT
metadata      JSONB                       -- not JSON
tags          TEXT[]                       -- array type
status        TEXT CHECK (status IN ('active','inactive'))
```

**Rules:**
- Use `TEXT` over `VARCHAR` (no performance difference in PostgreSQL)
- Use `TIMESTAMPTZ` over `TIMESTAMP` (always store timezone)
- Use `NUMERIC` for money (never `FLOAT`/`DOUBLE`)
- Use `JSONB` over `JSON` (indexable, faster reads)
- Use `BIGSERIAL` for internal IDs, `UUID` for public-facing IDs

### Index Basics

```sql
-- B-tree (default): equality and range queries
CREATE INDEX idx_users_email ON users (email);

-- Composite: column order matters (leftmost prefix rule)
CREATE INDEX idx_orders_user_date ON orders (user_id, created_at DESC);

-- Partial: index only relevant rows
CREATE INDEX idx_active_users ON users (email) WHERE status = 'active';

-- GIN: JSONB and array columns
CREATE INDEX idx_metadata ON products USING GIN (metadata);

-- Unique
CREATE UNIQUE INDEX idx_users_email_unique ON users (email);
```

### Quick EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC LIMIT 10;
```

**Red flags:** `Seq Scan` on large tables, `Nested Loop` with high row counts, `Sort` without index.

See `references/postgresql-optimization.md` for full EXPLAIN reading guide.

---

## Prisma ORM (v7.x — 70% faster TypeScript rebuilds)

**v7.0+ (2025)**: Prisma TypeScript rebuild is 70% faster using Rust-based type generation and WebAssembly caching layer on main thread. relationLoadStrategy (join vs query) now supports more granular control.

### Schema Design

```prisma
// schema.prisma
generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["relationJoins", "driverAdapters"]
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")  // For migrations through PgBouncer
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String?
  role      Role     @default(USER)
  posts     Post[]
  profile   Profile?
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  @@map("users")

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.