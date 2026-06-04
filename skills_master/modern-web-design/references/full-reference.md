---
name: modern-web-design
description: "Use this skill when working with web design, UI components, WCAG, accessibility, ShadCN, responsive design, design systems, Tailwind design, color theory, typography systems. 2025+ web design with OKLCH colors, Tailwind v4, WCAG 2.2, Core Web Vitals, View Transitions, and semantic HTML."
---

# Modern Web Design 2025

Production web design with WCAG 2.2 accessibility, Tailwind v4 CSS-first configuration, Core Web Vitals optimization, and OKLCH color system.

## Key Principles

### Accessibility First (WCAG 2.2)
- **Target Size**: Min 24×24px (44×44px mobile) for interactive elements
- **Focus**: Visible indicators, not obscured, 3px outline minimum
- **Contrast**: 4.5:1 normal text, 3:1 large text (AA level)
- **Semantic**: Use `<button>`, `<nav>`, `<header>`, not divs
- **ARIA**: Only when semantic HTML insufficient
- **Motion**: Respect `prefers-reduced-motion`

### Performance (Core Web Vitals)
| Metric | Good | Needs Work | Poor |
|--------|------|-----------|------|
| LCP | ≤2.5s | 2.5-4.0s | >4.0s |
| INP | ≤200ms | 200-500ms | >500ms |
| CLS | ≤0.1 | 0.1-0.25 | >0.25 |

### Color System (OKLCH)
- Uses perceptual color space (better than HSL/RGB)
- Format: `oklch(lightness chroma hue)`
- Example: Primary blue = `oklch(0.55 0.22 264)`
- Maintains color accuracy across light/dark modes

## Tailwind v4 Quick Setup

**v4 is CSS-first** (not JS config). Create `input.css`:

```css
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.55 0.22 264);
  --color-text: oklch(0.20 0 0);
  --font-display: "Cal Sans", system-ui;
  --breakpoint-3xl: 1920px;
}

@custom-variant dark (&:where([data-theme="dark"]));
```

**v3 → v4 breaking changes:**

| Change | v3 | v4 |
|--------|----|----|
| Shadow default | `shadow-sm` | `shadow-xs` |
| Ring default | `ring` (0px) | `ring-3` (3px) |
| Opacity syntax | `bg-opacity-50` | `bg-black/50` |
| Important | `!flex` | `flex!` |

See `references/tailwind-migration.md` for full changelog.

## CSS Features 2025+

**Container Queries** (90%+ support): Size components based on container, not viewport.

```css
.card-container { container: card / inline-size; }
@container card (min-width: 400px) {
  .card { display: flex; gap: 1.5rem; }
}
```

**:has() Selector**: Style based on child/sibling state.

```css
form:has(input:invalid) .submit-btn { opacity: 0.5; }
```

**Scroll-Driven Animations**: Progress bars, reveal-on-scroll effects.

```css
.progress { animation-timeline: scroll(); }
.reveal { animation-timeline: view(); }
```

**light-dark() Function**: Automatic light/dark mode colors.

```css
body { background: light-dark(white, #1a1a1a); }
```

**CSS Nesting**: Nested selectors without SCSS.

```css
.card {
  padding: 1rem;
  &:hover { opacity: 0.9; }
  & .title { font-size: 1.25rem; }
}
```

See `references/css-2026-features.md` for anchor positioning, view transitions, @starting-style.

## Color & Typography Patterns

**OKLCH Color System:**
```css
:root {
  --primary: oklch(0.55 0.22 264);
  --primary-light: oklch(0.75 0.15 264);
  --primary-dark: oklch(0.35 0.18 264);
  --text: oklch(0.20 0 0);
  --surface: oklch(0.98 0.002 250);
}
.dark {
  --text: oklch(0.98 0 0);
  --surface: oklch(0.15 0.02 250);
}
```

**Fluid Typography (scales with viewport):**
```css
:root {
  --text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-lg: clamp(1.125rem, 1rem + 0.6vw, 1.25rem);
  --text-2xl: clamp(1.5rem, 1.2rem + 1.5vw, 2rem);
}
```

**Visual Hierarchy:**
- Size: Use 1.25-1.5× scale ratios
- Weight: Bold for emphasis, light for secondary
- Color: High contrast (4.5:1 AA) for primary actions
- Space: Whitespace around important elements
- Position: Top-left reads first (F-pattern)

## Component Building Pattern

**Step 1: Semantic Structure**
```html
<article>
  <header><h2>Title</h2></header>
  <p>Content...</p>
  <nav aria-label="Actions">
    <button type="button">Share</button>
  </nav>
</article>
```

