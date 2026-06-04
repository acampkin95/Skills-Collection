# Tailwind CSS v4/v5 Guide

Complete reference for Tailwind CSS in Next.js 15/16. Covers configuration, migration, debugging, and common issues.

---

## Configuration Requirements

### Required Files

| File | Extension | Content |
|------|-----------|---------|
| `postcss.config.mjs` | **Must be .mjs** | `@tailwindcss/postcss` plugin |
| `globals.css` | `.css` | `@import "tailwindcss"` |
| `layout.tsx` | `.tsx` | Must import `globals.css` |

### postcss.config.mjs

**Critical: File MUST have `.mjs` extension, NOT `.js`**

```javascript
/** @type {import('postcss-load-config').Config} */
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

### globals.css (v4 Syntax)

```css
/* ✅ CORRECT - Tailwind v4 */
@import "tailwindcss";

/* ❌ WRONG - Old v3 syntax */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Dependencies

```bash
# Tailwind v4 (current)
npm install tailwindcss @tailwindcss/postcss

# No longer needed in v4:
# - autoprefixer (built-in)
# - postcss-import (built-in)
# - tailwind.config.js (optional, CSS-based config preferred)
```

---

## Tailwind v4 Key Changes

### New Import Syntax

```css
/* Single import replaces all @tailwind directives */
@import "tailwindcss";
```

### CSS-Based Configuration

```css
@import "tailwindcss";

/* Theme customization */
@theme {
  --color-primary: #3b82f6;
  --color-secondary: #8b5cf6;
  --font-sans: "Inter", system-ui, sans-serif;
  --breakpoint-3xl: 1920px;
}

/* Custom variants */
@custom-variant dark (&:where(.dark, .dark *));

/* Source paths for monorepos */
@source "../packages/ui/src";
@source not "./legacy";
```

### Renamed Utilities

| Old (v3) | New (v4) |
|----------|----------|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `rounded-sm` | `rounded-xs` |
| `rounded` | `rounded-sm` |
| `blur-sm` | `blur-xs` |
| `blur` | `blur-sm` |
| `ring-offset-*` | `ring-inset` + padding |

### Container Changes

```css
/* v4 container behavior */
.container {
  /* Centers by default */
  /* No automatic padding - add explicitly */
  @apply mx-auto px-4;
}
```

---

## Common Issues & Fixes

### Issue: No Styling / Blank Page

**Symptoms:** Page renders as raw HTML, no CSS applied

**Diagnostic:**

```bash
# 1. Check config extension
ls postcss.config.*
# Must show: postcss.config.mjs

# 2. Check import syntax
grep '@import.*tailwindcss\|@tailwind' app/globals.css

# 3. Check layout imports globals.css
grep "globals.css" app/layout.tsx

# 4. Check browser console for CSS errors
```

**Fixes:**

```bash
# Fix 1: Rename config file
mv postcss.config.js postcss.config.mjs

# Fix 2: Update globals.css
echo '@import "tailwindcss";' > app/globals.css

# Fix 3: Clear cache
rm -rf .next && npm run dev
```

### Issue: Dynamic Classes Not Working

**Symptom:** Classes like `bg-${color}-500` don't apply

**Cause:** Tailwind purges classes not found as complete strings

```typescript
// ❌ WRONG - Gets purged
const bgClass = `bg-${color}-500`

// ❌ WRONG - Template in className
<div className={`text-${size}`}>

// ✅ CORRECT - Complete strings
const bgClass = color === 'red' ? 'bg-red-500' : 'bg-blue-500'

// ✅ CORRECT - Safelist approach
const colorMap = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
  green: 'bg-green-500',
} as const
```

**Alternative: Use CSS variables**

```css
/* globals.css */
@theme {
  --color-brand: var(--brand-color, #3b82f6);
}
```

```typescript
// Component
<div 
  style={{ '--brand-color': dynamicColor } as React.CSSProperties}
  className="bg-brand"
>
```

### Issue: Custom Classes Not Compiling

**Symptom:** `@apply` doesn't work, custom utilities missing

**Fix: Use @layer correctly**

```css
/* Must be after @import */
@import "tailwindcss";

@layer components {
  .btn-primary {
    @apply bg-blue-500 text-white px-4 py-2 rounded-sm;
  }
}

@layer utilities {
  .text-shadow {
    text-shadow: 2px 2px 4px rgb(0 0 0 / 10%);
  }
}
```

### Issue: Monorepo Classes Not Detected

**Symptom:** Classes from shared packages don't compile

