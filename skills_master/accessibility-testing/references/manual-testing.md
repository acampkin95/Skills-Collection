# Manual Accessibility Testing

## Keyboard-Only Navigation Audit

### Full Keyboard Testing Checklist (25 Items)

```markdown
## Keyboard Audit: [Page Name] — [Date]

### General Navigation
- [ ] All interactive elements reachable via Tab
- [ ] Focus order follows visual/logical layout
- [ ] Focus indicator is clearly visible (not just browser default)
- [ ] Focus indicator has ≥ 3:1 contrast against adjacent colors
- [ ] No keyboard traps (can always Tab/Escape out)
- [ ] Skip-to-content link present and working
- [ ] Skip link visible on focus
- [ ] Reverse tab (Shift+Tab) works correctly
- [ ] No positive tabindex values used (tabindex > 0)
- [ ] Hidden/offscreen elements not in tab order

### Interactive Elements
- [ ] Buttons activate with Enter and Space
- [ ] Links activate with Enter only (not Space)
- [ ] Checkboxes toggle with Space
- [ ] Radio buttons navigate with Arrow keys
- [ ] Select/dropdown opens with Enter/Space/Arrow
- [ ] Custom components follow ARIA pattern keyboard interaction
- [ ] Tooltips dismiss with Escape
- [ ] Autocomplete navigable with Arrow keys, selectable with Enter

### Modal/Dialog
- [ ] Focus moves to modal on open
- [ ] Focus trapped inside modal
- [ ] Escape closes modal
- [ ] Focus returns to trigger element on close
- [ ] Background content is inert (aria-hidden or inert attribute)

### Navigation & Menus
- [ ] Menu items navigable with Arrow keys
- [ ] Escape closes submenus and returns focus to parent
```

### Playwright Keyboard Audit Script

```typescript
// e2e/keyboard-audit.spec.ts
import { test, expect, Page } from "@playwright/test";

async function getAllFocusableElements(page: Page) {
  return page.evaluate(() => {
    const selector = [
      "a[href]",
      "button:not([disabled])",
      "input:not([disabled]):not([type='hidden'])",
      "select:not([disabled])",
      "textarea:not([disabled])",
      "[tabindex]:not([tabindex='-1'])",
      "[contenteditable='true']",
    ].join(", ");
    return Array.from(document.querySelectorAll(selector)).map((el) => ({
      tag: el.tagName.toLowerCase(),
      id: el.id,
      text: el.textContent?.trim().slice(0, 50),
      role: el.getAttribute("role"),
      tabIndex: (el as HTMLElement).tabIndex,
    }));
  });
}

test("audit focusable elements", async ({ page }) => {
  await page.goto("/");
  const elements = await getAllFocusableElements(page);
  console.table(elements);

  // Verify no positive tabindex (anti-pattern)
  const positiveTabindex = elements.filter((e) => e.tabIndex > 0);
  expect(positiveTabindex).toEqual([]);
});

test("tab through entire page without traps", async ({ page }) => {
  await page.goto("/");
  const totalFocusable = await getAllFocusableElements(page);
  const maxTabs = totalFocusable.length + 5;

  const visited: string[] = [];
  for (let i = 0; i < maxTabs; i++) {
    await page.keyboard.press("Tab");
    const activeId = await page.evaluate(() => {
      const el = document.activeElement;
      return el?.id || el?.tagName || "unknown";
    });

    if (visited.includes(activeId) && activeId === visited[0]) {
      break;
    }
    visited.push(activeId);
  }

  expect(visited.length).toBeGreaterThanOrEqual(totalFocusable.length - 1);
});
```

## Screen Reader Testing

### VoiceOver (macOS) — Complete Commands Table

**Toggle:** Cmd+F5 | **VO key:** Ctrl+Option (abbreviated as VO)

#### Basic Navigation

| Action | Shortcut |
|--------|----------|
| Next element | VO + Right Arrow |
| Previous element | VO + Left Arrow |
| Activate/click | VO + Space |
| Read all from cursor | VO + A |
| Stop reading | Ctrl |
| Read current element | VO + F3 |
| Go to top of page | VO + Home |
| Go to bottom of page | VO + End |

#### Heading Navigation

| Action | Shortcut |
|--------|----------|
| Next heading | VO + Cmd + H |
| Previous heading | VO + Cmd + Shift + H |
| Heading level 1-6 | VO + Cmd + 1-6 (in Web Rotor) |

#### Landmark & Structure

| Action | Shortcut |
|--------|----------|
| Open Rotor | VO + U |
| Navigate in Rotor | Left/Right Arrow (category), Up/Down (items) |
| Next landmark | Rotor → Landmarks → Down Arrow |
| Next link | Rotor → Links → Down Arrow |
| Next form control | Rotor → Form Controls → Down Arrow |
| Next table | VO + Cmd + T |
| Navigate table cells | VO + Arrow keys (within table) |

#### Forms & Interaction

| Action | Shortcut |
|--------|----------|
| Enter form interaction | VO + Shift + Down Arrow |
| Exit form interaction | VO + Shift + Up Arrow |
| Select checkbox/radio | VO + Space |
| Open select menu | VO + Space |
| Read form label | VO + F3 (when focused) |

#### Advanced

| Action | Shortcut |
|--------|----------|
| Open VoiceOver Help | VO + H |
| Find text on page | VO + F |
| Read link URL | VO + U (on a link) |
| Read word/character | VO + W / VO + C |
| Increase/decrease value | VO + Up/Down (on slider/stepper) |

#### VoiceOver Testing Checklist

