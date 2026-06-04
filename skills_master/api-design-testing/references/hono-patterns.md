# Hono Framework Patterns

Hono is an ultrafast, lightweight web framework that runs on any JavaScript runtime (Bun, Deno, Node.js, Cloudflare Workers, Vercel Edge).

## Setup

```bash
# Create new project
npm create hono@latest my-api

# Or add to existing project
npm install hono
```

```typescript
// src/index.ts
import { Hono } from "hono";

const app = new Hono();

app.get("/", (c) => c.json({ message: "Hello Hono" }));

export default app; // Works with Bun, Deno, Cloudflare Workers

// For Node.js
import { serve } from "@hono/node-server";
serve({ fetch: app.fetch, port: 3000 });
```

---

## Routing

### Basic Routes

```typescript
const app = new Hono();

app.get("/users", listUsers);
app.get("/users/:id", getUser);
app.post("/users", createUser);
app.patch("/users/:id", updateUser);
app.delete("/users/:id", deleteUser);

// Path parameters
app.get("/users/:id", (c) => {
  const id = c.req.param("id");
  return c.json({ id });
});

// Query parameters
app.get("/users", (c) => {
  const search = c.req.query("search");
  const limit = c.req.query("limit");
  return c.json({ search, limit });
});

// Wildcard
app.get("/files/*", (c) => {
  const path = c.req.path;
  return c.text(`File: ${path}`);
});
```

### Route Groups

```typescript
// Group routes with shared prefix
const users = new Hono()
  .get("/", listUsers)
  .get("/:id", getUser)
  .post("/", createUser)
  .patch("/:id", updateUser)
  .delete("/:id", deleteUser);

const posts = new Hono()
  .get("/", listPosts)
  .get("/:id", getPost)
  .post("/", createPost);

// Mount groups
const api = new Hono().basePath("/api/v1");
api.route("/users", users);
api.route("/posts", posts);

const app = new Hono();
app.route("/", api);
```

### Chained Routes

```typescript
const app = new Hono()
  .basePath("/api/v1")
  .get("/health", (c) => c.json({ status: "ok" }))
  .get("/users", listUsers)
  .post("/users", createUser);
```

---

## Middleware

### Built-in Middleware

```typescript
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { prettyJSON } from "hono/pretty-json";
import { secureHeaders } from "hono/secure-headers";
import { timing } from "hono/timing";
import { compress } from "hono/compress";

const app = new Hono();

// Apply globally
app.use("*", logger());
app.use("*", secureHeaders());
app.use("*", timing());
app.use("*", compress());
app.use("*", prettyJSON());
app.use("*", cors({
  origin: ["https://app.example.com"],
  allowMethods: ["GET", "POST", "PUT", "PATCH", "DELETE"],
  credentials: true,
}));
```

### Custom Middleware

```typescript
import { createMiddleware } from "hono/factory";
import type { Context, Next } from "hono";

// Simple middleware
const requestId = createMiddleware(async (c, next) => {
  const id = crypto.randomUUID();
  c.set("requestId", id);
  c.header("X-Request-ID", id);
  await next();
});

// Auth middleware
const authMiddleware = createMiddleware<{
  Variables: { userId: string; userRole: string };
}>(async (c, next) => {
  const token = c.req.header("Authorization")?.replace("Bearer ", "");
  if (!token) {
    return c.json({ type: "https://api.example.com/errors/unauthorized", title: "Unauthorized", status: 401 }, 401);
  }
  const payload = await verifyToken(token);
  c.set("userId", payload.sub);
  c.set("userRole", payload.role);
  await next();
});

// Role guard
function requireRole(...roles: string[]) {
  return createMiddleware(async (c, next) => {
    const userRole = c.get("userRole");
    if (!roles.includes(userRole)) {
      return c.json({ type: "https://api.example.com/errors/forbidden", title: "Forbidden", status: 403 }, 403);
    }
    await next();
  });
}

// Usage
app.use("/api/*", authMiddleware);
app.delete("/api/v1/users/:id", requireRole("admin"), deleteUser);
```

### Error Handling Middleware

