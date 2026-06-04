#!/bin/bash

# Sanity + Next.js Project Audit Script
# Usage: ./sanity-audit.sh [project-path]

set -euo pipefail

PROJECT_PATH="${1:-.}"
ISSUES=()
WARNINGS=()
INFO=()

echo "🔍 Auditing Sanity + Next.js project at: $PROJECT_PATH"
echo "=============================================="
echo ""

cd "$PROJECT_PATH"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ No package.json found. Is this a Next.js project?"
    exit 1
fi

# Check for required dependencies
echo "📦 Checking dependencies..."

check_dep() {
    if grep -q "\"$1\"" package.json; then
        VERSION=$(grep -o "\"$1\": *\"[^\"]*\"" package.json | head -1 | grep -o '"[0-9^~]*[^"]*"$' | tr -d '"')
        echo "  ✅ $1 ($VERSION)"
    else
        ISSUES+=("Missing dependency: $1")
        echo "  ❌ $1 (missing)"
    fi
}

check_dep "sanity"
check_dep "next-sanity"
check_dep "@sanity/image-url"
check_dep "@portabletext/react"

echo ""

# Check Next.js version
echo "⚡ Checking Next.js version..."
if grep -q '"next"' package.json; then
    NEXT_VERSION=$(grep -o '"next": *"[^"]*"' package.json | grep -o '"[0-9^~]*[^"]*"$' | tr -d '"')
    echo "  ℹ️  Next.js version: $NEXT_VERSION"
    
    # Check for v15
    if [[ "$NEXT_VERSION" == *"15"* ]]; then
        INFO+=("Using Next.js 15 - ensure async request APIs are used")
    fi
fi

echo ""

# Check for Sanity configuration
echo "⚙️  Checking Sanity configuration..."

if [ -f "sanity.config.ts" ] || [ -f "sanity.config.js" ]; then
    echo "  ✅ sanity.config found"
else
    WARNINGS+=("No sanity.config.ts/js found in root")
    echo "  ⚠️  No sanity.config found in root"
fi

if [ -f "sanity.cli.ts" ] || [ -f "sanity.cli.js" ]; then
    echo "  ✅ sanity.cli found"
else
    WARNINGS+=("No sanity.cli.ts/js found - TypeGen won't work")
    echo "  ⚠️  No sanity.cli found"
fi

# Check for schema types
SCHEMA_DIR=""
for dir in "sanity/schemaTypes" "src/sanity/schemaTypes" "schemas" "sanity/schemas"; do
    if [ -d "$dir" ]; then
        SCHEMA_DIR="$dir"
        break
    fi
done

if [ -n "$SCHEMA_DIR" ]; then
    echo "  ✅ Schema directory found: $SCHEMA_DIR"
    SCHEMA_COUNT=$(find "$SCHEMA_DIR" -name "*.ts" -o -name "*.js" 2>/dev/null | wc -l | tr -d ' ')
    echo "     Found $SCHEMA_COUNT schema files"
else
    WARNINGS+=("No schema directory found")
    echo "  ⚠️  No schema directory found"
fi

echo ""

# Check for Live Content API setup
echo "🔴 Checking Live Content API..."

if grep -r "defineLive" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".next" | head -1 > /dev/null; then
    echo "  ✅ defineLive configured"
    
    if grep -r "SanityLive" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".next" | head -1 > /dev/null; then
        echo "  ✅ SanityLive component used"
    else
        WARNINGS+=("defineLive configured but SanityLive component not found in layout")
        echo "  ⚠️  SanityLive component not found"
    fi
else
    INFO+=("Live Content API not configured - consider using defineLive for real-time updates")
    echo "  ℹ️  Live Content API not configured"
fi

echo ""

# Check for environment variables
echo "🔐 Checking environment configuration..."

check_env() {
    if [ -f ".env.local" ] && grep -q "$1" .env.local 2>/dev/null; then
        echo "  ✅ $1 configured"
    elif [ -f ".env" ] && grep -q "$1" .env 2>/dev/null; then
        echo "  ✅ $1 configured"
    else
        WARNINGS+=("Environment variable $1 not found")
        echo "  ⚠️  $1 not found"
    fi
}

