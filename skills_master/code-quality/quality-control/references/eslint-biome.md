# ESLint and Biome for JavaScript/TypeScript

<overview>
ESLint and Biome are linting tools for JavaScript and TypeScript. Biome is newer, faster, and includes formatting. ESLint is mature with extensive plugins.
</overview>

<when_to_use>
## Choosing Between ESLint and Biome

**Use Biome when:**
- Starting a new project
- Want all-in-one tooling (linting + formatting)
- Speed is priority (Biome is 10-100x faster)
- Simple setup preferred

**Use ESLint when:**
- Existing project with ESLint configuration
- Need specific plugins (testing libraries, frameworks)
- Team familiar with ESLint ecosystem
- Gradual migration preferred

**Use Both (transition):**
- Run Biome for performance
- Keep ESLint for plugin-specific rules
- Gradually migrate custom rules to Biome
</when_to_use>

<biome_setup>
## Biome Complete Setup

### Installation
```bash
npm install --save-dev @biomejs/biome
```

### Configuration (biome.json)
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
        "noExcessiveCognitiveComplexity": "warn",
        "noForEach": "off"
      },

      "style": {
        "noNonNullAssertion": "warn",
        "useConst": "error",
        "useTemplate": "warn"
      },

      "suspicious": {
        "noExplicitAny": "warn",
        "noArrayIndexKey": "error",
        "noDoubleEquals": "error"
      },

      "correctness": {
        "noUnusedVariables": "error",
        "useExhaustiveDependencies": "warn"
      }
    }
  },

  "formatter": {
    "enabled": true,
    "formatWithErrors": false,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100,
    "lineEnding": "lf"
  },

  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "jsxQuoteStyle": "double",
      "trailingComma": "es5",
      "semicolons": "always",
      "arrowParentheses": "always",
      "bracketSpacing": true
    }
  },

  "json": {
    "formatter": {
      "enabled": true
    },
    "parser": {
      "allowComments": true
    }
  }
}
```

### NPM Scripts
```json
{
  "scripts": {
    "lint": "biome check .",
    "lint:fix": "biome check --apply .",
    "lint:unsafe": "biome check --apply-unsafe .",
    "format": "biome format --write ."
  }
}
```

### VS Code Integration
`.vscode/settings.json`:
```json
{
  "editor.defaultFormatter": "biomejs.biome",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "quickfix.biome": "explicit",
    "source.organizeImports.biome": "explicit"
  }
}
```
</biome_setup>

<eslint_setup>
## ESLint Complete Setup

### Installation
```bash
# Base
npm install --save-dev eslint

# TypeScript
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin

# React
npm install --save-dev eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-jsx-a11y

# Import rules
npm install --save-dev eslint-plugin-import

# Formatting (with Prettier)
npm install --save-dev prettier eslint-config-prettier
```

### Configuration (.eslintrc.js)
```javascript
module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
    'plugin:import/recommended',
    'plugin:import/typescript',
    'prettier', // Must be last
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
    project: './tsconfig.json',
  },
  plugins: [
    '@typescript-eslint',
    'react',
    'react-hooks',
    'jsx-a11y',
    'import',
  ],
  rules: {
    // TypeScript
    '@typescript-eslint/no-unused-vars': ['error', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
    }],
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/explicit-function-return-type': 'off',

    // React
    'react/react-in-jsx-scope': 'off', // Not needed in React 17+
    'react/prop-types': 'off', // Using TypeScript
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',

    // Imports
    'import/order': ['error', {
      groups: [
        'builtin',
        'external',
        'internal',
        'parent',
        'sibling',
        'index',
      ],
      'newlines-between': 'always',
      alphabetize: {
        order: 'asc',
      },
    }],
    'import/no-duplicates': 'error',

    // General
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
  },
  settings: {
    react: {
      version: 'detect',
    },
    'import/resolver': {
      typescript: true,
      node: true,
    },
  },
  overrides: [
    {
      files: ['*.test.ts', '*.test.tsx', '*.spec.ts', '*.spec.tsx'],
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
      },
    },
  ],
};
```

### Prettier Configuration
`.prettierrc.json`:
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

### NPM Scripts
```json
{
  "scripts": {
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```
</eslint_setup>

<comparison>
## Biome vs ESLint Comparison

| Feature | Biome | ESLint |
|---------|-------|--------|
| **Speed** | 10-100x faster | Slower |
| **Setup** | Single tool | Multiple tools (ESLint + Prettier) |
| **Formatting** | Built-in | Requires Prettier |
| **Plugins** | Limited | Extensive ecosystem |
| **Maturity** | New (2023+) | Mature (2013+) |
| **Migration** | Easy for new projects | Large existing ecosystem |
| **Configuration** | Single JSON file | Multiple config files |
| **Error Messages** | Clear, detailed | Varies by plugin |
</comparison>

<common_rules>
## Most Important Rules to Enable

### Code Quality
- `no-unused-vars` / `noUnusedVariables` - Catch dead code
- `no-console` - Prevent debug code in production
- `useExhaustiveDependencies` - React hooks safety

### Type Safety (TypeScript)
- `noExplicitAny` - Avoid `any` type
- `strictNullChecks` - Prevent null/undefined errors

### React Specific
- `rules-of-hooks` - Hooks must follow rules
- `exhaustive-deps` - useEffect dependencies complete

### Security
- `noArrayIndexKey` - Don't use array index as key
- `noDoubleEquals` - Use === instead of ==
- `noDangerouslySetInnerHtml` - Prevent XSS

### Performance
- `noForEach` - Use for...of instead (debatable)
- `noExcessiveCognitiveComplexity` - Keep functions simple
</common_rules>

<migration_guide>
## Migrating from ESLint to Biome

### Step 1: Install Biome
```bash
npm install --save-dev @biomejs/biome
npx biome init
```

### Step 2: Run Parallel (Transition)
Keep ESLint for now, add Biome:
```json
{
  "scripts": {
    "lint": "npm run lint:eslint && npm run lint:biome",
    "lint:eslint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "lint:biome": "biome check ."
  }
}
```

### Step 3: Migrate Rules
Map ESLint rules to Biome equivalents:
- `no-unused-vars` → `correctness/noUnusedVariables`
- `no-console` → `suspicious/noConsoleLog`
- `eqeqeq` → `suspicious/noDoubleEquals`

### Step 4: Remove ESLint (Final)
Once comfortable with Biome:
```bash
npm uninstall eslint prettier @typescript-eslint/parser @typescript-eslint/eslint-plugin
rm .eslintrc.js .prettierrc.json
```

Update scripts:
```json
{
  "scripts": {
    "lint": "biome check .",
    "lint:fix": "biome check --apply ."
  }
}
```
</migration_guide>
