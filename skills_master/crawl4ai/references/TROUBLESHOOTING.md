# Troubleshooting Guide

Production-tested solutions for common issues, performance problems, and deployment challenges.

## Quick Diagnostics

```bash
# Run comprehensive health check
python scripts/validate_setup.py

# Check Docker services
docker ps
docker logs crawl4ai-1

# Test API connectivity
curl http://localhost:11235/health

# Verify browser installation
python -c "from crawl4ai import AsyncWebCrawler; import asyncio; asyncio.run(AsyncWebCrawler().start())"
```

## Common Issues

### Installation Problems

#### Issue: Browser Installation Fails

**Symptoms:**
```
Error: Failed to download browser
playwright install failed
```

**Solutions:**
```bash
# Method 1: Manual installation
playwright install chromium

# Method 2: Use Docker (bypasses local browser issues)
cd docker && ./setup.sh

# Method 3: Clear cache and retry
rm -rf ~/.cache/ms-playwright
pip install --upgrade crawl4ai
crawl4ai-setup

# Method 4: Install system dependencies (Linux)
apt-get install -y \
    libnss3 libnspr4 libdbus-1-3 \
    libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2
```

#### Issue: Import Error - Module Not Found

**Symptoms:**
```python
ModuleNotFoundError: No module named 'crawl4ai'
```

**Solutions:**
```bash
# Verify installation
pip list | grep crawl4ai

# Reinstall
pip uninstall crawl4ai
pip install crawl4ai --upgrade

# Check Python version (requires 3.10+)
python --version

# Install with all dependencies
pip install "crawl4ai[all]"
```

### Runtime Errors

#### Issue: Memory Exhaustion

**Symptoms:**
```
MemoryError: Unable to allocate array
Killed (OOM)
```

**Solutions:**

1. **Increase Docker shared memory:**
```yaml
# docker-compose.yml
services:
  crawl4ai:
    shm_size: '4gb'  # Increase from 2gb
```

2. **Limit concurrent crawls:**
```python
# Reduce parallelism
config = CrawlerRunConfig()
results = await crawler.arun_many(
    urls[:5],  # Process in smaller batches
    config=config
)
```

3. **Enable aggressive caching:**
```python
config = CrawlerRunConfig(
    cache_mode=CacheMode.ENABLED,
    excluded_tags=['img', 'video', 'iframe']  # Skip heavy content
)
```

4. **Monitor memory usage:**
```python
import psutil
print(f"Memory: {psutil.virtual_memory().percent}%")
```

#### Issue: Timeout Errors

**Symptoms:**
```
TimeoutError: Page load timed out
asyncio.TimeoutError: 30000ms exceeded
```

**Solutions:**

1. **Increase timeout:**
```python
config = CrawlerRunConfig(
    page_timeout=60000,  # 60 seconds
    navigation_timeout=45000
)
```

2. **Wait for specific elements:**
```python
config = CrawlerRunConfig(
    wait_for="css:.content-loaded",
    page_timeout=30000
)
```

3. **Check network connectivity:**
```bash
# Test URL accessibility
curl -I https://target-site.com

# Check DNS resolution
nslookup target-site.com
```

4. **Use retry logic:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def reliable_crawl(url):
    async with AsyncWebCrawler() as crawler:
        return await crawler.arun(url)
```

#### Issue: Empty or Incorrect Extraction

**Symptoms:**
```json
{"extracted_content": "[]"}
{"items": []}
```

**Solutions:**

1. **Verify CSS selectors:**
```python
# Debug selector
result = await crawler.arun(url, config=CrawlerRunConfig(
    js_code=["console.log(document.querySelectorAll('.your-selector').length)"]
))
print(result.console_logs)
```

2. **Check page rendering:**
```python
# Take screenshot to debug
config = CrawlerRunConfig(screenshot=True)
result = await crawler.arun(url, config=config)
# Screenshot saved in result.screenshot
```

3. **Wait for dynamic content:**
```python
config = CrawlerRunConfig(
    wait_for="() => document.querySelector('.content') !== null",
    js_code=["window.scrollTo(0, document.body.scrollHeight)"]
)
```

4. **Validate schema:**
```python
# Test schema with simple extraction
schema = {
    "name": "test",
    "baseSelector": "body",  # Start broad
    "fields": [
        {"name": "all_text", "selector": "p", "type": "text"}
    ]
}
# Gradually refine selectors
```

### Performance Issues

#### Issue: Slow Crawling Speed

**Symptoms:**
- Pages taking >10 seconds each
- Low throughput (<50 pages/min)

**Solutions:**

1. **Enable caching:**
```python
config = CrawlerRunConfig(cache_mode=CacheMode.ENABLED)
```

2. **Increase parallelism:**
```python
# Use arun_many for batch processing
results = await crawler.arun_many(
    urls,
    config=config
)
```

3. **Optimize extraction strategy:**
```python
# Use CSS instead of LLM
strategy = JsonCssExtractionStrategy(schema)  # Fast
# vs
strategy = LLMExtractionStrategy(...)  # Slow, expensive
```

4. **Filter content early:**
```python
config = CrawlerRunConfig(
    excluded_tags=['script', 'style', 'nav', 'footer'],
    css_selector=".main-content"  # Target specific area
)
```

5. **Connection pooling:**
```python
# Reuse crawler instance
async with AsyncWebCrawler() as crawler:
    for url in urls:
        result = await crawler.arun(url)  # Reuses connection
