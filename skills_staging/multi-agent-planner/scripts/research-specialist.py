#!/usr/bin/env python3
"""
Research Specialist Agent for Multi-Agent Planner

Perplexity AI and web research integration with:
- Perplexity search and deep research
- Web fetch operations
- Source validation and citation
- Async/await patterns
- Rate limiting
- Activity logging
"""

import asyncio
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Async HTTP client
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

# Configuration
CONFIG_DIR = Path(__file__).parent.parent / "config"
LOG_DIR = Path(__file__).parent.parent / "aistore" / "logs" / "research"
RESEARCH_DIR = Path(__file__).parent.parent / "aistore" / "research"


class ResearchType(Enum):
    """Types of research operations"""
    WEB_SEARCH = "web_search"
    DEEP_RESEARCH = "deep_research"
    WEB_FETCH = "web_fetch"
    CURL = "curl"


@dataclass
class Citation:
    """Source citation with metadata"""
    source_id: str
    url: str
    title: str
    accessed_at: str
    content_type: str
    snippet: str = ""
    relevance_score: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "source_id": self.source_id,
            "url": self.url,
            "title": self.title,
            "accessed_at": self.accessed_at,
            "content_type": self.content_type,
            "snippet": self.snippet,
            "relevance_score": self.relevance_score,
        }


@dataclass
class ResearchResult:
    """Result of a research operation"""
    query: str
    research_type: ResearchType
    sources: List[Citation] = field(default_factory=list)
    content: str = ""
    error: Optional[str] = None
    duration_ms: float = 0.0
    tokens_used: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "research_type": self.research_type.value,
            "sources": [s.to_dict() for s in self.sources],
            "content": self.content,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "tokens_used": self.tokens_used,
            "timestamp": self.timestamp,
        }


