# Comprehensive Audit Checklist

Systematic Next.js 15/16 project audit for health checks, issue diagnosis, and production readiness.

---

## Quick Diagnostic (Run First)

```bash
# One-liner health check
npm run build 2>&1 | grep -iE "error|warning|failed" | head -20 && npx tsc --noEmit 2>&1 | head -10

# Dependency verification
npm ls next react react-dom tailwindcss @tailwindcss/postcss 2>/dev/null
```

---

## Full Audit Todo Checklist

Copy this checklist for each audit. Mark items as: ✅ Pass | ❌ Fail | ⚠️ Warning | ➖ N/A

### 1. Configuration Files

#### 1.1 next.config

```bash
ls next.config.*
cat next.config.* | head -30
```

- [ ] File exists (`next.config.ts` or `next.config.mjs`)
- [ ] `reactStrictMode: true` enabled
- [ ] No deprecated `experimental.serverComponentsExternalPackages` (use `serverExternalPackages`)
- [ ] No deprecated `experimental.turbo` (use `turbopack`)
- [ ] `output: 'standalone'` if using Docker
- [ ] Image domains configured if using external images
- [ ] No hardcoded secrets or URLs

#### 1.2 tsconfig.json

```bash
cat tsconfig.json
```

- [ ] `moduleResolution: "bundler"` (NOT `"node"`)
- [ ] `isolatedModules: true`
- [ ] `jsx: "preserve"`
- [ ] `strict: true`
- [ ] `.next/types/**/*.ts` in `include` array
- [ ] Path aliases configured correctly (`@/*`)
- [ ] `target` is ES2017 or higher

#### 1.3 postcss.config

```bash
ls postcss.config.* && cat postcss.config.*
```

- [ ] File extension is `.mjs` (NOT `.js`)
- [ ] Contains `"@tailwindcss/postcss": {}`
- [ ] No legacy `autoprefixer` (not needed in Tailwind v4)
- [ ] No legacy `postcss-import` (not needed in Tailwind v4)

#### 1.4 package.json

```bash
cat package.json | grep -A5 '"scripts"'
npm ls next react tailwindcss
```

- [ ] Next.js version 15.x or higher
- [ ] React version 18.x or 19.x
- [ ] Tailwind CSS v4.x with `@tailwindcss/postcss`
- [ ] `dev` script uses `--turbopack` (or explicit choice not to)
- [ ] `build` script is `next build`
- [ ] Type check script exists (`tsc --noEmit`)
- [ ] Lint script exists
- [ ] No conflicting React versions (`npm ls react`)

#### 1.5 Environment Files

```bash
ls -la .env* && cat .env.example 2>/dev/null
```

- [ ] `.env.example` or `.env.template` exists with all variables documented
- [ ] `.env.local` in `.gitignore`
- [ ] No secrets in `.env` (only `.env.local`)
- [ ] All `NEXT_PUBLIC_*` variables are safe for client exposure
- [ ] Production variables documented for deployment

---

### 2. App Directory Structure

#### 2.1 Required Files

```bash
ls -la app/layout.tsx app/page.tsx app/error.tsx app/not-found.tsx app/global-error.tsx 2>/dev/null
```

- [ ] `app/layout.tsx` exists
- [ ] `app/page.tsx` exists (for `/` route)
- [ ] `app/error.tsx` exists with `'use client'`
- [ ] `app/not-found.tsx` exists
- [ ] `app/global-error.tsx` exists with `'use client'`
- [ ] `app/loading.tsx` exists (recommended)

#### 2.2 Layout Structure

```bash
head -20 app/layout.tsx
grep -n "globals.css\|metadata\|<html\|<body" app/layout.tsx
```

- [ ] Imports `globals.css`
- [ ] Exports `metadata` object
- [ ] Has proper `<html>` and `<body>` tags
- [ ] Sets `lang` attribute on `<html>`
- [ ] Font variables applied correctly
- [ ] No `'use client'` (should be server component)

#### 2.3 Error Boundaries

```bash
head -5 app/error.tsx app/global-error.tsx 2>/dev/null
```

