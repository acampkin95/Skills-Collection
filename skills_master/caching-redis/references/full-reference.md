---
name: caching-redis
description: High-performance Redis caching with cache-aside, write-through, TTL management, and cache invalidation. Use this skill when Redis cache, ioredis, cache-aside pattern, write-through cache, TTL expiration, cache invalidation, cache stampede, pub/sub Redis, Redis cluster, Next.js Data Cache, Edge caching, CDN strategy, Redis client setup. Use this skill when implementing caching layers, optimizing database queries, preventing cache stampedes, designing cache invalidation strategies, configuring Redis key naming conventions, setting up CDN headers, managing cache TTL policies, and handling distributed caching across multiple services.
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

| Structure | Use Case | Example |
|-----------|----------|---------|
| `STRING` | Simple key-value, counters, JSON blobs | Session data, cached API response |
| `HASH` | Object with fields, partial updates | User profile fields |
| `LIST` | Queues, recent items, activity feeds | Job queue, recent notifications |
| `SET` | Unique collections, tags, membership | Online users, unique visitors |
| `SORTED SET` | Ranked data, leaderboards, time series | Leaderboard, rate limiting windows |
| `STREAM` | Event log, message broker | Event sourcing, real-time feeds |

### Hash for Partial Object Caching

```typescript
// Store user fields individually — update without full rewrite
await redis.hset(`user:${userId}`, {
  name: "Alex",
  email: "alex@example.com",
  role: "admin",
  lastLogin: new Date().toISOString(),
});

// Read specific fields
const [name, email] = await redis.hmget(`user:${userId}`, "name", "email");

// Update single field
await redis.hset(`user:${userId}`, "lastLogin", new Date().toISOString());

// Set expiry on the whole hash
await redis.expire(`user:${userId}`, 3600);
```

### Sorted Set for Leaderboards

```typescript
// Add scores
await redis.zadd("leaderboard:daily", score, `player:${playerId}`);

// Top 10 players (highest first)
const top10 = await redis.zrevrange("leaderboard:daily", 0, 9, "WITHSCORES");

// Player rank (0-based)
const rank = await redis.zrevrank("leaderboard:daily", `player:${playerId}`);
```

---

## ioredis Client Setup

### Basic Setup

```typescript
// lib/redis.ts
import Redis from "ioredis";

// Singleton pattern for serverless/Next.js
const globalForRedis = globalThis as unknown as { redis: Redis | undefined };

export const redis =
  globalForRedis.redis ??
  new Redis(process.env.REDIS_URL!, {
    maxRetriesPerRequest: 3,
    retryStrategy(times) {
      if (times > 3) return null; // Stop retrying
      return Math.min(times * 200, 2000);
    },
    reconnectOnError(err) {
      return err.message.includes("READONLY");
    },
    lazyConnect: true,
    enableReadyCheck: true,
    connectTimeout: 5000,
  });

if (process.env.NODE_ENV !== "production") {
  globalForRedis.redis = redis;
}
```

### With Cluster

```typescript
import Redis from "ioredis";

const redis = new Redis.Cluster(
  [
    { host: "redis-node-1", port: 6379 },
    { host: "redis-node-2", port: 6379 },
    { host: "redis-node-3", port: 6379 },
  ],
  {
    redisOptions: { password: process.env.REDIS_PASSWORD },
    scaleReads: "slave", // Read from replicas
    slotsRefreshTimeout: 2000,
  }
);
```

---

## Key Naming Conventions

```
{entity}:{id}                    → user:abc123
{entity}:{id}:{field}            → user:abc123:sessions
{scope}:{entity}:{id}            → cache:product:456
{scope}:{entity}:{qualifier}     → rate:api:/users:192.168.1.1
{env}:{scope}:{entity}:{id}      → prod:cache:order:789
```

**Rules:**
- Use colons `:` as delimiters
- Lowercase everything
- Keep keys short (Redis stores keys in memory)
- Prefix with namespace to avoid collisions: `myapp:cache:user:123`
- Use `{}` for Redis Cluster hash tags: `{user:123}:profile`, `{user:123}:posts` (same slot)

---

## TTL Strategies

### Tiered TTL by Data Volatility

```typescript
const TTL = {
  // Rarely changes
  CONFIG: 86400,        // 24 hours
  STATIC_CONTENT: 3600, // 1 hour

  // Changes occasionally
  USER_PROFILE: 900,    // 15 minutes
  PRODUCT_LISTING: 300, // 5 minutes

  // Changes frequently
  FEED: 60,             // 1 minute
  ONLINE_STATUS: 30,    // 30 seconds

  // Volatile
  RATE_LIMIT: 60,       // 1 minute window
  OTP: 300,             // 5 minutes
} as const;
```

### Sliding TTL (Reset on Access)

```typescript
async function getWithSlidingTTL(key: string, ttl: number): Promise<string | null> {
  const pipeline = redis.pipeline();
  pipeline.get(key);
  pipeline.expire(key, ttl); // Reset TTL on every read
  const [[, value]] = await pipeline.exec() as [[null, string | null]];
  return value;
}
```

---

## Cache Invalidation Patterns

### Direct Invalidation

