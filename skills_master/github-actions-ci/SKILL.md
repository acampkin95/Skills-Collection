---
name: github-actions-ci
description: Writes and reviews GitHub Actions CI/CD workflows, covering triggers, jobs and matrix builds, caching, artifacts, deploy environments and approvals, concurrency, least-privilege permissions, secrets, service containers, and runner cost control. Use when creating or fixing a .github/workflows YAML file, adding a CI pipeline, setting up matrix or reusable workflows, configuring deploy environments and approvals, hardening GITHUB_TOKEN permissions, or reducing GitHub Actions minutes.
version: "1.0.0"
---

# GitHub Actions CI/CD Skill

**Quick reference:**
- `references/reusable-workflows.md` — Composite actions, templates, job patterns
- `references/deployment-workflows.md` — Environments, approvals, rollbacks
- `references/security-hardening.md` — OIDC, Dependabot, CodeQL, supply chain

## GitHub Actions Pricing & Strategy (2026 Changes; Verify Billing)

**Verification status (checked 2026-10-12):** GitHub's December 2025 announcement of a hosted-runner price reduction effective 2026-01-01 (net decrease of up to about 39%, varying by runner size) was confirmed by secondary coverage. The self-hosted runner platform charge announced for 2026-03-01 is reported as postponed, and sources conflict. The ARM64 free-tier change could not be checked against GitHub's billing documentation, and the GitHub pricing pages were not reachable from this session. Check current billing docs before changing runner strategy or quoting savings.

| Update | Announced date | Status |
|--------|----------------|--------|
| Hosted runner price reduction | 2026-01-01 | Announced; up to about 39% net decrease, varies by runner size |
| ARM64 runner free tier | 2026-01-29 | Not verified |
| Self-hosted runner platform charge ($0.002/min) | 2026-03-01 | Conflicting reports; reported as postponed. Verify before relying on it |

**Strategy implications:**
- **Hosted runners**: Prefer `ubuntu-latest` for CI (the price reduction applies to standard runners)
- **ARM64**: Use for compatible workloads (Node.js, Python, Go) only after checking current pricing
- **Self-hosted**: Use only for specialized hardware needs or long-running jobs, and check current charges first

## Quick Navigation

| Task | Reference |
|------|-----------|
| Composite actions, reusable workflows, templates | `references/reusable-workflows.md` |
| Preview deploys, environments, approvals, rollbacks | `references/deployment-workflows.md` |
| OIDC, permissions, Dependabot, CodeQL, supply chain | `references/security-hardening.md` |

---

## Workflow Syntax Essentials

### Minimal Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

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

**Rules:** Always set explicit `permissions` (least privilege). Pin action versions (a major tag such as `@v7`, or a full commit SHA). Use `npm ci` over `npm install` (deterministic, faster). Workflow files go in `.github/workflows/*.yml`.

---

## Trigger Events

### Common Triggers

```yaml
on:
  push:
    branches: [main, "release/**"]
    paths: ["src/**", "package.json"]        # only run when these change
    paths-ignore: ["docs/**", "**.md"]       # skip for these changes
    tags: ["v*"]                             # tag pattern
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]   # default types

  workflow_dispatch:                         # manual trigger
    inputs:
      environment:
        description: "Deploy target"
        required: true
        type: choice
        options: [staging, production]

  schedule:
    - cron: "0 6 * * 1"                     # Monday 6am UTC

  workflow_call:                             # called by another workflow
    inputs:
      node-version:
        type: string
        default: "22"
    secrets:
      NPM_TOKEN:
        required: true

  release:
    types: [published]
```

Branch/path patterns support globs (`release/**`), negation (`!release/**-beta`), and tag patterns (`v*`).

---

## Jobs and Steps

