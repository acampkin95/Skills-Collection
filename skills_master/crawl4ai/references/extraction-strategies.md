# Extraction Strategies Guide

This guide covers the different extraction methods available in Crawl4AI and when to use each.

## Overview

Crawl4AI provides three primary extraction strategies:

1. **CSS/JSON Extraction** - Fast, deterministic, pattern-based
2. **LLM-Based Extraction** - Flexible, handles complex/irregular content
3. **Hybrid Extraction** - Combines both approaches

---

## 1. CSS/JSON Extraction Strategy

The fastest and most efficient method for structured, repetitive content.

### When to Use
- E-commerce product listings
- Table data
- Repeating card layouts
- News article feeds
- Any content with consistent HTML structure

### Basic Usage

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# Define schema for extraction
schema = {
    "name": "products",
    "baseSelector": ".product-grid .product-card",
    "fields": [
        {"name": "name", "selector": "h2.title", "type": "text"},
        {"name": "price", "selector": ".price", "type": "text"},
        {"name": "image", "selector": "img", "type": "attribute", "attribute": "src"},
        {"name": "url", "selector": "a", "type": "attribute", "attribute": "href"},
        {"name": "rating", "selector": ".stars", "type": "attribute", "attribute": "data-rating"}
    ]
}

extraction_strategy = JsonCssExtractionStrategy(schema=schema)
config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun("https://shop.example.com", config=config)
    products = result.extracted_content  # List of dicts
```

### Schema Reference

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique name for this extraction |
| `baseSelector` | string | CSS selector for repeating container |
| `fields` | array | Field definitions |

### Field Definition

```python
{
    "name": "field_name",           # Output key
    "selector": ".css-selector",    # CSS selector within container
    "type": "text|html|attribute|number|date",
    "attribute": "src|href|class",  # Required for 'attribute' type
    "optional": True                # Skip if not found
}
```

### Nested Structures

```python
schema = {
    "name": "products_with_variants",
    "baseSelector": ".product",
    "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {
            "name": "variants",
            "selector": ".variant",
            "type": "nested",
            "fields": [
                {"name": "name", "selector": ".name", "type": "text"},
                {"name": "price", "selector": ".price", "type": "text"}
            ]
        }
    ]
}
```

---

## 2. LLM-Based Extraction Strategy

Uses AI to understand and extract content, perfect for complex or irregular structures.

### When to Use
- Unstructured or semi-structured content
- Content that varies significantly across pages
- Complex relationships that are hard to express in CSS
- When schema generation is needed

### Basic Usage

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

extraction_strategy = LLMExtractionStrategy(
    provider="openai/gpt-4o-mini",
    instruction="Extract all financial metrics including revenue, profit, and growth rates from this report"
)

config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun("https://report.example.com", config=config)
    financial_data = result.extracted_content
```

### Providers

```python
# OpenAI
provider="openai/gpt-4o"
provider="openai/gpt-4o-mini"
provider="openai/gpt-3.5-turbo"

# Anthropic
provider="anthropic/claude-3-5-sonnet-20241022"
provider="anthropic/claude-3-haiku-20240307"

# Local/Ollama
provider="ollama/llama3.1"
provider="ollama/mistral"

# Groq
provider="groq/llama-3.1-70b-versatile"

# Google Gemini
provider="google/gemini-pro"
```

### Advanced Instructions

```python
instruction = """
Extract information about company executives from this page.
For each executive, extract:
- Full name
- Job title
- Biography (first 200 chars)
- Photo URL (if available)
- Direct email link

Return as JSON array with this structure:
[
  {
    "name": "...",
    "title": "...",
    "bio": "...",
    "photo_url": "...",
    "email": "..."
  }
]
"""
```

---

## 3. Hybrid Extraction Strategy

Combines CSS pre-filtering with LLM extraction for optimal results.

### When to Use
- Large pages where you want to focus LLM on specific sections
- When you need structure from CSS but understanding from LLM
- Performance optimization - reduce tokens sent to LLM

### Usage

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

# Pre-filter with CSS before LLM processing
css_pre_filter = {
    "selector": ".article-body",
    "fields": [
        {"name": "content", "selector": "p", "type": "html"}
    ]
}

extraction_strategy = LLMExtractionStrategy(
    provider="openai/gpt-4o-mini",
    instruction="Summarize the key points from this article",
    pre_filter_css=css_pre_filter
)
```

---

## 4. Content Filters

Enhance extraction by filtering content before processing.

### Pruning Content Filter

Removes low-quality or boilerplate content:

```python
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

filter = PruningContentFilter(
    threshold=0.4,          # Higher = more aggressive filtering
    threshold_type="fixed"  # or "adaptive"
)

md_generator = DefaultMarkdownGenerator(content_filter=filter)
config = CrawlerRunConfig(markdown_generator=md_generator)
```

### BM25 Content Filter

Relevance-based filtering for queries:

```python
from crawl4ai.content_filter_strategy import BM25ContentFilter

filter = BM25ContentFilter(
    user_query="machine learning tutorials",
    bm25_threshold=1.0,     # Minimum relevance score
    top_k=10                # Keep top K results
)
```

---

## 5. Batch Extraction

Process multiple URLs efficiently:

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

schema = load_json("product_schema.json")
extraction_strategy = JsonCssExtractionStrategy(schema=schema)
config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

urls = [
    "https://shop.com/product/1",
    "https://shop.com/product/2",
    "https://shop.com/product/3",
]

async with AsyncWebCrawler() as crawler:
    results = await crawler.arun_many(
        urls=urls,
        config=config,
        max_concurrent=5
    )

    for result in results:
        if result.success:
            products = result.extracted_content
            # Process products
```

---

## 6. Schema Generation

Auto-generate schemas using LLM:

```python
from crawl4ai.extraction_strategy import LLMExtractionStrategy

# Generate schema from page description
schema_generator = LLMExtractionStrategy(
    provider="openai/gpt-4o-mini",
    instruction="""
    Analyze this page and generate a JSON CSS extraction schema for:
    "extracting blog posts with title, date, author, and summary"

    Return ONLY valid JSON schema with name, baseSelector, and fields.
    """
)

# First crawl gets the page
async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url)
    # LLM generates schema based on result.markdown
```

---

## Performance Comparison

| Strategy | Speed | Cost | Accuracy | Best For |
|----------|-------|------|----------|----------|
| CSS/JSON | Fast | Free | High | Structured, repetitive |
| LLM | Slow | $$ | Very High | Complex, irregular |
| Hybrid | Medium | $ | High | Large, mixed content |

---

## Best Practices

1. **Start with CSS/JSON** - Faster and free, use LLM only when needed
2. **Generate schemas once** - Reuse across similar pages
3. **Use appropriate selectors** - Prefer classes over element types
4. **Test on edge cases** - Check for missing or malformed data
5. **Add error handling** - Handle missing elements gracefully
6. **Consider rate limits** - Space out requests for sensitive sites

```python
# Robust extraction with error handling
for field in schema["fields"]:
    try:
        value = element.query_selector(field["selector"])
        if value:
            result[field["name"]] = extract_value(value, field)
        elif not field.get("optional", False):
            result[field["name"]] = None  # or raise error
    except Exception as e:
        log.warning(f"Failed to extract {field['name']}: {e}")
```
