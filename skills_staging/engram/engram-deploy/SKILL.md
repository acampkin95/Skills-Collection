---
name: engram-deploy
description: Use when deploying Engram Platform updates to acdev-devnode — syncing code changes, rebuilding Docker services, protecting existing memories with pre-deploy backups, handling SSL cert issues, or establishing the git-based update workflow. Covers rsync deploy, service-selective rebuilds, memory backup/restore, nginx cert management, and health verification.
---

# Engram Deploy — Update Process

**Production host**: `acdev-devnode` | `100.78.187.5` | path: `/opt/engram/`
**Compose file**: `/opt/engram/Engram-Platform/docker-compose.yml`

---

## Standard Update Flow

### 1. Commit locally

```bash
cd /Users/alex/Projects/Dev/LIVE/Production/09_EngramPlatform
git add <files>
git commit -m "type(scope): description"
```

### 2. Backup memories on devnode (ALWAYS before any deploy)

```bash
ssh root@100.78.187.5 "cd /opt/engram && bash scripts/deploy-unified.sh backup quick"
# Backs up: Redis dump.rdb (API keys, audit log), Weaviate schema, .env
# Backup location: /opt/engram/backups/quick-YYYYMMDD-HHMMSS/
```

### 3. Rsync changed source directories

Rsync only the build contexts that changed. Always exclude secrets and build artifacts:

```bash
DEVNODE=root@100.78.187.5
REMOTE=/opt/engram
EXCLUDE="--exclude=node_modules --exclude=.next --exclude=dist --exclude=.venv --exclude=__pycache__ --exclude='*.pyc' --exclude=.env --exclude=.env.local"

# memory-api (Engram-AiMemory changes)
rsync -avz $EXCLUDE \
  Engram-AiMemory/packages/core/src/ \
  $DEVNODE:$REMOTE/Engram-AiMemory/packages/core/src/

# platform-frontend (Next.js frontend changes)
rsync -avz $EXCLUDE \
  Engram-Platform/frontend/ \
  $DEVNODE:$REMOTE/Engram-Platform/frontend/

# mcp-server (Engram-MCP changes)
rsync -avz $EXCLUDE \
  Engram-MCP/src/ \
  $DEVNODE:$REMOTE/Engram-MCP/src/

# docker-compose + nginx config
rsync -avz \
  Engram-Platform/docker-compose.yml \
  $DEVNODE:$REMOTE/Engram-Platform/docker-compose.yml
rsync -avz \
  Engram-Platform/nginx/nginx.conf \
  $DEVNODE:$REMOTE/Engram-Platform/nginx/nginx.conf
```

### 4. Rebuild affected services

Only rebuild services whose source changed:

| Changed area | Service to rebuild |
|---|---|
| `Engram-AiMemory/` | `memory-api` |
| `Engram-MCP/` | `mcp-server` |
| `Engram-Platform/frontend/` | `platform-frontend` |
| `Engram-AiCrawler/` | `crawler-api` |
| `nginx/nginx.conf` only | **no rebuild** — just reload |

```bash
# Rebuild backend services (parallel)
ssh root@100.78.187.5 "cd /opt/engram/Engram-Platform && \
  docker compose build memory-api mcp-server && \
  docker compose up -d --force-recreate memory-api mcp-server"

# Rebuild frontend
ssh root@100.78.187.5 "cd /opt/engram/Engram-Platform && \
  docker compose build platform-frontend && \
  docker compose up -d --force-recreate platform-frontend"

# nginx config change only (no rebuild)
ssh root@100.78.187.5 "docker exec engram-nginx nginx -s reload"
# OR if nginx needs restart:
ssh root@100.78.187.5 "cd /opt/engram/Engram-Platform && docker compose restart nginx"
```

### 5. Health check

```bash
ssh root@100.78.187.5 "
  docker ps --format 'table {{.Names}}\t{{.Status}}' | grep engram
  curl -sf http://localhost:8000/health
  curl -sk -o /dev/null -w 'nginx HTTPS: %{http_code}\n' https://127.0.0.1/
"
# Expected: all containers Up (healthy), memory-api {"status":"healthy",...}, nginx 200
```

---

## SSL Certificate Management

**Cert location on host**: `/etc/letsencrypt/live/velocitydigi.com/`
**Cert location for nginx**: `/opt/engram/Engram-Platform/certs/velocitydigi.crt` + `.key`

nginx.conf references `velocitydigi.crt` / `velocitydigi.key` — these must exist in the certs volume.

### Copy certs after Let's Encrypt renewal

