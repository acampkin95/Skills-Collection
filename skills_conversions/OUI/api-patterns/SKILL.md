---
name: api-patterns
description: "REST and GraphQL API interaction patterns, authentication workflows, pagination strategies, error handling, idempotency, and API design understanding for non-CLI agents. Use when interacting with APIs, understanding API patterns, handling authentication, managing pagination, debugging API responses, or designing API interactions."
version: "1.0.0"
metadata:
  category: web-interaction
  scope: non-cli
---

# API Interaction Patterns

Understanding REST and GraphQL APIs, authentication flows, pagination, error handling, and best practices for programmatic API consumption.

## REST API Patterns

### Resource-Oriented URL Structure

```
COLLECTION OPERATIONS:
GET    /api/v2/articles          → List articles
POST   /api/v2/articles          → Create article

SINGLE RESOURCE OPERATIONS:
GET    /api/v2/articles/123      → Get article #123
PUT    /api/v2/articles/123      → Replace article #123
PATCH  /api/v2/articles/123      → Update article #123
DELETE /api/v2/articles/123      → Delete article #123

NESTED RESOURCES:
GET    /api/v2/articles/123/comments     → List comments on article
POST   /api/v2/articles/123/comments     → Add comment to article

ACTIONS (non-CRUD):
POST   /api/v2/articles/123/publish      → Publish article
POST   /api/v2/articles/123/archive      → Archive article
```

### Common Query Parameters

```
FILTERING:
  ?status=published&author=john
  ?created_after=2025-01-01

SORTING:
  ?sort=-created_at,+title     # - = desc, + = asc
  ?order_by=date&order=desc

FIELD SELECTION:
  ?fields=id,title,author      # Only return these fields
  ?select=title,slug

SEARCH:
  ?q=search+terms
  ?search=fulltext+query

EXPANSION:
  ?include=author,tags          # Include related resources
  ?expand=comments(limit:5)
```

### Standard Response Envelope

```json
{
  "data": {
    "id": 123,
    "type": "article",
    "attributes": {
      "title": "Article Title",
      "body": "Content..."
    },
    "relationships": {
      "author": { "data": { "id": 1, "type": "user" } }
    }
  },
  "included": [
    { "id": 1, "type": "user", "attributes": { "name": "Author" } }
  ],
  "meta": {
    "total": 150,
    "page": 2,
    "per_page": 20
  }
}
```

## GraphQL Patterns

### Query Structure

```graphql
query GetArticle($id: ID!) {
  article(id: $id) {
    id
    title
    body
    author {
      id
      name
      avatarUrl
    }
    tags {
      id
      name
    }
    comments(limit: 10) {
      edges {
        node {
          id
          body
          author { name }
          createdAt
        }
      }
      totalCount
    }
  }
}
```

### GraphQL vs REST Decision

| Aspect | REST | GraphQL |
|--------|------|---------|
| **Over-fetching** | Returns full resources | Request only needed fields |
| **Under-fetching** | Multiple requests needed | Single query, nested data |
| **Caching** | HTTP caching built-in | More complex (normalized cache) |
| **Learning curve** | Lower | Higher |
| **File upload** | Simple multipart | Requires spec extension |
| **Error handling** | HTTP status codes | Always 200, errors in body |

### GraphQL Error Response

```json
{
  "data": { "article": null },
  "errors": [
    {
      "message": "Article not found",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["article"],
      "extensions": {
        "code": "NOT_FOUND",
        "timestamp": "2025-01-15T10:30:00Z"
      }
    }
  ]
}
```

## Authentication Workflows

### OAuth 2.0 Client Credentials Flow

```
STEP 1: Obtain token
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
&scope=read write

Response:
{
  "access_token": "eyJhbG...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "dGhpcyBpcyBh..."
}

STEP 2: Use token
GET /api/resource
Authorization: Bearer eyJhbG...

STEP 3: Refresh before expiry
POST /oauth/token
grant_type=refresh_token
&refresh_token=dGhpcyBpcyBh...
```

### Token Lifecycle Management

```
┌──────────────┐
│ Obtain Token │
└──────┬───────┘
       │
       ▼
┌──────────────┐     Token expired?     ┌──────────────┐
│ Use Token    │───────────────────────►│ Refresh Token│
└──────┬───────┘     (401 response)     └──────┬───────┘
       │                                         │
       │ Fresh token                             │
       ◄─────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Make Request │
└──────────────┘

RULES:
- Check expiry before each request
- Refresh at 80% of expiry window
- If refresh fails, re-authenticate
- Never expose tokens in logs or URLs
```

