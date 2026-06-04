# Migration Guide

Upgrade paths for Next.js 15→16, Zustand v4→v5, Tailwind v3→v4, and React Query v4→v5.

## Next.js 15 → 16

### Automated Migration

```bash
npm install next@16.0.10 react@19 react-dom@19
npx @next/codemod@latest
npm run build
```

### Manual Changes Required

#### 1. Async Request APIs

All request APIs are now async and must be awaited:

```typescript
// ❌ OLD (Next.js 15)
export default function Page({ params }: { params: { id: string } }) {
  const { id } = params
  const cookieStore = cookies()
  const headersList = headers()
}

// ✅ NEW (Next.js 16)
export default async function Page({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
  const cookieStore = await cookies()
  const headersList = await headers()
}
```

#### 2. Client Components with Params

```typescript
// ❌ OLD
'use client'
export default function Page({ params }: { params: { id: string } }) {
  const { id } = params
}

// ✅ NEW - use React.use()
'use client'
import { use } from 'react'

export default function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
}
```

#### 3. Security Patch Required

```bash
# If on any 16.0.x version, upgrade to 16.0.10+
npm install next@16.0.10

# Or use the fix tool
npx fix-react2shell-next
```

## Zustand v4 → v5

### Breaking Changes

| v4 | v5 |
|----|-----|
| Default export | Named export only |
| Mutable selectors | Stable reference required |
| TypeScript 4.1+ | TypeScript 4.5+ |
| React 17+ | React 18+ |

### Import Changes

```typescript
// ❌ OLD (v4)
import create from 'zustand'

// ✅ NEW (v5)
import { create } from 'zustand'
```

### Selector Stability (Critical)

```typescript
// ❌ OLD (v4) - worked but inefficient
const useStore = create((set) => ({
  user: { name: 'John', age: 30 },
}))

// Getting object returned new reference each time
function Component() {
  const { name, age } = useStore((state) => ({ 
    name: state.user.name, 
    age: state.user.age 
  }))
}

// ✅ NEW (v5) - use useShallow
import { useShallow } from 'zustand/shallow'

function Component() {
  const { name, age } = useStore(
    useShallow((state) => ({ 
      name: state.user.name, 
      age: state.user.age 
    }))
  )
}

// ✅ ALSO VALID (v5) - individual selectors
function Component() {
  const name = useStore((state) => state.user.name)
  const age = useStore((state) => state.user.age)
}
```

### Persist Middleware

```typescript
// ❌ OLD (v4) - auto-persisted on creation
const useStore = create(
  persist(
    (set) => ({ count: 0 }),
    { name: 'my-store' }
  )
)

// ✅ NEW (v5) - same API but check version migrations
const useStore = create(
  persist(
    (set) => ({ count: 0 }),
    { 
      name: 'my-store',
      version: 1, // Add version for migrations
      migrate: (state, version) => {
        if (version === 0) {
          // Migration from v0 to v1
          return { ...state, newField: 'default' }
        }
        return state
      }
    }
  )
)
```

## Tailwind CSS v3 → v4

### Automated Migration

```bash
npm install -D tailwindcss@4.1.18 @tailwindcss/postcss@4.1.18
npm install -D @tailwindcss/upgrade
npx @tailwindcss/upgrade
```

### PostCSS Configuration

```javascript
// ❌ OLD postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

// ✅ NEW postcss.config.mjs (MUST be .mjs)
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

### CSS Import Syntax

```css
/* ❌ OLD (v3) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ✅ NEW (v4) */
@import "tailwindcss";
```

### Configuration Location

```typescript
// ❌ OLD tailwind.config.js - JavaScript config
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: '#3b82f6',
      },
    },
  },
}

// ✅ NEW globals.css - CSS-first config
@import "tailwindcss";

@theme {
  --color-brand: #3b82f6;
}
```

### Utility Renames

| v3 Class | v4 Class |
|----------|----------|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `shadow-md` | `shadow` |
| `blur-sm` | `blur-xs` |
| `blur` | `blur-sm` |
| `rounded-sm` | `rounded-xs` |
| `rounded` | `rounded-sm` |
| `outline-none` | `outline-hidden` |
| `ring` | `ring-3` |

### Content Detection

```css
/* v4 auto-detects content from .gitignore */
/* For monorepos, add explicit sources: */

@import "tailwindcss";
@source "../packages/ui";
@source "../shared/components";
```

## TanStack Query v4 → v5

### Package Rename

```bash
# ❌ OLD
npm uninstall react-query
# ✅ NEW
npm install @tanstack/react-query@5
```

### API Changes

```typescript
// ❌ OLD (v4)
import { useQuery } from 'react-query'

const { isLoading, data } = useQuery(['users'], fetchUsers)

// ✅ NEW (v5)
import { useQuery } from '@tanstack/react-query'

const { isPending, data } = useQuery({
  queryKey: ['users'],
  queryFn: fetchUsers,
})
```

### Property Renames

| v4 | v5 |
|----|-----|
| `isLoading` | `isPending` |
| `cacheTime` | `gcTime` |
| `useQueryErrorResetBoundary` | `useQueryErrorResetBoundary` (unchanged) |

### Query Key Format

```typescript
// ❌ OLD (v4) - array shorthand
useQuery(['users', userId], () => fetchUser(userId))

// ✅ NEW (v5) - object format required
useQuery({
  queryKey: ['users', userId],
  queryFn: () => fetchUser(userId),
})
```

### Callbacks Moved

```typescript
// ❌ OLD (v4) - callbacks in useQuery
const { data } = useQuery({
  queryKey: ['users'],
  queryFn: fetchUsers,
  onSuccess: (data) => console.log(data),
  onError: (error) => console.error(error),
})

// ✅ NEW (v5) - use query client defaults or mutation callbacks
// For queries, handle in the component:
const { data, error } = useQuery({
  queryKey: ['users'],
  queryFn: fetchUsers,
})

useEffect(() => {
  if (data) console.log(data)
  if (error) console.error(error)
}, [data, error])

// Callbacks still work in useMutation
const mutation = useMutation({
  mutationFn: createUser,
  onSuccess: (data) => console.log(data),
  onError: (error) => console.error(error),
})
```

### QueryClient Options

```typescript
// ❌ OLD (v4)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      cacheTime: 1000 * 60 * 5,
    },
  },
})

// ✅ NEW (v5)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      gcTime: 1000 * 60 * 5,
    },
  },
})
```

## Full Upgrade Script

```bash
#!/bin/bash
# upgrade-to-nextjs16.sh

set -e

echo "🚀 Upgrading to Next.js 16 full-stack..."

# Core framework
npm install next@16.0.10 react@19 react-dom@19
npm install -D typescript@5.7 @types/react@19 @types/react-dom@19

# Tailwind v4
npm install -D tailwindcss@4.1.18 @tailwindcss/postcss@4.1.18 postcss@8.4.47

# State management
npm install zustand@5 @tanstack/react-query@5

# Run codemods
npx @next/codemod@latest

# Update postcss config
cat > postcss.config.mjs << 'EOF'
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
EOF

# Clear cache
rm -rf .next node_modules/.cache

echo "✅ Upgrade complete. Run 'npm run build' to verify."
```
