# Security Hardening for GitHub Actions

## OIDC Tokens (OpenID Connect)

OIDC lets workflows authenticate to cloud providers without storing long-lived credentials.

### How It Works

1. Workflow requests an OIDC token from GitHub
2. Token contains claims (repo, branch, environment, actor)
3. Cloud provider validates the token against its trust policy
4. Temporary credentials are issued

### Enable OIDC

```yaml
permissions:
  id-token: write    # Required for OIDC
  contents: read
```

### AWS Trust Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

### GCP Workload Identity Pool

```bash
# Create pool
gcloud iam workload-identity-pools create "github" \
  --location="global" \
  --display-name="GitHub Actions"

# Create provider
gcloud iam workload-identity-pools providers create-oidc "my-repo" \
  --location="global" \
  --workload-identity-pool="github" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='my-org/my-repo'"

# Grant access
gcloud iam service-accounts add-iam-policy-binding deploy@my-project.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/123/locations/global/workloadIdentityPools/github/attribute.repository/my-org/my-repo"
```

**OIDC Rules:**
- Scope trust to specific repo AND branch (never `repo:*`)
- Use environment claims for production deploys
- Rotate nothing — credentials are ephemeral
- Always prefer OIDC over static secrets for cloud access

---

## Minimal Permissions

### Default to Read-Only

```yaml
# Workflow level: restrictive
permissions:
  contents: read

jobs:
  ci:
    runs-on: ubuntu-latest
    # Inherits workflow permissions
    steps:
      - uses: actions/checkout@v4
      - run: npm test

  release:
    runs-on: ubuntu-latest
    # Escalate only where needed
    permissions:
      contents: write
      packages: write
      id-token: write
    steps:
      - run: echo "Releasing..."
```

### Permission Reference

| Permission | Read | Write | When Needed |
|-----------|------|-------|-------------|
| `contents` | Checkout code | Push commits, create releases |
| `packages` | Pull images | Push to GHCR |
| `pull-requests` | Read PR info | Comment, label, merge |
| `issues` | Read issues | Create, comment, close |
| `id-token` | — | OIDC cloud auth |
| `security-events` | — | Upload SARIF (CodeQL) |
| `actions` | Read workflow info | Cancel/rerun workflows |
| `deployments` | Read deployments | Create deployments |

### Org-Level Default

In **Settings > Actions > General > Workflow permissions**, set the default to **Read repository contents and packages permissions**. Individual workflows can escalate as needed.

---

## Dependabot Configuration

### Full Dependabot Setup

```yaml
# .github/dependabot.yml
version: 2
updates:
  # NPM dependencies
  - package-ecosystem: npm
    directory: "/"
    schedule:
      interval: weekly
      day: monday
      time: "06:00"
      timezone: "Australia/Sydney"
    open-pull-requests-limit: 10
    reviewers:
      - "my-org/platform-team"
    labels:
      - "dependencies"
      - "automated"
    groups:
      dev-dependencies:
        dependency-type: development
        update-types:
          - minor
          - patch
      production-deps:
        dependency-type: production
        update-types:
          - patch
    ignore:
      - dependency-name: "aws-sdk"
        update-types: ["version-update:semver-major"]
    versioning-strategy: increase

  # GitHub Actions
  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
    groups:
      actions:
        patterns:
          - "*"

  # Docker
  - package-ecosystem: docker
    directory: "/"
    schedule:
      interval: weekly
```

### Auto-Merge Dependabot PRs

```yaml
# .github/workflows/dependabot-auto-merge.yml
name: Dependabot Auto-Merge

on: pull_request

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    if: github.actor == 'dependabot[bot]'
    runs-on: ubuntu-latest
    steps:
      - uses: dependabot/fetch-metadata@v2
        id: metadata
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

      # Auto-merge patch and minor updates
      - if: steps.metadata.outputs.update-type != 'version-update:semver-major'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Secret Scanning

### GitHub Secret Scanning

Enabled by default on public repos. Enable for private repos in **Settings > Code security > Secret scanning**.

### Push Protection

Blocks pushes that contain detected secrets. Enable in **Settings > Code security > Push protection**.

### Custom Secret Patterns

```
# Settings > Code security > Custom patterns
# Pattern: Internal API keys
(?i)my-org-api-key-[a-z0-9]{32}
```

### Preventing Secret Leaks in Workflows

```yaml
steps:
  # NEVER echo secrets
  # - run: echo ${{ secrets.API_KEY }}            # LEAKED IN LOGS

  # NEVER use secrets in if conditions
  # - if: secrets.API_KEY != ''                   # LEAKED IN LOGS

  # CORRECT: pass as environment variable
  - run: ./deploy.sh
    env:
      API_KEY: ${{ secrets.API_KEY }}

  # CORRECT: mask values
  - run: |
      echo "::add-mask::$CUSTOM_VALUE"
      echo "Using masked value"
    env:
      CUSTOM_VALUE: ${{ secrets.CUSTOM_SECRET }}
