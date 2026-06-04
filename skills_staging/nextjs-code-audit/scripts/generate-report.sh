#!/bin/bash

# Next.js Code Audit - Generate Report
# Comprehensive report generation
# Usage: ./generate-report.sh [project-path]

set -euo pipefail

PROJECT_PATH="${1:-.}"
cd "$PROJECT_PATH"

REPORT="audit-report-$(date +%Y%m%d-%H%M%S).md"
PROJECT_NAME=$(basename "$(pwd)")

# ─────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────

cat > "$REPORT" << EOF
# Code Audit Report

**Project:** $PROJECT_NAME
**Date:** $(date '+%Y-%m-%d %H:%M')
**Path:** $(pwd)

---

## Executive Summary

EOF

# ─────────────────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────────────────

# File counts
TS_COUNT=$(find . -name "*.ts" ! -path "*/node_modules/*" ! -path "*/.next/*" 2>/dev/null | wc -l | tr -d ' ')
TSX_COUNT=$(find . -name "*.tsx" ! -path "*/node_modules/*" ! -path "*/.next/*" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_FILES=$((TS_COUNT + TSX_COUNT))

# Issue counts
CONSOLE_COUNT=$(grep -rn "console\." --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
ANY_COUNT=$(grep -rn ": any\|as any" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
TODO_COUNT=$(grep -rn "TODO\|FIXME" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
CLIENT_COUNT=$(grep -rl "'use client'" --include="*.tsx" app/ components/ 2>/dev/null | wc -l | tr -d ' ')

# Type coverage
TYPE_COV=$(npx type-coverage 2>/dev/null | grep -oE '[0-9]+\.[0-9]+%' | head -1 || echo "N/A")

# Calculate scores
QUALITY_SCORE=10
[ "$CONSOLE_COUNT" -gt 10 ] && QUALITY_SCORE=$((QUALITY_SCORE - 1))
[ "$ANY_COUNT" -gt 10 ] && QUALITY_SCORE=$((QUALITY_SCORE - 2))
[ "$TODO_COUNT" -gt 20 ] && QUALITY_SCORE=$((QUALITY_SCORE - 1))
[ "$QUALITY_SCORE" -lt 0 ] && QUALITY_SCORE=0

cat >> "$REPORT" << EOF

### Metrics Overview

| Metric | Value |
|--------|-------|
| Total Files | $TOTAL_FILES |
| TypeScript Files | $TS_COUNT |
| React Components | $TSX_COUNT |
| Client Components | $CLIENT_COUNT |
| Type Coverage | $TYPE_COV |

### Issue Summary

| Category | Count |
|----------|-------|
| Console Statements | $CONSOLE_COUNT |
| 'any' Usage | $ANY_COUNT |
| TODO/FIXME | $TODO_COUNT |

---

## Detailed Findings

### 1. Code Quality

EOF

# Quality findings
if [ "$CONSOLE_COUNT" -gt 0 ]; then
  echo "#### Console Statements: $CONSOLE_COUNT" >> "$REPORT"
  echo "" >> "$REPORT"
  echo '```' >> "$REPORT"
  grep -rn "console\." --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | head -10 >> "$REPORT"
  echo '```' >> "$REPORT"
  echo "" >> "$REPORT"
fi

if [ "$ANY_COUNT" -gt 0 ]; then
  echo "#### 'any' Usage: $ANY_COUNT" >> "$REPORT"
  echo "" >> "$REPORT"
  echo '```' >> "$REPORT"
  grep -rn ": any\|as any" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | head -10 >> "$REPORT"
  echo '```' >> "$REPORT"
  echo "" >> "$REPORT"
fi

cat >> "$REPORT" << EOF

### 2. Security

EOF

# Security findings
SECRET_COUNT=$(grep -rn "password.*=.*['\"]" --include="*.ts" --include="*.tsx" app/ lib/ 2>/dev/null | grep -v "example\|placeholder" | wc -l | tr -d ' ')
if [ "$SECRET_COUNT" -gt 0 ]; then
  echo "⚠️ **Potential hardcoded secrets found: $SECRET_COUNT**" >> "$REPORT"
  echo "" >> "$REPORT"
fi

DANGEROUS_COUNT=$(grep -rn "dangerouslySetInnerHTML" --include="*.tsx" app/ components/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$DANGEROUS_COUNT" -gt 0 ]; then
  echo "⚠️ **dangerouslySetInnerHTML usage: $DANGEROUS_COUNT**" >> "$REPORT"
  echo "" >> "$REPORT"
fi

# npm audit
npm audit --json 2>/dev/null | grep -c '"severity":"critical"' > /dev/null && echo "🔴 Critical npm vulnerabilities detected" >> "$REPORT"
npm audit --json 2>/dev/null | grep -c '"severity":"high"' > /dev/null && echo "🟠 High npm vulnerabilities detected" >> "$REPORT"

cat >> "$REPORT" << EOF

### 3. Architecture

EOF

# Architecture findings
CIRCULAR=$(npx madge --circular --extensions ts,tsx app/ lib/ components/ 2>/dev/null | grep -c "→" || echo "0")
if [ "$CIRCULAR" -gt 0 ]; then
  echo "⚠️ **Circular dependencies: $CIRCULAR**" >> "$REPORT"
  echo "" >> "$REPORT"
fi

# Layer violations
LIB_COMPS=$(grep -rn "from '@/components" --include="*.ts" lib/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$LIB_COMPS" -gt 0 ]; then
  echo "⚠️ **Layer violations (lib→components): $LIB_COMPS**" >> "$REPORT"
  echo "" >> "$REPORT"
fi

cat >> "$REPORT" << EOF

---

## Recommendations

### Short-Term (Sprint 1-2)

1. Remove console statements ($CONSOLE_COUNT)
2. Fix 'any' usage ($ANY_COUNT)
3. Run \`npm audit fix\`

### Long-Term (Quarter)

1. Increase type coverage to 90%+
2. Add comprehensive test coverage
3. Implement security headers
4. Add rate limiting to public APIs

---

## Configuration Status

| File | Status |
|------|--------|
EOF

[ -f "package.json" ] && echo "| package.json | ✅ |" >> "$REPORT" || echo "| package.json | ❌ |" >> "$REPORT"
[ -f "tsconfig.json" ] && echo "| tsconfig.json | ✅ |" >> "$REPORT" || echo "| tsconfig.json | ❌ |" >> "$REPORT"
ls next.config.* 2>/dev/null | head -1 > /dev/null && echo "| next.config | ✅ |" >> "$REPORT" || echo "| next.config | ❌ |" >> "$REPORT"
[ -f "biome.json" ] && echo "| biome.json | ✅ |" >> "$REPORT" || echo "| Linter config | ❌ |" >> "$REPORT"
[ -f ".env.example" ] && echo "| .env.example | ✅ |" >> "$REPORT" || echo "| .env.example | ❌ |" >> "$REPORT"
[ -f "middleware.ts" ] && echo "| middleware.ts | ✅ |" >> "$REPORT" || echo "| middleware.ts | ⚠️ |" >> "$REPORT"

cat >> "$REPORT" << EOF

---

*Generated by Next.js Code Audit Skill*
*$(date)*
EOF

echo "Report generated: $REPORT"
