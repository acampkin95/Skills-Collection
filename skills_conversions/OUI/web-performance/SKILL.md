---
name: web-performance
description: "Web performance fundamentals, Core Web Vitals, optimization strategies, lazy loading, caching, rendering performance, and performance budgeting for non-CLI agents. Use when evaluating web performance, understanding Core Web Vitals, optimizing load times, analyzing rendering bottlenecks, or establishing performance budgets."
version: "1.0.0"
metadata:
  category: design-visual
  scope: non-cli
---

# Web Performance

Core Web Vitals, optimization strategies, and performance principles for understanding and improving web performance.

## Core Web Vitals

### The Three Metrics

| Metric | What It Measures | Good | Needs Work | Poor |
|--------|-----------------|------|------------|------|
| **LCP** (Largest Contentful Paint) | Loading performance — when main content appears | ≤2.5s | 2.5-4.0s | >4.0s |
| **INP** (Interaction to Next Paint) | Interactivity — responsiveness to user input | ≤200ms | 200-500ms | >500ms |
| **CLS** (Cumulative Layout Shift) | Visual stability — unexpected layout movement | ≤0.1 | 0.1-0.25 | >0.25 |

### LCP Optimization

```
WHAT TRIGGERS LCP:
├── <img> or <picture> elements
├── <video> poster images
├── Background images (CSS)
├── <svg> elements
└── Block-level text elements

OPTIMIZATION STRATEGIES:
├── Preload critical resources: <link rel="preload">
├── Optimize images: WebP/AVIF, correct sizes, lazy non-hero
├── Server response: TTFB < 800ms
├── CSS: No render-blocking stylesheets for above-fold
├── JavaScript: No render-blocking scripts for above-fold
├── Fonts: Preload critical, font-display: swap
└── CDN: Static assets served from edge

CRITICAL RENDERING PATH:
1. HTML download → 2. Parse HTML → 3. Download CSS → 4. Parse CSS
→ 5. DOM + CSSOM → 6. Render tree → 7. Layout → 8. Paint

BLOCKERS TO ELIMINATE:
├── Render-blocking CSS (use <link rel="preload"> or inline critical)
├── Synchronous JavaScript in <head>
├── Unoptimized images (wrong format, no responsive sizes)
├── Slow server responses (TTFB)
└── Third-party scripts blocking render
```

### INP Optimization

```
WHAT CAUSES SLOW INP:
├── Heavy JavaScript execution on main thread
├── Large DOM reflows/repaints
├── Synchronous layout reads then writes (layout thrashing)
├── Complex CSS selectors
├── Third-party scripts
└── Event handlers doing too much work

STRATEGIES:
├── Break long tasks (>50ms) into smaller chunks
├── Use requestAnimationFrame for visual updates
├── Debounce/throttle frequent events (scroll, resize)
├── Use CSS transforms/animations (GPU-accelerated)
├── Avoid synchronous style reads + writes interleaved
├── Web Workers for heavy computation
├── Schedule non-critical work with requestIdleCallback
└── Minimize main thread work during interaction
```

### CLS Optimization

```
WHAT CAUSES CLS:
├── Images/ads/embeds without dimensions
├── Dynamic content injected above existing content
├── Web fonts causing FOIT/FOUT
├── Late-loading CSS/JS changing layout
└── Animations that move elements

STRATEGIES:
├── Always set width/height on images and videos
├── Reserve space for dynamic content (aspect-ratio)
├── Use font-display: optional or swap
├── Preload web fonts
├── Transform animations (translate, scale) not position animations
├── Skeleton screens for loading states
├── Avoid inserting content above existing content
└── Use CSS contain: layout for isolated components
```

## Loading Performance

### Resource Hints

