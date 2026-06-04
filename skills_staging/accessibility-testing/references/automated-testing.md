# Automated Accessibility Testing

## @axe-core/playwright — Complete API

```typescript
import AxeBuilder from "@axe-core/playwright";

// Run with specific WCAG tags
const results = await new AxeBuilder({ page })
  .withTags(["wcag2a", "wcag2aa", "wcag21aa", "best-practice"])
  .analyze();

// Exclude known issues (use sparingly)
const results2 = await new AxeBuilder({ page })
  .exclude("#third-party-widget")
  .disableRules(["region"]) // disable specific rules
  .analyze();

// Scan only a section
const results3 = await new AxeBuilder({ page })
  .include("#main-content")
  .analyze();
```

### Available Tags

| Tag | Description |
|-----|-------------|
| `wcag2a` | WCAG 2.0 Level A |
| `wcag2aa` | WCAG 2.0 Level AA |
| `wcag21a` | WCAG 2.1 Level A |
| `wcag21aa` | WCAG 2.1 Level AA |
| `wcag22aa` | WCAG 2.2 Level AA |
| `best-practice` | Non-WCAG best practices |
| `section508` | Section 508 compliance |

### checkA11y Options — Full Reference

```typescript
import { checkA11y, injectAxe } from "axe-playwright";

// Inject axe-core into page (required before checkA11y)
await injectAxe(page);

// Full options
await checkA11y(page, "#main-content", {
  // axe-core options
  axeOptions: {
    runOnly: {
      type: "tag",
      values: ["wcag2a", "wcag2aa", "wcag21aa"],
    },
    rules: {
      "color-contrast": { enabled: true },
      region: { enabled: false },
    },
    resultTypes: ["violations", "incomplete"],
  },
  // Reporting
  detailedReport: true,
  detailedReportOptions: {
    html: true, // include HTML snippets
  },
  // Don't throw on violations (for reporting-only mode)
  // verbose: false,
});
```

### Impact Level Filtering

```typescript
// Only fail on critical/serious violations
const results = await new AxeBuilder({ page }).analyze();

const critical = results.violations.filter(
  (v) => v.impact === "critical" || v.impact === "serious"
);
expect(critical).toEqual([]);

// Log moderate/minor as warnings
const warnings = results.violations.filter(
  (v) => v.impact === "moderate" || v.impact === "minor"
);
if (warnings.length > 0) {
  console.warn(`A11y warnings (${warnings.length}):`, warnings.map((w) => w.id));
}
```

### Rule Disabling with Documentation

```typescript
// Always document WHY a rule is disabled
const results = await new AxeBuilder({ page })
  .disableRules([
    "region", // Component tests lack page landmarks — tested at page level
    "page-has-heading-one", // Storybook wrapper doesn't have h1
  ])
  .analyze();
```

### Processing Results

```typescript
interface AxeViolation {
  id: string;           // rule ID like "color-contrast"
  impact: "critical" | "serious" | "moderate" | "minor";
  description: string;
  helpUrl: string;
  nodes: Array<{
    html: string;
    failureSummary: string;
    target: string[];   // CSS selectors
  }>;
}

function formatViolations(violations: AxeViolation[]): string {
  return violations
    .map((v) => {
      const nodes = v.nodes.map((n) => `  - ${n.html}\n    ${n.failureSummary}`);
      return `[${v.impact}] ${v.id}: ${v.description}\n${nodes.join("\n")}`;
    })
    .join("\n\n");
}

if (results.violations.length > 0) {
  throw new Error(
    `Found ${results.violations.length} a11y violations:\n${formatViolations(results.violations)}`
  );
}
```

## jest-axe — toHaveNoViolations with Custom Config

### Setup

```typescript
// jest.setup.ts
import "jest-axe/extend-expect";
```

### Custom Configuration

```typescript
import { configureAxe, axe } from "jest-axe";

// Global custom axe instance
const customAxe = configureAxe({
  rules: {
    region: { enabled: false }, // component tests lack page landmarks
    "page-has-heading-one": { enabled: false },
  },
  resultTypes: ["violations"],
  // Only check specific WCAG levels
  runOnly: {
    type: "tag",
    values: ["wcag2a", "wcag2aa"],
  },
});

test("component is accessible", async () => {
  const { container } = render(<MyComponent />);
  expect(await customAxe(container)).toHaveNoViolations();
});
```

### Testing All Component States

