---
name: responsive-design
description: "Responsive web design, mobile-first methodology, breakpoint strategies, container queries, adaptive layouts, flexible grids, and cross-device design patterns for non-CLI agents. Use when designing responsive layouts, choosing breakpoints, adapting content for different devices, or understanding mobile-first design."
version: "1.0.0"
metadata:
  category: design-visual
  scope: non-cli
---

# Responsive Design

Mobile-first design methodology, breakpoint strategies, container queries, and adaptive layout patterns for building interfaces that work across all devices.

## Mobile-First Methodology

### Core Principle

```
DESIGN PROGRESSION:
Mobile (base) → Tablet (enhance) → Desktop (enhance) → Large (enhance)

WHY MOBILE-FIRST:
├── Forces prioritization (limited space = focus on essentials)
├── Progressive enhancement (add, don't remove)
├── Better performance (base is lightweight)
├── Matches CSS cascading (base styles, then min-width queries)
└── 60%+ traffic is mobile (design for the majority)

CSS PATTERN:
/* Base: Mobile (default, no query needed) */
.card {
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

/* Tablet and up */
@media (min-width: 768px) {
  .card {
    flex-direction: row;
    padding: 1.5rem;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .card {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

## Breakpoint Strategy

### Standard Breakpoints

```
BREAKPOINT       WIDTH        TYPICAL DEVICE
─────────────────────────────────────────────
xs (base)        < 640px      Phones (portrait)
sm               ≥ 640px      Phones (landscape), small tablets
md               ≥ 768px      Tablets (portrait)
lg               ≥ 1024px     Tablets (landscape), small laptops
xl               ≥ 1280px     Desktops
2xl              ≥ 1536px     Large screens

RULES:
├── Use content-based breakpoints, not device-based
├── Start with standard breakpoints, add custom as needed
├── Test at breakpoint boundaries (±10px)
├── Don't create too many breakpoints (max 4-5)
└── Check: does the layout break between breakpoints?
```

### When to Add Custom Breakpoints

```
DON'T add breakpoints for specific devices (iPhone 15, iPad Pro)
DO add breakpoints when content looks bad:

SIGNS YOU NEED A BREAKPOINT:
├── Text lines too long (>90 chars) or too short (<35 chars)
├── Content touching edges (need more margin)
├── Grid items too cramped or too spaced
├── Navigation wrapping awkwardly
├── Images stretching or shrinking too much
└── Side-by-side layout becoming too cramped

APPROACH:
1. Start at mobile width (320px)
2. Slowly widen the browser
3. When something looks wrong → add a breakpoint
4. Continue widening
5. Repeat until max width
```

## Layout Patterns

### Responsive Grid

```
CSS GRID (auto-fit):
.card-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* Results:
   < 300px:  1 column (single card)
   300-599px: 1 column
   600-899px: 2 columns
   900-1199px: 3 columns
   1200px+:   4 columns
*/

FLEXBOX (wrapping):
.card-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.card {
  flex: 1 1 300px; /* Grow, shrink, min 300px */
  max-width: calc(50% - 0.75rem); /* Max 2 per row */
}

@media (min-width: 1024px) {
  .card {
    max-width: calc(33.333% - 1rem); /* Max 3 per row */
  }
}
```

### Responsive Navigation

```
MOBILE (≤ 768px):
┌───────────────────────────┐
│ ☰  Logo              🔍  │  ← Hamburger menu
├───────────────────────────┤
│                           │
│  Content                  │
│                           │
└───────────────────────────┘
Menu opens as overlay/sidebar

TABLET (768-1024px):
┌──────────────────────────────────────┐
│ Logo  Nav1  Nav2  Nav3      🔍  👤  │  ← Horizontal nav
├──────────────────────────────────────┤
│                                      │
│  Content                             │
│                                      │
└──────────────────────────────────────┘

DESKTOP (1024px+):
┌───────────────────────────────────────────────────┐
│ Logo    Nav1  Nav2  Nav3  Nav4          🔍  👤 🛒 │
├──────────┬────────────────────────────────────────┤
│          │                                         │
│  Sidebar │  Content (max-width: 65ch)              │
│          │                                         │
└──────────┴────────────────────────────────────────┘
```

### Responsive Typography

```
FLUID TYPE (clamp):
h1 { font-size: clamp(1.75rem, 1rem + 3vw, 3.5rem); }
h2 { font-size: clamp(1.5rem, 0.8rem + 2vw, 2.5rem); }
p  { font-size: clamp(0.875rem, 0.5rem + 0.5vw, 1rem); }