```

#### Issue: High LLM Costs

**Symptoms:**
- API costs exceeding budget
- Unexpected charges

**Solutions:**

1. **Pre-filter with BM25:**
```python
from crawl4ai.content_filter_strategy import BM25ContentFilter

filter_strategy = BM25ContentFilter(
    user_query="relevant keywords",
    bm25_threshold=1.5  # Higher = more aggressive filtering
)

config = CrawlerRunConfig(content_filter=filter_strategy)
```

2. **Use cheaper models:**
```python
# GPT-4o-mini vs GPT-4 (95% cost reduction)
strategy = LLMExtractionStrategy(
    provider="openai/gpt-4o-mini",  # Cheaper
    # vs provider="openai/gpt-4"
)
```

3. **Chunk wisely:**
```python
strategy = LLMExtractionStrategy(
    chunk_token_threshold=2048,  # Smaller chunks
    # Enables parallel processing
)
```

4. **Implement budget limits:**
```python
class BudgetEnforcer:
    def __init__(self, daily_limit=10.0):
        self.daily_limit = daily_limit
        self.spent = 0.0
    
    def can_spend(self, amount):
        return self.spent + amount <= self.daily_limit
    
    def record(self, amount):
        self.spent += amount

budget = BudgetEnforcer(daily_limit=10.0)

# Before extraction
if not budget.can_spend(estimated_cost):
    raise Exception("Budget limit reached")
```

5. **Monitor usage:**
```python
# Track token usage
if result.extraction_metadata:
    tokens = result.extraction_metadata.get('total_tokens', 0)
    cost = result.extraction_metadata.get('cost', 0)
    print(f"Used {tokens} tokens, cost: ${cost:.4f}")
```

### Docker Issues

#### Issue: Container Crashes

**Symptoms:**
```
Container exited with code 137 (OOM)
Container exited with code 1
```

**Solutions:**

1. **Increase memory limits:**
```yaml
# docker-compose.yml
services:
  crawl4ai:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
    shm_size: '3gb'
```

2. **Check logs:**
```bash
docker logs crawl4ai-1 --tail 100
docker logs --follow crawl4ai-1
```

3. **Inspect resource usage:**
```bash
docker stats crawl4ai-1
```

4. **Restart with clean state:**
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d
```

#### Issue: Port Already in Use

**Symptoms:**
```
Error: port 11235 is already allocated
```

**Solutions:**

1. **Find and kill process:**
```bash
# Linux/Mac
lsof -i :11235
kill -9 <PID>

# Windows
netstat -ano | findstr :11235
taskkill /PID <PID> /F
```

2. **Change port:**
```yaml
# docker-compose.yml
ports:
  - "11236:11235"  # Map to different external port
```

3. **Stop conflicting containers:**
```bash
docker ps
docker stop <container-id>
```

### API Issues

#### Issue: 429 Rate Limit Errors

**Symptoms:**
```
Error 429: Too Many Requests
RateLimitError: Rate limit exceeded
```

**Solutions:**

1. **Implement rate limiting:**
```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.rate = requests_per_minute / 60
        self.tokens = requests_per_minute
        self.last_update = datetime.now()
    
    async def acquire(self):
        now = datetime.now()
        elapsed = (now - self.last_update).total_seconds()
        self.tokens = min(60, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return
        
        wait_time = (1 - self.tokens) / self.rate
        await asyncio.sleep(wait_time)
        self.tokens = 0

limiter = RateLimiter(requests_per_minute=50)

async def rate_limited_crawl(url):
    await limiter.acquire()
    result = await crawler.arun(url)
    return result
```

2. **Use API key rotation:**
```python
api_keys = [
    os.getenv("OPENAI_API_KEY_1"),
    os.getenv("OPENAI_API_KEY_2"),
    os.getenv("OPENAI_API_KEY_3")
]
current_key_index = 0

def get_next_key():
    global current_key_index
    key = api_keys[current_key_index]
    current_key_index = (current_key_index + 1) % len(api_keys)
    return key
```

