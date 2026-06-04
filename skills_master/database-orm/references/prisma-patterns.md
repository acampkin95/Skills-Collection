# Prisma Advanced Patterns

## Relations

### One-to-One

```prisma
model User {
  id      String   @id @default(uuid())
  profile Profile?
}

model Profile {
  id     String @id @default(uuid())
  bio    String?
  user   User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId String @unique @map("user_id")

  @@map("profiles")
}
```

### One-to-Many

```prisma
model User {
  id    String @id @default(uuid())
  posts Post[]
}

model Post {
  id       String @id @default(uuid())
  author   User   @relation(fields: [authorId], references: [id], onDelete: Cascade)
  authorId String @map("author_id")

  @@index([authorId])
  @@map("posts")
}
```

### Many-to-Many (Implicit)

```prisma
model Post {
  id         String     @id @default(uuid())
  categories Category[]
}

model Category {
  id    String @id @default(uuid())
  name  String @unique
  posts Post[]
}
```

### Many-to-Many (Explicit Join Table)

```prisma
model Post {
  id         String         @id @default(uuid())
  categories PostCategory[]
}

model Category {
  id    String         @id @default(uuid())
  name  String         @unique
  posts PostCategory[]
}

model PostCategory {
  post       Post     @relation(fields: [postId], references: [id], onDelete: Cascade)
  postId     String   @map("post_id")
  category   Category @relation(fields: [categoryId], references: [id], onDelete: Cascade)
  categoryId String   @map("category_id")
  assignedAt DateTime @default(now()) @map("assigned_at")

  @@id([postId, categoryId])
  @@map("post_categories")
}
```

### Self-Relation

```prisma
model Employee {
  id         String     @id @default(uuid())
  name       String
  managerId  String?    @map("manager_id")
  manager    Employee?  @relation("ManagerReports", fields: [managerId], references: [id])
  reports    Employee[] @relation("ManagerReports")

  @@map("employees")
}
```

---

## Nested Writes

```typescript
// Create with nested relations
const user = await prisma.user.create({
  data: {
    email: "user@example.com",
    name: "Alex",
    profile: {
      create: { bio: "Developer" },
    },
    posts: {
      create: [
        { title: "Post 1", content: "Hello" },
        { title: "Post 2", content: "World" },
      ],
    },
  },
  include: { profile: true, posts: true },
});

// Update with nested operations
const updated = await prisma.user.update({
  where: { id: userId },
  data: {
    posts: {
      create: { title: "New Post" },          // add new
      update: {
        where: { id: postId },
        data: { published: true },             // update existing
      },
      deleteMany: { published: false },        // delete matching
      disconnect: { id: otherPostId },         // remove relation (M:N)
      connect: { id: existingPostId },         // add relation (M:N)
    },
  },
});

// createMany for bulk inserts (no nested creates)
await prisma.post.createMany({
  data: [
    { title: "A", authorId: userId },
    { title: "B", authorId: userId },
    { title: "C", authorId: userId },
  ],
  skipDuplicates: true,
});
```

---

## Transactions

### Sequential Operations

```typescript
const result = await prisma.$transaction(async (tx) => {
  // All queries use `tx` instead of `prisma`
  const user = await tx.user.create({
    data: { email: "new@example.com" },
  });

  const account = await tx.account.create({
    data: { userId: user.id, balance: 0 },
  });

  // Throw to rollback
  if (!account) {
    throw new Error("Failed to create account");
  }

  return { user, account };
});
```

### Batch Operations

```typescript
// All-or-nothing batch (runs in single transaction)
const [users, posts, deletedComments] = await prisma.$transaction([
  prisma.user.findMany(),
  prisma.post.updateMany({ where: { published: false }, data: { published: true } }),
  prisma.comment.deleteMany({ where: { spam: true } }),
]);
```

### Transaction Options

```typescript
await prisma.$transaction(
  async (tx) => {
    // long-running transaction
  },
  {
    maxWait: 5000,      // max time to acquire connection (ms)
    timeout: 10000,     // max transaction duration (ms)
    isolationLevel: "Serializable", // ReadUncommitted | ReadCommitted | RepeatableRead | Serializable
  }
);
```

---

## Client Extensions (Prisma 6.x)

### Custom Methods

```typescript
const prisma = new PrismaClient().$extends({
  model: {
    user: {
      async findByEmail(email: string) {
        return prisma.user.findUnique({ where: { email } });
      },
      async softDelete(id: string) {
        return prisma.user.update({
          where: { id },
          data: { deletedAt: new Date() },
        });
      },
    },
  },
});

// Usage
const user = await prisma.user.findByEmail("test@example.com");
await prisma.user.softDelete(userId);
```

