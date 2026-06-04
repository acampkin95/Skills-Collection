# Crawl4AI Error Recovery Guide

Advanced error recovery patterns for production crawling.

## Overview

This guide covers sophisticated error recovery strategies including:
- Intelligent retry mechanisms
- Circuit breaker implementation
- Dead letter queue management
- Checkpoint-based recovery
- Graceful degradation patterns

---

## 1. Advanced Retry Strategies

### Adaptive Retry with Error Classification

```python
import asyncio
import random
import time
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, Optional
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

class RetryStrategy(Enum):
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIBONACCI = "fibonacci"
    ADAPTIVE = "adaptive"

@dataclass
class RetryConfig:
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    jitter_factor: float = 0.3

class AdaptiveRetryHandler:
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.error_history = {}

    async def execute_with_retry(
        self,
        operation: Callable,
        *args,
        error_categories: dict = None,
        **kwargs
    ) -> tuple[bool, Any]:
        """Execute operation with adaptive retry logic."""
        error_categories = error_categories or {}

        for attempt in range(self.config.max_attempts):
            try:
                result = await operation(*args, **kwargs)
                return True, result

            except Exception as e:
                error_type = type(e).__name__
                error_category = error_categories.get(error_type, "unknown")

                # Update history for adaptive decisions
                self._record_attempt(error_type, attempt, e)

                # Determine if we should retry
                if not self._should_retry(error_type, attempt):
                    return False, e

                # Calculate delay
                delay = self._calculate_delay(attempt, error_category)

                if self.config.jitter:
                    delay = self._add_jitter(delay)

                print(f"Attempt {attempt + 1}/{self.config.max_attempts} failed: {e}")
                print(f"Retrying in {delay:.2f}s...")

                await asyncio.sleep(delay)

        return False, Exception(f"Max retries exceeded for {operation.__name__}")

    def _record_attempt(self, error_type: str, attempt: int, error: Exception):
        if error_type not in self.error_history:
            self.error_history[error_type] = {
                "attempts": [],
                "success_count": 0,
                "failure_count": 0,
            }

        self.error_history[error_type]["attempts"].append({
            "attempt": attempt,
            "timestamp": time.time(),
            "error": str(error),
        })

    def _should_retry(self, error_type: str, attempt: int) -> bool:
        if attempt >= self.config.max_attempts - 1:
            return False

        history = self.error_history.get(error_type)
        if not history:
            return True

        # Don't retry if we've failed too many times recently
        recent_failures = sum(
            1 for a in history["attempts"]
            if time.time() - a["timestamp"] < 300  # 5 minutes
        )

        return recent_failures < 10

    def _calculate_delay(self, attempt: int, error_category: str) -> float:
        if self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (2 ** attempt)
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay * (attempt + 1)
        elif self.config.strategy == RetryStrategy.FIBONACCI:
            delay = self._fibonacci_delay(attempt)
        else:  # ADAPTIVE
            delay = self._adaptive_delay(attempt, error_category)

        return min(delay, self.config.max_delay)

    def _fibonacci_delay(self, attempt: int) -> float:
        a, b = 0, 1
        for _ in range(attempt):
            a, b = b, a + b
        return self.config.base_delay * a

    def _adaptive_delay(self, attempt: int, error_category: str) -> float:
        base = self.config.base_delay * (2 ** attempt)

        # Adjust based on error category
        category_multipliers = {
            "network": 1.5,
            "timeout": 1.0,
            "rate_limit": 2.0,
            "blocked": 3.0,
            "server_error": 1.0,
        }

        multiplier = category_multipliers.get(error_category, 1.0)
        return base * multiplier

    def _add_jitter(self, delay: float) -> float:
        jitter_range = delay * self.config.jitter_factor
        return delay + random.uniform(-jitter_range, jitter_range)
```

### Strategy-Based Retry

```python
class StrategyBasedRetry:
    """Retry with different crawling strategies."""

    STRATEGIES = [
        {"wait_for": "networkidle", "timeout": 30000},
        {"wait_for": "domcontentloaded", "timeout": 15000},
        {"wait_for": "css:.main-content", "timeout": 20000},
        {"wait_for": "js:document.readyState === 'complete'", "timeout": 25000},
        {"headless": False, "timeout": 30000},  # Visible browser as last resort
    ]

    async def crawl_with_strategy_fallback(
        self,
        url: str,
        crawler: AsyncWebCrawler,
        strategies: list = None
    ) -> Any:
        """Try different strategies until one succeeds."""
        strategies = strategies or self.STRATEGIES

        for i, strategy in enumerate(strategies):
            try:
                config = CrawlerRunConfig(
                    page_timeout=strategy.get("timeout", 30000),
                    wait_for=strategy.get("wait_for"),
                )

                result = await crawler.arun(url, config=config)

                if result.success:
                    print(f"Strategy {i + 1} succeeded")
                    return result

            except Exception as e:
                print(f"Strategy {i + 1} failed: {e}")
                continue

        return None
```

