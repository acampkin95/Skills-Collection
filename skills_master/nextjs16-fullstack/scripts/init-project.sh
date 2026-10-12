#!/bin/bash
#
# init-project.sh - Initialize a Next.js 16 full-stack project
#
# DEFAULTS: Full-stack with Auth.js, Prisma, ShadCN/UI (use --minimal to opt out)
#
# Usage: ./init-project.sh <project-name> [options]
#
# Options:
#   --minimal       Minimal setup (no auth, no database, no UI library)
#   --no-auth       Skip Auth.js authentication
#   --no-db         Skip Prisma database
#   --no-ui         Skip ShadCN/UI components
#   --no-git        Skip git initialization
#   --with-biome    Use Biome instead of ESLint + Prettier (25x faster)
#   --with-docker   Add Dockerfile + docker-compose
#   --with-husky    Add Husky git hooks + lint-staged
#   --with-playwright Add Playwright E2E testing
#   --with-monorepo Create Turborepo monorepo structure
#   --with-sanity   Add Sanity CMS with embedded Studio
#   --with-accelerate Configure Prisma Accelerate for serverless
#   -h, --help      Show this help message
#
# Examples:
#   ./init-project.sh my-app                    # Full-stack (default)
#   ./init-project.sh my-app --minimal          # Minimal setup
#   ./init-project.sh my-app --with-biome       # Full-stack + Biome
#   ./init-project.sh my-app --no-db            # Full-stack without database
#   ./init-project.sh my-app --with-monorepo    # Turborepo monorepo

set -euo pipefail

# ============================================================================
# Colors and Logging
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_step() { echo -e "\n${CYAN}${BOLD}▸ $1${NC}"; }
log_substep() { echo -e "${DIM}  → $1${NC}"; }

show_help() {
  cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║               Next.js 16 Full-Stack Project Initializer                    ║
╚════════════════════════════════════════════════════════════════════════════╝

Usage: ./init-project.sh <project-name> [options]

DEFAULT BEHAVIOR (Full-Stack):
  • Auth.js v5 (OAuth + Credentials, Edge-compatible)
  • Prisma ORM with PostgreSQL
  • ShadCN/UI components
  • TanStack Query + Zustand
  • Vitest testing
  • TypeScript strict mode

Options:
  --minimal         Minimal setup (just Next.js + Tailwind + TypeScript)
  --no-auth         Skip Auth.js authentication
  --no-db           Skip Prisma database
  --no-ui           Skip ShadCN/UI components
  --no-git          Skip git initialization
  --with-biome      Use Biome instead of ESLint + Prettier (25x faster)
  --with-docker     Add Dockerfile + docker-compose.yml
  --with-husky      Add Husky git hooks + lint-staged
  --with-playwright Add Playwright E2E testing
  --with-sanity     Add Sanity CMS with embedded Studio
  --with-monorepo   Create Turborepo monorepo structure
  --with-accelerate Configure Prisma Accelerate for serverless
  -h, --help        Show this help message

Examples:
  ./init-project.sh my-app                      # Full-stack (recommended)
  ./init-project.sh my-app --minimal            # Just the basics
  ./init-project.sh my-app --with-biome         # Full-stack + faster linting
  ./init-project.sh my-app --no-db --no-auth    # Frontend only
  ./init-project.sh my-app --with-monorepo      # Turborepo monorepo

Stack (Next.js 16):
  • Turbopack (default bundler)
  • React 19 + React Compiler
  • Tailwind CSS v4 (CSS-first)
  • TypeScript 5.7+ (strict)
EOF
  exit 0
}

# ============================================================================
# Parse Arguments
# ============================================================================
PROJECT_NAME=""
NO_GIT=""
MINIMAL=""
WITH_AUTH="true"
WITH_DB="true"
WITH_UI="true"
WITH_BIOME=""
WITH_DOCKER=""
WITH_HUSKY=""
WITH_PLAYWRIGHT=""
WITH_MONOREPO=""
WITH_SANITY=""
WITH_ACCELERATE=""

for arg in "$@"; do
  case $arg in
    -h|--help) show_help ;;
    --no-git) NO_GIT="true" ;;
    --minimal) MINIMAL="true"; WITH_AUTH=""; WITH_DB=""; WITH_UI="" ;;
    --no-auth) WITH_AUTH="" ;;
    --no-db) WITH_DB="" ;;
    --no-ui) WITH_UI="" ;;
    --with-biome) WITH_BIOME="true" ;;
    --with-docker) WITH_DOCKER="true" ;;
    --with-husky) WITH_HUSKY="true" ;;
    --with-playwright) WITH_PLAYWRIGHT="true" ;;
    --with-sanity) WITH_SANITY="true" ;;
    --with-monorepo) WITH_MONOREPO="true" ;;
    --with-accelerate) WITH_ACCELERATE="true"; WITH_DB="true" ;;
    -*) log_error "Unknown option: $arg"; echo "Run with --help for usage"; exit 1 ;;
    *) PROJECT_NAME="$arg" ;;
  esac
done

# Validate project name
if [ -z "$PROJECT_NAME" ]; then
  log_error "Project name is required"
  echo "Usage: ./init-project.sh <project-name> [options]"
  exit 1
fi

if [ -d "$PROJECT_NAME" ]; then
  log_error "Directory '$PROJECT_NAME' already exists"
  exit 1
fi

# ============================================================================
# Banner
# ============================================================================
echo ""
echo -e "${MAGENTA}${BOLD}"
cat << 'EOF'
    _   __          __      _        ___  ___
   / | / /__  _  __/ /_    (_)____  <  / / _ \
  /  |/ / _ \| |/_/ __/   / / ___/  / / / // /
 / /|  /  __/>  </ /_    / (__  )  / / / ___/
/_/ |_/\___/_/|_|\__/ __/ /____/  /_/  \/
                     /___/
EOF
echo -e "${NC}"
echo -e "${DIM}Full-Stack Project Initializer${NC}"
echo ""

# Show configuration
log_info "Project: ${BOLD}$PROJECT_NAME${NC}"
echo ""
echo -e "${CYAN}Configuration:${NC}"
[ "$WITH_AUTH" = "true" ] && echo "  ✓ Auth.js v5" || echo "  ○ Auth.js"
[ "$WITH_DB" = "true" ] && echo "  ✓ Prisma${WITH_ACCELERATE:+ + Accelerate}" || echo "  ○ Prisma"
[ "$WITH_UI" = "true" ] && echo "  ✓ ShadCN/UI" || echo "  ○ ShadCN/UI"
[ "$WITH_BIOME" = "true" ] && echo "  ✓ Biome (linting)" || echo "  ✓ ESLint + Prettier"
[ "$WITH_DOCKER" = "true" ] && echo "  ✓ Docker"
[ "$WITH_HUSKY" = "true" ] && echo "  ✓ Husky"
[ "$WITH_PLAYWRIGHT" = "true" ] && echo "  ✓ Playwright"
[ "$WITH_SANITY" = "true" ] && echo "  ✓ Sanity CMS"
[ "$WITH_MONOREPO" = "true" ] && echo "  ✓ Turborepo Monorepo"
echo ""

# ============================================================================
# STEP 1: Create Next.js Project
# ============================================================================
log_step "Creating Next.js 16 project..."

