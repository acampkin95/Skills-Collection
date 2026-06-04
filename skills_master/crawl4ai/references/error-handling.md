# Error Handling Guide

Robust error recovery patterns for reliable web crawling.

## Overview

This guide covers:
- Common error types and identification
- Retry strategies
- Graceful degradation
- Circuit breaker pattern
- Logging and monitoring

---

## 1. Error Types

### Network Errors

```python
from crawl4ai import AsyncWebCrawler, CrawlerResult

async def safe_crawl(url):
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url)

            if not result.success:
                return handle_crawl_error(result)

            return result

    except Exception as e:
        # Network-level errors
        if "Connection" in str(e):
            return {"error": "connection_failed", "url": url}
        if "Timeout" in str(e):
            return {"error": "timeout", "url": url}
        raise

def handle_crawl_error(result: CrawlResult):
    """Handle crawl-specific errors."""
    error_mapping = {
        "page_timeout": "Page load timeout",
        "js_error": "JavaScript execution error",
        "blocked": "Access blocked (403/429)",
        "not_found": "Page not found (404)",
        "server_error": "Server error (5xx)",
    }

    return {
        "error": error_mapping.get(result.error_type, "unknown"),
        "url": result.url,
        "details": result.error_message,
    }
```

### HTTP Status Codes

```python
from crawl4ai import AsyncWebCrawler

async def crawl_with_status_check(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)

        # Check HTTP status via response
        if hasattr(result, 'status_code'):
            status = result.status_code

            if status == 200:
                return result
            elif status == 404:
                return {"error": "not_found", "url": url}
            elif status == 403:
                return {"error": "forbidden", "url": url}
            elif status == 429:
                return {"error": "rate_limited", "url": url}
            elif status >= 500:
                return {"error": "server_error", "url": url, "status": status}

        return result
```

### JavaScript Errors

```python
# Capture JS errors
js_code = """
(async () => {
    try {
        // Your JavaScript code
        const result = await doSomething();
        return { success: true, data: result };
    } catch (e) {
        return {
            success: false,
            error: e.message,
            stack: e.stack
        };
    }
})();
"""
```

---

## 2. Retry Strategies

### Basic Retry

```python
import asyncio
import random
from typing import Optional

async def retry_crawl(
    url: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> Optional[dict]:
    """Crawl with exponential backoff retry."""

    for attempt in range(max_retries):
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url)

                if result.success:
                    return {"success": True, "data": result}

                # Don't retry certain errors
                if result.error_type in ["not_found", "forbidden"]:
                    return {"success": False, "error": result.error_type}

        except Exception as e:
            error_type = type(e).__name__

        # Calculate delay with exponential backoff + jitter
        delay = min(base_delay * (2 ** attempt), max_delay)
        delay += random.uniform(0, 0.5)  # Add jitter

        print(f"Attempt {attempt + 1}/{max_retries} failed. Retrying in {delay:.1f}s...")
        await asyncio.sleep(delay)

    return {"success": False, "error": "max_retries_exceeded", "url": url}
```

### Retry with Different Strategies

```python
async def smart_retry(url: str, strategies: list = None):
    """Try different crawling strategies on failure."""

    if strategies is None:
        strategies = [
            {"wait_for": "networkidle", "timeout": 30000},
            {"wait_for": "domcontentloaded", "timeout": 15000},
            {"wait_for": "css:.main-content", "timeout": 20000},
        ]

    for i, strategy in enumerate(strategies):
        try:
            config = CrawlerRunConfig(
                page_timeout=strategy.get("timeout", 30000),
                wait_for=strategy.get("wait_for", "networkidle"),
            )

            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url, config=config)

                if result.success:
                    return result

        except Exception as e:
            print(f"Strategy {i + 1} failed: {e}")
            await asyncio.sleep(1)

    return None
```

### Circuit Breaker

```python
import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class CircuitState:
    failure_count: int = 0
    last_failure: float = 0
    state: str = "closed"  # closed, open, half_open

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.states: Dict[str, CircuitState] = {}

    def record_failure(self, key: str):
        if key not in self.states:
            self.states[key] = CircuitState()

        state = self.states[key]
        state.failure_count += 1
        state.last_failure = time.time()

        if state.failure_count >= self.failure_threshold:
            state.state = "open"

    def record_success(self, key: str):
        if key in self.states:
            self.states[key].failure_count = 0
            self.states[key].state = "closed"

    def can_execute(self, key: str) -> bool:
        if key not in self.states:
            return True

        state = self.states[key]
        if state.state == "closed":
            return True

        if state.state == "open":
            if time.time() - state.last_failure > self.reset_timeout:
                state.state = "half_open"
                return True
            return False

        return True  # half_open

# Usage
breaker = CircuitBreaker(failure_threshold=3, reset_timeout=30)

async def protected_crawl(url: str):
    if not breaker.can_execute(url):
        return {"error": "circuit_open", "url": url}

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url)

            if result.success:
                breaker.record_success(url)
                return result
            else:
                breaker.record_failure(url)
                return {"error": "crawl_failed", "url": url}

    except Exception as e:
        breaker.record_failure(url)
        raise
```

---

## 3. Graceful Degradation

### Fallback Content

```python
async def crawl_with_fallback(url: str):
    """Try multiple extraction methods as fallback."""

    methods = [
        ("css_extraction", try_css_extraction),
        ("llm_extraction", try_llm_extraction),
        ("basic_crawl", try_basic_crawl),
    ]

    for name, method in methods:
        try:
            result = await method(url)
            if result and result.get("success"):
                result["extraction_method"] = name
                return result
        except Exception as e:
            print(f"{name} failed: {e}")
            continue

    return {"success": False, "error": "all_methods_failed"}


async def try_css_extraction(url: str):
    # Primary extraction
    schema = {"baseSelector": ".content", "fields": [...]}
    config = CrawlerRunConfig(extraction_strategy=JsonCssExtractionStrategy(schema))
    result = await crawl_with_config(url, config)
    return result if result.success else None
```

