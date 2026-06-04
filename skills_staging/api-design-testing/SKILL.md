---
name: api-design-testing
description: REST API design with OpenAPI 3.1, Zod validation, Hono routing, MSW mocking, and Pact contract testing. Use for API versioning, error handling, and type-safe endpoints.
version: 2.0.0
reviewed: "2026-06-04"
---
# API Design & Testing Skill

**Read the relevant reference file before starting work.**

## Quick Navigation

| Task | Reference |
|------|-----------|
| OpenAPI 3.1 specs, Zod-to-OpenAPI, Swagger UI | `references/openapi-spec.md` |
| Hono routing, middleware, validation, RPC, testing | `references/hono-patterns.md` |
| MSW mocking, Pact contract testing | `references/contract-testing.md` |

---

## REST Conventions

### HTTP Methods

| Method | Purpose | Idempotent | Request Body |
|--------|---------|------------|--------------|
| `GET` | Read resource(s) | Yes | No |
| `POST` | Create resource | No | Yes |
| `PUT` | Full replace | Yes | Yes |
| `PATCH` | Partial update | Yes | Yes |
| `DELETE` | Remove resource | Yes | Optional |

### URL Naming Rules

```
# Collections: plural nouns, lowercase, kebab-case
GET    /api/v1/users
GET    /api/v1/users/:id
POST   /api/v1/users
PATCH  /api/v1/users/:id
DELETE /api/v1/users/:id

# Nested resources: max 2 levels deep
GET    /api/v1/users/:userId/posts
POST   /api/v1/users/:userId/posts

# Actions (non-CRUD): use verbs as sub-resource
POST   /api/v1/users/:id/activate
POST   /api/v1/orders/:id/cancel

# Filtering via query params, not path
GET    /api/v1/posts?status=published&authorId=123
```

**Rules:**
- Use plural nouns for collections (`/users` not `/user`)
- Use kebab-case for multi-word resources (`/order-items`)
- Never nest deeper than 2 levels
- No trailing slashes
- No file extensions in URLs

### Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| `200` | OK | Successful GET, PATCH, DELETE |
| `201` | Created | Successful POST creating a resource |
| `204` | No Content | Successful DELETE with no response body |
| `400` | Bad Request | Validation error, malformed input |
| `401` | Unauthorized | Missing or invalid authentication |
| `403` | Forbidden | Authenticated but not authorized |
| `404` | Not Found | Resource does not exist |
| `409` | Conflict | Duplicate resource, state conflict |
| `422` | Unprocessable Entity | Semantically invalid input |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unexpected server failure |

---

## Error Response Format (RFC 7807)

Every error response MUST use this structure:

```typescript
// Standard error response type
type ProblemDetail = {
  type: string;       // URI identifying the error type
  title: string;      // Short human-readable summary
  status: number;     // HTTP status code
  detail?: string;    // Human-readable explanation
  instance?: string;  // URI identifying the occurrence
  errors?: Array<{    // Validation errors (extension)
    field: string;
    message: string;
    code: string;
  }>;
};

// Example: validation error
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid fields.",
  "errors": [
    { "field": "email", "message": "Invalid email format", "code": "invalid_format" },

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.