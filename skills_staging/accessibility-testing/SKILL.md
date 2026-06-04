---
name: accessibility-testing
description: Accessibility testing and WCAG 2.2 compliance for React/Next.js. Use for axe-core audits, ARIA validation, keyboard nav, color contrast, and CI a11y pipelines.
version: 2.0.0
reviewed: "2026-06-04"
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

## References

- [Automated testing patterns](references/automated-testing.md)
- [Manual testing guide](references/manual-testing.md)


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.