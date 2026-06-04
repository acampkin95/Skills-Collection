# Deployment Guide

Production deployment for Next.js 15/16. For Ubuntu/Nginx/PostgreSQL setup, see `server-infrastructure.md`.

---

## Pre-Deployment Checklist

```bash
# Build verification
rm -rf .next && npm run build

# Type & lint check
npx tsc --noEmit && npm run lint

# Test suite
npm run test:ci

# Check all env vars documented
grep -rn "process.env" --include="*.ts" --include="*.tsx" app/ lib/ src/
```

---

## Environment Variables

### Naming Rules

```bash
# Server-only (NOT exposed to client)
DATABASE_URL=postgres://...
NEXTAUTH_SECRET=...

# Client-exposed (MUST have prefix)
NEXT_PUBLIC_API_URL=https://api.example.com
```

### Validation (Optional)

```typescript
// lib/env.ts
import { z } from 'zod'

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  NEXTAUTH_SECRET: z.string().min(32),
  NEXT_PUBLIC_API_URL: z.string().url(),
})

export const env = envSchema.parse(process.env)
```

---

## Vercel Deployment

```bash
# Install CLI & deploy
npm i -g vercel
vercel link
vercel              # Preview
vercel --prod       # Production

# Environment variables
vercel env add DATABASE_URL production
```

### vercel.json

```json
{
  "framework": "nextjs",
  "regions": ["syd1"],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    }
  ]
}
```

---

## Docker Deployment

### Dockerfile

```dockerfile
# Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

# Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000 HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

### next.config.ts

```typescript
const nextConfig: NextConfig = {
  output: 'standalone',  // Required for Docker
}
```

### Build & Run

```bash
docker build -t myapp:latest --build-arg NEXT_PUBLIC_API_URL=https://api.example.com .
docker run -d -p 3000:3000 -e DATABASE_URL="..." --name myapp myapp:latest
```

---

## Docker Swarm / Traefik

```yaml
# stack.yml
version: '3.8'

services:
  app:
    image: registry.example.com/myapp:${TAG:-latest}
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      labels:
        - traefik.enable=true
        - traefik.http.routers.myapp.rule=Host(`app.example.com`)
        - traefik.http.routers.myapp.entrypoints=websecure
        - traefik.http.routers.myapp.tls.certresolver=letsencrypt
        - traefik.http.services.myapp.loadbalancer.server.port=3000
        - traefik.http.services.myapp.loadbalancer.healthcheck.path=/api/health
    secrets:
      - database_url
    networks:
      - traefik-public

secrets:
  database_url:
    external: true

networks:
  traefik-public:
    external: true
```

```bash
docker stack deploy -c stack.yml myapp
```

---

## Health Check Endpoint

```typescript
// app/api/health/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Optional: Add DB check
    // await db.$queryRaw`SELECT 1`
    
    return NextResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
    })
  } catch {
    return NextResponse.json({ status: 'unhealthy' }, { status: 503 })
  }
}
```

---

## Performance Optimization

### Image Optimization

```typescript
// next.config.ts
images: {
  remotePatterns: [{ protocol: 'https', hostname: '**.example.com' }],
  formats: ['image/avif', 'image/webp'],
},
```

### Caching Headers

```typescript
// next.config.ts
async headers() {
  return [
    {
      source: '/:all*(svg|jpg|png|webp|avif)',
      headers: [{ key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }],
    },
    {
      source: '/_next/static/:path*',
      headers: [{ key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }],
    },
  ]
},
```

---

## Security Headers

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const response = NextResponse.next()
  
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set('Permissions-Policy', 'camera=(), microphone=()')
  
  return response
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

---

## Deployment Checklist

### Before Deploy

- [ ] `npm run build` succeeds
- [ ] `npx tsc --noEmit` passes
- [ ] Tests pass
- [ ] Environment variables documented
- [ ] Security headers configured
- [ ] Health endpoint works

### After Deploy

- [ ] Site loads correctly
- [ ] All routes accessible
- [ ] API endpoints respond
- [ ] No console errors
- [ ] Monitoring configured

### Rollback

```bash
# Vercel
vercel rollback

# Docker Swarm
docker service rollback myapp_app
```

---

## CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npm run lint
      - run: npm run test:ci
      - run: npm run build
      
      # Deploy step depends on your platform
      - run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```
