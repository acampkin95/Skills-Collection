# Advanced Patterns

Production patterns for Server Actions, forms, authentication, caching, and error handling.

## Server Actions with File Upload

```typescript
// src/app/actions/upload.ts
'use server'

import { writeFile } from 'fs/promises'
import path from 'path'

export async function uploadFile(formData: FormData) {
  const file = formData.get('file') as File
  if (!file) return { error: 'No file provided' }
  
  // Validate
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) return { error: 'File too large' }
  
  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowed.includes(file.type)) return { error: 'Invalid file type' }
  
  // Save
  const bytes = await file.arrayBuffer()
  const buffer = Buffer.from(bytes)
  const filename = `${Date.now()}-${file.name}`
  const filepath = path.join(process.cwd(), 'public/uploads', filename)
  
  await writeFile(filepath, buffer)
  
  return { success: true, url: `/uploads/${filename}` }
}
```

## Form with Multiple Actions

```typescript
// src/app/posts/[id]/page.tsx
import { updatePost, deletePost, publishPost } from '@/app/actions/posts'

export default async function PostPage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
  const post = await getPost(id)

  return (
    <div>
      <form action={updatePost}>
        <input type="hidden" name="id" value={id} />
        <input name="title" defaultValue={post.title} />
        <textarea name="content" defaultValue={post.content} />
        <button type="submit">Save</button>
      </form>
      
      <form action={publishPost}>
        <input type="hidden" name="id" value={id} />
        <button type="submit">Publish</button>
      </form>
      
      <form action={deletePost}>
        <input type="hidden" name="id" value={id} />
        <button type="submit" className="text-red-500">Delete</button>
      </form>
    </div>
  )
}
```

## Reusable Action Factory

```typescript
// src/lib/actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { z } from 'zod'

type ActionResult<T> = { success: true; data: T } | { success: false; error: string }

export function createAction<TInput, TOutput>(
  schema: z.ZodSchema<TInput>,
  handler: (input: TInput) => Promise<TOutput>,
  revalidate?: string
) {
  return async (formData: FormData): Promise<ActionResult<TOutput>> => {
    try {
      const raw = Object.fromEntries(formData)
      const input = schema.parse(raw)
      const data = await handler(input)
      
      if (revalidate) revalidatePath(revalidate)
      
      return { success: true, data }
    } catch (e) {
      if (e instanceof z.ZodError) {
        return { success: false, error: e.errors[0].message }
      }
      return { success: false, error: 'An error occurred' }
    }
  }
}

// Usage
const createUserSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
})

export const createUser = createAction(
  createUserSchema,
  async (input) => {
    return await db.user.create({ data: input })
  },
  '/users'
)
```

## Pending UI with useFormStatus

```typescript
'use client'

import { useFormStatus } from 'react-dom'

function SubmitButton({ children }: { children: React.ReactNode }) {
  const { pending } = useFormStatus()
  
  return (
    <button 
      type="submit" 
      disabled={pending}
      className="disabled:opacity-50"
    >
      {pending ? 'Submitting...' : children}
    </button>
  )
}

// Usage in form
export function ContactForm() {
  return (
    <form action={submitContact}>
      <input name="email" type="email" required />
      <textarea name="message" required />
      <SubmitButton>Send Message</SubmitButton>
    </form>
  )
}
```

## Rate Limiting

```typescript
// src/lib/rateLimit.ts
import { headers } from 'next/headers'

const rateLimit = new Map<string, { count: number; reset: number }>()

export async function checkRateLimit(
  limit = 10,
  window = 60000
): Promise<{ allowed: boolean; remaining: number }> {
  const headersList = await headers()
  const ip = headersList.get('x-forwarded-for') || 'anonymous'
  const now = Date.now()
  
  const record = rateLimit.get(ip)
  
  if (!record || now > record.reset) {
    rateLimit.set(ip, { count: 1, reset: now + window })
    return { allowed: true, remaining: limit - 1 }
  }
  
  if (record.count >= limit) {
    return { allowed: false, remaining: 0 }
  }
  
  record.count++
  return { allowed: true, remaining: limit - record.count }
}

// Usage in action
export async function submitForm(formData: FormData) {
  const { allowed, remaining } = await checkRateLimit(5, 60000)
  if (!allowed) {
    return { error: 'Too many requests. Please wait.' }
  }
  // ... process form
}
```

## Middleware Authentication

```typescript
// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const protectedPaths = ['/dashboard', '/settings', '/api/private']
const authPaths = ['/login', '/register']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const token = request.cookies.get('session')?.value
  
  // Protect routes
  const isProtected = protectedPaths.some(p => pathname.startsWith(p))
  if (isProtected && !token) {
    const url = new URL('/login', request.url)
    url.searchParams.set('from', pathname)
    return NextResponse.redirect(url)
  }
  
  // Redirect authenticated users from auth pages
  const isAuthPage = authPaths.some(p => pathname.startsWith(p))
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
```

## Parallel Data Fetching

```typescript
// src/app/dashboard/page.tsx
export default async function DashboardPage() {
  // Parallel fetching — much faster
  const [user, posts, stats] = await Promise.all([
    getUser(),
    getPosts(),
    getStats(),
  ])

  return (
    <div>
      <UserCard user={user} />
      <PostList posts={posts} />
      <StatsWidget stats={stats} />
    </div>
  )
}
```

## Streaming with Suspense