ESLINT_FLAG="--eslint"
[ "$WITH_BIOME" = "true" ] && ESLINT_FLAG=""

npx create-next-app@latest "$PROJECT_NAME" \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --turbopack \
  $ESLINT_FLAG \
  ${NO_GIT:+--no-git}

cd "$PROJECT_NAME"
log_success "Project scaffolded"

# ============================================================================
# STEP 2: Install Dependencies
# ============================================================================
log_step "Installing dependencies..."

# Core dependencies (always installed)
log_substep "Core packages..."
npm install zustand@5 @tanstack/react-query@5 clsx tailwind-merge zod

# Dev dependencies
log_substep "Dev packages..."
npm install -D @tailwindcss/postcss vitest @vitest/ui \
  @testing-library/react @testing-library/jest-dom jsdom \
  @tanstack/react-query-devtools @vitejs/plugin-react

# Biome or Prettier
if [ "$WITH_BIOME" = "true" ]; then
  log_substep "Biome..."
  npm install -D @biomejs/biome
else
  log_substep "Prettier..."
  npm install -D prettier prettier-plugin-tailwindcss
fi

# Auth dependencies
if [ "$WITH_AUTH" = "true" ]; then
  log_substep "Auth.js..."
  npm install next-auth@beta bcryptjs
  npm install -D @types/bcryptjs
fi

# Prisma dependencies
if [ "$WITH_DB" = "true" ]; then
  log_substep "Prisma..."
  npm install @prisma/client
  npm install -D prisma
  [ "$WITH_AUTH" = "true" ] && npm install @auth/prisma-adapter
  [ "$WITH_ACCELERATE" = "true" ] && npm install @prisma/extension-accelerate
fi

# Husky
if [ "$WITH_HUSKY" = "true" ]; then
  log_substep "Husky..."
  npm install -D husky lint-staged
fi

# Playwright
if [ "$WITH_PLAYWRIGHT" = "true" ]; then
  log_substep "Playwright..."
  npm install -D @playwright/test
fi

log_success "Dependencies installed"

# ============================================================================
# STEP 3: Configure Next.js 16
# ============================================================================
log_step "Configuring Next.js 16..."

cat > next.config.ts << 'EOF'
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Turbopack configuration (stable in Next.js 16)
  turbopack: {
    resolveAlias: {
      '@': './src',
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
    remotePatterns: [
      { protocol: 'https', hostname: '**.githubusercontent.com' },
      { protocol: 'https', hostname: 'avatars.githubusercontent.com' },
    ],
  },
  
  // Transpile internal packages (for monorepos)
  transpilePackages: [],
}

export default nextConfig
EOF

log_success "next.config.ts configured"

# ============================================================================
# STEP 4: Configure PostCSS for Tailwind v4
# ============================================================================
log_step "Configuring Tailwind CSS v4..."

cat > postcss.config.mjs << 'EOF'
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
EOF
rm -f postcss.config.js tailwind.config.ts tailwind.config.js 2>/dev/null || true

log_success "PostCSS configured"

# ============================================================================
# STEP 5: Create Directory Structure
# ============================================================================
log_step "Creating directory structure..."

mkdir -p src/{lib,hooks,types,test,components/ui}
mkdir -p src/app/{actions,api/health}

if [ "$WITH_AUTH" = "true" ]; then
  mkdir -p src/app/api/auth/\[...nextauth\]
  mkdir -p src/app/\(auth\)/{login,register}
  mkdir -p src/app/\(dashboard\)/dashboard
fi

log_success "Directories created"

# ============================================================================
# STEP 6: Global CSS with Tailwind v4
# ============================================================================
log_step "Creating Tailwind v4 theme..."

cat > src/app/globals.css << 'EOF'
@import "tailwindcss";

@theme {
  /* Spacing */
  --spacing: 0.25rem;
  
  /* Typography */
  --font-sans: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 
               "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, 
               Consolas, "Liberation Mono", monospace;
  
  /* Brand Colors (OKLCH for perceptual uniformity) */
  --color-brand-50: oklch(0.98 0.01 250);
  --color-brand-100: oklch(0.95 0.02 250);
  --color-brand-200: oklch(0.90 0.05 250);
  --color-brand-300: oklch(0.82 0.10 250);
  --color-brand-400: oklch(0.70 0.15 250);
  --color-brand-500: oklch(0.55 0.20 250);
  --color-brand-600: oklch(0.48 0.18 250);
  --color-brand-700: oklch(0.40 0.15 250);
  --color-brand-800: oklch(0.32 0.12 250);
  --color-brand-900: oklch(0.25 0.08 250);
  --color-brand-950: oklch(0.18 0.05 250);
  
  /* Semantic Colors */
  --color-success: oklch(0.65 0.20 145);
  --color-warning: oklch(0.75 0.18 85);
  --color-error: oklch(0.55 0.22 25);
  
  /* Breakpoints */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
  --breakpoint-3xl: 1920px;
  
  /* Animation */
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
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
  
  .dark body {
    @apply bg-slate-950 text-slate-50;
  }
}

@utility focus-ring {
  @apply focus:outline-none focus-visible:ring-2 
         focus-visible:ring-brand-500 focus-visible:ring-offset-2;
}

@utility text-balance {
  text-wrap: balance;
}

@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}
EOF

log_success "Tailwind v4 theme created"

# ============================================================================
# STEP 7: Core Library Files
# ============================================================================
log_step "Creating library files..."

# src/lib/utils.ts
cat > src/lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Merge Tailwind classes with clsx */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Format date for display */
export function formatDate(date: Date | string, options?: Intl.DateTimeFormatOptions): string {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    ...options,
  }).format(new Date(date))
}

/** Format relative time (e.g., "2 hours ago") */
export function formatRelativeTime(date: Date | string): string {
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
  const now = Date.now()
  const then = new Date(date).getTime()
  const diff = then - now
  
  const seconds = Math.round(diff / 1000)
  const minutes = Math.round(seconds / 60)
  const hours = Math.round(minutes / 60)
  const days = Math.round(hours / 24)
  
  if (Math.abs(days) >= 1) return rtf.format(days, 'day')
  if (Math.abs(hours) >= 1) return rtf.format(hours, 'hour')
  if (Math.abs(minutes) >= 1) return rtf.format(minutes, 'minute')
  return rtf.format(seconds, 'second')
}

/** Sleep utility */
export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

/** Generate a random ID */
export const generateId = (prefix = '') => 
  `${prefix}${Math.random().toString(36).slice(2, 11)}`

/** Type-safe Object.keys */
export const keys = <T extends object>(obj: T) => Object.keys(obj) as (keyof T)[]
EOF

# src/lib/queryClient.ts
cat > src/lib/queryClient.ts << 'EOF'
import { QueryClient, isServer } from '@tanstack/react-query'

function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,         // 1 minute
        gcTime: 5 * 60 * 1000,        // 5 minutes (was cacheTime)
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  })
}

let browserQueryClient: QueryClient | undefined

export function getQueryClient() {
  if (isServer) {
    // Server: always make a new query client
    return makeQueryClient()
  }
  // Browser: reuse client across renders
  if (!browserQueryClient) {
    browserQueryClient = makeQueryClient()
  }
  return browserQueryClient
}
EOF

