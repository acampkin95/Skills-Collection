# Crawl4AI Extraction Customization

Custom extractors, LLM prompt optimization, and advanced configuration.

## Custom Extraction Strategies

### Building Custom Extractors

```python
from crawl4ai import CrawlerRunConfig
from crawl4ai.extraction_strategy import ExtractionStrategy
from bs4 import BeautifulSoup
from typing import Any, Dict, Optional

class CustomExtractionStrategy(ExtractionStrategy):
    """
    Custom extraction strategy for specialized data extraction.
    """

    def __init__(self, extractors: list):
        """
        Initialize with list of extractor functions.

        Each extractor: (selector: str, type: str, options: dict) -> Any
        """
        self.extractors = extractors

    def extract(
        self,
        html: str,
        url: str = None,
        extra: Dict = None
    ) -> Dict[str, Any]:
        """Extract data from HTML using configured extractors."""
        soup = BeautifulSoup(html, "html.parser")
        results = {}

        for selector, field_type, options in self.extractors:
            elements = soup.select(selector)

            if field_type == "text":
                results[options["name"]] = [
                    el.get_text(strip=True) for el in elements
                ]
            elif field_type == "attribute":
                attr = options.get("attribute", "href")
                results[options["name"]] = [
                    el.get(attr, "") for el in elements
                ]
            elif field_type == "html":
                results[options["name"]] = [
                    str(el) for el in elements
                ]
            elif field_type == "count":
                results[options["name"]] = len(elements)

        return results

    def run(self, url, html, *args, **kwargs) -> Any:
        """Required by ExtractionStrategy interface."""
        return self.extract(html, url)


# Usage
extractors = [
    (".product-title", "text", {"name": "titles"}),
    (".product-price", "text", {"name": "prices"}),
    (".product-image img", "attribute", {"name": "images", "attribute": "src"}),
    (".product-card", "count", {"name": "total_products"}),
]

config = CrawlerRunConfig(
    extraction_strategy=CustomExtractionStrategy(extractors)
)
```

### LLM-Based Custom Extraction

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from typing import List, Dict, Any

class StructuredLLMExtractor(LLMExtractionStrategy):
    """
    LLM-based extraction with structured output.
    """

    def __init__(
        self,
        provider: str = "openai/gpt-4o-mini",
        schema: Dict = None,
        system_prompt: str = None,
    ):
        self.schema = schema or {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}},
                "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
            }
        }

        full_prompt = f"""
        Extract structured information from the content.

        Return JSON matching this schema:
        {self.schema}

        Content to analyze:
        {{markdown}}
        """

        super().__init__(
            provider=provider,
            instruction=full_prompt,
        )

    def extract(self, markdown: str) -> Dict[str, Any]:
        """Extract with schema enforcement."""
        result = self.run(markdown=markdown)

        try:
            import json
            return json.loads(result.extracted_content)
        except:
            return {"raw": result.extracted_content}
```

---

## Prompt Engineering for LLM Extraction

### Optimized Prompts

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ExtractionPrompt:
    """Optimized prompt for LLM extraction."""
    system_prompt: str
    user_template: str
    examples: List[dict]
    temperature: float = 0.0
    max_tokens: int = 4096

PROMPTS = {
    "product_extraction": ExtractionPrompt(
        system_prompt="""You are a data extraction expert. Your task is to extract
product information from web content accurately and consistently. Return only
valid JSON without any additional text or explanations.""",

        user_template="""Extract the following product information from this page:

        Required fields:
        - name: Full product name
        - price: Current price with currency
        - description: Product description or summary
        - availability: In stock, out of stock, or limited
        - rating: Average customer rating (0-5) if available

        Content:
        {markdown}

        Return JSON in this format:
        {{
            "name": "...",
            "price": "...",
            "description": "...",
            "availability": "...",
            "rating": null
        }}""",

        examples=[
            {
                "input": "Product page content...",
                "output": {"name": "Widget Pro", "price": "$99.99", ...}
            }
        ],
    ),

    "article_extraction": ExtractionPrompt(
        system_prompt="You are an article extraction specialist. Extract key information from news articles and blog posts.",

        user_template="""Extract article metadata and key information:

        Required fields:
        - title: Article headline
        - author: Author name(s)
        - publish_date: Publication date
        - summary: Brief summary (2-3 sentences)
        - topics: Main topics covered

        Content:
        {markdown}""",

        examples=[],
    ),

    "contact_extraction": ExtractionPrompt(
        system_prompt="""You extract contact information from web pages.
        Be thorough but only extract publicly available contact details.
        Never fabricate information - return null for missing fields.""",

        user_template="""Extract all contact information found:

        Look for:
        - Email addresses
        - Phone numbers
        - Physical addresses
        - Social media links
        - Contact form URLs

        Content:
        {markdown}

        Return JSON:
        {{
            "emails": [...],
            "phones": [...],
            "address": null,
            "social_media": {{}},
            "contact_forms": [...]
        }}""",

        examples=[],
    ),
}


class PromptEngine:
    """Prompt engineering utilities."""

    @staticmethod
    def format_prompt(
        template: str,
        context: dict,
        markdown: str = None
    ) -> str:
        """Format prompt with context variables."""
        variables = {
            "markdown": markdown or "",
            **context,
        }

        return template.format(**variables)

    @staticmethod
    def create_extraction_prompt(
        prompt_key: str,
        markdown: str,
        context: dict = None
    ) -> str:
        """Create a formatted extraction prompt."""
        prompt = PROMPTS.get(prompt_key)
        if not prompt:
            raise ValueError(f"Unknown prompt: {prompt_key}")

        return PromptEngine.format_prompt(
            prompt.user_template,
            context or {},
            markdown
        )
```

