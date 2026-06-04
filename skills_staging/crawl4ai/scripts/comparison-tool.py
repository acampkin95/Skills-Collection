#!/usr/bin/env python3
"""
Comparison Tool - Compare multiple pages/documents for differences.

This script compares web pages, extracted content, or documents to identify
differences in structure, content, links, media, and visual elements.

Usage:
    python comparison-tool.py <url1> <url2> [--type content|structure|links|all]
    python comparison-tool.py --batch comparison.csv --output <dir>
    python comparison-tool.py --compare-files file1.md file2.md
"""

import argparse
import asyncio
import difflib
import hashlib
import json
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
except ImportError:
    print("Error: crawl4ai not installed. Run: pip install crawl4ai")
    sys.exit(1)


class ComparisonType(Enum):
    CONTENT = "content"
    STRUCTURE = "structure"
    LINKS = "links"
    MEDIA = "media"
    ALL = "all"


@dataclass
class PageData:
    """Data extracted from a web page."""
    url: str
    title: str = ""
    markdown: str = ""
    html: str = ""
    links: Dict[str, List[str]] = field(default_factory=dict)
    media: Dict[str, List[Dict]] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)
    structure: Dict[str, Any] = field(default_factory=dict)
    links_hash: str = ""
    content_hash: str = ""


@dataclass
class ComparisonResult:
    """Result of comparing two pages."""
    url1: str
    url2: str
    comparison_type: ComparisonType
    is_similar: bool
    similarity_score: float
    differences: List[Dict[str, Any]]
    timestamp: str = ""


