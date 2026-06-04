# 07. Testing Audit

## Table of Contents
1. [Coverage Analysis](#1-coverage-analysis)
2. [Test Organization](#2-test-organization)
3. [Test Quality](#3-test-quality)
4. [Missing Tests](#4-missing-tests)
5. [Testing Patterns](#5-testing-patterns)

---

## 1. Coverage Analysis

### Run Coverage

```bash
# Jest coverage
npm test -- --coverage --coverageReporters=text-summary

# Vitest coverage
npx vitest run --coverage

# Detailed HTML report
npm test -- --coverage --coverageReporters=html
open coverage/index.html
```

### Coverage Thresholds

| Metric | Minimum | Good | Excellent |
|--------|---------|------|-----------|
| Statements | 60% | 80% | 90%+ |
| Branches | 50% | 70% | 85%+ |
| Functions | 60% | 80% | 90%+ |
| Lines | 60% | 80% | 90%+ |

### Configure Thresholds

```javascript
// jest.config.js or vitest.config.ts
export default {
  coverageThreshold: {
    global: {
      statements: 80,
      branches: 70,
      functions: 80,
      lines: 80
    },
    './lib/': {
      statements: 90
    }
  }
}
```

---

## 2. Test Organization

### Discovery

```bash
# Find all test files
echo "=== Test Files ==="
find . -name "*.test.ts" -o -name "*.spec.ts" -o -name "*.test.tsx" -o -name "*.spec.tsx" | \
  grep -v node_modules | wc -l

# Test file locations
echo ""
echo "=== Test Locations ==="
echo "Colocated: $(find app/ lib/ components/ -name "*.test.*" 2>/dev/null | wc -l)"
echo "__tests__: $(find __tests__ -name "*.test.*" 2>/dev/null | wc -l)"
echo "tests/: $(find tests/ -name "*.test.*" 2>/dev/null | wc -l)"

# Source files without tests
echo ""
echo "=== Missing Tests ==="
for f in $(find lib/ -name "*.ts" ! -name "*.test.ts" ! -name "*.d.ts"); do
  test="${f%.ts}.test.ts"
  [ ! -f "$test" ] && echo "No test: $f"
done | head -10
```

### Recommended Structure

```
# Colocated (recommended for components)
components/
├── Button/
│   ├── Button.tsx
│   ├── Button.test.tsx
│   └── index.ts

# Separate (for lib/utils)
lib/
├── utils.ts
├── utils.test.ts

# E2E tests
e2e/
├── auth.spec.ts
├── dashboard.spec.ts
```

---

## 3. Test Quality

### Detection

```bash
# Empty test files
find . -name "*.test.ts" -o -name "*.test.tsx" | \
  xargs -I {} sh -c 'lines=$(wc -l < "{}"); [ "$lines" -lt 10 ] && echo "Minimal test: {}"' 2>/dev/null

# Tests without assertions
for f in $(find . -name "*.test.ts" -o -name "*.test.tsx" | grep -v node_modules); do
  asserts=$(grep -c "expect\|assert\|should" "$f" 2>/dev/null || echo 0)
  tests=$(grep -c "it(\|test(" "$f" 2>/dev/null || echo 0)
  if [ "$tests" -gt 0 ] && [ "$asserts" -lt "$tests" ]; then
    echo "Low assertions: $f ($asserts asserts, $tests tests)"
  fi
done

# Skipped tests
grep -rn "\.skip\|xit\|xtest\|xdescribe" --include="*.test.*" .

# Focused tests (should not be committed)
grep -rn "\.only\|fit\|fdescribe" --include="*.test.*" .
```

### Test Smells

```typescript
// ❌ Test without assertion
test('renders', () => {
  render(<Component />)
})

// ✅ Test with assertion
test('renders title', () => {
  render(<Component title="Hello" />)
  expect(screen.getByText('Hello')).toBeInTheDocument()
})

// ❌ Testing implementation details
test('calls setState', () => {
  const setState = jest.fn()
  jest.spyOn(React, 'useState').mockReturnValue([null, setState])
  // ...
})

// ✅ Testing behavior
test('updates when clicked', async () => {
  render(<Counter />)
  await userEvent.click(screen.getByRole('button'))
  expect(screen.getByText('1')).toBeInTheDocument()
})
```

---

## 4. Missing Tests

### Priority Areas

```bash
# API routes without tests
for f in $(find app/api -name "route.ts"); do
  dir=$(dirname "$f")
  if [ ! -f "$dir/route.test.ts" ] && [ ! -f "tests/api/$(basename "$dir").test.ts" ]; then
    echo "No test: $f"
  fi
done

# Server actions without tests
grep -rl "'use server'" --include="*.ts" lib/ app/ | while read f; do
  test="${f%.ts}.test.ts"
  [ ! -f "$test" ] && echo "No test for server action: $f"
done

# Utility functions without tests
for f in $(find lib/ -name "*.ts" ! -name "*.test.ts" ! -name "*.d.ts" ! -name "index.ts"); do
  exports=$(grep -c "^export" "$f" 2>/dev/null || echo 0)
  if [ "$exports" -gt 0 ]; then
    test="${f%.ts}.test.ts"
    [ ! -f "$test" ] && echo "No test ($exports exports): $f"
  fi
done
```

### Test Priority

| Priority | What to Test | Coverage Target |
|----------|--------------|-----------------|
| Critical | API routes, auth, payments | 90%+ |
| High | Server actions, data mutations | 85%+ |
| Medium | Utility functions, hooks | 80%+ |
| Standard | Components with logic | 70%+ |
| Low | Pure UI components | 50%+ |

---

## 5. Testing Patterns

### Component Testing

```typescript
// Testing React components with Testing Library
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

describe('LoginForm', () => {
  it('submits with valid credentials', async () => {
    const onSubmit = jest.fn()
    render(<LoginForm onSubmit={onSubmit} />)
    
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com')
    await userEvent.type(screen.getByLabelText(/password/i), 'password123')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      })
    })
  })
  
  it('shows error for invalid email', async () => {
    render(<LoginForm onSubmit={jest.fn()} />)
    
    await userEvent.type(screen.getByLabelText(/email/i), 'invalid')
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }))
    
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument()
  })
})
```

### API Route Testing

```typescript
// Testing Next.js API routes
import { POST } from '@/app/api/users/route'
import { NextRequest } from 'next/server'

describe('POST /api/users', () => {
  it('creates user with valid data', async () => {
    const request = new NextRequest('http://localhost/api/users', {
      method: 'POST',
      body: JSON.stringify({ name: 'Test', email: 'test@example.com' })
    })
    
    const response = await POST(request)
    const data = await response.json()
    
    expect(response.status).toBe(201)
    expect(data.user.email).toBe('test@example.com')
  })
  
  it('returns 400 for invalid data', async () => {
    const request = new NextRequest('http://localhost/api/users', {
      method: 'POST',
      body: JSON.stringify({ name: '' })
    })
    
    const response = await POST(request)
    
    expect(response.status).toBe(400)
  })
})
```

### Server Action Testing

```typescript
// Testing Server Actions
import { createUser } from '@/lib/actions/users'

// Mock the database
jest.mock('@/lib/db', () => ({
  db: {
    users: {
      create: jest.fn()
    }
  }
}))

describe('createUser', () => {
  it('creates user with valid form data', async () => {
    const formData = new FormData()
    formData.append('name', 'Test User')
    formData.append('email', 'test@example.com')
    
    const result = await createUser(formData)
    
    expect(result.success).toBe(true)
  })
})
```

### Hook Testing

```typescript
// Testing custom hooks
import { renderHook, act } from '@testing-library/react'
import { useCounter } from '@/hooks/useCounter'

describe('useCounter', () => {
  it('increments counter', () => {
    const { result } = renderHook(() => useCounter(0))
    
    act(() => {
      result.current.increment()
    })
    
    expect(result.current.count).toBe(1)
  })
})
```

### E2E Testing (Playwright)

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('user can log in', async ({ page }) => {
    await page.goto('/login')
    
    await page.fill('[name="email"]', 'test@example.com')
    await page.fill('[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/dashboard')
    await expect(page.getByText('Welcome')).toBeVisible()
  })
})
```
