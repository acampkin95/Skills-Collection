# Content Cleanup Guide

Clean and normalize extracted web content for better quality output.

## Overview

Raw web content often contains:
- HTML artifacts
- Boilerplate text
- Navigation elements
-广告 and promotional content
- Formatting inconsistencies

This guide covers cleaning techniques for optimal content quality.

---

## 1. Basic Text Cleaning

### HTML Tag Removal

```python
import re
from html import unescape
from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    """Remove HTML tags while preserving text."""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ")

    # Decode HTML entities
    text = unescape(text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def remove_specific_tags(html: str, tags: list = None) -> str:
    """Remove specific HTML elements."""
    soup = BeautifulSoup(html, "html.parser")

    tags = tags or ['script', 'style', 'nav', 'footer', 'aside', 'header']

    for tag in tags:
        for element in soup.find_all(tag):
            element.decompose()

    return str(soup)
```

### Whitespace Normalization

```python
def normalize_whitespace(text: str) -> str:
    """Normalize all whitespace to single spaces."""
    # Remove leading/trailing whitespace
    text = text.strip()

    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove empty lines
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Normalize line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text

def fix_common_issues(text: str) -> str:
    """Fix common text extraction issues."""
    # Fix broken words (e.g., "web\ncrawling" -> "web crawling")
    text = re.sub(r'(\w)\n(\w)', r'\1 \2', text)

    # Fix missing spaces after punctuation
    text = re.sub(r'([.,;:])([A-Za-z])', r'\1 \2', text)

    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    return text
```

---

## 2. Boilerplate Removal

### Navigation Removal

```python
def remove_navigation(html: str) -> str:
    """Remove navigation elements."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove common nav elements
    selectors = [
        'nav', '[role="navigation"]', '.nav', '.navigation',
        '.menu', '.navbar', '.sidebar', '.breadcrumb',
        '[class*="nav"]', '[class*="menu"]'
    ]

    for selector in selectors:
        for nav in soup.select(selector):
            nav.decompose()

    return str(soup)
```

### Footer/Header Removal

```python
def remove_headers_footers(html: str) -> str:
    """Remove header and footer sections."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove headers
    for header in soup.find_all(['header', 'footer']):
        header.decompose()

    # Remove by common classes
    for elem in soup.find_all(class_=lambda x: x and any(c in str(x).lower() for c in
                ['header', 'footer', 'copyright', 'disclaimer'])):
        elem.decompose()

    return str(soup)
```

### Ad/Social Removal

```python
def remove_ads_social(html: str) -> str:
    """Remove advertisements and social elements."""
    soup = BeautifulSoup(html, "html.parser")

    # Ad selectors
    ad_selectors = [
        '[class*="ad-"]', '[class*="advertisement"]',
        '[id*="ad-"]', '[id*="advertisement"]',
        '.ads', '.advertising', '.social-share',
        '[class*="share"]', '[aria-label*="share"]',
        '.comments', '#comments', '.social-links'
    ]

    for selector in ad_selectors:
        for elem in soup.select(selector):
            elem.decompose()

    # Remove iframes (often ads)
    for iframe in soup.find_all('iframe'):
        if iframe.get('src') and any(x in iframe['src'] for x in ['ads', 'analytics', 'doubleclick']):
            iframe.decompose()

    return str(soup)
```

---

## 3. Content Extraction

### Main Content Extraction

```python
def extract_main_content(html: str) -> str:
    """Extract main article/content area."""
    soup = BeautifulSoup(html, "html.parser")

    # Try common article selectors
    article_selectors = [
        'article',
        '[role="main"]',
        '.post-content',
        '.article-content',
        '.entry-content',
        '.content-body',
        '.main-content',
        '.post',
        '.blog-post'
    ]

    for selector in article_selectors:
        content = soup.select_one(selector)
        if content and len(content.get_text()) > 200:
            return str(content)

    # Fallback: find largest text block
    text_elements = soup.find_all(['div', 'section', 'article'])
    if text_elements:
        largest = max(text_elements, key=lambda x: len(x.get_text()))
        return str(largest)

    return str(soup)
```

