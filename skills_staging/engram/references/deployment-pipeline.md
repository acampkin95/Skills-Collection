## Deployment Pipeline

### Flow Diagram

```
Local Development
      ↓
[quality-gate.sh] <- Run all linters, tests, bundle checks
      ↓
git push origin main
      ↓
GitHub Actions CI
  - Run quality-gate.sh
  - Build Docker images
  - Push to registry
      ↓
Deploy to devnode (acdev-devnode.icefish-discus.ts.net)
  - validate-env.sh
  - docker compose pull & up
  - verify-health.sh
  - smoke-test.sh
      ↓
Deploy to production (dv-syd-host01.icefish-discus.ts.net)
  - Pre-flight checks (SSL, disk, RAM)
  - Backup existing stack
  - deploy-unified.sh or deploy-production.sh
  - health gates per service
  - post-deploy smoke-test.sh
  - Systemd auto-start setup
      ↓
[release-smoke-test.sh] <- Final release verification
```

