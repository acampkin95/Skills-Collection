# Authentication with Auth.js (NextAuth v5)

Production patterns for Auth.js v5 with Next.js 16 App Router.

## Installation

```bash
npm install next-auth@beta @auth/prisma-adapter
npm install -D @types/bcryptjs
```

## Configuration

### auth.ts (Core Config)

```typescript
// src/auth.ts
import NextAuth from 'next-auth'
import { PrismaAdapter } from '@auth/prisma-adapter'
import Credentials from 'next-auth/providers/credentials'
import Google from 'next-auth/providers/google'
import GitHub from 'next-auth/providers/github'
import bcrypt from 'bcryptjs'
import { prisma } from '@/lib/prisma'

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  session: { strategy: 'jwt' },
  pages: {
    signIn: '/login',
    error: '/login',
  },
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
    Credentials({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string },
        })

        if (!user || !user.hashedPassword) {
          return null
        }

        const isValid = await bcrypt.compare(
          credentials.password as string,
          user.hashedPassword
        )

        if (!isValid) {
          return null
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          image: user.image,
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, trigger, session }) {
      if (user) {
        token.id = user.id
      }
      // Handle session updates
      if (trigger === 'update' && session) {
        token.name = session.name
      }
      return token
    },
    async session({ session, token }) {
      if (token && session.user) {
        session.user.id = token.id as string
      }
      return session
    },
    async authorized({ auth, request }) {
      const isLoggedIn = !!auth?.user
      const isOnDashboard = request.nextUrl.pathname.startsWith('/dashboard')
      
      if (isOnDashboard) {
        return isLoggedIn
      }
      return true
    },
  },
})
```

### Route Handler

```typescript
// src/app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/auth'

export const { GET, POST } = handlers
```

### Middleware

```typescript
// src/middleware.ts
import { auth } from '@/auth'

export default auth((req) => {
  const isLoggedIn = !!req.auth
  const isOnAuth = req.nextUrl.pathname.startsWith('/login') ||
                   req.nextUrl.pathname.startsWith('/register')
  const isOnDashboard = req.nextUrl.pathname.startsWith('/dashboard')
  const isOnApi = req.nextUrl.pathname.startsWith('/api')

  // Redirect authenticated users away from auth pages
  if (isOnAuth && isLoggedIn) {
    return Response.redirect(new URL('/dashboard', req.nextUrl))
  }

  // Protect dashboard routes
  if (isOnDashboard && !isLoggedIn) {
    return Response.redirect(new URL('/login', req.nextUrl))
  }

  // Protect API routes (except auth)
  if (isOnApi && !req.nextUrl.pathname.startsWith('/api/auth') && !isLoggedIn) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }
})

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|public).*)'],
}
```

### Environment Variables

```bash
# .env.local
AUTH_SECRET=generate-with-openssl-rand-base64-32
AUTH_URL=http://localhost:3000

# OAuth Providers
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Database
DATABASE_URL=postgresql://...
```

## Type Extensions

```typescript
// src/types/next-auth.d.ts
import { DefaultSession, DefaultUser } from 'next-auth'
import { JWT, DefaultJWT } from 'next-auth/jwt'

declare module 'next-auth' {
  interface Session {
    user: {
      id: string
    } & DefaultSession['user']
  }

  interface User extends DefaultUser {
    id: string
  }
}

declare module 'next-auth/jwt' {
  interface JWT extends DefaultJWT {
    id: string
  }
}
```

## Server Components

### Get Session

```typescript
// src/app/dashboard/page.tsx
import { auth } from '@/auth'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await auth()
  
  if (!session?.user) {
    redirect('/login')
  }

  return (
    <div>
      <h1>Welcome, {session.user.name}</h1>
      <p>Email: {session.user.email}</p>
    </div>
  )
}
```

### Protected Layout

```typescript
// src/app/dashboard/layout.tsx
import { auth } from '@/auth'
import { redirect } from 'next/navigation'

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const session = await auth()
  
  if (!session) {
    redirect('/login')
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar user={session.user} />
      <main className="flex-1 p-6">{children}</main>
    </div>
  )
}
```

