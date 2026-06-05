---
name: database-orm
description: PostgreSQL database design with Prisma and Drizzle ORM.
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
  @@index([email])
}

model Post {
  id          String     @id @default(uuid())
  title       String
  content     String?
  published   Boolean    @default(false)
  author      User       @relation(fields: [authorId], references: [id], onDelete: Cascade)
  authorId    String     @map("author_id")
  categories  Category[]
  createdAt   DateTime   @default(now()) @map("created_at")

  @@map("posts")
  @@index([authorId])
  @@index([published, createdAt(sort: Desc)])
}

enum Role {
  USER
  ADMIN
  MODERATOR
}
```

### Common Queries

```typescript
// Include relations (avoid N+1)
const users = await prisma.user.findMany({
  include: { posts: { where: { published: true }, take: 5 } },
});

// Select specific fields
const emails = await prisma.user.findMany({
  select: { id: true, email: true },
});

// Upsert
await prisma.user.upsert({
  where: { email: "user@example.com" },
  update: { name: "Updated" },
  create: { email: "user@example.com", name: "New" },
});

// Transaction
const [user, post] = await prisma.$transaction([
  prisma.user.create({ data: { email: "a@b.com" } }),
  prisma.post.create({ data: { title: "Hello", authorId: userId } }),
]);
```

### N+1 Prevention (v7.x relationLoadStrategy)

```typescript
// BAD: N+1 queries
const users = await prisma.user.findMany();
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { authorId: user.id } });
}

// GOOD: Single query with include
const users = await prisma.user.findMany({
  include: { posts: true },
});

// GOOD v7.x: Explicit SQL JOIN (relationLoadStrategy: "join")
const users = await prisma.user.findMany({
  include: { posts: true },
  relationLoadStrategy: "join", // SQL JOIN instead of separate queries
});
```

See `references/prisma-patterns.md` for advanced patterns.

---

## Drizzle ORM (v1.0-beta.2 — 10x faster schema introspection)

**v1.0-beta.2 (Feb 2025)**: Schema introspection is 10x faster (10s → <1s for large schemas). MSSQL support added. Unified imports across drivers.

### Schema Definition

```typescript
// src/db/schema.ts
import { pgTable, uuid, text, boolean, timestamp, pgEnum } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

export const roleEnum = pgEnum("role", ["user", "admin", "moderator"]);

export const users = pgTable("users", {
  id: uuid("id").defaultRandom().primaryKey(),
  email: text("email").notNull().unique(),
  name: text("name"),
  role: roleEnum("role").default("user").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

export const posts = pgTable("posts", {
  id: uuid("id").defaultRandom().primaryKey(),
  title: text("title").notNull(),
  content: text("content"),
  published: boolean("published").default(false).notNull(),
  authorId: uuid("author_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
}, (table) => [
  index("idx_posts_author").on(table.authorId),
  index("idx_posts_published").on(table.published, table.createdAt),
]);

// Relations (for query API)
export const usersRelations = relations(users, ({ many, one }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, { fields: [posts.authorId], references: [users.id] }),
}));
```

### Queries

```typescript
import { db } from "./db";
import { users, posts } from "./schema";
import { eq, and, desc, sql } from "drizzle-orm";

// Select with filter
const activeUsers = await db
  .select()
  .from(users)
  .where(eq(users.role, "admin"));

// Join
const postsWithAuthors = await db
  .select({
    postTitle: posts.title,
    authorName: users.name,
  })
  .from(posts)
  .innerJoin(users, eq(posts.authorId, users.id))
  .where(eq(posts.published, true))
  .orderBy(desc(posts.createdAt));

// Relational queries (like Prisma include)
const usersWithPosts = await db.query.users.findMany({
  with: { posts: { where: eq(posts.published, true), limit: 5 } },
});

// Insert returning
const [newUser] = await db
  .insert(users)
  .values({ email: "user@example.com", name: "Alex" })
  .returning();

// Transaction
await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ email: "a@b.com" }).returning();
  await tx.insert(posts).values({ title: "First", authorId: user.id });
});
```

See `references/drizzle-patterns.md` for joins, subqueries, and prepared statements.

---

## Migration Workflows

### Prisma

```bash
# Development: create and apply migration
npx prisma migrate dev --name add_user_role

# Production: apply pending migrations
npx prisma migrate deploy

# Reset database (development only)
npx prisma migrate reset

# Generate client after schema change
npx prisma generate
```

### Drizzle

```bash
# Generate migration SQL from schema changes
npx drizzle-kit generate

# Apply migrations
npx drizzle-kit migrate

# Push schema directly (development only, no migration files)
npx drizzle-kit push

# Open Drizzle Studio
npx drizzle-kit studio
```

See `references/migration-strategies.md` for zero-downtime patterns.

---

## Connection Pooling

### With PgBouncer

```
# .env - connect through PgBouncer
DATABASE_URL="postgresql://user:pass@localhost:6432/mydb?pgbouncer=true"

# Direct connection for migrations
DIRECT_URL="postgresql://user:pass@localhost:5432/mydb"
```

```prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}
```

### Prisma Accelerate

```typescript
import { PrismaClient } from "@prisma/client";
import { withAccelerate } from "@prisma/extension-accelerate";

const prisma = new PrismaClient().$extends(withAccelerate());

// Cached query
const users = await prisma.user.findMany({
  cacheStrategy: { ttl: 60, swr: 120 },
});
```

---

## Database Testing

```typescript
// test/helpers/db.ts
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient({
  datasourceUrl: process.env.TEST_DATABASE_URL,
});

export async function cleanDatabase() {
  const tablenames = await prisma.$queryRaw<{ tablename: string }[]>`
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  `;
  for (const { tablename } of tablenames) {
    if (tablename !== "_prisma_migrations") {
      await prisma.$executeRawUnsafe(`TRUNCATE TABLE "${tablename}" CASCADE`);
    }
  }
}

// In tests
beforeEach(async () => {
  await cleanDatabase();
});
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| N+1 queries in loops | Use `include`/`with` or `relationLoadStrategy: "join"` |
| `FLOAT` for money | Use `Decimal`/`NUMERIC(10,2)` |
| Missing indexes on foreign keys | Always add `@@index([fkField])` |
| `TIMESTAMP` without timezone | Use `TIMESTAMPTZ` / `timestamp({ withTimezone: true })` |
| Not using transactions for multi-step writes | Wrap in `$transaction` / `db.transaction()` |
| Forgetting `prisma generate` after schema change | Run after every `schema.prisma` edit |
| Raw string interpolation in SQL | Use parameterized queries (`$queryRaw` with tagged template) |
| Seeding in production migration | Keep seeds separate from migrations |
| Not setting `onDelete` on relations | Explicitly set `Cascade`, `SetNull`, or `Restrict` |
| Connection exhaustion in serverless | Use connection pooling (PgBouncer / Accelerate) |

---

## Seeding

```typescript
// prisma/seed.ts
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  // Upsert to make seeds idempotent
  const admin = await prisma.user.upsert({
    where: { email: "admin@example.com" },
    update: {},
    create: {
      email: "admin@example.com",
      name: "Admin",
      role: "ADMIN",
      posts: {
        create: [
          { title: "Welcome", content: "First post", published: true },
        ],
      },
    },
  });
  console.log({ admin });
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
```

```json
// package.json
{
  "prisma": {
    "seed": "tsx prisma/seed.ts"
  }
}
```

```bash
npx prisma db seed
```
