# Internal Packages & Shared Configuration

## Package Types: JIT vs Prebuild

Turborepo supports two strategies for internal packages:

### Just-in-Time (JIT) Packages (Recommended for Most Cases)

The consuming app's bundler compiles the TypeScript directly. **No build step needed.**

```json
{
  "name": "@repo/ui",
  "private": true,
  "type": "module",
  "exports": {
    "./button": "./src/button.tsx",
    "./card": "./src/card.tsx",
    "./dialog": "./src/dialog.tsx"
  },
  "scripts": {
    "lint": "eslint . --max-warnings 0",
    "check-types": "tsc --noEmit"
  },
  "devDependencies": {
    "@repo/config-typescript": "workspace:*",
    "typescript": "^5.7"
  },
  "peerDependencies": {
    "react": "^18 || ^19",
    "react-dom": "^18 || ^19"
  }
}
```

**Advantages:** No build step, faster development, simpler config.
**Requirement:** The consuming application's bundler (Next.js, Vite) must support transpiling workspace packages.

**Next.js** handles this automatically via `transpilePackages` (Next 13+) or automatically if using `next.config.ts`. Vite requires `optimizeDeps.include` or a plugin.

### Prebuilt (Compiled) Packages

Compiled to JS before consumption. Required for packages consumed by Node.js directly or published to npm.

```json
{
  "name": "@repo/shared",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "lint": "eslint . --max-warnings 0",
    "check-types": "tsc --noEmit"
  },
  "exports": {
    ".": {
      "types": "./src/index.ts",
      "default": "./dist/index.js"
    },
    "./utils": {
      "types": "./src/utils.ts",
      "default": "./dist/utils.js"
    }
  },
  "devDependencies": {
    "@repo/config-typescript": "workspace:*",
    "typescript": "^5.7"
  }
}
```

**turbo.json must include the build task:**
```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    }
  }
}
```

### When to Use Each

| Strategy | When |
|----------|------|
| JIT | UI components, shared React hooks, utilities consumed by bundled apps |
| Prebuilt | Server-side packages, CLI tools, packages with complex build (codegen), npm publishable packages |

---

## Exports Field Patterns

### Simple (JIT — TypeScript Direct)

```json
{
  "exports": {
    ".": "./src/index.ts",
    "./button": "./src/button.tsx",
    "./hooks": "./src/hooks/index.ts"
  }
}
```

### Conditional Exports (Prebuilt)

```json
{
  "exports": {
    ".": {
      "types": "./src/index.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "default": "./dist/index.js"
    },
    "./utils": {
      "types": "./src/utils.ts",
      "default": "./dist/utils.js"
    }
  }
}
```

### Wildcard Exports

```json
{
  "exports": {
    "./*": {
      "types": "./src/*.ts",
      "default": "./dist/*.js"
    }
  }
}
```

### Package with Styles

```json
{
  "exports": {
    ".": {
      "types": "./src/index.ts",
      "default": "./src/index.tsx"
    },
    "./styles.css": "./dist/styles.css"
  }
}
```

---

## Shared UI Components Package

### Full Example: `packages/ui/`

**`packages/ui/package.json`**:
```json
{
  "name": "@repo/ui",
  "private": true,
  "type": "module",
  "exports": {
    "./button": "./src/button.tsx",
    "./card": "./src/card.tsx",
    "./dialog": "./src/dialog.tsx",
    "./input": "./src/input.tsx",
    "./label": "./src/label.tsx",
    "./cn": "./src/lib/cn.ts"
  },
  "scripts": {
    "lint": "eslint . --max-warnings 0",
    "check-types": "tsc --noEmit"
  },
  "dependencies": {
    "class-variance-authority": "^0.7",
    "clsx": "^2",
    "tailwind-merge": "^2"
  },
  "devDependencies": {
    "@repo/config-typescript": "workspace:*",
    "react": "^19",
    "react-dom": "^19",
    "typescript": "^5.7"
  },
  "peerDependencies": {
    "react": "^18 || ^19",
    "react-dom": "^18 || ^19"
  }
}
```

**`packages/ui/src/button.tsx`**:
```tsx
import { type VariantProps, cva } from "class-variance-authority";
import { cn } from "./lib/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        outline: "border border-input bg-background hover:bg-accent",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 px-3",
        lg: "h-11 px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}
```