```
<link rel="preload">    → Download now, will need soon
<link rel="prefetch">   → Download in idle time, might need later
<link rel="preconnect"> → Establish connection early
<link rel="dns-prefetch"> → DNS lookup only
<link rel="modulepreload"> → Preload ES modules

PRIORITY ORDER:
1. Preload critical resources (hero image, main CSS, key fonts)
2. Preconnect to third-party origins
3. Prefetch likely next-page resources (low priority)
```

### Image Optimization

```
FORMAT SELECTION:
├── Photos: WebP (fallback JPEG) or AVIF (fallback WebP)
├── Icons/logos: SVG (vector) or WebP
├── Transparent: WebP (fallback PNG)
├── Animations: Video (MP4/WebM) or animated WebP
└── Never: GIF (too large, use video)

RESPONSIVE IMAGES:
<picture>
  <source srcset="img.avif" type="image/avif">
  <source srcset="img.webp" type="image/webp">
  <img src="img.jpg" 
       srcset="img-400.jpg 400w, img-800.jpg 800w, img-1200.jpg 1200w"
       sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
       width="800" height="600"
       alt="Description"
       loading="lazy"
       decoding="async">
</picture>

RULES:
├── Always specify width + height (prevents CLS)
├── Hero images: loading="eager", fetchpriority="high"
├── Below-fold: loading="lazy"
├── Use modern formats with <picture> fallbacks
└── Serve responsive sizes (srcset + sizes)
```

### JavaScript Performance

```
CODE SPLITTING:
├── Route-based: Load code per page/route
├── Component-based: Lazy load heavy components
├── Feature-based: Load features on interaction
└── Vendor splitting: Separate framework from app code

TREE SHAKING:
├── Use ES modules (import/export)
├── Avoid side-effect imports
├── Use named imports (not wildcard)
└── Check bundle with analyzer tools

EXECUTION OPTIMIZATION:
├── Defer non-critical: <script defer>
├── Async independent: <script async>
├── Code split heavy features
├── Web Workers for computation
└── requestIdleCallback for non-urgent work
```

### Caching Strategy

```
CACHE HIERARCHY:
├── Browser cache (fastest, local)
├── Service Worker cache (offline, programmable)
├── CDN cache (edge servers)
├── Server cache (Redis, memcached)
└── Database cache (query cache)

CACHE HEADERS:
├── Cache-Control: max-age=31536000 (immutable assets)
├── Cache-Control: no-cache (validate before use)
├── Cache-Control: no-store (never cache)
├── ETag: "hash" (validation token)
├── Last-Modified: date (conditional request)
└── Vary: Accept-Encoding (don't mix compressed/uncompressed)

STRATEGY BY RESOURCE:
├── HTML: no-cache (always validate, fast updates)
├── CSS/JS with hash: max-age=1year, immutable
├── Images: max-age=1year (long-lived)
├── Fonts: max-age=1year, immutable
├── API responses: no-cache or short max-age
└── User data: no-store (private)
```

## Performance Budget

```
BUDGET TEMPLATE:
────────────────
Transfer size:
├── HTML:     < 50KB
├── CSS:      < 50KB
├── JS:       < 200KB (compressed)
├── Images:   < 500KB (above fold)
├── Fonts:    < 100KB
└── Total:    < 1MB initial load

Timing:
├── TTFB:     < 800ms
├── FCP:      < 1.8s
├── LCP:      < 2.5s
├── TTI:      < 3.8s
└── TBT:      < 200ms

Third-party:
├── Max 3 third-party scripts
├── Total 3P budget: < 100KB
└── Load async/fallback if possible
```

## Performance Debugging Decision Trees

### LCP Debugging Flow

