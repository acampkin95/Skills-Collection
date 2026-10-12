#!/bin/bash
# Next.js Project Audit Script v2.0
# Run from project root: ./scripts/audit-nextjs.sh

set -euo pipefail

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Next.js Project Audit v2.0                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"

PASS="✅"
FAIL="❌"
WARN="⚠️"
INFO="ℹ️"
ISSUES=0
WARNINGS=0

section() { echo -e "\n━━━ $1 ━━━"; }
pass() { echo "$PASS $1"; }
fail() { echo "$FAIL $1"; ((ISSUES++)); }
warn() { echo "$WARN $1"; ((WARNINGS++)); }
info() { echo "$INFO $1"; }

# Determine app directory
APP_DIR="app"
[ -d "src/app" ] && APP_DIR="src/app"

# ━━━ 1. Configuration Files ━━━
section "1. Configuration Files"

# next.config
if [ -f "next.config.ts" ] || [ -f "next.config.mjs" ] || [ -f "next.config.js" ]; then
  pass "next.config exists"
  
  # Check for deprecated options
  if grep -q "experimental.serverComponentsExternalPackages" next.config.* 2>/dev/null; then
    warn "Deprecated: Use 'serverExternalPackages' instead of 'experimental.serverComponentsExternalPackages'"
  fi
  
  if grep -q "experimental.turbo" next.config.* 2>/dev/null; then
    warn "Deprecated: Use 'turbopack' instead of 'experimental.turbo'"
  fi
else
  fail "next.config not found"
fi

# tsconfig.json
if [ -f "tsconfig.json" ]; then
  pass "tsconfig.json exists"
  
  if grep -q '"moduleResolution".*"bundler"' tsconfig.json; then
    pass "moduleResolution is 'bundler'"
  else
    fail "moduleResolution should be 'bundler' (not 'node')"
  fi
  
  if grep -q '.next/types' tsconfig.json; then
    pass "tsconfig includes .next/types"
  else
    warn "tsconfig should include '.next/types/**/*.ts'"
  fi
  
  if grep -q '"isolatedModules".*true' tsconfig.json; then
    pass "isolatedModules is true"
  else
    warn "isolatedModules should be true"
  fi
else
  fail "tsconfig.json not found"
fi

# postcss.config
if [ -f "postcss.config.mjs" ]; then
  pass "postcss.config.mjs exists (correct extension)"
  
  if grep -q "@tailwindcss/postcss" postcss.config.mjs; then
    pass "Uses @tailwindcss/postcss plugin"
  else
    fail "postcss.config should use @tailwindcss/postcss"
  fi
elif [ -f "postcss.config.js" ]; then
  fail "postcss.config.js found - MUST be .mjs for Tailwind v4"
else
  fail "postcss.config.mjs not found"
fi

# ━━━ 2. App Directory Structure ━━━
section "2. App Directory Structure"

# layout.tsx
if [ -f "$APP_DIR/layout.tsx" ]; then
  pass "layout.tsx exists"
  
  if grep -q "globals.css" "$APP_DIR/layout.tsx"; then
    pass "layout.tsx imports globals.css"
  else
    fail "layout.tsx should import globals.css"
  fi
  
  if grep -q "'use client'" "$APP_DIR/layout.tsx"; then
    warn "layout.tsx has 'use client' - usually should be Server Component"
  fi
else
  fail "layout.tsx not found"
fi

# error.tsx
if [ -f "$APP_DIR/error.tsx" ]; then
  if head -1 "$APP_DIR/error.tsx" | grep -q "use client"; then
    pass "error.tsx has 'use client'"
  else
    fail "error.tsx MUST have 'use client' as first line"
  fi
else
  warn "error.tsx not found (recommended)"
fi

# global-error.tsx
if [ -f "$APP_DIR/global-error.tsx" ]; then
  if head -1 "$APP_DIR/global-error.tsx" | grep -q "use client"; then
    pass "global-error.tsx has 'use client'"
  else
    fail "global-error.tsx MUST have 'use client' as first line"
  fi
else
  warn "global-error.tsx not found (recommended)"
fi

# not-found.tsx
if [ -f "$APP_DIR/not-found.tsx" ]; then
  pass "not-found.tsx exists"
else
  warn "not-found.tsx not found (recommended)"
fi

# loading.tsx
if [ -f "$APP_DIR/loading.tsx" ]; then
  pass "loading.tsx exists"
else
  info "loading.tsx not found (optional)"
fi

# ━━━ 3. CSS & Tailwind ━━━
section "3. CSS & Tailwind"

CSS_FILE=""
[ -f "$APP_DIR/globals.css" ] && CSS_FILE="$APP_DIR/globals.css"

if [ -n "$CSS_FILE" ]; then
  pass "globals.css exists"
  
  if grep -q '@import.*tailwindcss' "$CSS_FILE"; then
    pass "Uses Tailwind v4 syntax (@import)"
  else
    fail "Should use @import 'tailwindcss' (Tailwind v4)"
  fi
  
  if grep -q '@tailwind' "$CSS_FILE"; then
    fail "Old @tailwind syntax found - update to @import 'tailwindcss'"
  fi
else
  fail "globals.css not found"
fi

# ━━━ 4. Dependencies ━━━
section "4. Dependencies"

