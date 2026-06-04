# Drizzle ORM Patterns

## Schema Definition

### Column Types

```typescript
import {
  pgTable, pgEnum, uuid, text, varchar, integer, bigint, boolean,
  timestamp, date, numeric, real, doublePrecision, json, jsonb,
  serial, bigserial, index, uniqueIndex, primaryKey,
} from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  // Primary keys
  id: uuid("id").defaultRandom().primaryKey(),
  // or: id: serial("id").primaryKey(),

  // Strings
  email: text("email").notNull().unique(),
  name: varchar("name", { length: 255 }),

  // Numbers
  age: integer("age"),
  balance: numeric("balance", { precision: 10, scale: 2 }),
  score: real("score"),

  // Boolean
  active: boolean("active").default(true).notNull(),

  // JSON
  metadata: jsonb("metadata").$type<{ theme: string; lang: string }>(),

  // Timestamps
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
  deletedAt: timestamp("deleted_at", { withTimezone: true }),
});
```

### Enums

```typescript
export const statusEnum = pgEnum("status", ["active", "inactive", "suspended"]);
export const roleEnum = pgEnum("role", ["user", "admin", "moderator"]);

export const users = pgTable("users", {
  id: uuid("id").defaultRandom().primaryKey(),
  status: statusEnum("status").default("active").notNull(),
  role: roleEnum("role").default("user").notNull(),
});
```

### Indexes

```typescript
import { index, uniqueIndex } from "drizzle-orm/pg-core";

export const posts = pgTable("posts", {
  id: uuid("id").defaultRandom().primaryKey(),
  title: text("title").notNull(),
  slug: text("slug").notNull(),
  authorId: uuid("author_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  published: boolean("published").default(false).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
}, (table) => [
  index("idx_posts_author").on(table.authorId),
  index("idx_posts_published_date").on(table.published, table.createdAt),
  uniqueIndex("idx_posts_slug").on(table.slug),
]);
```

### Composite Primary Key

```typescript
export const postTags = pgTable("post_tags", {
  postId: uuid("post_id").notNull().references(() => posts.id, { onDelete: "cascade" }),
  tagId: uuid("tag_id").notNull().references(() => tags.id, { onDelete: "cascade" }),
  assignedAt: timestamp("assigned_at", { withTimezone: true }).defaultNow().notNull(),
}, (table) => [
  primaryKey({ columns: [table.postId, table.tagId] }),
]);
```

---

## Relations

```typescript
import { relations } from "drizzle-orm";

// One-to-Many
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
  comments: many(comments),
}));

export const postsRelations = relations(posts, ({ one, many }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
  comments: many(comments),
  tags: many(postTags),
}));

// One-to-One
export const profilesRelations = relations(profiles, ({ one }) => ({
  user: one(users, {
    fields: [profiles.userId],
    references: [users.id],
  }),
}));

// Self-relation
export const employeesRelations = relations(employees, ({ one, many }) => ({
  manager: one(employees, {
    fields: [employees.managerId],
    references: [employees.id],
    relationName: "manager",
  }),
  reports: many(employees, { relationName: "manager" }),
}));
```

---

## Database Client Setup

```typescript
// src/db/index.ts
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import * as schema from "./schema";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 5000,
});

export const db = drizzle(pool, { schema });

// For serverless (Neon)
import { drizzle } from "drizzle-orm/neon-http";
import { neon } from "@neondatabase/serverless";

const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql, { schema });
```

---

## Query Patterns

### Select

```typescript
import { eq, ne, gt, lt, gte, lte, and, or, like, ilike, inArray, isNull, isNotNull, sql, desc, asc, count, sum, avg } from "drizzle-orm";

// Basic select
const allUsers = await db.select().from(users);

// With conditions
const admins = await db
  .select()
  .from(users)
  .where(eq(users.role, "admin"));

// Complex where
const filtered = await db
  .select()
  .from(users)
  .where(
    and(
      eq(users.active, true),
      or(
        ilike(users.name, "%alex%"),
        ilike(users.email, "%alex%"),
      ),
      isNull(users.deletedAt),
    )
  )
  .orderBy(desc(users.createdAt))
  .limit(20)
  .offset(0);

// Select specific columns
const emails = await db
  .select({ id: users.id, email: users.email })
  .from(users);

// Count
const [{ total }] = await db
  .select({ total: count() })
  .from(users)
  .where(eq(users.active, true));

// Group by with aggregates
const postCounts = await db
  .select({
    authorId: posts.authorId,
    postCount: count(),
    avgScore: avg(posts.score),
  })
  .from(posts)
  .groupBy(posts.authorId)
  .having(gt(count(), 5));
```

### Joins

```typescript
// Inner join
const postsWithAuthors = await db
  .select({
    postId: posts.id,
    postTitle: posts.title,
    authorName: users.name,
    authorEmail: users.email,
  })
  .from(posts)
  .innerJoin(users, eq(posts.authorId, users.id))
  .where(eq(posts.published, true));

// Left join
const usersWithPosts = await db
  .select({
    userId: users.id,
    userName: users.name,
    postTitle: posts.title,
  })
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId));

// Multiple joins
const fullData = await db
  .select({
    post: posts,
    author: users,
    commentCount: count(comments.id),
  })
  .from(posts)
  .innerJoin(users, eq(posts.authorId, users.id))
  .leftJoin(comments, eq(posts.id, comments.postId))
  .groupBy(posts.id, users.id);
```

