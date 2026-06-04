# Next.js Performance Optimization

## ISR (Incremental Static Regeneration)

```typescript
// app/products/[id]/page.tsx
export const revalidate = 3600; // revalidate every hour

export async function generateStaticParams() {
  const products = await getTopProducts();
  return products.map((p) => ({ id: p.id.toString() }));
}

export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const product = await getProduct(id);
  return <ProductDetail product={product} />;
}
```

### On-Demand Revalidation

```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { path, tag, secret } = await request.json();

  if (secret !== process.env.REVALIDATION_SECRET) {
    return NextResponse.json({ error: "Invalid secret" }, { status: 401 });
  }

  if (tag) {
    revalidateTag(tag);
  } else if (path) {
    revalidatePath(path);
  }

  return NextResponse.json({ revalidated: true, now: Date.now() });
}
```

## PPR (Partial Prerendering) — Next.js 15+

```typescript
// next.config.js
module.exports = {
  experimental: {
    ppr: true,
  },
};

// app/dashboard/page.tsx
import { Suspense } from "react";

// Static shell renders at build time
export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>           {/* Static — in the shell */}
      <StaticSidebar />             {/* Static */}
      <Suspense fallback={<ChartSkeleton />}>
        <DynamicCharts />           {/* Dynamic — streams in */}
      </Suspense>
      <Suspense fallback={<FeedSkeleton />}>
        <LiveFeed />                {/* Dynamic — streams in */}
      </Suspense>
    </div>
  );
}
```

## Streaming with Suspense

```typescript
// app/search/page.tsx
import { Suspense } from "react";

export default function SearchPage({ searchParams }: {
  searchParams: Promise<{ q: string }>;
}) {
  return (
    <div>
      <SearchBar />  {/* Renders immediately */}
      <Suspense fallback={<ResultsSkeleton />}>
        <SearchResults searchParams={searchParams} />  {/* Streams when ready */}
      </Suspense>
      <Suspense fallback={<FiltersSkeleton />}>
        <Filters searchParams={searchParams} />
      </Suspense>
    </div>
  );
}

async function SearchResults({ searchParams }: { searchParams: Promise<{ q: string }> }) {
  const { q } = await searchParams;
  const results = await searchDatabase(q); // This can take time
  return <ResultsList results={results} />;
}
```

## Image Optimization

```tsx
import Image from "next/image";

// LCP image — priority loading
<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={630}
  priority              // preloads, no lazy loading
  sizes="100vw"
  quality={85}
/>

// Below-the-fold image — lazy loaded (default)
<Image
  src="/gallery/photo.jpg"
  alt="Gallery photo"
  width={400}
  height={300}
  sizes="(max-width: 768px) 100vw, 33vw"
  placeholder="blur"
  blurDataURL={blurHash}  // base64 tiny placeholder
/>

// Remote images — configure domains
// next.config.js
module.exports = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "cdn.example.com" },
    ],
    formats: ["image/avif", "image/webp"],
    deviceSizes: [640, 750, 828, 1080, 1200],
  },
};
```

## Font Optimization

```typescript
// app/layout.tsx
import { Inter, JetBrains_Mono } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono",
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

```css
/* app/globals.css */
body { font-family: var(--font-inter), system-ui, sans-serif; }
code { font-family: var(--font-mono), monospace; }
```

## Script Optimization

```tsx
import Script from "next/script";

// Analytics — load after page is interactive
<Script
  src="https://analytics.example.com/script.js"
  strategy="afterInteractive"
/>

// Non-critical widget — load when browser is idle
<Script
  src="https://widget.example.com/embed.js"
  strategy="lazyOnload"
/>

// Critical inline script — load before hydration
<Script id="theme-init" strategy="beforeInteractive">
  {`document.documentElement.dataset.theme = localStorage.getItem('theme') || 'light'`}
</Script>
```

## Data Fetching Optimization

```typescript
// Parallel data fetching
async function Dashboard() {
  // BAD: sequential (waterfall)
  const user = await getUser();
  const posts = await getPosts(user.id);

  // GOOD: parallel where possible
  const [user, notifications, stats] = await Promise.all([
    getUser(),
    getNotifications(),
    getStats(),
  ]);

  return <DashboardUI user={user} notifications={notifications} stats={stats} />;
}

// Cache with tags for targeted revalidation
async function getProduct(id: string) {
  const res = await fetch(`${API}/products/${id}`, {
    next: { tags: [`product-${id}`] },
  });
  return res.json();
}
```

## Route Segment Config

```typescript
// app/blog/[slug]/page.tsx

// Static generation (default for pages without dynamic data)
export const dynamic = "force-static";

// Always server-render (for personalized content)
export const dynamic = "force-dynamic";

// Revalidation interval
export const revalidate = 60; // seconds

// Runtime
export const runtime = "edge"; // or "nodejs"

// Maximum duration for serverless function
export const maxDuration = 30; // seconds
```

## Performance Checklist for Next.js

```markdown
- [ ] LCP image uses `priority` prop
- [ ] Images have explicit `width`/`height` or `fill`
- [ ] Fonts use `next/font` (not external <link>)
- [ ] Third-party scripts use appropriate `strategy`
- [ ] Data fetches are parallel where possible
- [ ] Suspense boundaries around slow data
- [ ] Bundle analyzer shows no unexpected large packages
- [ ] `revalidate` set appropriately per route
- [ ] Dynamic imports for heavy client components
- [ ] No unnecessary `"use client"` on data-fetching components
```
