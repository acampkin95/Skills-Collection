#!/usr/bin/env python3
"""
Basic Crawl4AI Crawler Template.

Demonstrates basic web crawling using Crawl4AI with markdown output,
screenshot capture, and metadata extraction.
"""

import asyncio
import sys
from typing import Any

# Version check
MIN_CRAWL4AI_VERSION = "0.7.4"
try:
    from crawl4ai.__version__ import __version__
    from packaging import version
    if version.parse(__version__) < version.parse(MIN_CRAWL4AI_VERSION):
        print(f"⚠️  Warning: Crawl4AI {MIN_CRAWL4AI_VERSION}+ recommended (you have {__version__})")
except ImportError:
    print(f"ℹ️  Crawl4AI {MIN_CRAWL4AI_VERSION}+ required")

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from typing import Optional, Dict

async def crawl_basic(url: str) -> Any:
    """Crawl a URL and extract content as markdown with screenshots.

    Performs basic web crawling using Crawl4AI with headless browser automation.
    Extracts markdown content, metadata, links, media, and optionally captures
    a screenshot of the rendered page.

    Args:
        url: Target URL to crawl.

    Returns:
        Crawl result object containing success status, markdown content, metadata,
        links, media, and screenshot data. Returns result even if crawl fails.

    Raises:
        OSError: If file writing fails when saving output files.
    """
    import base64

    # Configure browser
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080
    )

    # Configure crawler
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        remove_overlay_elements=True,
        wait_for_images=True,
        screenshot=True
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=crawler_config
        )

        if result.success:
            print(f"✅ Crawled: {result.url}")
            print(f"   Title: {result.metadata.get('title', 'N/A')}")
            print(f"   Links found: {len(result.links.get('internal', []))} internal, {len(result.links.get('external', []))} external")
            print(f"   Media found: {len(result.media.get('images', []))} images, {len(result.media.get('videos', []))} videos")
            print(f"   Content length: {len(result.markdown)} chars")

            # Save markdown
            try:
                with open("output.md", "w") as f:
                    f.write(result.markdown)
                print("📄 Saved to output.md")
            except (OSError, IOError) as e:
                print(f"Error saving markdown: {e}")

            # Save screenshot if available
            if result.screenshot:
                try:
                    # Check if screenshot is base64 string or bytes
                    if isinstance(result.screenshot, str):
                        screenshot_data = base64.b64decode(result.screenshot)
                    else:
                        screenshot_data = result.screenshot
                    with open("screenshot.png", "wb") as f:
                        f.write(screenshot_data)
                    print("📸 Saved screenshot.png")
                except (OSError, IOError) as e:
                    print(f"Error saving screenshot: {e}")
        else:
            print(f"❌ Failed: {result.error_message}")

        return result

def main() -> None:
    """CLI entry point for basic web crawler.

    Validates command-line arguments and executes asynchronous crawl operation.
    Requires a URL argument and optionally outputs markdown and screenshot files.
    Extracts and saves page content as markdown (output.md) and renders a screenshot
    (screenshot.png) for visual verification.

    Command-line Arguments:
        url: Target URL to crawl (required).

    Output Files:
        output.md: Extracted markdown content from the crawled page.
        screenshot.png: PNG screenshot of the rendered page (if available).

    Exit Codes:
        0: Success (crawl completed, may have errors in output).
        1: Error (invalid arguments provided).

    Raises:
        SystemExit: With code 0 or 1 depending on argument validation.
    """
    if len(sys.argv) < 2:
        print("Usage: python basic_crawler.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    asyncio.run(crawl_basic(url))


if __name__ == "__main__":
    main()