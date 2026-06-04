# 04. Security Audit

## Table of Contents
1. [Exposed Secrets](#1-exposed-secrets)
2. [Input Validation](#2-input-validation)
3. [Dependency Vulnerabilities](#3-dependency-vulnerabilities)
4. [Authentication & Authorization](#4-authentication--authorization)
5. [API Security](#5-api-security)
6. [Security Headers](#6-security-headers)

---

## 1. Exposed Secrets

### Automated Detection

```bash
# Gitleaks - comprehensive secret scanner
npx gitleaks detect --source . --verbose

# Trufflehog
npx trufflehog filesystem .

# Manual patterns
echo "=== Hardcoded Secrets ==="
grep -rn "password\s*=\s*['\"]" --include="*.ts" --include="*.tsx" . | grep -v node_modules
grep -rn "secret\s*=\s*['\"]" --include="*.ts" --include="*.tsx" . | grep -v node_modules
grep -rn "api[_-]?key\s*=\s*['\"]" --include="*.ts" --include="*.tsx" . | grep -v node_modules

echo "=== API Key Patterns ==="
grep -rn "sk-[a-zA-Z0-9]" --include="*.ts" --include="*.tsx" . | grep -v node_modules  # OpenAI
grep -rn "pk_\(live\|test\)_" --include="*.ts" --include="*.tsx" . | grep -v node_modules  # Stripe
grep -rn "AKIA[A-Z0-9]" --include="*.ts" --include="*.tsx" . | grep -v node_modules  # AWS
grep -rn "ghp_[a-zA-Z0-9]" --include="*.ts" --include="*.tsx" . | grep -v node_modules  # GitHub
grep -rn "xox[baprs]-" --include="*.ts" --include="*.tsx" . | grep -v node_modules  # Slack

echo "=== Database Connection Strings ==="
grep -rn "mongodb://\|postgres://\|mysql://\|redis://" --include="*.ts" . | grep -v node_modules

echo "=== Private Keys ==="
grep -rn "BEGIN.*PRIVATE KEY" --include="*.ts" --include="*.tsx" --include="*.pem" .
```

### Environment Variable Audit

```bash
# List all env var usage
grep -rh "process\.env\." --include="*.ts" --include="*.tsx" app/ lib/ | \
  sed 's/.*process\.env\.\([A-Z_]*\).*/\1/' | sort -u

# Check NEXT_PUBLIC_ exposure
echo "=== Public env vars (exposed to client) ==="
grep -rn "NEXT_PUBLIC_" --include="*.ts" --include="*.tsx" .

echo "=== Server env vars in client components ==="
grep -l "'use client'" --include="*.tsx" app/ components/ | while read f; do
  if grep -q "process.env\." "$f" && ! grep -q "NEXT_PUBLIC_" "$f"; then
    echo "⚠️ Server env var in client component: $f"
  fi
done

# Verify .env files not committed
git ls-files | grep -E "\.env$|\.env\.local$|\.env\.production$"

# Check .gitignore
grep "\.env" .gitignore || echo "⚠️ .env not in .gitignore"
```

### Fix Patterns

```typescript
// ❌ Hardcoded secret
const API_KEY = 'sk-abc123...'

// ✅ Environment variable (server-side)
const API_KEY = process.env.API_KEY!

// ❌ Client-exposed secret
'use client'
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY)

// ✅ Server-side only
// app/api/payment/route.ts
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

// ❌ Logging secrets
console.log('Config:', { apiKey, secretToken, password })

// ✅ Never log secrets
console.log('Config:', { endpoint, timeout })
```

---

## 2. Input Validation

### Detection

```bash
# Find form handlers
grep -rn "onSubmit\|handleSubmit" --include="*.tsx" app/ components/

# Find API routes without validation
for f in $(find app -name "route.ts"); do
  if ! grep -q "zod\|yup\|joi\|validate" "$f"; then
    echo "⚠️ No validation library: $f"
  fi
done

# Find direct JSON parsing without validation
grep -rn "req\.json()\|request\.json()" --include="*.ts" app/api/

# Find SQL-like patterns (injection risk)
grep -rn "\${\|+ .*\(query\|sql\)" --include="*.ts" lib/ app/
```

### Validation Patterns

```typescript
// ❌ No validation
export async function POST(req: Request) {
  const body = await req.json()
  await db.users.create({ data: body }) // Dangerous!
}

// ✅ With Zod validation
import { z } from 'zod'

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().positive().optional()
})

export async function POST(req: Request) {
  const body = await req.json()
  const result = CreateUserSchema.safeParse(body)
  
  if (!result.success) {
    return Response.json(
      { error: result.error.flatten() },
      { status: 400 }
    )
  }
  
  await db.users.create({ data: result.data })
}

// ✅ Server action with validation
'use server'
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  message: z.string().min(10).max(1000)
})

export async function submitContact(formData: FormData) {
  const result = schema.safeParse({
    email: formData.get('email'),
    message: formData.get('message')
  })
  
  if (!result.success) {
    return { error: 'Invalid input' }
  }
  
  // Process validated data
}
```

### XSS Prevention

```bash
# Find dangerouslySetInnerHTML
grep -rn "dangerouslySetInnerHTML" --include="*.tsx" app/ components/
```

```typescript
// ❌ Direct HTML injection
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// ✅ Sanitize with DOMPurify
import DOMPurify from 'dompurify'

<div dangerouslySetInnerHTML={{ 
  __html: DOMPurify.sanitize(userContent, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p'],
    ALLOWED_ATTR: ['href']
  }) 
}} />

// ✅ Better: Use markdown with sanitization
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const html = DOMPurify.sanitize(marked.parse(userContent))
```

---

## 3. Dependency Vulnerabilities

### Automated Scans

```bash
# npm audit
npm audit
npm audit --production
npm audit --json > audit-report.json

# Snyk (more comprehensive)
npx snyk test
npx snyk monitor  # Continuous monitoring

# Check for outdated packages
npm outdated

# Socket.dev (supply chain security)
npx socket scan

# Audit-ci for CI/CD
npx audit-ci --moderate
```

### Severity Response Matrix

| Severity | Response Time | Action |
|----------|---------------|--------|
| Critical | Immediate | Stop deployment, fix now |
| High | < 24 hours | Prioritize hotfix |
| Moderate | < 1 week | Schedule in sprint |
| Low | Next sprint | Add to backlog |

### Update Commands

```bash
# Auto-fix vulnerabilities
npm audit fix

# Force fix (may break)
npm audit fix --force

# Update specific package
npm update package-name

# Update all packages
npx npm-check-updates -u
npm install

# Check for breaking changes
npx npm-check-updates --doctor
```

---

## 4. Authentication & Authorization

### Middleware Protection

```bash
# Check for middleware
ls middleware.ts 2>/dev/null || echo "⚠️ No middleware.ts"

# Check protected routes
grep -rn "session\|isAuthenticated\|auth(" --include="*.ts" --include="*.tsx" app/

# Find unprotected API routes
for f in $(find app/api -name "route.ts"); do
  if ! grep -q "auth\|session\|token" "$f"; then
    echo "⚠️ Potentially unprotected: $f"
  fi
done
```

### Middleware Pattern

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { getToken } from 'next-auth/jwt'

export async function middleware(request: NextRequest) {
  const token = await getToken({ req: request })
  const isAuthPage = request.nextUrl.pathname.startsWith('/login')
  const isProtected = request.nextUrl.pathname.startsWith('/dashboard')
  const isApiProtected = request.nextUrl.pathname.startsWith('/api/protected')
  
  // Redirect to login if not authenticated
  if ((isProtected || isApiProtected) && !token) {
    if (isApiProtected) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  // Redirect to dashboard if already logged in
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*', '/login']
}
```

### Server Action Protection

```typescript
// ❌ No auth check
'use server'
export async function deleteUser(id: string) {
  await db.users.delete({ where: { id } })
}

// ✅ With auth check
'use server'
import { auth } from '@/lib/auth'

export async function deleteUser(id: string) {
  const session = await auth()
  
  if (!session) {
    throw new Error('Unauthorized')
  }
  
  if (!session.user.isAdmin) {
    throw new Error('Forbidden')
  }
  
  await db.users.delete({ where: { id } })
}
```

---

## 5. API Security

### Rate Limiting

```bash
# Check for rate limiting
grep -rn "ratelimit\|rate-limit\|throttle" --include="*.ts" app/api/ lib/
```

```typescript
// Using upstash/ratelimit
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),
  analytics: true,
})

export async function POST(req: Request) {
  const ip = req.headers.get('x-forwarded-for') ?? '127.0.0.1'
  const { success, limit, reset, remaining } = await ratelimit.limit(ip)
  
  if (!success) {
    return Response.json(
      { error: 'Too many requests' },
      { 
        status: 429,
        headers: {
          'X-RateLimit-Limit': limit.toString(),
          'X-RateLimit-Remaining': remaining.toString(),
          'X-RateLimit-Reset': reset.toString()
        }
      }
    )
  }
  
  // Process request
}
```

### CORS Configuration

```typescript
// next.config.ts
export default {
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: 'https://yourdomain.com' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,POST,PUT,DELETE,OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ]
  },
}
```

---

## 6. Security Headers

### Recommended Headers

```typescript
// next.config.ts
const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on'
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()'
  },
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' blob: data: https:;
      font-src 'self';
      connect-src 'self' https://api.yourdomain.com;
      frame-ancestors 'none';
    `.replace(/\s+/g, ' ').trim()
  }
]

export default {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ]
  },
}
```

### Security Audit Checklist

```markdown
- [ ] No hardcoded secrets in code
- [ ] All env vars documented in .env.example
- [ ] .env files in .gitignore
- [ ] npm audit shows no critical/high vulnerabilities
- [ ] All API routes have input validation
- [ ] Auth middleware protects sensitive routes
- [ ] Server actions check authentication
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Rate limiting on public endpoints
- [ ] No dangerouslySetInnerHTML without sanitization
- [ ] CSRF protection on forms
- [ ] Secure cookies (httpOnly, secure, sameSite)
```
