#!/usr/bin/env python3
"""
Basic Web Crawling Example
===========================

This example demonstrates basic web crawling with Crawl4AI including:
- Simple URL crawling
- Markdown generation
- Error handling
- Basic configuration
"""

import asyncio
import sys
from typing import Optional, List, Any
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


async def basic_crawl(url: str) -> Optional[Any]:
    """Perform a basic crawl of a single URL"""
    
    print(f"Crawling: {url}")
    print("-" * 80)
    
    # Configure browser
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
    )
    
    # Configure crawler run
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Always fetch fresh content
        word_count_threshold=10,      # Minimum words per block
    )
    
    # Create crawler and execute
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
        
        if not result.success:
            print(f"❌ Crawl failed: {result.error_message}")
            return None
        
        # Display results
        print(f"✓ Success!")
        print(f"  Status Code: {result.status_code}")
        print(f"  Final URL: {result.url}")
        print(f"  Markdown length: {len(result.markdown.raw_markdown)} chars")
        print(f"  Internal links: {len(result.links.internal)}")
        print(f"  External links: {len(result.links.external)}")
        print(f"  Images: {len(result.media.images)}")
        print()
        
        # Show first 500 characters of markdown
        print("Markdown preview:")
        print("-" * 80)
        print(result.markdown.raw_markdown[:500])
        print("...")
        print("-" * 80)
        
        return result


async def crawl_with_css_selector(url: str, selector: str) -> None:
    """Crawl only specific parts of a page using CSS selector.

    Extracts and displays content matching a specific CSS selector from the target URL.

    Args:
        url: Target URL to crawl.
        selector: CSS selector string to extract matching elements.

    Returns:
        None. Output is printed to stdout.

    Raises:
        No exceptions raised; errors are caught and printed.
    """

    print(f"\nCrawling {url} with selector: {selector}")
    print("-" * 80)
    
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        css_selector=selector,  # Only extract this part
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        
        if result.success:
            print(f"✓ Extracted content length: {len(result.markdown.raw_markdown)} chars")
            print(result.markdown.raw_markdown[:300])
        else:
            print(f"❌ Failed: {result.error_message}")


async def crawl_multiple_urls(urls: List[str]) -> None:
    """Crawl multiple URLs in parallel.

    Processes multiple URLs concurrently using arun_many with streaming results.

    Args:
        urls: List of URLs to crawl in parallel.

    Returns:
        None. Results are printed to stdout as they arrive.

    Raises:
        No exceptions raised; errors are caught and printed.
    """

    print(f"\nCrawling {len(urls)} URLs...")
    print("-" * 80)
    
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=True,  # Process results as they arrive
    )
    
    async with AsyncWebCrawler() as crawler:
        # Stream results
        async for result in await crawler.arun_many(urls, config=config):
            if result.success:
                print(f"✓ {result.url}: {len(result.markdown.raw_markdown)} chars")
            else:
                print(f"✗ {result.url}: {result.error_message}")


async def crawl_with_screenshot(url: str, output_path: str = "screenshot.png") -> None:
    """Crawl a page and take a screenshot.

    Crawls the URL and captures a screenshot, saving it as a PNG file.

    Args:
        url: Target URL to crawl and screenshot.
        output_path: File path to save the screenshot (default: "screenshot.png").

    Returns:
        None. Screenshot is saved to the specified output_path.

    Raises:
        OSError: If screenshot file write fails.
        IOError: If file I/O operation fails.
    """

    print(f"\nCrawling and capturing screenshot: {url}")
    print("-" * 80)
    
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        screenshot=True,
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        
        if result.success and result.screenshot:
            # Save screenshot (base64 decoded)
            import base64
            screenshot_data = base64.b64decode(result.screenshot)
            with open(output_path, 'wb') as f:
                f.write(screenshot_data)
            print(f"✓ Screenshot saved to {output_path}")
        else:
            print("❌ Failed to capture screenshot")


def main() -> None:
    """Main entry point for basic crawling examples.

    Demonstrates four essential Crawl4AI features:
    1. Basic URL crawling with metadata extraction
    2. CSS selector-based content extraction
    3. Parallel multi-URL crawling with streaming
    4. Screenshot capture during crawling

    Returns:
        None. Output is printed to stdout.

    Raises:
        No exceptions raised; errors are caught and printed by individual functions.
    """
    # Example URLs
    urls = [
        "https://docs.crawl4ai.com/",
        "https://example.com",
    ]
    
    if len(sys.argv) > 1:
        # Use URL from command line
        url = sys.argv[1]
        asyncio.run(basic_crawl(url))
    else:
        # Run all examples
        print("=" * 80)
        print("Crawl4AI Basic Examples")
        print("=" * 80)
        
        # Example 1: Basic crawl
        asyncio.run(basic_crawl("https://example.com"))
        
        # Example 2: CSS selector
        asyncio.run(crawl_with_css_selector(
            "https://docs.crawl4ai.com/",
            "article"
        ))
        
        # Example 3: Multiple URLs
        asyncio.run(crawl_multiple_urls(urls))
        
        # Example 4: Screenshot
        asyncio.run(crawl_with_screenshot("https://example.com"))
        
        print("\n" + "=" * 80)
        print("Examples complete!")
        print("=" * 80)


if __name__ == "__main__":
    main()
