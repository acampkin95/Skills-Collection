#!/usr/bin/env python3
"""
DeepInfra olmOCR Batch Processing

Process multiple images or PDFs with parallel execution and progress tracking.

Usage:
    python ocr_batch.py <input> [options]
    
Examples:
    python ocr_batch.py document.pdf -o result.txt
    python ocr_batch.py ./images/ -o results.json -f json
    python ocr_batch.py ./scans/ -o ./output/ -f markdown --parallel 4
    python ocr_batch.py invoice.png -p "Extract as JSON: invoice_number, date, total"
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from deepinfra_ocr import OCRClient, ocr_image, ocr_pdf

SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".tif"}


def process_image(
    client: OCRClient,
    image_path: Path,
    prompt: Optional[str] = None,
) -> dict:
    """Process a single image file."""
    try:
        text = client.ocr_image(image_path, prompt)
        return {
            "file": image_path.name,
            "path": str(image_path),
            "type": "image",
            "text": text,
            "error": None
        }
    except Exception as e:
        return {
            "file": image_path.name,
            "path": str(image_path),
            "type": "image",
            "text": None,
            "error": str(e)
        }


def process_pdf(
    client: OCRClient,
    pdf_path: Path,
    dpi: int = 200,
    prompt: Optional[str] = None,
) -> dict:
    """Process a PDF file."""
    try:
        def progress(current, total):
            print(f"  Page {current}/{total}", file=sys.stderr, end="\r")
        
        result = client.ocr_pdf(pdf_path, dpi, prompt, progress_callback=progress)
        print(" " * 20, file=sys.stderr, end="\r")  # Clear progress line
        
        return {
            "file": pdf_path.name,
            "path": str(pdf_path),
            "type": "pdf",
            "pages": result["pages"],
            "page_count": result["page_count"],
            "error": None
        }
    except Exception as e:
        return {
            "file": pdf_path.name,
            "path": str(pdf_path),
            "type": "pdf",
            "pages": None,
            "error": str(e)
        }


def collect_files(input_path: Path) -> list[Path]:
    """Collect all processable files from input path."""
    if input_path.is_file():
        return [input_path]
    
    files = []
    for ext in SUPPORTED_IMAGES | {".pdf"}:
        files.extend(input_path.glob(f"*{ext}"))
        files.extend(input_path.glob(f"*{ext.upper()}"))
    
    return sorted(set(files))


def format_as_text(results: list[dict]) -> str:
    """Format results as plain text."""
    output = []
    for r in results:
        if r.get("error"):
            output.append(f"=== ERROR: {r['file']} ===\n{r['error']}\n")
            continue
        
        if r["type"] == "pdf":
            output.append(f"=== {r['file']} ({r['page_count']} pages) ===\n")
            for page in r["pages"]:
                output.append(f"--- Page {page['page']} ---\n{page['text']}\n")
        else:
            output.append(f"=== {r['file']} ===\n{r['text']}\n")
    
    return "\n".join(output)


def format_as_markdown(results: list[dict]) -> str:
    """Format results as Markdown."""
    output = ["# OCR Results\n"]
    
    for r in results:
        if r.get("error"):
            output.append(f"## ❌ {r['file']}\n\n**Error:** {r['error']}\n")
            continue
        
        if r["type"] == "pdf":
            output.append(f"## 📄 {r['file']}\n\n*{r['page_count']} pages*\n")
            for page in r["pages"]:
                output.append(f"### Page {page['page']}\n\n{page['text']}\n")
        else:
            output.append(f"## 🖼️ {r['file']}\n\n{r['text']}\n")
    
    return "\n".join(output)


def format_as_json(results: list[dict]) -> str:
    """Format results as JSON."""
    return json.dumps({"results": results}, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Batch OCR images and PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan.png                      # OCR single image to stdout
  %(prog)s document.pdf -o doc.txt       # OCR PDF to text file
  %(prog)s ./images/ -o results.json -f json
  %(prog)s ./pdfs/ -o ./markdown/ -f markdown --parallel 2
  %(prog)s invoice.png -p "Extract: invoice_number, date, total as JSON"
        """
    )
    
    parser.add_argument("input", type=Path, help="Image, PDF, or directory")
    parser.add_argument("-o", "--output", type=Path, help="Output file or directory")
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument("-p", "--prompt", help="Custom extraction prompt")
    parser.add_argument("--dpi", type=int, default=200, help="PDF DPI (default: 200)")
    parser.add_argument(
        "--parallel", type=int, default=1,
        help="Parallel workers for images (default: 1)"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress")
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)
    
    # Collect files
    files = collect_files(args.input)
    if not files:
        print(f"No supported files found in {args.input}", file=sys.stderr)
        sys.exit(1)
    
    if not args.quiet:
        print(f"Processing {len(files)} file(s)...", file=sys.stderr)
    
    # Process files
    client = OCRClient()
    results = []
    start_time = time.time()
    
    # Separate PDFs and images
    pdfs = [f for f in files if f.suffix.lower() == ".pdf"]
    images = [f for f in files if f.suffix.lower() in SUPPORTED_IMAGES]
    
    # Process PDFs sequentially (they have internal parallelism)
    for pdf_path in pdfs:
        if not args.quiet:
            print(f"📄 {pdf_path.name}", file=sys.stderr)
        results.append(process_pdf(client, pdf_path, args.dpi, args.prompt))
    
    # Process images with optional parallelism
    if images:
        if args.parallel > 1 and len(images) > 1:
            if not args.quiet:
                print(f"Processing {len(images)} images with {args.parallel} workers...", file=sys.stderr)
            
            with ThreadPoolExecutor(max_workers=args.parallel) as executor:
                futures = {
                    executor.submit(process_image, client, img, args.prompt): img
                    for img in images
                }
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    if not args.quiet:
                        status = "✓" if not result["error"] else "✗"
                        print(f"  {status} {result['file']}", file=sys.stderr)
        else:
            for img_path in images:
                if not args.quiet:
                    print(f"🖼️  {img_path.name}", file=sys.stderr, end=" ")
                result = process_image(client, img_path, args.prompt)
                results.append(result)
                if not args.quiet:
                    status = "✓" if not result["error"] else "✗"
                    print(status, file=sys.stderr)
    
    # Sort results by original file order
    file_order = {f: i for i, f in enumerate(files)}
    results.sort(key=lambda r: file_order.get(Path(r["path"]), 999))
    
    # Format output
    if args.format == "json":
        output = format_as_json(results)
    elif args.format == "markdown":
        output = format_as_markdown(results)
    else:
        output = format_as_text(results)
    
    # Write output
    if args.output:
        if args.output.suffix:
            # Output is a file
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        else:
            # Output is a directory - write individual files
            args.output.mkdir(parents=True, exist_ok=True)
            ext = {"json": ".json", "markdown": ".md", "text": ".txt"}[args.format]
            output_file = args.output / f"ocr_results{ext}"
            output_file.write_text(output, encoding="utf-8")
        
        if not args.quiet:
            print(f"\nOutput: {args.output}", file=sys.stderr)
    else:
        print(output)
    
    # Summary
    elapsed = time.time() - start_time
    errors = sum(1 for r in results if r.get("error"))
    if not args.quiet:
        print(f"\nCompleted: {len(results) - errors}/{len(results)} files in {elapsed:.1f}s", file=sys.stderr)
        if errors:
            print(f"Errors: {errors}", file=sys.stderr)


if __name__ == "__main__":
    main()
