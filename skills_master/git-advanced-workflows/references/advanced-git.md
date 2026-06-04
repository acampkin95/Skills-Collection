# Advanced Git Techniques

## Git Bisect — Binary Search for Bugs

### Manual Bisect

```bash
# Start bisect session
git bisect start

# Current commit is broken
git bisect bad

# This tag/commit was working
git bisect good v2.0.0

# Git checks out the midpoint — test, then mark:
git bisect good  # This commit is fine
# or
git bisect bad   # This commit has the bug

# Continue until Git finds the first bad commit
# "abc1234 is the first bad commit"

# Done — return to original branch
git bisect reset
```

### Automated Bisect

```bash
# Bisect with test command (exit 0 = good, non-zero = bad)
git bisect start HEAD v2.0.0
git bisect run npm test

# With specific test
git bisect run npx jest --testPathPattern="auth.test"

# With custom script
git bisect run bash -c '
  npm run build 2>/dev/null && node -e "
    const { validateToken } = require(\"./dist\");
    const result = validateToken(\"test-token\");
    process.exit(result ? 0 : 1);
  "
'

# Skip commits that can't be tested (exit code 125)
git bisect run bash -c '
  npm run build 2>/dev/null || exit 125  # Skip if build fails
  npm test || exit 1
'
```

### Bisect with Terms

```bash
# Custom terms instead of good/bad
git bisect start --term-old=slow --term-new=fast
git bisect fast  # Current is fast
git bisect slow v1.0  # v1.0 was slow
# Finds the commit that made things fast
```

## Git Reflog — Recovery

```bash
# Show HEAD movement history
git reflog
# a1b2c3d HEAD@{0}: commit: feat: add auth
# e4f5g6h HEAD@{1}: checkout: moving from main to feature
# i7j8k9l HEAD@{2}: reset: moving to HEAD~3

# Show branch-specific reflog
git reflog show feature/auth

# Recover from accidental hard reset
git reset --hard HEAD~5   # Oops!
git reflog                 # Find the commit before reset
git reset --hard HEAD@{1}  # Go back

# Recover deleted branch
git branch -D feature/important   # Oops!
git reflog | grep "feature/important"
# a1b2c3d HEAD@{5}: commit: last commit on feature/important
git checkout -b feature/important a1b2c3d

# Recover dropped stash
git stash drop   # Oops!
git fsck --no-reflogs --unreachable | grep commit
# Find the stash commit and:
git stash apply <sha>

# Reflog expires after 90 days (30 for unreachable)
# Extend if needed:
git config gc.reflogExpire 180.days
```

## git filter-repo — History Rewriting

`git filter-repo` replaces the deprecated `git filter-branch`.

```bash
# Install
pip install git-filter-repo

# Remove a file from entire history
git filter-repo --invert-paths --path secrets.env

# Remove a directory from history
git filter-repo --invert-paths --path-glob '*.log'

# Move everything into a subdirectory (for monorepo migration)
git filter-repo --to-subdirectory-filter packages/core

# Extract a subdirectory into its own repo
git filter-repo --subdirectory-filter packages/utils

# Replace sensitive text
git filter-repo --replace-text expressions.txt
# expressions.txt format:
# literal:APIKEY123==>REDACTED
# regex:password\s*=\s*"[^"]*"==>password="REDACTED"

# Rename author
git filter-repo --mailmap mailmap.txt
# mailmap.txt:
# New Name <new@email.com> <old@email.com>
```

**Warning**: filter-repo rewrites commit SHAs. Coordinate with team before running on shared branches.

## git rerere — Reuse Recorded Resolution

Remembers how you resolved conflicts and auto-applies the same resolution.

```bash
# Enable rerere
git config rerere.enabled true

# How it works:
# 1. You resolve a merge conflict
# 2. Git records the resolution
# 3. Next time the SAME conflict appears, Git resolves it automatically

# View recorded resolutions
git rerere diff       # Show current conflict resolution
git rerere status     # Files with recorded resolutions

# Forget a resolution
git rerere forget path/to/file.ts

# Useful for:
# - Long-running feature branches that rebase frequently
# - Repeated merge conflicts in the same files
# - Testing merges without committing (git merge --no-commit)
```

## Sparse Checkout

Only check out specific directories — ideal for huge monorepos.

```bash
# Clone with sparse checkout
git clone --sparse --filter=blob:none https://github.com/org/huge-monorepo.git
cd huge-monorepo

# Check out specific directories
git sparse-checkout set packages/core packages/cli

# Add more directories later
git sparse-checkout add packages/utils

# List checked-out directories
git sparse-checkout list

# Disable (check out everything)
git sparse-checkout disable

# Cone mode (faster, directory-based patterns)
git sparse-checkout init --cone
git sparse-checkout set packages/core
```

## Shallow Clone

```bash
# Clone only recent history
git clone --depth 1 https://github.com/org/repo.git

# Clone with limited history
git clone --depth 50 https://github.com/org/repo.git

# Deepen later if needed
git fetch --deepen 100

# Convert to full clone
git fetch --unshallow

# Shallow clone specific branch
git clone --depth 1 --branch release/1.x https://github.com/org/repo.git

# Useful for CI/CD where full history isn't needed
```

## Submodules vs Subtrees

### Submodules

```bash
# Add submodule
git submodule add https://github.com/org/shared-lib.git lib/shared

# Clone repo with submodules
git clone --recurse-submodules https://github.com/org/main-repo.git

# Update submodules
git submodule update --init --recursive

# Update to latest remote
git submodule update --remote lib/shared

# Remove submodule
git submodule deinit lib/shared
git rm lib/shared
rm -rf .git/modules/lib/shared
```

### Subtrees

```bash
# Add subtree
git subtree add --prefix=lib/shared https://github.com/org/shared-lib.git main --squash

# Pull updates
git subtree pull --prefix=lib/shared https://github.com/org/shared-lib.git main --squash

# Push changes back to the subtree repo
git subtree push --prefix=lib/shared https://github.com/org/shared-lib.git main
```

### Comparison

| Feature | Submodules | Subtrees |
|---------|-----------|----------|
| Separate history | Yes | Merged into parent |
| Requires special clone | Yes (`--recurse`) | No |
| Push changes upstream | Easy | `subtree push` |
| Complexity | Higher | Lower |
| Offline access | Need init | Always available |
| CI/CD setup | More config | Just works |
| Best for | Shared libs, exact versions | Vendored deps, simpler workflow |

## Git Worktree

```bash
# List current worktrees
git worktree list

# Add worktree (existing branch)
git worktree add ../project-hotfix hotfix/critical

# Add worktree (new branch from main)
git worktree add -b feature/new-thing ../project-new main

# Remove worktree
git worktree remove ../project-hotfix

# Prune stale entries
git worktree prune

# Lock worktree (prevent pruning)
git worktree lock ../project-important --reason "Long-running experiment"
```

### Practical Patterns

```bash
# Review a PR without stashing current work
git worktree add ../review-pr-42 origin/pr/42
cd ../review-pr-42
npm install && npm test
cd ../main-project
git worktree remove ../review-pr-42

# Run tests on main while working on feature
git worktree add ../main-tests main
cd ../main-tests && npm test &
# Continue working in feature branch
```
