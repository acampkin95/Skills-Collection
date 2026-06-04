# OpenTelemetry for Node.js / Next.js

Reference for OpenTelemetry JS SDK (2025/2026 stable APIs).

---

## Packages

```bash
npm install @opentelemetry/sdk-node \
  @opentelemetry/api \
  @opentelemetry/auto-instrumentations-node \
  @opentelemetry/exporter-trace-otlp-http \
  @opentelemetry/exporter-metrics-otlp-http \
  @opentelemetry/resources \
  @opentelemetry/semantic-conventions
```

---

## SDK Setup (Next.js)

### Instrumentation Hook

```typescript
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    const { NodeSDK } = await import("@opentelemetry/sdk-node");
    const { getNodeAutoInstrumentations } = await import(
      "@opentelemetry/auto-instrumentations-node"
    );
    const { OTLPTraceExporter } = await import(
      "@opentelemetry/exporter-trace-otlp-http"
    );
    const { OTLPMetricExporter } = await import(
      "@opentelemetry/exporter-metrics-otlp-http"
    );
    const { PeriodicExportingMetricReader } = await import(
      "@opentelemetry/sdk-metrics"
    );
    const { Resource } = await import("@opentelemetry/resources");
    const {
      ATTR_SERVICE_NAME,
      ATTR_SERVICE_VERSION,
      ATTR_DEPLOYMENT_ENVIRONMENT_NAME,
    } = await import("@opentelemetry/semantic-conventions");

    const resource = new Resource({
      [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME ?? "my-app",
      [ATTR_SERVICE_VERSION]: process.env.npm_package_version ?? "0.0.0",
      [ATTR_DEPLOYMENT_ENVIRONMENT_NAME]: process.env.NODE_ENV ?? "development",
    });

    const sdk = new NodeSDK({
      resource,
      traceExporter: new OTLPTraceExporter({
        url: `${process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? "http://localhost:4318"}/v1/traces`,
      }),
      metricReader: new PeriodicExportingMetricReader({
        exporter: new OTLPMetricExporter({
          url: `${process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? "http://localhost:4318"}/v1/metrics`,
        }),
        exportIntervalMillis: 30_000,
      }),
      instrumentations: [
        getNodeAutoInstrumentations({
          // Disable noisy FS instrumentation
          "@opentelemetry/instrumentation-fs": { enabled: false },
          // Customize HTTP instrumentation
          "@opentelemetry/instrumentation-http": {
            ignoreIncomingPaths: ["/api/health", "/favicon.ico"],
          },
        }),
      ],
    });

    sdk.start();

    // Graceful shutdown
    process.on("SIGTERM", () => {
      sdk.shutdown().catch(console.error);
    });
  }
}
```

### Standalone Node.js Setup

```typescript
// tracing.ts — import before anything else
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { Resource } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";

const sdk = new NodeSDK({
  resource: new Resource({
    [ATTR_SERVICE_NAME]: "my-api",
  }),
  traceExporter: new OTLPTraceExporter(),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

process.on("SIGTERM", () => sdk.shutdown());
```

```bash
# Run with tracing
node --import ./tracing.ts src/server.ts
# Or via NODE_OPTIONS
NODE_OPTIONS="--import ./tracing.ts" node src/server.ts
```

---

## Auto-Instrumentation

Auto-instrumentation automatically traces:

| Library | What's Traced |
|---------|--------------|
| `http` / `https` | Incoming and outgoing HTTP requests |
| `fetch` (Node 18+) | Outgoing fetch calls |
| `pg` / `mysql2` | Database queries |
| `redis` / `ioredis` | Redis commands |
| `express` / `fastify` | Route handling |
| `graphql` | GraphQL resolvers |
| `grpc` | gRPC calls |
| `dns` | DNS lookups |

### Configuring Auto-Instrumentation

```typescript
getNodeAutoInstrumentations({
  // Disable specific instrumentations
  "@opentelemetry/instrumentation-fs": { enabled: false },
  "@opentelemetry/instrumentation-dns": { enabled: false },

  // Configure HTTP instrumentation
  "@opentelemetry/instrumentation-http": {
    ignoreIncomingPaths: ["/health", "/_next/static"],
    requestHook: (span, request) => {
      span.setAttribute("http.request.custom_header",
        request.headers["x-custom"] ?? "unknown"
      );
    },
  },

  // Configure pg instrumentation
  "@opentelemetry/instrumentation-pg": {
    enhancedDatabaseReporting: true,
    addSqlCommenterComment: true,
  },
});
```

