# Troubleshooting Guide

Systematic debugging for Next.js 15/16. Work through sections in order for fastest resolution.

---

## Quick Diagnostic

Run this first to identify the issue category:

```bash
# Full diagnostic
npm run build 2>&1 | head -50        # Build errors
npx tsc --noEmit 2>&1 | head -50     # Type errors
npm run lint                          # Lint errors

# Dependency check
npm ls next react react-dom tailwindcss @tailwindcss/postcss

# Configuration check
ls -la next.config.* tsconfig.json postcss.config.* app/globals.css app/layout.tsx

# Clear caches
rm -rf .next node_modules/.cache
```

---

## Dead UI / White Screen / No Styling

Page renders as raw HTML without CSS or JavaScript.

### Diagnostic Flowchart

```
Page loads but no styling?
├─ Check browser console for errors
│  └─ CSS 404? → Check globals.css path
│  └─ JS error? → Check component errors
│
├─ Check postcss.config extension
│  └─ Is it .mjs? 
│     └─ No → Rename to postcss.config.mjs
│
├─ Check CSS import syntax
│  └─ Uses @tailwind? → Update to @import "tailwindcss"
│
├─ Check layout.tsx
│  └─ Missing globals.css import? → Add import './globals.css'
│
└─ Clear cache and rebuild
   └─ rm -rf .next && npm run dev
```

### Step-by-Step Fix

```bash
# Step 1: Check PostCSS config extension (MOST COMMON ISSUE)
ls postcss.config.*
# MUST be: postcss.config.mjs (NOT .js)

# Step 2: Check PostCSS content
cat postcss.config.mjs
# MUST contain: "@tailwindcss/postcss": {}

# Step 3: Check CSS import syntax
head -5 app/globals.css
# MUST be: @import "tailwindcss";
# NOT: @tailwind base; @tailwind components; @tailwind utilities;

# Step 4: Check layout imports CSS
grep "globals.css" app/layout.tsx
# MUST show: import './globals.css'

# Step 5: Clear and rebuild
rm -rf .next node_modules/.cache
npm run dev
```

### Quick Fixes

```bash
# Fix 1: Rename PostCSS config
mv postcss.config.js postcss.config.mjs

# Fix 2: Create correct PostCSS config
cat > postcss.config.mjs << 'EOF'
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
EOF

# Fix 3: Update globals.css for Tailwind v4
cat > app/globals.css << 'EOF'
@import "tailwindcss";
EOF

# Fix 4: Verify layout has CSS import
grep -q "globals.css" app/layout.tsx || echo "⚠️ Missing CSS import in layout.tsx"
```

---

## Hydration Errors

Console shows "Hydration failed" or "Text content does not match".

### Common Causes & Fixes

| Cause | Error Message | Fix |
|-------|--------------|-----|
| Browser API in render | "window is not defined" | Use `useEffect` |
| Different content | "Text content does not match" | Ensure server/client same |
| Invalid HTML nesting | "Expected server HTML" | Fix nesting |
| Date/time formatting | "Hydration mismatch" | Use `suppressHydrationWarning` |

### Debugging Steps

```bash
# Find browser API usage
grep -rn "window\." --include="*.tsx" app/ components/ src/ | grep -v "typeof window"
grep -rn "document\." --include="*.tsx" app/ components/ src/ | grep -v "typeof document"

# Find Date/random usage
grep -rn "new Date()" --include="*.tsx" app/ components/ src/
grep -rn "Math.random" --include="*.tsx" app/ components/ src/

# Find invalid HTML nesting
grep -rn "<p.*<div" --include="*.tsx" app/ components/ src/
grep -rn "<a.*<a" --include="*.tsx" app/ components/ src/
```

### Fix Patterns

