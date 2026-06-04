# Tailwind CSS v3 ↔ v4 Reference

## Quick Detection

```bash
# v4 indicators
ls postcss.config.mjs 2>/dev/null && echo "v4: mjs config"
grep "@import.*tailwindcss" **/*.css 2>/dev/null && echo "v4: @import syntax"
grep "@tailwindcss/postcss" package.json && echo "v4: postcss plugin"

# v3 indicators
ls tailwind.config.* 2>/dev/null && echo "v3: config file"
grep "@tailwind" **/*.css 2>/dev/null && echo "v3: @tailwind directives"
```

## Configuration Comparison

### v4 Setup

```javascript
// postcss.config.mjs (MUST be .mjs)
export default {
  plugins: {
    '@tailwindcss/postcss': {}
  }
}
```

```css
/* globals.css */
@import "tailwindcss";

/* Dark mode */
@custom-variant dark (&:where(.dark, .dark *));

/* Custom theme */
@theme {
  --color-brand: #3b82f6;
  --color-brand-light: #60a5fa;
  --font-display: "Cal Sans", sans-serif;
}

/* Monorepo sources */
@source "../packages/ui/src";

/* Plugins */
@plugin "@tailwindcss/typography";
```

**No `tailwind.config.js` needed** - CSS-first configuration

### v3 Setup

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#3b82f6',
          light: '#60a5fa',
        },
      },
      fontFamily: {
        display: ['Cal Sans', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Utility Renames (v3 → v4)

### Shadows
| v3 | v4 |
|----|----|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `shadow-md` | `shadow-md` |
| `shadow-lg` | `shadow-lg` |
| `shadow-xl` | `shadow-xl` |
| `shadow-2xl` | `shadow-2xl` |

### Blur
| v3 | v4 |
|----|----|
| `blur-sm` | `blur-xs` |
| `blur` | `blur-sm` |
| `blur-md` | `blur-md` |
| `blur-lg` | `blur-lg` |

### Border Radius
| v3 | v4 |
|----|----|
| `rounded-sm` | `rounded-xs` |
| `rounded` | `rounded-sm` |
| `rounded-md` | `rounded-md` |
| `rounded-lg` | `rounded-lg` |

### Outline & Ring
| v3 | v4 |
|----|----|
| `outline-none` | `outline-hidden` |
| `ring` | `ring-3` |
| `ring-1` | `ring-1` |
| `ring-2` | `ring-2` |

### Other Changes
| v3 | v4 |
|----|----|
| `flex-grow` | `grow` |
| `flex-shrink` | `shrink` |
| `overflow-clip` | `overflow-clip` |
| `decoration-clone` | `box-decoration-clone` |
| `decoration-slice` | `box-decoration-slice` |

## Dark Mode

### v4
```css
@import "tailwindcss";

/* Class-based (default) */
@custom-variant dark (&:where(.dark, .dark *));

/* Media query based */
@custom-variant dark (&:where(@media (prefers-color-scheme: dark), @media (prefers-color-scheme: dark) *));
```

### v3
```javascript
module.exports = {
  darkMode: 'class',  // or 'media'
}
```

## Custom Colors

### v4
```css
@theme {
  /* Single color */
  --color-brand: #3b82f6;
  
  /* Color scale */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-500: #3b82f6;
  --color-primary-900: #1e3a8a;
}
```

Usage: `bg-brand`, `text-primary-500`

### v3
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: '#3b82f6',
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
    },
  },
}
```

## Custom Fonts

### v4
```css
@theme {
  --font-display: "Cal Sans", "Inter", sans-serif;
  --font-body: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;
}
```

### v3
```javascript
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        display: ['Cal Sans', 'Inter', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
}
```

## Plugins

### v4
```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
@plugin "@tailwindcss/container-queries";
```

### v3
```javascript
module.exports = {
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
}
```

## Content/Source Detection

### v4 (Automatic + @source)

v4 auto-detects most content. Use `@source` for:
- Monorepo packages
- External component libraries
- Non-standard paths

```css
@import "tailwindcss";
@source "../packages/ui/src";
@source "../../node_modules/@company/ui/dist";
```

### v3 (Manual)
```javascript
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    '../../packages/ui/src/**/*.{js,ts,jsx,tsx}',
  ],
}
```

## Vite Integration

### v4
```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

### v3
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  css: { postcss: './postcss.config.js' }
})
```

## Next.js Integration

### v4
```javascript
// postcss.config.mjs
export default {
  plugins: {
    '@tailwindcss/postcss': {}
  }
}
```

### v3
```javascript
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

## Common Migration Issues

### Issue: Classes not applying

**Cause:** Dynamic class construction
```typescript
// ❌ Gets purged
const className = `bg-${color}-500`

// ✅ Works
const colorMap = { red: 'bg-red-500', blue: 'bg-blue-500' }
const className = colorMap[color]
```

### Issue: PostCSS config not working

**v4 requires `.mjs` extension:**
```bash
mv postcss.config.js postcss.config.mjs
```

### Issue: Styles not loading in monorepo

**Add @source directives:**
```css
@import "tailwindcss";
@source "../packages/**/src";
```

### Issue: Dark mode not working in v4

**Add custom variant:**
```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));
```

### Issue: Renamed utilities not working

**Run migration script:**
```bash
python3 scripts/migrate-tailwind.py ./src
```

## CSS Variables Bridge

Use CSS variables to share values between v3 and v4:

```css
:root {
  --brand-color: #3b82f6;
}
```

**v4:**
```css
@theme {
  --color-brand: var(--brand-color);
}
```

**v3:**
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: 'var(--brand-color)',
      },
    },
  },
}
```
