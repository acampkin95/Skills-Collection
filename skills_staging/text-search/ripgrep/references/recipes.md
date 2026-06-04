# Ripgrep Recipes — Extended Reference

## Table of Contents

1. [TypeScript / JavaScript](#typescript--javascript)
2. [Python](#python)
3. [Next.js / React](#nextjs--react)
4. [Docker & Infrastructure](#docker--infrastructure)
5. [Git Integration](#git-integration)
6. [Data & CSV Processing](#data--csv-processing)
7. [Security Scanning](#security-scanning)
8. [Refactoring Workflows](#refactoring-workflows)
9. [Pipeline Patterns](#pipeline-patterns)
10. [Debugging & Diagnostics](#debugging--diagnostics)

---

## TypeScript / JavaScript

### Finding Definitions

```bash
# Function declarations and expressions
rg '(export\s+)?(async\s+)?function\s+(\w+)' -t ts

# Arrow function assignments
rg '(export\s+)?(const|let|var)\s+(\w+)\s*=\s*(async\s+)?\(' -t ts

# Class definitions
rg 'class\s+\w+(\s+extends\s+\w+)?(\s+implements\s+\w+)?' -t ts

# Interface and type definitions
rg '(export\s+)?(interface|type)\s+\w+' -t ts

# Enum definitions
rg 'enum\s+\w+' -t ts
```

### Import/Export Analysis

```bash
# All imports from a specific package
rg "from\s+['\"]react['\"]" -t ts
rg "from\s+['\"]@/components" -t ts

# Default exports
rg 'export default' -t ts

# Named exports
rg 'export\s+(const|function|class|interface|type|enum)\s+\w+' -t ts

# Re-exports
rg "export\s+\{.*\}\s+from" -t ts
rg "export\s+\*\s+from" -t ts

# Dynamic imports
rg "import\(['\"]" -t ts

# Require statements (CJS)
rg "require\(['\"]" -t js
```

### Finding Issues

```bash
# Console statements (for cleanup)
rg 'console\.(log|warn|error|debug|info|trace|dir)' -t ts

# Debugger statements
rg '\bdebugger\b' -t ts

# Any type usage
rg ':\s*any\b|as\s+any\b|<any>' -t ts

# Type assertions (potential code smell)
rg 'as\s+\w+[^=]|(<\w+>)(?!.*=>)' -t ts

# Non-null assertions
rg '\w+!' -t ts

# Disabled eslint rules
rg 'eslint-disable' -t ts -t js

# ts-ignore / ts-expect-error
rg '@ts-(ignore|expect-error|nocheck)' -t ts
```

---

## Python

### Finding Definitions

```bash
# Functions (including async)
rg '(async\s+)?def\s+\w+' -t py

# Classes with inheritance
rg 'class\s+\w+\(.*\):' -t py

# Decorators
rg '@\w+(\.\w+)*(\(.*\))?' -t py

# Global variables and constants
rg '^[A-Z_]+\s*=' -t py
```

### Import Analysis

```bash
# All imports
rg '^(from\s+\S+\s+)?import\s+' -t py

# Specific module imports
rg 'from\s+django' -t py
rg 'import\s+pandas|from\s+pandas' -t py

# Relative imports
rg 'from\s+\.\w*\s+import' -t py

# Star imports (code smell)
rg 'from\s+\S+\s+import\s+\*' -t py
```

### Finding Issues

```bash
# Bare except clauses
rg 'except\s*:' -t py

# Print statements (should be logging)
rg '\bprint\s*\(' -t py

# Mutable default arguments
rg 'def\s+\w+\(.*=\s*(\[\]|\{\}|set\(\))' -t py

# TODO/FIXME in Python
rg '#\s*(TODO|FIXME|HACK|XXX)' -t py

# Assert statements (removed with -O flag)
rg '^\s*assert\s+' -t py

# Hardcoded credentials
rg '(password|secret|token|api_key)\s*=\s*["\x27][^"\x27]+["\x27]' -t py -i
```

---

## Next.js / React

### Component Patterns

```bash
# Client components
rg "^['\"]use client['\"]" -t ts -l

# Server components (files without 'use client')
rg --files -t tsx | xargs rg -L "use client"

# Server actions
rg "^['\"]use server['\"]" -t ts -l

# Hook usage per file (complexity indicator)
rg -c 'use[A-Z]\w+\(' -t tsx | sort -t: -k2 -rn | head -20

# Custom hooks
rg 'export\s+(default\s+)?function\s+use[A-Z]\w+' -t ts

# Suspense boundaries
rg '<Suspense' -t tsx

# Error boundaries
rg 'class\s+\w+\s+extends.*ErrorBoundary|error\.(ts|js)x?' -t ts
```

### Next.js Specific

```bash
# Route handlers
rg 'export\s+(async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)' -t ts

# Page components
rg --files -g '**/page.{ts,tsx,js,jsx}'

# Layout components
rg --files -g '**/layout.{ts,tsx,js,jsx}'

# Loading states
rg --files -g '**/loading.{ts,tsx,js,jsx}'

# Middleware
rg --files -g 'middleware.{ts,js}'

# Server component data fetching
rg 'async\s+function\s+\w+.*\{' -g '**/page.tsx'

# Metadata exports
rg 'export\s+(const|async\s+function)\s+(metadata|generateMetadata)' -t ts

# Dynamic route params
rg --files -g '**/*\[*\]*'

# Revalidation settings
rg 'revalidate\s*=' -t ts
rg 'revalidatePath|revalidateTag' -t ts

# Image optimisation
rg "from ['\"]next/image['\"]" -t ts
rg '<img\s' -t tsx  # Unoptimised images
```

### State Management

```bash
# Zustand stores
rg 'create\(' -g '*store*' -t ts

# Redux usage
rg 'useSelector|useDispatch|createSlice' -t ts

# Context providers
rg 'createContext|useContext' -t ts

# React Query usage
rg 'useQuery|useMutation|useInfiniteQuery' -t ts
```

---

## Docker & Infrastructure

```bash
# Exposed ports
rg 'EXPOSE\s+\d+' -g 'Dockerfile*'

# Environment variables in Dockerfiles
rg 'ENV\s+\w+' -g 'Dockerfile*'

# Volume mounts in compose
rg 'volumes:' -A 5 -g 'docker-compose*.yml'

# Service dependencies
rg 'depends_on:' -A 5 -g 'docker-compose*.yml'

# Health checks
rg 'healthcheck:' -A 8 -g 'docker-compose*.yml' -g 'Dockerfile*'

# Find all docker-compose files
rg --files -g 'docker-compose*.{yml,yaml}'

# Terraform resources
rg 'resource\s+"[^"]+"\s+"[^"]+"' -t tf

# Kubernetes manifests
rg 'kind:\s+\w+' -g '*.{yaml,yml}' -g '!node_modules'
```

---

## Git Integration

```bash
# Search only tracked files
git ls-files | xargs rg 'pattern'

# Search only modified files
git diff --name-only | xargs rg 'pattern'

# Search only staged files
git diff --cached --name-only | xargs rg 'pattern'

# Search files changed in a branch (vs main)
git diff --name-only main...HEAD | xargs rg 'pattern'

# Search in a specific commit's tree
git show HEAD:path/to/file | rg 'pattern'

# Search across all branches for a string
git branch -a | sed 's/^..//' | xargs -I{} git grep 'pattern' {} -- '*.ts'

# Find files that were deleted but contained a pattern
git log --all --full-history -- '*.ts' | rg 'delete mode'

# Search commit messages
git log --oneline | rg 'pattern'
```

---

## Data & CSV Processing

```bash
# Search CSV for values in specific columns (rough — for exact column work, use awk/csvkit)
rg '^[^,]*,[^,]*,target_value' data.csv

# Find rows with empty fields
rg ',,' data.csv

# Find header row
rg -m 1 '.' data.csv

# Search JSON files for keys
rg '"key_name"\s*:' -t json

# Find YAML keys
rg '^\s*key_name:' -g '*.{yaml,yml}'

# Extract all email addresses
rg -o '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' --no-filename | sort -u

# Extract all URLs
rg -o 'https?://[^\s"'"'"'`>)]+' --no-filename | sort -u

# Extract all IP addresses
rg -o '\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b' --no-filename | sort -u
```

---

## Security Scanning

```bash
# Hardcoded secrets (broad pattern)
rg -i '(api[_-]?key|secret|password|token|credential)\s*[=:]\s*["\x27][^"\x27]{8,}' \
  -g '!*.lock' -g '!package-lock.json' -g '!yarn.lock'

# AWS keys
rg 'AKIA[0-9A-Z]{16}' -g '!*.lock'

# Private keys
rg -- '-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----'

# JWT tokens
rg 'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.' -g '!*.lock'

# Connection strings
rg '(mongodb|postgres|mysql|redis)://[^\s"]+' -g '!*.lock'

# Sensitive files that shouldn't be committed
rg --files -g '*.{pem,key,p12,pfx,env,env.local}'

# eval() usage (security risk)
rg '\beval\s*\(' -t ts -t js -t py

# SQL injection vectors (parameterised queries missing)
rg 'f".*SELECT|f".*INSERT|f".*UPDATE|f".*DELETE' -t py
rg '`.*\$\{.*SELECT|`.*\$\{.*INSERT' -t ts

# Dangerous HTML rendering
rg 'dangerouslySetInnerHTML|v-html|innerHTML\s*=' -t ts -t js
```

---

## Refactoring Workflows

### Rename Symbol Across Codebase

```bash
# Step 1: Find all occurrences
rg -w 'OldName' -t ts --stats

# Step 2: Preview the change
rg -w 'OldName' -t ts --replace 'NewName'

# Step 3: Apply (with sed)
rg -l -w 'OldName' -t ts | xargs sed -i 's/\bOldName\b/NewName/g'

# Step 4: Verify
rg -w 'OldName' -t ts  # Should return nothing
rg -w 'NewName' -t ts  # Should show all new occurrences
```

### Find Dead Code

```bash
# Find exported functions
rg -o 'export (const|function|class) (\w+)' -r '$2' -t ts --no-filename | sort -u > /tmp/exports.txt

# Check each for imports (basic dead code detection)
while IFS= read -r name; do
  imports=$(rg -c "import.*\b${name}\b|from.*\b${name}\b" -t ts 2>/dev/null | awk -F: '{s+=$NF}END{print s+0}')
  usages=$(rg -c "\b${name}\b" -t ts 2>/dev/null | awk -F: '{s+=$NF}END{print s+0}')
  # If only 1 usage (the export itself) and 0 imports, likely dead
  [ "$imports" -eq 0 ] && [ "$usages" -le 1 ] && echo "Dead: $name"
done < /tmp/exports.txt
```

### Migration Patterns

```bash
# Find deprecated API usage
rg 'getStaticProps|getServerSideProps|getInitialProps' -t ts  # Next.js pages → app router

# Find class components (React modernisation)
rg 'extends\s+(React\.)?(Component|PureComponent)' -t tsx

# Find callback refs (modernise to useRef)
rg 'ref=\{?\(' -t tsx

# Find legacy lifecycle methods
rg 'componentDidMount|componentWillUnmount|componentDidUpdate|UNSAFE_' -t tsx
```

---

## Pipeline Patterns

### Progressive Filtering

When you need to narrow results through multiple criteria:

```bash
# Find TypeScript files with both useState and useEffect
rg -l 'useState' -t tsx | xargs rg -l 'useEffect'

# Find error handling that doesn't log
rg -l 'catch\s*\(' -t ts | xargs rg -L 'console\.(error|warn)|logger\.'

# Files with more than N matches (complexity indicator)
rg -c 'TODO' -t ts | awk -F: '$NF > 3' | sort -t: -k2 -rn
```

### Structured Output

```bash
# JSON output for programmatic processing
rg --json 'pattern' | python3 -c "
import json, sys
for line in sys.stdin:
    obj = json.loads(line)
    if obj['type'] == 'match':
        data = obj['data']
        print(f\"{data['path']['text']}:{data['line_number']}: {data['lines']['text'].strip()}\")
"

# CSV-formatted output
rg -n 'pattern' --no-heading | sed 's/:/ , /' | sed 's/:/ , /'

# Group by file with counts
rg -c 'pattern' | sort -t: -k2 -rn
```

### Batch Processing

```bash
# Process search results with parallel
rg -l 'pattern' | parallel 'process_file {}'

# Apply transformation to all matching files
rg -l 'old_import' -t ts | while read -r f; do
  sed -i 's|old_import|new_import|g' "$f"
  echo "Updated: $f"
done

# Generate report from search results
{
  echo "# Search Report: $(date -I)"
  echo ""
  echo "## Files with pattern"
  rg -c 'pattern' | while IFS=: read -r file count; do
    echo "- **$file**: $count matches"
  done
} > report.md
```

---

## Debugging & Diagnostics

```bash
# Why isn't a file being searched?
rg --debug 'pattern' path/to/file 2>&1 | rg 'DEBUG'

# List all files rg would search
rg --files path/ | wc -l

# Show which ignore rules apply
rg --debug 'pattern' 2>&1 | rg 'ignore'

# Force search a specific file that's being ignored
rg 'pattern' path/to/ignored/file  # Explicit paths override ignore rules

# Test regex without searching files
echo "test string" | rg 'pattern'

# Benchmark a search
time rg --stats 'pattern' > /dev/null
```
