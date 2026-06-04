---
name: quality-control
description: Code quality control with Biome, testing, linting, formatting, type checking, pre-commit hooks, and CI/CD quality gates.
version: 2.0.0
reviewed: "2026-06-04"
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

## References

- [Biome documentation](https://biomejs.dev/reference/configuration/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Pre-commit framework](https://pre-commit.com/)
- [Jest configuration](https://jestjs.io/docs/configuration)
- [Pytest documentation](https://docs.pytest.org/)


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.