---
name: sonar-scanner
description: SonarScanner CLI for SonarQube/SonarCloud code quality analysis. Use for static analysis, quality gates, and multi-language project scanning.
version: 2.0.0
reviewed: "2026-06-04"
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


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.