---

## 2. Circuit Breaker Implementation

### Production-Grade Circuit Breaker

```python
import asyncio
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from threading import Lock

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitError(Exception):
    """Raised when circuit breaker is open."""
    pass

@dataclass
class CircuitMetrics:
    failure_count: int = 0
    success_count: int = 0
    last_failure: Optional[float] = None
    last_success: Optional[float] = None
    state: CircuitState = CircuitState.CLOSED
    half_open_successes: int = 0

@dataclass
class CircuitConfig:
    failure_threshold: int = 5
    success_threshold: int = 3  # For half-open state
    reset_timeout: float = 60.0
    half_open_timeout: float = 30.0
    monitoring_window: int = 300  # 5 minutes

class CircuitBreaker:
    """
    Production-grade circuit breaker implementation.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failures exceeded threshold, requests rejected
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(self, config: CircuitConfig = None):
        self.config = config or CircuitConfig()
        self.circuits: Dict[str, CircuitMetrics] = {}
        self.lock = Lock()

    def register(self, key: str):
        """Register a new circuit."""
        with self.lock:
            if key not in self.circuits:
                self.circuits[key] = CircuitMetrics()

    def record_failure(self, key: str):
        """Record a failure for the circuit."""
        with self.lock:
            if key not in self.circuits:
                self.register(key)

            metrics = self.circuits[key]
            metrics.failure_count += 1
            metrics.last_failure = time.time()

            # Check if we should open the circuit
            if self._should_open(metrics):
                metrics.state = CircuitState.OPEN
                print(f"Circuit {key} OPENED after {metrics.failure_count} failures")

    def record_success(self, key: str):
        """Record a success for the circuit."""
        with self.lock:
            if key not in self.circuits:
                self.register(key)

            metrics = self.circuits[key]
            metrics.success_count += 1
            metrics.last_success = time.time()

            if metrics.state == CircuitState.HALF_OPEN:
                metrics.half_open_successes += 1
                if metrics.half_open_successes >= self.config.success_threshold:
                    metrics.state = CircuitState.CLOSED
                    metrics.failure_count = 0
                    metrics.half_open_successes = 0
                    print(f"Circuit {key} CLOSED (recovered)")

    def can_execute(self, key: str) -> bool:
        """Check if execution is allowed."""
        with self.lock:
            if key not in self.circuits:
                self.register(key)
                return True

            metrics = self.circuits[key]

            if metrics.state == CircuitState.CLOSED:
                return True

            if metrics.state == CircuitState.OPEN:
                # Check if reset timeout has passed
                if metrics.last_failure:
                    elapsed = time.time() - metrics.last_failure
                    if elapsed >= self.config.reset_timeout:
                        metrics.state = CircuitState.HALF_OPEN
                        metrics.half_open_successes = 0
                        print(f"Circuit {key} HALF_OPEN (testing recovery)")
                        return True
                return False

            if metrics.state == CircuitState.HALF_OPEN:
                # Allow limited requests
                return metrics.half_open_successes < self.config.success_threshold

            return True

    async def execute(self, key: str, operation: Callable, *args, **kwargs):
        """Execute operation with circuit breaker protection."""
        if not self.can_execute(key):
            raise CircuitError(f"Circuit {key} is OPEN")

        try:
            result = await operation(*args, **kwargs)
            self.record_success(key)
            return result

        except Exception as e:
            self.record_failure(key)
            raise

    def _should_open(self, metrics: CircuitMetrics) -> bool:
        """Determine if circuit should open."""
        if metrics.state != CircuitState.CLOSED:
            return False

        return metrics.failure_count >= self.config.failure_threshold

    def get_status(self, key: str) -> dict:
        """Get circuit status."""
        with self.lock:
            if key not in self.circuits:
                return {"state": "not_registered"}

            metrics = self.circuits[key]
            return {
                "state": metrics.state.value,
                "failure_count": metrics.failure_count,
                "success_count": metrics.success_count,
                "last_failure": metrics.last_failure,
                "last_success": metrics.last_success,
            }

    def reset(self, key: str):
        """Reset circuit to closed state."""
        with self.lock:
            if key in self.circuits:
                self.circuits[key] = CircuitMetrics()
```

### Usage Example