# src/lib/store.ts
cat > src/lib/store.ts << 'EOF'
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

// ============================================================================
// App Store - UI state, preferences
// ============================================================================
interface AppState {
  theme: 'light' | 'dark' | 'system'
  setTheme: (theme: AppState['theme']) => void
  
  sidebarOpen: boolean
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        theme: 'system',
        setTheme: (theme) => set({ theme }),
        
        sidebarOpen: true,
        toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
        setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
      }),
      { 
        name: 'app-store',
        version: 1,
        partialize: (state) => ({ theme: state.theme }),
      }
    ),
    { name: 'AppStore' }
  )
)
EOF

# src/lib/actions.ts
cat > src/lib/actions.ts << 'EOF'
import { z } from 'zod'

/** Standard action result type */
export type ActionResult<T = void> = 
  | { success: true; data: T }
  | { success: false; error: string; code?: string; fieldErrors?: Record<string, string[]> }

/** Success response helper */
export const success = <T>(data: T): ActionResult<T> => ({ success: true, data })

/** Error response helper */
export const error = (message: string, code?: string): ActionResult<never> => ({
  success: false,
  error: message,
  code,
})

/** Validation error helper */
export const validationError = (
  fieldErrors: Record<string, string[]>
): ActionResult<never> => ({
  success: false,
  error: 'Validation failed',
  code: 'VALIDATION_ERROR',
  fieldErrors,
})

/** Create a type-safe server action with Zod validation */
export function createAction<TInput, TOutput>(
  schema: z.ZodSchema<TInput>,
  handler: (input: TInput) => Promise<TOutput>
): (formData: FormData) => Promise<ActionResult<TOutput>> {
  return async (formData: FormData) => {
    try {
      const raw = Object.fromEntries(formData)
      const result = schema.safeParse(raw)
      
      if (!result.success) {
        return validationError(result.error.flatten().fieldErrors as Record<string, string[]>)
      }
      
      const data = await handler(result.data)
      return success(data)
    } catch (e) {
      console.error('Action error:', e)
      return error('An unexpected error occurred', 'UNKNOWN_ERROR')
    }
  }
}
EOF

log_success "Library files created"

# ============================================================================
# STEP 8: Providers
# ============================================================================
log_step "Creating providers..."

if [ "$WITH_AUTH" = "true" ]; then
  cat > src/components/providers.tsx << 'EOF'
'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { SessionProvider } from 'next-auth/react'
import { getQueryClient } from '@/lib/queryClient'

export function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient()

  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        {children}
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </SessionProvider>
  )
}
EOF
else
  cat > src/components/providers.tsx << 'EOF'
'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { getQueryClient } from '@/lib/queryClient'

export function Providers({ children }: { children: React.ReactNode }) {
  const queryClient = getQueryClient()

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
EOF
fi

log_success "Providers created"

# ============================================================================
# STEP 9: Layout and Pages
# ============================================================================
log_step "Creating pages..."

# Root layout
cat > src/app/layout.tsx << 'EOF'
import type { Metadata, Viewport } from 'next'
import { Providers } from '@/components/providers'
import './globals.css'

export const metadata: Metadata = {
  title: {
    default: 'My App',
    template: '%s | My App',
  },
  description: 'Built with Next.js 16',
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
}

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
  width: 'device-width',
  initialScale: 1,
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
EOF

# Home page
cat > src/app/page.tsx << 'EOF'
import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl text-balance">
          Welcome to{' '}
          <span className="text-brand-500">Next.js 16</span>
        </h1>
        
        <p className="mt-6 text-lg text-slate-600 text-balance">
          Production-ready full-stack application with React 19, 
          Tailwind CSS v4, and the React Compiler.
        </p>
        
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/dashboard"
            className="rounded-lg bg-brand-500 px-6 py-3 font-medium text-white 
                       hover:bg-brand-600 focus-ring transition-colors"
          >
            Go to Dashboard
          </Link>
          
          <a
            href="https://nextjs.org/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border border-slate-300 px-6 py-3 font-medium 
                       hover:bg-slate-50 focus-ring transition-colors"
          >
            Documentation →
          </a>
        </div>
        
        <div className="mt-16 grid gap-4 sm:grid-cols-3">
          <FeatureCard
            title="React Compiler"
            description="Automatic memoization for optimal performance"
          />
          <FeatureCard
            title="Turbopack"
            description="Lightning-fast dev server and builds"
          />
          <FeatureCard
            title="Tailwind v4"
            description="CSS-first configuration with OKLCH colors"
          />
        </div>
      </div>
    </main>
  )
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-xl border border-slate-200 p-6 text-left hover:border-brand-300 transition-colors">
      <h3 className="font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-slate-600">{description}</p>
    </div>
  )
}
EOF

# Error page
cat > src/app/error.tsx << 'EOF'
'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Error:', error)
  }, [error])

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-6">
      <div className="rounded-full bg-red-100 p-4">
        <svg className="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <div className="text-center">
        <h2 className="text-2xl font-bold">Something went wrong!</h2>
        <p className="mt-2 max-w-md text-slate-600">
          {error.message || 'An unexpected error occurred'}
        </p>
        {error.digest && (
          <p className="mt-2 text-sm text-slate-400">Error ID: {error.digest}</p>
        )}
      </div>
      <button
        onClick={reset}
        className="rounded-lg bg-brand-500 px-6 py-2.5 font-medium text-white 
                   hover:bg-brand-600 focus-ring transition-colors"
      >
        Try again
      </button>
    </main>
  )
}
EOF

# Loading page
cat > src/app/loading.tsx << 'EOF'
export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    </div>
  )
}
EOF

# Not found page
cat > src/app/not-found.tsx << 'EOF'
import Link from 'next/link'

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-6">
      <h1 className="text-8xl font-bold text-slate-200">404</h1>
      <div className="text-center">
        <h2 className="text-2xl font-bold">Page Not Found</h2>
        <p className="mt-2 text-slate-600">
          The page you're looking for doesn't exist.
        </p>
      </div>
      <Link
        href="/"
        className="rounded-lg bg-brand-500 px-6 py-2.5 font-medium text-white 
                   hover:bg-brand-600 focus-ring transition-colors"
      >
        Go Home
      </Link>
    </main>
  )
}
EOF

# Health API
cat > src/app/api/health/route.ts << 'EOF'
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '0.0.0',
    environment: process.env.NODE_ENV,
  })
}
EOF

log_success "Pages created"

# ============================================================================
# STEP 10: Testing Setup (Vitest)
# ============================================================================
log_step "Setting up Vitest..."

cat > vitest.config.mts << 'EOF'
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
EOF

npm install -D vite-tsconfig-paths

cat > src/test/setup.ts << 'EOF'
import '@testing-library/jest-dom/vitest'
import { afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// Cleanup after each test
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
EOF

# Example test
cat > src/lib/utils.test.ts << 'EOF'
import { describe, it, expect } from 'vitest'
import { cn, formatDate, generateId } from './utils'

describe('cn', () => {
  it('merges class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar')
  })

  it('handles conditional classes', () => {
    expect(cn('base', false && 'hidden', true && 'visible')).toBe('base visible')
  })

  it('merges tailwind classes correctly', () => {
    expect(cn('px-2 py-1', 'px-4')).toBe('py-1 px-4')
  })
})