## Client Components

### useSession Hook

```typescript
'use client'

import { useSession } from 'next-auth/react'

export function UserMenu() {
  const { data: session, status } = useSession()

  if (status === 'loading') {
    return <Skeleton className="h-8 w-8 rounded-full" />
  }

  if (!session) {
    return <LoginButton />
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger>
        <Avatar>
          <AvatarImage src={session.user.image || ''} />
          <AvatarFallback>{session.user.name?.[0]}</AvatarFallback>
        </Avatar>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem>{session.user.email}</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <SignOutButton />
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### Session Provider

```typescript
// src/components/providers.tsx
'use client'

import { SessionProvider } from 'next-auth/react'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/lib/queryClient'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </SessionProvider>
  )
}
```

## Server Actions

### Sign In

```typescript
// src/app/actions/auth.ts
'use server'

import { signIn, signOut } from '@/auth'
import { AuthError } from 'next-auth'
import { z } from 'zod'

const loginSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export async function login(prevState: any, formData: FormData) {
  const raw = Object.fromEntries(formData)
  const result = loginSchema.safeParse(raw)

  if (!result.success) {
    return { error: result.error.errors[0].message }
  }

  try {
    await signIn('credentials', {
      email: result.data.email,
      password: result.data.password,
      redirectTo: '/dashboard',
    })
  } catch (error) {
    if (error instanceof AuthError) {
      switch (error.type) {
        case 'CredentialsSignin':
          return { error: 'Invalid email or password' }
        default:
          return { error: 'Something went wrong' }
      }
    }
    throw error
  }
}

export async function loginWithGoogle() {
  await signIn('google', { redirectTo: '/dashboard' })
}

export async function loginWithGitHub() {
  await signIn('github', { redirectTo: '/dashboard' })
}

export async function logout() {
  await signOut({ redirectTo: '/' })
}
```

### Register

```typescript
// src/app/actions/auth.ts (continued)
import bcrypt from 'bcryptjs'
import { prisma } from '@/lib/prisma'

const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export async function register(prevState: any, formData: FormData) {
  const raw = Object.fromEntries(formData)
  const result = registerSchema.safeParse(raw)

  if (!result.success) {
    return { error: result.error.errors[0].message }
  }

  const { name, email, password } = result.data

  // Check if user exists
  const existing = await prisma.user.findUnique({
    where: { email },
  })

  if (existing) {
    return { error: 'Email already registered' }
  }

  // Hash password
  const hashedPassword = await bcrypt.hash(password, 12)

  // Create user
  await prisma.user.create({
    data: {
      name,
      email,
      hashedPassword,
    },
  })

  // Auto sign in
  try {
    await signIn('credentials', {
      email,
      password,
      redirectTo: '/dashboard',
    })
  } catch (error) {
    if (error instanceof AuthError) {
      return { error: 'Failed to sign in after registration' }
    }
    throw error
  }
}
```

## Login Page

```typescript
// src/app/login/page.tsx
import { LoginForm } from '@/components/auth/login-form'
import { OAuthButtons } from '@/components/auth/oauth-buttons'

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-6 p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold">Welcome back</h1>
          <p className="text-slate-600">Sign in to your account</p>
        </div>

        <OAuthButtons />

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-white px-2 text-slate-500">
              Or continue with
            </span>
          </div>
        </div>

        <LoginForm />

        <p className="text-center text-sm text-slate-600">
          Don't have an account?{' '}
          <a href="/register" className="text-brand-600 hover:underline">
            Sign up
          </a>
        </p>
      </div>
    </div>
  )
}
```

### Login Form Component

```typescript
// src/components/auth/login-form.tsx
'use client'

import { useActionState } from 'react'
import { useFormStatus } from 'react-dom'
import { login } from '@/app/actions/auth'

function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button
      type="submit"
      disabled={pending}
      className="w-full rounded-md bg-brand-500 py-2 text-white hover:bg-brand-600 disabled:opacity-50"
    >
      {pending ? 'Signing in...' : 'Sign in'}
    </button>
  )
}

