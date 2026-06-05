---
name: feature-flags
description: Feature flag systems, for gradual rollouts, A/B testing.
---

# Feature Flags

Feature flag management for controlled releases, A/B testing, and operational control.

## Flag Types

| Type | Purpose | Lifetime | Example |
|------|---------|----------|---------|
| **Release** | Gate incomplete features | Days–weeks | `new-checkout-flow` |
| **Experiment** | A/B test variants | Weeks–months | `pricing-page-v2` |
| **Ops** | Kill switch / circuit breaker | Permanent | `enable-search-cache` |
| **Permission** | User-level access control | Permanent | `beta-access` |

## 2025-2026 Platform Landscape

For teams at scale, consider managed platforms:

| Platform | Best For | Pricing | Key Features |
|----------|----------|---------|--------------|
| **LaunchDarkly** | Enterprise DevOps teams | $10+/mo | Enterprise security, advanced targeting, integrations |
| **Statsig** | Product teams + experimentation | Free-$150+/mo | Built-in statistical analysis, experimentation framework |
| **GrowthBook** | Open-source or growth teams | Free (open) | A/B testing focus, experimentation, cost-effective |
| **Flagsmith** | Small-to-medium teams | Free tier + paid | Lightweight, developer-friendly, event tracking |

**2025 Trend**: 96% of high-growth companies (expected 2025+ growth) invest in feature experimentation.

## Simple JSON-Based Flags (Zero Dependencies)

```typescript
// lib/flags.ts
type FlagValue = boolean | string | number;

interface FlagDefinition {
  value: FlagValue;
  description: string;
  type: "release" | "experiment" | "ops" | "permission";
  owner: string;
  createdAt: string;
}

const FLAGS: Record<string, FlagDefinition> = {
  "new-dashboard": {
    value: false,
    description: "Redesigned dashboard with charts",
    type: "release",
    owner: "team-frontend",
    createdAt: "2025-01-15",
  },
  "enable-search-cache": {
    value: true,
    description: "Cache search results in Redis",
    type: "ops",
    owner: "team-backend",
    createdAt: "2024-11-01",
  },
  "checkout-variant": {
    value: "control",
    description: "A/B test for checkout flow",
    type: "experiment",
    owner: "team-growth",
    createdAt: "2025-01-20",
  },
};

export function getFlag<T extends FlagValue = boolean>(key: string): T {
  const flag = FLAGS[key];
  if (!flag) {
    console.warn(`Unknown flag: ${key}`);
    return false as T;
  }
  return flag.value as T;
}

export function isEnabled(key: string): boolean {
  return getFlag<boolean>(key) === true;
}
```

### Usage

```tsx
import { isEnabled, getFlag } from "@/lib/flags";

export default function Dashboard() {
  if (isEnabled("new-dashboard")) {
    return <NewDashboard />;
  }
  return <LegacyDashboard />;
}

// Variant flags
function CheckoutPage() {
  const variant = getFlag<string>("checkout-variant");

  switch (variant) {
    case "streamlined":
      return <StreamlinedCheckout />;
    case "one-page":
      return <OnePageCheckout />;
    default:
      return <StandardCheckout />;
  }
}
```

## React Context Provider Pattern

```tsx
// lib/feature-flags/provider.tsx
"use client";

import { createContext, useContext, ReactNode } from "react";

type Flags = Record<string, boolean | string | number>;

const FlagContext = createContext<Flags>({});

export function FlagProvider({
  flags,
  children,
}: {
  flags: Flags;
  children: ReactNode;
}) {
  return <FlagContext.Provider value={flags}>{children}</FlagContext.Provider>;
}

export function useFlag<T = boolean>(key: string, defaultValue?: T): T {
  const flags = useContext(FlagContext);
  return (flags[key] as T) ?? (defaultValue as T);
}

export function useIsEnabled(key: string): boolean {
  return useFlag<boolean>(key, false);
}
```

```tsx
// app/layout.tsx
import { FlagProvider } from "@/lib/feature-flags/provider";

async function getFlags(): Promise<Record<string, boolean>> {
  // Fetch from your flag source (API, Edge Config, DB, etc.)
  const res = await fetch(`${process.env.FLAG_SERVICE_URL}/flags`, {
    next: { revalidate: 60 },
  });
  return res.json();
}

export default async function Layout({ children }: { children: React.ReactNode }) {
  const flags = await getFlags();
  return (
    <html lang="en">
      <body>
        <FlagProvider flags={flags}>{children}</FlagProvider>
      </body>
    </html>
  );
}
```

```tsx
// components/FeatureGate.tsx
"use client";

import { useIsEnabled } from "@/lib/feature-flags/provider";

export function FeatureGate({
  flag,
  children,
  fallback = null,
}: {
  flag: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  const enabled = useIsEnabled(flag);
  return enabled ? <>{children}</> : <>{fallback}</>;
}

// Usage
<FeatureGate flag="new-sidebar" fallback={<OldSidebar />}>
  <NewSidebar />
</FeatureGate>
```

