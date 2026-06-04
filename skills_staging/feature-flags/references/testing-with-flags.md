# Testing with Feature Flags

## Flag-Aware Test Fixtures

```typescript
// tests/helpers/flags.ts
import { FlagProvider } from "@/lib/feature-flags/provider";
import { render, RenderOptions } from "@testing-library/react";

type Flags = Record<string, boolean | string | number>;

function renderWithFlags(
  ui: React.ReactElement,
  flags: Flags = {},
  options?: Omit<RenderOptions, "wrapper">,
) {
  return render(ui, {
    wrapper: ({ children }) => (
      <FlagProvider flags={flags}>{children}</FlagProvider>
    ),
    ...options,
  });
}

export { renderWithFlags };
```

```typescript
// tests/Dashboard.test.tsx
import { renderWithFlags } from "./helpers/flags";
import { Dashboard } from "@/components/Dashboard";

describe("Dashboard", () => {
  it("shows new dashboard when flag enabled", () => {
    const { getByTestId } = renderWithFlags(<Dashboard />, {
      "new-dashboard": true,
    });
    expect(getByTestId("new-dashboard")).toBeInTheDocument();
  });

  it("shows legacy dashboard when flag disabled", () => {
    const { getByTestId } = renderWithFlags(<Dashboard />, {
      "new-dashboard": false,
    });
    expect(getByTestId("legacy-dashboard")).toBeInTheDocument();
  });

  it("shows both sidebar variants", () => {
    // Test control variant
    const { rerender, getByTestId } = renderWithFlags(<Dashboard />, {
      "sidebar-variant": "control",
    });
    expect(getByTestId("sidebar-classic")).toBeInTheDocument();

    // Test treatment variant
    rerender(
      <FlagProvider flags={{ "sidebar-variant": "compact" }}>
        <Dashboard />
      </FlagProvider>
    );
    expect(getByTestId("sidebar-compact")).toBeInTheDocument();
  });
});
```

## Testing Flag Combinations

```typescript
// Generate all flag combinations for thorough testing
function flagCombinations(flagNames: string[]): Record<string, boolean>[] {
  const combos: Record<string, boolean>[] = [];
  const total = Math.pow(2, flagNames.length);

  for (let i = 0; i < total; i++) {
    const combo: Record<string, boolean> = {};
    flagNames.forEach((name, index) => {
      combo[name] = Boolean(i & (1 << index));
    });
    combos.push(combo);
  }
  return combos;
}

// Test all combinations
const interactingFlags = ["new-checkout", "express-shipping", "loyalty-points"];
const combos = flagCombinations(interactingFlags);

describe.each(combos)("Checkout with flags %j", (flags) => {
  it("renders without crashing", () => {
    const { container } = renderWithFlags(<Checkout />, flags);
    expect(container).toBeTruthy();
  });
});
```

## Mocking Flag Services

```typescript
// LaunchDarkly mock
jest.mock("launchdarkly-react-client-sdk", () => ({
  useFlags: () => ({
    newFeature: true,
    experimentVariant: "treatment",
  }),
  useLDClient: () => ({
    identify: jest.fn(),
    track: jest.fn(),
  }),
  LDProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Statsig mock
jest.mock("@statsig/react-bindings", () => ({
  useGate: (name: string) => ({
    value: name === "new_feature" ? true : false,
  }),
  useExperiment: (name: string) => ({
    value: name === "button_test" ? { color: "green" } : {},
  }),
  StatsigProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
```

## E2E Tests with Flags

```typescript
// e2e/feature-flags.spec.ts
import { test, expect } from "@playwright/test";

// Override flags via cookie/header
test("new checkout flow with flag enabled", async ({ page }) => {
  // Set flag override cookie
  await page.context().addCookies([
    {
      name: "feature-overrides",
      value: JSON.stringify({ "new-checkout": true }),
      domain: "localhost",
      path: "/",
    },
  ]);

  await page.goto("/checkout");
  await expect(page.getByTestId("new-checkout")).toBeVisible();
});

// Or use query params for flag overrides (dev/staging only)
test("test with flag override params", async ({ page }) => {
  await page.goto("/checkout?flag_new-checkout=true");
  await expect(page.getByTestId("new-checkout")).toBeVisible();
});
```

