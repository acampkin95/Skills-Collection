---
name: github-actions-ci
description: GitHub Actions CI/CD for workflows, reusable actions, deployment pipelines, and security hardening.
version: 2.0.0
reviewed: "2026-06-04"
---
# GitHub Actions CI/CD Skill

**Quick reference:**
- `references/reusable-workflows.md` — Composite actions, templates, job patterns
- `references/deployment-workflows.md` — Environments, approvals, rollbacks
- `references/security-hardening.md` — OIDC, Dependabot, CodeQL, supply chain

## 2026 GitHub Actions Pricing & Strategy

**Major changes effective 2026:**

| Update | Date | Impact |
|--------|------|--------|
| **Hosted runner price reduction** | Jan 1, 2026 | 39% decrease on standard runners (save ~40% on CI costs) |
| **ARM64 free-tier runners** | Jan 29, 2026 | ARM runners free in private repos (used to be paid) |
| **Self-hosted runner tax** | Mar 1, 2026 | $0.002/min for self-hosted runners (was free) |

**Strategy implications:**
- **Hosted runners**: Now much cheaper; prefer `ubuntu-latest` for CI (was 10x pricier than Linux)
- **ARM64 free**: Use for compatible workloads (Node.js, Python, Go) to save money
- **Self-hosted**: Only use for specialized hardware needs or long-running jobs; costs accumulate fast

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

**Rules:** Always set explicit `permissions` (least privilege). Pin action versions (`@v4` or SHA). Use `npm ci` over `npm install` (deterministic, faster). Workflow files go in `.github/workflows/*.yml`.

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

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.