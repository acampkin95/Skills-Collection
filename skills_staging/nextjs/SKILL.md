---
name: nextjs
description: Next.js 16 full-stack development with App Router, React 19, and Turbopack, Use when app router.
---

# Next.js Development Skill

**Read the relevant reference file before starting work.**

## 2026 Next.js 15/16 Features

### Core Features (Next.js 15)

**Server Actions (Stable)**
```javascript
'use server';
export async function saveFormData(data) {
  // process securely on server
}
```

**Enhanced Security** - Unguessable action IDs, dead code elimination

**Turbopack as Default** - 10x faster builds in development

**Partial Prerendering** - Static shell + dynamic content streaming

**React 19 Support** - First-class RSC integration

**New Metadata API**
```javascript
export const metadata = {
  title: "My Page",
  description: "SEO optimized",
};
```

**`<Form>` Component** - Built-in prefetching and progressive enhancement

### Breaking Changes in Next.js 15

- **Async Request APIs**: `cookies()`, `headers()`, `params` are now async
- **Caching Semantics**: Page data has `staleTime: 0` by default

## Quick Navigation

| Task | Reference |
|------|-----------|
| Starting / core patterns | `references/critical-rules.md` |
| Configuration files | `references/config-templates.md` |
| **Debugging / white screen** | `references/troubleshooting.md` |
| **Tailwind v4/v5 issues** | `references/tailwind-guide.md` |
| **Turbopack problems** | `references/turbopack-guide.md` |
| Testing setup | `references/testing-guide.md` |
| **Deployment (Docker/Vercel)** | `references/deployment-guide.md` |
| **Ubuntu/Nginx/PostgreSQL** | `references/server-infrastructure.md` |
| Full project audit | `references/audit-checklist.md` |

---

## Emergency: Dead UI (No Styling)

```bash
# 1. Check CSS import in layout.tsx
grep -n "globals.css" app/layout.tsx

# 2. MUST be postcss.config.mjs (not .js)
ls postcss.config.* && cat postcss.config.mjs

# 3. Clear cache
rm -rf .next && npm run dev
```

**See `references/troubleshooting.md` for full diagnostic.**

---

## Critical Rules (Summary)

### Async APIs (Next.js 15+)

```typescript
// ✅ CORRECT
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const cookieStore = await cookies()
  return <div>{id}</div>
}
```

### Client Components

`'use client'` required (as first line) when using: `useState`, `useEffect`, `onClick`, `window`, `document`

**Required files:** `error.tsx`, `global-error.tsx`

### Configuration Requirements

| File | Requirement |
|------|-------------|
| `postcss.config.mjs` | Must be `.mjs` |
| `tsconfig.json` | `moduleResolution: "bundler"` |
| `globals.css` | `@import "tailwindcss";` |

---

## File Conventions

| File | Server/Client | Notes |
|------|---------------|-------|
| `page.tsx` | Server | Route UI |
| `layout.tsx` | Server | Shared wrapper |
| `loading.tsx` | Server | Suspense fallback |
| `error.tsx` | **Client** | Error boundary |
| `not-found.tsx` | Server | 404 UI |
| `route.ts` | N/A | API endpoint |

---

## Common Commands

```bash
npm run dev                # Dev with Turbopack
npm run build              # Production build
npx tsc --noEmit           # Type check
rm -rf .next               # Clear cache
./scripts/audit-nextjs.sh  # Full audit
```

---

## 2026 Trends: React Compiler

React Compiler is now stable and automatically optimizes components:

```typescript
// No more useMemo/useCallback needed - Compiler handles it
function UserProfile({ user, onUpdate }) {
  // Compiler automatically memoizes these computations
  const formattedName = `${user.firstName} ${user.lastName}`;
  const initials = user.firstName[0] + user.lastName[0];

  return (
    <div>
      <h1>{formattedName}</h1>
      <Avatar initials={initials} />
      <button onClick={() => onUpdate(user.id)}>Update</button>
    </div>
  );
}
```

Enable in `next.config.ts`:

```typescript
const nextConfig = {
  experimental: {
    reactCompiler: true,
  },
};
```

## 2026: Advanced Server Component Patterns

### Parallel Routes with Suspense

```typescript
// app/dashboard/page.tsx
export default async function DashboardPage() {
  return (
    <div>
      <Suspense fallback={<TeamsSkeleton />}>
        <Teams />
      </Suspense>
      <Suspense fallback={<ProjectsSkeleton />}>
        <Projects />
      </Suspense>
    </div>
  );
}
```

### Server Actions with Validation

```typescript
// app/actions.ts
'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';

const schema = z.object({
  email: z.string().email(),
  name: z.string().min(2),
});

export async function createUser(formData: FormData) {
  const validated = schema.parse({
    email: formData.get('email'),
    name: formData.get('name'),
  });

  const user = await db.user.create({ data: validated });

  revalidatePath('/users');
  redirect(`/users/${user.id}`);
}
```

### Streaming Responses

```typescript
// app/api/generate/route.ts
export async function GET() {
  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        controller.enqueue(`data: ${i}\n\n`);
        await new Promise(r => setTimeout(r, 1000));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  });
}
```

## 2026: Partial Prerendering (PPR)

```typescript
// next.config.ts
export default {
  experimental: {
    ppr: 'incremental', // or true for all routes
  },
};
```

```typescript
// app/shop/page.tsx
// Static shell, dynamic content
export const experimental_ppr = true;

export default function ShopPage() {
  return (
    <div>
      <h1>Products</h1>
      <Suspense fallback={<ProductListSkeleton />}>
        <ProductList /> {/* Streamed in */}
      </Suspense>
    </div>
  );
}
```
