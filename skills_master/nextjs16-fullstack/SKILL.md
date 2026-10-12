---
name: nextjs16-fullstack
description: "Builds full-stack Next.js 16 apps with React 19, Tailwind CSS v4, Zustand v5 and TanStack Query v5: cache components and use cache, async request APIs, Server Actions with validation, React 19 hooks, API route handlers, and file conventions. Use when building or upgrading a Next.js 16 project, adding Server Actions or forms, setting up client state with Zustand or server state with TanStack Query, wiring Tailwind v4, or asking about Next.js 16 caching, revalidation or proxy.ts."
version: "1.0.0"
reviewed: "2026-10-12"
---

# Next.js 16 Full-Stack Development

Production-ready full-stack patterns for Next.js 16, React 19, and modern tooling.

## Security Notice

**Next.js 16.0.10+ required** — patches RSC vulnerabilities:
- CVE-2025-66478 (RCE, CVSS 10.0) — fixed in 16.0.7+
- CVE-2025-55183 (source exposure) — fixed in 16.0.10+
- CVE-2025-67779 (DoS) — fixed in 16.0.10+

*Not verified (checked 2026-10-12):* the fixed-version floors above could not be confirmed, because the Vercel bulletin (https://vercel.com/kb/bulletin/security-bulletin-cve-2025-55184-and-cve-2025-55183) was not reachable. Confirm each floor against that bulletin's patched-versions table before relying on it. The Next.js docs index lists 16.2.9 as the newest 16.x tag.

Upgrade immediately: `npm install next@latest`

## Next.js 16 Core Features

### Cache Components & `use cache` Directive

The defining innovation is granular caching control:

```javascript
'use cache';
export async function getStaticData() {
  return await fetchCachedData();
}
```

**Benefits:**
- Replaces implicit ISR with explicit control
- Dynamic code executes at request time by default
- Build on Partial Pre-Rendering foundation

Enable with `cacheComponents: true` in `next.config.ts` (see the nextjs skill's PPR section; the experimental PPR flags are not used in Next.js 16).

### Turbopack Default

- 2-5x faster production builds
- 10x faster Fast Refresh
- No config changes required

### New Caching APIs

```javascript
import { revalidateTag, updateTag, refresh } from 'next/cache';

revalidateTag('data', 'max');  // second argument is a cacheLife profile; 'max' is recommended
updateTag('content');          // Server Actions only: expire and refresh immediately
refresh();                     // Server Actions only: refresh the client router
```

Source: https://github.com/vercel/next.js/blob/v16.2.9/docs/01-app/02-guides/upgrading/version-16.mdx and the `revalidateTag`, `updateTag` and `refresh` API pages in the same docs tree (checked 2026-10-12). The single-argument `revalidateTag(tag)` form is deprecated.

### DevTools MCP (New!)

**AI-native debugging** with Cursor/Claude integration:
- Direct AI access to routing tree and logs
- Automated upgrades via natural language

```bash
next dev --mcp
```

## Stack Versions

| Package | Version | Notes |
|---------|---------|-------|
| Next.js | 16.0.10+ | Security patched |
| React | 19.0.0+ | Server Components |
| TypeScript | 5.7+ | Strict mode |
| Tailwind CSS | 4.1.18+ | CSS-first config |
| Zustand | 5.0.9+ | Client state |
| TanStack Query | 5.90+ | Server state |

## Quick Start

```bash
./scripts/init-project.sh my-app
./scripts/init-project.sh my-app --minimal
./scripts/init-project.sh my-app --with-biome
./scripts/init-project.sh my-app --with-docker --with-playwright
```

## Key Async APIs (Breaking Change)

All request APIs are async in Next.js 16:

```typescript
export default async function Page({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const cookieStore = await cookies()
  const headersList = await headers()
  return <div>{id}</div>
}

// Client Component — use React.use()
'use client'
import { use } from 'react'
export default function ClientPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <div>{id}</div>
}
```

## Server Actions Pattern

```typescript
'use server'
import { revalidatePath } from 'next/cache'

export async function createUser(formData: FormData) {
  const name = formData.get('name') as string
  const email = formData.get('email') as string

  const user = await db.user.create({ data: { name, email } })
  revalidatePath('/users')
  return { success: true, user }
}
```

With validation (Zod):
```typescript
'use server'
import { z } from 'zod'

const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
})

export async function createUser(formData: FormData) {
  const raw = Object.fromEntries(formData)
  const result = schema.safeParse(raw)
  if (!result.success) return { error: 'Validation failed' }
  const user = await db.user.create({ data: result.data })
  revalidatePath('/users')
  return { success: true, user }
}
```

## React 19 Hooks

### useActionState

```typescript
'use client'
import { useActionState } from 'react'
import { createUser } from '@/app/actions/user'

export function CreateUserForm() {
  const [state, action, isPending] = useActionState(createUser, {})
  return (
    <form action={action}>
      <input name="name" disabled={isPending} />
      {state.error && <p>{state.error}</p>}
      <button disabled={isPending}>Create</button>
    </form>
  )
}
```

### useOptimistic

```typescript
'use client'
import { useOptimistic } from 'react'

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimistic, addOptimistic] = useOptimistic(todos, (state, newTodo) => [...state, newTodo])

  async function handleAdd(formData: FormData) {
    const title = formData.get('title') as string
    addOptimistic({ id: crypto.randomUUID(), title, completed: false })
    await addTodo(formData)
  }

  return (
    <>
      <form action={handleAdd}>
        <input name="title" />
        <button>Add</button>
      </form>
      <ul>{optimistic.map(todo => <li key={todo.id}>{todo.title}</li>)}</ul>
    </>
  )
}
```

## Zustand v5 Patterns

```typescript
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        setUser: (user) => set({ user }),
        logout: () => set({ user: null }),
      }),
      { name: 'user-store', version: 1 }
    ),
    { name: 'UserStore' }
  )
)

// Selector optimization — critical!
import { useShallow } from 'zustand/shallow'
const { name, age } = useStore(useShallow((s) => ({ name: s.name, age: s.age })))
```

## TanStack Query v5

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await fetch('/api/users')
      if (!res.ok) throw new Error('Failed')
      return res.json()
    },
  })
}

