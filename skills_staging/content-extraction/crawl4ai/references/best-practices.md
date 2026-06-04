# Crawl4AI Best Practices Guide

Comprehensive guide for production-ready web crawling with Crawl4AI.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Configuration Management](#configuration-management)
3. [Error Handling](#error-handling)
4. [Performance Optimization](#performance-optimization)
5. [Resource Management](#resource-management)
6. [Monitoring and Observability](#monitoring-and-observability)
7. [Security Best Practices](#security-best-practices)
8. [Testing Strategies](#testing-strategies)

---

## Project Structure

### Recommended Directory Layout

```
crawl4ai-project/
├── config/
│   ├── default.yaml         # Default configurations
│   ├── production.yaml      # Production settings
│   └── schemas/             # Extraction schemas
│       ├── products.json
│       ├── articles.json
│       └── users.json
├── src/
│   ├── crawler.py           # Main crawler class
│   ├── extractors.py        # Custom extractors
│   ├── pipeline.py          # Processing pipeline
│   └── utils.py             # Utilities
├── data/
│   ├── raw/                 # Raw crawl results
│   └── processed/           # Processed data
├── outputs/
│   ├── reports/             # Analysis reports
│   └── exports/             # Final exports
├── logs/
│   ├── crawl.log
│   └── errors.log
├── tests/
├── docker/
└── scripts/
```

### Configuration File Example

```yaml
# config/default.yaml
crawler:
  browser:
    headless: true
    viewport_width: 1280
    viewport_height: 720
    user_agent: "Mozilla/5.0..."

  timeout: 30000
  cache_mode: "enabled"
  max_concurrent: 10
  rate_limit:
    requests_per_minute: 60
    burst: 5

extraction:
  default_strategy: "css"
  llm:
    provider: "openai"
    model: "gpt-4o-mini"
    temperature: 0.0

retry:
  max_attempts: 3
  base_delay: 1.0
  max_delay: 60.0
  exponential_base: 2

monitoring:
  metrics_enabled: true
  log_level: "INFO"
  prometheus_port: 9090
```

---

## Configuration Management

### Environment-Based Configuration

```python
import os
from dataclasses import dataclass

@dataclass
class CrawlerConfig:
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout: int = 30000
    cache_mode: str = "enabled"
    max_concurrent: int = 10
    rate_limit_rpm: int = 60

    @classmethod
    def from_env(cls) -> "CrawlerConfig":
        return cls(
            headless=os.getenv("HEADLESS", "true").lower() == "true",
            viewport_width=int(os.getenv("VIEWPORT_WIDTH", "1280")),
            viewport_height=int(os.getenv("VIEWPORT_HEIGHT", "720")),
            timeout=int(os.getenv("TIMEOUT", "30000")),
            cache_mode=os.getenv("CACHE_MODE", "enabled"),
            max_concurrent=int(os.getenv("MAX_CONCURRENT", "10")),
            rate_limit_rpm=int(os.getenv("RATE_LIMIT_RPM", "60")),
        )
```

### Profile-Based Configuration

```python
from enum import Enum

class ConfigProfile(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

PROFILES = {
    ConfigProfile.DEVELOPMENT: {
        "headless": False,
        "cache_mode": "disabled",
        "max_concurrent": 2,
        "rate_limit_rpm": 30,
        "log_level": "DEBUG",
    },
    ConfigProfile.STAGING: {
        "headless": True,
        "cache_mode": "enabled",
        "max_concurrent": 5,
        "rate_limit_rpm": 60,
        "log_level": "INFO",
    },
    ConfigProfile.PRODUCTION: {
        "headless": True,
        "cache_mode": "enabled",
        "max_concurrent": 20,
        "rate_limit_rpm": 120,
        "log_level": "WARNING",
    },
}
```

---

## Performance Optimization

### Connection Pooling

```python
import asyncio
from crawl4ai import AsyncWebCrawler

class OptimizedCrawler:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def crawl_with_pool(self, urls: list):
        """Crawl URLs with connection pooling."""
        async with self.semaphore:
            async with AsyncWebCrawler() as crawler:
                results = await crawler.arun_many(urls)
                return results
```

### Memory-Efficient Processing

```python
import asyncio
from typing import AsyncGenerator

class MemoryEfficientProcessor:
    def __init__(self, chunk_size: int = 100):
        self.chunk_size = chunk_size

    async def process_large_dataset(
        self,
        urls: list,
        processor: callable,
    ) -> AsyncGenerator[dict, None]:
        """Process URLs in chunks with checkpointing."""
        completed = set()

        for i in range(0, len(urls), self.chunk_size):
            chunk = urls[i:i + self.chunk_size]

            for url in chunk:
                if url in completed:
                    continue

                try:
                    result = await processor(url)
                    yield result
                    completed.add(url)
                except Exception as e:
                    print(f"Error processing {url}: {e}")
                    continue
```

---

## Monitoring and Observability

### Prometheus Metrics Integration

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
CRAWL_REQUESTS = Counter(
    "crawl4ai_requests_total",
    "Total crawl requests",
    ["status", "url_pattern"]
)

CRAWL_DURATION = Histogram(
    "crawl4ai_request_duration_seconds",
    "Crawl request duration",
    ["url_pattern"],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

ACTIVE_CRAWLS = Gauge(
    "crawl4ai_active_crawls",
    "Number of currently active crawls"
)

def setup_monitoring(port: int = 9090):
    """Start Prometheus metrics server."""
    start_http_server(port)
    print(f"Prometheus metrics on port {port}")
```

### Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured JSON logger for crawl operations."""

    def __init__(self, name: str = "crawl4ai"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

    def log_crawl(self, url: str, success: bool, duration: float = 0):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "crawl_complete" if success else "crawl_failure",
            "url": url,
            "success": success,
            "duration_seconds": duration,
        }
        self.logger.info(json.dumps(log_data))
```

---

## Security Best Practices

### Input Validation

```python
import re
from urllib.parse import urlparse
from typing import Tuple, Optional

class URLValidator:
    ALLOWED_SCHEMES = {"http", "https"}
    BLOCKED_DOMAINS = {"localhost", "127.0.0.1"}

    @classmethod
    def validate(cls, url: str) -> Tuple[bool, Optional[str]]:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in cls.ALLOWED_SCHEMES:
                return False, f"Invalid scheme: {parsed.scheme}"
            if parsed.hostname in cls.BLOCKED_DOMAINS:
                return False, f"Blocked domain: {parsed.hostname}"
            return True, None
        except Exception as e:
            return False, str(e)
```

### Rate Limiting

```python
import asyncio
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    burst_limit: int = 5

class RateLimiter:
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.tokens = config.burst_limit if config else 5
        self.last_refill = datetime.now()

    async def acquire(self) -> bool:
        now = datetime.now()
        elapsed = (now - self.last_refill).total_seconds()
        refill_rate = self.config.requests_per_minute / 60
        self.tokens = min(self.tokens + elapsed * refill_rate, self.config.burst_limit)
        self.last_refill = now

        if self.tokens > 0:
            self.tokens -= 1
            return True
        return False

    async def wait_for_token(self, timeout: float = 60.0):
        for _ in range(int(timeout * 10)):
            if await self.acquire():
                return
            await asyncio.sleep(0.1)
        raise TimeoutError("Rate limit timeout")
```

---

## Testing Strategies

### Unit Tests

```python
import pytest
from unittest.mock import Mock, AsyncMock
from crawl4ai import AsyncWebCrawler

@pytest.fixture
def mock_crawler():
    crawler = AsyncMock(spec=AsyncWebCrawler)
    result = Mock()
    result.success = True
    result.markdown = "# Test Content"
    result.html = "<h1>Test</h1>"
    crawler.arun = AsyncMock(return_value=result)
    return crawler

@pytest.mark.asyncio
async def test_crawl_success(mock_crawler):
    result = await mock_crawler.arun("https://example.com")
    assert result.success
    assert "# Test Content" in result.markdown
```

---

## Summary Checklist

- [ ] Use environment-based configuration
- [ ] Implement proper error handling with retry logic
- [ ] Add circuit breaker for external services
- [ ] Set up structured logging
- [ ] Integrate Prometheus metrics
- [ ] Implement rate limiting
- [ ] Add resource limits
- [ ] Use connection pooling
- [ ] Validate URLs before crawling
- [ ] Write comprehensive tests
