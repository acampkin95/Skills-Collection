#!/usr/bin/env python3
"""
Crawl4AI Orchestrator - Multi-URL crawling and extraction pipeline.

Enhanced with:
- Error recovery with retry logic
- Circuit breaker pattern
- Rate limiting
- Result caching
- Checkpoint recovery

Usage:
    python3 crawl-orchestrator.py crawl <urls-file> [--output <dir>] [--format <json|markdown>]
    python3 crawl-orchestrator.py extract <url> <schema-file>
    python3 crawl-orchestrator.py monitor <urls-file> [--interval <minutes>]
    python3 crawl-orchestrator.py crawl <urls-file> --retry-failed
"""

import asyncio
import json
import sys
import yaml
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Set
from dataclasses import dataclass, field
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy, JsonCssExtractionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("crawl-orchestrator")


# =============================================================================
# Rate Limiter
# =============================================================================

class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, requests_per_second: float = 2.0, burst: int = 5):
        self.tokens = burst
        self.max_tokens = burst
        self.rate = requests_per_second
        self.last_update = datetime.now()
        self.lock = asyncio.Lock()

    async def acquire(self) -> float:
        """Acquire a token, return wait time if throttled."""
        async with self.lock:
            now = datetime.now()
            elapsed = (now - self.last_update).total_seconds()

            # Refill tokens
            self.tokens = min(
                self.tokens + elapsed * self.rate,
                self.max_tokens
            )
            self.last_update = now

            if self.tokens >= 1:
                self.tokens -= 1
                return 0.0

            # Calculate wait time for next token
            deficit = 1 - self.tokens
            return deficit / self.rate

    async def wait(self):
        """Wait until a token is available."""
        wait_time = await self.acquire()
        if wait_time > 0:
            await asyncio.sleep(wait_time)


# =============================================================================
# Circuit Breaker
# =============================================================================