### Relational Queries (Query API)

```typescript
// Find many with relations (like Prisma include)
const usersWithPosts = await db.query.users.findMany({
  with: {
    posts: {
      where: eq(posts.published, true),
      limit: 5,
      orderBy: desc(posts.createdAt),
      with: {
        comments: true, // nested relation
      },
    },
  },
  where: eq(users.active, true),
});

// Find first
const user = await db.query.users.findFirst({
  where: eq(users.email, "alex@example.com"),
  with: { posts: true },
});

// Select specific columns with relations
const result = await db.query.users.findMany({
  columns: { id: true, name: true, email: true },
  with: {
    posts: {
      columns: { id: true, title: true },
    },
  },
});
```

### Subqueries

```typescript
// Subquery in where
const subquery = db
  .select({ authorId: posts.authorId })
  .from(posts)
  .where(eq(posts.published, true))
  .groupBy(posts.authorId)
  .having(gt(count(), 3));

const prolificAuthors = await db
  .select()
  .from(users)
  .where(inArray(users.id, subquery));

// Subquery as column
const userPostCounts = await db
  .select({
    id: users.id,
    name: users.name,
    postCount: db
      .select({ count: count() })
      .from(posts)
      .where(eq(posts.authorId, users.id)),
  })
  .from(users);
```

---

## Insert, Update, Delete

```typescript
// Insert single
const [newUser] = await db
  .insert(users)
  .values({ email: "new@example.com", name: "New User" })
  .returning();

// Insert multiple
await db.insert(users).values([
  { email: "a@b.com", name: "User A" },
  { email: "c@d.com", name: "User B" },
]);

// Upsert (on conflict)
await db
  .insert(users)
  .values({ email: "a@b.com", name: "Updated" })
  .onConflictDoUpdate({
    target: users.email,
    set: { name: "Updated", updatedAt: new Date() },
  });

// On conflict do nothing
await db
  .insert(users)
  .values({ email: "a@b.com", name: "Skip" })
  .onConflictDoNothing({ target: users.email });

// Update
const [updated] = await db
  .update(users)
  .set({ name: "New Name", updatedAt: new Date() })
  .where(eq(users.id, userId))
  .returning();

// Delete
await db.delete(users).where(eq(users.id, userId));

// Soft delete
await db
  .update(users)
  .set({ deletedAt: new Date() })
  .where(eq(users.id, userId));
```

---

## Prepared Statements

```typescript
import { placeholder } from "drizzle-orm";

// Prepare a reusable statement
const getUserByEmail = db
  .select()
  .from(users)
  .where(eq(users.email, placeholder("email")))
  .prepare("get_user_by_email");

// Execute with parameters
const user = await getUserByEmail.execute({ email: "alex@example.com" });

// Prepared insert
const createUser = db
  .insert(users)
  .values({
    email: placeholder("email"),
    name: placeholder("name"),
  })
  .returning()
  .prepare("create_user");

const [newUser] = await createUser.execute({ email: "new@b.com", name: "New" });
```

---

## Drizzle + Zod Integration

```typescript
import { createInsertSchema, createSelectSchema, createUpdateSchema } from "drizzle-zod";
import { z } from "zod";

// Auto-generate Zod schemas from Drizzle table
const insertUserSchema = createInsertSchema(users, {
  email: z.string().email("Invalid email"),
  name: z.string().min(2, "Name too short").optional(),
});

const selectUserSchema = createSelectSchema(users);
const updateUserSchema = createUpdateSchema(users);

// Use in API routes / Server Actions
export async function createUser(formData: FormData) {
  const parsed = insertUserSchema.parse({
    email: formData.get("email"),
    name: formData.get("name"),
  });

  const [user] = await db.insert(users).values(parsed).returning();
  return user;
}

// Infer types
type NewUser = z.infer<typeof insertUserSchema>;
type User = z.infer<typeof selectUserSchema>;
```

---

## Transactions

```typescript
// Basic transaction
const result = await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ email: "a@b.com" }).returning();
  const [post] = await tx.insert(posts).values({ title: "Hello", authorId: user.id }).returning();

  // Throw to rollback
  if (!post) throw new Error("Failed");

  return { user, post };
});

// Nested savepoints
await db.transaction(async (tx) => {
  await tx.insert(users).values({ email: "outer@b.com" });

  try {
    await tx.transaction(async (nestedTx) => {
      await nestedTx.insert(users).values({ email: "inner@b.com" });
      throw new Error("rollback inner only");
    });
  } catch {
    // inner savepoint rolled back, outer continues
  }

  // This still commits
  await tx.insert(users).values({ email: "after@b.com" });
});
```

---

## Drizzle Kit Configuration

```typescript
// drizzle.config.ts
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
  verbose: true,
  strict: true,
});
```

### Migration Commands

```bash
# Generate migration from schema changes
npx drizzle-kit generate

# Apply pending migrations
npx drizzle-kit migrate

# Push schema directly (no migration files, dev only)
npx drizzle-kit push

# Drop migration
npx drizzle-kit drop

# View database in browser
npx drizzle-kit studio
```