**Step 2: Apply Styling (Tailwind v4)**
```tsx
<button className={cn(
  "inline-flex items-center justify-center",  // layout
  "gap-2 px-4 py-2",                          // spacing
  "h-10 min-w-[120px]",                       // sizing (24×24px min)
  "rounded-lg bg-primary text-primary-fg",    // visual
  "hover:bg-primary/90 focus-visible:ring-2", // states
  "transition-colors duration-150"             // animation
)} />
```

**Step 3: React 19 Patterns**
- `ref` as prop: `<Input ref={ref} />`
- `useActionState`: Server actions + loading state
- `useOptimistic`: Instant feedback before server

## ShadCN/UI Setup

```bash
npx shadcn@latest init
npx shadcn@latest add button card dialog input
```

**globals.css with OKLCH:**
```css
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.55 0.22 264);
}
.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
}
```

See `references/shadcn.md` for component patterns and theming.

## WCAG 2.2 Checklist

| Criterion | Level | Implementation |
|-----------|-------|-----------------|
| 2.5.8 Target Size | AA | Min 24×24px (44×44px mobile) |
| 2.4.11 Focus Not Obscured | AA | 3px outline, outline-offset 4px |
| 3.3.8 Accessible Auth | AA | No CAPTCHA-only, offer alternatives |
| 2.5.7 Dragging | AA | Pointer alternatives for drag/drop |

**Target Size:**
```css
button { min-width: 24px; min-height: 24px; padding: 8px; }
@media (max-width: 768px) { button { min-height: 44px; } }
```

**Focus Visibility:**
```css
:focus-visible {
  outline: 3px solid var(--focus-ring);
  outline-offset: 4px;
}
html { scroll-padding-top: 100px; }
```

See `references/accessibility.md` for full WCAG 2.2 guide.

## Core Web Vitals Optimization

**LCP (Largest Contentful Paint):** Image/text rendering
- Optimize largest image, use `priority` attribute
- Lazy-load below-fold content
- Eliminate render-blocking CSS/JS

**INP (Interaction to Next Paint):** Response time to user input
- Break long tasks: `await scheduler.yield()`
- Update UI immediately, defer processing
- Minimize JavaScript execution

**CLS (Cumulative Layout Shift):** Visual stability
- Set explicit image dimensions
- Reserve space for ads/embeds
- Avoid inserting content above viewport

**Preload/Prefetch:**
```html
<link rel="preload" as="image" href="/hero.jpg">
<link rel="prefetch" href="/next-page.html">
<script type="speculationrules">
  { "prerender": [{ "where": { "href_matches": "/products/*" }}] }
</script>
```

See `references/seo.md` for detailed optimization.

## View Transitions & Motion

**MPA View Transitions:**
```css
@view-transition { navigation: auto; }
::view-transition-old(root) { animation: 0.4s slide-out; }
::view-transition-new(root) { animation: 0.4s slide-in; }
.hero { view-transition-name: hero; }
```

**SPA Transitions (React):**
```tsx
const { startTransition } = useViewTransition();
startTransition(() => router.push('/page'));
```

See `references/motion-design.md` for animation patterns.

## SEO 2025

**AI Overview Optimization (85%+ of searches):**
- 50-70 word TL;DR summaries at top
- Clear H2/H3 hierarchy
- Bullet points, tables, lists
- Author credentials (E-E-A-T)
- Original content: photos, case studies

**Essential Meta Tags:**
```tsx
export const metadata: Metadata = {
  title: 'Site | Brand',
  description: 'Under 160 chars compelling description',
  openGraph: { type: 'website', images: [...] }
}
```

See `references/seo.md` for structured data.

## Pre-Deploy Checklist

1. ✅ Alt text on all images
2. ✅ Color contrast 4.5:1 (AA standard)
3. ✅ Keyboard navigation works
4. ✅ Focus indicators visible (3px outline)
5. ✅ Touch targets 24×24px (44×44px mobile)
6. ✅ Animations respect `prefers-reduced-motion`
7. ✅ OG images & meta tags set
8. ✅ Structured data validates
9. ✅ Core Web Vitals: LCP ≤2.5s, INP ≤200ms, CLS ≤0.1
10. ✅ No layout shift on fonts/images

## Documentation Router

| Need | File | Purpose |
|------|------|---------|
| All WCAG rules | `accessibility.md` | 2.2 checklist + testing |
| ShadCN components | `shadcn.md` | Installation + patterns |
| SEO & structured data | `seo.md` | AI overview optimization |
| Animations | `motion-design.md` | View Transitions, keyframes |
| Design system | `design-systems.md` | DTCG tokens, branding |
| Tailwind v4 | `tailwind-migration.md` | v3→v4 breaking changes |
| CSS 2026 features | `css-2026-features.md` | Anchor positioning, @starting-style |
| 2025 trends | `2026-trends.md` | Motion, 3D, typography trends |
