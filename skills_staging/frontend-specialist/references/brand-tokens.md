# Brand Tokens Implementation

## Token Architecture

### Three-Layer System

```
┌─────────────────────────────────────────────────┐
│  Component Tokens (most specific)               │
│  --btn-primary-bg, --card-radius                │
├─────────────────────────────────────────────────┤
│  Semantic Tokens (purpose-based)                │
│  --color-primary, --spacing-content             │
├─────────────────────────────────────────────────┤
│  Primitive Tokens (raw values)                  │
│  --blue-500, --space-4, --radius-md             │
└─────────────────────────────────────────────────┘
```

## Complete Token Set

### Primitives

```css
:root {
  /* Colors */
  --blue-50: #eff6ff;
  --blue-100: #dbeafe;
  --blue-500: #3b82f6;
  --blue-600: #2563eb;
  --blue-900: #1e3a8a;
  
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-500: #6b7280;
  --gray-700: #374151;
  --gray-900: #111827;
  
  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  
  /* Border Radius */
  --radius-xs: 0.125rem;
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
  --radius-full: 9999px;
  
  /* Typography */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-4xl: 2.25rem;
  
  /* Shadows */
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  
  /* Transitions */
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Semantic Tokens

```css
:root {
  /* Background */
  --color-background: var(--gray-50);
  --color-background-subtle: var(--gray-100);
  
  /* Foreground */
  --color-foreground: var(--gray-900);
  --color-foreground-muted: var(--gray-500);
  
  /* Primary */
  --color-primary: var(--blue-500);
  --color-primary-hover: var(--blue-600);
  --color-primary-foreground: white;
  
  /* Secondary */
  --color-secondary: var(--gray-100);
  --color-secondary-hover: var(--gray-200);
  --color-secondary-foreground: var(--gray-900);
  
  /* Border */
  --color-border: var(--gray-200);
  
  /* Ring (focus) */
  --color-ring: var(--blue-500);
  
  /* Semantic spacing */
  --spacing-page: var(--space-6);
  --spacing-section: var(--space-12);
  --spacing-content: var(--space-4);
}

/* Dark mode */
.dark {
  --color-background: var(--gray-900);
  --color-background-subtle: var(--gray-800);
  --color-foreground: var(--gray-50);
  --color-foreground-muted: var(--gray-400);
  --color-primary: var(--blue-400);
  --color-border: var(--gray-700);
}
```

### Component Tokens

```css
:root {
  /* Button */
  --btn-height-sm: 2rem;
  --btn-height-md: 2.5rem;
  --btn-height-lg: 3rem;
  --btn-radius: var(--radius-md);
  --btn-font-size: var(--text-sm);
  
  /* Input */
  --input-height: 2.5rem;
  --input-radius: var(--radius-md);
  --input-border: 1px solid var(--color-border);
  
  /* Card */
  --card-padding: var(--space-6);
  --card-radius: var(--radius-lg);
  
  /* Avatar */
  --avatar-size-sm: 2rem;
  --avatar-size-md: 2.5rem;
  --avatar-size-lg: 3rem;
}
```

## Tailwind Integration

### Tailwind v4

```css
@import "tailwindcss";

@theme {
  /* Map CSS variables to Tailwind */
  --color-background: var(--color-background);
  --color-foreground: var(--color-foreground);
  --color-primary: var(--color-primary);
  --color-secondary: var(--color-secondary);
  --color-border: var(--color-border);
  --color-ring: var(--color-ring);
}

@custom-variant dark (&:where(.dark, .dark *));
```

### Tailwind v3

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        background: 'var(--color-background)',
        foreground: 'var(--color-foreground)',
        primary: {
          DEFAULT: 'var(--color-primary)',
          foreground: 'var(--color-primary-foreground)',
        },
        secondary: {
          DEFAULT: 'var(--color-secondary)',
          foreground: 'var(--color-secondary-foreground)',
        },
        border: 'var(--color-border)',
        ring: 'var(--color-ring)',
      },
      borderRadius: {
        button: 'var(--btn-radius)',
        card: 'var(--card-radius)',
      },
    },
  },
}
```

## Typography System

```css
:root {
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-display: 'Cal Sans', 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

/* Fluid typography */
.text-display-xl {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 5vw, 4.5rem);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.text-heading-lg {
  font-family: var(--font-sans);
  font-size: 1.875rem;
  line-height: 1.25;
  font-weight: 600;
}

.text-body {
  font-family: var(--font-sans);
  font-size: 1rem;
  line-height: 1.5;
}
```

## Animation Tokens

```css
:root {
  --duration-instant: 0ms;
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  
  --ease-linear: linear;
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
  
  --transition-colors: color var(--duration-normal) var(--ease-in-out),
                       background-color var(--duration-normal) var(--ease-in-out);
  --transition-transform: transform var(--duration-normal) var(--ease-out);
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in var(--duration-normal) var(--ease-out);
}

.animate-slide-up {
  animation: slide-up var(--duration-normal) var(--ease-out);
}
```

## Usage Example

```tsx
// Button using tokens
export function Button({ variant = 'primary', size = 'md', ...props }) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center font-medium transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        
        // Size using tokens
        size === 'sm' && 'h-8 px-3 text-sm rounded-button',
        size === 'md' && 'h-10 px-4 text-sm rounded-button',
        size === 'lg' && 'h-12 px-6 text-base rounded-button',
        
        // Variants
        variant === 'primary' && 'bg-primary text-primary-foreground hover:bg-primary/90',
        variant === 'secondary' && 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
      )}
      {...props}
    />
  )
}

// Page using tokens
export default function Page() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-page py-section">
        <h1 className="text-display-xl text-foreground">Welcome</h1>
        <p className="text-body text-foreground-muted mt-content">
          Description here
        </p>
      </div>
    </div>
  )
}
```

## Brand Theming

```css
/* Default brand */
:root {
  --brand-primary: #3b82f6;
  --brand-secondary: #8b5cf6;
  --brand-accent: #f59e0b;
}

/* Alternative theme */
[data-theme="warm"] {
  --brand-primary: #f97316;
  --brand-secondary: #ec4899;
  --brand-accent: #eab308;
}

/* Dark variant */
.dark {
  --brand-primary: #60a5fa;
  --brand-secondary: #a78bfa;
  --brand-accent: #fbbf24;
}
```

```tsx
// Theme switcher
<html data-theme="warm" className="dark">
```