describe('formatDate', () => {
  it('formats date correctly', () => {
    const date = new Date('2025-01-15')
    const formatted = formatDate(date)
    expect(formatted).toContain('Jan')
    expect(formatted).toContain('15')
  })
})

describe('generateId', () => {
  it('generates unique ids', () => {
    const id1 = generateId()
    const id2 = generateId()
    expect(id1).not.toBe(id2)
  })

  it('supports prefix', () => {
    const id = generateId('user_')
    expect(id.startsWith('user_')).toBe(true)
  })
})
EOF

log_success "Vitest configured"

# ============================================================================
# STEP 11: Linting/Formatting (Biome or ESLint + Prettier)
# ============================================================================
log_step "Configuring linting..."

if [ "$WITH_BIOME" = "true" ]; then
  cat > biome.json << 'EOF'
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
      },
      "style": {
        "noNonNullAssertion": "off"
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
EOF
  log_success "Biome configured"
else
  # ESLint flat config (Next.js 16)
  cat > eslint.config.mjs << 'EOF'
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
    },
  },
  {
    ignores: ['.next/**', 'node_modules/**', 'dist/**'],
  },
]

export default eslintConfig
EOF

  npm install -D @eslint/eslintrc

  # Prettier config
  cat > .prettierrc << 'EOF'
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
EOF

  cat > .prettierignore << 'EOF'
.next
node_modules
dist
pnpm-lock.yaml
package-lock.json
EOF

  log_success "ESLint + Prettier configured"
fi

# ============================================================================
# STEP 12: Environment Files
# ============================================================================
log_step "Creating environment files..."

cat > .env.local << EOF
# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development
EOF

cat > .env.example << 'EOF'
# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development

# Database (Prisma)
DATABASE_URL="postgresql://user:password@localhost:5432/mydb?schema=public"
# For Prisma Accelerate (optional):
# DATABASE_URL="prisma://accelerate.prisma-data.net/?api_key=YOUR_KEY"
# DIRECT_URL="postgresql://user:password@localhost:5432/mydb"

# Auth.js
AUTH_SECRET="generate-with: openssl rand -base64 32"
AUTH_URL="http://localhost:3000"

# OAuth Providers (optional)
AUTH_GITHUB_ID=""
AUTH_GITHUB_SECRET=""
AUTH_GOOGLE_ID=""
AUTH_GOOGLE_SECRET=""
EOF

log_success "Environment files created"

# ============================================================================
# STEP 13: Package.json Scripts
# ============================================================================
log_step "Configuring scripts..."

npm pkg set scripts.dev="next dev --turbo"
npm pkg set scripts.build="next build"
npm pkg set scripts.start="next start"
npm pkg set scripts.test="vitest"
npm pkg set scripts.test:ui="vitest --ui"
npm pkg set scripts.test:coverage="vitest run --coverage"
npm pkg set scripts.typecheck="tsc --noEmit"

if [ "$WITH_BIOME" = "true" ]; then
  npm pkg set scripts.lint="biome check ."
  npm pkg set scripts.lint:fix="biome check --write ."
  npm pkg set scripts.format="biome format --write ."
else
  npm pkg set scripts.lint="next lint"
  npm pkg set scripts.lint:fix="next lint --fix"
  npm pkg set scripts.format="prettier --write ."
  npm pkg set scripts.format:check="prettier --check ."
fi

log_success "Scripts configured"

# ============================================================================
# STEP 14: VS Code Settings
# ============================================================================
log_step "Creating VS Code settings..."

mkdir -p .vscode

cat > .vscode/settings.json << 'EOF'
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.organizeImports": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "tailwindCSS.experimental.classRegex": [
    ["cn\\(([^)]*)\\)", "(?:'|\"|`)([^']*)(?:'|\"|`)"]
  ],
  "files.associations": {
    "*.css": "tailwindcss"
  }
}
EOF

if [ "$WITH_BIOME" = "true" ]; then
  cat > .vscode/settings.json << 'EOF'
{
  "editor.defaultFormatter": "biomejs.biome",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "quickfix.biome": "explicit",
    "source.organizeImports.biome": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "tailwindCSS.experimental.classRegex": [
    ["cn\\(([^)]*)\\)", "(?:'|\"|`)([^']*)(?:'|\"|`)"]
  ],
  "files.associations": {
    "*.css": "tailwindcss"
  }
}
EOF
fi

cat > .vscode/extensions.json << 'EOF'
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "biomejs.biome",
    "prisma.prisma"
  ]
}
EOF

log_success "VS Code settings created"

# ============================================================================
# OPTIONAL: Auth.js v5 Setup
# ============================================================================
if [ "$WITH_AUTH" = "true" ]; then
  log_step "Setting up Auth.js v5..."
  
  # Edge-compatible config (no database imports)
  cat > src/auth.config.ts << 'EOF'
import type { NextAuthConfig } from 'next-auth'

export default {
  pages: {
    signIn: '/login',
    error: '/login',
  },
  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user
      const isOnDashboard = nextUrl.pathname.startsWith('/dashboard')
      const isOnAuth = nextUrl.pathname.startsWith('/login') || 
                       nextUrl.pathname.startsWith('/register')
      
      if (isOnDashboard) {
        return isLoggedIn
      }
      if (isOnAuth && isLoggedIn) {
        return Response.redirect(new URL('/dashboard', nextUrl))
      }
      return true
    },
  },
  providers: [], // Configured in auth.ts
} satisfies NextAuthConfig
EOF

  # Full auth config with database
  if [ "$WITH_DB" = "true" ]; then
    cat > src/auth.ts << 'EOF'
import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'
import Google from 'next-auth/providers/google'
import Credentials from 'next-auth/providers/credentials'
import { PrismaAdapter } from '@auth/prisma-adapter'
import bcrypt from 'bcryptjs'
import { prisma } from '@/lib/prisma'
import authConfig from './auth.config'

export const { handlers, auth, signIn, signOut } = NextAuth({
  ...authConfig,
  adapter: PrismaAdapter(prisma),
  session: { strategy: 'jwt' },
  providers: [
    GitHub, // Auto-reads AUTH_GITHUB_ID, AUTH_GITHUB_SECRET
    Google, // Auto-reads AUTH_GOOGLE_ID, AUTH_GOOGLE_SECRET
    Credentials({
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null
        
        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string },
        })
        
        if (!user?.hashedPassword) return null
        
        const isValid = await bcrypt.compare(
          credentials.password as string,
          user.hashedPassword
        )
        
        if (!isValid) return null
        
        return { id: user.id, email: user.email, name: user.name, image: user.image }
      },
    }),
  ],
  callbacks: {
    ...authConfig.callbacks,
    jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    session({ session, token }) {
      if (session.user && token.id) {
        session.user.id = token.id as string
      }
      return session
    },
  },
})
EOF
  else
    cat > src/auth.ts << 'EOF'
import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'
import Google from 'next-auth/providers/google'
import Credentials from 'next-auth/providers/credentials'
import authConfig from './auth.config'

