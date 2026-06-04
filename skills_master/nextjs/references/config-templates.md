# Configuration Templates

Copy-paste ready configuration files for Next.js 15/16.

---

## next.config.ts

```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone',  // For Docker
  
  serverExternalPackages: ['sharp', '@prisma/client'],
  
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },
  
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.example.com' },
    ],
    formats: ['image/avif', 'image/webp'],
  },
}

export default nextConfig
```

---

## tsconfig.json

```json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] },
    "target": "ES2017",
    "forceConsistentCasingInFileNames": true
  },
  "include": ["next-env.d.ts", ".next/types/**/*.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

**Critical:** `moduleResolution: "bundler"` and `.next/types/**/*.ts` in include.

---

## postcss.config.mjs

**Must be `.mjs`, NOT `.js`**

```javascript
/** @type {import('postcss-load-config').Config} */
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

---

## app/globals.css

```css
@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --color-primary: #3b82f6;
  --color-secondary: #8b5cf6;
  --font-sans: var(--font-geist-sans), system-ui, sans-serif;
  --font-mono: var(--font-geist-mono), monospace;
}

@layer base {
  :root {
    --background: #ffffff;
    --foreground: #0a0a0a;
  }
  .dark {
    --background: #0a0a0a;
    --foreground: #ededed;
  }
  body {
    background: var(--background);
    color: var(--foreground);
  }
}

@layer components {
  .btn-primary {
    @apply bg-primary text-white px-4 py-2 rounded-sm font-medium hover:bg-primary/90;
  }
}
```

---

## app/layout.tsx

```typescript
import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import './globals.css'

export const metadata: Metadata = {
  title: 'App Title',
  description: 'App description',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

---

## app/error.tsx

```typescript
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <p className="mt-2 text-gray-600">{error.message}</p>
      <button onClick={() => reset()} className="mt-4 btn-primary">
        Try again
      </button>
    </div>
  )
}
```

---

## app/loading.tsx

```typescript
export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )
}
```

---

## app/not-found.tsx

```typescript
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h2 className="text-2xl font-bold">404 - Not Found</h2>
      <p className="mt-2 text-gray-600">Could not find requested resource</p>
      <Link href="/" className="mt-4 text-primary hover:underline">
        Return Home
      </Link>
    </div>
  )
}
```

---

## app/global-error.tsx

```typescript
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
        <div className="flex min-h-screen flex-col items-center justify-center">
          <h2 className="text-2xl font-bold">Something went wrong!</h2>
          <button onClick={() => reset()} className="mt-4 rounded bg-blue-600 px-4 py-2 text-white">
            Try again
          </button>
        </div>
      </body>
    </html>
  )
}
```

---

## package.json Scripts

```json
{
  "scripts": {
    "dev": "next dev --turbopack",
    "dev:webpack": "NEXT_TURBOPACK=0 next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "e2e": "playwright test"
  }
}
```

---

## .env.local Template

```bash
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

# Authentication
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="generate-with-openssl-rand-base64-32"

# Server-only
API_SECRET_KEY="your-secret-key"

# Client-exposed (MUST have NEXT_PUBLIC_ prefix)
NEXT_PUBLIC_API_URL="http://localhost:3000/api"
```

---

## .gitignore

```gitignore
node_modules
.next
out
build
dist
.env
.env.local
.env.*.local
npm-debug.log*
coverage
playwright-report
.DS_Store
*.swp
```

---

## Monorepo CSS

```css
@import "tailwindcss";

@source "../packages/ui/src";
@source "../shared/components";
@source not "./legacy";
```

```typescript
// next.config.ts for monorepo
import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  turbopack: {
    root: path.join(__dirname, '../..'),
  },
  transpilePackages: ['@myorg/ui', '@myorg/shared'],
}

export default nextConfig
```
