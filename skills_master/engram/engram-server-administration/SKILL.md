---
name: engram-server-administration
description: Use when administering the Engram production server (acdev-devnode, 100.78.187.5) — SSH access, Docker service management, container health/logs, API key rotation, credential management, backup/restore (Redis, Weaviate), DNS/SSL config, disk management, or SFTP deployment. Always via Tailscale, never public IP.
---

# Engram Server Administration

## Production Host

| Property | Value |
|---|---|
| **Hostname** | acdev-devnode |
| **Tailscale** | acdev-devnode.icefish-discus.ts.net |
| **IP** | 100.78.187.5 |
| **OS** | Ubuntu, i5 10C 16GB 1TB |
| **Role** | All Engram services (Docker) |
| **Path** | /opt/engram/Engram-Platform |

**NEVER use public IP for SSH. Always Tailscale.**

```bash
ssh root@100.78.187.5   # acdev-devnode
```

---

## Tailscale Infrastructure

| Host | Tailscale IP | Role |
|---|---|---|
| acdev-devnode | 100.78.187.5 | Engram production (Docker) |
| alex-macbookm4pro | 100.117.68.96 | Daily driver, M4 Pro 48GB |
| alex-home-pc | 100.114.241.115 | GPU dev, SonarQube, RTX3090 |
| vd-syd-dc-hv01 | 100.118.114.56 | Sydney PVE hypervisor |
| proxy01 | 100.111.195.74 | Traefik v3 reverse proxy |
| web01 | 100.107.75.57 | Nginx static sites |
| docker01 | 100.125.96.56 | Docker CE (non-Engram) |
| db01 | 100.109.96.107 | PostgreSQL 16 |
| ops01 | 100.90.175.111 | Prometheus + Grafana + Loki |

### Sydney Hypervisor VMs (vd-syd-dc-hv01)

| VM | ID | Type | LAN IP | Role |
|---|---|---|---|---|
| fw01 | 100 | VM | 10.10.0.1 | OPNsense firewall/DHCP |
| proxy01 | 101 | LXC | 10.10.0.10 | Traefik v3 + Redis 7 |
| web01 | 102 | LXC | 10.10.0.20 | Nginx 1.29.7 + PHP-FPM |
| docker01 | 103 | VM | 10.10.0.30 | Docker CE 29.3.1 |
| db01 | 104 | VM | 10.10.0.40 | PostgreSQL 16 |
| ops01 | 107 | VM | 10.10.0.57 | Prometheus + Grafana |

**Access via PVE host:**
```bash
ssh root@100.118.114.56              # PVE host
pct exec 101 -- bash                 # proxy01 (LXC)
pct exec 102 -- bash                 # web01 (LXC)
ssh root@10.10.0.30                  # docker01 (from PVE)
```

---

## Docker Service Management

### Startup / Shutdown

```bash
# Full stack
cd /opt/engram/Engram-Platform
docker compose up -d                 # Start all services
docker compose down                  # Stop all services

# Single service
docker compose up -d memory-api      # Start one
docker compose restart memory-api    # Restart one
docker compose stop memory-api       # Stop one

# Rebuild after code changes
docker compose build memory-api      # Rebuild image
docker compose up -d memory-api      # Recreate container

# Force recreate (picks up .env changes)
docker compose up -d --force-recreate memory-api
```

### Containers (8 services)

| Container | Image | Internal Port | Health Check |
|---|---|---|---|
| engram-memory-api | engram-memory-api | 8000 | GET /health |
| engram-crawler-api | crawl4ai-engram | 11235 | GET /health |
| engram-mcp-server | engram-mcp-server | 3000 | GET /health |
| engram-platform-frontend | engram-platform-frontend | 3000 | GET / |
| engram-weaviate | weaviate:1.27.0 | 8080 | GET /v1/.well-known/ready |
| engram-memory-redis | redis:7-alpine | 6379 | redis-cli ping |
| engram-crawler-redis | redis:7-alpine | 6379 | redis-cli ping |
| engram-nginx | nginx:alpine | 80/443 | — |

