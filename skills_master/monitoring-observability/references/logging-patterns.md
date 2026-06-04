# Logging Patterns with Pino

Reference for structured logging in TypeScript applications using Pino.

---

## Installation

```bash
npm install pino
npm install -D pino-pretty  # development formatting
```

---

## Base Logger Setup

```typescript
// lib/logger.ts
import pino, { type Logger } from "pino";

const isProduction = process.env.NODE_ENV === "production";

export const logger: Logger = pino({
  level: process.env.LOG_LEVEL ?? (isProduction ? "info" : "debug"),

  // Use ISO timestamps
  timestamp: pino.stdTimeFunctions.isoTime,

  // Output level as string, not number
  formatters: {
    level(label) {
      return { level: label };
    },
  },

  // Redact sensitive fields
  redact: {
    paths: [
      "req.headers.authorization",
      "req.headers.cookie",
      "*.password",
      "*.token",
      "*.secret",
      "*.apiKey",
      "*.creditCard",
      "*.ssn",
    ],
    censor: "[REDACTED]",
  },

  // Pretty-print in development
  transport: isProduction
    ? undefined
    : {
        target: "pino-pretty",
        options: {
          colorize: true,
          translateTime: "HH:MM:ss.l",
          ignore: "pid,hostname",
        },
      },
});
```

---

## Child Loggers

Child loggers inherit parent config and add context:

```typescript
// Create contextual loggers
const userLogger = logger.child({ module: "user-service" });
const paymentLogger = logger.child({ module: "payment-service" });

// Nest further with request context
export function createRequestLogger(correlationId: string, userId?: string) {
  return logger.child({
    correlationId,
    ...(userId && { userId }),
  });
}

// Usage in API route
export async function POST(request: Request) {
  const correlationId = request.headers.get("x-correlation-id") ?? crypto.randomUUID();
  const log = createRequestLogger(correlationId);

  log.info({ method: "POST", url: request.url }, "request started");

  try {
    const body = await request.json();
    log.debug({ bodyKeys: Object.keys(body) }, "parsed request body");

    const result = await processData(body, log);
    log.info({ resultId: result.id }, "request completed");

    return Response.json(result, { status: 201 });
  } catch (error) {
    log.error({ err: error }, "request failed");
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}

// Pass logger through call chain
async function processData(data: unknown, log: Logger) {
  log.debug("processing data");
  // child logger preserves all parent context (correlationId, etc.)
  const childLog = log.child({ step: "validation" });
  childLog.info("validating input");
  // ...
}
```

---

## Serializers

Custom serializers control how objects are logged:

```typescript
import pino from "pino";

export const logger = pino({
  serializers: {
    // Standard request serializer
    req: pino.stdSerializers.req,
    // Standard response serializer
    res: pino.stdSerializers.res,
    // Standard error serializer (includes stack trace)
    err: pino.stdSerializers.err,

    // Custom serializer for user objects
    user(user: { id: string; email: string; role: string }) {
      return {
        id: user.id,
        role: user.role,
        // Omit email from logs
      };
    },

    // Custom serializer for database queries
    query(q: { text: string; duration: number; rowCount: number }) {
      return {
        text: q.text.slice(0, 200), // Truncate long queries
        durationMs: q.duration,
        rows: q.rowCount,
      };
    },
  },
});
```

---

## Redaction

### Path-Based Redaction

```typescript
const logger = pino({
  redact: {
    paths: [
      // Exact paths
      "password",
      "req.headers.authorization",
      "req.headers.cookie",

      // Wildcard: any key named "secret" at any depth
      "*.secret",
      "*.token",
      "*.apiKey",

      // Array items
      "users[*].password",
      "users[*].ssn",

      // Nested wildcards
      "**.password",  // any depth
    ],
    censor: "[REDACTED]",
    remove: false, // set true to remove key entirely
  },
});
```

### Dynamic Redaction with a Function

