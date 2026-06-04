#!/usr/bin/env python3
"""
DeepInfra olmOCR Client

Extract text from images and PDFs using DeepInfra's olmOCR-2-7B-1025 model.

Usage:
    from deepinfra_ocr import ocr_image, ocr_pdf, ocr_url, pdf_to_markdown
    
    text = ocr_image("document.png")
    result = ocr_pdf("report.pdf")
    markdown = pdf_to_markdown("report.pdf", "report.md")
    text = ocr_url("https://example.com/image.png")
    
    # With custom prompt
    text = ocr_image("invoice.png", prompt="Extract as JSON: invoice number, date, total")
    
    # Async batch processing
    results = await ocr_images_async(["img1.png", "img2.png", "img3.png"])
"""

import asyncio
import base64
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from typing import Callable, Optional, Union

import requests

# ============================================================================
# Configuration
# ============================================================================

API_KEY = os.getenv("DEEPINFRA_API_KEY", "")
API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
MODEL = "allenai/olmOCR-2-7B-1025"

DEFAULT_MAX_TOKENS = 4096
DEFAULT_TIMEOUT = 120
DEFAULT_DPI = 200
MAX_RETRIES = 3
RETRY_DELAY = 2.0

MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}


# ============================================================================
# Exceptions
# ============================================================================

class OCRError(Exception):
    """Base exception for OCR operations."""
    pass


