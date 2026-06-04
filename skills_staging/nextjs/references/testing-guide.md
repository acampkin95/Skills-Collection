# Testing Guide

Testing setup for Next.js 15/16 App Router applications.

---

## Quick Setup

### Install Dependencies

```bash
# Jest + React Testing Library
npm install -D jest jest-environment-jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event ts-jest @types/jest

# Playwright E2E
npm install -D @playwright/test
npx playwright install
```

### jest.config.js

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({ dir: './' })

module.exports = createJestConfig({
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: { '^@/(.*)$': '<rootDir>/src/$1' },
  testPathIgnorePatterns: ['<rootDir>/e2e/'],
})
```

### jest.setup.js

```javascript
import '@testing-library/jest-dom'

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    refresh: jest.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
  useParams: () => ({}),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: (props) => <img {...props} alt={props.alt} />,
}))
```

### Package.json Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:ci": "jest --ci --coverage",
    "e2e": "playwright test",
    "e2e:ui": "playwright test --ui"
  }
}
```

---

## Component Testing

### Client Component

```typescript
// Counter.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Counter } from './Counter'

describe('Counter', () => {
  it('increments on click', async () => {
    const user = userEvent.setup()
    render(<Counter />)
    
    await user.click(screen.getByRole('button', { name: /increment/i }))
    
    expect(screen.getByTestId('count')).toHaveTextContent('1')
  })
})
```

### Form Testing

```typescript
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

it('submits form', async () => {
  const user = userEvent.setup()
  const onSubmit = jest.fn()
  render(<LoginForm onSubmit={onSubmit} />)

  await user.type(screen.getByLabelText(/email/i), 'test@example.com')
  await user.type(screen.getByLabelText(/password/i), 'password')
  await user.click(screen.getByRole('button', { name: /submit/i }))

  await waitFor(() => {
    expect(onSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password',
    })
  })
})
```

---

## API Mocking (MSW)

### Setup

```bash
npm install -D msw
```

```typescript
// mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([{ id: 1, name: 'John' }])
  }),
]

// mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'
export const server = setupServer(...handlers)
```

```javascript
// jest.setup.js (add)
import { server } from './mocks/server'
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### Override in Test

```typescript
import { http, HttpResponse } from 'msw'
import { server } from '@/mocks/server'

it('handles error', async () => {
  server.use(
    http.get('/api/users', () => HttpResponse.json({ error: 'Failed' }, { status: 500 }))
  )
  
  render(<UserList />)
  
  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument()
  })
})
```

---

## E2E Testing (Playwright)

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### E2E Test Example

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test('user can log in', async ({ page }) => {
  await page.goto('/login')
  
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password')
  await page.click('button[type="submit"]')
  
  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('text=Welcome')).toBeVisible()
})
```

### Page Object Pattern

```typescript
// e2e/pages/LoginPage.ts
import { Page } from '@playwright/test'

export class LoginPage {
  constructor(private page: Page) {}
  
  async goto() { await this.page.goto('/login') }
  
  async login(email: string, password: string) {
    await this.page.fill('input[name="email"]', email)
    await this.page.fill('input[name="password"]', password)
    await this.page.click('button[type="submit"]')
  }
}

// Usage
test('login', async ({ page }) => {
  const login = new LoginPage(page)
  await login.goto()
  await login.login('test@example.com', 'password')
  await expect(page).toHaveURL('/dashboard')
})
```

---

## Server Component Testing

```typescript
// page.test.tsx
import { render, screen } from '@testing-library/react'
import UsersPage from './page'

jest.mock('@/lib/queries', () => ({
  getUsers: jest.fn().mockResolvedValue([{ id: 1, name: 'John' }]),
}))

it('renders users', async () => {
  const Component = await UsersPage()
  render(Component)
  
  expect(screen.getByText('John')).toBeInTheDocument()
})
```

---

## CI/CD

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npm run lint
      - run: npm run test:ci
      
      - uses: codecov/codecov-action@v3

  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run e2e
      
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Coverage Goals

| Type | Target | Focus |
|------|--------|-------|
| Unit | 80%+ | Business logic |
| Integration | Key flows | API interactions |
| E2E | Happy paths | Critical journeys |
