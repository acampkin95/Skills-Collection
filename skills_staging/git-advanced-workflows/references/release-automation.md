# Release Automation

## semantic-release

Fully automated version management and package publishing.

### Setup

```bash
npm install --save-dev semantic-release @semantic-release/changelog @semantic-release/git
```

### .releaserc.json

```json
{
  "branches": ["main", { "name": "beta", "prerelease": true }],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", { "changelogFile": "CHANGELOG.md" }],
    ["@semantic-release/npm", { "npmPublish": true }],
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "package.json"],
      "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
    }],
    "@semantic-release/github"
  ]
}
```

### GitHub Actions

```yaml
name: Release
on:
  push:
    branches: [main, beta]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm test
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### How It Works

```
Commit message → Analyze → Determine bump → Generate notes → Publish

fix(parser): handle edge case    → PATCH (1.0.0 → 1.0.1)
feat(auth): add OAuth            → MINOR (1.0.0 → 1.1.0)
feat!: new API                   → MAJOR (1.0.0 → 2.0.0)
docs: update readme              → No release
```

## release-please (Google)

Creates release PRs automatically. Merging the PR triggers the release.

### GitHub Actions

```yaml
name: Release Please
on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    outputs:
      release_created: ${{ steps.release.outputs.release_created }}
      tag_name: ${{ steps.release.outputs.tag_name }}
    steps:
      - uses: googleapis/release-please-action@v4
        id: release
        with:
          release-type: node
          # For monorepos:
          # config-file: release-please-config.json
          # manifest-file: .release-please-manifest.json

      - uses: actions/checkout@v4
        if: ${{ steps.release.outputs.release_created }}
      - uses: actions/setup-node@v4
        if: ${{ steps.release.outputs.release_created }}
        with:
          node-version: 20
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci && npm publish
        if: ${{ steps.release.outputs.release_created }}
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Monorepo Config (release-please-config.json)

```json
{
  "packages": {
    "packages/core": { "release-type": "node" },
    "packages/cli": { "release-type": "node" },
    "packages/utils": { "release-type": "node" }
  },
  "changelog-sections": [
    { "type": "feat", "section": "Features" },
    { "type": "fix", "section": "Bug Fixes" },
    { "type": "perf", "section": "Performance" },
    { "type": "deps", "section": "Dependencies" }
  ]
}
```

## Changesets

Best for monorepos with manual changelog entries.

### Setup

```bash
npx @changesets/cli init
# Creates .changeset/ directory
```

### Workflow

```bash
# 1. Developer creates a changeset
npx changeset
# Interactive: select packages, bump type, write summary

# Creates .changeset/fuzzy-lions-sing.md:
# ---
# "@myorg/core": minor
# "@myorg/cli": patch
# ---
#
# Added new authentication middleware with JWT support.

# 2. CI creates a "Version Packages" PR
# 3. Merging the PR bumps versions and publishes
```

### GitHub Actions

```yaml
name: Changesets
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - uses: changesets/action@v1
        with:
          publish: npx changeset publish
          version: npx changeset version
          title: 'chore: version packages'
          commit: 'chore: version packages'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## GitHub Releases API

```bash
# Create a release via gh CLI
gh release create v1.2.0 \
  --title "v1.2.0" \
  --notes "## What's Changed
- Added OAuth support (#123)
- Fixed parser bug (#456)" \
  --target main

# Upload assets
gh release upload v1.2.0 ./dist/app-linux-x64.tar.gz ./dist/app-darwin-arm64.tar.gz

# Create pre-release
gh release create v2.0.0-rc.1 --prerelease --generate-notes

# Auto-generate notes from PRs
gh release create v1.3.0 --generate-notes

# List releases
gh release list --limit 10
```

## npm Publish Automation

```yaml
# .github/workflows/npm-publish.yml
name: Publish to npm
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # For npm provenance
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm test
      - run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Comparison

| Feature | semantic-release | release-please | Changesets |
|---------|-----------------|----------------|------------|
| Automation | Fully automated | PR-based | PR-based |
| Changelog | Auto-generated | Auto-generated | Manual entries |
| Monorepo | Plugin needed | Built-in | Built-in |
| Control | Low (automated) | Medium (approve PR) | High (write entries) |
| Best for | Libraries | Google-style | Monorepos |
