# DeepInfra OCR Patterns: Batch Processing, Table Extraction, Structured Output

Advanced patterns for OCR workflows using DeepInfra's vision models.

## Model Selection Guide

### When to Use Each Model

| Model | Best For | Accuracy | Speed | Cost |
|-------|----------|----------|-------|------|
| **olmOCR-2** | PDFs, scans, mixed content | High (95%+) | Medium | Low |
| **DeepSeek-OCR** | High-res, compression, complex | Very High (97%+) | Fast | Medium |
| **NVIDIA Nemotron** | Financial docs, contracts | High (96%+) | Fast | Medium |
| **Qwen-VL** | General images, figures | High (95%+) | Very Fast | Low |

## Batch OCR Processing

### 1. Concurrent Batch Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json
from typing import List, Dict
import time

class BatchOCRProcessor:
    def __init__(self, api_key: str, model: str = "allenai/olmOCR-2"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.deepinfra.com/v1/openai/chat/completions"
        self.rate_limit_delay = 1.0  # seconds between requests

    def ocr_image(self, image_path: str) -> str:
        """Single image OCR with rate limiting."""
        time.sleep(self.rate_limit_delay)

        with open(image_path, "rb") as f:
            import base64
            b64 = base64.b64encode(f.read()).decode()

        # Detect MIME type
        ext = image_path.rsplit(".", 1)[-1].lower()
        mime_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
            "gif": "image/gif",
        }
        mime_type = mime_types.get(ext, "image/png")

        response = requests.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime_type};base64,{b64}"}
                            }
                        ]
                    }
                ]
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def process_batch(self, image_paths: List[str], max_workers: int = 3) -> List[Dict]:
        """Process multiple images concurrently."""
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.ocr_image, path): path for path in image_paths}

            for future in as_completed(futures):
                path = futures[future]
                try:
                    text = future.result()
                    results.append({
                        "path": path,
                        "text": text,
                        "status": "success",
                        "error": None
                    })
                except Exception as e:
                    results.append({
                        "path": path,
                        "text": None,
                        "status": "failed",
                        "error": str(e)
                    })

        return results

    def save_results(self, results: List[Dict], output_file: str):
        """Save batch results to JSON."""
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

# Usage
processor = BatchOCRProcessor("your-api-key")
results = processor.process_batch(["doc1.png", "doc2.jpg", "doc3.png"], max_workers=5)
processor.save_results(results, "ocr_results.json")
```

### 2. Batch Processing with Retry Logic

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustBatchOCR:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.max_retries = 3
        self.backoff_factor = 2

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def ocr_with_retry(self, image_path: str) -> str:
        """OCR with exponential backoff on rate limit."""
        # ... OCR call ...
        pass

    def process_folder(self, folder_path: str) -> Dict:
        """Process all images in folder with retry."""
        import os
        from pathlib import Path

        results = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "documents": []
        }

        image_files = list(Path(folder_path).glob("**/*.png")) + \
                      list(Path(folder_path).glob("**/*.jpg"))

        for idx, image_file in enumerate(image_files, 1):
            print(f"[{idx}/{len(image_files)}] Processing {image_file.name}...")

            try:
                text = self.ocr_with_retry(str(image_file))
                results["documents"].append({
                    "file": image_file.name,
                    "path": str(image_file),
                    "text": text,
                    "success": True
                })
                results["successful"] += 1
            except Exception as e:
                results["documents"].append({
                    "file": image_file.name,
                    "path": str(image_file),
                    "error": str(e),
                    "success": False
                })
                results["failed"] += 1

            results["total"] += 1

        return results
```

## Table Extraction and Conversion

### 1. Extract Tables as Markdown

```python
def ocr_table_to_markdown(image_path: str, api_key: str) -> str:
    """Extract table from image and convert to Markdown."""
    import base64
    import requests

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    response = requests.post(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "allenai/olmOCR-2",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"}
                        },
                        {
                            "type": "text",
                            "text": """Extract the table from this image and convert it to Markdown format.

Rules:
- Use standard Markdown table syntax (pipes and hyphens)
- Preserve column alignment
- Include headers if present
- Return ONLY the table, no additional text"""
                        }
                    ]
                }
            ]
        }
    )

    return response.json()["choices"][0]["message"]["content"]

# Usage
markdown_table = ocr_table_to_markdown("table.png", "api-key")
print(markdown_table)
```

### 2. Extract Tables as JSON

```python
import json

def ocr_table_to_json(image_path: str, api_key: str) -> dict:
    """Extract table and return as JSON."""
    import base64
    import requests

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    response = requests.post(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "allenai/olmOCR-2",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"}
                        },
                        {
                            "type": "text",
                            "text": """Extract this table and return as JSON.

Format:
{
  "headers": ["col1", "col2", ...],
  "rows": [
    ["val1", "val2", ...],
    ...
  ]
}

Return ONLY valid JSON, no markdown or explanation."""
                        }
                    ]
                }
            ]
        }
    )

    json_str = response.json()["choices"][0]["message"]["content"]
    # Extract JSON from response if wrapped in markdown
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0]

    return json.loads(json_str)

# Usage
table_data = ocr_table_to_json("table.png", "api-key")
print(json.dumps(table_data, indent=2))
```

## Structured Data Extraction

### 1. Invoice Extraction