### Health Checks

```bash
# All containers
docker compose ps

# Individual service health
curl -s http://localhost:8000/health          # Memory API (from devnode)
curl -s http://localhost:8080/v1/.well-known/ready  # Weaviate
docker exec engram-memory-redis redis-cli ping      # Redis

# Full stack health script
for svc in memory-api:8000 weaviate:8080; do
  host=$(echo $svc | cut -d: -f1)
  port=$(echo $svc | cut -d: -f2)
  code=$(docker exec engram-nginx curl -s -o /dev/null -w '%{http_code}' http://$host:$port/health 2>/dev/null)
  echo "$host: $code"
done
```

### Logs

```bash
docker logs engram-memory-api --tail 50       # Last 50 lines
docker logs engram-memory-api -f              # Follow live
docker logs engram-memory-api --since 1h      # Last hour
docker logs engram-memory-api 2>&1 | grep ERROR  # Filter errors
```

---

## API Key Management

```bash
API=http://100.78.187.5:8000
KEY=88uCZeOw0RPvbEO3kBoWe-phek19u5R8vu1ACvZxWNc

# List all keys
curl -s -H "X-API-Key: $KEY" $API/admin/keys | python3 -m json.tool

# Create new key
curl -s -X POST -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"name":"New Key"}' $API/admin/keys

# Revoke a key
curl -s -X DELETE -H "X-API-Key: $KEY" $API/admin/keys/<key_id>

# View audit log
curl -s -H "X-API-Key: $KEY" "$API/admin/audit-log?limit=10"
```

---

## Credential Rotation

### API Keys
Create new key via `/admin/keys`, update all clients, revoke old key.

### JWT Secret
```bash
# Generate new secret
openssl rand -base64 32
# Update in /opt/engram/Engram-Platform/.env (JWT_SECRET=...)
# Restart: docker compose up -d --force-recreate memory-api
```

### Clerk Keys
Update in `.env`: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`
Rebuild frontend: `docker compose build platform-frontend && docker compose up -d platform-frontend`

---

## Backup & Restore

### Redis Backup
```bash
# Trigger RDB snapshot
docker exec engram-memory-redis redis-cli BGSAVE
# Copy RDB file
docker cp engram-memory-redis:/data/dump.rdb ./backup-redis-$(date +%Y%m%d).rdb
```

### Weaviate Backup
```bash
# Volume backup
docker compose stop weaviate
docker run --rm -v engram-platform_weaviate_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/weaviate-backup-$(date +%Y%m%d).tar.gz /data
docker compose up -d weaviate
```

### Full Platform Backup
```bash
# .env + Redis + Weaviate volumes
cp /opt/engram/Engram-Platform/.env ./backup-env-$(date +%Y%m%d)
```

### Restore Redis
```bash
docker compose stop memory-api
docker cp ./backup-redis.rdb engram-memory-redis:/data/dump.rdb
docker compose restart memory-redis
docker compose up -d memory-api
```

---

## DNS & SSL

| Domain | Target | Status |
|---|---|---|
| memory.velocitydigi.com | Landing site | Active |
| app.velocitydigi.com | Dashboard | DNS pending |
| *.velocitydigi.com | Wildcard cert | Active |

**SSL cert location:** Mounted into nginx container via Docker volumes.

**No Cloudflare API keys available** — DNS changes require Cloudflare dashboard login.

---

## Disk Management

```bash
# Docker disk usage
docker system df

# Volume sizes
docker system df -v | grep engram

# Prune unused images/containers
docker system prune -f

# Check host disk
df -h /
```

---

## SFTP Deployment

```bash
# From local machine to devnode
sftp root@100.78.187.5:/opt/engram/Engram-Platform/frontend/app/
put <local-file>

# Then rebuild
ssh root@100.78.187.5 "cd /opt/engram/Engram-Platform && docker compose build platform-frontend && docker compose up -d platform-frontend"
```
