# Sentry Setup for Next.js (App Router)

Reference for Sentry v8 with Next.js 14/15/16 App Router.

---

## Installation

```bash
npx @sentry/wizard@latest -i nextjs
```

The wizard creates:
- `sentry.client.config.ts`
- `sentry.server.config.ts`
- `sentry.edge.config.ts`
- `instrumentation.ts`
- Updates `next.config.ts` with `withSentryConfig`

### Manual Package Install

```bash
npm install @sentry/nextjs
```

---

## Configuration Files

### Client Config

```typescript
// sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_VERCEL_ENV ?? "development",

  // Performance
  tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,

  // Session Replay
  replaysSessionSampleRate: 0.01, // 1% of sessions
  replaysOnErrorSampleRate: 1.0,  // 100% of sessions with errors

  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
    Sentry.browserTracingIntegration(),
    Sentry.feedbackIntegration({
      colorScheme: "system",
    }),
  ],

  // Filter noisy errors
  beforeSend(event, hint) {
    const error = hint.originalException;
    if (error instanceof Error) {
      // Ignore bot/crawler errors
      if (event.request?.headers?.["user-agent"]?.match(/bot|crawl|spider/i)) {
        return null;
      }
      // Ignore network errors from user leaving page
      if (error.message?.includes("AbortError")) {
        return null;
      }
    }
    return event;
  },

  // Ignore specific error messages
  ignoreErrors: [
    "ResizeObserver loop",
    "Non-Error promise rejection",
    /Loading chunk \d+ failed/,
  ],
});
```

### Server Config

```typescript
// sentry.server.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.VERCEL_ENV ?? "development",
  tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,

  // Capture unhandled promise rejections
  integrations: [
    Sentry.captureConsoleIntegration({ levels: ["error"] }),
  ],

  beforeSend(event) {
    // Scrub sensitive data from server errors
    if (event.request?.cookies) {
      event.request.cookies = {};
    }
    return event;
  },
});
```

### Edge Config

```typescript
// sentry.edge.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_VERCEL_ENV ?? "development",
  tracesSampleRate: 0.1,
});
```

### Instrumentation Hook

```typescript
// instrumentation.ts
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./sentry.server.config");
  }
  if (process.env.NEXT_RUNTIME === "edge") {
    await import("./sentry.edge.config");
  }
}

export const onRequestError = Sentry.captureRequestError;
```

### Next.js Config

```typescript
// next.config.ts
import { withSentryConfig } from "@sentry/nextjs";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // your config
};

export default withSentryConfig(nextConfig, {
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  authToken: process.env.SENTRY_AUTH_TOKEN,

  // Upload source maps in CI only
  silent: !process.env.CI,

  // Hides source maps from client bundles
  hideSourceMaps: true,

  // Tree-shake Sentry logger in production
  disableLogger: true,

  // Tunnel to avoid ad-blockers (optional)
  // tunnelRoute: "/monitoring",

  // Automatically instrument API routes and server components
  autoInstrumentServerFunctions: true,
  autoInstrumentMiddleware: true,
  autoInstrumentAppDirectory: true,
});
```

---

## Source Maps

### CI Upload (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
env:
  SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
  SENTRY_ORG: my-org
  SENTRY_PROJECT: my-nextjs-app

steps:
  - name: Build
    run: npm run build
    # Source maps are uploaded automatically by withSentryConfig during build
```

### Environment Variables

```bash
# .env.local (development)
NEXT_PUBLIC_SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0

# CI/CD secrets
SENTRY_AUTH_TOKEN=sntrys_...
SENTRY_ORG=my-org
SENTRY_PROJECT=my-project
```

---

## Error Boundaries

### Global Error Boundary

```typescript
// app/global-error.tsx
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
        <div style={{ padding: "2rem", textAlign: "center" }}>
          <h1>Something went wrong</h1>
          <p>Our team has been notified.</p>
          <button onClick={() => reset()}>Try again</button>
        </div>
      </body>
    </html>
  );
}
```

### Route-Level Error Boundary

```typescript
// app/dashboard/error.tsx
"use client";

