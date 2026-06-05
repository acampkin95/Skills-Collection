---
name: engram
description: Engram Platform master navigator, for CI/CD, deployment scripts, health checks.
---

# Engram Platform

## Sub-Skills Navigator

| Task | Use Skill |
|------|-----------|
| System overview, architecture, tech stack | `engram-system-architecture` |
| Docker containers, volumes, networking | `engram-docker-services` |
| Memory CRUD, search, RAG, knowledge graph | `engram-weaviate-memory` |
| MCP server setup, tools, Claude Code config | `engram-mcp-integration` |
| SSH, server ops, backups, credentials | `engram-server-administration` |
| Decay, consolidation, cleanup, SonarQube | `engram-maintenance-schedules` |
| Live API tests, memory hooks | `engram-hooks-tests` |
| Deploy updates, rsync, rebuild, SSL certs | `engram-deploy` |
| CI/CD, deployment scripts, quality gates | This skill (see below) |

---

## Quick Reference

- Production host: acdev-devnode (100.78.187.5) — Tailscale only
- Memory API: http://100.78.187.5:8000
- Platform: port 3002 (dev), 80/443 (Docker)
- Monorepo: /Users/alex/Projects/Dev/LIVE/Production/09_EngramPlatform
- Docker path (production): /opt/engram/Engram-Platform

---

## Automation Scripts & CI/CD Reference

This section documents all automation scripts, deployment workflows, quality gates, and CI/CD patterns
for the Engram Platform monorepo.

---

## Quick Script Reference

| Script | Purpose | Env | Needs Root | Time |
|--------|---------|-----|------------|------|
| `deploy-unified.sh` | Interactive orchestration menu | Any | No | varies |
| `quality-gate.sh` | Full platform QA gate | Dev | No | 3-5m |
| `smoke-test.sh` | E2E health checks | Docker | No | 1-2m |
| `validate-env.sh` | Configuration validation | Any | No | <5s |
| `release-smoke-test.sh` | Release verification | Any | No | 1m |
| `deploy-production.sh` | Legacy: prod deploy | dv-syd | Yes | 10-15m |
| `deploy-devnode.sh` | Legacy: dev deploy | acdev | No | 5-10m |
| `verify-health.sh` | Quick container health | Docker | No | 1-2m |
| `deploy-full.sh` (AiMemory) | Full AI Memory stack | Any | Yes | 15-30m |
| `healthcheck.sh` (AiMemory) | Deep system health | Any | No | 1m |

---

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

### Pre-Deployment Checklist

- [ ] All tests pass: `scripts/quality-gate.sh`
- [ ] Bundle size <5MB: checked in quality-gate.sh
- [ ] Environment file validated: `Engram-Platform/scripts/validate-env.sh .env`
- [ ] SSL certificates valid (prod): >30 days until expiry
- [ ] Backup created before deployment
- [ ] Tailscale connectivity verified: `tailscale status | grep -E "dv-syd|acdev"`
- [ ] Docker daemon running on target host
- [ ] Disk space available: >10GB on `/` and `/var/lib/docker`
- [ ] No other deployments in progress

---

## Quality Gates

### Platform Quality Gate (`scripts/quality-gate.sh`)

Runs all linters, builds, and tests across the monorepo:

```bash
cd /Users/alex/Projects/Dev/LIVE/Production/09_EngramPlatform
scripts/quality-gate.sh
```

**Coverage:**

1. **MCP Server** (TypeScript)
   - Build: `npm run build`
   - Lint: `npx @biomejs/biome check src/`
   - Tests: `npm test` (382+ pass expected)

2. **Platform Frontend** (Next.js 15)
   - Build: `npm run build`
   - Type check: `npx tsc --noEmit`
   - Lint: `npx @biomejs/biome check src/ app/`
   - Tests: `npm run test:run` (511+ pass expected)

3. **AI Memory** (Python + TypeScript)
   - Python lint: `python -m ruff check app/`
   - Type check: mypy (via `make lint`)
   - Tests: pytest (901+ pass expected, skipped in CI if redis/weaviate offline)

4. **AI Crawler** (Python)
   - Lint: `python -m ruff check app/`
   - Tests: pytest (2393+ pass expected)

5. **Shell Scripts**
   - ShellCheck: `shellcheck -S warning *.sh`

6. **Bundle Size**
   - Check: `.next/static/chunks/*.js` total <5MB uncompressed
   - Threshold: 5242880 bytes (5.0 MB)
   - Warning issued if exceeded, but gate does not fail

