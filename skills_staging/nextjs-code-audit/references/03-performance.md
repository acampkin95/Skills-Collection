# 03. Performance Audit

## Table of Contents
1. [Bundle Analysis](#1-bundle-analysis)
2. [Re-render Prevention](#2-re-render-prevention)
3. [Lazy Loading](#3-lazy-loading)
4. [Caching Strategies](#4-caching-strategies)
5. [Next.js 16 Optimizations](#5-nextjs-16-optimizations)
6. [Core Web Vitals](#6-core-web-vitals)

---

## 1. Bundle Analysis

### Automated Analysis

```bash
# Build with analyzer
ANALYZE=true npm run build

# Webpack bundle analyzer
npx webpack-bundle-analyzer .next/analyze/client.html

# Bundle size check
npx bundlesize

# Cost of modules
npx cost-of-modules --less --no-install

# Import cost (per file)
npx import-cost path/to/file.tsx

# Check chunk sizes
du -sh .next/static/chunks/* | sort -h | tail -20
ls -lhS .next/static/chunks/*.js | head -20
```

### Size Thresholds

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| First Load JS (shared) | < 85kb | 85-120kb | > 120kb |
| Page JS | < 50kb | 50-80kb | > 80kb |
| Individual chunk | < 30kb | 30-50kb | > 50kb |
| Total JS | < 200kb | 200-350kb | > 350kb |

### Common Bloat Sources

```bash
# Find large library imports
grep -rn "import.*from 'lodash'" --include="*.tsx" app/ components/
grep -rn "import.*from 'moment'" --include="*.tsx" app/ components/
grep -rn "import.*from 'date-fns'" --include="*.tsx" app/ components/
grep -rn "import.*from '@mui/'" --include="*.tsx" app/ components/
grep -rn "import.*from 'antd'" --include="*.tsx" app/ components/

# Namespace imports (prevent tree-shaking)
grep -rn "import \* as" --include="*.tsx" --include="*.ts" app/ components/

# Barrel imports in client components
grep -A5 "'use client'" --include="*.tsx" app/ components/ | \
  grep "from '@/components'" | head -10

# Check if tree-shaking is working
grep -rn "import { [a-zA-Z, ]* } from 'lodash'" --include="*.tsx" .
```

### Bundle Optimization

```typescript
// ❌ Import entire library
import _ from 'lodash'
import moment from 'moment'

// ✅ Import specific functions
import debounce from 'lodash/debounce'
import { format } from 'date-fns'

// ❌ Barrel imports in client components
'use client'
import { Button, Card, Modal, Table, Input } from '@/components/ui'

// ✅ Direct imports
'use client'
import { Button } from '@/components/ui/button'

// ❌ Import heavy library in client component
'use client'
import { Chart } from 'chart.js/auto'

// ✅ Dynamic import
'use client'
import dynamic from 'next/dynamic'
const Chart = dynamic(() => import('@/components/Chart'), { ssr: false })
```

---

## 2. Re-render Prevention

### Detection

```bash
# Components without memo
grep -rn "export function\|export const" --include="*.tsx" components/ | \
  grep -v "memo\|React.memo" | head -20

# Inline function props
grep -rn "onClick={() =>" --include="*.tsx" app/ components/
grep -rn "onChange={() =>" --include="*.tsx" app/ components/
grep -rn "onSubmit={() =>" --include="*.tsx" app/ components/

# Inline object props
grep -rn "style={{" --include="*.tsx" app/ components/
grep -rn "className={{" --include="*.tsx" app/ components/

# Object/array creation in render
grep -rn "\[.*\]\.filter\|\[.*\]\.map\|{.*})" --include="*.tsx" app/ components/ | \
  grep -v "useMemo\|useCallback" | head -10

# Missing dependency arrays
grep -rn "useEffect(() =>" --include="*.tsx" app/ components/ | \
  grep -v ", \[" | head -10
grep -rn "useMemo(() =>" --include="*.tsx" app/ components/ | \
  grep -v ", \[" | head -10
```

### Fix Patterns

```typescript
// ❌ Inline function causes re-render on every parent render
<Button onClick={() => handleClick(id)} />

// ✅ Memoized callback
const handleButtonClick = useCallback(() => handleClick(id), [id])
<Button onClick={handleButtonClick} />

// ❌ Inline object creates new reference
<Component style={{ color: 'red', padding: 16 }} />

// ✅ Memoized object
const style = useMemo(() => ({ color: 'red', padding: 16 }), [])
<Component style={style} />

// ❌ Derived data recalculated every render
const sorted = data.sort((a, b) => a.name.localeCompare(b.name))
const filtered = data.filter(x => x.active)

// ✅ Memoized derived data
const sorted = useMemo(
  () => [...data].sort((a, b) => a.name.localeCompare(b.name)),
  [data]
)
const filtered = useMemo(() => data.filter(x => x.active), [data])

// ❌ Component re-renders on every parent render
export function ExpensiveList({ items }: Props) { }

// ✅ Memoized component
export const ExpensiveList = memo(function ExpensiveList({ items }: Props) {
  return <>{items.map(item => <Item key={item.id} {...item} />)}</>
})

// ✅ Custom comparison for memo
export const UserCard = memo(
  function UserCard({ user }: Props) { },
  (prev, next) => prev.user.id === next.user.id
)
```

### React DevTools Profiler

```typescript
// Add Profiler for performance measurement
import { Profiler } from 'react'

function onRender(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number
) {
  console.log(`${id} ${phase}: ${actualDuration.toFixed(2)}ms`)
}

<Profiler id="ExpensiveComponent" onRender={onRender}>
  <ExpensiveComponent />
</Profiler>
```

---

## 3. Lazy Loading

### Component Lazy Loading

```typescript
// ❌ Static import of heavy component
import HeavyChart from '@/components/HeavyChart'
import AdminPanel from '@/components/AdminPanel'

// ✅ Dynamic import with loading state
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(
  () => import('@/components/HeavyChart'),
  {
    loading: () => <ChartSkeleton />,
    ssr: false // For client-only components
  }
)

const AdminPanel = dynamic(
  () => import('@/components/AdminPanel'),
  {
    loading: () => <AdminSkeleton />
  }
)

// ✅ Conditional loading
const DebugPanel = dynamic(
  () => import('@/components/DebugPanel'),
  { ssr: false }
)

{process.env.NODE_ENV === 'development' && <DebugPanel />}
```

### Route-based Code Splitting

```typescript
// Next.js automatically code-splits by route
// Ensure routes are properly structured

// ❌ Don't import page components directly
import DashboardPage from './dashboard/page'

// ✅ Use Link for navigation
import Link from 'next/link'
<Link href="/dashboard">Dashboard</Link>

// ✅ Use router for programmatic navigation
import { useRouter } from 'next/navigation'
const router = useRouter()
router.push('/dashboard')
```

### Image Lazy Loading

```bash
# Find unoptimized images
grep -rn "<img " --include="*.tsx" app/ components/
grep -rn 'src="http' --include="*.tsx" app/ components/
grep -rn "background-image:" --include="*.css" --include="*.tsx" app/

# Check next/image usage
grep -rn "from 'next/image'" --include="*.tsx" app/ components/ | wc -l

# Find images missing priority
grep -rn "<Image" --include="*.tsx" app/ | grep -v "priority"
```

```typescript
// ✅ Optimized image loading
import Image from 'next/image'

// Above-fold hero image - priority loading
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>

// Below-fold images - lazy loaded by default
<Image
  src="/product.jpg"
  alt="Product"
  width={400}
  height={300}
  loading="lazy"
/>

// Fill container
<div className="relative h-64 w-full">
  <Image src="/bg.jpg" alt="Background" fill className="object-cover" />
</div>
```

---

## 4. Caching Strategies

### Next.js 16 Fetch Caching

```typescript
// Default: NO caching (changed in Next.js 15)
const data = await fetch('/api/data')

// Force cache (old default behavior)
const data = await fetch('/api/data', { cache: 'force-cache' })

// Revalidate every hour
const data = await fetch('/api/data', { next: { revalidate: 3600 } })

// Tags for on-demand revalidation
const data = await fetch('/api/data', { next: { tags: ['posts'] } })

// No store (never cache)
const data = await fetch('/api/data', { cache: 'no-store' })
```

### unstable_cache Usage

```typescript
import { unstable_cache } from 'next/cache'

const getCachedUser = unstable_cache(
  async (userId: string) => {
    return await db.users.findUnique({ where: { id: userId } })
  },
  ['user'], // cache key prefix
  {
    revalidate: 3600, // 1 hour
    tags: ['user']    // for invalidation
  }
)

// Usage
const user = await getCachedUser(userId)

// Invalidate
import { revalidateTag } from 'next/cache'
revalidateTag('user')
```

### Client-Side Caching

```typescript
// React Query / TanStack Query
const { data, isLoading } = useQuery({
  queryKey: ['users', userId],
  queryFn: () => fetchUser(userId),
  staleTime: 5 * 60 * 1000,    // Fresh for 5 minutes
  gcTime: 30 * 60 * 1000,      // Keep in cache 30 minutes
  refetchOnWindowFocus: false,
})

// SWR
const { data, error } = useSWR(`/api/users/${userId}`, fetcher, {
  revalidateOnFocus: false,
  revalidateOnReconnect: false,
  dedupingInterval: 60000,
})
```

---

## 5. Next.js 16 Optimizations

### Server vs Client Components

```bash
# Count client vs server components
echo "Client components: $(grep -rl "'use client'" --include="*.tsx" app/ components/ | wc -l)"
echo "Total components: $(find app/ components/ -name "*.tsx" | wc -l)"

# Find page.tsx files with 'use client' (anti-pattern)
grep -l "'use client'" app/**/page.tsx 2>/dev/null

# Find large client components (should be split)
grep -l "'use client'" --include="*.tsx" app/ components/ | while read f; do
  lines=$(wc -l < "$f")
  [ "$lines" -gt 100 ] && echo "Large client: $f ($lines lines)"
done
```

### Optimal Patterns

```typescript
// ❌ Entire page is client component
'use client'
export default function Page() {
  const [data, setData] = useState(null)
  useEffect(() => {
    fetch('/api/data').then(r => r.json()).then(setData)
  }, [])
  return <div>{data?.title}</div>
}

// ✅ Server component page, client component for interactivity
// page.tsx (Server Component)
export default async function Page() {
  const data = await getData()
  return (
    <div>
      <h1>{data.title}</h1>
      <InteractiveSection data={data} />
    </div>
  )
}

// InteractiveSection.tsx (Client Component)
'use client'
export function InteractiveSection({ data }) {
  const [expanded, setExpanded] = useState(false)
  return <button onClick={() => setExpanded(!expanded)}>Toggle</button>
}
```

### Streaming & Suspense

```typescript
// Stream slow data with Suspense
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<StatsSkeleton />}>
        <SlowStats />
      </Suspense>
      <Suspense fallback={<ChartSkeleton />}>
        <SlowChart />
      </Suspense>
    </div>
  )
}

// Parallel data loading
async function SlowStats() {
  const stats = await getStats() // 2 second delay
  return <Stats data={stats} />
}
```

---

## 6. Core Web Vitals

### Measurement

```bash
# Run Lighthouse
npx lighthouse http://localhost:3000 \
  --output html \
  --output-path ./lighthouse-report.html \
  --only-categories=performance

# Web Vitals in code
npm install web-vitals
```

```typescript
// app/layout.tsx
import { WebVitals } from '@/components/WebVitals'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <WebVitals />
        {children}
      </body>
    </html>
  )
}

// components/WebVitals.tsx
'use client'
import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    console.log(metric)
    // Send to analytics
  })
  return null
}
```

### Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | ≤ 2.5s | 2.5-4.0s | > 4.0s |
| INP (Interaction to Next Paint) | ≤ 200ms | 200-500ms | > 500ms |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | 0.1-0.25 | > 0.25 |
| FCP (First Contentful Paint) | ≤ 1.8s | 1.8-3.0s | > 3.0s |
| TTFB (Time to First Byte) | ≤ 800ms | 800-1800ms | > 1800ms |

### Common Fixes

```typescript
// LCP: Optimize hero images
<Image src="/hero.jpg" priority placeholder="blur" />

// CLS: Set dimensions on images/embeds
<Image width={1200} height={600} />
<iframe width="560" height="315" />

// CLS: Reserve space for dynamic content
<div style={{ minHeight: 400 }}>
  <Suspense fallback={<Skeleton height={400} />}>
    <DynamicContent />
  </Suspense>
</div>

// INP: Avoid blocking main thread
// Use Web Workers for heavy computation
// Use requestIdleCallback for non-urgent tasks
// Debounce event handlers

// Font optimization
import { Inter } from 'next/font/google'
const inter = Inter({ subsets: ['latin'], display: 'swap' })
```
