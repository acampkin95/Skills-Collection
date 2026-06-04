# 10. Audit Report Template

---

## Report Structure

```markdown
# Code Audit Report

**Project:** [Name]
**Date:** [YYYY-MM-DD]
**Auditor:** Claude
**Commit:** [hash]

---

## Executive Summary

[2-3 sentences on overall health]

### Health Score: X/10

| Category | Score | Status |
|----------|-------|--------|
| Code Quality | X/10 | 🟢/🟡/🔴 |
| Type Safety | X/10 | 🟢/🟡/🔴 |
| Performance | X/10 | 🟢/🟡/🔴 |
| Security | X/10 | 🟢/🟡/🔴 |
| Technical Debt | X/10 | 🟢/🟡/🔴 |
| Architecture | X/10 | 🟢/🟡/🔴 |
| Testing | X/10 | 🟢/🟡/🔴 |
| Accessibility | X/10 | 🟢/🟡/🔴 |

### Key Metrics

| Metric | Value | Target |
|--------|-------|--------|
| Files Scanned | X | 100% |
| Type Coverage | X% | 85% |
| Test Coverage | X% | 80% |
| Bundle Size | Xkb | <100kb |
| Dependencies | X | - |
| Vulnerabilities | X | 0 |

---

## Issues Summary

| Severity | Count | Examples |
|----------|-------|----------|
| 🔴 Critical | X | [Brief list] |
| 🟠 High | X | [Brief list] |
| 🟡 Medium | X | [Brief list] |
| 🔵 Low | X | [Brief list] |

---

## Critical Issues

### CRIT-001: [Title]

- **Category:** Security/Performance/etc.
- **Location:** `path/to/file.tsx:42`
- **Description:** [What's wrong]
- **Impact:** [Why it matters]
- **Fix:**
  ```typescript
  // Before
  [problematic code]
  
  // After
  [fixed code]
  ```
- **Effort:** 30 minutes

---

## High Priority Issues

### HIGH-001: [Title]

- **Category:** [Category]
- **Location:** `path/to/file.tsx:42`
- **Description:** [Description]
- **Fix:** [How to fix]
- **Effort:** [Time estimate]

---

## Medium Priority Issues

### MED-001: [Title]

[Same structure as above, abbreviated]

---

## Low Priority Issues

### LOW-001: [Title]

[Brief description, can be bullet points]

---

## Findings by Category

### 1. Code Quality

**Score: X/10**

| Check | Status | Details |
|-------|--------|---------|
| Dead code | ✅/❌ | X instances |
| Unused imports | ✅/❌ | X instances |
| Console logs | ✅/❌ | X instances |
| Naming conventions | ✅/❌ | X violations |

### 2. Type Safety

**Score: X/10**

| Check | Status | Details |
|-------|--------|---------|
| Type coverage | X% | Target: 85% |
| `any` usage | X | Target: 0 |
| Missing types | X | [Locations] |
| Strict mode | ✅/❌ | [Details] |

### 3. Performance

**Score: X/10**

| Check | Status | Details |
|-------|--------|---------|
| Bundle size | Xkb | Target: <100kb |
| Client components | X/Y | Ratio |
| Lazy loading | ✅/❌ | [Details] |
| Image optimization | ✅/❌ | [Details] |

### 4. Security

**Score: X/10**

| Check | Status | Details |
|-------|--------|---------|
| Exposed secrets | ✅/❌ | X found |
| npm audit | ✅/❌ | X critical, X high |
| Input validation | ✅/❌ | X routes checked |
| Auth middleware | ✅/❌ | [Details] |

### 5. Technical Debt

**Score: X/10**

| Check | Status | Details |
|-------|--------|---------|
| TODOs | X | X with tickets |
| FIXMEs | X | [Locations] |
| Error handling | ✅/❌ | X empty catch |
| Duplication | ✅/❌ | X instances |

### 6. Architecture

**Score: X/10**

| Check | Status | Details |
|-------|--------|---------|
| Structure | ✅/❌ | [Assessment] |
| Circular deps | ✅/❌ | X found |
| Layer violations | ✅/❌ | X found |
| File organization | ✅/❌ | [Assessment] |

### 7. Testing

**Score: X/10**

| Check | Status | Details |
|-------|--------|---------|
| Test coverage | X% | Target: 80% |
| Test quality | ✅/❌ | [Assessment] |
| Missing tests | X | [Priority areas] |
| E2E tests | ✅/❌ | [Coverage] |

### 8. Accessibility

**Score: X/10**

| Check | Status | Details |
|-------|--------|---------|
| Axe violations | X | [Types] |
| Semantic HTML | ✅/❌ | [Assessment] |
| Keyboard nav | ✅/❌ | [Assessment] |
| Form labels | ✅/❌ | X missing |

---

## Configuration Status

| File | Status | Notes |
|------|--------|-------|
| package.json | ✅/❌ | [Notes] |
| tsconfig.json | ✅/❌ | [Notes] |
| next.config.ts | ✅/❌ | [Notes] |
| postcss.config.mjs | ✅/❌ | [Notes] |
| biome.json | ✅/❌ | [Notes] |
| .env.example | ✅/❌ | [Notes] |

---

## Roadmap

### Short-Term (Sprint 1-2)

| Priority | Task | Category | Effort | Owner |
|----------|------|----------|--------|-------|
| 1 | [CRIT-001] | Security | 1h | - |
| 2 | [CRIT-002] | Performance | 2h | - |
| 3 | [HIGH-001] | Types | 3h | - |

**Sprint Goals:**
- [ ] Resolve all critical issues
- [ ] Fix high-priority security issues
- [ ] Increase type coverage to X%

### Long-Term (Quarter)

| Month | Focus | Deliverables |
|-------|-------|--------------|
| Month 1 | Foundation | Security fixes, critical bugs |
| Month 2 | Quality | Type safety 90%, test coverage 80% |
| Month 3 | Architecture | Refactoring, patterns |

**Quarterly Targets:**
- Type coverage: X% → 90%
- Test coverage: X% → 80%
- Bundle size: Xkb → <100kb
- Health score: X → 8+

---

## Critical Actions Checklist

### Today
- [ ] CRIT-001: [Action]
- [ ] CRIT-002: [Action]

### This Week
- [ ] HIGH-001: [Action]
- [ ] HIGH-002: [Action]

### This Sprint
- [ ] MED-001: [Action]
- [ ] Setup CI checks

---

## Appendix

### A. Tools Used
- TypeScript X.X
- ESLint/Biome X.X
- type-coverage
- npm audit
- madge
- Axe

### B. Files Scanned
[List or count]

### C. Excluded Files
- node_modules/
- .next/
- coverage/

---

*Generated by Next.js Code Audit Skill*
```
