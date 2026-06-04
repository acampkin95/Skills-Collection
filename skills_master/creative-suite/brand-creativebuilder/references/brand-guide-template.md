# Brand Guide Template Reference

## Table of Contents
1. [HTML Structure](#html-structure)
2. [Pantone Swatch Layout](#pantone-swatches)
3. [Required Sections](#required-sections)
4. [Interactive Components](#interactive-components)
5. [Tailwind v4 Config Template](#tailwind-config)
6. [Component Migration Guide](#migration)

---

## HTML Structure

Single self-contained HTML file. All CSS inline, fonts from Google Fonts CDN. No external JS dependencies.

### Page Skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[BRAND] — Brand Identity Guide v1.0</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>/* All CSS inline — design tokens + components */</style>
</head>
<body>
  <nav class="nav"><!-- 260px fixed left sidebar --></nav>
  <main class="main"><!-- Content sections --></main>
  <div id="toast" class="toast">Copied</div>
  <script>/* Copy handlers + scroll tracking */</script>
</body>
</html>
```

---

## Pantone Swatch Layout

### Modern Swatch Card Design

Each swatch is a tall card with a large fill area and a structured info panel below. The layout uses a **bento-style grid** (variable column widths) not a uniform 4-column grid.

### CSS for Pantone Swatches

```css
.pantone-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--sp-4);
  margin: var(--sp-6) 0;
}

.pantone-swatch {
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.pantone-swatch:hover {
  border-color: var(--border-hover);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}

.pantone-fill {
  height: 140px;
  display: flex;
  align-items: flex-end;
  padding: var(--sp-3);
  position: relative;
}

.pantone-fill .contrast-sample {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  opacity: 0.8;
}

.pantone-info {
  padding: var(--sp-4);
  background: var(--bg-raised);
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.pantone-name {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.9375rem;
  color: var(--text);
}

.pantone-ref {
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  color: var(--sage-400); /* or brand accent */
  letter-spacing: 0.02em;
}

.pantone-specs {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 2px var(--sp-3);
  font-size: 0.75rem;
}

.pantone-spec-label {
  font-family: var(--font-mono);
  font-size: 0.5625rem;
  color: var(--text-subtle);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding-top: 2px;
}

.pantone-spec-value {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
}

.pantone-usage {
  font-family: var(--font-body);
  font-size: 0.75rem;
  color: var(--text-subtle);
  font-style: italic;
  margin-top: var(--sp-1);
  line-height: 1.4;
}
```

### HTML for a Single Pantone Swatch

```html
<div class="pantone-swatch" onclick="copyHex('#7A9E81')">
  <div class="pantone-fill" style="background: #7A9E81;">
    <span class="contrast-sample" style="color: #0E100F;">Aa</span>
  </div>
  <div class="pantone-info">
    <div class="pantone-name">Brand Primary</div>
    <div class="pantone-ref">PANTONE 16-6116 TPX · Shale Green</div>
    <div class="pantone-specs">
      <span class="pantone-spec-label">CMYK</span>
      <span class="pantone-spec-value">45 / 12 / 38 / 8</span>
      <span class="pantone-spec-label">HEX</span>
      <span class="pantone-spec-value">#7A9E81</span>
      <span class="pantone-spec-label">RGB</span>
      <span class="pantone-spec-value">122, 158, 129</span>
    </div>
    <div class="pantone-usage">Primary CTAs, active states, brand accent</div>
  </div>
</div>
```

### Swatch Grid with Featured Primary

For emphasis, make the primary colour swatch span 2 columns:

```css
.pantone-swatch.featured {
  grid-column: span 2;
}

.pantone-swatch.featured .pantone-fill {
  height: 200px;
}
```

### 11-Step Scale Strip

The interactive scale strip sits below the Pantone swatches. Each step is clickable:

```html
<div class="scale-strip">
  <div class="scale-step" style="background:#HEX;color:#CONTRAST"
       onclick="copyHex('#HEX')">
    <span class="tip">#HEX</span>
    [STEP_NUMBER]
  </div>
  <!-- Repeat for 50 through 950 -->
</div>
```

---

## Required Sections (13)

1. **Brand Identity** — name, tagline, category, aesthetic (info-grid)
2. **Brand Story** — etymology, audience, personality traits
3. **Positioning** — statement in type-sample box, voice Do/Don't
4. **Logo System** — SVG inline: dark/light/mark/wordmark + rules
5. **Colour Palette** — Pantone swatches (modern card layout), scale strips, semantic colours
6. **Typography** — live type samples, type scale, font specs
7. **Visual Language** — blueprint grid, glass surfaces, stroke style, motion principles
8. **Tailwind v4 Config** — complete @theme block, copyable
9. **Component Patterns** — find-and-replace migration table (if rebranding)
10. **Pipeline Stages** — status colour definitions with dot indicators
11. **Iconography** — approved icon tables, usage rules, import patterns
12. **Animation System** — live demos, Framer Motion patterns, keyframe catalogue, reduced motion
13. **Accessibility** — contrast ratio table, keyboard rules, ARIA patterns, checklist

---

## Interactive Components

### Copy Functions

```javascript
function copyHex(hex) {
  navigator.clipboard.writeText(hex).then(() => {
    const t = document.getElementById('toast');
    t.textContent = 'Copied ' + hex;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 1400);
  });
}

function copyBlock(btn) {
  const pre = btn.closest('pre');
  const code = pre.querySelector('code');
  navigator.clipboard.writeText(code.textContent).then(() => {
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 1400);
  });
}
```

### Scroll-Tracking Nav

```javascript
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navLinks.forEach(l => l.classList.remove('active'));
      const a = document.querySelector('.nav-link[href="#' + entry.target.id + '"]');
      if (a) a.classList.add('active');
    }
  });
}, { rootMargin: '-20% 0px -70% 0px' });
sections.forEach(s => observer.observe(s));
```

### Toast Notification

Fixed bottom-right, transform slide-up on `.show`, auto-hide 1.4s.

### Live Animation Demos

Render keyframe animations inline in small preview cards:

```html
<div class="anim-demo">
  <div class="anim-preview">
    <div class="demo-dot pulse"></div>
  </div>
  <div class="anim-meta">
    <div class="anim-name">Stage Pulse</div>
    <div class="anim-detail">2s cubic-bezier · opacity 1→0.5</div>
  </div>
