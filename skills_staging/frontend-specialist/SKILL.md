---
name: frontend-specialist
description: Next.js 16, React 19, and Tailwind v4 development. Use for scaffolding, UI components, framework migration, CSS/hydration debugging, and Server Components.
version: 2.0.0
reviewed: "2026-06-04"
---

# Frontend Specialist Agent

Expert agent for production-grade, visually distinctive web applications.

## 2025-2026 Frontend Development Trends

### Framework Evolution

**Next.js 16 Dominance**
- Cache Components with "use cache" directive for explicit caching control
- Async `params` and `searchParams` (required to await in Server Components)
- Partial Pre-Rendering (PPR) for hybrid static/dynamic content
- Server Components as default; use "use client" for interactivity only
- React 19 integration with improved Server Actions

**Server-Side Rendering Renaissance**
- Shift toward server rendering, less JS shipped to browsers
- HTML streaming for progressive page delivery
- Edge computing (Vercel, Netlify, Cloudflare) for global delivery

### CSS Modernization (Interop 2025)

**Tailwind CSS v4** (January 2025)
- **CSS-first configuration**: No `tailwind.config.js` required
- `@theme` directive for customization (replaces config files)
- `@import "tailwindcss"` replaces `@tailwind` directives
- Oxide engine: 5x faster builds
- Backward compatible with v3 utilities (but use v4 patterns for new work)

**Native CSS Features (Now Production-Ready)**
- **Container Queries** (`@container`): Component-level responsive design without media queries
- **Cascade Layers** (`@layer`): Explicit control over cascade without specificity wars
- **@scope rule**: Scoped styling for DOM subtrees without BEM naming
- Scroll-driven animations: Trigger animations by scroll position
- Mathematical functions: `calc()`, `min()`, `max()`, `clamp()`

### WebAssembly (Wasm) Adoption

- High-performance applications in browser
- Rust, C++, Go running with near-native performance
- Graphics, video, financial applications

### AI Integration in Development

**Development Tools**
- GitHub Copilot, Codeium, ChatGPT for VS Code
- Figma AI for UI component generation
- TensorFlow.js, Brain.js, ml5.js for ML integration

### Design Systems Evolution

- AI-enhanced design tokens
- Automated style guide management
- Real-time designer-developer collaboration
- Built-in WCAG compliance

## Workflow

### Step 1: Environment Detection (Always First)

```bash
python3 scripts/detect-stack.py [project-path]
```

Quick manual detection:
```bash
grep -E '"next"|"vite"|"tailwindcss"' package.json
ls postcss.config.mjs 2>/dev/null && echo "Tailwind v4"
ls tailwind.config.* 2>/dev/null && echo "Tailwind v3"
```

### Step 2: Version-Specific Implementation

#### Tailwind CSS v4 Setup (2025+)

**Configuration with @theme directive:**
```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --color-brand: #3b82f6;
  --color-accent: #ec4899;
  --font-display: "Cal Sans", "Helvetica Neue", sans-serif;
  --font-mono: "Fira Code", monospace;
  --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

@layer utilities {
  @media (prefers-color-scheme: dark) {
    .dark {
      color-scheme: dark;
    }
  }
}
```

**Container Queries (Component-Based Responsive):**
```jsx
// Instead of media queries, size components based on their container
<div className="@container">
  <div className="@md:grid @md:grid-cols-2">
    {/* Responsive to container width, not viewport */}
  </div>
</div>
```

**Cascade Layers (@layer) - Control CSS Priority:**
```css
@layer base {
  body { @apply text-base leading-relaxed; }
}

@layer components {
  .btn { @apply px-4 py-2 rounded-md font-semibold; }
}

@layer utilities {
  .shadow-brand { @apply shadow-lg border-brand; }
}
/* Utilities > components > base (unlike specificity wars) */
```

**@scope for Scoped Styling:**
```css
@scope (.card) to (.card-footer) {
  p { color: blue; } /* Only p inside .card, not inside .card-footer */
}
```

**Critical v3→v4 Renames:**
| v3 | v4 | v3 | v4 |
|----|----|----|----|
| `shadow-sm` | `shadow-xs` | `rounded-sm` | `rounded-xs` |
| `shadow` | `shadow-sm` | `rounded` | `rounded-sm` |
| `blur-sm` | `blur-xs` | `outline-none` | `outline-hidden` |
| `blur` | `blur-sm` | `ring` | `ring-3` |

**Migrate:** `python3 scripts/migrate-tailwind.py [path]`

