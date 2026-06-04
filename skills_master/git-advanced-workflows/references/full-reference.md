---
name: git-advanced-workflows
description: Advanced Git workflows with Conventional Commits, semantic versioning, and automated release pipelines. Use this skill when Conventional Commits, git bisect, semantic versioning, release automation, changelog generation, interactive rebase, cherry-pick, git worktree, branch strategy, commit message, version bump, breaking changes, git reset, commit squashing, revert strategy. Use this skill when implementing release automation pipelines, writing Conventional Commits for semantic versioning, generating changelogs automatically, debugging regressions with git bisect, managing complex branch strategies, performing interactive rebases for clean histories, cherry-picking commits across branches, recovering lost work, and managing multiple worktrees for parallel development.
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

## Changelog Generation

### Format (Keep a Changelog)

```markdown
# Changelog

## [1.2.0] - 2025-01-15

### Added
- OAuth2 PKCE authentication flow (#123)
- Cursor-based pagination for list endpoints (#456)

### Fixed
- Nested quote parsing in template engine (#789)

### Changed
- Minimum Node.js version is now 20 (#101)

### Deprecated
- `/v1/users` endpoint, use `/v2/users` (#102)

### Removed
- Legacy XML response format (#103)

### Security
- Upgrade jsonwebtoken to fix CVE-2024-XXXX (#104)
```

## Interactive Rebase Strategies

```bash
# Rebase last N commits
git rebase -i HEAD~5

# Rebase onto branch
git rebase -i main

# Autosquash (works with fixup!/squash! prefixes)
git commit --fixup=abc123
git rebase -i --autosquash main
```

### Rebase Commands

| Command | Effect |
|---------|--------|
| `pick` | Keep commit as-is |
| `reword` | Change commit message |
| `edit` | Stop to amend commit |
| `squash` | Meld into previous, keep message |
| `fixup` | Meld into previous, discard message |
| `drop` | Remove commit |
| `exec` | Run shell command |

### Common Patterns

```bash
# Squash all feature commits before merge
# In rebase editor:
pick abc1234 feat: initial implementation
fixup def5678 wip: more work
fixup ghi9012 fix: typo
reword jkl3456 feat: final version

# Split a commit
# In rebase editor, change pick to edit, then:
git reset HEAD~
git add -p          # Stage parts separately
git commit -m "feat: part 1"
git add -p
git commit -m "feat: part 2"
git rebase --continue
```

## Cherry-Pick Workflows

```bash
# Single commit
git cherry-pick abc123

# Range of commits (exclusive start)
git cherry-pick abc123..def456

# Multiple specific commits
git cherry-pick abc123 def456 ghi789

# Without committing (stage only)
git cherry-pick --no-commit abc123

# Cherry-pick merge commit (pick parent 1)
git cherry-pick -m 1 abc123

# Handle conflicts
git cherry-pick abc123
# ... fix conflicts ...
git add .
git cherry-pick --continue
# or abort:
git cherry-pick --abort
```

### Backport Pattern

```bash
git checkout release/1.x
git cherry-pick -x abc123    # -x adds "cherry picked from" note
git push origin release/1.x
```

## Stash Management

```bash
# Basic stash
git stash                     # Stash tracked changes
git stash -u                  # Include untracked files
git stash -a                  # Include ignored files
git stash push -m "WIP: auth" # Named stash

# Selective stash
git stash push -p             # Interactive: choose hunks
git stash push -- src/auth.ts # Specific files

# Apply stash
git stash pop                 # Apply + remove from list
git stash apply               # Apply but keep in list
git stash apply stash@{2}     # Apply specific stash

# Inspect
git stash list                # List all stashes
git stash show stash@{0}      # Show diffstat
git stash show -p stash@{0}   # Show full diff

# Branch from stash
git stash branch new-feature stash@{0}

# Clean up
git stash drop stash@{0}      # Remove one
git stash clear                # Remove all
```

## Worktree Usage

```bash
# Add worktree for a branch
git worktree add ../project-fix hotfix/critical-bug

# Add worktree with new branch
git worktree add -b feature/new ../project-new main

# List worktrees
git worktree list

# Remove worktree
git worktree remove ../project-fix

# Prune stale worktrees
git worktree prune
```

### Use Cases

- Review PR while keeping current work: `git worktree add ../review pr-branch`
- Run tests on another branch simultaneously
- Compare behavior between branches side-by-side

## Git Bisect (Bug Hunting)

```bash
# Start bisect
git bisect start

# Mark current as bad
git bisect bad

# Mark known good commit
git bisect good v1.0.0

# Git checks out middle commit — test it, then:
git bisect good   # or
git bisect bad

# Repeat until found, then:
git bisect reset
```

### Automated Bisect

```bash
# Run a test script automatically
git bisect start HEAD v1.0.0
git bisect run npm test

# With custom script
git bisect run bash -c 'node -e "require(\"./src\").validate()" && echo PASS'

# Exit codes: 0 = good, 1-124 = bad, 125 = skip
git bisect run ./test-regression.sh
```

## Git Reflog Recovery

```bash
# View reflog
git reflog                    # HEAD movements
git reflog show main          # Branch movements

# Recover deleted branch
git reflog | grep "feature/lost"
git checkout -b feature/recovered abc1234

# Undo hard reset
git reflog
git reset --hard HEAD@{2}

# Recover dropped stash
git fsck --no-reflogs | grep commit
git stash apply <sha>

# Reflog with dates
git reflog --date=relative
```

## Release Workflow

See [references/release-automation.md](references/release-automation.md) for semantic-release, release-please, and changesets setup.

See [references/advanced-git.md](references/advanced-git.md) for bisect, reflog, filter-repo, rerere, sparse checkout, and submodules.