class RateLimiter:
    """Token bucket rate limiter for API calls"""

    def __init__(self, requests_per_minute: int = 60, burst: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.tokens = burst
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now

            # Add tokens based on elapsed time
            tokens_to_add = elapsed * (self.requests_per_minute / 60)
            self.tokens = min(self.burst, self.tokens + tokens_to_add)

            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / (self.requests_per_minute / 60)
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class PerplexityClient:
    """Perplexity AI API client for search and research operations"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.perplexity.ai",
        rate_limiter: Optional[RateLimiter] = None,
    ):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.base_url = base_url
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_log: List[Dict] = []

        if not self.api_key:
            logging.warning("PERPLEXITY_API_KEY not set. API calls will fail.")

    async def __aenter__(self) -> "PerplexityClient":
        if HAS_AIOHTTP:
            timeout = aiohttp.ClientTimeout(total=300)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()

    def _log_request(self, operation: str, query: str, **kwargs) -> str:
        """Log request details and return request ID"""
        request_id = str(uuid.uuid4())[:8]
        log_entry = {
            "request_id": request_id,
            "operation": operation,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            **kwargs,
        }
        self.request_log.append(log_entry)
        return request_id

    async def search(
        self,
        query: str,
        focus: Optional[List[str]] = None,
        max_results: int = 10,
    ) -> ResearchResult:
        """
        Perform a Perplexity search query.

        Args:
            query: The search query
            focus: Optional list of focus areas (e.g., ["academic", "news"])
            max_results: Maximum number of results to return

        Returns:
            ResearchResult with search results and citations
        """
        start_time = time.monotonic()
        request_id = self._log_request("search", query, max_results=max_results)

        await self.rate_limiter.acquire()

        if not self.api_key or not self.session:
            return ResearchResult(
                query=query,
                research_type=ResearchType.WEB_SEARCH,
                error="API key or session not available",
                duration_ms=(time.monotonic() - start_time) * 1000,
            )

        try:
            payload = {
                "query": query,
                "num_results": min(max_results, 20),
            }
            if focus:
                payload["focus"] = focus

            async with self.session.post(
                f"{self.base_url}/search",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return ResearchResult(
                        query=query,
                        research_type=ResearchType.WEB_SEARCH,
                        error=f"API error {response.status}: {error_text}",
                        duration_ms=(time.monotonic() - start_time) * 1000,
                    )

                data = await response.json()

                # Extract citations from response
                sources = []
                for i, result in enumerate(data.get("results", [])):
                    citation = Citation(
                        source_id=f"{request_id}-{i}",
                        url=result.get("url", ""),
                        title=result.get("title", ""),
                        accessed_at=datetime.now().isoformat(),
                        content_type=result.get("type", "web"),
                        snippet=result.get("snippet", "")[:500],
                        relevance_score=result.get("score", 0.0),
                    )
                    sources.append(citation)

                return ResearchResult(
                    query=query,
                    research_type=ResearchType.WEB_SEARCH,
                    sources=sources,
                    content=data.get("answer", ""),
                    duration_ms=(time.monotonic() - start_time) * 1000,
                    tokens_used=data.get("usage", {}).get("total_tokens", 0),
                )

        except asyncio.TimeoutError:
            return ResearchResult(
                query=query,
                research_type=ResearchType.WEB_SEARCH,
                error="Request timed out",
                duration_ms=(time.monotonic() - start_time) * 1000,
            )
        except Exception as e:
            return ResearchResult(
                query=query,
                research_type=ResearchType.WEB_SEARCH,
                error=str(e),
                duration_ms=(time.monotonic() - start_time) * 1000,
            )

    async def deep_research(
        self,
        query: str,
        focus_areas: Optional[List[str]] = None,
        max_sources: int = 20,
    ) -> ResearchResult:
        """
        Perform a Perplexity deep research query.

        Args:
            query: The research question
            focus_areas: Optional areas to focus research on
            max_sources: Maximum number of sources to gather

        Returns:
            ResearchResult with comprehensive research findings
        """
        start_time = time.monotonic()
        request_id = self._log_request(
            "deep_research", query, max_sources=max_sources
        )

        await self.rate_limiter.acquire()

        if not self.api_key or not self.session:
            return ResearchResult(
                query=query,
                research_type=ResearchType.DEEP_RESEARCH,
                error="API key or session not available",
                duration_ms=(time.monotonic() - start_time) * 1000,
            )

        try:
            payload = {
                "query": query,
                "max_sources": min(max_sources, 50),
                "mode": "comprehensive",
            }
            if focus_areas:
                payload["focus_areas"] = focus_areas

            async with self.session.post(
                f"{self.base_url}/deep-research",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return ResearchResult(
                        query=query,
                        research_type=ResearchType.DEEP_RESEARCH,
                        error=f"API error {response.status}: {error_text}",
                        duration_ms=(time.monotonic() - start_time) * 1000,
                    )

                data = await response.json()

                # Extract citations from deep research results
                sources = []
                for i, result in enumerate(data.get("sources", [])):
                    citation = Citation(
                        source_id=f"{request_id}-{i}",
                        url=result.get("url", ""),
                        title=result.get("title", ""),
                        accessed_at=datetime.now().isoformat(),
                        content_type=result.get("type", "web"),
                        snippet=result.get("snippet", "")[:500],
                        relevance_score=result.get("relevance", 0.0),
                    )
                    sources.append(citation)

                return ResearchResult(
                    query=query,
                    research_type=ResearchType.DEEP_RESEARCH,
                    sources=sources,
                    content=data.get("answer", data.get("summary", "")),
                    duration_ms=(time.monotonic() - start_time) * 1000,
                    tokens_used=data.get("usage", {}).get("total_tokens", 0),
                )

        except asyncio.TimeoutError:
            return ResearchResult(
                query=query,
                research_type=ResearchType.DEEP_RESEARCH,
                error="Request timed out (deep research may take longer)",
                duration_ms=(time.monotonic() - start_time) * 1000,
            )
        except Exception as e:
            return ResearchResult(
                query=query,
                research_type=ResearchType.DEEP_RESEARCH,
                error=str(e),
                duration_ms=(time.monotonic() - start_time) * 1000,
            )


class WebFetchClient:
    """Web content fetching with proper headers, auth, and caching"""

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        cache_dir: Optional[Path] = None,
        proxy: Optional[str] = None,
        default_headers: Optional[Dict] = None,
    ):
        self.rate_limiter = rate_limiter or RateLimiter(requests_per_minute=120)
        self.cache_dir = cache_dir or (RESEARCH_DIR / "cache")
        self.proxy = proxy
        self.session: Optional[aiohttp.ClientSession] = None
        self.default_headers = default_headers or {
            "User-Agent": "ResearchAgent/1.0 (Educational/Research)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def __aenter__(self) -> "WebFetchClient":
        if HAS_AIOHTTP:
            timeout = aiohttp.ClientTimeout(total=60)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.default_headers,
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()

    def _get_cache_path(self, url: str) -> Path:
        """Generate cache file path for a URL"""
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.cache"

    async def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        body: Optional[bytes] = None,
        use_cache: bool = True,
        timeout: int = 30,
    ) -> Dict:
        """
        Fetch web content with caching and rate limiting.

        Args:
            url: URL to fetch
            method: HTTP method (GET, POST, etc.)
            headers: Additional headers
            body: Request body for POST/PUT
            use_cache: Whether to use cached responses
            timeout: Request timeout in seconds

        Returns:
            Dict with status, content, headers, and metadata
        """
        await self.rate_limiter.acquire()

        if not self.session:
            return {
                "success": False,
                "error": "HTTP session not available",
                "url": url,
            }

        # Check cache
        cache_path = self._get_cache_path(url)
        if use_cache and cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    cached = json.load(f)
                    if cached.get("expires_at"):
                        if datetime.fromisoformat(cached["expires_at"]) > datetime.now():
                            cached["from_cache"] = True
                            return cached
            except Exception:
                pass

        try:
            req_headers = headers or {}
            async with self.session.request(
                method,
                url,
                headers=req_headers,
                data=body,
                proxy=self.proxy,
                allow_redirects=True,
            ) as response:
                content_type = response.headers.get("Content-Type", "")

                # Parse content based on type
                content = ""
                if "application/json" in content_type:
                    content = await response.json()
                    content = json.dumps(content)
                elif "text/" in content_type or "application/xml" in content_type:
                    content = await response.text()

                result = {
                    "success": response.status < 400,
                    "status_code": response.status,
                    "url": str(response.url),
                    "content": content,
                    "content_type": content_type,
                    "headers": dict(response.headers),
                    "from_cache": False,
                }

                # Cache successful responses
                if use_cache and result["success"]:
                    self.cache_dir.mkdir(parents=True, exist_ok=True)
                    cache_data = {
                        **result,
                        "cached_at": datetime.now().isoformat(),
                        "expires_at": None,
                    }
                    if "max-age" in response.headers.get("Cache-Control", ""):
                        # Parse max-age and set expiration
                        cache_data["expires_at"] = datetime.now().isoformat()

                    try:
                        with open(cache_path, "w") as f:
                            json.dump(cache_data, f)
                    except Exception:
                        pass

                return result

        except asyncio.TimeoutError:
            return {"success": False, "error": "Request timed out", "url": url}
        except Exception as e:
            return {"success": False, "error": str(e), "url": url}


class CurlWrapper:
    """Curl command wrapper for CLI operations"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[List[str]] = None,
        data: Optional[str] = None,
        follow_redirects: bool = True,
        user_agent: Optional[str] = None,
    ) -> Dict:
        """
        Execute a curl command.

        Args:
            url: URL to fetch
            method: HTTP method
            headers: List of header strings
            data: POST data
            follow_redirects: Follow redirects
            user_agent: Custom user agent

        Returns:
            Dict with stdout, stderr, return code
        """
        import subprocess

        cmd = ["curl", "-s", "-w", "\n%{http_code}"]

        if follow_redirects:
            cmd.append("-L")

        if method.upper() == "POST":
            cmd.append("-X")
            cmd.append("POST")

        if user_agent:
            cmd.extend(["-A", user_agent])

        if headers:
            for header in headers:
                cmd.extend(["-H", header])

        if data:
            cmd.extend(["-d", data])

        cmd.append(url)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.timeout
            )

            output = stdout.decode().strip()
            lines = output.rsplit("\n", 1)
            http_code = lines[-1] if len(lines) > 1 else "000"
            content = "\n".join(lines[:-1]) if len(lines) > 1 else ""

            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "http_code": int(http_code) if http_code.isdigit() else None,
                "content": content,
                "stderr": stderr.decode().strip(),
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Command timed out",
                "returncode": -1,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "returncode": -1}


