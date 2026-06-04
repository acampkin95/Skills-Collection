# Configuration Templates

Complete, copy-paste ready configuration files for Next.js 16 full-stack projects.

## package.json

```json
{
  "name": "my-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "vitest",
    "test:ui": "vitest --ui"
  },
  "dependencies": {
    "next": "^16.0.10",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@tanstack/react-query": "^5.90.12",
    "zustand": "^5.0.9",
    "zod": "^3.24.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.5"
  },
  "devDependencies": {
    "@types/node": "^22.10.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.7.0",
    "tailwindcss": "^4.1.18",
    "@tailwindcss/postcss": "^4.1.18",
    "postcss": "^8.4.47",
    "eslint": "^9.0.0",
    "eslint-config-next": "^16.0.10",
    "vitest": "^2.1.0",
    "@vitest/ui": "^2.1.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.6.0",
    "@tanstack/react-query-devtools": "^5.90.12",
    "jsdom": "^25.0.0"
  }
}
```

## next.config.ts (Next.js 16)

```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Turbopack (stable in Next.js 16, top-level config)
  turbopack: {
    resolveAlias: {
      '@': './src',
    },
    rules: {
      '*.svg': { loaders: ['@svgr/webpack'], as: '*.js' },
    },
  },
  
  // React Compiler (stable in Next.js 16)
  reactCompiler: true,
  
  // Standalone output for Docker
  output: 'standalone',
  
  // Server Actions
  serverActions: {
    bodySizeLimit: '5mb',
  },
  
  // Images
  images: {
    formats: ['image/webp', 'image/avif'],
    remotePatterns: [
      { protocol: 'https', hostname: '**.cloudinary.com' },
      { protocol: 'https', hostname: 'avatars.githubusercontent.com' },
    ],
  },
  
  // Transpile internal packages (for monorepos)
  transpilePackages: [],
  
  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ]
  },
}

export default nextConfig
```

**Key changes from Next.js 15:**
- `turbopack` is now top-level (was `experimental.turbo`)
- `reactCompiler` is now top-level (was `experimental.reactCompiler`)
- Turbopack is the default bundler for both dev and build

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "preserve",
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "skipLibCheck": true,
    "incremental": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/types/*": ["./src/types/*"]
    },
    "plugins": [{ "name": "next" }]
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

## postcss.config.mjs (MUST be .mjs)

```javascript
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

## tailwind.config.ts (Minimal for v4)

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/app/**/*.{js,ts,jsx,tsx}',
    './src/components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

export default config
```

## src/app/globals.css

```css
@import "tailwindcss";

@theme {
  /* Spacing scale */
  --spacing: 0.25rem;
  
  /* Typography */
  --font-sans: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 
               "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, 
               Consolas, "Liberation Mono", monospace;
  
  /* Brand colors (OKLCH for better color manipulation) */
  --color-brand-50: oklch(0.98 0.01 200);
  --color-brand-100: oklch(0.95 0.03 200);
  --color-brand-200: oklch(0.88 0.06 200);
  --color-brand-300: oklch(0.78 0.12 200);
  --color-brand-400: oklch(0.68 0.18 200);
  --color-brand-500: oklch(0.55 0.23 200);
  --color-brand-600: oklch(0.45 0.20 200);
  --color-brand-700: oklch(0.38 0.16 200);
  --color-brand-800: oklch(0.30 0.12 200);
  --color-brand-900: oklch(0.22 0.10 200);
  
  /* Breakpoints */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
  
  /* Transitions */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
}

@layer base {
  *,
  *::before,
  *::after {
    @apply border-slate-200;
  }
  
  html {
    @apply scroll-smooth;
  }
  
  body {
    @apply bg-white text-slate-950 antialiased;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
  
  h1 { @apply text-4xl font-bold tracking-tight; }
  h2 { @apply text-3xl font-bold tracking-tight; }
  h3 { @apply text-2xl font-semibold; }
  h4 { @apply text-xl font-semibold; }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
  
  .focus-ring {
    @apply focus:outline-none focus-visible:ring-2 
           focus-visible:ring-brand-500 focus-visible:ring-offset-2;
  }
}
```

## src/app/layout.tsx

```typescript
import type { Metadata } from 'next'
import { Providers } from '@/components/providers'
import './globals.css'

export const metadata: Metadata = {
  title: {
    default: 'My App',
    template: '%s | My App',
  },
  description: 'Next.js 16 full-stack application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

## src/components/providers.tsx

```typescript
'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { queryClient } from '@/lib/queryClient'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

## src/lib/queryClient.ts

```typescript
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,     // 5 minutes
      gcTime: 1000 * 60 * 10,       // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
})
```

## src/lib/store.ts

```typescript
import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'

