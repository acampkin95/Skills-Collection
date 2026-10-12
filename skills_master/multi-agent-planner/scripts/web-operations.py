#!/usr/bin/env python3
"""
Web Operations Module for Multi-Agent Planner

Web scraping and fetch operations with:
- HTTP fetch with headers and authentication
- Rate limiting and caching
- Proxy support
- Content-type handling
- Error recovery and retries
- Async/await patterns
"""

import asyncio
import gzip
import hashlib
import json
import logging
import os
import re
import time
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

try:
    import aiohttp
    from aiohttp import ClientTimeout, TCPConnector
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False


# Configuration paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
CACHE_DIR = PROJECT_ROOT / "aistore" / "cache" / "web"
LOG_DIR = PROJECT_ROOT / "aistore" / "logs" / "web"


class ContentType(Enum):
    """Content type enum for response handling"""
    HTML = "text/html"
    JSON = "application/json"
    XML = "application/xml"
    TEXT = "text/plain"
    CSS = "text/css"
    JAVASCRIPT = "application/javascript"
    PDF = "application/pdf"
    BINARY = "application/octet-stream"
    UNKNOWN = "unknown"


@dataclass
class FetchOptions:
    """Options for web fetch operations"""
    method: str = "GET"
    headers: dict = field(default_factory=dict)
    auth: Optional[tuple] = None  # (username, password)
    cookies: dict = field(default_factory=dict)
    data: Optional[bytes] = None
    timeout: int = 30
    max_redirects: int = 10
    follow_redirects: bool = True
    verify_ssl: bool = True
    use_cache: bool = True
    cache_ttl: int = 3600  # seconds
    proxy: Optional[str] = None
    retries: int = 3
    retry_delay: float = 1.0
    user_agent: str = "WebOperations/1.0"


@dataclass
class FetchResult:
    """Result of a web fetch operation"""
    success: bool
    url: str
    final_url: str
    status_code: Optional[int]
    content_type: ContentType
    content: Any  # str, dict, or bytes
    headers: dict
    cookies: dict
    response_time_ms: float
    from_cache: bool = False
    error: Optional[str] = None
    attempts: int = 1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "url": self.url,
            "final_url": self.final_url,
            "status_code": self.status_code,
            "content_type": self.content_type.value,
            "content": self.content if isinstance(self.content, str) else str(self.content),
            "headers": dict(self.headers),
            "cookies": dict(self.cookies),
            "response_time_ms": self.response_time_ms,
            "from_cache": self.from_cache,
            "error": self.error,
            "attempts": self.attempts,
            "timestamp": self.timestamp,
        }


