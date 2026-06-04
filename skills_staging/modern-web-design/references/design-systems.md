# Design Systems & Branding Guide - 2025

## Design Token Architecture

### DTCG Specification (W3C Standard - Oct 2025)

The Design Tokens Community Group released v2025.10, the first stable design token interchange format with contributions from Adobe, Google, Microsoft, Figma, and 20+ organizations.

### DTCG Token Format

```json
{
  "$name": "Brand Design Tokens",
  "$description": "Core design tokens for the brand",
  
  "color": {
    "$type": "color",
    "primitive": {
      "blue": {
        "50": { "$value": "oklch(0.97 0.02 250)" },
        "100": { "$value": "oklch(0.93 0.04 250)" },
        "500": { "$value": "oklch(0.55 0.22 250)" },
        "900": { "$value": "oklch(0.25 0.12 250)" }
      },
      "gray": {
        "50": { "$value": "oklch(0.98 0.002 250)" },
        "900": { "$value": "oklch(0.15 0.02 250)" }
      }
    },
    "semantic": {
      "background": {
        "$value": "{color.primitive.gray.50}",
        "$description": "Default page background"
      },
      "primary": {
        "$value": "{color.primitive.blue.500}",
        "$description": "Primary brand color"
      }
    }
  },
  
  "spacing": {
    "$type": "dimension",
    "1": { "$value": { "value": 4, "unit": "px" } },
    "2": { "$value": { "value": 8, "unit": "px" } },
    "4": { "$value": { "value": 16, "unit": "px" } },
    "8": { "$value": { "value": 32, "unit": "px" } }
  },
  
  "typography": {
    "$type": "typography",
    "heading": {
      "1": {
        "$value": {
          "fontFamily": "{font.family.display}",
          "fontSize": "{font.size.5xl}",
          "fontWeight": "{font.weight.bold}",
          "lineHeight": "{font.lineHeight.tight}"
        }
      }
    }
  },
  
  "shadow": {
    "$type": "shadow",
    "sm": {
      "$value": {
        "offsetX": { "value": 0, "unit": "px" },
        "offsetY": { "value": 1, "unit": "px" },
        "blur": { "value": 3, "unit": "px" },
        "spread": { "value": 0, "unit": "px" },
        "color": "oklch(0 0 0 / 0.1)"
      }
    }
  }
}
```

