# Performance Optimization Guide

Optimize Crawl4AI for speed, resource efficiency, and cost reduction.

## Overview

Performance optimization covers:
- Crawling speed improvements
- Memory efficiency
- Network bandwidth optimization
- Cost reduction strategies
- Concurrent processing patterns

---

## 1. Concurrent Crawling

### Basic Concurrency

```python
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

urls = [
    "https://site.com/page1",
    "https://site.com/page2",
    "https://site.com/page3",
    # ... more URLs
]

async def crawl_all(urls):
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(
            urls=urls,
            max_concurrent=10  # Adjust based on target server
        )
    return results

results = asyncio.run(crawl_all(urls))
```

### Rate Limiting

```python
import asyncio
import random

async def crawl_with_rate_limit(urls, delay_range=(1, 3)):
    async with AsyncWebCrawler() as crawler:
        results = []
        for url in urls:
            result = await crawler.arun(url)
            results.append(result)
            # Random delay between requests
            delay = random.uniform(*delay_range)
            await asyncio.sleep(delay)
    return results
```

### Semaphore-Based Concurrency

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def crawl_with_semaphore(urls, max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def crawl_with_limit(url):
        async with semaphore:
            async with AsyncWebCrawler() as crawler:
                return await crawler.arun(url)

    tasks = [crawl_with_limit(url) for url in urls]
    return await asyncio.gather(*tasks)
```

---

## 2. Memory Optimization

### Streaming Large Responses

```python
async def stream_crawl(url):
    browser_config = BrowserConfig(headless=True)
    crawler_config = CrawlerRunConfig(
        page_timeout=30000,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url, config=crawler_config)

    # Process in chunks
    markdown = result.markdown
    chunk_size = 10000
    for i in range(0, len(markdown), chunk_size):
        chunk = markdown[i:i + chunk_size]
        # Process chunk without loading all into memory
```

### Limit Screenshot Size

```python
# Don't capture screenshots unless needed
crawler_config = CrawlerRunConfig(
    screenshot=False,  # Disable by default
    screenshot_timeout=5000,  # Add timeout
)

# Or resize before saving
import base64
from PIL import Image
from io import BytesIO

def optimize_screenshot(base64_data, max_width=800):
    image_data = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_data))

    # Resize if needed
    if image.width > max_width:
        ratio = max_width / image.width
        image = image.resize((max_width, int(image.height * ratio)))

    # Save optimized
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode()
```

### Browser Memory Management

```python
# Reuse browser instance
browser_config = BrowserConfig(
    headless=True,
    java_script_enabled=True,
    # Limit browser memory
    browser_args=["--no-sandbox", "--disable-setuid-sandbox"]
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    # Process multiple pages with same browser
    for url in urls:
        result = await crawler.arun(url)
        # Browser stays alive between requests
```

---

## 3. Network Optimization

### Compression

```python
# Enable gzip/deflate if supported
crawler_config = CrawlerRunConfig(
    # Crawl4AI handles compression automatically
)
```

### Caching

```python
from crawl4ai import CacheMode

# Enable caching during development
crawler_config = CrawlerRunConfig(
    cache_mode=CacheMode.ENABLED
)

# Bypass cache for fresh data
crawler_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS
)
```

### Conditional Requests

```python
async def crawl_with_etag(url, cached_etag=None):
    browser_config = BrowserConfig(
        headers={"If-None-Match": cached_etag} if cached_etag else {}
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url)

        # Save ETag for future requests
        new_etag = result.headers.get("ETag")
        return result, new_etag
```

---

## 4. Browser Configuration Tuning

### Minimal Browser

```python
browser_config = BrowserConfig(
    headless=True,
    java_script_enabled=False,  # Disable if not needed
    images_enabled=False,       # Don't load images
    viewport_width=1280,
    viewport_height=720,
)
```

### Fast Page Loading

```python
crawler_config = CrawlerRunConfig(
    page_timeout=10000,         # Shorter timeout
    wait_for="domcontentloaded",  # Don't wait for full load
    remove_overlay_elements=True,
)
```

### Virtual Scrolling Optimization

```python
from crawl4ai import VirtualScrollConfig

