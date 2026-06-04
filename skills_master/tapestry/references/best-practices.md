# Content Extraction Best Practices

## URL Processing Strategies

### 1. Content Type Detection

```python
CONTENT_TYPES = {
    "youtube.com": "video",
    "youtu.be": "video",
    "pdf": "document",
    "github.com": "code",
    "medium.com": "article",
    "news.ycombinator.com": "discussion",
}

def detect_content_type(url: str) -> str:
    for pattern, type_name in CONTENT_TYPES.items():
        if pattern in url.lower():
            return type_name
    return "webpage"
```

### 2. Extraction Strategy Selection

| Content Type | Strategy | Tools |
|--------------|----------|-------|
| YouTube | Transcript API | youtube-transcript |
| PDF | Text extraction | PyPDF2, pdfplumber |
| GitHub | Repository API | gh CLI, PyGithub |
| Article | HTML parsing | BeautifulSoup, lxml |
| Code | Syntax analysis | Tree-sitter, regex |

### 3. Rate Limiting

```python
import asyncio
from datetime import datetime

class RateLimiter:
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = []

    async def wait(self):
        now = datetime.now()
        self.requests = [t for t in self.requests if (now - t).seconds < self.window]

        if len(self.requests) >= self.max_requests:
            wait_time = self.window - (now - self.requests[0]).seconds
            await asyncio.sleep(wait_time)

        self.requests.append(datetime.now())
```

### 4. Content Validation

```python
def validate_content(content: dict) -> bool:
    """Validate extracted content meets quality standards."""
    if not content.get("text"):
        return False

    if len(content["text"]) < 100:  # Too short
        return False

    if not content.get("title"):
        return False

    return True
```

### 5. Error Handling

```python
class ExtractionError(Exception):
    pass

async def safe_extract(url: str) -> dict:
    try:
        return await extract_content(url)
    except TimeoutError:
        raise ExtractionError(f"Timeout extracting {url}")
    except ConnectionError:
        raise ExtractionError(f"Connection failed for {url}")
    except Exception as e:
        raise ExtractionError(f"Unexpected error: {e}")
```

### 6. Output Formats

| Format | Use Case | Example |
|--------|----------|---------|
| Markdown | Documentation | `extract_and_plan <url> --format md` |
| JSON | API integration | `extract_and_plan <url> --format json` |
| YAML | Configuration | `extract_and_plan <url> --format yaml` |
| Action Plan | Task tracking | `extract_and_plan <url> --format plan` |
