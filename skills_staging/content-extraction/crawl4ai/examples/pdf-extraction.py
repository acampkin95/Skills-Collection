#!/usr/bin/env python3
"""
PDF Extraction - Extract text and content from PDF documents.

This script handles PDF extraction via web-based PDF viewers and converters.
For local PDF processing, it also integrates with popular PDF libraries.

Usage:
    python pdf-extraction.py <pdf-url>
    python pdf-extraction.py --batch pdfs.txt --output ./extracted
    python pdf-extraction.py --local document.pdf --method pypdf
"""

import argparse
import asyncio
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, BinaryIO

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
except ImportError:
    print("Error: crawl4ai not installed. Run: pip install crawl4ai")
    sys.exit(1)

# Try importing PDF libraries
PDF_LIBS_AVAILABLE = {}
try:
    import PyPDF2
    PDF_LIBS_AVAILABLE["pypdf"] = PyPDF2
except ImportError:
    pass

try:
    import pdfplumber
    PDF_LIBS_AVAILABLE["pdfplumber"] = pdfplumber
except ImportError:
    pass

try:
    from PIL import Image
    PDF_LIBS_AVAILABLE["pillow"] = Image
except ImportError:
    pass


class PDFExtractor:
    """Extract content from PDF documents via web and local files."""

    def __init__(self, output_dir: str = "./pdf_extracted"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract text from PDF via browser rendering."""
        js_extraction = """
        async () => {
            const result = {
                pages: [],
                metadata: {},
                error: null
            };

            try {
                // Get PDF metadata
                result.metadata = {
                    title: document.title,
                    url: window.location.href
                };

                // For PDF.js rendered PDFs
                const pages = document.querySelectorAll('.page');
                if (pages.length > 0) {
                    result.rendered_with = 'pdfjs';

                    pages.forEach((page, i) => {
                        const textLayer = page.querySelector('.textLayer');
                        const canvas = page.querySelector('canvas');

                        result.pages.push({
                            page_num: i + 1,
                            text: textLayer?.textContent || '',
                            has_canvas: !!canvas,
                            dimensions: canvas ? {
                                width: canvas.width,
                                height: canvas.height
                            } : null
                        });
                    });
                }

                // Try alternative selectors for other viewers
                const viewerText = document.querySelector('#viewer');
                if (viewerText) {
                    result.full_text = viewerText.textContent;
                }

                // Get page count from various sources
                const pageInfo = document.querySelector('[data-page-count], #page-count, .page-count');
                if (pageInfo) {
                    result.page_count = parseInt(pageInfo.textContent);
                }

            } catch (e) {
                result.error = e.message;
            }

            return result;
        }
        """

        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1200,
            viewport_height=1600,
        )
        crawler_config = CrawlerRunConfig(
            js_code=js_extraction,
            page_timeout=60000,
            wait_for="networkidle",
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return result.js_result or {}

        return {"error": "Failed to extract PDF content"}

    def extract_from_local_pdf(
        self, file_path: str, method: str = "auto"
    ) -> Dict[str, Any]:
        """
        Extract text from local PDF file.

        Args:
            file_path: Path to PDF file
            method: 'auto', 'pypdf', 'pdfplumber', or 'text'
        """
        result = {
            "file": file_path,
            "pages": [],
            "metadata": {},
            "text": "",
            "extracted_at": datetime.now().isoformat(),
        }

        if method == "auto":
            method = self._choose_best_method(file_path)

        try:
            if method == "pypdf" and "pypdf" in PDF_LIBS_AVAILABLE:
                result = self._extract_with_pypdf(file_path, result)
            elif method == "pdfplumber" and "pdfplumber" in PDF_LIBS_AVAILABLE:
                result = self._extract_with_pdfplumber(file_path, result)
            elif method == "text":
                result = self._extract_with_text(file_path, result)
            else:
                result["error"] = f"Method {method} not available. Install: pip install pypdf pdfplumber"

        except Exception as e:
            result["error"] = str(e)

        return result

    def _choose_best_method(self, file_path: str) -> str:
        """Choose best extraction method based on file and available libraries."""
        if "pdfplumber" in PDF_LIBS_AVAILABLE:
            return "pdfplumber"
        elif "pypdf" in PDF_LIBS_AVAILABLE:
            return "pypdf"
        else:
            return "text"

    def _extract_with_pypdf(self, file_path: str, result: Dict) -> Dict:
        """Extract using PyPDF2 library."""
        import PyPDF2

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            result["metadata"] = {
                "page_count": len(reader.pages),
                "pdf_version": reader.pdf_header if hasattr(reader, 'pdf_header') else "unknown",
            }

            # Extract metadata
            if reader.metadata:
                result["metadata"].update({
                    "title": str(reader.metadata.get("/Title", "")),
                    "author": str(reader.metadata.get("/Author", "")),
                    "subject": str(reader.metadata.get("/Subject", "")),
                    "creator": str(reader.metadata.get("/Creator", "")),
                    "producer": str(reader.metadata.get("/Producer", "")),
                    "creation_date": str(reader.metadata.get("/CreationDate", "")),
                })

            # Extract text from each page
            full_text = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                result["pages"].append({
                    "page_num": i + 1,
                    "text": page_text or "",
                    "char_count": len(page_text or ""),
                })
                full_text.append(page_text or "")

            result["text"] = "\n\n".join(full_text)
            result["total_pages"] = len(reader.pages)

        return result

    def _extract_with_pdfplumber(self, file_path: str, result: Dict) -> Dict:
        """Extract using pdfplumber library for better formatting."""
        import pdfplumber

        with pdfplumber.open(file_path) as pdf:
            result["metadata"] = {
                "page_count": len(pdf.pages),
            }

            # Extract metadata
            if pdf.metadata:
                result["metadata"].update({
                    "title": pdf.metadata.get("Title", ""),
                    "author": pdf.metadata.get("Author", ""),
                    "subject": pdf.metadata.get("Subject", ""),
                    "creator": pdf.metadata.get("Creator", ""),
                    "producer": pdf.metadata.get("Producer", ""),
                })

            full_text = []
            for i, page in enumerate(pdf.pages):
                page_data = {
                    "page_num": i + 1,
                    "text": page.extract_text() or "",
                }

                # Additional extraction for tables
                tables = page.extract_tables()
                page_data["tables"] = []
                for table in tables:
                    table_data = []
                    for row in table:
                        if row:
                            cleaned_row = [cell if cell else "" for cell in row]
                            table_data.append(cleaned_row)
                    if table_data:
                        page_data["tables"].append(table_data)

                # Image extraction info
                images = page.images
                page_data["image_count"] = len(images)

                result["pages"].append(page_data)
                full_text.append(page_data["text"])

            result["text"] = "\n\n".join(full_text)
            result["total_pages"] = len(pdf.pages)

        return result

    def _extract_with_text(self, file_path: str, result: Dict) -> Dict:
        """Simple text extraction using PDF text conversion."""
        import subprocess

        try:
            # Try using pdftotext if available
            result_file = result["file"] + ".txt"
            subprocess.run(
                ["pdftotext", "-layout", file_path, result_file],
                check=False,
                capture_output=True,
            )

            if Path(result_file).exists():
                with open(result_file) as f:
                    result["text"] = f.read()
                    result["pages"] = [{"page_num": 1, "text": result["text"]}]
                    result["total_pages"] = 1

        except Exception as e:
            result["error"] = f"Text extraction failed: {e}"

        return result

    def save_output(
        self,
        extraction_result: Dict[str, Any],
        base_name: str = None,
        formats: List[str] = None,
    ) -> Dict[str, str]:
        """Save extraction result in multiple formats."""
        if formats is None:
            formats = ["txt", "json"]

        output_files = {}
        filename = base_name or Path(extraction_result.get("file", "output")).stem

        if "json" in formats:
            json_file = self.output_dir / f"{filename}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(extraction_result, f, indent=2, ensure_ascii=False)
            output_files["json"] = str(json_file)

        if "txt" in formats:
            txt_file = self.output_dir / f"{filename}.txt"
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(extraction_result.get("text", ""))
            output_files["txt"] = str(txt_file)

        if "markdown" in formats:
            md_file = self.output_dir / f"{filename}.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(self._convert_to_markdown(extraction_result))
            output_files["markdown"] = str(md_file)

        return output_files

    def _convert_to_markdown(self, result: Dict) -> str:
        """Convert extraction result to markdown."""
        lines = [
            f"# {result.get('metadata', {}).get('title', 'PDF Document')}",
            "",
            f"**Extracted:** {result.get('extracted_at', '')}",
            f"**Pages:** {result.get('total_pages', 0)}",
            "",
            "---",
            "",
            "## Table of Contents",
            "",
        ]

        # Add page list
        for page in result.get("pages", []):
            lines.append(f"- [Page {page.get('page_num', '?')}](#page-{page.get('page_num', '')})")

        lines.extend(["", "---", ""])

        # Add each page
        for page in result.get("pages", []):
            lines.append(f"## Page {page.get('page_num', '')}")
            lines.append("")
            lines.append(page.get("text", ""))
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


async def batch_process_urls(urls: List[str], output_dir: str) -> List[Dict]:
    """Process multiple PDF URLs."""
    extractor = PDFExtractor(output_dir)
    results = []

    for url in urls:
        url = url.strip()
        if not url:
            continue

        print(f"Processing: {url}")
        result = await extractor.extract_from_url(url)
        result["source_url"] = url

        # Save output
        filename = re.sub(r'[<>:"/\\|?*]', '_', url.split("/")[-1].split(".")[0][:30])
        extractor.save_output(result, filename)

        results.append(result)
        await asyncio.sleep(2)  # Rate limiting

    return results


def main():
    parser = argparse.ArgumentParser(description="Extract content from PDF documents")
    parser.add_argument("url", nargs="?", help="PDF URL or file path")
    parser.add_argument(
        "--output", "-o", default="./pdf_extracted", help="Output directory"
    )
    parser.add_argument(
        "--batch", "-b", help="File containing PDF URLs/paths (one per line)"
    )
    parser.add_argument(
        "--local", "-l", action="store_true",
        help="Treat input as local file path(s)"
    )
    parser.add_argument(
        "--method",
        choices=["auto", "pypdf", "pdfplumber", "text"],
        default="auto",
        help="Extraction method for local PDFs"
    )
    parser.add_argument(
        "--formats",
        default="txt,json",
        help="Output formats (comma-separated: txt,json,markdown)"
    )

    args = parser.parse_args()

    if not any([args.url, args.batch]):
        parser.print_help()
        print("\nExamples:")
        print("  python pdf-extraction.py https://example.com/document.pdf")
        print("  python pdf-extraction.py ./local/file.pdf --method pypdf")
        print("  python pdf-extraction.py --batch pdfs.txt --output ./extracted")
        sys.exit(1)

    extractor = PDFExtractor(args.output)
    formats = args.formats.split(",")

    if args.batch:
        with open(args.batch) as f:
            lines = f.readlines()

        if args.local:
            # Process local files
            for path in lines:
                path = path.strip()
                if path and Path(path).exists():
                    result = extractor.extract_from_local_pdf(path, args.method)
                    filename = Path(path).stem
                    extractor.save_output(result, filename, formats)
        else:
            # Process URLs
            results = asyncio.run(batch_process_urls(lines, args.output))
            print(f"Processed {len(results)} PDFs")

    elif args.url:
        if args.local and Path(args.url).exists():
            # Local file
            result = extractor.extract_from_local_pdf(args.url, args.method)
            filename = Path(args.url).stem
            output_files = extractor.save_output(result, filename, formats)
            print(f"Saved: {list(output_files.values())}")
        else:
            # URL
            result = asyncio.run(extractor.extract_from_url(args.url))
            filename = re.sub(r'[<>:"/\\|?*]', '_', args.url.split("/")[-1].split(".")[0][:30])
            output_files = extractor.save_output(result, filename, formats)
            print(f"Saved: {list(output_files.values())}")


if __name__ == "__main__":
    asyncio.run(main())