check_env "NEXT_PUBLIC_SANITY_PROJECT_ID"
check_env "NEXT_PUBLIC_SANITY_DATASET"
check_env "SANITY_API_READ_TOKEN"

echo ""

# Check for Studio route
echo "🎨 Checking Studio integration..."

STUDIO_FOUND=false
for path in "app/studio" "src/app/studio" "pages/studio"; do
    if [ -d "$path" ]; then
        STUDIO_FOUND=true
        echo "  ✅ Studio route found at $path"
        
        # Check for catch-all route
        if [ -d "${path}/[[...tool]]" ]; then
            echo "  ✅ Catch-all route configured correctly"
        else
            WARNINGS+=("Studio route missing [[...tool]] catch-all")
            echo "  ⚠️  Missing [[...tool]] catch-all route"
        fi
        break
    fi
done

if [ "$STUDIO_FOUND" = false ]; then
    WARNINGS+=("No Studio route found")
    echo "  ⚠️  No Studio route found"
fi

echo ""

# Check for API routes
echo "🌐 Checking API routes..."

# Draft mode
DRAFT_FOUND=false
for path in "app/api/draft-mode" "src/app/api/draft-mode" "app/api/draft" "pages/api/draft"; do
    if [ -d "$path" ] || [ -f "${path}.ts" ]; then
        DRAFT_FOUND=true
        echo "  ✅ Draft mode route found"
        break
    fi
done

if [ "$DRAFT_FOUND" = false ]; then
    WARNINGS+=("No draft mode API route found - Visual Editing won't work")
    echo "  ⚠️  No draft mode route found"
fi

# Revalidation
REVALIDATE_FOUND=false
for path in "app/api/revalidate" "src/app/api/revalidate" "pages/api/revalidate"; do
    if [ -d "$path" ] || [ -f "${path}/route.ts" ] || [ -f "${path}.ts" ]; then
        REVALIDATE_FOUND=true
        echo "  ✅ Revalidation route found"
        break
    fi
done

if [ "$REVALIDATE_FOUND" = false ]; then
    INFO+=("No revalidation webhook route - not needed if using Live Content API")
    echo "  ℹ️  No revalidation route (OK if using Live Content API)"
fi

echo ""

# Check for Next.js config
echo "📋 Checking Next.js configuration..."

CONFIG_FILE=""
for file in "next.config.js" "next.config.mjs" "next.config.ts"; do
    if [ -f "$file" ]; then
        CONFIG_FILE="$file"
        break
    fi
done

if [ -n "$CONFIG_FILE" ]; then
    if grep -q "cdn.sanity.io" "$CONFIG_FILE" 2>/dev/null; then
        echo "  ✅ Sanity CDN configured in image domains"
    else
        WARNINGS+=("cdn.sanity.io not in Next.js image config")
        echo "  ⚠️  cdn.sanity.io not in image config"
    fi
else
    echo "  ℹ️  No next.config found (using defaults)"
fi

echo ""

# Check for TypeScript types
echo "📝 Checking TypeScript setup..."

TYPES_FOUND=false
for file in "sanity.types.ts" "src/sanity/types.ts" "sanity/types.ts"; do
    if [ -f "$file" ]; then
        TYPES_FOUND=true
        echo "  ✅ Generated Sanity types found: $file"
        break
    fi
done

if [ "$TYPES_FOUND" = false ]; then
    WARNINGS+=("No generated types - run: npx sanity typegen generate")
    echo "  ⚠️  No generated types (run: npx sanity typegen generate)"
fi

# Check for schema.json
if [ -f "schema.json" ] || [ -f "src/sanity/extract.json" ]; then
    echo "  ✅ Schema extraction file found"
else
    INFO+=("No schema.json - extract with: npx sanity schema extract")
    echo "  ℹ️  No schema.json found"
fi

echo ""

# Check for defineQuery usage
echo "📝 Checking query patterns..."

if grep -r "defineQuery" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".next" | head -1 > /dev/null; then
    echo "  ✅ defineQuery used for type-safe queries"
