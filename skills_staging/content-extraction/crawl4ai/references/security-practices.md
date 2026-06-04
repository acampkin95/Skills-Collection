# Crawl4AI Security Practices

Safe crawling practices, robots.txt compliance, and rate limiting.

## Responsible Crawling

### robots.txt Compliance

```python
import httpx
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Set, List, Optional
from datetime import datetime
import asyncio

@dataclass
class RobotsRule:
    """Represents a robots.txt rule."""
    user_agent: str
    allow: List[str]
    disallow: List[str]
    crawl_delay: Optional[int]
    sitemaps: List[str]

class RobotsTxtChecker:
    """Check and respect robots.txt rules."""

    def __init__(self, user_agent: str = "Crawl4AI/1.0"):
        self.user_agent = user_agent
        self._cache = {}

    async def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        domain = urlparse(url).netloc

        if domain in self._cache:
            rules = self._cache[domain]
        else:
            rules = await self._fetch_robots_txt(domain)
            self._cache[domain] = rules

        if not rules:
            return True  # No robots.txt, allow by default

        # Check if our user agent is allowed
        matching_rules = [
            r for r in rules
            if r.user_agent == "*" or r.user_agent == self.user_agent
        ]

        if not matching_rules:
            return True

        # Check the most specific rule
        for rule in matching_rules:
            for path in rule.disallow:
                if url.startswith(f"https://{domain}{path}"):
                    return False

            for path in rule.allow:
                if url.startswith(f"https://{domain}{path}"):
                    return True

        return True

    async def _fetch_robots_txt(self, domain: str) -> List[RobotsRule]:
        """Fetch and parse robots.txt."""
        robots_url = f"https://{domain}/robots.txt"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(robots_url, timeout=10.0)

                if response.status_code != 200:
                    return []

                return self._parse_robots_txt(response.text)

        except Exception:
            return []

    def _parse_robots_txt(self, content: str) -> List[RobotsRule]:
        """Parse robots.txt content."""
        rules = []
        current_rule = None

        for line in content.split("\n"):
            line = line.strip().lower()

            if not line or line.startswith("#"):
                continue

            if line.startswith("user-agent:"):
                if current_rule:
                    rules.append(current_rule)
                current_rule = RobotsRule(
                    user_agent=line.split(":")[1].strip(),
                    allow=[],
                    disallow=[],
                    crawl_delay=None,
                    sitemaps=[],
                )
            elif line.startswith("allow:") and current_rule:
                current_rule.allow.append(line.split(":")[1].strip())
            elif line.startswith("disallow:") and current_rule:
                current_rule.disallow.append(line.split(":")[1].strip())
            elif line.startswith("crawl-delay:") and current_rule:
                try:
                    current_rule.crawl_delay = int(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("sitemap:") and current_rule:
                current_rule.sitemaps.append(line.split(":")[1].strip())

        if current_rule:
            rules.append(current_rule)

        return rules
```

### Rate Limiting

```python
import asyncio
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class RateLimitConfig:
    requests_per_second: float = 1.0
    requests_per_minute: float = 60.0
    burst_size: int = 5
    retry_after_base: float = 1.0

class RateLimiter:
    """Token bucket rate limiter with adaptive backoff."""

    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.tokens = config.burst_size if config else 5
        self.last_update = time.monotonic()
        self.domain_limits = {}  # Per-domain rate limits
        self.lock = asyncio.Lock()

    async def acquire(self, domain: str = None) -> float:
        """Acquire a token, returns wait time if throttled."""
        async with self.lock:
            current = time.monotonic()
            elapsed = current - self.last_update

            # Refill tokens based on rate
            refill_rate = self.config.requests_per_second
            self.tokens = min(
                self.tokens + elapsed * refill_rate,
                self.config.burst_size
            )
            self.last_update = current

            # Check domain-specific limits
            if domain:
                if domain not in self.domain_limits:
                    self.domain_limits[domain] = {
                        "requests": 0,
                        "window_start": current,
                    }

                domain_window = self.domain_limits[domain]
                window_duration = 60.0  # 1 minute window

                if current - domain_window["window_start"] >= window_duration:
                    domain_window["requests"] = 0
                    domain_window["window_start"] = current

                if domain_window["requests"] >= self.config.requests_per_minute:
                    wait_time = window_duration - (current - domain_window["window_start"])
                    return max(wait_time, self.config.retry_after_base)

            if self.tokens >= 1:
                self.tokens -= 1
                if domain:
                    if domain in self.domain_limits:
                        self.domain_limits[domain]["requests"] += 1
                return 0.0

            # Calculate wait time for next token
            deficit = 1 - self.tokens
            wait_time = deficit / self.config.requests_per_second

            return max(wait_time, self.config.retry_after_base)

    async def wait(self, domain: str = None):
        """Wait until a token is available."""
        wait_time = await self.acquire(domain)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
```

---

## Data Sanitization

### Sensitive Data Detection

