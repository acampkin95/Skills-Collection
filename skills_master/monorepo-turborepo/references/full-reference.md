---
name: monorepo-turborepo
description: Turborepo monorepo build system and workspace orchestration. Use this skill when Turborepo, monorepo, turbo.json, workspace packages, pnpm workspace, npm workspaces, task pipeline, remote caching, docker prune, turbo cache. Use this skill when workspace dependencies, task filtering, turborepo build, shared packages, incremental builds, cache misses, turbo graph.
---

# Turborepo Monorepo Skill

## Quick Navigation

| Task | Reference |
|------|-----------|
| Internal packages, exports field, shared configs, JIT vs prebuild | `references/shared-packages.md` |
| Remote caching, turbo prune, Docker builds, CI/CD optimization | `references/build-optimization.md` |

---

## Repository Structure

### Standard Monorepo Layout

```
my-monorepo/
├── turbo.json                  # Turborepo configuration
├── package.json                # Root workspace config
├── pnpm-workspace.yaml         # pnpm workspace definition (if pnpm)
├── apps/
│   ├── web/                    # Next.js app
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── api/                    # Express/Fastify API
│       ├── package.json
│       └── tsconfig.json
└── packages/
    ├── ui/                     # Shared UI components
    │   ├── package.json
    │   └── src/
    ├── config-typescript/      # Shared tsconfig
    │   ├── package.json
    │   └── base.json
    ├── config-eslint/          # Shared ESLint config
    │   └── package.json
    └── shared/                 # Shared utilities/types
        ├── package.json
        └── src/
```

### Root package.json

```json
{
  "name": "my-monorepo",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "check-types": "turbo run check-types",
    "test": "turbo run test",
    "clean": "turbo run clean"
  },
  "devDependencies": {
    "turbo": "^2"
  },
  "packageManager": "pnpm@9.15.0"
}
```

### Workspace Configuration

**pnpm** (`pnpm-workspace.yaml`):
```yaml
packages:
  - "apps/*"
  - "packages/*"
```

**npm/bun** (root `package.json`):
```json
{
  "workspaces": ["apps/*", "packages/*"]
}
```

---

## turbo.json Configuration

### Task Definitions

```json
{
  "$schema": "https://turborepo.com/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"],
      "inputs": ["src/**", "package.json", "tsconfig.json"]
    },
    "dev": {
      "dependsOn": ["^build"],
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", ".eslintrc.*", "eslint.config.*"]
    },
    "check-types": {
      "dependsOn": ["^build"],
      "inputs": ["**/*.{ts,tsx}", "tsconfig.json"]
    },
    "test": {
      "dependsOn": ["build"],
      "inputs": ["src/**", "test/**", "vitest.config.*"]
    },
    "clean": {
      "cache": false
    }
  }
}
```

### Key Configuration Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `dependsOn` | Task dependencies | `["^build"]` (topological), `["lint"]` (same-package) |
| `outputs` | Files to cache | `["dist/**", ".next/**"]` |
| `inputs` | Files that affect cache key | `["src/**", "tsconfig.json"]` |
| `cache` | Enable/disable caching | `false` for `dev` |
| `persistent` | Long-running task (dev servers) | `true` for `dev` |
| `env` | Environment variables in cache key | `["NODE_ENV", "API_URL"]` |
| `passThroughEnv` | Env vars passed without hashing | `["CI"]` |

### Dependency Operators

```json
{
  "tasks": {
    "build": {
      "dependsOn": [
        "^build",       // Run build in ALL dependencies first (topological)
        "^check-types"  // Also run check-types in dependencies
      ]
    },
    "test": {
      "dependsOn": [
        "build",        // Run build in THIS package first (same package)
        "^build"        // And build in all dependencies
      ]
    },
    "deploy": {
      "dependsOn": [
        "build",
        "test",
        "lint"          // All same-package tasks
      ]
    }
  }
}
```

**`^` prefix** = topological dependency (run in upstream packages first).
**No prefix** = same-package dependency (run in the same package first).

### Environment Variables in Cache Key

```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_API_URL", "NODE_ENV"],
      "passThroughEnv": ["CI", "VERCEL"]
    }
  },
  "globalEnv": ["GITHUB_TOKEN"],
  "globalPassThroughEnv": ["TERM"]
}
```

