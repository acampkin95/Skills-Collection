# Build Optimization & Caching

## Remote Caching

### Vercel Remote Cache (Managed)

```bash
# Authenticate (one-time)
npx turbo login

# Link monorepo to Vercel team
npx turbo link
```

This creates `.turbo/config.json`:
```json
{
  "teamId": "team_xxxxxxxxxxxx",
  "apiUrl": "https://vercel.com"
}
```

**CI setup** — set environment variables:
```bash
TURBO_TOKEN=<your-token>       # from Vercel dashboard
TURBO_TEAM=<your-team-slug>
```

```yaml
# .github/workflows/ci.yml
env:
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
  TURBO_TEAM: ${{ vars.TURBO_TEAM }}
```

### Self-Hosted Remote Cache

Use an open-source server like `ducktors/turborepo-remote-cache` or `fox1t/turborepo-remote-cache`:

```bash
TURBO_API=https://cache.example.com
TURBO_TOKEN=<your-secret>
TURBO_TEAM=my-team
```

Or configure in `turbo.json`:
```json
{
  "remoteCache": {
    "enabled": true,
    "apiUrl": "https://cache.example.com"
  }
}
```

---

## Task Hashing

Turborepo creates a hash for each task based on:

1. **Source files** matching `inputs` globs (or all files if `inputs` not set)
2. **Environment variables** listed in `env` and `globalEnv`
3. **Dependency tasks** hashes (from `dependsOn`)
4. **Lockfile** changes for the package
5. **turbo.json** task configuration

### Debugging Cache Misses

```bash
# Show what's included in the hash
turbo run build --summarize

# Compare two runs
turbo run build --dry-run=json > run1.json
# ...make changes...
turbo run build --dry-run=json > run2.json
# diff the hash fields
```

### Optimizing Inputs for Better Cache Hits

```json
{
  "tasks": {
    "lint": {
      "inputs": [
        "src/**/*.{ts,tsx,js,jsx}",
        "eslint.config.*",
        "!src/**/*.test.*"
      ]
    },
    "check-types": {
      "inputs": ["**/*.{ts,tsx}", "tsconfig.json"]
    },
    "test": {
      "inputs": [
        "src/**",
        "test/**",
        "vitest.config.*",
        "jest.config.*"
      ]
    }
  }
}
```

**Narrow `inputs`** = more cache hits. Don't let README changes bust your build cache.

---

## Turbo Prune for Docker

### The Problem

Docker `COPY . .` copies the entire monorepo. This means:
- Massive image contexts
- Every change invalidates the cache
- Unnecessary dependencies installed

### The Solution: `turbo prune`

```bash
# Prune for a specific package, optimized for Docker
turbo prune api --docker
```

This creates:
```
out/
├── json/                      # Only package.json + lockfile (for install layer)
│   ├── package.json
│   └── packages/
│       └── shared/
│           └── package.json
├── full/                      # Full source code (for build layer)
│   ├── apps/
│   │   └── api/
│   └── packages/
│       └── shared/
└── pnpm-lock.yaml             # Pruned lockfile
```

### Optimized Dockerfile with turbo prune

```dockerfile
# ---- Prune Stage ----
FROM node:22-slim AS pruner
RUN corepack enable
WORKDIR /app
COPY . .
RUN npx turbo prune api --docker

# ---- Install Stage ----
FROM node:22-slim AS installer
RUN corepack enable
WORKDIR /app

# Copy pruned package.json files + lockfile (cached unless deps change)
COPY --from=pruner /app/out/json/ .
RUN pnpm install --frozen-lockfile

# Copy full source code
COPY --from=pruner /app/out/full/ .

# Build with turbo
RUN pnpm turbo run build --filter=api

# ---- Runtime Stage ----
FROM node:22-slim AS runner
RUN corepack enable
WORKDIR /app

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

# Copy only built output + production deps
COPY --from=installer /app/apps/api/dist ./dist
COPY --from=installer /app/apps/api/package.json ./
COPY --from=installer /app/node_modules ./node_modules

USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Key insight:** Splitting `json/` (install) and `full/` (source) means Docker only re-runs `pnpm install` when dependencies change — not on every source code edit.

### Next.js Dockerfile with turbo prune

```dockerfile
FROM node:22-slim AS pruner
RUN corepack enable
WORKDIR /app
COPY . .
RUN npx turbo prune web --docker

