# Compose Patterns Reference

## Dev/Prod Compose Overrides

### Base + Override Pattern

```yaml
# docker-compose.yml (base — shared config)
services:
  app:
    image: myapp:latest
    environment:
      NODE_ENV: production
    depends_on:
      db:
        condition: service_healthy
    networks:
      - backend

  db:
    image: postgres:17
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - backend

volumes:
  pgdata:

networks:
  backend:
```

```yaml
# docker-compose.override.yml (auto-loaded in development)
services:
  app:
    build:
      context: .
      target: development
    ports:
      - "3000:3000"
      - "9229:9229"         # Node.js debug port
    environment:
      NODE_ENV: development
      DEBUG: "app:*"
    volumes:
      - ./src:/app/src      # Hot reload
      - app_node_modules:/app/node_modules
    command: npm run dev

  db:
    ports:
      - "127.0.0.1:5432:5432"  # Expose locally for tools
    environment:
      POSTGRES_PASSWORD: localdev

volumes:
  app_node_modules:
```

```yaml
# docker-compose.prod.yml (explicit production overrides)
services:
  app:
    image: registry.example.com/myapp:${APP_VERSION:-latest}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "2.0"
          memory: 1G
        reservations:
          cpus: "0.5"
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  db:
    deploy:
      resources:
        limits:
          cpus: "4.0"
          memory: 4G
```

### Usage

```bash
# Development (auto-loads docker-compose.yml + docker-compose.override.yml)
docker compose up

# Production (explicitly specify files)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Validate merged config
docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```

**Rules:**
- `docker-compose.override.yml` is auto-loaded — never commit production secrets here
- Use `docker compose config` to preview the merged result
- Use `${VARIABLE:-default}` syntax for environment variable substitution

---

## Compose Profiles

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    # No profile — always starts

  db:
    image: postgres:17
    # No profile — always starts

  # === Debug Tools ===
  mailhog:
    image: mailhog/mailhog
    ports:
      - "8025:8025"
    profiles: [debug]

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@local.dev
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    profiles: [debug]

  # === Monitoring Stack ===
  prometheus:
    image: prom/prometheus:v2.53.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    profiles: [monitoring]

  grafana:
    image: grafana/grafana:11.0.0
    ports:
      - "3001:3000"
    profiles: [monitoring]

  # === Testing ===
  test-runner:
    build:
      context: .
      target: test
    command: npm test
    depends_on:
      db:
        condition: service_healthy
    profiles: [test]
```

```bash
docker compose up                                    # app + db
docker compose --profile debug up                    # + mailhog, pgadmin
docker compose --profile monitoring up               # + prometheus, grafana
docker compose --profile debug --profile monitoring up  # everything except test
docker compose --profile test run --rm test-runner   # run tests
```

---

## Health Checks — Patterns by Service Type

### HTTP API with Dedicated Health Endpoint

```yaml
app:
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"]
    interval: 10s
    timeout: 5s
    retries: 3
    start_period: 30s
```

Implement the health endpoint:

```typescript
// src/routes/health.ts
app.get("/health", async (req, res) => {
  try {
    await db.query("SELECT 1");
    res.json({ status: "healthy", db: "connected" });
  } catch (err) {
    res.status(503).json({ status: "unhealthy", db: "disconnected" });
  }
});
```

### Database Health Checks

```yaml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-postgres}"]
    interval: 5s
    timeout: 3s
    retries: 5
    start_period: 10s

mysql:
  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$$MYSQL_ROOT_PASSWORD"]
    interval: 5s
    timeout: 3s
    retries: 5

mongodb:
  healthcheck:
    test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Queue / Cache Health Checks

```yaml
redis:
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 3s
    retries: 5

rabbitmq:
  healthcheck:
    test: ["CMD-SHELL", "rabbitmq-diagnostics -q ping"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 30s
```

---

## Service Discovery and Internal Networking

Services communicate by **service name** within shared networks:

```yaml
services:
  api:
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/myapp
      REDIS_URL: redis://cache:6379
      QUEUE_URL: amqp://rabbitmq:5672
    networks:
      - backend

  worker:
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/myapp
      REDIS_URL: redis://cache:6379
    networks:
      - backend

  db:
    networks:
      - backend

  cache:
    networks:
      - backend
```

### Network Isolation Pattern

```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true    # No outbound internet access

services:
  nginx:
    networks: [frontend]
    ports: ["80:80", "443:443"]

  app:
    networks: [frontend, backend]   # Bridge between networks

  db:
    networks: [backend]             # Isolated — no external access

  cache:
    networks: [backend]
```

### Custom DNS Aliases

```yaml
services:
  app:
    networks:
      backend:
        aliases:
          - api.local          # Additional hostname
          - app.internal
```