```typescript
import { HTTPException } from "hono/http-exception";

// Global error handler
app.onError((err, c) => {
  if (err instanceof HTTPException) {
    return c.json(
      { type: "https://api.example.com/errors/http", title: err.message, status: err.status },
      err.status,
    );
  }
  console.error(err);
  return c.json(
    { type: "https://api.example.com/errors/internal", title: "Internal Server Error", status: 500 },
    500,
  );
});

// Not found handler
app.notFound((c) => {
  return c.json(
    { type: "https://api.example.com/errors/not-found", title: "Not Found", status: 404, instance: c.req.path },
    404,
  );
});

// Throw in handlers
app.get("/users/:id", async (c) => {
  const user = await findUser(c.req.param("id"));
  if (!user) throw new HTTPException(404, { message: "User not found" });
  return c.json(user);
});
```

---

## Validation with Zod

```bash
npm install @hono/zod-validator
```

```typescript
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(["user", "admin"]).default("user"),
});

const listQuerySchema = z.object({
  limit: z.coerce.number().int().min(1).max(100).default(20),
  offset: z.coerce.number().int().min(0).default(0),
  search: z.string().optional(),
});

const idParamSchema = z.object({
  id: z.string().uuid(),
});

// Validate JSON body
app.post("/api/v1/users", zValidator("json", createUserSchema), async (c) => {
  const body = c.req.valid("json"); // Fully typed
  const user = await createUser(body);
  return c.json(user, 201);
});

// Validate query parameters
app.get("/api/v1/users", zValidator("query", listQuerySchema), async (c) => {
  const query = c.req.valid("query"); // { limit: number, offset: number, search?: string }
  return c.json(await listUsers(query));
});

// Validate path parameters
app.get("/api/v1/users/:id", zValidator("param", idParamSchema), async (c) => {
  const { id } = c.req.valid("param");
  return c.json(await getUser(id));
});

// Multiple validators on one route
app.patch(
  "/api/v1/users/:id",
  zValidator("param", idParamSchema),
  zValidator("json", createUserSchema.partial()),
  async (c) => {
    const { id } = c.req.valid("param");
    const body = c.req.valid("json");
    return c.json(await updateUser(id, body));
  },
);

// Custom error handler for validation
app.post(
  "/api/v1/users",
  zValidator("json", createUserSchema, (result, c) => {
    if (!result.success) {
      return c.json({
        type: "https://api.example.com/errors/validation",
        title: "Validation Error",
        status: 422,
        errors: result.error.issues.map((i) => ({
          field: i.path.join("."),
          message: i.message,
          code: i.code,
        })),
      }, 422);
    }
  }),
  createUserHandler,
);
```

---

## OpenAPI Integration

```bash
npm install @hono/zod-openapi
```

```typescript
import { OpenAPIHono, createRoute, z } from "@hono/zod-openapi";

const app = new OpenAPIHono();

// Define a route with OpenAPI metadata
const getUserRoute = createRoute({
  method: "get",
  path: "/api/v1/users/{id}",
  tags: ["Users"],
  summary: "Get a user by ID",
  request: {
    params: z.object({
      id: z.string().uuid().openapi({ description: "User ID", example: "550e8400-e29b-41d4-a716-446655440000" }),
    }),
  },
  responses: {
    200: {
      description: "User found",
      content: {
        "application/json": {
          schema: z.object({
            id: z.string().uuid(),
            email: z.string().email(),
            name: z.string(),
          }).openapi("User"),
        },
      },
    },
    404: {
      description: "User not found",
      content: {
        "application/json": {
          schema: z.object({
            type: z.string(),
            title: z.string(),
            status: z.number(),
          }).openapi("ProblemDetail"),
        },
      },
    },
  },
});

// Register the route handler (fully typed from schema)
app.openapi(getUserRoute, async (c) => {
  const { id } = c.req.valid("param");
  const user = await findUser(id);
  if (!user) {
    return c.json({ type: "not-found", title: "Not Found", status: 404 }, 404);
  }
  return c.json(user, 200);
});

// Auto-generate and serve OpenAPI doc
app.doc("/api/openapi.json", {
  openapi: "3.1.0",
  info: { title: "My API", version: "1.0.0" },
});

// Serve Swagger UI
import { swaggerUI } from "@hono/swagger-ui";
app.get("/docs", swaggerUI({ url: "/api/openapi.json" }));
```

---

## RPC Mode

Hono RPC provides end-to-end type safety between server and client without code generation.

### Server

