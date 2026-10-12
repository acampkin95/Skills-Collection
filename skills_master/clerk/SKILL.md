---
name: clerk
description: Clerk authentication for Next.js 16 with the async auth() API used in Clerk v6, proxy.ts middleware, route protection, organisations, webhooks, and React 19 compatibility. Use when adding sign-in, sign-up, or user management with Clerk, protecting Next.js routes or server actions, reading the current user or organisation with auth(), or syncing Clerk users through webhooks.
version: "1.0.0"
---

# Clerk v6 — Authentication for Next.js

Managed authentication and user management platform. The examples in this skill use the **Clerk v6 async `auth()` API**; treat `await auth()` as the pattern to follow.

**Version note (checked 2026-10-12):** the latest `@clerk/nextjs` on npm is 7.9.14. Its peer range is Next.js 15.2.8 or later in the 15 line, or 16.0.10 or later in the 16 line, and it needs Node 20.9.0 or newer. Clerk 7.0.0 removed `<SignedIn>`, `<SignedOut>`, and `<Protect>` in favour of `<Show when>`, removed `initialAuthState` from `useAuth` (pass `initialState` to `<ClerkProvider>`), and requires `CLERK_ENCRYPTION_KEY` when `clerkMiddleware` receives a `secretKey` at runtime. Check the changelog for the version you install. The 7.0.0 text checked did not restate the async `auth()` change.

## Quick Router

| Need | Reference |
|------|-----------|
| **Next.js 16 integration, middleware, route protection** | `references/next-integration.md` |
| **OAuth, MFA, JWT, webhooks** | `references/auth-patterns.md` |
| **Core setup, async patterns, organisations** | This page |

## Key Changes in v6

```typescript
// ❌ v5 (Synchronous - NO LONGER WORKS)
const { userId } = auth()

// ✅ v6 (Asynchronous - REQUIRED)
const { userId } = await auth()

// ✅ clerkClient is also async
const client = await clerkClient()

// ✅ Route protection goes inside clerkMiddleware (see Middleware below)
clerkMiddleware((auth, req) => {
  if (isProtectedRoute(req)) auth.protect()
})
```

## Installation & Setup

```bash
npm install @clerk/nextjs

# Environment variables
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
```

### Root Layout Setup

```typescript
import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html>
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}
```

## Core Features at a Glance

| Feature | Details |
|---------|---------|
| **Auth Methods** | Email/password, OAuth (20+ providers), passkeys, magic links, Web3 |
| **MFA** | SMS, authenticator apps, backup codes |
| **Organizations** | Multi-tenant with role hierarchy and RBAC |
| **Sessions** | 60-second JWTs with auto-refresh |
| **Machine Auth** | API keys, OAuth tokens, session tokens (v6.21+) |
| **Webhooks** | Real-time user lifecycle events (user.created, user.updated, etc.) |
| **Security** | SOC 2 Type II, credential stuffing protection, password breach checking |
| **Compliance** | HIPAA-eligible, GDPR-compliant |

## Key Async Patterns

### Server Components (async)

```typescript
import { auth } from '@clerk/nextjs'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const { userId } = await auth()

  if (!userId) {
    redirect('/sign-in')
  }

  return <h1>Welcome</h1>
}
```

### Server Actions (async)

```typescript
'use server'
import { auth } from '@clerk/nextjs'

export async function updateProfile(formData: FormData) {
  const { userId } = await auth()
  if (!userId) throw new Error('Unauthorized')

  // Update in your database
  await db.user.update({
    where: { clerkId: userId },
    data: { name: formData.get('name') }
  })
}
```

### Middleware

```typescript
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isProtectedRoute = createRouteMatcher(['/dashboard(.*)'])

export default clerkMiddleware((auth, req) => {
  if (isProtectedRoute(req)) {
    auth.protect()
  }
})

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)']
}
```

## Next.js 16 Middleware (proxy.ts)

Next.js 16 replaces `middleware.ts` with `proxy.ts` for auth:

```typescript
// proxy.ts (Next.js 16+)
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isProtectedRoute = createRouteMatcher(['/dashboard(.*)'])

export default clerkMiddleware((auth, req) => {
  if (isProtectedRoute(req)) {
    auth.protect()
  }
})
```

## Machine-to-Machine Auth

Not verified: the "v6.21+" introduction version, and the `sessionClaims.metadata.isMachine` check below, were not confirmed against Clerk's machine-token documentation. The Clerk changelog mentions M2M token support in 6.37.x and 6.39.0. Check the current M2M API before using this pattern.

```typescript
import { auth } from '@clerk/nextjs/server'

export async function GET(req: Request) {
  const { userId, sessionClaims } = await auth()

  // Machine tokens use session tokens or API keys
  // Verify machine identity via custom JWT claims
  if (sessionClaims?.metadata?.isMachine) {
    // Handle machine-to-machine request
  }
}
```

## Clerk Elements — Custom Auth UI

Not verified against the current Clerk Elements API; confirm the import path and component names before use.

Build fully custom sign-in/sign-up flows without Clerk's prebuilt components:

```typescript
import { SignIn } from '@clerk/elements/sign-in'

export default function CustomSignIn() {
  return (
    <SignIn.Root>
      <SignIn.Step name="start">
        <SignIn.Field name="identifier">
          <SignIn.Input />
        </SignIn.Field>
        <SignIn.Action submit>Continue</SignIn.Action>
      </SignIn.Step>
    </SignIn.Root>
  )
}
```

## Organisation & Multi-Tenant

```typescript
// Get current organization
const { userId, orgId, orgRole } = await auth()

// Use in database queries
const orgData = await db.organization.findUnique({
  where: { clerkId: orgId }
})

// Webhook syncing organizations
case 'organization.created':
  await db.organization.create({
    data: { clerkId: evt.data.id, name: evt.data.name }
  })
```

## Reference Files

| File | Purpose |
|------|---------|
| `references/next-integration.md` | Next.js 16 App Router setup, middleware, route protection, Server Actions |
| `references/auth-patterns.md` | OAuth providers, MFA, JWT customization, user metadata, webhooks |
| `references/organizations-billing-views.md` | Organisation roles, billing, and framework SDK views; read when building multi-tenant or billing features |
| `references/schema-patterns.md` | Database schema for syncing Clerk users and organisations; read when designing local user tables |

## Common Issues & Solutions

**Hydration Error**: Always check `isLoaded` before rendering auth-dependent content in client components.

**Stale Session Data**: Use webhooks to sync Clerk user changes to your database in real-time.

**Async/Await**: Remember — `auth()` is **async in v6**. Wrap all auth() calls with `await`.

---

*For detailed patterns, advanced security, and provider-specific setup, see reference files.*
