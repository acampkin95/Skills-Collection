#!/bin/bash
#
# Frontend Project Audit Script
# Diagnoses common issues in Next.js, Vite, and Tailwind projects
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_PATH="${1:-.}"
ISSUES=0
WARNINGS=0

echo ""
echo "=========================================="
echo "  Frontend Project Audit"
echo "=========================================="
echo "Project: $PROJECT_PATH"
echo ""

pass() { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; ((ISSUES++)); }
warn() { echo -e "${YELLOW}!${NC} $1"; ((WARNINGS++)); }
info() { echo -e "${BLUE}ℹ${NC} $1"; }

cd "$PROJECT_PATH"

###################
# Package.json
###################
echo "--- Package.json ---"

if [ -f "package.json" ]; then
    pass "package.json exists"
    
    grep -q '"next"' package.json && info "Next.js detected"
    grep -q '"vite"' package.json && info "Vite detected"
    grep -q '"tailwindcss"' package.json && info "Tailwind CSS detected"
else
    fail "package.json not found"
fi

echo ""

###################
# Tailwind CSS
###################
echo "--- Tailwind CSS ---"

# Detect version
TW_V4=false
if grep -q '"tailwindcss".*"4\.' package.json 2>/dev/null || grep -q '"@tailwindcss/' package.json 2>/dev/null; then
    TW_V4=true
    info "Tailwind v4 detected"
else
    info "Tailwind v3 detected"
fi

# Check PostCSS config
if [ "$TW_V4" = true ]; then
    if [ -f "postcss.config.mjs" ]; then
        pass "postcss.config.mjs exists"
    elif [ -f "postcss.config.js" ]; then
        fail "Rename postcss.config.js to .mjs for Tailwind v4"
    else
        warn "No PostCSS config found"
    fi
else
    if [ -f "postcss.config.js" ] || [ -f "postcss.config.mjs" ]; then
        pass "PostCSS config exists"
    fi
    
    if [ -f "tailwind.config.js" ] || [ -f "tailwind.config.ts" ]; then
        pass "Tailwind config exists"
    else
        warn "No tailwind.config.* found"
    fi
fi

# Check CSS syntax
if find . -name "*.css" -not -path "./node_modules/*" -exec grep -l '@import.*tailwindcss' {} \; 2>/dev/null | head -1 | grep -q .; then
    if [ "$TW_V4" = true ]; then
        pass "Using @import 'tailwindcss' (v4 syntax)"
    else
        warn "Using v4 syntax but v3 detected"
    fi
elif find . -name "*.css" -not -path "./node_modules/*" -exec grep -l '@tailwind' {} \; 2>/dev/null | head -1 | grep -q .; then
    if [ "$TW_V4" = false ]; then
        pass "Using @tailwind directives (v3 syntax)"
    else
        fail "Using v3 syntax but v4 detected"
    fi
fi

echo ""

###################
# Next.js
###################
if grep -q '"next"' package.json 2>/dev/null; then
    echo "--- Next.js ---"
    
    # Check App Router
    if [ -d "app" ] || [ -d "src/app" ]; then
        pass "App Router detected"
        
        # Check layout
        LAYOUT=$(find . -path "*/app/layout.tsx" -o -path "*/app/layout.jsx" 2>/dev/null | grep -v node_modules | head -1)
        if [ -n "$LAYOUT" ]; then
            pass "Root layout found"
            if grep -q 'globals\|global' "$LAYOUT" 2>/dev/null; then
                pass "CSS import in layout"
            else
                warn "No global CSS import in layout"
            fi
        else
            fail "No root layout found"
        fi
        
        # Check error.tsx files
        for f in $(find . -name "error.tsx" -o -name "global-error.tsx" 2>/dev/null | grep -v node_modules); do
            if grep -q "'use client'" "$f" || grep -q '"use client"' "$f"; then
                pass "$f has 'use client'"
            else
                fail "$f missing 'use client'"
            fi
        done
    fi
    
    # Check for next/router in App Router
    if [ -d "app" ] || [ -d "src/app" ]; then
        if grep -r "from 'next/router'" --include="*.tsx" --include="*.jsx" . 2>/dev/null | grep -v node_modules | head -1 | grep -q .; then
            fail "Using next/router in App Router - use next/navigation"
        fi
    fi
    
    echo ""
fi

###################
# TypeScript
###################
echo "--- TypeScript ---"

if [ -f "tsconfig.json" ]; then
    pass "tsconfig.json exists"
    
    if grep -q '"moduleResolution".*"bundler"' tsconfig.json 2>/dev/null; then
        pass "moduleResolution: bundler"
    else
        warn "Consider moduleResolution: bundler"
    fi
else
    info "JavaScript project (no tsconfig.json)"
fi

echo ""

###################
# Common Issues
###################
echo "--- Common Issues ---"

# Dynamic Tailwind classes
if grep -r 'className.*\${' --include="*.tsx" --include="*.jsx" . 2>/dev/null | grep -v node_modules | head -1 | grep -q .; then
    warn "Dynamic Tailwind classes detected (may be purged)"
fi

# Check cache size
if [ -d ".next" ]; then
    SIZE=$(du -sh .next 2>/dev/null | cut -f1)
    info ".next cache: $SIZE"
fi

# node_modules
if [ -d "node_modules" ]; then
    pass "node_modules exists"
else
    warn "node_modules missing - run npm install"
fi

echo ""

###################
# Summary
###################
echo "=========================================="
echo "  SUMMARY"
echo "=========================================="
if [ $ISSUES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
else
    echo -e "Issues: ${RED}$ISSUES${NC}"
    echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
fi
echo ""

if [ $ISSUES -gt 0 ]; then
    echo "Quick fix: rm -rf .next node_modules/.cache && npm run dev"
    echo ""
fi

exit $ISSUES
