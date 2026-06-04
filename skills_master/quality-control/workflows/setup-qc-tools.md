# Workflow: Setup QC Tools

<required_reading>
**Read these reference files based on project stack:**

For JavaScript/TypeScript:
1. references/eslint-biome.md
2. references/typescript-quality.md

For Python:
1. references/ruff-python.md
2. references/python-testing.md

For all projects:
1. references/tool-configs.md
2. references/best-practices.md
3. references/pre-commit-hooks.md
</required_reading>

<process>
## Step 1: Analyze Project Stack

Determine what tools are needed:

```bash
# Check package.json for JavaScript/TypeScript
cat package.json 2>/dev/null | grep -E '"(typescript|react|vue|next)"'

# Check for Python
cat pyproject.toml setup.py requirements.txt 2>/dev/null

# Check existing QC tools
ls .eslintrc* biome.json ruff.toml .ruff.toml 2>/dev/null
```

## Step 2: Install QC Tools

### JavaScript/TypeScript Projects

**Option A: Biome (recommended for new projects)**
```bash
npm install --save-dev @biomejs/biome

# Initialize config
npx biome init
```

**Option B: ESLint + Prettier (for existing projects)**
```bash
npm install --save-dev eslint prettier eslint-config-prettier

# For TypeScript
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin

# For React
npm install --save-dev eslint-plugin-react eslint-plugin-react-hooks

# Initialize
npx eslint --init
```

### Python Projects

**Ruff (recommended - fast, comprehensive)**
```bash
pip install ruff

# Or add to pyproject.toml
# [tool.poetry.dev-dependencies]
# ruff = "^0.1.0"
```

**Additional tools if needed:**
```bash
# Type checking
pip install mypy

# Testing
pip install pytest pytest-cov
```

## Step 3: Configure Tools

### Biome Configuration

Create/edit `biome.json`:
```json
{
  "$schema": "https://biomejs.dev/schemas/1.4.1/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "complexity": {
        "noForEach": "warn"
      },
      "suspicious": {
        "noExplicitAny": "warn"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2
  }
}
```

### Ruff Configuration

Create/edit `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## Step 4: Add NPM/Make Scripts

### JavaScript/TypeScript (package.json)

```json
{
  "scripts": {
    "lint": "biome check .",
    "lint:fix": "biome check --apply .",
    "type-check": "tsc --noEmit",
    "test": "vitest run",
    "test:coverage": "vitest run --coverage",
    "quality": "npm run lint && npm run type-check && npm run test"
  }
}
```

### Python (Makefile)

```makefile
.PHONY: lint format type-check test quality

lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy src/

test:
	pytest --cov=src --cov-report=term-missing

quality: lint type-check test
	@echo "All quality checks passed!"
```

## Step 5: Setup Pre-commit Hooks

Install pre-commit framework:
```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:

### For JavaScript/TypeScript
```yaml
repos:
  - repo: local
    hooks:
      - id: biome
        name: Biome
        entry: npx biome check --apply
        language: system
        types: [javascript, typescript, jsx, tsx]
        pass_filenames: false

      - id: typescript
        name: TypeScript
        entry: npx tsc --noEmit
        language: system
        types: [typescript, tsx]
        pass_filenames: false
```

### For Python
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

Install hooks:
```bash
pre-commit install
```

## Step 6: Add Editor Integration

### VS Code Settings

Create/edit `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "quickfix.biome": "explicit",
    "source.organizeImports.biome": "explicit"
  },
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit",
      "source.fixAll": "explicit"
    }
  }
}
```

### Recommended Extensions

Add `.vscode/extensions.json`:
```json
{
  "recommendations": [
    "biomejs.biome",
    "charliermarsh.ruff",
    "ms-python.python"
  ]
}
```

## Step 7: Document QC Setup

Create `QC.md` or add to README:
```markdown
## Code Quality

### Running Checks

```bash
# JavaScript/TypeScript
npm run quality

# Python
make quality
```

### Auto-fixing Issues

```bash
# JavaScript/TypeScript
npm run lint:fix

# Python
make format
```

### Pre-commit Hooks

Quality checks run automatically before each commit. To bypass (not recommended):
```bash
git commit --no-verify
```
```

## Step 8: Initial QC Run and Baseline

Run QC on existing codebase:
```bash
# This will likely find many issues
npm run quality  # or make quality
```

**For existing codebases with many issues:**
1. Fix auto-fixable issues first: `npm run lint:fix`
2. Create baseline for manual issues: document current state
3. Set up "no new violations" policy
4. Schedule time to address existing issues incrementally
</process>

<success_criteria>
QC tools are properly set up when:
- [ ] Appropriate tools installed for project stack
- [ ] Configuration files created with sensible defaults
- [ ] NPM scripts or Makefile commands added for common operations
- [ ] Pre-commit hooks configured and installed
- [ ] Editor integration configured
- [ ] Documentation added to project
- [ ] Initial QC run completed and baseline established
- [ ] Team members know how to run and fix QC issues
</success_criteria>
