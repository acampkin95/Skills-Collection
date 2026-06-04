# Installation Guide

## Project Dependencies

```bash
# Core Next.js
npm install next@latest react@latest react-dom@latest

# TypeScript
npm install -D typescript @types/react @types/node

# Tailwind CSS v4
npm install tailwindcss @tailwindcss/postcss
```

## Configuration Files

### 1. postcss.config.mjs

**Must be `.mjs` extension**

```javascript
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

### 2. tsconfig.json

```json
{
  "compilerOptions": {
    "moduleResolution": "bundler",
    "isolatedModules": true
  },
  "include": [".next/types/**/*.ts", "**/*.ts", "**/*.tsx"]
}
```

### 3. app/globals.css

```css
@import "tailwindcss";
```

### 4. app/layout.tsx

```typescript
import './globals.css'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

## Verification

```bash
# Test build
npm run build

# Check for styling
npm run dev
# Open http://localhost:3000
```

## Troubleshooting

If styles don't appear:

1. Verify `postcss.config.mjs` extension (not `.js`)
2. Check `globals.css` uses `@import "tailwindcss"`
3. Ensure `layout.tsx` imports `globals.css`
4. Clear cache: `rm -rf .next && npm run dev`

See `references/troubleshooting.md` for detailed debugging.