```typescript
// Delete on write
async function updateProduct(id: string, data: Partial<Product>): Promise<Product> {
  const product = await db.product.update({ where: { id }, data });

  // Invalidate specific key
  await redis.del(`product:${id}`);

  // Invalidate related keys (list pages, category pages)
  await redis.del(`products:list`, `category:${product.categoryId}:products`);

  return product;
}
```

### Pattern-Based Invalidation (SCAN)

```typescript
// Delete all keys matching a pattern — use SCAN, never KEYS in production
async function invalidatePattern(pattern: string): Promise<number> {
  let cursor = "0";
  let deleted = 0;

  do {
    const [nextCursor, keys] = await redis.scan(cursor, "MATCH", pattern, "COUNT", 100);
    cursor = nextCursor;
    if (keys.length > 0) {
      deleted += await redis.del(...keys);
    }
  } while (cursor !== "0");

  return deleted;
}

await invalidatePattern("product:*");
```

### Tag-Based Invalidation

```typescript
// Tag cache entries for group invalidation
async function setWithTags(key: string, value: string, ttl: number, tags: string[]): Promise<void> {
  const pipeline = redis.pipeline();
  pipeline.set(key, value, "EX", ttl);
  for (const tag of tags) {
    pipeline.sadd(`tag:${tag}`, key);
    pipeline.expire(`tag:${tag}`, ttl + 60); // Tag outlives entries
  }
  await pipeline.exec();
}

async function invalidateByTag(tag: string): Promise<void> {
  const keys = await redis.smembers(`tag:${tag}`);
  if (keys.length > 0) {
    await redis.del(...keys, `tag:${tag}`);
  }
}

// Usage
await setWithTags("product:123", json, 300, ["products", "category:electronics"]);
await invalidateByTag("category:electronics"); // Clears all electronics products
```

---

## Cache Stampede Prevention

### Mutex Lock (Single Recompute)

```typescript
async function getWithMutex<T>(
  key: string,
  ttl: number,
  fetchFn: () => Promise<T>,
): Promise<T> {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const lockKey = `lock:${key}`;
  // NX = only set if not exists, EX = lock expires in 10s
  const acquired = await redis.set(lockKey, "1", "EX", 10, "NX");

  if (acquired) {
    try {
      const data = await fetchFn();
      await redis.set(key, JSON.stringify(data), "EX", ttl);
      return data;
    } finally {
      await redis.del(lockKey);
    }
  }

  // Another process is recomputing — wait and retry
  await new Promise((r) => setTimeout(r, 100));
  return getWithMutex(key, ttl, fetchFn);
}
```

### Probabilistic Early Expiration (PER)

```typescript
async function getWithPER<T>(
  key: string,
  ttl: number,
  fetchFn: () => Promise<T>,
  beta: number = 1.0, // Higher = earlier recompute
): Promise<T> {
  const pipeline = redis.pipeline();
  pipeline.get(key);
  pipeline.ttl(key);
  const [[, cached], [, remainingTTL]] = await pipeline.exec() as [[null, string | null], [null, number]];

  if (cached) {
    // Probabilistically recompute before expiry
    const expiry = ttl - (remainingTTL as number);
    const random = -Math.log(Math.random()) * beta;
    if (random < expiry / ttl) {
      // Don't await — recompute in background
      fetchFn().then((data) =>
        redis.set(key, JSON.stringify(data), "EX", ttl)
      );
    }
    return JSON.parse(cached as string);
  }

  // Cache miss
  const data = await fetchFn();
  await redis.set(key, JSON.stringify(data), "EX", ttl);
  return data;
}
```

### Stale-While-Revalidate in Redis

```typescript
async function getWithSWR<T>(
  key: string,
  ttl: number,
  staleTTL: number, // Extra time to serve stale data
  fetchFn: () => Promise<T>,
): Promise<T> {
  const raw = await redis.get(key);

  if (raw) {
    const { data, setAt } = JSON.parse(raw);
    const age = Date.now() - setAt;

    if (age > ttl * 1000) {
      // Stale — revalidate in background
      fetchFn().then((fresh) =>
        redis.set(key, JSON.stringify({ data: fresh, setAt: Date.now() }), "EX", ttl + staleTTL)
      );
    }
    return data;
  }

  // Cache miss
  const data = await fetchFn();
  await redis.set(key, JSON.stringify({ data, setAt: Date.now() }), "EX", ttl + staleTTL);
  return data;
}
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Using `KEYS` in production | Use `SCAN` with cursor — `KEYS` blocks Redis |
| No TTL on cache entries | Always set TTL — unbounded cache = memory leak |
| JSON.stringify on every read/write | Use hashes for objects you update partially |
| Single Redis instance for everything | Separate cache from session/queue Redis instances |
| Not handling Redis connection failures | Wrap in try/catch, fall back to DB on failure |
| Cache and DB out of sync | Use write-through or invalidate-on-write |
| Thundering herd on popular key expiry | Use mutex lock or probabilistic early expiration |
| Caching errors/null values | Check before caching: `if (data) await redis.set(...)` |
| Keys without namespace prefix | Always prefix: `myapp:cache:entity:id` |
| Large values in Redis (>1MB) | Compress with gzip or split into chunks |