### Flag Override Middleware (Dev/Staging Only)

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  if (process.env.NODE_ENV !== "production") {
    // Allow query param overrides in non-production
    const flagOverrides: Record<string, string> = {};
    request.nextUrl.searchParams.forEach((value, key) => {
      if (key.startsWith("flag_")) {
        flagOverrides[key.replace("flag_", "")] = value;
      }
    });
    if (Object.keys(flagOverrides).length > 0) {
      const response = NextResponse.next();
      response.cookies.set("feature-overrides", JSON.stringify(flagOverrides));
      return response;
    }
  }
  return NextResponse.next();
}
```

## Stale Flag Detection

```typescript
// scripts/find-stale-flags.ts
import { readFileSync, readdirSync, statSync } from "fs";
import { join } from "path";

interface FlagUsage {
  flag: string;
  files: string[];
  createdAt: string;
  ageInDays: number;
}

// 1. Get all defined flags
const FLAGS_FILE = "lib/flags.ts";
const flagContent = readFileSync(FLAGS_FILE, "utf-8");
const flagKeys = [...flagContent.matchAll(/"([a-z-]+)":\s*{/g)].map((m) => m[1]);

// 2. Search for usage across codebase
function findFlagUsages(flag: string, dir: string): string[] {
  const files: string[] = [];
  // Recursively search .ts/.tsx files for flag references
  function walk(d: string) {
    for (const entry of readdirSync(d)) {
      const full = join(d, entry);
      if (statSync(full).isDirectory() && !entry.startsWith(".") && entry !== "node_modules") {
        walk(full);
      } else if (/\.(ts|tsx)$/.test(entry)) {
        const content = readFileSync(full, "utf-8");
        if (content.includes(`"${flag}"`) || content.includes(`'${flag}'`)) {
          files.push(full);
        }
      }
    }
  }
  walk(dir);
  return files.filter((f) => f !== FLAGS_FILE); // exclude definition file
}

// 3. Report
const staleThreshold = 90; // days
const report: FlagUsage[] = flagKeys.map((flag) => {
  const files = findFlagUsages(flag, "src");
  return {
    flag,
    files,
    createdAt: extractCreatedAt(flag), // parse from flags definition
    ageInDays: daysSince(extractCreatedAt(flag)),
  };
});

const stale = report.filter((r) => r.ageInDays > staleThreshold);
if (stale.length > 0) {
  console.warn(`Found ${stale.length} stale flags (>${staleThreshold} days):`);
  stale.forEach((f) =>
    console.warn(`  ${f.flag} — ${f.ageInDays} days old, used in ${f.files.length} files`)
  );
  process.exit(1); // fail CI
}
```

## Flag Deprecation Workflow

```typescript
// lib/flags.ts — add deprecation support
interface FlagDefinition {
  value: FlagValue;
  description: string;
  type: "release" | "experiment" | "ops" | "permission";
  owner: string;
  createdAt: string;
  deprecated?: {
    since: string;
    removeBy: string;
    replacement?: string;
  };
}

export function getFlag<T extends FlagValue = boolean>(key: string): T {
  const flag = FLAGS[key];
  if (!flag) return false as T;

  if (flag.deprecated) {
    console.warn(
      `[FLAG DEPRECATED] "${key}" deprecated since ${flag.deprecated.since}. ` +
      `Remove by ${flag.deprecated.removeBy}. ` +
      (flag.deprecated.replacement
        ? `Use "${flag.deprecated.replacement}" instead.`
        : "")
    );
  }

  return flag.value as T;
}
```

## CI Flag Health Check

```yaml
# .github/workflows/flag-hygiene.yml
name: Flag Hygiene
on:
  schedule:
    - cron: "0 9 * * 1" # Weekly Monday 9am
  pull_request:
    paths: ["lib/flags.ts"]

jobs:
  check-flags:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npx tsx scripts/find-stale-flags.ts
```
