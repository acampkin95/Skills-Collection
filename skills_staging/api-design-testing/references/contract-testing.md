# API Contract Testing Reference

## MSW (Mock Service Worker)

MSW intercepts network requests at the service worker/network level. Use it for:
- Mocking API responses in tests (unit, integration, e2e)
- Development without a backend
- Testing error states and edge cases

### Installation

```bash
npm install -D msw
```

### Define Handlers

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from "msw";

const users = [
  { id: "1", email: "alice@example.com", name: "Alice", role: "admin" },
  { id: "2", email: "bob@example.com", name: "Bob", role: "user" },
];

export const handlers = [
  // GET /api/v1/users
  http.get("http://localhost:3000/api/v1/users", ({ request }) => {
    const url = new URL(request.url);
    const limit = Number(url.searchParams.get("limit") ?? 20);
    const offset = Number(url.searchParams.get("offset") ?? 0);
    const search = url.searchParams.get("search");

    let filtered = users;
    if (search) {
      filtered = users.filter((u) => u.name.toLowerCase().includes(search.toLowerCase()));
    }

    return HttpResponse.json({
      data: filtered.slice(offset, offset + limit),
      pagination: { total: filtered.length, limit, offset, hasMore: offset + limit < filtered.length },
    });
  }),

  // GET /api/v1/users/:id
  http.get("http://localhost:3000/api/v1/users/:id", ({ params }) => {
    const user = users.find((u) => u.id === params.id);
    if (!user) {
      return HttpResponse.json(
        { type: "not-found", title: "Not Found", status: 404 },
        { status: 404 },
      );
    }
    return HttpResponse.json(user);
  }),

  // POST /api/v1/users
  http.post("http://localhost:3000/api/v1/users", async ({ request }) => {
    const body = (await request.json()) as { email: string; name: string };

    if (!body.email || !body.email.includes("@")) {
      return HttpResponse.json(
        {
          type: "validation",
          title: "Validation Error",
          status: 422,
          errors: [{ field: "email", message: "Invalid email", code: "invalid_format" }],
        },
        { status: 422 },
      );
    }

    const newUser = { id: crypto.randomUUID(), ...body, role: "user" };
    return HttpResponse.json(newUser, { status: 201 });
  }),

  // DELETE /api/v1/users/:id
  http.delete("http://localhost:3000/api/v1/users/:id", () => {
    return new HttpResponse(null, { status: 204 });
  }),
];
```

### Setup for Tests (Node.js / Vitest)

```typescript
// src/mocks/server.ts
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);
```

```typescript
// src/setup-tests.ts (or vitest.setup.ts)
import { beforeAll, afterEach, afterAll } from "vitest";
import { server } from "./mocks/server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    setupFiles: ["./src/setup-tests.ts"],
  },
});
```

### Using in Tests

```typescript
import { describe, it, expect } from "vitest";
import { server } from "./mocks/server";
import { http, HttpResponse } from "msw";

describe("UserService", () => {
  it("fetches users", async () => {
    const response = await fetch("http://localhost:3000/api/v1/users?limit=10");
    const body = await response.json();

    expect(response.status).toBe(200);
    expect(body.data).toHaveLength(2);
    expect(body.pagination.total).toBe(2);
  });

  it("handles server errors", async () => {
    // Override handler for this specific test
    server.use(
      http.get("http://localhost:3000/api/v1/users", () => {
        return HttpResponse.json(
          { type: "internal", title: "Internal Server Error", status: 500 },
          { status: 500 },
        );
      }),
    );

    const response = await fetch("http://localhost:3000/api/v1/users");
    expect(response.status).toBe(500);
  });

  it("handles network errors", async () => {
    server.use(
      http.get("http://localhost:3000/api/v1/users", () => {
        return HttpResponse.error();
      }),
    );

    await expect(fetch("http://localhost:3000/api/v1/users")).rejects.toThrow();
  });
});
```

### Setup for Browser (Development Mocking)

```typescript
// src/mocks/browser.ts
import { setupWorker } from "msw/browser";
import { handlers } from "./handlers";