export function useCreateUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data) => fetch('/api/users', { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  })
}
```

**v5 Breaking Changes:**
- `isLoading` → `isPending`
- `cacheTime` → `gcTime`

## Tailwind CSS v4

```css
@import "tailwindcss";

@theme {
  --spacing: 0.25rem;
  --font-sans: ui-sans-serif, system-ui, -apple-system, sans-serif;
  --color-brand-500: oklch(0.55 0.23 200);
}

@layer base {
  body { @apply bg-white text-slate-950 antialiased; }
}
```

## API Routes

```typescript
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const page = parseInt(searchParams.get('page') || '1')
  const users = await db.user.findMany({ skip: (page - 1) * 10, take: 10 })
  return NextResponse.json(users)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const user = await db.user.create({ data: body })
  return NextResponse.json(user, { status: 201 })
}

// Dynamic route
export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const user = await db.user.findUnique({ where: { id } })
  if (!user) return NextResponse.json({ error: 'Not found' }, { status: 404 })
  return NextResponse.json(user)
}
```

## File Conventions

| File | Use Client? | Notes |
|------|-------------|-------|
| `page.tsx` | No | Server Component |
| `layout.tsx` | No | Server Component |
| `error.tsx` | **YES** | Error boundary |
| `global-error.tsx` | **YES** | Root error |
| `route.ts` | N/A | API endpoint |

## Anti-Patterns

```typescript
// ❌ Entire page as client component
'use client'
export default function Page() {
  const [data, setData] = useState(null)
  useEffect(() => { fetch('/api')... }, [])
}

// ✅ Server fetching, client interactivity
export default async function Page() {
  const data = await getData()
  return <><Static data={data} /><Interactive /></>
}
```

## Common Issues & Fixes

1. **Styles not loading**: Check `import './globals.css'` in layout.tsx
2. **Hydration errors**: Verify `'use client'` on hook/event components
3. **Dynamic Tailwind classes purged**: Use complete static strings only
4. **Request-level redirects**: Use `proxy.ts` for request-level logic on Next.js 16 (exports a function named `proxy`; the pre-16 `middleware.ts` name is renamed). Source: https://github.com/vercel/next.js/blob/v16.2.9/docs/01-app/02-guides/upgrading/version-16.mdx (checked 2026-10-12).

---

## Reference Files

| Resource | Purpose |
|----------|---------|
| `references/config-templates.md` | next.config.ts, tsconfig, postcss configs |
| `references/advanced-patterns.md` | Forms, streaming, caching strategies |
| `references/nextauth.md` | Auth.js v5, OAuth, RBAC, credentials |
| `references/migration-guide.md` | v15 → v16 upgrade paths |
| `references/troubleshooting.md` | Hydration, "dead UI", common errors |
