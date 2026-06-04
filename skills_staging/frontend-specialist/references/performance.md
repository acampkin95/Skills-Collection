# Performance Optimization Reference

## Core Web Vitals

| Metric | Good | Needs Work | Poor |
|--------|------|------------|------|
| LCP (Largest Contentful Paint) | ≤2.5s | ≤4.0s | >4.0s |
| INP (Interaction to Next Paint) | ≤200ms | ≤500ms | >500ms |
| CLS (Cumulative Layout Shift) | ≤0.1 | ≤0.25 | >0.25 |

## Images

### Next.js Image Component

```tsx
import Image from 'next/image'

// Basic usage - automatically optimized
<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority  // LCP image - preload
/>

// Fill container
<div className="relative aspect-video">
  <Image
    src="/background.jpg"
    alt=""
    fill
    className="object-cover"
    sizes="100vw"
  />
</div>

// Responsive sizes
<Image
  src="/product.jpg"
  alt="Product"
  width={800}
  height={600}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
/>
```

### Image Best Practices

```tsx
// ✅ Use modern formats (automatic in Next.js)
// WebP, AVIF served automatically

// ✅ Lazy load below-fold images (default)
<Image src="..." loading="lazy" />

// ✅ Priority for LCP images
<Image src="..." priority />

// ✅ Specify dimensions to prevent CLS
<Image src="..." width={400} height={300} />

// ✅ Use blur placeholder
<Image
  src="..."
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>

// ❌ Don't use layout shift causing patterns
<img src="..." />  // No dimensions = CLS
```

### Responsive Images (Vanilla)

```html
<picture>
  <source
    srcset="/hero-mobile.webp"
    media="(max-width: 768px)"
    type="image/webp"
  />
  <source
    srcset="/hero-desktop.webp"
    media="(min-width: 769px)"
    type="image/webp"
  />
  <img
    src="/hero-desktop.jpg"
    alt="Hero"
    loading="lazy"
    decoding="async"
    width="1200"
    height="600"
  />
</picture>
```

## Code Splitting

### Dynamic Imports

```tsx
// Component-level splitting
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('@/components/Chart'), {
  loading: () => <ChartSkeleton />,
  ssr: false,  // Client-only component
})

// Route-level (automatic in App Router)
// Each page.tsx is automatically code-split
```

### Lazy Loading Components

```tsx
'use client'
import { lazy, Suspense } from 'react'

const HeavyComponent = lazy(() => import('./HeavyComponent'))

export function Parent() {
  return (
    <Suspense fallback={<Loading />}>
      <HeavyComponent />
    </Suspense>
  )
}
```

### Bundle Analysis

```bash
# Next.js
npm install @next/bundle-analyzer

# next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})
module.exports = withBundleAnalyzer(nextConfig)

# Run
ANALYZE=true npm run build
```

## Fonts

### Next.js Font Optimization

```tsx
// app/layout.tsx
import { Inter, Playfair_Display } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

const playfair = Playfair_Display({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-playfair',
})

export default function Layout({ children }) {
  return (
    <html className={`${inter.variable} ${playfair.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  )
}
```

```css
/* tailwind.config or CSS */
:root {
  --font-sans: var(--font-inter);
  --font-display: var(--font-playfair);
}
```

### Local Fonts

```tsx
import localFont from 'next/font/local'

const calSans = localFont({
  src: '../fonts/CalSans-SemiBold.woff2',
  display: 'swap',
  variable: '--font-cal',
})
```

### Font Loading Strategies

```tsx
// swap - show fallback immediately, swap when loaded (best for body)
display: 'swap'

// optional - use if available, don't block (good for non-critical)
display: 'optional'

// block - hide text until loaded (use sparingly)
display: 'block'
```

## JavaScript

### Defer Non-Critical Scripts

```tsx
// next/script
import Script from 'next/script'

// Analytics - load after hydration
<Script
  src="https://analytics.example.com/script.js"
  strategy="afterInteractive"
/>

// Third-party widgets - load when idle
<Script
  src="https://widget.example.com/embed.js"
  strategy="lazyOnload"
/>

// Critical - load immediately (rare)
<Script
  src="https://critical.example.com/script.js"
  strategy="beforeInteractive"
/>
```

### Minimize Client-Side JS

```tsx
// ✅ Server Component (no JS shipped)
export default async function Page() {
  const data = await getData()
  return <StaticContent data={data} />
}

