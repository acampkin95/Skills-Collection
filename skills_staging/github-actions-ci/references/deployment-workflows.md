# Deployment Workflows

## Preview Deploys (Vercel)

### Automatic Preview on PR

```yaml
# .github/workflows/preview.yml
name: Preview Deploy

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

concurrency:
  group: preview-${{ github.head_ref }}
  cancel-in-progress: true

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci
      - run: npm run build

      - id: deploy
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./

      - uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `Preview deployed to: ${{ steps.deploy.outputs.preview-url }}`
            });
```

### Vercel with OIDC (No Static Secrets)

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - run: npx vercel pull --yes --token=${{ secrets.VERCEL_TOKEN }}
      - run: npx vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
      - run: npx vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## Preview Deploys (Netlify)

```yaml
# .github/workflows/netlify-preview.yml
name: Netlify Preview

on:
  pull_request:

permissions:
  contents: read
  pull-requests: write

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci && npm run build

      - uses: nwtgck/actions-netlify@v3
        with:
          publish-dir: ./dist
          production-branch: main
          github-token: ${{ secrets.GITHUB_TOKEN }}
          deploy-message: "PR #${{ github.event.pull_request.number }}"
          enable-pull-request-comment: true
          enable-commit-comment: false
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

---

## Staging and Production Environments

### Two-Stage Deploy Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

permissions:
  contents: read
  id-token: write

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
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: dist/
          retention-days: 3

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: dist/
      - run: echo "Deploying to staging..."
        env:
          DEPLOY_URL: ${{ vars.DEPLOY_URL }}
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}

  smoke-test:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          # Wait for deployment to propagate
          sleep 10
          # Run smoke tests against staging
          curl --fail https://staging.example.com/health
      - run: npx playwright test --project=smoke
        env:
          BASE_URL: https://staging.example.com

  deploy-production:
    needs: smoke-test
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    concurrency:
      group: deploy-production
      cancel-in-progress: false
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: dist/
      - run: echo "Deploying to production..."
        env:
          DEPLOY_URL: ${{ vars.DEPLOY_URL }}
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

---

## Manual Approval Gates

### Environment Protection Rules

Configure in **Settings > Environments > production**:
- **Required reviewers**: Add team members who must approve
- **Wait timer**: Optional delay (0–43200 minutes)
- **Branch restrictions**: Limit to `main` or `release/*`

### Manual Trigger with Environment Selection

```yaml
name: Manual Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Target environment"
        required: true
        type: choice
        options:
          - staging
          - production
      version:
        description: "Version to deploy (e.g., v1.2.3)"
        required: true
        type: string
      confirm:
        description: "Type 'deploy' to confirm"
        required: true
        type: string

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - if: inputs.confirm != 'deploy'
        run: |
          echo "::error::Confirmation failed. Type 'deploy' to confirm."
          exit 1

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    environment:
      name: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.version }}
      - run: echo "Deploying ${{ inputs.version }} to ${{ inputs.environment }}"
```

---

## Rollback Workflows

### Redeploy Previous Version

```yaml
name: Rollback

on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Environment to rollback"
        required: true
        type: choice
        options: [staging, production]
      commit-sha:
        description: "Commit SHA to rollback to"
        required: true
        type: string
      reason:
        description: "Reason for rollback"
        required: true
        type: string

permissions:
  contents: read
  actions: read

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment:
      name: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.commit-sha }}

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci
      - run: npm run build

      - run: echo "Rolling back ${{ inputs.environment }} to ${{ inputs.commit-sha }}"
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}

      # Notify team
      - uses: slackapi/slack-github-action@v2
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK }}
          webhook-type: incoming-webhook
          payload: |
            {
              "text": "Rollback: ${{ inputs.environment }} → ${{ inputs.commit-sha }}\nReason: ${{ inputs.reason }}\nBy: ${{ github.actor }}"
            }
```

### Automatic Rollback on Health Check Failure

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    outputs:
      previous-version: ${{ steps.current.outputs.version }}
    steps:
      - id: current
        run: |
          CURRENT=$(curl -s https://example.com/version)
          echo "version=$CURRENT" >> "$GITHUB_OUTPUT"
      - run: echo "Deploy new version..."

  verify:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - id: health
        run: |
          for i in {1..5}; do
            if curl --fail https://example.com/health; then
              echo "healthy=true" >> "$GITHUB_OUTPUT"
              exit 0
            fi
            sleep 10
          done
          echo "healthy=false" >> "$GITHUB_OUTPUT"
          exit 1
        continue-on-error: true

      - if: steps.health.outputs.healthy != 'true'
        run: |
          echo "Health check failed — rolling back to ${{ needs.deploy.outputs.previous-version }}"
          # Trigger rollback deploy
          exit 1
```

---

## OIDC for Cloud Deploys

### AWS (No Static Credentials)

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1

      - run: aws s3 sync dist/ s3://my-bucket/
```

### Google Cloud (Workload Identity Federation)

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/github/providers/my-repo
          service_account: deploy@my-project.iam.gserviceaccount.com

      - uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: my-service
          region: us-central1
          image: gcr.io/my-project/my-image:${{ github.sha }}
```

### Azure (Federated Credentials)

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - uses: azure/webapps-deploy@v3
        with:
          app-name: my-app
          package: dist/
```

**OIDC Rules:**
- Always prefer OIDC over static credentials (keys/secrets)
- Requires `id-token: write` permission
- Configure trust policy on the cloud provider to accept GitHub's OIDC tokens
- Scope trust to specific repo, branch, and environment
- See `references/security-hardening.md` for full OIDC setup details

---

## Docker / Container Deploy

```yaml
name: Build & Push Container

on:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  build-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```