# Check core packages
if npm ls next 2>/dev/null | grep -q "next@"; then
  NEXT_VER=$(npm ls next --json 2>/dev/null | grep -o '"version": "[^"]*"' | head -1 | grep -o '[0-9][0-9.]*' || echo "unknown")
  pass "Next.js installed (v$NEXT_VER)"
else
  fail "Next.js not installed"
fi

if npm ls tailwindcss 2>/dev/null | grep -q "tailwindcss@"; then
  TAIL_VER=$(npm ls tailwindcss --json 2>/dev/null | grep -o '"version": "[^"]*"' | head -1 | grep -o '[0-9][0-9.]*' || echo "unknown")
  pass "Tailwind CSS installed (v$TAIL_VER)"
else
  fail "Tailwind CSS not installed"
fi

if npm ls @tailwindcss/postcss 2>/dev/null | grep -q "@tailwindcss/postcss@"; then
  pass "@tailwindcss/postcss installed"
else
  fail "@tailwindcss/postcss not installed (required for Tailwind v4)"
fi

# Check for legacy packages
if npm ls autoprefixer 2>/dev/null | grep -q "autoprefixer@"; then
  warn "autoprefixer found - not needed with Tailwind v4"
fi

if npm ls postcss-import 2>/dev/null | grep -q "postcss-import@"; then
  warn "postcss-import found - not needed with Tailwind v4"
fi

# ━━━ 5. Code Quality ━━━
section "5. Code Quality Checks"

# Client components in pages
PAGE_CLIENT=$(grep -rl "'use client'" --include="page.tsx" "$APP_DIR" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PAGE_CLIENT" -eq 0 ]; then
  pass "No 'use client' in page.tsx files"
else
  warn "'use client' found in $PAGE_CLIENT page.tsx file(s) - usually wrong"
fi

# Wrong router import
WRONG_ROUTER=$(grep -rn "from 'next/router'" --include="*.tsx" --include="*.ts" . 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
if [ "$WRONG_ROUTER" -eq 0 ]; then
  pass "No imports from next/router"
else
  fail "$WRONG_ROUTER import(s) from next/router - use next/navigation"
fi

# Dynamic class names
DYN_CLASS=$(grep -rn 'className.*`.*\${' --include="*.tsx" . 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
if [ "$DYN_CLASS" -eq 0 ]; then
  pass "No dynamic Tailwind classes"
else
  warn "$DYN_CLASS dynamic class(es) found - may be purged"
fi

# Browser APIs
BROWSER_API=$(grep -rn "window\.\|document\." --include="*.tsx" "$APP_DIR" components 2>/dev/null | grep -v "typeof" | wc -l | tr -d ' ')
if [ "$BROWSER_API" -eq 0 ]; then
  pass "No unguarded browser API usage"
else
  warn "$BROWSER_API potential browser API issue(s) - ensure in useEffect"
fi

# Component stats
TOTAL_COMP=$(find "$APP_DIR" components src -name "*.tsx" 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
CLIENT_COMP=$(grep -rl "'use client'" --include="*.tsx" "$APP_DIR" components src 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
SERVER_COMP=$((TOTAL_COMP - CLIENT_COMP))
info "Components: $TOTAL_COMP total, $CLIENT_COMP client, $SERVER_COMP server"

# ━━━ 6. Async APIs (Next.js 15+) ━━━
section "6. Async API Patterns"

# Check for sync params access
SYNC_PARAMS=$(grep -rn "params\." --include="*.tsx" "$APP_DIR" 2>/dev/null | grep -v "await params\|use(params\|Promise" | wc -l | tr -d ' ')
if [ "$SYNC_PARAMS" -eq 0 ]; then
  pass "params accessed correctly"
else
  warn "$SYNC_PARAMS potential sync params access - should use await"
fi

# Check cookies/headers
SYNC_COOKIES=$(grep -rn "cookies()\|headers()" --include="*.tsx" --include="*.ts" . 2>/dev/null | grep -v "await\|node_modules" | wc -l | tr -d ' ')
if [ "$SYNC_COOKIES" -eq 0 ]; then
  pass "cookies()/headers() accessed correctly"
else
  warn "$SYNC_COOKIES potential sync cookies/headers - should use await"
fi

# ━━━ 7. Build Verification ━━━
section "7. Build Verification"

info "Running type check..."
if npx tsc --noEmit 2>&1 | grep -qi "error"; then
  fail "TypeScript errors found"
else
  pass "TypeScript check passed"
fi

info "Running lint..."
if npm run lint 2>&1 | grep -qi "error"; then
  warn "Lint errors found"
else
  pass "Lint check passed"
fi

# ━━━ Summary ━━━
section "Audit Summary"

echo ""
if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo "🎉 All checks passed!"
elif [ $ISSUES -eq 0 ]; then
  echo "✅ No critical issues, $WARNINGS warning(s)"
else
  echo "❌ $ISSUES issue(s), $WARNINGS warning(s)"
fi

echo ""
echo "━━━ Next Steps ━━━"
[ $ISSUES -gt 0 ] && echo "• Fix critical issues ($FAIL items)"
[ $WARNINGS -gt 0 ] && echo "• Review warnings ($WARN items)"
echo "• Run 'npm run build' for full build test"
echo "• See references/troubleshooting.md for fixes"
echo ""
