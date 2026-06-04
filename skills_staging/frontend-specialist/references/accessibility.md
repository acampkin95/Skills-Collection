# Accessibility Reference

## Quick Checklist

### Must Have (Level A)
- [ ] All images have `alt` text
- [ ] Form inputs have associated `<label>`
- [ ] Color is not the only way to convey information
- [ ] All functionality available via keyboard
- [ ] Focus indicator visible
- [ ] Page has a `<title>`
- [ ] Language declared with `<html lang="en">`

### Should Have (Level AA)
- [ ] Color contrast 4.5:1 for text, 3:1 for large text
- [ ] Text resizable to 200% without loss of functionality
- [ ] Skip link to main content
- [ ] Consistent navigation
- [ ] Error messages identify the field and describe the error
- [ ] Headings are hierarchical (h1 → h2 → h3)

## Semantic HTML

### Landmark Regions

```tsx
<header>          {/* Site header */}
<nav>             {/* Navigation */}
<main>            {/* Main content (one per page) */}
<aside>           {/* Sidebar/complementary */}
<footer>          {/* Site footer */}
<section>         {/* Thematic grouping */}
<article>         {/* Self-contained content */}
```

### Correct Structure

```tsx
// ✅ Correct
<main>
  <h1>Page Title</h1>
  <section aria-labelledby="section-heading">
    <h2 id="section-heading">Section</h2>
    <article>
      <h3>Article Title</h3>
      <p>Content...</p>
    </article>
  </section>
</main>

// ❌ Wrong - div soup
<div className="main">
  <div className="title">Page Title</div>
  <div className="section">
    <div className="heading">Section</div>
  </div>
</div>
```

## Keyboard Navigation

### Focus Management

```tsx
// Visible focus indicator
<button className="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">
  Click me
</button>

// Custom focus styles
.focus-ring {
  @apply focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2;
}
```

### Skip Link

```tsx
// At the very top of the page
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-white focus:px-4 focus:py-2 focus:text-black"
>
  Skip to main content
</a>

// Main content
<main id="main-content" tabIndex={-1}>
  {/* Content */}
</main>
```

### Focus Trap (Modals)

```tsx
// Using @radix-ui or similar handles this automatically
// Manual implementation:
import { useFocusTrap } from '@/hooks/use-focus-trap'

function Modal({ open, children }) {
  const ref = useFocusTrap(open)
  
  return (
    <div ref={ref} role="dialog" aria-modal="true">
      {children}
    </div>
  )
}
```

### Keyboard Patterns

| Component | Keys |
|-----------|------|
| Button | Enter, Space |
| Link | Enter |
| Menu | Arrow keys, Enter, Escape |
| Dialog | Escape to close, Tab trapped |
| Tabs | Arrow keys, Home, End |
| Combobox | Arrow keys, Enter, Escape |

## ARIA Patterns

### Interactive Components

```tsx
// Button
<button 
  type="button"
  aria-pressed={isActive}
  aria-expanded={isExpanded}
  aria-controls="panel-id"
>

// Toggle
<button
  role="switch"
  aria-checked={isOn}
>

// Menu
<button aria-haspopup="menu" aria-expanded={open}>
  Menu
</button>
<ul role="menu" hidden={!open}>
  <li role="menuitem">Item 1</li>
</ul>

// Tabs
<div role="tablist">
  <button role="tab" aria-selected={active} aria-controls="panel-1">
    Tab 1
  </button>
</div>
<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
  Content
</div>
```

### Live Regions

```tsx
// Polite announcements (wait for idle)
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// Assertive announcements (interrupt)
<div aria-live="assertive" role="alert">
  {errorMessage}
</div>

// Status updates
<div role="status" aria-live="polite">
  Loading... {progress}%
</div>
```

### Labels and Descriptions

```tsx
// Visible label
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// Hidden label (icon button)
<button aria-label="Close dialog">
  <XIcon />
</button>

// Described by
<input
  aria-describedby="email-hint email-error"
/>
<p id="email-hint">We'll never share your email</p>
<p id="email-error" role="alert">Invalid email format</p>

// Labelled by
<section aria-labelledby="section-title">
  <h2 id="section-title">Features</h2>
</section>
```

## Forms

### Accessible Form Pattern

