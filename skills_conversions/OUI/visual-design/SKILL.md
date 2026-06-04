---
name: visual-design
description: "Visual design fundamentals covering color theory (OKLCH), typography systems, spacing systems, layout grids, composition principles, and visual branding for non-CLI agents. Use when making color decisions, choosing typography, designing layouts, creating visual hierarchy, or establishing design systems."
version: "1.0.0"
metadata:
  category: design-visual
  scope: non-cli
---

# Visual Design

Color theory, typography, layout, and composition principles for creating cohesive visual designs.

## Color System (OKLCH)

### Why OKLCH Over HSL/RGB

```
OKLCH (Oklch color space):
├── Perceptually uniform (equal numeric steps = equal visual steps)
├── Predictable lightness adjustments
├── Better dark mode generation (same hue, adjust L)
├── Format: oklch(lightness chroma hue)
│   L: 0-1 (0=black, 1=white)
│   C: 0-0.4 (0=gray, higher=vivid)
│   H: 0-360 (hue angle)

vs HSL:
├── HSL is NOT perceptually uniform
├── "Same lightness" looks different across hues
└── Dark mode calculations unreliable
```

### Building a Color Palette

```
STEP 1: Choose brand hue
  Primary: oklch(0.55 0.22 264) — Blue

STEP 2: Generate shades (adjust L only)
  50:  oklch(0.97 0.02 264)   — Lightest background
  100: oklch(0.93 0.04 264)   — Light background
  200: oklch(0.85 0.08 264)   — Light surface
  300: oklch(0.75 0.12 264)   — Muted
  400: oklch(0.65 0.17 264)   — Soft
  500: oklch(0.55 0.22 264)   — Base
  600: oklch(0.45 0.20 264)   — Dark
  700: oklch(0.37 0.16 264)   — Darker
  800: oklch(0.28 0.12 264)   — Dark surface
  900: oklch(0.20 0.08 264)   — Darkest

STEP 3: Add semantic colors
  Success: oklch(0.65 0.20 145)   — Green
  Warning: oklch(0.75 0.18 85)    — Amber
  Error:   oklch(0.55 0.22 25)    — Red
  Info:    oklch(0.55 0.18 240)   — Blue

STEP 4: Add neutrals (chroma ≈ 0)
  Neutral-0:  oklch(1.00 0 0)    — White
  Neutral-50: oklch(0.97 0.005 264) — Near white (tiny brand tint)
  Neutral-100:oklch(0.93 0.005 264)
  ...
  Neutral-900:oklch(0.15 0.01 264) — Near black
```

### Color Usage Rules

```
BACKGROUND COLORS:
├── Base:     Neutral-0 (white) or Neutral-50
├── Surface:  Neutral-50 or Neutral-100 (cards, panels)
├── Overlay:  Neutral-900 at 50% opacity (modals)
└── Accent:   Primary-50 (subtle highlights)

TEXT COLORS:
├── Primary:   Neutral-900 (headings, important)
├── Secondary: Neutral-700 (body text)
├── Tertiary:  Neutral-500 (captions, labels)
├── Disabled:  Neutral-400
└── Inverse:   Neutral-0 (text on dark backgrounds)

DONT'S:
├── Never use pure black (#000) for text — use dark gray
├── Never use pure white on bright colors
├── Don't put saturated colors on saturated colors
├── Don't rely on color alone for information
└── Don't use more than 3-4 colors in a palette
```

## Typography System

### Font Selection

```
CATEGORIES:
├── Serif:     Traditional, authoritative (Georgia, Merriweather)
├── Sans-serif: Modern, clean (Inter, system-ui, Roboto)
├── Monospace:  Technical, code (JetBrains Mono, Fira Code)
├── Display:    Expressive, headings (custom/display fonts)
└── Variable:   Modern, single file with weight variations

SYSTEM FONT STACK (no download needed):
├── Sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif
├── Serif: "Iowan Old Style", Georgia, serif
└── Mono: "SF Mono", "Fira Code", "Fira Mono", monospace
```

### Type Scale & Hierarchy

```
SCALE (Major Third — 1.25 ratio):
──────────────────────────────────
12px → Caption, legal, overline
14px → Small body, table cells, helper text
16px → Base body text (default)
18px → Lead paragraph, intro text
20px → H4, card headings
24px → H3, subsection headings
30px → H2, section headings
36px → H1, page headings
48px → Display, hero headings
60px → Large display

WEIGHT:
├── 400 (Regular):    Body text
├── 500 (Medium):     Subtle emphasis, navigation
├── 600 (Semi-bold):  Subheadings, labels
├── 700 (Bold):       Headings, strong emphasis
└── 800-900:          Display only (overuse looks heavy)
```

### Responsive Typography