```typescript
// src/app/dashboard/page.tsx
import { Suspense } from 'react'

export default async function DashboardPage() {
  const user = await getUser() // Fast, needed for layout

  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      
      <Suspense fallback={<PostsSkeleton />}>
        <PostList userId={user.id} />
      </Suspense>
      
      <Suspense fallback={<StatsSkeleton />}>
        <StatsWidget userId={user.id} />
      </Suspense>
    </div>
  )
}

// These are async Server Components
async function PostList({ userId }: { userId: string }) {
  const posts = await getPosts(userId) // Slow query
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>
}
```

## Caching Strategies

```typescript
// Force cache (default for fetch in Server Components)
const data = await fetch(url)

// Revalidate every 60 seconds
const data = await fetch(url, { next: { revalidate: 60 } })

// No cache
const data = await fetch(url, { cache: 'no-store' })

// For non-fetch data
import { unstable_cache } from 'next/cache'

const getCachedUser = unstable_cache(
  async (id: string) => db.user.findUnique({ where: { id } }),
  ['user'],
  { revalidate: 60, tags: ['users'] }
)

// Invalidate by tag
import { revalidateTag } from 'next/cache'
revalidateTag('users')
```

## Error Handling in Actions

```typescript
'use server'

import { z } from 'zod'

class ActionError extends Error {
  constructor(message: string, public code: string) {
    super(message)
  }
}

export async function riskyAction(formData: FormData) {
  try {
    // Validation
    const schema = z.object({ id: z.string().uuid() })
    const { id } = schema.parse(Object.fromEntries(formData))
    
    // Business logic
    const result = await someRiskyOperation(id)
    if (!result) {
      throw new ActionError('Resource not found', 'NOT_FOUND')
    }
    
    return { success: true, data: result }
  } catch (e) {
    if (e instanceof z.ZodError) {
      return { success: false, error: 'Invalid input', code: 'VALIDATION' }
    }
    if (e instanceof ActionError) {
      return { success: false, error: e.message, code: e.code }
    }
    console.error('Unexpected error:', e)
    return { success: false, error: 'Something went wrong', code: 'UNKNOWN' }
  }
}
```

## Optimistic Updates with Query Invalidation

```typescript
'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateTodo } from '@/app/actions/todo'

export function useTodoMutation() {
  const qc = useQueryClient()
  
  return useMutation({
    mutationFn: updateTodo,
    onMutate: async (newTodo) => {
      // Cancel outgoing refetches
      await qc.cancelQueries({ queryKey: ['todos'] })
      
      // Snapshot previous value
      const previous = qc.getQueryData(['todos'])
      
      // Optimistically update
      qc.setQueryData(['todos'], (old: Todo[]) =>
        old.map(t => t.id === newTodo.id ? { ...t, ...newTodo } : t)
      )
      
      return { previous }
    },
    onError: (err, newTodo, context) => {
      // Rollback on error
      qc.setQueryData(['todos'], context?.previous)
    },
    onSettled: () => {
      // Always refetch after error or success
      qc.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
```

## Search with URL State

```typescript
'use client'

import { useSearchParams, usePathname, useRouter } from 'next/navigation'
import { useDebouncedCallback } from 'use-debounce'

export function SearchInput() {
  const searchParams = useSearchParams()
  const pathname = usePathname()
  const { replace } = useRouter()
  
  const handleSearch = useDebouncedCallback((term: string) => {
    const params = new URLSearchParams(searchParams)
    params.set('page', '1')
    
    if (term) {
      params.set('q', term)
    } else {
      params.delete('q')
    }
    
    replace(`${pathname}?${params.toString()}`)
  }, 300)
  
  return (
    <input
      type="search"
      placeholder="Search..."
      defaultValue={searchParams.get('q') || ''}
      onChange={(e) => handleSearch(e.target.value)}
    />
  )
}
```

## Infinite Scroll

```typescript
'use client'

import { useInfiniteQuery } from '@tanstack/react-query'
import { useInView } from 'react-intersection-observer'
import { useEffect } from 'react'

export function InfiniteList() {
  const { ref, inView } = useInView()
  
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['items'],
    queryFn: async ({ pageParam = 0 }) => {
      const res = await fetch(`/api/items?cursor=${pageParam}`)
      return res.json()
    },
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: 0,
  })
  
  useEffect(() => {
    if (inView && hasNextPage) {
      fetchNextPage()
    }
  }, [inView, hasNextPage, fetchNextPage])
  
  return (
    <div>
      {data?.pages.map((page, i) => (
        <div key={i}>
          {page.items.map((item: Item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      ))}
      
      <div ref={ref}>
        {isFetchingNextPage && <Spinner />}
      </div>
    </div>
  )
}
```

## WebSocket Integration

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'

export function useRealtimeUpdates(channel: string) {
  const qc = useQueryClient()
  const [connected, setConnected] = useState(false)
  
  useEffect(() => {
    const ws = new WebSocket(`${process.env.NEXT_PUBLIC_WS_URL}/${channel}`)
    
    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    
    ws.onmessage = (event) => {
      const { type, data } = JSON.parse(event.data)
      
      switch (type) {
        case 'created':
          qc.invalidateQueries({ queryKey: [channel] })
          break
        case 'updated':
          qc.setQueryData([channel, data.id], data)
          break
        case 'deleted':
          qc.invalidateQueries({ queryKey: [channel] })
          break
      }
    }
    
    return () => ws.close()
  }, [channel, qc])
  
  return { connected }
}
```
