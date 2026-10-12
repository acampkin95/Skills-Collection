#!/bin/bash

# Next.js Code Audit - Full Comprehensive Scan
# Usage: ./audit-full.sh [project-path]

set -euo pipefail

PROJECT_PATH="${1:-.}"
cd "$PROJECT_PATH"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
CRITICAL=0
HIGH=0
MEDIUM=0
LOW=0

# Output
REPORT="audit-report-$(date +%Y%m%d-%H%M%S).md"

# Helpers
log() { echo -e "$1"; }
critical() { echo -e "${RED}[CRIT]${NC} $1"; ((CRITICAL++)); echo "- 🔴 CRITICAL: $1" >> "$REPORT"; }
high() { echo -e "${YELLOW}[HIGH]${NC} $1"; ((HIGH++)); echo "- 🟠 HIGH: $1" >> "$REPORT"; }
medium() { echo -e "${BLUE}[MED]${NC} $1"; ((MEDIUM++)); echo "- 🟡 MEDIUM: $1" >> "$REPORT"; }
low() { echo "[LOW] $1"; ((LOW++)); echo "- 🔵 LOW: $1" >> "$REPORT"; }
pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
section() { 
  echo ""
  echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
  echo -e "${CYAN}  $1${NC}"
  echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
  echo "" >> "$REPORT"
  echo "## $1" >> "$REPORT"
  echo "" >> "$REPORT"
}

# Header
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           NEXT.JS CODE AUDIT - FULL SCAN                     ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║  Path: $(pwd)"
echo "║  Date: $(date)"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Initialize report
cat > "$REPORT" << EOF
# Code Audit Report

**Project:** $(basename "$(pwd)")
**Date:** $(date)
**Path:** $(pwd)

---

EOF

# Count total files
TOTAL_FILES=$(find . -type f \( -name "*.ts" -o -name "*.tsx" \) \
  ! -path "*/node_modules/*" ! -path "*/.next/*" 2>/dev/null | wc -l | tr -d ' ')

log "📁 Files to scan: $TOTAL_FILES"
echo "" 

# ============================================
section "1. CONFIGURATION AUDIT"
# ============================================

log "Checking configuration files..."

# package.json
if [ -f "package.json" ]; then
  pass "package.json exists"
  
  NEXT_VER=$(grep '"next"' package.json | grep -oE '[0-9]+' | head -1 || echo "0")
  [ "$NEXT_VER" -lt 15 ] && high "Next.js version < 15 detected"
  
  # npm audit
  if npm audit --json 2>/dev/null | grep -q '"severity":"critical"'; then
    critical "npm audit: Critical vulnerabilities found"
  elif npm audit --json 2>/dev/null | grep -q '"severity":"high"'; then
    high "npm audit: High severity vulnerabilities"
  else
    pass "No critical/high npm vulnerabilities"
  fi
else
  critical "package.json not found"
fi

# tsconfig.json
if [ -f "tsconfig.json" ]; then
  pass "tsconfig.json exists"
  grep -q '"strict".*true' tsconfig.json || medium "TypeScript strict mode not enabled"
  grep -q '"moduleResolution".*"bundler"' tsconfig.json || medium "moduleResolution should be 'bundler'"
  grep -q '"noUncheckedIndexedAccess"' tsconfig.json || low "Consider enabling noUncheckedIndexedAccess"
else
  critical "tsconfig.json not found"
fi

# next.config
if ls next.config.* 2>/dev/null | head -1 > /dev/null; then
  pass "next.config found"
else
  critical "next.config not found"
fi

# postcss.config
if [ -f "postcss.config.mjs" ]; then
  pass "postcss.config.mjs (correct extension)"
elif [ -f "postcss.config.js" ]; then
  high "postcss.config.js should be .mjs for Tailwind v4"
fi

# Linter config
if [ -f "biome.json" ]; then
  pass "Biome configured"
elif ls .eslintrc* eslint.config.* 2>/dev/null | head -1 > /dev/null; then
  pass "ESLint configured"
else
  medium "No linter configuration found"
fi

# ============================================
section "2. CODE QUALITY"
# ============================================

log "Scanning code quality..."

