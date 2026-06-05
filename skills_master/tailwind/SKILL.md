---
name: tailwind
description: "Use this skill when working with Tailwind, tailwind."
---

# Tailwind CSS v4 - Utility-First CSS Framework

Tailwind CSS v4 with Oxide (Rust) engine, CSS-first configuration, automatic content detection, and native CSS variable theme support. 5-100x faster than v3.

## Installation

### Standalone CLI

```bash
npm install -D tailwindcss
npx tailwindcss init -p
```

### PostCSS Integration

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Framework Integration

```bash
# Next.js
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Create React App
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Vite
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

## Configuration

### tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: '#0f172a',
      },
      spacing: {
        '128': '32rem',
      },
    },
  },
  plugins: [],
};
```

### CSS Setup

```css
/* input.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700;
  }
}
```

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

```javascript
// tailwind.config.js
export default {
  darkMode: 'class', // or 'media'
  // ...
};
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

### Breaking Changes

| Change | v3 | v4 |
|--------|----|----|
| CSS API | `@apply` only | CSS variables, `theme()` |
| Config | JavaScript | JavaScript or CSS |
| Colors | Limited palette | Extended palette |
| Sizing | Predefined | Arbitrary values everywhere |

### Migration Steps

1. Update Tailwind:
   ```bash
   npm install tailwindcss@latest
   ```

2. Update config format (CSS option):
   ```css
   @import "tailwindcss";

   @theme {
     --color-primary: #3b82f6;
   }
   ```

3. Update utility variants
4. Run production build to test

---

## Performance

### Optimize Bundle Size

```javascript
// tailwind.config.js
export default {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    // Exclude unnecessary files
  ],
  // ...
};
```

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