export function LoginForm() {
  const [state, action] = useActionState(login, null)

  return (
    <form action={action} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          required
          className="mt-1 w-full rounded-md border px-3 py-2"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          required
          className="mt-1 w-full rounded-md border px-3 py-2"
        />
      </div>

      {state?.error && (
        <p className="text-sm text-red-500">{state.error}</p>
      )}

      <SubmitButton />
    </form>
  )
}
```

### OAuth Buttons

```typescript
// src/components/auth/oauth-buttons.tsx
'use client'

import { loginWithGoogle, loginWithGitHub } from '@/app/actions/auth'

export function OAuthButtons() {
  return (
    <div className="grid grid-cols-2 gap-4">
      <form action={loginWithGoogle}>
        <button
          type="submit"
          className="flex w-full items-center justify-center gap-2 rounded-md border py-2 hover:bg-slate-50"
        >
          <GoogleIcon className="h-5 w-5" />
          Google
        </button>
      </form>

      <form action={loginWithGitHub}>
        <button
          type="submit"
          className="flex w-full items-center justify-center gap-2 rounded-md border py-2 hover:bg-slate-50"
        >
          <GitHubIcon className="h-5 w-5" />
          GitHub
        </button>
      </form>
    </div>
  )
}
```

## Prisma Schema

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id             String    @id @default(cuid())
  name           String?
  email          String?   @unique
  emailVerified  DateTime?
  image          String?
  hashedPassword String?
  createdAt      DateTime  @default(now())
  updatedAt      DateTime  @updatedAt
  accounts       Account[]
  sessions       Session[]
}

model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String? @db.Text
  access_token      String? @db.Text
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String? @db.Text
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
}
```

## Role-Based Access Control

### Extended Schema

```prisma
enum Role {
  USER
  ADMIN
  MODERATOR
}

model User {
  // ... existing fields
  role Role @default(USER)
}
```

### Auth Config with Roles

```typescript
// src/auth.ts
callbacks: {
  async jwt({ token, user }) {
    if (user) {
      token.id = user.id
      token.role = user.role
    }
    return token
  },
  async session({ session, token }) {
    if (token && session.user) {
      session.user.id = token.id as string
      session.user.role = token.role as Role
    }
    return session
  },
}
```

### Role Check Helper

```typescript
// src/lib/auth-utils.ts
import { auth } from '@/auth'
import { redirect } from 'next/navigation'

export async function requireRole(allowedRoles: Role[]) {
  const session = await auth()
  
  if (!session?.user) {
    redirect('/login')
  }
  
  if (!allowedRoles.includes(session.user.role)) {
    redirect('/unauthorized')
  }
  
  return session
}

// Usage
export default async function AdminPage() {
  const session = await requireRole(['ADMIN'])
  // ...
}
```

## Update Session

```typescript
'use client'

import { useSession } from 'next-auth/react'

export function UpdateProfileForm() {
  const { data: session, update } = useSession()

  async function handleSubmit(formData: FormData) {
    const name = formData.get('name') as string
    
    // Update in database via Server Action
    await updateProfile(formData)
    
    // Update session client-side
    await update({ name })
  }

  return (
    <form action={handleSubmit}>
      <input name="name" defaultValue={session?.user?.name || ''} />
      <button type="submit">Update</button>
    </form>
  )
}
```

## Protected API Route

```typescript
// src/app/api/user/route.ts
import { auth } from '@/auth'
import { NextResponse } from 'next/server'

export async function GET() {
  const session = await auth()
  
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
    select: {
      id: true,
      name: true,
      email: true,
      image: true,
      role: true,
    },
  })
  
  return NextResponse.json(user)
}
```

## Sign Out Button

```typescript
// src/components/auth/sign-out-button.tsx
'use client'

import { logout } from '@/app/actions/auth'

export function SignOutButton() {
  return (
    <form action={logout}>
      <button type="submit" className="text-red-600 hover:underline">
        Sign out
      </button>
    </form>
  )
}
```
