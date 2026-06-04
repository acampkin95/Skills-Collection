# 05. Technical Debt Audit

## Table of Contents
1. [TODO/FIXME Analysis](#1-todofixme-analysis)
2. [Error Handling](#2-error-handling)
3. [Code Duplication](#3-code-duplication)
4. [Pattern Inconsistencies](#4-pattern-inconsistencies)
5. [Documentation Gaps](#5-documentation-gaps)
6. [Debt Tracking](#6-debt-tracking)

---

## 1. TODO/FIXME Analysis

### Comprehensive Detection

```bash
# Find all markers with context
echo "=== FIXMEs (Critical) ==="
grep -rn "FIXME" --include="*.ts" --include="*.tsx" app/ lib/ components/

echo "=== BUGs (High) ==="
grep -rn "BUG\|BUGFIX" --include="*.ts" --include="*.tsx" app/ lib/ components/

echo "=== TODOs (Medium) ==="
grep -rn "TODO" --include="*.ts" --include="*.tsx" app/ lib/ components/

echo "=== HACKs (Medium) ==="
grep -rn "HACK\|XXX\|KLUDGE" --include="*.ts" --include="*.tsx" app/ lib/ components/

echo "=== TEMPs (Low) ==="
grep -rn "TEMP\|TEMPORARY" --include="*.ts" --include="*.tsx" app/ lib/ components/

# Summary counts
echo ""
echo "=== SUMMARY ==="
echo "FIXMEs: $(grep -r "FIXME" --include="*.ts" --include="*.tsx" app/ lib/ | wc -l)"
echo "BUGs: $(grep -r "BUG" --include="*.ts" --include="*.tsx" app/ lib/ | wc -l)"
echo "TODOs: $(grep -r "TODO" --include="*.ts" --include="*.tsx" app/ lib/ | wc -l)"
echo "HACKs: $(grep -r "HACK\|XXX" --include="*.ts" --include="*.tsx" app/ lib/ | wc -l)"

# TODOs with ticket references (good practice)
echo ""
echo "=== TODOs with tickets ==="
grep -rn "TODO.*#[0-9]\|TODO.*JIRA\|TODO.*ticket" --include="*.ts" --include="*.tsx" app/ lib/

# Old TODOs (check git blame)
echo ""
echo "=== Old TODOs (>6 months) ==="
for file in $(grep -rl "TODO\|FIXME" --include="*.ts" --include="*.tsx" app/ lib/); do
  while IFS=: read -r line_num content; do
    date=$(git blame -L "$line_num,$line_num" "$file" 2>/dev/null | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')
    if [ -n "$date" ]; then
      days_old=$(( ($(date +%s) - $(date -d "$date" +%s 2>/dev/null || echo 0)) / 86400 ))
      [ "$days_old" -gt 180 ] && echo "$file:$line_num ($days_old days old)"
    fi
  done < <(grep -n "TODO\|FIXME" "$file")
done 2>/dev/null
```

### Classification & Priority

| Marker | Priority | Expected Resolution |
|--------|----------|-------------------|
| FIXME | Critical | This sprint |
| BUG | High | This sprint |
| TODO | Medium | Next 2-3 sprints |
| HACK | Medium | When touching code |
| XXX | Low | Backlog |
| TEMP | Low | When feature complete |

### Good TODO Format

```typescript
// ❌ Bad: Vague TODO
// TODO: fix this

// ❌ Bad: No context
// TODO: refactor

// ✅ Good: Actionable with context
// TODO(auth): Implement token refresh before expiry - ticket #123

// ✅ Good: With owner and date
// TODO(@username 2024-01): Add rate limiting to this endpoint

// ✅ Good: With explanation
// HACK: Using setTimeout to wait for animation. Replace with proper
// animation completion callback when upgrading framer-motion.
```

---

## 2. Error Handling

### Detection

```bash
# Empty catch blocks
grep -rn "catch.*{[[:space:]]*}" --include="*.ts" --include="*.tsx" app/ lib/
grep -rn -A1 "catch" --include="*.ts" app/ lib/ | grep -B1 "^[[:space:]]*}$"

# Catch with only console
grep -rn -A2 "catch" --include="*.ts" --include="*.tsx" app/ lib/ | \
  grep -B2 "console\.\(log\|error\)" | grep "catch"

# Async functions without try-catch
for f in $(find app/ lib/ -name "*.ts" -o -name "*.tsx"); do
  async_count=$(grep -c "async" "$f" 2>/dev/null || echo 0)
  try_count=$(grep -c "try {" "$f" 2>/dev/null || echo 0)
  if [ "$async_count" -gt 0 ] && [ "$try_count" -eq 0 ]; then
    echo "No try-catch: $f (async: $async_count)"
  fi
done

# Unhandled promise rejections
grep -rn "\.then(" --include="*.ts" --include="*.tsx" app/ lib/ | \
  grep -v "\.catch\|await"

# Error boundaries
find app/ -name "error.tsx" | wc -l
ls app/global-error.tsx 2>/dev/null || echo "⚠️ No global-error.tsx"
```

### Error Handling Patterns

```typescript
// ❌ Empty catch
try { await operation() } catch (e) { }

// ❌ Console only
try { await operation() } catch (e) { console.error(e) }

// ❌ Re-throw without context
try { await operation() } catch (e) { throw e }

// ✅ Proper handling
try {
  await operation()
} catch (error) {
  logger.error('Operation failed', { error, context: { userId } })
  throw new AppError('OPERATION_FAILED', 'Unable to complete operation', { cause: error })
}

// ✅ API route error handling
export async function POST(req: Request) {
  try {
    const data = await processRequest(req)
    return Response.json(data)
  } catch (error) {
    if (error instanceof ValidationError) {
      return Response.json({ error: error.message }, { status: 400 })
    }
    if (error instanceof AuthError) {
      return Response.json({ error: 'Unauthorized' }, { status: 401 })
    }
    logger.error('API error', { error, path: req.url })
    return Response.json({ error: 'Internal error' }, { status: 500 })
  }
}
```

### Centralized Error Class

```typescript
// lib/errors.ts
export class AppError extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode: number = 500,
    public details?: Record<string, unknown>
  ) {
    super(message)
    this.name = 'AppError'
  }
  
  toJSON() {
    return {
      code: this.code,
      message: this.message,
      details: this.details
    }
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: Record<string, unknown>) {
    super('VALIDATION_ERROR', message, 400, details)
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super('NOT_FOUND', `${resource} not found`, 404)
  }
}
```

---

## 3. Code Duplication

### Detection

```bash
# JSCpd - Copy/paste detector
npx jscpd --min-lines 5 --min-tokens 50 --reporters consoleFull app/ lib/ components/

# Output to JSON
npx jscpd --min-lines 5 --reporters json --output ./jscpd-report app/

# Similar function names
grep -rh "export.*function\|export const" --include="*.ts" --include="*.tsx" app/ lib/ | \
  sed 's/.*function \([a-zA-Z]*\).*/\1/;s/.*const \([a-zA-Z]*\).*/\1/' | \
  sort | uniq -d

# Similar file names
find app/ components/ lib/ -name "*.ts" -o -name "*.tsx" | \
  xargs -I {} basename {} | sort | uniq -d
```

### Common Duplication Patterns

```typescript
// ❌ Duplicated API calls
// In user-service.ts
const response = await fetch('/api/users', {
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
})

// In post-service.ts
const response = await fetch('/api/posts', {
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
})

// ✅ Extracted API client
// lib/api-client.ts
export async function apiClient<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = getToken()
  const response = await fetch(`/api${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : '',
      ...options?.headers,
    },
  })
  if (!response.ok) throw new ApiError(response)
  return response.json()
}

// ❌ Duplicated validation
// In form-a.tsx
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
if (!emailRegex.test(email)) throw new Error('Invalid email')

// In form-b.tsx
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
if (!emailPattern.test(email)) throw new Error('Invalid email')

// ✅ Shared validation
// lib/validation.ts
import { z } from 'zod'
export const emailSchema = z.string().email('Invalid email format')
```

---

## 4. Pattern Inconsistencies

### Detection

```bash
# Data fetching patterns
echo "=== Fetch patterns ==="
echo "fetch(): $(grep -rn "fetch(" --include="*.ts" --include="*.tsx" app/ lib/ | wc -l)"
echo "axios: $(grep -rn "axios\." --include="*.ts" --include="*.tsx" app/ lib/ | wc -l)"
echo "useSWR: $(grep -rn "useSWR" --include="*.tsx" app/ | wc -l)"
echo "useQuery: $(grep -rn "useQuery" --include="*.tsx" app/ | wc -l)"

# State management
echo ""
echo "=== State patterns ==="
echo "useState: $(grep -rn "useState" --include="*.tsx" app/ components/ | wc -l)"
echo "useReducer: $(grep -rn "useReducer" --include="*.tsx" app/ | wc -l)"
echo "zustand: $(grep -rn "create(" --include="*.ts" lib/ | wc -l)"
echo "redux: $(grep -rn "useSelector\|useDispatch" --include="*.tsx" app/ | wc -l)"

# Styling
echo ""
echo "=== Styling patterns ==="
echo "className=: $(grep -rn "className=" --include="*.tsx" app/ components/ | wc -l)"
echo "style=: $(grep -rn "style={{" --include="*.tsx" app/ components/ | wc -l)"
echo "styled.: $(grep -rn "styled\." --include="*.tsx" app/ | wc -l)"
echo "css\`: $(grep -rn "css\`" --include="*.tsx" app/ | wc -l)"

# Form handling
echo ""
echo "=== Form patterns ==="
echo "react-hook-form: $(grep -rn "useForm" --include="*.tsx" app/ components/ | wc -l)"
echo "formik: $(grep -rn "useFormik\|Formik" --include="*.tsx" app/ | wc -l)"
echo "native forms: $(grep -rn "onSubmit=" --include="*.tsx" app/ | grep -v "handleSubmit" | wc -l)"
```

### Standardization Recommendations

| Area | Recommendation |
|------|----------------|
| Data Fetching | Use React Query or SWR consistently |
| API Calls | Single apiClient wrapper |
| Validation | Zod schemas everywhere |
| State | React state for local, Zustand for global |
| Forms | react-hook-form + zod |
| Styling | Tailwind only, no inline styles |

---

## 5. Documentation Gaps

### Detection

```bash
# Public functions without JSDoc
for f in $(find lib/ -name "*.ts"); do
  exports=$(grep -n "^export" "$f" | cut -d: -f1)
  for line in $exports; do
    prev=$((line - 1))
    if ! sed -n "${prev}p" "$f" | grep -q "\*/"; then
      echo "Missing JSDoc: $f:$line"
    fi
  done
done | head -20

# README files
for dir in lib app/api components hooks; do
  [ -d "$dir" ] && [ ! -f "$dir/README.md" ] && echo "Missing README: $dir/"
done

# Complex files without docs (>100 lines)
find lib/ -name "*.ts" | while read f; do
  lines=$(wc -l < "$f")
  docs=$(grep -c "\/\*\*\|^\/\/" "$f" || echo 0)
  if [ "$lines" -gt 100 ] && [ "$docs" -lt 10 ]; then
    echo "Under-documented ($docs comments in $lines lines): $f"
  fi
done
```

### Documentation Template

```typescript
/**
 * Fetches user data by ID
 * 
 * @param userId - The unique identifier for the user
 * @returns The user object if found, null otherwise
 * @throws {NotFoundError} When user doesn't exist
 * @throws {AuthError} When not authorized to access user
 * 
 * @example
 * ```ts
 * const user = await getUser('123')
 * if (user) {
 *   console.log(user.name)
 * }
 * ```
 */
export async function getUser(userId: string): Promise<User | null> {
  // Implementation
}
```

---

## 6. Debt Tracking

### Debt Register Template

```markdown
# Technical Debt Register

| ID | Description | Location | Impact | Effort | Priority | Created | Owner |
|----|-------------|----------|--------|--------|----------|---------|-------|
| TD-001 | Mixed fetch/axios | app/, lib/ | Medium | 4h | Medium | 2024-01 | @dev |
| TD-002 | No error boundaries | components/ | High | 2h | High | 2024-01 | @dev |
| TD-003 | Duplicated validation | forms/ | Low | 1h | Low | 2024-02 | @dev |
```

### Debt Score Calculation

```
Debt Score = (
  (FIXME_count × 5) +
  (BUG_count × 4) +
  (TODO_count × 2) +
  (HACK_count × 3) +
  (empty_catch × 3) +
  (duplication_instances × 2) +
  (missing_docs × 1)
) / total_files

Lower is better. Target: < 5
```

### Sprint Debt Reduction Goals

| Sprint | Focus | Target |
|--------|-------|--------|
| 1 | FIXMEs & BUGs | Reduce by 100% |
| 2 | Error handling | Add to all API routes |
| 3 | Duplication | Extract 5 shared utilities |
| 4 | Documentation | JSDoc on all lib/ exports |