7. **Smoke Tests**
   - Conditional: only if Docker services running
   - Runs: `Engram-Platform/scripts/smoke-test.sh`

**Exit Codes:**
- `0`: All gates passed
- `1`: Any gate failed (stops at first failure)

---

## Health Checks & Endpoints

### Service Health Endpoints

| Service | Port | Endpoint | Expected |
|---------|------|----------|----------|
| Memory API | 8000 | `/health` | `200 {status: ok}` |
| Crawler API | 11235 | `/health` | `200 {status: ok}` |
| MCP Server | 3000 | `/health` | `200 {version: ...}` |
| Platform Frontend | 3002 | `/` | `200 (HTML)` |
| Platform Frontend | 3000 | `/` | `200 (HTML)` (Docker internal) |
| Weaviate | 8080 | `/v1/.well-known/ready` | `204` |
| Nginx Proxy | 8080 | `/health` | `200` |

### Docker Compose Health Check Pattern

```bash
# Quick health check
Engram-Platform/scripts/verify-health.sh

# Full E2E smoke test
Engram-Platform/scripts/smoke-test.sh

# Deep system health (AI Memory)
Engram-AiMemory/scripts/healthcheck.sh
```

### HTTP Check with Retries

All scripts use this pattern for resilient health checks:

```bash
http_check() {
  local url="$1" method="${2:-GET}" data="${3:-}"
  local attempt=0 max_retries=3 timeout=10

  while (( attempt < max_retries )); do
    local http_code
    if [[ "$method" == "GET" ]]; then
      http_code=$(curl -sk -o /dev/null -w '%{http_code}' \
        --max-time "$timeout" "$url" 2>/dev/null) || true
    else
      http_code=$(curl -sk -o /dev/null -w '%{http_code}' \
        --max-time "$timeout" -X "$method" \
        -H 'Content-Type: application/json' -d "$data" "$url" 2>/dev/null) || true
    fi

    if [[ "$http_code" =~ ^[23] ]]; then
      return 0
    fi

    ((attempt+=1))
    [[ $attempt -lt $max_retries ]] && sleep 2
  done

  return 1
}
```

---

## Environment Validation

### Schema Validation (`validate-env.sh`)

```bash
Engram-Platform/scripts/validate-env.sh .env
```

**Required Variables:**
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` — Clerk frontend key
- `CLERK_SECRET_KEY` — Clerk backend secret
- `JWT_SECRET` — Server JWT signing (min 32 chars)
- `DEEPINFRA_API_KEY` — LLM inference provider
- `MCP_AUTH_TOKEN` — MCP server bearer token
- `BINDING_ADDRESS` — NOT `0.0.0.0` (security)
- `EMBEDDING_PROVIDER` — openai, deepinfra, nomic, ollama, or local

**Optional Variables:**
- `MEMORY_API_KEY` — Memory API authentication
- `NEXT_PUBLIC_MEMORY_API_KEY` — Frontend memory API key
- `TAILSCALE_HOSTNAME` — Tailscale network hostname
- `CORS_ORIGINS` — CORS whitelist
- `NEXT_PUBLIC_APP_URL` — Frontend URL
- `EMBEDDING_MODEL` — Specific embedding model
- `EMBEDDING_DIMENSIONS` — Vector dimensions
- `NEXT_PUBLIC_SENTRY_DSN` — Error tracking
- `SENTRY_AUTH_TOKEN` — Sentry backend
- `SENTRY_ORG`, `SENTRY_PROJECT` — Sentry config

**Validation Rules:**
- No empty values
- No placeholder values (e.g., `your-api-key`, `...`)
- `JWT_SECRET` must be >= 32 characters
- `BIND_ADDRESS` must not be `0.0.0.0`

---

## Deployment Scripts Catalog

### 1. deploy-unified.sh (Primary Entry Point)

**Location:** `scripts/deploy-unified.sh` (1478 lines)

**Purpose:** Interactive orchestration menu for all deployment scenarios.

**Usage:**

```bash
scripts/deploy-unified.sh
# Prompts for:
# 1. Deploy to devnode
# 2. Deploy to production
# 3. Maintenance (logs, rebuild, restart, stop)
# 4. Backups (list, restore)
# 5. Health dashboard
# 6. Environment wizard
```

**Options:**
- `--target devnode|production` — Skip menu, deploy directly
- `--env-file <path>` — Use custom .env file
- `--skip-checks` — Skip pre-flight validation
- `--dry-run` — Show commands without executing

**Features:**
- Interactive menu with colored output
- Pre-flight validation (Docker, env, Tailscale)
- Health monitoring dashboard
- Backup/restore integration
- Environment configuration wizard
- Service status display

---

### 2. quality-gate.sh (CI/CD Gate)

**Location:** `scripts/quality-gate.sh` (121 lines)

**Purpose:** Unified quality gate for all subprojects.

**Usage:**

```bash
scripts/quality-gate.sh
# Runs all checks and exits 0 if all pass, 1 if any fail
```

**Execution Order:**
1. MCP Server: build + biome lint + tests (382+)
2. Platform Frontend: next build + tsc + biome + tests (511+)
3. AI Memory: ruff + mypy (pytest skipped if no redis/weaviate)
4. AI Crawler: ruff lint
5. Shell scripts: shellcheck
6. Bundle size: <5MB check
7. Smoke tests: if Docker running

---

### 3. smoke-test.sh (E2E Tests)

**Location:** `Engram-Platform/scripts/smoke-test.sh` (321 lines)

**Purpose:** End-to-end health checks for UI -> API -> Backend flow.

**Usage:**

```bash
# Default: http://localhost:8080
Engram-Platform/scripts/smoke-test.sh