---

## Logging Drivers

```yaml
services:
  app:
    logging:
      driver: json-file        # Default
      options:
        max-size: "10m"        # Rotate at 10MB
        max-file: "3"          # Keep 3 rotated files
        compress: "true"
```

| Driver | Use Case |
|--------|----------|
| `json-file` | Default, good for development |
| `local` | Optimized default with compression |
| `journald` | Systemd integration |
| `fluentd` | Centralized logging (EFK stack) |
| `awslogs` | AWS CloudWatch |
| `gcplogs` | Google Cloud Logging |

**Always set `max-size` and `max-file`** — without limits, logs grow unbounded and fill the disk.

---

## Restart Policies

```yaml
services:
  app:
    restart: unless-stopped     # Recommended for most services

  db:
    restart: always             # Critical infrastructure

  migration:
    restart: "no"               # One-shot tasks
```

| Policy | Behavior |
|--------|----------|
| `"no"` | Never restart (default). Use for one-shot tasks. |
| `always` | Always restart, even if stopped manually. |
| `unless-stopped` | Restart unless explicitly stopped. Best for services. |
| `on-failure` | Restart only on non-zero exit code. |

### With deploy (Compose v2):

```yaml
services:
  app:
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
```

---

## One-Shot Services (Migrations, Seeds)

```yaml
services:
  migrate:
    build:
      context: .
      target: migration
    command: npx prisma migrate deploy
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/myapp
    depends_on:
      db:
        condition: service_healthy
    restart: "no"
    profiles: [setup]

  seed:
    build:
      context: .
      target: migration
    command: npx prisma db seed
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/myapp
    depends_on:
      migrate:
        condition: service_completed_successfully
    restart: "no"
    profiles: [setup]

  app:
    depends_on:
      migrate:
        condition: service_completed_successfully
```

```bash
# Run migrations then start app
docker compose --profile setup up -d

# Or run migration separately
docker compose run --rm migrate
```

---

## Compose Watch (Development)

```yaml
services:
  app:
    build:
      context: .
      target: development
    develop:
      watch:
        # Sync source files — hot reload handles the rest
        - action: sync
          path: ./src
          target: /app/src
          ignore:
            - "**/*.test.ts"

        # Rebuild container when deps change
        - action: rebuild
          path: ./package.json
        - action: rebuild
          path: ./package-lock.json

        # Sync + restart for config changes
        - action: sync+restart
          path: ./config
          target: /app/config

  worker:
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
```

```bash
docker compose watch          # Start with file watching
docker compose up --watch     # Alternative syntax
```

---

## Variable Substitution

```yaml
# .env file (auto-loaded)
APP_VERSION=1.2.3
POSTGRES_PASSWORD=supersecret
REGISTRY=ghcr.io/myorg

# docker-compose.yml
services:
  app:
    image: ${REGISTRY}/app:${APP_VERSION:-latest}
    environment:
      DB_HOST: ${DB_HOST:-db}

  db:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Error: POSTGRES_PASSWORD is required}
```

| Syntax | Behavior |
|--------|----------|
| `${VAR}` | Value of VAR, empty string if unset |
| `${VAR:-default}` | Value of VAR, or `default` if unset/empty |
| `${VAR-default}` | Value of VAR, or `default` if unset (empty is kept) |
| `${VAR:?error}` | Value of VAR, or **error and abort** if unset/empty |

---

## Full Production Stack Example

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:1.27-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - certs:/etc/nginx/certs:ro
    depends_on:
      app:
        condition: service_healthy
    networks:
      - frontend
    restart: unless-stopped
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "3" }

  app:
    image: registry.example.com/app:${APP_VERSION}
    environment:
      NODE_ENV: production
      DATABASE_URL: postgresql://postgres:${DB_PASS}@db:5432/myapp
      REDIS_URL: redis://cache:6379
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
    deploy:
      replicas: 2
      resources:
        limits: { cpus: "2.0", memory: 1G }
    networks:
      - frontend
      - backend
    restart: unless-stopped

  worker:
    image: registry.example.com/app:${APP_VERSION}
    command: node dist/worker.js
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASS}@db:5432/myapp
      REDIS_URL: redis://cache:6379
    deploy:
      replicas: 2
      resources:
        limits: { cpus: "1.0", memory: 512M }
    networks:
      - backend
    restart: unless-stopped

  db:
    image: postgres:17
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASS}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
    deploy:
      resources:
        limits: { cpus: "4.0", memory: 4G }
    networks:
      - backend
    restart: always

  cache:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - backend
    restart: unless-stopped

volumes:
  pgdata:
  redisdata:
  certs:

networks:
  frontend:
  backend:
    internal: true
```
