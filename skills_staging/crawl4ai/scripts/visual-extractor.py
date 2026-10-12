#!/usr/bin/env python3
"""
Visual Extractor - Extract visual elements and screenshots from web pages.

This script provides comprehensive visual extraction capabilities including:
- Page screenshots with full-page capture
- Element-specific screenshots via CSS selectors
- Visual element analysis (images, videos, icons)
- DOM structure visualization
- Visual diff comparison

Usage:
    python visual-extractor.py <url> [--full-page] [--selector <css>] [--output <dir>]
    python visual-extractor.py --batch urls.txt [--output <dir>]
"""

import argparse
import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from urllib.parse import urlparse

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
except ImportError:
    print("Error: crawl4ai not installed. Run: pip install crawl4ai")
    sys.exit(1)


class VisualExtractor:
    """Extract visual elements and screenshots from web pages."""

    def __init__(self, output_dir: str = "./visual_output") -> None:
        """Initialize visual extractor with output directory.

        Creates output directory if it doesn't exist and initializes session data storage
        for tracking extraction operations and results across multiple invocations.

        Args:
            output_dir: Directory path for saving screenshots and analysis results
                       (default: "./visual_output").

        Returns:
            None.

        Raises:
            OSError: Raised if output directory cannot be created.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_data: Dict[str, Any] = {}

    async def extract_full_screenshot(self, url: str, delay: int = 2) -> Dict[str, Any]:
        """Capture full-page screenshot of a URL with network idle detection.

        Takes a screenshot of the entire webpage after waiting for network idle state,
        ensuring all assets and lazy-loaded content have finished loading. Saves the
        screenshot as PNG file with timestamp in the output directory.

        Args:
            url: Target URL to capture screenshot from.
            delay: Additional delay in seconds to wait after network idle (default: 2).

        Returns:
            Dict[str, Any]: Dictionary with keys:
                - success (bool): True if screenshot was captured and saved.
                - url (str): The target URL that was processed.
                - screenshot_path (str, optional): Full path to saved PNG file.
                - filename (str, optional): Generated filename with timestamp.
                - timestamp (str, optional): ISO format timestamp of capture.
                - error (str, optional): Error message if capture failed.

        Raises:
            OSError: Raised if screenshot file cannot be written to output directory.
        """
        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1920,
            viewport_height=1080,
        )

        crawler_config = CrawlerRunConfig(
            screenshot=True,
            page_timeout=60000,
            wait_for="networkidle",
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success and result.screenshot:
                # Decode and save screenshot
                screenshot_data = base64.b64decode(result.screenshot)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                filepath = self.output_dir / filename

                with open(filepath, "wb") as f:
                    f.write(screenshot_data)

                return {
                    "success": True,
                    "url": url,
                    "screenshot_path": str(filepath),
                    "filename": filename,
                    "timestamp": timestamp,
                }

            return {
                "success": False,
                "url": url,
                "error": result.error_message if hasattr(result, 'error_message') else "Unknown error"
            }

    async def extract_element_screenshot(
        self, url: str, selector: str, delay: int = 1
    ) -> Dict[str, Any]:
        """Capture screenshot of a specific element via CSS selector.

        Targets a specific DOM element using CSS selector, scrolls it into view, and captures
        a screenshot. Useful for extracting individual components like product cards, headers,
        or form sections from a page.

        Args:
            url: Target URL containing the element to screenshot.
            selector: CSS selector to identify the target element (e.g., '.product-card', '#header').
            delay: Additional delay in milliseconds after scrolling element into view (default: 1).

        Returns:
            Dict[str, Any]: Dictionary with keys:
                - success (bool): True if element was found and screenshot captured.
                - url (str): The target URL that was processed.
                - selector (str): The CSS selector used for targeting.
                - screenshot_path (str, optional): Full path to saved PNG file.
                - filename (str, optional): Generated filename with selector and timestamp.
                - error (str, optional): Error message if element not found or capture failed.

        Raises:
            OSError: Raised if screenshot file cannot be written to output directory.
        """
        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1920,
            viewport_height=1080,
        )

        # JavaScript to capture element screenshot
        js_code = f"""
        async () => {{
            const element = document.querySelector('{selector}');
            if (!element) return null;

            // Scroll element into view
            element.scrollIntoView({{ behavior: 'instant', block: 'center' }});
            await new Promise(r => setTimeout(r, 500));

            // Get element bounds
            const rect = element.getBoundingClientRect();
            return {{
                selector: '{selector}',
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                top: rect.top,
                left: rect.left
            }};
        }}
        """

        crawler_config = CrawlerRunConfig(
            js_code=js_code,
            page_timeout=60000,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"element_{selector.replace(' ', '_').replace('.', '_').replace('#', '_')}_{timestamp}.png"

                # Full page screenshot for element extraction
                if result.screenshot:
                    screenshot_data = base64.b64decode(result.screenshot)
                    filepath = self.output_dir / filename

                    with open(filepath, "wb") as f:
                        f.write(screenshot_data)

                    return {
                        "success": True,
                        "url": url,
                        "selector": selector,
                        "screenshot_path": str(filepath),
                        "filename": filename,
                    }

            return {
                "success": False,
                "url": url,
                "selector": selector,
                "error": result.error_message if hasattr(result, 'error_message') else "Unknown error"
            }

    async def analyze_visual_elements(self, url: str) -> Dict[str, Any]:
        """Analyze and extract information about visual elements on a page.

        Performs comprehensive visual analysis of a webpage including image extraction,
        video detection, icon identification, color palette extraction, and font analysis.
        Saves analysis results to JSON file in output directory.

        Args:
            url: Target URL to analyze for visual elements.

        Returns:
            Dict[str, Any]: Dictionary with keys:
                - success (bool): True if analysis completed successfully.
                - url (str): The target URL that was analyzed.
                - analysis_path (str, optional): Full path to saved analysis JSON file.
                - summary (Dict, optional): Layout summary with counts of elements,
                  unique colors, and unique fonts.
                - error (str, optional): Error message if analysis failed.

        Raises:
            OSError: Raised if analysis JSON file cannot be written to output directory.
        """
        js_analysis = """
        async () => {
            const analysis = {
                images: [],
                videos: [],
                icons: [],
                colors: new Set(),
                fonts: new Set(),
                layout: {}
            };

            // Analyze images
            document.querySelectorAll('img').forEach((img, i) => {
                if (img.src) {
                    analysis.images.push({
                        src: img.src,
                        alt: img.alt || '',
                        width: img.naturalWidth || img.width,
                        height: img.naturalHeight || img.height,
                        visible: img.offsetParent !== null
                    });
                }
            });

            // Analyze videos
            document.querySelectorAll('video').forEach((video, i) => {
                analysis.videos.push({
                    src: video.src || video.querySelector('source')?.src,
                    poster: video.poster,
                    duration: video.duration,
                    visible: video.offsetParent !== null
                });
            });

            // Analyze icons (common icon classes)
            document.querySelectorAll('[class*="icon"], [class*="svg"], [class*="fa-"]').forEach((el, i) => {
                analysis.icons.push({
                    tag: el.tagName,
                    classes: el.className,
                    visible: el.offsetParent !== null
                });
            });

            // Extract colors from computed styles
            document.querySelectorAll('*').forEach(el => {
                const color = window.getComputedStyle(el).color;
                if (color && color !== 'rgba(0, 0, 0, 0)') {
                    analysis.colors.add(color);
                }
                const font = window.getComputedStyle(el).fontFamily;
                if (font) analysis.fonts.add(font.split(',')[0].trim().replace(/["']/g, ''));
            });

            // Layout analysis
            const body = document.body;
            analysis.layout = {
                totalElements: document.querySelectorAll('*').length,
                images: analysis.images.length,
                videos: analysis.videos.length,
                icons: analysis.icons.length,
                uniqueColors: analysis.colors.size,
                uniqueFonts: analysis.fonts.size
            };

            return analysis;
        }
        """

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(js_code=js_analysis)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                # Save analysis results
                analysis_file = self.output_dir / "visual_analysis.json"
                with open(analysis_file, "w") as f:
                    json.dump(result.js_result, f, indent=2, default=list)

                return {
                    "success": True,
                    "url": url,
                    "analysis_path": str(analysis_file),
                    "summary": result.js_result.get("layout", {}),
                }

        return {
            "success": False,
            "url": url,
            "error": result.error_message if hasattr(result, 'error_message') else "Unknown error"
        }

    async def compare_visual_elements(
        self, url1: str, url2: str, selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compare visual elements between two URLs via side-by-side screenshots.

        Captures full-page screenshots of two URLs and creates a comparison report,
        allowing visual inspection of differences between website versions, A/B tests,
        or competitive pages.

        Args:
            url1: First URL to capture for comparison.
            url2: Second URL to capture for comparison.
            selector: Optional CSS selector for element-specific comparison (not used in current implementation).

        Returns:
            Dict[str, Any]: Dictionary with keys:
                - url1 (str): First URL that was compared.
                - url2 (str): Second URL that was compared.
                - screenshots (Dict): Paths to saved screenshots with url1 and url2 keys.
                - both_successful (bool): True if both captures succeeded.

        Raises:
            OSError: Raised if comparison report JSON file cannot be written to output directory.
        """
        results = await asyncio.gather(
            self.extract_full_screenshot(url1),
            self.extract_full_screenshot(url2),
        )

        comparison = {
            "url1": url1,
            "url2": url2,
            "screenshots": {
                "url1": results[0].get("screenshot_path"),
                "url2": results[1].get("screenshot_path"),
            },
            "both_successful": results[0]["success"] and results[1]["success"],
        }

        # Save comparison report
        report = {
            "timestamp": datetime.now().isoformat(),
            "comparison": comparison,
        }
        report_file = self.output_dir / "visual_comparison.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        return comparison


async def batch_process(
    urls: List[str], output_dir: str, full_page: bool = True
) -> List[Dict[str, Any]]:
    """Process multiple URLs for visual extraction with rate limiting.

    Asynchronously processes a batch of URLs to extract full-page screenshots,
    applying 1-second rate limiting between requests to avoid overwhelming servers.
    Saves individual results and generates a batch summary JSON file with all results.

    Args:
        urls: List of URLs to process for visual extraction.
        output_dir: Directory path where screenshots and batch results JSON will be saved.
        full_page: Whether to capture full-page screenshots (default: True). Currently,
                  both branches call extract_full_screenshot regardless of value.

    Returns:
        List[Dict[str, Any]]: List of extraction result dictionaries, each containing
            success status, URL, screenshot paths, and timestamps. Returns empty list
            if no URLs are provided or all URLs are empty strings.

    Raises:
        OSError: Raised if batch results JSON file cannot be written to output directory.
    """
    extractor = VisualExtractor(output_dir)
    results = []

    for url in urls:
        url = url.strip()
        if not url:
            continue

        print(f"Processing: {url}")
        if full_page:
            result = await extractor.extract_full_screenshot(url)
        else:
            result = await extractor.extract_full_screenshot(url)
        results.append(result)

        # Rate limiting
        await asyncio.sleep(1)

    # Save batch results
    batch_file = Path(output_dir) / "batch_results.json"
    with open(batch_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nBatch complete. Results saved to: {batch_file}")
    return results


def main() -> None:
    """CLI entry point for visual element extraction and screenshot capture.

    Orchestrates command-line interface for extracting visual elements, capturing
    full-page or element-specific screenshots, analyzing visual components, and
    comparing visual elements between URLs. Supports single URL, batch file, and
    comparison modes with optional CSS selector targeting for element-specific extraction.

    Command-line Arguments:
        url: Target URL for visual extraction (optional if using --batch or --compare).
        --full-page: Capture entire page including below-the-fold content (default: True).
        --selector, -s: CSS selector for element-specific screenshot extraction
                       (e.g., '.product-card', '#header').
        --output, -o: Output directory for screenshots and analysis files
                     (default: './visual_output').
        --batch, -b: File path containing URLs to process (one per line) for batch extraction.
        --analyze: Perform comprehensive visual element analysis including image extraction,
                  video detection, icon identification, color palette, and font analysis.
        --compare URL1 URL2: Side-by-side comparison of two URLs with screenshot capture.

    Output Files:
        screenshot_*.png: Full-page screenshots with timestamp in filename.
        element_*.png: Element-specific screenshots when using --selector.
        visual_analysis.json: Analysis results from --analyze including element counts.
        visual_comparison.json: Comparison report from --compare with both screenshots.
        batch_results.json: Batch processing summary when using --batch.

    Exit Codes:
        0: Success (extraction completed).
        1: Error (missing URL argument or no valid mode specified).

    Raises:
        SystemExit: With code 0 or 1 depending on argument validation and execution result.
    """
    parser.add_argument("url", nargs="?", help="URL to extract visuals from")
    parser.add_argument(
        "--full-page", action="store_true", default=True, help="Capture full page"
    )
    parser.add_argument(
        "--selector", "-s", help="CSS selector for element-specific screenshot"
    )
    parser.add_argument(
        "--output", "-o", default="./visual_output", help="Output directory"
    )
    parser.add_argument(
        "--batch", "-b", help="File containing URLs to process"
    )
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze visual elements on page"
    )
    parser.add_argument(
        "--compare", nargs=2, metavar=("URL1", "URL2"), help="Compare two URLs"
    )

    args = parser.parse_args()

    if not any([args.url, args.batch, args.compare]):
        parser.print_help()
        print("\nExamples:")
        print("  python visual-extractor.py https://example.com")
        print("  python visual-extractor.py https://example.com --selector '.product'")
        print("  python visual-extractor.py --batch urls.txt")
        print("  python visual-extractor.py --compare https://a.com https://b.com")
        print("  python visual-extractor.py https://example.com --analyze")
        sys.exit(1)

    extractor = VisualExtractor(args.output)

    if args.compare:
        results = asyncio.run(extractor.compare_visual_elements(args.compare[0], args.compare[1]))
        print(f"Comparison complete: {results}")
    elif args.batch:
        with open(args.batch) as f:
            urls = f.readlines()
        results = asyncio.run(batch_process(urls, args.output, args.full_page))
    elif args.url:
        if args.selector:
            result = asyncio.run(extractor.extract_element_screenshot(args.url, args.selector))
        elif args.analyze:
            result = asyncio.run(extractor.analyze_visual_elements(args.url))
        else:
            result = asyncio.run(extractor.extract_full_screenshot(args.url))

        print(f"Result: {result}")
        if result.get("success"):
            print(f"Screenshot saved: {result.get('screenshot_path')}")


if __name__ == "__main__":
    main()
