# 11. Next.js 16 Patterns

Critical patterns and breaking changes for Next.js 16 / App Router.

---

## 1. Async Request APIs (Breaking in Next.js 15+)

### Detection

```bash
# Find synchronous params usage
grep -rn "params\." --include="*.tsx" app/ | grep -v "await params"

# Find synchronous searchParams usage
grep -rn "searchParams\." --include="*.tsx" app/ | grep -v "await searchParams"

# Find old cookies/headers patterns
grep -rn "cookies()\." --include="*.ts" --include="*.tsx" app/ | grep -v "await cookies()"
grep -rn "headers()\." --include="*.ts" --include="*.tsx" app/ | grep -v "await headers()"
```

### Fix Patterns

```typescript
// ❌ OLD (Next.js 14)
export default function Page({ params }: { params: { id: string } }) {
  const { id } = params  // Error in Next.js 15+
  return <div>{id}</div>
}

// ✅ NEW (Next.js 15+) - Server Component
export default async function Page({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
  return <div>{id}</div>
}

// ✅ NEW - Client Component
'use client'
import { use } from 'react'

export default function Page({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = use(params)
  return <div>{id}</div>
}

// ✅ NEW - searchParams
export default async function Page({
  searchParams
}: {
  searchParams: Promise<{ q?: string }>
}) {
  const { q } = await searchParams
  return <Search query={q} />
}

// ✅ NEW - cookies/headers
import { cookies, headers } from 'next/headers'

export async function GET() {
  const cookieStore = await cookies()
  const headersList = await headers()
  
  const token = cookieStore.get('token')
  const auth = headersList.get('authorization')
}
```

---

## 2. Server vs Client Components

### Detection

```bash
# Count components by type
echo "Server Components: $(find app/ components/ -name "*.tsx" | xargs grep -L "'use client'" | wc -l)"
echo "Client Components: $(grep -rl "'use client'" --include="*.tsx" app/ components/ | wc -l)"

# Find pages that are client components (anti-pattern)
grep -l "'use client'" app/**/page.tsx 2>/dev/null

# Find 'use client' not on first line
for f in $(grep -l "'use client'" --include="*.tsx" app/ components/); do
  if ! head -1 "$f" | grep -q "'use client'"; then
    echo "Wrong position: $f"
  fi
done
```

### Rules

| File Type | Default | 'use client' Required? |
|-----------|---------|------------------------|
| page.tsx | Server | Only if interactive |
| layout.tsx | Server | Only if interactive |
| loading.tsx | Server | No |
| error.tsx | Client | **YES (required)** |
| not-found.tsx | Server | No |
| global-error.tsx | Client | **YES (required)** |
| route.ts | Server | N/A |
| Components | Server | When using hooks/events |

### Patterns

```typescript
// ✅ Server Component page with client interactive part
// app/page.tsx
export default async function Page() {
  const data = await getData()  // Direct DB/API access
  return (
    <div>
      <h1>{data.title}</h1>
      <InteractiveSection />  {/* Client component */}
    </div>
  )
}

// components/InteractiveSection.tsx
'use client'  // MUST be first line
import { useState } from 'react'

export function InteractiveSection() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}

// ✅ Passing server component as children
// ClientWrapper.tsx
'use client'
export function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return <div>{open && children}</div>
}

// page.tsx
export default async function Page() {
  return (
    <ClientWrapper>
      <ServerComponent />  {/* ✅ Works! */}
    </ClientWrapper>
  )
}
```

---

## 3. Caching Changes (Next.js 15+)

### Detection

```bash
# Find fetch without cache options
grep -rn "await fetch(" --include="*.ts" --include="*.tsx" app/ lib/ | \
  grep -v "cache:\|revalidate:\|next:"
```

### New Defaults

```typescript
// Next.js 14: Cached by default
// Next.js 15+: NOT cached by default

// ❌ OLD assumption: this was cached
const data = await fetch('/api/data')

// ✅ NEW: Explicitly cache
const data = await fetch('/api/data', { cache: 'force-cache' })

// Revalidate options
fetch('/api/data', { next: { revalidate: 3600 } })  // ISR: 1 hour
fetch('/api/data', { next: { revalidate: 0 } })     // No cache
fetch('/api/data', { next: { tags: ['posts'] } })   // Tag for invalidation
fetch('/api/data', { cache: 'no-store' })           // Never cache
```

---

## 4. Server Actions

### Detection

```bash
# Find server actions
grep -rn "'use server'" --include="*.ts" --include="*.tsx" app/ lib/

# Check for validation
for f in $(grep -rl "'use server'" --include="*.ts" app/ lib/); do
  if ! grep -q "zod\|yup\|validate" "$f"; then
    echo "No validation: $f"
  fi
done
```

