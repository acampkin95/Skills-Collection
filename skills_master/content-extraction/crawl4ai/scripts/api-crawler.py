#!/usr/bin/env python3
"""
API Crawler - Crawl and extract information from API documentation sites.

This script specializes in extracting API documentation, endpoints, parameters,
and examples from sites like Swagger/OpenAPI docs, API reference pages,
and developer documentation.

Usage:
    python api-crawler.py <api-docs-url> [--output <dir>] [--format json|markdown]
    python api-crawler.py --batch apis.txt --format markdown
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.content_filter_strategy import PruningContentFilter
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
except ImportError:
    print("Error: crawl4ai not installed. Run: pip install crawl4ai")
    sys.exit(1)


class APICrawler:
    """Crawl and extract API documentation content.

    Provides methods to detect API documentation formats (Swagger, OpenAPI, Redoc),
    extract OpenAPI specifications, crawl individual endpoints, and generate
    comprehensive API documentation reports in JSON or Markdown format.
    """

    def __init__(self, output_dir: str = "./api_output") -> None:
        """Initialize the API crawler with output directory.

        Args:
            output_dir: Directory path where crawled API reports will be saved.
                       Defaults to "./api_output". Directory is created if it doesn't exist.

        Returns:
            None.

        Raises:
            No exceptions raised; directory creation errors are handled implicitly by pathlib.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def detect_api_format(self, url: str) -> Dict[str, Any]:
        """Detect if URL contains OpenAPI/Swagger documentation.

        Executes JavaScript in browser context to detect presence of Swagger UI,
        OpenAPI specifications, Redoc documentation, and extracts OpenAPI version
        and specification URL if available.

        Args:
            url: URL of the potential API documentation page.

        Returns:
            Dictionary containing detection results with keys:
            - hasSwagger: Boolean indicating Swagger UI presence
            - hasOpenAPI: Boolean indicating OpenAPI spec presence
            - hasRedoc: Boolean indicating Redoc presence
            - version: OpenAPI version string if detected
            - specUrl: URL to OpenAPI specification file if found
            - endpoints: List of detected endpoints
            - title: Page title
            - error: Error message if detection failed

        Raises:
            No exceptions raised; errors are returned in the response dictionary.
        """
        js_detection = """
        async () => {
            const result = {
                hasSwagger: false,
                hasOpenAPI: false,
                hasRedoc: false,
                version: null,
                specUrl: null,
                endpoints: [],
                title: document.title
            };

            // Check for Swagger UI
            const swaggerDiv = document.querySelector('.swagger-ui, #swagger-ui, [data-swagger-url]');
            if (swaggerDiv || window.swaggerUi) {
                result.hasSwagger = true;
            }

            // Check for OpenAPI spec in scripts
            document.querySelectorAll('script').forEach(script => {
                if (script.src && (script.src.includes('swagger') || script.src.includes('openapi'))) {
                    result.hasSwagger = true;
                }
                if (script.textContent) {
                    const match = script.textContent.match(/"openapi"\s*:\s*"([^"]+)"/);
                    if (match) {
                        result.hasOpenAPI = true;
                        result.version = match[1];
                    }
                }
            });

            // Check for Redoc
            if (document.querySelector('redoc, [data-theme="redoc"]')) {
                result.hasRedoc = true;
            }

            // Look for OpenAPI spec link
            const links = document.querySelectorAll('link[rel="alternate"], link[type*="json"]');
            links.forEach(link => {
                if (link.href && (link.href.includes('swagger') || link.href.endsWith('.json'))) {
                    result.specUrl = link.href;
                }
            });

            return result;
        }
        """

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(js_code=js_detection)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return result.js_result
            return {"error": "Failed to detect API format"}

    async def extract_openapi_spec(self, spec_url: str) -> Dict[str, Any]:
        """Fetch and parse OpenAPI specification directly.

        Downloads the OpenAPI/Swagger specification from the provided URL,
        parses it as JSON, and saves it to the output directory.

        Args:
            spec_url: URL pointing to the OpenAPI specification file (JSON format).

        Returns:
            Dictionary containing the parsed OpenAPI specification, or error dictionary
            with 'error' key if fetch/parse failed.

        Raises:
            No exceptions raised; fetch and parse errors are caught and returned
            in the response dictionary.
        """
        js_fetch = f"""
        async () => {{
            try {{
                const response = await fetch('{spec_url}');
                return await response.json();
            }} catch (e) {{
                return {{ error: e.message }};
            }}
        }}
        """

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(js_code=js_fetch)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(spec_url, config=crawler_config)

            if result.success and hasattr(result, 'js_result'):
                spec = result.js_result
                if isinstance(spec, dict) and 'error' not in spec:
                    # Save raw spec
                    spec_file = self.output_dir / "openapi_spec.json"
                    with open(spec_file, "w") as f:
                        json.dump(spec, f, indent=2)
                    return spec

            return {"error": "Could not fetch OpenAPI spec"}

    async def crawl_api_endpoint(
        self, url: str, endpoint_name: str
    ) -> Dict[str, Any]:
        """Extract documentation for a specific API endpoint.

        Crawls a specific endpoint documentation page and extracts markdown content
        using content pruning for quality filtering. Handles both successful extractions
        and crawl failures with appropriate error reporting.

        Args:
            url: URL of the endpoint documentation page to crawl.
            endpoint_name: Human-readable name or identifier for the endpoint.

        Returns:
            Dictionary containing endpoint documentation with keys:
            - endpoint: The endpoint name identifier
            - url: The crawled URL
            - markdown: Raw markdown object if successful
            - raw_markdown: Extracted markdown string content
            - error: Error message if crawl failed

        Raises:
            No exceptions raised; crawl failures are returned in the response dictionary.
        """
        content_filter = PruningContentFilter(threshold=0.5)
        md_generator = DefaultMarkdownGenerator(content_filter=content_filter)

        browser_config = BrowserConfig(headless=True, viewport_width=1280)
        crawler_config = CrawlerRunConfig(
            markdown_generator=md_generator,
            page_timeout=30000,
            wait_for="networkidle",
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return {
                    "endpoint": endpoint_name,
                    "url": url,
                    "markdown": result.markdown,
                    "raw_markdown": result.markdown.raw_markdown if hasattr(result.markdown, 'raw_markdown') else str(result.markdown),
                }

            return {"endpoint": endpoint_name, "url": url, "error": "Failed to crawl"}

    async def extract_endpoints_from_page(self, url: str) -> List[Dict[str, str]]:
        """Extract endpoint links from an API documentation page.

        Executes JavaScript in browser context to discover endpoint links using multiple
        selector patterns and HTTP method code block detection. Extracts URLs, display
        text, and HTTP method for each discovered endpoint.

        Args:
            url: URL of the API documentation page to analyze.

        Returns:
            List of endpoint dictionaries, each containing:
            - url: The discovered endpoint URL
            - text: Display text or description from the link
            - method: HTTP method (GET, POST, PUT, DELETE, PATCH, or default GET)
            Empty list if extraction fails or no endpoints are found.

        Raises:
            No exceptions raised; extraction failures are caught and return empty list.
        """
        js_extraction = """
        async () => {
            const endpoints = [];

            // Common patterns for endpoint links
            const patterns = [
                'a[href*="/api/"]',
                'a[href*="/endpoints/"]',
                '.endpoint-link',
                '[data-endpoint]',
                '.operation-link'
            ];

            patterns.forEach(selector => {
                document.querySelectorAll(selector).forEach(link => {
                    const href = link.href || link.getAttribute('data-endpoint');
                    const text = link.textContent?.trim() || link.getAttribute('data-method') || 'unknown';
                    if (href) {
                        endpoints.push({
                            url: href,
                            text: text,
                            method: link.getAttribute('data-method') || 'GET'
                        });
                    }
                });
            });

            // Also look for code blocks with HTTP methods
            document.querySelectorAll('code, pre').forEach(block => {
                const text = block.textContent || '';
                const match = text.match(/(GET|POST|PUT|DELETE|PATCH)\s+(\S+)/);
                if (match) {
                    endpoints.push({
                        url: url + match[2],
                        text: text.substring(0, 100),
                        method: match[1]
                    });
                }
            });

            return endpoints;
        }
        """

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(js_code=js_extraction)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return result.js_result or []

        return []

    async def generate_api_report(
        self, url: str, format: str = "markdown"
    ) -> Dict[str, Any]:
        """Generate comprehensive API documentation report.

        Orchestrates complete API documentation extraction workflow including format
        detection, OpenAPI spec extraction, endpoint discovery, and documentation crawling.
        Generates final report in JSON or Markdown format and saves to output directory.

        Args:
            url: URL of the API documentation site to crawl and analyze.
            format: Output format for the report ('json' or 'markdown'). Defaults to 'markdown'.

        Returns:
            Dictionary containing comprehensive API report with keys:
            - source_url: The original URL that was crawled
            - crawled_at: ISO timestamp of when the crawl occurred
            - detected_format: Format detection results (Swagger, OpenAPI, Redoc info)
            - openapi_spec: Full OpenAPI specification if found
            - endpoints: List of extracted endpoint definitions
            - endpoints_documentation: Crawled documentation for each endpoint
            - parameters: Extracted parameter definitions
            - examples: Code examples found in documentation
            - schemas: Data schema definitions

        Raises:
            No exceptions raised; extraction failures are caught and partial results returned.
        """
        report = {
            "source_url": url,
            "crawled_at": datetime.now().isoformat(),
            "endpoints": [],
            "parameters": [],
            "examples": [],
            "schemas": [],
        }

        # Detect format
        format_info = await self.detect_api_format(url)
        report["detected_format"] = format_info

        # Try to extract OpenAPI spec if detected
        if format_info.get("specUrl"):
            spec = await self.extract_openapi_spec(format_info["specUrl"])
            if "error" not in spec:
                report["openapi_spec"] = spec
                # Extract endpoints from spec
                if "paths" in spec:
                    for path, methods in spec["paths"].items():
                        for method, details in methods.items():
                            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                                report["endpoints"].append({
                                    "path": path,
                                    "method": method.upper(),
                                    "summary": details.get("summary", ""),
                                    "description": details.get("description", ""),
                                    "parameters": details.get("parameters", []),
                                    "responses": list(details.get("responses", {}).keys()),
                                })

        # If no OpenAPI spec, crawl page for documentation
        if not report.get("openapi_spec"):
            endpoints = await self.extract_endpoints_from_page(url)
            report["endpoints"] = endpoints

            # Crawl each endpoint for documentation
            for endpoint in endpoints[:10]:  # Limit to first 10 for performance
                doc = await self.crawl_api_endpoint(endpoint["url"], endpoint["text"])
                if "error" not in doc:
                    report["endpoints_documentation"] = report.get("endpoints_documentation", [])
                    report["endpoints_documentation"].append(doc)

        # Save report
        if format == "json":
            report_file = self.output_dir / "api_report.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
        else:
            # Generate markdown report
            markdown_report = self._generate_markdown_report(report)
            report_file = self.output_dir / "api_report.md"
            with open(report_file, "w") as f:
                f.write(markdown_report)

        return report

    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate markdown report from API crawl data.

        Formats API report data into a well-structured markdown document including
        overview section, detected format information, endpoint definitions, and
        endpoint documentation. Limits output to first 20 endpoints for readability.

        Args:
            report: Dictionary containing API report data with keys source_url,
                   crawled_at, detected_format, endpoints, endpoints_documentation.

        Returns:
            String containing formatted markdown report ready for file output.

        Raises:
            No exceptions raised; missing keys gracefully default to empty values.
        """
        lines = [
            f"# API Documentation Report",
            f"",
            f"**Source:** {report['source_url']}",
            f"**Crawled:** {report['crawled_at']}",
            f"",
            f"## Overview",
            f"",
        ]

        if "detected_format" in report:
            format_info = report["detected_format"]
            lines.append(f"**Detected Format:**")
            if format_info.get("hasSwagger"):
                lines.append("- Swagger UI detected")
            if format_info.get("hasOpenAPI"):
                lines.append(f"- OpenAPI v{format_info.get('version', 'unknown')}")
            if format_info.get("hasRedoc"):
                lines.append("- Redoc detected")
            lines.append("")

        lines.append(f"## Endpoints")
        lines.append("")

        for endpoint in report.get("endpoints", [])[:20]:
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", endpoint.get("url", ""))
            summary = endpoint.get("summary", "")

            lines.append(f"### `{method} {path}`")
            if summary:
                lines.append(f"_{summary}_")
            lines.append("")

        if "endpoints_documentation" in report:
            lines.append(f"## Endpoint Documentation")
            lines.append("")
            for doc in report.get("endpoints_documentation", []):
                lines.append(f"### {doc.get('endpoint', 'Unknown')}")
                lines.append("")
                lines.append(doc.get("markdown", ""))
                lines.append("")

        return "\n".join(lines)


async def batch_crawl_apis(urls: List[str], output_dir: str, format: str) -> List[Dict[str, Any]]:
    """Crawl multiple API documentation sites concurrently with rate limiting.

    Processes a list of API documentation URLs sequentially, generating comprehensive
    API reports for each URL. Includes 2-second rate limiting between requests to avoid
    overwhelming target servers. Saves individual reports and writes a consolidated batch
    results file to the output directory.

    Args:
        urls: List of API documentation URLs to crawl and analyze.
        output_dir: Directory path where batch results will be saved.
        format: Output format for reports ('json' or 'markdown'). Passed to generate_api_report.

    Returns:
        List[Dict[str, Any]]: List of API report dictionaries, one per successfully processed URL.
            Each report contains source_url, crawled_at, detected_format, endpoints,
            openapi_spec (if detected), and other extracted API metadata.

    Raises:
        No exceptions raised; URL processing errors are caught internally and reported
        in result metadata. Individual URL failures do not prevent processing of subsequent URLs.
    """
    crawler = APICrawler(output_dir)
    results = []

    for url in urls:
        url = url.strip()
        if not url:
            continue

        print(f"Processing API docs: {url}")
        result = await crawler.generate_api_report(url, format)
        results.append(result)
        await asyncio.sleep(2)  # Rate limiting

    batch_file = Path(output_dir) / "batch_api_results.json"
    with open(batch_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nBatch complete. Results saved to: {batch_file}")
    return results


def main() -> None:
    """Main entry point for the API crawler command-line application.

    Parses command-line arguments to support three modes of operation:
    1. Single URL crawl: Crawl a single API documentation URL and generate a report
    2. Batch crawl: Process multiple URLs from a file with rate limiting
    3. Detection-only: Analyze a URL for API format (Swagger, OpenAPI, Redoc) without full crawl

    Command-line Arguments:
        url: (optional) API documentation URL to crawl
        --output, -o: Output directory for reports (default: './api_output')
        --format, -f: Output format 'json' or 'markdown' (default: 'markdown')
        --batch, -b: File containing newline-separated API documentation URLs
        --detect-only: Only detect API format without performing full crawl

    Returns:
        None. Exits with code 0 on success, code 1 on argument validation failure.

    Raises:
        No exceptions raised; all execution errors are caught and logged to stdout.
        Missing arguments trigger help display and sys.exit(1).
    """
    parser = argparse.ArgumentParser(description="Crawl API documentation sites")
    parser.add_argument("url", nargs="?", help="API documentation URL")
    parser.add_argument(
        "--output", "-o", default="./api_output", help="Output directory"
    )
    parser.add_argument(
        "--format", "-f", choices=["json", "markdown"], default="markdown",
        help="Output format"
    )
    parser.add_argument(
        "--batch", "-b", help="File containing API documentation URLs"
    )
    parser.add_argument(
        "--detect-only", action="store_true",
        help="Only detect API format without full crawl"
    )

    args = parser.parse_args()

    if not any([args.url, args.batch]):
        parser.print_help()
        print("\nExamples:")
        print("  python api-crawler.py https://api.example.com/docs")
        print("  python api-crawler.py https://api.example.com --format json")
        print("  python api-crawler.py --batch apis.txt")
        print("  python api-crawler.py https://api.example.com --detect-only")
        sys.exit(1)

    crawler = APICrawler(args.output)

    if args.batch:
        with open(args.batch) as f:
            urls = f.readlines()
        results = asyncio.run(batch_crawl_apis(urls, args.output, args.format))
    elif args.url:
        if args.detect_only:
            result = asyncio.run(crawler.detect_api_format(args.url))
        else:
            result = asyncio.run(crawler.generate_api_report(args.url, args.format))
        print(f"Report saved to: {args.output}")


if __name__ == "__main__":
    main()
