# Workflow: Create Custom Rules

<required_reading>
**Read these reference files:**
1. references/tool-configs.md
2. references/best-practices.md
3. references/eslint-biome.md (for JavaScript/TypeScript)
4. references/ruff-python.md (for Python)
</required_reading>

<process>
## Step 1: Identify Custom Rule Needs

Common reasons for custom rules:
- Project-specific conventions (naming, file structure)
- Business logic patterns (security, data handling)
- Team preferences (beyond standard style guides)
- Framework-specific patterns (React hooks, Vue composables)

Document what you need:
```markdown
## Custom Quality Rules

### Naming Conventions
- Component files must use PascalCase
- Utility files must use camelCase
- Constants must use SCREAMING_SNAKE_CASE

### Import Rules
- Absolute imports for src/
- Relative imports within same module only
- No circular dependencies

### Security Rules
- No console.log in production code
- API keys must use environment variables
- Database queries must use parameterized statements
```

## Step 2: Configure Custom Rules in Existing Tools

### Biome Custom Rules (JavaScript/TypeScript)

Edit `biome.json`:
```json
{
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,

      "style": {
        "useNamingConvention": {
          "level": "error",
          "options": {
            "strictCase": false,
            "conventions": [
              {
                "selector": {
                  "kind": "classMember",
                  "modifiers": ["private"]
                },
                "formats": ["camelCase"],
                "requiresPrefix": ["_"]
              },
              {
                "selector": {
                  "kind": "const"
                },
                "match": "^[A-Z][A-Z0-9_]*$"
              }
            ]
          }
        }
      },

      "suspicious": {
        "noConsoleLog": "error",
        "noExplicitAny": "warn"
      },

      "complexity": {
        "noExcessiveCognitiveComplexity": {
          "level": "warn",
          "options": {
            "maxComplexity": 15
          }
        }
      }
    }
  },

  "overrides": [
    {
      "include": ["*.test.ts", "*.spec.ts"],
      "linter": {
        "rules": {
          "suspicious": {
            "noExplicitAny": "off"
          }
        }
      }
    }
  ]
}
```

### ESLint Custom Rules

Create/edit `.eslintrc.js`:
```javascript
module.exports = {
  extends: ['eslint:recommended'],
  rules: {
    // Custom naming conventions
    'camelcase': ['error', {
      'properties': 'never',
      'ignoreDestructuring': true
    }],

    // No console in production
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',

    // Complexity limits
    'complexity': ['warn', 15],
    'max-depth': ['error', 4],
    'max-lines-per-function': ['warn', 100],

    // Import rules
    'import/no-cycle': 'error',
    'import/order': ['error', {
      'groups': ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
      'alphabetize': {'order': 'asc'}
    }],

    // React-specific
    'react/prop-types': 'off', // Using TypeScript
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn'
  },

  overrides: [
    {
      files: ['*.test.ts', '*.spec.ts'],
      rules: {
        'max-lines-per-function': 'off'
      }
    }
  ]
};
```

### Ruff Custom Rules (Python)

Edit `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
# Enable specific rule sets
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "C90",  # mccabe complexity
    "DTZ",  # flake8-datetimez
    "RUF",  # Ruff-specific rules
]

# Custom ignore patterns
ignore = [
    "E501",  # line too long (handled by formatter)
]

# Per-file customization
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # Allow assert in tests
"__init__.py" = ["F401"]    # Allow unused imports

# Naming conventions
[tool.ruff.lint.pep8-naming]
classmethod-decorators = ["classmethod", "validator"]

# Complexity
[tool.ruff.lint.mccabe]
max-complexity = 15

# Import sorting
[tool.ruff.lint.isort]
known-first-party = ["myapp"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
```

## Step 3: Create Custom ESLint Plugin (Advanced)

For truly custom rules, create an ESLint plugin:

### Project Structure
```
eslint-plugin-myproject/
├── package.json
├── index.js
└── rules/
    └── no-direct-db-access.js
```

### Example Custom Rule