## Server-Side Middleware for Flags

```typescript
// middleware.ts (Next.js)
import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Percentage-based rollout using cookie for consistency
  let bucket = request.cookies.get("ab-bucket")?.value;
  if (!bucket) {
    bucket = Math.random() < 0.5 ? "control" : "treatment";
    response.cookies.set("ab-bucket", bucket, {
      httpOnly: true,
      maxAge: 60 * 60 * 24 * 30, // 30 days
    });
  }

  // Set header for downstream use
  response.headers.set("x-ab-bucket", bucket);
  return response;
}
```

## Vercel Edge Config

```typescript
// lib/flags-edge.ts
import { createClient } from "@vercel/edge-config";

const edgeConfig = createClient(process.env.EDGE_CONFIG);

export async function getEdgeFlag(key: string): Promise<boolean> {
  const value = await edgeConfig.get<boolean>(key);
  return value ?? false;
}

// In a server component or API route
export default async function Page() {
  const showBanner = await getEdgeFlag("promo-banner");
  return (
    <main>
      {showBanner && <PromoBanner />}
      <Content />
    </main>
  );
}
```

## Rollout Strategies

### Percentage Rollout

```typescript
function isInRollout(userId: string, flagKey: string, percentage: number): boolean {
  // Deterministic hash ensures same user always gets same result
  const hash = simpleHash(`${flagKey}:${userId}`);
  return (hash % 100) < percentage;
}

function simpleHash(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0; // Convert to 32-bit integer
  }
  return Math.abs(hash);
}
```

### User Targeting

```typescript
interface TargetingRule {
  attribute: string;
  operator: "eq" | "in" | "contains" | "gt" | "lt";
  value: string | string[] | number;
}

interface FlagConfig {
  key: string;
  defaultValue: boolean;
  rules: Array<{
    conditions: TargetingRule[];
    value: boolean;
  }>;
  rolloutPercentage?: number;
}

function evaluateFlag(config: FlagConfig, context: Record<string, any>): boolean {
  for (const rule of config.rules) {
    if (rule.conditions.every((c) => matchCondition(c, context))) {
      return rule.value;
    }
  }

  if (config.rolloutPercentage !== undefined && context.userId) {
    return isInRollout(context.userId, config.key, config.rolloutPercentage);
  }

  return config.defaultValue;
}
```

## Kill Switch Pattern

```typescript
// Wrap risky operations with a kill switch
async function searchProducts(query: string) {
  if (!isEnabled("enable-search-service")) {
    // Fallback to basic database search
    return basicDatabaseSearch(query);
  }

  try {
    return await externalSearchService.search(query);
  } catch (error) {
    // Auto-disable on repeated failures (circuit breaker)
    console.error("Search service failed:", error);
    return basicDatabaseSearch(query);
  }
}
```

## Flag Lifecycle Management

```
1. PROPOSED  → PR creates flag definition with owner + description
2. ACTIVE    → Flag is in use, controlling behavior
3. ROLLED_OUT → Flag is 100% ON, code path proven stable
4. CLEANUP   → Remove flag checks, delete old code path
5. ARCHIVED  → Flag definition removed
```

## Enterprise Integration (2025+)

### LaunchDarkly Integration

```typescript
import { LDClient } from "@launchdarkly/node-server-sdk";

const client = new LDClient(process.env.LD_SDK_KEY!);

export async function getLDFlag(userId: string, flagKey: string): Promise<boolean> {
  const user = { key: userId };
  return await client.variation(flagKey, user, false);
}
```

### Statsig Integration

```typescript
import { StatsigClient, User } from "statsig-node";

const statsig = new StatsigClient(process.env.STATSIG_SDK_KEY!);

export async function getStatsigFlag(userId: string, flagKey: string): Promise<boolean> {
  const user: User = { userID: userId };
  return statsig.checkGate(user, flagKey);
}
```

### GrowthBook Integration

```typescript
import { GrowthBook } from "@growthbook/sdk-js";

const gb = new GrowthBook({
  apiHost: process.env.GROWTHBOOK_API_HOST,
  clientKey: process.env.GROWTHBOOK_CLIENT_KEY,
});

export async function getGBFlag(userId: string, flagKey: string): Promise<boolean> {
  await gb.loadFeatures();
  gb.setUserAttributes({ id: userId });
  return gb.evalFeature(flagKey).value ?? false;
}
```

## References

- [Implementation patterns](references/implementation-patterns.md) — LaunchDarkly, Statsig, Edge Config integration (2025+)
- [Testing with flags](references/testing-with-flags.md) — test fixtures, flag combinations, stale flag cleanup