// ❌ Unnecessary client component
'use client'
export default function Page() {
  // Only use client when needed
}
```

### Tree Shaking

```tsx
// ✅ Named imports (tree shakeable)
import { format } from 'date-fns'

// ❌ Default imports (may include entire library)
import _ from 'lodash'

// ✅ Specific imports
import debounce from 'lodash/debounce'
```

## CSS

### Critical CSS

Next.js automatically inlines critical CSS. For custom setups:

```html
<!-- Inline critical CSS -->
<style>
  /* Above-fold styles */
</style>

<!-- Defer non-critical CSS -->
<link rel="preload" href="/styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="/styles.css"></noscript>
```

### Tailwind Optimization

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  // Purges unused CSS automatically in production
}
```

### Avoid Layout Shift

```css
/* Reserve space for dynamic content */
.image-container {
  aspect-ratio: 16 / 9;
}

/* Fixed heights for loading states */
.skeleton {
  height: 200px;
}

/* Font metrics matching */
.fallback-font {
  font-family: Arial;
  size-adjust: 100.06%;
  ascent-override: 99%;
  descent-override: 22%;
}
```

## Caching

### Next.js Caching

```tsx
// Static (cached indefinitely)
fetch('https://api.example.com/data')

// Revalidate every 60 seconds
fetch('https://api.example.com/data', {
  next: { revalidate: 60 }
})

// No cache
fetch('https://api.example.com/data', {
  cache: 'no-store'
})

// Tag-based revalidation
fetch('https://api.example.com/data', {
  next: { tags: ['posts'] }
})

// Revalidate tag
import { revalidateTag } from 'next/cache'
revalidateTag('posts')
```

### Static Generation

```tsx
// Generates at build time
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({
    slug: post.slug,
  }))
}

export default async function Page({ params }) {
  const post = await getPost(params.slug)
  return <Post post={post} />
}
```

## Server Components

### Benefits

- Zero client-side JavaScript
- Direct database/API access
- Smaller bundle size
- Better SEO

### Pattern

```tsx
// Server Component (default)
export default async function Page() {
  const data = await db.query('SELECT * FROM posts')
  
  return (
    <div>
      <h1>Posts</h1>
      {data.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
          <LikeButton postId={post.id} />  {/* Client island */}
        </article>
      ))}
    </div>
  )
}

// Client Component (interactive island)
'use client'
export function LikeButton({ postId }) {
  const [likes, setLikes] = useState(0)
  return <button onClick={() => like(postId)}>♥ {likes}</button>
}
```

## Measuring Performance

### Lighthouse

```bash
# CLI
npm install -g lighthouse
lighthouse https://example.com --view

# Chrome DevTools
# Performance tab > Lighthouse
```

### Web Vitals

```tsx
// app/layout.tsx
import { SpeedInsights } from '@vercel/speed-insights/next'
import { Analytics } from '@vercel/analytics/react'

export default function Layout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />
        <Analytics />
      </body>
    </html>
  )
}
```

### Custom Metrics

```tsx
'use client'
import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    console.log(metric)
    // Send to analytics
    analytics.track(metric.name, {
      value: metric.value,
      rating: metric.rating,
    })
  })
  return null
}
```

## Quick Wins

| Issue | Solution |
|-------|----------|
| Slow LCP | Add `priority` to hero image |
| High CLS | Add width/height to images, reserve space |
| Large bundle | Dynamic imports, tree shaking |
| Slow fonts | Use `next/font`, `display: swap` |
| Too much JS | Move to Server Components |
| No caching | Add `revalidate` to fetches |
| Slow third-party | Load with `lazyOnload` strategy |

## Performance Budget

```javascript
// Example budget
{
  "resourceSizes": [
    { "resourceType": "script", "budget": 300 },  // 300KB JS
    { "resourceType": "image", "budget": 500 },   // 500KB images
    { "resourceType": "font", "budget": 100 },    // 100KB fonts
    { "resourceType": "total", "budget": 1000 }   // 1MB total
  ],
  "timings": [
    { "metric": "largest-contentful-paint", "budget": 2500 },
    { "metric": "first-contentful-paint", "budget": 1500 },
    { "metric": "total-blocking-time", "budget": 300 }
  ]
}
```