```
FLUID TYPE (clamp):
───────────────────
font-size: clamp(1rem, 0.5rem + 2vw, 1.5rem);

/* Maps to:
   Mobile (320px):  1rem (16px)
   Desktop (1280px): 1.5rem (24px)
   Linear interpolation between */

RECOMMENDED CLAMP VALUES:
H1:  clamp(2rem, 1rem + 3vw, 3.5rem)
H2:  clamp(1.5rem, 0.8rem + 2vw, 2.5rem)
H3:  clamp(1.25rem, 0.7rem + 1.5vw, 1.875rem)
Body: clamp(0.875rem, 0.5rem + 0.5vw, 1rem)
```

## Spacing System

### 8-Point Grid

```
TOKEN SYSTEM:
─────────────
space-0:  0px      → No gap
space-0.5: 4px     → Micro (icon gaps)
space-1:  8px      → Tight (within components)
space-1.5: 12px    → Close (between related items)
space-2:  16px     → Standard (component padding)
space-3:  24px     → Comfortable (between components)
space-4:  32px     → Spacious (section gaps)
space-6:  48px     → Generous (major sections)
space-8:  64px     → Expansive (hero padding)
space-12: 96px     → Maximum (page margins)

USAGE:
├── Component internal:  space-0.5 to space-2
├── Component external:  space-2 to space-4
├── Section gaps:        space-4 to space-8
├── Page margins:        space-4 to space-8
└── Max content width:   65-75ch or 1152-1280px
```

## Layout & Composition

### Container Widths

```
BREAKPOINTS (mobile-first):
─────────────────────────────
sm:  640px    → Large phones
md:  768px    → Tablets
lg:  1024px   → Small laptops
xl:  1280px   → Desktops
2xl: 1536px   → Large screens

MAX WIDTHS:
├── Content:     65ch (text), 1152px (UI)
├── Prose:       65-75ch (optimal reading)
├── Navigation:  1280px
├── Full bleed:  100vw (hero images, etc.)
```

### Layout Patterns

```
HOLY GRAIL LAYOUT:
┌──────────────────────────────────┐
│            HEADER                │
├──────┬───────────────────┬───────┤
│      │                   │       │
│ SIDE │     CONTENT       │ SIDE  │
│ BAR  │                   │ BAR   │
│      │                   │       │
├──────┴───────────────────┴───────┤
│            FOOTER                │
└──────────────────────────────────┘

DASHBOARD LAYOUT:
┌─────┬─────┬─────┬─────┐
│ KPI │ KPI │ KPI │ KPI │
├─────┴─────┼─────┴─────┤
│  CHART    │  CHART    │
│  (wide)   │  (wide)   │
├───────────┼───────────┤
│  TABLE    │  ACTIVITY │
└───────────┴───────────┘

CONTENT PAGE:
┌──────────────────────────────────┐
│         HERO / HEADER            │
├──────────────────────────────────┤
│                                  │
│         ARTICLE CONTENT          │
│         (max-width: 65ch)        │
│                                  │
├──────────────────────────────────┤
│         RELATED CONTENT          │
└──────────────────────────────────┘
```

### Alignment Principles

```
ALIGNMENT RULES:
├── Left-align body text (for LTR languages)
├── Right-align numbers in tables (decimal alignment)
├── Center-align short headings, hero text
├── Align labels with their inputs
├── Maintain consistent alignment within sections
└── Break alignment deliberately (not accidentally)

VERTICAL RHYTHM:
├── All elements sit on the baseline grid
├── Spacing between elements is consistent
├── Headings, paragraphs, lists all rhythm together
└── Creates visual harmony even with varied content
```

## Dark Mode

### Color Adjustment Strategy

```
DON'T JUST INVERT — ADJUST:

Light → Dark adjustments:
├── Background:  White (#fff) → Dark gray (#121212), NOT black
├── Surface:    Light gray (#f5f5f5) → Darker gray (#1e1e1e)
├── Elevation:  Shadows → Lighter surfaces (overlay layers)
├── Text:       Dark (#1a1a1a) → Light (#e4e4e7)
├── Muted text:  Medium gray → Lighter gray
├── Accent:     Reduce saturation slightly
└── Error:      Soften red (less eye-strain on dark)

SURFACE HIERARCHY (dark mode):
├── Level 0: #121212 (base/background)
├── Level 1: #1e1e1e (cards)
├── Level 2: #242424 (raised cards)
├── Level 3: #2c2c2c (modals, popovers)
└── Level 4: #383838 (highest elevation)
```


## When to Use

- Selecting color palettes using OKLCH color space
- Choosing and pairing typography for web projects
- Defining spacing systems and layout grids
- Creating dark mode variants of light designs
- Building design tokens or design system foundations

## Limitations

- OKLCH support requires modern browsers (2023+)
- Color perception varies by display calibration and user vision
- Typography rendering differs across operating systems
- Design tokens require translation to framework-specific formats

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [design-principles](../design-principles/SKILL.md) | Visual design implements core design principles |
| [responsive-design](../responsive-design/SKILL.md) | Visual design must adapt across breakpoints |
| [accessibility-knowledge](../accessibility-knowledge/SKILL.md) | Color contrast and typography affect accessibility |
| [modern-web-standards](../modern-web-standards/SKILL.md) | Modern CSS features enable better visual design |