```typescript
const logger = pino({
  redact: {
    paths: ["*.email"],
    censor(value: string) {
      // Partially mask email
      if (typeof value === "string" && value.includes("@")) {
        const [local, domain] = value.split("@");
        return `${local[0]}***@${domain}`;
      }
      return "[REDACTED]";
    },
  },
});
```

---

## Structured JSON Output

All Pino output is JSON by default:

```json
{"level":"info","time":"2026-01-29T10:30:00.000Z","correlationId":"abc-123","module":"user-service","msg":"user created","userId":"user_456"}
```

### Structured Log Best Practices

```typescript
// GOOD: Structured data + message
log.info({ userId: "123", action: "login", ip: "1.2.3.4" }, "user authenticated");

// BAD: Interpolating data into message string
log.info(`User 123 logged in from 1.2.3.4`);

// GOOD: Error with context
log.error({ err: error, orderId: "abc", step: "payment" }, "payment processing failed");

// BAD: Error without context
log.error("something went wrong");

// GOOD: Measurable values as numbers
log.info({ durationMs: 342, rowCount: 50 }, "query completed");

// BAD: Numbers embedded in strings
log.info("query took 342ms and returned 50 rows");
```

---

## Correlation IDs

### Middleware Pattern (Next.js)

```typescript
// middleware.ts
import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const correlationId = request.headers.get("x-correlation-id") ?? crypto.randomUUID();

  // Forward to API routes
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-correlation-id", correlationId);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  // Return to client for debugging
  response.headers.set("x-correlation-id", correlationId);

  return response;
}

export const config = {
  matcher: ["/api/:path*"],
};
```

### AsyncLocalStorage Pattern (Node.js)

```typescript
// lib/async-context.ts
import { AsyncLocalStorage } from "node:async_hooks";

interface RequestContext {
  correlationId: string;
  userId?: string;
  startTime: number;
}

export const asyncContext = new AsyncLocalStorage<RequestContext>();

export function getCorrelationId(): string {
  return asyncContext.getStore()?.correlationId ?? "no-context";
}
```

```typescript
// lib/logger.ts
import pino from "pino";
import { asyncContext } from "./async-context";

const baseLogger = pino({ /* config */ });

// Logger that auto-attaches correlation ID
export const logger = new Proxy(baseLogger, {
  get(target, prop) {
    const store = asyncContext.getStore();
    if (store && typeof target[prop as keyof typeof target] === "function") {
      const child = target.child({
        correlationId: store.correlationId,
        ...(store.userId && { userId: store.userId }),
      });
      return child[prop as keyof typeof child];
    }
    return target[prop as keyof typeof target];
  },
});
```

```typescript
// Usage: wrap request handler
import { asyncContext } from "@/lib/async-context";

export async function GET(request: Request) {
  const correlationId = request.headers.get("x-correlation-id") ?? crypto.randomUUID();

  return asyncContext.run(
    { correlationId, startTime: performance.now() },
    async () => {
      // All nested logger calls automatically include correlationId
      logger.info("handling request");
      const data = await fetchData(); // internal logs get correlationId too
      return Response.json(data);
    },
  );
}
```

---

## Request Logging Middleware

### Express/Fastify-Style

```typescript
import pino from "pino";
import pinoHttp from "pino-http";

export const httpLogger = pinoHttp({
  logger: pino({ /* base config */ }),

  // Custom request ID
  genReqId: (req) => req.headers["x-correlation-id"] as string ?? crypto.randomUUID(),

  // What to log on request/response
  customProps(req) {
    return {
      correlationId: req.id,
    };
  },

  // Custom success message
  customSuccessMessage(req, res) {
    return `${req.method} ${req.url} completed`;
  },

  // Custom error message
  customErrorMessage(req, res, error) {
    return `${req.method} ${req.url} failed: ${error.message}`;
  },

  // Don't log health checks
  autoLogging: {
    ignore(req) {
      return req.url === "/api/health" || req.url === "/favicon.ico";
    },
  },

  // Customize what's logged about req/res
  serializers: {
    req(req) {
      return {
        method: req.method,
        url: req.url,
        query: req.query,
        // Omit headers and body by default
      };
    },
    res(res) {
      return {
        statusCode: res.statusCode,
      };
    },
  },
});
```