```markdown
- [ ] Page title announced on load
- [ ] Headings read in correct order (use VO+Cmd+H to cycle)
- [ ] Images have descriptive alt text (or hidden from AT)
- [ ] Form labels read when field is focused
- [ ] Required fields announced as "required"
- [ ] Error messages announced via aria-live or focus move
- [ ] Button purpose clear from announcement alone
- [ ] Links describe destination (not "click here")
- [ ] Tables have headers announced with data cells
- [ ] Dynamic content changes announced (live regions)
- [ ] Modal announced as "dialog" with name
- [ ] Loading states announced ("Loading..." via aria-live)
- [ ] Rotor shows logical heading/landmark structure
```

### NVDA (Windows) — Navigation Cheatsheet

**Toggle:** Ctrl+Alt+N | **NVDA key:** Insert (or Caps Lock if remapped)

#### Browse Mode (Reading)

| Action | Shortcut |
|--------|----------|
| Next element | Down Arrow |
| Previous element | Up Arrow |
| Read all | Insert + Down Arrow |
| Stop speech | Ctrl |
| Read current line | Insert + Up Arrow |
| Read current word | Insert + Numpad 5 |

#### Quick Navigation (Single Letters in Browse Mode)

| Key | Navigates to |
|-----|-------------|
| H | Next heading |
| 1-6 | Next heading at level 1-6 |
| K | Next link |
| U | Next unvisited link |
| V | Next visited link |
| F | Next form field |
| B | Next button |
| T | Next table |
| L | Next list |
| I | Next list item |
| D | Next landmark |
| G | Next graphic |
| Shift + [key] | Previous of same type |

#### Forms Mode

| Action | Shortcut |
|--------|----------|
| Enter forms mode | Enter (on form field) |
| Exit forms mode | Escape |
| Toggle forms/browse | Insert + Space |
| Next form field | Tab |
| Submit form | Enter (on submit button) |

#### Element Lists (Like VoiceOver Rotor)

| Action | Shortcut |
|--------|----------|
| Elements list | Insert + F7 |
| Headings list | Insert + F7 → select Headings |
| Links list | Insert + F7 → select Links |
| Landmarks list | Insert + F7 → select Landmarks |

#### NVDA Testing Checklist

```markdown
- [ ] Page title spoken on load (Insert+T)
- [ ] Browse mode navigation follows visual order
- [ ] Headings list (Insert+F7) shows correct hierarchy
- [ ] Landmarks list shows banner, nav, main, contentinfo
- [ ] Forms mode auto-enters on form fields
- [ ] Form labels announced correctly
- [ ] Error messages spoken on invalid submission
- [ ] Live regions announce dynamic updates
- [ ] Tables read with row/column headers
- [ ] ARIA widgets announce role and state
```

## Focus Trap Testing

```typescript
// e2e/focus-trap.spec.ts
test("dialog focus trap", async ({ page }) => {
  await page.goto("/");
  await page.click('[data-testid="open-dialog"]');

  const dialog = page.locator('[role="dialog"]');
  await expect(dialog).toBeVisible();

  const focusable = await dialog.evaluate((el) => {
    const elements = el.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    return Array.from(elements).map((e) => e.id || e.tagName);
  });

  for (const _ of focusable) {
    await page.keyboard.press("Tab");
    const inDialog = await page.evaluate(() =>
      document.activeElement?.closest('[role="dialog"]') !== null
    );
    expect(inDialog).toBe(true);
  }

  // One more Tab should wrap to first element
  await page.keyboard.press("Tab");
  const wrappedBack = await page.evaluate(() =>
    document.activeElement?.closest('[role="dialog"]') !== null
  );
  expect(wrappedBack).toBe(true);
});
```

## Live Region Testing

```typescript
test("status messages announced", async ({ page }) => {
  await page.goto("/form");
  await page.fill("#email", "test@example.com");
  await page.click('[type="submit"]');

  const liveRegion = page.locator('[aria-live="polite"], [role="status"]');
  await expect(liveRegion).toContainText("submitted successfully");
});

test("error messages announced", async ({ page }) => {
  await page.goto("/form");
  await page.click('[type="submit"]');

  const errorRegion = page.locator('[aria-live="assertive"], [role="alert"]');
  await expect(errorRegion).toBeVisible();
});
```

## High Contrast Mode Testing

```typescript
test("UI works in forced-colors mode", async ({ page }) => {
  await page.emulateMedia({ forcedColors: "active" });
  await page.goto("/");

  await page.screenshot({ path: "high-contrast.png", fullPage: true });

  const focusStyle = await page.evaluate(() => {
    const btn = document.querySelector("button");
    btn?.focus();
    const styles = window.getComputedStyle(btn!, ":focus-visible");
    return {
      outline: styles.outlineStyle,
      outlineWidth: styles.outlineWidth,
    };
  });
  expect(focusStyle.outline).not.toBe("none");
});
```

## Complete Audit Template

```markdown
# Accessibility Audit Report

## Page: _______________
## Date: _______________
## Standard: WCAG 2.2 AA

### Automated Results
- axe-core violations: ___
- Lighthouse score: ___/100

### Keyboard
- [ ] All controls reachable
- [ ] Logical tab order
- [ ] Visible focus indicator
- [ ] No keyboard traps
- [ ] Skip link works

### Screen Reader
- [ ] Page title meaningful
- [ ] Heading hierarchy correct
- [ ] Images described
- [ ] Forms labeled
- [ ] Errors announced
- [ ] Dynamic content announced

### Visual
- [ ] Color contrast ≥ 4.5:1 (text) / 3:1 (large text)
- [ ] Not color-only information
- [ ] Text resizable to 200%
- [ ] Reflow at 320px width
- [ ] Focus indicator visible

### Findings
| # | Issue | WCAG | Impact | Element | Fix |
|---|-------|------|--------|---------|-----|
| 1 | | | | | |
```
