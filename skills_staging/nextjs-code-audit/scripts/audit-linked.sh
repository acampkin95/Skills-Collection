#!/bin/bash

# Next.js Code Audit - Linked File Analysis
# Cross-file integrity checks
# Usage: ./audit-linked.sh [project-path]

set -euo pipefail

PROJECT_PATH="${1:-.}"
cd "$PROJECT_PATH"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              LINKED FILE ANALYSIS                             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

ISSUES=0

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ CIRCULAR DEPENDENCIES ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if command -v npx &> /dev/null; then
  CIRCULAR=$(npx madge --circular --extensions ts,tsx app/ lib/ components/ 2>/dev/null)
  
  if echo "$CIRCULAR" | grep -q "Circular"; then
    echo -e "${RED}$CIRCULAR${NC}"
    COUNT=$(echo "$CIRCULAR" | grep -c "→" || echo "0")
    echo -e "${RED}Found $COUNT circular dependency chains${NC}"
    ISSUES=$((ISSUES + COUNT * 5))
  else
    echo -e "${GREEN}✓ No circular dependencies detected${NC}"
  fi
else
  echo "Install madge for circular dependency detection:"
  echo "  npm install -g madge"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ IMPORT RESOLUTION CHECK ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo "Checking import paths..."

# Extract all imports and verify they resolve
BROKEN_IMPORTS=0
for f in $(find app/ lib/ components/ -name "*.ts" -o -name "*.tsx" 2>/dev/null | head -100); do
  imports=$(grep "^import.*from ['\"]" "$f" 2>/dev/null | \
    grep -oE "from ['\"][^'\"]+['\"]" | sed "s/from ['\"]//;s/['\"]//")
  
  for imp in $imports; do
    # Skip node_modules
    [[ "$imp" == @* ]] && [[ "$imp" != @/* ]] && continue
    [[ "$imp" == react* ]] && continue
    [[ "$imp" == next* ]] && continue
    
    # Check @/ alias
    if [[ "$imp" == @/* ]]; then
      rel_path="${imp#@/}"
      if [ ! -f "$rel_path.ts" ] && [ ! -f "$rel_path.tsx" ] && \
         [ ! -f "$rel_path/index.ts" ] && [ ! -f "$rel_path/index.tsx" ] && \
         [ ! -d "$rel_path" ]; then
        echo -e "${YELLOW}Unresolved: $imp in $f${NC}"
        BROKEN_IMPORTS=$((BROKEN_IMPORTS + 1))
      fi
    fi
  done
done

if [ "$BROKEN_IMPORTS" -eq 0 ]; then
  echo -e "${GREEN}✓ All sampled imports resolve correctly${NC}"
else
  echo -e "${YELLOW}Found $BROKEN_IMPORTS potentially broken imports${NC}"
  ISSUES=$((ISSUES + BROKEN_IMPORTS * 2))
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ UNUSED EXPORTS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if command -v npx &> /dev/null; then
  UNUSED=$(npx ts-prune --error 2>/dev/null | head -20)
  
  if [ -n "$UNUSED" ]; then
    echo "$UNUSED"
    COUNT=$(echo "$UNUSED" | wc -l | tr -d ' ')
    echo -e "${YELLOW}Found $COUNT unused exports${NC}"
    ISSUES=$((ISSUES + COUNT))
  else
    echo -e "${GREEN}✓ No unused exports detected${NC}"
  fi
else
  echo "Install ts-prune for unused export detection:"
  echo "  npm install -g ts-prune"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ LAYER VIOLATIONS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo "Checking layer boundaries..."

# lib/ should NOT import from components/
LIB_COMPS=$(grep -rn "from ['\"]@/components" --include="*.ts" lib/ 2>/dev/null)
if [ -n "$LIB_COMPS" ]; then
  echo -e "${RED}lib/ imports from components/ (violation):${NC}"
  echo "$LIB_COMPS"
  COUNT=$(echo "$LIB_COMPS" | wc -l | tr -d ' ')
  ISSUES=$((ISSUES + COUNT * 3))
else
  echo -e "${GREEN}✓ lib/ does not import from components/${NC}"
fi

# hooks/ should NOT import from components/
HOOKS_COMPS=$(grep -rn "from ['\"]@/components" --include="*.ts" hooks/ 2>/dev/null)
if [ -n "$HOOKS_COMPS" ]; then
  echo -e "${RED}hooks/ imports from components/ (violation):${NC}"
  echo "$HOOKS_COMPS"
  COUNT=$(echo "$HOOKS_COMPS" | wc -l | tr -d ' ')
  ISSUES=$((ISSUES + COUNT * 3))
else
  echo -e "${GREEN}✓ hooks/ does not import from components/${NC}"
fi

# components/ should NOT import from app/
COMPS_APP=$(grep -rn "from ['\"]@/app" --include="*.tsx" components/ 2>/dev/null)
if [ -n "$COMPS_APP" ]; then
  echo -e "${RED}components/ imports from app/ (violation):${NC}"
  echo "$COMPS_APP"
  COUNT=$(echo "$COMPS_APP" | wc -l | tr -d ' ')
  ISSUES=$((ISSUES + COUNT * 3))
else
  echo -e "${GREEN}✓ components/ does not import from app/${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ BARREL FILES ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo "Checking barrel file (index.ts) usage..."

BARRELS=$(find . -name "index.ts" -o -name "index.tsx" 2>/dev/null | \
  grep -v node_modules | grep -v ".next")

BARREL_COUNT=$(echo "$BARRELS" | wc -l | tr -d ' ')
echo "Found $BARREL_COUNT barrel files:"
echo "$BARRELS" | head -10 | sed 's/^/  /'

# Check for barrel imports in client components
echo ""
echo "Barrel imports in client components (anti-pattern):"
for f in $(grep -l "'use client'" --include="*.tsx" app/ components/ 2>/dev/null); do
  if grep -q "from ['\"]@/components['\"]" "$f" 2>/dev/null; then
    echo -e "${YELLOW}  $f imports from @/components (use direct imports)${NC}"
    ISSUES=$((ISSUES + 1))
  fi
done

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ IMPORT STYLE CONSISTENCY ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

ALIAS=$(grep -rn "from ['\"]@/" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
RELATIVE=$(grep -rn "from ['\"]\.\./" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')
DEEP_RELATIVE=$(grep -rn "from ['\"]\.\.\/\.\.\/\.\.\/" --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | wc -l | tr -d ' ')

echo "  Alias imports (@/):     $ALIAS"
echo "  Relative imports (../): $RELATIVE"
echo "  Deep relative (../../..): $DEEP_RELATIVE"

if [ "$DEEP_RELATIVE" -gt 0 ]; then
  echo -e "${YELLOW}Found $DEEP_RELATIVE deep relative imports - consider using @/ alias${NC}"
  ISSUES=$((ISSUES + DEEP_RELATIVE))
fi

TOTAL_IMPORTS=$((ALIAS + RELATIVE))
if [ "$TOTAL_IMPORTS" -gt 0 ]; then
  ALIAS_PERCENT=$((ALIAS * 100 / TOTAL_IMPORTS))
  echo "  Alias usage: $ALIAS_PERCENT%"
  
  if [ "$ALIAS_PERCENT" -lt 50 ]; then
    echo -e "${YELLOW}Low alias usage - consider standardizing on @/ imports${NC}"
  fi
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ CROSS-DIRECTORY DEPENDENCIES ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo "Dependency flow:"
echo ""

# Count imports between directories
for src in app lib components hooks; do
  [ ! -d "$src" ] && continue
  echo "  From $src/:"
  for dest in app lib components hooks types; do
    [ "$src" = "$dest" ] && continue
    count=$(grep -rn "from ['\"]@/$dest" --include="*.ts" --include="*.tsx" "$src/" 2>/dev/null | wc -l | tr -d ' ')
    [ "$count" -gt 0 ] && echo "    → $dest/: $count imports"
  done
done

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ TYPE DEFINITION COMPLETENESS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if [ -d "types" ]; then
  TYPE_FILES=$(find types/ -name "*.ts" 2>/dev/null | wc -l | tr -d ' ')
  echo "Type definition files: $TYPE_FILES"
  
  # Check for index.ts
  if [ -f "types/index.ts" ]; then
    echo -e "${GREEN}✓ types/index.ts exists${NC}"
  else
    echo -e "${YELLOW}Missing types/index.ts barrel file${NC}"
  fi
else
  echo -e "${YELLOW}No types/ directory found${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ DEPENDENCY GRAPH ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if command -v npx &> /dev/null; then
  echo "Generate visual dependency graph:"
  echo "  npx madge --image deps.svg --extensions ts,tsx app/ lib/ components/"
  echo ""
  echo "Most depended-on files:"
  npx madge --extensions ts,tsx app/ lib/ components/ 2>/dev/null | \
    awk -F: '{for(i=2;i<=NF;i++) print $i}' | tr ',' '\n' | tr -d ' ' | \
    sort | uniq -c | sort -rn | head -10 | sed 's/^/  /'
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ SUMMARY ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo ""
if [ "$ISSUES" -eq 0 ]; then
  echo -e "${GREEN}✅ No linked file issues found!${NC}"
elif [ "$ISSUES" -lt 10 ]; then
  echo -e "${GREEN}Found $ISSUES minor linking issues${NC}"
elif [ "$ISSUES" -lt 30 ]; then
  echo -e "${YELLOW}Found $ISSUES linking issues - refactoring recommended${NC}"
else
  echo -e "${RED}Found $ISSUES linking issues - architecture review needed${NC}"
fi

echo ""
