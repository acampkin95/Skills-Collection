# State Management Patterns

## Decision Tree

```
Is state needed across multiple pages?
├─ No → Local component state (useState)
└─ Yes
   ├─ Is it server/cached data? → React Query / SWR
   └─ Is it client-only state?
      ├─ Few components? → Context + useReducer
      └─ Complex app? → Zustand / Jotai
```

## Local State

### useState

```tsx
// Simple value
const [count, setCount] = useState(0)

// Object
const [user, setUser] = useState({ name: '', email: '' })
setUser(prev => ({ ...prev, name: 'John' }))  // Partial update

// Lazy initialization (expensive computation)
const [data, setData] = useState(() => computeExpensiveValue())

// Type inference
const [items, setItems] = useState<string[]>([])
```

### useReducer

```tsx
// For complex state logic
type State = { count: number; step: number }
type Action = 
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'setStep'; payload: number }
  | { type: 'reset' }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + state.step }
    case 'decrement':
      return { ...state, count: state.count - state.step }
    case 'setStep':
      return { ...state, step: action.payload }
    case 'reset':
      return { count: 0, step: 1 }
    default:
      return state
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0, step: 1 })
  
  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <input
        type="number"
        value={state.step}
        onChange={e => dispatch({ type: 'setStep', payload: +e.target.value })}
      />
    </div>
  )
}
```

## Context

### Basic Context

```tsx
// contexts/theme-context.tsx
import { createContext, useContext, useState, ReactNode } from 'react'

type Theme = 'light' | 'dark'

interface ThemeContextValue {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggle: () => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light')
  
  const toggle = () => setTheme(t => t === 'light' ? 'dark' : 'light')
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggle }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
```

### Context + Reducer

```tsx
// contexts/cart-context.tsx
import { createContext, useContext, useReducer, ReactNode, Dispatch } from 'react'

interface CartItem {
  id: string
  name: string
  price: number
  quantity: number
}

interface CartState {
  items: CartItem[]
  total: number
}

type CartAction =
  | { type: 'ADD_ITEM'; payload: Omit<CartItem, 'quantity'> }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_QUANTITY'; payload: { id: string; quantity: number } }
  | { type: 'CLEAR' }

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existing = state.items.find(i => i.id === action.payload.id)
      if (existing) {
        return {
          ...state,
          items: state.items.map(i =>
            i.id === action.payload.id
              ? { ...i, quantity: i.quantity + 1 }
              : i
          ),
          total: state.total + action.payload.price,
        }
      }
      return {
        ...state,
        items: [...state.items, { ...action.payload, quantity: 1 }],
        total: state.total + action.payload.price,
      }
    }
    case 'REMOVE_ITEM': {
      const item = state.items.find(i => i.id === action.payload)
      return {
        ...state,
        items: state.items.filter(i => i.id !== action.payload),
        total: state.total - (item ? item.price * item.quantity : 0),
      }
    }
    case 'CLEAR':
      return { items: [], total: 0 }
    default:
      return state
  }
}

const CartContext = createContext<{
  state: CartState
  dispatch: Dispatch<CartAction>
} | null>(null)

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [], total: 0 })
  
  return (
    <CartContext.Provider value={{ state, dispatch }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const context = useContext(CartContext)
  if (!context) throw new Error('useCart must be within CartProvider')
  return context
}

// Custom hooks for common actions
export function useAddToCart() {
  const { dispatch } = useCart()
  return (item: Omit<CartItem, 'quantity'>) => 
    dispatch({ type: 'ADD_ITEM', payload: item })
}
```

## Zustand (Recommended for Global State)

```bash
npm install zustand
```

### Basic Store

```tsx
// stores/counter-store.ts
import { create } from 'zustand'

interface CounterStore {
  count: number
  increment: () => void
  decrement: () => void
  reset: () => void
}

export const useCounterStore = create<CounterStore>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}))

// Usage
function Counter() {
  const { count, increment, decrement } = useCounterStore()
  return (
    <div>
      <span>{count}</span>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  )
}

// Select specific values (prevents re-render)
function CountDisplay() {
  const count = useCounterStore((state) => state.count)
  return <span>{count}</span>
}
```

### Store with Persistence

```tsx
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SettingsStore {
  theme: 'light' | 'dark'
  language: string
  setTheme: (theme: 'light' | 'dark') => void
  setLanguage: (language: string) => void
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      theme: 'light',
      language: 'en',
      setTheme: (theme) => set({ theme }),
      setLanguage: (language) => set({ language }),
    }),
    {
      name: 'settings-storage',  // localStorage key
    }
  )
)
```

### Store with Immer

```tsx
import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

interface TodoStore {
  todos: Array<{ id: string; text: string; done: boolean }>
  addTodo: (text: string) => void
  toggleTodo: (id: string) => void
  removeTodo: (id: string) => void
}

export const useTodoStore = create<TodoStore>()(
  immer((set) => ({
    todos: [],
    addTodo: (text) =>
      set((state) => {
        state.todos.push({ id: crypto.randomUUID(), text, done: false })
      }),
    toggleTodo: (id) =>
      set((state) => {
        const todo = state.todos.find((t) => t.id === id)
        if (todo) todo.done = !todo.done
      }),
    removeTodo: (id) =>
      set((state) => {
        state.todos = state.todos.filter((t) => t.id !== id)
      }),
  }))
)
```

### Slices Pattern