class CircuitState:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Circuit breaker for external service protection."""
    failure_threshold: int = 5
    reset_timeout: float = 60.0
    states: Dict[str, Dict] = field(default_factory=dict)

    def record_failure(self, key: str):
        """Record a failure."""
        if key not in self.states:
            self.states[key] = {"failures": 0, "last_failure": None, "state": CircuitState.CLOSED}

        self.states[key]["failures"] += 1
        self.states[key]["last_failure"] = datetime.now()

        if self.states[key]["failures"] >= self.failure_threshold:
            self.states[key]["state"] = CircuitState.OPEN
            logger.warning(f"Circuit OPEN for {key}")

    def record_success(self, key: str):
        """Record a success."""
        if key in self.states:
            self.states[key]["failures"] = 0
            self.states[key]["state"] = CircuitState.CLOSED

    def can_execute(self, key: str) -> bool:
        """Check if execution is allowed."""
        if key not in self.states:
            return True

        state = self.states[key]
        if state["state"] == CircuitState.CLOSED:
            return True

        if state["state"] == CircuitState.OPEN:
            elapsed = (datetime.now() - state["last_failure"]).total_seconds()
            if elapsed >= self.reset_timeout:
                state["state"] = CircuitState.HALF_OPEN
                return True
            return False

        return True  # HALF_OPEN


# =============================================================================
# Cache Manager
# =============================================================================

class CacheManager:
    """Simple in-memory cache with TTL."""

    def __init__(self, ttl_minutes: int = 60):
        self.cache: Dict[str, Dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def _get_key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def get(self, url: str) -> Optional[Dict]:
        """Get cached result."""
        key = self._get_key(url)
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["timestamp"] < self.ttl:
                logger.info(f"Cache hit for {url}")
                return entry["data"]
            del self.cache[key]
        return None

    def set(self, url: str, data: Dict):
        """Cache result."""
        key = self._get_key(url)
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.now(),
        }
        logger.debug(f"Cached {url}")


# =============================================================================
# Checkpoint Manager
# =============================================================================

@dataclass
class CheckpointManager:
    """Checkpoint manager for recovery."""
    completed: Set[str] = field(default_factory=set)
    failed: Set[str] = field(default_factory=set)
    checkpoint_file: str = "crawl-checkpoint.json"

    def __post_init__(self):
        self._load()

    def _load(self):
        """Load checkpoint from disk."""
        path = Path(self.checkpoint_file)
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    self.completed = set(data.get("completed", []))
                    self.failed = set(data.get("failed", []))
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")

    def save(self):
        """Save checkpoint to disk."""
        path = Path(self.checkpoint_file)
        with open(path, "w") as f:
            json.dump({
                "completed": list(self.completed),
                "failed": list(self.failed),
            }, f)

    def mark_completed(self, url: str):
        self.completed.add(url)
        self.save()

    def mark_failed(self, url: str):
        self.failed.add(url)
        self.save()

    def is_completed(self, url: str) -> bool:
        return url in self.completed

    def get_remaining(self, urls: list) -> list:
        return [u for u in urls if u not in self.completed]


# =============================================================================
# Retry Handler
# =============================================================================

class RetryHandler:
    """Retry logic with exponential backoff."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def execute(self, operation, *args, **kwargs) -> Any:
        """Execute with retry."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
                    await asyncio.sleep(delay)

        raise last_error


# =============================================================================
# Crawl Orchestrator
# =============================================================================

class CrawlOrchestrator:
    """Enhanced orchestrator with error recovery and rate limiting."""

    def __init__(
        self,
        rate_limit_rps: float = 2.0,
        max_retries: int = 3,
        use_cache: bool = True,
        checkpoint_file: str = "crawl-checkpoint.json"
    ):
        self.results = []
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit_rps)
        self.circuit_breaker = CircuitBreaker()
        self.cache = CacheManager() if use_cache else None
        self.checkpoint = CheckpointManager(checkpoint_file)
        self.retry_handler = RetryHandler(max_retries=max_retries)

    async def crawl_url(
        self,
        url: str,
        output_dir: Path = None,
        format: str = "markdown",
        force: bool = False
    ) -> Dict:
        """Crawl a single URL with error recovery."""

        # Check cache
        if not force and self.cache:
            cached = self.cache.get(url)
            if cached:
                cached["from_cache"] = True
                self.results.append(cached)
                return cached

        # Check circuit breaker
        domain = url.split("/")[2] if "/" in url else url
        if not self.circuit_breaker.can_execute(domain):
            logger.warning(f"Circuit open for {domain}, skipping {url}")
            return {"url": url, "success": False, "error": "circuit_open"}

        # Apply rate limiting
        await self.rate_limiter.wait()

        # Check if already completed
        if not force and self.checkpoint.is_completed(url):
            logger.info(f"Skipping already completed: {url}")
            return {"url": url, "success": True, "skipped": True}

        try:
            # Execute crawl with retry
            result = await self.retry_handler.execute(
                self._do_crawl, url, format
            )

            if result["success"]:
                self.circuit_breaker.record_success(domain)
                self.checkpoint.mark_completed(url)

                # Save to cache
                if self.cache:
                    self.cache.set(url, result)

            else:
                self.circuit_breaker.record_failure(domain)
                self.checkpoint.mark_failed(url)

            self.results.append(result)
            return result

        except Exception as e:
            logger.error(f"Crawl failed for {url}: {e}")
            self.circuit_breaker.record_failure(domain)
            error_result = {"url": url, "success": False, "error": str(e)}
            self.checkpoint.mark_failed(url)
            self.results.append(error_result)
            return error_result

    async def _do_crawl(self, url: str, format: str) -> Dict:
        """Actual crawl implementation."""
        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1280,
            viewport_height=720,
        )

        crawler_config = CrawlerRunConfig(
            cache_mode=True,
            screenshot=True,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            output = {
                "url": url,
                "success": result.success,
                "timestamp": datetime.now().isoformat(),
            }

            if result.success:
                if format == "markdown":
                    output["content"] = result.markdown
                    output["markdown_length"] = len(result.markdown) if result.markdown else 0
                elif format == "json":
                    output["html"] = result.html
                    output["links"] = result.links
                    output["media"] = result.media

            return output

    async def crawl_batch(
        self,
        urls: list,
        output_dir: Path = None,
        format: str = "markdown",
        max_concurrent: int = 5,
        force: bool = False
    ) -> list:
        """Crawl multiple URLs concurrently with rate limiting."""
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        # Filter to remaining URLs if using checkpoint
        if not force:
            remaining = self.checkpoint.get_remaining(urls)
            logger.info(f"Crawling {len(remaining)}/{len(urls)} URLs (checkpoint active)")
        else:
            remaining = urls

        semaphore = asyncio.Semaphore(max_concurrent)

        async def crawl_with_sem(url):
            async with semaphore:
                return await self.crawl_url(url, output_dir, format, force)

        tasks = [crawl_with_sem(url) for url in remaining]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return results

    async def crawl_with_retry(
        self,
        urls: list,
        output_dir: Path = None,
        format: str = "markdown",
        max_concurrent: int = 5
    ) -> list:
        """Crawl with retry for failed URLs."""
        # Initial crawl
        results = await self.crawl_batch(urls, output_dir, format, max_concurrent)

        # Identify and retry failed URLs
        failed = [r for r in results if isinstance(r, dict) and not r.get("success")]

        if failed:
            logger.info(f"Retrying {len(failed)} failed URLs...")
            failed_urls = [r["url"] for r in failed if isinstance(r, dict)]

            retry_results = await self.crawl_batch(
                failed_urls, output_dir, format, max_concurrent, force=True
            )

            # Update results
            for i, r in enumerate(results):
                if isinstance(r, dict) and not r.get("success"):
                    # Find corresponding retry result
                    for retry in retry_results:
                        if isinstance(retry, dict) and retry.get("url") == r["url"]:
                            results[results.index(r)] = retry
                            break

        return results

    async def extract_with_schema(self, url: str, schema: dict) -> Optional[Dict]:
        """Extract structured data using a schema."""
        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(
            extraction_strategy=JsonCssExtractionStrategy(schema=schema)
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success and result.extracted_content:
                try:
                    return json.loads(result.extracted_content)
                except json.JSONDecodeError:
                    return {"raw": result.extracted_content}

        return None


# =============================================================================
# Command Handlers
# =============================================================================

def load_urls(file_path: str) -> list:
    """Load URLs from a file."""
    path = Path(file_path)
    if path.suffix == ".json":
        with open(path) as f:
            data = json.load(f)
            return data.get("urls", data) if isinstance(data, dict) else data
    elif path.suffix in (".yaml", ".yml"):
        with open(path) as f:
            data = yaml.safe_load(f)
            return data.get("urls", data) if isinstance(data, dict) else data
    else:
        with open(path) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def load_schema(file_path: str) -> dict:
    """Load extraction schema from file."""
    path = Path(file_path)
    with open(path) as f:
        if path.suffix == ".json":
            return json.load(f)
        elif path.suffix in (".yaml", ".yml"):
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unknown schema format: {path.suffix}")


async def cmd_crawl(args):
    """Handle crawl command."""
    orchestrator = CrawlOrchestrator(
        rate_limit_rps=getattr(args, 'rate_limit', 2.0),
        max_retries=getattr(args, 'max_retries', 3),
        use_cache=not getattr(args, 'no_cache', False),
    )

    urls = load_urls(args.urls_file)
    output_dir = Path(args.output) if args.output else None
    format = getattr(args, 'format', 'markdown') or "markdown"

    print(f"Crawling {len(urls)} URLs...")

    if getattr(args, 'retry_failed', False):
        results = await orchestrator.crawl_with_retry(urls, output_dir, format)
    else:
        results = await orchestrator.crawl_batch(urls, output_dir, format)

    successful = len([r for r in results if isinstance(r, dict) and r.get('success')])
    failed = len([r for r in results if isinstance(r, dict) and not r.get('success')])
    skipped = len([r for r in results if isinstance(r, dict) and r.get('skipped')])

    print(f"\nCompleted: {successful}/{len(urls)} successful, {failed} failed, {skipped} skipped")

    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total": len(urls),
        "successful": successful,
        "failed": failed,
        "skipped": skipped,
        "results": [
            {"url": r.get("url"), "success": r.get("success"), "error": r.get("error")}
            for r in results if isinstance(r, dict)
        ]
    }

    if output_dir:
        with open(output_dir / "crawl-summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

    return summary


async def cmd_extract(args):
    """Handle extract command."""
    orchestrator = CrawlOrchestrator()
    schema = load_schema(args.schema_file)

    print(f"Extracting from {args.url} using schema...")

    result = await orchestrator.extract_with_schema(args.url, schema)

    if result:
        print(json.dumps(result, indent=2))
        return result
    else:
        print("Extraction failed")
        return None


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Crawl4AI Orchestrator - Enhanced with error recovery")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Crawl command
    crawl_parser = subparsers.add_parser("crawl", help="Crawl multiple URLs")
    crawl_parser.add_argument("urls_file", help="File containing URLs")
    crawl_parser.add_argument("--output", "-o", help="Output directory")
    crawl_parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    crawl_parser.add_argument("--rate-limit", type=float, default=2.0, help="Requests per second")
    crawl_parser.add_argument("--max-retries", type=int, default=3, help="Max retry attempts")
    crawl_parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    crawl_parser.add_argument("--retry-failed", action="store_true", help="Retry failed URLs")
    crawl_parser.add_argument("--concurrent", type=int, default=5, help="Max concurrent crawls")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract with schema")
    extract_parser.add_argument("url", help="URL to extract from")
    extract_parser.add_argument("schema_file", help="Schema file (JSON or YAML)")

    args = parser.parse_args()

    if args.command == "crawl":
        asyncio.run(cmd_crawl(args))
    elif args.command == "extract":
        asyncio.run(cmd_extract(args))


if __name__ == "__main__":
    main()
