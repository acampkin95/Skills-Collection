---
name: web-fetching
description: "HTTP request patterns, fetch/curl equivalents, authentication strategies, header management, rate limiting, and request lifecycle for non-CLI agents. Use when making HTTP requests, interacting with APIs via fetch, understanding request/response patterns, managing authentication, or debugging web requests."
version: "1.0.0"
metadata:
  category: web-interaction
  scope: non-cli
---

# Web Fetching & HTTP Patterns

Understanding HTTP request patterns, authentication, headers, and response handling for agents that interact with web services without terminal access.

## HTTP Method Reference

| Method | Purpose | Idempotent | Cacheable | Body |
|--------|---------|------------|-----------|------|
| `GET` | Retrieve resource | Yes | Yes | No |
| `POST` | Create/submit | No | Rarely | Yes |
| `PUT` | Replace entire resource | Yes | No | Yes |
| `PATCH` | Partial update | No | No | Yes |
| `DELETE` | Remove resource | Yes | No | Optional |
| `HEAD` | Get headers only | Yes | Yes | No |
| `OPTIONS` | Get allowed methods | Yes | No | No |

## Request Structure

### Anatomy of a Request

```
URL:          https://api.example.com/v2/resources?page=1&limit=20
              ├───────┬──────────┘ ├──────┬──────────┘ ├───────┬──────┘
              │ scheme + host      │ path              │ query params

Method:       GET
Headers:      Authorization: Bearer eyJhbG...
              Accept: application/json
              Content-Type: application/json
              User-Agent: AgentName/1.0

Body:         (none for GET)
```

### Common Headers

| Header | Purpose | When to Include |
|--------|---------|-----------------|
| `Authorization` | Authentication credentials | Every authenticated request |
| `Accept` | Expected response format | When you need specific format |
| `Content-Type` | Request body format | When sending a body |
| `User-Agent` | Identify the client | Always (polite practice) |
| `Accept-Encoding` | Compression support | When you can handle compressed responses |
| `If-None-Match` | Conditional request (ETag) | Caching |
| `If-Modified-Since` | Conditional request (date) | Caching |
| `Cache-Control` | Caching directives | When controlling cache behavior |
| `X-Request-ID` | Request tracking | Debugging, idempotency |
| `Retry-After` | When to retry (from server) | Rate limiting response |

## Authentication Patterns

### Bearer Token

```
Authorization: Bearer <token>
```
Most common for modern APIs. Token obtained from OAuth flow or API key.

### API Key (Header)

```
X-API-Key: <key>
```
Simple but less secure. Common for internal/development APIs.

### API Key (Query Parameter)

```
https://api.example.com/resource?api_key=<key>
```
Less secure (logged in URLs). Avoid for sensitive operations.

### Basic Authentication

```
Authorization: Basic base64(username:password)
```
Legacy pattern. Only use over HTTPS.

### OAuth 2.0 Flows

```
CLIENT CREDENTIALS (server-to-server):
┌────────┐           ┌────────┐           ┌──────────┐
│ Agent  │──(1)─────►│ Auth   │──(2)─────►│ Resource │
│        │◄──(3)─────│ Server │           │ Server   │
│        │──(4)──────────────────────────►│          │
└────────┘           └────────┘           └──────────┘

(1) POST /token with client_id + client_secret
(2) Validate credentials
(3) Return access_token (+ optional refresh_token)
(4) Request resource with Bearer token
```

## Rate Limiting

### Common Rate Limit Headers

```
X-RateLimit-Limit:     1000        # Total allowed per window
X-RateLimit-Remaining: 842         # Remaining in current window
X-RateLimit-Reset:     1700000000  # Unix timestamp when window resets
Retry-After:           30          # Seconds to wait before retry
```

### Rate Limit Strategies

| Strategy | Implementation | Use When |
|----------|---------------|----------|
| **Fixed window** | Reset counter every N seconds | Simple APIs |
| **Sliding window** | Count requests in last N seconds | Most modern APIs |
| **Token bucket** | Tokens replenish at fixed rate | Burst-tolerant systems |
| **Leaky bucket** | Process at constant rate | Queue-like systems |

### Backoff Strategy

```
Response: 429 Too Many Requests

Strategy: Exponential backoff with jitter
─────────────────────────────────────────
Attempt 1: Wait 1 second
Attempt 2: Wait 2 seconds
Attempt 3: Wait 4 seconds
Attempt 4: Wait 8 seconds
Attempt 5: Wait 16 seconds (cap at ~60s)
...then fail gracefully

With jitter: random(0.5 * wait, 1.5 * wait)
```