# Custom URL
SMOKE_TEST_BASE_URL=http://dv-syd-host01.icefish-discus.ts.net \
SMOKE_TEST_TIMEOUT=15 \
SMOKE_TEST_RETRIES=5 \
  Engram-Platform/scripts/smoke-test.sh
```

**Phases:**

1. **Docker Service Health**
   - Check container status (healthy/running)
   - Required: nginx, platform-frontend, crawler-api, memory-api, weaviate, redis x2
   - Optional: mcp-server

2. **Direct Service Endpoints**
   - Memory API: `http://localhost:8000/health`
   - Crawler API: `http://localhost:11235/health`
   - MCP Server: `http://localhost:3000/health`
   - Platform: `http://localhost:3002/` or `http://localhost:3000/`

3. **Nginx Proxy Routes**
   - Health: `${BASE_URL}/health`
   - Memory API: `${BASE_URL}/api/memory/health`
   - Crawler API: `${BASE_URL}/api/crawler/health`
   - MCP: `${BASE_URL}/mcp/health`
   - Frontend: `${BASE_URL}/`

4. **API Functional Tests**
   - POST `/api/memory/memories/search` (with auth check: 401/403/422 OK)
   - GET `/api/crawler/api/stats/dashboard`
   - GET `/api/crawler/health`

**Exit Codes:**
- `0`: All tests passed
- `1`: Any test failed

---

### 4. validate-env.sh (Configuration Check)

**Location:** `Engram-Platform/scripts/validate-env.sh` (110 lines)

**Purpose:** Validate environment configuration against schema.

**Usage:**

```bash
# Check default .env
Engram-Platform/scripts/validate-env.sh

# Check specific file
Engram-Platform/scripts/validate-env.sh /path/to/.env
```

**Output:**
- Green checkmarks for OK variables
- Red errors for missing/invalid required variables
- Yellow warnings for optional/unset variables
- Summary: `PASSED: 0 errors, N warnings` or `FAILED: N errors, M warnings`

---

### 5. release-smoke-test.sh (Release Verification)

**Location:** `scripts/release-smoke-test.sh` (85 lines)

**Purpose:** Minimal smoke test for release verification.

**Usage:**

```bash
# Local
./scripts/release-smoke-test.sh

# Production
./scripts/release-smoke-test.sh http://dv-syd-host01.icefish-discus.ts.net

# With auth required handling
./scripts/release-smoke-test.sh http://localhost:8080
# Accepts 401/403 as passing (endpoint exists, auth enforced)
```

**Checks:**
- Memory API health, Crawler API health, MCP health
- Platform sign-in page
- Health response JSON structure
- OAuth metadata endpoint
- API documentation endpoints

---

### 6. deploy-production.sh (Legacy)

**Location:** `Engram-Platform/scripts/deploy-production.sh` (618 lines)

**Status:** Deprecated, use `deploy-unified.sh` instead

**Purpose:** Full production deployment with backups and systemd setup.

**Usage:**

