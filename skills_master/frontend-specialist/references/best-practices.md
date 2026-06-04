# Frontend Best Practices 2026

## Project Structure

### Next.js 16 App Router

```
src/
├── app/                    # App Router (Next.js 16+)
│   ├── (marketing)/        # Route group
│   │   ├── page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx      # Dashboard-specific layout
│   │   ├── page.tsx
│   │   └── [slug]/
│   │       └── page.tsx
│   ├── api/                # API routes
│   ├── favicon.ico
│   ├── globals.css
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page
├── components/
│   ├── ui/                 # Base UI components (shadcn/ui)
│   ├── features/           # Feature-specific components
│   └── layout/             # Layout components
├── hooks/                  # Custom React hooks
├── lib/                    # Utility functions
│   ├── utils.ts
│   ├── api.ts
│   └── db.ts
├── types/                  # TypeScript types
├── styles/                 # Global styles
└── public/                 # Static assets
```

### Feature-Based Structure (Alternative)

```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── lib/
│   └── dashboard/
│       ├── components/
│       ├── hooks/
│       └── lib/
├── shared/
│   ├── components/
│   ├── hooks/
│   └── lib/
└── app/
    └── [feature]/         # Routes by feature
```

## Component Patterns

### Server Component

```tsx
// app/dashboard/page.tsx
import { getData } from '@/lib/db';
import { DataTable } from '@/components/ui/table';

export default async function DashboardPage() {
  const data = await getData();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <DataTable data={data} />
    </div>
  );
}

// Opt-in to caching
export const revalidate = 3600; // Revalidate every hour
```

### Client Component

```tsx
// components/counter.tsx
'use client';

import { useState } from 'react';
import { useCounter } from '@/hooks/use-counter';

interface CounterProps {
  initialValue?: number;
}

export function Counter({ initialValue = 0 }: CounterProps) {
  const { count, increment, decrement } = useCounter(initialValue);

  return (
    <div className="flex items-center gap-4">
      <button
        onClick={decrement}
        className="px-4 py-2 rounded bg-gray-100"
        aria-label="Decrement"
      >
        -
      </button>
      <span className="text-xl font-mono">{count}</span>
      <button
        onClick={increment}
        className="px-4 py-2 rounded bg-gray-100"
        aria-label="Increment"
      >
        +
      </button>
    </div>
  );
}
```

### Custom Hook

```tsx
// hooks/use-counter.ts
import { useState, useCallback } from 'react';

export function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);

  const increment = useCallback(() => {
    setCount(c => c + 1);
  }, []);

  const decrement = useCallback(() => {
    setCount(c => c - 1);
  }, []);

  return { count, increment, decrement };
}
```

## Data Fetching

### TanStack Query (v5)

```tsx
// hooks/use-users.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await fetch('/api/users');
      if (!res.ok) throw new Error('Failed to fetch users');
      return res.json();
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateUserDTO) => {
      const res = await fetch('/api/users', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

### Server Actions

```tsx
// app/actions/user.ts
'use server';

import { revalidatePath } from 'next/cache';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
});

export async function createUser(formData: FormData) {
  const data = schema.parse({
    name: formData.get('name'),
    email: formData.get('email'),
  });

  await db.user.create({ data });

  revalidatePath('/users');
  return { success: true };
}
```

## State Management

### Zustand (v5)

```tsx
// lib/store/user-store.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        isAuthenticated: false,
        setUser: (user) => set({ user, isAuthenticated: !!user }),
        logout: () => set({ user: null, isAuthenticated: false }),
      }),
      { name: 'user-store' }
    ),
    { name: 'UserStore' }
  )
);

// Use with useShallow for performance
import { useShallow } from 'zustand/react/shallow';

function UserAvatar() {
  const { user } = useUserStore(
    useShallow((state) => ({ user: state.user }))
  );
  // ...
}
```

## Styling (Tailwind CSS v4)

```tsx
// app/layout.tsx
import './globals.css';

@theme {
  --color-brand: oklch(0.65 0.2 250);
  --font-display: "Inter var", sans-serif;
  --radius-lg: 0.5rem;
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
```

### Utility Function

```ts
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
```

## Testing

### Vitest + React Testing Library

```tsx
// components/counter.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Counter } from './counter';

describe('Counter', () => {
  it('renders correctly', () => {
    render(<Counter initialValue={0} />);
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('increments on button click', () => {
    render(<Counter initialValue={0} />);
    fireEvent.click(screen.getByLabelText('Increment'));
    expect(screen.getByText('1')).toBeInTheDocument();
  });
});
```

### Playwright E2E

```typescript
// tests/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test('dashboard flow', async ({ page }) => {
  await page.goto('/dashboard');

  // Check page loads
  await expect(page.locator('h1')).toContainText('Dashboard');

  // Interact with counter
  const incrementBtn = page.getByLabelText('Increment');
  await incrementBtn.click();
  await incrementBtn.click();

  // Verify state
  await expect(page.locator('.font-mono')).toContainText('2');
});
```

## Performance Optimization

### Code Splitting

```tsx
// Lazy load heavy components
import { lazy, Suspense } from 'react';

const HeavyChart = lazy(() => import('./heavy-chart'));

function Dashboard() {
  return (
    <Suspense fallback={<ChartSkeleton />}>
      <HeavyChart />
    </Suspense>
  );
}
```

### Image Optimization

```tsx
import Image from 'next/image';

function HeroImage() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero"
      width={1200}
      height={600}
      priority
      placeholder="blur"
      blurDataURL="data:image/..."
      sizes="(max-width: 768px) 100vw, 50vw"
    />
  );
}
```

### Bundle Analysis

```bash
# Analyze bundle size
npm run build
npx @next/bundle-analyzer
```

## Error Handling

### Error Boundary

```tsx
// components/error-boundary.tsx
'use client';

import { useState } from 'react';

export function ErrorBoundary({ children }: { children: React.ReactNode }) {
  const [error, setError] = useState<Error | null>(null);

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-600 rounded">
        <h2>Something went wrong</h2>
        <p>{error.message}</p>
        <button onClick={() => setError(null)}>Try again</button>
      </div>
    );
  }

  return (
    <ErrorBoundaryInner onError={setError}>
      {children}
    </ErrorBoundaryInner>
  );
}
```

## Security

### Content Security Policy

```ts
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: `
              default-src 'self';
              script-src 'self' 'unsafe-eval' 'unsafe-inline';
              style-src 'self' 'unsafe-inline';
              img-src 'self' data: https:;
              font-src 'self' data:;
            `.replace(/\n/g, ' ').trim(),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
```

## Git Workflow

### Commit Messages

```
feat: add user dashboard
fix: resolve hydration error on Safari
docs: update API reference
style: format code with prettier
refactor: extract useCounter hook
test: add counter component tests
chore: update dependencies
```

### Branch Strategy

```
main
├── develop
│   ├── feature/user-dashboard
│   ├── feature/auth-flow
│   └── bugfix/hydration-error
└── release/v1.0.0
```
