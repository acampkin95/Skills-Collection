#!/bin/bash

# Next.js Code Audit - Discovery Script
# Usage: ./discover.sh [project-path]

set -euo pipefail

PROJECT_PATH="${1:-.}"
cd "$PROJECT_PATH"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              PROJECT DISCOVERY SCAN                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}📁 Project:${NC} $(basename "$(pwd)")"
echo -e "${GREEN}📍 Path:${NC} $(pwd)"
echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ FRAMEWORK DETECTION ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if [ -f "package.json" ]; then
  NEXT_VER=$(grep '"next"' package.json | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "not found")
  REACT_VER=$(grep '"react"' package.json | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "not found")
  TS_VER=$(grep '"typescript"' package.json | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "not found")
  
  echo "  Next.js:     $NEXT_VER"
  echo "  React:       $REACT_VER"
  echo "  TypeScript:  $TS_VER"
  
  # Router type
  if [ -d "app" ]; then
    echo "  Router:      App Router ✓"
  elif [ -d "pages" ]; then
    echo "  Router:      Pages Router (legacy)"
  fi
  
  # Styling
  if [ -f "tailwind.config.ts" ] || [ -f "tailwind.config.js" ] || grep -q "tailwindcss" package.json 2>/dev/null; then
    if grep -q '@import "tailwindcss"' app/globals.css 2>/dev/null; then
      echo "  Styling:     Tailwind CSS v4"
    else
      echo "  Styling:     Tailwind CSS v3"
    fi
  fi
  
  # Linting
  if [ -f "biome.json" ]; then
    echo "  Linter:      Biome"
  elif ls .eslintrc* eslint.config.* 2>/dev/null | head -1 > /dev/null; then
    echo "  Linter:      ESLint"
  else
    echo "  Linter:      None configured"
  fi
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ FILE INVENTORY ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

TS_COUNT=$(find . -name "*.ts" ! -path "*/node_modules/*" ! -path "*/.next/*" 2>/dev/null | wc -l | tr -d ' ')
TSX_COUNT=$(find . -name "*.tsx" ! -path "*/node_modules/*" ! -path "*/.next/*" 2>/dev/null | wc -l | tr -d ' ')
CSS_COUNT=$(find . -name "*.css" ! -path "*/node_modules/*" ! -path "*/.next/*" 2>/dev/null | wc -l | tr -d ' ')
JSON_COUNT=$(find . -name "*.json" ! -path "*/node_modules/*" ! -path "*/.next/*" 2>/dev/null | wc -l | tr -d ' ')
MD_COUNT=$(find . -name "*.md" ! -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
TEST_COUNT=$(find . -name "*.test.*" -o -name "*.spec.*" 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')

TOTAL=$((TS_COUNT + TSX_COUNT))

echo "  TypeScript (.ts):   $TS_COUNT"
echo "  React TSX (.tsx):   $TSX_COUNT"
echo "  CSS files:          $CSS_COUNT"
echo "  JSON files:         $JSON_COUNT"
echo "  Markdown files:     $MD_COUNT"
echo "  Test files:         $TEST_COUNT"
echo "  ─────────────────────"
echo -e "  ${GREEN}Total to audit:       $TOTAL${NC}"

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ DIRECTORY STRUCTURE ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

tree -I 'node_modules|.next|.git|dist|coverage' -L 2 --dirsfirst 2>/dev/null || \
  find . -maxdepth 2 -type d ! -path "*/node_modules/*" ! -path "*/.next/*" ! -path "*/.git/*" | sort

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ KEY DEPENDENCIES ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if [ -f "package.json" ]; then
  echo "  Production:"
  grep -E '"@?[a-z]' package.json | grep -v '"version"\|"name"\|"description"' | \
    grep -A1000 '"dependencies"' | grep -B1000 '"devDependencies"' | \
    grep -E '^\s+"[^"]+":' | head -10 | sed 's/^/    /'
  
  echo ""
  echo "  Development:"
  grep -A1000 '"devDependencies"' package.json | \
    grep -E '^\s+"[^"]+":' | head -10 | sed 's/^/    /'
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ QUICK ISSUE SCAN ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

TODO_COUNT=$(grep -rn "TODO\|FIXME" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
ANY_COUNT=$(grep -rn ": any\|as any" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
CONSOLE_COUNT=$(grep -rn "console\." --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
CLIENT_COUNT=$(grep -rl "'use client'" --include="*.tsx" app/ components/ 2>/dev/null | wc -l | tr -d ' ')

echo "  TODOs/FIXMEs:        $TODO_COUNT"
echo "  'any' usage:         $ANY_COUNT"
echo "  console statements:  $CONSOLE_COUNT"
echo "  Client components:   $CLIENT_COUNT / $TSX_COUNT"

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ ROUTES ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo "  Pages:"
find app -name "page.tsx" 2>/dev/null | sed 's|/page.tsx||;s|^app||;s|^$|/|' | sort | head -15 | sed 's/^/    /'

echo ""
echo "  API Routes:"
find app/api -name "route.ts" 2>/dev/null | sed 's|/route.ts||;s|^app/api||' | sort | head -10 | sed 's/^/    /'

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ CONFIG FILES STATUS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

check_file() {
  [ -f "$1" ] && echo "  ✅ $1" || echo "  ❌ $1"
}

check_file "package.json"
check_file "tsconfig.json"
ls next.config.* 2>/dev/null | head -1 | xargs -I {} echo "  ✅ {}" || echo "  ❌ next.config.*"
check_file "postcss.config.mjs"
[ -f "biome.json" ] && echo "  ✅ biome.json" || (ls .eslintrc* eslint.config.* 2>/dev/null | head -1 | xargs -I {} echo "  ✅ {}" || echo "  ⚠️  No linter config")
check_file ".env.example"
check_file "middleware.ts"

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ NEXT STEPS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo "  Run full audit:"
echo "    ./scripts/audit-full.sh"
echo ""
echo "  Run quick quality scan:"
echo "    ./scripts/audit-quick.sh"
echo ""
echo "  Run linked file analysis:"
echo "    ./scripts/audit-linked.sh"
echo ""

echo -e "${GREEN}Discovery complete. $TOTAL files ready for audit.${NC}"
