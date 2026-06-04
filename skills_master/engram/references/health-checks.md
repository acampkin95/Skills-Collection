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