### Computed Fields

```typescript
const prisma = new PrismaClient().$extends({
  result: {
    user: {
      fullName: {
        needs: { firstName: true, lastName: true },
        compute(user) {
          return `${user.firstName} ${user.lastName}`;
        },
      },
    },
  },
});

const user = await prisma.user.findFirst();
console.log(user.fullName); // typed and computed
```

### Query Middleware via Extensions

```typescript
const prisma = new PrismaClient().$extends({
  query: {
    $allModels: {
      async findMany({ model, operation, args, query }) {
        // Add soft-delete filter globally
        args.where = { ...args.where, deletedAt: null };
        return query(args);
      },
    },
  },
});
```

---

## Raw SQL

```typescript
// Tagged template (safe from injection)
const users = await prisma.$queryRaw<User[]>`
  SELECT * FROM users WHERE email = ${email}
`;

// With Prisma.sql for dynamic queries
import { Prisma } from "@prisma/client";

const orderBy = Prisma.sql`ORDER BY created_at DESC`;
const users = await prisma.$queryRaw`
  SELECT * FROM users ${orderBy} LIMIT ${limit}
`;

// Execute (INSERT, UPDATE, DELETE)
const count = await prisma.$executeRaw`
  UPDATE users SET status = 'inactive'
  WHERE last_login < NOW() - INTERVAL '1 year'
`;

// NEVER do this (SQL injection)
// await prisma.$queryRawUnsafe(`SELECT * FROM users WHERE email = '${email}'`);
```

---

## Type-Safe Queries

### Filtering

```typescript
import { Prisma } from "@prisma/client";

// Build dynamic where clause
function buildUserFilter(params: {
  search?: string;
  role?: string;
  active?: boolean;
}): Prisma.UserWhereInput {
  const where: Prisma.UserWhereInput = {};

  if (params.search) {
    where.OR = [
      { name: { contains: params.search, mode: "insensitive" } },
      { email: { contains: params.search, mode: "insensitive" } },
    ];
  }
  if (params.role) {
    where.role = params.role as Role;
  }
  if (params.active !== undefined) {
    where.deletedAt = params.active ? null : { not: null };
  }
  return where;
}

const users = await prisma.user.findMany({
  where: buildUserFilter({ search: "alex", role: "ADMIN" }),
  orderBy: { createdAt: "desc" },
  take: 20,
  skip: 0,
});
```

### Pagination Pattern

```typescript
async function paginate<T>(
  model: { findMany: Function; count: Function },
  args: { where?: any; orderBy?: any; page: number; perPage: number }
) {
  const { page, perPage, ...queryArgs } = args;
  const skip = (page - 1) * perPage;

  const [items, total] = await prisma.$transaction([
    (model as any).findMany({ ...queryArgs, skip, take: perPage }),
    (model as any).count({ where: queryArgs.where }),
  ]);

  return {
    items: items as T[],
    total,
    page,
    perPage,
    totalPages: Math.ceil(total / perPage),
  };
}

// Usage
const result = await paginate<User>(prisma.user, {
  where: { role: "ADMIN" },
  orderBy: { createdAt: "desc" },
  page: 1,
  perPage: 20,
});
```

---

## Prisma Accelerate

```typescript
import { PrismaClient } from "@prisma/client";
import { withAccelerate } from "@prisma/extension-accelerate";

const prisma = new PrismaClient().$extends(withAccelerate());

// Cache strategies
const users = await prisma.user.findMany({
  cacheStrategy: {
    ttl: 60,      // Time to live in seconds
    swr: 120,     // Stale-while-revalidate window
  },
});

// No cache (real-time data)
const order = await prisma.order.findUnique({
  where: { id: orderId },
  // No cacheStrategy = no caching
});
```

**Setup:**
```
# .env
DATABASE_URL="prisma://accelerate.prisma-data.net/?api_key=YOUR_KEY"
DIRECT_URL="postgresql://user:pass@host:5432/db"  # for migrations
```

---

## Connection Pooling Best Practices

```typescript
// Singleton pattern (critical for serverless)
import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "development" ? ["query", "warn", "error"] : ["error"],
  });

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
```

### Connection Limits

| Environment | Recommended Pool Size |
|-------------|----------------------|
| Serverless (Vercel) | 1-5 (use Accelerate) |
| Small server | 5-10 |
| Medium server | 10-20 |
| Large server | 20-50 |

```
# Control pool size via URL
DATABASE_URL="postgresql://user:pass@host:5432/db?connection_limit=10&pool_timeout=30"
```