```

---

## CodeQL Analysis

### Basic CodeQL Setup

```yaml
# .github/workflows/codeql.yml
name: CodeQL

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 6 * * 1"    # Weekly scan

permissions:
  security-events: write
  contents: read

jobs:
  analyze:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        language: [javascript-typescript]
        # Also: python, java-kotlin, csharp, go, ruby, cpp, swift
    steps:
      - uses: actions/checkout@v4

      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: +security-extended,security-and-quality

      - uses: github/codeql-action/autobuild@v3

      - uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

### Custom CodeQL Config

```yaml
# .github/codeql/codeql-config.yml
name: "Custom CodeQL Config"
queries:
  - uses: security-extended
  - uses: security-and-quality
paths:
  - src/
paths-ignore:
  - src/**/*.test.ts
  - src/generated/
```

```yaml
# In workflow
- uses: github/codeql-action/init@v3
  with:
    config-file: .github/codeql/codeql-config.yml
```

---

## Supply Chain Security

### Pin Actions by SHA

```yaml
# INSECURE: mutable tag
- uses: actions/checkout@v4

# SECURE: pinned to SHA (immutable)
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

### Automated SHA Pinning

```yaml
# .github/dependabot.yml — keeps SHA pins updated
version: 2
updates:
  - package-ecosystem: github-actions
    directory: "/"
    schedule:
      interval: weekly
```

Use `step-security/harden-runner` for runtime monitoring:

```yaml
steps:
  - uses: step-security/harden-runner@v2
    with:
      egress-policy: audit    # or 'block' for strict mode
      allowed-endpoints: >
        github.com:443
        registry.npmjs.org:443
        api.github.com:443

  - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
```

### Artifact Attestations (Supply Chain Provenance)

```yaml
# Generate SLSA provenance for build artifacts
permissions:
  id-token: write
  contents: read
  attestations: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build

      - uses: actions/attest-build-provenance@v2
        with:
          subject-path: dist/
```

### Lock File Enforcement

```yaml
steps:
  # npm: ci uses package-lock.json (fails if out of sync)
  - run: npm ci

  # pnpm: --frozen-lockfile fails if lockfile needs update
  - run: pnpm install --frozen-lockfile

  # yarn: --immutable fails if lockfile needs update
  - run: yarn install --immutable
```

---

## Fork Safety

### Prevent Secret Exposure to Forks

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test

  # Only run with secrets on non-fork PRs
  deploy-preview:
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    steps:
      - run: echo "Safe to use secrets"
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

**Rules:**
- `pull_request` from forks does NOT have access to secrets
- `pull_request_target` from forks DOES — use with extreme caution
- Never use `pull_request_target` with `actions/checkout` of the PR head
- Use `pull_request_target` only for labeling, commenting — never for code execution

### Dangerous Anti-Pattern

```yaml
# DANGEROUS — executes untrusted code with secrets
on: pull_request_target
jobs:
  build:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}  # UNTRUSTED CODE
      - run: npm test  # Runs attacker's code with repo secrets
```

### Safe Pattern

```yaml
# SAFE — only use pull_request_target for metadata operations
on: pull_request_target
jobs:
  label:
    permissions:
      pull-requests: write
    steps:
      - uses: actions/labeler@v5  # Only reads file paths, doesn't execute PR code
```

---

## Security Checklist

| Check | Status |
|-------|--------|
| `permissions` explicitly set at workflow level | Required |
| Actions pinned by SHA (or at least major version) | Recommended |
| Dependabot enabled for `github-actions` ecosystem | Required |
| Secret scanning enabled | Required |
| Push protection enabled | Recommended |
| CodeQL enabled on default branch | Recommended |
| OIDC used for cloud deploys (no static keys) | Recommended |
| Fork PRs don't get secrets | Required |
| `pull_request_target` not used with code checkout | Required |
| Lock files enforced (`npm ci`, `--frozen-lockfile`) | Required |
| Secrets never echoed or used in `if:` conditions | Required |
| Environment protection rules for production | Recommended |
| `harden-runner` for egress monitoring | Optional |
| Artifact attestations for provenance | Optional |