```bash
sudo scripts/deploy-production.sh \
  --env-file /path/to/.env \
  --host dv-syd-host01.icefish-discus.ts.net
```

**Requirements:**
- Root (sudo) access
- Target host reachable via Tailscale
- `.env` file with all required variables
- Docker and Docker Compose installed

**Pre-Flight Checks:**
- Docker and Compose installed
- Compose file syntax valid
- Required env vars set (no placeholders)
- Tailscale connectivity to target
- Bind address matches local interfaces
- SSL certificates exist and valid (>30 days)
- Disk space available (>10GB)
- RAM available (>8GB)

**Deployment Steps:**
1. Validate environment and certificates
2. Create backup of existing stack
3. Build/pull Docker images
4. Deploy services with health gates
5. Verify endpoints after deployment
6. Setup systemd auto-start
7. Display deployment summary

**Systemd Setup:**
- Service: `/etc/systemd/system/engram-platform.service`
- Auto-start on reboot
- Restart on failure (max 5 retries)

---

### 7. deploy-devnode.sh (Legacy Dev Deployment)

**Location:** `Engram-Platform/scripts/deploy-devnode.sh` (164 lines)

**Status:** Deprecated, use `deploy-unified.sh` instead

**Purpose:** Development node deployment on acdev-devnode.

**Usage:**

```bash
scripts/deploy-devnode.sh \
  --env-file /path/to/.env \
  --host acdev-devnode.icefish-discus.ts.net
```

**Pre-Flight Checks:**
- Docker and Compose installed
- `.env` file exists and readable
- Required env vars set
- Tailscale connectivity

**Deployment Steps:**
1. Validate environment
2. Pull latest Docker images
3. Deploy services via docker compose
4. Health check loop (30 retries x 5s)
5. Display final status

---

### 8. verify-health.sh (Quick Container Health)

**Location:** `Engram-Platform/scripts/verify-health.sh` (140 lines)

**Purpose:** Quick health check for all containers.

**Usage:**

```bash
Engram-Platform/scripts/verify-health.sh

# Customize retries
MAX_RETRIES=50 RETRY_INTERVAL=1 \
  Engram-Platform/scripts/verify-health.sh
```

**Containers Checked:**
- Required: nginx, platform-frontend, crawler-api, memory-api, weaviate, crawler-redis, memory-redis
- Optional: mcp-server

**Health States:**
- `healthy` — Passing health check
- `running` — No health check defined, but container running
- `exited` — Container stopped
- `restarting` — Container restarting

**Exit Codes:**
- `0`: All required containers healthy
- `1`: Any required container not healthy

---

### 9. deploy-full.sh (AI Memory Full Deploy)

**Location:** `Engram-AiMemory/scripts/deploy-full.sh` (957 lines)

**Purpose:** Complete AI Memory system deployment with optimization and Weaviate schema setup.

**Usage:**

```bash
# Interactive deployment
./scripts/deploy-full.sh

# Non-interactive with defaults
./scripts/deploy-full.sh --non-interactive

# Upgrade existing installation
./scripts/deploy-full.sh --upgrade

# Skip system optimization
./scripts/deploy-full.sh --skip-optimize

# Dry-run (show commands only)
./scripts/deploy-full.sh --dry-run
```

**Options:**
- `--non-interactive` — Use defaults, no prompts
- `--upgrade` — Upgrade existing installation
- `--skip-optimize` — Skip kernel/system tuning
- `--skip-systemd` — Don't setup auto-start
- `--dry-run` — Show commands without executing
- `--force` — Skip confirmations

**9-Step Process:**

1. **Pre-Flight Validation**
   - OS support (Linux required)
   - RAM: >= 16GB
   - Disk: >= 50GB available
   - Docker, Python 3.11+, Node.js 20+

2. **Environment Configuration**
   - Prompts for embedding provider, keys, URLs
   - Generates JWT_SECRET, WEAVIATE_API_KEY
   - Writes to `.env` file

3. **System Optimization**
   - `vm.max_map_count = 262144` (Weaviate)
   - `vm.overcommit_memory = 1` (Redis)
   - Disable Transparent Huge Pages
   - Enable TCP BBR congestion control
   - Increase file descriptor limits
   - Docker daemon optimization

4. **Docker Image Build/Pull**
   - Build local images (if docker/Dockerfile present)
   - Pull public images (weaviate, redis)
   - Progress tracking with spinner

