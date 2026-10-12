# ESLint and Prettier to Biome Migration Guide

Complete step-by-step guide for migrating from ESLint, Prettier, or both to Biome.

## Prerequisites

- Node.js 18+
- Current ESLint + Prettier versions documented
- Git working directory clean (commit/stash changes)

## Phase 1: Assessment

### Inventory ESLint Plugins

```bash
cat .eslintrc.json | grep -A 20 "plugins"
```

Document all plugins and extends:

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "plugins": ["react", "react-hooks", "@typescript-eslint"]
}
```

### Inventory Prettier Config

```bash
cat .prettierrc
# or
cat package.json | grep -A 10 "prettier"
```

Record options like indentation, line width, trailing commas.

## Phase 2: Setup Biome

### 1. Install Biome

```bash
npm install -D @biomejs/biome
# or
bun add -d @biomejs/biome
```

### 2. Initialize biome.json

```bash
npx biome init
```

Generates a basic config:

```json
{
  "$schema": "https://biomejs.dev/schemas/1.8.0/schema.json",
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  },
  "organizeImports": { "enabled": true },
  "linter": { "enabled": true, "rules": { "recommended": true } },
  "formatter": { "enabled": true }
}
```

### 3. Configure biome.json to Match Old Style

```json
{
  "formatter": {
    "indentStyle": "space",      // From Prettier
    "indentWidth": 2,
    "lineWidth": 100,
    "trailingCommas": "all",
    "semicolons": "always",
    "arrowParentheses": "always"
  },
  "javascript": {
    "formatter": {
      "jsxQuoteStyle": "double",
      "bracketSpacing": true
    }
  },
  "linter": {
    "rules": {
      "recommended": true,
      // Map ESLint rules below
    }
  }
}
```

## Phase 3: Rule Mapping

### Core Rules (Most Common)

| ESLint Rule | Biome Rule | Severity | Notes |
|-------------|------------|----------|-------|
| `no-unused-vars` | `correctness/noUnusedVariables` | error | Catches unused imports/variables |
| `no-explicit-any` | `suspicious/noExplicitAny` | warn | TypeScript strictness |
| `prefer-const` | `style/useConst` | error | Use const over let |
| `no-var` | `style/noVar` | error | Avoid var keyword |
| `eqeqeq` | `suspicious/noDoubleEquals` | error | Use === not == |
| `curly` | `style/useWhile` | warn | Brace enforcement |
| `no-console` | `suspicious/noConsole` | warn | Disallow console.log |
| `no-delete` | `performance/noDelete` | warn | Avoid delete operator |

### React Rules

| ESLint Plugin Rule | Biome Rule | Config |
|--------------------|------------|--------|
| `react/react-in-jsx-scope` | *Not needed* | Biome handles automatically |
| `react-hooks/exhaustive-deps` | `correctness/useExhaustiveDependencies` | warn |
| `react-hooks/rules-of-hooks` | `correctness/useHookAtTopLevel` | error |
| `react/prop-types` | *Not in Biome* | Use TypeScript instead |
| `react/jsx-no-useless-fragment` | *Not in Biome* | Use suppression comment |

### Accessibility Rules

| ESLint Rule | Biome Rule | Notes |
|-------------|------------|-------|
| `jsx-a11y/click-events-have-key-events` | `a11y/useKeyWithClickEvents` | warn |
| `jsx-a11y/anchor-is-valid` | `a11y/useValidAnchor` | warn |
| `jsx-a11y/role-has-required-aria-props` | `a11y/useAriaProps` | error |
| `jsx-a11y/img-redundant-alt` | `a11y/useAltText` | warn |

### TypeScript Rules

| @typescript-eslint | Biome | Coverage |
|-------------------|-------|----------|
| `no-explicit-any` | `suspicious/noExplicitAny` | Full |
| `no-floating-promises` | *Not in Biome* | Use TSC instead |
| `no-misused-promises` | `correctness/useValidRenderReturn` | Partial |
| `no-unused-vars` | `correctness/noUnusedVariables` | Full |

## Phase 4: Configuration Example

### Basic Setup (Most Projects)

```json
{
  "$schema": "https://biomejs.dev/schemas/1.8.0/schema.json",
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  },
  "files": {
    "ignore": [
      "node_modules",
      "dist",
      "build",
      ".next",
      ".turbo",
      "coverage",
      ".git"
    ]
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100,
    "trailingCommas": "all",
    "semicolons": "always"
  },
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": {
        "noUnusedVariables": "error",
        "noUnusedImports": "error",
        "useExhaustiveDependencies": "warn",
        "useHookAtTopLevel": "error"
      },
      "style": {
        "useConst": "error",
        "noVar": "error",
        "useTemplate": "warn"
      },
      "suspicious": {
        "noExplicitAny": "warn",
        "noConsole": "warn",
        "noArrayIndexKey": "warn",
        "noDoubleEquals": "error"
      },
      "a11y": {
        "useKeyWithClickEvents": "warn",
        "useValidAnchor": "warn"
      }
    }
  },
  "javascript": {
    "formatter": {
      "jsxQuoteStyle": "double",
      "bracketSpacing": true,
      "arrowParentheses": "always"
    }
  }
}
```

### React + TypeScript Project

```json
{
  "extends": ["@biomejs/biome/rules/recommended.json"],
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "formatter": {
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "linter": {
    "rules": {
      "recommended": true,
      "correctness": {
        "useExhaustiveDependencies": "warn",
        "useHookAtTopLevel": "error",
        "noUnusedVariables": "error"
      },
      "suspicious": {
        "noExplicitAny": "warn",
        "noArrayIndexKey": "warn"
      },
      "a11y": {
        "useKeyWithClickEvents": "warn",
        "useValidAnchor": "warn"
      }
    }
  },
  "organizeImports": { "enabled": true }
}
```

## Phase 5: Execution

### 1. Test Biome Against Current Code

```bash
npx biome check . --verbose
```

Review errors. Some will be new (Biome catches more), some will differ from ESLint.

### 2. Apply Fixes

```bash
npx biome check --write .
npx biome format --write .
```

### 3. Review Changes

```bash
git diff --stat
git diff src/  # Spot-check key files
```

### 4. Run Tests

```bash
npm test
# or
npm run typecheck  # TypeScript check (Biome doesn't replace tsc)
```

## Phase 6: Cleanup Old Tools

### Remove ESLint

```bash
npm uninstall eslint \
  @typescript-eslint/parser \
  @typescript-eslint/eslint-plugin \
  eslint-config-airbnb \
  eslint-config-react \
  eslint-plugin-react \
  eslint-plugin-react-hooks \
  eslint-plugin-jsx-a11y

rm .eslintrc* .eslintignore
```

### Remove Prettier

```bash
npm uninstall prettier \
  eslint-config-prettier \
  eslint-plugin-prettier

rm .prettierrc* .prettierignore
```

### Update package.json Scripts

Before:

```json
{
  "scripts": {
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "format": "prettier --write src",
    "check": "npm run lint && npm run format"
  }
}
```

After:

```json
{
  "scripts": {
    "lint": "biome check .",
    "lint:fix": "biome check --write .",
    "format": "biome format --write .",
    "check": "biome check ."
  }
}
```

## Phase 7: CI/CD Updates

### GitHub Actions

Before:

```yaml
- name: Lint
  run: npm run lint

- name: Format
  run: npm run format
```

After:

```yaml
- name: Lint & Format
  run: biome check --error-on-warnings .
```

### Pre-commit Hook (Husky)

```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npx biome check --write .
git add .
```

## Handling Gaps

### Rule Not Available in Biome

Use suppression comments:

```typescript
// biome-ignore lint: ESLint rule not in Biome
const result = someFunctionWithAnyType(data);
```

Document in issue tracker.

### Performance Issues

Enable caching:

```json
{
  "files": {
    "maxSize": 1048576  // 1MB max file size
  }
}
```

### Monorepo Special Cases

For monorepos, use nested `biome.json` files per workspace:

```
project/
├── biome.json          # root config
├── packages/
│   ├── app/
│   │   └── biome.json  # extends root
│   └── lib/
│       └── biome.json  # extends root
```

## Rollback

If issues arise, revert to ESLint+Prettier:

```bash
git reset --hard
npm install  # Reinstalls old dependencies
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Format changes break build | Run full test suite after biome check --write |
| Rules conflict | Adjust biome.json severity (warn vs error) |
| Slow on large repos | Use biome check . --no-ignore (with git filter) |
| Missing rule from ESLint | Use biome-ignore comment, file issue on GitHub |

## Validation

Post-migration checklist:

- [ ] All files pass `biome check .`
- [ ] Tests pass
- [ ] TypeScript compilation succeeds (`tsc --noEmit`)
- [ ] CI/CD pipeline runs successfully
- [ ] Code formatting is consistent
- [ ] No biome-ignore comments except necessary gaps
- [ ] package.json scripts updated
- [ ] Team trained on `biome check` + `biome check --write`

## Further Reading

- Biome docs: https://biomejs.dev/guides/migrate-eslint-prettier/
- Rule reference: https://biomejs.dev/linter/rules/
- Configuration: https://biomejs.dev/reference/configuration/
