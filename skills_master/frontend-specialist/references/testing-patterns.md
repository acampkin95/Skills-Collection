# Testing Patterns

## Setup

### Vitest + React Testing Library

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitejs/plugin-react
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['**/*.{test,spec}.{js,ts,jsx,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/test/'],
    },
  },
})
```

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

afterEach(() => {
  cleanup()
})

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})
```

### Next.js Testing

```bash
npm install -D vitest @testing-library/react @vitejs/plugin-react jsdom @testing-library/jest-dom
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

## Component Testing

### Basic Component Test

```tsx
// button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from './button'

describe('Button', () => {
  it('renders children', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('applies custom className', () => {
    render(<Button className="custom">Click</Button>)
    expect(screen.getByRole('button')).toHaveClass('custom')
  })
})
```

### userEvent (More Realistic)

```tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('Form', () => {
  it('submits with form data', async () => {
    const user = userEvent.setup()
    const handleSubmit = vi.fn()
    
    render(<LoginForm onSubmit={handleSubmit} />)
    
    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')
    await user.click(screen.getByRole('button', { name: /submit/i }))
    
    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    })
  })

  it('shows validation errors', async () => {
    const user = userEvent.setup()
    render(<LoginForm onSubmit={vi.fn()} />)
    
    await user.click(screen.getByRole('button', { name: /submit/i }))
    
    expect(screen.getByText(/email is required/i)).toBeInTheDocument()
  })
})
```

### Testing Hooks

```tsx
import { renderHook, act } from '@testing-library/react'
import { useCounter } from './use-counter'

describe('useCounter', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useCounter())
    expect(result.current.count).toBe(0)
  })

  it('initializes with provided value', () => {
    const { result } = renderHook(() => useCounter(10))
    expect(result.current.count).toBe(10)
  })

  it('increments count', () => {
    const { result } = renderHook(() => useCounter())
    
    act(() => {
      result.current.increment()
    })
    
    expect(result.current.count).toBe(1)
  })

  it('decrements count', () => {
    const { result } = renderHook(() => useCounter(5))
    
    act(() => {
      result.current.decrement()
    })
    
    expect(result.current.count).toBe(4)
  })
})
```

### Testing with Context

```tsx
import { render, screen } from '@testing-library/react'
import { ThemeProvider, useTheme } from './theme-context'

function TestComponent() {
  const { theme, toggle } = useTheme()
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <button onClick={toggle}>Toggle</button>
    </div>
  )
}

describe('ThemeProvider', () => {
  it('provides default theme', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )
    
    expect(screen.getByTestId('theme')).toHaveTextContent('light')
  })

  it('toggles theme', async () => {
    const user = userEvent.setup()
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    )
    
    await user.click(screen.getByRole('button'))
    expect(screen.getByTestId('theme')).toHaveTextContent('dark')
  })
})

// Wrapper helper
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
)

it('works with wrapper', () => {
  render(<TestComponent />, { wrapper })
  expect(screen.getByTestId('theme')).toHaveTextContent('light')
})
```

### Testing Async Components

```tsx
import { render, screen, waitFor } from '@testing-library/react'

describe('UserProfile', () => {
  it('loads and displays user data', async () => {
    render(<UserProfile userId="1" />)
    
    // Loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
    
    // Wait for data
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })
  })

  it('handles error state', async () => {
    // Mock API to fail
    server.use(
      rest.get('/api/users/:id', (req, res, ctx) => {
        return res(ctx.status(500))
      })
    )
    
    render(<UserProfile userId="1" />)
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
    })
  })
})
```

## Mocking

### Mocking Functions

```tsx
import { vi } from 'vitest'

// Mock function
const mockFn = vi.fn()
mockFn.mockReturnValue(42)
mockFn.mockResolvedValue({ data: 'test' })
mockFn.mockImplementation((x) => x * 2)

// Check calls
expect(mockFn).toHaveBeenCalled()
expect(mockFn).toHaveBeenCalledWith('arg')
expect(mockFn).toHaveBeenCalledTimes(2)
```

### Mocking Modules

```tsx
// Mock entire module
vi.mock('./api', () => ({
  fetchUser: vi.fn().mockResolvedValue({ name: 'John' }),
}))

