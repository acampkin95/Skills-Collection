# Clerk Authentication Patterns

## OAuth Provider Configuration

### Google OAuth

```typescript
// app/sign-in/page.tsx
'use client'

import { useSignIn } from '@clerk/nextjs'
import { Button } from '@/components/ui/button'

export function GoogleSignIn() {
  const { isLoaded, signIn, setActive } = useSignIn()

  const handleGoogleSignIn = async () => {
    if (!isLoaded) return

    try {
      const result = await signIn.authenticateWithRedirect({
        strategy: 'oauth_google',
        redirectUrl: '/auth/callback',
        redirectUrlComplete: '/dashboard',
      })

      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
      }
    } catch (err) {
      console.error('Google sign-in failed:', err)
    }
  }

  return <Button onClick={handleGoogleSignIn}>Sign in with Google</Button>
}
```

### GitHub OAuth

```typescript
export function GitHubSignIn() {
  const { isLoaded, signIn, setActive } = useSignIn()

  const handleGitHubSignIn = async () => {
    if (!isLoaded) return

    try {
      const result = await signIn.authenticateWithRedirect({
        strategy: 'oauth_github',
        redirectUrl: '/auth/callback',
        redirectUrlComplete: '/dashboard',
      })

      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
      }
    } catch (err) {
      console.error('GitHub sign-in failed:', err)
    }
  }

  return <Button onClick={handleGitHubSignIn}>Sign in with GitHub</Button>
}
```

### OAuth Callback Handler

```typescript
// app/auth/callback/page.tsx
'use client'

import { useEffect } from 'react'
import { useSignIn } from '@clerk/nextjs'

export default function AuthCallback() {
  const { isLoaded, signIn } = useSignIn()

  useEffect(() => {
    if (!isLoaded || !signIn) return

    // Handle redirect from OAuth provider
    signIn
      .authenticateWithRedirect({
        redirectUrl: '/auth/callback',
        redirectUrlComplete: '/dashboard',
      })
      .catch((err) => console.error('Auth callback error:', err))
  }, [isLoaded, signIn])

  return <div>Completing sign in...</div>
}
```

## Passwordless Authentication

### Magic Link (Email)

```typescript
'use client'

import { useState } from 'react'
import { useSignIn } from '@clerk/nextjs'

export function MagicLinkSignIn() {
  const { isLoaded, signIn, setActive } = useSignIn()
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [pendingVerification, setPendingVerification] = useState(false)

  const handleSendMagicLink = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isLoaded) return

    try {
      await signIn.create({
        strategy: 'email_link',
        identifier: email,
      })
      setPendingVerification(true)
    } catch (err) {
      console.error('Failed to send magic link:', err)
    }
  }

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isLoaded) return

    try {
      const result = await signIn.attemptFirstFactor({
        strategy: 'email_link_web',
        code,
      })

      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
      }
    } catch (err) {
      console.error('Verification failed:', err)
    }
  }

  return !pendingVerification ? (
    <form onSubmit={handleSendMagicLink} className="space-y-4">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
        required
      />
      <button type="submit">Send Magic Link</button>
    </form>
  ) : (
    <form onSubmit={handleVerify} className="space-y-4">
      <input
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Enter verification code"
        required
      />
      <button type="submit">Verify</button>
    </form>
  )
}
```

### One-Time Password (OTP)

```typescript
export function OTPSignIn() {
  const { isLoaded, signIn, setActive } = useSignIn()
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [pendingVerification, setPendingVerification] = useState(false)

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isLoaded) return

    try {
      await signIn.create({
        strategy: 'email_code',
        identifier: email,
      })
      setPendingVerification(true)
    } catch (err) {
      console.error('Failed to send OTP:', err)
    }
  }

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isLoaded) return

    try {
      const result = await signIn.attemptFirstFactor({
        strategy: 'email_code',
        code,
      })

      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
      }
    } catch (err) {
      console.error('OTP verification failed:', err)
    }
  }

  return !pendingVerification ? (
    <form onSubmit={handleSendOTP}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <button type="submit">Send Code</button>
    </form>
  ) : (
    <form onSubmit={handleVerifyOTP}>
      <input
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="6-digit code"
        required
      />
      <button type="submit">Verify</button>
    </form>
  )
}
```

