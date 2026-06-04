# CI/CD for AI-Assisted Projects

This document outlines strategies for CI/CD pipelines that accommodate AI-assisted development workflows.

## Overview

AI-assisted projects have unique CI/CD requirements:
- Larger, more complex changes
- Need for autonomous testing
- Cost-aware deployment strategies
- Integration with agent workflows

## Pipeline Architecture

### Agent-Friendly CI/CD

```yaml
# .github/workflows/agent-ci.yml
name: Agent CI

on:
  push:
    branches: [main, develop]
  pull_request:
    types: [opened, synchronize]

env:
  MAX_BUILD_COST: 10.00
  AGENT_MODE: true

jobs:
  quick-checks:
    name: Quick Validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint Check
        run: |
          echo "Running linters..."
          ruff check src/ tests/

      - name: Type Check
        run: |
          echo "Type checking..."
          mypy src/

      - name: Security Scan
        run: |
          echo "Security scan..."
          bandit -r src/

  agent-changes:
    name: Agent Changes
    # Only run when AI-assisted changes detected
    if: contains(github.event.head_commit.message, '[AI]')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate Change Summary
        run: |
          echo "AI-assisted changes detected"
          # Extract changed files
          git diff --name-only HEAD~1 > changed_files.txt

      - name: Extended Test Suite
        run: |
          echo "Running extended tests for AI changes"
          pytest -v --tb=short -x

      - name: AI Change Review
        uses: ./tools/ai-review-action
        with:
          model: "MiniMax-M2"
          focus: "security,performance"

  full-test-suite:
    name: Full Test Suite
    needs: [quick-checks, agent-changes]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Dependencies
        run: |
          pip install -r requirements.txt

      - name: Run Tests
        run: |
          pytest --cov=src/ --cov-report=xml

      - name: Upload Coverage
        uses: codecov/codecov-action@v3

  build:
    name: Build & Containerize
    needs: full-test-suite
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker Image
        run: |
          docker build -t ${{ env.IMAGE_NAME }}:${{ github.sha }} .

      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'image'
          image-ref: '${{ env.IMAGE_NAME }}:${{ github.sha }}'
          severity: 'CRITICAL,HIGH'

      - name: Push Image
        run: |
          docker push ${{ env.IMAGE_NAME }}:${{ github.sha }}
```

### Multi-Stage Deployment

```yaml
# deployment.yml
stages:
  - name: development
    requires: ['quick-checks']
    environment:
      url: https://dev.example.com
    auto_approve: true

  - name: staging
    requires: ['full-test-suite']
    environment:
      url: https://staging.example.com
    auto_approve: false  # Human review for staging

  - name: production
    requires: ['staging']
    environment:
      url: https://example.com
    auto_approve: false  # Production requires approval
    promotion_strategy: canary
```

## Automated Testing Strategies

### 1. Test Pyramid for AI Projects

```
                    ┌─────────────┐
                    │   E2E Tests │  (5%)
                    │  User flows │
                    └─────────────┘
              ┌─────────────────────────┐
              │   Integration Tests    │  (25%)
              │   Service boundaries   │
              └─────────────────────────┘
        ┌───────────────────────────────────┐
        │        Unit Tests (AI)            │  (70%)
        │   Function/Module level tests     │
        └───────────────────────────────────┘
```

### 2. AI-Specific Test Categories

```python
# tests/ai_specific/conftest.py
import pytest

@pytest.fixture
def ai_generated_code():
    """Marker for AI-generated code requiring extra scrutiny."""
    return {
        "needs_review": True,
        "test_coverage_threshold": 90,
        "complexity_threshold": 8
    }

@pytest.fixture
def agent_context():
    """Provide context from agent execution."""
    return {
        "agent_id": "agent-123",
        "task_id": "task-456",
        "changes_summary": "Added user authentication"
    }
```

### 3. Intelligent Test Selection

