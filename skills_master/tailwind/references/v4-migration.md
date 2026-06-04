# Tailwind CSS v3 to v4 Migration Guide

Complete migration guide from Tailwind v3 to v4, including CSS-first configuration, new features, and compatibility strategies.

## Overview: What Changed

| Feature | v3 | v4 |
|---------|----|----|
| **Engine** | JavaScript PostCSS | Rust (Oxide) |
| **Config** | JavaScript file | CSS-first with @theme |
| **Imports** | @tailwind directives | @import "tailwindcss" |
| **Content** | Manual content array | Auto-detected |
| **Variables** | Limited | Full CSS custom properties |
| **Build speed** | Baseline | 5-100x faster |
| **Container queries** | Via plugins | Native @container |
| **Defaults** | Borders gray-200 | currentColor |

## Phase 1: Pre-Migration Checklist

### Verify Compatibility

```bash
# Check Node version
node --version  # Requires 18+

# Update npm
npm install -g npm@latest

# Backup current tailwind.config
cp tailwind.config.js tailwind.config.js.backup
```

### Document Current Config

Extract from `tailwind.config.js`:

```bash
cat tailwind.config.js | grep -E "(colors:|spacing:|fontSize:|theme:)" > config-backup.txt
```

### List Installed Plugins

```bash
cat package.json | grep "tailwind\|@tailwind"
```

Note plugins that may need updates (check npm for v4 compatibility).

## Phase 2: Upgrade Installation

### Update Dependencies

```bash
# Upgrade Tailwind
npm install tailwindcss@latest

# Upgrade Autoprefixer and PostCSS
npm install -D postcss@latest autoprefixer@latest
```

### Run Official Upgrade Tool (Recommended)

```bash
npx @tailwindcss/upgrade
```

This tool:
- Converts `tailwind.config.js` → CSS `@theme` directives
- Updates `@tailwind` imports to `@import "tailwindcss"`
- Migrates content paths
- Preserves theme customizations

Manual approach if tool doesn't work for your setup follows below.

## Phase 3: Manual Configuration Migration

### CSS-First Setup

Replace `tailwind.config.js`:

**Before (v3):**

```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: "#0f172a",
        accent: "#3b82f6",
      },
      spacing: {
        "128": "32rem",
      },
    },
  },
  plugins: [],
};
```

**After (v4):**

```css
/* input.css */
@import "tailwindcss";

@theme {
  --color-brand: #0f172a;
  --color-accent: #3b82f6;
  --spacing-128: 32rem;
  --font-display: "Inter", sans-serif;
}

@layer components {
  .btn-primary {
    @apply px-4 py-2 rounded-lg font-semibold transition-colors;
    @apply bg-brand text-white hover:opacity-90;
  }
}
```

### Update PostCSS Config

**Before (v3):**

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

**After (v4):** Can be removed (Tailwind v4 handles it):

```javascript
module.exports = {};
```

Or explicitly:

```javascript
module.exports = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

### Migrate CSS Entry Point

**Before (v3):**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .card {
    @apply p-4 rounded-lg shadow-md;
  }
}
```

**After (v4):**

```css
@import "tailwindcss";

@layer components {
  .card {
    @apply p-4 rounded-lg shadow-md;
  }
}
```

The `@import "tailwindcss"` automatically includes base, components, and utilities.

## Phase 4: Content Path Updates

### Auto-Detection (v4 Default)

v4 automatically scans your project for class usage. Usually works out-of-the-box:

```bash
npm run build  # Should work without changes
```

### Manual Content Paths (If Needed)

If auto-detection misses files, add to `input.css`:

```css
@import "tailwindcss";

@layer components {
  /* ... */
}

/* Optionally: hint content paths via comment */
/* @content "./src/**/*.{js,ts,jsx,tsx}" */
```

Or use environment variable:

```bash
TAILWIND_CONTENT="./src/**/*.{js,ts,jsx,tsx}" npm run build
```

## Phase 5: Feature Migrations

### 1. CSS Variables (Now Native)

**v3:**

```javascript
// tailwind.config.js
theme: {
  colors: {
    primary: "#3b82f6",
  }
}

// Usage in CSS only
.btn { color: theme("colors.primary"); }
```

**v4:** Use CSS custom properties anywhere:

```css
@theme {
  --color-primary: #3b82f6;
}

/* In CSS */
.btn {
  color: var(--color-primary);
}

/* In component JS */
<div style={{ color: getComputedStyle(document.documentElement).getPropertyValue('--color-primary') }}
```

### 2. Container Queries (Now Native)

**v3:** Requires plugin

```javascript
module.exports = {
  plugins: [require("@tailwindcss/container-queries")],
};
```

**v4:** Built-in, no plugin needed

```css
@import "tailwindcss";
```

Usage:

```html
<div class="@container">
  <div class="@sm:grid-cols-2 @lg:grid-cols-3">
    Responsive to parent size
  </div>
</div>
```

### 3. Modern CSS Features

**v4 now supports:**

```css
@import "tailwindcss";

.card {
  @apply p-4 rounded-lg;
  background: color-mix(in srgb, var(--color-primary) 50%, white);
  /* or */
  background: oklch(from var(--color-primary) l c h);
}

.gradient {
  background: linear-gradient(45deg, var(--color-primary), var(--color-accent));
}
```

