# Next.js Caching Layers

## Caching Architecture Overview

Next.js has four caching layers:

| Layer | What | Where | Duration | Invalidation |
|-------|------|-------|----------|--------------|
| **Request Memoization** | Deduplicates identical `fetch()` calls in a single render | Server | Per-request | Automatic |
| **Data Cache** | Persists `fetch()` results across requests | Server | Persistent | `revalidatePath`, `revalidateTag`, time-based |
| **Full Route Cache** | Caches rendered HTML and RSC payload for static routes | Server | Persistent | Revalidation, redeployment |
| **Router Cache** | Caches RSC payload on client for visited routes | Client | Session (5min auto, 30s dynamic) | `router.refresh()`, `revalidatePath`, cookie/header changes |

---

## Data Cache (fetch)

### Time-Based Revalidation

```typescript
// Revalidate every 60 seconds
const data = await fetch("https://api.example.com/products", {
  next: { revalidate: 60 },
});

// No cache (always fresh)
const data = await fetch("https://api.example.com/live", {
  cache: "no-store",
});

// Cache forever until manually invalidated (default for static)
const data = await fetch("https://api.example.com/config");
```

### Tag-Based Revalidation

```typescript
// Tag a fetch request
const products = await fetch("https://api.example.com/products", {
  next: { tags: ["products"] },
});

const product = await fetch(`https://api.example.com/products/${id}`, {
  next: { tags: ["products", `product-${id}`] },
});
```

```typescript
// app/actions.ts
"use server";
import { revalidateTag, revalidatePath } from "next/cache";

export async function updateProduct(id: string, data: FormData) {
  await db.product.update({ where: { id }, data: Object.fromEntries(data) });

  // Invalidate specific product and product list
  revalidateTag(`product-${id}`);
  revalidateTag("products");
}

export async function revalidateProductPage(id: string) {
  // Invalidate a specific path
  revalidatePath(`/products/${id}`);

  // Invalidate a layout and all nested pages
  revalidatePath("/products", "layout");
}
```

### Route Segment Config

```typescript
// app/products/page.tsx

// Opt entire route out of caching
export const dynamic = "force-dynamic";

// Set default revalidation for all fetches in this route
export const revalidate = 60;

// Force static generation
export const dynamic = "force-static";
```

---

## unstable_cache (non-fetch caching)

Cache database queries and other async operations that don't use `fetch()`.

```typescript
import { unstable_cache } from "next/cache";

const getCachedUser = unstable_cache(
  async (userId: string) => {
    return db.user.findUnique({
      where: { id: userId },
      include: { posts: true },
    });
  },
  ["user"],               // Cache key prefix
  {
    revalidate: 900,       // 15 minutes
    tags: ["users"],       // For on-demand invalidation
  },
);

// Usage in Server Component
export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await getCachedUser(params.id);
  return <UserProfile user={user} />;
}
```

### Dynamic Cache Keys

```typescript
const getProductsByCategory = unstable_cache(
  async (categoryId: string, page: number) => {
    return db.product.findMany({
      where: { categoryId },
      skip: (page - 1) * 20,
      take: 20,
    });
  },
  ["products-by-category"], // Base key
  {
    revalidate: 300,
    tags: ["products"],
  },
);

// Arguments are appended to the cache key automatically
const electronics = await getProductsByCategory("electronics", 1);
const clothing = await getProductsByCategory("clothing", 2);
```

---

## ISR (Incremental Static Regeneration)

### Static Params + Revalidation

```typescript
// app/products/[id]/page.tsx

// Generate static pages at build time
export async function generateStaticParams() {
  const products = await db.product.findMany({ select: { id: true } });
  return products.map((p) => ({ id: p.id }));
}

// Revalidate every 5 minutes
export const revalidate = 300;

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await db.product.findUnique({ where: { id: params.id } });
  if (!product) notFound();
  return <ProductDetail product={product} />;
}
```

### On-Demand ISR via Webhook

```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const secret = request.headers.get("x-revalidation-secret");
  if (secret !== process.env.REVALIDATION_SECRET) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { type, id } = await request.json();

  switch (type) {
    case "product":
      revalidateTag(`product-${id}`);
      revalidatePath(`/products/${id}`);
      break;
    case "all-products":
      revalidateTag("products");
      revalidatePath("/products", "layout");
      break;
  }

  return NextResponse.json({ revalidated: true, now: Date.now() });
}
```

---

## Combining Next.js Cache + Redis

### Redis as External Cache for Server Components

```typescript
// lib/cached.ts
import { redis } from "./redis";