else
    INFO+=("Not using defineQuery - consider for better TypeScript integration")
    echo "  ℹ️  defineQuery not found (recommended for TypeGen)"
fi

# Check for schema helpers
if grep -r "defineType\|defineField" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".next" | head -1 > /dev/null; then
    echo "  ✅ Using defineType/defineField helpers"
else
    WARNINGS+=("Not using defineType/defineField helpers - may lack TypeScript support")
    echo "  ⚠️  Not using schema helper functions"
fi

echo ""

# Check for common issues
echo "🔎 Scanning for common issues..."

# Check for useCdn in production
if grep -r "useCdn.*false" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".next" | grep -v "preview" | head -1 > /dev/null; then
    WARNINGS+=("CDN disabled in non-preview client - may affect performance")
    echo "  ⚠️  CDN disabled in some files"
else
    echo "  ✅ No CDN issues found"
fi

# Check for hardcoded project IDs
if grep -rE "projectId:\s*['\"][a-z0-9]{8}['\"]" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".next" | head -1 > /dev/null; then
    WARNINGS+=("Hardcoded projectId found - use environment variable")
    echo "  ⚠️  Hardcoded projectId found"
else
    echo "  ✅ No hardcoded project IDs"
fi

# Check for VisualEditing component
if grep -r "VisualEditing" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".next" | head -1 > /dev/null; then
    echo "  ✅ VisualEditing component configured"
else
    INFO+=("VisualEditing component not found - Visual Editing overlays won't work")
    echo "  ℹ️  VisualEditing component not found"
fi

# Check for webhook signature verification
if grep -r "SANITY_WEBHOOK_SECRET\|sanity-webhook-signature" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".next" | head -1 > /dev/null; then
    echo "  ✅ Webhook signature verification found"
else
    if [ "$REVALIDATE_FOUND" = true ]; then
        WARNINGS+=("Webhook route found but no signature verification - security risk")
        echo "  ⚠️  No webhook signature verification"
    fi
fi

# Check for exposed tokens
if grep -rE "token:\s*['"][^'\"]+['"]" --include="*.ts" --include="*.tsx" . 2>/dev/null | grep -v node_modules | grep -v ".next" | grep -v "process.env" | head -1 > /dev/null; then
    ISSUES+=("Hardcoded API token found - use environment variable")
    echo "  ❌ Hardcoded token found - SECURITY RISK"
else
    echo "  ✅ No hardcoded tokens"
fi

# Check for defined() in slug queries
if grep -rE "slug\.current.*==" --include="*.ts" --include="*.tsx" --include="*.groq" . 2>/dev/null | grep -v node_modules | grep -v ".next" | grep -v "defined" | head -1 > /dev/null; then
    WARNINGS+=("Slug queries without defined() filter found - may cause undefined errors")
    echo "  ⚠️  Slug queries missing defined() filter"
else
    echo "  ✅ Slug queries properly filtered"
fi

echo ""
echo "=============================================="
echo "📊 AUDIT SUMMARY"
echo "=============================================="

if [ ${#ISSUES[@]} -eq 0 ] && [ ${#WARNINGS[@]} -eq 0 ] && [ ${#INFO[@]} -eq 0 ]; then
    echo ""
    echo "✅ All checks passed! Your Sanity + Next.js setup looks great."
else
    if [ ${#ISSUES[@]} -gt 0 ]; then
        echo ""
        echo "❌ ISSUES (${#ISSUES[@]}) - Must fix:"
        for issue in "${ISSUES[@]}"; do
            echo "   • $issue"
        done
    fi

    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo ""
        echo "⚠️  WARNINGS (${#WARNINGS[@]}) - Should fix:"
        for warning in "${WARNINGS[@]}"; do
            echo "   • $warning"
        done
    fi

    if [ ${#INFO[@]} -gt 0 ]; then
        echo ""
        echo "ℹ️  INFO (${#INFO[@]}) - Consider:"
        for info in "${INFO[@]}"; do
            echo "   • $info"
        done
    fi
fi

echo ""
echo "=============================================="

exit 0