**Fix: Add @source directives**

```css
@import "tailwindcss";

/* Include external packages */
@source "../packages/ui/src";
@source "../shared/components";

/* Exclude directories */
@source not "./node_modules";
@source not "./legacy";
```

### Issue: Dark Mode Not Working

**Fix: Configure variant**

```css
@import "tailwindcss";

/* Class-based dark mode */
@custom-variant dark (&:where(.dark, .dark *));
```

```typescript
// Usage
<html className="dark">
  <body>
    <div className="bg-white dark:bg-gray-900">
```

### Issue: Build Performance

**Symptoms:** Slow builds, memory issues

**Fixes:**

```css
/* Limit source scanning */
@source "./src";
@source not "./node_modules";
@source not "./.next";
@source not "./public";
```

---

## Tailwind v5 Preview

### Expected Changes (When Released)

1. **Native CSS Nesting** - Full support without plugins
2. **Improved Performance** - Faster compilation
3. **Enhanced Container Queries** - Better `@container` support
4. **P3 Color Support** - Wider color gamut

### Migration Preparation

```css
/* Start using CSS-based config now */
@import "tailwindcss";

@theme {
  /* Define all custom values here */
  --color-*: ...;
  --font-*: ...;
  --spacing-*: ...;
}
```

---

## Best Practices

### 1. Use Static Class Names

```typescript
// ✅ Best: Object mapping
const variants = {
  primary: 'bg-blue-500 text-white',
  secondary: 'bg-gray-200 text-gray-800',
  danger: 'bg-red-500 text-white',
} as const

type Variant = keyof typeof variants

function Button({ variant = 'primary' }: { variant?: Variant }) {
  return <button className={variants[variant]}>Click</button>
}
```

### 2. Organize Custom Styles

```css
@import "tailwindcss";

/* 1. Theme variables */
@theme {
  --color-primary: #3b82f6;
}

/* 2. Custom variants */
@custom-variant dark (&:where(.dark, .dark *));

/* 3. Base styles */
@layer base {
  body {
    @apply antialiased;
  }
}

/* 4. Component styles */
@layer components {
  .card {
    @apply rounded-sm border bg-white p-4 shadow-xs;
  }
}

/* 5. Utility styles */
@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

### 3. TypeScript Integration

```typescript
// lib/cn.ts - Class name utility
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Usage
<div className={cn(
  'base-styles',
  isActive && 'active-styles',
  className
)}>
```

### 4. Performance Optimization

```css
/* Minimize @source scope */
@source "./src/app";
@source "./src/components";

/* Exclude build artifacts */
@source not "./.next";
@source not "./dist";
```

---

## Debugging Checklist

```bash
# 1. Verify installation
npm ls tailwindcss @tailwindcss/postcss

# 2. Check config extension
ls postcss.config.*  # Must be .mjs

# 3. Check import syntax
head -5 app/globals.css  # Must have @import "tailwindcss"

# 4. Check layout imports
grep "globals.css" app/layout.tsx

# 5. Check for dynamic classes
grep -rn 'className.*`.*\${' --include="*.tsx" src/ app/

# 6. Clear cache and rebuild
rm -rf .next node_modules/.cache
npm run dev

# 7. Check browser dev tools
# - Inspect element, verify classes present
# - Check Network tab for CSS loading
# - Check Console for errors
```

---

## Migration: v3 to v4

### Step 1: Update Dependencies

```bash
npm uninstall tailwindcss autoprefixer
npm install tailwindcss @tailwindcss/postcss
```

### Step 2: Update PostCSS Config

```javascript
// postcss.config.mjs (rename from .js)
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

### Step 3: Update CSS

```css
/* Before (v3) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* After (v4) */
@import "tailwindcss";
```

### Step 4: Update Renamed Classes

```bash
# Find renamed utilities
grep -rn "shadow-sm\|rounded-sm\|blur-sm" --include="*.tsx" src/
```

Replace:
- `shadow-sm` → `shadow-xs`
- `rounded-sm` → `rounded-xs`
- `blur-sm` → `blur-xs`

### Step 5: Migrate Config to CSS

```css
/* Move tailwind.config.js content to globals.css */
@import "tailwindcss";

@theme {
  /* From theme.extend.colors */
  --color-primary: #3b82f6;
  
  /* From theme.extend.fontFamily */
  --font-sans: "Inter", system-ui, sans-serif;
}
```

### Step 6: Test

```bash
rm -rf .next
npm run build
npm run dev
```
