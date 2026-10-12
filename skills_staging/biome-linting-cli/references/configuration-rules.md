# Biome Configuration, Rule Groups, and Domains

Reference for advanced Biome configuration patterns, rule categories, custom rules, and suppression strategies.

## biome.json Schema

Complete configuration structure:

```json
{
  "$schema": "https://biomejs.dev/schemas/1.8.0/schema.json",

  // Version control (git integration)
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true,
    "defaultBranch": "main"
  },

  // File handling
  "files": {
    "ignore": ["node_modules", "dist", "build"],
    "ignoreUnknown": false,
    "maxSize": 1048576  // 1MB
  },

  // Formatting
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineEnding": "lf",
    "lineWidth": 100,
    "formatWithErrors": false
  },

  // Import organization
  "organizeImports": {
    "enabled": true
  },

  // Linting
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      // Rule overrides below
    }
  },

  // Language-specific settings
  "javascript": {
    "formatter": { /* ... */ },
    "organizeImports": { /* ... */ }
  },
  "typescript": {
    "formatter": { /* ... */ }
  },
  "json": {
    "formatter": { /* ... */ }
  },
  "css": {
    "formatter": { /* ... */ },
    "parser": {
      "cssModules": false,
      "allowWrongLineComments": false
    }
  }
}
```

## Rule Categories (Linter Groups)

### 1. Correctness (Prevent Bugs)

Rules that catch actual errors:

```json
{
  "linter": {
    "rules": {
      "correctness": {
        "noUnusedImports": "error",
        "noUnusedVariables": "error",
        "useExhaustiveDependencies": "warn",
        "useHookAtTopLevel": "error",
        "noConstAssign": "error",
        "noInvalidConstructorSuper": "error",
        "noInvalidRenderReturn": "error",
        "noNewSymbol": "error",
        "noUndeclaredVariables": "error",
        "noUnreachable": "error",
        "useValidRenderReturn": "warn",
        "noInvalidBuiltinInstantiation": "error"
      }
    }
  }
}
```

### 2. Style (Code Consistency)

Enforce consistent code style:

```json
{
  "linter": {
    "rules": {
      "style": {
        "useConst": "error",
        "noVar": "error",
        "useTemplate": "warn",
        "noNonNullAssertion": "warn",
        "useAsConstAssertion": "warn",
        "noNamespacedImport": "off",
        "useDefaultParameterLast": "warn",
        "useWhile": "warn",
        "useNumberNamedBitwise": "warn",
        "useSelfClosingElements": "warn"
      }
    }
  }
}
```

### 3. Suspicious (Likely Mistakes)

Detect potential bugs and suspicious patterns:

```json
{
  "linter": {
    "rules": {
      "suspicious": {
        "noExplicitAny": "warn",
        "noDoubleEquals": "error",
        "noConsole": "warn",
        "noArrayIndexKey": "warn",
        "noDeleteOperator": "warn",
        "noDuplicateElseIfBlocks": "warn",
        "noDuplicateObjectKeys": "error",
        "noDuplicateParameters": "error",
        "noEmptyInterface": "warn",
        "noImplicitAnyLet": "error",
        "noMisleadingCharacterClass": "error",
        "noRedeclare": "error",
        "noRenderReturnValue": "error",
        "noSelfAssign": "error",
        "noTypePredicateAssignment": "error",
        "useAwaitInAsyncFn": "error"
      }
    }
  }
}
```

### 4. Accessibility (a11y)

Enforce accessible HTML/JSX:

```json
{
  "linter": {
    "rules": {
      "a11y": {
        "useKeyWithClickEvents": "warn",
        "useValidAnchor": "warn",
        "useAriaProps": "error",
        "useValidAriaRole": "error",
        "useAltText": "warn",
        "useButtonType": "warn",
        "useIframeTitle": "warn",
        "useHeadingContent": "warn",
        "useHtmlLang": "warn",
        "useMediaCaption": "warn"
      }
    }
  }
}
```

### 5. Nursery (Experimental)

Newer, opt-in rules (may change):

```json
{
  "linter": {
    "rules": {
      "nursery": {
        "useSortedClasses": {
          "level": "error",
          "fix": "safe"
        },
        "useValidString": "warn",
        "useConsistentMemberAccessibility": "warn",
        "useExplicitUndefinedCheck": "warn"
      }
    }
  }
}
```

### 6. Performance

Performance optimization hints:

```json
{
  "linter": {
    "rules": {
      "performance": {
        "noDelete": "warn",
        "noReexportAll": "warn",
        "noCharacterClassInRegex": "warn"
      }
    }
  }
}
```

### 7. Security

Security-related rules:

```json
{
  "linter": {
    "rules": {
      "security": {
        "noDangerouslySetInnerHtml": "warn",
        "noDangerouslySetInnerHtmlWithChildren": "error",
        "noEval": "error"
      }
    }
  }
}
```

### 8. Complexity

Code complexity and readability:

```json
{
  "linter": {
    "rules": {
      "complexity": {
        "noForEach": "warn",
        "noNestedTernary": "warn",
        "noPyramidNesting": "warn"
      }
    }
  }
}
```

## Rule Severity Levels

```json
{
  "rules": {
    "correctness": {
      "noUnusedVariables": "off",        // Disabled
      "noUnusedImports": "warn",         // Warning (non-blocking)
      "useHookAtTopLevel": "error"       // Error (blocks on --error-on-warnings)
    }
  }
}
```

## Rule-Specific Configuration

Some rules accept additional options:

