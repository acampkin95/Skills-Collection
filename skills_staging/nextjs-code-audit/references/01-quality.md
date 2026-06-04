# 01. Code Quality Audit

## Table of Contents
1. [Dead Code Detection](#1-dead-code-detection)
2. [Unused Imports](#2-unused-imports)
3. [Formatting & Consistency](#3-formatting--consistency)
4. [Naming Conventions](#4-naming-conventions)
5. [Code Smells](#5-code-smells)
6. [Auto-Fix Commands](#6-auto-fix-commands)

---

## 1. Dead Code Detection

### Automated Scans

```bash
# Comprehensive dead code detection
npx ts-prune --error                              # Unused exports
npx knip                                          # Unused files, deps, exports
npx unimported                                    # Unimported files

# ESLint rules
npx eslint . --rule "no-unused-vars: error" \
             --rule "no-unreachable: error" \
             --rule "@typescript-eslint/no-unused-vars: error" \
             --ext .ts,.tsx

# Biome
npx @biomejs/biome lint --only=correctness/noUnusedVariables \
                        --only=correctness/noUnreachable .
```

### Manual Detection Patterns

```bash
# Empty functions/callbacks
grep -rn "() => {}" --include="*.tsx" --include="*.ts" app/ lib/ components/
grep -rn "function.*() {}" --include="*.tsx" --include="*.ts" app/ lib/

# Empty catch blocks
grep -rn "catch.*{[[:space:]]*}" --include="*.ts" --include="*.tsx" .
grep -rn -A1 "catch" --include="*.ts" . | grep -B1 "^[[:space:]]*}$"

# Unreachable code after return/throw
grep -rn -A2 "return\|throw" --include="*.ts" --include="*.tsx" . | \
  grep -v "^--$" | grep -A1 "return\|throw" | grep -v "return\|throw\|}\|//"

# Unused parameters (underscore prefix is intentional)
grep -rn "function.*([^)]*,[^)]*)" --include="*.ts" . | \
  grep -v "_[a-zA-Z]"

# Commented code blocks (3+ lines)
awk '/^[[:space:]]*\/\// {count++; if(count==1) start=NR} 
     !/^[[:space:]]*\/\// {if(count>=3) print FILENAME":"start"-"NR-1; count=0}
     END {if(count>=3) print FILENAME":"start"-"NR}' app/**/*.tsx

# Console statements
grep -rn "console\.\(log\|warn\|error\|info\|debug\|trace\)" \
  --include="*.ts" --include="*.tsx" app/ lib/ components/

# Debugger statements
grep -rn "debugger" --include="*.ts" --include="*.tsx" .
```

### Dead Code Categories

| Type | Detection | Severity | Auto-fixable |
|------|-----------|----------|--------------|
| Unused variable | ESLint/Biome | Low | Yes |
| Unused import | ESLint/Biome | Low | Yes |
| Unused export | ts-prune/knip | Medium | Manual |
| Unreachable code | ESLint | Medium | Manual |
| Empty function | grep | Low | Manual |
| Commented code | grep/manual | Low | Manual |
| console.log | grep | Low | Yes |
| Dead file | knip/unimported | Medium | Manual |

---

## 2. Unused Imports

### Detection

```bash
# ESLint with unused-imports plugin
npx eslint . --rule "unused-imports/no-unused-imports: error" --ext .ts,.tsx

# Biome
npx @biomejs/biome lint --only=correctness/noUnusedImports .

# TypeScript
npx tsc --noEmit --noUnusedLocals

# Manual: Find imports, check if used
grep -rn "^import" --include="*.tsx" app/ | while read line; do
  file=$(echo "$line" | cut -d: -f1)
  imports=$(echo "$line" | grep -oE "{ [^}]+ }" | tr -d '{} ' | tr ',' '\n')
  for imp in $imports; do
    count=$(grep -c "$imp" "$file" 2>/dev/null || echo 0)
    if [ "$count" -eq 1 ]; then
      echo "Potentially unused: $imp in $file"
    fi
  done
done 2>/dev/null | head -20
```

### Common Patterns

```typescript
// ❌ Imported but never used
import { Button, Card, Modal } from '@/components/ui'
// Only Button used below

// ❌ Type import without 'type' keyword
import { User } from '@/types'  // Should be: import type { User }

// ❌ React import not needed (React 17+)
import React from 'react'

// ❌ Namespace import with partial usage
import * as utils from '@/lib/utils'  // Only utils.cn used

// ❌ Side-effect import that's not needed
import './styles.css'  // File doesn't exist or not used

// ✅ Correct patterns
import { Button } from '@/components/ui/button'
import type { User } from '@/types'
import { cn } from '@/lib/utils'
```

---

## 3. Formatting & Consistency

### Configuration Check

```bash
# List all formatting configs
ls -la .eslintrc* eslint.config.* .prettierrc* prettier.config.* biome.json .editorconfig 2>/dev/null

# Check for conflicts
if [ -f "biome.json" ] && [ -f ".prettierrc" ]; then
  echo "⚠️ Both Biome and Prettier configured - potential conflicts"
fi

# Verify editorconfig
cat .editorconfig 2>/dev/null || echo "⚠️ No .editorconfig found"
```

### Consistency Checks

```bash
# Indentation consistency
grep -rn "^  [^ ]" --include="*.tsx" app/ | head -5   # 2-space
grep -rn "^    [^ ]" --include="*.tsx" app/ | head -5 # 4-space
grep -rn "^	" --include="*.tsx" app/ | head -5        # tabs

# Quote consistency
echo "Single quotes: $(grep -roh "'" --include="*.tsx" app/ | wc -l)"
echo "Double quotes: $(grep -roh '"' --include="*.tsx" app/ | wc -l)"

# Semicolon consistency
echo "With semicolons: $(grep -rn ";$" --include="*.tsx" app/ | wc -l)"
echo "Without: $(grep -rn "[^;]$" --include="*.tsx" app/ | grep -v "^$\|{\|}\|//\|/*" | wc -l)"

# Trailing commas
grep -rn ",$" --include="*.tsx" app/ | grep -E "\],$|\},$" | wc -l

# Line length violations (>100)
awk 'length > 100 {print FILENAME":"NR": "length" chars"}' app/**/*.tsx 2>/dev/null | head -10

# Trailing whitespace
grep -rln "[[:space:]]$" --include="*.ts" --include="*.tsx" app/ lib/

# Multiple blank lines
awk '/^$/ {blank++; if(blank>1) print FILENAME":"NR} !/^$/ {blank=0}' app/**/*.tsx 2>/dev/null
```

### Recommended Config (Biome)

```json
{
  "formatter": {
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "semicolons": "asNeeded",
      "trailingCommas": "es5"
    }
  }
}
```

---

## 4. Naming Conventions

### Expected Patterns

| Type | Convention | Pattern | Example |
|------|------------|---------|---------|
| Component files | PascalCase | `[A-Z][a-zA-Z]+\.tsx` | `UserProfile.tsx` |
| Hook files | camelCase + use | `use[A-Z][a-zA-Z]+\.ts` | `useAuth.ts` |
| Utility files | kebab-case | `[a-z-]+\.ts` | `date-utils.ts` |
| Type files | kebab-case or PascalCase | varies | `user-types.ts` |
| Constants | SCREAMING_SNAKE | `[A-Z_]+` | `API_BASE_URL` |
| Functions | camelCase | `[a-z][a-zA-Z]+` | `formatDate` |
| Components | PascalCase | `[A-Z][a-zA-Z]+` | `UserProfile` |
| Hooks | camelCase + use | `use[A-Z][a-zA-Z]+` | `useAuth` |
| Boolean vars | is/has/should prefix | `is[A-Z]` | `isLoading` |

### Detection

```bash
# Components not PascalCase
find components/ -name "*.tsx" | xargs -I {} basename {} .tsx | \
  grep -v "^[A-Z]" | while read f; do echo "❌ $f should be PascalCase"; done

# Hooks without 'use' prefix
find hooks/ -name "*.ts" | xargs -I {} basename {} .ts | \
  grep -v "^use[A-Z]" | while read f; do echo "❌ $f should start with 'use'"; done

# Constants not SCREAMING_SNAKE
grep -rn "^const [a-z].*=" --include="*.ts" lib/constants/ 2>/dev/null

# Boolean variables without is/has/should
grep -rn "const \(loading\|visible\|open\|active\|disabled\|checked\) =" \
  --include="*.tsx" app/ components/

# Generic variable names
grep -rn "const \(data\|info\|result\|temp\|item\|value\) =" \
  --include="*.ts" --include="*.tsx" app/ lib/
```

---

## 5. Code Smells

### Detection Patterns

```bash
# Long functions (>50 lines)
awk '/^(export )?(async )?function|^const.*=>.*{$/ {start=NR; name=$0} 
     /^}$/ {if(NR-start>50) print FILENAME":"start": Function too long ("NR-start" lines)"}' \
     app/**/*.tsx 2>/dev/null

# Deep nesting (>4 levels)
awk '{
  depth=0; for(i=1;i<=length($0);i++) {
    c=substr($0,i,1)
    if(c=="{") depth++
    if(depth>4) {print FILENAME":"NR": Deep nesting ("depth")"; break}
    if(c=="}") depth--
  }
}' app/**/*.tsx 2>/dev/null | head -10

# Long parameter lists (>4 params)
grep -rn "function.*([^)]*,[^)]*,[^)]*,[^)]*,[^)]*)" --include="*.ts" .

# Magic numbers
grep -rn "[^a-zA-Z_][0-9]\{2,\}[^0-9px%rem]" --include="*.tsx" app/ | \
  grep -v "//\|console\|version\|[12][0-9][0-9][0-9]" | head -10

# Nested ternaries
grep -rn "?.*?.*:" --include="*.tsx" app/ components/

# Long files (>300 lines)
wc -l app/**/*.tsx components/**/*.tsx 2>/dev/null | \
  awk '$1 > 300 {print "❌ "$2" has "$1" lines"}' | head -10

# Too many imports (>15)
for f in $(find app/ components/ -name "*.tsx"); do
  imports=$(grep -c "^import" "$f" 2>/dev/null || echo 0)
  [ "$imports" -gt 15 ] && echo "❌ $f has $imports imports"
done
```

---

## 6. Auto-Fix Commands

### Safe Fixes (Non-breaking)

```bash
# Remove unused imports
npx @biomejs/biome check --apply .
# or
npx eslint . --fix --ext .ts,.tsx

# Format code
npx @biomejs/biome format --write .
# or
npx prettier --write .

# Sort imports
npx @biomejs/biome check --apply --only=organizeImports .

# Remove console.logs (careful!)
find app/ lib/ components/ -name "*.tsx" -o -name "*.ts" | \
  xargs sed -i '' '/console\.log/d'
```

### Fix Script

```bash
#!/bin/bash
# fix-quality.sh - Apply quality fixes

echo "🔧 Applying quality fixes..."

# Biome format + lint fixes
npx @biomejs/biome check --apply . 2>/dev/null

# ESLint fixes
npx eslint . --fix --ext .ts,.tsx 2>/dev/null

# Remove trailing whitespace
find app/ lib/ components/ -name "*.ts" -o -name "*.tsx" | \
  xargs sed -i '' 's/[[:space:]]*$//'

echo "✅ Quality fixes applied"
```

### Quality Score Calculation

```
Quality Score = 10 - (
  (dead_code_count × 0.1) +
  (unused_imports × 0.05) +
  (formatting_issues × 0.02) +
  (naming_violations × 0.1) +
  (code_smells × 0.2)
)

Minimum: 0, Maximum: 10
```
