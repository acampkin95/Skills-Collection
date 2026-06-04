# Edge & CDN Caching

## Cache-Control Headers

### Syntax

```
Cache-Control: <directive>, <directive>, ...
```

### Essential Directives

| Directive | Meaning |
|-----------|---------|
| `public` | Any cache (CDN, browser) can store |
| `private` | Only browser can store (user-specific data) |
| `no-cache` | Must revalidate with origin before using cached copy |
| `no-store` | Never cache (sensitive data) |
| `max-age=N` | Fresh for N seconds |
| `s-maxage=N` | Fresh for N seconds in shared caches (CDN) — overrides `max-age` |
| `stale-while-revalidate=N` | Serve stale for N seconds while fetching fresh copy |
| `stale-if-error=N` | Serve stale for N seconds if origin is down |
| `immutable` | Never revalidate (use with hashed filenames) |
| `must-revalidate` | Don't serve stale — revalidate or error |

### Common Patterns

```typescript
// Next.js API route / Route Handler headers

// Static asset (hashed filename)
// Cache forever at CDN and browser — immutable
headers.set("Cache-Control", "public, max-age=31536000, immutable");

// API response — cache at CDN for 60s, serve stale for 300s while revalidating
headers.set("Cache-Control", "public, s-maxage=60, stale-while-revalidate=300");

// User-specific — browser only, no CDN
headers.set("Cache-Control", "private, max-age=0, must-revalidate");

// Sensitive data — never cache
headers.set("Cache-Control", "no-store");

// HTML page — CDN 10min, browser 0 (always revalidate), stale fallback 1hr
headers.set("Cache-Control", "public, s-maxage=600, max-age=0, stale-while-revalidate=3600, stale-if-error=86400");
```

### Next.js Route Handler Example

```typescript
// app/api/products/route.ts
import { NextResponse } from "next/server";

export async function GET() {
  const products = await db.product.findMany();

  return NextResponse.json(products, {
    headers: {
      "Cache-Control": "public, s-maxage=300, stale-while-revalidate=600",
      "CDN-Cache-Control": "max-age=300", // Vercel/Cloudflare specific
      "Vary": "Accept-Encoding",
    },
  });
}
```

---

## Vary Header

Controls which request headers cause a separate cache entry.

```typescript
// Different cache entries for different Accept-Encoding
headers.set("Vary", "Accept-Encoding");

// Different cache for JSON vs HTML
headers.set("Vary", "Accept");

// Per-language cache
headers.set("Vary", "Accept-Language");

// Multiple headers
headers.set("Vary", "Accept-Encoding, Accept-Language, Authorization");
```

**Warning:** `Vary: *` disables caching entirely. `Vary: Cookie` effectively disables CDN caching (every user gets unique entry). Use `Vary: Authorization` instead when possible.

---

## Vercel Edge Caching

### Route Handler Caching

```typescript
// app/api/data/route.ts
export const runtime = "edge"; // Run at edge

export async function GET(request: Request) {
  const data = await fetchData();

  return new Response(JSON.stringify(data), {
    headers: {
      "Content-Type": "application/json",
      // Vercel CDN caches this for 60s
      "Cache-Control": "s-maxage=60, stale-while-revalidate=300",
    },
  });
}
```

### Vercel-Specific Headers

```typescript
// CDN-Cache-Control: separate CDN and browser cache times
headers.set("CDN-Cache-Control", "max-age=3600"); // CDN: 1 hour
headers.set("Cache-Control", "max-age=60");        // Browser: 1 minute

// Vercel-CDN-Cache-Control: Vercel-only directive
headers.set("Vercel-CDN-Cache-Control", "max-age=3600");
```

### Vercel Cache Tags (Purge API)

```typescript
// Set cache tag in response
export async function GET() {
  return NextResponse.json(data, {
    headers: {
      "Cache-Tag": "products,product-123",
    },
  });
}

// Purge via API
await fetch("https://api.vercel.com/v1/edge-config/purge", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.VERCEL_API_TOKEN}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    tags: ["products"],
  }),
});
```

