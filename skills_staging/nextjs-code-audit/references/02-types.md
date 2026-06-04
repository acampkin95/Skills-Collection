# 02. Type Safety Audit

## Table of Contents
1. [Type Coverage Analysis](#1-type-coverage-analysis)
2. [Any Usage Audit](#2-any-usage-audit)
3. [Missing Types](#3-missing-types)
4. [Type Improvements](#4-type-improvements)
5. [Strict Mode Compliance](#5-strict-mode-compliance)
6. [Next.js 16 Type Patterns](#6-nextjs-16-type-patterns)

---

## 1. Type Coverage Analysis

### Automated Measurement

```bash
# Install and run type-coverage
npm install -g type-coverage

# Basic coverage
npx type-coverage

# Detailed report with uncovered locations
npx type-coverage --detail --at-least 80

# JSON output for CI
npx type-coverage --json > type-coverage.json

# By directory
npx type-coverage --project tsconfig.json app/
npx type-coverage --project tsconfig.json lib/
npx type-coverage --project tsconfig.json components/

# Strict mode (counts implicit any)
npx type-coverage --strict
```

### Coverage Targets

| Level | Coverage | Status | Action |
|-------|----------|--------|--------|
| Critical | < 60% | 🔴 | Stop, fix immediately |
| Poor | 60-75% | 🟠 | High priority |
| Acceptable | 75-85% | 🟡 | Improve incrementally |
| Good | 85-95% | 🟢 | Maintain |
| Excellent | > 95% | ✅ | Gold standard |

### Coverage Report Script

```bash
#!/bin/bash
# type-report.sh

echo "═══ TYPE COVERAGE REPORT ═══"
echo ""

# Overall coverage
COVERAGE=$(npx type-coverage 2>/dev/null | grep -oE '[0-9]+\.[0-9]+%' || echo "unknown")
echo "Overall Coverage: $COVERAGE"

# By directory
for dir in app lib components hooks; do
  if [ -d "$dir" ]; then
    DIR_COV=$(npx type-coverage --project tsconfig.json "$dir" 2>/dev/null | \
              grep -oE '[0-9]+\.[0-9]+%' || echo "N/A")
    echo "  $dir/: $DIR_COV"
  fi
done

# Worst files
echo ""
echo "Lowest coverage files:"
npx type-coverage --detail 2>/dev/null | sort -t: -k3 -n | head -10
```

---

## 2. Any Usage Audit

### Comprehensive Detection

```bash
# All any patterns
echo "=== Explicit any ==="
grep -rn ": any" --include="*.ts" --include="*.tsx" app/ lib/ components/

echo "=== Generic any ==="
grep -rn "<any>" --include="*.ts" --include="*.tsx" app/ lib/ components/

echo "=== Array any ==="
grep -rn "any\[\]" --include="*.ts" --include="*.tsx" app/ lib/ components/

echo "=== As any assertions ==="
grep -rn "as any" --include="*.ts" --include="*.tsx" app/ lib/ components/

echo "=== Any in function params ==="
grep -rn "([^)]*: any" --include="*.ts" --include="*.tsx" app/ lib/

echo "=== Any return types ==="
grep -rn "): any" --include="*.ts" --include="*.tsx" app/ lib/

# Count by category
echo ""
echo "=== SUMMARY ==="
echo "Explicit ': any': $(grep -rn ": any" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | wc -l)"
echo "Assertion 'as any': $(grep -rn "as any" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | wc -l)"
echo "Generic '<any>': $(grep -rn "<any>" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | wc -l)"
```

### Any Classification

| Category | Example | Severity | Fix Effort |
|----------|---------|----------|------------|
| Function param | `(data: any)` | High | Medium |
| Return type | `): any` | High | Medium |
| Variable | `const x: any` | Medium | Low |
| Generic | `Array<any>` | Medium | Low |
| Assertion | `as any` | High | High |
| Catch clause | `catch (e: any)` | Low | Low |

### Fix Patterns

```typescript
// ❌ Function parameter
function process(data: any) { }
// ✅ Fix with interface
interface ProcessInput { id: string; value: number }
function process(data: ProcessInput) { }

// ❌ API response
const response: any = await fetch('/api').then(r => r.json())
// ✅ Fix with type + validation
interface ApiResponse { users: User[] }
const response = await fetch('/api').then(r => r.json()) as ApiResponse
// Better: use zod
const response = ApiResponseSchema.parse(await fetch('/api').then(r => r.json()))

// ❌ Event handler
const handleChange = (e: any) => { }
// ✅ Fix with React types
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => { }

// ❌ Dynamic object
const config: any = { }
// ✅ Fix with Record or interface
const config: Record<string, unknown> = { }
// or
interface Config { apiUrl: string; timeout: number }
const config: Config = { apiUrl: '', timeout: 5000 }

// ❌ Catch clause
catch (e: any) { console.log(e.message) }
// ✅ Fix with unknown + type guard
catch (e: unknown) {
  if (e instanceof Error) console.log(e.message)
}
```

---

## 3. Missing Types

### Detection Commands

```bash
# Functions without explicit return types
grep -rn "function.*)[[:space:]]*{" --include="*.ts" --include="*.tsx" app/ lib/ | \
  grep -v "): " | head -20

# Arrow functions without types
grep -rn "const.*= (" --include="*.ts" --include="*.tsx" app/ lib/ | \
  grep -v ": .*=>" | head -20

# useState without type
grep -rn "useState()" --include="*.tsx" app/ components/
grep -rn "useState(null)" --include="*.tsx" app/ components/
grep -rn "useState(\[\])" --include="*.tsx" app/ components/

# useRef without type
grep -rn "useRef(null)" --include="*.tsx" app/ components/ | grep -v "<"

# Object literals without type
grep -rn "const.*= {$" --include="*.ts" --include="*.tsx" lib/ | \
  grep -v ": " | head -10

# Function params without types
grep -rn "([a-z][a-zA-Z]*)" --include="*.ts" app/ lib/ | \
  grep -v ": \|import\|require" | head -10

# Event handlers without types
grep -rn "on[A-Z][a-z]*={(" --include="*.tsx" app/ components/ | head -10
```

### Priority Locations

| Location | Priority | Impact |
|----------|----------|--------|
| API route handlers | Critical | Request/Response safety |
| Server actions | Critical | Data integrity |
| Form handlers | High | User input safety |
| Shared utilities | High | Multiple consumers |
| Custom hooks | High | Reusability |
| Component props | Medium | Component contracts |
| Local variables | Low | Inference works |

### Type Generation

```bash
# Generate types from JSON response
npx quicktype -l typescript --src api-response.json -o types/api.ts

# Generate from JSON schema
npx json-schema-to-typescript schema.json > types/schema.ts

# Generate from OpenAPI
npx openapi-typescript ./openapi.yaml -o types/api.ts

# Infer types from runtime
npx ts-auto-guard path/to/file.ts
```

---

## 4. Type Improvements

### Generic Opportunities

```typescript
// ❌ Repeated specific types
function getUser(id: string): User | undefined { }
function getPost(id: string): Post | undefined { }
function getComment(id: string): Comment | undefined { }

// ✅ Generic function
function getById<T>(collection: T[], id: string): T | undefined {
  return collection.find(item => (item as any).id === id)
}
```

### Union Type Improvements

```typescript
// ❌ String type for limited values
function setStatus(status: string) { }

// ✅ Union type
type Status = 'pending' | 'active' | 'completed' | 'cancelled'
function setStatus(status: Status) { }

// ❌ Boolean flags
interface User {
  isAdmin: boolean
  isModerator: boolean
  isViewer: boolean
}

// ✅ Union type
interface User {
  role: 'admin' | 'moderator' | 'viewer'
}
```

### Discriminated Unions

```typescript
// ❌ Optional properties
interface ApiResponse {
  success: boolean
  data?: any
  error?: string
}

// ✅ Discriminated union
type ApiResponse<T> = 
  | { success: true; data: T }
  | { success: false; error: string }

// Usage with type narrowing
if (response.success) {
  console.log(response.data) // T
} else {
  console.log(response.error) // string
}
```

### Utility Types

```typescript
// Partial - make all properties optional
type PartialUser = Partial<User>

// Required - make all properties required
type RequiredConfig = Required<Config>

// Pick - select specific properties
type UserPreview = Pick<User, 'id' | 'name' | 'avatar'>

// Omit - exclude specific properties
type UserInput = Omit<User, 'id' | 'createdAt'>

// Record - typed object with specific key type
type UserMap = Record<string, User>

// ReturnType - extract function return type
type FetchResult = ReturnType<typeof fetchUsers>

// Parameters - extract function parameters
type FetchParams = Parameters<typeof fetchUsers>

// Awaited - unwrap Promise type
type User = Awaited<ReturnType<typeof getUser>>
```

---

## 5. Strict Mode Compliance

### tsconfig.json Checks

```bash
# Check strict settings
grep -E '"strict"|"noImplicitAny"|"strictNullChecks"|"strictFunctionTypes"' tsconfig.json

# Required settings for Next.js 16
cat tsconfig.json | grep -E '"moduleResolution"|"isolatedModules"|"esModuleInterop"'
```

### Recommended Strict Config

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### Incremental Strict Mode

Enable one flag at a time:

```bash
# Step 1: Enable noImplicitAny
npx tsc --noEmit --noImplicitAny 2>&1 | head -50

# Step 2: Enable strictNullChecks
npx tsc --noEmit --strictNullChecks 2>&1 | head -50

# Step 3: Enable strictFunctionTypes
npx tsc --noEmit --strictFunctionTypes 2>&1 | head -50

# Full strict mode
npx tsc --noEmit --strict 2>&1 | head -50
```

---

## 6. Next.js 16 Type Patterns

### Async Request APIs

```typescript
// ❌ Old pattern (Next.js 14)
export default function Page({ params }: { params: { id: string } }) {
  const { id } = params
}

// ✅ New pattern (Next.js 15+)
export default async function Page({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
}

// Client component with params
'use client'
import { use } from 'react'

export default function ClientPage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = use(params)
}
```

### Server Action Types

```typescript
// ❌ Untyped server action
'use server'
export async function createUser(formData: FormData) {
  const name = formData.get('name')
}

// ✅ Typed server action with Zod
'use server'
import { z } from 'zod'

const CreateUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email()
})

export async function createUser(formData: FormData) {
  const result = CreateUserSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email')
  })
  
  if (!result.success) {
    return { error: result.error.flatten() }
  }
  
  // result.data is typed
}
```

### Route Handler Types

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server'

interface User {
  id: string
  name: string
}

export async function GET(
  request: NextRequest
): Promise<NextResponse<User[] | { error: string }>> {
  try {
    const users = await getUsers()
    return NextResponse.json(users)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch users' },
      { status: 500 }
    )
  }
}
```

### Component Props Types

```typescript
// Recommended pattern for components
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
}

export function Button({ 
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  ...props 
}: ButtonProps) {
  return <button {...props}>{children}</button>
}
```
