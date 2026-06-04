#!/bin/bash
set -e

# Crawl4AI Container Entry Point

echo "Starting Crawl4AI..."

# Environment validation
export CRAWL4AI_HOST=${CRAWL4AI_HOST:-0.0.0.0}
export CRAWL4AI_PORT=${CRAWL4AI_PORT:-8000}
export REDIS_URL=${REDIS_URL:-redis://localhost:6379}
export CACHE_MODE=${CACHE_MODE:-enabled}
export LOG_LEVEL=${LOG_LEVEL:-INFO}
export MAX_CONCURRENT_CRAWLS=${MAX_CONCURRENT_CRAWLS:-10}
export RATE_LIMIT_REQUESTS_PER_MINUTE=${RATE_LIMIT_REQUESTS_PER_MINUTE:-60}

# Create required directories
mkdir -p /app/data /app/outputs /app/logs
chmod -R 755 /app/outputs /app/logs

# Wait for Redis if configured
if [[ "$REDIS_URL" != "redis://localhost:6379" ]] && [[ "$REDIS_URL" != "" ]]; then
    echo "Waiting for Redis at $REDIS_URL..."
    REDIS_HOST=$(echo "$REDIS_URL" | sed -E 's|redis://([^:/]+).*|\1|')
    REDIS_PORT=$(echo "$REDIS_URL" | sed -E 's|.*:([0-9]+).*|\1|' || echo "6379")

    for i in {1..30}; do
        if nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null || redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null; then
            echo "Redis is ready!"
            break
        fi
        echo "Waiting for Redis... ($i/30)"
        sleep 2
    done
fi

# Verify Playwright browsers
echo "Verifying Playwright installation..."
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')" 2>/dev/null || playwright install chromium

# Run health check before starting
echo "Running health check..."
python -c "
import asyncio
from crawl4ai import AsyncWebCrawler
async def health():
    async with AsyncWebCrawler() as c:
        r = await c.arun('http://localhost:$CRAWL4AI_PORT/health')
        return r.success
ok = asyncio.run(health())
if ok:
    print('Health check passed')
else:
    print('Health check warning - starting anyway')
" 2>/dev/null || echo "Health check skipped"

# Start the application
echo "Starting Crawl4AI server on $CRAWL4AI_HOST:$CRAWL4AI_PORT..."

exec python -m crawl4ai \
    --host "$CRAWL4AI_HOST" \
    --port "$CRAWL4AI_PORT" \
    --redis-url "$REDIS_URL" \
    --cache-mode "$CACHE_MODE" \
    --log-level "$LOG_LEVEL" \
    --max-concurrent "$MAX_CONCURRENT_CRAWLS" \
    --rate-limit "$RATE_LIMIT_REQUESTS_PER_MINUTE" \
    "$@"