export const worker = setupWorker(...handlers);
```

```typescript
// src/main.tsx (or entry point)
async function enableMocking() {
  if (process.env.NODE_ENV !== "development") return;
  const { worker } = await import("./mocks/browser");
  return worker.start({ onUnhandledRequest: "bypass" });
}

enableMocking().then(() => {
  // Mount your app
  createRoot(document.getElementById("root")!).render(<App />);
});
```

```bash
# Generate the service worker script
npx msw init public/ --save
```

---

## Pact Contract Testing

Pact verifies that a consumer (frontend/client) and provider (API server) agree on the API contract. Tests run independently — no shared environment needed.

### Concepts

| Term | Meaning |
|------|---------|
| **Consumer** | The API client (React app, mobile app, another service) |
| **Provider** | The API server |
| **Pact** | A contract file (JSON) describing expected interactions |
| **Interaction** | A single request-response pair |
| **Pact Broker** | Central registry for pact files (optional) |

### Installation

```bash
# Consumer side
npm install -D @pact-foundation/pact

# Provider side
npm install -D @pact-foundation/pact
```

### Consumer Test (Generate Contract)

```typescript
// consumer/tests/user-api.pact.test.ts
import { PactV4, MatchersV3 } from "@pact-foundation/pact";
import path from "path";

const { like, eachLike, integer, string, uuid } = MatchersV3;

const provider = new PactV4({
  consumer: "WebApp",
  provider: "UserAPI",
  dir: path.resolve(process.cwd(), "pacts"),
});

describe("User API Contract", () => {
  it("returns a list of users", async () => {
    await provider
      .addInteraction()
      .given("users exist")
      .uponReceiving("a request to list users")
      .withRequest("GET", "/api/v1/users", (builder) => {
        builder.query({ limit: "10", offset: "0" });
      })
      .willRespondWith(200, (builder) => {
        builder
          .headers({ "Content-Type": "application/json" })
          .jsonBody({
            data: eachLike({
              id: uuid("550e8400-e29b-41d4-a716-446655440000"),
              email: string("alice@example.com"),
              name: string("Alice"),
              role: string("user"),
            }),
            pagination: {
              total: integer(2),
              limit: integer(10),
              offset: integer(0),
              hasMore: like(false),
            },
          });
      })
      .executeTest(async (mockServer) => {
        const response = await fetch(`${mockServer.url}/api/v1/users?limit=10&offset=0`);
        const body = await response.json();

        expect(response.status).toBe(200);
        expect(body.data).toBeInstanceOf(Array);
        expect(body.data[0]).toHaveProperty("id");
        expect(body.data[0]).toHaveProperty("email");
        expect(body.pagination.total).toBeGreaterThanOrEqual(0);
      });
  });

  it("creates a user", async () => {
    await provider
      .addInteraction()
      .uponReceiving("a request to create a user")
      .withRequest("POST", "/api/v1/users", (builder) => {
        builder
          .headers({ "Content-Type": "application/json" })
          .jsonBody({
            email: "newuser@example.com",
            name: "New User",
          });
      })
      .willRespondWith(201, (builder) => {
        builder
          .headers({ "Content-Type": "application/json" })
          .jsonBody({
            id: uuid(),
            email: string("newuser@example.com"),
            name: string("New User"),
            role: string("user"),
          });
      })
      .executeTest(async (mockServer) => {
        const response = await fetch(`${mockServer.url}/api/v1/users`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "newuser@example.com", name: "New User" }),
        });
        expect(response.status).toBe(201);

        const body = await response.json();
        expect(body.email).toBe("newuser@example.com");
      });
  });

  it("returns 404 for missing user", async () => {
    await provider
      .addInteraction()
      .given("user does not exist")
      .uponReceiving("a request to get a non-existent user")
      .withRequest("GET", "/api/v1/users/non-existent-id")
      .willRespondWith(404, (builder) => {
        builder
          .headers({ "Content-Type": "application/json" })
          .jsonBody({
            type: string("not-found"),
            title: string("Not Found"),
            status: integer(404),
          });
      })
      .executeTest(async (mockServer) => {
        const response = await fetch(`${mockServer.url}/api/v1/users/non-existent-id`);
        expect(response.status).toBe(404);
      });
  });
});
```

### Provider Verification

```typescript
// provider/tests/pact-verification.test.ts
import { Verifier } from "@pact-foundation/pact";
import path from "path";

