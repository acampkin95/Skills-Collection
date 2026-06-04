# Workflow: Add QC to CI/CD

<required_reading>
**Read these reference files:**
1. references/ci-cd-patterns.md
2. references/best-practices.md
</required_reading>

<process>
## Step 1: Identify CI/CD Platform

Detect which platform is in use:
```bash
# GitHub Actions
ls .github/workflows/*.yml 2>/dev/null

# GitLab CI
ls .gitlab-ci.yml 2>/dev/null

# Circle CI
ls .circleci/config.yml 2>/dev/null

# Jenkins
ls Jenkinsfile 2>/dev/null
```

## Step 2: Create or Update CI Configuration

### GitHub Actions

Create/edit `.github/workflows/quality.yml`:

```yaml
name: Quality Checks

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      # JavaScript/TypeScript
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run Biome
        run: npx biome ci .

      - name: Type check
        run: npx tsc --noEmit

      - name: Run tests
        run: npm test -- --coverage

      # Python
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        run: |
          pip install -r requirements.txt
          pip install ruff pytest pytest-cov

      - name: Run Ruff
        run: ruff check .

      - name: Run Python tests
        run: pytest --cov=src --cov-report=xml

      # Upload coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info,./coverage.xml
          fail_ci_if_error: true
```

### GitLab CI

Create/edit `.gitlab-ci.yml`:

```yaml
stages:
  - quality
  - test

quality-check:
  stage: quality
  image: node:20
  script:
    - npm ci
    - npx biome ci .
    - npx tsc --noEmit
  only:
    - merge_requests
    - main

python-quality:
  stage: quality
  image: python:3.11
  script:
    - pip install -r requirements.txt ruff
    - ruff check .
  only:
    - merge_requests
    - main

test:
  stage: test
  image: node:20
  script:
    - npm ci
    - npm test -- --coverage
  coverage: '/Statements\s*:\s*([^%]+)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
```

### CircleCI

Create/edit `.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  quality:
    docker:
      - image: cimg/node:20.0
    steps:
      - checkout
      - restore_cache:
          keys:
            - deps-{{ checksum "package-lock.json" }}
      - run:
          name: Install dependencies
          command: npm ci
      - save_cache:
          key: deps-{{ checksum "package-lock.json" }}
          paths:
            - node_modules
      - run:
          name: Lint
          command: npx biome ci .
      - run:
          name: Type check
          command: npx tsc --noEmit
      - run:
          name: Test
          command: npm test -- --coverage
      - store_artifacts:
          path: coverage

workflows:
  quality-workflow:
    jobs:
      - quality
```

## Step 3: Configure Quality Gates

### Fail CI on Quality Issues

Set strict exit codes:
- Linting errors: Fail build
- Type errors: Fail build
- Test failures: Fail build
- Coverage below threshold: Fail build (optional)

### Example: Strict Biome Check
```yaml
- name: Run Biome (strict)
  run: npx biome ci --error-on-warnings .
```

### Example: Coverage Threshold
```yaml
- name: Test with coverage threshold
  run: npm test -- --coverage --coverageThreshold='{"global":{"lines":80}}'
```

## Step 4: Add Status Badges

Update README.md with CI status badges:

### GitHub Actions
```markdown
![Quality](https://github.com/username/repo/actions/workflows/quality.yml/badge.svg)
```

### GitLab CI
```markdown
![Quality](https://gitlab.com/username/repo/badges/main/pipeline.svg)
```

### Coverage Badge
```markdown
![Coverage](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)
```

## Step 5: Branch Protection Rules

### GitHub

Go to Settings → Branches → Add rule:
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Select: "Quality Checks" job

### GitLab

Go to Settings → Repository → Protected Branches:
- Require pipelines to succeed
- Require approval from code owners

## Step 6: Optimization for Speed

CI should be fast. Optimize by:

### Caching Dependencies
```yaml
- name: Cache node modules
  uses: actions/cache@v3
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('package-lock.json') }}
```

### Parallel Jobs
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npx biome check .

  type-check:
    runs-on: ubuntu-latest
    steps:
      - run: npx tsc --noEmit

  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
```

### Only Run on Changed Files (for large repos)
```yaml
- name: Get changed files
  id: changed-files
  uses: tj-actions/changed-files@v40

- name: Lint changed files
  run: npx biome check ${{ steps.changed-files.outputs.all_changed_files }}
```

## Step 7: Notifications

Configure failure notifications:

### GitHub Actions - Slack
```yaml
- name: Notify Slack on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email notifications (GitLab)
```yaml
quality-check:
  script:
    - ruff check .
  after_script:
    - 'curl -X POST -H "Content-Type: application/json" -d "{\"status\": \"$CI_JOB_STATUS\"}" $WEBHOOK_URL'
```

## Step 8: Documentation

Add CI/CD documentation to project:

```markdown
## Continuous Integration

### Quality Checks

Every PR runs:
- Linting (Biome/Ruff)
- Type checking (TypeScript/mypy)
- Tests with coverage
- Security scanning

### Local Pre-commit

Install pre-commit hooks to catch issues before pushing:
```bash
pre-commit install
```

### Bypassing Checks (Emergency Only)

Don't do this unless absolutely necessary:
```bash
git commit --no-verify
git push --no-verify
```
```
</process>

<success_criteria>
CI/CD quality checks are properly configured when:
- [ ] CI configuration file exists and is valid
- [ ] Quality checks run on PRs and main branch
- [ ] Linting, type checking, and tests all execute
- [ ] Failed quality checks block merging
- [ ] Status badges added to README
- [ ] Branch protection rules enabled
- [ ] Caching configured for faster builds
- [ ] Team notified of CI/CD setup and requirements
</success_criteria>
