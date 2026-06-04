# Next.js Patterns Reference

## Version Detection

```bash
grep '"next":' package.json | sed 's/.*"\^*\([0-9]*\).*/\1/'
```

## Version Feature Matrix

| Feature | v13 | v14 | v15 |
|---------|-----|-----|-----|
| App Router | ✅ | ✅ | ✅ |
| Server Components | ✅ | ✅ | ✅ |
| Async params | ❌ | ❌ | **Required** |
| Async searchParams | ❌ | ❌ | **Required** |
| Async cookies() | ❌ | ❌ | **Required** |
| Async headers() | ❌ | ❌ | **Required** |
| Turbopack stable | ❌ | Partial | ✅ |
| PPR | ❌ | Experimental | ✅ |

## Next.js 15 Breaking Changes

### Async Request APIs

**All request-time APIs are now async:**

```typescript
// ✅ CORRECT - Next.js 15
export default async function Page({ 
  params,
  searchParams 
}: { 
  params: Promise<{ slug: string }>
  searchParams: Promise<{ q?: string }>
}) {
  const { slug } = await params
  const { q } = await searchParams
  const cookieStore = await cookies()
  const headersList = await headers()
  
  return <div>{slug} - {q}</div>
}

// ❌ WRONG - Will fail in v15
export default function Page({ params }: { params: { slug: string } }) {
  return <div>{params.slug}</div>
}
```

### Client Components with Async Props

```typescript
'use client'
import { use } from 'react'

export default function ClientPage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = use(params)  // React.use() unwraps promises
  return <div>{id}</div>
}
```

### searchParams in Client Components

```typescript
'use client'
import { useSearchParams } from 'next/navigation'

export function SearchInput() {
  const searchParams = useSearchParams()
  const q = searchParams.get('q')
  return <input defaultValue={q ?? ''} />
}
```

## File Conventions

| File | Purpose | 'use client' |
|------|---------|--------------|
| `page.tsx` | Route UI | No |
| `layout.tsx` | Shared wrapper | No |
| `loading.tsx` | Suspense fallback | No |
| `error.tsx` | Error boundary | **YES** |
| `not-found.tsx` | 404 UI | No |
| `global-error.tsx` | Root error | **YES** |
| `route.ts` | API handler | N/A |
| `template.tsx` | Re-render wrapper | No |
| `default.tsx` | Parallel route fallback | No |

## Server vs Client Components

### When to use 'use client'

Add `'use client'` when component uses:
- State: `useState`, `useReducer`
- Effects: `useEffect`, `useLayoutEffect`
- Events: `onClick`, `onChange`, `onSubmit`
- Browser APIs: `window`, `document`, `localStorage`
- Context: `useContext`
- Third-party hooks

### Composition Pattern (Server inside Client)

```typescript
// ClientWrapper.tsx
'use client'
import { useState } from 'react'

export function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return <div onClick={() => setOpen(!open)}>{children}</div>
}

// page.tsx (Server Component)
import { ClientWrapper } from './ClientWrapper'
import { ServerContent } from './ServerContent'  // Server Component

export default function Page() {
  return (
    <ClientWrapper>
      <ServerContent />  {/* ✅ Server component as children */}
    </ClientWrapper>
  )
}
```

### Serializable Props Boundary

```typescript
// ✅ CAN pass Server → Client:
// strings, numbers, booleans, null, undefined,
// arrays, plain objects, Date, Map, Set, Promises, JSX

// ❌ CANNOT pass:
// functions, class instances, Symbols
```

## Data Fetching

### Server Component (Recommended)

```typescript
async function getData() {
  const res = await fetch('https://api.example.com/data', {
    next: { revalidate: 3600 }  // ISR: revalidate hourly
  })
  if (!res.ok) throw new Error('Failed to fetch')
  return res.json()
}

export default async function Page() {
  const data = await getData()
  return <div>{data.title}</div>
}
```

### Caching Options

