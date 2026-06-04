---
name: docker-compose
description: Docker Compose orchestration for local development and production deployment with multi-container services. Use this skill when docker-compose, docker compose, docker-compose.yml, Dockerfile, services:, depends_on, container orchestration, multi-container, Docker networking, health checks, BuildKit, volume management, compose watch, multi-stage builds. Use this skill when setting up local dev environment with Docker, defining service dependencies and orchestration, configuring container networking and communication, implementing health checks and restart policies, optimizing Docker builds with multi-stage patterns, managing persistent volumes, debugging container issues, and deploying production applications with Docker Compose.
---

# Docker & Docker Compose Skill

Read the relevant reference file before starting work.

## Quick Navigation

| Task | Reference |
|------|-----------|
| Multi-stage builds, distroless, layer caching | `references/multi-stage-builds.md` |
| Compose overrides, profiles, health checks, patterns | `references/compose-patterns.md` |
| Container debugging, logs, networking, volumes | `references/debugging.md` |

## Dockerfile Best Practices

### Layer Ordering (Most Stable First)

```dockerfile
FROM node:22-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build
```

**Rules:**
- Copy dependency manifests before source code (maximizes cache hits)
- Never use `latest` tag — pin versions (`node:22.12-slim`, `python:3.13-slim`)
- Combine `RUN` commands with `&&` and clean apt caches in same layer
- Copy patterns: `COPY package.json package-lock.json ./` for deps, then `COPY . .` for source

### Multi-Stage Build (Minimal Production Image)

```dockerfile
FROM node:22-slim AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-slim AS production
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

Example: 400MB (builder) → 150MB (production)

### .dockerignore

```
node_modules
.git
.github
.env*
dist
.next
coverage
docker-compose*.yml
Dockerfile*
```

Without `.dockerignore`, `COPY . .` sends everything (including `node_modules`, `.git`) to the daemon.

## Docker Compose v3.8 - v5 Essentials

### Service Definition

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
      args:
        NODE_ENV: development
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/myapp
      REDIS_URL: redis://cache:6379
    env_file:
      - .env.local
    volumes:
      - ./src:/app/src
      - app_node_modules:/app/node_modules
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    networks:
      - backend
    restart: unless-stopped

  db:
    image: postgres:17
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s
    networks:
      - backend

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - backend

volumes:
  pgdata:
  redisdata:
  app_node_modules:

networks:
  backend:
    driver: bridge
```

### Volumes

```yaml
volumes:
  pgdata:          # Named volume — Docker-managed
    driver: local
```

In service definition:
- Named volume: `- pgdata:/var/lib/postgresql/data`
- Bind mount: `- ./data:/app/data` (dev only)
- tmpfs: `tmpfs: ['/app/tmp']` (in-memory)

**Rules:**
- Use named volumes for databases (not bind mounts)
- Use bind mounts only for development
- Named volume for `node_modules` prevents host/container conflicts

### Networks

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true    # No external access

services:
  app:
    networks:
      - frontend
      - backend
  db:
    networks:
      - backend       # Only on internal network
```

Services reach each other by service name as hostname (`db:5432`, `cache:6379`).

### Health Checks

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 30s
```

Common commands:
- PostgreSQL: `pg_isready -U postgres`
- Redis: `redis-cli ping`
- HTTP: `curl -f http://localhost:PORT/health || exit 1`
- MySQL: `mysqladmin ping -h localhost`
- MongoDB: `mongosh --eval "db.adminCommand('ping')"`

### depends_on with Conditions

```yaml
depends_on:
  db:
    condition: service_healthy
  cache:
    condition: service_started
  migrations:
    condition: service_completed_successfully
```

### Environment Variables

```yaml
environment:
  NODE_ENV: production
  LOG_LEVEL: info

env_file:
  - .env
  - .env.local    # Overrides .env
```

Never put secrets in `docker-compose.yml`; use `env_file` instead.

### Port Mapping

```yaml
ports:
  - "3000:3000"       # host:container
  - "8080:80"         # Map container 80 to host 8080
  - "127.0.0.1:5432:5432"  # Bind only to localhost
```

Bind databases to `127.0.0.1` to prevent external access.

### Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: "2.0"
      memory: 1G
    reservations:
      cpus: "0.5"
      memory: 256M
```

## Compose Watch (2025+)

```yaml
services:
  app:
    build:
      context: .
      target: development
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
        - action: rebuild
          path: ./package.json
        - action: sync+restart
          path: ./config
          target: /app/config
```

```bash
docker compose watch
```

| Action | When to Use |
|--------|-------------|
| `sync` | Source files with hot reload (Vite, Next.js) |
| `rebuild` | Dependency changes (package.json, requirements.txt) |
| `sync+restart` | Config files needing process restart |

## Compose Profiles

```yaml
services:
  app:
    build: .                    # No profile — always starts
  mailhog:
    image: mailhog/mailhog
    profiles: [debug]           # Only with --profile debug
  prometheus:
    image: prom/prometheus
    profiles: [monitoring]
```

```bash
docker compose up                       # Unprofiied services only
docker compose --profile debug up       # + debug services
docker compose --profile debug --profile monitoring up  # Both
```

## Common Commands

```bash
docker compose up -d                    # Start services
docker compose up -d --build            # Start with rebuild
docker compose down                     # Stop and remove containers
docker compose down -v                  # Also remove volumes
docker compose logs -f app              # Follow logs
docker compose exec app sh              # Run command in container
docker compose run --rm app npm test    # One-off command
docker compose up -d --scale worker=3   # Scale service
docker compose stats                    # Resource usage
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `COPY . .` without `.dockerignore` | Create `.dockerignore` |
| Using `latest` tag | Pin versions (`node:22-slim`, `postgres:17`) |
| Running as root | Add `USER appuser` after creating user |
| DB volume as bind mount in prod | Use named volumes |
| `depends_on` without `condition` | Add `condition: service_healthy` |
| Secrets in `environment:` block | Use `env_file` |
| Exposing DB ports | Bind to `127.0.0.1:5432:5432` |
| `npm install` in Dockerfile | Use `npm ci` (deterministic) |
| Forgetting `--rm` with run | Stopped containers accumulate |
| Not cleaning apt cache | Clean in same RUN layer |

See reference files for deep dives.