FLUID SPACING:
section { padding: clamp(1.5rem, 1rem + 2vw, 4rem) clamp(1rem, 0.5rem + 2vw, 3rem); }

FLUID GRID:
gap: clamp(1rem, 0.5rem + 1vw, 2rem);
```

## Container Queries

### Component-Level Responsiveness

```
CONTAINER QUERY PATTERN:
─────────────────────────
/* Define the container */
.card-wrapper {
  container: card / inline-size;
}

/* Base: Single column (narrow) */
.card {
  display: grid;
  grid-template-rows: auto 1fr;
}

/* Wide card: Side-by-side */
@container card (min-width: 400px) {
  .card {
    grid-template-columns: 200px 1fr;
    grid-template-rows: auto;
  }
}

/* Extra wide: More detail */
@container card (min-width: 600px) {
  .card .description {
    display: block; /* Show extended description */
  }
}

WHY CONTAINER QUERIES > MEDIA QUERIES:
├── Respond to parent size, not viewport
├── Component works in any layout context
├── Sidebar + main content can have different breakpoints
├── True component encapsulation
└── Reusable across different page layouts
```

## Responsive Images & Media

```
RESPONSIVE IMAGE PATTERNS:
──────────────────────────
<!-- Art direction (different images per size) -->
<picture>
  <source media="(min-width: 1024px)" srcset="wide.jpg">
  <source media="(min-width: 768px)" srcset="medium.jpg">
  <img src="narrow.jpg" alt="Description" width="800" height="600">
</picture>

<!-- Resolution switching (same image, different sizes) -->
<img srcset="small.jpg 400w, medium.jpg 800w, large.jpg 1200w"
     sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 33vw"
     src="medium.jpg" alt="Description"
     width="800" height="600" loading="lazy">

<!-- Responsive video -->
.video-container {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
}
.video-container iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
```

## Touch & Mobile UX

```
TOUCH TARGETS:
├── Minimum: 44x44px (WCAG), 48x48dp (Material Design)
├── Spacing between targets: ≥ 8px
├── No tiny links in text (use buttons for key actions)
└── Swipe targets: ≥ 20px height

MOBILE PATTERNS:
├── Bottom sheet for filters/options (thumb-reachable)
├── Sticky CTA at bottom of viewport
├── Swipe gestures: horizontal for tabs, vertical for scroll
├── Pull to refresh for content updates
├── Back button: Hardware + in-page
└── Forms: Single column, large inputs

THUMB ZONE:
┌─────────────────────┐
│      HARD TO REACH  │  ← Top of screen
│                     │
│   EASY TO REACH     │  ← Middle-bottom
│      (thumb zone)   │
│                     │
└─────────────────────┘

PUT:
├── Primary actions: Bottom thumb zone
├── Navigation: Top (expected, not frequently tapped)
├── Content: Middle (scrollable)
└── Destructive actions: Top (harder to reach accidentally)
```


## When to Use

- Designing layouts that adapt from mobile to desktop viewports
- Implementing container queries for component-level responsiveness
- Optimizing images and media for different screen sizes
- Designing touch-friendly interfaces for mobile users
- Choosing breakpoint strategies for a design system

## Limitations

- Device landscape is constantly evolving — new form factors emerge regularly
- Container query support is modern (2023+) — fallbacks needed for older browsers
- Responsive images require significant image pipeline infrastructure
- Touch and pointer interaction patterns differ across platforms

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [visual-design](../visual-design/SKILL.md) | Responsive layouts implement visual design systems |
| [modern-web-standards](../modern-web-standards/SKILL.md) | Container queries and modern CSS enable responsive design |
| [accessibility-knowledge](../accessibility-knowledge/SKILL.md) | Responsive design impacts zoom, reflow, and touch targets |
| [interaction-patterns](../interaction-patterns/SKILL.md) | Touch and mobile interaction patterns are responsive concerns |
