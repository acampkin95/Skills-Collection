# Workflow: Run QC Checks

<required_reading>
**Read these reference files based on project stack:**

For JavaScript/TypeScript projects:
1. references/eslint-biome.md
2. references/typescript-quality.md

For Python projects:
1. references/ruff-python.md
2. references/python-testing.md

For all projects:
1. references/best-practices.md
</required_reading>

<process>
## Step 1: Detect Project Stack

Analyze the project to determine which QC tools to run:

```bash
# Check for JavaScript/TypeScript
ls package.json tsconfig.json 2>/dev/null

# Check for Python
ls pyproject.toml setup.py requirements.txt 2>/dev/null

# Check for existing QC configs
ls .eslintrc* biome.json ruff.toml .ruff.toml 2>/dev/null
```

## Step 2: Run Appropriate Linters

### JavaScript/TypeScript Projects

**If Biome is configured:**
```bash
npx biome check .
```

**If ESLint is configured:**
```bash
npx eslint . --ext .js,.jsx,.ts,.tsx
```

**If TypeScript is present:**
```bash
npx tsc --noEmit
```

### Python Projects

**If Ruff is configured:**
```bash
ruff check .
```

**If other tools are configured:**
```bash
# Pylint
pylint src/

# mypy for type checking
mypy src/

# Black for formatting check
black --check .
```

## Step 3: Run Tests with Coverage

### JavaScript/TypeScript

```bash
# Jest
npm test -- --coverage

# Vitest
npx vitest run --coverage
```

### Python

```bash
# Pytest with coverage
pytest --cov=src --cov-report=term-missing

# With strict coverage threshold
pytest --cov=src --cov-fail-under=80
```

## Step 4: Aggregate and Report Results

Collect results from all checks:
- Linting errors and warnings count
- Type checking errors
- Test failures and coverage percentage
- Critical issues requiring immediate attention

Present results in priority order:
1. **Blocking issues**: Syntax errors, test failures, critical linting errors
2. **High priority**: Type errors, security warnings, low test coverage
3. **Medium priority**: Code style violations, missing docstrings
4. **Low priority**: Formatting issues (auto-fixable)

## Step 5: Provide Fix Recommendations

For each category of issues:
- Suggest auto-fix commands if available
- Provide manual fix guidance for complex issues
- Link to relevant documentation or examples
- Estimate effort (quick fix vs. refactor required)
</process>

<success_criteria>
QC checks are complete when:
- [ ] All configured linters have run successfully
- [ ] Type checking completed (if applicable)
- [ ] Tests executed with coverage report
- [ ] Results aggregated and prioritized
- [ ] Fix recommendations provided for all issues
- [ ] Critical blocking issues clearly identified
</success_criteria>
