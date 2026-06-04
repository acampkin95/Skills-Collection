# Concurrent Crawling

Parallel execution strategies.

## Concurrency Models

### Semaphore-Based

```python
import asyncio
from crawl4ai import AsyncWebCrawler

class ConcurrentCrawler:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def crawl_with_semaphore(
        self,
        crawler,
        url: str
    ) -> dict:
        """Crawl with semaphore to limit concurrency."""
        async with self.semaphore:
            result = await crawler.arun(url)
            return {
                "url": url,
                "success": result.success,
                "content_length": len(result.markdown) if result.markdown else 0,
            }
```

### Priority Queue

```python
import asyncio
from dataclasses import dataclass
from typing import Optional

@dataclass
class PriorityUrl:
    url: str
    priority: int  # Lower = higher priority
    max_retries: int = 3

class PriorityCrawler:
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.priority_queue = asyncio.PriorityQueue()

    async def add_url(self, url: str, priority: int = 10):
        await self.priority_queue.put(PriorityUrl(url, priority))

    async def crawl_prioritized(self, crawler, total_urls: int):
        """Crawl URLs by priority."""
        results = []

        async def worker():
            while not self.priority_queue.empty():
                item = await self.priority_queue.get()
                result = await crawler.arun(item.url)
                results.append(result)

        workers = [
            asyncio.create_task(worker())
            for _ in range(self.max_concurrent)
        ]

        await asyncio.gather(*workers)
        return results
```
