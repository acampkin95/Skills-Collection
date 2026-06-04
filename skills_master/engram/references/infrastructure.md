### Docker Compose Pattern

```bash
compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    docker compose -f "$COMPOSE_FILE" "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose -f "$COMPOSE_FILE" "$@"
  else
    error "Docker Compose not found"
  fi
}
```

### Health Check Pattern with Gates

```bash
wait_for_service() {
  local service="$1" port="$2" timeout="${3:-60}"
  local elapsed=0 interval=5
  while (( elapsed < timeout )); do
    if curl -sf "http://localhost:$port/health" >/dev/null 2>&1; then
      success "$service is ready"; return 0
    fi
    sleep "$interval"; elapsed=$((elapsed + interval))
  done
  error "$service did not start within ${timeout}s"
}

wait_for_service "Weaviate" 8080 120
wait_for_service "Memory API" 8000 90
wait_for_service "Redis" 6379 30
```

---

## New Script Checklist

- [ ] Shebang: `#!/bin/bash`
- [ ] Error handling: `set -euo pipefail`
- [ ] File header comment with purpose and usage
- [ ] Color definitions (RED, GREEN, YELLOW, BLUE, NC)
- [ ] Helper functions (log, info, success, warn, error)
- [ ] SCRIPT_DIR and PROJECT_ROOT path calculation
- [ ] Configuration variables (TIMEOUT, MAX_RETRIES, etc.)
- [ ] Pre-flight validation (command existence, file checks)
- [ ] Timeout handling for network/service checks
- [ ] Retry logic for transient failures
- [ ] Exit codes: 0 (success), 1 (failure)
- [ ] Cleanup: trap for temporary files
- [ ] Usage instructions in header or `--help`
- [ ] Optional: JSON output for CI/CD integration

---

## Troubleshooting Guide

### Deployment Fails: "Docker daemon not running"

```bash
docker ps
open /Applications/Docker.app        # macOS
sudo systemctl start docker           # Linux
```

### Smoke Test Fails: "curl: (7) Failed to connect"

```bash
docker compose ps
netstat -tlnp | grep 8080
docker compose logs nginx
tailscale status
```

### Validation Error: "MISSING: JWT_SECRET"

```bash
openssl rand -hex 32
echo "JWT_SECRET=$(openssl rand -hex 32)" >> .env
Engram-Platform/scripts/validate-env.sh .env
```

### Health Check Timeout: Service not starting

```bash
docker compose logs memory-api
TIMEOUT=30 Engram-Platform/scripts/smoke-test.sh
docker stats
docker system prune -a
```

### SSH to Production: "Permission denied"

```bash
ssh root@100.100.42.6   # Correct: Tailscale IP
# NOT: ssh root@46.250.245.181  (public IP)
tailscale status
```

---

## Integration Examples

### Local Development Workflow

```bash
cd /Users/alex/Projects/Dev/LIVE/Production/09_EngramPlatform
scripts/quality-gate.sh
git add -A && git commit -m "feat(scope): description"
git push origin main
```

### CI/CD Pipeline Step

```yaml
name: Quality Gate
on:
  push:
    branches: [main]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: ./scripts/quality-gate.sh
```

### Deployment to Production

```bash
Engram-Platform/scripts/validate-env.sh .env.prod
tar -czf backup-$(date +%s).tar.gz -C /var/lib/docker/volumes engram-memory-volume engram-crawler-volume
SMOKE_TEST_BASE_URL=https://dv-syd-host01.icefish-discus.ts.net scripts/deploy-unified.sh --target production --env-file .env.prod
scripts/release-smoke-test.sh https://dv-syd-host01.icefish-discus.ts.net
```

### Monitoring & Maintenance

```bash
watch -n 60 Engram-Platform/scripts/verify-health.sh
Engram-AiMemory/scripts/healthcheck.sh
docker compose logs -f memory-api crawler-api
```

---

## Infrastructure

### Target Servers

| Server | Role | Tailscale IP |
|--------|------|-------------|
| dv-syd-host01 | Production | 100.100.42.6 |
| acdev-devnode | Development | 100.78.187.5 |
| alex-macbookm4pro | Local dev | 100.117.68.96 |

### Deployment Paths

| Environment | Base Path | Compose | Env File |
|-------------|-----------|---------|----------|
| Production | `/opt/engram` | `/opt/engram/docker-compose.yml` | `/opt/engram/.env` |
| Dev | `/home/user/engram` | `./docker-compose.yml` | `./.env` |
| Local | `~/Projects/Dev/LIVE/Production/09_EngramPlatform` | `./Engram-Platform/docker-compose.yml` | `./Engram-Platform/.env` |

### Port Mappings

| Service | Internal | External | Host |
|---------|----------|----------|------|
| Memory API | 8000 | 8000 | All |
| Crawler API | 11235 | 11235 | All |
| MCP Server | 3000 | 3000 | All |
| Platform Frontend | 3000 | 3002 | Dev |
| Platform Frontend | 3000 | 80/443 | Prod (via nginx) |
| Weaviate | 8080 | 8080 | All |
| Redis Crawler | 6379 | 6379 | All |
| Redis Memory | 6379 | 6380 | All |
| Nginx | 80/443 | 8080 | Docker |

---

## File Reference

| Path | Type | Purpose |
|------|------|---------|
| `scripts/deploy-unified.sh` | Bash | Primary deployment orchestrator |
| `scripts/quality-gate.sh` | Bash | CI/CD quality gate |
| `scripts/release-smoke-test.sh` | Bash | Release verification |
| `Engram-Platform/scripts/smoke-test.sh` | Bash | E2E health checks |
| `Engram-Platform/scripts/validate-env.sh` | Bash | Environment validation |
| `Engram-Platform/scripts/verify-health.sh` | Bash | Quick container health |
| `Engram-Platform/docker-compose.yml` | YAML | Main orchestration file |
| `Engram-Platform/nginx/nginx.conf` | YAML | Reverse proxy config |
| `Engram-AiMemory/scripts/deploy-full.sh` | Bash | Full AI Memory deployment |
| `Engram-AiMemory/scripts/healthcheck.sh` | Bash | Deep system health |
| `Engram-AiMemory/docker-compose.yml` | YAML | AI Memory stack |
| `.env.example` | Shell | Environment template |
| `docs/RELEASE_CHECKLIST.md` | Markdown | Release verification steps |

---

**Last Updated:** 2026-04-01
**Scope:** Engram Platform master navigator + automation scripts, CI/CD, deployments, health checks
**Status:** Complete production reference