crawler_config = CrawlerRunConfig(
    virtual_scroll_config=VirtualScrollConfig(
        scroll_distance=500,      # Smaller scroll increments
        scroll_delay=0.1,         # Shorter delay
        max_scrolls=50,           # Limit total scrolls
        wait_after_scroll=0.1,    # Brief wait
    )
)
```

---

## 5. Extraction Optimization

### CSS Over LLM

```python
# Fast CSS extraction
extraction_strategy = JsonCssExtractionStrategy(schema=product_schema)
crawler_config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

# vs slower LLM extraction
llm_strategy = LLMExtractionStrategy(provider="openai/gpt-4o-mini")
```

### Limit Markdown Generation

```python
from crawl4ai.content_filter_strategy import PruningContentFilter

# Only extract what you need
filter = PruningContentFilter(threshold=0.6)
md_generator = DefaultMarkdownGenerator(content_filter=filter)

crawler_config = CrawlerRunConfig(markdown_generator=md_generator)
```

### Selective Field Extraction

```python
# Extract only needed fields
schema = {
    "baseSelector": ".product",
    "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        # Only extract essential fields
    ]
}
```

---

## 6. Cost Optimization

### Token Reduction

```python
# Use smaller LLM models
LLMExtractionStrategy(provider="openai/gpt-4o-mini")  # Cheaper
# vs
LLMExtractionStrategy(provider="openai/gpt-4o")       # More expensive

# Reduce context with CSS pre-filtering
extraction_strategy = LLMExtractionStrategy(
    provider="openai/gpt-4o-mini",
    instruction="Extract X from this specific section",
    chunk_size=1000  # Smaller chunks
)
```

### Batch Processing

```python
# Process multiple URLs in single session
async with AsyncWebCrawler() as crawler:
    # Batch reduces per-request overhead
    results = await crawler.arun_many(urls, max_concurrent=10)
```

### Caching Strategy

```python
from crawl4ai import CacheMode

# Cache successful responses
crawler_config = CrawlerRunConfig(
    cache_mode=CacheMode.ENABLED
)

# For volatile content, use conditional
crawler_config = CrawlerRunConfig(
    cache_mode=CacheMode.ONLY_IF_CACHED
)
```

---

## 7. Monitoring and Profiling

### Request Timing

```python
import time

async def profile_crawl(urls):
    async with AsyncWebCrawler() as crawler:
        for url in urls:
            start = time.time()
            result = await crawler.arun(url)
            elapsed = time.time() - start

            print(f"{url}: {elapsed:.2f}s - {'OK' if result.success else 'FAIL'}")
```

### Memory Profiling

```python
import tracemalloc

tracemalloc.start()

# Run crawl
result = await crawler.arun(url)

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024:.1f} KB")
print(f"Peak: {peak / 1024:.1f} KB")

tracemalloc.stop()
```

### Throughput Benchmark

```python
import time

async def benchmark(urls, concurrency=5):
    start = time.time()

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(urls, max_concurrent=concurrency)

    elapsed = time.time() - start
    success_count = sum(1 for r in results if r.success)

    print(f"URLs: {len(urls)}")
    print(f"Concurrency: {concurrency}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Throughput: {len(urls)/elapsed:.1f} URLs/sec")
    print(f"Success rate: {success_count/len(urls)*100:.1f}%")
```

---

## 8. Recommended Configurations

### Fastest Crawling

```python
browser_config = BrowserConfig(
    headless=True,
    java_script_enabled=False,
    images_enabled=False,
    viewport_width=800,
    viewport_height=600,
)

crawler_config = CrawlerRunConfig(
    page_timeout=10000,
    wait_for="domcontentloaded",
    screenshot=False,
    cache_mode=CacheMode.ENABLED,
)
```

### Balanced Performance

```python
browser_config = BrowserConfig(
    headless=True,
    java_script_enabled=True,
    viewport_width=1280,
    viewport_height=720,
)

crawler_config = CrawlerRunConfig(
    page_timeout=30000,
    wait_for="networkidle",
    screenshot=False,
    remove_overlay_elements=True,
)
```

### High Accuracy (Slower)

```python
browser_config = BrowserConfig(
    headless=True,
    java_script_enabled=True,
    viewport_width=1920,
    viewport_height=1080,
)

crawler_config = CrawlerRunConfig(
    page_timeout=60000,
    wait_for="networkidle",
    screenshot=True,
    cache_mode=CacheMode.BYPASS,
)
```