```typescript
// ❌ WRONG - Causes hydration error
function Component() {
  const width = window.innerWidth  // Runs during render
  return <div>Width: {width}</div>
}

// ✅ CORRECT - Browser API in useEffect
'use client'
import { useState, useEffect } from 'react'

function Component() {
  const [width, setWidth] = useState(0)
  
  useEffect(() => {
    setWidth(window.innerWidth)
  }, [])
  
  return <div>Width: {width}</div>
}
```

```typescript
// ✅ CORRECT - Date with suppressHydrationWarning
<time dateTime={date.toISOString()} suppressHydrationWarning>
  {date.toLocaleDateString()}
</time>

// ✅ CORRECT - Client-only component
import dynamic from 'next/dynamic'

const ClientOnlyWidget = dynamic(() => import('./Widget'), { ssr: false })
```

### Browser Extension Issues

Some extensions inject content causing hydration mismatches:

1. Test in incognito/private mode
2. Disable extensions temporarily
3. Add `suppressHydrationWarning` to `<html>` if needed

---

## Build Failures

### Type Errors

```bash
# Run type check
npx tsc --noEmit

# Common fixes shown below
```

| Error | Cause | Fix |
|-------|-------|-----|
| `params` type error | Not typed as Promise | Add `Promise<>` wrapper |
| Hook in server component | Missing 'use client' | Add directive |
| Module not found | Wrong import path | Check path alias |

```typescript
// ❌ WRONG - Old params type
function Page({ params }: { params: { id: string } })

// ✅ CORRECT - New async params type
async function Page({ params }: { params: Promise<{ id: string }> })
```

### Module Resolution Errors

```bash
# Check tsconfig
grep -n "moduleResolution" tsconfig.json
# MUST be: "bundler"

# Check paths
grep -A5 '"paths"' tsconfig.json
```

```json
{
  "compilerOptions": {
    "moduleResolution": "bundler",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Dependency Conflicts

```bash
# Check for version mismatches
npm ls react react-dom
npm ls next

# Check for duplicate React
npm ls react | grep -E "^[├└]"

# Clean install
rm -rf node_modules package-lock.json
npm install
```

---

## params/searchParams Errors

### Server Components

```typescript
// ❌ WRONG
export default function Page({ params }: { params: { id: string } }) {
  const { id } = params  // Error!
}

// ✅ CORRECT
export default async function Page({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
  return <div>{id}</div>
}
```

### Client Components

```typescript
// ✅ CORRECT - Use React.use()
'use client'
import { use } from 'react'

export default function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <div>{id}</div>
}
```

---

## API Route Issues

### 404 Not Found

```bash
# Check file location
ls -la app/api/*/route.ts

# Verify structure
# app/api/users/route.ts → GET /api/users
# app/api/users/[id]/route.ts → GET /api/users/123
```

### 405 Method Not Allowed

```typescript
// MUST export named function matching HTTP method
export async function GET(request: Request) { ... }
export async function POST(request: Request) { ... }
export async function PUT(request: Request) { ... }
export async function DELETE(request: Request) { ... }
```

### Request Body Issues

```typescript
// ✅ CORRECT - Await JSON parsing
export async function POST(request: Request) {
  const body = await request.json()
  // ...
}
```

---

## Environment Variables

### Not Loading

```bash
# Check files exist at project root
ls -la .env*

# Check variable names
# Server-only: any name
# Client-side: MUST have NEXT_PUBLIC_ prefix

# Restart dev server (required after .env changes)
```

### Wrong Value

```typescript
// Check at runtime
console.log('DATABASE_URL:', process.env.DATABASE_URL ? '***set***' : 'NOT SET')
console.log('PUBLIC_URL:', process.env.NEXT_PUBLIC_API_URL)
```

### Precedence

```
.env                    # Base (lowest priority)
.env.local              # Local overrides
.env.development        # Dev mode only
.env.development.local  # Local dev overrides
.env.production         # Prod mode only
.env.production.local   # Local prod overrides (highest)
```

---

## Turbopack Issues

### Compatibility Problems

```bash
# Fall back to webpack
NEXT_TURBOPACK=0 npm run dev

# Or use script
# "dev:webpack": "next dev" (without --turbopack flag)
```

### Module Resolution

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  turbopack: {
    resolveAlias: {
      '@components': './src/components',
    },
  },
}
```

**See `references/turbopack-guide.md` for full details.**

---

## Performance Issues

### Slow Dev Server

```bash
# Check for heavy imports in client components
grep -A 20 "'use client'" app/**/*.tsx | grep "^import"

