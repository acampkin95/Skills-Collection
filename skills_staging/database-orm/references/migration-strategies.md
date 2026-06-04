# Migration Strategies

## Zero-Downtime Migrations

### Principles

1. **Never drop columns/tables in the same deploy** that removes code references
2. **Always add before remove** (expand-contract pattern)
3. **New columns must be nullable or have defaults**
4. **Never rename columns directly** - add new, migrate data, drop old
5. **Keep migrations fast** - no long-running locks on production tables

### Expand-Contract Pattern

```
Phase 1 (Expand):  Add new column        → Deploy code that writes to both
Phase 2 (Migrate): Backfill data          → Deploy code that reads from new
Phase 3 (Contract): Drop old column       → Clean deploy
```

### Example: Renaming a Column

```sql
-- Migration 1: Add new column (safe, no lock)
ALTER TABLE users ADD COLUMN full_name TEXT;

-- Migration 2: Backfill (run in batches)
UPDATE users SET full_name = name WHERE full_name IS NULL AND id > $cursor LIMIT 1000;

-- Migration 3: App now reads from full_name, writes to both
-- (deploy application change)

-- Migration 4: Drop old column (after verifying all reads use new column)
ALTER TABLE users DROP COLUMN name;
```

### Safe vs Unsafe Operations

| Operation | Safe? | Notes |
|-----------|-------|-------|
| `ADD COLUMN` (nullable) | Yes | No lock |
| `ADD COLUMN` with `DEFAULT` (PG 11+) | Yes | Metadata-only change |
| `ADD COLUMN NOT NULL` without default | **No** | Locks table, scans all rows |
| `DROP COLUMN` | Yes | Quick metadata change |
| `ALTER COLUMN TYPE` | **No** | Rewrites table (usually) |
| `CREATE INDEX` | **No** | Locks writes |
| `CREATE INDEX CONCURRENTLY` | Yes | Slow but no lock |
| `ADD CONSTRAINT` (CHECK, FK) | **No** | Scans table |
| `ADD CONSTRAINT ... NOT VALID` | Yes | Skip validation |
| `VALIDATE CONSTRAINT` | Yes | Non-blocking scan |
| `DROP TABLE` | Yes | Quick |
| `RENAME COLUMN` | Yes | Quick but breaks app |
| `RENAME TABLE` | Yes | Quick but breaks app |

### Concurrent Index Creation

```sql
-- ALWAYS use CONCURRENTLY in production
CREATE INDEX CONCURRENTLY idx_orders_user ON orders (user_id);

-- Check if index creation failed (can happen with CONCURRENTLY)
SELECT * FROM pg_indexes WHERE indexname = 'idx_orders_user';

-- If failed, drop invalid index and retry
DROP INDEX CONCURRENTLY IF EXISTS idx_orders_user;
CREATE INDEX CONCURRENTLY idx_orders_user ON orders (user_id);
```

### Adding NOT NULL Constraint Safely

```sql
-- Step 1: Add CHECK constraint (not validated, instant)
ALTER TABLE users ADD CONSTRAINT users_email_not_null
  CHECK (email IS NOT NULL) NOT VALID;

-- Step 2: Validate (non-blocking scan)
ALTER TABLE users VALIDATE CONSTRAINT users_email_not_null;

-- Step 3: Now safe to add NOT NULL (instant, PG knows constraint holds)
ALTER TABLE users ALTER COLUMN email SET NOT NULL;

-- Step 4: Drop redundant CHECK
ALTER TABLE users DROP CONSTRAINT users_email_not_null;
```

### Adding Foreign Key Safely

```sql
-- Step 1: Add FK without validation (instant)
ALTER TABLE posts ADD CONSTRAINT fk_posts_author
  FOREIGN KEY (author_id) REFERENCES users (id) NOT VALID;

-- Step 2: Validate (non-blocking)
ALTER TABLE posts VALIDATE CONSTRAINT fk_posts_author;
```

---

## Rollback Procedures

### Prisma Rollback

