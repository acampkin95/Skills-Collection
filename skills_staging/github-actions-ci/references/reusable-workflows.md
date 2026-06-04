# Reusable Workflows & Composite Actions

## Composite Actions

A composite action bundles multiple steps into a single reusable action.

### Creating a Composite Action

```yaml
# .github/actions/setup-node-project/action.yml
name: "Setup Node Project"
description: "Checkout, install Node, install dependencies"

inputs:
  node-version:
    description: "Node.js version"
    required: false
    default: "22"
  package-manager:
    description: "Package manager (npm, pnpm, yarn)"
    required: false
    default: "pnpm"
  pnpm-version:
    description: "pnpm version"
    required: false
    default: "9"

outputs:
  cache-hit:
    description: "Whether cache was hit"
    value: ${{ steps.cache.outputs.cache-hit }}

runs:
  using: composite
  steps:
    - uses: actions/checkout@v4

    - if: inputs.package-manager == 'pnpm'
      uses: pnpm/action-setup@v4
      with:
        version: ${{ inputs.pnpm-version }}

    - uses: actions/setup-node@v4
      id: cache
      with:
        node-version: ${{ inputs.node-version }}
        cache: ${{ inputs.package-manager }}

    - shell: bash
      run: |
        if [ "${{ inputs.package-manager }}" = "pnpm" ]; then
          pnpm install --frozen-lockfile
        elif [ "${{ inputs.package-manager }}" = "yarn" ]; then
          yarn install --immutable
        else
          npm ci
        fi
```

### Using a Composite Action

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: ./.github/actions/setup-node-project
        with:
          node-version: "22"
          package-manager: pnpm
      - run: pnpm test
```

### Composite Action Rules

- `runs.using` must be `composite`
- Every `run` step must have `shell: bash` (or another shell) explicitly set
- Can reference other actions with `uses:`
- Cannot use `secrets` context — pass secrets as inputs
- Store in `.github/actions/<name>/action.yml` for local actions
- Store in a separate repo for shared actions

---

## Reusable Workflows

A reusable workflow is a full workflow called by other workflows via `workflow_call`.

### Creating a Reusable Workflow

```yaml
# .github/workflows/reusable-ci.yml
name: Reusable CI

on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: "22"
      run-e2e:
        type: boolean
        default: false
      working-directory:
        type: string
        default: "."
    secrets:
      NPM_TOKEN:
        required: false
      CODECOV_TOKEN:
        required: false
    outputs:
      build-artifact:
        description: "Name of uploaded build artifact"
        value: ${{ jobs.build.outputs.artifact-name }}

permissions:
  contents: read

jobs:
  lint-and-typecheck:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck

  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci
      - run: npm test -- --coverage
      - if: inputs.run-e2e
        run: npm run test:e2e

  build:
    needs: [lint-and-typecheck, test]
    runs-on: ubuntu-latest
    outputs:
      artifact-name: build-${{ github.sha }}
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci
      - run: npm run build
        env:
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
      - uses: actions/upload-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: ${{ inputs.working-directory }}/dist/
          retention-days: 3
```

### Calling a Reusable Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    uses: ./.github/workflows/reusable-ci.yml
    with:
      node-version: "22"
      run-e2e: ${{ github.ref == 'refs/heads/main' }}
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}

  # Or inherit all secrets
  ci-inherit:
    uses: ./.github/workflows/reusable-ci.yml
    secrets: inherit
```

### Calling from Another Repository

```yaml
jobs:
  ci:
    uses: my-org/shared-workflows/.github/workflows/node-ci.yml@v2
    with:
      node-version: "22"
    secrets: inherit
```

### Reusable Workflow Rules

- Max 4 levels of nesting (workflow calling workflow)
- Max 20 unique reusable workflows per workflow file
- `env` context is NOT available in the called workflow (pass via `inputs`)
- `secrets` must be explicitly passed or use `secrets: inherit`
- Called workflow runs in the context of the **caller** (same repo permissions)
- Cannot use `concurrency` at the caller job level for reusable workflows

---

## Composite Action vs Reusable Workflow

| Feature | Composite Action | Reusable Workflow |
|---------|-----------------|-------------------|
| Scope | Steps within a job | Entire jobs |
| Secrets access | Via inputs only | Via `secrets:` or `inherit` |
| Services | Uses caller's services | Can define own services |
| Matrix | Uses caller's matrix | Can define own matrix |
| `runs-on` | Uses caller's runner | Can specify own runner |
| Nesting | Unlimited | Max 4 levels |
| Location | `.github/actions/` or separate repo | `.github/workflows/` or separate repo |
| Use case | Shared setup steps | Shared CI/CD pipelines |

**Choose composite action** when you want to reuse a sequence of steps.
**Choose reusable workflow** when you want to reuse entire job configurations.

---

## Organization Workflow Templates

Create starter workflows for your organization.

### Template Structure

```
# In org's .github repository
.github/
├── workflow-templates/
│   ├── node-ci.yml                    # Workflow template
│   ├── node-ci.properties.json        # Template metadata
│   ├── python-ci.yml
│   └── python-ci.properties.json
```

### Template Workflow

```yaml
# .github/workflow-templates/node-ci.yml
name: Node.js CI

on:
  push:
    branches: [$default-branch]       # replaced with repo's default branch
  pull_request:
    branches: [$default-branch]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm test
```

### Template Metadata

```json
{
  "name": "Node.js CI",
  "description": "Standard Node.js CI workflow for our organization",
  "iconName": "nodejs",
  "categories": ["JavaScript", "Node.js"],
  "filePatterns": ["package.json"]
}
```

Templates appear in the **Actions > New workflow** tab for all repos in the org.

---

## Action Versioning

### Semantic Versioning for Actions

```bash
# Tag a release
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# Create/move major version tag (consumers use @v1)
git tag -fa v1 -m "Update v1 tag"
git push origin v1 --force
```

### Consuming Actions

```yaml
# By major version tag (recommended for most cases)
- uses: my-org/my-action@v1

# By exact version (most stable)
- uses: my-org/my-action@v1.2.3

# By SHA (most secure — immutable)
- uses: my-org/my-action@a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2

# By branch (not recommended for production)
- uses: my-org/my-action@main
```

### Dependabot for Action Updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
    groups:
      actions:
        patterns:
          - "*"
```

**Rules:**
- Publish actions with SemVer tags
- Always maintain a floating major version tag (`v1`, `v2`)
- Document breaking changes when bumping major version
- Pin by SHA in security-critical workflows (see `references/security-hardening.md`)
