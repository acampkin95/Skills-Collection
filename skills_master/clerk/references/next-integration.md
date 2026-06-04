# Clerk + Next.js 16 Integration Guide

## App Router Setup

### Root Layout with ClerkProvider

```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
```

**Best Practice**: ClerkProvider at root enables optimal performance and hydration handling.

## Middleware: Route Protection

### Basic Middleware Setup

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/settings(.*)',
  '/api/protected(.*)',
])

export default clerkMiddleware((auth, req) => {
  if (isProtectedRoute(req)) {
    auth.protect()
  }
})

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
}
```

### Advanced Middleware with Custom Logic

```typescript
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

const isPublicRoute = createRouteMatcher(['/', '/sign-in(.*)', '/sign-up(.*)'])
const isAdminRoute = createRouteMatcher(['/admin(.*)'])

export default clerkMiddleware(async (auth, req) => {
  // Public routes - allow access
  if (isPublicRoute(req)) {
    return NextResponse.next()
  }

  // Admin routes - verify role
  if (isAdminRoute(req)) {
    const { sessionClaims } = await auth()
    if (sessionClaims?.org_role !== 'admin') {
      return NextResponse.redirect(new URL('/dashboard', req.url))
    }
  }

  // Protected routes - require authentication
  const { userId } = await auth()
  if (!userId) {
    return NextResponse.redirect(new URL('/sign-in', req.url))
  }
})

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
}
```

## Server Components with Auth

### Basic Auth Check

```typescript
// app/dashboard/page.tsx
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const { userId } = await auth()

  if (!userId) {
    redirect('/sign-in')
  }

  // userId is guaranteed here
  return <h1>Welcome, {userId}</h1>
}
```

**Remember**: `auth()` is **async in v6**. Always use `await`.

### Access Full User Object

```typescript
// app/profile/page.tsx
import { auth, currentUser } from '@clerk/nextjs/server'

export default async function ProfilePage() {
  const user = await currentUser()

  if (!user) {
    redirect('/sign-in')
  }

  return (
    <div>
      <h1>{user.firstName} {user.lastName}</h1>
      <p>{user.emailAddresses[0]?.emailAddress}</p>
      <img src={user.imageUrl} alt="avatar" />
    </div>
  )
}
```

**Performance Tip**: Use `auth()` for quick checks. Only call `currentUser()` when you need full details (it makes an additional API call).

### Organization Context

```typescript
// app/org/[orgId]/page.tsx
import { auth } from '@clerk/nextjs/server'

export default async function OrgPage({
  params,
}: {
  params: { orgId: string }
}) {
  const { userId, orgId, orgRole } = await auth()

  if (!userId || orgId !== params.orgId) {
    redirect('/dashboard')
  }

  return (
    <div>
      <h1>Organization {orgId}</h1>
      <p>Your role: {orgRole}</p>
    </div>
  )
}
```

## Server Actions with Auth

### Protected Server Action

```typescript
// app/actions/update-profile.ts
'use server'

import { auth } from '@clerk/nextjs/server'
import { db } from '@/lib/db'
import { revalidatePath } from 'next/cache'

export async function updateProfile(formData: FormData) {
  const { userId } = await auth()

  if (!userId) {
    throw new Error('Unauthorized')
  }

  const firstName = formData.get('firstName') as string

  // Update in your database
  await db.user.update({
    where: { clerkId: userId },
    data: { firstName },
  })

  revalidatePath('/profile')
  return { success: true }
}

export async function deleteAccount() {
  'use server'

  const { userId } = await auth()
  if (!userId) throw new Error('Unauthorized')

  // Delete user data from your database
  await db.user.delete({ where: { clerkId: userId } })

  // Optionally delete from Clerk too
  const client = await clerkClient()
  await client.users.deleteUser(userId)
}
```

### Usage in Client Components

```typescript
// app/components/update-profile-form.tsx
'use client'

import { updateProfile } from '../actions/update-profile'

export function UpdateProfileForm() {
  return (
    <form action={updateProfile} className="space-y-4">
      <input name="firstName" placeholder="First name" required />
      <button type="submit">Update Profile</button>
    </form>
  )
}
```

## Route Handlers with Auth

### GET with Auth Check

```typescript
// app/api/user/profile/route.ts
import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET(request: Request) {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  const user = await db.user.findUnique({
    where: { clerkId: userId },
  })

  return NextResponse.json(user)
}
```

### POST with Validation

```typescript
// app/api/posts/route.ts
import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'
import { z } from 'zod'

const createPostSchema = z.object({
  title: z.string().min(1),
  content: z.string().min(1),
})

