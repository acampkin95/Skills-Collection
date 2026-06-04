# Ruff for Python Quality Control

<overview>
Ruff is an extremely fast Python linter and formatter written in Rust. It replaces Flake8, isort, Black, pyupgrade, and more - all in one tool with 10-100x better performance.
</overview>

<why_ruff>
## Why Ruff?

**Speed**: 10-100x faster than existing Python tools
**Comprehensive**: Replaces 10+ tools with one
**Compatible**: Drop-in replacement for Flake8, Black, isort
**Modern**: Built for Python 3.11+
**Maintained**: Active development, regular updates

**Replaces:**
- Flake8 (linting)
- Black (formatting)
- isort (import sorting)
- pyupgrade (Python version upgrades)
- autoflake (remove unused imports)
- pydocstyle (docstring conventions)
- And many more...
</why_ruff>

<installation>
## Installation

```bash
# Using pip
pip install ruff

# Using poetry
poetry add --group dev ruff

# Using uv (fastest)
uv pip install ruff
```
</installation>

<configuration>
## Configuration (pyproject.toml)

### Basic Configuration
```toml
[tool.ruff]
# Python version target
target-version = "py311"

# Line length (default: 88, Black compatible)
line-length = 100

# Exclude patterns
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]
```

### Comprehensive Linting Rules
```toml
[tool.ruff.lint]
# Enable rule sets
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort (import sorting)
    "N",     # pep8-naming
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "SIM",   # flake8-simplify
    "C90",   # mccabe complexity
    "DTZ",   # flake8-datetimez
    "RUF",   # Ruff-specific rules
    "S",     # flake8-bandit (security)
    "ARG",   # flake8-unused-arguments
    "PTH",   # flake8-use-pathlib
    "PL",    # Pylint rules
]

# Ignore specific rules
ignore = [
    "E501",    # line too long (handled by formatter)
    "S101",    # use of assert (OK in tests)
    "PLR0913", # too many arguments
]

# Allow autofix for specific rules
fixable = ["ALL"]
unfixable = []

# Per-file rule ignores
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",    # assert allowed in tests
    "ARG",     # unused arguments OK in fixtures
    "PLR2004", # magic values OK in tests
]
"__init__.py" = [
    "F401",    # unused imports (re-exports)
]
"migrations/**/*.py" = [
    "E501",    # long lines OK in migrations
]

# Complexity
[tool.ruff.lint.mccabe]
max-complexity = 15

# Import sorting
[tool.ruff.lint.isort]
known-first-party = ["myapp"]
section-order = [
    "future",
    "standard-library",
    "third-party",
    "first-party",
    "local-folder",
]
lines-after-imports = 2

# Naming conventions
[tool.ruff.lint.pep8-naming]
classmethod-decorators = [
    "classmethod",
    "pydantic.validator",
]
```

### Formatting Configuration
```toml
[tool.ruff.format]
# Format style (Black compatible)
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

# Docstring formatting
docstring-code-format = true
docstring-code-line-length = 72
```
</configuration>

<usage>
## Usage Commands

### Linting
```bash
# Check all files
ruff check .

# Check specific files
ruff check src/ tests/

# Auto-fix issues
ruff check --fix .

# Show all violations (no fix)
ruff check --no-fix .

# Explain a specific rule
ruff rule F401
```

### Formatting
```bash
# Format all files
ruff format .

# Check formatting without changing
ruff format --check .

# Format specific files
ruff format src/
```

### Combined (lint + format)
```bash
# Check both
ruff check . && ruff format --check .

# Fix both
ruff check --fix . && ruff format .
```

### Watch Mode
```bash
# Auto-fix on file changes
ruff check --watch .
```
</usage>

<common_rules>
## Most Important Rules

### Code Quality
- **F401**: Unused imports (auto-fixable)
- **F841**: Unused variables
- **E711**: Comparison to None should be `is None`
- **B006**: Mutable default arguments
- **SIM**: Simplification suggestions