# Use dynamic imports for heavy components
```

```typescript
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <p>Loading...</p>,
  ssr: false
})
```

### Large Bundle Size

```bash
# Analyze bundle
ANALYZE=true npm run build
```

---

## Dependency Verification Script

```bash
#!/bin/bash
echo "=== Next.js Dependency Check ==="

echo -e "\n--- Core Packages ---"
npm ls next react react-dom typescript 2>/dev/null || echo "❌ Missing core packages"

echo -e "\n--- Tailwind v4 ---"
npm ls tailwindcss @tailwindcss/postcss 2>/dev/null || echo "❌ Missing Tailwind v4 packages"

echo -e "\n--- Potential Issues ---"
npm ls autoprefixer 2>/dev/null && echo "⚠️ autoprefixer not needed with Tailwind v4"
npm ls postcss-import 2>/dev/null && echo "⚠️ postcss-import not needed with Tailwind v4"

echo -e "\n--- Config Files ---"
[ -f "next.config.ts" ] || [ -f "next.config.mjs" ] || [ -f "next.config.js" ] && echo "✅ next.config exists" || echo "❌ Missing next.config"
[ -f "tsconfig.json" ] && echo "✅ tsconfig.json exists" || echo "❌ Missing tsconfig.json"
[ -f "postcss.config.mjs" ] && echo "✅ postcss.config.mjs exists" || echo "❌ Missing postcss.config.mjs (or wrong extension)"
[ -f "app/globals.css" ] || [ -f "src/app/globals.css" ] && echo "✅ globals.css exists" || echo "❌ Missing globals.css"

echo -e "\n--- CSS Syntax Check ---"
if grep -q "@tailwind" app/globals.css 2>/dev/null || grep -q "@tailwind" src/app/globals.css 2>/dev/null; then
    echo "❌ Using old @tailwind syntax - update to @import \"tailwindcss\""
else
    echo "✅ CSS syntax OK"
fi

echo -e "\n--- tsconfig Check ---"
if grep -q '"moduleResolution".*"bundler"' tsconfig.json 2>/dev/null; then
    echo "✅ moduleResolution is 'bundler'"
else
    echo "⚠️ moduleResolution should be 'bundler'"
fi
```

---

## Debug Logging

```typescript
// Server Component
export default async function Page({ params }: Props) {
  console.log('[Server] Params:', await params)
  const data = await getData()
  console.log('[Server] Data fetched:', !!data)
  return <div>...</div>
}

// Client Component
'use client'
export function ClientComponent() {
  useEffect(() => {
    console.log('[Client] Mounted')
    console.log('[Client] Window:', typeof window !== 'undefined')
  }, [])
  return <div>...</div>
}

// API Route
export async function GET(request: Request) {
  console.log('[API] Request URL:', request.url)
  // ...
}
```

Check:
- **Terminal** for server-side logs
- **Browser Console** for client-side logs

---

## Common Error Messages

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| "Hydration failed" | Server/client mismatch | Check for browser APIs in render |
| "Text content does not match" | Dynamic content | Use `suppressHydrationWarning` |
| "Cannot find module" | Wrong import path | Check path aliases |
| "params is not iterable" | Sync params access | Add `await` |
| "window is not defined" | Browser API on server | Use `useEffect` |
| "Module not found: @tailwindcss/postcss" | Missing dependency | `npm i @tailwindcss/postcss` |
| "error.tsx must be a Client Component" | Missing directive | Add `'use client'` |
