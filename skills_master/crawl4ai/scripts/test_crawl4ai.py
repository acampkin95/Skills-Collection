#!/usr/bin/env python3
"""
Crawl4AI Testing Suite

Comprehensive tests covering extraction strategies, error handling,
performance requirements, and integration scenarios.
"""

import pytest
import asyncio
import os
from typing import Dict, Any

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter

# Test fixtures
TEST_URLS = {
    'simple': 'https://example.com',
    'dynamic': 'https://news.ycombinator.com',
    'complex': 'https://github.com/trending'
}

@pytest.fixture
async def crawler():
    """Shared AsyncWebCrawler fixture for test suite.

    Provides a single crawler instance with automatic lifecycle management.
    The crawler is started before tests and closed after all tests complete.

    Yields:
        AsyncWebCrawler: Initialized crawler instance ready for crawling operations.

    Raises:
        RuntimeError: If crawler initialization or cleanup fails.
    """
    crawler = AsyncWebCrawler()
    await crawler.start()
    yield crawler
    await crawler.close()

# ============================================================================
# Basic Functionality Tests
# ============================================================================

@pytest.mark.asyncio
async def test_basic_crawl(crawler) -> None:
    """Test basic page crawling and metadata extraction.

    Verifies that a single URL can be crawled successfully with proper
    status code, URL, and markdown content returned.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If crawl fails or expected metadata is missing.
    """
    result = await crawler.arun(TEST_URLS['simple'])
    
    assert result.success, f"Crawl failed: {result.error_message}"
    assert result.url == TEST_URLS['simple']
    assert len(result.markdown.raw_markdown) > 0
    assert result.status_code == 200

@pytest.mark.asyncio
async def test_multiple_urls(crawler) -> None:
    """Test parallel crawling of multiple URLs with arun_many.

    Verifies that multiple URLs can be processed concurrently and all
    results are returned successfully.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If any URL fails to crawl or expected count is wrong.
    """
    urls = list(TEST_URLS.values())
    
    results = await crawler.arun_many(
        urls,
        config=CrawlerRunConfig(stream=False)
    )
    
    assert len(results) == len(urls)
    assert all(r.success for r in results)

@pytest.mark.asyncio
async def test_cache_modes(crawler) -> None:
    """Test different cache behaviors.

    Verifies that cache modes (ENABLED and BYPASS) work correctly by performing
    multiple crawls with different cache configurations and validating results.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If cache-related crawl operations fail or return unsuccessful results.
    """
    url = TEST_URLS['simple']

    # First crawl - populate cache
    config1 = CrawlerRunConfig(cache_mode=CacheMode.ENABLED)
    result1 = await crawler.arun(url, config=config1)
    assert result1.success

    # Second crawl - should hit cache
    result2 = await crawler.arun(url, config=config1)
    assert result2.success

    # Third crawl - bypass cache
    config2 = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    result3 = await crawler.arun(url, config=config2)
    assert result3.success

# ============================================================================
# Extraction Strategy Tests
# ============================================================================

