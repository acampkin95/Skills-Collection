---
name: biome-linting-cli
description: Biome 2.x — ultrafast Rust-based all-in-one linter, formatter, and import sorter for JavaScript and TypeScript. Use when setting up or running Biome lint and format checks from the CLI, writing or migrating biome.json configuration, replacing ESLint or Prettier with Biome, suppressing violations with biome-ignore comments, or wiring Biome into editors and CI pipelines.
metadata:
  interface: "cli"
version: "1.0.0"
---

# Biome 2 — Unified Linting & Formatting

Biome is a fast, unified formatter and linter for JavaScript, TypeScript, JSX, TSX, JSON, CSS, and GraphQL with Rust-based compilation. Vendor-reported speed claims (10-100x faster than ESLint+Prettier) are not independently verified; measure in your own repository.

**Version note (checked 2026-10-12):** the current stable release on the Biome GitHub releases page is `@biomejs/biome` 2.5.15 (published 30 Sep). The feature notes below were written for the 2.4 line (embedded CSS and GraphQL snippets, 15 HTML accessibility rules); 2.5-specific changes were not reviewed. Run `biome migrate --write` after upgrading and check the release notes for your version.

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

Figures above are unverified benchmark claims; they are not reproduced in this skill.

## Installation

```bash
npm install -D @biomejs/biome
# or
bun add -d @biomejs/biome
```

## Core Concepts

- **Linter**: rule groups include correctness, style, suspicious, security, complexity, performance, and accessibility (the exact rule count is not verified)
- **Formatter**: Opinionated, Prettier-like defaults (the "97% compatible" figure is unverified)
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
  "assist": { "actions": { "source": { "organizeImports": "on" } } }
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

# Key changes: files.include/files.ignore → files.includes, style rules warn by default
# Verify with: git diff biome.json
```

## Monorepo Support

Biome 2 reads the root `biome.json` and exposes the `files.includes` list (negated `!` patterns exclude paths). The `files.ignore` key used by Biome 1 is no longer in the v2 schema.

```json
{
  "extends": ["@biomejs/biome/rules/recommended.json"],
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "files": { "includes": ["**", "!node_modules", "!dist", "!.next"] }
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
