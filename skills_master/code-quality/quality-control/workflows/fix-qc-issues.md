# Workflow: Fix QC Issues

<required_reading>
**Read these reference files based on what needs fixing:**

For auto-fixing:
1. references/best-practices.md

For specific stacks:
1. references/eslint-biome.md (JavaScript/TypeScript)
2. references/ruff-python.md (Python)
</required_reading>

<process>
## Step 1: Run QC Checks First

Before fixing, identify what needs fixing:
- Use the run-qc-checks workflow to get current state
- Categorize issues: auto-fixable vs. manual
- Prioritize: blocking issues first

## Step 2: Auto-Fix Safe Issues

### JavaScript/TypeScript

**Biome auto-fix:**
```bash
npx biome check --apply .
```

**ESLint auto-fix:**
```bash
npx eslint . --ext .js,.jsx,.ts,.tsx --fix
```

**Prettier formatting:**
```bash
npx prettier --write .
```

### Python

**Ruff auto-fix:**
```bash
# Fix all auto-fixable issues
ruff check --fix .

# Also format code
ruff format .
```

**Black formatting:**
```bash
black .
```

**isort for import sorting:**
```bash
isort .
```

## Step 3: Verify Auto-Fixes

After auto-fixing, verify nothing broke:

```bash
# Run tests
npm test  # or pytest

# Re-run linters to confirm fixes
npx biome check .  # or ruff check .

# Check git diff to review changes
git diff
```

**IMPORTANT**: Review auto-fixes before committing. Auto-fixers can occasionally:
- Change logic unintentionally
- Break formatting in edge cases
- Miss context-specific requirements

## Step 4: Manual Fixes for Complex Issues

For issues that can't be auto-fixed:

### Type Errors
- Add proper type annotations
- Fix type mismatches
- Add type guards where needed

### Logic Issues
- Undefined variable usage
- Unreachable code
- Missing error handling

### Security Issues
- SQL injection vulnerabilities
- XSS vulnerabilities
- Insecure dependencies

**For each manual fix:**
1. Understand the root cause
2. Fix the issue properly (don't just silence the warning)
3. Add tests to prevent regression
4. Run QC checks again to verify

## Step 5: Handle Intentional Exceptions

Sometimes rules need to be disabled for valid reasons:

### JavaScript/TypeScript

```javascript
// eslint-disable-next-line no-console
console.log('Debugging output');

// biome-ignore lint/suspicious/noExplicitAny: External API typing
const data: any = externalApi.getData();
```

### Python

```python
# ruff: noqa: E501
very_long_line = "this line is intentionally long because..."

# type: ignore[arg-type]
result = function_with_complex_typing(data)
```

**Rules for exceptions:**
- Always include a comment explaining WHY
- Be specific (disable single rule, not all rules)
- Use inline disables, not file-wide
- Document project-wide exceptions in config

## Step 6: Commit Fixes Incrementally

Don't commit all fixes at once:

```bash
# Commit auto-fixes first
git add -A
git commit -m "chore: auto-fix linting and formatting issues"

# Commit manual fixes by category
git add src/components/
git commit -m "fix: resolve type errors in components"

git add src/utils/
git commit -m "fix: add error handling to utility functions"
```

This makes fixes easier to review and revert if needed.
</process>

<success_criteria>
QC issues are resolved when:
- [ ] All auto-fixable issues have been fixed automatically
- [ ] Manual fixes completed for complex issues
- [ ] Tests pass after all fixes
- [ ] Git diff reviewed and changes are intentional
- [ ] Intentional exceptions documented with clear reasoning
- [ ] Fixes committed in logical, reviewable chunks
- [ ] QC checks now pass or only show expected exceptions
</success_criteria>