### Patterns

```typescript
// ✅ Server action with validation
'use server'

import { z } from 'zod'
import { revalidatePath } from 'next/cache'

const schema = z.object({
  title: z.string().min(1),
  content: z.string().min(10)
})

export async function createPost(formData: FormData) {
  const result = schema.safeParse({
    title: formData.get('title'),
    content: formData.get('content')
  })
  
  if (!result.success) {
    return { error: result.error.flatten() }
  }
  
  await db.posts.create({ data: result.data })
  revalidatePath('/posts')
  return { success: true }
}

// Usage in form
<form action={createPost}>
  <input name="title" />
  <textarea name="content" />
  <button type="submit">Create</button>
</form>
```

---

## 5. Imports & Navigation

### Detection

```bash
# Wrong router import
grep -rn "from 'next/router'" --include="*.tsx" app/ components/

# Check navigation imports
grep -rn "from 'next/navigation'" --include="*.tsx" app/ components/
```

### Fix

```typescript
// ❌ Pages Router (wrong for App Router)
import { useRouter } from 'next/router'

// ✅ App Router
import { useRouter, usePathname, useSearchParams } from 'next/navigation'

// ❌ Old redirect pattern
const router = useRouter()
router.push('/dashboard')

// ✅ Server-side redirect
import { redirect } from 'next/navigation'
redirect('/dashboard')

// ✅ Client-side navigation
'use client'
import { useRouter } from 'next/navigation'
const router = useRouter()
router.push('/dashboard')
```

---

## 6. Metadata

### Detection

```bash
# Check metadata exports
for f in $(find app -name "layout.tsx" -o -name "page.tsx"); do
  if ! grep -q "metadata\|generateMetadata" "$f"; then
    echo "No metadata: $f"
  fi
done
```

### Patterns

```typescript
// Static metadata
export const metadata: Metadata = {
  title: 'My App',
  description: 'App description',
}

// Dynamic metadata
export async function generateMetadata({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}): Promise<Metadata> {
  const { id } = await params
  const post = await getPost(id)
  
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      images: [post.image],
    },
  }
}
```

---

## 7. Error Handling

### Required Files

```bash
# Verify error files
[ -f "app/error.tsx" ] && head -1 app/error.tsx
[ -f "app/global-error.tsx" ] && head -1 app/global-error.tsx
```

### Patterns

```typescript
// app/error.tsx - MUST have 'use client'
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}

// app/global-error.tsx - MUST have 'use client'
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
        <h2>Something went wrong!</h2>
        <button onClick={() => reset()}>Try again</button>
      </body>
    </html>
  )
}
```

---

## 8. Tailwind CSS v4

### Detection

```bash
# Check postcss config extension
ls postcss.config.* 2>/dev/null

# Check Tailwind import style
grep "@tailwind\|@import" app/globals.css
```

### Requirements

```css
/* ❌ OLD (Tailwind v3) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* ✅ NEW (Tailwind v4) */
@import "tailwindcss";

/* Custom theme */
@theme {
  --color-primary: #3b82f6;
}

/* Dark mode */
@custom-variant dark (&:where(.dark, .dark *));
```

### Class Changes

| v3 | v4 |
|----|-----|
| shadow-sm | shadow-xs |
| shadow | shadow-sm |
| blur-sm | blur-xs |
| blur | blur-sm |
| rounded-sm | rounded-xs |
| rounded | rounded-sm |
| outline-none | outline-hidden |
| ring | ring-3 |

---

## Quick Audit Checklist

```bash
# Run this for quick Next.js 16 compliance check
echo "=== Next.js 16 Compliance Check ==="

echo ""
echo "1. Async params/searchParams:"
grep -rn "params\." --include="*.tsx" app/ 2>/dev/null | grep -v "await params\|Promise<" | wc -l

echo ""
echo "2. Wrong router import:"
grep -rn "from 'next/router'" --include="*.tsx" app/ components/ 2>/dev/null | wc -l

echo ""
echo "3. error.tsx has 'use client':"
[ -f "app/error.tsx" ] && head -1 app/error.tsx | grep -q "'use client'" && echo "✅" || echo "❌"

echo ""
echo "4. postcss.config.mjs (not .js):"
[ -f "postcss.config.mjs" ] && echo "✅" || echo "❌"

echo ""
echo "5. Tailwind v4 import:"
grep -q '@import "tailwindcss"' app/globals.css 2>/dev/null && echo "✅" || echo "❌"

echo ""
echo "6. Client pages (should be minimal):"
grep -l "'use client'" app/**/page.tsx 2>/dev/null | wc -l
```