</div>
```

### Code Blocks with Syntax Highlighting

Use CSS classes for lightweight syntax colouring:
- `.c` — comments (text-subtle)
- `.k` — keys/properties (brand accent)
- `.s` — strings/values (warm amber)

```html
<pre><code><span class="c">/* comment */</span>
<span class="k">--property</span>: <span class="s">value</span>;
</code><button class="copy-code" onclick="copyBlock(this)">Copy</button></pre>
```

---

## Tailwind v4 Config Template

```css
@import "tailwindcss";
@import "@fontsource-variable/[display-font]";
@import "@fontsource/[body-font]";

@theme {
  --color-background: [near-black with hue tint];
  --color-foreground: [warm off-white];
  --color-card: [primary at 4-6% opacity];
  --color-card-foreground: [foreground];
  --color-popover: [dark surface at 95% opacity];
  --color-popover-foreground: [foreground];

  --color-primary: [primary-400 — Pantone-derived HEX];
  --color-primary-foreground: [background];
  --color-secondary: [primary at 8% opacity];
  --color-secondary-foreground: [foreground];
  --color-muted: [primary at 6% opacity];
  --color-muted-foreground: [neutral-400];
  --color-accent: [primary at 12% opacity];
  --color-accent-foreground: [primary-400];
  --color-destructive: [error — Pantone-derived HEX];
  --color-destructive-foreground: #FFFFFF;

  --color-border: [primary at 12% opacity];
  --color-input: [primary at 12% opacity];
  --color-ring: [primary-400];

  --color-brand: [primary-400];
  --color-brand-dark: [primary-500];
  --color-brand-light: [primary-300];

  /* Full 11-step primary scale */
  --color-[name]-50 through --color-[name]-950;

  /* Full 11-step neutral scale */
  --color-stone-50 through --color-stone-950;

  /* Pipeline stages */
  --color-stage-pending: [neutral-600];
  --color-stage-running: [primary-400];
  --color-stage-completed: [primary-500];
  --color-stage-failed: [error];

  /* Glass */
  --color-glass: [primary at 4%];
  --color-glass-border: [primary at 10%];
  --color-glass-border-hover: [primary at 22%];

  /* Typography */
  --font-sans: "[Display]", system-ui, sans-serif;
  --font-body: "[Body]", system-ui, sans-serif;
  --font-mono: var(--font-geist-mono), "[Mono]", ui-monospace, monospace;

  /* Radii + Shadows */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --shadow-glass: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 [primary at 5%];
}
```

---

## Component Migration Guide

When rebranding an existing app:

### Migration Table Structure

```
OLD_VALUE    → NEW_VALUE    // COMMENT
#38bdf8      → #7A9E81     // brand accent (from Pantone 16-6116)
sky-400      → sage-400    // Tailwind class
```

### Ordered Steps

1. **Font swap**: `npm remove [old]` + `npm install [new]`
2. **Replace @theme block** in globals.css
3. **Global colour find-and-replace** across all components
4. **Update layout.tsx**: title, description, body classes
5. **Update Navbar**: wordmark, icon container, active indicator
6. **Update AnimatedBackground**: wireframe mesh colours
7. **Update ::selection**: highlight colour
8. **Update keyframes**: gradient colours in shimmer/glow
9. **Verify contrast**: test all text/background pairs against WCAG AA
10. **Test reduced motion**: verify all animations respect prefers-reduced-motion