- [ ] `error.tsx` has `'use client'` as first line
- [ ] `error.tsx` accepts `error` and `reset` props
- [ ] `error.tsx` has try-again functionality
- [ ] `global-error.tsx` has `'use client'` as first line
- [ ] `global-error.tsx` includes `<html>` and `<body>` tags

#### 2.4 Route Organization

```bash
find app -name "page.tsx" -o -name "route.ts" | head -20
```

- [ ] Consistent naming conventions
- [ ] No mixing of `page.tsx` and `route.ts` in same directory
- [ ] Dynamic routes use `[param]` syntax correctly
- [ ] Catch-all routes use `[...param]` correctly
- [ ] Optional catch-all uses `[[...param]]` correctly
- [ ] Route groups `(group)` used appropriately
- [ ] Private folders `_folder` for non-route code

---

### 3. CSS & Styling

#### 3.1 Tailwind Configuration

```bash
head -20 app/globals.css
grep -E "@import|@tailwind|@theme|@layer|@source" app/globals.css
```

- [ ] Uses `@import "tailwindcss"` (NOT `@tailwind` directives)
- [ ] Custom theme variables in `@theme` block
- [ ] Dark mode variant configured (`@custom-variant dark`)
- [ ] `@source` directives for monorepo (if applicable)
- [ ] No deprecated `@tailwind base/components/utilities`

#### 3.2 Class Name Patterns

