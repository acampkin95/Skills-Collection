#!/usr/bin/env python3
"""
PDF to Markdown Converter using DeepInfra olmOCR

Convert PDF documents to well-structured Markdown files with optional
heading detection, table of contents generation, and smart formatting.

Usage:
    python pdf_to_markdown.py <input.pdf> [options]
    python pdf_to_markdown.py <pdf_folder/> -o <output_folder/> [options]

Examples:
    python pdf_to_markdown.py report.pdf
    python pdf_to_markdown.py report.pdf -o report.md
    python pdf_to_markdown.py report.pdf -o report.md --structured --toc
    python pdf_to_markdown.py ./scans/ -o ./markdown/ --dpi 300
    python pdf_to_markdown.py invoice.pdf -o invoice.md -p "Format as structured data"
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

from deepinfra_ocr import OCRClient


def clean_text(text: str) -> str:
    """Clean OCR text: normalize whitespace, fix common issues."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Remove excessive blank lines (keep max 2)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    
    # Fix common OCR artifacts
    text = re.sub(r"(\w)- \n(\w)", r"\1\2", text)  # Hyphenated line breaks
    
    return text.strip()


def detect_headings(text: str) -> str:
    """Apply heuristic heading detection to OCR text."""
    lines = text.split("\n")
    processed = []
    prev_blank = True
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if not stripped:
            processed.append("")
            prev_blank = True
            continue
        
        is_short = len(stripped) < 80
        is_standalone = prev_blank and (i + 1 >= len(lines) or not lines[i + 1].strip() or len(lines[i + 1].strip()) < 20)
        
        # ALL CAPS short lines → H3
        if stripped.isupper() and is_short and len(stripped) > 3 and not stripped.endswith(":"):
            processed.append(f"### {stripped.title()}")
        
        # Numbered sections: 1. Introduction, 1.1 Methods, etc.
        elif re.match(r"^(\d+\.)+\s*[A-Z]", stripped):
            depth = stripped.count(".")
            level = min(depth + 2, 5)
            processed.append(f"{'#' * level} {stripped}")
        
        # Roman numerals: I. II. III.
        elif re.match(r"^(I{1,3}|IV|V|VI{0,3}|IX|X)\.?\s+[A-Z]", stripped):
            processed.append(f"### {stripped}")
        
        # Letters: A. B. C.
        elif re.match(r"^[A-Z]\.\s+[A-Z]", stripped) and is_standalone:
            processed.append(f"#### {stripped}")
        
        # Short standalone lines that look like titles
        elif is_short and is_standalone and stripped[0].isupper() and not stripped.endswith((",", ".", ";", ":")):
            if len(stripped.split()) <= 6:
                processed.append(f"### {stripped}")
            else:
                processed.append(stripped)
        else:
            processed.append(stripped)
        
        prev_blank = False
    
    return "\n".join(processed)


def format_tables(text: str) -> str:
    """Attempt to detect and format simple tables."""
    lines = text.split("\n")
    processed = []
    table_buffer = []
    in_table = False
    
    for line in lines:
        # Detect table-like lines (multiple whitespace-separated columns)
        columns = re.split(r"\s{2,}", line.strip())
        
        if len(columns) >= 3 and all(len(c) < 50 for c in columns):
            if not in_table:
                in_table = True
                table_buffer = []
            table_buffer.append(columns)
        else:
            if in_table and len(table_buffer) >= 2:
                # Output collected table as markdown
                max_cols = max(len(row) for row in table_buffer)
                
                # Normalize column count
                for row in table_buffer:
                    while len(row) < max_cols:
                        row.append("")
                
                # Header row
                processed.append("| " + " | ".join(table_buffer[0]) + " |")
                processed.append("| " + " | ".join(["---"] * max_cols) + " |")
                
                # Data rows
                for row in table_buffer[1:]:
                    processed.append("| " + " | ".join(row) + " |")
                
                processed.append("")
            elif table_buffer:
                # Not enough rows for a table, output as-is
                for row in table_buffer:
                    processed.append("  ".join(row))
            
            in_table = False
            table_buffer = []
            processed.append(line)
    
    return "\n".join(processed)


def generate_toc(markdown: str) -> str:
    """Generate table of contents from markdown headings."""
    toc = ["## Table of Contents\n"]
    
    for line in markdown.split("\n"):
        match = re.match(r"^(#{2,5})\s+(.+)$", line)
        if match:
            level = len(match.group(1)) - 2
            title = match.group(2)
            # Create slug for anchor
            slug = re.sub(r"[^\w\s-]", "", title.lower())
            slug = re.sub(r"[\s_]+", "-", slug).strip("-")
            toc.append(f"{'  ' * level}- [{title}](#{slug})")
    
    if len(toc) > 1:
        toc.append("\n---\n")
        return "\n".join(toc)
    return ""


