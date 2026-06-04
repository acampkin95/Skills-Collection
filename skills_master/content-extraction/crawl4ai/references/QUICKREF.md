# Crawl4AI Quick Reference

## 🚀 Quick Start

```python
from crawl4ai import AsyncWebCrawler

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun("https://example.com")
    print(result.markdown.raw_markdown)
```

## 📦 Installation

```bash
# Basic
pip install crawl4ai
crawl4ai-setup

# With all features
pip install crawl4ai[all]

# Docker
docker pull unclecode/crawl4ai:latest
docker run -d -p 11235:11235 --shm-size=3g unclecode/crawl4ai:latest
```

## 🔧 Core Imports

```python
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode
)
from crawl4ai.extraction_strategy import (
    JsonCssExtractionStrategy,
    LLMExtractionStrategy,
    RegexExtractionStrategy
)
from crawl4ai.content_filter_strategy import (
    PruningContentFilter,
    BM25ContentFilter,
    LLMContentFilter
)
```

## ⚙️ Basic Configuration

```python
# Browser config
browser_config = BrowserConfig(
    headless=True,
    viewport_width=1920,
    viewport_height=1080,
    user_agent="Mozilla/5.0...",
    proxy="http://proxy:8080"
)

# Crawler config
run_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    css_selector="article",
    word_count_threshold=10,
    excluded_tags=['nav', 'footer'],
    page_timeout=60000
)
```

## 📊 CSS Extraction (No LLM)

```python
schema = {
    "name": "items",
    "baseSelector": ".item",
    "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {"name": "price", "selector": ".price", "type": "text"},
        {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
    ]
}

strategy = JsonCssExtractionStrategy(schema=schema)
result = await crawler.arun(url, config=CrawlerRunConfig(extraction_strategy=strategy))
data = json.loads(result.extracted_content)
```

## 🤖 LLM Extraction

```python
from pydantic import BaseModel

class Article(BaseModel):
    title: str
    author: str
    summary: str

strategy = LLMExtractionStrategy(
    provider="openai/gpt-4o-mini",
    api_token=os.getenv("OPENAI_API_KEY"),
    schema=Article.model_json_schema(),
    extraction_type="schema",
    instruction="Extract article metadata",
    chunk_token_threshold=4096
)

result = await crawler.arun(url, config=CrawlerRunConfig(extraction_strategy=strategy))
```

## 🎯 Content Filtering

```python
# Pruning filter
filter = PruningContentFilter(threshold=0.5, min_word_threshold=50)

# BM25 relevance filter
filter = BM25ContentFilter(
    user_query="machine learning",
    bm25_threshold=1.0
)

# LLM filter
filter = LLMContentFilter(
    provider="openai/gpt-4o-mini",
    api_token=os.getenv("OPENAI_API_KEY"),
    instruction="Extract main content, remove ads"
)

config = CrawlerRunConfig(content_filter=filter)
result = await crawler.arun(url, config=config)
print(result.markdown.fit_markdown)  # Filtered content
```

## 🔄 Multiple URLs

```python
urls = ["https://example.com/1", "https://example.com/2"]

# Streaming mode
async for result in await crawler.arun_many(urls, config=CrawlerRunConfig(stream=True)):
    print(f"{result.url}: {len(result.markdown.raw_markdown)} chars")

# Batch mode
results = await crawler.arun_many(urls, config=CrawlerRunConfig(stream=False))
```

## 🔐 Authentication

```python
# Session-based
session_id = "my_session"
result = await crawler.arun(
    "https://example.com/login",
    config=CrawlerRunConfig(
        session_id=session_id,
        js_code=["document.querySelector('#login-btn').click()"]
    )
)

# Use same session
result = await crawler.arun(
    "https://example.com/protected",
    config=CrawlerRunConfig(session_id=session_id)
)
```

## 📸 Screenshots & Media

```python
config = CrawlerRunConfig(
    screenshot=True,
    pdf=True,
    process_iframes=True
)

result = await crawler.arun(url, config=config)
# result.screenshot (base64)
# result.pdf (base64)
```