- `env` — included in task hash (cache key). Change invalidates cache.
- `passThroughEnv` — passed to task but NOT in hash.
- `globalEnv` / `globalPassThroughEnv` — applies to ALL tasks.

### Per-Package Task Overrides

Create `apps/web/turbo.json` to override root config for a specific package:

```json
{
  "$schema": "https://turborepo.com/schema.json",
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": [".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_GA_ID"]
    }
  }
}
```

`"extends": ["//"]` inherits from the root `turbo.json`.

---

## Workspace Dependencies

### Adding Internal Dependencies

```bash
# pnpm — add @repo/ui to the web app
pnpm add @repo/ui --filter web --workspace

# npm
npm install @repo/ui -w apps/web

# bun
bun add @repo/ui --cwd apps/web
```

### App package.json with Internal Deps

```json
{
  "name": "web",
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/shared": "workspace:*",
    "next": "^15",
    "react": "^19"
  },
  "devDependencies": {
    "@repo/config-typescript": "workspace:*",
    "@repo/config-eslint": "workspace:*"
  }
}
```

**`workspace:*`** (pnpm/bun) or `"*"` (npm) — always resolves to the local workspace version.

---

## Task Filtering

### --filter Syntax

```bash
# Run build for a specific package
turbo run build --filter=web

# Run build for a package and all its dependencies
turbo run build --filter=web...

# Run build for all packages that depend on @repo/ui
turbo run build --filter=...@repo/ui

# Run for packages changed since main branch
turbo run build --filter=[main...HEAD]

# Run for changed packages AND their dependents
turbo run build --filter=...[main...HEAD]

# Combine filters
turbo run build --filter=web --filter=api

# Exclude a package
turbo run lint --filter='!@repo/config-eslint'

# Run in directory scope
turbo run build --filter='./apps/*'
```

### Common Filter Patterns

| Filter | Effect |
|--------|--------|
| `--filter=web` | Only `web` package |
| `--filter=web...` | `web` + all its dependencies |
| `--filter=...web` | `web` + all its dependents |
| `--filter='./apps/*'` | All packages in `apps/` |
| `--filter=[HEAD^1]` | Changed since last commit |
| `--filter=[main...HEAD]` | Changed since diverging from `main` |
| `--filter=...{./packages/ui}` | All dependents of packages in `./packages/ui` directory |

---

## TypeScript Configuration

### Shared Base tsconfig (`packages/config-typescript/base.json`)

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "incremental": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "exclude": ["node_modules", "dist"]
}
```

### App tsconfig Extending Base

```json
{
  "extends": "@repo/config-typescript/base.json",
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "ES2022"],
    "jsx": "preserve",
    "outDir": "dist",
    "rootDir": "src",
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src", "next-env.d.ts", ".next/types/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### Package tsconfig with References

```json
{
  "extends": "@repo/config-typescript/base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

---

## Common Commands

```bash
# Run all tasks
turbo run build

# Run with verbose output
turbo run build --verbosity=2

# Dry run — show what WOULD run
turbo run build --dry-run

# Show task graph as text
turbo run build --graph

# Output task graph as DOT/image
turbo run build --graph=graph.svg

# Force re-run (ignore cache)
turbo run build --force

# Limit concurrency
turbo run build --concurrency=4

# Run with summary
turbo run build --summarize

# Clean turbo cache
turbo clean
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Missing `^` in `dependsOn` | `"^build"` for dependencies, `"build"` for same-package |
| `outputs` not configured | Build artifacts won't be cached; set `["dist/**"]` etc. |
| `dev` task cached | Set `"cache": false` and `"persistent": true` for dev servers |
| Cache miss on env var changes | Add env vars to `env` array in task config |
| `workspace:*` not resolving | Ensure package `name` in package.json matches import |
| Circular dependencies | Turborepo detects and errors; restructure packages |
| Wrong `inputs` causing stale cache | Narrow `inputs` to only files that affect the task |
| Missing `--frozen-lockfile` in CI | Always use `pnpm install --frozen-lockfile` in CI |
| Importing from package `src/` directly | Use `exports` field; don't import from internal paths |
| Not extending root turbo.json | Per-package config must have `"extends": ["//"]` |
| `node_modules` in outputs | Never cache `node_modules`; only cache build artifacts |
| Tasks running out of order | Check `dependsOn` graph; use `--graph` to visualize |