```python
import re
from dataclasses import dataclass
from typing import Set, List

@dataclass
class SensitiveDataPattern:
    """Pattern for detecting sensitive data."""
    name: str
    pattern: re.Pattern
    severity: str  # "high", "medium", "low"
    action: str  # "redact", "block", "warn"

class SensitiveDataDetector:
    """Detect and handle sensitive data in crawl results."""

    PATTERNS = [
        SensitiveDataPattern(
            name="email",
            pattern=re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            severity="medium",
            action="redact",
        ),
        SensitiveDataPattern(
            name="phone",
            pattern=re.compile(r'\+?[\d\s\-()]{10,}'),
            severity="medium",
            action="redact",
        ),
        SensitiveDataPattern(
            name="ssn",
            pattern=re.compile(r'\d{3}-\d{2}-\d{4}'),
            severity="high",
            action="block",
        ),
        SensitiveDataPattern(
            name="credit_card",
            pattern=re.compile(r'\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}'),
            severity="high",
            action="block",
        ),
        SensitiveDataPattern(
            name="api_key",
            pattern=re.compile(r'(api[_-]?key|apikey|secret|token)[\s=:]["\' ]?([a-zA-Z0-9]{20,})', re.IGNORECASE),
            severity="high",
            action="block",
        ),
    ]

    def __init__(self):
        self.findings = []

    def scan(self, content: str) -> dict:
        """Scan content for sensitive data."""
        self.findings = []

        for pattern in self.PATTERNS:
            matches = pattern.pattern.findall(content)
            for match in matches:
                self.findings.append({
                    "type": pattern.name,
                    "severity": pattern.severity,
                    "action": pattern.action,
                    "count": len(matches) if isinstance(matches[0], (list, tuple)) else len(matches),
                })

        return {
            "has_sensitive_data": len(self.findings) > 0,
            "findings": self.findings,
            "should_redact": any(f["action"] == "redact" for f in self.findings),
            "should_block": any(f["action"] == "block" for f in self.findings),
        }

    def redact(self, content: str) -> str:
        """Redact sensitive data from content."""
        redacted = content

        for pattern in self.PATTERNS:
            if pattern.action in ("redact", "block"):
                redacted = pattern.pattern.sub("[REDACTED]", redacted)

        return redacted
```

---

## Access Control

### URL Filtering

```python
import re
from typing import Set, Optional, Callable
from urllib.parse import urlparse

class URLFilter:
    """Filter URLs based on configurable rules."""

    def __init__(self):
        self.allowed_domains: Set[str] = set()
        self.blocked_domains: Set[str] = set()
        self.allowed_patterns: list = []
        self.blocked_patterns: list = []

    def set_allowed_domains(self, domains: list):
        """Set list of allowed domains."""
        self.allowed_domains = set(domains)

    def set_blocked_domains(self, domains: list):
        """Set list of blocked domains."""
        self.blocked_domains = set(domains)

    def add_allowed_pattern(self, pattern: str):
        """Add regex pattern for allowed URLs."""
        self.allowed_patterns.append(re.compile(pattern))

    def add_blocked_pattern(self, pattern: str):
        """Add regex pattern for blocked URLs."""
        self.blocked_patterns.append(re.compile(pattern))

    def is_allowed(self, url: str) -> tuple[bool, Optional[str]]:
        """
        Check if URL is allowed.
        Returns (is_allowed, reason_if_not_allowed).
        """
        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in ("http", "https"):
                return False, "Invalid URL scheme"

            # Check blocked domains
            if parsed.netloc in self.blocked_domains:
                return False, f"Domain {parsed.netloc} is blocked"

            # Check allowed domains (if set)
            if self.allowed_domains and parsed.netloc not in self.allowed_domains:
                return False, f"Domain {parsed.netloc} not in allowed list"

            # Check blocked patterns
            for pattern in self.blocked_patterns:
                if pattern.search(url):
                    return False, f"URL matches blocked pattern"

            # Check allowed patterns
            if self.allowed_patterns:
                if not any(p.search(url) for p in self.allowed_patterns):
                    return False, "URL does not match any allowed pattern"

            return True, None

        except Exception as e:
            return False, f"URL parsing error: {e}"

    def filter_urls(self, urls: list) -> list:
        """Filter a list of URLs."""
        allowed = []
        for url in urls:
            is_allowed, _ = self.is_allowed(url)
            if is_allowed:
                allowed.append(url)
        return allowed
```

---

## Compliance Checklist

```python
class ComplianceChecker:
    """Check crawling compliance with best practices."""

    CHECKS = [
        "robots_txt_respected",
        "rate_limiting_enabled",
        "sensitive_data_masked",
        "url_filtering_enabled",
        "proper_user_agent",
        "cache_control_respected",
    ]

    def __init__(self):
        self.violations = []

    def check_compliance(self, config: dict) -> dict:
        """Check configuration for compliance."""
        self.violations = []

        # Check robots.txt
        if not config.get("respect_robots_txt", False):
            self.violations.append("robots.txt not being respected")

        # Check rate limiting
        if not config.get("rate_limit"):
            self.violations.append("Rate limiting not configured")

        # Check sensitive data handling
        if not config.get("mask_sensitive_data", False):
            self.violations.append("Sensitive data masking not enabled")

        # Check URL filtering
        if not config.get("url_filter"):
            self.violations.append("URL filtering not configured")

        # Check user agent
        if not config.get("user_agent"):
            self.violations.append("User agent not set")

        return {
            "compliant": len(self.violations) == 0,
            "violations": self.violations,
            "checks_passed": len(self.CHECKS) - len(self.violations),
            "checks_failed": len(self.violations),
        }
```