class CacheManager:
    """HTTP response cache with TTL support"""

    def __init__(self, cache_dir: Path, max_size_mb: int = 100):
        self.cache_dir = cache_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, url: str, options: FetchOptions) -> str:
        """Generate cache key from URL and options"""
        key_data = f"{url}:{json.dumps(options.headers, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.cache"

    def get(self, key: str) -> Optional[dict]:
        """Retrieve cached response"""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r") as f:
                cached = json.load(f)

            # Check TTL
            if cached.get("expires_at"):
                expires = datetime.fromisoformat(cached["expires_at"])
                if expires < datetime.now():
                    cache_path.unlink()
                    return None

            cached["from_cache"] = True
            return cached
        except Exception:
            return None

    def set(self, key: str, data: dict, ttl: int = 3600) -> None:
        """Store response in cache"""
        cache_path = self._get_cache_path(key)

        cache_data = {
            **data,
            "cached_at": datetime.now().isoformat(),
            "expires_at": datetime.now() + timedelta(seconds=ttl),
        }

        try:
            with open(cache_path, "w") as f:
                json.dump(cache_data, f)
            self._cleanup_if_needed()
        except Exception as e:
            logging.warning(f"Failed to cache response: {e}")

    def _cleanup_if_needed(self) -> None:
        """Clean up old cache files if cache exceeds max size"""
        total_size = sum(
            f.stat().st_size for f in self.cache_dir.glob("*.cache") if f.exists()
        )

        if total_size > self.max_size_bytes:
            # Delete oldest files
            files = sorted(
                self.cache_dir.glob("*.cache"),
                key=lambda f: f.stat().st_mtime,
            )
            for f in files[: len(files) // 4]:  # Remove oldest 25%
                f.unlink()

    def clear(self) -> int:
        """Clear all cached files, return count deleted"""
        count = 0
        for f in self.cache_dir.glob("*.cache"):
            f.unlink()
            count += 1
        return count


class RateLimiter:
    """Token bucket rate limiter for HTTP requests"""

    def __init__(self, requests_per_second: float = 2.0, burst: int = 5):
        self.rate = requests_per_second
        self.burst = burst
        self.tokens = burst
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now

            tokens_to_add = elapsed * self.rate
            self.tokens = min(self.burst, self.tokens + tokens_to_add)

            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class ContentDecoder:
    """Handle various content encodings"""

    @staticmethod
    def decode(content: bytes, encoding: str, content_type: str) -> str:
        """Decode content based on encoding"""
        if not content:
            return ""

        # Handle content-encoding
        try:
            if encoding == "gzip" or content[:2] == b"\x1f\x8b":
                content = gzip.decompress(content)
            elif encoding == "deflate":
                try:
                    content = zlib.decompress(content)
                except zlib.error:
                    content = zlib.decompress(content, -zlib.MAX_WBITS)
            elif encoding == "br" and HAS_BROTLI:
                content = brotli.decompress(content)
        except Exception as e:
            logging.warning(f"Failed to decode content: {e}")

        # Decode to string based on content type
        if "charset=" in content_type:
            match = re.search(r'charset=["\']?([^"\'\s;]+)', content_type, re.I)
            if match:
                encoding = match.group(1)
                try:
                    return content.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    pass

        # Fallback to utf-8 with error handling
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content.decode("latin-1")
            except Exception:
                return content.decode("utf-8", errors="replace")

    @staticmethod
    def parse(content_type: str) -> ContentType:
        """Parse content type header"""
        content_type = content_type.lower().split(";")[0].strip()

        if "html" in content_type:
            return ContentType.HTML
        elif "json" in content_type:
            return ContentType.JSON
        elif "xml" in content_type:
            return ContentType.XML
        elif "text/plain" in content_type:
            return ContentType.TEXT
        elif "css" in content_type:
            return ContentType.CSS
        elif "javascript" in content_type or "ecmascript" in content_type:
            return ContentType.JAVASCRIPT
        elif "pdf" in content_type:
            return ContentType.PDF
        elif "octet-stream" in content_type or "binary" in content_type:
            return ContentType.BINARY
        else:
            return ContentType.UNKNOWN


class WebFetcher:
    """Main web fetcher class with all features"""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        rate_limit: float = 2.0,
        max_concurrent: int = 10,
        proxy: Optional[str] = None,
        default_headers: Optional[dict] = None,
    ):
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_manager = CacheManager(self.cache_dir)
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit)
        self.proxy = proxy
        self.session: Optional[aiohttp.ClientSession] = None
        self.default_headers = default_headers or {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

        # Semaphore for concurrent requests
        self.semaphore = asyncio.Semaphore(max_concurrent)

        # Setup logging
        self.logger = logging.getLogger("WebFetcher")
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(LOG_DIR / f"web_{datetime.now():%Y%m%d}.log")
        fh.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(fh)
        self.logger.setLevel(logging.INFO)

    async def __aenter__(self) -> "WebFetcher":
        if HAS_AIOHTTP:
            timeout = ClientTimeout(total=60, connect=10, sock_read=30)
            connector = TCPConnector(
                limit=50, limit_per_host=10, ttl_dns_cache=300
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.default_headers,
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()

    def _build_headers(self, options: FetchOptions) -> Dict:
        """Build request headers"""
        headers = dict(options.headers)

        if "User-Agent" not in headers and options.user_agent:
            headers["User-Agent"] = options.user_agent

        if options.method in ("POST", "PUT", "PATCH"):
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/x-www-form-urlencoded"

        return headers

    async def _fetch_with_retry(
        self, url: str, options: FetchOptions
    ) -> FetchResult:
        """Execute fetch with retry logic"""
        last_error = None

        for attempt in range(options.retries):
            try:
                headers = self._build_headers(options)

                start_time = time.monotonic()
                async with self.semaphore:
                    await self.rate_limiter.acquire()

                    if not self.session:
                        return FetchResult(
                            success=False,
                            url=url,
                            final_url=url,
                            status_code=None,
                            content_type=ContentType.UNKNOWN,
                            content="",
                            headers={},
                            cookies={},
                            response_time_ms=0,
                            error="HTTP session not available",
                            attempts=attempt + 1,
                        )

                    async with self.session.request(
                        options.method,
                        url,
                        headers=headers,
                        auth=options.auth,
                        cookies=options.cookies,
                        data=options.data,
                        proxy=self.proxy or options.proxy,
                        ssl=options.verify_ssl,
                        allow_redirects=options.follow_redirects,
                    ) as response:
                        content_type_header = response.headers.get(
                            "Content-Type", "application/octet-stream"
                        )
                        content_type = ContentDecoder.parse(content_type_header)
                        encoding = response.headers.get("Content-Encoding", "")

                        # Read content
                        content_bytes = await response.read()

                        # Decode content
                        content = ContentDecoder.decode(
                            content_bytes, encoding, content_type_header
                        )

                        # Parse JSON if applicable
                        if content_type == ContentType.JSON:
                            try:
                                content = json.loads(content)
                            except json.JSONDecodeError as e:
                                self.logger.warning(f"Failed to parse JSON: {e}")

                        response_time = (time.monotonic() - start_time) * 1000

                        return FetchResult(
                            success=response.status < 400,
                            url=url,
                            final_url=str(response.url),
                            status_code=response.status,
                            content_type=content_type,
                            content=content,
                            headers=dict(response.headers),
                            cookies=dict(response.cookies),
                            response_time_ms=response_time,
                            attempts=attempt + 1,
                        )

            except asyncio.TimeoutError:
                last_error = "Request timed out"
                self.logger.warning(f"Attempt {attempt + 1} timeout for {url}")

            except aiohttp.ClientError as e:
                last_error = str(e)
                self.logger.warning(f"Attempt {attempt + 1} error for {url}: {e}")

            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Unexpected error for {url}: {e}")

            # Wait before retry (exponential backoff)
            if attempt < options.retries - 1:
                await asyncio.sleep(options.retry_delay * (2 ** attempt))

        return FetchResult(
            success=False,
            url=url,
            final_url=url,
            status_code=None,
            content_type=ContentType.UNKNOWN,
            content="",
            headers={},
            cookies={},
            response_time_ms=0,
            error=last_error or "Max retries exceeded",
            attempts=options.retries,
        )

    async def fetch(
        self,
        url: str,
        options: Optional[FetchOptions] = None,
    ) -> FetchResult:
        """
        Fetch a URL with all options.

        Args:
            url: URL to fetch
            options: FetchOptions instance or None for defaults

        Returns:
            FetchResult with response data
        """
        opts = options or FetchOptions()

        # Check cache first
        if opts.use_cache:
            cache_key = self.cache_manager._get_cache_key(url, opts)
            cached = self.cache_manager.get(cache_key)
            if cached:
                return FetchResult(**cached)

        # Check URL validity
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                url = "https://" + url
                parsed = urlparse(url)
            if not parsed.netloc:
                return FetchResult(
                    success=False,
                    url=url,
                    final_url=url,
                    status_code=None,
                    content_type=ContentType.UNKNOWN,
                    content="",
                    headers={},
                    cookies={},
                    response_time_ms=0,
                    error="Invalid URL",
                )
        except Exception as e:
            return FetchResult(
                success=False,
                url=url,
                final_url=url,
                status_code=None,
                content_type=ContentType.UNKNOWN,
                content="",
                headers={},
                cookies={},
                response_time_ms=0,
                error=f"URL parsing error: {e}",
            )

        # Perform fetch
        result = await self._fetch_with_retry(url, opts)

        # Cache successful responses
        if opts.use_cache and result.success:
            cache_key = self.cache_manager._get_cache_key(url, opts)
            self.cache_manager.set(cache_key, result.to_dict(), opts.cache_ttl)

        self.logger.info(
            f"FETCH | url={url[:80]} | status={result.status_code} | "
            f"time={result.response_time_ms:.0f}ms | cache={'hit' if result.from_cache else 'miss'}"
        )

        return result

    async def fetch_all(
        self, urls: List[str], options: Optional[FetchOptions] = None
    ) -> List[FetchResult]:
        """Fetch multiple URLs concurrently"""
        tasks = [self.fetch(url, options) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def clear_cache(self) -> int:
        """Clear all cached responses"""
        return self.cache_manager.clear()


class ProxyManager:
    """Manage proxy configurations"""

    def __init__(self):
        self.proxies: List[str] = []
        self.current_index = 0

    def add_proxy(self, proxy_url: str) -> None:
        """Add a proxy to the rotation"""
        if not proxy_url.startswith(("http://", "https://", "socks://")):
            proxy_url = f"http://{proxy_url}"
        self.proxies.append(proxy_url)

    def load_from_env(self, env_var: str = "HTTP_PROXIES") -> None:
        """Load proxies from environment variable (comma-separated)"""
        proxies = os.getenv(env_var, "")
        for proxy in proxies.split(","):
            proxy = proxy.strip()
            if proxy:
                self.add_proxy(proxy)

    def get_next(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy

    def rotate(self) -> Optional[str]:
        """Rotate to next proxy"""
        return self.get_next()


# Convenience functions
async def fetch_html(url: str, **kwargs) -> FetchResult:
    """Quick fetch HTML content"""
    async with WebFetcher() as fetcher:
        options = FetchOptions(
            headers={"Accept": "text/html"},
            **kwargs,
        )
        return await fetcher.fetch(url, options)


async def fetch_json(url: str, **kwargs) -> FetchResult:
    """Quick fetch JSON content"""
    async with WebFetcher() as fetcher:
        options = FetchOptions(
            headers={"Accept": "application/json"},
            **kwargs,
        )
        return await fetcher.fetch(url, options)


async def fetch_text(url: str, **kwargs) -> FetchResult:
    """Quick fetch plain text"""
    async with WebFetcher() as fetcher:
        options = FetchOptions(
            headers={"Accept": "text/plain"},
            **kwargs,
        )
        return await fetcher.fetch(url, options)


# Main execution
if __name__ == "__main__":
    import sys

    async def demo():
        print("Web Operations Demo")
        print("=" * 50)

        # Demo fetch
        print("\n1. Testing web fetcher:")
        async with WebFetcher(rate_limit=5) as fetcher:
            result = await fetcher.fetch("https://example.com")
            print(f"   Success: {result.success}")
            print(f"   Status: {result.status_code}")
            print(f"   Content Type: {result.content_type.value}")
            print(f"   Response Time: {result.response_time_ms:.0f}ms")
            if result.success:
                print(f"   Content Preview: {result.content[:150]}...")

        # Demo JSON fetch
        print("\n2. Testing JSON fetch:")
        result = await fetch_json("https://httpbin.org/json")
        print(f"   Success: {result.success}")
        print(f"   Content Type: {result.content_type.value}")
        if result.success and isinstance(result.content, dict):
            print(f"   Parsed JSON keys: {list(result.content.keys())}")

        # Demo cache
        print("\n3. Testing cache (second request should be faster):")
        start = time.monotonic()
        result1 = await fetch_html("https://example.com")
        time1 = (time.monotonic() - start) * 1000

        start = time.monotonic()
        result2 = await fetch_html("https://example.com")
        time2 = (time.monotonic() - start) * 1000

        print(f"   First request: {time1:.0f}ms (cache: {'hit' if result1.from_cache else 'miss'})")
        print(f"   Second request: {time2:.0f}ms (cache: {'hit' if result2.from_cache else 'miss'})")

        # Demo parallel fetch
        print("\n4. Testing parallel fetch:")
        urls = [
            "https://httpbin.org/get",
            "https://httpbin.org/headers",
            "https://httpbin.org/uuid",
        ]
        async with WebFetcher(rate_limit=10, max_concurrent=5) as fetcher:
            results = await fetcher.fetch_all(urls)
        print(f"   Fetched {len([r for r in results if r.success])}/{len(urls)} URLs successfully")

    asyncio.run(demo())
