---
name: engram-docker-services
description: Use when managing Engram Docker Compose services — starting, stopping, rebuilding, or debugging containers. Covers 8 services (memory-api, crawler-api, mcp-server, platform-frontend, weaviate, redis x2, nginx), volumes, health checks, resource limits, security hardening, and network configuration.
---

# Engram Docker Services

**Compose file**: `Engram-Platform/docker-compose.yml`
**Production path**: `/opt/engram/Engram-Platform/docker-compose.yml`

## Services (8 containers)

| Service | Container | Image | Port | Memory Limit | Depends On |
|---|---|---|---|---|---|
| memory-api | engram-memory-api | engram-memory-api (build) | 8000 | 768M | weaviate (healthy), memory-redis (healthy) |
| crawler-api | engram-crawler-api | crawl4ai-engram (build) | 11235 | 2048M | crawler-redis (healthy), memory-api (healthy) |
| mcp-server | engram-mcp-server | engram-mcp-server (build) | 3000 | 256M | memory-api (healthy) |
| platform-frontend | engram-platform-frontend | engram-platform-frontend (build) | 3000 | 512M | — |
| weaviate | engram-weaviate | semitechnologies/weaviate:1.27.0 | 8080 | 1536M | — |
| memory-redis | engram-memory-redis | redis:7-alpine | 6379 | 512M | — |
| crawler-redis | engram-crawler-redis | redis:7-alpine | 6379 | 256M | — |
| nginx | engram-nginx | nginx:alpine | 80, 443 | — | all services |

## Build Contexts

```yaml
memory-api:
  build:
    context: ../Engram-AiMemory
    dockerfile: docker/Dockerfile

crawler-api:
  build:
    context: ../Engram-AiCrawler/01_devroot
    dockerfile: Dockerfile

mcp-server:
  build:
    context: ../Engram-MCP
    dockerfile: docker/Dockerfile

platform-frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
    args:
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
      - NEXT_PUBLIC_APP_URL
```

## Volumes (11 named)

| Volume | Used By | Purpose |
|---|---|---|
| weaviate_data | weaviate | Vector database storage |
| memory_redis_data | memory-redis | Redis RDB persistence |
| crawler_redis_data | crawler-redis | Crawler Redis persistence |
| crawler_cache | crawler-api | Crawl4AI browser cache |
| crawler_logs | crawler-api | Crawler log files |
| crawler_hot | crawler-api | Hot tier data |
| crawler_warm | crawler-api | Warm tier data |
| crawler_cold | crawler-api | Cold tier data |
| crawler_archive | crawler-api | Archive tier data |
| crawler_chroma_data | crawler-api | ChromaDB vectors |
| crawler_supervisor | crawler-api | Supervisord state |

## Security Hardening

```yaml
# Applied to memory-api, mcp-server, platform-frontend
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp
  - /var/tmp
```

## Health Checks

```yaml
memory-api:
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
    interval: 30s
    timeout: 10s
    retries: 3

weaviate:
  healthcheck:
    test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/v1/.well-known/ready"]
    interval: 10s
    timeout: 5s
    retries: 5

memory-redis:
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 3
```

## Common Commands

```bash
cd /opt/engram/Engram-Platform

# Full stack
docker compose up -d
docker compose down
docker compose ps

# Single service operations
docker compose build memory-api
docker compose up -d memory-api
docker compose restart memory-api
docker compose logs -f memory-api --tail 50

# Force recreate (picks up .env changes)
docker compose up -d --force-recreate memory-api

# View resource usage
docker stats --no-stream

# Prune unused images
docker system prune -f
```

## Network

All services on `engram-platform-network` (bridge). Nginx has aliases: `memory.velocitydigi.com`, `engram.velocitydigi.com`, `dv-syd-host01.icefish-discus.ts.net`.

Crawler-api has `extra_hosts: host.docker.internal:host-gateway` for LM Studio access.

## Resource Budget

| Service | Limit | Reservation |
|---|---|---|
| memory-api | 768M | 256M |
| crawler-api | 2048M | 512M |
| mcp-server | 256M | 128M |
| platform-frontend | 512M | 256M |
| weaviate | 1536M | 512M |
| memory-redis | 512M | 128M |
| crawler-redis | 256M | 128M |
| **Total** | **5,888M** | **1,920M** |
