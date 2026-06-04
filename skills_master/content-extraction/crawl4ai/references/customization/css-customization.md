# CSS Customization Guide

Advanced CSS selector patterns for extraction.

## Basic Selectors

```python
SELECTORS = {
    "by_id": "#header",
    "by_class": ".product-card",
    "by_tag": "article",
    "by_attribute": "[data-product-id]",
    "by_attribute_value": "[type='text']",
    "by_partial_attribute": "[href*='product']",
}
```

## Common Patterns

```python
COMMON_SELECTORS = {
    "main_content": [
        "article",
        "[role='main']",
        ".main-content",
        "#main",
        ".post-content",
    ],
    "product_cards": [
        ".product-card",
        ".product-item",
        "[data-product]",
        ".catalog-item",
    ],
    "navigation": [
        "nav",
        "[role='navigation']",
        ".menu",
        ".nav-menu",
    ],
    "headings": "h1, h2, h3, h4",
    "links": "a[href]",
    "images": "img[src]",
}
```

## Advanced Selectors

```python
ADVANCED_SELECTORS = {
    "nth_item": ".items > div:nth-child(2)",
    "has_text": ":has-text('Add to Cart')",
    "has_class": ":has(.sale-badge)",
    "sibling": "h3 + p",
    "not_selector": "div:not(.advertisement)",
    "contains": "[class*='product']",
    "starts_with": "[id^='item-']",
    "ends_with": "[href$='.pdf']",
}
```