```typescript
// src/server.ts
import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";

const app = new Hono()
  .basePath("/api")
  .get("/users", zValidator("query", z.object({ limit: z.coerce.number().default(20) })), async (c) => {
    const { limit } = c.req.valid("query");
    const users = await listUsers(limit);
    return c.json({ users });
  })
  .post("/users", zValidator("json", z.object({ email: z.string().email(), name: z.string() })), async (c) => {
    const body = c.req.valid("json");
    const user = await createUser(body);
    return c.json({ user }, 201);
  })
  .get("/users/:id", async (c) => {
    const user = await getUser(c.req.param("id"));
    return c.json({ user });
  });

// Export the type for the client
export type AppType = typeof app;
export default app;
```

### Client

```typescript
// src/client.ts
import { hc } from "hono/client";
import type { AppType } from "./server";

const client = hc<AppType>("http://localhost:3000");

// Fully typed — autocomplete for paths, params, and responses
const res = await client.api.users.$get({ query: { limit: 10 } });
const { users } = await res.json(); // typed!

const res2 = await client.api.users.$post({ json: { email: "a@b.com", name: "Alice" } });
const { user } = await res2.json(); // typed!

const res3 = await client.api.users[":id"].$get({ param: { id: "123" } });
const { user: u } = await res3.json(); // typed!
```

---

## Testing

### Unit Testing Handlers

```typescript
import { describe, it, expect } from "vitest";
import app from "./index";

describe("Users API", () => {
  it("GET /api/v1/users returns paginated list", async () => {
    const res = await app.request("/api/v1/users?limit=5");
    expect(res.status).toBe(200);

    const body = await res.json();
    expect(body.data).toBeInstanceOf(Array);
    expect(body.pagination.limit).toBe(5);
  });

  it("POST /api/v1/users creates user", async () => {
    const res = await app.request("/api/v1/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "test@example.com", name: "Test" }),
    });
    expect(res.status).toBe(201);

    const body = await res.json();
    expect(body.email).toBe("test@example.com");
  });

  it("POST /api/v1/users rejects invalid email", async () => {
    const res = await app.request("/api/v1/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "not-an-email", name: "Test" }),
    });
    expect(res.status).toBe(422);

    const body = await res.json();
    expect(body.errors[0].field).toBe("email");
  });

  it("GET /api/v1/users/:id returns 404 for missing user", async () => {
    const res = await app.request("/api/v1/users/550e8400-e29b-41d4-a716-446655440000");
    expect(res.status).toBe(404);
  });
});
```

### Testing with RPC Client

```typescript
import { testClient } from "hono/testing";
import app from "./index";

describe("Users API (RPC)", () => {
  const client = testClient(app);

  it("lists users", async () => {
    const res = await client.api.v1.users.$get({ query: { limit: 5 } });
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.data).toHaveLength(5);
  });
});
```

### Testing Middleware

```typescript
import { Hono } from "hono";
import { authMiddleware } from "./middleware";

describe("Auth Middleware", () => {
  const app = new Hono();
  app.use("*", authMiddleware);
  app.get("/protected", (c) => c.json({ userId: c.get("userId") }));

  it("rejects unauthenticated requests", async () => {
    const res = await app.request("/protected");
    expect(res.status).toBe(401);
  });

  it("passes authenticated requests", async () => {
    const res = await app.request("/protected", {
      headers: { Authorization: `Bearer ${validToken}` },
    });
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body.userId).toBeDefined();
  });
});
```

---

## Common Patterns

### Request ID + Structured Logging

```typescript
import { logger } from "hono/logger";

app.use("*", async (c, next) => {
  const requestId = c.req.header("X-Request-ID") ?? crypto.randomUUID();
  c.set("requestId", requestId);
  c.header("X-Request-ID", requestId);
  await next();
});

app.use("*", logger());
```

### Graceful Shutdown (Node.js)

```typescript
import { serve } from "@hono/node-server";

const server = serve({ fetch: app.fetch, port: 3000 });

process.on("SIGTERM", () => {
  console.log("Shutting down...");
  server.close(() => process.exit(0));
});
```

### Environment Variables with Type Safety

```typescript
type Bindings = {
  DATABASE_URL: string;
  JWT_SECRET: string;
  NODE_ENV: "development" | "production";
};

const app = new Hono<{ Bindings: Bindings }>();

app.get("/", (c) => {
  const dbUrl = c.env.DATABASE_URL; // typed
  return c.text("ok");
});
```