class ResearchLogger:
    """Logger for research activities"""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Setup logging
        self.logger = logging.getLogger("ResearchAgent")
        self.logger.setLevel(logging.INFO)

        # Clear existing handlers
        self.logger.handlers = []

        # File handler
        log_file = self.log_dir / f"research_{self.session_id}.log"
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        fh.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        self.logger.addHandler(fh)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(ch)

    def log_research_start(self, query: str, research_type: ResearchType) -> str:
        """Log research operation start"""
        research_id = str(uuid.uuid4())[:8]
        self.logger.info(
            f"RESEARCH_START | id={research_id} | type={research_type.value} | query={query[:100]}"
        )
        return research_id

    def log_research_result(
        self, research_id: str, result: ResearchResult
    ) -> None:
        """Log research result summary"""
        status = "ERROR" if result.error else "SUCCESS"
        self.logger.info(
            f"RESEARCH_END | id={research_id} | status={status} | "
            f"sources={len(result.sources)} | duration={result.duration_ms:.0f}ms"
        )

    def log_source(self, citation: Citation) -> None:
        """Log source citation"""
        self.logger.info(
            f"SOURCE | id={citation.source_id} | url={citation.url[:80]} | "
            f"score={citation.relevance_score:.2f}"
        )

    def get_session_log(self) -> List[Dict]:
        """Get all log entries for this session"""
        return []  # Implement if needed with log file parsing


