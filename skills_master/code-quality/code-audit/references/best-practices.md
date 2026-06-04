# Code Audit Best Practices

## Security Scanning Guidelines

### 1. Dependency Vulnerability Checking

```bash
# npm audit
npm audit --production

# Check for known CVEs
npm list --depth=0 | grep -v @types

# Use Snyk for comprehensive scanning
snyk test --severity-threshold=high
```

### 2. Static Analysis Rules

| Category | Tool | Purpose |
|----------|------|---------|
| Linting | ESLint/ Biome | Code style, common errors |
| Type safety | TypeScript | Type checking |
| Security | CodeQL | Deep security analysis |
| Dependencies | Snyk/ Dependabot | CVE scanning |

### 3. Performance Budgets

```json
{
  "performance": {
    "lighthouse": {
      "performance": 0.9,
      "accessibility": 0.95,
      "best-practices": 0.9,
      "seo": 0.9
    },
    "bundleSize": {
      "javascript": "500KB",
      "css": "50KB",
      "images": "1MB"
    }
  }
}
```

### 4. Automated Audit Pipeline

```yaml
# .github/workflows/audit.yml
name: Code Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: npm ci

      - name: Type check
        run: npx tsc --noEmit

      - name: Lint
        run: npm run lint

      - name: Security audit
        run: npm audit --production

      - name: Build
        run: npm run build
```

### 5. Common Issues & Fixes

| Issue | Severity | Fix |
|-------|----------|-----|
| Missing CSRF tokens | Critical | Add CSRF protection |
| Insecure direct object references | High | Implement authorization checks |
| Missing input sanitization | High | Use proper validation |
| Verbose error messages | Medium | Log errors, show generic messages |
| Insecure caching | Low | Set proper cache headers |