### Next.js API Route Wrapper

```typescript
// lib/with-logging.ts
import { type NextRequest, NextResponse } from "next/server";
import { logger } from "@/lib/logger";

type Handler = (
  request: NextRequest,
  context: { params: Promise<Record<string, string>> },
) => Promise<Response>;

export function withLogging(handler: Handler): Handler {
  return async (request, context) => {
    const correlationId = request.headers.get("x-correlation-id") ?? crypto.randomUUID();
    const log = logger.child({ correlationId });
    const start = performance.now();

    log.info(
      { method: request.method, url: request.url },
      "request started",
    );

    try {
      const response = await handler(request, context);
      const duration = Math.round(performance.now() - start);

      log.info(
        { statusCode: response.status, durationMs: duration },
        "request completed",
      );

      return response;
    } catch (error) {
      const duration = Math.round(performance.now() - start);

      log.error(
        { err: error, durationMs: duration },
        "request failed",
      );

      return NextResponse.json(
        { error: "Internal Server Error" },
        { status: 500 },
      );
    }
  };
}
```

```typescript
// app/api/users/route.ts
import { withLogging } from "@/lib/with-logging";

export const GET = withLogging(async (request) => {
  const users = await db.user.findMany();
  return Response.json(users);
});
```

---

## Log Levels Strategy

### Per-Environment Configuration

```bash
# .env.development
LOG_LEVEL=debug

# .env.production
LOG_LEVEL=info

# .env.staging
LOG_LEVEL=debug
```

### Dynamic Level Changes

```typescript
// Useful for temporary production debugging
import { logger } from "@/lib/logger";

// app/api/admin/log-level/route.ts
export async function PUT(request: Request) {
  const { level } = await request.json();
  if (!["fatal", "error", "warn", "info", "debug", "trace"].includes(level)) {
    return Response.json({ error: "Invalid level" }, { status: 400 });
  }

  logger.level = level;
  logger.info({ newLevel: level }, "log level changed");

  return Response.json({ level });
}
```

---

## Production Log Pipeline

```
App (Pino JSON) → stdout → Container runtime → Log aggregator
                                                 ├── Datadog
                                                 ├── Grafana Loki
                                                 ├── AWS CloudWatch
                                                 └── Elasticsearch
```

### Key Rules

1. **Always log to stdout** — never write to files in containers
2. **Always use JSON** — no `pino-pretty` in production
3. **Always include correlationId** — enables cross-service tracing
4. **Always use appropriate levels** — `info` for business events, `error` for failures
5. **Never log PII** — use redaction for emails, names, addresses
6. **Never log request/response bodies** by default — too verbose, potential PII
7. **Keep messages short and consistent** — "user created", not "A new user has been successfully created in the system"

---

## Testing Logs

```typescript
// test/helpers/logger.ts
import pino from "pino";
import { Writable } from "node:stream";

export function createTestLogger() {
  const logs: Array<Record<string, unknown>> = [];

  const stream = new Writable({
    write(chunk, _encoding, callback) {
      logs.push(JSON.parse(chunk.toString()));
      callback();
    },
  });

  const logger = pino({ level: "trace" }, stream);

  return { logger, logs };
}

// In tests
test("logs user creation", async () => {
  const { logger, logs } = createTestLogger();
  await createUser({ email: "test@example.com" }, logger);

  expect(logs).toContainEqual(
    expect.objectContaining({
      level: "info",
      msg: "user created",
      userId: expect.any(String),
    }),
  );
});
```