## Multi-Factor Authentication (MFA)

### Setup MFA

```typescript
'use client'

import { useUser } from '@clerk/nextjs'
import { useState } from 'react'

export function SetupMFA() {
  const { user, isLoaded } = useUser()
  const [showMFASetup, setShowMFASetup] = useState(false)

  if (!isLoaded || !user) return null

  const handleSetupAuthenticator = async () => {
    try {
      const response = await user.createTOTPSecret()
      if (response) {
        console.log('QR Code:', response.qrCodeSvgUrl)
        // Show QR code to user for scanning
      }
    } catch (err) {
      console.error('Failed to setup MFA:', err)
    }
  }

  const handleSetupSMS = async () => {
    try {
      await user.createPhoneNumberVerification({
        phoneNumber: '+1234567890', // Get from user input
        strategy: 'phone_code',
      })
    } catch (err) {
      console.error('Failed to setup SMS MFA:', err)
    }
  }

  return (
    <div className="space-y-4">
      <button onClick={handleSetupAuthenticator}>
        Setup Authenticator App
      </button>
      <button onClick={handleSetupSMS}>Setup SMS Code</button>
    </div>
  )
}
```

### MFA During Sign-In

```typescript
export function SignInWithMFA() {
  const { isLoaded, signIn, setActive } = useSignIn()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [needsMFA, setNeedsMFA] = useState(false)

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isLoaded) return

    try {
      const result = await signIn.create({
        identifier: email,
        password,
      })

      if (result.status === 'needs_second_factor') {
        setNeedsMFA(true)
      } else if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
      }
    } catch (err) {
      console.error('Sign-in failed:', err)
    }
  }

  const handleMFAVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isLoaded || !signIn) return

    try {
      const result = await signIn.attemptSecondFactor({
        strategy: 'totp',
        code: mfaCode,
      })

      if (result.status === 'complete') {
        await setActive({ session: result.createdSessionId })
      }
    } catch (err) {
      console.error('MFA verification failed:', err)
    }
  }

  return !needsMFA ? (
    <form onSubmit={handleSignIn} className="space-y-4">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">Sign In</button>
    </form>
  ) : (
    <form onSubmit={handleMFAVerify} className="space-y-4">
      <input
        value={mfaCode}
        onChange={(e) => setMfaCode(e.target.value)}
        placeholder="MFA Code"
        required
      />
      <button type="submit">Verify</button>
    </form>
  )
}
```

## User Metadata & Custom Claims

### Update User Metadata

```typescript
'use server'

import { auth, clerkClient } from '@clerk/nextjs/server'

export async function updateUserMetadata(metadata: Record<string, any>) {
  const { userId } = await auth()
  if (!userId) throw new Error('Unauthorized')

  const client = await clerkClient()

  // Public metadata (accessible to user)
  await client.users.updateUser(userId, {
    publicMetadata: metadata,
  })

  // Private metadata (server-only)
  await client.users.updateUser(userId, {
    privateMetadata: {
      tier: 'premium',
      customerId: 'stripe_123',
    },
  })
}
```

### Access Metadata in App

```typescript
'use client'

import { useUser } from '@clerk/nextjs'

export function UserTier() {
  const { user, isLoaded } = useUser()

  if (!isLoaded) return <div>Loading...</div>

  const tier = user?.publicMetadata?.tier || 'free'

  return <div>Your plan: {tier}</div>
}
```

### Server-Side Access

```typescript
'use server'

import { auth } from '@clerk/nextjs/server'

export async function getUserTier() {
  const { userId, sessionClaims } = await auth()

  // Access from session claims
  const tier = sessionClaims?.tier || 'free'
  return tier
}
```

## Webhook Events

### User Lifecycle Webhooks