```python
# tools/test-selector/test_selector.py
import subprocess
from pathlib import Path

class IntelligentTestSelector:
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)

    def select_tests(self, changed_files, ai_mode=False):
        """Select relevant tests based on changes."""
        tests = set()

        # Always run critical path tests
        tests.update(self._get_critical_tests())

        # Find tests for changed files
        for changed_file in changed_files:
            tests.update(self._find_related_tests(changed_file))

        # Add AI-specific tests if applicable
        if ai_mode:
            tests.update(self._get_ai_safety_tests())

        return list(tests)

    def _get_critical_tests(self):
        """Get always-run critical tests."""
        return [
            "tests/core/test_authentication.py",
            "tests/core/test_authorization.py",
            "tests/api/test_core_endpoints.py"
        ]

    def _find_related_tests(self, changed_file):
        """Find tests related to a changed file."""
        # Map file patterns to test files
        mappings = {
            "src/models/": "tests/models/",
            "src/api/": "tests/api/",
            "src/services/": "tests/services/"
        }

        for pattern, test_dir in mappings.items():
            if pattern in str(changed_file):
                return self._find_tests_in_dir(test_dir)

        return []

    def run_selected_tests(self, tests, coverage=True):
        """Execute selected tests."""
        cmd = ["pytest", "-v", "--tb=short"]
        if coverage:
            cmd.extend(["--cov=src/", "--cov-report=term-missing"])
        cmd.extend(tests)

        result = subprocess.run(cmd)
        return result.returncode == 0
```

## Staging Deployment Strategies

### 1. Canary Deployment

```python
# deployment/canary.py
class CanaryDeployer:
    def __init__(self, k8s_client, config):
        self.client = k8s_client
        self.config = config

    def deploy_canary(self, image_tag, percentage=10):
        """Deploy canary version alongside stable."""
        canary_name = f"{self.config.app_name}-canary"

        # Create canary deployment
        self.client.create_deployment(
            name=canary_name,
            image=image_tag,
            replicas=1,
            labels={"version": "canary"}
        )

        # Route percentage of traffic
        self.client.update_istio_virtual_service(
            routes=[
                {"destination": "stable", "weight": 100 - percentage},
                {"destination": "canary", "weight": percentage}
            ]
        )

        return canary_name

    def promote_canary(self):
        """Promote canary to stable."""
        # Get canary config
        canary = self.client.get_deployment(f"{self.config.app_name}-canary")

        # Update stable deployment
        self.client.update_deployment(
            self.config.app_name,
            image=canary.image
        )

        # Route all traffic to stable
        self.client.update_istio_virtual_service(
            routes=[{"destination": "stable", "weight": 100}]
        )

        # Remove canary
        self.client.delete_deployment(f"{self.config.app_name}-canary")
```

### 2. Blue-Green Deployment

```python
class BlueGreenDeployer:
    def __init__(self, environment):
        self.environment = environment
        self.current_color = "blue"
        self.next_color = "green"

    def deploy(self, image_tag):
        """Deploy to inactive environment."""
        inactive = self.next_color

        # Deploy to inactive environment
        self._deploy_to(inactive, image_tag)

        # Run smoke tests
        if not self._smoke_test(inactive):
            self._rollback(inactive)
            return False

        # Switch traffic
        self._switch_traffic(inactive)
        self.current_color = inactive
        self.next_color = "blue" if inactive == "green" else "green"

        return True

    def _switch_traffic(self, target_color):
        """Switch all traffic to target color."""
        # Update load balancer or service mesh
        pass
```

## Production Release Strategies

### 1. Release Approval Workflow

```yaml
# .github/workflows/production-release.yml
name: Production Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Release version (e.g., 1.2.3)'
        required: true
      approval_required:
        description: 'Require approval'
        default: 'true'

jobs:
  validate:
    name: Validate Release
    runs-on: ubuntu-latest
    steps:
      - name: Validate version format
        run: |
          echo "${{ github.event.inputs.version }}" | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$'
          echo "Version validated"

      - name: Check changelog
        run: |
          if [ ! -f "CHANGELOG.md" ]; then
            echo "CHANGELOG.md not found"
            exit 1
          fi

  staging-deployment:
    name: Deploy to Staging
    needs: validate
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: |
          kubectl apply -f k8s/staging/

  production-check:
    name: Production Readiness Check
    needs: staging-deployment
    runs-on: ubuntu-latest
    steps:
      - name: Run health checks
        run: |
          # Verify staging is healthy
          curl -f https://staging.example.com/health

      - name: Generate release report
        run: |
          echo "# Release Report" > release-report.md
          echo "Version: ${{ github.event.inputs.version }}" >> release-report.md
          echo "Date: $(date -Iseconds)" >> release-report.md

  manual-approval:
    name: Manual Approval
    needs: production-check
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Wait for approval
        run: echo "Waiting for manual approval..."

  production-deploy:
    name: Deploy to Production
    needs: manual-approval
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        run: |
          kubectl apply -f k8s/production/
```