3. **Add exponential backoff:**
```python
import time

def exponential_backoff(attempt):
    return min(60, 2 ** attempt)

for attempt in range(5):
    try:
        result = await crawler.arun(url)
        break
    except RateLimitError:
        wait = exponential_backoff(attempt)
        print(f"Rate limited, waiting {wait}s...")
        await asyncio.sleep(wait)
```

### Authentication Issues

#### Issue: Login/Session Handling Fails

**Symptoms:**
- Returns login page instead of content
- Session expires during crawl

**Solutions:**

1. **Use session management:**
```python
config = CrawlerRunConfig(
    session_id="my_session",
    cache_mode=CacheMode.ENABLED
)

# First request - login
result1 = await crawler.arun(login_url, config=config)

# Subsequent requests - maintain session
result2 = await crawler.arun(protected_url, config=config)
```

2. **Implement login hook:**
```python
async def login_hook(page):
    await page.fill('input[name="username"]', 'user')
    await page.fill('input[name="password"]', 'pass')
    await page.click('button[type="submit"]')
    await page.wait_for_selector('.dashboard')

config = CrawlerRunConfig(
    hooks={'before_goto': [login_hook]}
)
```

3. **Pass cookies:**
```python
cookies = [
    {
        'name': 'session_id',
        'value': 'abc123',
        'domain': '.example.com',
        'path': '/'
    }
]

# Set cookies before crawl
# (Implementation depends on Crawl4AI version)
```

## Debugging Tools

### Enable Verbose Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now you'll see detailed logs
result = await crawler.arun(url)
```

### Network Request Inspection

```python
config = CrawlerRunConfig(
    verbose=True,  # Enable request logging
)

result = await crawler.arun(url, config=config)

# Check network requests
if hasattr(result, 'network_requests'):
    for req in result.network_requests:
        print(f"{req.method} {req.url} - {req.status}")
```

### Browser DevTools

```python
# Launch browser in headful mode for debugging
from crawl4ai import BrowserConfig

browser_config = BrowserConfig(
    headless=False,  # Show browser
    devtools=True    # Open DevTools
)

crawler = AsyncWebCrawler(config=browser_config)
```

## Performance Profiling

```python
import cProfile
import pstats

async def profile_crawl():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
    return result

# Profile execution
profiler = cProfile.Profile()
profiler.enable()

asyncio.run(profile_crawl())

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest functions
```

## Health Check Script

```python
#!/usr/bin/env python3
"""Quick health check for Crawl4AI deployment"""

import asyncio
import sys

async def health_check():
    checks = []
    
    # 1. Import test
    try:
        from crawl4ai import AsyncWebCrawler
        checks.append(("Import crawl4ai", True, None))
    except Exception as e:
        checks.append(("Import crawl4ai", False, str(e)))
        return checks
    
    # 2. Crawler initialization
    try:
        crawler = AsyncWebCrawler()
        await crawler.start()
        checks.append(("Initialize crawler", True, None))
    except Exception as e:
        checks.append(("Initialize crawler", False, str(e)))
        return checks
    
    # 3. Basic crawl
    try:
        result = await crawler.arun("https://example.com")
        success = result.success and len(result.markdown.raw_markdown) > 0
        checks.append(("Basic crawl", success, None if success else "Empty result"))
    except Exception as e:
        checks.append(("Basic crawl", False, str(e)))
    
    # 4. Cleanup
    try:
        await crawler.close()
        checks.append(("Cleanup", True, None))
    except Exception as e:
        checks.append(("Cleanup", False, str(e)))
    
    return checks

async def main():
    print("Running health checks...\n")
    
    checks = await health_check()
    
    all_passed = True
    for name, passed, error in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {name}")
        if error:
            print(f"  Error: {error}")
        all_passed = all_passed and passed
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ All checks passed")
        return 0
    else:
        print("✗ Some checks failed")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

## Getting Help

1. **Check documentation:** Review SKILL.md, QUICKREF.md
2. **Search issues:** https://github.com/unclecode/crawl4ai/issues
3. **Enable debug logging:** Set logging level to DEBUG
4. **Test in isolation:** Create minimal reproduction case
5. **Join Discord:** https://discord.gg/jP8KfhDhyN
6. **Report bug:** Include Python version, OS, error logs, minimal code sample

## Prevention Best Practices

1. **Monitor proactively** - Set up alerts before issues occur
2. **Test changes** - Always test in staging first
3. **Version pin** - Lock dependency versions in production
4. **Resource limits** - Set memory/CPU limits to prevent runaway processes
5. **Graceful degradation** - Implement fallbacks for non-critical features
6. **Circuit breakers** - Prevent cascade failures
7. **Health checks** - Regular automated health monitoring
8. **Logging** - Comprehensive logging for post-mortem analysis
9. **Backup strategies** - Cache crawl results for replay
10. **Documentation** - Keep runbooks updated with incident learnings
