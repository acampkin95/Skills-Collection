# Feature Flag Implementation Patterns

## LaunchDarkly SDK

### Server-Side (Node.js)

```typescript
// lib/launchdarkly-server.ts
import LaunchDarkly from "@launchdarkly/node-server-sdk";

let client: LaunchDarkly.LDClient;

export async function getLDClient(): Promise<LaunchDarkly.LDClient> {
  if (!client) {
    client = LaunchDarkly.init(process.env.LAUNCHDARKLY_SDK_KEY!);
    await client.waitForInitialization({ timeout: 5 });
  }
  return client;
}

export async function getFlag<T>(
  key: string,
  user: { key: string; email?: string; custom?: Record<string, any> },
  defaultValue: T,
): Promise<T> {
  const ld = await getLDClient();
  const context: LaunchDarkly.LDContext = {
    kind: "user",
    key: user.key,
    email: user.email,
    ...user.custom,
  };
  return ld.variation(key, context, defaultValue) as T;
}

// In an API route or server component
export default async function Page() {
  const showNewUI = await getFlag("new-ui", { key: userId }, false);
  return showNewUI ? <NewUI /> : <OldUI />;
}
```

### Client-Side (React)

```tsx
// app/providers.tsx
"use client";

import { LDProvider } from "launchdarkly-react-client-sdk";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <LDProvider
      clientSideID={process.env.NEXT_PUBLIC_LD_CLIENT_ID!}
      context={{
        kind: "user",
        key: "anonymous",
      }}
    >
      {children}
    </LDProvider>
  );
}

// components/Feature.tsx
"use client";

import { useFlags, useLDClient } from "launchdarkly-react-client-sdk";

function FeatureComponent() {
  const { newCheckout, searchAlgorithm } = useFlags();
  const ldClient = useLDClient();

  // Update context when user logs in
  useEffect(() => {
    if (user) {
      ldClient?.identify({
        kind: "user",
        key: user.id,
        email: user.email,
        custom: { plan: user.plan },
      });
    }
  }, [user, ldClient]);

  if (newCheckout) {
    return <NewCheckout />;
  }
  return <StandardCheckout />;
}
```

## Statsig SDK

### Server-Side

```typescript
// lib/statsig-server.ts
import Statsig from "statsig-node";

let initialized = false;

export async function initStatsig() {
  if (!initialized) {
    await Statsig.initialize(process.env.STATSIG_SERVER_KEY!, {
      environment: { tier: process.env.NODE_ENV },
    });
    initialized = true;
  }
}

export async function checkGate(
  userId: string,
  gateName: string,
): Promise<boolean> {
  await initStatsig();
  const user = { userID: userId };
  return Statsig.checkGate(user, gateName);
}

export async function getExperiment(
  userId: string,
  experimentName: string,
): Promise<Record<string, any>> {
  await initStatsig();
  const user = { userID: userId };
  const experiment = Statsig.getExperiment(user, experimentName);
  return experiment.value;
}

// Usage in server component
export default async function PricingPage() {
  const variant = await getExperiment(userId, "pricing_page_test");
  const layout = variant.layout ?? "default"; // "default" | "comparison" | "minimal"

  return <PricingLayout variant={layout} />;
}
```

### Client-Side

```tsx
"use client";

import { StatsigProvider, useGate, useExperiment } from "@statsig/react-bindings";
import { StatsigClient } from "@statsig/js-client";

const client = new StatsigClient(
  process.env.NEXT_PUBLIC_STATSIG_CLIENT_KEY!,
  { userID: "anonymous" },
);

export function StatsigWrapper({ children }: { children: React.ReactNode }) {
  return (
    <StatsigProvider client={client}>
      {children}
    </StatsigProvider>
  );
}

function Component() {
  const gate = useGate("new_feature");
  const experiment = useExperiment("button_color_test");
  const buttonColor = experiment.value.color ?? "blue";

  if (gate.value) {
    return <button style={{ backgroundColor: buttonColor }}>New Feature</button>;
  }
  return null;
}
```

## Vercel Edge Config Pattern

```typescript
// lib/edge-flags.ts
import { get } from "@vercel/edge-config";

interface EdgeFlags {
  "maintenance-mode": boolean;
  "new-pricing": boolean;
  "api-rate-limit": number;
  "allowed-beta-emails": string[];
}

export async function getEdgeFlags(): Promise<Partial<EdgeFlags>> {
  try {
    const flags = await get<EdgeFlags>("feature-flags");
    return flags ?? {};
  } catch {
    return {};
  }
}

export async function isMaintenanceMode(): Promise<boolean> {
  const flags = await getEdgeFlags();
  return flags["maintenance-mode"] ?? false;
}
```

```typescript
// middleware.ts — Edge Config is ultra-fast in middleware
import { NextRequest, NextResponse } from "next/server";
import { get } from "@vercel/edge-config";

export async function middleware(request: NextRequest) {
  const maintenance = await get<boolean>("maintenance-mode");
  if (maintenance) {
    return NextResponse.rewrite(new URL("/maintenance", request.url));
  }

  const betaEmails = await get<string[]>("allowed-beta-emails");
  const userEmail = request.cookies.get("user-email")?.value;

  if (
    request.nextUrl.pathname.startsWith("/beta") &&
    !betaEmails?.includes(userEmail ?? "")
  ) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}
```

## Gradual Rollout with Sticky Bucketing

```typescript
// lib/rollout.ts
import { createHash } from "crypto";

interface RolloutConfig {
  flag: string;
  percentage: number; // 0-100
  salt?: string;
}

export function isUserInRollout(
  userId: string,
  config: RolloutConfig,
): boolean {
  const input = `${config.flag}:${config.salt ?? "default"}:${userId}`;
  const hash = createHash("sha256").update(input).digest("hex");
  const bucket = parseInt(hash.slice(0, 8), 16) % 100;
  return bucket < config.percentage;
}

// Gradual rollout: 10% → 25% → 50% → 100%
const rollout: RolloutConfig = {
  flag: "new-search",
  percentage: 25, // currently at 25%
  salt: "v1",     // change salt to re-randomize buckets
};

function SearchPage({ userId }: { userId: string }) {
  if (isUserInRollout(userId, rollout)) {
    return <NewSearch />;
  }
  return <OldSearch />;
}
```

## Multi-Variant Experiment

```typescript
interface Experiment<T extends string> {
  name: string;
  variants: Record<T, number>; // variant name → weight
  salt: string;
}

function assignVariant<T extends string>(
  userId: string,
  experiment: Experiment<T>,
): T {
  const hash = simpleHash(`${experiment.name}:${experiment.salt}:${userId}`);
  const bucket = hash % 100;

  let cumulative = 0;
  for (const [variant, weight] of Object.entries(experiment.variants) as [T, number][]) {
    cumulative += weight;
    if (bucket < cumulative) {
      return variant;
    }
  }

  return Object.keys(experiment.variants)[0] as T;
}

// Usage
const pricingTest: Experiment<"control" | "annual-first" | "enterprise-highlight"> = {
  name: "pricing-page-2025",
  variants: {
    "control": 34,
    "annual-first": 33,
    "enterprise-highlight": 33,
  },
  salt: "v1",
};

const variant = assignVariant(userId, pricingTest);
```