### 4. Dark Mode

**v3:**

```javascript
module.exports = {
  darkMode: "class",  // or "media"
};
```

**v4:** Configure in CSS:

```css
@import "tailwindcss";

@theme {
  --default-color-scheme: light;
  /* Optionally force dark mode */
}
```

Usage (same):

```html
<html class="dark">
  <div class="bg-white dark:bg-gray-900">Content</div>
</html>
```

### 5. Custom Fonts

**v3:**

```javascript
module.exports = {
  theme: {
    fontFamily: {
      display: ["Inter", "sans-serif"],
    },
  },
};
```

**v4:**

```css
@import "tailwindcss";

@theme {
  --font-display: "Inter", sans-serif;
}

/* Usage */
.heading {
  @apply font-display;
}
```

## Phase 6: Default Value Changes

Review default changes that might affect styling:

### Border Color

**v3:** `border-gray-200` (light gray)

**v4:** `currentColor` (inherits text color)

Migrate:

```html
<!-- v3 -->
<button class="border border-gray-200">Click</button>

<!-- v4 -->
<button class="border border-gray-200">Click</button>  <!-- Explicit if needed -->
```

### Ring Width

**v3:** `ring-2` (default 2px)

**v4:** `ring-1` (1px, lighter default)

Update if you relied on 2px:

```html
<!-- Explicit to maintain v3 behavior -->
<input class="ring-2 ring-blue-500" />
```

### Color Palette

v4 introduces refined color scales. Test visual regression.

## Phase 7: Testing and Validation

### 1. Build Test

```bash
npm run build
```

Check build succeeds and CSS size is similar or smaller.

### 2. Visual Regression

Spot-check key pages:

```bash
# Compare output
diff <(v3-build.css) <(v4-build.css)
```

### 3. Run Full Test Suite

```bash
npm test
npm run typecheck  # TypeScript
npm run lint       # ESLint/Biome
```

### 4. Browser Testing

Test in:

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Phase 8: Cleanup

### Remove Old Config

```bash
# Remove v3 config
rm -f tailwind.config.js tailwind.config.cjs

# Keep PostCSS only if needed for other plugins
```

### Update package.json Scripts

**Before:**

```json
{
  "scripts": {
    "build": "tailwindcss -i ./src/input.css -o ./src/output.css",
    "watch": "tailwindcss -i ./src/input.css -o ./src/output.css --watch"
  }
}
```

**After (usually unchanged):**

```json
{
  "scripts": {
    "build": "tailwindcss -i ./src/input.css -o ./src/output.css",
    "watch": "tailwindcss -i ./src/input.css -o ./src/output.css --watch"
  }
}
```

## Phase 9: Migration Troubleshooting

### Issue: Classes Not Being Detected

**Symptom:** Utilities missing from output CSS.

**Fix:** Check `input.css` content paths or auto-detection:

```bash
# Force content scan
TAILWIND_DEBUG=1 npm run build
```

### Issue: Styling Breaks After Upgrade

**Symptom:** Colors/spacing look different.

**Cause:** Default value changes (border color, ring width).

**Fix:** Explicitly set v3 defaults:

```css
@import "tailwindcss";

@theme {
  --default-border-color: #e5e7eb;  /* v3 default */
  --spacing-ring-width: 2px;         /* v3 default */
}
```

### Issue: Plugin Not Compatible

**Symptom:** v3 plugin doesn't work in v4.

**Fix:**
1. Check npm/GitHub for v4 version
2. Or recreate as CSS utility:

```css
@import "tailwindcss";

@layer utilities {
  .custom-feature {
    /* Custom CSS */
  }
}
```

### Issue: Build Slower or Memory Issues

**Symptom:** v4 build is slow despite being faster.

**Cause:** Large content paths or many files.

**Fix:** Optimize content:

```css
@import "tailwindcss";

/* Narrow down content scan */
@layer utilities {
  /* ... */
}
```

## Coexistence (v3 + v4 for Monorepos)

If some packages still need v3:

```json
{
  "dependencies": {
    "tailwindcss": "^4.0.0"  // v4
  },
  "devDependencies": {
    "tailwindcss-legacy": "npm:tailwindcss@3"  // v3 alias
  }
}
```

Use in respective packages:

```bash
# Package A (v4)
npm run build:a

# Package B (v3)
npm run build:b  # Uses tailwindcss-legacy
```

## Rollback Plan

If issues arise:

```bash
npm install tailwindcss@3
git checkout tailwind.config.js
npm run build
```

## Validation Checklist

- [ ] Build completes successfully
- [ ] CSS file size is similar or smaller
- [ ] All pages render correctly
- [ ] Tests pass (unit, visual, integration)
- [ ] Dark mode works (if used)
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] Custom fonts/colors load
- [ ] No browser console errors
- [ ] TypeScript types work (if using)
- [ ] CI/CD pipeline passes

## References

- Tailwind v4 docs: https://tailwindcss.com/docs/v4-release-notes
- Upgrade guide: https://tailwindcss.com/blog/tailwindcss-v4
- CSS-first config: https://tailwindcss.com/docs/configuration
- Community migration issues: GitHub Tailwind CSS discussions