```typescript
// app/api/webhooks/clerk/route.ts
import { Webhook } from 'svix'
import { headers } from 'next/headers'
import { db } from '@/lib/db'

type WebhookEvent = {
  type: string
  data: Record<string, any>
}

export async function POST(req: Request) {
  const payload = await req.json()
  const headersList = await headers()
  const wh = new Webhook(process.env.CLERK_WEBHOOK_SECRET!)

  let evt: WebhookEvent
  try {
    evt = wh.verify(JSON.stringify(payload), {
      'svix-id': headersList.get('svix-id')!,
      'svix-timestamp': headersList.get('svix-timestamp')!,
      'svix-signature': headersList.get('svix-signature')!,
    })
  } catch {
    return new Response('Invalid signature', { status: 400 })
  }

  // Handle events
  switch (evt.type) {
    case 'user.created':
      await db.user.create({
        data: {
          clerkId: evt.data.id,
          email: evt.data.email_addresses[0]?.email_address,
          firstName: evt.data.first_name,
          lastName: evt.data.last_name,
          imageUrl: evt.data.image_url,
        },
      })
      break

    case 'user.updated':
      await db.user.update({
        where: { clerkId: evt.data.id },
        data: {
          email: evt.data.email_addresses[0]?.email_address,
          firstName: evt.data.first_name,
          lastName: evt.data.last_name,
          imageUrl: evt.data.image_url,
        },
      })
      break

    case 'user.deleted':
      await db.user.delete({
        where: { clerkId: evt.data.id },
      })
      break

    case 'organization.created':
      await db.organization.create({
        data: {
          clerkId: evt.data.id,
          name: evt.data.name,
          slug: evt.data.slug,
        },
      })
      break

    case 'organizationMembership.created':
      await db.membership.create({
        data: {
          clerkId: evt.data.id,
          userId: evt.data.public_user_id,
          organizationId: evt.data.organization_id,
          role: evt.data.role,
        },
      })
      break
  }

  return new Response('Webhook processed', { status: 200 })
}
```

## Role-Based Access Control (RBAC)

### Organization Roles

```typescript
'use server'

import { auth } from '@clerk/nextjs/server'

export async function requireOrgRole(requiredRoles: string[]) {
  const { orgRole } = await auth()

  if (!orgRole || !requiredRoles.includes(orgRole)) {
    throw new Error('Insufficient permissions')
  }

  return orgRole
}

export async function isAdmin() {
  const { orgRole } = await auth()
  return orgRole === 'admin'
}

// Usage in Server Component
export default async function AdminPage() {
  await requireOrgRole(['admin'])

  return <AdminDashboard />
}
```

### Permission Middleware

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isAdminRoute = createRouteMatcher(['/admin(.*)'])

export default clerkMiddleware(async (auth, req) => {
  if (isAdminRoute(req)) {
    const { sessionClaims } = await auth()
    const role = sessionClaims?.org_role

    if (role !== 'admin') {
      // Redirect non-admins
      return new Response('Forbidden', { status: 403 })
    }
  }
})
```

## Machine Authentication

### API Key Generation (v6.21+)

```typescript
'use server'

import { auth, clerkClient } from '@clerk/nextjs/server'

export async function generateAPIKey() {
  const { userId } = await auth()
  if (!userId) throw new Error('Unauthorized')

  const client = await clerkClient()

  // Create API key for service-to-service auth
  const apiKey = await client.users.createAPIKey(userId, {
    name: 'Production API Key',
  })

  return apiKey
}
```

### Service Authentication

```typescript
// lib/service-auth.ts
import { clerkClient } from '@clerk/nextjs/server'

export async function authenticateService() {
  // Use environment variable with API key
  const apiKey = process.env.CLERK_SERVICE_API_KEY

  const client = await clerkClient()

  // Make authenticated requests
  const user = await client.users.getUser('user_123')
  return user
}
```

## JWT Customization

### Add Custom Claims to JWT

```typescript
// app/api/auth/session/route.ts
'use server'

import { auth, clerkClient } from '@clerk/nextjs/server'

export async function updateSessionClaims() {
  const { userId } = await auth()
  if (!userId) throw new Error('Unauthorized')

  const client = await clerkClient()

  // Update user to add custom claims to JWT
  await client.users.updateUser(userId, {
    publicMetadata: {
      tier: 'premium',
      permissions: ['read', 'write', 'delete'],
    },
  })

  // JWT will now include these claims
}
```

### Access Custom Claims in JWT

```typescript
'use client'

import { useAuth } from '@clerk/nextjs'

export function useUserPermissions() {
  const { sessionClaims } = useAuth()

  const permissions = (sessionClaims?.permissions as string[]) || []

  return {
    canRead: permissions.includes('read'),
    canWrite: permissions.includes('write'),
    canDelete: permissions.includes('delete'),
  }
}
```
