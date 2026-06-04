# Quality Control Best Practices

<philosophy>
## Quality Control Philosophy

### 1. Prevention Over Detection
Configure tools to prevent bad code from being written, not just detect it after the fact.

### 2. Fast Feedback Loops
- **Editor**: Real-time linting and formatting
- **Pre-commit**: Catch issues before commit
- **CI/CD**: Final safety net before merge

### 3. Auto-fix When Safe
Automate fixes for formatting, import sorting, and simple linting rules. Reserve manual review for complex logic issues.

### 4. Progressive Enforcement
Start lenient, tighten gradually:
1. **Baseline**: Report issues, don't block
2. **Warnings**: Block errors, allow warnings
3. **Strict**: Block all violations
</philosophy>

<quality_layers>
## Layers of Quality Control

### Layer 1: Editor Integration (Real-time)
**Purpose**: Catch issues while typing

**Tools**:
- VS Code with ESLint/Biome/Ruff extensions
- Format on save
- Inline error highlighting

**Configuration**:
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit",
    "source.organizeImports": "explicit"
  }
}
```

### Layer 2: Pre-commit Hooks (Pre-commit)
**Purpose**: Prevent bad commits

**Tools**: pre-commit framework

**Benefits**:
- Catches issues before they enter git history
- Fast (only checks changed files)
- Consistent across team

**Configuration**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: quality-check
        name: Quality Check
        entry: npm run quality  # or make quality
        language: system
        pass_filenames: false
```

### Layer 3: CI/CD (Pre-merge)
**Purpose**: Final safety net, enforce on all PRs

**Tools**: GitHub Actions, GitLab CI, CircleCI

**Benefits**:
- Runs on every PR
- Blocks merge if failed
- Consistent environment

**Configuration**:
```yaml
# .github/workflows/quality.yml
on: [pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - run: npm run quality
```
</quality_layers>

<rules_of_thumb>
## Rules of Thumb

### What to Auto-fix
✅ **Always Auto-fix**:
- Formatting (indentation, line length, quotes)
- Import sorting
- Trailing whitespace
- Missing semicolons/commas

✅ **Usually Auto-fix** (review in PR):
- Unused imports
- Simple type annotations
- Variable declarations (const vs let)

❌ **Never Auto-fix** (manual review required):
- Logic changes
- Type coercion
- Function complexity
- Security issues

### Complexity Thresholds

**Cyclomatic Complexity**:
- **1-10**: Simple, easy to maintain
- **11-15**: Warning level, consider refactoring
- **16+**: Too complex, must refactor

**Lines per Function**:
- **< 50**: Good
- **50-100**: Warning
- **100+**: Refactor into smaller functions

**Function Arguments**:
- **0-3**: Good
- **4-5**: Warning
- **6+**: Consider object parameter

### Test Coverage Thresholds

**Minimum Coverage**:
- **Statements**: 80%
- **Branches**: 75%
- **Functions**: 80%
- **Lines**: 80%

**Critical Code** (payments, security, auth):
- **90%+** coverage required
- **100%** for critical paths

**Utility/Helpers**:
- **100%** coverage (easy to test)

### Security Rules (Never Disable)

These rules should NEVER be disabled:
- SQL injection checks
- XSS vulnerability checks
- Hardcoded credentials
- Eval usage
- Dangerous HTML injection

Exception: Only in test files with clear justification
</rules_of_thumb>

<configuration_strategy>
## Configuration Strategy

### Start Lenient
```toml
# pyproject.toml (initial)
[tool.ruff.lint]
select = ["E", "F"]  # Only errors and critical issues
ignore = ["E501"]    # Ignore line length for now
```

### Gradually Tighten
```toml
# pyproject.toml (week 2)
[tool.ruff.lint]
select = ["E", "F", "W", "I"]  # Add warnings and import sorting
ignore = []  # Start enforcing line length
```

### Final State
```toml
# pyproject.toml (production)
[tool.ruff.lint]
select = ["ALL"]  # All rules
ignore = [
    # Only exceptions with documented reasons
    "E501",  # Line length (handled by formatter)
]
```

### Per-File Exceptions
```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # Assert OK in tests
"migrations/**/*.py" = ["E501"]  # Long lines OK in migrations
```
</configuration_strategy>

<team_adoption>
## Team Adoption Strategy

### Phase 1: Introduction (Week 1)
1. **Setup**: Install tools, configure basics
2. **Documentation**: Add QC docs to README
3. **Training**: Team meeting on QC workflow
4. **Non-blocking**: Warnings only, no CI failures

### Phase 2: Feedback (Weeks 2-3)
1. **Collect feedback**: What's too strict? What's helpful?
2. **Adjust rules**: Fine-tune configuration
3. **Auto-fix**: Enable auto-fix for safe rules
4. **Pre-commit**: Add pre-commit hooks (optional)

### Phase 3: Enforcement (Week 4+)
1. **CI/CD**: Enable quality checks in pipeline
2. **Block merges**: Failed checks block PR merge
3. **Code review**: Quality becomes part of review
4. **Continuous improvement**: Regular config updates

### Communication Template
```markdown
## New Quality Checks

We've added automated quality checks to improve code consistency.

### What's changing
- Linting runs on all PRs
- Auto-formatting on save (optional)
- Pre-commit hooks available

### How to check locally
```bash
npm run quality  # or make quality
```

### How to fix
```bash
npm run lint:fix  # auto-fix most issues
```

### Need help?
- See QC.md for detailed docs
- Ask in #engineering channel
```
</team_adoption>

<monitoring>
## Monitoring Quality Metrics

### Key Metrics to Track

**Code Quality**:
- Linting violations over time (should decrease)
- Auto-fixable vs manual issues
- Time to fix violations

**Test Coverage**:
- Overall coverage percentage
- Coverage trend (should increase)
- Uncovered critical paths

**CI/CD**:
- Quality check pass rate
- Average check duration
- False positive rate

**Team Metrics**:
- Pre-commit hook usage
- Developer satisfaction
- Time spent on quality fixes

### Quality Dashboard
```python
# Track metrics in CI
{
    "timestamp": "2024-01-15T10:00:00Z",
    "linting_errors": 5,
    "linting_warnings": 12,
    "test_coverage": 85.2,
    "ci_duration": "45s",
    "auto_fixed": 20
}
```

### Review Regularly
- **Weekly**: Check metrics, identify trends
- **Monthly**: Review rules, adjust config
- **Quarterly**: Team retrospective on QC process
</monitoring>

<troubleshooting>
## Common Issues and Solutions

### Issue: Too Many False Positives
**Solution**: Adjust rule severity or add exceptions
```toml
[tool.ruff.lint]
ignore = ["RUF012"]  # Mutable class attributes (too strict)
```

### Issue: Checks Too Slow
**Solution**:
1. Cache node_modules / .venv in CI
2. Run checks in parallel
3. Use faster tools (Biome > ESLint, Ruff > Flake8)

### Issue: Developers Bypassing Checks
**Solution**:
1. Make checks faster
2. Add auto-fix for more rules
3. Enforce in CI (can't bypass)
4. Better documentation on why rules matter

### Issue: Merge Conflicts in Config
**Solution**:
1. One person owns QC config changes
2. Communicate config changes to team
3. Document reasoning for all changes

### Issue: Different Results Locally vs CI
**Solution**:
1. Pin tool versions in package.json / requirements.txt
2. Use same Node/Python version
3. Document required versions
</troubleshooting>
