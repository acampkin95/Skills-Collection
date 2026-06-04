# API Reference Documentation

## TypeDoc — TypeScript API Docs

### Setup

```bash
npm install --save-dev typedoc typedoc-plugin-markdown
```

### typedoc.json Configuration

```json
{
  "$schema": "https://typedoc.org/schema.json",
  "entryPoints": ["src/index.ts"],
  "out": "docs/api",
  "plugin": ["typedoc-plugin-markdown"],
  "exclude": ["**/*.test.ts", "**/*.spec.ts", "**/node_modules/**"],
  "excludePrivate": true,
  "excludeProtected": false,
  "excludeInternal": true,
  "includeVersion": true,
  "readme": "none",
  "githubPages": false,
  "hideGenerator": true,
  "categorizeByGroup": true,
  "categoryOrder": ["Core", "Utilities", "Types", "*"],
  "sort": ["source-order"],
  "navigation": {
    "includeCategories": true,
    "includeGroups": true
  }
}
```

### Markdown Output (for Docusaurus/Nextra)

```json
{
  "plugin": ["typedoc-plugin-markdown"],
  "out": "docs/api-reference",
  "outputFileStrategy": "modules",
  "entryFileName": "index",
  "hidePageTitle": false,
  "hidePageHeader": false,
  "useCodeBlocks": true,
  "expandObjects": true,
  "parametersFormat": "table",
  "enumMembersFormat": "table",
  "typeDeclarationFormat": "table"
}
```

### Docusaurus Integration

```bash
npm install --save-dev docusaurus-plugin-typedoc typedoc typedoc-plugin-markdown
```

```typescript
// docusaurus.config.ts
plugins: [
  [
    'docusaurus-plugin-typedoc',
    {
      entryPoints: ['../src/index.ts'],
      tsconfig: '../tsconfig.json',
      out: 'api',
      sidebar: {
        categoryLabel: 'API Reference',
        position: 4,
      },
      watch: process.env.TYPEDOC_WATCH === 'true',
    },
  ],
],
```

### JSDoc Annotations for Better Output

```typescript
/**
 * Client for interacting with the API.
 *
 * @example
 * ```typescript
 * const client = new APIClient({
 *   apiKey: 'your-key',
 *   baseUrl: 'https://api.example.com',
 * });
 *
 * const users = await client.users.list();
 * ```
 *
 * @category Core
 * @see {@link APIClientConfig} for configuration options
 */
export class APIClient {
  /**
   * Creates a new API client instance.
   *
   * @param config - Configuration options for the client
   * @throws {ConfigError} If required config values are missing
   */
  constructor(private config: APIClientConfig) {}

  /**
   * Fetches a user by their unique identifier.
   *
   * @param id - The user's unique ID
   * @returns The user object if found
   * @throws {NotFoundError} If the user does not exist
   * @throws {AuthError} If the API key is invalid
   *
   * @example
   * ```typescript
   * const user = await client.getUser('usr_123');
   * console.log(user.name); // "Alice"
   * ```
   *
   * @since 1.0.0
   * @deprecated Use {@link APIClient.users.get} instead
   */
  async getUser(id: string): Promise<User> {
    // ...
  }

  /**
   * @internal
   * Internal helper — excluded from docs when excludeInternal is true
   */
  private async _fetch(url: string): Promise<Response> {
    // ...
  }
}

/**
 * Configuration for the API client.
 *
 * @category Types
 */
export interface APIClientConfig {
  /** API key for authentication */
  apiKey: string;

  /** Base URL for the API. Defaults to production. */
  baseUrl?: string;

  /** Request timeout in milliseconds. @defaultValue 30000 */
  timeout?: number;

  /** Maximum number of retry attempts. @defaultValue 3 */
  maxRetries?: number;
}
```

### Generate Docs

```bash
# One-time generation
npx typedoc

# Watch mode
npx typedoc --watch

# With custom config
npx typedoc --options typedoc.json

# Add to package.json scripts
```

```json
{
  "scripts": {
    "docs:api": "typedoc",
    "docs:api:watch": "typedoc --watch",
    "docs:build": "npm run docs:api && npm run build"
  }
}
```

---

## OpenAPI Documentation Renderers

### Redoc

Generates beautiful, responsive API documentation from OpenAPI specs.

#### Standalone HTML

```bash
npm install -g @redocly/cli
redocly build-docs openapi.yaml --output docs/api.html
```

#### React Component

```bash
npm install redoc
```

