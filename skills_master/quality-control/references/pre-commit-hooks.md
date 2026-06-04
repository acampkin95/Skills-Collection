# Pre-commit Hooks for Quality Control

<overview>
Pre-commit hooks run quality checks before commits are created. They catch issues early, before they enter version control, providing the fastest feedback loop for code quality.
</overview>

<why_pre_commit>
## Why Use Pre-commit Hooks?

**Benefits**:
- **Fast feedback**: Catch issues in seconds, not minutes (vs CI)
- **Prevent bad commits**: Issues never enter git history
- **Consistent**: Same checks for all team members
- **Efficient**: Only checks changed files
- **Educational**: Developers learn quality standards faster

**Drawbacks**:
- Adds time to commit process (usually 2-10 seconds)
- Can be bypassed with `--no-verify`
- Requires team buy-in
</why_pre_commit>

<installation>
## Installation

### Pre-commit Framework
```bash
# Using pip
pip install pre-commit

# Using homebrew (macOS)
brew install pre-commit

# Using npm
npm install --save-dev pre-commit
```

### Install Hooks
```bash
# After creating .pre-commit-config.yaml
pre-commit install

# Install for commit-msg (optional)
pre-commit install --hook-type commit-msg

# Install for pre-push (optional)
pre-commit install --hook-type pre-push
```
</installation>

<configuration>
## Configuration (.pre-commit-config.yaml)

### JavaScript/TypeScript with Biome
```yaml
repos:
  # Biome for linting and formatting
  - repo: local
    hooks:
      - id: biome-check
        name: Biome Check
        entry: npx biome check --apply
        language: system
        types: [javascript, typescript, jsx, tsx, json]
        pass_filenames: false

      - id: type-check
        name: TypeScript Check
        entry: npx tsc --noEmit
        language: system
        types: [typescript, tsx]
        pass_filenames: false
        stages: [push]  # Only on push, not every commit
```

### JavaScript/TypeScript with ESLint + Prettier
```yaml
repos:
  - repo: local
    hooks:
      - id: eslint
        name: ESLint
        entry: npx eslint --fix
        language: system
        types: [javascript, typescript, jsx, tsx]
        pass_filenames: true

      - id: prettier
        name: Prettier
        entry: npx prettier --write
        language: system
        types_or: [javascript, typescript, jsx, tsx, css, json, markdown]
        pass_filenames: true

      - id: tsc
        name: TypeScript
        entry: npx tsc --noEmit
        language: system
        types: [typescript, tsx]
        pass_filenames: false
```

### Python with Ruff
```yaml
repos:
  # Ruff - linting and formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      # Linter with auto-fix
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

      # Formatter
      - id: ruff-format

  # Type checking with mypy
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
```

### Combined JavaScript + Python Project
```yaml
repos:
  # JavaScript/TypeScript
  - repo: local
    hooks:
      - id: biome
        name: Biome
        entry: npx biome check --apply
        language: system
        types_or: [javascript, typescript, jsx, tsx, json]
        pass_filenames: false

  # Python
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # Common checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files
        args: [--maxkb=1000]
```

### Testing in Pre-commit (Optional)
```yaml
repos:
  - repo: local
    hooks:
      # Fast unit tests only
      - id: jest
        name: Jest Tests
        entry: npm test -- --bail --findRelatedTests
        language: system
        types: [javascript, typescript, jsx, tsx]
        pass_filenames: true
        stages: [push]  # Only on push

      # Python tests
      - id: pytest
        name: Pytest
        entry: pytest tests/unit --exitfirst
        language: system
        types: [python]
        pass_filenames: false
        stages: [push]
```
</configuration>

<usage>
## Usage

### Normal Workflow
```bash
# Make changes
git add .

# Commit (hooks run automatically)
git commit -m "feat: add user authentication"

# If hooks fail, fix issues and try again
git add .
git commit -m "feat: add user authentication"
```

### Bypass Hooks (Emergency Only)
```bash
# Skip pre-commit hooks
git commit --no-verify -m "emergency fix"

# Skip pre-push hooks
git push --no-verify
```

**Warning**: Only bypass in emergencies. Issues will still fail in CI.

### Run Hooks Manually
```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run biome-check --all-files

# Run on staged files only
pre-commit run
```

