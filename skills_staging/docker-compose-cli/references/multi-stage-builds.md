# Multi-Stage Builds Reference

## Why Multi-Stage?

Single-stage images include build tools, dev dependencies, and source — inflating image size and attack surface. Multi-stage builds copy only production artifacts into the final image.

```
Single stage:  1.2 GB (node:22 + devDeps + source + build output)
Multi-stage:   180 MB (node:22-slim + prodDeps + build output)
Distroless:     95 MB (gcr.io/distroless/nodejs22 + build output)
```

---

## Node.js Multi-Stage Template

```dockerfile
# syntax=docker/dockerfile:1

# === 1. Dependencies Stage ===
FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# === 2. Build Stage ===
FROM node:22-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# === 3. Production Dependencies ===
FROM node:22-slim AS prod-deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# === 4. Production Stage ===
FROM node:22-slim AS production
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Why Separate deps and prod-deps Stages?

- `deps`: all dependencies (including devDependencies for build)
- `prod-deps`: only production dependencies for the final image
- This avoids shipping TypeScript, ESLint, testing libraries in production

---

## Python Multi-Stage Template

```dockerfile
# syntax=docker/dockerfile:1

# === Build Stage ===
FROM python:3.13-slim AS builder
WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .

# === Production Stage ===
FROM python:3.13-slim AS production
WORKDIR /app

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

COPY --from=builder /install /usr/local
COPY --from=builder /app/src ./src

USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Go Multi-Stage Template (Scratch Final)

```dockerfile
# syntax=docker/dockerfile:1

FROM golang:1.23 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /server ./cmd/server

# Scratch — no OS, no shell, minimal attack surface
FROM scratch AS production
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

---

## Next.js Standalone Build

```dockerfile
# syntax=docker/dockerfile:1

FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-slim AS production
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Next.js standalone output — includes only necessary files
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
```

**Requires** in `next.config.ts`:
```typescript
export default {
  output: "standalone",
};
```

---

## Distroless Base Images

Distroless images contain only the runtime — no shell, no package manager, no OS utilities:

```dockerfile
# Node.js distroless
FROM gcr.io/distroless/nodejs22-debian12 AS production
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/node_modules /app/node_modules
WORKDIR /app
CMD ["dist/index.js"]

# Python distroless
FROM gcr.io/distroless/python3-debian12 AS production
COPY --from=builder /install /usr/local
COPY --from=builder /app/src /app/src
WORKDIR /app
CMD ["src/main.py"]

# Static binary (Go, Rust)
FROM gcr.io/distroless/static-debian12 AS production
COPY --from=builder /server /server
ENTRYPOINT ["/server"]
```

**Trade-offs:**
- Smaller images, fewer CVEs, immutable
- Cannot `docker exec sh` for debugging — use debug variant: `gcr.io/distroless/nodejs22-debian12:debug`

---

## Layer Caching Strategies

### 1. Order by Change Frequency

```dockerfile
# Rarely changes → cache hit
COPY package.json package-lock.json ./
RUN npm ci

# Changes often → only this layer rebuilds
COPY . .
RUN npm run build
```

### 2. BuildKit Cache Mounts

```dockerfile
# npm cache persists across builds (not stored in image)
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Go module cache
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

# apt cache
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y curl
```

### 3. Remote Cache (CI/CD)

```bash
# Push cache to registry
docker buildx build \
  --cache-to type=registry,ref=registry.example.com/app:cache,mode=max \
  --cache-from type=registry,ref=registry.example.com/app:cache \
  -t registry.example.com/app:latest \
  --push .
```

In `docker-bake.hcl`:
```hcl
target "app" {
  cache-from = ["type=registry,ref=registry.example.com/app:cache"]
  cache-to   = ["type=registry,ref=registry.example.com/app:cache,mode=max"]
}
```

### 4. GitHub Actions Cache

```yaml
# .github/workflows/build.yml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/org/app:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

---

## Build Args vs Environment Variables

```dockerfile
# ARG — available only during build, not in running container
ARG NODE_ENV=production
ARG BUILDKIT_INLINE_CACHE=1

# ENV — available during build AND at runtime
ENV NODE_ENV=production
ENV PORT=3000

# Common pattern: ARG that sets ENV
ARG APP_VERSION=unknown
ENV APP_VERSION=$APP_VERSION
```

```yaml
# docker-compose.yml
services:
  app:
    build:
      args:
        NODE_ENV: production        # Sets ARG during build
        APP_VERSION: "1.2.3"
    environment:
      DATABASE_URL: postgres://...  # Sets ENV at runtime
```

| Feature | `ARG` | `ENV` |
|---------|-------|-------|
| Available during build | Yes | Yes |
| Available at runtime | No | Yes |
| Stored in image layers | No (unless used in RUN) | Yes |
| Overridable at build | `--build-arg` | No |
| Overridable at run | No | `-e` / `environment:` |

**Security rule:** Never pass secrets as `ARG` — they appear in image history. Use `--mount=type=secret` instead:

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/app/.npmrc \
    npm ci
```

```bash
docker buildx build --secret id=npmrc,src=.npmrc .
```

---

## Multi-Platform Builds

```bash
# Create builder with multi-platform support
docker buildx create --name multiarch --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t registry.example.com/app:latest \
  --push .
```

In `docker-bake.hcl`:
```hcl
target "app" {
  platforms = ["linux/amd64", "linux/arm64"]
}
```

**Note:** Cross-compilation is much faster than emulation. For Go:
```dockerfile
ARG TARGETPLATFORM
ARG TARGETOS
ARG TARGETARCH
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build -o /server
```

---

## Image Size Comparison

| Base Image | Size | Shell | Use Case |
|------------|------|-------|----------|
| `node:22` | ~1.1 GB | Yes | Development only |
| `node:22-slim` | ~200 MB | Yes | Production (most common) |
| `node:22-alpine` | ~130 MB | Yes | Size-critical (musl libc — test thoroughly) |
| `gcr.io/distroless/nodejs22` | ~95 MB | No | Security-critical |
| `scratch` | 0 MB | No | Static binaries (Go, Rust) |

**Recommendation:** Use `-slim` variants for most production workloads. Use `alpine` only if you've tested musl compatibility. Use `distroless` for maximum security.
