# Common Errors & Debugging Guide

## Next.js Errors

### Hydration Mismatch

**Error:** `Hydration failed because the initial UI does not match what was rendered on the server`

**Causes & Fixes:**

```tsx
// ❌ Browser-only APIs in render
function Component() {
  return <div>{window.innerWidth}</div>  // undefined on server
}

// ✅ Use useEffect
function Component() {
  const [width, setWidth] = useState(0)
  useEffect(() => setWidth(window.innerWidth), [])
  return <div>{width}</div>
}

// ❌ Date/time without suppression
<span>{new Date().toLocaleString()}</span>

// ✅ Suppress warning
<span suppressHydrationWarning>{new Date().toLocaleString()}</span>

// ❌ Invalid HTML nesting
<p><div>Nested div in p</div></p>
<a><a>Nested anchor</a></a>

// ✅ Valid nesting
<div><div>Valid</div></div>
<a><span>Valid</span></a>

// ❌ Browser extensions injecting content
// Solution: Use specific container IDs, test in incognito
```

### Module Not Found

**Error:** `Module not found: Can't resolve '@/components/...'`

```typescript
// tsconfig.json - Ensure paths configured
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]  // or ["./*"] if no src folder
    }
  }
}

// Check file exists and case matches (case-sensitive on Linux)
```

### 'use client' Errors

**Error:** `You're importing a component that needs useState. It only works in a Client Component`

```tsx
// ❌ Missing directive
import { useState } from 'react'
export function Counter() {
  const [count, setCount] = useState(0)  // Error!
}

// ✅ Add directive
'use client'
import { useState } from 'react'
export function Counter() {
  const [count, setCount] = useState(0)  // Works
}
```

**Error:** `Attempted to call X from the server but X is on the client`

```tsx
// ❌ Passing function to client component
// page.tsx (Server)
<ClientComponent onClick={() => console.log('hi')} />

// ✅ Define handler in client component
// ClientComponent.tsx
'use client'
export function ClientComponent() {
  const handleClick = () => console.log('hi')
  return <button onClick={handleClick}>Click</button>
}
```

### Async Component Errors (Next.js 15)

**Error:** `params.id is a Promise and must be awaited`

```tsx
// ❌ v14 pattern (breaks in v15)
export default function Page({ params }: { params: { id: string } }) {
  return <div>{params.id}</div>
}

// ✅ v15 pattern
export default async function Page({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
  return <div>{id}</div>
}
```

## Tailwind CSS Errors

### Styles Not Applying

**Checklist:**

1. **CSS imported in root layout?**
```tsx
// app/layout.tsx
import './globals.css'  // Must be imported!
```

2. **Correct config extension?**
```bash
# Tailwind v4: postcss.config.mjs (not .js)
# Tailwind v3: tailwind.config.js or .ts
```

3. **Content paths configured? (v3)**
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
}
```

4. **Correct CSS syntax?**
```css
/* v4 */
@import "tailwindcss";

/* v3 */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

5. **Clear cache**
```bash
rm -rf .next node_modules/.cache
npm run dev
```

### Dynamic Classes Not Working

```tsx
// ❌ Dynamically constructed (gets purged)
const color = 'red'
<div className={`bg-${color}-500`} />

// ✅ Complete class strings
const colorClasses = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
}
<div className={colorClasses[color]} />

// ✅ Safelist in config (v3)
module.exports = {
  safelist: ['bg-red-500', 'bg-blue-500'],
}
```

### v3 → v4 Class Changes

```tsx
// These changed in v4!
// v3 → v4
'shadow-sm'     → 'shadow-xs'
'shadow'        → 'shadow-sm'
'blur-sm'       → 'blur-xs'
'blur'          → 'blur-sm'
'rounded-sm'    → 'rounded-xs'
'rounded'       → 'rounded-sm'
'outline-none'  → 'outline-hidden'
'ring'          → 'ring-3'
```

## React Errors

### Invalid Hook Call

**Error:** `Invalid hook call. Hooks can only be called inside of the body of a function component`

**Causes:**
1. Calling hook outside component
2. Calling hook conditionally
3. Multiple React versions
4. Breaking rules of hooks

```tsx
// ❌ Conditional hook
function Component({ show }) {
  if (show) {
    const [state, setState] = useState()  // Error!
  }
}

// ✅ Always call hooks at top level
function Component({ show }) {
  const [state, setState] = useState()
  if (!show) return null
  return <div>{state}</div>
}

// Check for duplicate React
npm ls react  // Should show only one version
```

