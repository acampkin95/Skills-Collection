---
name: tailwind
description: "Writes, configures and migrates Tailwind CSS v4 utility-first styling: PostCSS and CSS-first setup with @import and @theme, responsive and dark-mode variants, common layout and form patterns, and upgrading v3 projects to v4 (ring, important modifier, opacity and config changes). Use when adding Tailwind to a project, styling components with utility classes, configuring theme tokens, enabling dark mode, or migrating a Tailwind v3 project to v4."
version: "1.0.0"
reviewed: "2026-10-12"
---

# Tailwind CSS v4 - Utility-First CSS Framework

Tailwind CSS v4 with the Oxide (Rust) engine, CSS-first configuration, automatic content detection, and native CSS variable theme support.

## Installation

Tailwind CSS v4 ships its PostCSS plugin as a separate package. Checked against https://tailwindcss.com/docs/installation/using-postcss on 2026-10-12.

```bash
npm install tailwindcss @tailwindcss/postcss postcss
```

```javascript
// postcss.config.mjs
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
```

Do not add `autoprefixer` or `postcss-import` (v4 handles both), and do not run `npx tailwindcss init -p`, which is the v3 setup.

---

## Configuration

Tailwind v4 is CSS-first: theme tokens are declared in CSS with `@theme`, and sources are detected automatically, so there is no `content` array.

### CSS Setup

```css
/* app/globals.css (or src/index.css) */
@import "tailwindcss";

@theme {
  --color-brand: #0f172a;
}

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700;
  }
}
```

Replace the v3 `@tailwind base;`, `@tailwind components;` and `@tailwind utilities;` lines with the single `@import "tailwindcss";` line.

---

## Core Utility Classes

### Display & Layout

| Class | Effect |
|-------|--------|
| `flex` | `display: flex` |
| `grid` | `display: grid` |
| `grid-cols-3` | `grid-template-columns: repeat(3, minmax(0, 1fr))` |
| `flex-col` | `flex-direction: column` |
| `gap-4` | `gap: 1rem` |
| `justify-center` | `justify-content: center` |
| `items-center` | `align-items: center` |

### Spacing (Padding, Margin)

```html
<!-- Padding -->
<div class="p-4"><!-- 1rem padding all sides --></div>
<div class="px-8"><!-- Horizontal padding --></div>
<div class="pt-2"><!-- Padding-top --></div>

<!-- Margin -->
<div class="m-4"><!-- 1rem margin --></div>
<div class="mx-auto"><!-- Horizontal centering --></div>
<div class="mb-8"><!-- Margin-bottom --></div>
```

### Typography

```html
<h1 class="text-4xl font-bold text-gray-900">Heading</h1>
<p class="text-base text-gray-600 leading-relaxed">Paragraph</p>
<span class="text-sm font-semibold text-blue-600">Label</span>
```

### Colors & Backgrounds

```html
<div class="bg-blue-500 text-white">Blue background</div>
<button class="bg-gradient-to-r from-purple-500 to-pink-500">Gradient</button>
<div class="border-2 border-gray-300">Border</div>
```

### Sizing

```html
<div class="w-full h-screen">Full screen</div>
<div class="w-64 h-64">Fixed size</div>
<div class="max-w-2xl mx-auto">Max width container</div>
```

---

## Responsive Design

### Breakpoints

| Prefix | Breakpoint | Media Query |
|--------|-----------|-------------|
| `sm` | 640px | `@media (min-width: 640px)` |
| `md` | 768px | `@media (min-width: 768px)` |
| `lg` | 1024px | `@media (min-width: 1024px)` |
| `xl` | 1280px | `@media (min-width: 1280px)` |
| `2xl` | 1536px | `@media (min-width: 1536px)` |

### Mobile-First Responsive Design

```html
<!-- Default: single column on mobile -->
<!-- Medium screens and up: 2 columns -->
<!-- Large screens and up: 3 columns -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>
```

### Responsive Text

```html
<h1 class="text-2xl md:text-4xl lg:text-6xl font-bold">
  Responsive Heading
</h1>
```

---

## Dark Mode

### Setup

Class-based dark mode in v4 is declared in CSS (the v3 `darkMode` config key is gone). Exact selector not re-checked against the dark-mode docs in this pass; confirm before use.

```css
/* app/globals.css */
@custom-variant dark (&:where(.dark, .dark *));
```

### Usage

