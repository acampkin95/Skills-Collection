# Vite Configuration Patterns

## Project Detection

```bash
grep '"vite":' package.json
ls vite.config.* 2>/dev/null
```

## Base Configurations

### React SPA

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@lib': path.resolve(__dirname, './src/lib'),
    },
  },
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
```

### React + Tailwind v4

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': '/src' },
  },
})
```

### React + Tailwind v3

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // PostCSS handles Tailwind
})
```

### Vue 3

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
```

### Svelte

```typescript
import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
})
```

## SSR Configuration

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    ssr: true,
  },
  ssr: {
    noExternal: ['@company/ui'],  // Bundle these
    external: ['lodash'],         // Keep external
  },
})
```

## Library Mode

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import dts from 'vite-plugin-dts'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    dts({ insertTypesEntry: true }),
  ],
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/index.ts'),
      name: 'MyLibrary',
      formats: ['es', 'cjs'],
      fileName: (format) => `my-library.${format}.js`,
    },
    rollupOptions: {
      external: ['react', 'react-dom'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM',
        },
      },
    },
  },
})
```

## Monorepo Configuration

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@app': path.resolve(__dirname, './src'),
      '@packages/ui': path.resolve(__dirname, '../../packages/ui/src'),
      '@packages/utils': path.resolve(__dirname, '../../packages/utils/src'),
    },
  },
  optimizeDeps: {
    include: ['@packages/ui', '@packages/utils'],
  },
})
```

## Environment Variables

```typescript
// vite.config.ts
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
  envPrefix: 'VITE_',  // Only VITE_ vars exposed to client
})
```

```bash
# .env
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App
```

```typescript
// Usage
const apiUrl = import.meta.env.VITE_API_URL
const isDev = import.meta.env.DEV
const isProd = import.meta.env.PROD
```

```typescript
// Type definitions - src/vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_TITLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

## Proxy Configuration

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/socket.io': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
})
```

## Build Optimization

### Code Splitting

```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu'],
        },
      },
    },
  },
})
```

### Dynamic Chunks

```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react')) return 'vendor-react'
            if (id.includes('@radix-ui')) return 'vendor-radix'
            return 'vendor'
          }
        },
      },
    },
  },
})
```

### Compression

```typescript
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  plugins: [
    react(),
    viteCompression({ algorithm: 'gzip', ext: '.gz' }),
    viteCompression({ algorithm: 'brotliCompress', ext: '.br' }),
  ],
})
```

## Testing with Vitest

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['**/*.{test,spec}.{js,ts,jsx,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
})
```

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => cleanup())
```

## Common Plugins

```typescript
import react from '@vitejs/plugin-react'        // React
import tailwindcss from '@tailwindcss/vite'     // Tailwind v4
import dts from 'vite-plugin-dts'               // TypeScript declarations
import svgr from 'vite-plugin-svgr'             // SVG as React components
import { visualizer } from 'rollup-plugin-visualizer'  // Bundle analysis

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    svgr({ svgrOptions: { icon: true } }),
    visualizer({ open: true, filename: 'dist/stats.html' }),
  ],
})
```

## Troubleshooting

### Module not found
```typescript
resolve: {
  alias: { '@': path.resolve(__dirname, './src') },
}
```

### CORS in development
```typescript
server: {
  proxy: { '/api': 'http://localhost:8080' },
}
```

### Slow HMR
```typescript
optimizeDeps: {
  include: ['large-dependency'],
  exclude: ['local-package'],
}
```

### ESM/CJS mismatch
```typescript
build: {
  rollupOptions: {
    external: ['problematic-package'],
    output: { format: 'es' },
  },
}
```