### Job Structure

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    needs: lint                    # depends on lint job
    strategy:
      matrix:
        node-version: [20, 22]     # Node 20 reached end-of-life in April 2026 (Node.js release schedule; not re-verified here). Consider 22 and 24.
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm test

  deploy:
    runs-on: ubuntu-latest
    needs: [lint, test]            # depends on both
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - run: echo "Deploying..."
```

### Job Outputs

Jobs can export outputs for dependent jobs: echo "key=value" >> "$GITHUB_OUTPUT" in a step, then access via `${{ needs.job_id.outputs.key }}`. Use in `if:` conditions to control job execution. See `references/reusable-workflows.md` for detailed patterns.

---

## Matrix Strategy

### Basic Matrix

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false              # don't cancel others on failure
      max-parallel: 4               # limit concurrency
      matrix:
        node-version: [20, 22]     # Node 20 reached end-of-life in April 2026 (Node.js release schedule; not re-verified here). Consider 22 and 24.
        os: [ubuntu-latest, macos-latest]
        include:
          - node-version: 22
            os: ubuntu-latest
            coverage: true          # extra variable for this combo
        exclude:
          - node-version: 20
            os: macos-latest        # skip this combination
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
      - if: matrix.coverage
        run: npm run test:coverage
```

### Dynamic Matrix

```yaml
jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set.outputs.matrix }}
    steps:
      - id: set
        run: echo 'matrix={"package":["api","web"],"node":["20","22"]}' >> "$GITHUB_OUTPUT"

  build:
    needs: prepare
    strategy:
      matrix: ${{ fromJson(needs.prepare.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building ${{ matrix.package }} on Node ${{ matrix.node }}"
```

---

## Caching

### actions/setup-node Built-in Cache

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: npm                     # also supports yarn, pnpm
```

### Explicit Cache Control

```yaml
- uses: actions/cache@v4
  id: deps-cache
  with:
    path: |
      node_modules
      ~/.cache/Cypress
    key: deps-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      deps-${{ runner.os }}-

- if: steps.deps-cache.outputs.cache-hit != 'true'
  run: npm ci
```

### pnpm / Turborepo Caching

```yaml
- uses: pnpm/action-setup@v4
  with:
    version: 9
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: pnpm
- run: pnpm install --frozen-lockfile
- uses: actions/cache@v4                     # Turbo remote cache alternative
  with:
    path: .turbo
    key: turbo-${{ runner.os }}-${{ github.sha }}
    restore-keys: turbo-${{ runner.os }}-
```

---

## Artifacts

**Version note:** the examples use `upload-artifact@v4` and `download-artifact@v4`. A mirror of the `actions/upload-artifact` repository shows a v7 release (checked 2026-10-12). A v8 release of `download-artifact` could not be confirmed from the review environment; check the official releases pages before bumping either action, and test upload and download majors together.

### Upload and Download

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/
          retention-days: 7
          if-no-files-found: error   # fail if nothing to upload

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: dist/
      - run: ls -la dist/
```

---

## Environments and Approvals

```yaml
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - run: echo "Deploy to staging"

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - run: echo "Deploy to production"
```

Configure approval rules in **Settings > Environments > production > Required reviewers**.

---

## Concurrency Groups

```yaml
# Cancel in-progress runs for same branch
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# Per-environment concurrency (don't cancel deploys)
jobs:
  deploy:
    concurrency:
      group: deploy-production
      cancel-in-progress: false
```

**Rules:** Use `cancel-in-progress: true` for CI (save minutes), `false` for deploys (prevent partial deploys).

---

## Permissions (GITHUB_TOKEN)

```yaml
# Workflow-level: restrictive default
permissions:
  contents: read

jobs:
  release:
    permissions:
      contents: write          # create releases
      packages: write          # push to GHCR
      id-token: write          # OIDC for cloud deploys
    runs-on: ubuntu-latest
    steps:
      - run: echo "Releasing..."
```

| Permission | Use Case |
|-----------|----------|
| `contents: read/write` | Checkout code / create releases, push tags |
| `packages: write` | Push to GitHub Container Registry |
| `pull-requests: write` | Post PR comments, add labels |
| `id-token: write` | OIDC authentication to cloud providers |
| `security-events: write` | Upload CodeQL/SARIF results |