```html
<!-- Light mode: white background, dark text -->
<!-- Dark mode: dark background, light text -->
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Content
</div>

<button class="bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600">
  Button
</button>
```

### Toggle Dark Mode

```typescript
function DarkModeToggle() {
  const toggleDarkMode = () => {
    document.documentElement.classList.toggle('dark');
  };

  return (
    <button onClick={toggleDarkMode}>
      Toggle Dark Mode
    </button>
  );
}
```

---

## Advanced Patterns

### Custom Components

```css
@layer components {
  .card {
    @apply rounded-lg shadow-md p-6 bg-white;
  }

  .card-title {
    @apply text-xl font-bold text-gray-900 mb-4;
  }

  .btn {
    @apply px-4 py-2 rounded-md font-semibold transition-colors;
  }

  .btn-primary {
    @apply btn bg-blue-600 text-white hover:bg-blue-700;
  }
}
```

### State Variants

```html
<!-- Hover -->
<button class="bg-blue-600 hover:bg-blue-700">Hover</button>

<!-- Focus -->
<input class="border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />

<!-- Active -->
<div class="bg-gray-100 active:bg-gray-200">Active</div>

<!-- Group hover -->
<div class="group">
  <div class="bg-gray-100 group-hover:bg-blue-100">
    Hovered when parent is hovered
  </div>
</div>
```

### Pseudo-Elements

```html
<div class="before:content-['→'] before:mr-2">Before content</div>
<div class="after:content-['*'] after:ml-1 after:text-red-500">Required field</div>
```

---

## Common Patterns

### Centered Container

```html
<div class="max-w-6xl mx-auto px-4">Content</div>
```

### Flex Center

```html
<div class="flex items-center justify-center h-screen">Centered</div>
```

### Card Layout

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div class="rounded-lg shadow-md p-6 bg-white hover:shadow-lg transition-shadow">
    <h3 class="text-lg font-bold mb-2">Card Title</h3>
    <p class="text-gray-600">Card content</p>
  </div>
</div>
```

### Form

```html
<form class="space-y-4">
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1">
      Email
    </label>
    <input class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500" />
  </div>
  <button class="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700">
    Submit
  </button>
</form>
```

---

## v3 to v4 Migration

Checked against https://tailwindcss.com/docs/upgrade-guide on 2026-10-12.

### Breaking Changes

| Change | v3 | v4 |
|--------|----|----|
| Import | `@tailwind base;` / `components;` / `utilities;` | `@import "tailwindcss";` |
| PostCSS plugin | `tailwindcss` | `@tailwindcss/postcss`; remove `autoprefixer` and `postcss-import` |
| Configuration | `tailwind.config.js` with `content` and `theme.extend` | CSS-first `@theme`; sources detected automatically |
| `ring` with no width | 3px | 1px; use `ring-3` for 3px |
| Important modifier | `!flex` (prefix) | `flex!` (suffix); the prefix form is deprecated |
| Background opacity | `bg-opacity-50` | Color opacity modifier, e.g. `bg-black/50` |
| Shadow scale | `shadow-sm` | `shadow-xs` (scale shifted; check each use) |

### Migration Steps

1. Run the official upgrade tool, then review its changes against the upgrade guide.
2. Replace the `@tailwind` directives with `@import "tailwindcss";`.
3. Move the PostCSS plugin to `@tailwindcss/postcss` and remove `autoprefixer` and `postcss-import`.
4. Move `theme.extend` values into `@theme` in CSS, and remove the `content` array.
5. Replace bare `ring` with `ring-3` where a 3px ring is meant; replace `bg-opacity-*` with color opacity modifiers; move `!` to the end of the class.
6. Run a production build and check the pages visually.

---

## Performance

### Optimize Bundle Size

v4 scans the project for class names automatically, so there is no `content` array to trim. To add or exclude sources, use the v4 `@source` directive in CSS (not re-checked in this pass; see the docs).

### Purge Unused Styles

```bash
npm run build  # Production includes only used styles
```

---

## Resources

| Resource | Purpose |
|----------|---------|
| [Tailwind Docs](https://tailwindcss.com/docs) | Official documentation |
| [UI Components](https://tailwindui.com) | Tailwind UI component library |
| [Headless UI](https://headlessui.com) | Unstyled, accessible components |
| [Color Reference](https://tailwindcss.com/docs/customizing-colors) | Complete color palette |
