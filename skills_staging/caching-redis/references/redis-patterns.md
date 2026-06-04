# Redis Advanced Patterns

## Pub/Sub

### Basic Pub/Sub

```typescript
import Redis from "ioredis";

// Publisher
const pub = new Redis(process.env.REDIS_URL!);

async function publishEvent(channel: string, event: object): Promise<void> {
  await pub.publish(channel, JSON.stringify(event));
}

await publishEvent("orders", { type: "created", orderId: "abc123" });

// Subscriber (separate connection required)
const sub = new Redis(process.env.REDIS_URL!);

sub.subscribe("orders", "notifications");

sub.on("message", (channel, message) => {
  const event = JSON.parse(message);
  console.log(`[${channel}]`, event);
});
```

### Pattern Subscribe

```typescript
sub.psubscribe("orders:*");

sub.on("pmessage", (pattern, channel, message) => {
  // pattern = "orders:*", channel = "orders:created"
  const event = JSON.parse(message);
  console.log(`[${channel}]`, event);
});
```

**Important:** Pub/Sub is fire-and-forget. If subscriber is offline, messages are lost. Use Redis Streams for durable messaging.

### Cache Invalidation via Pub/Sub

```typescript
// Service A: invalidate and notify
async function updateAndInvalidate(productId: string, data: Partial<Product>) {
  await db.product.update({ where: { id: productId }, data });
  await redis.del(`product:${productId}`);
  await pub.publish("cache:invalidate", JSON.stringify({
    type: "product",
    id: productId,
  }));
}

// Service B: listen for invalidations
sub.subscribe("cache:invalidate");
sub.on("message", async (channel, message) => {
  const { type, id } = JSON.parse(message);
  await localCache.del(`${type}:${id}`); // Clear local in-memory cache
});
```

---

## Lua Scripting

Lua scripts execute atomically — no other command runs between script lines.

### Rate Limiter (Sliding Window)

```typescript
const slidingWindowRateLimit = `
  local key = KEYS[1]
  local window = tonumber(ARGV[1])
  local limit = tonumber(ARGV[2])
  local now = tonumber(ARGV[3])

  -- Remove entries outside the window
  redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

  -- Count current entries
  local count = redis.call('ZCARD', key)

  if count < limit then
    -- Allow: add this request
    redis.call('ZADD', key, now, now .. '-' .. math.random(1000000))
    redis.call('EXPIRE', key, window)
    return 1
  else
    return 0
  end
`;

async function checkRateLimit(
  identifier: string,
  windowMs: number,
  limit: number,
): Promise<boolean> {
  const key = `rate:${identifier}`;
  const now = Date.now();
  const result = await redis.eval(
    slidingWindowRateLimit,
    1,
    key,
    windowMs,
    limit,
    now,
  );
  return result === 1;
}

// Usage: 100 requests per minute
const allowed = await checkRateLimit("api:/users:192.168.1.1", 60000, 100);
```

### Atomic Get-or-Set (Cache-Aside in Lua)

```typescript
const getOrSetScript = `
  local value = redis.call('GET', KEYS[1])
  if value then
    return value
  end
  -- Return nil to signal cache miss (caller must populate)
  return nil
`;

// Load script for reuse (returns SHA)
const sha = await redis.script("LOAD", getOrSetScript);
const result = await redis.evalsha(sha, 1, "product:123");
```

### Distributed Lock (Redlock-like)

```typescript
const acquireLock = `
  local key = KEYS[1]
  local token = ARGV[1]
  local ttl = tonumber(ARGV[2])

  if redis.call('SET', key, token, 'NX', 'PX', ttl) then
    return 1
  end
  return 0
`;

const releaseLock = `
  local key = KEYS[1]
  local token = ARGV[1]

  if redis.call('GET', key) == token then
    return redis.call('DEL', key)
  end
  return 0
`;

async function withLock<T>(
  resource: string,
  ttlMs: number,
  fn: () => Promise<T>,
): Promise<T> {
  const token = crypto.randomUUID();
  const lockKey = `lock:${resource}`;

  const acquired = await redis.eval(acquireLock, 1, lockKey, token, ttlMs);
  if (!acquired) throw new Error(`Failed to acquire lock: ${resource}`);

  try {
    return await fn();
  } finally {
    await redis.eval(releaseLock, 1, lockKey, token);
  }
}

// Usage
const order = await withLock("order:abc123", 5000, async () => {
  return processOrder("abc123");
});
```

---

## Transactions (MULTI/EXEC)

```typescript
// Atomic transfer between accounts
async function transfer(from: string, to: string, amount: number): Promise<void> {
  const pipeline = redis.multi();
  pipeline.decrby(`balance:${from}`, amount);
  pipeline.incrby(`balance:${to}`, amount);
  const results = await pipeline.exec();

  if (!results) throw new Error("Transaction aborted");
  for (const [err] of results) {
    if (err) throw err;
  }
}
```

### Optimistic Locking with WATCH

```typescript
async function incrementIfBelow(key: string, max: number): Promise<boolean> {
  while (true) {
    await redis.watch(key);
    const current = parseInt(await redis.get(key) || "0", 10);

    if (current >= max) {
      await redis.unwatch();
      return false;
    }

    const result = await redis
      .multi()
      .incr(key)
      .exec();

    if (result) return true; // Success
    // result is null = WATCH detected change, retry
  }
}
```

---

## Pipelining

Batch multiple commands in a single round trip.

