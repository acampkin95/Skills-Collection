# Project Configuration Templates

## Next.js / TypeScript (App Router)

```properties
sonar.projectKey=my-nextjs-app
sonar.projectName=My Next.js App
sonar.sources=src,app
sonar.tests=src,app
sonar.sourceEncoding=UTF-8

# Exclusions
sonar.exclusions=\
  **/node_modules/**,\
  **/.next/**,\
  **/dist/**,\
  **/build/**,\
  **/coverage/**,\
  **/*.config.js,\
  **/*.config.ts,\
  **/*.config.mjs,\
  **/public/**

# TypeScript / JavaScript
sonar.typescript.lcov.reportPaths=coverage/lcov.info
sonar.javascript.lcov.reportPaths=coverage/lcov.info

# Test patterns
sonar.test.inclusions=**/*.test.ts,**/*.test.tsx,**/*.spec.ts,**/*.spec.tsx
sonar.coverage.exclusions=\
  **/*.test.*,\
  **/*.spec.*,\
  **/test/**,\
  **/tests/**,\
  **/__tests__/**,\
  **/__mocks__/**,\
  **/mocks/**,\
  **/fixtures/**
```

## Next.js / TypeScript (Pages Router)

```properties
sonar.projectKey=my-nextjs-pages-app
sonar.projectName=My Next.js Pages App
sonar.sources=src,pages,components,lib
sonar.tests=src,pages,components,lib
sonar.sourceEncoding=UTF-8

sonar.exclusions=\
  **/node_modules/**,\
  **/.next/**,\
  **/dist/**,\
  **/public/**,\
  **/*.config.*

sonar.typescript.lcov.reportPaths=coverage/lcov.info
sonar.test.inclusions=**/*.test.ts,**/*.test.tsx,**/*.spec.ts,**/*.spec.tsx
sonar.coverage.exclusions=**/*.test.*,**/*.spec.*,**/test/**,**/__tests__/**
```

## React (Vite)

```properties
sonar.projectKey=my-react-app
sonar.projectName=My React App
sonar.sources=src
sonar.tests=src
sonar.sourceEncoding=UTF-8

sonar.exclusions=\
  **/node_modules/**,\
  **/dist/**,\
  **/coverage/**,\
  **/*.config.*

sonar.typescript.lcov.reportPaths=coverage/lcov.info
sonar.test.inclusions=**/*.test.ts,**/*.test.tsx,**/*.spec.ts,**/*.spec.tsx
sonar.coverage.exclusions=**/*.test.*,**/*.spec.*,**/test/**
```

## Python (Django / FastAPI / General)

```properties
sonar.projectKey=my-python-app
sonar.projectName=My Python App
sonar.sources=src
sonar.tests=tests
sonar.sourceEncoding=UTF-8
sonar.language=py

sonar.exclusions=\
  **/__pycache__/**,\
  **/.venv/**,\
  **/venv/**,\
  **/migrations/**,\
  **/*.pyc,\
  **/dist/**,\
  **/build/**,\
  **/.eggs/**

sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml

sonar.coverage.exclusions=\
  **/tests/**,\
  **/test_*,\
  **/conftest.py,\
  **/migrations/**
```

## Multi-Language (Monorepo)

```properties
sonar.projectKey=my-monorepo
sonar.projectName=My Monorepo
sonar.sources=.
sonar.sourceEncoding=UTF-8

sonar.exclusions=\
  **/node_modules/**,\
  **/.next/**,\
  **/dist/**,\
  **/build/**,\
  **/coverage/**,\
  **/__pycache__/**,\
  **/.venv/**,\
  **/public/**

# Multiple coverage reports
sonar.typescript.lcov.reportPaths=apps/web/coverage/lcov.info,packages/*/coverage/lcov.info
sonar.python.coverage.reportPaths=apps/api/coverage.xml

sonar.test.inclusions=**/*.test.*,**/*.spec.*,**/tests/**
sonar.coverage.exclusions=**/*.test.*,**/*.spec.*,**/test/**,**/tests/**
```

## Node.js API (Express / Fastify)

```properties
sonar.projectKey=my-node-api
sonar.projectName=My Node API
sonar.sources=src
sonar.tests=src,test,tests
sonar.sourceEncoding=UTF-8

sonar.exclusions=\
  **/node_modules/**,\
  **/dist/**,\
  **/coverage/**,\
  **/*.config.*

sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.test.inclusions=**/*.test.ts,**/*.test.js,**/*.spec.ts,**/*.spec.js
sonar.coverage.exclusions=**/*.test.*,**/*.spec.*,**/test/**
```

## SonarCloud Additions

Append to any config above when using SonarCloud instead of self-hosted:

```properties
sonar.organization=my-org-key
sonar.host.url=https://sonarcloud.io
```