`rules/no-direct-db-access.js`:
```javascript
module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow direct database access outside repository layer',
      category: 'Best Practices',
    },
    messages: {
      directDbAccess: 'Direct database access not allowed. Use repository layer instead.',
    },
  },

  create(context) {
    return {
      CallExpression(node) {
        const callee = node.callee;

        // Check for direct db.query() calls
        if (
          callee.type === 'MemberExpression' &&
          callee.object.name === 'db' &&
          callee.property.name === 'query'
        ) {
          const filename = context.getFilename();

          // Allow only in repository files
          if (!filename.includes('/repositories/')) {
            context.report({
              node,
              messageId: 'directDbAccess',
            });
          }
        }
      },
    };
  },
};
```

`index.js`:
```javascript
module.exports = {
  rules: {
    'no-direct-db-access': require('./rules/no-direct-db-access'),
  },
};
```

Use in `.eslintrc.js`:
```javascript
module.exports = {
  plugins: ['myproject'],
  rules: {
    'myproject/no-direct-db-access': 'error',
  },
};
```

## Step 4: Create Custom Ruff Plugin (Advanced)

For Python, create custom Ruff checks using AST:

```python
# custom_checks.py
import ast
from typing import Any

class NoDirectDatabaseAccess(ast.NodeVisitor):
    """Check for direct database access outside repositories."""

    def __init__(self, filename: str):
        self.filename = filename
        self.errors = []

    def visit_Call(self, node: ast.Call) -> Any:
        # Check for db.execute() or db.query()
        if isinstance(node.func, ast.Attribute):
            if (
                isinstance(node.func.value, ast.Name) and
                node.func.value.id == 'db' and
                node.func.attr in ('execute', 'query')
            ):
                if '/repositories/' not in self.filename:
                    self.errors.append({
                        'line': node.lineno,
                        'message': 'Direct database access not allowed outside repositories',
                    })

        self.generic_visit(node)
```

## Step 5: Document Custom Rules

Create `QUALITY_RULES.md`:
```markdown
# Project Quality Rules

## Custom Rules

### Naming Conventions

- **Components**: PascalCase (e.g., `UserProfile.tsx`)
- **Utilities**: camelCase (e.g., `formatDate.ts`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `API_BASE_URL`)

### Architecture Rules

#### Database Access
- ❌ Direct `db.query()` calls outside `/repositories/`
- ✅ Use repository pattern

```typescript
// Bad
const users = await db.query('SELECT * FROM users');

// Good
const users = await userRepository.findAll();
```

#### API Routes
- ❌ Business logic in route handlers
- ✅ Move logic to service layer

### Security Rules

#### Environment Variables
- ❌ Hardcoded API keys
- ✅ Use environment variables

```typescript
// Bad
const apiKey = 'sk_live_12345';

// Good
const apiKey = process.env.STRIPE_API_KEY;
```

## Exceptions

### When to Disable Rules

Use `eslint-disable-next-line` or `ruff: noqa` only when:
1. External library forces violation
2. Performance-critical code requires exception
3. Type system limitation

Always include comment explaining WHY:
```typescript
// eslint-disable-next-line @typescript-eslint/no-explicit-any
// External API returns untyped data
const result: any = await legacyApi.fetch();
```

## Enforcement

- **Pre-commit**: Rules checked locally
- **CI/CD**: Rules must pass before merge
- **Review**: Code reviewers verify exceptions are justified
```

## Step 6: Team Communication

Announce custom rules to team:
```markdown
## New Quality Rules

We've added custom quality rules to enforce project conventions:

### What's New
- No direct database access outside repositories
- Enforced naming conventions
- Complexity limits (max 15 cyclomatic complexity)

### How to Check
```bash
npm run lint  # or make lint
```

### Auto-fix
Many issues can be auto-fixed:
```bash
npm run lint:fix
```

### Questions?
See QUALITY_RULES.md for detailed explanations and examples.
```

## Step 7: Iterate Based on Feedback

Monitor rule effectiveness:
- Are rules catching real issues?
- Are there too many false positives?
- Are developers disabling rules frequently?

Adjust configuration based on real usage:
- Convert errors to warnings if too strict
- Add exceptions for valid use cases
- Remove rules that don't add value
</process>

<success_criteria>
Custom quality rules are properly implemented when:
- [ ] Rules documented with clear reasoning
- [ ] Configuration added to Biome/ESLint/Ruff config
- [ ] Custom plugins created if needed (for complex rules)
- [ ] Examples provided for correct and incorrect patterns
- [ ] Exceptions process documented
- [ ] Team notified and trained on new rules
- [ ] Rules tested on real codebase
- [ ] Feedback loop established for adjustments
</success_criteria>
