---
name: quality-control
description: Code quality control with linting, formatting, and testing integration. Use this skill when QA, quality control, testing, test coverage, regression, smoke test, linting, code formatting, Biome, ESLint, Ruff. Use this skill when code quality gates, pre-commit hooks, CI/CD quality, type checking, automated fixes, quality standards, testing framework.
---

# Code Quality Control

Comprehensive guide for linting, formatting, type checking, and testing integration.

## Quality Control Principles

### Principle 1: Quality Gates Before Merge

Code quality checks should run automatically before code reaches main branches.

- Configure linters (Biome for JS/TS, Ruff for Python)
- Integrate testing frameworks (Jest, Pytest, Vitest)
- Set up pre-commit hooks and CI/CD quality gates
- Fix issues automatically when possible

### Principle 2: Stack-Specific Tooling

- **JavaScript/TypeScript**: Biome v2.4, ESLint, Prettier
- **Python**: Ruff 0.15.1, Black, mypy
- **Full-stack**: Combination approaches with shared configs

### Principle 3: Progressive Enforcement

1. **Baseline**: Run checks, report issues (non-blocking)
2. **Warning phase**: Block PRs with errors, allow warnings
3. **Strict**: Block all quality violations

### Principle 4: Auto-fix First, Manual Second

- Formatting: Always auto-fix
- Import sorting: Auto-fix
- Simple linting rules: Auto-fix where safe
- Complex logic issues: Manual review required

---

## Modern Code Quality Tools (Feb 2026)

### Biome v2.4 (JavaScript/TypeScript)

**Released Feb 2026**: 10-25x faster than ESLint + Prettier combined, 423+ lint rules, type-aware linting, GritQL plugin engine.

```bash
# Check and fix
biome check --apply src/
biome format --write src/

# Single command for lint + format
biome check --apply .
```

**Why Biome:**
- Single tool replaces ESLint + Prettier
- 25x faster than traditional setup
- 423+ lint rules with type awareness
- Plugin engine for extensibility
- Zero configuration mode available

### Ruff 0.15.1 (Python)

**Released Feb 19, 2026**: 10-100x faster than Flake8, 800+ built-in rules, 2026 style guide support, written in Rust.

```bash
# Check and fix
ruff check --fix .

# Format code
ruff format .

# Both operations
ruff check --fix . && ruff format .
```

**What Ruff Replaces:**
- Black (formatting)
- isort (import sorting)
- pyupgrade (syntax modernization)
- flake8 (linting) — 800+ rules now built-in
- pylint (style checking)

---

## Modern Tooling Comparison

| Tool | Language | Speed | Replaces | Rules |
|------|----------|-------|----------|-------|
| **Biome v2.4** | JS/TS | 25x ESLint | ESLint + Prettier | 423+ (type-aware) |
| **Ruff 0.15.1** | Python | 10-100x Flake8 | Black + isort + flake8 | 800+ |
| **ESLint** | JS/TS | Baseline | - | 200+ |
| **Prettier** | Multi | Baseline | - | - |

---

## Setup Patterns

### Biome Configuration (biome.json)

```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.4/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "suspicious": {
        "noConsole": "warn"
      }
    }
  },
  "formatter": {
    "indentWidth": 2,
    "lineWidth": 100,
    "trailingComma": "es5"
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single"
    }
  }
}
```

### Ruff Configuration (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
  "E",    # pycodestyle errors
  "W",    # pycodestyle warnings
  "F",    # Pyflakes
  "I",    # isort
  "B",    # flake8-bugbear
  "UP",   # pyupgrade
]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

---

## Pre-commit Hooks Integration

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/biomejs/pre-commit
    rev: v0.2.0
    hooks:
      - id: biome-check
        args: [--apply]
      - id: biome-format

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.1
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: detect-private-key
```

Install hooks:

```bash
pre-commit install
pre-commit run --all-files  # Test all files
```

---

## Testing Integration

### Jest Configuration (JavaScript/TypeScript)

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

### Pytest Configuration (Python)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=app --cov-report=html --cov-report=term-missing"
filterwarnings = ["ignore::DeprecationWarning"]

[tool.coverage.run]
branch = true
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
```

---

## CI/CD Integration Example

### GitHub Actions Workflow

```yaml
name: Quality Control

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      # Biome check
      - run: npx biome@latest ci .

      # Tests
      - run: npm test -- --coverage

      # Type checking
      - run: npm run type-check

      # Python (if applicable)
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install ruff pytest
      - run: ruff check .
      - run: pytest
```

---

## Common Quality Issues & Fixes

| Issue | Tool | Fix |
|-------|------|-----|
| Unused imports | Biome/Ruff | Auto-fix with `--fix` |
| Inconsistent formatting | Biome/Prettier | Run `biome format --write` |
| Import ordering | Biome/Ruff | Auto-fix included |
| Missing semicolons | Biome | Auto-fix |
| Trailing whitespace | pre-commit | Auto-fix |
| Type errors | TypeScript/mypy | Manual review |
| Missing test coverage | Jest/Pytest | Write tests |
| Complexity violations | ESLint/Ruff | Refactor function |

---

## Performance Benchmarks (2026)

**Biome v2.4 Performance:**
- ESLint + Prettier: ~5,000ms
- Biome alone: ~200ms
- **Speedup: 25x**

**Ruff 0.15.1 Performance:**
- Flake8 + Black + isort: ~3,000ms
- Ruff alone: ~30-300ms (depending on rules)
- **Speedup: 10-100x**

---

## Best Practices Checklist

- [ ] Biome or ESLint configured for JavaScript/TypeScript
- [ ] Ruff or Black configured for Python
- [ ] Pre-commit hooks installed and passing
- [ ] CI/CD pipeline enforces quality gates
- [ ] Test coverage > 80%
- [ ] All auto-fixable issues addressed in CI
- [ ] Team aligned on quality standards
- [ ] Type checking enabled (TypeScript/mypy)
- [ ] No `console.log` in production code
- [ ] Linting errors block merges to main

---

## References

- [Biome documentation](https://biomejs.dev/reference/configuration/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Pre-commit framework](https://pre-commit.com/)
- [Jest configuration](https://jestjs.io/docs/configuration)
- [Pytest documentation](https://docs.pytest.org/)
