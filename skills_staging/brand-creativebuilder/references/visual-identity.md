# Visual Identity Reference

## Table of Contents
1. [Pantone Colour System](#pantone-colour-system)
2. [Digital Scale Construction](#digital-scale)
3. [SVG Logo System](#svg-logo)
4. [Favicon Package](#favicon)
5. [Typography System](#typography)
6. [Icon Library](#icons)
7. [Animation System](#animation)
8. [Accessibility](#accessibility)
9. [UK/EU 2026 Design Defaults](#uk-eu-defaults)

---

## Pantone Colour System

### Pantone-First Workflow

Every brand colour starts with a Pantone reference — this is the single source of truth. Digital values (HEX, RGB) and print values (CMYK) are derived approximations.

### Colour Specification Format

Each brand colour must include ALL of:

```
Name:     [Colour Name]
Pantone:  [PANTONE XX-XXXX TPX/TCX · Descriptive Name]
CMYK:     C% M% Y% K%
HEX:      #XXXXXX
RGB:      R, G, B
Usage:    [When and where to use this colour]
```

### Example Pantone Palettes by Mood

#### Sage / Natural / Craft
| Role | Pantone | CMYK | HEX | RGB |
|------|---------|------|-----|-----|
| Primary | PANTONE 16-6116 TPX · Shale Green | 45 12 38 8 | #7A9E81 | 122, 158, 129 |
| Primary Dark | PANTONE 18-6018 TPX · Foliage | 52 18 52 22 | #5E8365 | 94, 131, 101 |
| Primary Light | PANTONE 14-6312 TPX · Frosty Green | 30 4 24 0 | #9AB5A0 | 154, 181, 160 |

#### Deep Indigo / Technical
| Role | Pantone | CMYK | HEX | RGB |
|------|---------|------|-----|-----|
| Primary | PANTONE 19-3940 TPX · Blue Ribbon | 85 72 0 0 | #3B4CC0 | 59, 76, 192 |
| Accent | PANTONE 17-3938 TPX · Very Peri | 55 45 0 0 | #6667AB | 102, 103, 171 |

#### Warm Terracotta / Material
| Role | Pantone | CMYK | HEX | RGB |
|------|---------|------|-----|-----|
| Primary | PANTONE 17-1436 TPX · Raw Sienna | 10 52 65 8 | #C47F50 | 196, 127, 80 |
| Accent | PANTONE 18-1248 TPX · Rust | 12 62 72 18 | #B5573A | 181, 87, 58 |

#### Charcoal / Amber / Industrial
| Role | Pantone | CMYK | HEX | RGB |
|------|---------|------|-----|-----|
| Primary | PANTONE 19-0812 TPX · Turkish Coffee | 35 45 55 72 | #3B302A | 59, 48, 42 |
| Accent | PANTONE 15-1142 TPX · Honey Gold | 8 38 78 0 | #D4943A | 212, 148, 58 |

### Neutral Scale (Always Warm-Tinted)

Never use pure grey. Tint neutrals toward the primary hue:
- Sage primary → warm stone neutrals (PANTONE Warm Gray family)
- Blue primary → cool slate neutrals (PANTONE Cool Gray family)
- Amber primary → warm sand neutrals

### Semantic Colours (Fixed Across All Brands)

| State | Pantone | CMYK | HEX | RGB |
|-------|---------|------|-----|-----|
| Success | PANTONE 17-6153 TPX · Jelly Bean | 65 8 68 18 | #4A8B50 | 74, 139, 80 |
| Warning | PANTONE 14-1051 TPX · Marigold | 4 38 82 0 | #E5A02D | 229, 160, 45 |
| Error | PANTONE 18-1555 TPX · Molten Lava | 8 72 58 8 | #C45A4A | 196, 90, 74 |
| Info | PANTONE 16-4421 TPX · Blue Mist | 52 12 10 0 | #5A8FA0 | 90, 143, 160 |

---

## Digital Scale Construction

From each Pantone anchor, generate an 11-step digital scale:

```
50:  97% lightness — background tint
100: 91% lightness — subtle surface
200: 82% lightness — light border
300: 70% lightness — secondary accent text
400: 58% lightness — primary accent (links, interactive)
500: 48% lightness — primary brand (CTAs, active)
600: 38% lightness — hover state
700: 30% lightness — pressed state, dark logo variant
800: 23% lightness — dark surface
900: 17% lightness — dark text on light backgrounds
950: 10% lightness — near-black
```

### Surface Colours (Dark Theme)

```
background:         near-black with hue tint (e.g., #0E100F for sage)
bg-raised:          +1 lightness step from background
card:               primary at 4-6% opacity
glass:              primary at 4% + backdrop-blur(16px)
glass-border:       primary at 10-12% opacity
glass-border-hover: primary at 20-22% opacity
```

### Contrast Requirements

| Context | Minimum Ratio | Standard |
|---------|---------------|----------|
| Normal text (<18px) | 4.5:1 | WCAG 2.2 AA |
| Large text (≥18px / ≥14px bold) | 3:1 | WCAG 2.2 AA |
| UI components / graphics | 3:1 | WCAG 2.2 AA |
| Enhanced (optional) | 7:1 / 4.5:1 | WCAG 2.2 AAA |

---

## SVG Logo System

### Construction Rules

1. **Stroked outlines only** — 1.5–2px consistent stroke weight, never solid fills
2. **Geometric forms** — circles, rectangles, paths with rounded joins
3. **Represent the product's core concept** — abstractly, not literally
4. **Colour-independent** — works in single colour, must be legible in monochrome
5. **Scale-proof** — clean at 24px (favicon) and 512px (splash screen)

### Required SVG Variants

| Variant | Stroke Colour | Background |
|---------|--------------|------------|
| Primary (dark bg) | Brand accent (400 step) | Dark / transparent |
| Primary (light bg) | Brand dark (700-800 step) | Light / transparent |
| Logomark only | As above | Transparent |
| Wordmark only | As above | Transparent |
| Monochrome | White or Black | Transparent |

### SVG Technical Spec

```xml
<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- All elements use stroke, not fill -->
  <!-- stroke-width="2" for primary elements -->
  <!-- stroke-width="1.5" for detail elements -->
  <!-- stroke-linecap="round" for terminals -->
  <!-- stroke-linejoin="round" for corners -->
  <!-- stroke-dasharray for flow/liquid indicators -->
  <!-- Subtle fill at 8% opacity for containment areas only -->
</svg>
```

### Wordmark Specifications

- Display font at weight 800
- All UPPERCASE
- Letter-spacing: 0.06em to 0.10em
- Dark bg: brand accent colour (400 step)
- Light bg: brand dark colour (700-800 step)

### Clear Space

Minimum clear space = height of the logomark on all sides. Minimum digital size: 24px height for mark, 80px width for full lockup.

---

## Favicon Package

### Required Files

| File | Size | Format | Purpose |
|------|------|--------|---------|
| favicon.ico | 16, 32, 48px | ICO | Legacy browser fallback |
| favicon.svg | Scalable | SVG | Modern browsers (primary) |
| favicon-16.png | 16×16 | PNG | Size-specific fallback |
| favicon-32.png | 32×32 | PNG | Size-specific fallback |
| apple-touch-icon.png | 180×180 | PNG | iOS home screen |
| icon-192.png | 192×192 | PNG | Android / PWA |
| icon-512.png | 512×512 | PNG | PWA splash screen |
| site.webmanifest | — | JSON | PWA manifest |
| browserconfig.xml | — | XML | Windows tiles |

### HTML Implementation

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="[PRIMARY_HEX]">
```

### Generation (Python PIL)

```python
from PIL import Image
import cairosvg

# SVG to PNG at multiple sizes
for size in [16, 32, 48, 180, 192, 512]:
    cairosvg.svg2png(
        url="logomark.svg",
        write_to=f"favicon-{size}.png",
        output_width=size,
        output_height=size,
    )
```

---

## Typography System

### Three-Family Structure

| Role | Usage | Weight | Tracking |
|------|-------|--------|----------|
| Display | h1-h3, hero, stats | 600-800 | -0.02em to -0.03em |
| Body | Paragraphs, UI text | 400-500 | Normal |
| Mono | Numbers, code, data, labels | 400-600 | Normal to +0.02em |

### Recommended Display Fonts (2026)

**AVOID**: Inter, Roboto, Arial, system fonts, Plus Jakarta Sans (overused in AI products)

| Font | Character | Best For |
|------|-----------|----------|
| Outfit | Geometric, precision | Technical tools, SaaS |
| Space Grotesk | Clean geometric, tech | Developer tools |
| Manrope | Modern, friendly | Consumer products |
| General Sans | Neutral professional | B2B, enterprise |
| Satoshi | Sharp, contemporary | Design tools |
| Cabinet Grotesk | Condensed grotesque | Bold headlines |
| Syne | Distinctive, experimental | Creative brands |

### Critical Type Rules

1. **Numbers ALWAYS use mono font** — `font-mono tabular-nums`
2. **Stage/status names** — uppercase mono, xs (0.75rem), 0.08em tracking
3. **Dimensions** — `142.3 × 89.7 × 45.1mm` (× not x, unit stuck to last number)
4. **Timestamps** — relative ("2m ago"), tooltip for full ISO

---

## Icon Library

Library: **Remix Icon** via `react-icons/ri`

### Why Remix
- 1.5px strokes at 24px match logomark stroke language
- Line + Fill pairs for active state toggles
- Tree-shakeable imports

### Sizing Rules

| Context | Size | Tailwind |
|---------|------|----------|
| Nav, inline actions | 16px | `h-4 w-4` |
| Primary CTAs | 20px | `h-5 w-5` |
| Empty state placeholders | 24px | `h-6 w-6` |

### Core Rules

1. Line variant default, Fill for active only
2. Icons inherit text colour from parent
3. Icon-only buttons require `aria-label` + Tooltip
4. No decorative icons in headings/stats/empty states
5. Semantic pairing: icon must match label exactly

---

## Animation System

### Dual-Library Approach

| Library | Use For |
|---------|---------|
| Framer Motion | Component-level React (enter/exit, layout, gestures) |
| CSS @keyframes | Persistent ambient loops (shimmer, pulse, glow) |

### CSS Keyframe Catalogue

| Class | Duration | Effect | Reduced Motion |
|-------|----------|--------|----------------|
| `animate-stage-pulse` | 2s | opacity 1→0.5→1 | Static glow |
| `shimmer-sweep` | 2s | 4% white gradient sweep | Static opacity |
| `animate-glow-ring` | 2s | box-shadow pulse | Static shadow |
| `animate-float` | 3s | translateY -8px bob | Disabled |
| `animate-logo-shimmer` | 4s | brand gradient sweep on text | Static colour |
| `animate-shake` | 0.4s | translateX ±4px (once) | N/A |

### Reduced Motion (Mandatory)

```css
@media (prefers-reduced-motion: reduce) {
  .animate-stage-pulse, .animate-glow-ring,
  .animate-float, .animate-logo-shimmer, .shimmer-sweep {
    animation: none;
  }
  * { transition-duration: 0.01ms !important; }
}
```

React: `useReducedMotion()` from framer-motion to skip entrance variants.

---

## Accessibility

### Target: WCAG 2.2 AA (EU Accessibility Act compliant)

### Keyboard
- All interactive elements reachable via Tab, activatable via Enter/Space
- Visible focus ring: `focus-visible:ring-2 ring-[brand] ring-offset-2`
- Tab order matches visual layout
- Focus trapping in modals

### Screen Reader
- Status changes: `role="status"` with `aria-live="polite"`
- Errors: `aria-live="assertive"`
- Icon-only buttons: `aria-label` on parent, `aria-hidden="true"` on SVG
- Decorative elements: `aria-hidden="true"`
- Form inputs: visible `<label>` or `aria-label`, errors via `aria-describedby`

### Colour
- Never convey information by colour alone
- Status uses colour + text + icon
- All pairs tested against WCAG AA ratios

### Touch Targets
- Minimum 44×44px effective area
- Icon buttons: 32px visual + padding to reach 44px

---

## UK/EU 2026 Design Defaults

### Compliance Requirements
- **EU Accessibility Act** (effective June 2025) — WCAG 2.2 AA minimum
- **UK GDPR** — consent-first cookie/data capture, designed as UI not afterthought
- **Dark mode mandatory** — UK users expect both themes, toggle in nav

### Visual Patterns for UK/EU

1. **Reduced-energy palettes** — dark backgrounds, efficient colour, less visual noise
2. **Mobile-first** — UK mobile commerce at 57-59% of transactions
3. **Variable fonts** — single file, responsive weight/width, better CWV scores
4. **Typography-led design** — oversized display type, aggressive scale contrast
5. **Glassmorphism for depth** — frosted panels, backdrop blur, layered surfaces
6. **Soft brutalist structure** — bold shapes smoothed with rounded corners and muted tones
7. **Micro-interactions** — hover states, scroll triggers, purposeful transitions
8. **Component-driven** — atomic design, headless UI (Radix/ShadCN), design tokens
9. **Bento grid layouts** — modular, asymmetric content blocks
10. **Scroll-triggered narrative** — "scrollytelling" for product pages and onboarding

### Performance Targets (Core Web Vitals)
- LCP < 2.5s
- FID < 100ms
- CLS < 0.1
- `next/font` with `font-display: swap`
- WebP/AVIF images, lazy-loaded 3D content
