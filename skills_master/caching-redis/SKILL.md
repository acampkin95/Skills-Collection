---
name: caching-redis
description: Redis caching with cache-aside, write-through, TTL, and invalidation patterns. Use for ioredis, cache stampede prevention, CDN headers, and distributed caching.
version: 2.0.0
reviewed: "2026-06-04"
---
# Caching & Redis Skill

**Read the relevant reference file before starting work.**

## Quick Navigation

| Task | Reference |
|------|-----------|
| Redis pub/sub, Lua scripts, transactions, clustering | `references/redis-patterns.md` |
| Next.js Data Cache, Route Cache, ISR, revalidation | `references/nextjs-caching.md` |
| CDN headers, Vercel Edge, Cloudflare, browser cache | `references/edge-caching.md` |

---

## Caching Fundamentals

### Cache-Aside (Lazy Loading)

Application checks cache first, fetches from DB on miss, then populates cache.

```typescript
import Redis from "ioredis";

const redis = new Redis(process.env.REDIS_URL);

async function getUser(userId: string): Promise<User> {
  const cacheKey = `user:${userId}`;

  // 1. Check cache
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // 2. Cache miss — fetch from DB
  const user = await db.user.findUniqueOrThrow({ where: { id: userId } });

  // 3. Populate cache with TTL
  await redis.set(cacheKey, JSON.stringify(user), "EX", 3600);

  return user;
}
```

**Pros:** Only caches what's requested, resilient to cache failures.
**Cons:** Cache miss penalty (3 round trips), data can be stale.

### Write-Through

Write to cache and DB simultaneously on every write.

```typescript
async function updateUser(userId: string, data: Partial<User>): Promise<User> {
  // 1. Write to DB
  const user = await db.user.update({ where: { id: userId }, data });

  // 2. Write to cache immediately
  await redis.set(`user:${userId}`, JSON.stringify(user), "EX", 3600);

  return user;
}
```

**Pros:** Cache always consistent with DB.
**Cons:** Write latency (2 writes), caches data that may never be read.

### Write-Behind (Write-Back)

Write to cache immediately, asynchronously persist to DB.

```typescript
async function updateUserFast(userId: string, data: Partial<User>): Promise<void> {
  const cacheKey = `user:${userId}`;

  // 1. Write to cache
  await redis.set(cacheKey, JSON.stringify(data), "EX", 3600);

  // 2. Queue async DB write
  await redis.lpush("write-behind:users", JSON.stringify({ userId, data, ts: Date.now() }));
}

// Background worker processes the queue
async function processWriteBehindQueue(): Promise<void> {
  while (true) {
    const item = await redis.brpop("write-behind:users", 5);
    if (item) {
      const { userId, data } = JSON.parse(item[1]);
      await db.user.update({ where: { id: userId }, data });
    }
  }
}
```

**Pros:** Fastest writes, batching possible.
**Cons:** Risk of data loss if Redis crashes before DB write.

---

## Redis Data Structures

### When to Use What


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.