```tsx
// stores/slices/user-slice.ts
export interface UserSlice {
  user: { id: string; name: string } | null
  login: (user: { id: string; name: string }) => void
  logout: () => void
}

export const createUserSlice = (set: any): UserSlice => ({
  user: null,
  login: (user) => set({ user }),
  logout: () => set({ user: null }),
})

// stores/slices/cart-slice.ts
export interface CartSlice {
  items: Array<{ id: string; quantity: number }>
  addItem: (id: string) => void
  clearCart: () => void
}

export const createCartSlice = (set: any): CartSlice => ({
  items: [],
  addItem: (id) =>
    set((state: any) => ({
      items: [...state.items, { id, quantity: 1 }],
    })),
  clearCart: () => set({ items: [] }),
})

// stores/index.ts
import { create } from 'zustand'
import { createUserSlice, UserSlice } from './slices/user-slice'
import { createCartSlice, CartSlice } from './slices/cart-slice'

type Store = UserSlice & CartSlice

export const useStore = create<Store>()((...a) => ({
  ...createUserSlice(...a),
  ...createCartSlice(...a),
}))
```

## React Query (Server State)

```bash
npm install @tanstack/react-query
```

### Setup

```tsx
// app/providers.tsx
'use client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,  // 1 minute
        refetchOnWindowFocus: false,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

### Basic Query

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// Fetch
function usePosts() {
  return useQuery({
    queryKey: ['posts'],
    queryFn: () => fetch('/api/posts').then(res => res.json()),
  })
}

// With parameters
function usePost(id: string) {
  return useQuery({
    queryKey: ['posts', id],
    queryFn: () => fetch(`/api/posts/${id}`).then(res => res.json()),
    enabled: !!id,  // Only fetch when id exists
  })
}

// Usage
function PostList() {
  const { data: posts, isLoading, error } = usePosts()

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <ul>
      {posts.map((post: any) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

### Mutations

```tsx
function useCreatePost() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (newPost: { title: string; content: string }) =>
      fetch('/api/posts', {
        method: 'POST',
        body: JSON.stringify(newPost),
      }).then(res => res.json()),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['posts'] })
    },
  })
}

function CreatePostForm() {
  const { mutate, isPending } = useCreatePost()

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    mutate({
      title: formData.get('title') as string,
      content: formData.get('content') as string,
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" required />
      <textarea name="content" required />
      <button disabled={isPending}>
        {isPending ? 'Creating...' : 'Create'}
      </button>
    </form>
  )
}
```

### Optimistic Updates

```tsx
function useToggleTodo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) =>
      fetch(`/api/todos/${id}/toggle`, { method: 'PATCH' }),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['todos'] })

      const previous = queryClient.getQueryData(['todos'])

      queryClient.setQueryData(['todos'], (old: any[]) =>
        old.map((todo) =>
          todo.id === id ? { ...todo, done: !todo.done } : todo
        )
      )

      return { previous }
    },
    onError: (err, id, context) => {
      queryClient.setQueryData(['todos'], context?.previous)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
```

## Jotai (Atomic State)

```bash
npm install jotai
```

```tsx
import { atom, useAtom, useAtomValue, useSetAtom } from 'jotai'

// Primitive atom
const countAtom = atom(0)

// Derived atom (read-only)
const doubleCountAtom = atom((get) => get(countAtom) * 2)

// Derived atom (read-write)
const countWithLimitAtom = atom(
  (get) => get(countAtom),
  (get, set, newValue: number) => {
    set(countAtom, Math.min(100, Math.max(0, newValue)))
  }
)

// Async atom
const userAtom = atom(async () => {
  const res = await fetch('/api/user')
  return res.json()
})

// Usage
function Counter() {
  const [count, setCount] = useAtom(countAtom)
  const doubleCount = useAtomValue(doubleCountAtom)  // Read-only
  const setCountOnly = useSetAtom(countAtom)  // Write-only

  return (
    <div>
      <span>{count} (double: {doubleCount})</span>
      <button onClick={() => setCount(c => c + 1)}>+</button>
    </div>
  )
}
```

## URL State

### nuqs (Recommended)

```bash
npm install nuqs
```

```tsx
'use client'
import { useQueryState, parseAsInteger, parseAsString } from 'nuqs'

function ProductFilters() {
  const [search, setSearch] = useQueryState('q', parseAsString.withDefault(''))
  const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1))
  const [sort, setSort] = useQueryState('sort', parseAsString.withDefault('newest'))

  return (
    <div>
      <input
        value={search}
        onChange={e => setSearch(e.target.value)}
        placeholder="Search..."
      />
      <select value={sort} onChange={e => setSort(e.target.value)}>
        <option value="newest">Newest</option>
        <option value="price-asc">Price: Low to High</option>
        <option value="price-desc">Price: High to Low</option>
      </select>
      <button onClick={() => setPage(page + 1)}>Next Page</button>
    </div>
  )
}
```

## Comparison

| Feature | useState | Context | Zustand | React Query | Jotai |
|---------|----------|---------|---------|-------------|-------|
| Bundle | 0 | 0 | ~1KB | ~13KB | ~3KB |
| Persistence | Manual | Manual | Middleware | Cache | Middleware |
| DevTools | React | React | Yes | Yes | Yes |
| Server state | No | No | No | Yes | No |
| Async | useEffect | useEffect | Yes | Yes | Yes |
| Best for | Local | Theme, Auth | Global UI | API data | Atomic |
