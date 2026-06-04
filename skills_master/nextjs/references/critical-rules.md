# Critical Rules - Next.js 15/16

Essential breaking changes and patterns. **Read before starting any Next.js work.**

---

## 1. Async Request APIs (Breaking Change)

All request-time APIs are async in Next.js 15+:

| API | New Signature |
|-----|---------------|
| `params` | `Promise<{ key: string }>` |
| `searchParams` | `Promise<{ key?: string }>` |
| `cookies()` | `await cookies()` |
| `headers()` | `await headers()` |
| `draftMode()` | `await draftMode()` |

### Server Components

```typescript
// ✅ CORRECT
export default async function Page({ 
  params,
  searchParams 
}: { 
  params: Promise<{ id: string }>
  searchParams: Promise<{ query?: string }>
}) {
  const { id } = await params
  const { query } = await searchParams
  const cookieStore = await cookies()
  
  return <div>{id}</div>
}
```

### Client Components

```typescript
'use client'
import { use } from 'react'

export default function ClientPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)  // use() instead of await
  return <div>{id}</div>
}
```

---

## 2. 'use client' Directive

### When Required

Add `'use client'` as **FIRST line** (before imports) when using:

- State: `useState`, `useReducer`
- Effects: `useEffect`, `useLayoutEffect`
- Events: `onClick`, `onChange`, `onSubmit`
- Browser: `window`, `document`, `localStorage`
- Context: `useContext`
- Third-party hooks

### Required Files

```typescript
// app/error.tsx - MUST have 'use client'
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

```typescript
// app/global-error.tsx - MUST have 'use client'
'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <h2>Something went wrong!</h2>
        <button onClick={() => reset()}>Try again</button>
      </body>
    </html>
  )
}
```

### Best Practice: Leaf Components

```typescript
// ❌ WRONG - Entire page is client
'use client'
export default function Page() {
  const [count, setCount] = useState(0)
  return <div>...</div>
}

// ✅ CORRECT - Only interactive parts are client
// page.tsx (Server Component)
export default async function Page() {
  const data = await getData()
  return (
    <div>
      <StaticContent data={data} />
      <Counter />  {/* Only this is 'use client' */}
    </div>
  )
}
```

---

## 3. Server/Client Boundary

### What CAN Be Passed (Server → Client)

✅ Primitives: strings, numbers, booleans, null  
✅ Plain objects (JSON-serializable)  
✅ Arrays, Date, Map, Set  
✅ Promises, JSX/React elements

### What CANNOT Be Passed

❌ Functions  
❌ Class instances  
❌ Symbols  
❌ Circular references

### Pattern: Server Components as Children

```typescript
// ClientWrapper.tsx
'use client'
export function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return <div onClick={() => setOpen(!open)}>{children}</div>
}

// page.tsx (Server Component)
export default function Page() {
  return (
    <ClientWrapper>
      <ServerContent />  {/* ✅ Server component passed as children */}
    </ClientWrapper>
  )
}
```

---

## 4. Hydration Error Prevention

### Browser APIs - Use useEffect

```typescript
'use client'
function Component() {
  const [width, setWidth] = useState(0)
  
  useEffect(() => {
    setWidth(window.innerWidth)
  }, [])
  
  return <div>Width: {width}</div>
}
```

### Date/Time - Suppress or Client-Only

```typescript
<time dateTime={date.toISOString()} suppressHydrationWarning>
  {date.toLocaleDateString()}
</time>
```

### Stable IDs

```typescript
import { useId } from 'react'

function Form() {
  const id = useId()  // Stable across server/client
  return <input id={`${id}-email`} />
}
```

### Invalid HTML Nesting (Causes Hydration Failures)

```typescript
// ❌ WRONG
<p><div>...</div></p>
<a><a>...</a></a>
<button><button>...</button></button>
```

---

## 5. Common Anti-Patterns

### Don't Call Route Handlers from Server Components

```typescript
// ❌ WRONG - Unnecessary network hop
export default async function Page() {
  const res = await fetch('http://localhost:3000/api/data')
  const data = await res.json()
}

// ✅ CORRECT - Call function directly
import { getData } from '@/lib/data'

export default async function Page() {
  const data = await getData()
}
```

### Don't Use redirect() Inside try/catch

```typescript
// ❌ WRONG - redirect throws NEXT_REDIRECT
try {
  await saveData()
  redirect('/success')  // Gets caught!
} catch (e) { }

// ✅ CORRECT
let success = false
try {
  await saveData()
  success = true
} catch (e) { }
if (success) redirect('/success')
```

### Don't Import from next/router

```typescript
// ❌ WRONG - Pages Router
import { useRouter } from 'next/router'

// ✅ CORRECT - App Router
import { useRouter, usePathname, useSearchParams } from 'next/navigation'
```

---

## 6. Fetch and Caching (Next.js 15+)

### Default: No Caching

```typescript
// Explicitly cache if needed
const data = await fetch(url, { cache: 'force-cache' })

// ISR with revalidation
const data = await fetch(url, { next: { revalidate: 3600 } })

// No cache (default)
const data = await fetch(url, { cache: 'no-store' })
```

### Route Segment Config

```typescript
// Force dynamic
export const dynamic = 'force-dynamic'

// Force static
export const dynamic = 'force-static'

// Revalidate every hour
export const revalidate = 3600
```

---

## 7. File Conventions

| File | Purpose | 'use client'? |
|------|---------|---------------|
| `page.tsx` | Route UI | No (Server) |
| `layout.tsx` | Shared wrapper | No |
| `loading.tsx` | Suspense fallback | No |
| `error.tsx` | Error boundary | **YES** |
| `not-found.tsx` | 404 UI | No |
| `global-error.tsx` | Root error | **YES** |
| `route.ts` | API endpoint | N/A |

---

## 8. Required Configuration

| File | Requirement | Why |
|------|-------------|-----|
| `postcss.config.mjs` | Extension must be `.mjs` | Tailwind v4 ESM |
| `tsconfig.json` | `moduleResolution: "bundler"` | App Router imports |
| `globals.css` | `@import "tailwindcss"` | Tailwind v4 syntax |
| `layout.tsx` | Import `globals.css` | CSS loading |

**See `references/config-templates.md` for copy-paste configs.**
