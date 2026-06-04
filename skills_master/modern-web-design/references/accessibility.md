# Accessibility (A11y) Complete Guide - WCAG 2.2

## WCAG 2.2 Checklist (2025 Standard)

WCAG 2.2 is now the legal accessibility standard referenced by the European Accessibility Act (effective June 2025) and updated Section 508 guidance.

### New in WCAG 2.2

| Criterion | Level | Requirement | Implementation |
|-----------|-------|-------------|----------------|
| 2.4.11 Focus Not Obscured (Min) | AA | Focus indicator not fully hidden | Scroll padding, z-index management |
| 2.4.12 Focus Not Obscured (Enhanced) | AAA | Focus indicator fully visible | No overlapping elements |
| 2.4.13 Focus Appearance | AAA | Focus indicator ≥2px, 3:1 contrast | Custom focus styles |
| 2.5.7 Dragging Movements | AA | Single-pointer alternatives to drag | Click/tap alternatives |
| 2.5.8 Target Size (Minimum) | AA | 24×24px minimum target size | Padding, min-width/height |
| 3.2.6 Consistent Help | A | Help in same location across pages | Consistent nav placement |
| 3.3.7 Redundant Entry | A | Don't re-ask for same info | Auto-fill, session storage |
| 3.3.8 Accessible Authentication | AA | No cognitive function tests | Passkeys, magic links |
| 3.3.9 Accessible Auth (Enhanced) | AAA | No object/content recognition | Full alternatives |

### Level A (Minimum)

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 1.1.1 | Non-text content has text alternatives | `alt` on images, `aria-label` on icons |
| 1.3.1 | Info and relationships programmatically determined | Semantic HTML, proper headings |
| 1.4.1 | Color not sole means of conveying info | Add icons/text with color indicators |
| 2.1.1 | All functionality keyboard accessible | No mouse-only interactions |
| 2.4.1 | Skip navigation mechanism | Skip-to-content link |
| 2.4.2 | Pages have descriptive titles | `<title>` reflects content |
| 3.1.1 | Page language defined | `<html lang="en">` |
| 3.2.6 | Consistent Help | Help mechanism in same location |
| 3.3.7 | Redundant Entry | Don't re-request submitted info |
| 4.1.1 | No duplicate IDs | Validate HTML |

### Level AA (Standard Target)

| Criterion | Requirement | Implementation |
|-----------|-------------|----------------|
| 1.4.3 | Contrast 4.5:1 (normal), 3:1 (large) | Use contrast checker tools |
| 1.4.4 | Text resizable to 200% | Use `rem`/`em`, test zoom |
| 1.4.10 | Reflow at 320px width | Responsive design |
| 1.4.11 | Non-text contrast 3:1 | UI components, focus states |
| 2.4.6 | Headings and labels descriptive | Clear, unique headings |
| 2.4.7 | Focus visible | Never hide focus outline |
| 2.4.11 | Focus Not Obscured (Min) | Focus not fully hidden |
| 2.5.7 | Dragging Movements | Single-pointer alternatives |
| 2.5.8 | Target Size (Minimum) | 24×24px interactive areas |
| 3.2.3 | Consistent navigation | Same nav across pages |
| 3.3.8 | Accessible Authentication | No cognitive tests |

## Target Size Implementation (2.5.8)

```css
/* Minimum 24×24px for all interactive elements */
button, 
[role="button"], 
input[type="submit"],
input[type="checkbox"],
input[type="radio"],
a {
  min-width: 24px;
  min-height: 24px;
}

/* Icon buttons need explicit sizing */
.icon-btn {
  min-width: 24px;
  min-height: 24px;
  padding: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Mobile: Apple's 44×44pt recommendation */
@media (max-width: 768px) {
  button, .btn, a.nav-link { 
    min-height: 44px;
    min-width: 44px;
  }
}

/* Inline links exception: adequate spacing */
p a {
  /* Inline links exempt if line-height provides spacing */
  line-height: 1.5;
}

/* Tailwind pattern */
.btn {
  @apply min-h-[24px] min-w-[24px] px-4 py-2;
}

@media (max-width: 768px) {
  .btn { @apply min-h-[44px]; }
}
```

## Focus Not Obscured (2.4.11)

```css
/* Ensure focus is never hidden by sticky elements */
html {
  scroll-padding-top: 100px;  /* Height of sticky header */
  scroll-padding-bottom: 80px; /* Height of sticky footer */
}

/* Focus indicators with offset */
:focus-visible {
  outline: 3px solid var(--color-focus-ring, #0066cc);
  outline-offset: 4px;
  scroll-margin: 20px;
}

/* Ensure modals don't obscure focus */
.modal-open {
  overflow: hidden;
}

.modal-backdrop {
  /* Trap focus within modal */
}

/* Z-index management */
:root {
  --z-header: 100;
  --z-dropdown: 200;
  --z-modal: 300;
  --z-tooltip: 400;
}

/* Skip link that appears on focus */
.skip-link {
  position: absolute;
  top: -100px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  background: var(--color-primary);
  color: white;
  z-index: 9999;
  border-radius: 0 0 8px 8px;
  transition: top 0.2s;
}

.skip-link:focus {
  top: 0;
}
```

