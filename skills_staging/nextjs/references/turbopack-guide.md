# Turbopack Guide

Comprehensive reference for Turbopack in Next.js 15/16. Covers configuration, debugging, compatibility, and best practices.

---

## Overview

Turbopack is Next.js's Rust-based bundler, enabled by default in Next.js 15+ development. Significantly faster than webpack for incremental builds.

### Status

| Mode | Turbopack Status |
|------|------------------|
| Development (`next dev`) | ✅ Stable (default in Next.js 15) |
| Production (`next build`) | ⚠️ Beta (opt-in with `--turbopack`) |

### Enabling/Disabling

```json
{
  "scripts": {
    "dev": "next dev",              
    "dev:turbo": "next dev --turbopack",
    "dev:webpack": "NEXT_TURBOPACK=0 next dev",
    "build": "next build",
    "build:turbo": "next build --turbopack"
  }
}
```

---

## Configuration

### next.config.ts

```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Turbopack-specific config (Next.js 15.3+)
  turbopack: {
    // Custom loaders
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
    
    // Resolve aliases
    resolveAlias: {
      'old-package': 'new-package',
    },
    
    // Monorepo root
    root: process.cwd(),
  },
  
  // Server-external packages (works with both bundlers)
  serverExternalPackages: ['sharp', '@prisma/client'],
}

export default nextConfig
```

### Monorepo Configuration

```typescript
import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  turbopack: {
    // Point to monorepo root
    root: path.join(__dirname, '../..'),
  },
  
  // Transpile workspace packages
  transpilePackages: ['@myorg/ui', '@myorg/shared'],
}

export default nextConfig
```

---

## Common Issues & Fixes

### Issue: Build Fails with Turbopack

**Symptom:** Dev works, but `next build --turbopack` fails

**Common causes:**

1. **Incompatible webpack plugins**
2. **Custom webpack config not supported**
3. **Dynamic requires**

**Fix: Use conditional config**

```typescript
// next.config.ts
const isUsingTurbopack = process.env.TURBOPACK === '1'

const nextConfig: NextConfig = {
  // Turbopack config
  turbopack: {
    rules: { /* ... */ },
  },
  
  // Webpack config (only used when Turbopack disabled)
  webpack: isUsingTurbopack ? undefined : (config) => {
    // Custom webpack config
    return config
  },
}
```

### Issue: Module Not Found

**Symptom:** `Cannot find module 'xyz'` only with Turbopack

**Causes:**

1. **Different resolution algorithm**
2. **Missing file extensions**
3. **Alias not configured**

**Fixes:**

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  turbopack: {
    resolveAlias: {
      // Explicit aliases
      '@components': './src/components',
      '@lib': './src/lib',
    },
    
    // Add extensions
    resolveExtensions: ['.tsx', '.ts', '.jsx', '.js', '.json'],
  },
}
```

### Issue: Custom Loader Not Working

**Symptom:** SVGs, MDX, or other files not processed

**Fix: Configure Turbopack rules**

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      // SVG as React components
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
      
      // MDX support
      '*.mdx': {
        loaders: ['@mdx-js/loader'],
        as: '*.js',
      },
      
      // GraphQL
      '*.graphql': {
        loaders: ['graphql-tag/loader'],
        as: '*.js',
      },
    },
  },
}
```

### Issue: Slow Initial Build

**Symptom:** First build takes long time

**Cause:** Cold cache, large dependency tree

**Fixes:**

```bash
# 1. Ensure persistent cache directory
# Turbopack caches to .next/cache

# 2. Check for large dependencies
npm ls --all | wc -l

# 3. Externalize large server packages
```

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  serverExternalPackages: [
    'sharp',
    '@prisma/client',
    'puppeteer',
    // Add other large packages
  ],
}
```

### Issue: Memory Issues

**Symptom:** Out of memory errors, system slowdown

**Fixes:**

```bash
# 1. Increase Node memory limit
NODE_OPTIONS='--max-old-space-size=8192' npm run dev

# 2. Check for memory leaks in dev
# Watch memory in Activity Monitor/htop

# 3. Reduce scope
```

```typescript
// next.config.ts  
const nextConfig: NextConfig = {
  turbopack: {
    // Limit file watching scope
    root: './src',
  },
}
```

### Issue: HMR (Hot Module Replacement) Not Working

**Symptom:** Changes don't reflect without full reload

**Diagnostic:**

```bash
# Check terminal for HMR messages
# Should see: "compiled successfully"

# Check browser console for WebSocket errors
```

**Fixes:**

1. **Check file is being watched**
2. **Clear .next cache**: `rm -rf .next`
3. **Check for syntax errors in file**
4. **Verify component exports correctly**

```typescript
// ✅ CORRECT - Named or default export
export function Component() { }
export default Component