class PageComparator:
    """Compare web pages for differences.

    Orchestrates web page crawling and comparison across multiple dimensions:
    content, structure, links, and media. Caches crawled pages to avoid redundant
    network requests when comparing the same URL multiple times.
    """

    def __init__(self) -> None:
        """Initialize the page comparator with empty cache.

        Args:
            None.

        Returns:
            None.
        """
        self.cache: Dict[str, PageData] = {}

    async def crawl_page(self, url: str) -> PageData:
        """Crawl and extract all data from a page.

        Fetches a URL using AsyncWebCrawler with JavaScript code execution to extract
        page structure, metadata, links, and media. Returns cached result if URL was
        previously crawled. Generates MD5 hashes of content and links for quick comparison.

        Args:
            url: Target URL to crawl and extract data from.

        Returns:
            PageData object containing markdown, HTML, links, media, structure, and metadata.

        Raises:
            No exceptions raised; errors in crawling are captured in result object.
        """
        if url in self.cache:
            return self.cache[url]

        js_extraction = """
        async () => {
            // Extract page structure
            const structure = {
                headings: [],
                paragraphs: 0,
                links: 0,
                images: 0,
                forms: 0,
                tables: 0,
                divCount: 0,
                spanCount: 0,
                classNames: [],
                ids: []
            };

            // Count elements
            document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach((h, i) => {
                structure.headings.push({ level: parseInt(h.tagName[1]), text: h.textContent?.trim() });
            });
            structure.paragraphs = document.querySelectorAll('p').length;
            structure.links = document.querySelectorAll('a').length;
            structure.images = document.querySelectorAll('img').length;
            structure.forms = document.querySelectorAll('form').length;
            structure.tables = document.querySelectorAll('table').length;
            structure.divCount = document.querySelectorAll('div').length;
            structure.spanCount = document.querySelectorAll('span').length;

            document.querySelectorAll('[class]').forEach(el => {
                el.classList.forEach(c => { if (!structure.classNames.includes(c)) structure.classNames.push(c); });
            });
            document.querySelectorAll('[id]').forEach(el => {
                if (!structure.ids.includes(el.id)) structure.ids.push(el.id);
            });

            return structure;
        }
        """

        browser_config = BrowserConfig(headless=True, viewport_width=1280)
        crawler_config = CrawlerRunConfig(
            js_code=js_extraction,
            page_timeout=30000,
            wait_for="networkidle",
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

        page_data = PageData(
            url=url,
            title=result.metadata.get("title", "") if result.metadata else "",
            markdown=result.markdown or "",
            html=result.html or "",
            links=result.links or {},
            media=result.media or {},
            metadata=result.metadata or {},
            structure=result.js_result or {},
        )

        # Generate hashes for quick comparison
        page_data.content_hash = hashlib.md5(page_data.markdown.encode()).hexdigest()
        page_data.links_hash = hashlib.md5(
            json.dumps(page_data.links, sort_keys=True).encode()
        ).hexdigest()

        self.cache[url] = page_data
        return page_data

    def compare_content(
        self, page1: PageData, page2: PageData
    ) -> ComparisonResult:
        """Compare content between two pages.

        Uses difflib.SequenceMatcher to calculate text similarity and performs
        line-by-line unified diff to identify specific content changes between pages.

        Args:
            page1: First PageData object to compare.
            page2: Second PageData object to compare.

        Returns:
            ComparisonResult with content similarity score and diff details.

        Raises:
            No exceptions raised; comparison always succeeds even with empty content.
        """
        differences = []

        # Text similarity using difflib
        text1 = page1.markdown.lower()
        text2 = page2.markdown.lower()

        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()

        # Find line-by-line differences
        lines1 = page1.markdown.split("\n")
        lines2 = page2.markdown.split("\n")

        diff = list(difflib.unified_diff(lines1, lines2, lineterm="", n=3))
        diff_lines = [line for line in diff if line.startswith(("+", "-", "@"))]

        if diff_lines:
            differences.append(
                {
                    "type": "content",
                    "description": "Content differences found",
                    "diff_sample": diff_lines[:20],
                    "added_lines": len([l for l in diff_lines if l.startswith("+")]),
                    "removed_lines": len([l for l in diff_lines if l.startswith("-")]),
                }
            )

        return ComparisonResult(
            url1=page1.url,
            url2=page2.url,
            comparison_type=ComparisonType.CONTENT,
            is_similar=similarity > 0.8,
            similarity_score=similarity,
            differences=differences,
            timestamp=datetime.now().isoformat(),
        )

    def compare_structure(
        self, page1: PageData, page2: PageData
    ) -> ComparisonResult:
        """Compare page structure between two pages.

        Analyzes element counts (headings, paragraphs, links, images, forms, tables, divs)
        and heading hierarchy to identify structural differences. Calculates structural
        similarity as a percentage based on element count variations.

        Args:
            page1: First PageData object to compare.
            page2: Second PageData object to compare.

        Returns:
            ComparisonResult with structural similarity score and element differences.

        Raises:
            No exceptions raised; comparison handles missing structure data gracefully.
        """
        differences = []
        struct1 = page1.structure
        struct2 = page2.structure

        # Compare element counts
        comparisons = [
            ("headings", struct1.get("headings", []), struct2.get("headings", [])),
            ("paragraphs", struct1.get("paragraphs", 0), struct2.get("paragraphs", 0)),
            ("links", struct1.get("links", 0), struct2.get("links", 0)),
            ("images", struct1.get("images", 0), struct2.get("images", 0)),
            ("forms", struct1.get("forms", 0), struct2.get("forms", 0)),
            ("tables", struct1.get("tables", 0), struct2.get("tables", 0)),
            ("divs", struct1.get("divCount", 0), struct2.get("divCount", 0)),
        ]

        for name, val1, val2 in comparisons:
            if val1 != val2:
                differences.append(
                    {
                        "type": "structure",
                        "element": name,
                        "page1_value": val1,
                        "page2_value": val2,
                        "description": f"{name} count differs",
                    }
                )

        # Compare heading hierarchy
        headings1 = struct1.get("headings", [])
        headings2 = struct2.get("headings", [])

        if headings1 != headings2:
            differences.append(
                {
                    "type": "structure",
                    "element": "heading_hierarchy",
                    "page1_headings": headings1[:5],
                    "page2_headings": headings2[:5],
                    "description": "Heading structure differs",
                }
            )

        # Calculate structural similarity
        total_diff = sum(
            abs(v.get("page1_value", 0) - v.get("page2_value", 0))
            for v in differences
            if isinstance(v, dict) and "page1_value" in v
        )
        max_elements = sum(
            max(v[1], v[2]) for v in comparisons if isinstance(v[1], int)
        )
        structural_similarity = 1 - (total_diff / max(max_elements, 1))

        return ComparisonResult(
            url1=page1.url,
            url2=page2.url,
            comparison_type=ComparisonType.STRUCTURE,
            is_similar=structural_similarity > 0.8,
            similarity_score=structural_similarity,
            differences=differences,
            timestamp=datetime.now().isoformat(),
        )

    def compare_links(
        self, page1: PageData, page2: PageData
    ) -> ComparisonResult:
        """Compare links between two pages.

        Compares both internal and external links from two pages, identifying added
        and removed links, and calculating Jaccard similarity metric. Useful for
        detecting navigation changes, broken link patterns, and redirect updates.

        Args:
            page1: First PageData object containing link information from crawled page.
            page2: Second PageData object containing link information from crawled page.

        Returns:
            ComparisonResult object with comparison_type=LINKS containing similarity score
            (0.0-1.0 based on Jaccard similarity), is_similar flag (True if score > 0.7),
            and differences list showing added/removed links with counts and samples.

        Raises:
            No exceptions raised; handles missing link data gracefully with empty defaults.
        """
        differences = []
        links1 = set(page1.links.get("internal", []) + page1.links.get("external", []))
        links2 = set(page2.links.get("internal", []) + page2.links.get("external", []))

        added = links2 - links1
        removed = links1 - links2
        common = links1 & links2

        if added:
            differences.append(
                {
                    "type": "links",
                    "subtype": "added",
                    "count": len(added),
                    "links": list(added)[:10],
                }
            )

        if removed:
            differences.append(
                {
                    "type": "links",
                    "subtype": "removed",
                    "count": len(removed),
                    "links": list(removed)[:10],
                }
            )

        similarity = len(common) / max(len(links1 | links2), 1)

        return ComparisonResult(
            url1=page1.url,
            url2=page2.url,
            comparison_type=ComparisonType.LINKS,
            is_similar=similarity > 0.7,
            similarity_score=similarity,
            differences=differences,
            timestamp=datetime.now().isoformat(),
        )

    def compare_media(
        self, page1: PageData, page2: PageData
    ) -> ComparisonResult:
        """Compare media elements between two pages.

        Compares image elements (by src attribute) between two pages, identifying added
        and removed images. Calculates Jaccard similarity based on image source URLs.
        Useful for detecting image gallery changes, missing assets, or media updates.

        Args:
            page1: First PageData object containing media information from crawled page.
            page2: Second PageData object containing media information from crawled page.

        Returns:
            ComparisonResult object with comparison_type=MEDIA containing similarity score
            (0.0-1.0 based on Jaccard similarity of image sources), is_similar flag
            (True if score > 0.7), and differences list with added/removed image counts.

        Raises:
            No exceptions raised; handles missing media data gracefully with empty defaults.
        """
        differences = []

        images1 = page1.media.get("images", [])
        images2 = page2.media.get("images", [])

        src1 = set(img.get("src", "") for img in images1)
        src2 = set(img.get("src", "") for img in images2)

        added = src2 - src1
        removed = src1 - src2

        if added:
            differences.append(
                {
                    "type": "media",
                    "subtype": "images_added",
                    "count": len(added),
                    "examples": list(added)[:5],
                }
            )

        if removed:
            differences.append(
                {
                    "type": "media",
                    "subtype": "images_removed",
                    "count": len(removed),
                    "examples": list(removed)[:5],
                }
            )

        similarity = len(src1 & src2) / max(len(src1 | src2), 1)

        return ComparisonResult(
            url1=page1.url,
            url2=page2.url,
            comparison_type=ComparisonType.MEDIA,
            is_similar=similarity > 0.7,
            similarity_score=similarity,
            differences=differences,
            timestamp=datetime.now().isoformat(),
        )

    async def compare(
        self,
        url1: str,
        url2: str,
        comparison_type: ComparisonType = ComparisonType.ALL,
    ) -> Dict[str, ComparisonResult]:
        """Compare two pages with specified comparison type.

        Orchestrates the comparison of two URLs across one or more dimensions (content,
        structure, links, media). Crawls both pages asynchronously, caching results
        for efficiency, then runs selected comparison methods based on comparison_type.

        Args:
            url1: First URL to compare.
            url2: Second URL to compare.
            comparison_type: ComparisonType enum specifying comparison dimensions (default: ALL).
                Options: CONTENT, STRUCTURE, LINKS, MEDIA, or ALL to run all comparisons.

        Returns:
            Dictionary mapping comparison dimension names to ComparisonResult objects.
            Keys include 'content', 'structure', 'links', 'media' depending on comparison_type.
            Each ComparisonResult contains similarity score, differences, and detailed metrics.

        Raises:
            OSError: If crawling fails due to network or file system errors.
            aiohttp.ClientError: If HTTP request fails during page crawling.
        """
        print(f"Crawling {url1}...")
        page1 = await self.crawl_page(url1)

        print(f"Crawling {url2}...")
        page2 = await self.crawl_page(url2)

        results = {}

        if comparison_type in (ComparisonType.ALL, ComparisonType.CONTENT):
            results["content"] = self.compare_content(page1, page2)

        if comparison_type in (ComparisonType.ALL, ComparisonType.STRUCTURE):
            results["structure"] = self.compare_structure(page1, page2)

        if comparison_type in (ComparisonType.ALL, ComparisonType.LINKS):
            results["links"] = self.compare_links(page1, page2)

        if comparison_type in (ComparisonType.ALL, ComparisonType.MEDIA):
            results["media"] = self.compare_media(page1, page2)

        return results


class FileComparator:
    """Compare local files for differences.

    Provides static methods for comparing local files on disk using line-by-line
    diffing and SequenceMatcher similarity analysis. Useful for version control
    comparisons, generated file audits, and snapshot testing.
    """

    @staticmethod
    def compare_files(file1: str, file2: str) -> ComparisonResult:
        """Compare two files line by line.

        Loads two local files, generates a unified diff, and calculates overall
        similarity using difflib.SequenceMatcher. Returns differences as unified
        diff format with up to 50 diff lines displayed and total count provided.

        Args:
            file1: Path to first file to compare.
            file2: Path to second file to compare.

        Returns:
            ComparisonResult object with comparison_type=CONTENT containing similarity score
            (0.0-1.0 based on SequenceMatcher ratio), is_similar flag (True if score > 0.8),
            and differences list with unified diff output (max 50 lines shown, total tracked).

        Raises:
            FileNotFoundError: Raised if either file1 or file2 does not exist or cannot be opened.
            IOError: Raised if file reading fails due to permission or encoding errors.
        """
        with open(file1) as f1, open(file2) as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()

        diff = list(difflib.unified_diff(lines1, lines2, lineterm="", n=3))

        similarity = difflib.SequenceMatcher(
            None, "".join(lines1), "".join(lines2)
        ).ratio()

        differences = []
        if diff:
            differences.append(
                {
                    "type": "file_diff",
                    "diff_lines": [l for l in diff[:50]],
                    "total_diff_lines": len(diff),
                }
            )

        return ComparisonResult(
            url1=file1,
            url2=file2,
            comparison_type=ComparisonType.CONTENT,
            is_similar=similarity > 0.8,
            similarity_score=similarity,
            differences=differences,
            timestamp=datetime.now().isoformat(),
        )


def format_result(result: ComparisonResult) -> str:
    """Format comparison result as readable string.

    Converts a ComparisonResult object into human-readable text format with clear
    headers, similarity metrics, and detailed differences. Useful for console output
    and human review of comparison results.

    Args:
        result: ComparisonResult object containing comparison metrics and differences.

    Returns:
        String formatted as multi-line text with separators, headers, similarity score,
        differences list with key-value pairs, or "No significant differences" message.

    Raises:
        No exceptions raised; handles missing difference data gracefully.
    """
    lines = [
        f"\n{'='*60}",
        f"Comparison: {result.url1} vs {result.url2}",
        f"Type: {result.comparison_type.value}",
        f"Similarity: {result.similarity_score:.2%}",
        f"Is Similar: {'Yes' if result.is_similar else 'No'}",
        f"{'='*60}",
    ]

    if result.differences:
        lines.append("\nDifferences Found:")
        for diff in result.differences:
            lines.append(f"\n  [{diff.get('type', 'unknown')}]")
            for key, value in diff.items():
                if key != "type":
                    lines.append(f"    {key}: {value}")
    else:
        lines.append("\nNo significant differences found.")

    return "\n".join(lines)


def main() -> None:
    """CLI entry point for comparing web pages and local files.

    Orchestrates page and file comparison operations with flexible input modes:
    - Single comparison: compare two URLs or files
    - Batch comparison: read multiple comparisons from CSV file
    - Format options: output as text or JSON

    Command-line Arguments:
        url1: First URL or file path (optional, required with url2 unless --batch or --compare-files).
        url2: Second URL or file path (optional, required with url1 unless --batch or --compare-files).
        --type, -t: Comparison type - 'content', 'structure', 'links', 'media', or 'all' (default: 'all').
        --output, -o: Output file path for results in JSON format (optional).
        --batch, -b: CSV file with multiple comparisons (url1,url2,type per line).
        --compare-files: Compare local files instead of URLs (takes FILE1 FILE2 arguments).
        --format: Output format - 'text' or 'json' (default: 'text').

    Output Files:
        When --output is specified: results are appended to JSON file with ComparisonResult objects.
        Console output: formatted comparison results in specified format (text or JSON).

    Exit Codes:
        0: Success (comparisons completed, may have differences in results).
        1: Error (invalid arguments, missing required parameters, or file not found).

    Raises:
        SystemExit: With code 0 or 1 depending on argument validation and execution result.
    """
    parser = argparse.ArgumentParser(description="Compare web pages and documents")
    parser.add_argument("url1", nargs="?", help="First URL or file path")
    parser.add_argument("url2", nargs="?", help="Second URL or file path")
    parser.add_argument(
        "--type",
        "-t",
        choices=["content", "structure", "links", "media", "all"],
        default="all",
        help="Type of comparison",
    )
    parser.add_argument(
        "--output", "-o", help="Output file for results (JSON)"
    )
    parser.add_argument(
        "--batch", "-b", help="CSV file with comparisons (url1,url2,type)"
    )
    parser.add_argument(
        "--compare-files", nargs=2, metavar=("FILE1", "FILE2"),
        help="Compare local files instead of URLs"
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format"
    )

    args = parser.parse_args()

    if not any([args.url1 and args.url2, args.compare_files, args.batch]):
        parser.print_help()
        print("\nExamples:")
        print("  python comparison-tool.py https://a.com https://b.com")
        print("  python comparison-tool.py https://a.com https://b.com --type content")
        print("  python comparison-tool.py --compare-files file1.md file2.md")
        print("  python comparison-tool.py --batch comparisons.csv")
        sys.exit(1)

    if args.compare_files:
        comparator = FileComparator()
        result = comparator.compare_files(args.compare_files[0], args.compare_files[1])
        output = format_result(result) if args.format == "text" else json.dumps(result.__dict__, indent=2)
        print(output)
        return

    comparator = PageComparator()
    comparison_type = ComparisonType(args.type)

    if args.batch:
        # Process batch file
        with open(args.batch) as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    u1, u2 = parts[0], parts[1]
                    ctype = ComparisonType(parts[2]) if len(parts) > 2 else comparison_type

                    print(f"\nComparing: {u1} vs {u2}")
                    results = asyncio.run(comparator.compare(u1, u2, ctype))

                    for key, result in results.items():
                        output = format_result(result) if args.format == "text" else json.dumps(result.__dict__, indent=2)
                        print(output)

                        if args.output:
                            # Append to output file
                            with open(args.output, "a") as f:
                                f.write(json.dumps(result.__dict__) + "\n")
    else:
        results = asyncio.run(comparator.compare(args.url1, args.url2, comparison_type))

        if args.format == "json":
            output = {k: v.__dict__ for k, v in results.items()}
            print(json.dumps(output, indent=2))
        else:
            for key, result in results.items():
                print(format_result(result))

        if args.output:
            with open(args.output, "w") as f:
                for key, result in results.items():
                    f.write(json.dumps(result.__dict__) + "\n")


if __name__ == "__main__":
    main()