```python
def extract_invoice(image_path: str, api_key: str) -> dict:
    """Extract structured invoice data."""
    import base64
    import requests
    import json

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    extraction_prompt = """Extract the following from this invoice and return as JSON:
    {
        "invoice_number": "string",
        "date": "YYYY-MM-DD",
        "vendor": {
            "name": "string",
            "address": "string",
            "email": "string"
        },
        "customer": {
            "name": "string",
            "address": "string"
        },
        "items": [
            {
                "description": "string",
                "quantity": number,
                "unit_price": number,
                "total": number
            }
        ],
        "subtotal": number,
        "tax": number,
        "total": number,
        "due_date": "YYYY-MM-DD"
    }

Return ONLY valid JSON."""

    response = requests.post(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "allenai/olmOCR-2",
            "max_tokens": 2048,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"}
                        },
                        {
                            "type": "text",
                            "text": extraction_prompt
                        }
                    ]
                }
            ]
        }
    )

    json_str = response.json()["choices"][0]["message"]["content"]
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0]

    return json.loads(json_str)

# Usage
invoice = extract_invoice("invoice.png", "api-key")
print(f"Invoice #{invoice['invoice_number']} - Total: ${invoice['total']}")
```

### 2. Form Field Extraction

```python
def extract_form_fields(image_path: str, api_key: str) -> dict:
    """Extract form field data."""
    import base64
    import requests
    import json

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    response = requests.post(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "allenai/olmOCR-2",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"}
                        },
                        {
                            "type": "text",
                            "text": """Extract all form fields and their values. Return as JSON:
{
    "fields": {
        "field_name": "field_value",
        ...
    }
}

Return ONLY valid JSON."""
                        }
                    ]
                }
            ]
        }
    )

    json_str = response.json()["choices"][0]["message"]["content"]
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0]

    return json.loads(json_str)
```

## Error Handling and Recovery

### Rate Limiting and Backoff

```python
import time
import random

class RateLimitedOCR:
    def __init__(self, api_key: str, rps: float = 0.5):
        """
        Initialize with requests per second limit.
        rps=0.5 means 1 request per 2 seconds.
        """
        self.api_key = api_key
        self.min_interval = 1.0 / rps
        self.last_request_time = 0

    def _wait_for_rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def ocr_with_backoff(self, image_path: str, max_retries: int = 3) -> str:
        """OCR with exponential backoff on failure."""
        import requests
        import base64

        for attempt in range(max_retries):
            self._wait_for_rate_limit()

            try:
                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()

                response = requests.post(
                    "https://api.deepinfra.com/v1/openai/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=60,
                    json={
                        "model": "allenai/olmOCR-2",
                        "max_tokens": 4096,
                        "messages": [{
                            "role": "user",
                            "content": [{
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64}"}
                            }]
                        }]
                    }
                )

                if response.status_code == 429:  # Rate limited
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]

            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt+1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Error on attempt {attempt+1}: {e}. Retrying...")
                time.sleep(2 ** attempt)

        raise Exception(f"Failed after {max_retries} attempts")
```

## Performance Optimization

### Image Preprocessing

```python
from PIL import Image
import numpy as np

def optimize_image_for_ocr(image_path: str, output_path: str, dpi: int = 200) -> str:
    """Optimize image for better OCR results."""
    img = Image.open(image_path)

    # 1. Increase DPI/resolution
    width, height = img.size
    new_width = int(width * dpi / 96)
    new_height = int(height * dpi / 96)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 2. Convert to grayscale (better for scans)
    img = img.convert("L")

    # 3. Increase contrast
    np_img = np.array(img)
    # Normalize to 0-255
    np_img = ((np_img - np_img.min()) / (np_img.max() - np_img.min()) * 255).astype(np.uint8)
    # Increase contrast
    np_img = np.clip(np_img * 1.2 - 20, 0, 255).astype(np.uint8)
    img = Image.fromarray(np_img)

    # 4. Remove noise (optional)
    img = img.filter(Image.SMOOTH)

    # 5. Threshold for cleaner results (if pure black & white)
    # img = img.point(lambda x: 0 if x < 128 else 255, '1')

    img.save(output_path, dpi=(dpi, dpi))
    return output_path

# Usage
optimized = optimize_image_for_ocr("scan.jpg", "scan_optimized.png", dpi=300)
```

## Logging and Monitoring

```python
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitoredOCR:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "total_tokens_used": 0,
            "start_time": datetime.now()
        }

    def ocr_image(self, image_path: str) -> str:
        """OCR with monitoring."""
        try:
            logger.info(f"Processing: {image_path}")
            # ... OCR call ...
            self.stats["successful"] += 1
            logger.info(f"Success: {image_path}")
        except Exception as e:
            self.stats["failed"] += 1
            logger.error(f"Failed: {image_path} - {str(e)}")
            raise
        finally:
            self.stats["total_requests"] += 1

    def print_stats(self):
        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
        success_rate = self.stats["successful"] / self.stats["total_requests"] * 100 if self.stats["total_requests"] > 0 else 0

        logger.info(f"""
OCR Statistics:
- Total: {self.stats['total_requests']}
- Successful: {self.stats['successful']}
- Failed: {self.stats['failed']}
- Success Rate: {success_rate:.1f}%
- Duration: {elapsed:.1f}s
        """)
```

## References

- DeepInfra API: https://deepinfra.com/docs/
- olmOCR-2: https://deepinfra.com/allenai/olmOCR-2/api
- DeepSeek-OCR: https://deepinfra.com/deepseek-ai/DeepSeek-OCR/api
- Pillow (image processing): https://pillow.readthedocs.io/