## Accessible Authentication (3.3.8)

```html
<!-- Allow password managers and paste -->
<input 
  type="password" 
  name="password"
  autocomplete="current-password"
  aria-describedby="password-hint"
>
<p id="password-hint">Password managers are supported</p>

<!-- Magic link alternative (no memorization required) -->
<form action="/auth/magic-link" method="POST">
  <label for="email">Email address</label>
  <input type="email" id="email" name="email" autocomplete="email" required>
  <button type="submit">Send sign-in link</button>
</form>

<!-- WebAuthn/Passkey support -->
<button onclick="authenticateWithPasskey()">
  Sign in with Passkey
</button>

<!-- Social login (delegated authentication) -->
<button onclick="signInWithGoogle()">
  Continue with Google
</button>
```

```tsx
// Passkey implementation
async function authenticateWithPasskey() {
  const credential = await navigator.credentials.get({
    publicKey: {
      challenge: new Uint8Array(32),
      rpId: window.location.hostname,
      userVerification: 'preferred',
    }
  });
  // Send credential to server for verification
}
```

## Dragging Movements (2.5.7)

```tsx
// Drag-and-drop with keyboard alternatives
function SortableList({ items, onReorder }) {
  const [draggedIndex, setDraggedIndex] = useState(null);
  
  // Keyboard support
  const handleKeyDown = (e, index) => {
    if (e.key === 'ArrowUp' && index > 0) {
      e.preventDefault();
      onReorder(index, index - 1);
    }
    if (e.key === 'ArrowDown' && index < items.length - 1) {
      e.preventDefault();
      onReorder(index, index + 1);
    }
  };
  
  return (
    <ul role="listbox" aria-label="Sortable list">
      {items.map((item, index) => (
        <li
          key={item.id}
          role="option"
          tabIndex={0}
          draggable
          onDragStart={() => setDraggedIndex(index)}
          onKeyDown={(e) => handleKeyDown(e, index)}
          aria-describedby="sort-instructions"
        >
          {item.name}
          {/* Button alternatives for mouse users */}
          <button 
            onClick={() => onReorder(index, index - 1)}
            disabled={index === 0}
            aria-label={`Move ${item.name} up`}
          >
            ↑
          </button>
          <button 
            onClick={() => onReorder(index, index + 1)}
            disabled={index === items.length - 1}
            aria-label={`Move ${item.name} down`}
          >
            ↓
          </button>
        </li>
      ))}
    </ul>
  );
}

// Instructions for screen readers
<p id="sort-instructions" className="sr-only">
  Use arrow keys to reorder items, or use the move buttons.
</p>
```

## Semantic HTML Reference

### Document Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title | Site Name</title>
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to content</a>
  
  <header role="banner">
    <nav aria-label="Main navigation">
      <!-- Primary nav -->
    </nav>
  </header>
  
  <main id="main-content">
    <article>
      <h1>Page Heading</h1>
      <!-- Content -->
    </article>
    
    <aside aria-label="Related content">
      <!-- Sidebar -->
    </aside>
  </main>
  
  <footer role="contentinfo">
    <nav aria-label="Footer navigation">
      <!-- Footer nav -->
    </nav>
  </footer>
</body>
</html>
```

## ARIA Patterns

### Buttons

```tsx
// Standard button
<button type="button">Click me</button>

// Icon-only button (MUST have label)
<button type="button" aria-label="Close dialog">
  <XIcon aria-hidden="true" />
</button>

// Toggle button
<button
  type="button"
  aria-pressed={isActive}
  onClick={() => setIsActive(!isActive)}
>
  {isActive ? 'Active' : 'Inactive'}
</button>

// Loading button
<button
  type="submit"
  aria-busy={isLoading}
  aria-disabled={isLoading}
>
  {isLoading ? (
    <>
      <Spinner aria-hidden="true" />
      <span>Saving...</span>
    </>
  ) : (
    'Save'
  )}
</button>
```

### Forms

```tsx
// Input with error
<div>
  <label htmlFor="email">Email address</label>
  <input
    id="email"
    type="email"
    aria-describedby={error ? 'email-error' : 'email-hint'}
    aria-invalid={!!error}
    autoComplete="email"
  />
  <p id="email-hint" className="hint">We'll never share your email</p>
  {error && (
    <p id="email-error" role="alert" className="error">
      {error}
    </p>
  )}
