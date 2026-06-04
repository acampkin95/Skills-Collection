---
name: tailwind
description: Tailwind CSS v4 utility-first styling with CSS-first config, native variables, design tokens, container queries, and @theme directives.
version: 2.0.0
reviewed: "2026-06-04"
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


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.