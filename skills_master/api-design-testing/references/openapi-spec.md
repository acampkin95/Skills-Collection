# OpenAPI 3.1 Specification Reference

## Writing OpenAPI 3.1

OpenAPI 3.1 is fully compatible with JSON Schema draft 2020-12.

### Minimal Spec Structure

```yaml
openapi: "3.1.0"
info:
  title: My API
  version: "1.0.0"
  description: REST API for managing users and posts.
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: http://localhost:3000/v1
    description: Local development
paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
      tags: [Users]
      parameters:
        - $ref: "#/components/parameters/Limit"
        - $ref: "#/components/parameters/Offset"
      responses:
        "200":
          description: Paginated list of users
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/PaginatedUsers"
    post:
      operationId: createUser
      summary: Create a new user
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateUser"
      responses:
        "201":
          description: User created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
          headers:
            Location:
              schema:
                type: string
              description: URL of the created resource
        "422":
          $ref: "#/components/responses/ValidationError"
components:
  schemas:
    User:
      type: object
      required: [id, email, name, createdAt]
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
        role:
          type: string
          enum: [user, admin]
          default: user
        createdAt:
          type: string
          format: date-time
    CreateUser:
      type: object
      required: [email, name]
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100
        role:
          type: string
          enum: [user, admin]
          default: user
    ProblemDetail:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          format: uri
        title:
          type: string
        status:
          type: integer
        detail:
          type: string
        instance:
          type: string
        errors:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string
              code:
                type: string
  parameters:
    Limit:
      name: limit
      in: query
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20
    Offset:
      name: offset
      in: query
      schema:
        type: integer
        minimum: 0
        default: 0
  responses:
    ValidationError:
      description: Validation error
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ProblemDetail"
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
security:
  - BearerAuth: []
```

---

## Zod-to-OpenAPI (@asteasolutions/zod-to-openapi)

Generate OpenAPI specs directly from Zod schemas. This is the recommended approach — define schemas once, get validation AND documentation.

### Installation

```bash
npm install @asteasolutions/zod-to-openapi zod
```

### Setup

```typescript
import { OpenAPIRegistry, OpenApiGeneratorV31 } from "@asteasolutions/zod-to-openapi";
import { extendZodWithOpenApi } from "@asteasolutions/zod-to-openapi";
import { z } from "zod";

// Extend Zod with OpenAPI methods (call once at app startup)
extendZodWithOpenApi(z);
```

### Register Schemas

```typescript
const registry = new OpenAPIRegistry();

// Register reusable schema
const UserSchema = registry.register(
  "User",
  z.object({
    id: z.string().uuid().openapi({ example: "550e8400-e29b-41d4-a716-446655440000" }),
    email: z.string().email().openapi({ example: "user@example.com" }),
    name: z.string().openapi({ example: "Jane Doe" }),
    role: z.enum(["user", "admin"]).default("user"),
    createdAt: z.string().datetime(),
  }),
);

const CreateUserSchema = registry.register(
  "CreateUser",
  z.object({
    email: z.string().email(),
    name: z.string().min(1).max(100),
    role: z.enum(["user", "admin"]).default("user"),
  }),
);

// Register security scheme
registry.registerComponent("securitySchemes", "BearerAuth", {
  type: "http",
  scheme: "bearer",
  bearerFormat: "JWT",
});
```

### Register Endpoints

