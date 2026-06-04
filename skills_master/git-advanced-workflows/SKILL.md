---
name: git-advanced-workflows
description: Git workflows with Conventional Commits, semantic versioning, and automated releases. Use for bisect, rebase, cherry-pick, worktrees, and changelog generation.
version: 2.0.0
reviewed: "2026-06-04"
---
# Git Advanced Workflows

## Conventional Commits

Format: `<type>[optional scope]: <description>`

### Types

| Type | When | Bump |
|------|------|------|
| `feat` | New feature | MINOR |
| `fix` | Bug fix | PATCH |
| `docs` | Documentation only | none |
| `style` | Formatting, semicolons | none |
| `refactor` | Neither fix nor feature | none |
| `perf` | Performance improvement | PATCH |
| `test` | Adding/fixing tests | none |
| `build` | Build system, deps | none |
| `ci` | CI configuration | none |
| `chore` | Other changes | none |

### Breaking Changes

```
feat(api)!: remove deprecated endpoints

BREAKING CHANGE: The /v1/users endpoint has been removed.
Use /v2/users instead.
```

The `!` after scope or the `BREAKING CHANGE:` footer triggers a MAJOR version bump.

### Examples

```bash
# Feature with scope
git commit -m "feat(auth): add OAuth2 PKCE flow"

# Fix with body
git commit -m "fix(parser): handle nested quotes correctly

Previously, nested quotes would cause the parser to emit
an unterminated string error. This fix tracks quote depth."

# Multiple footers
git commit -m "feat(api): add pagination to list endpoints

Implements cursor-based pagination for all list endpoints.

Reviewed-by: Alice
Refs: #123, #456
BREAKING CHANGE: page/limit params replaced by cursor/limit"
```

## Semantic Versioning

Format: `MAJOR.MINOR.PATCH[-prerelease][+buildmeta]`

```
1.0.0        # Initial public release
1.0.1        # Patch: backward-compatible bug fix
1.1.0        # Minor: backward-compatible feature
2.0.0        # Major: breaking change
2.0.0-rc.1   # Pre-release: release candidate
2.0.0+build.42  # Build metadata (ignored in precedence)
```

### Version Bumping Rules

```
fix:    → PATCH  (1.0.0 → 1.0.1)
feat:   → MINOR  (1.0.0 → 1.1.0)
BREAKING CHANGE → MAJOR (1.0.0 → 2.0.0)
```


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.