#### Next.js 16 - Async APIs (Breaking Change)

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| App Router | ✅ | ✅ | ✅ |
| Async params/searchParams | ❌ | ❌ | **Required** |
| Cache Components | ❌ | ⚠️ Experimental | ✅ Stable |
| Turbopack stable | ❌ | Partial | ✅ |

**Server Component (Async params required):**
```typescript
export default async function Page({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params;
  const cookieStore = await cookies();

  return <main>Post {id}</main>;
}
```

**Client Component (Use React.use()):**
```typescript
'use client';
import { use } from 'react';

export default function Page({
  params
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params);
  return <main>Post {id}</main>;
}
```

**Cache Components (Explicit Caching):**
```typescript
'use cache';

export default async function UserCard({ userId }: { userId: string }) {
  // This component is cached and revalidates after 60 seconds
  // Declare at top of component

  const user = await getUser(userId);
  return <div>{user.name}</div>;
}
```

**Required 'use client':** `error.tsx`, `global-error.tsx`

See `references/nextjs-patterns.md` for complete patterns.

#### Vite Setup (v5+)

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite'; // v4 support

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': '/src' } }
});
```

See `references/vite-patterns.md` for SSR, library mode, and monorepo configs.

### Step 3: Component Architecture

**Directory Structure:**
```
components/
├── ui/          # Button, Input, Badge (primitives)
├── blocks/      # Card, FormField, SearchBar (compositions)
├── sections/    # Hero, Features, Pricing (page sections)
└── layouts/     # DashboardLayout, AuthLayout (wrappers)
```

**Essential Utility:**
```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));
```

**Generate Components:** `python3 scripts/scaffold-component.py ComponentName`

See `references/component-library.md` for patterns.

### Step 4: Creative UI Design

**Principles:**
1. **Commit to direction** - Bold maximalism OR refined minimalism, never middle-ground
2. **Typography first** - Distinctive fonts, not Inter/Arial/system defaults
3. **Color with purpose** - Dominant colors, sharp accents, not evenly distributed
4. **Spatial drama** - Asymmetry, overlap, grid-breaking elements
5. **Motion that matters** - Orchestrated loads, surprising hovers

**Avoid:** Purple gradients on white, overused fonts (Inter, Roboto, Space Grotesk), cookie-cutter layouts

See `references/creative-patterns.md` for implementations.

### Step 5: Debugging

**Dead UI (No Styling):**
1. Verify CSS import in root layout
2. Check config extension (`.mjs` for Tailwind v4, no config file needed)
3. Clear cache: `rm -rf .next node_modules/.vite`
4. Run: `bash scripts/audit-frontend.sh`

**Hydration Errors:**
1. Browser APIs only in `useEffect`
2. `suppressHydrationWarning` for dynamic content
3. Valid HTML nesting (no `<div>` in `<p>`)

**Performance:** See `references/performance.md`
**Accessibility:** See `references/accessibility.md`

## Reference Files

| File | Content |
|------|---------|
| `nextjs-patterns.md` | Version matrix (14-16), async APIs, Cache Components, Server/Client components |
| `tailwind-v4-migration.md` | @theme directive, config removal, class renames, Container Queries, Cascade Layers |
| `css-features.md` | Container Queries, @scope, @layer, scroll-driven animations |
| `vite-patterns.md` | SPA, SSR, library mode, monorepo, environment variables |
| `component-library.md` | Architecture, compound components, CVA variants, hooks |
| `brand-tokens.md` | Three-layer token system, Tailwind v4 integration, theming |
| `creative-patterns.md` | Bold UI implementations, typography, color, animations |
| `shadcn-patterns.md` | shadcn/ui setup, customization, dark mode, theming |
| `accessibility.md` | WCAG checklist, ARIA patterns, keyboard navigation, testing |
| `performance.md` | Core Web Vitals, images, fonts, code splitting, caching |
| `forms-validation.md` | React Hook Form, Zod schemas, Server Actions, patterns |
| `state-management.md` | useState, Context, Zustand, React Query, Jotai |
| `testing-patterns.md` | Vitest, RTL, MSW, hooks testing, E2E with Playwright |
| `debugging-guide.md` | Common errors, hydration issues, TypeScript, quick fixes |

## Scripts

| Script | Purpose |
|--------|---------|
| `detect-stack.py` | Auto-detect frameworks, versions, configuration issues |
| `audit-frontend.sh` | Diagnose common styling/config problems |
| `scaffold-component.py` | Generate React/Vue/Svelte component boilerplate |
| `migrate-tailwind.py` | Automated v3→v4 class name migration |
| `check-a11y.py` | Basic accessibility audit |
