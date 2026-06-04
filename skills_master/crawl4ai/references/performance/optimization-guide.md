# Crawl4AI Performance Optimization

Speed, memory, and resource optimization strategies.

## Speed Optimization

### Parallel Crawling

```python
import asyncio
from crawl4ai import AsyncWebCrawler

class ParallelCrawler:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def crawl_parallel(self, urls: list):
        """Crawl URLs in parallel with controlled concurrency."""
        async with AsyncWebCrawler() as crawler:
            async with self.semaphore:
                results = await crawler.arun_many(urls)
        return results
```

### Batched Processing

```python
async def crawl_batched(
    crawler,
    urls: list,
    batch_size: int = 20,
    delay_between_batches: float = 1.0
):
    """Process URLs in batches to manage resources."""
    results = []

    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        batch_results = await crawler.arun_many(batch)
        results.extend(batch_results)

        if i + batch_size < len(urls):
            await asyncio.sleep(delay_between_batches)

    return results
```

---

## Memory Optimization

### Stream Processing

```python
import asyncio
from typing import AsyncGenerator

class StreamProcessor:
    async def process_stream(
        self,
        urls: list,
        processor,
        checkpoint_interval: int = 100
    ) -> AsyncGenerator[dict, None]:
        """Process URLs and yield results without storing all in memory."""
        processed = 0

        for url in urls:
            try:
                result = await processor(url)
                yield result
                processed += 1

                if processed % checkpoint_interval == 0:
                    yield {"_checkpoint": processed}

            except Exception as e:
                yield {"_error": str(url), "error": e}
```

---

## Benchmarking

```python
import time
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    url_count: int
    total_time: float
    avg_time_per_url: float
    success_count: int
    success_rate: float

async def benchmark_crawler(
    crawler,
    urls: list,
    max_concurrent: int = 5
) -> BenchmarkResult:
    """Benchmark crawler performance."""
    start = time.perf_counter()

    results = await crawler.arun_many(urls, max_concurrent=max_concurrent)

    total_time = time.perf_counter() - start
    successful = sum(1 for r in results if r.success)

    return BenchmarkResult(
        url_count=len(urls),
        total_time=total_time,
        avg_time_per_url=total_time / len(urls),
        success_count=successful,
        success_rate=successful / len(urls),
    )
```
