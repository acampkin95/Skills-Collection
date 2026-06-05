---
name: api-design-testing
description: REST API design, type-safe validation, OpenAPI specs, and contract testing with Hono, Zod, and MSW.
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
    { "field": "age", "message": "Must be at least 18", "code": "too_small" }
  ]
}

// Example: not found
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User with ID '550e8400' does not exist.",
  "instance": "/api/v1/users/550e8400"
}
```

### Zod Error Formatting Helper

```typescript
import { ZodError } from "zod";
import type { ProblemDetail } from "./types";

export function formatZodError(error: ZodError, instance?: string): ProblemDetail {
  return {
    type: "https://api.example.com/errors/validation",
    title: "Validation Error",
    status: 422,
    detail: "The request body contains invalid fields.",
    instance,
    errors: error.issues.map((issue) => ({
      field: issue.path.join("."),
      message: issue.message,
      code: issue.code,
    })),
  };
}
```

---

## Request Validation with Zod

```typescript
import { z } from "zod";

// Define reusable schemas
const paginationSchema = z.object({
  limit: z.coerce.number().int().min(1).max(100).default(20),
  offset: z.coerce.number().int().min(0).default(0),
});

const cursorPaginationSchema = z.object({
  limit: z.coerce.number().int().min(1).max(100).default(20),
  cursor: z.string().optional(),
});

const sortSchema = z.object({
  sortBy: z.enum(["createdAt", "updatedAt", "name"]).default("createdAt"),
  sortOrder: z.enum(["asc", "desc"]).default("desc"),
});

// Resource schemas
const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(["user", "admin"]).default("user"),
});

const updateUserSchema = createUserSchema.partial();

const userIdSchema = z.object({
  id: z.string().uuid(),
});

// Compose for list endpoint
const listUsersSchema = paginationSchema.merge(sortSchema).extend({
  status: z.enum(["active", "inactive"]).optional(),
  search: z.string().max(200).optional(),
});

// Type inference
type CreateUserInput = z.infer<typeof createUserSchema>;
type ListUsersQuery = z.infer<typeof listUsersSchema>;
```

---

## Pagination

### Cursor-Based (Preferred for Large Datasets)

```typescript
// Response format
type CursorPaginatedResponse<T> = {
  data: T[];
  pagination: {
    hasMore: boolean;
    nextCursor: string | null;
    prevCursor: string | null;
  };
};

// Implementation
async function listUsers(cursor?: string, limit = 20) {
  const items = await db
    .select()
    .from(users)
    .where(cursor ? gt(users.id, cursor) : undefined)
    .orderBy(asc(users.id))
    .limit(limit + 1); // Fetch one extra to detect hasMore

  const hasMore = items.length > limit;
  const data = hasMore ? items.slice(0, -1) : items;

  return {
    data,
    pagination: {
      hasMore,
      nextCursor: hasMore ? data[data.length - 1].id : null,
      prevCursor: cursor ?? null,
    },
  };
}
```

### Offset-Based (Simple, Good for Small Datasets)

```typescript
type OffsetPaginatedResponse<T> = {
  data: T[];
  pagination: {
    total: number;
    limit: number;
    offset: number;
    hasMore: boolean;
  };
};

async function listUsers(offset = 0, limit = 20) {
  const [items, [{ count }]] = await Promise.all([
    db.select().from(users).limit(limit).offset(offset).orderBy(desc(users.createdAt)),
    db.select({ count: sql<number>`count(*)` }).from(users),
  ]);

  return {
    data: items,
    pagination: {
      total: Number(count),
      limit,
      offset,
      hasMore: offset + limit < Number(count),
    },
  };
}
```

**When to use which:**
- **Cursor**: Real-time feeds, infinite scroll, large datasets (>10k rows)
- **Offset**: Admin dashboards, page-numbered UIs, small datasets

---

## Filtering & Sorting

```typescript
// Query parameter schema
const filterSchema = z.object({
  status: z.enum(["active", "inactive", "pending"]).optional(),
  role: z.enum(["user", "admin"]).optional(),
  search: z.string().max(200).optional(),
  createdAfter: z.coerce.date().optional(),
  createdBefore: z.coerce.date().optional(),
  sortBy: z.enum(["createdAt", "name", "email"]).default("createdAt"),
  order: z.enum(["asc", "desc"]).default("desc"),
});

