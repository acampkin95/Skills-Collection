# Crawl4AI Prompt Engineering

Optimizing LLM prompts for extraction tasks.

## Prompt Design Principles

### Clear Instructions

```python
SYSTEM_PROMPT = """You are a precise data extraction assistant. Your task is to extract
information from web content accurately and consistently.

Rules:
1. Return ONLY valid JSON, no additional text
2. Use null for missing or unknown information
3. Be consistent with data types
4. Preserve exact values, do not summarize
5. If content is unclear, make the best guess and note uncertainty

Output format:
{
    "field_name": "value",
    "confidence": "high|medium|low"
}
"""
```

### Structured Output

```python
def create_extraction_prompt(
    content: str,
    fields: list,
    schema: dict = None
) -> str:
    """Create a structured extraction prompt."""

    fields_desc = "\n".join(
        f"- {f['name']}: {f['description']} ({f['type']})"
        for f in fields
    )

    return f"""Extract the following information from the content:

Required fields:
{fields_desc}

Content:
{content}

Return JSON matching this schema:
{schema or '{"type": "object", "properties": {}}'}

Do not include markdown code blocks. Return only raw JSON."""
```

---

## Field-Specific Prompts

### Product Fields

```python
PRODUCT_PROMPT = """Extract product information from this page:

Fields to extract:
- name: Full product title (string)
- price: Current price with currency (string)
- original_price: Original price if discounted (string or null)
- description: Product description (string)
- availability: "in_stock", "out_of_stock", or "limited" (string)
- rating: Average rating 0-5 (number or null)
- review_count: Number of reviews (number or null)
- features: List of key features (array)
- specifications: Object with technical specs (object)

Content:
{content}

Return valid JSON only."""
```

### Article Fields

```python
ARTICLE_PROMPT = """Extract article information:

Fields:
- title: Headline (string)
- author: Author name(s) (string or null)
- publish_date: Publication date (string or null)
- category: Article category (string or null)
- summary: Brief 2-3 sentence summary (string)
- key_points: Main points as array (array)
- tags: Topic tags (array)
- reading_time: Estimated reading time in minutes (number or null)

Content:
{content}

Return valid JSON only."""
```

---

## Few-Shot Examples

```python
FEW_SHOT_PROMPT = """You will extract structured data from product pages.

Here are examples:

Example 1:
Page: Wireless Headphones Pro
Price: $149.99, originally $199.99
Premium wireless headphones with noise cancellation
In Stock - Ships Today
4.5 rating from 2,341 reviews
Features: 30hr battery, BT 5.0, ANC
Output: {{"name": "Wireless Headphones Pro", "price": "$149.99", "original_price": "$199.99", "availability": "in_stock", "rating": 4.5}}

Example 2:
Page: Yoga Mat
Only $29.99
Standard yoga mat, various colors
Out of Stock
Output: {{"name": "Yoga Mat", "price": "$29.99", "availability": "out_of_stock", "rating": null}}

Now extract from:
{content}

Output:"""
```

---

## Optimization Techniques

### Token Optimization

```python
def optimize_prompt(
    prompt: str,
    max_tokens: int = 4000,
    content_length: int = 8000
) -> str:
    """Optimize prompt to fit within token limits."""

    # Calculate approximate tokens
    estimated_tokens = len(prompt.split()) * 1.3

    if estimated_tokens <= max_tokens:
        return prompt

    # Truncate content section
    lines = prompt.split("\n")
    for i, line in enumerate(lines):
        if "Content:" in line or "Input:" in line:
            # Keep prompt structure, truncate content
            remaining = max_tokens - (estimated_tokens - content_length)
            content = lines[i + 1] if i + 1 < len(lines) else ""
            truncated = content[:remaining] + "..."
            lines[i + 1] = truncated
            break

    return "\n".join(lines)
```

### Confidence Calibration

```python
def create_calibrated_prompt(
    base_prompt: str,
    confidence_fields: list = None
) -> str:
    """Add confidence scoring to prompt."""

    confidence_section = """

After extraction, rate your confidence for each field:
- high: Clearly stated in content
- medium: Inferred from context
- low: Best guess with uncertainty

Example: {"price": "$99.99", "confidence": "high"}
"""

    return base_prompt + confidence_section
```
