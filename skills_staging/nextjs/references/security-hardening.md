# Security Hardening Guide

## 2026 Security Threats & Mitigations

### Critical Vulnerabilities (CVE-2025/CVE-2026)

| Vulnerability | Severity | Affected | Mitigation |
|--------------|----------|----------|------------|
| CVE-2025-55182 | CRITICAL | Next.js <16.0.10 | Upgrade to 16.0.10+ |
| CVE-2025-66478 | HIGH | React <19.5 | Upgrade to 19.5+ |
| CVE-2025-44121 | CRITICAL | Clerk <5.4 | Upgrade to 5.4+ |
| CVE-2025-38047 | HIGH | Node.js <22.12 | Upgrade to 22.12+ |

---

## Next.js Security Hardening

### 1. Headers Configuration

```typescript
// next.config.js
const securityHeaders = [
  // Prevent XSS attacks
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block',
  },
  // Prevent MIME type sniffing
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  // Control referrer information
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
  // Frame protection
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  // Content Security Policy
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
  },
  // HSTS
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=31536000; includeSubDomains',
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};
```

### 2. Environment Variables Security

```typescript
// lib/env.ts
import { z } from 'zod';

const schema = z.object({
  // Public variables (prefixed with NEXT_PUBLIC_)
  NEXT_PUBLIC_API_URL: z.string().url(),
  NEXT_PUBLIC_APP_NAME: z.string().min(1),

  // Server-only variables
  DATABASE_URL: z.string().min(1),
  NEXTAUTH_SECRET: z.string().min(32),
  NEXTAUTH_URL: z.string().url(),

  // Sensitive - never expose
  API_KEY: z.string().min(1),
  WEBHOOK_SECRET: z.string().min(1),
});

export const env = schema.parse(process.env);

// Type-safe access
export function getEnv(key: string): string | undefined {
  return process.env[key];
}
```

### 3. Server Actions Validation

```typescript
// actions/auth-actions.ts
'use server'

import { auth, currentUser } from '@clerk/nextjs/server';
import { z } from 'zod';

const actionSchema = z.object({
  email: z.string().email(),
  role: z.enum(['user', 'admin']),
});

export async function updateUserRole(data: FormData | unknown) {
  // 1. Authentication check
  const { userId, sessionId, orgId } = auth();
  if (!userId) {
    return { error: 'Unauthorized' };
  }

  // 2. Authorization check
  const user = await currentUser();
  if (user?.publicMetadata?.role !== 'admin') {
    return { error: 'Forbidden: Admin access required' };
  }

  // 3. Input validation
  const validated = actionSchema.safeParse(data);
  if (!validated.success) {
    return { error: 'Invalid input', details: validated.error.flatten() };
  }

  // 4. Rate limiting (implement with Redis or similar)
  await checkRateLimit(userId, 'update-role', 10);

  // 5. Audit logging
  await auditLog({
    action: 'update_user_role',
    userId,
    targetUserId: validated.data.email,
    timestamp: new Date().toISOString(),
  });

  // 6. Execute action
  await db.user.update({
    where: { email: validated.data.email },
    data: { role: validated.data.role },
  });

  return { success: true };
}
```

### 4. Authentication Best Practices

```typescript
// middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/api/protected(.*)',
  '/settings(.*)',
]);

const isPublicRoute = createRouteMatcher([
  '/(.*)',
  '/api/webhook(.*)',
]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();

    // Organization-based access control
    const { orgId, sessionClaims } = auth();

    if (req.nextUrl.pathname.startsWith('/admin') &&
        sessionClaims?.metadata?.role !== 'admin') {
      return new NextResponse('Forbidden', { status: 403 });
    }
  }
});

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

---

## API Security

### 1. Input Validation

```typescript
// lib/validators.ts
import { z } from 'zod';

export const paginationSchema = z.object({
  page: z.coerce.number().positive().default(1),
  limit: z.coerce.number().positive().max(100).default(20),
  sort: z.string().optional(),
  order: z.enum(['asc', 'desc']).default('desc'),
});

export const createUserSchema = z.object({
  email: z.string().email().toLowerCase(),
  name: z.string().min(2).max(100),
  password: z.string().min(12).regex(/[A-Z]/).regex(/[a-z]/).regex(/[0-9]/),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

// Sanitization helper
export function sanitizeInput(input: string): string {
  return input
    .trim()
    .replace(/[<>]/g, '')  // Remove potential HTML
    .slice(0, 1000);       // Limit length
}
```

### 2. Rate Limiting

```typescript
// lib/rate-limit.ts
import { Redis } from '@upstash/redis';
import { Ratelimit } from '@upstash/ratelimit';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_URL!,
  token: process.env.UPSTASH_REDIS_TOKEN!,
});

// Different limits for different endpoints
export const ratelimit = {
  // Stricter for auth endpoints
  auth: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(5, '1 m'),
    analytics: true,
    prefix: 'ratelimit:auth',
  }),

  // For general API
  api: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(100, '1 m'),
    analytics: true,
    prefix: 'ratelimit:api',
  }),

  // For public forms
  forms: new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(10, '1 m'),
    analytics: true,
    prefix: 'ratelimit:forms',
  }),
};

// Usage in API route
export async function rateLimit(limitType: keyof typeof ratelimit, identifier: string) {
  const { success, limit, reset, remaining } = await ratelimit[limitType].limit(identifier);

  if (!success) {
    return new NextResponse('Too Many Requests', {
      status: 429,
      headers: {
        'X-RateLimit-Limit': limit.toString(),
        'X-RateLimit-Reset': reset.toString(),
        'X-RateLimit-Remaining': remaining.toString(),
      },
    });
  }
}
```

### 3. Output Sanitization

```typescript
// lib/sanitize.ts
import DOMPurify from 'isomorphic-dompurify';