```bash
ssh root@100.78.187.5 "
  cp /etc/letsencrypt/live/velocitydigi.com/fullchain.pem \
     /opt/engram/Engram-Platform/certs/velocitydigi.crt
  cp /etc/letsencrypt/live/velocitydigi.com/privkey.pem \
     /opt/engram/Engram-Platform/certs/velocitydigi.key
  chmod 644 /opt/engram/Engram-Platform/certs/velocitydigi.crt
  chmod 600 /opt/engram/Engram-Platform/certs/velocitydigi.key
  docker exec engram-nginx nginx -s reload
"
```

### Automate cert renewal copy (recommended one-time setup)

```bash
# Add to /etc/letsencrypt/renewal-hooks/deploy/ on devnode
ssh root@100.78.187.5 "cat > /etc/letsencrypt/renewal-hooks/deploy/engram-nginx.sh << 'EOF'
#!/bin/bash
cp /etc/letsencrypt/live/velocitydigi.com/fullchain.pem /opt/engram/Engram-Platform/certs/velocitydigi.crt
cp /etc/letsencrypt/live/velocitydigi.com/privkey.pem /opt/engram/Engram-Platform/certs/velocitydigi.key
chmod 644 /opt/engram/Engram-Platform/certs/velocitydigi.crt
chmod 600 /opt/engram/Engram-Platform/certs/velocitydigi.key
docker exec engram-nginx nginx -s reload
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/engram-nginx.sh"
```

---

## Memory Protection

### What gets backed up (quick backup)

| Data | Method | Location |
|---|---|---|
| Memory Redis (API keys, audit log, cache) | `BGSAVE` + `docker cp dump.rdb` | `/opt/engram/backups/quick-*/memory-redis.rdb` |
| Crawler Redis | `BGSAVE` + `docker cp dump.rdb` | `/opt/engram/backups/quick-*/crawler-redis.rdb` |
| Weaviate schema | `GET /v1/schema` | `/opt/engram/backups/quick-*/weaviate-schema.json` |
| `.env` | file copy | `/opt/engram/backups/quick-*/` |

**Weaviate vector data is NOT in the quick backup** — use full backup for that:

```bash
ssh root@100.78.187.5 "cd /opt/engram && bash scripts/deploy-unified.sh backup full"
```

### Restore from backup

```bash
# Restore Redis (if memories corrupted after deploy)
ssh root@100.78.187.5 "
  BACKUP=/opt/engram/backups/quick-YYYYMMDD-HHMMSS
  cd /opt/engram/Engram-Platform
  docker compose stop memory-api
  docker cp \$BACKUP/memory-redis.rdb engram-memory-redis:/data/dump.rdb
  docker compose restart memory-redis
  docker compose up -d memory-api
"
```

---

## One-Time: Git Setup on Devnode (future releases)

Currently devnode has no git repo — deploys use rsync. To enable `git pull`-based updates:

```bash
# 1. Generate deploy key on devnode
ssh root@100.78.187.5 "ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github -N '' -C 'engram-devnode'"
ssh root@100.78.187.5 "cat ~/.ssh/id_ed25519_github.pub"
# → Add this public key as a Deploy Key in GitHub repo settings (read-only)

# 2. Init git repo (code already present)
ssh root@100.78.187.5 "
  cd /opt/engram
  git init
  git remote add origin git@github.com:acampkin95/Engram-platform.git
  git config core.sshCommand 'ssh -i ~/.ssh/id_ed25519_github'
  git fetch origin
  git checkout -b main --track origin/main
  git reset --hard origin/main
"

# 3. Future update command (after git is set up)
# ssh root@100.78.187.5 "cd /opt/engram && git pull && \
#   docker compose -f Engram-Platform/docker-compose.yml build memory-api platform-frontend && \
#   docker compose -f Engram-Platform/docker-compose.yml up -d --force-recreate memory-api platform-frontend"
```

---

## Quick Reference

```bash
# Full update (all services changed)
DEVNODE=root@100.78.187.5
ssh $DEVNODE "cd /opt/engram && bash scripts/deploy-unified.sh backup quick"
rsync -avz --exclude=node_modules --exclude=.next --exclude=.venv --exclude=__pycache__ \
  --exclude=.env --exclude=.env.local \
  Engram-AiMemory/packages/core/src/ Engram-MCP/src/ \
  $DEVNODE:/opt/engram/Engram-AiMemory/packages/core/src/ && \
rsync -avz --exclude=node_modules --exclude=.next --exclude=.env.local \
  Engram-Platform/frontend/ $DEVNODE:/opt/engram/Engram-Platform/frontend/
ssh $DEVNODE "cd /opt/engram/Engram-Platform && \
  docker compose build memory-api mcp-server platform-frontend && \
  docker compose up -d --force-recreate memory-api mcp-server platform-frontend && \
  docker compose restart nginx"
ssh $DEVNODE "curl -sf http://localhost:8000/health"
```