// User Store
interface UserState {
  user: { id: string; name: string; email: string } | null
  isAuthenticated: boolean
  setUser: (user: UserState['user']) => void
  logout: () => void
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      subscribeWithSelector((set) => ({
        user: null,
        isAuthenticated: false,
        setUser: (user) => set({ user, isAuthenticated: !!user }),
        logout: () => set({ user: null, isAuthenticated: false }),
      })),
      { name: 'user-store', version: 1 }
    ),
    { name: 'UserStore' }
  )
)

// UI Store (non-persisted)
interface UIState {
  sidebarOpen: boolean
  modalStack: string[]
  toggleSidebar: () => void
  openModal: (id: string) => void
  closeModal: () => void
}

export const useUIStore = create<UIState>()(
  devtools(
    (set) => ({
      sidebarOpen: true,
      modalStack: [],
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      openModal: (id) => set((s) => ({ modalStack: [...s.modalStack, id] })),
      closeModal: () => set((s) => ({ modalStack: s.modalStack.slice(0, -1) })),
    }),
    { name: 'UIStore' }
  )
)
```

## src/lib/utils.ts

```typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: Date | string): string {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(date))
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
```

## src/app/error.tsx

```typescript
'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h2 className="text-2xl font-bold">Something went wrong!</h2>
      <p className="text-slate-600">{error.message}</p>
      <Button onClick={() => reset()}>Try again</Button>
    </div>
  )
}
```

## src/app/loading.tsx

```typescript
export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
    </div>
  )
}
```

## vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

## src/test/setup.ts

```typescript
import '@testing-library/jest-dom'
import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

afterEach(() => {
  cleanup()
})
```

## .env.local (Template)

```bash
# App
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Auth
NEXTAUTH_SECRET=your-secret-key-here
NEXTAUTH_URL=http://localhost:3000

# API Keys
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

## biome.json (Alternative to ESLint + Prettier)

Biome is 25x faster than ESLint + Prettier combined. Use `--with-biome` flag.

```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.4/schema.json",
  "organizeImports": { "enabled": true },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": {
        "noUnusedImports": "warn",
        "noUnusedVariables": "warn"
      },
      "suspicious": {
        "noExplicitAny": "warn"
      }
    }
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "semicolons": "asNeeded",
      "trailingCommas": "es5"
    }
  },
  "files": {
    "ignore": [".next", "node_modules", "dist", "*.config.*"]
  }
}
```

## eslint.config.mjs (ESLint Flat Config for Next.js 16)

Next.js 16 uses ESLint flat config format. Note: `next lint` is removed in v16.

```javascript
import { dirname } from 'path'
import { fileURLToPath } from 'url'
import { FlatCompat } from '@eslint/eslintrc'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const compat = new FlatCompat({
  baseDirectory: __dirname,
})

const eslintConfig = [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/consistent-type-imports': 'error',
    },
  },
  {
    ignores: ['.next/**', 'node_modules/**', 'dist/**'],
  },
]

export default eslintConfig
```

## vitest.config.mts

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/test/', '**/*.d.ts'],
    },
  },
})
```

## src/test/setup.ts

```typescript
import '@testing-library/jest-dom/vitest'
import { afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

afterEach(() => {
  cleanup()
})

// Mock next/navigation (required for App Router)
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
  redirect: vi.fn(),
  notFound: vi.fn(),
}))

// Mock next/headers (required for Server Components/Actions)
vi.mock('next/headers', () => ({
  cookies: () => ({
    get: vi.fn(() => undefined),
    getAll: vi.fn(() => []),
    set: vi.fn(),
    delete: vi.fn(),
    has: vi.fn(() => false),
  }),
  headers: () => new Headers(),
}))
```

## .gitignore

```gitignore
# Dependencies
node_modules
.pnpm-store

# Build
.next
out
dist
build

# Testing
coverage

# Env
.env*.local
.env

# IDE
.idea
.vscode
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts
```