```typescript
// Without pipeline: N round trips
for (const id of userIds) {
  await redis.get(`user:${id}`); // 100 users = 100 round trips
}

// With pipeline: 1 round trip
const pipeline = redis.pipeline();
for (const id of userIds) {
  pipeline.get(`user:${id}`);
}
const results = await pipeline.exec();
// results = [[null, "value1"], [null, "value2"], ...]

const users = results!
  .map(([err, val]) => (err ? null : val ? JSON.parse(val as string) : null))
  .filter(Boolean);
```

### Pipeline with Mixed Commands

```typescript
async function getUserDashboard(userId: string) {
  const pipeline = redis.pipeline();
  pipeline.get(`user:${userId}`);
  pipeline.smembers(`user:${userId}:roles`);
  pipeline.zrevrange(`user:${userId}:activity`, 0, 9);
  pipeline.hgetall(`user:${userId}:preferences`);

  const [
    [, userData],
    [, roles],
    [, activity],
    [, preferences],
  ] = await pipeline.exec() as any;

  return {
    user: userData ? JSON.parse(userData) : null,
    roles,
    recentActivity: activity,
    preferences,
  };
}
```

---

## Redis Cluster

### Hash Tags for Co-location

```typescript
// These keys land on different slots (distributed)
await redis.set("user:123:profile", "...");
await redis.set("user:123:posts", "...");

// Hash tags force same slot — required for multi-key operations
await redis.set("{user:123}:profile", "...");
await redis.set("{user:123}:posts", "...");

// Now you can use MGET across these keys
const [profile, posts] = await redis.mget("{user:123}:profile", "{user:123}:posts");
```

---

## Redis JSON (RedisJSON Module)

```typescript
// Store JSON natively (requires RedisJSON module)
await redis.call("JSON.SET", "user:123", "$", JSON.stringify({
  name: "Alex",
  address: { city: "Sydney", country: "AU" },
  scores: [95, 87, 92],
}));

// Get nested field
const city = await redis.call("JSON.GET", "user:123", "$.address.city");
// Returns: '["Sydney"]'

// Update nested field without fetching the whole object
await redis.call("JSON.SET", "user:123", "$.address.city", '"Melbourne"');

// Append to array
await redis.call("JSON.ARRAPPEND", "user:123", "$.scores", "88");
```

---

## Redis Search (RediSearch Module)

```typescript
// Create a search index
await redis.call(
  "FT.CREATE", "idx:products",
  "ON", "JSON",
  "PREFIX", "1", "product:",
  "SCHEMA",
  "$.name", "AS", "name", "TEXT", "WEIGHT", "5.0",
  "$.description", "AS", "description", "TEXT",
  "$.price", "AS", "price", "NUMERIC", "SORTABLE",
  "$.category", "AS", "category", "TAG",
);

// Full-text search
const results = await redis.call(
  "FT.SEARCH", "idx:products",
  "wireless headphones",
  "FILTER", "price", "0", "100",
  "SORTBY", "price", "ASC",
  "LIMIT", "0", "10",
);

// Tag filter
const electronics = await redis.call(
  "FT.SEARCH", "idx:products",
  "@category:{electronics}",
);
```

---

## Rate Limiting Patterns

### Fixed Window

```typescript
async function fixedWindowRateLimit(
  key: string,
  limit: number,
  windowSeconds: number,
): Promise<{ allowed: boolean; remaining: number }> {
  const current = await redis.incr(key);

  if (current === 1) {
    await redis.expire(key, windowSeconds);
  }

  return {
    allowed: current <= limit,
    remaining: Math.max(0, limit - current),
  };
}

// 100 requests per minute
const { allowed, remaining } = await fixedWindowRateLimit(
  `rate:${ip}:${Math.floor(Date.now() / 60000)}`,
  100,
  60,
);
```

### Token Bucket

```typescript
const tokenBucketScript = `
  local key = KEYS[1]
  local capacity = tonumber(ARGV[1])
  local refillRate = tonumber(ARGV[2])
  local now = tonumber(ARGV[3])
  local requested = tonumber(ARGV[4])

  local data = redis.call('HMGET', key, 'tokens', 'last_refill')
  local tokens = tonumber(data[1]) or capacity
  local lastRefill = tonumber(data[2]) or now

  -- Refill tokens
  local elapsed = (now - lastRefill) / 1000
  tokens = math.min(capacity, tokens + elapsed * refillRate)

  if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, math.ceil(capacity / refillRate) + 1)
    return 1
  end
  return 0
`;

async function tokenBucketAllow(
  identifier: string,
  capacity: number,
  refillPerSecond: number,
): Promise<boolean> {
  const result = await redis.eval(
    tokenBucketScript, 1,
    `bucket:${identifier}`,
    capacity, refillPerSecond, Date.now(), 1,
  );
  return result === 1;
}
```

---

## Redis Streams (Durable Messaging)

```typescript
// Producer: add event to stream
await redis.xadd("events:orders", "*", "type", "created", "orderId", "abc123", "total", "99.99");

// Consumer group setup
await redis.xgroup("CREATE", "events:orders", "order-processor", "0", "MKSTREAM").catch(() => {});

// Consumer: read events
async function consumeEvents(group: string, consumer: string): Promise<void> {
  while (true) {
    const results = await redis.xreadgroup(
      "GROUP", group, consumer,
      "COUNT", 10,
      "BLOCK", 5000,
      "STREAMS", "events:orders", ">",
    );

    if (results) {
      for (const [stream, messages] of results) {
        for (const [id, fields] of messages) {
          await processEvent(Object.fromEntries(
            fields.reduce((acc: [string, string][], v, i, a) =>
              i % 2 === 0 ? [...acc, [v, a[i + 1]]] : acc, [])
          ));
          // Acknowledge processed
          await redis.xack("events:orders", group, id);
        }
      }
    }
  }
}
```