```tsx
<form onSubmit={handleSubmit}>
  <div className="space-y-4">
    {/* Input with label */}
    <div>
      <label htmlFor="name" className="block text-sm font-medium">
        Name <span aria-hidden="true" className="text-red-500">*</span>
      </label>
      <input
        id="name"
        type="text"
        required
        aria-required="true"
        aria-invalid={errors.name ? "true" : undefined}
        aria-describedby={errors.name ? "name-error" : undefined}
        className="mt-1 block w-full rounded-md border"
      />
      {errors.name && (
        <p id="name-error" role="alert" className="mt-1 text-sm text-red-500">
          {errors.name.message}
        </p>
      )}
    </div>
    
    {/* Select with label */}
    <div>
      <label htmlFor="country" className="block text-sm font-medium">
        Country
      </label>
      <select id="country" className="mt-1 block w-full">
        <option value="">Select a country</option>
        <option value="us">United States</option>
      </select>
    </div>
    
    {/* Checkbox group */}
    <fieldset>
      <legend className="text-sm font-medium">Preferences</legend>
      <div className="mt-2 space-y-2">
        <label className="flex items-center gap-2">
          <input type="checkbox" name="prefs" value="email" />
          <span>Email notifications</span>
        </label>
      </div>
    </fieldset>
    
    <button type="submit">Submit</button>
  </div>
</form>
```

### Error Handling

```tsx
// Focus first error on submit
function handleSubmit(e) {
  const firstError = document.querySelector('[aria-invalid="true"]')
  if (firstError) {
    firstError.focus()
    return
  }
  // proceed with submission
}

// Announce errors
<div role="alert" aria-live="assertive">
  {Object.keys(errors).length > 0 && (
    <p>Please fix {Object.keys(errors).length} error(s) before submitting</p>
  )}
</div>
```

## Images

### Alt Text Guidelines

```tsx
// Informative - describe the content
<img src="chart.png" alt="Bar chart showing Q3 sales increased 25% over Q2" />

// Decorative - empty alt
<img src="divider.png" alt="" />

// Functional (in links/buttons) - describe the action
<a href="/home">
  <img src="logo.png" alt="Go to homepage" />
</a>

// Complex images - use figure
<figure>
  <img src="flowchart.png" alt="User registration process flowchart" />
  <figcaption>
    The registration process: 1. Enter email, 2. Verify email, 3. Set password
  </figcaption>
</figure>
```

## Color & Contrast

### Contrast Ratios

| Type | Minimum | Enhanced |
|------|---------|----------|
| Normal text | 4.5:1 | 7:1 |
| Large text (18px+ or 14px bold) | 3:1 | 4.5:1 |
| UI components | 3:1 | 3:1 |

### Don't Rely on Color Alone

```tsx
// ❌ Wrong - color only
<span className="text-red-500">Error</span>
<span className="text-green-500">Success</span>

// ✅ Correct - color + icon/text
<span className="text-red-500 flex items-center gap-1">
  <XCircle className="h-4 w-4" />
  Error: Invalid input
</span>
<span className="text-green-500 flex items-center gap-1">
  <CheckCircle className="h-4 w-4" />
  Success
</span>
```

## Screen Reader Utilities

### Tailwind Classes

```tsx
// Visually hidden but accessible
<span className="sr-only">Open menu</span>

// Visible only on focus (skip links)
<a className="sr-only focus:not-sr-only">Skip to content</a>
```

### Custom Implementation

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.not-sr-only {
  position: static;
  width: auto;
  height: auto;
  padding: 0;
  margin: 0;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

## Testing

### Manual Testing

1. **Keyboard only**: Tab through entire page, ensure all interactive elements reachable
2. **Screen reader**: Test with VoiceOver (Mac), NVDA (Windows), or ChromeVox
3. **Zoom**: Test at 200% zoom
4. **Color**: Use grayscale filter to check color reliance
5. **Motion**: Test with `prefers-reduced-motion`

### Automated Testing

```bash
# axe-core
npm install @axe-core/react

# eslint-plugin-jsx-a11y
npm install eslint-plugin-jsx-a11y
```

```tsx
// React axe (development only)
if (process.env.NODE_ENV === 'development') {
  import('@axe-core/react').then(({ default: axe }) => {
    axe(React, ReactDOM, 1000)
  })
}
```

### ESLint Config

```javascript
// .eslintrc.js
module.exports = {
  extends: ['plugin:jsx-a11y/recommended'],
  plugins: ['jsx-a11y'],
}
```

## Motion & Animation

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  ::before,
  ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

```tsx
// Tailwind
<div className="animate-bounce motion-reduce:animate-none">

// JavaScript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
```

## Quick Fixes

| Issue | Fix |
|-------|-----|
| Missing alt | Add descriptive alt or `alt=""` for decorative |
| No form labels | Add `<label htmlFor>` or `aria-label` |
| Low contrast | Increase to 4.5:1 minimum |
| No focus visible | Add `focus-visible:ring-2` |
| Missing lang | Add `<html lang="en">` |
| Missing page title | Add `<title>` in `<head>` |
| Click handlers on divs | Use `<button>` or `<a>` instead |