FROM node:22-slim AS installer
RUN corepack enable
WORKDIR /app
COPY --from=pruner /app/out/json/ .
RUN pnpm install --frozen-lockfile
COPY --from=pruner /app/out/full/ .
RUN pnpm turbo run build --filter=web

FROM node:22-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=installer /app/apps/web/public ./public
COPY --from=installer --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/apps/web/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000 HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
```

Requires `output: "standalone"` in `next.config.ts`.

---

## CI/CD Caching Strategies

### GitHub Actions with Turborepo Cache

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
  TURBO_TEAM: ${{ vars.TURBO_TEAM }}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # needed for --filter=[main...HEAD]

      - uses: pnpm/action-setup@v4
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm

      - run: pnpm install --frozen-lockfile

      # Option A: Remote cache via Vercel (configured via env vars above)
      - run: pnpm turbo run build lint check-types test

      # Option B: Local .turbo cache restored from GitHub Actions cache
      # (use this if NOT using Vercel remote cache)
      # - uses: actions/cache@v4
      #   with:
      #     path: .turbo
      #     key: turbo-${{ runner.os }}-${{ github.sha }}
      #     restore-keys: turbo-${{ runner.os }}-
      # - run: pnpm turbo run build lint check-types test
```

### Affected-Only Builds in CI

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: pnpm/action-setup@v4
        with:
          version: 9

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm

      - run: pnpm install --frozen-lockfile

      # Only build/test packages that changed since main
      - name: Build affected packages
        run: pnpm turbo run build --filter='...[origin/main...HEAD]'

      - name: Test affected packages
        run: pnpm turbo run test --filter='...[origin/main...HEAD]'

      - name: Lint affected packages
        run: pnpm turbo run lint --filter='[origin/main...HEAD]'
```

**`...[origin/main...HEAD]`** = packages changed since `main` AND their downstream dependents.
**`[origin/main...HEAD]`** = ONLY packages with direct changes.

### Parallel Jobs for Independent Tasks

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm turbo run lint

  check-types:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm turbo run check-types

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm turbo run test

  build:
    needs: [lint, check-types, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm turbo run build
```

With remote caching, each job benefits from caches created by previous runs and other jobs.

---

## Performance Tips

| Technique | Impact |
|-----------|--------|
| Enable remote caching | 50-90% faster CI builds |
| Narrow `inputs` per task | Fewer cache misses |
| Use `--filter` in CI | Skip unchanged packages |
| JIT packages (no build step) | Eliminates entire build tasks |
| `--concurrency` tuning | Match to CI runner cores |
| `fetch-depth: 0` in checkout | Required for git-based `--filter` |
| Cache `pnpm store` in CI | Faster installs |
| Separate `lint`/`test`/`build` CI jobs | Parallel execution |
| `turbo prune --docker` | Minimal Docker contexts, better layer caching |
| Set `outputs` on every build task | Without it, Turborepo can't restore cached artifacts |

### Checking Cache Hit Rate

```bash
# After a build, check the summary
turbo run build --summarize

# Look for:
# - FULL TURBO: all tasks cached
# - cache hit/miss ratio in output
```

### Common Cache Busters (and Fixes)

| Problem | Cause | Fix |
|---------|-------|-----|
| Timestamps in output | Build embeds `Date.now()` | Use `SOURCE_DATE_EPOCH` env var |
| Git info in build | `git rev-parse HEAD` in build | Move to runtime, not build time |
| Different env per CI run | `NODE_ENV` not in `env` array | Add to `env` in turbo.json |
| OS-dependent output | Native bindings differ | Separate cache keys per OS |
| Lockfile churn | Different pnpm versions | Pin `packageManager` in root package.json |
