---
name: modern-web-standards
description: "Modern web platform standards including HTML5 semantic markup, CSS4 features, Web APIs, progressive enhancement, browser capabilities, and platform interoperability for non-CLI agents. Use when understanding web platform capabilities, modern CSS features, semantic HTML, Web APIs, or browser standards."
version: "1.0.0"
metadata:
  category: design-visual
  scope: non-cli
---

# Modern Web Standards

Current web platform capabilities, semantic HTML, modern CSS, browser APIs, and progressive enhancement principles for understanding what the web platform can do.

## Semantic HTML5

### Document Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Page description for SEO">
  <meta property="og:title" content="Share Title">
  <meta property="og:description" content="Share description">
  <meta property="og:image" content="https://example.com/image.jpg">
  <link rel="canonical" href="https://example.com/page">
  <title>Page Title | Site Name</title>
</head>
<body>
  <header>
    <nav aria-label="Main">
      <a href="/">Logo/Home</a>
      <ul>
        <li><a href="/about">About</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
    </nav>
  </header>
  
  <main>
    <article>
      <h1>Page Heading</h1>
      <p>Content...</p>
      <section>
        <h2>Section Heading</h2>
        <p>Section content...</p>
      </section>
    </article>
    
    <aside aria-label="Related content">
      <h2>Related</h2>
      <p>Sidebar content...</p>
    </aside>
  </main>
  
  <footer>
    <p>&copy; 2025 Site Name</p>
  </footer>
</body>
</html>
```

### Semantic Element Reference

| Element | Purpose | Landmark Role |
|---------|---------|---------------|
| `<header>` | Introductory content, navigation | `banner` (top-level) |
| `<nav>` | Navigation links | `navigation` |
| `<main>` | Primary content (1 per page) | `main` |
| `<article>` | Self-contained composition | `article` |
| `<section>` | Thematic grouping with heading | `region` (if labeled) |
| `<aside>` | Tangentially related content | `complementary` |
| `<footer>` | Footer content | `contentinfo` (top-level) |
| `<figure>` | Illustration with caption | — |
| `<details>` | Disclosure widget | `group` |
| `<dialog>` | Modal/non-modal dialog | `dialog` |
| `<time>` | Date/time value | — |
| `<mark>` | Highlighted text | — |
| `<address>` | Contact information | — |

### Microdata & Structured Data

```
JSON-LD (recommended for SEO):
──────────────────────────────
Common schema types:
├── WebPage, Article, NewsArticle, BlogPosting
├── Product, Offer, AggregateRating
├── Person, Organization
├── BreadcrumbList
├── FAQ, HowTo
├── Event
├── LocalBusiness
└── SearchAction

BREADCRUMB:
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "/" },
    { "@type": "ListItem", "position": 2, "name": "Category", "item": "/cat" },
    { "@type": "ListItem", "position": 3, "name": "Current Page" }
  ]
}
```

## Modern CSS (2025+)

### CSS Layers

```css
@layer reset, base, components, utilities;

@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
}

@layer base {
  body { font-family: system-ui; line-height: 1.5; }
  h1, h2, h3 { line-height: 1.2; }
}

@layer components {
  .card { border-radius: 8px; padding: 1rem; }
  .btn { padding: 0.5rem 1rem; cursor: pointer; }
}

@layer utilities {
  .sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }
}
```

### CSS Nesting

```css
.card {
  padding: 1rem;
  border-radius: 8px;
  
  & .title {
    font-size: 1.25rem;
    font-weight: 600;
  }
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
  
  @media (width >= 768px) {
    padding: 2rem;
  }
}
```

### Container Queries

```css
.card-container {
  container: card / inline-size;
}

@container card (min-width: 400px) {
  .card {
    display: flex;
    gap: 1rem;
  }
}

@container card (min-width: 600px) {
  .card {
    flex-direction: row;
    align-items: center;
  }
}
```

### :has() Selector

```css
form:has(input:invalid) .submit-btn {
  opacity: 0.5;
  pointer-events: none;
}

.card:has(img) {
  grid-template-rows: auto 1fr;
}

.sidebar:not(:has(*)) {
  display: none;
}

.details:has(details[open]) {
  background: var(--surface-active);
}
```

### View Transitions

```css
@view-transition {
  navigation: auto;
}

::view-transition-old(root) {
  animation: fade-out 0.3s ease;
}

::view-transition-new(root) {
  animation: fade-in 0.3s ease;
}