```typescript
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "jest-axe";

test("dropdown is accessible in all states", async () => {
  const { container, rerender } = render(<Dropdown options={options} />);

  // Closed state
  expect(await axe(container)).toHaveNoViolations();

  // Open state
  await userEvent.click(screen.getByRole("combobox"));
  expect(await axe(container)).toHaveNoViolations();

  // With selection
  await userEvent.click(screen.getByRole("option", { name: "Option 1" }));
  expect(await axe(container)).toHaveNoViolations();

  // Error state
  rerender(<Dropdown options={options} error="Required field" />);
  expect(await axe(container)).toHaveNoViolations();

  // Disabled state
  rerender(<Dropdown options={options} disabled />);
  expect(await axe(container)).toHaveNoViolations();
});
```

### Custom Matcher with Better Error Messages

```typescript
import { axe } from "jest-axe";

expect.extend({
  async toBeAccessible(container: HTMLElement) {
    const results = await axe(container);
    const pass = results.violations.length === 0;

    return {
      pass,
      message: () =>
        pass
          ? "Expected accessibility violations but found none"
          : `Found ${results.violations.length} violation(s):\n` +
            results.violations
              .map(
                (v) =>
                  `  [${v.impact}] ${v.id}: ${v.description}\n` +
                  v.nodes.map((n) => `    ${n.html}`).join("\n")
              )
              .join("\n\n"),
    };
  },
});

// Usage
test("form is accessible", async () => {
  const { container } = render(<LoginForm />);
  await expect(container).toBeAccessible();
});
```

## pa11y-ci — Multi-Page Testing

### Configuration

```json
// .pa11yci.json
{
  "defaults": {
    "timeout": 10000,
    "standard": "WCAG2AA",
    "runners": ["axe", "htmlcs"],
    "ignore": [],
    "chromeLaunchConfig": {
      "args": ["--no-sandbox"]
    }
  },
  "urls": [
    "http://localhost:3000/",
    "http://localhost:3000/login",
    {
      "url": "http://localhost:3000/dashboard",
      "actions": [
        "set field #email to test@example.com",
        "set field #password to password",
        "click element #login-button",
        "wait for url to be http://localhost:3000/dashboard"
      ]
    }
  ]
}
```

### CLI Usage

```bash
# Single URL
npx pa11y http://localhost:3000

# CI mode with config
npx pa11y-ci

# Specific standard and reporter
npx pa11y --standard WCAG2AA --reporter cli http://localhost:3000

# JSON output for CI parsing
npx pa11y --reporter json http://localhost:3000 > a11y-results.json

# Test multiple URLs from sitemap
npx pa11y-ci --sitemap http://localhost:3000/sitemap.xml
```

### pa11y with Puppeteer Actions

```javascript
// pa11y-test.js — scripted testing
const pa11y = require("pa11y");

async function runTests() {
  const results = await pa11y("http://localhost:3000/login", {
    actions: [
      "set field #email to test@test.com",
      "set field #password to password123",
      "click element [type=submit]",
      "wait for path to be /dashboard",
    ],
    screenCapture: "./screenshots/dashboard-a11y.png",
    log: { debug: console.log, error: console.error, info: console.log },
  });

  console.log(`Found ${results.issues.length} issues`);
  results.issues.forEach((issue) => {
    console.log(`[${issue.type}] ${issue.code}: ${issue.message}`);
    console.log(`  Context: ${issue.context}`);
    console.log(`  Selector: ${issue.selector}`);
  });
}
runTests();
```

## CI Integration — GitHub Actions

```yaml
# .github/workflows/a11y.yml
name: Accessibility Tests
on: [pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - run: npm ci
      - run: npx playwright install --with-deps chromium

      # Component-level a11y
      - run: npm run test -- --testPathPattern="a11y" --ci

      # E2E a11y with Playwright
      - name: Build and start
        run: |
          npm run build
          npm start &
          npx wait-on http://localhost:3000

      - run: npx playwright test e2e/a11y/

      # Lighthouse CI
      - run: npx @lhci/cli autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_TOKEN }}
```

## Custom axe Rules

```typescript
const customRules = {
  rules: [
    {
      id: "ds-button-has-type",
      selector: "button.ds-button",
      any: [
        {
          id: "has-type-attribute",
          evaluate: (node: Element) => node.hasAttribute("type"),
        },
      ],
      tags: ["best-practice"],
      metadata: {
        description: "Design system buttons must have explicit type",
        help: "Add type='button' or type='submit' attribute",
      },
    },
  ],
};

const results = await new AxeBuilder({ page })
  .options(customRules)
  .analyze();
```

## Violation Severity Guide

| Impact | Action | Examples |
|--------|--------|---------|
| **critical** | Fix immediately | Missing alt, no keyboard access, aria-hidden on focusable |
| **serious** | Fix before release | Low contrast, missing form labels, empty headings |
| **moderate** | Fix soon | Tabindex > 0, missing lang on element |
| **minor** | Track and fix | Best practice violations, redundant roles |