```typescript
// Register a path/route
registry.registerPath({
  method: "get",
  path: "/api/v1/users",
  tags: ["Users"],
  summary: "List all users",
  security: [{ BearerAuth: [] }],
  request: {
    query: z.object({
      limit: z.coerce.number().int().min(1).max(100).default(20),
      offset: z.coerce.number().int().min(0).default(0),
      search: z.string().optional(),
    }),
  },
  responses: {
    200: {
      description: "Paginated list of users",
      content: {
        "application/json": {
          schema: z.object({
            data: z.array(UserSchema),
            pagination: z.object({
              total: z.number(),
              limit: z.number(),
              offset: z.number(),
              hasMore: z.boolean(),
            }),
          }),
        },
      },
    },
  },
});

registry.registerPath({
  method: "post",
  path: "/api/v1/users",
  tags: ["Users"],
  summary: "Create a new user",
  security: [{ BearerAuth: [] }],
  request: {
    body: {
      content: {
        "application/json": { schema: CreateUserSchema },
      },
    },
  },
  responses: {
    201: {
      description: "User created",
      content: {
        "application/json": { schema: UserSchema },
      },
    },
    422: {
      description: "Validation error",
      content: {
        "application/json": {
          schema: z.object({
            type: z.string(),
            title: z.string(),
            status: z.number(),
            detail: z.string().optional(),
            errors: z.array(z.object({
              field: z.string(),
              message: z.string(),
              code: z.string(),
            })).optional(),
          }),
        },
      },
    },
  },
});
```

### Generate the Spec

```typescript
const generator = new OpenApiGeneratorV31(registry.definitions);

const doc = generator.generateDocument({
  openapi: "3.1.0",
  info: {
    title: "My API",
    version: "1.0.0",
    description: "REST API for managing users and posts.",
  },
  servers: [
    { url: "https://api.example.com/v1", description: "Production" },
    { url: "http://localhost:3000/v1", description: "Development" },
  ],
});

// Write to file for Swagger UI or other tools
import { writeFileSync } from "fs";
writeFileSync("openapi.json", JSON.stringify(doc, null, 2));
```

### Route to Serve the Spec (Hono)

```typescript
import { swaggerUI } from "@hono/swagger-ui";

// Serve OpenAPI JSON
app.get("/api/openapi.json", (c) => c.json(doc));

// Serve Swagger UI
app.get("/api/docs", swaggerUI({ url: "/api/openapi.json" }));
```

---

## Code Generation from OpenAPI

### Generate TypeScript Types

```bash
# openapi-typescript: types only (recommended)
npm install -D openapi-typescript
npx openapi-typescript ./openapi.json -o src/api-types.ts

# Usage
import type { paths, components } from "./api-types";
type User = components["schemas"]["User"];
type ListUsersResponse = paths["/api/v1/users"]["get"]["responses"]["200"]["content"]["application/json"];
```

### Generate API Client

```bash
# openapi-fetch: lightweight type-safe client
npm install openapi-fetch
```

```typescript
import createClient from "openapi-fetch";
import type { paths } from "./api-types";

const client = createClient<paths>({ baseUrl: "https://api.example.com/v1" });

// Fully typed request and response
const { data, error } = await client.GET("/api/v1/users", {
  params: { query: { limit: 10, search: "jane" } },
});
// data is typed as PaginatedUsers
```

---

## Swagger UI Setup

### Standalone HTML

```html
<!DOCTYPE html>
<html>
<head>
  <title>API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: "/api/openapi.json",
      dom_id: "#swagger-ui",
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
    });
  </script>
</body>
</html>
```

### With Hono (@hono/swagger-ui)

```bash
npm install @hono/swagger-ui
```

```typescript
import { swaggerUI } from "@hono/swagger-ui";

app.get("/docs", swaggerUI({ url: "/api/openapi.json" }));
```

---

## Best Practices

| Practice | Detail |
|----------|--------|
| Single source of truth | Define Zod schemas once, derive OpenAPI + types |
| Use `operationId` | Enables better code generation naming |
| Use `$ref` for reuse | Reference common schemas, parameters, responses |
| Add `examples` | Improves Swagger UI usability |
| Tag all endpoints | Group operations in Swagger UI |
| Version your spec | Include version in `info.version` |
| Validate spec | Use `swagger-cli validate openapi.json` |
| Generate in CI | Auto-generate spec on build, commit to repo |
