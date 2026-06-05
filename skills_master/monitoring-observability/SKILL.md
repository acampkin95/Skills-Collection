---
name: monitoring-observability
description: Monitoring and observability, for TypeScript applications with Pino structured logging.
---

# Monitoring & Observability Skill

**Production monitoring with three pillars: logs, traces, and metrics.**

## Quick Navigation

| Task | Reference |
|------|-----------|
| Sentry v9.17.0+ setup, error boundaries, source maps | `references/sentry-setup.md` |
| OpenTelemetry SDK, spans, exporters, Grafana integration | `references/opentelemetry.md` |
| Pino setup, structured logging, correlation IDs | `references/logging-patterns.md` |

---

## Three Pillars of Observability

| Pillar | Purpose | Tool | Signal |
|--------|---------|------|--------|
| **Logs** | Discrete events with context | Pino | What happened |
| **Metrics** | Aggregated measurements over time | OpenTelemetry / Prometheus | How much / how often |
| **Traces** | Request lifecycle across services | OpenTelemetry / Sentry | Where time is spent |

All three pillars must share a **correlation ID** to enable cross-referencing.

---

## Structured Logging (Pino)

### Basic Setup

```typescript
import pino from "pino";

export const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  timestamp: pino.stdTimeFunctions.isoTime,
  redact: ["req.headers.authorization", "*.password", "*.token"],
});
```

### Child Loggers with Correlation

```typescript
import { randomUUID } from "node:crypto";

export function createRequestLogger(requestId?: string) {
  const correlationId = requestId ?? randomUUID();
  return logger.child({ correlationId });
}

export async function GET(request: Request) {
  const log = createRequestLogger(request.headers.get("x-request-id") ?? undefined);
  log.info({ url: request.url }, "incoming request");

  try {
    const data = await fetchData();
    log.info({ count: data.length }, "fetched data");
    return Response.json(data);
  } catch (error) {
    log.error({ err: error }, "request failed");
    return Response.json({ error: "Internal error" }, { status: 500 });
  }
}
```

### Log Levels

| Level | Use When |
|-------|----------|
| `fatal` | App is about to crash |
| `error` | Operation failed, needs attention |
| `warn` | Unexpected but recoverable |
| `info` | Normal business events (request served, job completed) |
| `debug` | Diagnostic detail for troubleshooting |
| `trace` | Fine-grained (loop iterations, variable states) |

**Production:** Set `LOG_LEVEL=info`. Never use `debug`/`trace` long-term.

---

## Error Tracking (Sentry v9.17.0+)

### Next.js App Router Setup

```bash
npx @sentry/wizard@latest -i nextjs
```

Generates: `sentry.client.config.ts`, `sentry.server.config.ts`, `sentry.edge.config.ts`, `instrumentation.ts`

### Minimal Client Config

```typescript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_VERCEL_ENV ?? "development",
  tracesSampleRate: 0.1, // 10% in production
  replaysSessionSampleRate: 0.01,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.replayIntegration(),
    Sentry.browserTracingIntegration(),
  ],
});
```

### Error Boundary

```typescript
"use client";
import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html>
      <body>
        <h2>Something went wrong</h2>
        <button onClick={() => reset()}>Try again</button>
      </body>
    </html>
  );
}
```

---

## Distributed Tracing (OpenTelemetry v0.135+)

### Instrumentation Registration

```typescript
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    const { NodeSDK } = await import("@opentelemetry/sdk-node");
    const { getNodeAutoInstrumentations } = await import(
      "@opentelemetry/auto-instrumentations-node"
    );
    const { OTLPTraceExporter } = await import(
      "@opentelemetry/exporter-trace-otlp-http"
    );
    const { Resource } = await import("@opentelemetry/resources");
    const { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } = await import(
      "@opentelemetry/semantic-conventions"
    );

    const sdk = new NodeSDK({
      resource: new Resource({
        [ATTR_SERVICE_NAME]: "my-nextjs-app",
        [ATTR_SERVICE_VERSION]: process.env.NEXT_PUBLIC_APP_VERSION ?? "0.0.0",
      }),
      traceExporter: new OTLPTraceExporter({
        url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? "http://localhost:4318/v1/traces",
      }),
      instrumentations: [
        getNodeAutoInstrumentations({
          "@opentelemetry/instrumentation-fs": { enabled: false },
        }),
      ],
    });

    sdk.start();
  }
}
```

### Manual Span Creation