### API Key Management

```
BEST PRACTICES:
├── Store keys in environment variables, never in code
├── Use different keys for different environments
├── Rotate keys regularly
├── Use least-privilege keys (read-only when possible)
├── Monitor key usage for anomalies
├── Revoke compromised keys immediately
└── Use key vaults/secrets managers in production

KEY ROTATION:
1. Generate new key
2. Update all consumers to use new key
3. Verify new key works
4. Revoke old key
```

## Pagination Strategies

### Choosing a Strategy

| Strategy | Pros | Cons | Best For |
|----------|------|------|----------|
| **Offset** | Simple, random access | Slow for large offsets, inconsistent with changes | Small datasets |
| **Cursor** | Consistent, performant | No random access, opaque | Large datasets, real-time |
| **Keyset** | Consistent, efficient | Requires indexed column | Ordered, time-series |
| **Link** | Standard, discoverable | Extra parsing | REST APIs (GitHub-style) |

### Implementing Complete Pagination

```
PAGINATION ALGORITHM:
─────────────────────
1. Start with first page/cursor
2. Process each page of results
3. Check for next page indicator
4. Continue until no more pages
5. Track total processed for verification

GUARD RAILS:
- Maximum pages limit (prevent infinite loops)
- Maximum total items limit
- Timeout for entire operation
- Progress logging every N pages
```

## Error Handling Patterns

### Error Response Formats

```json
// RFC 7807 Problem Details (recommended)
{
  "type": "https://example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The 'email' field must be a valid email address.",
  "instance": "/api/v2/users",
  "errors": [
    { "field": "email", "message": "Invalid email format" }
  ]
}

// Simple format
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": { "field": "email" }
  }
}
```

### Error Recovery Decision Tree

```
ERROR RECEIVED
      │
      ├── 4xx Error?
      │   ├── 400 → Fix request body/params
      │   ├── 401 → Refresh auth token
      │   ├── 403 → Check permissions
      │   ├── 404 → Resource gone or wrong URL
      │   ├── 409 → Resolve conflict, retry
      │   ├── 422 → Fix validation errors
      │   └── 429 → Honor Retry-After, backoff
      │
      └── 5xx Error?
          ├── Retry up to 3 times with backoff
          ├── If persists → API is down, alert
          └── Use cached data if available
```

## Idempotency

### Making Safe Requests

```
IDEMPOTENT BY DESIGN:
├── GET requests → always safe to repeat
├── PUT requests → same input = same result
├── DELETE requests → repeated deletes = same state
├── HEAD/OPTIONS → no side effects

NOT IDEMPOTENT:
├── POST (creates new resource each time)
├── PATCH (may have different effects)
│
MAKE IDEMPOTENT WITH:
├── Idempotency-Key header (server deduplicates)
├── Use PUT instead of POST when possible
├── Use conditional headers (If-Match, If-None-Match)
└── Check-before-create pattern (GET first, POST only if missing)
```

## API Versioning

```
COMMON STRATEGIES:
├── URL path:    /api/v2/resource (most common)
├── Header:      Accept: application/vnd.api.v2+json
├── Query param: /api/resource?version=2
└── Content-Type: application/vnd.api+json; version=2

VERSION LIFECYCLE:
Active → Deprecated (sunset header) → Sunset (removed)

Always check for:
- Sunset header (planned deprecation)
- Deprecation notices in responses
- API changelog for breaking changes
```


## When to Use

- Designing or documenting REST or GraphQL APIs
- Understanding API authentication, pagination, and error patterns
- Debugging API interactions and response handling
- Evaluating API design quality during architecture reviews
- Planning API versioning and backward compatibility strategies

## Limitations

- Patterns are guidelines, not rigid rules — context determines applicability
- Specific framework implementations may differ from generic patterns
- Security patterns require framework-specific configuration
- GraphQL patterns assume schema-first design philosophy

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [web-fetching](../web-fetching/SKILL.md) | Apply API patterns when making HTTP requests |
| [web-crawling](../web-crawling/SKILL.md) | APIs are often preferable to crawling when available |
| [modern-web-standards](../modern-web-standards/SKILL.md) | API patterns should follow web platform standards |
| [technical-writing](../technical-writing/SKILL.md) | Document APIs using established documentation patterns |