---

## CSS Customization

### Advanced CSS Selectors

```python
SELECTOR_PATTERNS = {
    # Text extraction
    "main_content": [
        "article",
        "[role='main']",
        ".main-content",
        "#main",
        ".post-content",
        ".entry-content",
    ],

    # Product listings
    "product_cards": [
        ".product-card",
        ".product-item",
        "[data-product-id]",
        ".catalog-item",
        ".shop-item",
    ],

    # Navigation
    "navigation": [
        "nav",
        "[role='navigation']",
        ".menu",
        ".nav-menu",
        "#navigation",
    ],

    # Tables
    "data_tables": [
        "table.data",
        "table.grid",
        "[role='grid']",
        ".results-table",
    ],

    # Forms
    "input_fields": [
        "input[type='text']",
        "input[type='email']",
        "input:not([type])",
        "textarea",
        "select",
    ],
}


class CSSSelectorBuilder:
    """Build complex CSS selectors for extraction."""

    def __init__(self):
        self.selectors = []

    def find_by_text(self, text: str, tag: str = "*") -> str:
        """Selector to find element containing specific text."""
        return f"{tag}:has-text('{text}')"

    def find_by_attribute(
        self,
        attr: str,
        value: str,
        tag: str = "*"
    ) -> str:
        """Selector to find element with specific attribute value."""
        return f'{tag}[{attr}*="{value}"]'

    def find_by_class(self, class_name: str, tag: str = "*") -> str:
        """Selector to find element with class."""
        return f"{tag}.{class_name}"

    def nth_child(self, selector: str, n: int) -> str:
        """Selector for nth child."""
        return f"{selector}:nth-child({n})"

    def within_parent(self, parent: str, child: str) -> str:
        """Selector for child within parent."""
        return f"{parent} {child}"

    def combine(self, *selectors, combinator: str = " ") -> str:
        """Combine multiple selectors."""
        return combinator.join(selectors)

    def build(self) -> str:
        """Build final selector."""
        return ", ".join(self.selectors)


# Example usage
builder = CSSSelectorBuilder()
selector = builder.combine(
    builder.find_by_class("product-card"),
    builder.find_by_attribute("data-price", "", "[data-price]")
)
# Result: ".product-card [data-price]"
```

---

## User Agent Management

```python
from dataclasses import dataclass
from typing import List, Optional
import random

@dataclass
class UserAgent:
    """User agent configuration."""
    string: str
    platform: str
    browser: str
    is_mobile: bool

class UserAgentManager:
    """Manage user agents for crawling."""

    USER_AGENTS = [
        UserAgent(
            string="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            platform="Windows",
            browser="Chrome",
            is_mobile=False,
        ),
        UserAgent(
            string="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            platform="macOS",
            browser="Chrome",
            is_mobile=False,
        ),
        UserAgent(
            string="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            platform="iOS",
            browser="Safari",
            is_mobile=True,
        ),
        UserAgent(
            string="Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            platform="Android",
            browser="Chrome",
            is_mobile=True,
        ),
    ]

    def __init__(self, rotate: bool = True):
        self.rotate = rotate
        self.current_index = 0

    def get(self, domain: str = None) -> str:
        """Get user agent, optionally rotating for each domain."""
        if self.rotate and domain:
            # Use consistent user agent per domain
            seed = hash(domain) % len(self.USER_AGENTS)
            return self.USER_AGENTS[seed].string

        if self.rotate:
            self.current_index = (self.current_index + 1) % len(self.USER_AGENTS)

        return self.USER_AGENTS[self.current_index].string

    def get_for_site(self, url: str) -> str:
        """Get user agent optimized for target site."""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc

        # Use mobile for mobile-specific sites
        mobile_domains = ["m.", "mobile."]
        if any(d in domain for d in mobile_domains):
            for ua in self.USER_AGENTS:
                if ua.is_mobile:
                    return ua.string

        return self.get(domain)


# Browser configuration with user agent
from crawl4ai import BrowserConfig

browser_config = BrowserConfig(
    headless=True,
    user_agent=UserAgentManager().get("example.com"),
    viewport_width=1920,
    viewport_height=1080,
)
```

---

## Headers Customization

```python
from typing import Dict, Optional
from crawl4ai import BrowserConfig

class HeaderManager:
    """Manage custom headers for requests."""

    DEFAULT_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    def __init__(self, extra_headers: Dict = None):
        self.headers = {**self.DEFAULT_HEADERS, **(extra_headers or {})}

    def get_headers(self, url: str = None) -> Dict:
        """Get headers for a specific URL."""
        headers = self.headers.copy()

        if url:
            # Add Referer header
            from urllib.parse import urlparse
            parsed = urlparse(url)
            headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"

        return headers

    def with_auth(self, token: str, auth_type: str = "Bearer") -> "HeaderManager":
        """Add authentication headers."""
        self.headers["Authorization"] = f"{auth_type} {token}"
        return self

    def with_cookies(self, cookies: Dict) -> "HeaderManager":
        """Add cookie header."""
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        self.headers["Cookie"] = cookie_str
        return self


# Usage
headers = HeaderManager(
    extra_headers={
        "X-Custom-Header": "value",
        "Cache-Control": "no-cache",
    }
).with_auth("my-token").get_headers("https://example.com")

browser_config = BrowserConfig(
    headless=True,
    headers=headers,
)
```
