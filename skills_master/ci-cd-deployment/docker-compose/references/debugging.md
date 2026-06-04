# Docker Debugging Reference

## Container Inspection

### View Running Containers

```bash
# All running containers with resource usage
docker compose ps
docker compose stats

# Detailed container info
docker inspect <container_name_or_id>

# Specific fields
docker inspect --format='{{.State.Status}}' myapp-app-1
docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' myapp-app-1
docker inspect --format='{{json .State.Health}}' myapp-app-1 | jq
```

### Execute Commands in Running Container

```bash
# Interactive shell
docker compose exec app sh
docker compose exec app bash

# Run a specific command
docker compose exec app node -e "console.log(process.env.NODE_ENV)"
docker compose exec db psql -U postgres -d myapp -c "SELECT count(*) FROM users"

# As root (even if USER is set in Dockerfile)
docker compose exec -u root app sh
```

### One-Off Containers

```bash
# Run command and remove container when done
docker compose run --rm app npm test
docker compose run --rm app npx prisma migrate deploy

# Override entrypoint
docker compose run --rm --entrypoint sh app

# With environment variable
docker compose run --rm -e DEBUG=true app npm run debug
```

---

## Logs

### View Logs

```bash
# Follow logs for all services
docker compose logs -f

# Follow logs for specific service
docker compose logs -f app

# Last 100 lines
docker compose logs --tail 100 app

# Logs with timestamps
docker compose logs -t app

# Logs since a specific time
docker compose logs --since "2025-01-29T10:00:00" app
docker compose logs --since 30m app        # Last 30 minutes

# Multiple services
docker compose logs -f app worker
```

### Log Analysis

```bash
# Search logs for errors
docker compose logs app 2>&1 | grep -i error

# Count error occurrences
docker compose logs app 2>&1 | grep -ci "error"

# Follow only error lines
docker compose logs -f app 2>&1 | grep --line-buffered -i "error\|fatal\|panic"

# Export logs to file
docker compose logs --no-color app > app.log 2>&1
```

### Log Rotation (Prevent Disk Fill)

```yaml
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

Check current log size:
```bash
# Find Docker log files
docker inspect --format='{{.LogPath}}' myapp-app-1
sudo du -sh /var/lib/docker/containers/*/

# On Docker Desktop (macOS)
docker run --rm -v /var/lib/docker:/docker alpine du -sh /docker/containers/*/
```

---

## Networking Troubleshooting

### Inspect Networks

```bash
# List networks
docker network ls

# Inspect a specific network
docker network inspect myapp_backend

# See which containers are on a network
docker network inspect myapp_backend --format='{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}'
```

### Test Connectivity Between Containers

```bash
# From inside a container, test connectivity to another service
docker compose exec app sh -c "ping -c 3 db"
docker compose exec app sh -c "nc -zv db 5432"
docker compose exec app sh -c "wget -qO- http://api:3000/health"

# DNS resolution
docker compose exec app sh -c "nslookup db"
docker compose exec app sh -c "getent hosts db"
```

### Install Network Tools (Missing in Slim Images)

```bash
# Debian/Ubuntu-based
docker compose exec -u root app sh -c "apt-get update && apt-get install -y curl iputils-ping netcat-openbsd dnsutils"

# Alpine-based
docker compose exec -u root app sh -c "apk add --no-cache curl bind-tools"
```

### Common Networking Issues

| Problem | Symptom | Fix |
|---------|---------|-----|
| Service name not resolving | `Name does not resolve` | Ensure both services are on the same network |
| Connection refused | `Connection refused` | Service isn't listening on the expected port/interface |
| Port conflict | `Bind: address already in use` | Change host port or stop conflicting process |
| Container can't reach internet | `Could not resolve host` | Check `internal: true` on network, DNS config |
| Intermittent connection failures | Random timeouts | Check healthcheck + `depends_on` conditions |

### Port Debugging

```bash
# Check what's listening inside the container
docker compose exec app sh -c "ss -tlnp"
docker compose exec app sh -c "netstat -tlnp"

# Check host port bindings
docker compose port app 3000
docker compose ps --format "table {{.Name}}\t{{.Ports}}"

# Check for port conflicts on host
lsof -i :3000
ss -tlnp | grep 3000
```

---

## Volume Troubleshooting

### Inspect Volumes

```bash
# List all volumes
docker volume ls

# Inspect a specific volume
docker volume inspect myapp_pgdata

# Check volume contents
docker run --rm -v myapp_pgdata:/data alpine ls -la /data

# Check volume disk usage
docker system df -v | grep -A 5 "VOLUME"
```

### Common Volume Issues

| Problem | Symptom | Fix |
|---------|---------|-----|
| Volume masking | Files updated on host don't appear in container | Named volume takes precedence. `docker compose down -v` to recreate |
| Permission denied | `EACCES: permission denied` | Match container user UID/GID with volume owner (see below) |
| Data not persisting | Data lost on `docker compose down` | Use named volumes (not anonymous). Don't use `-v` flag unless intentional |
| Stale node_modules | Build errors after dependency change | Remove volume: `docker volume rm myapp_app_node_modules` |
| Slow bind mounts (macOS) | Very slow file I/O | Use Compose Watch instead, or `:cached` / VirtioFS |

### Fix Permission Issues

```dockerfile
# In Dockerfile — create user with specific UID
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

