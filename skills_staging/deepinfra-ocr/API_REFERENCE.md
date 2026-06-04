# DeepInfra olmOCR API Reference

Complete API specification for DeepInfra's olmOCR-2-7B-1025 vision-language model.

## Endpoint

```
POST https://api.deepinfra.com/v1/openai/chat/completions
```

## Authentication

```http
Authorization: Bearer qEcg16aUm1XLr4yIbJ3FhH0OrgjTXSKe
Content-Type: application/json
```

## Basic Request

```json
{
  "model": "allenai/olmOCR-2-7B-1025",
  "max_tokens": 4096,
  "messages": [{
    "role": "user",
    "content": [{
      "type": "image_url",
      "image_url": {
        "url": "data:image/png;base64,iVBORw0KGgo..."
      }
    }]
  }]
}
```

## Request Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Must be `allenai/olmOCR-2-7B-1025` |
| `messages` | array | Message array with image content |

### Optional

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `max_tokens` | int | model max | 0-16384 | Max tokens to generate |
| `temperature` | float | 1.0 | 0-2 | Output randomness |
| `top_p` | float | 1.0 | 0-1 | Nucleus sampling |
| `top_k` | int | 0 | 0-999 | Top-k sampling (0=off) |
| `stream` | bool | false | - | Stream response |
| `presence_penalty` | float | 0 | -2 to 2 | New topic encouragement |
| `frequency_penalty` | float | 0 | -2 to 2 | Repetition penalty |
| `seed` | int | random | - | Reproducible output |
| `stop` | string/array | - | - | Stop sequences |

## Message Formats

### Image from Base64

```json
{
  "role": "user",
  "content": [{
    "type": "image_url",
    "image_url": {
      "url": "data:image/png;base64,iVBORw0KGgo..."
    }
  }]
}
```

### Image from URL

```json
{
  "role": "user",
  "content": [{
    "type": "image_url",
    "image_url": {
      "url": "https://example.com/document.png"
    }
  }]
}
```

### With Text Prompt

```json
{
  "role": "user",
  "content": [
    {
      "type": "image_url",
      "image_url": {"url": "data:image/png;base64,..."}
    },
    {
      "type": "text",
      "text": "Extract all text preserving the original layout and formatting."
    }
  ]
}
```

### Multiple Images

```json
{
  "role": "user",
  "content": [
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
    {"type": "text", "text": "Compare these two documents."}
  ]
}
```

## Response Format

```json
{
  "id": "chatcmpl-abc123def456",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "allenai/olmOCR-2-7B-1025",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "The extracted text from the document..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 1500,
    "completion_tokens": 450,
    "total_tokens": 1950,
    "estimated_cost": 0.00022
  }
}
```

### Finish Reasons

| Value | Description |
|-------|-------------|
| `stop` | Natural completion |
| `length` | Hit max_tokens limit |
| `content_filter` | Content filtered |

## Supported Image Formats

| Format | MIME Type | Notes |
|--------|-----------|-------|
| PNG | image/png | Recommended for documents |
| JPEG | image/jpeg | Good for photos |
| GIF | image/gif | Static only |
| WebP | image/webp | Good compression |
| BMP | image/bmp | Uncompressed |
| TIFF | image/tiff | High quality scans |

## Pricing

| Type | Cost |
|------|------|
| Input | $0.09 / 1M tokens |
| Output | $0.19 / 1M tokens |

**Context window:** 16,384 tokens

### Cost Estimation

Typical document page: ~1,000-2,000 input tokens
Average OCR output: ~200-500 tokens

**Example:** 10-page PDF ≈ 15,000 input + 3,000 output = ~$0.002

## Error Responses

```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "code": "error_code"
  }
}
```

### Error Codes

| Status | Code | Description | Resolution |
|--------|------|-------------|------------|
| 400 | invalid_request | Malformed request | Check JSON format |
| 401 | authentication_error | Invalid API key | Verify API key |
| 413 | request_too_large | Image too large | Reduce image size |
| 429 | rate_limit_exceeded | Too many requests | Implement backoff |
| 500 | server_error | Internal error | Retry with backoff |

## Rate Limiting

Implement exponential backoff for 429 responses:

```python
import time

def request_with_retry(payload, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        
        if response.status_code == 429:
            wait = 2 ** attempt
            time.sleep(wait)
            continue
        
        return response
    
    raise Exception("Max retries exceeded")
```

**Recommended:** 1-2 second delay between requests for batch processing.

## Best Practices

### Image Quality

| Use Case | Recommended DPI | Notes |
|----------|-----------------|-------|
| Clean printed docs | 150-200 | Fast, sufficient quality |
| Standard scans | 200-250 | Good balance |
| Poor quality/handwriting | 300+ | Higher accuracy |
| Photos of documents | 200 | Mobile camera captures |

### Optimal Parameters

```python
# For consistent OCR output
{
    "temperature": 0.1,
    "max_tokens": 4096,
}

# For creative interpretation
{
    "temperature": 0.7,
    "max_tokens": 4096,
}
```

### Image Size Limits

- **Maximum:** ~10MB per image (base64 encoded)
- **Recommended:** < 5MB for faster processing
- **Optimal resolution:** 150-300 DPI (higher rarely improves accuracy)

## Custom Prompts for Specific Tasks

### Structured Data Extraction

```json
{
  "type": "text",
  "text": "Extract the following fields as JSON:\n- invoice_number\n- date\n- vendor_name\n- line_items (array with description, quantity, price)\n- total_amount"
}
```

### Table Extraction

```json
{
  "type": "text",
  "text": "Convert all tables in this document to markdown table format."
}
```

### Form Field Extraction

```json
{
  "type": "text",
  "text": "Extract all form fields and their filled values as key-value pairs."
}
```

### Preserve Layout

```json
{
  "type": "text",
  "text": "Extract all text while preserving the original document layout, columns, and formatting as much as possible."
}
```

## cURL Examples

### Basic OCR

```bash
curl -X POST "https://api.deepinfra.com/v1/openai/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer qEcg16aUm1XLr4yIbJ3FhH0OrgjTXSKe" \
  -d '{
    "model": "allenai/olmOCR-2-7B-1025",
    "max_tokens": 4096,
    "messages": [{
      "role": "user",
      "content": [{
        "type": "image_url",
        "image_url": {"url": "https://example.com/document.png"}
      }]
    }]
  }'
```

### With Base64 Image

```bash
BASE64=$(base64 -w 0 document.png)

curl -X POST "https://api.deepinfra.com/v1/openai/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer qEcg16aUm1XLr4yIbJ3FhH0OrgjTXSKe" \
  -d "{
    \"model\": \"allenai/olmOCR-2-7B-1025\",
    \"max_tokens\": 4096,
    \"messages\": [{
      \"role\": \"user\",
      \"content\": [{
        \"type\": \"image_url\",
        \"image_url\": {\"url\": \"data:image/png;base64,$BASE64\"}
      }]
    }]
  }"
```