import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error, {
      tags: { route: "dashboard" },
      extra: { digest: error.digest },
    });
  }, [error]);

  return (
    <div className="p-8 text-center">
      <h2>Dashboard error</h2>
      <p>Failed to load dashboard data.</p>
      <button onClick={() => reset()}>Retry</button>
    </div>
  );
}
```

---

## Custom Context and Breadcrumbs

### Setting User Context

```typescript
// After authentication
import * as Sentry from "@sentry/nextjs";

export function setSentryUser(user: { id: string; email: string; role: string }) {
  Sentry.setUser({
    id: user.id,
    email: user.email,
  });
  Sentry.setTag("user.role", user.role);
}

// On logout
export function clearSentryUser() {
  Sentry.setUser(null);
}
```

### Custom Context for Server Actions

```typescript
"use server";

import * as Sentry from "@sentry/nextjs";

export async function createOrder(formData: FormData) {
  return Sentry.withServerActionInstrumentation(
    "createOrder",
    {
      recordResponse: true,
    },
    async () => {
      const productId = formData.get("productId") as string;

      Sentry.setContext("order", {
        productId,
        timestamp: new Date().toISOString(),
      });

      Sentry.addBreadcrumb({
        category: "order",
        message: `Creating order for product ${productId}`,
        level: "info",
      });

      // ... order creation logic
    },
  );
}
```

### Manual Breadcrumbs

```typescript
import * as Sentry from "@sentry/nextjs";

// Navigation breadcrumb
Sentry.addBreadcrumb({
  category: "navigation",
  message: "User navigated to checkout",
  level: "info",
  data: { from: "/cart", to: "/checkout" },
});

// User action breadcrumb
Sentry.addBreadcrumb({
  category: "ui.click",
  message: "Add to cart button clicked",
  level: "info",
  data: { productId: "abc123" },
});

// API call breadcrumb
Sentry.addBreadcrumb({
  category: "fetch",
  message: "POST /api/orders",
  level: "info",
  data: { status: 201, duration: 342 },
});
```

---

## Performance Monitoring

### Custom Transactions

```typescript
import * as Sentry from "@sentry/nextjs";

export async function processPayment(orderId: string) {
  return Sentry.startSpan(
    {
      name: "processPayment",
      op: "payment",
      attributes: { "order.id": orderId },
    },
    async (span) => {
      // Child span for validation
      await Sentry.startSpan(
        { name: "validatePayment", op: "payment.validate" },
        async () => {
          await validatePaymentDetails(orderId);
        },
      );

      // Child span for external API call
      await Sentry.startSpan(
        { name: "chargeStripe", op: "http.client" },
        async () => {
          await stripe.charges.create({ amount: 1000, currency: "usd" });
        },
      );
    },
  );
}
```

### Monitoring Server Components

```typescript
// app/dashboard/page.tsx
import * as Sentry from "@sentry/nextjs";

export default async function DashboardPage() {
  const data = await Sentry.startSpan(
    { name: "fetchDashboardData", op: "db.query" },
    async () => {
      return await db.dashboard.getData();
    },
  );

  return <Dashboard data={data} />;
}
```

---

## Release Tracking

### In Build Pipeline

```yaml
# .github/workflows/deploy.yml
- name: Create Sentry release
  uses: getsentry/action-release@v3
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: my-org
    SENTRY_PROJECT: my-project
  with:
    environment: production
    version: ${{ github.sha }}
    sourcemaps: .next
    # Associate commits with release
    set_commits: auto
```

### In Sentry Config

```typescript
// sentry.client.config.ts
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  release: process.env.NEXT_PUBLIC_SENTRY_RELEASE ?? process.env.VERCEL_GIT_COMMIT_SHA,
  // ...
});
```

---

## Tunneling (Ad-Blocker Bypass)

```typescript
// next.config.ts — withSentryConfig option
export default withSentryConfig(nextConfig, {
  tunnelRoute: "/monitoring",
  // Creates a /monitoring API route that proxies Sentry events
  // This avoids ad-blockers that block sentry.io requests
});
```

---

## Testing Sentry Locally

```typescript
// app/api/sentry-test/route.ts (remove before deploying)
export async function GET() {
  throw new Error("Sentry test error — delete this route");
}
```

Verify in Sentry dashboard that the error appears with:
- Correct source maps (readable stack trace)
- Environment tag
- Release tag
- User context (if authenticated)