```bash
# Revert last migration (development only)
npx prisma migrate reset  # WARNING: drops all data

# In production: create a new "undo" migration
npx prisma migrate dev --name revert_add_user_role

# Manual rollback SQL
npx prisma migrate resolve --rolled-back 20250101000000_add_user_role
```

**Prisma production rollback strategy:**
1. Never use `migrate reset` in production
2. Create a new migration that reverses changes
3. Test the rollback migration in staging first
4. Deploy the rollback migration with `prisma migrate deploy`

### Drizzle Rollback

```bash
# Drizzle doesn't have built-in rollback
# Strategy: create a new migration that undoes changes

# 1. Modify schema to previous state
# 2. Generate new migration
npx drizzle-kit generate

# Or manually write SQL in drizzle/XXXX_rollback.sql
```

### Manual SQL Rollback Template

```sql
-- migrations/rollback_20250101.sql
BEGIN;

-- Reverse column addition
ALTER TABLE users DROP COLUMN IF EXISTS new_column;

-- Reverse index creation
DROP INDEX CONCURRENTLY IF EXISTS idx_new_index;

-- Reverse enum value (PostgreSQL doesn't support removing enum values easily)
-- Must recreate the type
ALTER TYPE status RENAME TO status_old;
CREATE TYPE status AS ENUM ('active', 'inactive');
ALTER TABLE users ALTER COLUMN status TYPE status USING status::text::status;
DROP TYPE status_old;

COMMIT;
```

---

## Seed Data Patterns

### Idempotent Seeds

```typescript
// prisma/seed.ts
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  // Use upsert for idempotency
  const roles = ["USER", "ADMIN", "MODERATOR"] as const;

  for (const role of roles) {
    await prisma.role.upsert({
      where: { name: role },
      update: {},
      create: { name: role, description: `${role} role` },
    });
  }

  // Seed with relations
  await prisma.user.upsert({
    where: { email: "admin@example.com" },
    update: {},
    create: {
      email: "admin@example.com",
      name: "Admin",
      role: "ADMIN",
      posts: {
        create: [
          { title: "Welcome", content: "Getting started guide", published: true },
        ],
      },
    },
  });
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

### Drizzle Seeds

```typescript
// src/db/seed.ts
import { db } from "./index";
import { users, posts } from "./schema";
import { eq } from "drizzle-orm";

async function seed() {
  // Upsert pattern
  const existing = await db.query.users.findFirst({
    where: eq(users.email, "admin@example.com"),
  });

  if (!existing) {
    const [admin] = await db
      .insert(users)
      .values({ email: "admin@example.com", name: "Admin", role: "admin" })
      .returning();

    await db.insert(posts).values([
      { title: "Welcome", content: "Hello", authorId: admin.id, published: true },
    ]);
  }

  console.log("Seed complete");
}

seed().catch(console.error);
```

### Environment-Specific Seeds

```typescript
type SeedEnv = "development" | "staging" | "production";

async function seed(env: SeedEnv) {
  // Always seed: reference data
  await seedRoles();
  await seedCategories();
  await seedPermissions();

  if (env === "development") {
    // Fake data for local development
    await seedFakeUsers(50);
    await seedFakePosts(200);
  }

  if (env === "staging") {
    // Realistic but anonymized data
    await seedAnonymizedData();
  }

  // Production: only reference data (roles, categories, etc.)
}

seed((process.env.NODE_ENV as SeedEnv) ?? "development");
```

---

## Data Backfill Strategies

### Batched Backfill

```typescript
async function backfillFullName(batchSize = 1000) {
  let cursor: string | undefined;
  let processed = 0;

  while (true) {
    const batch = await prisma.user.findMany({
      where: {
        fullName: null,
        ...(cursor ? { id: { gt: cursor } } : {}),
      },
      orderBy: { id: "asc" },
      take: batchSize,
      select: { id: true, firstName: true, lastName: true },
    });

    if (batch.length === 0) break;

    await prisma.$transaction(
      batch.map((user) =>
        prisma.user.update({
          where: { id: user.id },
          data: { fullName: `${user.firstName} ${user.lastName}`.trim() },
        })
      )
    );

    cursor = batch[batch.length - 1].id;
    processed += batch.length;
    console.log(`Backfilled ${processed} users`);

    // Avoid overwhelming the database
    await new Promise((r) => setTimeout(r, 100));
  }

  console.log(`Backfill complete: ${processed} users`);
}
```

### SQL-Based Backfill (Faster)

```sql
-- Batch update with progress tracking
DO $$
DECLARE
  batch_size INTEGER := 5000;
  total_updated INTEGER := 0;
  rows_affected INTEGER;
