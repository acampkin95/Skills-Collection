# Next.js Migration Guides

## Next.js 15 → 16 Migration

### Breaking Changes

#### 1. Cache Components Replacement
```jsx
// Next.js 15 (deprecated)
<Cache>
  <HeavyComponent />
</Cache>

// Next.js 16
<Suspense fallback={<Skeleton />}>
  <HeavyComponent />
</Suspense>
```

#### 2. Async Request APIs Required
```jsx
// Next.js 15 (optional async)
export async function generateStaticParams() { ... }

// Next.js 16 (required for dynamic routes)
export async function generateStaticParams() {
  const data = await fetchData();
  return data.map(item => ({ slug: item.slug }));
}
```

#### 3. Server Actions Strict Mode
```jsx
// Next.js 15
'use server'
export async function action() { ... }

// Next.js 16 - additional validation required
'use server'
import { verifyAction } from '@/lib/auth'

export async function action() {
  await verifyAction()  // Required authentication check
  // ... action logic
}
```

### Migration Steps

1. **Update dependencies:**
```bash
npm install next@16 react@19 react-dom@19
```

2. **Replace Cache components:**
```bash
npx @nextjs/codemod@latest cache-to-suspense .
```

3. **Add authentication to Server Actions:**
```bash
npx @nextjs/codemod@latest server-actions-auth .
```

4. **Validate async functions:**
```bash
npm run lint
```

---

## React 18 → 19 Migration

### Key Changes

#### 1. use() Hook for Data Fetching
```jsx
// React 18
function Component() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch('/api').then(d => setData(d));
  }, []);
  return data ? <Display data={data} /> : null;
}

// React 19
import { use } from 'react';

function Component() {
  const data = use(fetch('/api'));
  return <Display data={data} />;
}
```

#### 2. useActionState (formerly useFormState)
```jsx
// React 18
import { useFormState } from 'react-dom';

function Form({ action }) {
  const [state, formAction] = useFormState(action, null);
  // ...
}

// React 19
import { useActionState } from 'react';

function Form({ action }) {
  const [state, formAction, isPending] = useActionState(action, null);
  // isPending is new in React 19
}
```

#### 3. useOptimistic
```jsx
// React 19 - New pattern for optimistic UI
import { useOptimistic } from 'react';

function ShoppingCart({ items, updateItem }) {
  const [optimisticItems, setOptimistic] = useOptimistic(
    items,
    (state, updatedItem) => [...state, updatedItem]
  );

  return (
    <ul>
      {optimisticItems.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

#### 4. Ref as Prop
```jsx
// React 18
<input ref={myRef} />

// React 19 - ref is now just a prop
<input ref={myRef} />
<MyComponent ref={myRef} />  // Works with custom components too
```

### Migration Steps

1. **Update React:**
```bash
npm install react@19 react-dom@19
```

2. **Update types if using TypeScript:**
```bash
npm install -D @types/react@19 @types/react-dom@19
```

3. **Run codemods:**
```bash
npx react-codemod@latest use .
npx react-codemod@latest use-form-state-to-use-action-state .
```

4. **Fix ref forwarding:**
```jsx
// Before (React 18)
const MyInput = forwardRef((props, ref) => (
  <input ref={ref} {...props} />
));

// After (React 19)
function MyInput(props) {
  return <input {...props} />;
}
```

---

## Clerk v4 → v5 Migration

### Breaking Changes

#### 1. Authentication Helper Renamed
```jsx
// Clerk v4
import { getAuth } from '@clerk/nextjs/server';

export async function GET(req) {
  const { userId, sessionId } = getAuth(req);
  // ...
}

// Clerk v5
import { auth } from '@clerk/nextjs/server';

export async function GET(req) {
  const { userId, sessionId } = auth();
  // ...
}
```

#### 2. Middleware Changes
```jsx
// Clerk v4
import { withClerkMiddleware } from '@clerk/nextjs/server';

export default withClerkMiddleware((req, ev) => NextResponse.next());

// Clerk v5
import { clerkMiddleware } from '@clerk/nextjs/server';

export default clerkMiddleware((auth, req, ev) => {
  // auth object with protect() method
  return NextResponse.next();
});
```

#### 3. protect() Function
```jsx
// Clerk v5 - New authorization pattern
import { clerkMiddleware, protect } from '@clerk/nextjs/server';

export default clerkMiddleware(async (auth, req) => {
  await protect();  // Requires authentication
  // Or with specific permissions:
  await protect({ permission: 'org:sys:profile:manage' });
});
```

### Migration Steps

1. **Update dependencies:**
```bash
npm install @clerk/nextjs@5
```

2. **Update imports and function calls:**
```bash
npx @clerk/codemod@latest v4-to-v5 .
```

3. **Update middleware:**
```jsx
// src/middleware.ts
import { clerkMiddleware } from '@clerk/nextjs/server';

export default clerkMiddleware();

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

---

## General Best Practices

### Pre-Migration Checklist

```bash
# 1. Create backup branch
git checkout -b migration-backup
git push origin migration-backup

# 2. Run full test suite
npm test

# 3. Create snapshot
npm run build -- --dump-snapshot

# 4. Check for deprecated APIs
npm run lint -- --rule 'no-deprecated'
```

### Post-Migration Validation

```typescript
// Type checking
npm run type-check

// E2E tests
npm run test:e2e

// Visual regression
npm run test:visual

// Performance budget
npm run lighthouse
```

### Rollback Plan

```bash
# Quick rollback
git checkout main
git branch -D migration-backup
npm install previous-versions

# Or use git tags
git checkout v1.0.0
```

---

## Incremental Migration Strategy

1. **Phase 1: Dependencies**
   - Update peer dependencies first
   - Run all tests

2. **Phase 2: TypeScript**
   - Fix type errors
   - Update type definitions

3. **Phase 3: Runtime**
   - Test in development
   - Fix runtime errors

4. **Phase 4: Production**
   - Feature flags for new behavior
   - Gradual rollout

5. **Phase 5: Cleanup**
   - Remove deprecated code
   - Update documentation