def pdf_to_markdown(
    client: OCRClient,
    pdf_path: Path,
    dpi: int = 250,
    prompt: Optional[str] = None,
    structured: bool = False,
    include_toc: bool = False,
    format_tables_flag: bool = False,
) -> str:
    """
    Convert PDF to Markdown.
    
    Args:
        client: OCRClient instance
        pdf_path: Path to PDF file
        dpi: Rendering resolution
        prompt: Optional extraction prompt
        structured: Apply heading detection
        include_toc: Generate table of contents
        format_tables_flag: Attempt to format tables
    
    Returns:
        Markdown string
    """
    print(f"Processing: {pdf_path.name}", file=sys.stderr)
    
    def progress(current, total):
        pct = int(current / total * 100)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"  [{bar}] {current}/{total} pages", file=sys.stderr, end="\r")
    
    result = client.ocr_pdf(str(pdf_path), dpi, prompt, progress_callback=progress)
    print(" " * 50, file=sys.stderr, end="\r")  # Clear progress
    
    # Build markdown
    parts = [f"# {pdf_path.stem}\n"]
    
    if result["page_count"] > 1:
        parts.append(f"*Converted from PDF • {result['page_count']} pages*\n")
    
    for page in result["pages"]:
        text = clean_text(page["text"])
        
        if structured:
            text = detect_headings(text)
        
        if format_tables_flag:
            text = format_tables(text)
        
        if result["page_count"] > 1:
            parts.append(f"\n## Page {page['page']}\n")
        
        parts.append(text)
        parts.append("")
    
    markdown = "\n".join(parts)
    
    # Add TOC after title
    if include_toc:
        toc = generate_toc(markdown)
        if toc:
            lines = markdown.split("\n", 3)
            markdown = f"{lines[0]}\n\n{toc}\n" + "\n".join(lines[1:])
    
    return markdown


def process_single(
    client: OCRClient,
    pdf_path: Path,
    output_path: Optional[Path],
    dpi: int,
    prompt: Optional[str],
    structured: bool,
    include_toc: bool,
    format_tables_flag: bool,
) -> None:
    """Process a single PDF file."""
    markdown = pdf_to_markdown(
        client, pdf_path, dpi, prompt, structured, include_toc, format_tables_flag
    )
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"Saved: {output_path}", file=sys.stderr)
    else:
        print(markdown)


def process_directory(
    client: OCRClient,
    input_dir: Path,
    output_dir: Path,
    dpi: int,
    prompt: Optional[str],
    structured: bool,
    include_toc: bool,
    format_tables_flag: bool,
) -> None:
    """Process all PDFs in a directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = sorted(input_dir.glob("*.pdf")) + sorted(input_dir.glob("*.PDF"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}", file=sys.stderr)
        return
    
    print(f"Found {len(pdf_files)} PDF files\n", file=sys.stderr)
    
    success = 0
    for pdf_path in pdf_files:
        output_path = output_dir / f"{pdf_path.stem}.md"
        
        try:
            markdown = pdf_to_markdown(
                client, pdf_path, dpi, prompt, structured, include_toc, format_tables_flag
            )
            output_path.write_text(markdown, encoding="utf-8")
            print(f"  ✓ {pdf_path.name} → {output_path.name}", file=sys.stderr)
            success += 1
        except Exception as e:
            print(f"  ✗ {pdf_path.name}: {e}", file=sys.stderr)
    
    print(f"\nCompleted: {success}/{len(pdf_files)} files", file=sys.stderr)
    print(f"Output: {output_dir}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDFs to Markdown using DeepInfra olmOCR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s report.pdf                    # Output to stdout
  %(prog)s report.pdf -o report.md       # Save to file
  %(prog)s report.pdf -o report.md --structured --toc
  %(prog)s ./pdfs/ -o ./markdown/        # Batch convert directory
  %(prog)s scan.pdf --dpi 300            # High-quality scan
  %(prog)s form.pdf -p "Extract form fields as structured data"
        """
    )
    
    parser.add_argument("input", type=Path, help="PDF file or directory")
    parser.add_argument("-o", "--output", type=Path, help="Output .md file or directory")
    parser.add_argument("--dpi", type=int, default=250, help="PDF DPI (default: 250)")
    parser.add_argument("-p", "--prompt", help="Custom extraction prompt")
    parser.add_argument(
        "--structured", "-s",
        action="store_true",
        help="Auto-detect headings and structure"
    )
    parser.add_argument(
        "--toc", "-t",
        action="store_true",
        help="Generate table of contents"
    )
    parser.add_argument(
        "--tables",
        action="store_true",
        help="Attempt to format tables as markdown"
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)
    
    client = OCRClient()
    
    if args.input.is_file():
        if args.input.suffix.lower() != ".pdf":
            print(f"Error: {args.input} is not a PDF file", file=sys.stderr)
            sys.exit(1)
        
        process_single(
            client, args.input, args.output, args.dpi,
            args.prompt, args.structured, args.toc, args.tables
        )
    
    elif args.input.is_dir():
        if not args.output:
            print("Error: Output directory required for batch processing (-o)", file=sys.stderr)
            sys.exit(1)
        
        process_directory(
            client, args.input, args.output, args.dpi,
            args.prompt, args.structured, args.toc, args.tables
        )


if __name__ == "__main__":
    main()