---

## Conditional Execution

```yaml
steps:
  - if: github.ref == 'refs/heads/main'            # main branch only
    run: npm run deploy
  - if: github.event_name == 'pull_request'         # PRs only
    run: npm run preview
  - if: startsWith(github.ref, 'refs/tags/v')       # tag pushes
    run: npm run release
  - if: github.actor != 'dependabot[bot]'           # skip Dependabot
    run: npm run e2e
  - if: always()                                     # run even if prior steps failed
    run: npm run cleanup
  - if: failure()                                    # run only on failure
    run: echo "Something failed"
  - run: npm run lint
    continue-on-error: true                          # don't fail the job
```

### Path-Based Conditional (Monorepo)

```yaml
  - uses: dorny/paths-filter@v3
    id: changes
    with:
      filters: |
        backend:
          - 'src/api/**'
  - if: steps.changes.outputs.backend == 'true'
    run: npm run test:api
```

---

## Secrets Management

- **Never echo secrets** — Use env vars, not `if:` conditions (logged to logs)
- **Environment-scoped:** Store per-env credentials in Settings > Environments > Secrets
- **Config vs secrets:** Use `${{ vars.API_URL }}` for public config, `${{ secrets.KEY }}` for credentials
- **Idempotency keys:** Pass secrets in request body/headers, not as action inputs

---

## Services (Databases, Redis)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7
        ports: ["6379:6379"]
    env:
      DATABASE_URL: postgresql://test:test@localhost:5432/testdb
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test
```

---

## Cost Optimization (2026 Pricing)

| Technique | Savings |
|-----------|---------|
| Use `ubuntu-latest` (hosted runner price reduction announced for 2026-01-01) | Large savings vs macOS |
| Use ARM64 runners for compatible workloads | Check current ARM64 pricing first (not verified) |
| `cancel-in-progress: true` on CI jobs | Stop paying for superseded runs |
| Use `paths` / `paths-ignore` filters | Skip irrelevant workflows entirely |
| Cache `node_modules`, `.turbo`, build outputs | Cut install/build time 50-80% |
| `fail-fast: true` on matrix (default) | Stop early on first failure |
| Combine lint + typecheck in one job | Fewer job boots (45s overhead each) |
| Use larger runners for parallelizable work | Faster = fewer billed minutes |
| Split unit tests from slow E2E tests | Run E2E only on main or nightly |
| Use `dorny/paths-filter` to skip unchanged packages | Monorepo cost control |
| **Avoid unnecessary self-hosted runners** | Self-hosted charge status is conflicting (see pricing note); check billing |

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `permissions` not set (defaults to `write-all`) | Always set explicit `permissions` block |
| Using `actions/checkout@main` (mutable tag) | Pin to a major tag such as `@v7`, or a SHA, for supply chain security |
| `npm install` in CI | Use `npm ci` (faster, deterministic) |
| Secrets in `if:` conditions | Secrets in conditions are logged; use step outputs |
| Missing `concurrency` on PRs | Wastes minutes on superseded pushes |
| `cancel-in-progress: true` on deploys | Can leave partial deployments; use `false` for deploys |
| Hardcoded Node version in every workflow | Use reusable workflow or matrix |
| Not using `--frozen-lockfile` (pnpm) / `ci` (npm) | Leads to non-reproducible builds |
| Missing service health checks | Jobs fail with "connection refused" |
| Large artifacts without `retention-days` | Eat storage quota (default is 90 days) |
| `continue-on-error` hiding real failures | Use sparingly; prefer `if: failure()` for cleanup |
| Forgetting `fetch-depth: 0` for git history | Needed for changelogs, `git describe`, monorepo tools |
| Using self-hosted runners unnecessarily | Check current self-hosted runner billing before choosing runners |