# Ensure the app directory is owned by appuser
RUN chown -R appuser:appgroup /app
USER appuser
```

```yaml
# In docker-compose.yml — match host UID
services:
  app:
    user: "${UID:-1000}:${GID:-1000}"
    volumes:
      - ./data:/app/data
```

```bash
# Fix existing volume permissions
docker compose exec -u root app chown -R appuser:appgroup /app/data
```

---

## Resource Monitoring

### Real-Time Stats

```bash
# CPU, memory, network, I/O for all containers
docker compose stats

# Specific service
docker stats myapp-app-1

# One-shot (not streaming)
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

### Disk Usage

```bash
# Overall Docker disk usage
docker system df

# Detailed breakdown
docker system df -v

# Find large images
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k3 -h

# Clean up unused resources
docker system prune              # Dangling images, stopped containers, unused networks
docker system prune -a           # Also remove unused images (not just dangling)
docker system prune -a --volumes # Nuclear option — removes everything unused including volumes
```

### Memory Issues

```bash
# Check container memory limit and usage
docker stats --no-stream --format "{{.Name}}: {{.MemUsage}} / {{.MemPerc}}"

# Check if OOM killer triggered
docker inspect --format='{{.State.OOMKilled}}' myapp-app-1

# Check kernel OOM events
dmesg | grep -i "oom\|killed"
```

---

## Build Debugging

### Inspect Build Steps

```bash
# Build with verbose output
docker compose build --no-cache --progress=plain app

# Build specific stage
docker compose build --build-arg BUILDKIT_PROGRESS=plain app

# Build only up to a specific stage
docker build --target builder -t debug-build .

# Run shell in intermediate build stage
docker build --target builder -t debug-build .
docker run --rm -it debug-build sh

# Show build history (layers)
docker history myapp-app --no-trunc
```

### Cache Debugging

```bash
# Build without cache
docker compose build --no-cache

# Show what cache is being used
BUILDKIT_PROGRESS=plain docker compose build 2>&1 | grep -E "CACHED|DONE"

# Clear build cache
docker builder prune

# Clear all build cache
docker builder prune -a
```

---

## Health Check Debugging

```bash
# Check health status
docker inspect --format='{{json .State.Health}}' myapp-app-1 | jq

# Watch health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' myapp-app-1

# Test health check command manually
docker compose exec app curl -f http://localhost:3000/health
docker compose exec db pg_isready -U postgres

# Override health check for debugging
docker compose exec app sh -c "curl -v http://localhost:3000/health"
```

---

## Process Debugging

```bash
# List processes inside a container
docker compose exec app ps aux
docker compose top app

# Check container events
docker events --filter container=myapp-app-1

# Check why container exited
docker inspect --format='{{.State.ExitCode}} {{.State.Error}}' myapp-app-1

# View container start command
docker inspect --format='{{.Config.Cmd}}' myapp-app-1
docker inspect --format='{{.Config.Entrypoint}}' myapp-app-1
```

### Common Exit Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 0 | Success | Normal exit |
| 1 | General error | Application crash, unhandled exception |
| 126 | Permission denied | Script not executable |
| 127 | Command not found | Wrong CMD/ENTRYPOINT, missing binary |
| 137 | SIGKILL (OOM) | Out of memory — increase memory limit |
| 139 | SIGSEGV | Segmentation fault — native code issue |
| 143 | SIGTERM | Graceful shutdown (docker stop) |

---

## Environment Variable Debugging

```bash
# List all env vars in running container
docker compose exec app env | sort

# Check specific variable
docker compose exec app sh -c 'echo $DATABASE_URL'

# Validate compose variable substitution
docker compose config | grep -A5 "environment"

# Check which .env file is loaded
docker compose --env-file .env.prod config
```

---

## Docker Desktop Debugging (macOS/Windows)

```bash
# Check Docker Desktop resource allocation
docker info | grep -E "Total Memory|CPUs"

# Reset Docker Desktop state (macOS)
# Docker Desktop → Troubleshoot → Clean / Purge data

# Check VirtioFS vs gRPC FUSE performance
docker info | grep "Storage Driver"

# macOS: Enable VirtioFS for faster bind mounts
# Docker Desktop → Settings → General → "Use VirtioFS"
```

---

## Quick Diagnostic Script

Run this to get a snapshot of your Docker Compose environment:

```bash
#!/bin/bash
echo "=== Docker Version ==="
docker version --format '{{.Server.Version}}'
docker compose version

echo -e "\n=== Running Containers ==="
docker compose ps

echo -e "\n=== Resource Usage ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo -e "\n=== Networks ==="
docker network ls --filter "name=$(basename $(pwd))"

echo -e "\n=== Volumes ==="
docker volume ls --filter "name=$(basename $(pwd))"

echo -e "\n=== Disk Usage ==="
docker system df

echo -e "\n=== Recent Errors ==="
docker compose logs --tail 20 2>&1 | grep -i "error\|fatal\|panic\|exception" | tail -10

echo -e "\n=== Health Status ==="
docker compose ps --format "table {{.Name}}\t{{.Status}}"
```