```json
{
  "linter": {
    "rules": {
      "style": {
        "useNamingConvention": {
          "level": "warn",
          "options": {
            "enforce": {
              "variableName": "camelCase",
              "functionName": "camelCase",
              "className": "PascalCase"
            }
          }
        }
      },
      "nursery": {
        "useSortedClasses": {
          "level": "error",
          "options": {
            "customFunctions": ["clsx", "cx"]
          }
        }
      }
    }
  }
}
```

## Formatter Configuration

Language-specific formatter options:

```json
{
  "formatter": {
    "enabled": true,
    "indentStyle": "space",            // or "tab"
    "indentWidth": 2,                  // Lines/spaces per indent
    "lineEnding": "lf",                // "lf", "crlf", "cr"
    "lineWidth": 100,                  // Print width for line wrapping
    "formatWithErrors": false,         // Format even if linting fails
    "attributePosition": "auto"        // JSX attribute position
  },

  "javascript": {
    "formatter": {
      "jsxQuoteStyle": "double",       // or "single"
      "quoteProperties": "asNeeded",   // or "preserve"
      "trailingCommas": "all",         // or "es5", "none"
      "semicolons": "always",          // or "asNeeded"
      "arrowParentheses": "always",    // or "asNeeded"
      "bracketSpacing": true,
      "bracketSameLine": false
    }
  },

  "typescript": {
    "formatter": {
      // Inherits from javascript
      "useSemicolons": true
    }
  },

  "json": {
    "formatter": {
      "indentWidth": 2,
      "trailingCommas": "none"
    }
  },

  "css": {
    "formatter": {
      "indentWidth": 2,
      "singleQuote": false             // Use double quotes
    }
  }
}
```

## Monorepo Configuration

Root `biome.json`:

```json
{
  "extends": ["@biomejs/biome/rules/recommended.json"],
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true
  },
  "formatter": {
    "indentStyle": "space",
    "indentWidth": 2
  },
  "linter": {
    "rules": { "recommended": true }
  }
}
```

Per-workspace override (`packages/app/biome.json`):

```json
{
  "extends": ["../../biome.json"],
  "linter": {
    "rules": {
      "suspicious": {
        "noConsole": "off"  // Allow console in this workspace
      }
    }
  }
}
```

## Suppression Comments

### Inline (specific rule)

```typescript
// biome-ignore lint/suspicious/noExplicitAny: intentional for adapter
function adapt(data: any) {
  return data;
}
```

### Line-level

```typescript
const x = 1; // biome-ignore-line style/noVar
```

### Next-line

```typescript
// biome-ignore-next-line lint/correctness/noUnusedVariables
const temporaryVariable = getData();
```

### Block-level (multiple lines)

```typescript
// biome-ignore-start
const x = 1;
const y = 2;
// biome-ignore-end
```

### File-level (entire file)

```typescript
/* biome-ignore-file: This file is auto-generated by tool X */

export const generated = { /* ... */ };
```

## Custom Lint Rules (Domains)

Biome automatically enables rules based on detected dependencies in `package.json`:

```json
{
  "linter": {
    "rules": {
      "correctness": {
        "useExhaustiveDependencies": "warn"
        // Auto-enabled if "react" is in dependencies
      }
    }
  }
}
```

Detected domains (auto-rules):

| Domain | Trigger | Rules |
|--------|---------|-------|
| React | `react` in dependencies | useExhaustiveDependencies, useHookAtTopLevel |
| JSX | `react` or `preact` | noUnknownProperty, noKeyWithoutStableIdentifier |
| Next.js | `next` in dependencies | (experimental rules) |
| Vue | `vue` in dependencies | (experimental rules) |

## Import Organization

Configure import grouping:

```json
{
  "organizeImports": {
    "enabled": true
  },

  "javascript": {
    "organizeImports": {
      "enabled": true,
      "ignoreSortOrder": ["react", "next"],  // Don't reorder these
      "sortOnSave": true
    }
  }
}
```

Import order (automatic):

1. Node.js builtins (`fs`, `path`)
2. Package imports (`react`, `lodash`)
3. Relative imports (`./utils`)
4. Type imports (via `import type`)

## Performance Tuning

### Ignore Large Directories

```json
{
  "files": {
    "ignore": [
      "node_modules",
      ".next",
      "dist",
      "build",
      "coverage",
      ".git",
      ".turbo"
    ]
  }
}
```

### Parallel Processing

Biome auto-detects CPU cores. Force with environment:

```bash
RAYON_NUM_THREADS=4 biome check .
```

### Incremental Checks

Biome caches by default. Full re-check:

```bash
biome check . --no-cache
```

## Integration Examples

### With pre-commit

```bash
# .husky/pre-commit
npx biome check --write .
git add .
```

### With GitHub Actions

```yaml
- uses: biomejs/setup-biome@v2
- run: biome check --error-on-warnings .
```

### With CI/CD Pipe

```bash
biome check .                      # Check & lint
biome check --error-on-warnings .  # Fail on warnings
biome format --write .             # Format in-place
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Rule not found" | Check rule path: `correctness/noUnusedVariables` |
| Conflicting rules | Use `off` for one, increase severity on other |
| Format != Linter | Run both: `biome check` then `biome format` |
| Slow checks | Increase `files.maxSize` or use `--no-cache` to profile |

## References

- Full schema: https://biomejs.dev/reference/configuration/
- All rules: https://biomejs.dev/linter/rules/
- Formatter options: https://biomejs.dev/formatter/options/
