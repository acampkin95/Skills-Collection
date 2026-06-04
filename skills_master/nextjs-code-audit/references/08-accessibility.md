# 08. Accessibility Audit

## Table of Contents
1. [Automated Scans](#1-automated-scans)
2. [Semantic HTML](#2-semantic-html)
3. [ARIA Attributes](#3-aria-attributes)
4. [Keyboard Navigation](#4-keyboard-navigation)
5. [Forms & Labels](#5-forms--labels)
6. [Images & Media](#6-images--media)

---

## 1. Automated Scans

### Tools

```bash
# Axe CLI
npx @axe-core/cli http://localhost:3000

# Pa11y
npx pa11y http://localhost:3000

# Lighthouse accessibility audit
npx lighthouse http://localhost:3000 \
  --only-categories=accessibility \
  --output html \
  --output-path ./a11y-report.html

# ESLint a11y plugin
npx eslint . --ext .tsx --plugin jsx-a11y
```

### React Testing Library + axe

```typescript
// In test files
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

test('component is accessible', async () => {
  const { container } = render(<MyComponent />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

### Playwright Accessibility

```typescript
// e2e/a11y.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('page is accessible', async ({ page }) => {
  await page.goto('/')
  
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze()
  
  expect(results.violations).toEqual([])
})
```

---

## 2. Semantic HTML

### Detection

```bash
# Find non-semantic elements
echo "=== Non-semantic elements ==="
grep -rn "<div.*onClick\|<span.*onClick" --include="*.tsx" app/ components/

# Missing landmarks
echo ""
echo "=== Check for landmarks ==="
echo "main: $(grep -rn "<main" --include="*.tsx" app/ | wc -l)"
echo "nav: $(grep -rn "<nav" --include="*.tsx" app/ components/ | wc -l)"
echo "header: $(grep -rn "<header" --include="*.tsx" app/ components/ | wc -l)"
echo "footer: $(grep -rn "<footer" --include="*.tsx" app/ components/ | wc -l)"
echo "article: $(grep -rn "<article" --include="*.tsx" app/ components/ | wc -l)"
echo "section: $(grep -rn "<section" --include="*.tsx" app/ components/ | wc -l)"

# Heading hierarchy
echo ""
echo "=== Headings ==="
grep -rn "<h[1-6]" --include="*.tsx" app/ | sed 's/.*<h\([1-6]\).*/h\1/' | sort | uniq -c

# Buttons vs divs with onClick
echo ""
echo "=== Click handlers ==="
echo "button onClick: $(grep -rn "<button.*onClick\|<Button.*onClick" --include="*.tsx" app/ components/ | wc -l)"
echo "div onClick: $(grep -rn "<div.*onClick" --include="*.tsx" app/ components/ | wc -l)"
```

### Fixes

```typescript
// ❌ Non-semantic clickable div
<div onClick={handleClick}>Click me</div>

// ✅ Use button
<button onClick={handleClick}>Click me</button>

// ❌ Div for navigation
<div className="nav">
  <a href="/">Home</a>
</div>

// ✅ Use nav
<nav aria-label="Main navigation">
  <a href="/">Home</a>
</nav>

// ❌ Missing main landmark
<div className="content">{children}</div>

// ✅ Use main
<main id="main-content">{children}</main>

// ❌ Skip to div
<h1>Title</h1>
<h3>Subtitle</h3>

// ✅ Proper heading hierarchy
<h1>Title</h1>
<h2>Subtitle</h2>
```

---

## 3. ARIA Attributes

### Detection

```bash
# ARIA usage
grep -rn "aria-" --include="*.tsx" app/ components/ | wc -l

# Specific ARIA attributes
echo "=== ARIA Usage ==="
echo "aria-label: $(grep -rn "aria-label=" --include="*.tsx" . | wc -l)"
echo "aria-labelledby: $(grep -rn "aria-labelledby=" --include="*.tsx" . | wc -l)"
echo "aria-describedby: $(grep -rn "aria-describedby=" --include="*.tsx" . | wc -l)"
echo "aria-hidden: $(grep -rn "aria-hidden=" --include="*.tsx" . | wc -l)"
echo "aria-live: $(grep -rn "aria-live=" --include="*.tsx" . | wc -l)"
echo "role=: $(grep -rn 'role="' --include="*.tsx" . | wc -l)"

# Missing ARIA on interactive elements
echo ""
echo "=== Interactive without labels ==="
grep -rn "<button>" --include="*.tsx" app/ components/ | grep -v "aria-label"
```

### Common Patterns

```typescript
// Icon-only button needs label
<button aria-label="Close dialog" onClick={onClose}>
  <XIcon />
</button>

// Loading state
<button aria-busy={isLoading} disabled={isLoading}>
  {isLoading ? 'Saving...' : 'Save'}
</button>

// Expandable section
<button 
  aria-expanded={isOpen}
  aria-controls="details-section"
  onClick={() => setIsOpen(!isOpen)}
>
  Details
</button>
<div id="details-section" hidden={!isOpen}>
  Content
</div>

// Modal dialog
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
>
  <h2 id="dialog-title">Dialog Title</h2>
</div>

// Live region for updates
<div aria-live="polite" aria-atomic="true">
  {message && <p>{message}</p>}
</div>
```

---

## 4. Keyboard Navigation

### Detection

```bash
# Interactive elements without keyboard handling
echo "=== Keyboard handling ==="
echo "onKeyDown: $(grep -rn "onKeyDown\|onKeyUp\|onKeyPress" --include="*.tsx" app/ components/ | wc -l)"

# tabIndex usage
grep -rn "tabIndex" --include="*.tsx" app/ components/

# Focus management
grep -rn "focus()\|\.focus\|autoFocus" --include="*.tsx" app/ components/
```

### Patterns

```typescript
// Keyboard-accessible custom component
function CustomButton({ onClick, children }) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onClick()
    }
  }
  
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKeyDown}
    >
      {children}
    </div>
  )
}