## 🌐 Dynamic Content

```python
config = CrawlerRunConfig(
    js_code=[
        "window.scrollTo(0, document.body.scrollHeight);",
        "await new Promise(r => setTimeout(r, 2000));"
    ],
    wait_for="css:.content-loaded",
    delay_before_return_html=2.0
)
```

## 🐳 Docker REST API

```bash
# Start
docker-compose up -d

# Health check
curl http://localhost:11235/health

# Basic crawl
curl -X POST http://localhost:11235/crawl \
  -H 'Content-Type: application/json' \
  -d '{"urls": ["https://example.com"]}'

# Streaming
curl -N -X POST http://localhost:11235/crawl/stream \
  -H 'Content-Type: application/json' \
  -d '{"urls": ["https://example.com"], "crawler_config": {"type": "CrawlerRunConfig", "params": {"stream": true}}}'
```

## 🔍 Result Object

```python
result = await crawler.arun(url)

# Content
result.markdown.raw_markdown        # Clean markdown
result.markdown.fit_markdown        # Filtered markdown
result.html                         # Raw HTML
result.cleaned_html                 # Cleaned HTML

# Metadata
result.success                      # Boolean
result.status_code                  # HTTP status
result.url                          # Final URL
result.error_message                # Error if failed

# Links & Media
result.links.internal               # Internal links
result.links.external               # External links
result.media.images                 # Images
result.media.videos                 # Videos

# Extracted data
result.extracted_content            # JSON string

# Debug
result.network_requests             # Captured requests
result.console_logs                 # Browser logs
```

## 💡 Common Patterns

### Pattern: News Scraper
```python
schema = {
    "name": "articles",
    "baseSelector": "article",
    "fields": [
        {"name": "title", "selector": "h1", "type": "text"},
        {"name": "author", "selector": ".author", "type": "text"},
        {"name": "date", "selector": "time", "type": "attribute", "attribute": "datetime"}
    ]
}
```

### Pattern: E-commerce Monitor
```python
config = CrawlerRunConfig(
    cache_mode=CacheMode.ENABLED,  # Compare with cached
    css_selector=".product-details",
    extraction_strategy=product_strategy
)
```

### Pattern: Multi-level Crawl
```python
from crawl4ai.async_crawler_strategy import DepthFirstCrawlerStrategy

strategy = DepthFirstCrawlerStrategy(
    max_depth=3,
    allowed_domains=["example.com"],
    include_patterns=[r'/blog/']
)
```

## ⚡ Performance Tips

```python
# 1. Use caching
cache_mode=CacheMode.ENABLED

# 2. Filter early
css_selector="article.main"

# 3. Parallel crawling
results = await crawler.arun_many(urls)

# 4. CSS over LLM (when possible)
# CSS = Free, Fast, Deterministic
# LLM = Costs money, slower, flexible

# 5. Chunk for parallel LLM
chunk_token_threshold=4096
```

## 🐛 Common Issues

```python
# Browser won't start
crawl4ai-setup
crawl4ai-doctor

# Docker memory
docker run --shm-size=3g ...

# Timeout
page_timeout=120000  # 2 minutes

# Authentication fails
# Use session management + hooks
```

## 📚 Cache Modes

```python
CacheMode.ENABLED      # Read and write cache
CacheMode.DISABLED     # No caching
CacheMode.BYPASS       # Skip cache, always fetch fresh
CacheMode.READ_ONLY    # Only read, never write
CacheMode.WRITE_ONLY   # Only write, never read
```

## 🔗 Links

- Docs: https://docs.crawl4ai.com/
- GitHub: https://github.com/unclecode/crawl4ai
- Discord: https://discord.gg/jP8KfhDhyN

## ⚙️ Environment Variables

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
MAX_CONCURRENT_TASKS=10
```

---

**Pro Tip**: Start with CSS extraction, add LLM only if needed!