### Structured Data Extraction

```python
def extract_structured_data(html: str, selectors: dict) -> dict:
    """Extract structured data using CSS selectors."""
    soup = BeautifulSoup(html, "html.parser")
    result = {}

    for key, selector in selectors.items():
        element = soup.select_one(selector)
        if element:
            if element.name == 'a':
                result[key] = {
                    'text': element.get_text(strip=True),
                    'href': element.get('href', '')
                }
            elif element.name in ['img']:
                result[key] = {
                    'src': element.get('src', ''),
                    'alt': element.get('alt', '')
                }
            else:
                result[key] = element.get_text(strip=True)

    return result
```

---

## 4. Markdown Generation

### Clean Markdown Output

```python
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

def generate_clean_markdown(html: str) -> str:
    """Generate clean markdown from HTML."""
    # Use Crawl4AI's built-in generation
    generator = DefaultMarkdownGenerator(
        options={
            "ignore_links": False,
            "ignore_images": False,
            "image_alt_text": True,
            "headings": True,
            "tables": True,
            "code_blocks": True,
        }
    )

    # Generate markdown
    return generator.generate(html)
```

### Custom Markdown Cleanup

```python
def cleanup_markdown(markdown: str) -> str:
    """Clean up generated markdown."""
    lines = markdown.split('\n')

    # Remove empty lines at start
    while lines and not lines[0].strip():
        lines.pop(0)

    # Remove multiple consecutive headers
    cleaned = []
    for i, line in enumerate(lines):
        # Skip if line is header after header
        if line.startswith('#') and i > 0 and lines[i-1].startswith('#'):
            continue
        cleaned.append(line)

    # Remove short lines that are likely artifacts
    cleaned = [l for l in cleaned if len(l) > 3 or l.startswith('#')]

    # Remove reference-style links without definitions
    cleaned = [l for l in cleaned if not (l.startswith('[') and l.endswith(']:'))]

    return '\n'.join(cleaned)
```

---

## 5. URL Processing

### URL Normalization

```python
from urllib.parse import urljoin, urlparse, parse_qs

def normalize_url(url: str, base_url: str = None) -> str:
    """Normalize URL for consistency."""
    # Resolve relative URLs
    if base_url:
        url = urljoin(base_url, url)

    parsed = urlparse(url)

    # Remove fragments
    url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # Sort query parameters
    if parsed.query:
        params = parse_qs(parsed.query)
        sorted_params = '&'.join(f"{k}={v[0]}" for k in sorted(params.keys()))
        url = f"{url}?{sorted_params}"

    return url

def is_internal_link(url: str, base_url: str) -> bool:
    """Check if URL is internal to the domain."""
    parsed_base = urlparse(base_url)
    parsed_url = urlparse(url)

    return parsed_url.netloc == '' or parsed_url.netloc == parsed_base.netloc
```

### Link Extraction and Filtering

```python
def extract_and_filter_links(html: str, base_url: str) -> dict:
    """Extract links and categorize them."""
    soup = BeautifulSoup(html, "html.parser")

    internal = []
    external = []
    broken = []

    for link in soup.find_all('a', href=True):
        href = link['href'].strip()

        # Skip anchors and empty links
        if not href or href.startswith('#'):
            continue

        # Normalize
        full_url = urljoin(base_url, href)
        normalized = normalize_url(full_url, base_url)

        # Categorize
        if is_internal_link(href, base_url):
            internal.append({'url': normalized, 'text': link.get_text(strip=True)})
        else:
            external.append({'url': normalized, 'text': link.get_text(strip=True)})

    return {
        'internal': internal,
        'external': external,
        'internal_count': len(internal),
        'external_count': len(external)
    }
```

---

## 6. Metadata Extraction

