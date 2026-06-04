---
name: monitoring-observability
description: Monitoring with OpenTelemetry, Sentry v9, Pino logging, distributed tracing, and metrics. Use for structured logging, error tracking, and alerting.
version: 2.0.0
reviewed: "2026-06-04"
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

See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.