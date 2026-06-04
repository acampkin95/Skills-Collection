---

## Parent router

This skill is a leaf of the [code-quality](../code-quality/SKILL.md) master router.
name: sonar-scanner
description: SonarScanner CLI setup and execution for code quality, security hotspots, and coverage analysis. Use when sonar-scanner, sonar-project.properties, sonarcloud, sonarqube, quality gate, code coverage upload.
---

# SonarScanner — Code Quality Analysis

## Installation

### macOS (Homebrew)

```bash
brew install sonar-scanner
sonar-scanner --version
```

### Linux (Manual)

```bash
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip
unzip sonar-scanner-cli-6.2.1.4610-linux-x64.zip
sudo mv sonar-scanner-6.2.1.4610-linux-x64 /opt/sonar-scanner
echo 'export PATH="/opt/sonar-scanner/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Docker (No Installation)

```bash
docker run --rm \
  -e SONAR_HOST_URL="http://host.docker.internal:9000" \
  -e SONAR_TOKEN="$SONAR_TOKEN" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli
```

---

## Configuration

Create `sonar-project.properties` in project root:

### Minimal Configuration

```properties
sonar.projectKey=my-project
sonar.projectName=My Project
sonar.projectVersion=1.0.0
sonar.sources=src
sonar.exclusions=**/*test.ts,**/*.spec.ts,node_modules/**
sonar.host.url=http://localhost:9000
sonar.login=your_token_here
```

### TypeScript/JavaScript Project

```properties
sonar.projectKey=my-app
sonar.projectName=My App
sonar.projectVersion=1.0.0
sonar.sources=src
sonar.tests=src
sonar.test.inclusions=**/*.test.ts,**/*.spec.ts
sonar.exclusions=**/*.d.ts,node_modules/**,dist/**,build/**
sonar.typescript.lcov.reportPaths=coverage/lcov.info
sonar.host.url=http://localhost:9000
sonar.login=$SONAR_TOKEN
```

### Python Project

```properties
sonar.projectKey=my-python-app
sonar.projectName=My Python App
sonar.sources=src
sonar.tests=tests
sonar.python.version=3.11
sonar.exclusions=**/migrations/**,**/venv/**,.venv/**
sonar.host.url=http://localhost:9000
sonar.login=$SONAR_TOKEN
```

---

## Coverage Integration

### TypeScript/Jest

```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

Configure `jest.config.js`:

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
  ],
  coverageReporters: ['lcov', 'text', 'json'],
  coverageDirectory: 'coverage',
};
```

Update `sonar-project.properties`:

```properties
sonar.typescript.lcov.reportPaths=coverage/lcov.info
```

### Python/pytest

```bash
pip install pytest pytest-cov
pytest --cov=src --cov-report=xml
```

Update `sonar-project.properties`:

```properties
sonar.python.coverage.reportPaths=coverage.xml
```

---

## Execution

### Local Execution

```bash
sonar-scanner
```

### With Explicit Token

```bash
sonar-scanner \
  -Dsonar.projectKey=my-project \
  -Dsonar.login=$SONAR_TOKEN \
  -Dsonar.host.url=https://sonarcloud.io
```

### Docker Execution

```bash
docker run --rm \
  -e SONAR_HOST_URL="https://sonarcloud.io" \
  -e SONAR_LOGIN="$SONAR_TOKEN" \
  -e SONAR_PROJECT_KEY="my-project" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli
```

---

## CI/CD Integration

### GitHub Actions (v7)

```yaml
name: SonarQube Scan

on: [push, pull_request]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run tests
        run: npm test -- --coverage

      - name: SonarScanner
        uses: SonarSource/sonarqube-scan-action@v5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}

      - name: Quality Gate
        uses: SonarSource/sonarqube-quality-gate-action@v1
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### GitLab CI

```yaml
sonarqube-check:
  image: sonarsource/sonar-scanner-cli:latest
  script:
    - npm run test:coverage
    - sonar-scanner
  only:
    - merge_requests
    - main
```

### Jenkins

```groovy
pipeline {
  agent any
  stages {
    stage('Test') {
      steps {
        sh 'npm test -- --coverage'
      }
    }
    stage('SonarQube Analysis') {
      steps {
        withSonarQubeEnv('SonarQube') {
          sh 'sonar-scanner'
        }
      }
    }
    stage('Quality Gate') {
      steps {
        waitForQualityGate abortPipeline: true
      }
    }
  }
}
```

---

## Quality Gates

### Create Quality Gate

1. Go to **Administration > Quality Gates**
2. Create new gate: "My Project"
3. Add conditions:
   - Coverage < 80%
   - Duplicated Lines > 5%
   - Code Smells > 50
   - Blocker Issues > 0

### Assign to Project

1. Go to project settings
2. **Quality Gate** section
3. Select gate

---

## Troubleshooting

### Common Issues

| Error | Solution |
|-------|----------|
| Token not found | Set `SONAR_TOKEN` env var or use `-Dsonar.login` |
| Project not created | Run with `-Dsonar.qualitygate.wait=true` on first run |
| Coverage not detected | Verify report path in `sonar-project.properties` |
| Cannot connect to host | Verify `sonar.host.url` is correct and accessible |

### Debug Mode

```bash
sonar-scanner -X
```

---

## AI Code Assurance (SonarQube 10.8+)

Quality gates can now flag AI-generated code with dedicated conditions:

- **AI Code Assurance** quality gate condition detects code generated by AI assistants
- Enforces stricter coverage and duplication thresholds on AI-generated code
- Enable via: **Administration > Quality Gates > Add Condition > AI Code Assurance**

## Security Hotspot Workflow

Security hotspots require human review before classification:

```
Detected → To Review → Safe / Fixed / Accepted Risk
```

- Hotspots differ from vulnerabilities: they need contextual review
- Use `sonar.security.hotspots.reviewed` metric in quality gates
- Assign reviewers via project permissions: **Administration > Permissions > Security Hotspot**

## Resources

| Resource | Purpose |
|----------|---------|
| [SonarQube Docs](https://docs.sonarqube.org) | Official SonarQube documentation |
| [SonarCloud](https://sonarcloud.io) | Cloud-hosted SonarQube |
| [Scanner CLI](https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/) | Scanner configuration reference |