### 2. Rollback Procedures

```python
# deployment/rollback.py
class RollbackManager:
    def __init__(self, k8s_client, rollback_store):
        self.client = k8s_client
        self.rollback_store = rollback_store

    def create_rollback_point(self, deployment_name):
        """Create a rollback point before deployment."""
        current_state = {
            "deployment": self.client.get_deployment(deployment_name),
            "configmaps": self.client.get_configmaps(deployment_name),
            "secrets": self.client.get_secrets(deployment_name),
            "timestamp": datetime.now().isoformat()
        }

        checkpoint_id = self.rollback_store.save(current_state)
        return checkpoint_id

    def rollback(self, checkpoint_id, deployment_name):
        """Rollback to a checkpoint."""
        # Load checkpoint
        state = self.rollback_store.load(checkpoint_id)

        # Apply previous state
        self.client.apply_deployment(state["deployment"])
        self.client.apply_configmaps(state["configmaps"])
        self.client.apply_secrets(state["secrets"])

        # Record rollback
        self._record_rollback(deployment_name, checkpoint_id)

    def quick_rollback(self, deployment_name):
        """Quick rollback to previous version."""
        previous = self.client.get_previous_replica_set(deployment_name)
        if previous:
            self.client.scale_to(deployment_name, 0)
            self.client.scale_to(previous, desired_replicas)

    def get_rollback_history(self, deployment_name):
        """Get rollback history."""
        return self.rollback_store.get_history(deployment_name)
```

## Monitoring Integration

```python
# monitoring/deployment_monitoring.py
class DeploymentMonitor:
    def __init__(self, prometheus_client, alert_manager):
        self.prometheus = prometheus_client
        self.alerts = alert_manager

    def monitor_deployment(self, deployment_id, duration_minutes=30):
        """Monitor deployment health during rollout."""
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < duration_minutes * 60:
            metrics = self._collect_metrics(deployment_id)

            if self._is_unhealthy(metrics):
                self._trigger_alert(deployment_id, metrics)
                return False

            time.sleep(30)  # Check every 30 seconds

        return True

    def _collect_metrics(self, deployment_id):
        return {
            "error_rate": self.prometheus.query(f"error_rate{{deployment='{deployment_id}'}}"),
            "latency_p99": self.prometheus.query(f"latency_p99{{deployment='{deployment_id}'}}"),
            "cpu_usage": self.prometheus.query(f"cpu_usage{{deployment='{deployment_id}'}}"),
            "memory_usage": self.prometheus.query(f"memory_usage{{deployment='{deployment_id}'}}")
        }

    def _is_unhealthy(self, metrics):
        return (
            metrics["error_rate"] > 0.01 or  # 1% error rate
            metrics["latency_p99"] > 2000 or  # 2s latency
            metrics["cpu_usage"] > 0.9  # 90% CPU
        )
```

## Best Practices

1. **Fast Feedback:** Keep CI pipeline under 10 minutes
2. **Test Isolation:** Each test should be independent
3. **Automate Everything:** Remove manual steps
4. **Feature Flags:** Enable/disable without deploy
5. **Observability:** Log, metrics, traces everywhere
6. **Rollback Ready:** Always have a rollback plan

## See Also

- [Workflow Orchestration](../scripts/workflow-orchestrator.py)
- [Quality Gates](../scripts/quality-gate.py)
- [Cost Estimation](../scripts/cost-estimator.py)