</div>

// Required field
<label htmlFor="name">
  Name <span aria-hidden="true">*</span>
  <span className="sr-only">(required)</span>
</label>
<input id="name" required aria-required="true" />
```

### Modal Dialog

```tsx
export function AccessibleDialog({ open, onClose, title, children }) {
  const titleId = useId();
  const descId = useId();

  useEffect(() => {
    if (open) {
      const previousFocus = document.activeElement as HTMLElement;
      return () => previousFocus?.focus();
    }
  }, [open]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      aria-describedby={descId}
    >
      <h2 id={titleId}>{title}</h2>
      <div id={descId}>{children}</div>
      <button onClick={onClose} aria-label="Close dialog">
        <XIcon aria-hidden="true" />
      </button>
    </div>
  );
}
```

### Live Regions

```tsx
// Status messages (polite)
<div aria-live="polite" aria-atomic="true">
  {successMessage && <p>{successMessage}</p>}
</div>

// Error alerts (assertive)
<div role="alert" aria-live="assertive">
  {errorMessage && <p>{errorMessage}</p>}
</div>

// Progress updates
<div aria-live="polite" aria-busy={isLoading}>
  {isLoading ? 'Loading...' : 'Complete'}
</div>
```

## Focus Management

### Focus Visible Styling

```css
/* Base focus style - WCAG 2.4.7 */
:focus-visible {
  outline: 3px solid var(--color-primary);
  outline-offset: 2px;
}

/* For dark backgrounds */
.dark :focus-visible {
  outline-color: white;
}

/* Enhanced focus for WCAG 2.4.13 (AAA) */
:focus-visible {
  outline: 3px solid var(--color-primary);
  outline-offset: 2px;
  /* Additional visual indicator */
  box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.3);
}

/* Tailwind pattern */
.focus-ring {
  @apply focus:outline-hidden focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2;
}
```

### Focus Trap for Modals

```tsx
import { useEffect, useRef } from 'react';

function useFocusTrap(isActive: boolean) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    firstElement?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement?.focus();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement?.focus();
      }
    };

    container.addEventListener('keydown', handleKeyDown);
    return () => container.removeEventListener('keydown', handleKeyDown);
  }, [isActive]);

  return containerRef;
}
```

## Screen Reader Utilities

```css
/* Visually hidden but accessible to screen readers */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Show on focus (for skip links) */
.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

## Automated Testing

### Playwright + axe-core

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('page meets WCAG 2.2 AA', async ({ page }) => {
    await page.goto('https://example.com');
    
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
      .analyze();
    
    expect(results.violations).toEqual([]);
  });

  test('modal is accessible', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="open-modal"]');
    
    // Check modal-specific accessibility
    const results = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .analyze();
    
    expect(results.violations).toEqual([]);
  });
});
```

### CLI Tools

```bash
# Axe CLI
npm install -g @axe-core/cli
axe https://localhost:3000 --tags wcag22aa

# Pa11y
npm install -g pa11y
pa11y https://localhost:3000 --standard WCAG2AA

# Lighthouse
npx lighthouse https://localhost:3000 --only-categories=accessibility
```

## Testing Checklist

### Manual Testing

1. **Keyboard Navigation**
   - Tab through entire page
   - All interactive elements reachable
   - Focus order logical
   - Focus visible at all times (not obscured)
   - Escape closes modals/dropdowns

2. **Screen Reader Testing**
   - Test with NVDA (Windows) or VoiceOver (Mac)
   - All content announced
   - Images have descriptions
   - Forms labeled correctly
   - Dynamic content announced via live regions

3. **Target Size Testing**
   - All interactive elements ≥24×24px
   - Mobile elements ≥44×44px
   - Inline links have adequate spacing

4. **Zoom Testing**
   - 200% zoom no horizontal scroll
   - Text reflows properly
   - No content cut off

## Common Mistakes to Avoid

1. **Images without alt text** - Every `<img>` needs `alt` (empty `alt=""` for decorative)
2. **Missing form labels** - Every input needs associated label
3. **Color-only indicators** - Add icons or text with colors
4. **Removing focus outlines** - Never `outline: none` without replacement
5. **Positive tabindex** - Avoid `tabindex > 0`
6. **Auto-playing media** - Provide pause controls
7. **Mouse-only interactions** - Add keyboard support
8. **Missing skip links** - Include for keyboard users
9. **Empty links/buttons** - Always have accessible name
10. **Low contrast text** - Meet WCAG minimums
11. **Small touch targets** - Minimum 24×24px (44×44px mobile)
12. **Hidden focus indicators** - Sticky headers can obscure focus
13. **CAPTCHA without alternatives** - Use passkeys or magic links
14. **Re-requesting entered data** - Remember form entries