```tsx
// components/APIReference.tsx
import { RedocStandalone } from 'redoc';

export default function APIReference() {
  return (
    <RedocStandalone
      specUrl="/openapi.yaml"
      options={{
        theme: {
          colors: {
            primary: { main: '#3578e5' },
          },
          typography: {
            fontFamily: 'Inter, sans-serif',
            headings: { fontFamily: 'Inter, sans-serif' },
          },
          sidebar: {
            width: '280px',
          },
        },
        scrollYOffset: 64,
        hideHostname: false,
        expandResponses: '200,201',
        requiredPropsFirst: true,
        sortPropsAlphabetically: true,
        pathInMiddlePanel: true,
        hideDownloadButton: false,
        nativeScrollbars: true,
      }}
    />
  );
}
```

#### Docusaurus Plugin

```bash
npm install docusaurus-theme-redoc redocusaurus
```

```typescript
// docusaurus.config.ts
presets: [
  [
    'redocusaurus',
    {
      specs: [
        {
          id: 'core-api',
          spec: 'openapi/core.yaml',
          route: '/api/',
        },
        {
          id: 'admin-api',
          spec: 'openapi/admin.yaml',
          route: '/api/admin/',
        },
      ],
      theme: {
        primaryColor: '#3578e5',
      },
    },
  ],
],
```

### Scalar (Modern Alternative to Swagger UI)

```bash
npm install @scalar/api-reference
```

```tsx
// React component
import { ApiReference } from '@scalar/api-reference-react';
import '@scalar/api-reference-react/style.css';

export default function APIPlayground() {
  return (
    <ApiReference
      configuration={{
        spec: {
          url: '/openapi.yaml',
          // or inline: content: openApiSpec,
        },
        theme: 'purple',
        layout: 'modern',
        darkMode: true,
        hiddenClients: ['unirest'],
        defaultHttpClient: {
          targetKey: 'javascript',
          clientKey: 'fetch',
        },
        authentication: {
          preferredSecurityScheme: 'bearerAuth',
          http: {
            bearer: {
              token: '',
            },
          },
        },
      }}
    />
  );
}
```

#### Scalar CDN (Zero Build)

```html
<!DOCTYPE html>
<html>
  <head>
    <title>API Reference</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body>
    <script
      id="api-reference"
      data-url="/openapi.yaml"
      data-configuration='{"theme":"purple"}'
    ></script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  </body>
</html>
```

### Stoplight Elements

```bash
npm install @stoplight/elements
```

```tsx
import { API } from '@stoplight/elements';
import '@stoplight/elements/styles.min.css';

export default function APIReference() {
  return (
    <API
      apiDescriptionUrl="/openapi.yaml"
      router="hash"
      layout="sidebar"
      hideSchemas={false}
      hideInternal={true}
      tryItCredentialsPolicy="same-origin"
      logo="/logo.svg"
    />
  );
}
```

---

## Swagger UI — Interactive API Playground

### Setup

```bash
npm install swagger-ui-react
```

### React Integration

```tsx
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';

export default function APIExplorer() {
  return (
    <SwaggerUI
      url="/openapi.yaml"
      docExpansion="list"
      defaultModelsExpandDepth={2}
      deepLinking={true}
      tryItOutEnabled={true}
      filter={true}
      displayRequestDuration={true}
      requestInterceptor={(req) => {
        // Add auth header
        req.headers['Authorization'] = `Bearer ${getToken()}`;
        return req;
      }}
    />
  );
}
```

### Custom Swagger UI Page (Docusaurus)

```tsx
// src/pages/api-playground.tsx
import React from 'react';
import Layout from '@theme/Layout';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';

export default function APIPlayground() {
  return (
    <Layout title="API Playground" description="Interactive API Explorer">
      <div style={{ padding: '20px' }}>
        <SwaggerUI
          url="/openapi.yaml"
          docExpansion="list"
          tryItOutEnabled={true}
        />
      </div>
    </Layout>
  );
}
```

---

## OpenAPI Spec Patterns

### Minimal OpenAPI 3.1 Spec