**`packages/ui/src/lib/cn.ts`**:
```ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### Consuming the UI Package

```tsx
// apps/web/src/app/page.tsx
import { Button } from "@repo/ui/button";
import { Card } from "@repo/ui/card";

export default function Page() {
  return (
    <Card>
      <Button variant="outline" size="sm">
        Click me
      </Button>
    </Card>
  );
}
```

---

## Shared Configuration Packages

### TypeScript Config (`packages/config-typescript/`)

**`package.json`**:
```json
{
  "name": "@repo/config-typescript",
  "private": true,
  "files": ["base.json", "nextjs.json", "react-library.json", "node.json"]
}
```

**`base.json`**:
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
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "verbatimModuleSyntax": true
  },
  "exclude": ["node_modules", "dist"]
}
```

**`nextjs.json`**:
```json
{
  "extends": "./base.json",
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "ES2022"],
    "jsx": "preserve",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowJs": true,
    "noEmit": true,
    "plugins": [{ "name": "next" }]
  }
}
```

**`react-library.json`**:
```json
{
  "extends": "./base.json",
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "ES2022"],
    "jsx": "react-jsx"
  }
}
```

**`node.json`**:
```json
{
  "extends": "./base.json",
  "compilerOptions": {
    "module": "NodeNext",
    "moduleResolution": "nodenext",
    "outDir": "dist",
    "rootDir": "src"
  }
}
```

**Usage in an app:**
```json
{
  "extends": "@repo/config-typescript/nextjs.json",
  "compilerOptions": {
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src", "next-env.d.ts", ".next/types/**/*.ts"]
}
```

### ESLint Config (`packages/config-eslint/`)

**`package.json`**:
```json
{
  "name": "@repo/config-eslint",
  "private": true,
  "type": "module",
  "exports": {
    "./base": "./base.js",
    "./next": "./next.js",
    "./react": "./react.js",
    "./node": "./node.js"
  },
  "dependencies": {
    "@eslint/js": "^9",
    "typescript-eslint": "^8",
    "eslint-plugin-react": "^7",
    "eslint-plugin-react-hooks": "^5",
    "globals": "^15"
  }
}
```

**`base.js`**:
```js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import globals from "globals";

/** @type {import("eslint").Linter.Config[]} */
export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    languageOptions: {
      globals: { ...globals.node },
    },
    rules: {
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },
  { ignores: ["dist/", ".next/", "node_modules/"] },
];
```

**Usage in an app (`apps/web/eslint.config.js`):**
```js
import baseConfig from "@repo/config-eslint/next";

export default [...baseConfig];
```

### Tailwind Config (`packages/config-tailwind/`)

**`package.json`**:
```json
{
  "name": "@repo/config-tailwind",
  "private": true,
  "type": "module",
  "exports": {
    ".": "./tailwind.config.ts"
  },
  "devDependencies": {
    "tailwindcss": "^4"
  }
}
```

**For Tailwind v4 (CSS-first)**, shared config is typically a CSS file:

**`base.css`**:
```css
@import "tailwindcss";

@theme {
  --color-brand-50: #eff6ff;
  --color-brand-500: #3b82f6;
  --color-brand-900: #1e3a5f;
  --font-sans: "Inter", sans-serif;
  --radius-lg: 0.75rem;
}
```

**Usage in app:**
```css
/* apps/web/src/app/globals.css */
@import "@repo/config-tailwind/base.css";
```

---

## TypeScript Path Resolution

For internal packages to resolve in editors and at build time:

1. **`exports` field** in the package's `package.json` (primary)
2. **`workspace:*`** dependency in the consuming app's `package.json`
3. **`moduleResolution: "bundler"`** in tsconfig (resolves `exports` field)

No `paths` or `references` needed for workspace packages when using modern `moduleResolution`. The package manager symlinks handle resolution.

### If Using tsconfig Project References (Optional)

```json
{
  "extends": "@repo/config-typescript/base.json",
  "compilerOptions": { "composite": true, "outDir": "dist", "rootDir": "src" },
  "references": [
    { "path": "../../packages/shared" },
    { "path": "../../packages/ui" }
  ]
}
```

Only needed for `tsc --build` mode. Most monorepos don't need this when using a bundler.