// Skip link
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>

// Focus trap in modal
import { FocusTrap } from '@headlessui/react'

<FocusTrap>
  <div role="dialog">
    {/* Modal content */}
  </div>
</FocusTrap>

// Focus management after action
const buttonRef = useRef<HTMLButtonElement>(null)

useEffect(() => {
  if (showSuccess) {
    buttonRef.current?.focus()
  }
}, [showSuccess])
```

---

## 5. Forms & Labels

### Detection

```bash
# Inputs without labels
echo "=== Form accessibility ==="
grep -rn "<input" --include="*.tsx" app/ components/ | \
  grep -v "aria-label\|id=.*label\|aria-labelledby" | head -10

# Missing htmlFor
grep -rn "<label" --include="*.tsx" app/ components/ | grep -v "htmlFor" | head -10

# Form without fieldset/legend
echo ""
echo "fieldset usage: $(grep -rn "<fieldset" --include="*.tsx" app/ components/ | wc -l)"
echo "legend usage: $(grep -rn "<legend" --include="*.tsx" app/ components/ | wc -l)"
```

### Patterns

```typescript
// Proper label association
<div>
  <label htmlFor="email">Email address</label>
  <input id="email" type="email" name="email" />
</div>

// Required field
<label htmlFor="name">
  Name <span aria-hidden="true">*</span>
</label>
<input 
  id="name" 
  name="name" 
  aria-required="true"
  aria-describedby="name-hint name-error"
/>
<p id="name-hint">Enter your full name</p>
{error && <p id="name-error" role="alert">{error}</p>}

// Form group with fieldset
<fieldset>
  <legend>Shipping Address</legend>
  {/* Address fields */}
</fieldset>

// Error handling
<input
  id="email"
  type="email"
  aria-invalid={!!errors.email}
  aria-describedby={errors.email ? 'email-error' : undefined}
/>
{errors.email && (
  <p id="email-error" role="alert" className="text-red-500">
    {errors.email}
  </p>
)}
```

---

## 6. Images & Media

### Detection

```bash
# Images without alt
echo "=== Images ==="
grep -rn "<img\|<Image" --include="*.tsx" app/ components/ | grep -v 'alt=' | head -10

# Empty alt (decorative)
grep -rn 'alt=""' --include="*.tsx" app/ components/ | wc -l

# Meaningful alt
grep -rn 'alt="[^"]' --include="*.tsx" app/ components/ | head -10

# Video/audio without captions
grep -rn "<video\|<audio" --include="*.tsx" app/ components/
```

### Patterns

```typescript
// Meaningful image
<Image 
  src="/profile.jpg" 
  alt="John Doe, Software Engineer"
  width={100}
  height={100}
/>

// Decorative image
<Image 
  src="/decoration.svg" 
  alt="" 
  aria-hidden="true"
  width={50}
  height={50}
/>

// Image in link
<a href="/profile">
  <Image src="/avatar.jpg" alt="" />
  <span>View John's profile</span>
</a>

// Video with captions
<video controls>
  <source src="/video.mp4" type="video/mp4" />
  <track 
    kind="captions" 
    src="/captions.vtt" 
    srcLang="en" 
    label="English"
  />
</video>

// SVG accessibility
<svg role="img" aria-labelledby="chart-title chart-desc">
  <title id="chart-title">Sales Chart</title>
  <desc id="chart-desc">Bar chart showing monthly sales from January to June</desc>
  {/* Chart content */}
</svg>
```

---

## Accessibility Score

| Category | Weight | Checks |
|----------|--------|--------|
| Semantic HTML | 25% | Landmarks, headings, buttons |
| ARIA | 20% | Labels, states, live regions |
| Keyboard | 20% | Focus, navigation, traps |
| Forms | 20% | Labels, errors, hints |
| Images | 15% | Alt text, decorative handling |

**Target Score:** 90+