## Response Handling

### Status Code Decision Tree

```
2xx Success
├── 200 OK → Use response body
├── 201 Created → Resource created, note Location header
├── 202 Accepted → Processing started, check status later
├── 204 No Content → Success, no body to parse
└── 206 Partial Content → Partial response, check Content-Range

3xx Redirection
├── 301 Moved Permanently → Update URL, follow redirect
├── 302 Found → Temporary redirect, follow but keep original URL
├── 304 Not Modified → Use cached version
└── 307/308 → Follow with same method

4xx Client Error
├── 400 Bad Request → Check request format/body
├── 401 Unauthorized → Check/update authentication
├── 403 Forbidden → No permission (different from auth failure)
├── 404 Not Found → Resource doesn't exist (or wrong URL)
├── 409 Conflict → State conflict, resolve before retry
├── 422 Unprocessable → Valid format, semantic errors in body
└── 429 Too Many Requests → Rate limited, back off and retry

5xx Server Error
├── 500 Internal → Server bug, retry with backoff
├── 502 Bad Gateway → Upstream failure, retry
├── 503 Unavailable → Server overloaded, retry with backoff
└── 504 Gateway Timeout → Upstream timeout, retry with longer timeout
```

### Pagination Patterns

```
OFFSET PAGINATION:
GET /resources?page=2&limit=20
Response: { data: [...], total: 150, page: 2, limit: 20 }

CURSOR PAGINATION:
GET /resources?cursor=abc123&limit=20
Response: { data: [...], next_cursor: "def456", has_more: true }

LINK PAGINATION (GitHub-style):
Response Headers:
  Link: <url?page=3>; rel="next", <url?page=50>; rel="last"

KEYSET PAGINATION:
GET /resources?created_after=2025-01-01&limit=20
Response: { data: [...], last_created: "2025-03-15" }
```

## Content Types

### Request Body Formats

| Content-Type | Use Case | Format |
|-------------|----------|--------|
| `application/json` | API data | `{"key": "value"}` |
| `application/x-www-form-urlencoded` | Form submission | `key=value&key2=value2` |
| `multipart/form-data` | File upload | Binary boundaries |
| `text/plain` | Simple text | Plain text string |
| `text/xml` | SOAP/Legacy | XML document |

### Response Content Negotiation

```
Accept: application/json              # Prefer JSON
Accept: text/html, application/json   # Prefer HTML, accept JSON
Accept: */*                           # Accept anything
Accept: text/markdown                 # Request markdown
```

## Error Recovery Patterns

### Retry Decision Matrix

| Condition | Retry? | Strategy |
|-----------|--------|----------|
| Network timeout | Yes | Backoff + increase timeout |
| Connection refused | Yes | Backoff (service may be restarting) |
| DNS failure | Maybe | Single retry (could be transient) |
| 4xx error | No | Fix the request instead |
| 429 rate limit | Yes | Honor Retry-After header |
| 5xx error | Yes | Backoff, limited retries (3-5) |
| SSL error | No | Certificate issue, not transient |
| Invalid JSON response | No | Parse error, check API version |

### Request Timeout Guidelines

```
QUICK READ:    5-10 seconds   (simple GET, small response)
STANDARD:      15-30 seconds  (typical API call)
LONG OPERATION: 60-120 seconds (complex query, file upload)
STREAMING:     No timeout      (use chunked transfer)
```


## When to Use

- Making HTTP requests to APIs or web endpoints
- Retrieving content from specific URLs
- Interacting with REST or GraphQL APIs
- Handling authentication flows for protected resources
- Debugging API responses, status codes, and error patterns

## Limitations

- Cannot execute JavaScript — SPA content may not render
- Rate limits and IP blocking may require backoff strategies
- Some APIs require interactive authentication flows (OAuth browser redirects)
- Large file downloads may exceed tool timeouts

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [web-research](../web-research/SKILL.md) | Fetching specific URLs identified during research |
| [api-patterns](../api-patterns/SKILL.md) | Understand API design patterns for better interaction |
| [content-extraction](../content-extraction/SKILL.md) | Extract structured data from fetched responses |
| [web-crawling](../web-crawling/SKILL.md) | Fetching individual pages as part of a crawl |