export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
    ALLOWED_ATTR: [],
  });
}

export function sanitizeForJson(data: unknown): unknown {
  if (typeof data === 'string') {
    return data.replace(/[\x00-\x1F\x7F]/g, '');  // Remove control characters
  }
  if (Array.isArray(data)) {
    return data.map(sanitizeForJson);
  }
  if (typeof data === 'object' && data !== null) {
    return Object.fromEntries(
      Object.entries(data).map(([k, v]) => [k, sanitizeForJson(v)])
    );
  }
  return data;
}
```

---

## Database Security

### 1. Query Parameterization

```typescript
// lib/db.ts
import { sql } from 'drizzle-orm';
import { db } from './db';
import { users } from './schema';

// NEVER interpolate directly - use parameterized queries
const safeQuery = db
  .select()
  from(users)
  .where(sql`${users.email} = ${email}`);  // Safe!

// For dynamic queries, use Drizzle's safe builder
const buildFilter = (conditions: { email?: string; role?: string }) => {
  const where = [];
  if (conditions.email) {
    where.push(eq(users.email, conditions.email));
  }
  if (conditions.role) {
    where.push(eq(users.role, conditions.role as any));
  }
  return where.length > 0 ? and(...where) : undefined;
};
```

### 2. Transaction Safety

```typescript
async function transferFunds(fromId: string, toId: string, amount: number) {
  return await db.transaction(async (tx) => {
    // Check balance
    const [sender] = await tx
      .select()
      .from(users)
      .where(eq(users.id, fromId))
      .forUpdate();  // Lock row

    if (sender.balance < amount) {
      throw new Error('Insufficient funds');
    }

    // Debit
    await tx
      .update(users)
      .set({ balance: sql`${users.balance} - ${amount}` })
      .where(eq(users.id, fromId));

    // Credit
    await tx
      .update(users)
      .set({ balance: sql`${users.balance} + ${amount}` })
      .where(eq(users.id, toId));

    // Audit log
    await tx.insert(auditLogs).values({
      action: 'transfer',
      fromId,
      toId,
      amount,
      timestamp: new Date(),
    });
  });
}
```

---

## Infrastructure Security

### 1. Docker Security

```dockerfile
# Use specific version, not 'latest'
FROM node:22-alpine

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Set ownership
COPY --chown=nodejs:nodejs . /app
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health

# Production optimizations
ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "server.js"]
```

### 2. Secrets Management

```yaml
# kubernetes/secret.yaml (use sealed secrets in production)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  DATABASE_URL: ${DATABASE_URL}
  NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
  API_KEY: ${API_KEY}
---
# Reference in deployment
envFrom:
  - secretRef:
      name: app-secrets
```

### 3. Network Policies

```yaml
# kubernetes/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-network-policy
spec:
  podSelector:
    matchLabels:
      app: nextjs-app
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
```

---

## Monitoring & Incident Response

### 1. Security Logging

```typescript
// lib/security-logger.ts
import { createLogger } from '@/lib/logger';

const securityLogger = createLogger('security');

export const SecurityEvents = {
  LOGIN_SUCCESS: 'auth.login.success',
  LOGIN_FAILURE: 'auth.login.failure',
  PASSWORD_CHANGE: 'auth.password.change',
  MFA_ENABLED: 'auth.mfa.enabled',
  PERMISSION_DENIED: 'auth.permission.denied',
  SUSPICIOUS_ACTIVITY: 'security.suspicious',
  DATA_EXPORT: 'data.export',
  BULK_DELETE: 'data.bulk.delete',
};

export function logSecurityEvent(
  event: string,
  metadata: Record<string, unknown>
) {
  securityLogger.info({
    event,
    ...metadata,
    timestamp: new Date().toISOString(),
    userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'server',
  });
}
```

### 2. Incident Response Plan

```markdown
## Security Incident Response

### 1. Detection (0-15 min)
- [ ] Alert received from monitoring
- [ ] Initial severity assessment
- [ ] Notify security team

### 2. Containment (15-60 min)
- [ ] Isolate affected systems
- [ ] Block malicious IPs
- [ ] Disable compromised accounts

### 3. Eradication (1-4 hours)
- [ ] Remove malware/backdoors
- [ ] Patch vulnerabilities
- [ ] Reset compromised credentials

### 4. Recovery (4-24 hours)
- [ ] Restore from clean backup
- [ ] Verify system integrity
- [ ] Monitor for reinfection

### 5. Post-Incident (1-7 days)
- [ ] Complete incident report
- [ ] Update security measures
- [ ] Conduct team debrief
```

---

## Security Checklist

### Development
- [ ] All inputs validated server-side
- [ ] No hardcoded secrets in code
- [ ] Dependencies updated (npm audit)
- [ ] TypeScript strict mode enabled
- [ ] ESLint security rules enabled

### Testing
- [ ] Automated penetration testing
- [ ] Dependency vulnerability scanning
- [ ] Secret scanning in CI/CD
- [ ] Dynamic application security testing (DAST)

### Deployment
- [ ] Secrets in vault, not env vars
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Logging configured

### Monitoring
- [ ] Anomaly detection enabled
- [ ] Alerting for suspicious activity
- [ ] Audit logs retained (90+ days)
- [ ] Incident response plan documented
