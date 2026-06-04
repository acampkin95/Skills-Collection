---
name: bun-runtime
description: Bun v1.3 high-performance JS/TS runtime, package manager, bundler, and test runner. 10-20x faster startup than Node.js, native TypeScript, Bun Shell, Bun.sql.
version: 2.0.0
reviewed: "2026-06-04"
---

# Bun v1.3 Runtime Skill

**Bun** is an all-in-one JavaScript runtime, toolkit, and package manager.

## Quick Router

| Need | Reference |
|------|-----------|
| **File system, HTTP, SQLite APIs** | `references/bun-apis.md` |
| **Node.js → Bun migration guide** | `references/migration-guide.md` |
| **Test runner, CLI examples** | This page |

## Why Bun?

- **10-20× faster** than Node.js for startup and I/O
- **Native TypeScript/JSX** - no compilation step needed
- **Built-in test runner** with mocking and coverage
- **Bun Shell** - cross-platform scripting (works on Windows/Linux/macOS)
- **Drop-in Node.js compatibility** - most npm packages work

## Quick Start

```bash
# Create new project
bun create template my-app

# Run TypeScript directly (no build step)
bun run index.ts

# Install dependencies (10× faster than npm)
bun install

# Run tests
bun test

# Package manager mode (use with node projects too)
bunx prettier --write .
```

## Key Differences from Node.js

| Feature | Node.js | Bun |
|---------|---------|-----|
| Startup time | ~100-500ms | ~5-20ms |
| Package manager | npm/pnpm/yarn | **Built-in** (drop-in) |
| TypeScript | Requires tsc/ts-node | **Native** - no build |
| Test runner | External (jest/vitest) | **Built-in** |
| Shell scripts | node:child_process | **Bun Shell** (cross-platform) |

## Test Framework

```typescript
// math.test.ts
import { test, expect, beforeEach, mock } from "bun:test";

// Basic test
test("addition", () => {
  expect(2 + 2).toBe(4);
});

// Async test
test("fetch user", async () => {
  const user = await getUser(1);
  expect(user).toEqual({ id: 1, name: "Alice" });
});

// Mocking
const mockFetch = mock(async (url: string) => {
  return Response.json({ id: 1, name: "Mocked" });
});

globalThis.fetch = mockFetch;

test("with mocked fetch", async () => {
  const user = await fetchUser(1);
  expect(mockFetch).toHaveBeenCalled();
  expect(user.name).toBe("Mocked");
});
```

Run tests with coverage:

```bash
bun test --coverage
```

## Bun Shell - Cross-Platform Scripting

```typescript
#!/usr/bin/env bun
// build.ts - works on Windows, Linux, macOS

import { $ } from "bun";

// Run commands (no cross-platform issues)
await $`mkdir -p dist`;
await $`rm -rf dist/*.js`;

// Chaining with && and ||
await $`tsc --noEmit && vite build`;

// Capture output
const gitBranch = await $`git branch --show-current`.text();
console.log(`Building on branch: ${gitBranch.trim()}`);

// Exit on error by default
await $`npm run test`;

// Quiet mode
await $`echo "This won't print"`.quiet();

// Conditional execution
const result = await $`some-command`.exitCode();
if (result !== 0) {
  console.error("Command failed");
  process.exit(1);
}
```

## Package Manager

```bash
# Install dependencies (faster than npm/pnpm/yarn)
bun install

# Add package
bun add react react-dom

# Add dev dependency
bun add -d typescript @types/react

# Run package (like npx)
bunx prettier --write .

# Lockfile format: bun.lockb (binary, faster parsing)
```

In package.json scripts, just use "bun":

```json
{
  "scripts": {
    "dev": "bun run src/index.ts",
    "build": "bun run build.ts",
    "test": "bun test"
  }
}
```

## Hot Reload

```bash
bun --watch src/index.ts
```

Automatically restarts on file changes. No need for nodemon or ts-node-dev.

## Environment Variables

```bash
# Load .env file automatically
bun --env-file=.env run src/index.ts

# Or use process.env (dotenv built-in)
# .env files are automatically loaded in development
DATABASE_URL="postgres://localhost/db" bun run src/index.ts
```

## HTTP Server

```typescript
// server.ts
Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === "/api/users") {
      return Response.json({ users: [] });
    }
    return new Response("Not Found", { status: 404 });
  },
});

console.log("Server running on http://localhost:3000");
```

## Bun.sql — Unified Database API (v1.3+)

```typescript
import { SQL } from "bun";

// Single API for PostgreSQL, MySQL/MariaDB, SQLite
const db = new SQL("postgres://localhost/mydb");
const rows = await db`SELECT * FROM users WHERE id = ${userId}`;

// Also works with MySQL and SQLite
const mysql = new SQL("mysql://localhost/mydb");
const sqlite = new SQL("sqlite://data.db");
```

## Bun.redis — Native Redis Client (v1.3+)

```typescript
import { Redis } from "bun";

const redis = new Redis();
await redis.set("key", "value");
const val = await redis.get("key");
// 7.9x faster than ioredis in benchmarks
// Supports Pub/Sub, auto-reconnect, Valkey
```

## Single-Executable Deployment

```bash
# Compile to standalone binary (no Bun install needed on target)
bun build --compile src/index.ts --outfile myapp
./myapp  # Runs anywhere, no runtime dependency
```

## When to Use Bun

- ✅ New TypeScript/JavaScript projects
- ✅ Replacing Node.js CLI tools
- ✅ Cross-platform shell scripts (Bun Shell)
- ✅ Fast test execution with built-in runner
- ✅ AWS Lambda / serverless functions (fast cold starts)
- ✅ Production HTTP servers (1.8x faster than nginx — used by Midjourney)
- ✅ Database-connected services via Bun.sql
- ✅ Single-executable deployments via `bun build --compile`

## Reference Files

- `references/bun-apis.md` - File system, HTTP, SQLite, Redis, native APIs
- `references/migration-guide.md` - Node.js → Bun migration patterns
