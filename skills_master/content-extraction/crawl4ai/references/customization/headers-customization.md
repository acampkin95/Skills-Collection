# Headers Customization

Custom HTTP headers for requests.

## Default Headers

```python
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}
```

## Header Manager

```python
from typing import Dict
from urllib.parse import urlparse

class HeaderManager:
    def __init__(self, base_headers: Dict = None):
        self.headers = base_headers or DEFAULT_HEADERS.copy()

    def get(self, url: str = None) -> Dict:
        """Get headers with dynamic Referer."""
        headers = self.headers.copy()

        if url:
            parsed = urlparse(url)
            headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"

        return headers

    def with_auth(self, token: str, type: str = "Bearer") -> "HeaderManager":
        self.headers["Authorization"] = f"{type} {token}"
        return self

    def with_cookies(self, cookies: Dict) -> "HeaderManager":
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        self.headers["Cookie"] = cookie_str
        return self
```

## Usage

```python
from crawl4ai import BrowserConfig

headers = HeaderManager().with_auth("token").get()

config = BrowserConfig(
    headless=True,
    headers=headers,
)
```