# Dead code patterns
CONSOLE_COUNT=$(grep -rn "console\.\(log\|warn\|error\)" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
[ "$CONSOLE_COUNT" -gt 0 ] && low "Found $CONSOLE_COUNT console statements"

EMPTY_CATCH=$(grep -rn "catch.*{[[:space:]]*}" --include="*.ts" --include="*.tsx" app/ lib/ 2>/dev/null | wc -l | tr -d ' ')
[ "$EMPTY_CATCH" -gt 0 ] && medium "Found $EMPTY_CATCH empty catch blocks"

DEBUGGER=$(grep -rn "debugger" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
[ "$DEBUGGER" -gt 0 ] && high "Found $DEBUGGER debugger statements"

# ============================================
section "3. TYPE SAFETY"
# ============================================

log "Scanning type safety..."

ANY_EXPLICIT=$(grep -rn ": any" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
ANY_ASSERT=$(grep -rn "as any" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
ANY_TOTAL=$((ANY_EXPLICIT + ANY_ASSERT))

if [ "$ANY_TOTAL" -gt 20 ]; then
  high "Excessive 'any' usage: $ANY_TOTAL instances"
elif [ "$ANY_TOTAL" -gt 5 ]; then
  medium "'any' usage: $ANY_TOTAL instances"
elif [ "$ANY_TOTAL" -gt 0 ]; then
  low "'any' usage: $ANY_TOTAL instances"
else
  pass "No explicit 'any' usage"
fi

# Type coverage
if command -v npx &> /dev/null; then
  TYPE_COV=$(npx type-coverage 2>/dev/null | grep -oE '[0-9]+\.[0-9]+%' | head -1 || echo "unknown")
  log "  Type coverage: $TYPE_COV"
  echo "Type coverage: $TYPE_COV" >> "$REPORT"
fi

# ============================================
section "4. PERFORMANCE"
# ============================================

log "Scanning performance..."

# Client components
CLIENT_COMPS=$(grep -rl "'use client'" --include="*.tsx" app/ components/ 2>/dev/null | wc -l | tr -d ' ')
TOTAL_COMPS=$(find app/ components/ -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')

if [ "$TOTAL_COMPS" -gt 0 ]; then
  RATIO=$((CLIENT_COMPS * 100 / TOTAL_COMPS))
  [ "$RATIO" -gt 70 ] && high "High client component ratio: $RATIO%"
  [ "$RATIO" -gt 50 ] && [ "$RATIO" -le 70 ] && medium "Moderate client component ratio: $RATIO%"
fi

# Client pages
CLIENT_PAGES=$(grep -l "'use client'" app/**/page.tsx 2>/dev/null | wc -l | tr -d ' ')
[ "$CLIENT_PAGES" -gt 0 ] && high "$CLIENT_PAGES page.tsx files have 'use client'"

# Large bundles
LODASH=$(grep -rn "import _ from 'lodash'" --include="*.tsx" --include="*.ts" . 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
[ "$LODASH" -gt 0 ] && medium "$LODASH full lodash imports (use specific imports)"

# Images
IMG_TAGS=$(grep -rn "<img " --include="*.tsx" app/ components/ 2>/dev/null | wc -l | tr -d ' ')
[ "$IMG_TAGS" -gt 0 ] && medium "Found $IMG_TAGS <img> tags (use next/image)"

# ============================================
section "5. SECURITY"
# ============================================

log "Scanning security..."

# Hardcoded secrets
PASSWORDS=$(grep -rn "password.*=.*['\"]" --include="*.ts" --include="*.tsx" app/ lib/ 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
[ "$PASSWORDS" -gt 0 ] && critical "Potential hardcoded passwords: $PASSWORDS"

API_KEYS=$(grep -rn "api[_-]?key.*=.*['\"].*['\"]" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".env" | wc -l | tr -d ' ')
[ "$API_KEYS" -gt 0 ] && critical "Potential hardcoded API keys: $API_KEYS"

# dangerouslySetInnerHTML
DANGEROUS=$(grep -rn "dangerouslySetInnerHTML" --include="*.tsx" app/ components/ 2>/dev/null | wc -l | tr -d ' ')
[ "$DANGEROUS" -gt 0 ] && medium "Found $DANGEROUS dangerouslySetInnerHTML usages"

# Server env in client
for f in $(grep -l "'use client'" --include="*.tsx" app/ components/ 2>/dev/null); do
  if grep -q "process.env\." "$f" 2>/dev/null && ! grep -q "NEXT_PUBLIC_" "$f" 2>/dev/null; then
    high "Server env var in client component: $f"
  fi
done

# ============================================
section "6. TECHNICAL DEBT"
# ============================================

log "Scanning technical debt..."

FIXMES=$(grep -rn "FIXME" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
[ "$FIXMES" -gt 0 ] && high "Found $FIXMES FIXME comments"

TODOS=$(grep -rn "TODO" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
[ "$TODOS" -gt 20 ] && medium "Found $TODOS TODO comments"
[ "$TODOS" -gt 0 ] && [ "$TODOS" -le 20 ] && low "Found $TODOS TODO comments"

HACKS=$(grep -rn "HACK\|XXX" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
[ "$HACKS" -gt 0 ] && medium "Found $HACKS HACK/XXX comments"

# ============================================
section "7. ARCHITECTURE"
# ============================================

log "Scanning architecture..."

# Layer violations
LIB_COMPS=$(grep -rn "from '@/components/" --include="*.ts" lib/ 2>/dev/null | wc -l | tr -d ' ')
[ "$LIB_COMPS" -gt 0 ] && high "Layer violation: lib/ imports from components/ ($LIB_COMPS)"

# Wrong router
WRONG_ROUTER=$(grep -rn "from 'next/router'" --include="*.tsx" app/ components/ 2>/dev/null | wc -l | tr -d ' ')
[ "$WRONG_ROUTER" -gt 0 ] && high "$WRONG_ROUTER files use 'next/router' (use 'next/navigation')"

# Circular dependencies
if command -v npx &> /dev/null; then
  CIRCULAR=$(npx madge --circular --extensions ts,tsx app/ lib/ 2>/dev/null | grep -c "Circular" || echo "0")
  [ "$CIRCULAR" -gt 0 ] && high "Circular dependencies detected"
fi

# Large files
for f in $(find app/ lib/ components/ -name "*.tsx" -o -name "*.ts" 2>/dev/null); do
  lines=$(wc -l < "$f" 2>/dev/null || echo "0")
  [ "$lines" -gt 300 ] && medium "Large file ($lines lines): $f"
done 2>/dev/null

# ============================================
section "8. NEXT.JS 16 COMPLIANCE"
# ============================================

log "Checking Next.js 16 patterns..."

# Async params
SYNC_PARAMS=$(grep -rn "params\." --include="*.tsx" app/ 2>/dev/null | grep -v "await params\|Promise<" | wc -l | tr -d ' ')
[ "$SYNC_PARAMS" -gt 0 ] && high "Synchronous params access: $SYNC_PARAMS (require await in Next.js 15+)"

# error.tsx
if [ -f "app/error.tsx" ]; then
  head -1 app/error.tsx | grep -q "'use client'" || critical "error.tsx missing 'use client'"
fi

# global-error.tsx
if [ -f "app/global-error.tsx" ]; then
  head -1 app/global-error.tsx | grep -q "'use client'" || critical "global-error.tsx missing 'use client'"
fi

# Tailwind v4
if [ -f "app/globals.css" ]; then
  if grep -q "@tailwind base" app/globals.css; then
    medium "Using Tailwind v3 syntax (upgrade to v4: @import 'tailwindcss')"
  fi
fi

# ============================================
section "9. SUMMARY"
# ============================================

# Calculate score
TOTAL_ISSUES=$((CRITICAL + HIGH + MEDIUM + LOW))
if [ "$CRITICAL" -gt 0 ]; then
  SCORE=$((10 - CRITICAL * 2 - HIGH))
elif [ "$HIGH" -gt 5 ]; then
  SCORE=$((8 - HIGH / 2))
else
  SCORE=$((10 - HIGH - MEDIUM / 3 - LOW / 5))
fi
[ "$SCORE" -lt 0 ] && SCORE=0
[ "$SCORE" -gt 10 ] && SCORE=10

# Summary
cat >> "$REPORT" << EOF

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | $CRITICAL |
| 🟠 High | $HIGH |
| 🟡 Medium | $MEDIUM |
| 🔵 Low | $LOW |
| **Total** | $TOTAL_ISSUES |

**Health Score:** $SCORE/10
**Files Scanned:** $TOTAL_FILES

---

*Generated by Next.js Code Audit Skill*
EOF

# Print summary
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    AUDIT SUMMARY                              ║${NC}"
echo -e "${CYAN}╠═══════════════════════════════════════════════════════════════╣${NC}"
echo -e "║  ${RED}🔴 Critical:${NC}  $CRITICAL"
echo -e "║  ${YELLOW}🟠 High:${NC}      $HIGH"
echo -e "║  ${BLUE}🟡 Medium:${NC}    $MEDIUM"
echo -e "║  🔵 Low:       $LOW"
echo -e "${CYAN}╠═══════════════════════════════════════════════════════════════╣${NC}"
echo -e "║  📊 Health Score: ${GREEN}$SCORE/10${NC}"
echo -e "║  📁 Files Scanned: $TOTAL_FILES"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$CRITICAL" -gt 0 ]; then
  echo -e "  ${RED}⛔ CRITICAL ISSUES - Fix before deploying${NC}"
elif [ "$HIGH" -gt 5 ]; then
  echo -e "  ${YELLOW}⚠️  Multiple high priority issues${NC}"
else
  echo -e "  ${GREEN}✅ Project is in reasonable health${NC}"
fi

echo ""
echo "  📄 Report saved to: $REPORT"
echo ""

exit $CRITICAL