```python
def extract_metadata(html: str) -> dict:
    """Extract page metadata."""
    soup = BeautifulSoup(html, "html.parser")
    metadata = {}

    # Title
    if soup.title:
        metadata['title'] = soup.title.get_text(strip=True)

    # Meta description
    desc = soup.find('meta', attrs={'name': 'description'})
    if desc:
        metadata['description'] = desc.get('content', '')

    # Open Graph
    og_props = ['title', 'description', 'image', 'type', 'url']
    for prop in og_props:
        meta = soup.find('meta', attrs={'property': f'og:{prop}'})
        if meta:
            metadata[f'og_{prop}'] = meta.get('content', '')

    # Twitter Card
    twitter_props = ['title', 'description', 'image', 'card']
    for prop in twitter_props:
        meta = soup.find('meta', attrs={'name': f'twitter:{prop}'})
        if meta:
            metadata[f'twitter_{prop}'] = meta.get('content', '')

    # Language
    html_tag = soup.find('html')
    metadata['language'] = html_tag.get('lang', '') if html_tag else ''

    # Canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if canonical:
        metadata['canonical_url'] = canonical.get('href', '')

    return metadata
```

---

## 7. Complete Pipeline

```python
class ContentCleaner:
    def __init__(self, config: dict = None):
        self.config = config or {}

    def process(self, html: str, base_url: str = None) -> dict:
        """Complete content cleaning pipeline."""
        result = {
            'original_length': len(html),
            'cleaned_html': html,
            'markdown': '',
            'metadata': {},
            'links': {},
            'text': '',
        }

        # 1. Remove unwanted elements
        html = remove_navigation(html)
        html = remove_headers_footers(html)
        html = remove_ads_social(html)
        html = remove_specific_tags(html, self.config.get('remove_tags', []))

        # 2. Extract main content
        main_content = extract_main_content(html)

        # 3. Generate markdown
        markdown = generate_clean_markdown(main_content)
        markdown = cleanup_markdown(markdown)
        result['markdown'] = markdown

        # 4. Extract metadata
        result['metadata'] = extract_metadata(html)

        # 5. Extract and filter links
        if base_url:
            result['links'] = extract_and_filter_links(html, base_url)

        # 6. Clean text
        text = clean_html(main_content)
        text = normalize_whitespace(text)
        text = fix_common_issues(text)
        result['text'] = text
        result['cleaned_length'] = len(text)

        return result

# Usage
cleaner = ContentCleaner({'remove_tags': ['script', 'style', 'nav']})
result = cleaner.process(html_content, base_url="https://example.com")

print(f"Original: {result['original_length']} chars")
print(f"Cleaned: {result['cleaned_length']} chars")
print(f"Title: {result['metadata'].get('title')}")
print(f"Links: {result['links'].get('internal_count', 0)} internal")
```

---

## 8. Quality Metrics

```python
def calculate_content_quality(text: str, html: str) -> dict:
    """Calculate content quality metrics."""
    metrics = {}

    # Text density
    text_length = len(text)
    html_length = len(html)
    metrics['text_density'] = text_length / max(html_length, 1)

    # Word count
    words = text.split()
    metrics['word_count'] = len(words)

    # Average sentence length
    sentences = re.split(r'[.!?]+', text)
    avg_sentence = len(words) / max(len([s for s in sentences if s.strip()]), 1)
    metrics['avg_sentence_length'] = avg_sentence

    # Heading ratio
    heading_count = len(re.findall(r'^#+\s', text, re.MULTILINE))
    metrics['heading_ratio'] = heading_count / max(len(words), 1)

    # Link density
    links = re.findall(r'\[.+?\]\(.+?\)', text)
    metrics['link_density'] = len(links) / max(len(words), 1)

    # Check for common issues
    issues = []

    # Check for excessive capitalization
    caps_words = re.findall(r'\b[A-Z]{2,}\b', text)
    if len(caps_words) > 10:
        issues.append('excessive_caps')

    # Check for broken links (requires external check)
    # Check for very short content
    if len(words) < 50:
        issues.append('very_short_content')

    metrics['issues'] = issues
    metrics['quality_score'] = 1.0 - (len(issues) * 0.2)

    return metrics
```