```python
# Initialize circuit breaker
breaker = CircuitBreaker(CircuitConfig(
    failure_threshold=5,
    reset_timeout=60.0,
    success_threshold=3,
))

async def protected_crawl(url: str):
    domain = url.split("/")[2]  # Extract domain

    return await breaker.execute(
        domain,
        crawler.arun,
        url
    )

# Check circuit status
print(breaker.get_status("example.com"))
```

---

## 3. Dead Letter Queue (DLQ)

### Persistent Dead Letter Queue

```python
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict

@dataclass
class DLQEntry:
    url: str
    error: str
    timestamp: float
    attempt_count: int
    context: dict
    original_error: Optional[dict] = None

class DeadLetterQueue:
    """
    Persistent dead letter queue for failed crawl operations.

    Entries are stored as JSON files in the DLQ directory.
    Supports retry with exponential backoff and context preservation.
    """

    def __init__(self, queue_dir: str = "./dlq", max_retries: int = 3):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries

    def _get_entry_path(self, url: str) -> Path:
        """Generate unique filename for entry."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        return self.queue_dir / f"{url_hash}.json"

    def add(
        self,
        url: str,
        error: str,
        context: dict = None,
        original_error: dict = None
    ):
        """Add failed crawl to dead letter queue."""
        entry = DLQEntry(
            url=url,
            error=error,
            timestamp=datetime.now().timestamp(),
            attempt_count=0,
            context=context or {},
            original_error=original_error,
        )

        path = self._get_entry_path(url)
        with open(path, "w") as f:
            json.dump(asdict(entry), f, indent=2)

        print(f"Added to DLQ: {url}")

    def get(self, url: str) -> Optional[DLQEntry]:
        """Get entry from queue."""
        path = self._get_entry_path(url)
        if path.exists():
            with open(path) as f:
                return DLQEntry(**json.load(f))
        return None

    def get_all(self) -> list:
        """Get all entries in queue."""
        entries = []
        for path in self.queue_dir.glob("*.json"):
            with open(path) as f:
                entries.append(DLQEntry(**json.load(f)))
        return entries

    def get_retryable(self, max_age_hours: int = 24) -> list:
        """Get entries eligible for retry."""
        retryable = []
        cutoff = datetime.now().timestamp() - (max_age_hours * 3600)

        for entry in self.get_all():
            if entry.attempt_count < self.max_retries:
                # Calculate backoff
                backoff = 2 ** entry.attempt_count * 60  # Exponential backoff
                retry_after = entry.timestamp + backoff

                if datetime.now().timestamp() >= retry_after:
                    retryable.append(entry)

        return retryable

    def remove(self, url: str):
        """Remove entry from queue after successful retry."""
        path = self._get_entry_path(url)
        if path.exists():
            path.unlink()
            print(f"Removed from DLQ: {url}")

    def increment_attempt(self, url: str):
        """Increment attempt count for entry."""
        entry = self.get(url)
        if entry:
            entry.attempt_count += 1
            path = self._get_entry_path(url)
            with open(path, "w") as f:
                json.dump(asdict(entry), f, indent=2)

    def clear(self):
        """Clear all entries from queue."""
        for path in self.queue_dir.glob("*.json"):
            path.unlink()
        print("DLQ cleared")
```

---

## 4. Checkpoint-Based Recovery

### Durable Checkpoint Manager

```python
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Set
from dataclasses import dataclass, field

@dataclass
class CheckpointState:
    completed: Set[str] = field(default_factory=set)
    failed: Set[str] = field(default_factory=set)
    in_progress: Set[str] = field(default_factory=set)
    start_time: Optional[str] = None
    last_update: Optional[str] = None

class CheckpointManager:
    """
    Durable checkpoint manager for long-running crawl operations.

    Features:
    - Automatic persistence after each operation
    - Support for resume from any point
    - In-progress tracking
    - Failed URL tracking
    """

    def __init__(self, checkpoint_file: str = "crawl_checkpoint.json"):
        self.checkpoint_file = Path(checkpoint_file)
        self.state = CheckpointState()
        self._load()

    def _load(self):
        """Load checkpoint from disk."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                data = json.load(f)
                self.state = CheckpointState(
                    completed=set(data.get("completed", [])),
                    failed=set(data.get("failed", [])),
                    in_progress=set(data.get("in_progress", [])),
                    start_time=data.get("start_time"),
                    last_update=data.get("last_update"),
                )

    def _save(self):
        """Save checkpoint to disk."""
        data = {
            "completed": list(self.state.completed),
            "failed": list(self.state.failed),
            "in_progress": list(self.state.in_progress),
            "start_time": self.state.start_time,
            "last_update": datetime.now().isoformat(),
        }

        # Write atomically using temp file
        temp_file = self.checkpoint_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)
        temp_file.replace(self.checkpoint_file)

    def start_session(self, urls: list):
        """Initialize a new crawl session."""
        self.state.start_time = datetime.now().isoformat()
        remaining = self.get_remaining(urls)
        print(f"Starting crawl session: {len(remaining)} URLs to process")
        self._save()

    def mark_started(self, url: str):
        """Mark URL as in progress."""
        self.state.in_progress.add(url)
        self._save()

    def mark_completed(self, url: str):
        """Mark URL as successfully completed."""
        self.state.in_progress.discard(url)
        self.state.completed.add(url)
        self._save()

    def mark_failed(self, url: str):
        """Mark URL as failed."""
        self.state.in_progress.discard(url)
        self.state.failed.add(url)
        self._save()

    def get_remaining(self, urls: list) -> list:
        """Get URLs that haven't been processed."""
        return [u for u in urls if u not in self.state.completed]

    def get_progress(self, total: int) -> dict:
        """Get current progress summary."""
        completed = len(self.state.completed)
        failed = len(self.state.failed)
        remaining = total - completed - failed

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "remaining": remaining,
            "progress_percent": (completed / total * 100) if total > 0 else 0,
        }

    def reset(self):
        """Reset all checkpoints."""
        self.state = CheckpointState()
        self._save()
        print("Checkpoint reset")
```