// Dynamic filter builder (Drizzle example)
function buildFilters(query: z.infer<typeof filterSchema>) {
  const conditions = [];
  if (query.status) conditions.push(eq(users.status, query.status));
  if (query.role) conditions.push(eq(users.role, query.role));
  if (query.search) conditions.push(ilike(users.name, `%${query.search}%`));
  if (query.createdAfter) conditions.push(gte(users.createdAt, query.createdAfter));
  if (query.createdBefore) conditions.push(lte(users.createdAt, query.createdBefore));

  return conditions.length > 0 ? and(...conditions) : undefined;
}
```

---

## API Versioning

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| URL path | `/api/v1/users` | Explicit, easy to route | URL pollution |
| Header | `Accept: application/vnd.api+json;version=1` | Clean URLs | Hidden, harder to test |
| Query param | `/api/users?version=1` | Easy to test | Easy to forget |

**Recommendation:** Use URL path versioning (`/api/v1/`). It is the most explicit, cacheable, and debuggable approach.

```typescript
// Hono example
const v1 = new Hono().basePath("/api/v1");
const v2 = new Hono().basePath("/api/v2");

v1.get("/users", listUsersV1);
v2.get("/users", listUsersV2);

app.route("/", v1);
app.route("/", v2);
```

---

## Rate Limiting

```typescript
// Simple sliding window with headers
type RateLimitInfo = {
  limit: number;
  remaining: number;
  reset: number; // Unix timestamp
};

// Standard response headers
function setRateLimitHeaders(c: Context, info: RateLimitInfo) {
  c.header("X-RateLimit-Limit", String(info.limit));
  c.header("X-RateLimit-Remaining", String(info.remaining));
  c.header("X-RateLimit-Reset", String(info.reset));
}

// 429 response
{
  "type": "https://api.example.com/errors/rate-limit",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Try again in 30 seconds.",
}
```

---

## CORS Configuration

```typescript
import { cors } from "hono/cors";

app.use("*", cors({
  origin: ["https://app.example.com", "https://admin.example.com"],
  allowMethods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
  allowHeaders: ["Content-Type", "Authorization", "X-Request-ID"],
  exposeHeaders: ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
  maxAge: 3600,
  credentials: true,
}));

// Development: allow all origins
app.use("*", cors({ origin: "*" }));
```

---

## Hono Framework Overview

Hono is a lightweight, ultrafast web framework for any JS runtime. See `references/hono-patterns.md` for full patterns.

```typescript
import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";

const app = new Hono();

// Validated route
app.post(
  "/api/v1/users",
  zValidator("json", createUserSchema),
  async (c) => {
    const body = c.req.valid("json");
    const user = await createUser(body);
    return c.json(user, 201);
  },
);

// Query validation
app.get(
  "/api/v1/users",
  zValidator("query", listUsersSchema),
  async (c) => {
    const query = c.req.valid("query");
    const result = await listUsers(query);
    return c.json(result);
  },
);

export default app;
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Using `200` for creation | Return `201 Created` with `Location` header |
| Exposing internal IDs | Use UUIDs for public-facing identifiers |
| No validation on query params | Validate with Zod (coerce numbers/dates) |
| Inconsistent error format | Always return RFC 7807 `ProblemDetail` |
| Nesting resources 3+ levels | Flatten: `/posts/:id` instead of `/users/:uid/blogs/:bid/posts/:pid` |
| Not paginating list endpoints | Always paginate; default to 20 items |
| Missing CORS for browser clients | Configure `cors()` middleware explicitly |
| Returning `500` for client errors | Map known errors to `4xx` status codes |
| Version in request body | Use URL path or header for versioning |
| No rate limit headers | Always return `X-RateLimit-*` headers |
