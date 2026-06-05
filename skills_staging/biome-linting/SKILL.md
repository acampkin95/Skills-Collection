---
name: biome-linting
description: Biome v2.4 — ultrafast Rust-based all-in-one linter, formatter, and import sorter, for JavaScript.
---

# Biome v2.4 — Unified Linting & Formatting

Biome is a fast, unified formatter and linter for JavaScript, TypeScript, JSX, TSX, JSON, CSS, and GraphQL with 451 rules and Rust-based compilation (10-100x faster than ESLint+Prettier).

## Quick Reference

```bash
biome check .                    # Lint + format check
biome check --write .            # Lint + format (apply fixes)
biome lint --write .             # Lint only (no format)
biome format --write .           # Format only
biome init                       # Create biome.json
```

## Performance Advantage

| Task | ESLint+Prettier | Biome | Speedup |
|------|---|---|---|
| Lint 25,000 files | 142.6s | 2.1s | 68x |
| Format large repo | 52.3s | 0.9s | 58x |
| Incremental (1 file) | Baseline | 0.05s | 100x |
| vs ESLint v9 (equivalent rules) | Baseline | ~35-45% faster | ~1.5x |
| Deep scan (11,493 files) | N/A | 657ms | — |

## Installation

```bash
npm install -D @biomejs/biome
# or
bun add -d @biomejs/biome
```

## Core Concepts

- **Linter**: 451 rules across correctness, style, suspicious, security, complexity, performance, a11y
- **Formatter**: Opinionated, Prettier-like defaults (97% compatible)
- **Import Organiser**: Auto-sort and group imports
- **Single Config**: `biome.json` replaces `.eslintrc` + `.prettierrc`
- **Zero Dependencies**: Single Rust binary — no npm packages needed
- **Embedded Snippets** (v2.4): Lint/format CSS and GraphQL inside JS template literals
- **GritQL Plugins** (v2.0+): Write custom lint rules using GritQL pattern language
- **HTML A11y**: 15 dedicated accessibility rules for ARIA validation and WCAG compliance

## Rule Categories

| Category | Examples | Purpose |
|----------|----------|---------|
| **Correctness** | noUnusedImports, useExhaustiveDependencies | Prevent bugs |
| **Style** | useConst, noVar, useTemplate | Code style enforcement |
| **Suspicious** | noExplicitAny, noConsole, noArrayIndexKey | Catch mistakes |
| **Performance** | noBarrelFile, noReExportAll | Bundle size optimisation |
| **Accessibility** | noAriaHiddenOnFocusable, useValidAriaValues | WCAG compliance |
| **Nursery** | useSortedClasses, useValidString | Experimental (24 promoted to stable in v2.4) |
| **Security** | noDoubleEquals, noImplicitReturns | Security patterns |

## Configuration (biome.json)

```json
{
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": { "noUnusedVariables": "error" },
      "nursery": { "useSortedClasses": { "level": "error", "fix": "safe" } }
    }
  },
  "formatter": {
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "organizeImports": { "enabled": true }
}
```

## Suppress Violations

```typescript
// biome-ignore lint/suspicious/noExplicitAny: <reason>
function foo(data: any) {}

// biome-ignore-next-line lint/correctness/noUnusedVariables
const x = 1;

/* biome-ignore-file: auto-generated */
```

## VS Code Integration

```bash
code --install-extension biomejs.biome
```

```json
{
  "[javascript]": { "editor.defaultFormatter": "biomejs.biome" },
  "[typescript]": { "editor.defaultFormatter": "biomejs.biome" },
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": { "quickfix.biome": "explicit" }
}
```

## v1 → v2 Migration

```bash
# Automatic migration (handles most breaking changes)
biome migrate --write

# Key changes: include/ignore → files.includes, style rules warn by default
# Verify with: git diff biome.json
```

## Monorepo Support

```json
{
  "extends": ["@biomejs/biome/rules/recommended.json"],
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "files": { "ignore": ["node_modules", "dist", ".next"] }
}
```

## ESLint → Biome Migration

| ESLint | Biome |
|--------|-------|
| no-unused-vars | correctness/noUnusedVariables |
| react-hooks/exhaustive-deps | correctness/useExhaustiveDependencies |
| no-console | suspicious/noConsole |
| prefer-const | style/useConst |
| @typescript-eslint/no-explicit-any | suspicious/noExplicitAny |

See `references/migration-guide.md` for complete mapping and step-by-step process.

## When to Use Biome

✅ New projects | ✅ Replace ESLint+Prettier | ✅ Large codebases (10k+ files)
✅ Zero dependencies needed | ✅ Monorepos | ✅ Fast CI/CD feedback

## Reference Files

- `references/migration-guide.md` — ESLint/Prettier → Biome (step-by-step, complete rule mappings)
- `references/configuration-rules.md` — biome.json patterns, rule groups, domains, custom rules