5. **Stack Deployment**
   - `docker compose up -d`
   - Health gates per service:
     - Weaviate: 120s timeout
     - Redis: 30s timeout
     - Memory API: 90s timeout
     - MCP Server: 30s timeout
     - Dashboard: 60s timeout

6. **Weaviate Schema Initialization**
   - Create Memories collection
   - Create Entities collection
   - Create Relationships collection
   - Define indexes and vectorizers

7. **MCP Server Verification**
   - Check server health
   - Display Claude Desktop config snippet
   - Instructions for `.mcp_servers.json` setup

8. **Systemd Auto-Start Setup**
   - Create service file: `/etc/systemd/system/engram-memory.service`
   - Enable and start service
   - Verify boot-time startup

9. **Post-Deploy Verification**
   - Run smoke tests
   - Verify endpoints
   - Generate deployment report (Markdown + JSON)

**Health Gate Timeouts:**
- Weaviate: 120s (slow to initialize)
- Memory API: 90s (builds schema, connections)
- Redis: 30s (fast startup)
- MCP Server: 30s (lightweight)
- Dashboard: 60s (npm build)

---

### 10. healthcheck.sh (Deep System Health)

**Location:** `Engram-AiMemory/scripts/healthcheck.sh` (431 lines)

**Purpose:** Comprehensive system health assessment across 10 dimensions.

**Usage:**

```bash
./scripts/healthcheck.sh

# Check specific service only
SERVICE=weaviate ./scripts/healthcheck.sh

# Output as JSON
./scripts/healthcheck.sh --json
```

**10 Health Dimensions:**

1. **Docker & Containers**
   - Docker daemon status
   - Container status (running, healthy)
   - Per-container memory/CPU usage

2. **Service Endpoints**
   - HTTP health checks: Weaviate, Memory API, Redis
   - Timeout: 5s per check, max 3 retries

3. **Weaviate Schema**
   - Collections present (Memories, Entities, Relationships)
   - Schema validation
   - Vector dimensions

4. **PostgreSQL** (if configured)
   - Connection status
   - Database size
   - Table count and sizes

5. **Redis**
   - Role (master/slave)
   - Memory usage
   - Connected clients
   - Persistence status (RDB/AOF)
   - Key count

6. **System Resources**
   - CPU load (1m, 5m, 15m averages)
   - RAM usage and swap
   - Disk usage (root, docker)
   - File descriptor usage

7. **Kernel Optimizations**
   - `vm.swappiness` (should be <= 10)
   - `vm.max_map_count` (should be >= 262144)
   - Transparent Huge Pages (should be disabled)
   - TCP congestion control (should be BBR)

8. **Configuration Files**
   - `.env` present and readable
   - `docker-compose.yml` present
   - Required directories exist

9. **Backup Status**
   - Backup directory present
   - Last backup age (<48h warning)
   - Backup size

10. **MCP Server Container**
    - Status (running, healthy)
    - Health endpoint response
    - Logs (last 5 lines on error)

**Exit Codes:**
- `0`: All checks passed
- `1`: Any critical check failed
- `2`: Warnings only (non-critical)

---

## Script Development Patterns

### Bash Template (Reusable)

```bash
#!/bin/bash
set -euo pipefail

# Script: my-script.sh
# Purpose: What this script does
# Usage: ./my-script.sh [OPTIONS]

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMEOUT="${TIMEOUT:-10}"
MAX_RETRIES="${MAX_RETRIES:-3}"

log() { printf '%s\n' "$*" >&2; }
info() { log "$(printf '%b' "${BLUE}i${NC}") $*"; }
success() { log "$(printf '%b' "${GREEN}ok${NC}") $*"; }
warn() { log "$(printf '%b' "${YELLOW}warn${NC}") $*"; }
error() { log "$(printf '%b' "${RED}err${NC}") $*"; exit 1; }

main() {
  info "Validating prerequisites..."
  [[ -f "$PROJECT_ROOT/.env" ]] || error ".env file not found"
  command -v docker >/dev/null || error "Docker not installed"
  success "Script completed"
}

main "$@"
```

### Error Handling Pattern

```bash
set -euo pipefail
trap 'rm -f /tmp/tempfile 2>/dev/null' EXIT

if ! command -v docker &>/dev/null; then
  echo "ERROR: Docker not found" >&2; exit 1
fi

curl -f "$URL" || {
  echo "WARNING: Failed to reach $URL, retrying..." >&2
  sleep 5
  curl -f "$URL" || exit 1
}
```

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
