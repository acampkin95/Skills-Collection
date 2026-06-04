---
name: modern-web-design
description: Modern web design with OKLCH colours, Tailwind v4, WCAG 2.2, Core Web Vitals, View Transitions, semantic HTML, and design systems.
version: 2.0.0
reviewed: "2026-06-04"
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


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.