### Middleware Caching

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Cache all /api/public/* routes
  if (request.nextUrl.pathname.startsWith("/api/public")) {
    response.headers.set(
      "Cache-Control",
      "public, s-maxage=300, stale-while-revalidate=600"
    );
  }

  // Never cache authenticated routes
  if (request.nextUrl.pathname.startsWith("/api/me")) {
    response.headers.set("Cache-Control", "private, no-cache");
  }

  return response;
}
```

---

## Cloudflare Cache Rules

### Page Rules (Cache Everything)

```
URL: example.com/api/products/*
Setting: Cache Level = Cache Everything
Edge Cache TTL: 300
Browser Cache TTL: 60
```

### Cache Rules (Modern)

```typescript
// Cloudflare Worker: programmatic cache control
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Check Cloudflare cache
    const cacheKey = new Request(url.toString(), request);
    const cache = caches.default;
    let response = await cache.match(cacheKey);

    if (!response) {
      response = await fetch(request);

      // Clone and modify headers
      response = new Response(response.body, response);
      response.headers.set("Cache-Control", "s-maxage=300");

      // Store in Cloudflare cache
      await cache.put(cacheKey, response.clone());
    }

    return response;
  },
};
```

### Cloudflare Cache Tags (Enterprise)

```typescript
// Set Surrogate-Key for tag-based purging
response.headers.set("Cache-Tag", "product-123,category-electronics");

// Purge by tag via API
await fetch(`https://api.cloudflare.com/client/v4/zones/${zoneId}/purge_cache`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${CF_API_TOKEN}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    tags: ["product-123"],
  }),
});

// Purge everything
await fetch(`https://api.cloudflare.com/client/v4/zones/${zoneId}/purge_cache`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${CF_API_TOKEN}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    purge_everything: true,
  }),
});
```

---

## Browser Cache Strategies

### Service Worker Cache

```typescript
// sw.ts
const CACHE_NAME = "app-cache-v1";
const PRECACHE_URLS = ["/", "/offline.html", "/styles/main.css"];

self.addEventListener("install", (event: ExtendableEvent) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
});

self.addEventListener("fetch", (event: FetchEvent) => {
  const { request } = event;

  // API calls: Network first, cache fallback
  if (request.url.includes("/api/")) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request) as Promise<Response>)
    );
    return;
  }

  // Static assets: Cache first, network fallback
  event.respondWith(
    caches.match(request).then((cached) => {
      return cached || fetch(request);
    })
  );
});
```

### ETag / If-None-Match

```typescript
// app/api/data/route.ts
import { createHash } from "crypto";

export async function GET(request: Request) {
  const data = await fetchData();
  const json = JSON.stringify(data);

  const etag = `"${createHash("md5").update(json).digest("hex")}"`;

  // Check if client has fresh copy
  if (request.headers.get("If-None-Match") === etag) {
    return new Response(null, { status: 304 });
  }

  return new Response(json, {
    headers: {
      "Content-Type": "application/json",
      "ETag": etag,
      "Cache-Control": "no-cache", // Always revalidate with ETag
    },
  });
}
```

---

## Caching Headers Decision Tree

```
Is this sensitive/user-specific data?
├── Yes → Cache-Control: private, no-store
│         (or private, no-cache if ETag is useful)
└── No → Is it a hashed/versioned static asset?
    ├── Yes → Cache-Control: public, max-age=31536000, immutable
    └── No → Does it change frequently?
        ├── Yes → Cache-Control: public, s-maxage=60, stale-while-revalidate=300
        └── No → Does it need instant invalidation?
            ├── Yes → Cache-Control: public, s-maxage=300
            │         + Use cache tags for purging
            └── No → Cache-Control: public, s-maxage=3600, stale-while-revalidate=86400
```

---

## Multi-Layer Caching Strategy

```
Request
  ↓
[Browser Cache] ← max-age (private)
  ↓ (miss)
[CDN Edge Cache] ← s-maxage (public), stale-while-revalidate
  ↓ (miss)
[Application Server]
  ↓
[Redis Cache] ← Application-level TTL
  ↓ (miss)
[Database]
```

```typescript
// Complete multi-layer example
export async function GET(request: Request) {
  // Layer 3: Redis cache
  const cacheKey = "api:products:featured";
  const cached = await redis.get(cacheKey);

  let products: Product[];
  if (cached) {
    products = JSON.parse(cached);
  } else {
    // Layer 4: Database
    products = await db.product.findMany({
      where: { featured: true },
      take: 20,
    });
    await redis.set(cacheKey, JSON.stringify(products), "EX", 300);
  }

  return NextResponse.json(products, {
    headers: {
      // Layer 1: Browser cache (1 minute)
      // Layer 2: CDN cache (5 minutes) with stale fallback
      "Cache-Control": "public, max-age=60, s-maxage=300, stale-while-revalidate=600",
      "Vary": "Accept-Encoding",
    },
  });
}
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `Vary: Cookie` kills CDN caching | Use `Vary: Authorization` or strip cookies at CDN |
| Forgetting `Vary: Accept-Encoding` | Always include for text responses (CDN compresses) |
| Setting `max-age` instead of `s-maxage` | Use `s-maxage` for CDN — `max-age` affects browser too |
| Caching HTML with `max-age > 0` | Use `s-maxage` for CDN, `max-age=0` for browser |
| Not including cache tag on response | Can't purge without tags — plan invalidation upfront |
| Long `max-age` on non-hashed assets | Only use immutable/long TTL with fingerprinted filenames |
| Caching 500/error responses at CDN | Set `Cache-Control: no-store` on error responses |
| Browser showing stale page after deploy | Use `max-age=0, must-revalidate` for HTML pages |
