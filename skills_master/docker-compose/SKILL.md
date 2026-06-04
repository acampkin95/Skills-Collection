---
name: docker-compose
description: Docker Compose orchestration for multi-container services. Use for local dev environments, service dependencies, health checks, networking, and production deployment.
version: 2.0.0
reviewed: "2026-06-04"
---
# Docker & Docker Compose Skill

Read the relevant reference file before starting work.

## Quick Navigation

| Task | Reference |
|------|-----------|
| Multi-stage builds, distroless, layer caching | `references/multi-stage-builds.md` |
| Compose overrides, profiles, health checks, patterns | `references/compose-patterns.md` |
| Container debugging, logs, networking, volumes | `references/debugging.md` |

## Dockerfile Best Practices

### Layer Ordering (Most Stable First)

```dockerfile
FROM node:22-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build
```

**Rules:**
- Copy dependency manifests before source code (maximizes cache hits)
- Never use `latest` tag — pin versions (`node:22.12-slim`, `python:3.13-slim`)
- Combine `RUN` commands with `&&` and clean apt caches in same layer
- Copy patterns: `COPY package.json package-lock.json ./` for deps, then `COPY . .` for source

### Multi-Stage Build (Minimal Production Image)

```dockerfile
FROM node:22-slim AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-slim AS production
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

Example: 400MB (builder) → 150MB (production)

### .dockerignore

```
node_modules
.git
.github
.env*
dist
.next
coverage
docker-compose*.yml
Dockerfile*
```

Without `.dockerignore`, `COPY . .` sends everything (including `node_modules`, `.git`) to the daemon.

## Docker Compose v3.8 - v5 Essentials

### Service Definition

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
      args:
        NODE_ENV: development
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/myapp
      REDIS_URL: redis://cache:6379
    env_file:
      - .env.local

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.