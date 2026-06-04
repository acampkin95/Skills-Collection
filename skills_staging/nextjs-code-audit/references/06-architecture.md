# 06. Architecture Audit

## Table of Contents
1. [Project Structure](#1-project-structure)
2. [App Router Patterns](#2-app-router-patterns)
3. [Component Organization](#3-component-organization)
4. [Module Boundaries](#4-module-boundaries)
5. [Dependency Analysis](#5-dependency-analysis)
6. [Recommendations](#6-recommendations)

---

## 1. Project Structure

### Discovery

```bash
# Project tree
tree -I 'node_modules|.next|.git|dist' -L 3 --dirsfirst

# File distribution
echo "=== Files by directory ==="
for dir in app components lib hooks types utils config public; do
  [ -d "$dir" ] && echo "$dir: $(find "$dir" -name "*.ts" -o -name "*.tsx" | wc -l) files"
done

# Large directories (potential splitting)
find . -type d ! -path "*/node_modules/*" ! -path "*/.next/*" -exec sh -c '
  count=$(find "$1" -maxdepth 1 -name "*.tsx" -o -name "*.ts" 2>/dev/null | wc -l)
  [ "$count" -gt 15 ] && echo "$count files: $1"
' _ {} \; | sort -rn

# Deep nesting
find . -mindepth 5 -name "*.tsx" ! -path "*/node_modules/*" | head -10
```

### Recommended Structure

```
project/
├── app/                      # App Router (routes only)
│   ├── (auth)/              # Route group: auth pages
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/         # Route group: dashboard
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── settings/page.tsx
│   ├── api/                 # API routes
│   │   └── [...]/route.ts
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home
│   ├── error.tsx            # Error boundary
│   ├── not-found.tsx        # 404
│   └── globals.css
├── components/              # Shared UI components
│   ├── ui/                 # Primitives (button, input, card)
│   ├── forms/              # Form components
│   ├── layouts/            # Header, footer, sidebar
│   └── [feature]/          # Feature-specific
├── lib/                     # Core logic
│   ├── actions/            # Server actions
│   ├── db/                 # Database client, queries
│   ├── auth/               # Auth utilities
│   ├── api/                # API client
│   └── utils/              # Utilities
├── hooks/                   # Custom hooks
├── types/                   # TypeScript types
├── config/                  # App configuration
├── public/                  # Static assets
└── tests/                   # Test files (or colocated)
```

### Anti-Patterns

```bash
# Files in project root
ls *.ts *.tsx 2>/dev/null | grep -v "config\|middleware"

# Deeply nested components
find components/ -mindepth 4 -name "*.tsx" 2>/dev/null

# Mixed concerns in directories
find app/ -name "*.ts" ! -name "*.test.ts" ! -name "route.ts" ! -name "page.tsx" ! -name "layout.tsx" | head

# Inconsistent naming
find components/ -name "*.tsx" | xargs -I {} basename {} .tsx | grep -E "^[a-z]"
```

---

## 2. App Router Patterns

### Route Analysis

```bash
# List all routes
find app -name "page.tsx" | sed 's|/page.tsx||;s|^app||' | sort

# API routes
find app/api -name "route.ts" | sed 's|/route.ts||;s|^app/api||' | sort

# Route groups
find app -type d -name "(*)" | sort

# Dynamic routes
find app -type d -name "[*]*" | sort

# Parallel routes
find app -type d -name "@*" | sort
```

### Required Files Audit

```bash
# Check required files
echo "=== Required Files ==="
[ -f "app/layout.tsx" ] && echo "✅ app/layout.tsx" || echo "❌ app/layout.tsx (REQUIRED)"
[ -f "app/page.tsx" ] && echo "✅ app/page.tsx" || echo "❌ app/page.tsx"
[ -f "app/error.tsx" ] && echo "✅ app/error.tsx" || echo "⚠️ app/error.tsx (recommended)"
[ -f "app/not-found.tsx" ] && echo "✅ app/not-found.tsx" || echo "⚠️ app/not-found.tsx (recommended)"
[ -f "app/loading.tsx" ] && echo "✅ app/loading.tsx" || echo "ℹ️ app/loading.tsx (optional)"
[ -f "app/global-error.tsx" ] && echo "✅ app/global-error.tsx" || echo "⚠️ app/global-error.tsx (recommended)"
[ -f "middleware.ts" ] && echo "✅ middleware.ts" || echo "ℹ️ middleware.ts (if auth needed)"

# Verify 'use client' on error files
echo ""
echo "=== Error File Directives ==="
[ -f "app/error.tsx" ] && head -1 app/error.tsx | grep -q "'use client'" && echo "✅ error.tsx has 'use client'" || echo "❌ error.tsx needs 'use client'"
[ -f "app/global-error.tsx" ] && head -1 app/global-error.tsx | grep -q "'use client'" && echo "✅ global-error.tsx has 'use client'" || echo "❌ global-error.tsx needs 'use client'"
```

### Layout Hierarchy

```bash
# Find all layouts
echo "=== Layout Hierarchy ==="
find app -name "layout.tsx" | sort | while read f; do
  depth=$(echo "$f" | tr -cd '/' | wc -c)
  indent=$(printf '%*s' $((depth * 2)) '')
  echo "${indent}${f}"
done

# Layouts without metadata
for f in $(find app -name "layout.tsx"); do
  if ! grep -q "metadata\|generateMetadata" "$f"; then
    echo "⚠️ No metadata export: $f"
  fi
done
```

---

## 3. Component Organization

### Analysis

```bash
# Component categories
echo "=== Component Distribution ==="
echo "UI primitives: $(ls components/ui/*.tsx 2>/dev/null | wc -l)"
echo "Forms: $(ls components/forms/*.tsx 2>/dev/null | wc -l)"
echo "Layouts: $(ls components/layouts/*.tsx 2>/dev/null | wc -l)"
echo "Features: $(find components -maxdepth 2 -name "*.tsx" | grep -v "ui/\|forms/\|layouts/" | wc -l)"

# Large components
echo ""
echo "=== Large Components (>150 lines) ==="
find components/ -name "*.tsx" | while read f; do
  lines=$(wc -l < "$f")
  [ "$lines" -gt 150 ] && echo "$lines lines: $f"
done | sort -rn

# High coupling (many imports)
echo ""
echo "=== High Coupling (>12 imports) ==="
find components/ -name "*.tsx" | while read f; do
  imports=$(grep -c "^import" "$f" 2>/dev/null || echo 0)
  [ "$imports" -gt 12 ] && echo "$imports imports: $f"
done | sort -rn
```

### Component Patterns

```typescript
// ✅ Good: Small, focused component
// components/ui/button.tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({ variant = 'primary', size = 'md', ...props }: ButtonProps) {
  return <button className={cn(variants[variant], sizes[size])} {...props} />
}

// ✅ Good: Compound component pattern
// components/ui/card.tsx
export function Card({ children, className }: CardProps) {
  return <div className={cn('rounded-lg border', className)}>{children}</div>
}

Card.Header = function CardHeader({ children }: { children: React.ReactNode }) {
  return <div className="p-4 border-b">{children}</div>
}

Card.Body = function CardBody({ children }: { children: React.ReactNode }) {
  return <div className="p-4">{children}</div>
}

// ❌ Bad: Giant component doing too much
// Split into smaller components
```

---

## 4. Module Boundaries

### Layer Violations

```bash
# lib/ should NOT import from components/
echo "=== Layer Violations ==="
grep -rn "from '@/components/" --include="*.ts" lib/ 2>/dev/null && echo "❌ lib/ imports components/"

# hooks/ should NOT import from components/
grep -rn "from '@/components/" --include="*.ts" hooks/ 2>/dev/null && echo "❌ hooks/ imports components/"

# components/ should NOT import from app/
grep -rn "from '@/app/" --include="*.tsx" components/ 2>/dev/null && echo "❌ components/ imports app/"

# types/ should NOT import from anywhere except types/
grep -rn "from '@/\(lib\|components\|hooks\|app\)" --include="*.ts" types/ 2>/dev/null && echo "❌ types/ has circular imports"
```

### Allowed Dependencies

```
Layer Dependency Rules:

app/ ────────────────────────────────────┐
  │ can import from                      │
  ▼                                      │
components/ ────────────────────┐        │
  │ can import from             │        │
  ▼                             │        │
hooks/ ──────────────┐          │        │
  │ can import from  │          │        │
  ▼                  ▼          ▼        ▼
lib/ ◄───────────────────────────────────
  │
  ▼
types/ (no external imports)

✅ app/ → components/, hooks/, lib/, types/
✅ components/ → hooks/, lib/, types/
✅ hooks/ → lib/, types/
✅ lib/ → types/ only
❌ lib/ → components/ (violation)
❌ types/ → anything (violation)
```

---

## 5. Dependency Analysis

### Circular Dependencies

```bash
# Detect circular dependencies
npx madge --circular --extensions ts,tsx app/ lib/ components/

# Generate dependency graph
npx madge --image deps.svg --extensions ts,tsx app/ lib/ components/

# Most depended-on files
npx madge --extensions ts,tsx app/ lib/ | \
  awk -F: '{for(i=2;i<=NF;i++) print $i}' | tr ',' '\n' | \
  sort | uniq -c | sort -rn | head -10
```

### Import Analysis

```bash
# Import style distribution
echo "=== Import Styles ==="
echo "Alias (@/): $(grep -rn "from '@/" --include="*.ts" --include="*.tsx" app/ lib/ components/ | wc -l)"
echo "Relative (../): $(grep -rn "from '\.\./" --include="*.ts" --include="*.tsx" app/ lib/ components/ | wc -l)"

# Deep relative imports (anti-pattern)
echo ""
echo "=== Deep Relative Imports ==="
grep -rn "from '\.\.\/\.\.\/\.\.\/" --include="*.ts" --include="*.tsx" app/ lib/ components/

# Barrel files
echo ""
echo "=== Barrel Files ==="
find . -name "index.ts" ! -path "*/node_modules/*" ! -path "*/.next/*"
```

---

## 6. Recommendations

### Structure Score

| Category | Weight | Score Criteria |
|----------|--------|----------------|
| Directory structure | 20% | Follows conventions |
| File organization | 20% | Proper grouping |
| Component sizes | 15% | <150 lines average |
| Layer violations | 20% | None |
| Circular deps | 15% | None |
| Import style | 10% | Consistent alias usage |

### Quick Improvements

```bash
#!/bin/bash
# create-structure.sh

# Create recommended directories
mkdir -p components/{ui,forms,layouts}
mkdir -p lib/{actions,db,auth,api,utils}
mkdir -p hooks
mkdir -p types
mkdir -p config

echo "✅ Directory structure created"
echo ""
echo "Next steps:"
echo "1. Move UI primitives to components/ui/"
echo "2. Move form components to components/forms/"
echo "3. Move shared logic to lib/"
echo "4. Move hooks to hooks/"
echo "5. Move types to types/"
```

### Migration Checklist

- [ ] Create directory structure
- [ ] Move components to appropriate directories
- [ ] Extract shared logic to lib/
- [ ] Create barrel exports (index.ts)
- [ ] Update import paths
- [ ] Fix layer violations
- [ ] Break circular dependencies
- [ ] Add README to each directory