class APIError(OCRError):
    """API request failed."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RateLimitError(APIError):
    """Rate limit exceeded."""
    pass


# ============================================================================
# OCR Client
# ============================================================================

class OCRClient:
    """Client for DeepInfra olmOCR API with retry and error handling."""

    def __init__(
        self,
        api_key: str = API_KEY,
        base_url: str = API_URL,
        model: str = MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        retry_delay: float = RETRY_DELAY,
    ) -> None:
        """Initialize OCRClient with API configuration.

        Args:
            api_key: DeepInfra API key (from DEEPINFRA_API_KEY env var or constructor).
                     If empty, will raise APIError on first request.
            base_url: API endpoint URL.
            model: Model name for OCR (default: allenai/olmOCR-2-7B-1025).
            max_tokens: Maximum tokens per response.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts for failed requests.
            retry_delay: Base delay in seconds for exponential backoff.

        Raises:
            APIError: If API key is empty and cannot be loaded from environment.
        """
        if not api_key:
            raise APIError("API key required: set DEEPINFRA_API_KEY environment variable")

        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session: Optional[requests.Session] = None
    
    @property
    def session(self) -> requests.Session:
        """Lazy-loaded requests session."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            })
        return self._session
    
    def _make_request(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
    ) -> str:
        """Make API request with retry logic."""
        content = [{"type": "image_url", "image_url": {"url": image_url}}]
        if prompt:
            content.append({"type": "text", "text": prompt})
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": content}]
        }
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 429:
                    wait_time = self.retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                
                if response.status_code >= 400:
                    error_data = response.json() if response.text else {}
                    raise APIError(
                        f"API error: {response.status_code}",
                        status_code=response.status_code,
                        response=error_data
                    )
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
            except requests.exceptions.Timeout:
                last_error = OCRError(f"Request timeout after {self.timeout}s")
                time.sleep(self.retry_delay)
            except requests.exceptions.RequestException as e:
                last_error = OCRError(f"Request failed: {e}")
                time.sleep(self.retry_delay)
        
        raise last_error or OCRError("Max retries exceeded")
    
    def ocr_bytes(
        self,
        image_bytes: bytes,
        media_type: str = "image/png",
        prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """OCR raw image bytes."""
        b64 = base64.b64encode(image_bytes).decode()
        return self._make_request(f"data:{media_type};base64,{b64}", prompt, max_tokens)
    
    def ocr_url(
        self,
        url: str,
        prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """OCR an image from URL."""
        return self._make_request(url, prompt, max_tokens)
    
    def ocr_image(
        self,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """OCR a local image file."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        
        media_type = MEDIA_TYPES.get(path.suffix.lower(), "image/png")
        with open(path, "rb") as f:
            return self.ocr_bytes(f.read(), media_type, prompt, max_tokens)
    
    def ocr_pdf(
        self,
        pdf_path: Union[str, Path],
        dpi: int = DEFAULT_DPI,
        prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> dict:
        """
        OCR all pages of a PDF.
        
        Args:
            pdf_path: Path to PDF file
            dpi: Rendering resolution (200-300 recommended)
            prompt: Optional extraction instructions
            max_tokens: Max tokens per page
            progress_callback: Optional callback(current_page, total_pages)
        
        Returns:
            dict with keys: pages, full_text, page_count
        """
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError("pdf2image required: pip install pdf2image")
        
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")
        
        images = convert_from_path(str(path), dpi=dpi)
        pages = []
        
        for i, img in enumerate(images):
            if progress_callback:
                progress_callback(i + 1, len(images))
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            text = self.ocr_bytes(buffer.getvalue(), "image/png", prompt, max_tokens)
            pages.append({"page": i + 1, "text": text})
            
            # Rate limiting between pages
            if i < len(images) - 1:
                time.sleep(1.0)
        
        full_text = "\n\n".join(p["text"] for p in pages)
        
        return {
            "pages": pages,
            "full_text": full_text,
            "page_count": len(pages)
        }
    
    def ocr_images_parallel(
        self,
        image_paths: list[Union[str, Path]],
        max_workers: int = 4,
        prompt: Optional[str] = None,
    ) -> list[dict]:
        """
        OCR multiple images in parallel.
        
        Returns:
            List of dicts with keys: path, text, error (if failed)
        """
        results = []
        
        def process_one(path):
            try:
                text = self.ocr_image(path, prompt)
                return {"path": str(path), "text": text, "error": None}
            except Exception as e:
                return {"path": str(path), "text": None, "error": str(e)}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_one, p): p for p in image_paths}
            for future in as_completed(futures):
                results.append(future.result())
        
        return sorted(results, key=lambda x: image_paths.index(Path(x["path"])))


# ============================================================================
# Async Client
# ============================================================================

class AsyncOCRClient:
    """Async client for batch processing."""
    
    def __init__(self, client: Optional[OCRClient] = None):
        self.client = client or OCRClient()
    
    async def ocr_image(
        self,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
    ) -> str:
        """Async OCR for single image."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.client.ocr_image(image_path, prompt)
        )
    
    async def ocr_images(
        self,
        image_paths: list[Union[str, Path]],
        prompt: Optional[str] = None,
        concurrency: int = 4,
    ) -> list[dict]:
        """
        OCR multiple images concurrently.
        
        Returns:
            List of dicts with keys: path, text, error
        """
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_one(path):
            async with semaphore:
                try:
                    text = await self.ocr_image(path, prompt)
                    return {"path": str(path), "text": text, "error": None}
                except Exception as e:
                    return {"path": str(path), "text": None, "error": str(e)}
        
        tasks = [process_one(p) for p in image_paths]
        return await asyncio.gather(*tasks)


# ============================================================================
# Module-level convenience functions
# ============================================================================

try:
    _client = OCRClient()
    _async_client = AsyncOCRClient(_client)
except APIError:
    # API key not configured; lazy initialization on first use
    _client = None
    _async_client = None


def _get_client() -> OCRClient:
    """Get or create the module-level OCR client.

    Raises:
        APIError: If API key is not configured.
    """
    global _client
    if _client is None:
        _client = OCRClient()
    return _client


def ocr_image(
    image_path: Union[str, Path],
    prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """OCR a local image file.

    Args:
        image_path: Path to image file.
        prompt: Optional custom extraction prompt.
        max_tokens: Optional max tokens for response.

    Returns:
        Extracted text from image.

    Raises:
        FileNotFoundError: If image file not found.
        APIError: If API request fails.
    """
    return _get_client().ocr_image(image_path, prompt, max_tokens)


def ocr_url(
    url: str,
    prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """OCR an image from URL.

    Args:
        url: Image URL.
        prompt: Optional custom extraction prompt.
        max_tokens: Optional max tokens for response.

    Returns:
        Extracted text from image.

    Raises:
        APIError: If API request fails.
    """
    return _get_client().ocr_url(url, prompt, max_tokens)


def ocr_bytes(
    image_bytes: bytes,
    media_type: str = "image/png",
    prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """OCR raw image bytes.

    Args:
        image_bytes: Raw image data.
        media_type: MIME type of image (e.g., 'image/png').
        prompt: Optional custom extraction prompt.
        max_tokens: Optional max tokens for response.

    Returns:
        Extracted text from image.

    Raises:
        APIError: If API request fails.
    """
    return _get_client().ocr_bytes(image_bytes, media_type, prompt, max_tokens)


def ocr_pdf(
    pdf_path: Union[str, Path],
    dpi: int = DEFAULT_DPI,
    prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> dict:
    """OCR all pages of a PDF.

    Args:
        pdf_path: Path to PDF file.
        dpi: Rendering resolution in dots per inch (200-300 recommended).
        prompt: Optional custom extraction instructions for each page.
        max_tokens: Optional max tokens per page response.
        progress_callback: Optional callback function to track progress.
                          Called with (current_page, total_pages).

    Returns:
        Dictionary with keys:
        - pages: List of dicts with 'page' (int) and 'text' (str) keys
        - full_text: Concatenated text from all pages
        - page_count: Total number of pages processed

    Raises:
        FileNotFoundError: If PDF file not found.
        ImportError: If pdf2image package not installed.
        APIError: If API request fails.
    """
    return _get_client().ocr_pdf(pdf_path, dpi, prompt, max_tokens, progress_callback)


def pdf_to_markdown(
    pdf_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    dpi: int = 250,
    prompt: Optional[str] = None,
) -> str:
    """
    Convert PDF to Markdown.
    
    Args:
        pdf_path: Path to input PDF
        output_path: Optional path to save .md file
        dpi: PDF rendering resolution
        prompt: Optional extraction instructions
    
    Returns:
        Markdown string
    """
    path = Path(pdf_path)
    result = _client.ocr_pdf(path, dpi, prompt)
    
    lines = [f"# {path.stem}\n"]
    
    if result["page_count"] > 1:
        lines.append(f"*{result['page_count']} pages*\n")
    
    for page in result["pages"]:
        if result["page_count"] > 1:
            lines.append(f"\n## Page {page['page']}\n")
        lines.append(page["text"])
        lines.append("")
    
    markdown = "\n".join(lines)
    
    if output_path:
        Path(output_path).write_text(markdown, encoding="utf-8")
    
    return markdown


def ocr_images_parallel(
    image_paths: list[Union[str, Path]],
    max_workers: int = 4,
    prompt: Optional[str] = None,
) -> list[dict]:
    """OCR multiple images in parallel using thread pool.

    Args:
        image_paths: List of paths to image files.
        max_workers: Maximum number of concurrent worker threads (default: 4).
        prompt: Optional custom extraction instructions for all images.

    Returns:
        List of dicts with keys:
        - path: Original image path (str)
        - text: Extracted text (str) or None if failed
        - error: Error message (str) or None if successful

    Raises:
        FileNotFoundError: If any image file not found.
        APIError: If API request fails.
    """
    return _get_client().ocr_images_parallel(image_paths, max_workers, prompt)


async def ocr_images_async(
    image_paths: list[Union[str, Path]],
    prompt: Optional[str] = None,
    concurrency: int = 4,
) -> list[dict]:
    """OCR multiple images asynchronously with concurrency control.

    Args:
        image_paths: List of paths to image files.
        prompt: Optional custom extraction instructions for all images.
        concurrency: Maximum concurrent requests (default: 4).

    Returns:
        List of dicts with keys:
        - path: Original image path (str)
        - text: Extracted text (str) or None if failed
        - error: Error message (str) or None if successful

    Raises:
        FileNotFoundError: If any image file not found.
        APIError: If API request fails.
    """
    client = _get_client()
    async_client = AsyncOCRClient(client)
    return await async_client.ocr_images(image_paths, prompt, concurrency)


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    import json
    import sys
    
    parser = argparse.ArgumentParser(description="OCR images and PDFs")
    parser.add_argument("input", help="Image or PDF file")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("-p", "--prompt", help="Custom extraction prompt")
    parser.add_argument("--dpi", type=int, default=200, help="PDF DPI")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    path = Path(args.input)
    
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        if path.suffix.lower() == ".pdf":
            result = ocr_pdf(path, args.dpi, args.prompt)
            output = json.dumps(result, indent=2) if args.json else result["full_text"]
        else:
            text = ocr_image(path, args.prompt)
            output = json.dumps({"text": text}) if args.json else text
        
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"Saved to {args.output}", file=sys.stderr)
        else:
            print(output)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
