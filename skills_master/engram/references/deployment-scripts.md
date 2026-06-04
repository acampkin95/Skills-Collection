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