### Partial Success

```python
async def crawl_with_partial(url: str):
    """Return partial results even on some failures."""

    result = {"url": url, "success": False, "partial": {}}

    try:
        async with AsyncWebCrawler() as crawler:
            # Try to get markdown
            try:
                md_result = await crawler.arun(url)
                if md_result.success:
                    result["markdown"] = md_result.markdown
                    result["partial"]["markdown"] = True
            except Exception:
                result["partial"]["markdown"] = False

            # Try to get links
            try:
                links_result = await crawler.arun(url)
                if links_result.success:
                    result["links"] = links_result.links
                    result["partial"]["links"] = True
            except Exception:
                result["partial"]["links"] = False

            # Try to get screenshot
            try:
                ss_result = await crawler.arun(url, config=CrawlerRunConfig(screenshot=True))
                if ss_result.success and ss_result.screenshot:
                    result["screenshot"] = True
                    result["partial"]["screenshot"] = True
            except Exception:
                result["partial"]["screenshot"] = False

        result["success"] = any(result["partial"].values())

    except Exception as e:
        result["error"] = str(e)

    return result
```

---

## 4. Logging and Monitoring

### Structured Logging

```python
import json
import logging
from datetime import datetime
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crawl4ai")

class CrawlLogger:
    def __init__(self, log_file: str = "crawl.log"):
        self.log_file = log_file

    def log(self, level: str, url: str, **kwargs):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "url": url,
            **kwargs
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        logger.log(getattr(logging, level), json.dumps(kwargs))

    def log_crawl_start(self, url: str):
        self.log("INFO", url, event="crawl_start")

    def log_crawl_success(self, url: str, metrics: dict):
        self.log("INFO", url, event="crawl_success", **metrics)

    def log_crawl_failure(self, url: str, error: str, attempt: int):
        self.log("WARNING", url, event="crawl_failure", error=error, attempt=attempt)

# Usage
logger = CrawlLogger()

async def logged_crawl(url: str):
    logger.log_crawl_start(url)

    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url)

            if result.success:
                logger.log_crawl_success(url, {
                    "markdown_length": len(result.markdown),
                    "links_count": len(result.links),
                })
            else:
                logger.log_crawl_failure(url, result.error_type, 1)

            return result

    except Exception as e:
        logger.log_crawl_failure(url, str(e), 1)
        raise
```

### Error Metrics

```python
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class ErrorMetrics:
    error_counts: defaultdict = None
    total_crawls: int = 0
    successful_crawls: int = 0

    def __post_init__(self):
        self.error_counts = defaultdict(int)

    def record(self, result):
        self.total_crawls += 1
        if result.success:
            self.successful_crawls += 1
        else:
            self.error_counts[result.error_type] += 1

    def success_rate(self) -> float:
        if self.total_crawls == 0:
            return 0
        return self.successful_crawls / self.total_crawls

    def top_errors(self, n: int = 5) -> list:
        return sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n]
```

---

## 5. Dead Letter Queue

```python
import json
import os
from pathlib import Path

class DeadLetterQueue:
    def __init__(self, dir_path: str = "./dlq"):
        self.dir = Path(dir_path)
        self.dir.mkdir(exist_ok=True)

    def save(self, url: str, error: str, context: dict = None):
        entry = {
            "url": url,
            "error": error,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "retry_count": 0,
        }

        filename = hashlib.md5(url.encode()).hexdigest()[:12] + ".json"
        with open(self.dir / filename, "w") as f:
            json.dump(entry, f, indent=2)

    def load_failed(self) -> list:
        failed = []
        for file in self.dir.glob("*.json"):
            with open(file) as f:
                failed.append(json.load(f))
        return failed

    def retry_all(self, crawler):
        failed = self.load_failed()
        for entry in failed:
            entry["retry_count"] += 1
            if entry["retry_count"] <= 3:
                result = crawler.arun(entry["url"])
                if result.success:
                    # Remove from DLQ
                    (self.dir / f"{hashlib.md5(entry['url'].encode()).hexdigest()[:12]}.json").unlink()
```

---

## 6. Recovery Patterns

### Checkpoint-Based Recovery

```python
import json
from pathlib import Path

class CrawlCheckpoint:
    def __init__(self, file_path: str = "crawl_checkpoint.json"):
        self.file = Path(file_path)
        self.data = self._load()

    def _load(self) -> dict:
        if self.file.exists():
            with open(self.file) as f:
                return json.load(f)
        return {"completed": [], "failed": []}

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f)

    def mark_completed(self, url: str):
        if url not in self.data["completed"]:
            self.data["completed"].append(url)
            self.save()

    def mark_failed(self, url: str):
        if url not in self.data["failed"]:
            self.data["failed"].append(url)
            self.save()

    def is_completed(self, url: str) -> bool:
        return url in self.data["completed"]

    def get_remaining(self, urls: list) -> list:
        return [u for u in urls if not self.is_completed(u)]

# Usage
checkpoint = CrawlCheckpoint()
urls_to_crawl = checkpoint.get_remaining(all_urls)

for url in urls_to_crawl:
    try:
        result = await crawler.arun(url)
        if result.success:
            checkpoint.mark_completed(url)
        else:
            checkpoint.mark_failed(url)
    except Exception:
        checkpoint.mark_failed(url)
```