```typescript
// Static (default) - cached indefinitely
fetch('https://api.example.com/data')

// Revalidate - ISR every N seconds
fetch('https://api.example.com/data', { next: { revalidate: 60 } })

// No cache - fresh every request
fetch('https://api.example.com/data', { cache: 'no-store' })

// Tag-based revalidation
fetch('https://api.example.com/data', { next: { tags: ['posts'] } })
// Then: revalidateTag('posts')
```

### Server Actions

```typescript
// actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  
  await db.post.create({ data: { title } })
  
  revalidatePath('/posts')
  redirect('/posts')
}

// In component
import { createPost } from './actions'

export function CreateForm() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <button type="submit">Create</button>
    </form>
  )
}
```

### useActionState (v15)

```typescript
'use client'
import { useActionState } from 'react'
import { createPost } from './actions'

export function CreateForm() {
  const [state, formAction, pending] = useActionState(createPost, null)
  
  return (
    <form action={formAction}>
      <input name="title" disabled={pending} />
      <button disabled={pending}>
        {pending ? 'Creating...' : 'Create'}
      </button>
      {state?.error && <p className="text-red-500">{state.error}</p>}
    </form>
  )
}
```

## Route Handlers

```typescript
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const page = searchParams.get('page') ?? '1'
  
  const posts = await getPosts({ page: parseInt(page) })
  return NextResponse.json(posts)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await createPost(body)
  return NextResponse.json(post, { status: 201 })
}

// Dynamic route: app/api/posts/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }  // v15: async
) {
  const { id } = await params
  const post = await getPost(id)
  if (!post) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }
  return NextResponse.json(post)
}
```

## Middleware

```typescript
// middleware.ts (root level)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Auth check
  const token = request.cookies.get('token')
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  // Add headers
  const response = NextResponse.next()
  response.headers.set('x-custom-header', 'value')
  return response
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*']
}
```

## Common Anti-Patterns

### ❌ Entire page as Client Component

```typescript
// ❌ WRONG - loses SSR benefits
'use client'
export default function Page() {
  const [data, setData] = useState(null)
  useEffect(() => { fetch('/api')... }, [])
}

// ✅ CORRECT - Server page, Client islands
export default async function Page() {
  const data = await getData()
  return (
    <>
      <StaticContent data={data} />
      <InteractiveWidget />  {/* Only this is 'use client' */}
    </>
  )
}
```

### ❌ Calling Route Handlers from Server Components

```typescript
// ❌ Unnecessary network hop
const res = await fetch('http://localhost:3000/api/data')

// ✅ Direct function call
import { getData } from '@/lib/data'
const data = await getData()
```

### ❌ redirect() inside try/catch

```typescript
// ❌ redirect throws NEXT_REDIRECT, gets caught
try {
  await saveData()
  redirect('/success')
} catch (e) { /* redirect caught here */ }

// ✅ redirect after try/catch
let success = false
try { 
  await saveData()
  success = true 
} catch (e) { handleError(e) }
if (success) redirect('/success')
```

### ❌ Using next/router in App Router

```typescript
// ❌ Pages Router import
import { useRouter } from 'next/router'

// ✅ App Router imports
import { useRouter, usePathname, useSearchParams } from 'next/navigation'
```

## Turbopack

**Enable in dev:**
```json
{ "scripts": { "dev": "next dev --turbopack" } }
```

**Incompatible plugins (fall back to webpack):**
- `@next/bundle-analyzer`
- `@sentry/nextjs`
- `@payloadcms/next`
- Custom webpack loaders

## Hydration Error Prevention

```typescript
// Browser APIs - defer to useEffect
'use client'
function Component() {
  const [width, setWidth] = useState(0)
  useEffect(() => { setWidth(window.innerWidth) }, [])
  return <div>Width: {width}</div>
}

// Dynamic content - suppressHydrationWarning
<time dateTime={date.toISOString()} suppressHydrationWarning>
  {date.toLocaleDateString()}
</time>

// Stable IDs
import { useId } from 'react'
const id = useId()  // Same on server and client

// Invalid HTML nesting causes hydration failure:
// ❌ <p><div>...</div></p>
// ❌ <a><a>...</a></a>
// ❌ <button><button>...</button></button>
```