```typescript
import { trace } from "@opentelemetry/api";

const tracer = trace.getTracer("my-app");

export async function processOrder(orderId: string) {
  return tracer.startActiveSpan("processOrder", async (span) => {
    try {
      span.setAttribute("order.id", orderId);

      const result = await tracer.startActiveSpan("validateOrder", async (child) => {
        const valid = await validate(orderId);
        child.setAttribute("order.valid", valid);
        child.end();
        return valid;
      });

      span.setStatus({ code: 1 }); // OK
      return result;
    } catch (error) {
      span.setStatus({ code: 2, message: String(error) }); // ERROR
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

---

## Health Check Endpoints

```typescript
interface HealthCheck {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  version: string;
  checks: Record<string, { status: string; latencyMs?: number; error?: string }>;
}

export async function GET(): Promise<Response> {
  const checks: HealthCheck["checks"] = {};

  const dbStart = performance.now();
  try {
    await db.$queryRaw`SELECT 1`;
    checks.database = { status: "ok", latencyMs: Math.round(performance.now() - dbStart) };
  } catch (error) {
    checks.database = { status: "error", error: String(error) };
  }

  const allOk = Object.values(checks).every((c) => c.status === "ok");
  const anyError = Object.values(checks).some((c) => c.status === "error");

  const health: HealthCheck = {
    status: anyError ? "unhealthy" : allOk ? "healthy" : "degraded",
    timestamp: new Date().toISOString(),
    version: process.env.NEXT_PUBLIC_APP_VERSION ?? "unknown",
    checks,
  };

  return Response.json(health, {
    status: health.status === "unhealthy" ? 503 : 200,
    headers: { "Cache-Control": "no-cache, no-store" },
  });
}
```

### Liveness vs Readiness

| Endpoint | Purpose | What It Checks |
|----------|---------|---------------|
| `/api/health/live` | Is process alive? | Return 200 always |
| `/api/health/ready` | Can it serve traffic? | DB, cache, external deps |

---

## Alerting Patterns

### Alert Severity Levels

| Severity | Response Time | Example | Action |
|----------|--------------|---------|--------|
| **P1 Critical** | < 15 min | App down, data loss | Page on-call, war room |
| **P2 High** | < 1 hour | Feature broken, degraded perf | Notify on-call |
| **P3 Medium** | < 8 hours | Non-critical errors spiking | Notify team channel |
| **P4 Low** | Next sprint | Warning thresholds, tech debt | Create ticket |

### Alert Design Rules

1. **Every alert must be actionable** — if you can't act on it, remove it
2. **Include runbook link** — what to do when this fires
3. **Set appropriate thresholds** — avoid single-occurrence alerts
4. **Use rate-of-change, not absolute values** — "error rate doubled" > "50 errors"
5. **Group related alerts** — avoid alert storms during incidents

---

## Correlation IDs (End-to-End)

### Middleware Injection

```typescript
import { NextRequest, NextResponse } from "next/server";
import { randomUUID } from "node:crypto";

export function middleware(request: NextRequest) {
  const correlationId = request.headers.get("x-correlation-id") ?? randomUUID();

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-correlation-id", correlationId);

  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("x-correlation-id", correlationId);

  return response;
}
```

### Bind to Sentry & Logger

```typescript
import * as Sentry from "@sentry/nextjs";
import { createRequestLogger } from "@/lib/logger";

export async function handleRequest(request: Request) {
  const correlationId = request.headers.get("x-correlation-id")!;
  const log = createRequestLogger(correlationId);

  Sentry.setTag("correlationId", correlationId);
  Sentry.setContext("request", { correlationId, url: request.url, method: request.method });

  log.info("processing request");
}
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Over-logging (every request body) | Log summaries; use `debug` level for detail; never log PII |
| Missing correlation IDs | Inject in middleware, propagate to logger + Sentry + OTel |
| Alert fatigue (too many noisy alerts) | Use rate-based thresholds, require actionable alerts only |
| Logging secrets/tokens | Use Pino `redact` option for sensitive fields |
| `console.log` in production | Replace with structured logger; lint with `no-console` rule |
| Not sampling traces | Set `tracesSampleRate` to 0.01-0.1 in production |
| Health endpoint behind auth | Keep `/api/health` public or use separate auth for monitors |
| Missing error context | Always attach `userId`, `correlationId`, request metadata |

---

## Reference Files

| File | Purpose |
|------|---------|
| `references/logging-patterns.md` | Pino setup, structured logging, redaction |
| `references/sentry-setup.md` | Configuration, source maps, custom contexts |
| `references/opentelemetry.md` | SDK setup, spans, exporters, metrics |
