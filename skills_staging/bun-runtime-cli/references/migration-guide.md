# Node.js to Bun Migration Guide

## Step 1: Install Bun

```bash
# macOS/Linux
curl -fsSL https://bun.sh/install | bash

# Windows (via scoop)
scoop install bun

# Verify
bun --version
```

## Step 2: Replace Runtime

Simply use `bun` instead of `node`:

```bash
# Before
node index.js
node --watch index.js
npx ts-node index.ts

# After
bun index.js
bun --watch index.js
bun index.ts  # No transpilation needed!
```

## Step 3: Replace Package Manager

```bash
# Before
npm install
npm add react
npm run build
npx prettier --write .

# After
bun install
bun add react
bun run build
bunx prettier --write .
```

Bun uses compatible `package.json` and `node_modules`, so it works seamlessly.

## Step 4: Remove Unnecessary Dependencies

When migrating to Bun, you can remove:

```json
{
  "devDependencies": {
    "typescript": "REMOVE - native support",
    "ts-node": "REMOVE - use bun directly",
    "ts-node-dev": "REMOVE - use bun --watch",
    "ts-jest": "REMOVE - use bun test",
    "jest": "REMOVE - use bun test",
    "@types/node": "REMOVE - built-in types"
  }
}
```

Keep packages you actually use (React, etc.), just remove the tooling ones.

## Step 5: Update Scripts in package.json

```json
{
  "scripts": {
    "dev": "bun run src/index.ts",
    "build": "bun run build.ts",
    "test": "bun test",
    "test:watch": "bun test --watch",
    "format": "bunx prettier --write ."
  }
}
```

## Compatibility Issues & Fixes

### CommonJS vs ES Modules

**Node.js quirk**: `__dirname` and `__filename` don't exist in ESM.

**Bun solution**: Import from `bun` (works in both CJS and ESM):

```typescript
import { dirname, filename } from "bun";

console.log(dirname(import.meta.url));  // /path/to/dir
console.log(filename(import.meta.url)); // file.ts
```

Or use standard approach:

```typescript
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
```

### require() in ESM Files

Node.js ESM doesn't allow `require()`. Bun allows it!

```typescript
// In .ts or .tsx
const { myFunction } = require("./module.js"); // Works in Bun!

// Still recommended: use import
import { myFunction } from "./module.js";
```

### process.env

Works identically in Bun, but you can also omit `.env` loading boilerplate:

```typescript
// Before (Node.js)
import dotenv from "dotenv";
dotenv.config();
console.log(process.env.DATABASE_URL);

// After (Bun)
// Just use process.env - .env is auto-loaded
console.log(process.env.DATABASE_URL);

// Or explicit:
bun --env-file=.env run index.ts
```

### npm Packages

Most npm packages work out-of-the-box. If you hit issues:

1. **Node.js polyfills needed?** Check `bun:` imports first:
   - `bun:sqlite` instead of `better-sqlite3`
   - `bun:ffi` for native library binding
   - Web APIs (`fetch`, `WebSocket`) are native

2. **Native modules?** Bun supports Node-API (napi). If a package uses `node-gyp`, it may need recompilation.

3. **ESM-only packages?** Bun handles them fine. CJS packages also work.

### TypeScript Configuration

**Node.js** requires `tsconfig.json` and a transpiler.

**Bun** doesn't require `tsconfig.json`, but respects it if present:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true
  }
}
```

Bun ignores some options (`module`, `target`) and enforces modern defaults.

### Cross-Platform Scripts

**Node.js** requires `cross-env` for Windows compatibility:

```json
{
  "scripts": {
    "dev": "cross-env NODE_ENV=development node server.js"
  }
}
```

**Bun Shell** handles this natively:

```typescript
#!/usr/bin/env bun
import { $ } from "bun";

process.env.NODE_ENV = "development";
await $`some-command`;
```

Or use Bun Shell in package.json:

```json
{
  "scripts": {
    "clean": "bun ./scripts/clean.ts"
  }
}
```

## Performance Tips After Migration

1. **Use Bun APIs** instead of Node.js equivalents:
   - `Bun.file()` instead of `fs.readFileSync()`
   - `Bun.serve()` instead of Express (10× faster)
   - `bun:sqlite` instead of `sqlite3` npm package

2. **Leverage `bun --watch`** instead of nodemon:
   ```bash
   bun --watch src/index.ts
   ```

3. **Use Bun Shell** for build scripts:
   ```typescript
   #!/usr/bin/env bun
   import { $ } from "bun";
   await $`npm run test && bun run build`;
   ```

4. **Lazy imports** (Bun startup is already fast, but helps with CLI tools):
   ```typescript
   const { heavyDependency } = await import("./heavy.ts");
   ```

## Verification Checklist

- [ ] Bun installed (`bun --version`)
- [ ] `bun install` runs successfully
- [ ] `bun run dev` works without errors
- [ ] `bun test` finds and runs tests
- [ ] Remove `typescript`, `ts-node`, etc. from devDependencies
- [ ] Test cross-platform (Windows, macOS, Linux)
- [ ] Verify database/file access works
- [ ] Check environment variable loading
- [ ] Confirm third-party packages work

## Rollback if Needed

If you need to rollback to Node.js:

```bash
# Reinstall npm packages
npm install

# Update scripts in package.json to use "node"
# Update imports to use Node.js APIs

# Reinstall type definitions
npm install -D @types/node
```

Bun is **100% backward compatible** — you can switch back anytime.