### Security (S prefix)
- **S608**: SQL injection risk
- **S301**: Pickle usage (security risk)
- **S307**: Use of eval()
- **S104**: Binding to all interfaces

### Best Practices
- **UP**: Python version upgrades (e.g., `UP006`: use `list` instead of `typing.List`)
- **PTH**: Use `pathlib` instead of `os.path`
- **ARG**: Unused function arguments
- **RUF100**: Unused `# noqa` comments

### Type Hints (when using mypy)
- **ANN**: Missing type annotations
- **TCH**: Type checking imports
</common_rules>

<integration>
## Integration with Other Tools

### Pre-commit Hooks
`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      # Linter
      - id: ruff
        args: [--fix]
      # Formatter
      - id: ruff-format
```

### VS Code
`.vscode/settings.json`:
```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "ruff.lint.args": ["--config=pyproject.toml"]
}
```

`.vscode/extensions.json`:
```json
{
  "recommendations": [
    "charliermarsh.ruff"
  ]
}
```

### GitHub Actions
```yaml
- name: Install Ruff
  run: pip install ruff

- name: Lint with Ruff
  run: ruff check .

- name: Check formatting
  run: ruff format --check .
```

### Makefile
```makefile
.PHONY: lint format check

lint:
	ruff check .

format:
	ruff format .

lint-fix:
	ruff check --fix .

check: lint
	ruff format --check .
	@echo "All quality checks passed!"
```
</integration>

<migration>
## Migrating from Other Tools

### From Flake8
Most Flake8 rules map directly to Ruff:
- Flake8 `E501` → Ruff `E501`
- Flake8 plugins → Ruff rule sets (B, S, etc.)

Configuration conversion:
```ini
# .flake8 (old)
[flake8]
max-line-length = 100
ignore = E501,W503
```

```toml
# pyproject.toml (new)
[tool.ruff]
line-length = 100

[tool.ruff.lint]
ignore = ["E501", "W503"]
```

### From Black
Ruff format is Black-compatible by default:
```bash
# Replace
black .

# With
ruff format .
```

### From isort
Ruff's import sorting is isort-compatible:
```toml
# pyproject.toml
[tool.ruff.lint.isort]
known-first-party = ["myapp"]
# ... other isort options
```

### Complete Migration
```bash
# Remove old tools
pip uninstall flake8 black isort pyupgrade autoflake

# Install Ruff
pip install ruff

# Update pre-commit config
# Update CI/CD pipelines
# Update editor settings
```
</migration>

<fixing_common_issues>
## Fixing Common Issues

### Unused Imports (F401)
```python
# Bad
import os
import sys  # F401: Unused import

def hello():
    print("Hello")

# Good
import os

def hello():
    print("Hello")
```

Auto-fix: `ruff check --fix .`

### Mutable Default Arguments (B006)
```python
# Bad
def add_item(item, items=[]):  # B006
    items.append(item)
    return items

# Good
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Comparison to None (E711)
```python
# Bad
if value == None:  # E711
    pass

# Good
if value is None:
    pass
```

Auto-fix: `ruff check --fix .`

### Use Modern Python (UP)
```python
# Bad
from typing import List, Dict  # UP035

def process(items: List[str]) -> Dict[str, int]:
    pass

# Good
def process(items: list[str]) -> dict[str, int]:
    pass
```

Auto-fix: `ruff check --fix .`
</fixing_common_issues>

<inline_configuration>
## Inline Rule Exceptions

### Disable Single Line
```python
# ruff: noqa: E501
very_long_line_that_cant_be_broken = "..."

# Better: be specific
long_url = "https://..."  # noqa: E501
```

### Disable Entire File
```python
# ruff: noqa
# Warning: Use sparingly!
```

### Disable Block
```python
# fmt: off
matrix = [
    [1, 2, 3],
    [4, 5, 6],
]
# fmt: on
```

**Best practices:**
- Always specify which rule (`# noqa: E501`, not just `# noqa`)
- Add comment explaining WHY
- Use inline exceptions, not file-wide
- Prefer fixing the issue over disabling the rule
</inline_configuration>