### Too Many Re-renders

**Error:** `Too many re-renders. React limits the number of renders to prevent an infinite loop`

```tsx
// ❌ Setting state during render
function Component() {
  const [count, setCount] = useState(0)
  setCount(count + 1)  // Infinite loop!
}

// ❌ Calling function instead of passing reference
<button onClick={handleClick()}>  // Calls immediately!

// ✅ Pass function reference
<button onClick={handleClick}>
<button onClick={() => handleClick()}>
```

### Memory Leak Warning

**Error:** `Can't perform a React state update on an unmounted component`

```tsx
// ❌ Updating state after unmount
useEffect(() => {
  fetchData().then(data => setData(data))  // May update after unmount
}, [])

// ✅ Cleanup with AbortController
useEffect(() => {
  const controller = new AbortController()
  
  fetchData({ signal: controller.signal })
    .then(data => setData(data))
    .catch(err => {
      if (err.name !== 'AbortError') throw err
    })
  
  return () => controller.abort()
}, [])

// ✅ Or use mounted flag
useEffect(() => {
  let mounted = true
  fetchData().then(data => {
    if (mounted) setData(data)
  })
  return () => { mounted = false }
}, [])
```

## TypeScript Errors

### Type Inference Issues

```tsx
// ❌ Generic not inferred
const [items, setItems] = useState([])  // never[]

// ✅ Provide type
const [items, setItems] = useState<string[]>([])
const [user, setUser] = useState<User | null>(null)
```

### Event Handler Types

```tsx
// Common event types
onClick: (e: React.MouseEvent<HTMLButtonElement>) => void
onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
onSubmit: (e: React.FormEvent<HTMLFormElement>) => void
onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void
```

### Component Props

```tsx
// Extend HTML element props
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

// Children type
interface Props {
  children: React.ReactNode
}

// Ref forwarding
const Button = forwardRef<HTMLButtonElement, ButtonProps>((props, ref) => {
  return <button ref={ref} {...props} />
})
```

## Build Errors

### Out of Memory

```bash
# Increase Node memory
NODE_OPTIONS="--max-old-space-size=4096" npm run build

# Or in package.json
"scripts": {
  "build": "NODE_OPTIONS='--max-old-space-size=4096' next build"
}
```

### ESLint Errors Blocking Build

```javascript
// next.config.js
module.exports = {
  eslint: {
    ignoreDuringBuilds: true,  // Not recommended for production
  },
}
```

### TypeScript Errors Blocking Build

```javascript
// next.config.js
module.exports = {
  typescript: {
    ignoreBuildErrors: true,  // Not recommended for production
  },
}
```

## Debugging Tools

### React DevTools

```tsx
// Name components for better debugging
const MyComponent = () => <div />
MyComponent.displayName = 'MyComponent'

// Or use named exports
export function MyComponent() {}  // Shows as "MyComponent"
```

### Console Debugging

```tsx
// Debug render cycles
useEffect(() => {
  console.log('Component mounted')
  return () => console.log('Component unmounted')
}, [])

// Debug state changes
useEffect(() => {
  console.log('State changed:', state)
}, [state])

// Debug props
console.log('Render with props:', props)
```

### Network Debugging

```tsx
// Intercept fetch
const originalFetch = window.fetch
window.fetch = async (...args) => {
  console.log('Fetch:', args)
  const response = await originalFetch(...args)
  console.log('Response:', response)
  return response
}
```

## Quick Fixes Cheatsheet

| Error | Quick Fix |
|-------|-----------|
| Hydration mismatch | Wrap in `useEffect`, add `suppressHydrationWarning` |
| Module not found | Check `tsconfig.json` paths, file case |
| Styles not loading | Check CSS import, clear `.next` cache |
| Hook errors | Ensure top-level, check for duplicate React |
| Too many re-renders | Check `onClick` syntax, remove state updates in render |
| Type errors | Add explicit types, check imports |
| Build OOM | Increase `--max-old-space-size` |
| v15 params error | Add `async`, wrap params in `Promise<>`, `await` |

## Logging Best Practices

```tsx
// Structured logging
console.group('Component Debug')
console.log('Props:', props)
console.log('State:', state)
console.groupEnd()

// Conditional logging (dev only)
if (process.env.NODE_ENV === 'development') {
  console.log('Debug info:', data)
}

// Performance timing
console.time('operation')
await expensiveOperation()
console.timeEnd('operation')
```
