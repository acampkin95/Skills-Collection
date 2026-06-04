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