export const { handlers, auth, signIn, signOut } = NextAuth({
  ...authConfig,
  session: { strategy: 'jwt' },
  providers: [
    GitHub,
    Google,
    Credentials({
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        // Demo user - replace with database lookup
        if (credentials?.email === 'demo@example.com' && 
            credentials?.password === 'password123') {
          return { id: '1', email: 'demo@example.com', name: 'Demo User' }
        }
        return null
      },
    }),
  ],
  callbacks: {
    ...authConfig.callbacks,
    jwt({ token, user }) {
      if (user) token.id = user.id
      return token
    },
    session({ session, token }) {
      if (session.user && token.id) {
        session.user.id = token.id as string
      }
      return session
    },
  },
})
EOF
  fi

  # Route handler
  cat > src/app/api/auth/\[...nextauth\]/route.ts << 'EOF'
import { handlers } from '@/auth'
export const { GET, POST } = handlers
EOF

  # Middleware (uses Edge-safe config)
  cat > src/middleware.ts << 'EOF'
import NextAuth from 'next-auth'
import authConfig from './auth.config'

export default NextAuth(authConfig).auth

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|public).*)'],
}
EOF

  # Auth actions
  cat > src/app/actions/auth.ts << 'EOF'
'use server'

import { signIn, signOut } from '@/auth'
import { AuthError } from 'next-auth'
import { z } from 'zod'

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export type AuthState = {
  error?: string
  fieldErrors?: Record<string, string[]>
}

export async function login(
  prevState: AuthState,
  formData: FormData
): Promise<AuthState> {
  const raw = Object.fromEntries(formData)
  const result = loginSchema.safeParse(raw)
  
  if (!result.success) {
    return { fieldErrors: result.error.flatten().fieldErrors }
  }
  
  try {
    await signIn('credentials', {
      email: result.data.email,
      password: result.data.password,
      redirectTo: '/dashboard',
    })
    return {}
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

export async function loginWithGitHub() {
  await signIn('github', { redirectTo: '/dashboard' })
}

export async function loginWithGoogle() {
  await signIn('google', { redirectTo: '/dashboard' })
}

export async function logout() {
  await signOut({ redirectTo: '/' })
}
EOF

  # Type extensions
  cat > src/types/next-auth.d.ts << 'EOF'
import { DefaultSession, DefaultUser } from 'next-auth'
import { DefaultJWT } from 'next-auth/jwt'

declare module 'next-auth' {
  interface Session {
    user: { id: string } & DefaultSession['user']
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
EOF

  # Login page
  cat > src/app/\(auth\)/login/page.tsx << 'EOF'
import { LoginForm } from './login-form'

export const metadata = { title: 'Sign In' }

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold">Welcome back</h1>
          <p className="mt-2 text-slate-600">Sign in to your account</p>
        </div>
        
        <LoginForm />
        
        <p className="text-center text-sm text-slate-600">
          Don't have an account?{' '}
          <a href="/register" className="text-brand-600 hover:underline">Sign up</a>
        </p>
      </div>
    </main>
  )
}
EOF

  # Login form
  cat > src/app/\(auth\)/login/login-form.tsx << 'EOF'
'use client'

import { useActionState } from 'react'
import { useFormStatus } from 'react-dom'
import { login, loginWithGitHub, loginWithGoogle, type AuthState } from '@/app/actions/auth'

function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button
      type="submit"
      disabled={pending}
      className="w-full rounded-lg bg-brand-500 py-2.5 font-medium text-white 
                 hover:bg-brand-600 disabled:opacity-50 focus-ring transition-colors"
    >
      {pending ? 'Signing in...' : 'Sign in'}
    </button>
  )
}

export function LoginForm() {
  const [state, action] = useActionState<AuthState, FormData>(login, {})
  
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3">
        <form action={loginWithGitHub}>
          <button type="submit" className="flex w-full items-center justify-center gap-2 
                   rounded-lg border py-2.5 hover:bg-slate-50 focus-ring transition-colors">
            <GitHubIcon className="h-5 w-5" />
            GitHub
          </button>
        </form>
        <form action={loginWithGoogle}>
          <button type="submit" className="flex w-full items-center justify-center gap-2 
                   rounded-lg border py-2.5 hover:bg-slate-50 focus-ring transition-colors">
            <GoogleIcon className="h-5 w-5" />
            Google
          </button>
        </form>
      </div>
      
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="bg-white px-4 text-slate-500">or</span>
        </div>
      </div>
      
      <form action={action} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            className="mt-1 w-full rounded-lg border px-3 py-2 focus:border-brand-500 
                       focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
          {state.fieldErrors?.email && (
            <p className="mt-1 text-sm text-red-500">{state.fieldErrors.email[0]}</p>
          )}
        </div>
        
        <div>
          <label htmlFor="password" className="block text-sm font-medium">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            className="mt-1 w-full rounded-lg border px-3 py-2 focus:border-brand-500 
                       focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
          {state.fieldErrors?.password && (
            <p className="mt-1 text-sm text-red-500">{state.fieldErrors.password[0]}</p>
          )}
        </div>
        
        {state.error && (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">{state.error}</div>
        )}
        
        <SubmitButton />
      </form>
    </div>
  )
}

function GitHubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
  )
}

function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  )
}
EOF

  # Dashboard page
  cat > src/app/\(dashboard\)/dashboard/page.tsx << 'EOF'
import { auth } from '@/auth'
import { redirect } from 'next/navigation'
import { logout } from '@/app/actions/auth'

export const metadata = { title: 'Dashboard' }

export default async function DashboardPage() {
  const session = await auth()
  if (!session?.user) redirect('/login')
  
  return (
    <main className="min-h-screen p-6">
      <div className="mx-auto max-w-4xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <p className="text-slate-600">Welcome, {session.user.name || session.user.email}</p>
          </div>
          <form action={logout}>
            <button type="submit" className="rounded-lg border px-4 py-2 text-sm 
                       hover:bg-slate-50 focus-ring transition-colors">
              Sign out
            </button>
          </form>
        </div>
        
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          <StatCard title="Total Users" value="1,234" change="+12%" />
          <StatCard title="Active Now" value="567" change="+5%" />
          <StatCard title="Revenue" value="$12,345" change="+18%" />
        </div>
        
        <div className="mt-8 rounded-xl border p-6">
          <h2 className="text-lg font-semibold">Your Profile</h2>
          <dl className="mt-4 space-y-3">
            <div className="flex justify-between">
              <dt className="text-slate-600">Email</dt>
              <dd className="font-medium">{session.user.email}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-600">User ID</dt>
              <dd className="font-mono text-sm text-slate-500">{session.user.id}</dd>
            </div>
          </dl>
        </div>
      </div>
    </main>
  )
}