class ResearchSpecialist:
    """
    Main research specialist agent coordinating all research operations.
    """

    def __init__(
        self,
        perplexity_api_key: Optional[str] = None,
        log_dir: Optional[Path] = None,
        research_dir: Optional[Path] = None,
    ):
        self.logger = ResearchLogger(log_dir)
        self.rate_limiter = RateLimiter()
        self.perplexity_api_key = perplexity_api_key
        self.research_dir = research_dir or RESEARCH_DIR
        self.research_dir.mkdir(parents=True, exist_ok=True)

    async def research(
        self,
        query: str,
        research_type: ResearchType = ResearchType.WEB_SEARCH,
        focus: Optional[List[str]] = None,
        max_results: int = 10,
        verify_with_fetch: bool = False,
    ) -> ResearchResult:
        """
        Perform research using the appropriate method.

        Args:
            query: Research query
            research_type: Type of research operation
            focus: Optional focus areas
            max_results: Maximum results
            verify_with_fetch: Whether to fetch and verify sources

        Returns:
            ResearchResult with findings and citations
        """
        research_id = self.logger.log_research_start(query, research_type)

        if research_type == ResearchType.WEB_SEARCH:
            async with PerplexityClient(
                api_key=self.perplexity_api_key, rate_limiter=self.rate_limiter
            ) as client:
                result = await client.search(query, focus=focus, max_results=max_results)

        elif research_type == ResearchType.DEEP_RESEARCH:
            async with PerplexityClient(
                api_key=self.perplexity_api_key, rate_limiter=self.rate_limiter
            ) as client:
                result = await client.deep_research(
                    query, focus_areas=focus, max_sources=max_results
                )

        elif research_type == ResearchType.WEB_FETCH:
            async with WebFetchClient(rate_limiter=self.rate_limiter) as client:
                fetch_result = await client.fetch(query)
                result = ResearchResult(
                    query=query,
                    research_type=ResearchType.WEB_FETCH,
                    content=fetch_result.get("content", ""),
                    error=fetch_result.get("error"),
                )

        elif research_type == ResearchType.CURL:
            curl = CurlWrapper()
            curl_result = await curl.execute(query)
            result = ResearchResult(
                query=query,
                research_type=ResearchType.CURL,
                content=curl_result.get("content", ""),
                error=None if curl_result["success"] else curl_result.get("error"),
            )

        else:
            result = ResearchResult(
                query=query,
                research_type=research_type,
                error=f"Unknown research type: {research_type}",
            )

        # Log result
        self.logger.log_research_result(research_id, result)

        # Log sources
        for citation in result.sources:
            self.logger.log_source(citation)

        return result

    async def save_result(self, result: ResearchResult) -> Path:
        """Save research result to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_{timestamp}_{result.research_type.value}.json"
        filepath = self.research_dir / filename

        with open(filepath, "w") as f:
            json.dump(result.to_dict(), f, indent=2)

        self.logger.logger.info(f"Saved research result to {filepath}")
        return filepath

    async def generate_citation_report(
        self, results: List[ResearchResult]
    ) -> Dict:
        """Generate a citation report from multiple research results"""
        citations = []
        for result in results:
            citations.extend(result.sources)

        # Sort by relevance score
        citations.sort(key=lambda x: x.relevance_score, reverse=True)

        return {
            "total_sources": len(citations),
            "citations": [c.to_dict() for c in citations],
            "generated_at": datetime.now().isoformat(),
        }


# Convenience functions
async def quick_search(query: str, api_key: Optional[str] = None) -> ResearchResult:
    """Quick web search for a query"""
    specialist = ResearchSpecialist(perplexity_api_key=api_key)
    return await specialist.research(query, ResearchType.WEB_SEARCH)


async def deep_research(
    query: str, api_key: Optional[str] = None, focus_areas: Optional[List[str]] = None
) -> ResearchResult:
    """Deep research on a topic"""
    specialist = ResearchSpecialist(perplexity_api_key=api_key)
    return await specialist.research(
        query, ResearchType.DEEP_RESEARCH, focus=focus_areas
    )


async def fetch_url(url: str) -> ResearchResult:
    """Fetch content from a URL"""
    specialist = ResearchSpecialist()
    return await specialist.research(url, ResearchType.WEB_FETCH)


# Main execution
if __name__ == "__main__":
    import sys

    async def demo():
        print("Research Specialist Demo")
        print("=" * 50)

        specialist = ResearchSpecialist()

        # Demo search (will fail without API key, demonstrating error handling)
        print("\n1. Testing search with missing API key:")
        result = await specialist.research(
            "What are the latest developments in AI?",
            ResearchType.WEB_SEARCH,
        )
        print(f"   Status: {'Success' if not result.error else 'Failed'}")
        if result.error:
            print(f"   Error: {result.error}")

        # Demo curl wrapper
        print("\n2. Testing curl wrapper (example.com):")
        curl = CurlWrapper()
        result = await curl.execute("https://example.com", user_agent="ResearchBot/1.0")
        print(f"   HTTP Code: {result.get('http_code')}")
        print(f"   Success: {result['success']}")
        if result["success"]:
            print(f"   Content preview: {result['content'][:200]}...")

        print("\n3. Research result structure:")
        print(f"   Query: {result}")
        print(f"   Type: {result}")
        print(f"   Duration: {result.duration_ms}ms")

    asyncio.run(demo())