---

## 5. Graceful Degradation

### Multi-Level Fallback System

```python
from enum import Enum
from typing import Any, Optional, Callable
from dataclasses import dataclass
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

class ExtractionLevel(Enum):
    CSS = "css"
    LLM = "llm"
    BASIC = "basic"
    MINIMAL = "minimal"

@dataclass
class FallbackStrategy:
    level: ExtractionLevel
    priority: int
    config_factory: Callable
    max_attempts: int = 1

class GracefulDegradationCrawler:
    """
    Crawler with graceful degradation across multiple extraction levels.
    """

    def __init__(self):
        self.strategies = [
            FallbackStrategy(
                level=ExtractionLevel.CSS,
                priority=1,
                config_factory=self._css_config,
            ),
            FallbackStrategy(
                level=ExtractionLevel.LLM,
                priority=2,
                config_factory=self._llm_config,
                max_attempts=2,
            ),
            FallbackStrategy(
                level=ExtractionLevel.BASIC,
                priority=3,
                config_factory=self._basic_config,
            ),
            FallbackStrategy(
                level=ExtractionLevel.MINIMAL,
                priority=4,
                config_factory=self._minimal_config,
            ),
        ]

    async def crawl_with_fallback(
        self,
        url: str,
        crawler: AsyncWebCrawler,
        on_level_complete: Callable = None
    ) -> dict:
        """Crawl with fallback through multiple levels."""
        result = {
            "url": url,
            "success": False,
            "level": None,
            "data": None,
            "attempts": [],
        }

        for strategy in self.strategies:
            try:
                config = strategy.config_factory()

                for attempt in range(strategy.max_attempts):
                    crawl_result = await crawler.arun(url, config=config)

                    if crawl_result.success:
                        result["success"] = True
                        result["level"] = strategy.level.value
                        result["data"] = {
                            "markdown": crawl_result.markdown,
                            "html": crawl_result.html,
                            "links": crawl_result.links,
                            "media": crawl_result.media,
                        }
                        result["attempts"].append({
                            "level": strategy.level.value,
                            "attempt": attempt + 1,
                            "success": True,
                        })

                        if on_level_complete:
                            on_level_complete(strategy.level, crawl_result)

                        return result

            except Exception as e:
                result["attempts"].append({
                    "level": strategy.level.value,
                    "attempt": attempt + 1,
                    "success": False,
                    "error": str(e),
                })
                continue

        return result

    def _css_config(self) -> CrawlerRunConfig:
        return CrawlerRunConfig(
            extraction_strategy=JsonCssExtractionStrategy(schema={}),
        )

    def _llm_config(self) -> CrawlerRunConfig:
        return CrawlerRunConfig(
            extraction_strategy=LLMExtractionStrategy(
                provider="openai",
                instruction="Extract main content",
            ),
        )

    def _basic_config(self) -> CrawlerRunConfig:
        return CrawlerRunConfig()

    def _minimal_config(self) -> CrawlerRunConfig:
        return CrawlerRunConfig(
            page_timeout=5000,
            screenshot=False,
        )
```

---

## Summary

| Pattern | Use Case | Benefits |
|---------|----------|----------|
| Adaptive Retry | Variable error conditions | Intelligent backoff |
| Circuit Breaker | External service protection | Prevents cascade failures |
| Dead Letter Queue | Failed job tracking | Enables manual review |
| Checkpoint Recovery | Long operations | Resume from interruption |
| Graceful Degradation | Partial failures | Maximize data extraction |