```yaml
openapi: 3.1.0
info:
  title: My API
  version: 2.0.0
  description: |
    REST API for managing users and resources.

    ## Authentication
    All endpoints require a Bearer token in the Authorization header.
  contact:
    name: API Support
    email: api@example.com
    url: https://docs.example.com/support
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.example.com/v2
    description: Production
  - url: https://staging-api.example.com/v2
    description: Staging

security:
  - bearerAuth: []

tags:
  - name: Users
    description: User management operations
  - name: Resources
    description: Resource CRUD operations

paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
      tags: [Users]
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
          description: Maximum number of users to return
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
          description: Number of users to skip
        - name: sort
          in: query
          schema:
            type: string
            enum: [created_at, name, email]
            default: created_at
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  meta:
                    $ref: '#/components/schemas/PaginationMeta'
              example:
                data:
                  - id: "usr_123"
                    name: "Alice"
                    email: "alice@example.com"
                meta:
                  total: 42
                  limit: 20
                  offset: 0

    post:
      operationId: createUser
      summary: Create a new user
      tags: [Users]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            example:
              name: "Bob"
              email: "bob@example.com"
              role: "member"
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          description: Email already exists

  /users/{id}:
    get:
      operationId: getUser
      summary: Get a user by ID
      tags: [Users]
      parameters:
        - $ref: '#/components/parameters/UserId'
      responses:
        '200':
          description: User details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  parameters:
    UserId:
      name: id
      in: path
      required: true
      schema:
        type: string
        pattern: '^usr_[a-zA-Z0-9]+$'
      description: User ID (prefixed with `usr_`)

  schemas:
    User:
      type: object
      required: [id, name, email, createdAt]
      properties:
        id:
          type: string
          example: "usr_123"
        name:
          type: string
          example: "Alice Smith"
        email:
          type: string
          format: email
        role:
          type: string
          enum: [admin, member, viewer]
          default: member
        createdAt:
          type: string
          format: date-time

    CreateUserRequest:
      type: object
      required: [name, email]
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 100
        email:
          type: string
          format: email
        role:
          type: string
          enum: [admin, member, viewer]
          default: member

    PaginationMeta:
      type: object
      properties:
        total:
          type: integer
        limit:
          type: integer
        offset:
          type: integer

  responses:
    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    Error:
      type: object
      properties:
        code:
          type: string
        message:
          type: string
```

---

## SDK Documentation Patterns

### SDK Quickstart Page Template

```mdx
---
title: SDK Quick Start
---

import { Tabs } from 'nextra/components';   {/* or use Docusaurus Tabs */}

# Quick Start

## Installation

<Tabs items={['npm', 'yarn', 'pnpm']}>
  <Tabs.Tab>
```bash
npm install @my-org/sdk
```
  </Tabs.Tab>
  <Tabs.Tab>
```bash
yarn add @my-org/sdk
```
  </Tabs.Tab>
  <Tabs.Tab>
```bash
pnpm add @my-org/sdk
```
  </Tabs.Tab>
</Tabs>

## Initialize the Client

```typescript
import { MyClient } from '@my-org/sdk';

const client = new MyClient({
  apiKey: process.env.MY_API_KEY,
});
```

## Make Your First Request

```typescript
// List users
const { data: users } = await client.users.list({
  limit: 10,
});

console.log(users);
// [{ id: 'usr_123', name: 'Alice', ... }]
```

## Error Handling

```typescript
import { MyClient, APIError, RateLimitError } from '@my-org/sdk';

try {
  const user = await client.users.get('usr_invalid');
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log(`Rate limited. Retry after ${error.retryAfter}s`);
  } else if (error instanceof APIError) {
    console.log(`API error: ${error.code} - ${error.message}`);
  }
}
```
```

### SDK Method Reference Template

```mdx
---
title: client.users.list()
---

# client.users.list()

Retrieves a paginated list of users.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | `number` | No | `20` | Max results (1-100) |
| `offset` | `number` | No | `0` | Pagination offset |
| `sort` | `'created_at' \| 'name'` | No | `'created_at'` | Sort field |
| `order` | `'asc' \| 'desc'` | No | `'desc'` | Sort order |

## Returns

`Promise<PaginatedResponse<User>>`

| Field | Type | Description |
|-------|------|-------------|
| `data` | `User[]` | Array of user objects |
| `meta.total` | `number` | Total matching users |
| `meta.limit` | `number` | Applied limit |
| `meta.offset` | `number` | Applied offset |

## Examples

### Basic Usage

```typescript
const { data: users } = await client.users.list();
```

### With Pagination

```typescript
const page1 = await client.users.list({ limit: 10, offset: 0 });
const page2 = await client.users.list({ limit: 10, offset: 10 });
```

### Iterate All Users

```typescript
for await (const user of client.users.listAutoPaginate()) {
  console.log(user.name);
}
```

## Errors

| Code | Description |
|------|-------------|
| `401` | Invalid or missing API key |
| `429` | Rate limit exceeded |
| `500` | Internal server error |
```