// ❌ WRONG - No export
function Component() { }
```

### Issue: CSS Not Updating

**Symptom:** Tailwind changes require restart

**Fixes:**

```css
/* Ensure proper @source directives */
@import "tailwindcss";
@source "./src";
```

```bash
# Clear cache
rm -rf .next && npm run dev
```

---

## Compatibility

### Supported Features

| Feature | Support |
|---------|---------|
| TypeScript | ✅ Full |
| CSS Modules | ✅ Full |
| Tailwind CSS | ✅ Full |
| PostCSS | ✅ Full |
| Sass/SCSS | ✅ Full |
| Image Optimization | ✅ Full |
| API Routes | ✅ Full |
| Server Components | ✅ Full |
| Client Components | ✅ Full |
| Dynamic Imports | ✅ Full |
| next/font | ✅ Full |
| MDX | ✅ With config |
| SVG imports | ✅ With config |

### Known Limitations

| Feature | Status |
|---------|--------|
| webpack plugins | ❌ Not compatible |
| Custom webpack config | ⚠️ Partial (some options) |
| Some babel plugins | ❌ Use SWC instead |
| @next/bundle-analyzer | ❌ Webpack only |
| Sentry webpack plugin | ⚠️ Use Sentry SDK |

### Plugin Migration

```typescript
// BEFORE: Webpack plugin
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})
module.exports = withBundleAnalyzer(nextConfig)

// AFTER: Use Turbopack-compatible approach
// For bundle analysis, use build output or external tools
const nextConfig: NextConfig = {
  // No webpack-specific plugins
}
```

---

## Debugging

### Enable Verbose Logging

```bash
# Debug mode
TURBOPACK_DEBUG=1 npm run dev

# Trace mode (very verbose)
TURBOPACK_TRACE=1 npm run dev
```

### Check Cache

```bash
# Cache location
ls -la .next/cache/

# Clear cache
rm -rf .next/cache
```

### Compare with Webpack

```bash
# Run with webpack to isolate Turbopack issues
NEXT_TURBOPACK=0 npm run dev
# or
npm run dev:webpack
```

### Performance Profiling

```bash
# Generate trace file
TURBOPACK_TRACE_FILE=trace.json npm run dev

# Analyze trace
# Open in chrome://tracing or perfetto
```

---

## Best Practices

### 1. Keep Config Simple

```typescript
// ✅ GOOD - Minimal config
const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      '*.svg': { loaders: ['@svgr/webpack'], as: '*.js' },
    },
  },
}

// ❌ AVOID - Complex webpack config
const nextConfig: NextConfig = {
  webpack: (config) => {
    // Complex modifications
    return config
  },
}
```

### 2. Use Built-in Features

```typescript
// ✅ Use next/font instead of custom font loaders
import { Inter } from 'next/font/google'

// ✅ Use next/image instead of custom image plugins
import Image from 'next/image'

// ✅ Use CSS Modules instead of CSS-in-JS requiring webpack
import styles from './Component.module.css'
```

### 3. Externalize Heavy Server Packages

```typescript
const nextConfig: NextConfig = {
  serverExternalPackages: [
    'sharp',           // Image processing
    '@prisma/client',  // Database
    'puppeteer',       // Browser automation
    'canvas',          // Graphics
    '@aws-sdk/*',      // AWS SDK
  ],
}
```

### 4. Monorepo Setup

```typescript
// apps/web/next.config.ts
import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  turbopack: {
    root: path.join(__dirname, '../..'),  // Monorepo root
  },
  transpilePackages: [
    '@repo/ui',
    '@repo/shared',
  ],
}

export default nextConfig
```

### 5. CI/CD Configuration

```yaml
# .github/workflows/build.yml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Cache Turbopack
        uses: actions/cache@v4
        with:
          path: |
            .next/cache
          key: turbopack-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            turbopack-
      
      - name: Build
        run: npm run build
```

---

## Migration: Webpack to Turbopack

### Step 1: Audit Current Config

```bash
# Check for webpack plugins
grep -n "webpack" next.config.*

# Check for custom loaders
grep -n "loader" next.config.*
```

### Step 2: Replace Webpack Plugins

| Webpack Plugin | Turbopack Alternative |
|----------------|----------------------|
| @next/bundle-analyzer | Build output analysis |
| terser-webpack-plugin | Built-in minification |
| css-minimizer-webpack-plugin | Built-in |
| copy-webpack-plugin | Use public/ directory |
| @svgr/webpack | Configure in turbopack.rules |

### Step 3: Update Config

```typescript
// BEFORE
const nextConfig = {
  webpack: (config) => {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    })
    return config
  },
}

// AFTER
const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      '*.svg': {
        loaders: ['@svgr/webpack'],
        as: '*.js',
      },
    },
  },
}
```

### Step 4: Test

```bash
# Test development
npm run dev

# Compare with webpack
NEXT_TURBOPACK=0 npm run dev

# Test production build
npm run build
```

---

## Troubleshooting Checklist

```bash
# 1. Check Turbopack is being used
# Terminal should show: "▲ Next.js 15.x (Turbopack)"

# 2. Verify Next.js version
npm ls next

# 3. Check for incompatible config
grep -E "webpack|experimental" next.config.*

# 4. Clear all caches
rm -rf .next node_modules/.cache

# 5. Check for errors in terminal
# Look for red error messages

# 6. Compare with webpack
NEXT_TURBOPACK=0 npm run dev

# 7. Check browser console
# Look for module resolution errors

# 8. Enable debug logging
TURBOPACK_DEBUG=1 npm run dev 2>&1 | head -100
```
