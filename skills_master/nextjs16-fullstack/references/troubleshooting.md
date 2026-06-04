# Troubleshooting Guide

Common issues and solutions for Next.js 16 full-stack development.

## Dead UI (No Styling/Interactivity)

Pages render as raw text without CSS or JavaScript functionality.

### Diagnostic Steps

```bash
# 1. Clear build cache
rm -rf .next node_modules/.cache
npm run dev

# 2. Check for build errors
npm run build 2>&1 | head -50

# 3. Verify Tailwind processing
grep -r "@import" src/app/globals.css
```

### Common Causes

#### Missing globals.css import

```typescript
// src/app/layout.tsx
import './globals.css'  // ← Must be present
```

#### Wrong PostCSS config extension

```bash
# ❌ postcss.config.js (won't work with Tailwind v4)
# ✅ postcss.config.mjs (required)
```

#### Invalid Tailwind import

```css
/* ❌ OLD (won't work in v4) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ✅ NEW */
@import "tailwindcss";
```

#### Dynamic class names getting purged

```typescript
// ❌ Gets purged - dynamic string
const className = `bg-${color}-500`

// ✅ Works - complete static strings
const colorMap = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
}
const className = colorMap[color]
```

## Hydration Errors

"Error: Hydration failed because the initial UI does not match what was rendered on the server"

### Browser APIs

```typescript
// ❌ Direct access causes mismatch
function Component() {
  const width = window.innerWidth  // Different on server vs client
}

// ✅ Defer to client with useEffect
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

### Date/Time Rendering

```typescript
// ❌ Different timezone on server vs client
<span>{new Date().toLocaleString()}</span>

// ✅ Use suppressHydrationWarning
<time 
  dateTime={date.toISOString()} 
  suppressHydrationWarning
>
  {date.toLocaleDateString()}
</time>

// ✅ Or defer to client
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return null
```

### Random Values

```typescript
// ❌ Different on server vs client
const id = Math.random().toString(36)

// ✅ Use React's useId hook
import { useId } from 'react'
const id = useId()
```

### Invalid HTML Nesting

```typescript
// ❌ Causes hydration failure
<p><div>Content</div></p>  // div inside p
<a href="/a"><a href="/b">Link</a></a>  // nested anchors
<button><button>Click</button></button>  // nested buttons

// ✅ Valid nesting
<div><p>Content</p></div>
<div><a href="/a">Link A</a><a href="/b">Link B</a></div>
```

## Zustand v5 Infinite Loops

"Maximum update depth exceeded" error.

### Cause: Unstable Selectors

```typescript
// ❌ Creates new object reference each render
const { name, age } = useStore((state) => ({ 
  name: state.name, 
  age: state.age 
}))
// Component re-renders → new object → re-render → loop

// ✅ Use useShallow for objects/arrays
import { useShallow } from 'zustand/shallow'

const { name, age } = useStore(
  useShallow((state) => ({ 
    name: state.name, 
    age: state.age 
  }))
)

// ✅ Or use individual selectors
const name = useStore((state) => state.name)
const age = useStore((state) => state.age)
```

### Cause: Store Updates in Render

```typescript
// ❌ Updates during render
function Component() {
  const count = useStore((s) => s.count)
  useStore.setState({ lastViewed: Date.now() })  // ← Causes loop
}

// ✅ Update in useEffect
function Component() {
  const count = useStore((s) => s.count)
  
  useEffect(() => {
    useStore.setState({ lastViewed: Date.now() })
  }, [])
}
```

## TanStack Query Stale Data

Data not updating after mutations.

### Solution: Invalidate Queries

```typescript
const queryClient = useQueryClient()

const mutation = useMutation({
  mutationFn: updateUser,
  onSuccess: () => {
    // Invalidate and refetch
    queryClient.invalidateQueries({ queryKey: ['users'] })
  },
})

// For optimistic updates:
const mutation = useMutation({
  mutationFn: updateUser,
  onMutate: async (newUser) => {
    await queryClient.cancelQueries({ queryKey: ['users'] })
    const previous = queryClient.getQueryData(['users'])
    queryClient.setQueryData(['users'], (old) => [...old, newUser])
    return { previous }
  },
  onError: (err, newUser, context) => {
    queryClient.setQueryData(['users'], context.previous)
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['users'] })
  },
})
```

## RSC Security Errors

"React Server Components protocol error"

### Solution: Update Next.js

```bash
# Check current version
npm list next

# Upgrade to patched version
npm install next@16.0.10

# Or use fix tool
npx fix-react2shell-next
```

## Module Not Found Errors

### Missing Path Aliases

```json
// tsconfig.json - ensure paths are configured
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Incorrect Import

```typescript
// ❌ next/router is for Pages Router
import { useRouter } from 'next/router'

// ✅ next/navigation is for App Router
import { useRouter, usePathname, useSearchParams } from 'next/navigation'
```

## Build Failures

### "params is not awaited"

```typescript
// ❌ OLD
export default function Page({ params }: { params: { id: string } }) {
  const { id } = params
}

// ✅ NEW
export default async function Page({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
}
```

### "Cannot use 'use client' with async function"

```typescript
// ❌ Can't mix
'use client'
export default async function Page() {}

// ✅ Split into Server + Client components
// page.tsx (Server)
export default async function Page() {
  const data = await getData()
  return <ClientComponent data={data} />
}

// ClientComponent.tsx
'use client'
export function ClientComponent({ data }) {
  const [state, setState] = useState(null)
  // Client-side logic
}
```

### "redirect() inside try/catch"

```typescript
// ❌ redirect throws, gets caught
try {
  await saveData()
  redirect('/success')  // ← Throws NEXT_REDIRECT
} catch (e) {
  // Catches the redirect!
}

// ✅ Redirect outside try/catch
let success = false
try {
  await saveData()
  success = true
} catch (e) {
  console.error(e)
}
if (success) redirect('/success')
```

## TypeScript Errors

### "Type 'Promise<...>' is not assignable"

Usually means you're not awaiting async APIs:

```typescript
// ❌ Missing await
const cookieStore = cookies()  // Returns Promise now

// ✅ Await the result
const cookieStore = await cookies()
```

### Missing Type Definitions

```bash
# Install type packages
npm install -D @types/react@19 @types/react-dom@19 @types/node
```

### Strict Mode Errors

```json
// tsconfig.json - if too strict, disable temporarily
{
  "compilerOptions": {
    "strict": true,
    // Or disable individual checks:
    "noImplicitAny": false,
    "strictNullChecks": false
  }
}
```

## Performance Issues

### Large Bundle Size

```bash
# Analyze bundle
ANALYZE=true npm run build

# Common culprits:
# - Importing entire libraries: import * as _ from 'lodash'
# - Missing dynamic imports for heavy components
# - Dev dependencies in production
```

### Slow Initial Load

```typescript
// Dynamic import heavy components
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(
  () => import('@/components/HeavyChart'),
  { 
    loading: () => <div>Loading chart...</div>,
    ssr: false  // Skip SSR if not needed
  }
)
```

### Slow API Routes

```typescript
// Add caching headers
export async function GET() {
  const data = await getData()
  
  return Response.json(data, {
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300',
    },
  })
}
```

## Quick Diagnostic Commands

```bash
# Check for issues
npm run lint
npm run build

# Clear all caches
rm -rf .next node_modules/.cache
npm run dev

# Check installed versions
npm list next react tailwindcss zustand @tanstack/react-query

# Verify TypeScript
npx tsc --noEmit

# Check for outdated packages
npm outdated
```