---

## Manual Spans

### Basic Span

```typescript
import { trace, SpanStatusCode } from "@opentelemetry/api";

const tracer = trace.getTracer("my-app", "1.0.0");

export async function processItem(itemId: string): Promise<void> {
  return tracer.startActiveSpan("processItem", async (span) => {
    try {
      span.setAttribute("item.id", itemId);

      const result = await doWork(itemId);
      span.setAttribute("item.result", result.status);
      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: String(error) });
      span.recordException(error as Error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

### Nested Spans

```typescript
export async function handleOrder(orderId: string) {
  return tracer.startActiveSpan("handleOrder", async (parentSpan) => {
    parentSpan.setAttribute("order.id", orderId);

    // Child span: validate
    const order = await tracer.startActiveSpan("validateOrder", async (span) => {
      const o = await db.order.findUnique({ where: { id: orderId } });
      span.setAttribute("order.status", o?.status ?? "not_found");
      span.end();
      return o;
    });

    if (!order) {
      parentSpan.setStatus({ code: SpanStatusCode.ERROR, message: "Order not found" });
      parentSpan.end();
      throw new Error("Order not found");
    }

    // Child span: process payment
    await tracer.startActiveSpan("processPayment", async (span) => {
      span.setAttribute("payment.amount", order.total);
      await chargePayment(order);
      span.end();
    });

    // Child span: send notification
    await tracer.startActiveSpan("sendNotification", async (span) => {
      await sendEmail(order.userEmail, "Order confirmed");
      span.end();
    });

    parentSpan.setStatus({ code: SpanStatusCode.OK });
    parentSpan.end();
  });
}
```

### Span Events (Logs within Spans)

```typescript
span.addEvent("cache.miss", {
  "cache.key": "user:123",
  "cache.backend": "redis",
});

span.addEvent("retry.attempt", {
  "retry.count": 2,
  "retry.delay_ms": 500,
});
```

---

## Context Propagation

### Extracting Trace Context from Headers

```typescript
import { propagation, context, trace } from "@opentelemetry/api";

export async function handleIncomingRequest(request: Request) {
  // Extract trace context from incoming headers
  const carrier: Record<string, string> = {};
  request.headers.forEach((value, key) => {
    carrier[key] = value;
  });

  const extractedContext = propagation.extract(context.active(), carrier);

  // Run handler within extracted context
  return context.with(extractedContext, async () => {
    return tracer.startActiveSpan("handleRequest", async (span) => {
      // This span is a child of the incoming trace
      span.setAttribute("http.method", request.method);
      span.setAttribute("http.url", request.url);

      const response = await processRequest(request);
      span.end();
      return response;
    });
  });
}
```

### Injecting Trace Context into Outgoing Requests

```typescript
import { propagation, context } from "@opentelemetry/api";

export async function callDownstreamService(url: string, body: unknown) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  // Inject current trace context into outgoing headers
  propagation.inject(context.active(), headers);

  return fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
}
```

---

## Metrics

### Creating Metrics

```typescript
import { metrics } from "@opentelemetry/api";

const meter = metrics.getMeter("my-app", "1.0.0");

// Counter: monotonically increasing value
const requestCounter = meter.createCounter("http.requests.total", {
  description: "Total HTTP requests",
  unit: "requests",
});

// Histogram: distribution of values
const requestDuration = meter.createHistogram("http.request.duration", {
  description: "HTTP request duration",
  unit: "ms",
});

// UpDownCounter: value that can increase or decrease
const activeConnections = meter.createUpDownCounter("db.connections.active", {
  description: "Active database connections",
});

// Observable gauge: async value
meter.createObservableGauge("process.memory.heap", {
  description: "Heap memory usage",
  unit: "bytes",
  callbacks: [(result) => {
    result.observe(process.memoryUsage().heapUsed);
  }],
});
```

### Using Metrics

```typescript
// Record request
requestCounter.add(1, {
  "http.method": "GET",
  "http.route": "/api/users",
  "http.status_code": 200,
});