```bash
grep -rn 'className.*`.*\${' --include="*.tsx" app/ components/ src/ 2>/dev/null | head -10
```

- [ ] No dynamic class interpolation (`bg-${color}-500`)
- [ ] Uses object mapping for dynamic styles
- [ ] Uses `clsx` or `cn` utility for conditional classes
- [ ] No inline styles where Tailwind classes would work

#### 3.3 CSS Organization

- [ ] Global styles only in `globals.css`
- [ ] Component styles use Tailwind or CSS Modules
- [ ] No conflicting CSS frameworks
- [ ] CSS custom properties used for theming
- [ ] Responsive design uses Tailwind breakpoints

---

### 4. Component Architecture

#### 4.1 Server/Client Boundaries

```bash
# Count client vs server components
echo "Client components:" && grep -rl "'use client'" --include="*.tsx" app/ components/ src/ 2>/dev/null | wc -l
echo "Total components:" && find app components src -name "*.tsx" 2>/dev/null | wc -l
```

- [ ] Majority of components are Server Components
- [ ] `'use client'` only where necessary (hooks, events, browser APIs)
- [ ] `'use client'` at leaf components, not entire pages
- [ ] No `'use client'` on page.tsx files (usually wrong)
- [ ] Client components in dedicated `components/client/` folder (optional convention)

#### 4.2 Data Passing

```bash
grep -rn "onClick\|onChange\|onSubmit" --include="*.tsx" app/ 2>/dev/null | grep -v "'use client'" | head -5
```

- [ ] Event handlers only in `'use client'` components
- [ ] No functions passed from Server to Client components
- [ ] Props are serializable (no classes, symbols, circular refs)
- [ ] Server components passed as `children` to client wrappers

#### 4.3 Import Patterns

```bash
grep -rn "from 'next/router'" --include="*.tsx" app/ components/ src/ 2>/dev/null
```

- [ ] Uses `next/navigation` (NOT `next/router`)
- [ ] Uses `next/image` for images
- [ ] Uses `next/link` for navigation
- [ ] Uses `next/font` for fonts
- [ ] No direct `react-dom` imports in Server Components

---

### 5. Async APIs (Next.js 15+)

#### 5.1 Page Props

```bash
grep -rn "params\|searchParams" --include="page.tsx" app/ 2>/dev/null | head -10
```

- [ ] `params` typed as `Promise<{ ... }>`
- [ ] `params` accessed with `await`
- [ ] `searchParams` typed as `Promise<{ ... }>`
- [ ] `searchParams` accessed with `await`
- [ ] Client components use `use(params)` instead of `await`

#### 5.2 Request APIs

```bash
grep -rn "cookies()\|headers()\|draftMode()" --include="*.ts" --include="*.tsx" app/ lib/ 2>/dev/null | head -10
```

- [ ] `cookies()` called with `await`
- [ ] `headers()` called with `await`
- [ ] `draftMode()` called with `await`
- [ ] Request APIs only in Server Components or Route Handlers

#### 5.3 Layout Props

```bash
grep -rn "params" --include="layout.tsx" app/ 2>/dev/null | head -5
```

- [ ] Layout `params` also typed as `Promise` and awaited

---

### 6. Hydration Safety

#### 6.1 Browser API Usage

```bash
grep -rn "window\.\|document\.\|localStorage\|sessionStorage" --include="*.tsx" app/ components/ 2>/dev/null | grep -v "typeof" | head -10
```

- [ ] Browser APIs only in `useEffect` or event handlers
- [ ] `typeof window !== 'undefined'` checks where needed
- [ ] No browser APIs in render path of client components
- [ ] `useEffect` for client-only initialization

#### 6.2 Dynamic Content

```bash
grep -rn "new Date()\|Date.now()\|Math.random()" --include="*.tsx" app/ components/ 2>/dev/null | head -10
```

- [ ] Dates formatted in `useEffect` or with `suppressHydrationWarning`
- [ ] Random values generated in `useEffect`
- [ ] `useId()` used for dynamic IDs (not `Math.random()`)
- [ ] No conditional rendering based on client-only values

#### 6.3 HTML Validity

```bash
grep -rn "<p.*<div\|<a.*<a\|<button.*<button" --include="*.tsx" app/ components/ 2>/dev/null
```

- [ ] No `<div>` inside `<p>`
- [ ] No `<a>` inside `<a>`
- [ ] No `<button>` inside `<button>`
- [ ] No interactive elements inside other interactive elements

---

### 7. API Routes

#### 7.1 Route Handler Structure

```bash
find app/api -name "route.ts" 2>/dev/null | head -10
grep -rn "export async function" --include="route.ts" app/api/ 2>/dev/null | head -10
```

- [ ] Route handlers in `app/api/**/route.ts`
- [ ] HTTP methods exported as named functions (`GET`, `POST`, etc.)
- [ ] Request type is `Request` (Web API)
- [ ] Returns `NextResponse` or `Response`
- [ ] Error handling with try/catch
- [ ] Proper status codes returned

#### 7.2 API Security

- [ ] Authentication/authorization checks
- [ ] Input validation (Zod recommended)
- [ ] Rate limiting considered
- [ ] CORS configured if needed
- [ ] No sensitive data in responses without auth

---

### 8. Data Fetching

#### 8.1 Server-Side Fetching

```bash
grep -rn "fetch(" --include="*.tsx" --include="*.ts" app/ lib/ 2>/dev/null | head -10
```

- [ ] Data fetching in Server Components (not Client)
- [ ] Direct database/API calls (not internal route handlers)
- [ ] Caching strategy defined (`cache`, `next.revalidate`)
- [ ] Error handling for failed fetches
- [ ] Loading states with Suspense

#### 8.2 Caching Configuration

```bash
grep -rn "revalidate\|dynamic\|cache:" --include="*.tsx" --include="*.ts" app/ 2>/dev/null | head -10
```

- [ ] `export const revalidate` set appropriately
- [ ] `export const dynamic` set where needed
- [ ] Fetch cache options specified
- [ ] Understands Next.js 15 default (no caching)

---

### 9. Performance

#### 9.1 Bundle Analysis

```bash
# Check for heavy imports in client components
grep -A 30 "'use client'" app/**/*.tsx components/**/*.tsx 2>/dev/null | grep "^import" | sort | uniq -c | sort -rn | head -10
```

- [ ] Heavy libraries dynamically imported
- [ ] No full library imports (`import _ from 'lodash'`)
- [ ] Tree-shakeable imports (`import { debounce } from 'lodash-es'`)
- [ ] Client component bundle sizes reasonable

#### 9.2 Image Optimization

```bash
grep -rn "<img" --include="*.tsx" app/ components/ 2>/dev/null | grep -v "next/image" | head -5
```

- [ ] Uses `next/image` for all images
- [ ] Images have `width` and `height` or `fill`
- [ ] Priority images marked with `priority`
- [ ] Remote image domains configured
- [ ] Proper `sizes` attribute for responsive images

#### 9.3 Font Optimization

```bash
grep -rn "next/font" --include="*.tsx" app/ 2>/dev/null | head -5
```

- [ ] Uses `next/font` for fonts
- [ ] Font variables applied to body/html
- [ ] Font subsets specified
- [ ] Font display strategy set

#### 9.4 Code Splitting

```bash
grep -rn "dynamic(" --include="*.tsx" app/ components/ 2>/dev/null | head -5
```

- [ ] Heavy components use `next/dynamic`
- [ ] Appropriate `loading` components provided
- [ ] `ssr: false` only where necessary
- [ ] Route-based code splitting automatic

---

### 10. Security

#### 10.1 Environment Variables

```bash
grep -rn "process.env\." --include="*.tsx" app/ components/ 2>/dev/null | grep -v "NEXT_PUBLIC" | head -5
```

- [ ] Server-only env vars not in client components
- [ ] Secrets not in client-exposed code
- [ ] `.env.local` in `.gitignore`
- [ ] Production secrets in secure secret manager

#### 10.2 Security Headers

```bash
cat middleware.ts 2>/dev/null | head -30
grep -rn "X-Frame-Options\|Content-Security-Policy" . 2>/dev/null | head -5
```

- [ ] `X-Frame-Options: DENY` or CSP frame-ancestors
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `Referrer-Policy` configured
- [ ] `Content-Security-Policy` configured
- [ ] `Strict-Transport-Security` for HTTPS

#### 10.3 Authentication

- [ ] Auth on protected routes
- [ ] Middleware for route protection
- [ ] Session management secure
- [ ] CSRF protection if using forms
- [ ] Rate limiting on auth endpoints

---

### 11. Testing

#### 11.1 Test Setup

```bash
ls jest.config.* playwright.config.* 2>/dev/null
cat package.json | grep -E "test|jest|playwright"
```

- [ ] Jest configured for unit/component tests
- [ ] React Testing Library setup
- [ ] Playwright configured for E2E
- [ ] Test scripts in package.json
- [ ] CI runs tests

#### 11.2 Test Coverage

```bash
find . -name "*.test.tsx" -o -name "*.spec.ts" 2>/dev/null | wc -l
```

- [ ] Critical components have tests
- [ ] API routes have tests
- [ ] E2E tests for critical flows
- [ ] Coverage thresholds defined

---

### 12. Build & Deploy

#### 12.1 Build Verification

```bash
rm -rf .next && npm run build
```

- [ ] Build completes without errors
- [ ] Build completes without warnings (or warnings reviewed)
- [ ] Bundle sizes acceptable
- [ ] Static pages generated where expected
- [ ] Dynamic pages marked correctly

#### 12.2 Production Readiness

- [ ] Health check endpoint exists (`/api/health`)
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Logging configured
- [ ] Environment variables for production
- [ ] Docker/deployment config tested
- [ ] Rollback procedure documented

---

## Automated Audit Script

Save as `scripts/audit-nextjs.sh`:

```bash
#!/bin/bash
set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Next.js Project Audit v2.0                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"

PASS="✅"
FAIL="❌"
WARN="⚠️"
INFO="ℹ️"

section() { echo -e "\n━━━ $1 ━━━"; }
check() { [ $1 -eq 0 ] && echo "$PASS $2" || echo "$FAIL $2"; }
warn() { echo "$WARN $1"; }
info() { echo "$INFO $1"; }

# 1. Configuration
section "Configuration Files"

[ -f "next.config.ts" ] || [ -f "next.config.mjs" ] || [ -f "next.config.js" ]
check $? "next.config exists"

[ -f "tsconfig.json" ]
check $? "tsconfig.json exists"

[ -f "postcss.config.mjs" ]
check $? "postcss.config.mjs exists (correct extension)"

[ -f "postcss.config.js" ] && warn "postcss.config.js found - should be .mjs for Tailwind v4"

grep -q '"moduleResolution".*"bundler"' tsconfig.json 2>/dev/null
check $? "tsconfig moduleResolution is 'bundler'"

grep -q '.next/types' tsconfig.json 2>/dev/null
check $? "tsconfig includes .next/types"

# 2. App Structure
section "App Directory Structure"

[ -f "app/layout.tsx" ] || [ -f "src/app/layout.tsx" ]
check $? "layout.tsx exists"

[ -f "app/error.tsx" ] || [ -f "src/app/error.tsx" ]
check $? "error.tsx exists"

if [ -f "app/error.tsx" ]; then
  head -1 app/error.tsx | grep -q "use client"
  check $? "error.tsx has 'use client'"
elif [ -f "src/app/error.tsx" ]; then
  head -1 src/app/error.tsx | grep -q "use client"
  check $? "error.tsx has 'use client'"
fi

# 3. CSS Setup
section "CSS & Tailwind"

CSS_FILE=""
[ -f "app/globals.css" ] && CSS_FILE="app/globals.css"
[ -f "src/app/globals.css" ] && CSS_FILE="src/app/globals.css"

if [ -n "$CSS_FILE" ]; then
  grep -q '@import.*tailwindcss' "$CSS_FILE"
  check $? "globals.css uses @import 'tailwindcss'"
  
  grep -q '@tailwind' "$CSS_FILE" && warn "Old @tailwind syntax found - update to @import"
else
  echo "$FAIL globals.css not found"
fi

# 4. Dependencies
section "Dependencies"

npm ls next 2>/dev/null | grep -q "next@"
check $? "Next.js installed"

npm ls tailwindcss 2>/dev/null | grep -q "tailwindcss@"
check $? "Tailwind CSS installed"

npm ls @tailwindcss/postcss 2>/dev/null | grep -q "@tailwindcss/postcss@"
check $? "@tailwindcss/postcss installed"

# Check versions
NEXT_VERSION=$(npm ls next --json 2>/dev/null | grep -o '"version": "[^"]*"' | head -1 | grep -o '[0-9][0-9.]*')
info "Next.js version: $NEXT_VERSION"

# 5. Code Quality
section "Code Quality Checks"

# Client components in pages
PAGE_CLIENT=$(grep -rl "'use client'" --include="page.tsx" app/ src/app/ 2>/dev/null | wc -l | tr -d ' ')
[ "$PAGE_CLIENT" -eq 0 ]
check $? "No 'use client' in page.tsx files ($PAGE_CLIENT found)"

# Wrong router import
WRONG_ROUTER=$(grep -rn "from 'next/router'" --include="*.tsx" app/ components/ src/ 2>/dev/null | wc -l | tr -d ' ')
[ "$WRONG_ROUTER" -eq 0 ]
check $? "No imports from next/router ($WRONG_ROUTER found)"

# Dynamic class names
DYN_CLASS=$(grep -rn 'className.*`.*\${' --include="*.tsx" app/ components/ src/ 2>/dev/null | wc -l | tr -d ' ')
[ "$DYN_CLASS" -eq 0 ]
check $? "No dynamic Tailwind classes ($DYN_CLASS found)"

# Browser APIs outside typeof check
BROWSER_API=$(grep -rn "window\.\|document\." --include="*.tsx" app/ components/ src/ 2>/dev/null | grep -v "typeof" | wc -l | tr -d ' ')
[ "$BROWSER_API" -lt 5 ]
check $? "Browser API usage checked ($BROWSER_API potential issues)"

# 6. Build Test
section "Build Verification"

info "Running build check..."
if npm run build 2>&1 | grep -qi "error"; then
  echo "$FAIL Build has errors"
else
  echo "$PASS Build successful"
fi

# Summary
section "Audit Complete"
echo "Review any $FAIL or $WARN items above"
echo "See references/troubleshooting.md for fixes"
```

---

## Audit Report Template

```markdown
# Next.js Audit Report

**Project:** [Project Name]
**Repository:** [URL]
**Date:** [YYYY-MM-DD]
**Auditor:** [Name]
**Next.js Version:** [X.X.X]
**Tailwind Version:** [X.X.X]

---

## Executive Summary

**Overall Status:** 🟢 Good / 🟡 Needs Attention / 🔴 Critical Issues

| Category | Status | Issues |
|----------|--------|--------|
| Configuration | 🟢/🟡/🔴 | X issues |
| App Structure | 🟢/🟡/🔴 | X issues |
| CSS & Styling | 🟢/🟡/🔴 | X issues |
| Components | 🟢/🟡/🔴 | X issues |
| Performance | 🟢/🟡/🔴 | X issues |
| Security | 🟢/🟡/🔴 | X issues |
| Testing | 🟢/🟡/🔴 | X issues |

---

## Critical Issues (Fix Immediately)

### Issue 1: [Title]
- **Location:** `path/to/file.tsx:line`
- **Impact:** [Description of impact]
- **Fix:** [How to fix]
- **Reference:** [Link to documentation]

### Issue 2: [Title]
...

---

## Warnings (Fix Soon)

### Warning 1: [Title]
- **Location:** `path/to/file.tsx`
- **Recommendation:** [What to do]

---

## Recommendations (Best Practices)

1. **[Recommendation]** - [Why and how]
2. **[Recommendation]** - [Why and how]

---

## Detailed Findings

### Configuration Files

| Check | Status | Notes |
|-------|--------|-------|
| next.config.ts | ✅/❌ | |
| tsconfig.json | ✅/❌ | |
| postcss.config.mjs | ✅/❌ | |
| package.json | ✅/❌ | |

### App Structure

| Check | Status | Notes |
|-------|--------|-------|
| layout.tsx | ✅/❌ | |
| error.tsx | ✅/❌ | |
| not-found.tsx | ✅/❌ | |

### Component Analysis

- **Total Components:** X
- **Client Components:** X (X%)
- **Server Components:** X (X%)
- **Potential Hydration Issues:** X

### Performance Metrics

- **Build Time:** Xs
- **Total Bundle Size:** X MB
- **Largest Client Bundle:** X KB

---

## Action Items

| Priority | Item | Owner | Due Date |
|----------|------|-------|----------|
| 🔴 High | Fix [issue] | | |
| 🟡 Medium | Update [item] | | |
| 🟢 Low | Consider [improvement] | | |

---

## Appendix

### Commands Used

```bash
npm run build
npx tsc --noEmit
npm run lint
./scripts/audit-nextjs.sh
```

### Files Reviewed

- [List of key files reviewed]
```

---

## Quick Reference Card

Print this for quick audits:

```
┌─────────────────────────────────────────────────────────────┐
│                  NEXT.JS AUDIT QUICK CHECK                  │
├─────────────────────────────────────────────────────────────┤
│ CONFIG                                                      │
│ □ postcss.config.mjs (NOT .js)                             │
│ □ tsconfig: moduleResolution: "bundler"                    │
│ □ globals.css: @import "tailwindcss"                       │
│                                                             │
│ STRUCTURE                                                   │
│ □ app/layout.tsx imports globals.css                       │
│ □ app/error.tsx has 'use client'                           │
│ □ app/global-error.tsx has 'use client'                    │
│                                                             │
│ COMPONENTS                                                  │
│ □ 'use client' only where needed                           │
│ □ params/searchParams use await                            │
│ □ No next/router imports (use next/navigation)             │
│                                                             │
│ STYLING                                                     │
│ □ No dynamic classes: bg-${color}-500                      │
│ □ No @tailwind directives (v3 syntax)                      │
│                                                             │
│ BUILD                                                       │
│ □ npm run build passes                                     │
│ □ npx tsc --noEmit passes                                  │
│ □ npm run lint passes                                      │
└─────────────────────────────────────────────────────────────┘
```
