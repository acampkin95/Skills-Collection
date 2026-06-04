---
name: nextjs-code-audit
description: Next.js codebase audit for security, performance, bundle analysis, dead code, type coverage, and code quality.
version: 2.0.0
reviewed: "2026-06-04"
---

# Next.js Code Audit Skill

Systematic eight-category audit methodology for Next.js 16 and TypeScript React applications.

## 2025 Critical Security Vulnerabilities

### CVE-2025 Next.js RCE Vulnerabilities

| CVE | Severity | Affected | Fix |
|-----|----------|----------|-----|
| CVE-2025-55182 | Critical | Next.js < 16.0.10 | Upgrade to 16.0.10+ |
| CVE-2025-66478 | Critical | Next.js < 16.0.10 | Upgrade to 16.0.10+ |
| CVE-2025-67779 | High | Next.js < 16.0.10 | Upgrade to 16.0.10+ |

**Action Required:** If auditing Next.js App Router projects, verify version is 16.0.10+ to patch RSC vulnerabilities.

## Audit Categories (Eight Minds)

| # | Category | Focus | Reference |
|---|----------|-------|-----------|
| 1 | **Quality** | Dead code, unused imports, formatting, naming | `references/01-quality.md` |
| 2 | **Types** | Type coverage, `any` usage, generics, inference | `references/02-types.md` |
| 3 | **Performance** | Bundle size, re-renders, lazy loading, caching | `references/03-performance.md` |
| 4 | **Security** | Secrets, validation, dependencies, auth | `references/04-security.md` |
| 5 | **Debt** | TODOs, error handling, patterns, duplication | `references/05-debt.md` |
| 6 | **Architecture** | Structure, boundaries, modules, conventions | `references/06-architecture.md` |
| 7 | **Testing** | Coverage, patterns, mocking, e2e | `references/07-testing.md` |
| 8 | **Accessibility** | ARIA, semantics, keyboard, screen readers | `references/08-accessibility.md` |

## Audit Execution Workflow

### Phase 1: Discovery (5 min)

```bash
./scripts/discover.sh [project-path]
```

Outputs: File inventory, dependency versions, structure overview, quick issue count.

### Phase 2: Configuration Audit (10 min)

Validate all config files against best practices:

```bash
./scripts/audit-config.sh [project-path]
```

Checks: `package.json`, `tsconfig.json`, `next.config.*`, `postcss.config.*`, ESLint/Biome, environment files.

See `references/09-config-templates.md` for recommended configurations.

### Phase 3: File-by-File Scan (varies)

Execute comprehensive scan with progress tracking:

```bash
./scripts/audit-full.sh [project-path]
```

Scans files in priority order:
1. Config files → 2. Layouts → 3. Pages → 4. Components → 5. Lib/Utils → 6. Styles → 7. Tests

Each file analyzed for all 8 categories. Progress displayed as `[42/156] Scanning app/page.tsx...`

### Phase 4: Cross-File Analysis (10 min)

```bash
./scripts/audit-linked.sh [project-path]
```

Checks: Circular dependencies, unused exports, import resolution, layer violations, barrel file issues.

### Phase 5: Specialized Scans

Run targeted audits as needed:

```bash
./scripts/audit-quick.sh .      # Fast quality scan only
./scripts/audit-security.sh .   # Deep security analysis
./scripts/audit-perf.sh .       # Performance deep-dive
./scripts/audit-a11y.sh .       # Accessibility audit
```

### Phase 6: Auto-Fix (optional)

Apply safe automatic fixes:

```bash
./scripts/fix-safe.sh .         # Non-breaking fixes only
./scripts/fix-all.sh .          # All auto-fixable issues
```

### Phase 7: Report Generation

Generate comprehensive report:

```bash
./scripts/generate-report.sh [project-path] > audit-report.md
```

See `references/10-report-template.md` for output format.

## Completion Requirements

An audit is complete when:

- [ ] ALL source files scanned (100% coverage)
- [ ] All 8 categories evaluated
- [ ] Config files validated
- [ ] Cross-file integrity verified
- [ ] Findings documented with `file:line` references
- [ ] Issues prioritized (Critical/High/Medium/Low)
- [ ] Health score calculated
- [ ] Short-term roadmap (1-2 sprints) produced
- [ ] Long-term roadmap (quarter) produced
- [ ] Critical actions checklist generated

## Quick Reference Commands

```bash
# Full audit
./scripts/audit-full.sh .

# Quick scans
npx tsc --noEmit                    # Type check
npx eslint . --ext .ts,.tsx         # Lint check
npx @biomejs/biome check .          # Biome check
npm audit                           # Security check
npx type-coverage --detail          # Type coverage

# Metrics
npx madge --circular .              # Circular deps
npx ts-prune                        # Dead exports
npx depcheck                        # Unused deps
npx bundlesize                      # Bundle analysis

# Auto-fix
npx eslint . --fix --ext .ts,.tsx
npx @biomejs/biome check --apply .
npm audit fix
```

## Output Deliverables

1. **Audit Report** (`audit-report.md`) - Complete findings
2. **Metrics Summary** - Health scores, file counts, issue breakdown
3. **Critical Actions** - Immediate fix checklist
4. **Short-Term Roadmap** - Sprint-level improvements
5. **Long-Term Roadmap** - Quarter-level goals
6. **CI Config** (optional) - GitHub Actions workflow

## Next.js 16 Specific Checks

Critical patterns for Next.js 16 App Router:

- Async Request APIs (`params`, `searchParams`, `cookies()`, `headers()`)
- Server/Client Component boundaries
- `'use client'` placement (first line, before imports)
- `error.tsx` and `global-error.tsx` must have `'use client'`
- Fetch caching changes (default: no cache)
- Turbopack compatibility
- React 19 patterns

See `references/11-nextjs16-patterns.md` for complete checklist.
