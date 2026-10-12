---
name: crawl4ai
description: "Scrapes web pages with the crawl4ai Python library, covering async crawling, Playwright-driven JavaScript pages, markdown generation, schema-based and LLM extraction, batch crawls, and session reuse. Use when working with crawl4ai, web scraping, async scraping, Playwright scraping, or extracting structured data from web pages."
version: "1.0.0"
---

# Crawl4AI - Web Scraping Toolkit

Async-first web scraping and structured data extraction. Fast markdown generation, schema-based extraction, vision capabilities, and production-ready patterns.

## Installation & Setup

```bash
# Install and verify
pip install crawl4ai
crawl4ai-doctor

# If issues, run setup
crawl4ai-setup
```

## Async Connection Pattern

Crawl4AI uses async/await throughout. Always use `AsyncWebCrawler`:

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    # Browser config (persistent across crawls)
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080
    )

    # Crawler config (per-crawl settings)
    crawler_config = CrawlerRunConfig(
        page_timeout=30000,
        screenshot=True,
        remove_overlay_elements=True
    )

    # Use context manager for proper cleanup
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://example.com",
            config=crawler_config
        )

        if result.success:
            print(f"Markdown: {len(result.markdown)} chars")
            print(f"Links: {len(result.links)} found")
            print(f"Media: {len(result.media)} items")

# Run async code
asyncio.run(main())
```

## Core Patterns

### 1. Markdown Extraction (Fastest)
```python
# Clean markdown ready for LLMs
result = await crawler.arun("https://docs.example.com")
with open("docs.md", "w") as f:
    f.write(result.markdown)
```

### 2. Schema-Based Extraction (No LLM Cost)
```python
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

schema = {
    "name": "products",
    "baseSelector": ".product",
    "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {"name": "price", "selector": ".price", "type": "text"}
    ]
}

config = CrawlerRunConfig(
    extraction_strategy=JsonCssExtractionStrategy(schema=schema)
)
result = await crawler.arun(url, config=config)
print(result.extracted_content)
```

### 3. LLM-Powered Extraction (Complex Content)
```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy

strategy = LLMExtractionStrategy(
    provider="openai/gpt-4o-mini",
    instruction="Extract all prices and product names"
)
config = CrawlerRunConfig(extraction_strategy=strategy)
result = await crawler.arun(url, config=config)
```

### 4. Batch Multi-URL Crawling
```python
urls = ["https://site1.com", "https://site2.com", "https://site3.com"]

results = await crawler.arun_many(
    urls=urls,
    config=crawler_config,
    max_concurrent=5
)

for result in results:
    if result.success:
        print(f"{result.url}: OK ({len(result.markdown)} chars)")
```

### 5. JavaScript & Session Handling
```python
# Wait for dynamic content
config = CrawlerRunConfig(
    wait_for="css:.dynamic-content",
    js_code="document.querySelector('.load-more').click();",
    page_timeout=60000,
    session_id="user_session"  # Reuse across crawls
)
result = await crawler.arun(url, config=config)
```

## Features Reference

| Feature | Config Option | Use Case |
|---------|---------------|----------|
| Screenshots | `screenshot=True` | Visual analysis, regression testing |
| Content Filter | `content_filter=BM25ContentFilter(query)` | Relevant content only |
| CSS Extraction | `extraction_strategy=JsonCssExtractionStrategy()` | Structured data, fast |
| LLM Extraction | `extraction_strategy=LLMExtractionStrategy()` | Complex patterns |
| Session Reuse | `session_id="id"` | Authenticated content |
| Wait Conditions | `wait_for="css:.selector"` | Dynamic content |
| JavaScript | `js_code="..."` | Page interaction, scrolling |
| Proxy Support | `BrowserConfig(proxy_config=...)` | Rotating IPs |
| Rate Limiting | `RateLimitConfig(requests_per_second=2)` | Respectful crawling |
| Circuit Breaker | `CircuitBreakerConfig(...)` | Failure resilience |

## Documentation Router

| Need | File | Purpose |
|------|------|---------|
| All SDK options | `complete-sdk-reference.md` | Full API documentation |
| Extract structured data | `extraction-strategies.md` | CSS, LLM, hybrid patterns |
| Handle dynamic pages | `javascript-handling.md` | SPAs, virtual scroll, waits |
| Fix errors gracefully | `error-handling.md` | Retry, circuit breaker |
| Speed up crawling | `performance-optimization.md` | Concurrency, caching, memory |
| Clean content | `content-cleanup.md` | Boilerplate removal |
| Production patterns | `best-practices.md` | Security, rate limits |
| Error recovery | `error-recovery.md` | DLQ patterns, resilience |

## Additional References

Read these only when the condition applies:

- `references/INSTALLATION.md` — when `pip install` or `crawl4ai-setup` fails, or when setting up browsers, Docker, or GPU support.
- `references/TROUBLESHOOTING.md` — when a crawl fails, times out, returns empty content, or is blocked.
- `references/QUICKREF.md` — for a quick lookup of configuration options and common calls.
- `references/SUMMARY.md` — for a one-page summary of the original reference package.
- `references/README.md` — for the index of the original reference package (overlaps with this file).
- `references/quality-guidelines.md` — when checking markdown fidelity or extraction accuracy.
- `references/security-practices.md` — before crawling sites that need credentials, proxies, or sensitive data handling.
- `references/performance/optimization-guide.md` — for an overview of crawl speed and resource tuning.
- `references/performance/caching-strategies.md` — when configuring cache modes.
- `references/performance/concurrent-crawling.md` — when raising concurrency for batch crawls.
- `references/performance/memory-management.md` — when a long crawl uses too much memory.
- `references/customization/css-customization.md` — when customizing CSS selection for extraction.
- `references/customization/extraction-customization.md` — when building or tuning extraction schemas or strategies.
- `references/customization/headers-customization.md` — when setting request headers.
- `references/customization/prompt-engineering.md` — when writing LLM extraction prompts.
- `references/customization/user-agents.md` — when choosing or rotating user agents.
- `references/docker-compose.yml` — a Docker Compose example for running the crawl4ai service.
- `tests/README.md` — when running the bundled tests in `tests/`.

## Quick Scripts

```bash
# Interactive schema generation
python scripts/schema-generator.py --interactive

# Extract API docs
python scripts/api-crawler.py https://api.example.com/docs

# Full-page screenshots
python scripts/visual-extractor.py https://site.com --full-page

# Build searchable docs
python scripts/knowledge-base-builder.py --seed https://docs.example.com
```

## Best Practices

1. Always use `async with AsyncWebCrawler()` for proper cleanup
2. Set `cache_mode=CacheMode.ENABLED` during development
3. Use schema extraction before LLM extraction (100x faster)
4. Add `remove_overlay_elements=True` for popups/modals
5. Use `max_concurrent` to respect rate limits
6. Add delays with `asyncio.sleep()` between requests
7. Implement retry logic with circuit breakers
8. Monitor memory for large-scale crawling

## Troubleshooting

**JavaScript not loading?** Set `wait_for` and increase `page_timeout` to 60000ms.

**Bot detection?** Use rotating user agents, add delays, try headless=False.

**Schema returns empty?** Test CSS selectors manually, check if elements exist.

**Session issues?** Verify `session_id` is consistent across crawls, check cookies in result.

See the Documentation Router and Additional References above for detailed guides on each topic.
