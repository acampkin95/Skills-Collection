#!/bin/bash

# Next.js Code Audit - Security Deep Scan
# Usage: ./audit-security.sh [project-path]

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
echo "║              SECURITY AUDIT                                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

CRITICAL=0
HIGH=0
MEDIUM=0

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ NPM AUDIT ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if [ -f "package-lock.json" ]; then
  AUDIT=$(npm audit --json 2>/dev/null)
  
  CRIT_VULNS=$(echo "$AUDIT" | grep -c '"severity":"critical"' || echo "0")
  HIGH_VULNS=$(echo "$AUDIT" | grep -c '"severity":"high"' || echo "0")
  MOD_VULNS=$(echo "$AUDIT" | grep -c '"severity":"moderate"' || echo "0")
  
  if [ "$CRIT_VULNS" -gt 0 ]; then
    echo -e "${RED}Critical vulnerabilities: $CRIT_VULNS${NC}"
    CRITICAL=$((CRITICAL + CRIT_VULNS))
  fi
  
  if [ "$HIGH_VULNS" -gt 0 ]; then
    echo -e "${YELLOW}High vulnerabilities: $HIGH_VULNS${NC}"
    HIGH=$((HIGH + HIGH_VULNS))
  fi
  
  if [ "$MOD_VULNS" -gt 0 ]; then
    echo "Moderate vulnerabilities: $MOD_VULNS"
    MEDIUM=$((MEDIUM + MOD_VULNS))
  fi
  
  if [ "$CRIT_VULNS" -eq 0 ] && [ "$HIGH_VULNS" -eq 0 ]; then
    echo -e "${GREEN}✓ No critical or high vulnerabilities${NC}"
  fi
  
  echo ""
  echo "Run 'npm audit' for details"
  echo "Run 'npm audit fix' to auto-fix"
else
  echo "No package-lock.json found"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ HARDCODED SECRETS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo "Scanning for potential hardcoded secrets..."
echo ""

# Password patterns
PASSWORDS=$(grep -rn "password.*=.*['\"][^'\"]\+['\"]" \
  --include="*.ts" --include="*.tsx" --include="*.js" \
  app/ lib/ components/ config/ 2>/dev/null | grep -v "node_modules\|.env\|example\|placeholder")

if [ -n "$PASSWORDS" ]; then
  echo -e "${RED}Potential hardcoded passwords:${NC}"
  echo "$PASSWORDS" | head -5
  COUNT=$(echo "$PASSWORDS" | wc -l | tr -d ' ')
  CRITICAL=$((CRITICAL + COUNT))
fi

# API Key patterns
echo ""
echo "API key patterns:"

OPENAI=$(grep -rn "sk-[a-zA-Z0-9]\{20,\}" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules)
[ -n "$OPENAI" ] && echo -e "${RED}OpenAI API key found!${NC}" && echo "$OPENAI" && CRITICAL=$((CRITICAL + 1))

STRIPE=$(grep -rn "sk_\(live\|test\)_[a-zA-Z0-9]\+" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules)
[ -n "$STRIPE" ] && echo -e "${RED}Stripe secret key found!${NC}" && echo "$STRIPE" && CRITICAL=$((CRITICAL + 1))

AWS=$(grep -rn "AKIA[A-Z0-9]\{16\}" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules)
[ -n "$AWS" ] && echo -e "${RED}AWS access key found!${NC}" && echo "$AWS" && CRITICAL=$((CRITICAL + 1))

GITHUB=$(grep -rn "ghp_[a-zA-Z0-9]\{36\}\|github_pat_" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules)
[ -n "$GITHUB" ] && echo -e "${RED}GitHub token found!${NC}" && echo "$GITHUB" && CRITICAL=$((CRITICAL + 1))

DB_URLS=$(grep -rn "mongodb://[^[:space:]]\+@\|postgres://[^[:space:]]\+@\|mysql://[^[:space:]]\+@" \
  --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".env")
[ -n "$DB_URLS" ] && echo -e "${RED}Database connection string found!${NC}" && echo "$DB_URLS" && CRITICAL=$((CRITICAL + 1))

PRIVATE_KEYS=$(grep -rn "BEGIN.*PRIVATE KEY" --include="*.ts" --include="*.tsx" --include="*.pem" . 2>/dev/null | grep -v node_modules)
[ -n "$PRIVATE_KEYS" ] && echo -e "${RED}Private key found!${NC}" && echo "$PRIVATE_KEYS" && CRITICAL=$((CRITICAL + 1))

if [ "$CRITICAL" -eq 0 ]; then
  echo -e "${GREEN}✓ No obvious hardcoded secrets detected${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ ENVIRONMENT VARIABLES ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo "Environment variable usage:"
echo ""

# List all env vars used
ENV_VARS=$(grep -roh "process\.env\.[A-Z_]\+" --include="*.ts" --include="*.tsx" app/ lib/ 2>/dev/null | \
  sort -u | sed 's/process\.env\.//')

echo "Server-side env vars:"
echo "$ENV_VARS" | grep -v "^NEXT_PUBLIC_" | sed 's/^/  /'

echo ""
echo "Client-exposed env vars (NEXT_PUBLIC_):"
echo "$ENV_VARS" | grep "^NEXT_PUBLIC_" | sed 's/^/  /'

# Check for .env.example
echo ""
if [ -f ".env.example" ]; then
  echo -e "${GREEN}✓ .env.example exists${NC}"
