#!/bin/bash

# Next.js Code Audit - Quick Quality Scan
# Fast scan for easy wins and low-hanging fruit
# Usage: ./audit-quick.sh [project-path]

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
echo "║              QUICK QUALITY SCAN                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

ISSUES=0

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ CONSOLE STATEMENTS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

CONSOLES=$(grep -rn "console\.\(log\|warn\|error\|info\|debug\)" \
  --include="*.ts" --include="*.tsx" \
  app/ lib/ components/ 2>/dev/null)

if [ -n "$CONSOLES" ]; then
  echo "$CONSOLES" | head -15
  COUNT=$(echo "$CONSOLES" | wc -l | tr -d ' ')
  echo -e "${YELLOW}Found: $COUNT console statements${NC}"
  ISSUES=$((ISSUES + COUNT))
  echo ""
  echo "Auto-fix: Remove manually or use:"
  echo "  grep -rl 'console\\.' --include='*.tsx' app/ | xargs sed -i '' '/console\\./d'"
else
  echo -e "${GREEN}✓ No console statements found${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ DEBUGGER STATEMENTS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

DEBUGGERS=$(grep -rn "debugger" --include="*.ts" --include="*.tsx" \
  app/ lib/ components/ 2>/dev/null)

if [ -n "$DEBUGGERS" ]; then
  echo "$DEBUGGERS"
  COUNT=$(echo "$DEBUGGERS" | wc -l | tr -d ' ')
  echo -e "${RED}Found: $COUNT debugger statements - REMOVE BEFORE DEPLOY${NC}"
  ISSUES=$((ISSUES + COUNT * 5))
else
  echo -e "${GREEN}✓ No debugger statements${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ EMPTY CATCH BLOCKS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

# Simple pattern for empty catches
EMPTY_CATCHES=$(grep -rn "catch.*{[[:space:]]*}" --include="*.ts" --include="*.tsx" \
  app/ lib/ 2>/dev/null)

if [ -n "$EMPTY_CATCHES" ]; then
  echo "$EMPTY_CATCHES" | head -10
  COUNT=$(echo "$EMPTY_CATCHES" | wc -l | tr -d ' ')
  echo -e "${YELLOW}Found: $COUNT empty catch blocks${NC}"
  ISSUES=$((ISSUES + COUNT * 2))
else
  echo -e "${GREEN}✓ No empty catch blocks${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ COMMENTED CODE BLOCKS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

COMMENTED=$(grep -rn "^[[:space:]]*//.*function\|^[[:space:]]*//.*const\|^[[:space:]]*//.*return" \
  --include="*.ts" --include="*.tsx" app/ lib/ components/ 2>/dev/null | head -10)

if [ -n "$COMMENTED" ]; then
  echo "$COMMENTED"
  COUNT=$(echo "$COMMENTED" | wc -l | tr -d ' ')
  echo -e "${YELLOW}Found: ~$COUNT commented code blocks${NC}"
  ISSUES=$((ISSUES + COUNT))
else
  echo -e "${GREEN}✓ No obvious commented code${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ TODO/FIXME COMMENTS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

FIXMES=$(grep -rn "FIXME" --include="*.ts" --include="*.tsx" \
  app/ lib/ components/ 2>/dev/null)

if [ -n "$FIXMES" ]; then
  echo -e "${RED}FIXMEs (should fix now):${NC}"
  echo "$FIXMES" | head -5
  FIXME_COUNT=$(echo "$FIXMES" | wc -l | tr -d ' ')
  ISSUES=$((ISSUES + FIXME_COUNT * 3))
fi

TODOS=$(grep -rn "TODO" --include="*.ts" --include="*.tsx" \
  app/ lib/ components/ 2>/dev/null)

if [ -n "$TODOS" ]; then
  echo ""
  echo "TODOs:"
  echo "$TODOS" | head -5
  TODO_COUNT=$(echo "$TODOS" | wc -l | tr -d ' ')
  ISSUES=$((ISSUES + TODO_COUNT))
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ EXPLICIT 'any' USAGE ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

ANYS=$(grep -rn ": any\|as any\|<any>" --include="*.ts" --include="*.tsx" \
  app/ lib/ components/ 2>/dev/null)

if [ -n "$ANYS" ]; then
  echo "$ANYS" | head -10
  COUNT=$(echo "$ANYS" | wc -l | tr -d ' ')
  echo -e "${YELLOW}Found: $COUNT 'any' usages${NC}"
  ISSUES=$((ISSUES + COUNT))
else
  echo -e "${GREEN}✓ No explicit 'any' usage${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ TRAILING WHITESPACE ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

TRAILING=$(grep -rln "[[:space:]]$" --include="*.ts" --include="*.tsx" \
  app/ lib/ components/ 2>/dev/null | head -10)

if [ -n "$TRAILING" ]; then
  echo "$TRAILING"
  COUNT=$(echo "$TRAILING" | wc -l | tr -d ' ')
  echo -e "${YELLOW}Found: $COUNT files with trailing whitespace${NC}"
  echo ""
  echo "Auto-fix:"
  echo "  find app/ lib/ components/ -name '*.tsx' -o -name '*.ts' | xargs sed -i '' 's/[[:space:]]*$//'"
else
  echo -e "${GREEN}✓ No trailing whitespace${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ LONG LINES (>120 chars) ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

LONG_LINES=$(find app/ lib/ components/ -name "*.tsx" -o -name "*.ts" 2>/dev/null | \
  xargs awk 'length > 120 {print FILENAME":"NR": "length" chars"}' 2>/dev/null | head -10)

if [ -n "$LONG_LINES" ]; then
  echo "$LONG_LINES"
  COUNT=$(echo "$LONG_LINES" | wc -l | tr -d ' ')
  echo -e "${YELLOW}Found: $COUNT+ long lines${NC}"
else
  echo -e "${GREEN}✓ No excessively long lines${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ LINTER AUTO-FIX ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if [ -f "biome.json" ]; then
  echo "Run Biome auto-fix:"
  echo "  npx @biomejs/biome check --apply ."
  echo ""
  echo "Safe fixes only:"
  echo "  npx @biomejs/biome check --apply-unsafe=false ."
elif ls .eslintrc* eslint.config.* 2>/dev/null | head -1 > /dev/null; then
  echo "Run ESLint auto-fix:"
  echo "  npx eslint . --fix --ext .ts,.tsx"
else
  echo "No linter configured. Consider adding Biome:"
  echo "  npm install -D @biomejs/biome"
  echo "  npx @biomejs/biome init"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ SUMMARY ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo ""
if [ "$ISSUES" -eq 0 ]; then
  echo -e "${GREEN}✅ No quick-fix issues found!${NC}"
elif [ "$ISSUES" -lt 20 ]; then
  echo -e "${GREEN}Found $ISSUES minor issues - quick cleanup needed${NC}"
elif [ "$ISSUES" -lt 50 ]; then
  echo -e "${YELLOW}Found $ISSUES issues - moderate cleanup needed${NC}"
else
  echo -e "${RED}Found $ISSUES issues - significant cleanup needed${NC}"
fi

echo ""
echo "Run full audit for comprehensive analysis:"
echo "  ./scripts/audit-full.sh"