### Three-Tier Token System

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: Component Tokens                                   │
│  --btn-primary-bg, --card-border, --input-focus-ring        │
│  Purpose: Component-specific values                         │
├─────────────────────────────────────────────────────────────┤
│  TIER 2: Semantic Tokens                                    │
│  --color-primary, --color-surface, --text-muted             │
│  Purpose: Meaning-based, context-aware                      │
├─────────────────────────────────────────────────────────────┤
│  TIER 1: Primitive Tokens                                   │
│  --blue-500, --gray-100, --space-4, --font-sans             │
│  Purpose: Raw values, brand colors, base scale              │
└─────────────────────────────────────────────────────────────┘
```

## OKLCH Color System (2025 Standard)

OKLCH provides perceptually uniform colors with 92% browser support as of 2025.

### Why OKLCH?

- **Perceptually uniform**: Equal changes in values = equal visual changes
- **Better for palettes**: Consistent lightness across hues
- **P3 color space**: Access to wider gamut displays
- **Dark mode**: Predictable lightness adjustments

### Complete Token Implementation

```css
:root {
  /* ═══════════════════════════════════════════════════════════
     TIER 1: PRIMITIVES
     Raw values using OKLCH (Lightness, Chroma, Hue)
     ═══════════════════════════════════════════════════════════ */
  
  /* Base colors */
  --white: oklch(1 0 0);
  --black: oklch(0 0 0);
  
  /* Gray scale (neutral hue ~250) */
  --gray-50: oklch(0.98 0.002 250);
  --gray-100: oklch(0.96 0.004 250);
  --gray-200: oklch(0.92 0.006 250);
  --gray-300: oklch(0.87 0.008 250);
  --gray-400: oklch(0.70 0.01 250);
  --gray-500: oklch(0.55 0.012 250);
  --gray-600: oklch(0.45 0.014 250);
  --gray-700: oklch(0.35 0.016 250);
  --gray-800: oklch(0.25 0.018 250);
  --gray-900: oklch(0.15 0.02 250);
  --gray-950: oklch(0.10 0.02 250);
  
  /* Brand colors */
  --brand-primary: oklch(0.55 0.22 250);      /* Blue */
  --brand-primary-light: oklch(0.70 0.18 250);
  --brand-primary-dark: oklch(0.40 0.20 250);
  
  --brand-secondary: oklch(0.65 0.18 180);    /* Teal */
  --brand-accent: oklch(0.75 0.16 85);        /* Gold */
  
  /* Status colors */
  --success-base: oklch(0.60 0.18 145);       /* Green */
  --warning-base: oklch(0.75 0.16 85);        /* Amber */
  --error-base: oklch(0.55 0.22 25);          /* Red */
  --info-base: oklch(0.60 0.18 250);          /* Blue */
  
  /* Spacing scale (4px base) */
  --space-0: 0;
  --space-0-5: 0.125rem;  /* 2px */
  --space-1: 0.25rem;     /* 4px */
  --space-2: 0.5rem;      /* 8px */
  --space-3: 0.75rem;     /* 12px */
  --space-4: 1rem;        /* 16px */
  --space-5: 1.25rem;     /* 20px */
  --space-6: 1.5rem;      /* 24px */
  --space-8: 2rem;        /* 32px */
  --space-10: 2.5rem;     /* 40px */
  --space-12: 3rem;       /* 48px */
  --space-16: 4rem;       /* 64px */
  --space-20: 5rem;       /* 80px */
  --space-24: 6rem;       /* 96px */
  
  /* Typography scale */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */
  --text-5xl: 3rem;       /* 48px */
  --text-6xl: 3.75rem;    /* 60px */
  
  /* Line heights */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;
  
  /* Font weights */
  --font-thin: 100;
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  --font-extrabold: 800;
  
  /* Font families */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-display: 'Cal Sans', 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Border radius */
  --radius-none: 0;
  --radius-sm: 0.125rem;  /* 2px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-2xl: 1rem;     /* 16px */
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-xs: 0 1px 2px 0 oklch(0 0 0 / 0.05);
  --shadow-sm: 0 1px 3px 0 oklch(0 0 0 / 0.1), 0 1px 2px -1px oklch(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px oklch(0 0 0 / 0.1), 0 2px 4px -2px oklch(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px oklch(0 0 0 / 0.1), 0 4px 6px -4px oklch(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px oklch(0 0 0 / 0.1), 0 8px 10px -6px oklch(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px oklch(0 0 0 / 0.25);
  
  /* ═══════════════════════════════════════════════════════════
     TIER 2: SEMANTIC TOKENS
     Meaning-based tokens that reference primitives
     ═══════════════════════════════════════════════════════════ */
  
  /* Backgrounds */
  --color-bg: var(--white);
  --color-bg-subtle: var(--gray-50);
  --color-bg-muted: var(--gray-100);
  --color-bg-emphasis: var(--gray-900);
  
  /* Surfaces (cards, panels) */
  --color-surface: var(--white);
  --color-surface-raised: var(--white);
  --color-surface-overlay: var(--white);
  
  /* Text */
  --color-text: var(--gray-900);
  --color-text-secondary: var(--gray-600);
  --color-text-muted: var(--gray-500);
  --color-text-subtle: var(--gray-400);
  --color-text-inverse: var(--white);
  
  /* Borders */
  --color-border: var(--gray-200);
  --color-border-subtle: var(--gray-100);
  --color-border-emphasis: var(--gray-300);
  
  /* Interactive */
  --color-primary: var(--brand-primary);
  --color-primary-hover: var(--brand-primary-dark);
  --color-primary-subtle: oklch(0.95 0.05 250);
  
  --color-secondary: var(--brand-secondary);
  --color-accent: var(--brand-accent);
  
  /* Status */
  --color-success: var(--success-base);
  --color-success-subtle: oklch(0.95 0.05 145);
  --color-warning: var(--warning-base);
  --color-warning-subtle: oklch(0.95 0.05 85);
  --color-error: var(--error-base);
  --color-error-subtle: oklch(0.95 0.05 25);
  --color-info: var(--info-base);
  --color-info-subtle: oklch(0.95 0.05 250);
  
  /* Focus */
  --color-focus-ring: var(--brand-primary);
  
  /* ═══════════════════════════════════════════════════════════
     TIER 3: COMPONENT TOKENS
     Component-specific tokens for consistent styling
     ═══════════════════════════════════════════════════════════ */
  
  /* Buttons */
  --btn-primary-bg: var(--color-primary);
  --btn-primary-bg-hover: var(--color-primary-hover);
  --btn-primary-text: var(--color-text-inverse);
  
  --btn-secondary-bg: var(--color-surface);
  --btn-secondary-bg-hover: var(--color-bg-subtle);
  --btn-secondary-text: var(--color-text);
  --btn-secondary-border: var(--color-border);
  
  --btn-ghost-bg: transparent;
  --btn-ghost-bg-hover: var(--color-bg-subtle);
  --btn-ghost-text: var(--color-text);
  
  /* Cards */
  --card-bg: var(--color-surface);
  --card-border: var(--color-border);
  --card-shadow: var(--shadow-sm);
  --card-radius: var(--radius-lg);
  
  /* Inputs */
  --input-bg: var(--color-surface);
  --input-border: var(--color-border);
  --input-border-hover: var(--color-border-emphasis);
  --input-border-focus: var(--color-primary);
  --input-text: var(--color-text);
  --input-placeholder: var(--color-text-muted);
  --input-radius: var(--radius-md);
  
  /* Navigation */
  --nav-bg: var(--color-surface);
  --nav-border: var(--color-border);
  --nav-link: var(--color-text-secondary);
  --nav-link-hover: var(--color-text);
  --nav-link-active: var(--color-primary);
}
```

### Dark Mode (Semantic Overrides Only)

```css
.dark {
  /* Semantic overrides - primitives stay the same */
  --color-bg: var(--gray-950);
  --color-bg-subtle: var(--gray-900);
  --color-bg-muted: var(--gray-800);
  --color-bg-emphasis: var(--gray-50);
  
  --color-surface: var(--gray-900);
  --color-surface-raised: var(--gray-800);
  --color-surface-overlay: var(--gray-800);
  
  --color-text: var(--gray-50);
  --color-text-secondary: var(--gray-300);
  --color-text-muted: var(--gray-400);
  --color-text-subtle: var(--gray-500);
  --color-text-inverse: var(--gray-900);
  
  --color-border: var(--gray-800);
  --color-border-subtle: var(--gray-900);
  --color-border-emphasis: var(--gray-700);
  
  /* Lighter primary for dark backgrounds */
  --color-primary: var(--brand-primary-light);
  --color-primary-hover: var(--brand-primary);
  --color-primary-subtle: oklch(0.20 0.08 250);
  
  /* Status colors - darker backgrounds */
  --color-success-subtle: oklch(0.20 0.08 145);
  --color-warning-subtle: oklch(0.20 0.08 85);
  --color-error-subtle: oklch(0.20 0.08 25);
  --color-info-subtle: oklch(0.20 0.08 250);
  
  /* Shadows need adjustment for dark mode */
  --shadow-sm: 0 1px 3px 0 oklch(0 0 0 / 0.3);
  --shadow-md: 0 4px 6px -1px oklch(0 0 0 / 0.4);
}
```

### Relative Color Syntax (Derived Colors)

```css
:root {
  --color-primary: oklch(0.55 0.22 250);
  
  /* Derive hover state by adjusting lightness */
  --color-primary-hover: oklch(from var(--color-primary) calc(l - 0.1) c h);
  
  /* Derive subtle background */
  --color-primary-subtle: oklch(from var(--color-primary) 0.95 0.05 h);
  
  /* Complementary color (opposite hue) */
  --color-complementary: oklch(from var(--color-primary) l c calc(h + 180));
  
  /* Analogous colors */
  --color-analogous-1: oklch(from var(--color-primary) l c calc(h + 30));
  --color-analogous-2: oklch(from var(--color-primary) l c calc(h - 30));
}
```

## Multi-Theme Architecture

```css
/* Theme base using data attributes */
:root,
[data-theme="light"] {
  --color-background: var(--white);
  --color-foreground: var(--gray-900);
  --color-primary: oklch(0.55 0.22 250);
}

[data-theme="dark"] {
  --color-background: var(--gray-950);
  --color-foreground: var(--gray-50);
  --color-primary: oklch(0.70 0.18 250);
}

/* Brand themes */
[data-theme="blue"] {
  --color-primary: oklch(0.55 0.22 250);
}

[data-theme="emerald"] {
  --color-primary: oklch(0.60 0.18 160);
}

[data-theme="rose"] {
  --color-primary: oklch(0.60 0.22 15);
}

[data-theme="purple"] {
  --color-primary: oklch(0.55 0.25 300);
}

/* System preference fallback */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --color-background: var(--gray-950);
    --color-foreground: var(--gray-50);
  }
}
```

```tsx
// Theme provider implementation
'use client';

import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';
type BrandTheme = 'blue' | 'emerald' | 'rose' | 'purple';

interface ThemeContextType {
  theme: Theme;
  brandTheme: BrandTheme;
  setTheme: (theme: Theme) => void;
  setBrandTheme: (theme: BrandTheme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('system');
  const [brandTheme, setBrandTheme] = useState<BrandTheme>('blue');
  
  useEffect(() => {
    const root = document.documentElement;
    
    // Apply color scheme
    if (theme === 'system') {
      root.removeAttribute('data-theme');
    } else {
      root.setAttribute('data-theme', theme);
    }
    
    // Apply brand theme
    root.setAttribute('data-brand', brandTheme);
  }, [theme, brandTheme]);
  
  return (
    <ThemeContext.Provider value={{ theme, brandTheme, setTheme, setBrandTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

## Typography System

### Font Loading Strategy (Next.js 15)

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google';
import localFont from 'next/font/local';

// Variable font from Google
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-sans',
});

// Local display font
const calSans = localFont({
  src: '../fonts/CalSans-SemiBold.woff2',
  variable: '--font-display',
  display: 'swap',
});

// Local mono font
const jetbrains = localFont({
  src: '../fonts/JetBrainsMono-Variable.woff2',
  variable: '--font-mono',
  display: 'swap',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html className={`${inter.variable} ${calSans.variable} ${jetbrains.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

### Fluid Typography Scale

```css
:root {
  /* Fluid typography using clamp() */
  --text-fluid-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --text-fluid-sm: clamp(0.875rem, 0.8rem + 0.35vw, 1rem);
  --text-fluid-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-fluid-lg: clamp(1.125rem, 1rem + 0.6vw, 1.25rem);
  --text-fluid-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
  --text-fluid-2xl: clamp(1.5rem, 1.2rem + 1.5vw, 2rem);
  --text-fluid-3xl: clamp(1.875rem, 1.4rem + 2.4vw, 2.5rem);
  --text-fluid-4xl: clamp(2.25rem, 1.6rem + 3.2vw, 3.5rem);
  --text-fluid-5xl: clamp(3rem, 2rem + 5vw, 4.5rem);
}

/* Text style compositions */
.heading-1 {
  font-family: var(--font-display);
  font-size: var(--text-fluid-5xl);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  letter-spacing: -0.02em;
}

.heading-2 {
  font-family: var(--font-display);
  font-size: var(--text-fluid-4xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  letter-spacing: -0.01em;
}

.heading-3 {
  font-family: var(--font-sans);
  font-size: var(--text-fluid-2xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-snug);
}

.body-large {
  font-family: var(--font-sans);
  font-size: var(--text-fluid-lg);
  line-height: var(--leading-relaxed);
}

.body-default {
  font-family: var(--font-sans);
  font-size: var(--text-fluid-base);
  line-height: var(--leading-normal);
}

.label {
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  line-height: var(--leading-none);
}

.caption {
  font-family: var(--font-sans);
  font-size: var(--text-xs);
  line-height: var(--leading-normal);
  color: var(--color-text-muted);
}
```

## Brand Implementation Workflow

### 1. Brand Discovery Checklist

```markdown
## Brand Assets Required

### Colors
- [ ] Primary brand color (provide hex/RGB)
- [ ] Secondary color(s)
- [ ] Accent color(s)
- [ ] Success/warning/error colors (or use defaults)
- [ ] Light mode preference
- [ ] Dark mode support needed?

### Typography
- [ ] Primary font family (for body text)
- [ ] Display font (for headings)
- [ ] Mono font (for code)
- [ ] Font weights used (regular, medium, bold, etc.)
- [ ] Font files (WOFF2 preferred)

### Visual Style
- [ ] Logo files (SVG preferred)
- [ ] Icon style (outlined, solid, duotone)
- [ ] Border radius preference (sharp/rounded/pill)
- [ ] Shadow style (subtle/prominent/none)

### Voice & Tone
- [ ] Brand adjectives (professional, playful, etc.)
- [ ] UI copy guidelines
```

### 2. Color Conversion to OKLCH

```typescript
// utils/color-convert.ts

/**
 * Convert hex color to OKLCH
 * For accurate conversion, use a library like 'culori' or 'color.js'
 */
import { oklch, formatCss } from 'culori';

export function hexToOklch(hex: string): string {
  const color = oklch(hex);
  if (!color) return hex;
  
  const l = (color.l * 100).toFixed(2);
  const c = color.c.toFixed(3);
  const h = (color.h || 0).toFixed(1);
  
  return `oklch(${l}% ${c} ${h})`;
}

// Generate color scale from brand color
export function generateColorScale(baseHex: string) {
  const base = oklch(baseHex);
  if (!base) return null;
  
  return {
    50: formatCss(oklch({ l: 0.97, c: base.c * 0.1, h: base.h })),
    100: formatCss(oklch({ l: 0.93, c: base.c * 0.2, h: base.h })),
    200: formatCss(oklch({ l: 0.85, c: base.c * 0.4, h: base.h })),
    300: formatCss(oklch({ l: 0.75, c: base.c * 0.6, h: base.h })),
    400: formatCss(oklch({ l: 0.65, c: base.c * 0.8, h: base.h })),
    500: formatCss(base),
    600: formatCss(oklch({ l: base.l - 0.1, c: base.c, h: base.h })),
    700: formatCss(oklch({ l: base.l - 0.2, c: base.c * 0.9, h: base.h })),
    800: formatCss(oklch({ l: base.l - 0.3, c: base.c * 0.8, h: base.h })),
    900: formatCss(oklch({ l: base.l - 0.35, c: base.c * 0.7, h: base.h })),
    950: formatCss(oklch({ l: base.l - 0.4, c: base.c * 0.6, h: base.h })),
  };
}
```

### 3. Tailwind v4 Theme Extension

```css
/* globals.css - Tailwind v4 CSS-first configuration */
@import "tailwindcss";

@theme {
  /* Colors from CSS variables */
  --color-background: var(--color-bg);
  --color-foreground: var(--color-text);
  --color-primary: var(--color-primary);
  --color-primary-foreground: var(--color-text-inverse);
  --color-secondary: var(--color-secondary);
  --color-muted: var(--color-bg-muted);
  --color-muted-foreground: var(--color-text-muted);
  --color-accent: var(--color-accent);
  --color-destructive: var(--color-error);
  --color-border: var(--color-border);
  --color-ring: var(--color-focus-ring);
  
  /* Font families */
  --font-sans: var(--font-sans);
  --font-display: var(--font-display);
  --font-mono: var(--font-mono);
  
  /* Border radius */
  --radius-sm: var(--radius-sm);
  --radius-md: var(--radius-md);
  --radius-lg: var(--radius-lg);
  --radius-xl: var(--radius-xl);
}
```

## Component Library Structure

### Atomic Design Organization

```
components/
├── atoms/           # Basic building blocks
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   ├── Input/
│   ├── Badge/
│   └── Avatar/
├── molecules/       # Combinations of atoms
│   ├── FormField/
│   ├── SearchBar/
│   ├── MenuItem/
│   └── Card/
├── organisms/       # Complex components
│   ├── Header/
│   ├── Footer/
│   ├── Sidebar/
│   └── DataTable/
├── templates/       # Page layouts
│   ├── DashboardLayout/
│   ├── AuthLayout/
│   └── MarketingLayout/
└── ui/              # ShadCN components
    ├── button.tsx
    ├── card.tsx
    └── ...
```

### Component Documentation

```tsx
// components/atoms/Button/Button.tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

/**
 * Primary UI button component.
 * 
 * @example
 * ```tsx
 * <Button variant="primary" size="lg">Click me</Button>
 * <Button variant="outline" leftIcon={<Plus />}>Add item</Button>
 * ```
 */
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /** Icon to display before button text */
  leftIcon?: React.ReactNode;
  /** Icon to display after button text */
  rightIcon?: React.ReactNode;
  /** Loading state */
  isLoading?: boolean;
}

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 font-medium transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-foreground hover:bg-primary-hover',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        outline: 'border border-border bg-background hover:bg-muted',
        ghost: 'hover:bg-muted',
        link: 'text-primary underline-offset-4 hover:underline',
        destructive: 'bg-destructive text-white hover:bg-destructive/90',
      },
      size: {
        sm: 'h-8 px-3 text-sm rounded-md',
        md: 'h-10 px-4 text-sm rounded-lg',
        lg: 'h-12 px-6 text-base rounded-lg',
        icon: 'h-10 w-10 rounded-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

export function Button({
  className,
  variant,
  size,
  leftIcon,
  rightIcon,
  isLoading,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? (
        <Spinner className="h-4 w-4 animate-spin" />
      ) : (
        leftIcon
      )}
      {children}
      {rightIcon}
    </button>
  );
}
```

## Best Practices

1. **Single source of truth** - All values flow from CSS variables
2. **Semantic naming** - Use purpose-based names (primary, surface) not appearance (blue, light)
3. **OKLCH for colors** - Perceptually uniform, better palettes
4. **Consistent scale** - Use 4px base for spacing
5. **Dark mode from day one** - Design tokens for both modes upfront
6. **Use DTCG format** - Standard interchange format for tools
7. **Document decisions** - Record why each token value was chosen
8. **Version tokens** - Track changes to design system over time
9. **Audit regularly** - Check for unused or inconsistent tokens
10. **Test across themes** - Verify all components work in all modes