```
LCP > 2.5s?
  ├── YES → Check TTFB
  │   ├── TTFB > 800ms?
  │   │   ├── YES → Server response optimization
  │   │   │   ├── Database query optimization
  │   │   │   ├── Server-side caching (Redis, CDN)
  │   │   │   ├── Edge rendering / CDN origin shield
  │   │   │   └── Reduce redirect chains
  │   │   └── NO → Check resource load timing
  │   │       ├── Load delay > 500ms?
  │   │       │   ├── YES → Add <link rel="preload"> for LCP resource
  │   │       │   ├── Check for render-blocking resources
  │   │       │   └── Inline critical CSS for above-fold
  │   │       └── Load time > 1s?
  │   │           ├── YES → Optimize the resource
  │   │           │   ├── Image: Compress, WebP/AVIF, responsive sizes
  │   │           │   ├── Font: Subset, preload, font-display: swap
  │   │           │   └── Video: Compress, poster image, lazy load
  │   │           └── NO → Check render timing
  │   │               ├── Client rendering blocking?
  │   │               │   ├── Heavy JS on main thread → Code split
  │   │               │   └── Hydration blocking → Streaming SSR
  │   │               └── Layout shifts delaying paint?
  │   │                   └── Set explicit dimensions, reduce CLS
  └── NO → Performance acceptable
```

### INP Debugging Flow

```
INP > 200ms?
  ├── YES → Identify the interaction
  │   ├── Long task on main thread?
  │   │   ├── YES → Profile the handler
  │   │   │   ├── >50ms task? → Break into smaller chunks
  │   │   │   ├── Heavy DOM manipulation? → Batch reads/writes
  │   │   │   ├── Expensive selector? → Simplify CSS selectors
  │   │   │   └── Third-party script? → Move to Web Worker
  │   │   └── NO → Check rendering pipeline
  │   │       ├── Large repaint? → Use CSS transforms (GPU)
  │   │       ├── Layout thrashing? → Batch DOM reads before writes
  │   │       └── Complex compositing? → Reduce layers, will-change
  │   └── Check event handler count
  │       ├── Too many listeners? → Event delegation
  │       ├── Unthrottled scroll/resize? → Debounce/throttle
  │       └── Passive listeners missing? → Add { passive: true }
  └── NO → Performance acceptable
```

## Third-Party Impact Audit

```
IMPACT ASSESSMENT PER THIRD-PARTY SCRIPT:
──────────────────────────────────────────
1. MEASURE: Compare page with and without the script
   ├── Block the script in browser DevTools
   ├── Run Lighthouse both ways
   └── Calculate delta for each metric

2. EVALUATE:
   ┌─────────────────────────────────────────────┐
   │ Script  │ LCP Δ │ INP Δ │ CLS Δ │ Size │ Keep? │
   │ Analytics│ +50ms │  0ms  │  0ms  │ 45KB│  YES  │
   │ Chat     │ +200ms│ +50ms │  0ms  │180KB│  MAYBE│
   │ Ads      │ +500ms│ +80ms │+.05  │350KB│  REVIEW│
   └─────────────────────────────────────────────┘

3. MITIGATE:
   ├── Load async/defer (never render-blocking)
   ├── Facade pattern: Show placeholder, load on interaction
   ├── Partytown: Move to Web Worker (off main thread)
   ├── Self-host if possible (reduce DNS/connect time)
   ├── Schedule with requestIdleCallback if non-critical
   └── Remove if impact > value
```


## When to Use

- Analyzing Core Web Vitals (LCP, INP, CLS) and their causes
- Optimizing page load speed and perceived performance
- Setting and enforcing performance budgets
- Diagnosing rendering bottlenecks and layout thrashing
- Advising on image optimization, code splitting, and caching strategies

## Limitations

- Performance data requires real user metrics (RUM) for accuracy
- Lab data (Lighthouse) does not fully represent field conditions
- Network conditions vary dramatically by geography and device
- Third-party scripts can negate first-party optimizations

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [web-fetching](../web-fetching/SKILL.md) | HTTP/2, caching headers, and fetch patterns affect performance |
| [modern-web-standards](../modern-web-standards/SKILL.md) | New web APIs can improve performance |
| [visual-design](../visual-design/SKILL.md) | Image optimization and font loading affect visual rendering |
| [responsive-design](../responsive-design/SKILL.md) | Serving appropriately sized resources per device |