---

## Auto-Generated Code Samples

### openapi-snippet (Multi-Language)

```bash
npm install openapi-snippet
```

```typescript
// scripts/generate-samples.ts
import OpenAPISnippet from 'openapi-snippet';
import { readFileSync, writeFileSync } from 'fs';
import yaml from 'js-yaml';

const spec = yaml.load(readFileSync('openapi.yaml', 'utf8')) as any;
const targets = ['node_fetch', 'python_requests', 'shell_curl', 'go_native'];

for (const [path, methods] of Object.entries(spec.paths)) {
  for (const [method, operation] of Object.entries(methods as any)) {
    if (typeof operation !== 'object') continue;

    const snippets = OpenAPISnippet.getEndpointSnippets(
      spec,
      path,
      method.toUpperCase(),
      targets
    );

    console.log(`\n## ${method.toUpperCase()} ${path}`);
    for (const snippet of snippets.snippets) {
      console.log(`### ${snippet.title}`);
      console.log('```');
      console.log(snippet.content);
      console.log('```');
    }
  }
}
```

### curl Examples in MDX

```mdx
## Create User

```bash
curl -X POST https://api.example.com/v2/users \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "role": "member"
  }'
```

**Response** (201 Created):

```json
{
  "id": "usr_abc123",
  "name": "Alice",
  "email": "alice@example.com",
  "role": "member",
  "createdAt": "2024-01-15T10:30:00Z"
}
```
```

### Multi-Language Code Samples Component

```tsx
// components/CodeSamples.tsx
import React from 'react';

interface CodeSample {
  language: string;
  label: string;
  code: string;
}

interface Props {
  method: string;
  path: string;
  samples: CodeSample[];
}

export function CodeSamples({ method, path, samples }: Props) {
  // Use your framework's tab component (Docusaurus Tabs, Nextra Tabs, etc.)
  return (
    <div>
      <h4>
        <code>{method}</code> <code>{path}</code>
      </h4>
      {/* Render tabs with code blocks per language */}
    </div>
  );
}
```

Usage:

```mdx
<CodeSamples
  method="POST"
  path="/api/users"
  samples={[
    {
      language: "typescript",
      label: "Node.js",
      code: `const user = await client.users.create({
  name: "Alice",
  email: "alice@example.com",
});`,
    },
    {
      language: "python",
      label: "Python",
      code: `user = client.users.create(
    name="Alice",
    email="alice@example.com",
)`,
    },
    {
      language: "bash",
      label: "cURL",
      code: `curl -X POST https://api.example.com/v2/users \\
  -H "Authorization: Bearer $API_KEY" \\
  -d '{"name":"Alice","email":"alice@example.com"}'`,
    },
  ]}
/>
```

---

## CI Pipeline: Auto-Generate All Docs

```yaml
# .github/workflows/docs.yml
name: Generate API Docs

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'openapi/**'
      - 'docs/**'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci

      # 1. Generate TypeDoc API reference
      - run: npx typedoc --options typedoc.json

      # 2. Validate OpenAPI spec
      - run: npx @redocly/cli lint openapi/core.yaml

      # 3. Generate OpenAPI HTML (Redoc)
      - run: npx @redocly/cli build-docs openapi/core.yaml --output docs/static/api.html

      # 4. Build documentation site
      - run: npm run build
        working-directory: docs

      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs/build
```

---

## Comparison: OpenAPI Renderers

| Feature | Redoc | Scalar | Stoplight Elements | Swagger UI |
|---------|-------|--------|-------------------|------------|
| **Look & feel** | Clean, 3-panel | Modern, polished | Professional | Classic |
| **Try-it-out** | No (Pro only) | Yes (built-in) | Yes | Yes |
| **Code samples** | Auto-generated | Auto-generated | Auto-generated | No |
| **Auth support** | Display only | Interactive | Interactive | Interactive |
| **Bundle size** | ~300KB | ~200KB | ~500KB | ~400KB |
| **React component** | Yes | Yes | Yes | Yes |
| **SSR support** | Yes | Yes | Partial | No |
| **Theming** | Extensive | Good | Good | Limited |
| **Best for** | Public docs | Developer portal | Enterprise | Internal tools |

### Recommendation

- **Public-facing API docs**: Redoc (clean) or Scalar (modern + interactive)
- **Developer portal with try-it**: Scalar
- **Enterprise/internal**: Stoplight Elements
- **Quick internal tool**: Swagger UI