function StatCard({ title, value, change }: { title: string; value: string; change: string }) {
  return (
    <div className="rounded-xl border p-6">
      <p className="text-sm text-slate-600">{title}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
      <p className={`mt-1 text-sm ${change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
        {change} from last month
      </p>
    </div>
  )
}
EOF

  # Update .env.local
  cat >> .env.local << 'EOF'

# Auth.js
AUTH_SECRET="change-me-run-openssl-rand-base64-32"
AUTH_URL="http://localhost:3000"

# OAuth (auto-detected by Auth.js)
# AUTH_GITHUB_ID=""
# AUTH_GITHUB_SECRET=""
# AUTH_GOOGLE_ID=""
# AUTH_GOOGLE_SECRET=""
EOF

  log_success "Auth.js v5 configured"
fi

# ============================================================================
# OPTIONAL: Prisma Setup
# ============================================================================
if [ "$WITH_DB" = "true" ]; then
  log_step "Setting up Prisma..."
  
  npx prisma init --datasource-provider postgresql --skip-generate
  
  # Prisma schema with auth models if needed
  if [ "$WITH_AUTH" = "true" ]; then
    cat > prisma/schema.prisma << 'EOF'
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL") // For Prisma Accelerate
}

// ============================================================================
// Auth.js Models
// ============================================================================

model User {
  id             String    @id @default(cuid())
  name           String?
  email          String?   @unique
  emailVerified  DateTime? @map("email_verified")
  image          String?
  hashedPassword String?   @map("hashed_password")
  createdAt      DateTime  @default(now()) @map("created_at")
  updatedAt      DateTime  @updatedAt @map("updated_at")
  accounts       Account[]
  sessions       Session[]

  @@map("users")
}

model Account {
  id                String  @id @default(cuid())
  userId            String  @map("user_id")
  type              String
  provider          String
  providerAccountId String  @map("provider_account_id")
  refresh_token     String? @db.Text
  access_token      String? @db.Text
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String? @db.Text
  session_state     String?
  user              User    @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
  @@map("accounts")
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique @map("session_token")
  userId       String   @map("user_id")
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
  @@map("verification_tokens")
}

// ============================================================================
// Application Models (add your own here)
// ============================================================================
EOF
  else
    cat > prisma/schema.prisma << 'EOF'
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL") // For Prisma Accelerate
}

// ============================================================================
// Application Models
// ============================================================================

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  @@map("users")
}
EOF
  fi

  # Prisma client singleton
  if [ "$WITH_ACCELERATE" = "true" ]; then
    cat > src/lib/prisma.ts << 'EOF'
import { PrismaClient } from '@prisma/client'
import { withAccelerate } from '@prisma/extension-accelerate'

const prismaClientSingleton = () => {
  return new PrismaClient().$extends(withAccelerate())
}

declare const globalThis: {
  prismaGlobal: ReturnType<typeof prismaClientSingleton>
} & typeof global

export const prisma = globalThis.prismaGlobal ?? prismaClientSingleton()

if (process.env.NODE_ENV !== 'production') {
  globalThis.prismaGlobal = prisma
}
EOF
  else
    cat > src/lib/prisma.ts << 'EOF'
import { PrismaClient } from '@prisma/client'

const prismaClientSingleton = () => {
  return new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  })
}

declare const globalThis: {
  prismaGlobal: ReturnType<typeof prismaClientSingleton>
} & typeof global

export const prisma = globalThis.prismaGlobal ?? prismaClientSingleton()

if (process.env.NODE_ENV !== 'production') {
  globalThis.prismaGlobal = prisma
}
EOF
  fi

  # Database scripts
  npm pkg set scripts.db:generate="prisma generate"
  npm pkg set scripts.db:push="prisma db push"
  npm pkg set scripts.db:migrate="prisma migrate dev"
  npm pkg set scripts.db:studio="prisma studio"
  npm pkg set scripts.db:seed="prisma db seed"

  # Update .env.local
  cat >> .env.local << 'EOF'

# Database
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/mydb?schema=public"
# DIRECT_URL="postgresql://postgres:postgres@localhost:5432/mydb" # For Accelerate
EOF

  log_success "Prisma configured"
fi

# ============================================================================
# OPTIONAL: ShadCN/UI Setup
# ============================================================================
if [ "$WITH_UI" = "true" ]; then
  log_step "Setting up ShadCN/UI..."
  
  npx shadcn@latest init -y -d
  npx shadcn@latest add button card input label -y
  
  log_success "ShadCN/UI configured"
fi

# ============================================================================
# OPTIONAL: Docker Setup
# ============================================================================
if [ "$WITH_DOCKER" = "true" ]; then
  log_step "Setting up Docker..."
  
  cat > Dockerfile << 'EOF'
# syntax=docker/dockerfile:1
FROM node:22-alpine AS base

# Dependencies
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# Build
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Production
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
EOF

  cat > docker-compose.yml << 'EOF'
services:
  app:
    build: .
    ports:
      - '3000:3000'
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
      - AUTH_SECRET=${AUTH_SECRET}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    ports:
      - '5432:5432'
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U postgres']
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF

  cat > .dockerignore << 'EOF'
.git
.next
node_modules
npm-debug.log
.env*.local
Dockerfile
docker-compose.yml
.dockerignore
README.md
EOF

  npm pkg set scripts.docker:build="docker build -t my-app ."
  npm pkg set scripts.docker:up="docker compose up -d"
  npm pkg set scripts.docker:down="docker compose down"
  npm pkg set scripts.docker:logs="docker compose logs -f"

  log_success "Docker configured"
fi

# ============================================================================
# OPTIONAL: Husky Setup
# ============================================================================
if [ "$WITH_HUSKY" = "true" ]; then
  log_step "Setting up Husky..."
  
  npx husky init
  
  if [ "$WITH_BIOME" = "true" ]; then
    echo "npx biome check --staged" > .husky/pre-commit
  else
    echo "npx lint-staged" > .husky/pre-commit
    
    cat > .lintstagedrc.json << 'EOF'
{
  "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
  "*.{json,md,css}": ["prettier --write"]
}
EOF
  fi
  
  log_success "Husky configured"
fi

# ============================================================================
# OPTIONAL: Playwright Setup
# ============================================================================
if [ "$WITH_PLAYWRIGHT" = "true" ]; then
  log_step "Setting up Playwright..."
  
  npx playwright install --with-deps chromium
  
  cat > playwright.config.ts << 'EOF'
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
EOF

  mkdir -p e2e
  
  cat > e2e/home.spec.ts << 'EOF'
import { test, expect } from '@playwright/test'

test('homepage has title', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/My App/)
})

test('homepage has welcome heading', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /Welcome to Next.js/i })).toBeVisible()
})
EOF

  npm pkg set scripts.e2e="playwright test"
  npm pkg set scripts.e2e:ui="playwright test --ui"
  npm pkg set scripts.e2e:report="playwright show-report"

  log_success "Playwright configured"
fi

# ============================================================================
# OPTIONAL: Sanity CMS Setup
# ============================================================================
if [ "$WITH_SANITY" = "true" ]; then
  log_step "Setting up Sanity CMS..."
  
  # Install Sanity dependencies
  log_substep "Installing Sanity packages..."
  npm install sanity next-sanity @sanity/image-url @sanity/vision @portabletext/react
  
  # Create Sanity directory structure
  mkdir -p src/sanity/{schemaTypes,lib}
  mkdir -p src/app/studio/\[\[...tool\]\]
  mkdir -p src/app/api/draft-mode/enable
  mkdir -p src/app/api/revalidate
  
  # sanity.config.ts
  cat > sanity.config.ts << 'EOF'
import { defineConfig } from 'sanity'
import { structureTool } from 'sanity/structure'
import { visionTool } from '@sanity/vision'
import { presentationTool } from 'sanity/presentation'
import { schemaTypes } from './src/sanity/schemaTypes'

export default defineConfig({
  name: 'default',
  title: 'My App',
  
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  
  plugins: [
    structureTool(),
    visionTool({ defaultApiVersion: '2024-12-01' }),
    presentationTool({
      previewUrl: {
        draftMode: {
          enable: '/api/draft-mode/enable',
        },
      },
    }),
  ],
  
  schema: {
    types: schemaTypes,
  },
})
EOF

  # sanity.cli.ts
  cat > sanity.cli.ts << 'EOF'
import { defineCliConfig } from 'sanity/cli'

export default defineCliConfig({
  api: {
    projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
    dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
  },
  studioHost: 'my-app', // Change this to your studio hostname
  autoUpdates: true,
})
EOF

  # Schema types index
  cat > src/sanity/schemaTypes/index.ts << 'EOF'
import { post } from './post'
import { author } from './author'
import { blockContent } from './blockContent'

export const schemaTypes = [post, author, blockContent]
EOF

  # Post schema
  cat > src/sanity/schemaTypes/post.ts << 'EOF'
import { defineType, defineField } from 'sanity'

export const post = defineType({
  name: 'post',
  title: 'Post',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (rule) => rule.required().min(5).max(100),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: { source: 'title', maxLength: 96 },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'author',
      title: 'Author',
      type: 'reference',
      to: [{ type: 'author' }],
    }),
    defineField({
      name: 'mainImage',
      title: 'Main Image',
      type: 'image',
      options: { hotspot: true },
      fields: [
        defineField({
          name: 'alt',
          title: 'Alt Text',
          type: 'string',
          validation: (rule) => rule.required(),
        }),
      ],
    }),
    defineField({
      name: 'publishedAt',
      title: 'Published At',
      type: 'datetime',
    }),
    defineField({
      name: 'body',
      title: 'Body',
      type: 'blockContent',
    }),
  ],
  preview: {
    select: {
      title: 'title',
      author: 'author.name',
      media: 'mainImage',
    },
    prepare({ title, author, media }) {
      return {
        title,
        subtitle: author ? `by ${author}` : '',
        media,
      }
    },
  },
})
EOF

  # Author schema
  cat > src/sanity/schemaTypes/author.ts << 'EOF'
import { defineType, defineField } from 'sanity'

export const author = defineType({
  name: 'author',
  title: 'Author',
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: { source: 'name' },
    }),
    defineField({
      name: 'image',
      title: 'Image',
      type: 'image',
      options: { hotspot: true },
    }),
    defineField({
      name: 'bio',
      title: 'Bio',
      type: 'text',
      rows: 4,
    }),
  ],
  preview: {
    select: { title: 'name', media: 'image' },
  },
})
EOF

  # Block content schema
  cat > src/sanity/schemaTypes/blockContent.ts << 'EOF'
import { defineType, defineArrayMember } from 'sanity'

export const blockContent = defineType({
  name: 'blockContent',
  title: 'Block Content',
  type: 'array',
  of: [
    defineArrayMember({
      type: 'block',
      styles: [
        { title: 'Normal', value: 'normal' },
        { title: 'H2', value: 'h2' },
        { title: 'H3', value: 'h3' },
        { title: 'H4', value: 'h4' },
        { title: 'Quote', value: 'blockquote' },
      ],
      lists: [
        { title: 'Bullet', value: 'bullet' },
        { title: 'Numbered', value: 'number' },
      ],
      marks: {
        decorators: [
          { title: 'Bold', value: 'strong' },
          { title: 'Italic', value: 'em' },
          { title: 'Code', value: 'code' },
        ],
        annotations: [
          {
            name: 'link',
            type: 'object',
            title: 'Link',
            fields: [
              {
                name: 'href',
                type: 'url',
                title: 'URL',
                validation: (rule) =>
                  rule.uri({ allowRelative: true, scheme: ['http', 'https', 'mailto', 'tel'] }),
              },
            ],
          },
        ],
      },
    }),
    defineArrayMember({
      type: 'image',
      options: { hotspot: true },
      fields: [
        {
          name: 'alt',
          type: 'string',
          title: 'Alt Text',
        },
        {
          name: 'caption',
          type: 'string',
          title: 'Caption',
        },
      ],
    }),
  ],
})
EOF

  # Sanity client
  cat > src/sanity/lib/client.ts << 'EOF'
import { createClient } from 'next-sanity'

export const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  apiVersion: '2024-12-01',
  useCdn: process.env.NODE_ENV === 'production',
  stega: {
    studioUrl: process.env.NEXT_PUBLIC_SANITY_STUDIO_URL || '/studio',
  },
})
EOF

  # Live Content API
  cat > src/sanity/lib/live.ts << 'EOF'
import { defineLive } from 'next-sanity'
import { client } from './client'

const token = process.env.SANITY_API_READ_TOKEN

export const { sanityFetch, SanityLive } = defineLive({
  client,
  serverToken: token,
  browserToken: token,
})
EOF

  # Image URL builder
  cat > src/sanity/lib/image.ts << 'EOF'
import imageUrlBuilder from '@sanity/image-url'
import { client } from './client'
import type { SanityImageSource } from '@sanity/image-url/lib/types/types'

const builder = imageUrlBuilder(client)

export function urlFor(source: SanityImageSource) {
  return builder.image(source)
}
EOF

  # GROQ Queries
  cat > src/sanity/lib/queries.ts << 'EOF'
import { defineQuery } from 'next-sanity'

export const POSTS_QUERY = defineQuery(`
  *[_type == "post" && defined(slug.current)] | order(publishedAt desc) {
    _id,
    title,
    "slug": slug.current,
    publishedAt,
    mainImage,
    author->{ name, image }
  }
`)

export const POST_BY_SLUG_QUERY = defineQuery(`
  *[_type == "post" && slug.current == $slug][0] {
    _id,
    title,
    "slug": slug.current,
    body,
    mainImage,
    publishedAt,
    author->{ name, image, bio }
  }
`)

export const AUTHORS_QUERY = defineQuery(`
  *[_type == "author"] | order(name asc) {
    _id,
    name,
    "slug": slug.current,
    image,
    bio
  }
`)
EOF

  # Embedded Studio page
  cat > src/app/studio/\[\[...tool\]\]/page.tsx << 'EOF'
'use client'

import { NextStudio } from 'next-sanity/studio'
import config from '../../../../sanity.config'

export default function StudioPage() {
  return <NextStudio config={config} />
}
EOF

  # Studio layout (prevents body styles)
  cat > src/app/studio/\[\[...tool\]\]/layout.tsx << 'EOF'
export const metadata = {
  title: 'Studio',
}

export default function StudioLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>{children}</body>
    </html>
  )
}
EOF

  # Draft mode enable route
  cat > src/app/api/draft-mode/enable/route.ts << 'EOF'
import { client } from '@/sanity/lib/client'
import { defineEnableDraftMode } from 'next-sanity/draft-mode'

export const { GET } = defineEnableDraftMode({
  client: client.withConfig({
    token: process.env.SANITY_API_READ_TOKEN,
  }),
})
EOF

  # Revalidation webhook
  cat > src/app/api/revalidate/route.ts << 'EOF'
import { revalidateTag } from 'next/cache'
import { parseBody } from 'next-sanity/webhook'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const { body, isValidSignature } = await parseBody<{
      _type: string
      slug?: { current?: string }
    }>(request, process.env.SANITY_WEBHOOK_SECRET)

    if (!isValidSignature) {
      return NextResponse.json({ message: 'Invalid signature' }, { status: 401 })
    }

    if (!body?._type) {
      return NextResponse.json({ message: 'Bad request' }, { status: 400 })
    }

    revalidateTag(body._type)
    if (body.slug?.current) {
      revalidateTag(`${body._type}:${body.slug.current}`)
    }

    return NextResponse.json({ revalidated: true, now: Date.now() })
  } catch (err) {
    console.error(err)
    return NextResponse.json({ message: 'Error revalidating' }, { status: 500 })
  }
}
EOF

  # Portable Text component
  cat > src/components/portable-text.tsx << 'EOF'
import { PortableText as BasePortableText, type PortableTextComponents } from '@portabletext/react'
import Image from 'next/image'
import Link from 'next/link'
import { urlFor } from '@/sanity/lib/image'

const components: PortableTextComponents = {
  types: {
    image: ({ value }) => {
      if (!value?.asset) return null
      return (
        <figure className="my-8">
          <Image
            src={urlFor(value).width(800).url()}
            alt={value.alt || ''}
            width={800}
            height={450}
            className="rounded-lg"
          />
          {value.caption && (
            <figcaption className="mt-2 text-center text-sm text-slate-500">
              {value.caption}
            </figcaption>
          )}
        </figure>
      )
    },
  },
  marks: {
    link: ({ value, children }) => {
      const href = value?.href || ''
      const isExternal = href.startsWith('http')
      return isExternal ? (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-brand-600 hover:underline"
        >
          {children}
        </a>
      ) : (
        <Link href={href} className="text-brand-600 hover:underline">
          {children}
        </Link>
      )
    },
  },
  block: {
    h2: ({ children }) => <h2 className="mt-8 mb-4 text-2xl font-bold">{children}</h2>,
    h3: ({ children }) => <h3 className="mt-6 mb-3 text-xl font-semibold">{children}</h3>,
    h4: ({ children }) => <h4 className="mt-4 mb-2 text-lg font-medium">{children}</h4>,
    blockquote: ({ children }) => (
      <blockquote className="my-6 border-l-4 border-brand-500 pl-4 italic text-slate-600">
        {children}
      </blockquote>
    ),
  },
  list: {
    bullet: ({ children }) => <ul className="my-4 ml-6 list-disc space-y-2">{children}</ul>,
    number: ({ children }) => <ol className="my-4 ml-6 list-decimal space-y-2">{children}</ol>,
  },
}

export function PortableText({ value }: { value: any }) {
  return <BasePortableText value={value} components={components} />
}
EOF

  # Update next.config.ts to add Sanity image domain
  cat > next.config.ts << 'EOF'
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  turbopack: {
    resolveAlias: {
      '@': './src',
    },
  },
  
  reactCompiler: true,
  output: 'standalone',
  
  serverActions: {
    bodySizeLimit: '5mb',
  },
  
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**.githubusercontent.com' },
      { protocol: 'https', hostname: 'avatars.githubusercontent.com' },
      { protocol: 'https', hostname: 'cdn.sanity.io' },
    ],
  },
  
  transpilePackages: [],
}

export default nextConfig
EOF

  # Update .env.local with Sanity vars
  cat >> .env.local << 'EOF'

# Sanity CMS
NEXT_PUBLIC_SANITY_PROJECT_ID="your-project-id"
NEXT_PUBLIC_SANITY_DATASET="production"
NEXT_PUBLIC_SANITY_STUDIO_URL="/studio"
SANITY_API_READ_TOKEN=""  # Get from sanity.io/manage -> API -> Tokens (Viewer)
SANITY_WEBHOOK_SECRET=""  # For revalidation webhook
EOF

  # Add Sanity scripts
  npm pkg set scripts.sanity:dev="sanity dev"
  npm pkg set scripts.sanity:build="sanity build"
  npm pkg set scripts.sanity:deploy="sanity deploy"
  npm pkg set scripts.typegen="sanity schema extract --enforce-required-fields && sanity typegen generate"

  log_success "Sanity CMS configured"
  log_warn "Remember to set NEXT_PUBLIC_SANITY_PROJECT_ID in .env.local"
fi

# ============================================================================
# Final Summary
# ============================================================================
echo ""
echo -e "${GREEN}${BOLD}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║                     Project Created Successfully! 🎉                       ║${NC}"
echo -e "${GREEN}${BOLD}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}Stack:${NC}"
echo "  • Next.js 16 + Turbopack + React Compiler"
echo "  • React 19 Server Components"
echo "  • TypeScript 5.7+ (strict)"
echo "  • Tailwind CSS v4 (CSS-first)"
echo "  • TanStack Query v5 + Zustand v5"
echo "  • Vitest + Testing Library"
[ "$WITH_AUTH" = "true" ] && echo "  • Auth.js v5 (Edge-compatible)"
[ "$WITH_DB" = "true" ] && echo "  • Prisma ORM${WITH_ACCELERATE:+ + Accelerate}"
[ "$WITH_UI" = "true" ] && echo "  • ShadCN/UI"
[ "$WITH_BIOME" = "true" ] && echo "  • Biome (lint + format)" || echo "  • ESLint + Prettier"
[ "$WITH_DOCKER" = "true" ] && echo "  • Docker (multi-stage)"
[ "$WITH_HUSKY" = "true" ] && echo "  • Husky + lint-staged"
[ "$WITH_PLAYWRIGHT" = "true" ] && echo "  • Playwright E2E"
[ "$WITH_SANITY" = "true" ] && echo "  • Sanity CMS + Studio"
echo ""

echo -e "${CYAN}Next steps:${NC}"
echo "  cd $PROJECT_NAME"
[ "$WITH_DB" = "true" ] && echo "  # Configure DATABASE_URL in .env.local"
[ "$WITH_SANITY" = "true" ] && echo "  # Set NEXT_PUBLIC_SANITY_PROJECT_ID in .env.local"
[ "$WITH_DB" = "true" ] && echo "  npm run db:push"
echo "  npm run dev"
[ "$WITH_SANITY" = "true" ] && echo "  # Studio available at http://localhost:3000/studio"
echo ""

[ "$WITH_AUTH" = "true" ] && [ -z "$WITH_DB" ] && echo -e "${YELLOW}Demo login:${NC} demo@example.com / password123"
echo ""

echo -e "${CYAN}Scripts:${NC}"
echo "  npm run dev          Start dev server (Turbopack)"
echo "  npm run build        Production build"
echo "  npm run test         Run unit tests"
echo "  npm run lint         Lint code"
[ "$WITH_DB" = "true" ] && echo "  npm run db:studio    Prisma Studio"
[ "$WITH_DOCKER" = "true" ] && echo "  npm run docker:up    Start with Docker"
[ "$WITH_PLAYWRIGHT" = "true" ] && echo "  npm run e2e          Run E2E tests"
[ "$WITH_SANITY" = "true" ] && echo "  npm run typegen      Generate Sanity types"
echo ""