// Mock specific export
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    back: vi.fn(),
  })),
  usePathname: vi.fn(() => '/'),
}))

// Partial mock
vi.mock('./utils', async () => {
  const actual = await vi.importActual('./utils')
  return {
    ...actual,
    formatDate: vi.fn(() => '2024-01-01'),
  }
})
```

### MSW (Mock Service Worker)

```bash
npm install -D msw
```

```typescript
// src/test/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: '1', name: 'John' },
      { id: '2', name: 'Jane' },
    ])
  }),

  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'John' })
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ id: '3', ...body }, { status: 201 })
  }),
]

// src/test/mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)

// src/test/setup.ts
import { server } from './mocks/server'

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

## Testing Patterns

### Arrange-Act-Assert

```tsx
it('adds item to cart', async () => {
  // Arrange
  const user = userEvent.setup()
  const product = { id: '1', name: 'Test Product', price: 99 }
  render(<ProductCard product={product} />)

  // Act
  await user.click(screen.getByRole('button', { name: /add to cart/i }))

  // Assert
  expect(screen.getByText(/added to cart/i)).toBeInTheDocument()
})
```

### Testing Error Boundaries

```tsx
import { render, screen } from '@testing-library/react'

const ThrowError = () => {
  throw new Error('Test error')
}

describe('ErrorBoundary', () => {
  // Suppress console.error for this test
  const originalError = console.error
  beforeAll(() => {
    console.error = vi.fn()
  })
  afterAll(() => {
    console.error = originalError
  })

  it('catches errors and shows fallback', () => {
    render(
      <ErrorBoundary fallback={<div>Something went wrong</div>}>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })
})
```

### Testing Portals/Modals

```tsx
describe('Modal', () => {
  it('renders in portal', async () => {
    const user = userEvent.setup()
    render(
      <>
        <div id="modal-root" />
        <ModalTrigger />
      </>
    )

    await user.click(screen.getByRole('button', { name: /open modal/i }))

    // Modal content rendered in portal
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByRole('dialog')).toHaveTextContent('Modal Content')
  })

  it('closes on escape key', async () => {
    const user = userEvent.setup()
    render(<Modal open onClose={vi.fn()} />)

    await user.keyboard('{Escape}')

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })
})
```

### Snapshot Testing

```tsx
import { render } from '@testing-library/react'

describe('Card', () => {
  it('matches snapshot', () => {
    const { container } = render(
      <Card title="Test" description="Description" />
    )
    expect(container).toMatchSnapshot()
  })

  // Inline snapshot
  it('matches inline snapshot', () => {
    const { container } = render(<Badge>New</Badge>)
    expect(container.innerHTML).toMatchInlineSnapshot(
      `"<span class="badge">New</span>"`
    )
  })
})
```

## React Query Testing

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={createTestQueryClient()}>
    {children}
  </QueryClientProvider>
)

describe('UserList', () => {
  it('fetches and displays users', async () => {
    render(<UserList />, { wrapper })

    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument()
    })
  })
})
```

## E2E Testing with Playwright

```bash
npm install -D @playwright/test
npx playwright install
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'

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
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('user can log in', async ({ page }) => {
    await page.goto('/login')

    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h1')).toContainText('Welcome')
  })

  test('shows error for invalid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('input[name="email"]', 'wrong@example.com')
    await page.fill('input[name="password"]', 'wrong')
    await page.click('button[type="submit"]')

    await expect(page.locator('[role="alert"]')).toContainText('Invalid credentials')
  })
})
```

## Test Organization

```
src/
├── components/
│   ├── button/
│   │   ├── button.tsx
│   │   ├── button.test.tsx     # Unit tests
│   │   └── index.ts
├── hooks/
│   ├── use-counter.ts
│   └── use-counter.test.ts
├── test/
│   ├── setup.ts
│   ├── utils.tsx               # Test utilities
│   └── mocks/
│       ├── handlers.ts
│       └── server.ts
e2e/
├── auth.spec.ts
└── checkout.spec.ts
```

## Commands

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```