export async function POST(request: Request) {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    )
  }

  try {
    const body = await request.json()
    const { title, content } = createPostSchema.parse(body)

    const post = await db.post.create({
      data: {
        title,
        content,
        userId,
      },
    })

    return NextResponse.json(post, { status: 201 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    )
  }
}
```

## Protected Route Layout

### Group by Auth State

```typescript
// app/(protected)/layout.tsx
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { userId } = await auth()

  if (!userId) {
    redirect('/sign-in')
  }

  return children
}
```

Usage:
```
app/
├── (protected)/
│   ├── layout.tsx        // Auth guard here
│   ├── dashboard/
│   │   └── page.tsx      // Inherits protection
│   └── settings/
│       └── page.tsx      // Inherits protection
├── sign-in/
└── sign-up/
```

## OAuth Callback Handling

### Custom Callback After Sign-In

```typescript
// middleware.ts with afterAuth
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export default clerkMiddleware(
  (auth, req) => {
    const { userId, sessionClaims } = auth()

    // Redirect based on user data
    if (userId && sessionClaims?.isAdmin) {
      if (req.nextUrl.pathname === '/sign-in') {
        return NextResponse.redirect(new URL('/admin', req.url))
      }
    }
  },
  {
    // Configure options
  }
)
```

## Environment Variables

### Required Variables

```env
# Publishable (safe for client)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...

# Secret (server-only)
CLERK_SECRET_KEY=sk_test_...

# Redirect URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

# Optional: Webhook verification
CLERK_WEBHOOK_SECRET=whsec_...
```

### Production Domain Configuration

In Clerk Dashboard:
1. Add your production domain to **Allowed Origins**
2. Configure **Redirect URLs** for production domain
3. Set **API Keys** for production environment
4. Enable **HTTPS enforcement**

## Performance Optimization

### Code Splitting Auth Components

```typescript
// app/layout.tsx
import dynamic from 'next/dynamic'
import { Suspense } from 'react'

const UserMenu = dynamic(() => import('@/components/user-menu'), {
  ssr: false,
  loading: () => <UserMenuSkeleton />,
})

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <header>
      <Suspense fallback={<UserMenuSkeleton />}>
        <UserMenu />
      </Suspense>
    </header>
  )
}
```

### Cache User in Session Claims

```typescript
// lib/session-cache.ts
import { auth } from '@clerk/nextjs/server'

let cachedUser: any = null
let cacheTime = 0

export async function getCachedUser() {
  const now = Date.now()
  if (cachedUser && now - cacheTime < 60000) { // 1 min cache
    return cachedUser
  }

  const { userId } = await auth()
  if (userId) {
    const user = await currentUser()
    cachedUser = user
    cacheTime = now
  }

  return cachedUser
}
```

## Database Sync with Webhooks

### Sync User on Webhook

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from 'svix'
import { headers } from 'next/headers'
import { db } from '@/lib/db'

export async function POST(req: Request) {
  const payload = await req.json()
  const headersList = await headers()
  const wh = new Webhook(process.env.CLERK_WEBHOOK_SECRET!)

  let evt
  try {
    evt = wh.verify(JSON.stringify(payload), {
      'svix-id': headersList.get('svix-id')!,
      'svix-timestamp': headersList.get('svix-timestamp')!,
      'svix-signature': headersList.get('svix-signature')!,
    })
  } catch {
    return new Response('Webhook invalid', { status: 400 })
  }

  if (evt.type === 'user.created') {
    await db.user.create({
      data: {
        clerkId: evt.data.id,
        email: evt.data.email_addresses[0].email_address,
        firstName: evt.data.first_name,
        lastName: evt.data.last_name,
        imageUrl: evt.data.image_url,
      },
    })
  }

  return new Response('OK', { status: 200 })
}
```

## Type Safety

### InferType Patterns

```typescript
import { auth, currentUser } from '@clerk/nextjs/server'

// Get types for better type safety
export type AuthContext = Awaited<ReturnType<typeof auth>>
export type CurrentUser = Awaited<ReturnType<typeof currentUser>>

async function protectedFunction(authCtx: AuthContext) {
  const userId = authCtx.userId
  // TypeScript knows userId type
}
```

## Common Gotchas

### Gotcha 1: Forgetting `await`

```typescript
// ❌ Wrong - won't work
const { userId } = auth()

// ✅ Correct
const { userId } = await auth()
```

### Gotcha 2: Client vs Server

```typescript
// ❌ Can't use auth() in client components
'use client'
import { auth } from '@clerk/nextjs' // Error!

// ✅ Use hooks instead
'use client'
import { useAuth } from '@clerk/nextjs'
export function Component() {
  const { userId } = useAuth()
}
```

### Gotcha 3: Revalidation After Updates

```typescript
// ✅ Revalidate cache after server action
'use server'
import { revalidatePath } from 'next/cache'

export async function updateUser() {
  // ... update logic
  revalidatePath('/profile') // Invalidate cached data
}
```

### Gotcha 4: Organization Context Availability

```typescript
// ❌ Organization may be null if not set
const { orgId } = await auth()

// ✅ Check before using
if (orgId) {
  // Safe to use orgId
}
```