export async function cachedQuery<T>(
  key: string,
  queryFn: () => Promise<T>,
  ttl: number = 300,
  tags?: string[],
): Promise<T> {
  // Check Redis first
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  // Execute query
  const data = await queryFn();

  // Store in Redis with TTL
  const pipeline = redis.pipeline();
  pipeline.set(key, JSON.stringify(data), "EX", ttl);
  if (tags) {
    for (const tag of tags) {
      pipeline.sadd(`tag:${tag}`, key);
    }
  }
  await pipeline.exec();

  return data;
}

// Usage in Server Component
export default async function DashboardPage() {
  const stats = await cachedQuery(
    "dashboard:stats",
    () => db.$queryRaw`SELECT count(*) FROM orders WHERE created_at > NOW() - INTERVAL '24 hours'`,
    60,
    ["dashboard"],
  );
  return <Dashboard stats={stats} />;
}
```

### Invalidate Both Redis and Next.js

```typescript
// lib/invalidate.ts
"use server";
import { revalidateTag } from "next/cache";
import { redis } from "./redis";

export async function invalidateProduct(productId: string) {
  // 1. Invalidate Redis
  await redis.del(`product:${productId}`);
  const relatedKeys = await redis.smembers(`tag:products`);
  if (relatedKeys.length) await redis.del(...relatedKeys);
  await redis.del("tag:products");

  // 2. Invalidate Next.js Data Cache
  revalidateTag(`product-${productId}`);
  revalidateTag("products");
}
```

---

## Router Cache (Client-Side)

### Force Refresh

```typescript
"use client";
import { useRouter } from "next/navigation";

function RefreshButton() {
  const router = useRouter();

  return (
    <button onClick={() => router.refresh()}>
      Refresh Data
    </button>
  );
}
```

### Opt Out of Router Cache

```typescript
// next.config.ts
const nextConfig = {
  experimental: {
    staleTimes: {
      dynamic: 0,  // Don't cache dynamic pages on client
      static: 300,  // Cache static pages for 5 min on client
    },
  },
};
```

---

## Request Memoization

Automatic deduplication within a single render pass. No configuration needed.

```typescript
// This fetch is called in layout, page, and 3 components
// but only executes ONCE per request
async function getCurrentUser() {
  const res = await fetch("/api/me");
  return res.json();
}

// Layout calls getCurrentUser()  → fetch executes
// Page calls getCurrentUser()    → returns memoized
// Component calls getCurrentUser() → returns memoized
```

**Note:** Only works with `fetch()` using the same URL and options. Does NOT work with `db.query()` or other non-fetch calls. Use `React.cache()` for non-fetch memoization:

```typescript
import { cache } from "react";

export const getCurrentUser = cache(async () => {
  return db.user.findUnique({ where: { id: getAuthUserId() } });
});
```

---

## Caching Decision Matrix

| Data Type | Strategy | Config |
|-----------|----------|--------|
| Static content (about page) | Full Route Cache | `export const dynamic = "force-static"` |
| CMS content | ISR | `export const revalidate = 300` |
| Product catalog | Tag-based | `next: { tags: ["products"] }` + `revalidateTag` |
| User-specific data | No cache | `cache: "no-store"` or `dynamic = "force-dynamic"` |
| API response (shared) | Time-based | `next: { revalidate: 60 }` |
| DB query (non-fetch) | `unstable_cache` | With tags and TTL |
| Expensive computation | Redis + `unstable_cache` | Double-layer caching |
| Real-time data | No cache + SWR client | `cache: "no-store"` server, `useSWR` client |

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `cookies()` / `headers()` opts entire route out of cache | Move dynamic logic to client components or middleware |
| `unstable_cache` inside a component re-creates function | Define outside component or use module-level constant |
| Forgetting to invalidate on mutations | Always call `revalidateTag` or `revalidatePath` in Server Actions |
| Router cache showing stale data after mutation | Call `router.refresh()` or use `revalidatePath` in the action |
| Caching user-specific data without key differentiation | Include userId in cache key or tag |
| Over-caching during development | Data Cache persists in `.next/cache` — delete to reset |