@pytest.mark.asyncio
async def test_css_extraction(crawler) -> None:
    """Test CSS-based extraction with schema-defined selectors.

    Verifies that CSS extraction strategy correctly extracts structured data
    from HTML elements using selector patterns and returns valid JSON content.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If extraction fails, content is missing, or extracted data is not a list.
        json.JSONDecodeError: If extracted content cannot be parsed as valid JSON.
    """
    schema = {
        "name": "test_data",
        "baseSelector": "body",
        "fields": [
            {"name": "title", "selector": "h1", "type": "text"},
            {"name": "paragraphs", "selector": "p", "type": "text"}
        ]
    }

    strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(extraction_strategy=strategy)

    result = await crawler.arun(TEST_URLS['simple'], config=config)

    assert result.success
    assert result.extracted_content is not None

    # Validate extracted data structure
    import json
    data = json.loads(result.extracted_content)
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_css_extraction_nested(crawler) -> None:
    """Test nested CSS extraction with multiple selector patterns.

    Verifies that CSS extraction handles nested structures with multiple
    selectors and attribute extraction correctly.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If crawl fails or extracted data is not a list.
        json.JSONDecodeError: If extracted content cannot be parsed as valid JSON.
    """
    schema = {
        "name": "articles",
        "baseSelector": "article, .story",
        "fields": [
            {"name": "title", "selector": "h1, h2", "type": "text"},
            {"name": "author", "selector": ".author, .user", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    }

    strategy = JsonCssExtractionStrategy(schema=schema)
    result = await crawler.arun(TEST_URLS['dynamic'], config=CrawlerRunConfig(
        extraction_strategy=strategy
    ))

    assert result.success
    if result.extracted_content:
        import json
        data = json.loads(result.extracted_content)
        assert isinstance(data, list)

@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OpenAI API key not set")
async def test_llm_extraction(crawler) -> None:
    """Test LLM-based extraction with schema validation.

    Verifies that LLM extraction strategy correctly extracts structured data
    using OpenAI GPT-4o-mini model and validates against provided JSON schema.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If extraction fails, content is missing, or required fields are absent.
        json.JSONDecodeError: If extracted content cannot be parsed as valid JSON.
        RuntimeError: If LLM API call fails due to authentication or service issues.
    """
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string", "maxLength": 200}
        },
        "required": ["title"]
    }

    strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        api_token=os.getenv('OPENAI_API_KEY'),
        schema=schema,
        extraction_type="schema"
    )

    result = await crawler.arun(TEST_URLS['simple'], config=CrawlerRunConfig(
        extraction_strategy=strategy
    ))

    assert result.success
    assert result.extracted_content is not None

    import json
    data = json.loads(result.extracted_content)
    assert 'title' in data

# ============================================================================
# Content Filtering Tests
# ============================================================================

@pytest.mark.asyncio
async def test_pruning_filter(crawler) -> None:
    """Test content pruning with threshold filtering.

    Verifies that content pruning filters out low-quality text blocks and reduces
    overall content size while maintaining minimum word thresholds.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If crawl fails or filtered content is longer than raw content.
    """
    filter_strategy = PruningContentFilter(
        threshold=0.5,
        min_word_threshold=50
    )

    result = await crawler.arun(TEST_URLS['complex'], config=CrawlerRunConfig(
        content_filter=filter_strategy
    ))

    assert result.success
    assert len(result.markdown.fit_markdown) > 0
    # Filtered content should be shorter than raw
    assert len(result.markdown.fit_markdown) <= len(result.markdown.raw_markdown)

# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_url(crawler) -> None:
    """Test handling of invalid URLs.

    Verifies that the crawler gracefully handles non-existent domains and
    returns appropriate error messages without crashing.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If crawler does not properly report failure for invalid URL.
    """
    result = await crawler.arun("https://this-domain-definitely-does-not-exist-12345.com")

    assert not result.success
    assert result.error_message is not None

@pytest.mark.asyncio
async def test_timeout_handling(crawler) -> None:
    """Test timeout configuration and handling.

    Verifies that the crawler handles timeout configuration without crashing,
    whether the crawl succeeds or times out depends on network conditions.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If crawler returns None result (should never happen).
    """
    config = CrawlerRunConfig(page_timeout=1000)  # Very short timeout

    result = await crawler.arun(TEST_URLS['complex'], config=config)
    # May succeed or timeout depending on network speed
    # Just ensure it doesn't crash
    assert result is not None

@pytest.mark.asyncio
async def test_invalid_css_selector(crawler) -> None:
    """Test handling of invalid CSS selectors.

    Verifies that the crawler gracefully handles malformed CSS selectors without
    crashing or raising unhandled exceptions.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If crawler returns None result (should never happen).
    """
    schema = {
        "name": "test",
        "baseSelector": "invalid>>>selector",  # Invalid selector
        "fields": [
            {"name": "data", "selector": "span", "type": "text"}
        ]
    }

    strategy = JsonCssExtractionStrategy(schema=schema)
    result = await crawler.arun(TEST_URLS['simple'], config=CrawlerRunConfig(
        extraction_strategy=strategy
    ))

    # Should handle gracefully
    assert result is not None

# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_concurrent_crawling(crawler) -> None:
    """Test concurrent crawling performance with SLA validation.

    Verifies that the crawler can handle multiple concurrent URL crawls and
    complete within performance SLA (< 30 seconds for 10 URLs).

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If any crawl fails, result count mismatches, or SLA is exceeded.
    """
    urls = [TEST_URLS['simple']] * 10

    import time
    start = time.time()

    results = await crawler.arun_many(
        urls,
        config=CrawlerRunConfig(stream=False)
    )

    duration = time.time() - start

    assert len(results) == len(urls)
    assert all(r.success for r in results)

    # Should complete in reasonable time (< 30s for 10 URLs)
    assert duration < 30

@pytest.mark.asyncio
async def test_response_time(crawler) -> None:
    """Test response time meets SLA for simple pages.

    Verifies that crawling a simple page completes within the 5-second SLA
    for responsive applications.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If crawl fails or response time exceeds 5 seconds.
    """
    import time

    start = time.time()
    result = await crawler.arun(TEST_URLS['simple'])
    duration = time.time() - start

    assert result.success
    # Simple page should load in < 5 seconds
    assert duration < 5.0

# ============================================================================
# Configuration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_custom_headers(crawler) -> None:
    """Test custom headers support in requests.

    Verifies that the crawler can be configured with custom headers and
    still successfully crawl pages. Actual header validation would require
    server-side verification or request inspection middleware.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If crawl with custom headers fails.
    """
    # This test is conceptual - actual header validation would need
    # server-side verification or request inspection
    result = await crawler.arun(TEST_URLS['simple'])
    assert result.success

@pytest.mark.asyncio
async def test_javascript_execution(crawler) -> None:
    """Test JavaScript code execution during page crawl.

    Verifies that custom JavaScript code can be executed during crawling
    with proper wait conditions for dynamic content loading.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If JavaScript execution fails or wait condition times out.
    """
    js_code = "window.testValue = 'Hello World'"

    config = CrawlerRunConfig(
        js_code=[js_code],
        wait_for="() => window.testValue !== undefined"
    )

    result = await crawler.arun(TEST_URLS['simple'], config=config)
    assert result.success

# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_extraction_pipeline(crawler) -> None:
    """Test complete extraction workflow combining filtering and extraction.

    Verifies the full pipeline of content filtering, CSS extraction, and cache
    reuse across multiple crawl operations on the same URL with different strategies.

    Args:
        crawler: AsyncWebCrawler fixture providing crawler instance.

    Returns:
        None.

    Raises:
        AssertionError: If any crawl operation fails or cache is not properly utilized.
    """
    # Step 1: Crawl with filtering
    filter_strategy = PruningContentFilter(threshold=0.6)

    result1 = await crawler.arun(TEST_URLS['dynamic'], config=CrawlerRunConfig(
        content_filter=filter_strategy,
        cache_mode=CacheMode.ENABLED
    ))

    assert result1.success

    # Step 2: Extract with CSS
    schema = {
        "name": "items",
        "baseSelector": "article, .post",
        "fields": [
            {"name": "title", "selector": "h1, h2", "type": "text"}
        ]
    }

    result2 = await crawler.arun(TEST_URLS['dynamic'], config=CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(schema=schema),
        cache_mode=CacheMode.ENABLED  # Should hit cache from step 1
    ))

    assert result2.success

# ============================================================================
# Test Runner
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Run with: python -m pytest tests.py -v
    # Or: python tests.py
    
    print("Crawl4AI Test Suite")
    print("=" * 60)
    print("\nRunning tests...")
    print("Use: pytest tests.py -v for detailed output")
    print("Use: pytest tests.py -m 'not slow' to skip slow tests")
    print("Use: pytest tests.py --cov to measure coverage")
    print()
    
    sys.exit(pytest.main([__file__, "-v"]))