describe("Pact Verification", () => {
  it("validates the expectations of WebApp", async () => {
    const verifier = new Verifier({
      providerBaseUrl: "http://localhost:3000",
      pactUrls: [path.resolve(process.cwd(), "../consumer/pacts/WebApp-UserAPI.json")],
      // Or from Pact Broker:
      // pactBrokerUrl: "https://your-broker.pactflow.io",
      // pactBrokerToken: process.env.PACT_BROKER_TOKEN,
      // providerVersion: process.env.GIT_SHA,

      // State handlers — set up test data for each "given" state
      stateHandlers: {
        "users exist": async () => {
          await seedTestUsers();
        },
        "user does not exist": async () => {
          await clearTestUsers();
        },
      },
    });

    await verifier.verifyProvider();
  });
});
```

### Provider State Handlers

```typescript
// Map Pact "given" states to setup functions
const stateHandlers: Record<string, () => Promise<void>> = {
  "users exist": async () => {
    await db.insert(users).values([
      { id: "550e8400-e29b-41d4-a716-446655440000", email: "alice@example.com", name: "Alice", role: "user" },
      { id: "660e8400-e29b-41d4-a716-446655440000", email: "bob@example.com", name: "Bob", role: "admin" },
    ]);
  },
  "user does not exist": async () => {
    await db.delete(users);
  },
  "no users exist": async () => {
    await db.delete(users);
  },
};
```

---

## Consumer-Driven Contracts Workflow

### The Flow

```
1. Consumer writes contract tests → generates pact file (JSON)
2. Pact file is shared (Pact Broker or file)
3. Provider runs pact verification against pact file
4. Both sides pass → contract is satisfied → safe to deploy
```

### CI/CD Integration

```yaml
# .github/workflows/consumer.yml
name: Consumer Contract Tests
on: [push]
jobs:
  pact:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run test:pact
      - name: Publish pact to broker
        run: |
          npx pact-broker publish ./pacts \
            --consumer-app-version=${{ github.sha }} \
            --broker-base-url=${{ secrets.PACT_BROKER_URL }} \
            --broker-token=${{ secrets.PACT_BROKER_TOKEN }}
```

```yaml
# .github/workflows/provider.yml
name: Provider Contract Verification
on: [push]
jobs:
  pact:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run start:test &
      - run: npm run test:pact:verify
```

### Pact Broker Can-I-Deploy

```bash
# Check if it's safe to deploy consumer
npx pact-broker can-i-deploy \
  --pacticipant WebApp \
  --version $GIT_SHA \
  --to-environment production

# Check if it's safe to deploy provider
npx pact-broker can-i-deploy \
  --pacticipant UserAPI \
  --version $GIT_SHA \
  --to-environment production
```

---

## MSW vs Pact: When to Use Which

| Scenario | Use MSW | Use Pact |
|----------|---------|----------|
| Unit/integration tests in frontend | Yes | No |
| Development without backend | Yes | No |
| Verify API contract between services | No | Yes |
| CI/CD deployment safety gate | No | Yes |
| Mock third-party APIs | Yes | No |
| Test error states quickly | Yes | No |
| Multi-team API coordination | No | Yes |

**Combine them:** Use MSW for fast feedback in development and unit tests. Use Pact for contract verification in CI before deploying.

---

## Best Practices

| Practice | Detail |
|----------|--------|
| Keep pact tests minimal | Test contract shape, not business logic |
| Use matchers, not exact values | `like()`, `eachLike()` allow provider flexibility |
| Name states clearly | `"users exist"` not `"state1"` |
| Run contract tests in CI | Both consumer and provider pipelines |
| Version pacts with git SHA | Enables `can-i-deploy` checks |
| Use `onUnhandledRequest: "error"` | Catch missing MSW handlers in tests |
| Reset handlers between tests | `server.resetHandlers()` prevents test bleed |
| Keep MSW handlers close to tests | Override defaults for edge cases inline |
