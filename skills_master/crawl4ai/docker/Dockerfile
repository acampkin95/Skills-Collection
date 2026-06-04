# Build stage
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install crawl4ai and dependencies
RUN pip install --no-cache-dir \
    crawl4ai \
    aiohttp \
    redis \
    prometheus-client \
    && pip cache purge

# Production stage
FROM python:3.11-slim-bookworm AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r crawl4ai && useradd -r -g crawl4ai crawl4ai
RUN mkdir -p /app/outputs /app/logs && chown -R crawl4ai:crawl4ai /app
USER crawl4ai

# Copy application files
COPY --chown=crawl4ai:crawl4ai entrypoint.sh /app/
COPY --chown=crawl4ai:crawl4ai scripts/ /app/scripts/

# Environment variables for Playwright
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; asyncio.run(__import__('crawl4ai').AsyncWebCrawler().arun('http://localhost:8000/health'))" 2>/dev/null || exit 1

# Expose port
EXPOSE 8000

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