// Record duration
const start = performance.now();
await handleRequest();
requestDuration.record(performance.now() - start, {
  "http.method": "GET",
  "http.route": "/api/users",
});

// Track connections
activeConnections.add(1);
try {
  await doQuery();
} finally {
  activeConnections.add(-1);
}
```

### Business Metrics

```typescript
const orderCounter = meter.createCounter("orders.created", {
  description: "Orders created",
});

const orderValue = meter.createHistogram("orders.value", {
  description: "Order monetary value",
  unit: "cents",
});

export async function createOrder(order: Order) {
  await db.order.create({ data: order });

  orderCounter.add(1, {
    "order.type": order.type,
    "order.region": order.region,
  });

  orderValue.record(order.totalCents, {
    "order.type": order.type,
  });
}
```

---

## Exporters

### OTLP (Recommended)

```typescript
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { OTLPMetricExporter } from "@opentelemetry/exporter-metrics-otlp-http";

// HTTP (default port 4318)
const traceExporter = new OTLPTraceExporter({
  url: "http://localhost:4318/v1/traces",
  headers: { "x-api-key": process.env.OTEL_API_KEY },
});

// gRPC (port 4317) — use @opentelemetry/exporter-trace-otlp-grpc
```

### Jaeger

```bash
# Run Jaeger all-in-one with OTLP support
docker run -d --name jaeger \
  -p 16686:16686 \   # UI
  -p 4317:4317 \     # OTLP gRPC
  -p 4318:4318 \     # OTLP HTTP
  jaegertracing/jaeger:2
```

No Jaeger-specific exporter needed — Jaeger v2 accepts OTLP natively.

### Console (Development)

```typescript
import { ConsoleSpanExporter } from "@opentelemetry/sdk-trace-node";
import { ConsoleMetricExporter } from "@opentelemetry/sdk-metrics";

const sdk = new NodeSDK({
  traceExporter: new ConsoleSpanExporter(),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new ConsoleMetricExporter(),
  }),
  // ...
});
```

---

## Environment Variables

OTel SDK respects standard environment variables:

```bash
OTEL_SERVICE_NAME=my-app
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_EXPORTER_OTLP_HEADERS=x-api-key=secret
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1
OTEL_LOG_LEVEL=info
```

These override SDK configuration. Useful for environment-specific settings without code changes.

---

## Sampling Strategies

```typescript
import { ParentBasedSampler, TraceIdRatioBasedSampler } from "@opentelemetry/sdk-trace-node";

const sdk = new NodeSDK({
  sampler: new ParentBasedSampler({
    root: new TraceIdRatioBasedSampler(0.1), // 10% of new traces
    // Always sample if parent was sampled
  }),
  // ...
});
```

| Strategy | Use Case |
|----------|----------|
| `AlwaysOnSampler` | Development, low-traffic |
| `TraceIdRatioBasedSampler(0.1)` | Production (10% sampling) |
| `ParentBasedSampler` | Respect upstream sampling decision |

---

## Connecting OTel with Sentry

Sentry v8 supports OpenTelemetry natively. Sentry's Next.js SDK auto-instruments using OTel under the hood. If you need both standalone OTel and Sentry:

```typescript
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    // Sentry sets up its own OTel integration
    await import("./sentry.server.config");

    // If you also need to export to Jaeger/other backends,
    // add a SpanProcessor to the existing provider:
    const { trace } = await import("@opentelemetry/api");
    const { BatchSpanProcessor } = await import("@opentelemetry/sdk-trace-base");
    const { OTLPTraceExporter } = await import("@opentelemetry/exporter-trace-otlp-http");

    const provider = trace.getTracerProvider() as any;
    if (provider.addSpanProcessor) {
      provider.addSpanProcessor(
        new BatchSpanProcessor(
          new OTLPTraceExporter({
            url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
          }),
        ),
      );
    }
  }
}
```

---

## Docker Compose for Local Development

```yaml
# docker-compose.otel.yml
services:
  jaeger:
    image: jaegertracing/jaeger:2
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  # Optional: OTel Collector for routing
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otelcol/config.yaml"]
    ports:
      - "4317:4317"
      - "4318:4318"
    volumes:
      - ./otel-collector-config.yaml:/etc/otelcol/config.yaml
```
