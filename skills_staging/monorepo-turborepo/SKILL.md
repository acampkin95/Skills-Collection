---
name: monorepo-turborepo
description: Turborepo monorepo build system with pnpm workspaces, task pipelines, remote caching, and incremental builds.
version: 2.0.0
reviewed: "2026-06-04"
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

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.