BEGIN
  LOOP
    UPDATE users
    SET full_name = first_name || ' ' || last_name
    WHERE id IN (
      SELECT id FROM users
      WHERE full_name IS NULL
      LIMIT batch_size
      FOR UPDATE SKIP LOCKED
    );

    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    total_updated := total_updated + rows_affected;
    RAISE NOTICE 'Updated % rows (total: %)', rows_affected, total_updated;

    EXIT WHEN rows_affected = 0;
    PERFORM pg_sleep(0.1);  -- Brief pause
  END LOOP;
END $$;
```

---

## Migration Testing

### Pre-Deploy Checklist

```bash
#!/bin/bash
# scripts/test-migration.sh

set -e

echo "1. Creating test database..."
createdb migration_test

echo "2. Applying all migrations..."
DATABASE_URL="postgresql://localhost/migration_test" npx prisma migrate deploy

echo "3. Running seed..."
DATABASE_URL="postgresql://localhost/migration_test" npx prisma db seed

echo "4. Running integration tests..."
DATABASE_URL="postgresql://localhost/migration_test" npm run test:integration

echo "5. Testing rollback migration..."
DATABASE_URL="postgresql://localhost/migration_test" psql -f migrations/rollback_latest.sql

echo "6. Cleanup..."
dropdb migration_test

echo "All migration tests passed!"
```

### Dry Run in Production

```sql
-- Wrap migration in transaction, then rollback to verify
BEGIN;

-- Your migration SQL here
ALTER TABLE users ADD COLUMN phone TEXT;
CREATE INDEX CONCURRENTLY idx_users_phone ON users (phone);

-- Check what changed
\d users

-- Rollback (nothing actually changes)
ROLLBACK;
```

### CI/CD Migration Pipeline

```yaml
# .github/workflows/migration-check.yml
name: Migration Check
on:
  pull_request:
    paths:
      - 'prisma/migrations/**'
      - 'prisma/schema.prisma'

jobs:
  migration-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - run: npm ci
      - run: npx prisma migrate deploy
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db

      - run: npx prisma db seed
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db

      - run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db
```

---

## Blue-Green Database Deployments

### Strategy

```
1. Blue (current) ─── serves traffic
2. Green (new)    ─── apply migrations, verify

Switch:
3. Blue  ─── drain connections
4. Green ─── receives traffic

Rollback:
5. Green ─── drain connections
6. Blue  ─── receives traffic (no migration changes needed)
```

### Requirements

- Migrations must be **backward compatible** (expand-contract)
- Both old and new code must work with the migrated schema
- Use feature flags to control which code paths read new columns

### Logical Replication Setup

```sql
-- On Blue (source)
CREATE PUBLICATION blue_pub FOR ALL TABLES;

-- On Green (target)
CREATE SUBSCRIPTION green_sub
  CONNECTION 'host=blue-db port=5432 dbname=mydb'
  PUBLICATION blue_pub;

-- Verify replication lag
SELECT slot_name, confirmed_flush_lsn, pg_current_wal_lsn(),
       pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) as lag_bytes
FROM pg_replication_slots;
```

### Cutover Checklist

1. Verify replication lag is near zero
2. Put application in maintenance mode (or use connection draining)
3. Wait for final replication sync
4. Update DNS/load balancer to point to Green
5. Verify application health on Green
6. Keep Blue running for 1 hour as rollback option
7. Decommission Blue after verification period