.page-transition {
  view-transition-name: page-content;
}
```

### Scroll-Driven Animations

```css
.progress-bar {
  animation: grow linear;
  animation-timeline: scroll();
}

@keyframes grow {
  from { width: 0%; }
  to { width: 100%; }
}

.reveal {
  animation: fade-in linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

### CSS Custom Properties (Themable)

```css
@theme {
  --color-primary: oklch(0.55 0.22 264);
  --color-surface: oklch(1.00 0 0);
  --font-display: "Inter", system-ui;
  --font-body: system-ui;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-surface: oklch(0.15 0 0);
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  }
}
```

## Key Web APIs

### Intersection Observer

```
PURPOSE: Detect when elements enter/leave viewport
USE FOR: Lazy loading, infinite scroll, reveal animations, analytics

KEY PROPERTIES:
├── isIntersecting: Is element visible?
├── intersectionRatio: How much is visible (0-1)
├── rootMargin: Expand/shrink viewport boundary
└── threshold: Array of visibility percentages to trigger
```

### Resize Observer

```
PURPOSE: Detect element size changes
USE FOR: Container queries, responsive components, layout recalculation

KEY PROPERTIES:
├── contentRect: Element's content box dimensions
├── borderBoxSize: Including padding/border
└── contentBoxSize: Content only
```

### Web Workers

```
PURPOSE: Run JavaScript in background threads
USE FOR: Heavy computation, data processing, no UI blocking

COMMUNICATION: postMessage() / onmessage
LIMITATION: No DOM access (send data, not elements)
```

### MutationObserver

```
PURPOSE: Watch for DOM changes
USE FOR: Dynamic content, third-party script monitoring, accessibility

OBSERVES:
├── childList: Added/removed children
├── attributes: Attribute changes
├── characterData: Text content changes
└── subtree: Entire subtree or just target
```

### Clipboard API

```
PURPOSE: Read/write system clipboard
USE FOR: Copy buttons, paste handling

PERMISSIONS: Requires user gesture
SECURITY: Only HTTPS or localhost
```

### Storage APIs

```
localStorage:     5-10MB, permanent, synchronous
sessionStorage:   5-10MB, tab lifetime, synchronous
IndexedDB:        Large storage, async, structured data
Cache API:        HTTP response caching, async, Service Worker

PATTERNS:
├── User preferences → localStorage
├── Session data → sessionStorage
├── Offline data → IndexedDB
├── HTTP caching → Cache API
└── Sensitive data → None (server only)
```

## Progressive Enhancement

### Strategy

```
BASE LAYER:      Semantic HTML (works everywhere)
       ↓
ENHANCEMENT:     CSS (visual styling)
       ↓
ENHANCEMENT:     JavaScript (interactivity)
       ↓
ENHANCEMENT:     Modern APIs (performance bonus)

PRINCIPLES:
├── Content must be accessible without JS
├── Core functionality works without CSS
├── JS enhances, doesn't create
├── Feature detect, don't browser detect
└── Each layer independent and functional
```

### Feature Detection

```
CHECK BEFORE USING:
├── CSS: @supports (property: value) { ... }
├── JS:  if ('IntersectionObserver' in window) { ... }
├── HTML: Elements degrade gracefully
└── API: Try/catch with fallback behavior

COMMON FALLBACKS:
├── No IntersectionObserver → Load all images immediately
├── No Web Animations → CSS transitions as fallback
├── No Service Worker → Standard caching only
└── No Clipboard API → execCommand fallback (deprecated but functional)
```


## When to Use

- Writing HTML that leverages semantic elements and modern attributes
- Using 2025+ CSS features (container queries, :has(), layers, nesting)
- Evaluating browser support for web platform features
- Implementing progressive enhancement strategies
- Advising on web platform capabilities (Intersection Observer, View Transitions, etc.)

## Limitations

- Browser support varies — always check caniuse.com or MDN for current status
- Cutting-edge features may have unstable specifications
- Polyfills add bundle size and may not cover all edge cases
- Some features require HTTPS or specific security contexts

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [responsive-design](../responsive-design/SKILL.md) | Container queries and modern layout are responsive-design tools |
| [accessibility-knowledge](../accessibility-knowledge/SKILL.md) | Semantic HTML is the shared foundation |
| [visual-design](../visual-design/SKILL.md) | Modern CSS enables advanced visual design techniques |
| [web-performance](../web-performance/SKILL.md) | New APIs can improve or hurt performance depending on usage |