### Update Hook Versions
```bash
# Update to latest versions
pre-commit autoupdate

# Review changes
git diff .pre-commit-config.yaml
```
</usage>

<hook_types>
## Hook Types and When to Use

### pre-commit (Default)
**When**: Before commit is created
**Use for**: Linting, formatting, quick checks
**Speed**: Must be fast (<10 seconds)

```yaml
hooks:
  - id: lint
    stages: [commit]  # Default
```

### commit-msg
**When**: After commit message is written
**Use for**: Commit message validation

```yaml
hooks:
  - id: commitlint
    stages: [commit-msg]
```

Example commitlint:
```yaml
- repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
  rev: v9.5.0
  hooks:
    - id: commitlint
      stages: [commit-msg]
```

### pre-push
**When**: Before push to remote
**Use for**: Slower checks (tests, type checking)
**Speed**: Can be slower (up to 60 seconds)

```yaml
hooks:
  - id: test
    stages: [push]
```

### pre-merge-commit
**When**: Before merge commit
**Use for**: Additional checks on merges

```yaml
hooks:
  - id: security-scan
    stages: [pre-merge-commit]
```
</hook_types>

<optimization>
## Performance Optimization

### 1. Only Check Changed Files
```yaml
hooks:
  - id: eslint
    entry: npx eslint --fix
    pass_filenames: true  # Pass changed files only
```

### 2. Parallel Execution
```yaml
# pre-commit runs hooks in parallel by default
# No configuration needed
```

### 3. Skip Slow Checks on Commit
```yaml
hooks:
  - id: type-check
    stages: [push]  # Only on push, not every commit
```

### 4. Use Local Binaries
```yaml
repos:
  - repo: local  # Faster than remote repos
    hooks:
      - id: biome
        entry: npx biome check
        language: system  # Use local environment
```

### 5. Cache Dependencies
Pre-commit automatically caches hook environments.

### Timing Hooks
```bash
# See how long each hook takes
pre-commit run --all-files --verbose
```
</optimization>

<team_setup>
## Team Setup Guide

### Step 1: Add Configuration
Create `.pre-commit-config.yaml` and commit:
```bash
git add .pre-commit-config.yaml
git commit -m "chore: add pre-commit hooks"
git push
```

### Step 2: Team Installation
Add to project README:
```markdown
## Setup

After cloning, install pre-commit hooks:
```bash
pip install pre-commit  # or npm install
pre-commit install
```

This ensures code quality checks run before every commit.
```

### Step 3: Automated Installation
Add to `package.json` or `Makefile`:
```json
{
  "scripts": {
    "postinstall": "pre-commit install || true"
  }
}
```

Or add to setup script:
```bash
#!/bin/bash
# setup.sh

npm install
pre-commit install

echo "Setup complete! Pre-commit hooks installed."
```

### Step 4: CI Validation
Ensure CI runs the same checks:
```yaml
# .github/workflows/quality.yml
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install pre-commit
      - run: pre-commit run --all-files
```
</team_setup>

<common_hooks>
## Common Pre-commit Hooks

### General Quality
```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: check-yaml
    - id: check-json
    - id: check-merge-conflict
    - id: check-added-large-files
    - id: detect-private-key
    - id: mixed-line-ending
```

### Security
```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets
      args: [--baseline, .secrets.baseline]
```

### Documentation
```yaml
- repo: https://github.com/pre-commit/mirrors-markdownlint
  rev: v0.33.0
  hooks:
    - id: markdownlint
```

### Git
```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
    - id: no-commit-to-branch
      args: [--branch, main, --branch, production]
```
</common_hooks>

<troubleshooting>
## Troubleshooting

### Hooks Not Running
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Check installation
ls -la .git/hooks/pre-commit
```

### Hooks Failing on Clean Code
```bash
# Update hook dependencies
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall
pre-commit install --install-hooks
```

### Slow Hooks
```bash
# Identify slow hooks
pre-commit run --all-files --verbose

# Move slow checks to pre-push
# Edit .pre-commit-config.yaml
hooks:
  - id: slow-check
    stages: [push]
```

### Different Results: Local vs CI
```bash
# Run same check as CI
pre-commit run --all-files

# Ensure same versions
pre-commit autoupdate
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```
</troubleshooting>
