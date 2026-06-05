---
name: accessibility-testing
description: Comprehensive accessibility (a11y) testing and WCAG 2.2 compliance automation.
---

# Accessibility Testing

## A11y Testing Pyramid

### Layer 1: Unit Tests (jest-axe)

```typescript
import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

test("Button is accessible", async () => {
  const { container } = render(
    <button type="button" aria-label="Close dialog">
      <CloseIcon />
    </button>
  );
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

test("Form has proper labels", async () => {
  const { container } = render(
    <form>
      <label htmlFor="email">Email</label>
      <input id="email" type="email" required />
      <button type="submit">Submit</button>
    </form>
  );
  expect(await axe(container)).toHaveNoViolations();
});
```

### Layer 2: Integration Tests (Playwright + axe)

```typescript
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("home page has no a11y violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

test("login form is accessible", async ({ page }) => {
  await page.goto("/login");
  const results = await new AxeBuilder({ page })
    .include("#login-form")
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

### Layer 3: Manual Testing

Manual screen reader testing is essential. Automated tools catch ~30-40% of a11y issues.
Verify: reading order, announcement clarity, interaction flow, live region timing.

## WCAG 2.2 Quick Reference

### Level A (Minimum)

| Criterion | Check |
|-----------|-------|
| Alt text for images | 1.1.1 |
| Captions for video | 1.2.2 |
| Not by color alone | 1.3.3 |
| Keyboard accessible | 2.1.1 |
| No keyboard trap | 2.1.2 |
| Skip navigation present | 2.4.1 |
| Descriptive page title | 2.4.2 |
| Logical focus order | 2.4.3 |
| Link purpose clear | 2.4.4 |
| `<html lang="en">` | 3.1.1 |
| Valid HTML | 4.1.1 |
| ARIA roles assigned | 4.1.2 |

### Level AA (Standard)

| Criterion | Check |
|-----------|-------|
| Contrast (text) | 1.4.3 (≥4.5:1) |
| Contrast (large) | 1.4.3 (≥3:1) |
| Text resizable 200% | 1.4.4 |
| Focus indicator visible | 2.4.7 |
| Multiple ways to find pages | 2.4.5 |
| Consistent navigation | 3.2.3 |

### Level AAA (Enhanced)

| Criterion | Check |
|-----------|-------|
| Enhanced contrast | 1.4.6 (≥7:1) |
| Link purpose from text | 2.4.9 |

## Color Contrast

### Calculation

```typescript
function relativeLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function contrastRatio(fg: [number, number, number], bg: [number, number, number]): number {
  const l1 = relativeLuminance(...fg);
  const l2 = relativeLuminance(...bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// WCAG AA: ≥4.5:1 normal, ≥3:1 large
// WCAG AAA: ≥7:1 normal, ≥4.5:1 large
```

### Automated Testing

```typescript
test("all text meets AA contrast", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page })
    .withRules(["color-contrast"])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

## Focus Management

### Tab Order Verification

```typescript
test("tab order follows logical sequence", async ({ page }) => {
  await page.goto("/");
  const expectedOrder = ["skip-link", "nav-home", "nav-about", "search-input"];
  const actualOrder: string[] = [];

  for (let i = 0; i < expectedOrder.length; i++) {
    await page.keyboard.press("Tab");
    const id = await page.evaluate(() => document.activeElement?.id);
    actualOrder.push(id ?? "unknown");
  }
  expect(actualOrder).toEqual(expectedOrder);
});
```

### Modal Focus Trap

```typescript
test("modal traps focus correctly", async ({ page }) => {
  await page.goto("/");
  await page.click('[data-testid="open-modal"]');

  const dialog = page.locator('[role="dialog"]');
  await expect(dialog).toBeVisible();

  const focused = await page.evaluate(() =>
    document.activeElement?.closest('[role="dialog"]') !== null
  );
  expect(focused).toBe(true);

  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  const returnedFocus = await page.evaluate(() =>
    document.activeElement?.getAttribute("data-testid")
  );
  expect(returnedFocus).toBe("open-modal");
});
```

### Skip Link

```typescript
test("skip link bypasses navigation", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  const skipLink = page.locator("#skip-link");
  await expect(skipLink).toBeFocused();
  await page.keyboard.press("Enter");
  const focused = await page.evaluate(() => document.activeElement?.id);
  expect(focused).toBe("main-content");
});
```

## ARIA Landmark Verification

```typescript
test("page has required landmarks", async ({ page }) => {
  await page.goto("/");
  const banner = page.locator('[role="banner"]');
  const main = page.locator('[role="main"]');
  const contentinfo = page.locator('[role="contentinfo"]');

  await expect(banner).toBeVisible();
  await expect(main).toBeVisible();
  await expect(contentinfo).toBeVisible();
});
```

## CI/CD Integration

### GitHub Actions with Playwright axe

```yaml
# .github/workflows/a11y.yml
name: Accessibility Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: npm install
      - run: npm run build
      - run: npx playwright install --with-deps
      - run: npx playwright test --grep @a11y
```

## Storybook a11y Addon

```bash
npm install -D @storybook/addon-a11y
```

```typescript
// .storybook/main.ts
const config: StorybookConfig = {
  addons: ["@storybook/addon-a11y"],
};
export default config;
```

```typescript
// .storybook/test-runner.ts
import { checkA11y, injectAxe } from "axe-playwright";
import type { TestRunnerConfig } from "@storybook/test-runner";

const config: TestRunnerConfig = {
  async preVisit(page) {
    await injectAxe(page);
  },
  async postVisit(page) {
    await checkA11y(page, "#storybook-root", {
      detailedReport: true,
    });
  },
};
export default config;
```

## Lighthouse CI Setup

```json
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:3000/",
        "http://localhost:3000/login"
      ],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:accessibility": [
          "error",
          { "minScore": 0.95 }
        ],
        "color-contrast": "error",
        "document-title": "error",
        "html-has-lang": "error",
        "image-alt": "error",
        "label": "error",
        "link-name": "error"
      }
    }
  }
}
```

## References

- [Automated testing patterns](references/automated-testing.md)
- [Manual testing guide](references/manual-testing.md)