else
  echo -e "${YELLOW}Missing .env.example - document required env vars${NC}"
  MEDIUM=$((MEDIUM + 1))
fi

# Check gitignore
if grep -q "\.env" .gitignore 2>/dev/null; then
  echo -e "${GREEN}✓ .env in .gitignore${NC}"
else
  echo -e "${RED}.env NOT in .gitignore!${NC}"
  CRITICAL=$((CRITICAL + 1))
fi

# Check for committed .env files
COMMITTED_ENV=$(git ls-files 2>/dev/null | grep -E "^\.env$|^\.env\.local$|^\.env\.production$")
if [ -n "$COMMITTED_ENV" ]; then
  echo -e "${RED}WARNING: .env files are committed to git!${NC}"
  echo "$COMMITTED_ENV"
  CRITICAL=$((CRITICAL + 1))
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ XSS VULNERABILITIES ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

DANGEROUS=$(grep -rn "dangerouslySetInnerHTML" --include="*.tsx" app/ components/ 2>/dev/null)

if [ -n "$DANGEROUS" ]; then
  echo -e "${YELLOW}dangerouslySetInnerHTML usage:${NC}"
  echo "$DANGEROUS"
  COUNT=$(echo "$DANGEROUS" | wc -l | tr -d ' ')
  HIGH=$((HIGH + COUNT))
  echo ""
  echo "Ensure all content is sanitized with DOMPurify or similar"
else
  echo -e "${GREEN}✓ No dangerouslySetInnerHTML usage${NC}"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ API ROUTE SECURITY ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo "Checking API routes..."
echo ""

API_ROUTES=$(find app/api -name "route.ts" 2>/dev/null)

for route in $API_ROUTES; do
  echo "Checking: $route"
  
  # Check for input validation
  if ! grep -q "zod\|yup\|joi\|validate\|safeParse" "$route" 2>/dev/null; then
    echo -e "  ${YELLOW}⚠ No validation library detected${NC}"
    MEDIUM=$((MEDIUM + 1))
  else
    echo -e "  ${GREEN}✓ Has validation${NC}"
  fi
  
  # Check for auth
  if ! grep -q "auth\|session\|token\|getServerSession\|getToken" "$route" 2>/dev/null; then
    # Check if it's a public route
    if echo "$route" | grep -q "public\|health\|webhook"; then
      echo "  ℹ Appears to be a public endpoint"
    else
      echo -e "  ${YELLOW}⚠ No auth check detected${NC}"
      MEDIUM=$((MEDIUM + 1))
    fi
  else
    echo -e "  ${GREEN}✓ Has auth check${NC}"
  fi
done

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ MIDDLEWARE CHECK ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if [ -f "middleware.ts" ]; then
  echo -e "${GREEN}✓ middleware.ts exists${NC}"
  
  # Check what it protects
  if grep -q "matcher" middleware.ts; then
    echo "Protected routes:"
    grep "matcher" middleware.ts | head -5 | sed 's/^/  /'
  fi
else
  echo -e "${YELLOW}No middleware.ts - consider adding for auth protection${NC}"
  MEDIUM=$((MEDIUM + 1))
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ SECURITY HEADERS ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if ls next.config.* 2>/dev/null | head -1 > /dev/null; then
  CONFIG=$(ls next.config.* 2>/dev/null | head -1)
  
  if grep -q "headers" "$CONFIG"; then
    echo -e "${GREEN}✓ Custom headers configured in $CONFIG${NC}"
    
    # Check for specific headers
    grep -q "Strict-Transport-Security" "$CONFIG" && echo "  ✓ HSTS" || echo "  ⚠ Missing HSTS"
    grep -q "X-Content-Type-Options" "$CONFIG" && echo "  ✓ X-Content-Type-Options" || echo "  ⚠ Missing X-Content-Type-Options"
    grep -q "X-Frame-Options" "$CONFIG" && echo "  ✓ X-Frame-Options" || echo "  ⚠ Missing X-Frame-Options"
    grep -q "Content-Security-Policy" "$CONFIG" && echo "  ✓ CSP" || echo "  ⚠ Missing CSP"
  else
    echo -e "${YELLOW}No security headers configured${NC}"
    MEDIUM=$((MEDIUM + 1))
  fi
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ RATE LIMITING ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

if grep -rq "ratelimit\|rate-limit\|@upstash/ratelimit" --include="*.ts" app/api/ lib/ 2>/dev/null; then
  echo -e "${GREEN}✓ Rate limiting detected${NC}"
else
  echo -e "${YELLOW}No rate limiting detected - consider adding for public APIs${NC}"
  MEDIUM=$((MEDIUM + 1))
fi

echo ""

# ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}═══ SUMMARY ═══${NC}"
# ─────────────────────────────────────────────────────────────────────

echo ""
echo "Security Issues:"
echo -e "  ${RED}Critical: $CRITICAL${NC}"
echo -e "  ${YELLOW}High:     $HIGH${NC}"
echo -e "  Medium:   $MEDIUM"
echo ""

if [ "$CRITICAL" -gt 0 ]; then
  echo -e "${RED}⛔ CRITICAL SECURITY ISSUES - Fix immediately!${NC}"
elif [ "$HIGH" -gt 0 ]; then
  echo -e "${YELLOW}⚠️  High priority security issues found${NC}"
else
  echo -e "${GREEN}✅ No critical security issues detected${NC}"
fi

echo ""
