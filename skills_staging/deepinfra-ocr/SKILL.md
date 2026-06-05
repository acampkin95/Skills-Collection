---
name: deepinfra-ocr
description: DeepInfra vision-language model OCR, for extracting text from PDFs, scanned documents, images.
---

# DeepInfra OCR — Document Text Extraction

Extract text from PDFs, images, scanned documents, handwritten notes, tables, and forms using DeepInfra's vision-language models (olmOCR-2, DeepSeek-OCR, Nemotron).

## Quick Reference

```python
# Import the module
from deepinfra_ocr import ocr_image, ocr_pdf, ocr_url, pdf_to_markdown

# Single image
text = ocr_image("scan.png")

# PDF (returns dict with pages and full_text)
result = ocr_pdf("document.pdf")

# PDF to Markdown file
pdf_to_markdown("report.pdf", "report.md")

# Image from URL
text = ocr_url("https://example.com/image.png")
```

**CLI tools:**
```bash
python scripts/ocr_batch.py ./scans/ -o results.json
python scripts/pdf_to_markdown.py report.pdf -o report.md --structured --toc
```

## Configuration

```python
import os
API_KEY = os.environ["DEEPINFRA_API_KEY"]  # Never hardcode — source from env
API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
MODEL = "allenai/olmOCR-2-7B-1025"  # Default; also supports deepseek-ai/DeepSeek-OCR, nvidia/Nemotron
```

Set the environment variable before use:
```bash
export DEEPINFRA_API_KEY="your-key-here"
```

## Core Workflows

### 1. Image OCR (Base64 and URL-based)

```python
import base64
import requests

def ocr_image(image_path: str) -> str:
    """Extract text from image file."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    ext = image_path.rsplit(".", 1)[-1].lower()
    media = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")

    r = requests.post(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['DEEPINFRA_API_KEY']}"},
        json={
            "model": "allenai/olmOCR-2-7B-1025",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:{media};base64,{b64}"}}
            ]}]
        }
    )
    return r.json()["choices"][0]["message"]["content"]

def ocr_url_image(image_url: str) -> str:
    """Extract text from image URL (no base64 conversion needed)."""
    r = requests.post(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['DEEPINFRA_API_KEY']}"},
        json={
            "model": "allenai/olmOCR-2-7B-1025",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": image_url}}
            ]}]
        }
    )
    return r.json()["choices"][0]["message"]["content"]
```

### 2. PDF OCR (Multi-page Processing)

```python
from pdf2image import convert_from_path
from io import BytesIO
import asyncio
from concurrent.futures import ThreadPoolExecutor

def ocr_pdf(pdf_path: str, dpi: int = 200) -> dict:
    """OCR all pages of a PDF."""
    images = convert_from_path(pdf_path, dpi=dpi)
    pages = []

    for i, img in enumerate(images):
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        r = requests.post(
            "https://api.deepinfra.com/v1/openai/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['DEEPINFRA_API_KEY']}"},
            json={
                "model": "allenai/olmOCR-2-7B-1025",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]}]
            }
        )
        pages.append({"page": i + 1, "text": r.json()["choices"][0]["message"]["content"]})

    return {"pages": pages, "full_text": "\n\n".join(p["text"] for p in pages)}
```

### 3. Batch Processing with Concurrency

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def ocr_batch(image_paths: list[str], max_workers: int = 3) -> list[dict]:
    """Process multiple images with rate limiting."""
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for idx, path in enumerate(image_paths):
            # Rate limiting: 1-2 second delay between requests
            time.sleep(1)
            future = executor.submit(ocr_image, path)
            futures[future] = path

        for future in as_completed(futures):
            path = futures[future]
            try:
                text = future.result()
                results.append({"path": path, "text": text, "error": None})
            except Exception as e:
                results.append({"path": path, "text": None, "error": str(e)})

    return results
```

### 4. Error Handling with Exponential Backoff

```python
import time

def ocr_with_retry(image_path: str, max_retries: int = 3) -> str:
    """OCR with exponential backoff on rate limits."""
    for attempt in range(max_retries):
        try:
            return ocr_image(image_path)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")
```

### 5. Structured Data Extraction (JSON)

```python
def ocr_with_prompt(image_path: str, instruction: str) -> str:
    """OCR with custom extraction instructions."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    r = requests.post(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['DEEPINFRA_API_KEY']}"},
        json={
            "model": "allenai/olmOCR-2-7B-1025",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": instruction}
            ]}]
        }
    )
    return r.json()["choices"][0]["message"]["content"]

# Examples
invoice_json = ocr_with_prompt(
    "invoice.png",
    "Extract invoice number, date, total amount, line items as JSON"
)
form_data = ocr_with_prompt(
    "form.png",
    "Extract all form fields and their values as JSON"
)
table_md = ocr_with_prompt(
    "table.png",
    "Convert this table to markdown format"
)
```

### 6. PDF to Markdown Conversion

```bash
# Basic conversion
python scripts/pdf_to_markdown.py document.pdf -o document.md

# With auto-detected headings and table of contents
python scripts/pdf_to_markdown.py document.pdf -o document.md --structured --toc

# Batch convert folder
python scripts/pdf_to_markdown.py ./pdfs/ -o ./markdown/

# High quality (slower, 300 DPI)
python scripts/pdf_to_markdown.py scan.pdf -o scan.md --dpi 300
```

## Image Optimization Before OCR

```python
from PIL import Image
import numpy as np

def optimize_image_for_ocr(image_path: str, output_path: str, dpi: int = 200):
    """Optimize image for better OCR results."""
    img = Image.open(image_path)

    # Resize to increase DPI/resolution
    width, height = img.size
    img = img.resize((int(width * dpi / 96), int(height * dpi / 96)), Image.Resampling.LANCZOS)

    # Convert to grayscale (improves OCR for scans)
    img = img.convert('L')

    # Increase contrast (helps with faded documents)
    np_img = np.array(img)
    np_img = np.clip(np_img * 1.5, 0, 255).astype(np.uint8)
    img = Image.fromarray(np_img)

    img.save(output_path)
    return output_path
```

## Scripts Reference

| Script | Purpose | Example |
|--------|---------|---------|
| `deepinfra_ocr.py` | Python module | `from deepinfra_ocr import ocr_pdf` |
| `ocr_batch.py` | Batch processing CLI | `python ocr_batch.py ./images/ -o out.json` |
| `pdf_to_markdown.py` | PDF→MD conversion | `python pdf_to_markdown.py doc.pdf -o doc.md` |

## API Reference

**Key parameters:**
- `max_tokens`: Up to 16384 (default 4096)
- `temperature`: 0-2 (default 1.0, use 0.1-0.3 for consistent OCR)

**Pricing:** $0.09/1M input tokens, $0.19/1M output tokens

## Best Practices

1. **DPI selection**: 200 for clean documents, 250-300 for scans/handwriting
2. **Rate limiting**: 1-2 second delay between requests to avoid 429 errors
3. **Large PDFs**: Process in parallel with `concurrent.futures.ThreadPoolExecutor`
4. **Error handling**: Implement retry with exponential backoff (2^n seconds)
5. **Structured output**: Use custom prompts for JSON/table extraction
6. **Image optimization**: Increase DPI, convert to grayscale, normalize contrast before sending
7. **Batch processing**: Group similar documents together, process with concurrency limits
