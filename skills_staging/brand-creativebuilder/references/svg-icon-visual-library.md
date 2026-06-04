# Visual SVG Icon Library & Interactive Examples

Visual reference for the Remix Icon set, inline SVG examples for brand guide embedding, and production-ready interactive component snippets.

## Table of Contents
1. [SVG Icon Visual Reference](#icon-reference)
2. [Brand Guide Interactive Examples](#interactive-examples)
3. [Component Snippet Library](#snippets)
4. [Logomark Construction Guide](#logomark)

---

## SVG Icon Visual Reference

### How to Embed Icons in the Brand Guide HTML

The brand guide is a self-contained HTML file — it cannot import react-icons. Instead, embed Remix Icon SVGs inline. All icons below use the standard Remix Icon viewBox and stroke conventions.

### Navigation & Chrome Icons

```html
<!-- RiHomeLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
  <path d="M20 20a1 1 0 01-1 1H5a1 1 0 01-1-1v-9H1l10.327-9.388a1 1 0 011.346 0L23 11h-3v9z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>

<!-- RiAddLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
</svg>

<!-- RiSettings4Line -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <circle cx="12" cy="12" r="3.5"/>
  <path d="M12 1v3M12 20v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M1 12h3M20 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/>
</svg>

<!-- RiCloseLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <line x1="6" y1="6" x2="18" y2="18"/><line x1="6" y1="18" x2="18" y2="6"/>
</svg>

<!-- RiMenuLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
</svg>

<!-- RiQuestionLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><circle cx="12" cy="17" r="0.5" fill="currentColor"/>
</svg>
```

### Pipeline & Action Icons

```html
<!-- RiUploadCloud2Line -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M16 16l-4-4-4 4M12 12v9"/>
  <path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/>
</svg>

<!-- RiPlayCircleLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/><polygon points="10,8 16,12 10,16"/>
</svg>

<!-- RiStopCircleLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <circle cx="12" cy="12" r="10"/><rect x="9" y="9" width="6" height="6" rx="0.5"/>
</svg>

<!-- RiDeleteBinLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <path d="M3 6h18M8 6V4a1 1 0 011-1h6a1 1 0 011 1v2"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6"/>
  <line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>
</svg>

<!-- RiDownloadLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7,10 12,15 17,10"/><line x1="12" y1="15" x2="12" y2="3"/>
</svg>

<!-- RiRefreshLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23,4 23,10 17,10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/>
</svg>

<!-- RiCheckLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="5,12 10,17 19,8"/>
</svg>

<!-- RiEyeLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
</svg>
```

### Status & Feedback Icons

```html
<!-- RiErrorWarningLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
  <line x1="12" y1="9" x2="12" y2="13"/><circle cx="12" cy="17" r="0.5" fill="currentColor"/>
</svg>

<!-- RiInformationLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><circle cx="12" cy="8" r="0.5" fill="currentColor"/>
</svg>

<!-- RiTimeLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/>
</svg>

<!-- RiFileCopyLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
</svg>
```

### Media & Content Icons

```html
<!-- RiImageLine -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21,15 16,10 5,21"/>
</svg>

<!-- RiBox3Line -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
  <polyline points="3.27,6.96 12,12.01 20.73,6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
</svg>

<!-- RiContrastDropLine (theme toggle) -->
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z"/>
</svg>
```

### Icon Display in Brand Guide HTML

Embed icons in a visual grid within the brand guide:

```html
<div class="icon-visual-grid">
  <div class="icon-visual-item">
    <div class="icon-visual-preview">
      <!-- Inline SVG here -->
    </div>
    <div class="icon-visual-name">RiHomeLine</div>
    <div class="icon-visual-usage">Dashboard nav</div>
  </div>
  <!-- Repeat for each icon -->
</div>
```

```css
.icon-visual-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: var(--sp-3);
  margin: var(--sp-4) 0;
}
.icon-visual-item {
  text-align: center;
  padding: var(--sp-3);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--bg-raised);
  transition: all 0.2s;
}
.icon-visual-item:hover {
  border-color: var(--border-hover);
  transform: translateY(-2px);
}
.icon-visual-preview {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--sage-400); /* brand accent */
  margin-bottom: var(--sp-2);
}
.icon-visual-name {
  font-family: var(--font-mono);
  font-size: 0.5625rem;
  color: var(--text-muted);
}
.icon-visual-usage {
  font-family: var(--font-mono);
  font-size: 0.5rem;
  color: var(--text-subtle);
}
```

---

## Brand Guide Interactive Examples

### Interactive Pantone Swatch with Full Spec

```html
<div class="pantone-swatch" onclick="copyHex('#7A9E81')"
     role="button" tabindex="0" aria-label="Copy hex value #7A9E81">
  <div class="pantone-fill" style="background: #7A9E81;">
    <span class="contrast-sample" style="color: #0E100F;">Aa</span>
  </div>
  <div class="pantone-info">
    <div class="pantone-name">Brand Primary</div>
    <div class="pantone-ref">PANTONE 16-6116 TPX · Shale Green</div>
    <div class="pantone-specs">
      <span class="pantone-spec-label">Pantone</span>
      <span class="pantone-spec-value">16-6116 TPX</span>
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

### Interactive Pipeline Stage Demo

A live, animated pipeline progress bar embedded in the brand guide:

```html
<div class="pipeline-demo" role="img" aria-label="Pipeline stage demonstration">
  <div class="pipeline-stage completed">
    <div class="pipeline-dot"></div>
    <div class="pipeline-label">UPLOAD</div>
  </div>
  <div class="pipeline-line completed"></div>
  <div class="pipeline-stage completed">
    <div class="pipeline-dot"></div>
    <div class="pipeline-label">VALIDATE</div>
  </div>
  <div class="pipeline-line completed"></div>
  <div class="pipeline-stage running">
    <div class="pipeline-dot"></div>
    <div class="pipeline-label">CONFIGURE</div>
  </div>
  <div class="pipeline-line pending"></div>
  <div class="pipeline-stage pending">
    <div class="pipeline-dot"></div>
    <div class="pipeline-label">REVIEW</div>
  </div>
  <div class="pipeline-line pending"></div>
  <div class="pipeline-stage pending">
    <div class="pipeline-dot"></div>
    <div class="pipeline-label">RUN</div>
  </div>
</div>
```

```css
.pipeline-demo {
  display: flex;
  align-items: flex-start;
  gap: 0;
  padding: var(--sp-6) var(--sp-4);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin: var(--sp-4) 0;
}

.pipeline-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--sp-2);
}

.pipeline-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid var(--border);
  background: transparent;
  transition: all 0.3s;
}

.pipeline-stage.completed .pipeline-dot {
  background: var(--sage-500);
  border-color: var(--sage-500);
}

.pipeline-stage.running .pipeline-dot {
  background: var(--sage-400);
  border-color: var(--sage-400);
  box-shadow: 0 0 10px rgba(122, 158, 129, 0.5);
  animation: stage-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.pipeline-stage.pending .pipeline-dot {
  border-color: var(--stone-600);
}

.pipeline-line {
  flex: 1;
  height: 2px;
  min-width: 40px;
  margin-top: 6px;
  background: var(--border);
}

.pipeline-line.completed { background: var(--sage-500); }

.pipeline-label {
  font-family: var(--font-mono);
  font-size: 0.5625rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-subtle);
}

.pipeline-stage.running .pipeline-label { color: var(--sage-400); }
.pipeline-stage.completed .pipeline-label { color: var(--text-muted); }
```

### Interactive Glass Card Example

```html
<div class="glass-card-demo">
  <div class="glass-demo-card" tabindex="0">
    <div class="glass-demo-header">
      <span class="glass-demo-title">Mould_v3.2_final</span>
      <span class="glass-demo-badge">COMPLETED</span>
    </div>
    <div class="glass-demo-meta">
      <span>6 images</span>
      <span>·</span>
      <span>14.2 MB</span>
      <span>·</span>
      <span>2m ago</span>
    </div>
    <div class="glass-demo-pipeline">
      <!-- Inline pipeline dots -->
    </div>
  </div>
</div>
```

```css
.glass-demo-card {
  background: rgba(94, 131, 101, 0.04);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(94, 131, 101, 0.10);
  border-radius: var(--radius-lg);
  padding: var(--sp-4);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.glass-demo-card:hover {
  border-color: rgba(122, 158, 129, 0.22);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.glass-demo-card:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--sage-400);
}

.glass-demo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--sp-2);
}

.glass-demo-title {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 0.875rem;
}

.glass-demo-badge {
  font-family: var(--font-mono);
  font-size: 0.5625rem;
  letter-spacing: 0.06em;
  color: var(--sage-400);
  background: rgba(94, 131, 101, 0.1);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.glass-demo-meta {
  display: flex;
  gap: var(--sp-2);
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  color: var(--text-subtle);
}
```

### Interactive Typography Scale Demo

```html
<div class="type-scale-interactive">
  <div class="type-scale-demo-row" style="--size: 3rem; --weight: 800; --tracking: -0.03em;">
    <span class="type-meta">5xl · 3rem · Outfit 800</span>
    <span class="type-preview" style="font-family: var(--font-display); font-size: var(--size); font-weight: var(--weight); letter-spacing: var(--tracking);">Pipeline</span>
  </div>
  <!-- Repeat with decreasing sizes -->
</div>
```

### Contrast Checker Demo (Interactive)

```html
<div class="contrast-demo">
  <div class="contrast-pair-demo">
    <div class="contrast-bg" style="background: #0E100F; padding: 16px; border-radius: 8px;">
      <span style="color: #E8E6E3; font-size: 1rem;">Foreground on Background</span>
      <span class="contrast-ratio-badge pass">15.4:1 ✓</span>
    </div>
  </div>
  <div class="contrast-pair-demo">
    <div class="contrast-bg" style="background: #0E100F; padding: 16px; border-radius: 8px;">
      <span style="color: #635D55; font-size: 1rem;">Subtle on Background</span>
      <span class="contrast-ratio-badge fail">3.4:1 ✕</span>
    </div>
  </div>
</div>
```

```css
.contrast-ratio-badge {
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  margin-left: auto;
}
.contrast-ratio-badge.pass {
  color: var(--sage-400);
  background: rgba(94, 131, 101, 0.15);
}
.contrast-ratio-badge.fail {
  color: var(--error);
  background: rgba(196, 90, 74, 0.15);
}
```

---

## Component Snippet Library

### Button Variants (Production-Ready)

```tsx
// Primary CTA
<Button className="bg-sage-500 text-sage-50 hover:bg-sage-600
  focus-visible:ring-2 focus-visible:ring-sage-400
  focus-visible:ring-offset-2 focus-visible:ring-offset-[#0E100F]">
  <RiPlayCircleLine className="h-4 w-4" aria-hidden="true" />
  Run Pipeline
</Button>

// Ghost (nav/toolbar)
<Button variant="ghost" className="text-stone-400 hover:text-stone-50
  hover:bg-sage-400/[0.06]">
  <RiSettings4Line className="h-4 w-4" aria-hidden="true" />
  Settings
</Button>

// Destructive
<Button variant="destructive" className="bg-transparent text-[#C45A4A]
  border border-[#C45A4A]/20 hover:bg-[#C45A4A]/10">
  <RiDeleteBinLine className="h-4 w-4" aria-hidden="true" />
  Delete Job
</Button>
```

### Status Badge Component

```tsx
const statusConfig = {
  completed: { color: 'text-sage-400 bg-sage-400/10', label: 'COMPLETED' },
  running:   { color: 'text-sage-300 bg-sage-300/10 animate-stage-pulse', label: 'RUNNING' },
  failed:    { color: 'text-[#C45A4A] bg-[#C45A4A]/10', label: 'FAILED' },
  pending:   { color: 'text-stone-500 bg-stone-500/10', label: 'PENDING' },
} as const;

function StatusBadge({ status }: { status: keyof typeof statusConfig }) {
  const config = statusConfig[status];
  return (
    <span className={`font-mono text-[0.5625rem] tracking-wider
      px-2 py-0.5 rounded ${config.color}`}
      role="status" aria-label={`Status: ${config.label}`}>
      {config.label}
    </span>
  );
}
```

### Stat Display (Typography-First)

```tsx
function StatRow({ stats }: { stats: Array<{ value: string; label: string; accent?: boolean }> }) {
  return (
    <div className="flex items-baseline gap-8">
      {stats.map((stat, i) => (
        <Fragment key={stat.label}>
          {i > 0 && <div className="w-px h-8 bg-sage-400/10" />}
          <div className="text-center">
            <div className={`font-mono text-[1.75rem] font-semibold tabular-nums
              ${stat.accent ? 'text-sage-400' : 'text-foreground'}`}>
              {stat.value}
            </div>
            <div className="font-mono text-[0.5625rem] uppercase tracking-widest
              text-stone-500 mt-0.5">
              {stat.label}
            </div>
          </div>
        </Fragment>
      ))}
    </div>
  );
}
```

---

## Logomark Construction Guide

### SVG Construction Steps

1. **Start with viewBox**: `viewBox="0 0 48 48"` (standard) or `0 0 32 32` (compact)
2. **Outer container**: `<rect>` with `rx` for rounded corners, stroke only
3. **Core concept elements**: Paths representing the product's function
4. **Flow indicators**: Dashed lines (`stroke-dasharray`) for liquid/data flow
5. **Cavity/target area**: Inner `<rect>` with subtle fill at 6-10% opacity

### SVG Attributes Checklist

```xml
<!-- Every logomark SVG must include: -->
<svg
  viewBox="0 0 48 48"
  fill="none"
  xmlns="http://www.w3.org/2000/svg"
  role="img"
  aria-label="[BRAND] logomark"
>
  <!-- All elements: -->
  <!-- stroke="[COLOUR]" -->
  <!-- stroke-width="2" (primary) or "1.5" (detail) -->
  <!-- stroke-linecap="round" -->
  <!-- stroke-linejoin="round" -->
  <!-- fill="none" (or rgba at max 10% for cavities) -->
</svg>
```

### Dark/Light Colour Swap

```javascript
// In brand guide JS — swap logo colours for theme preview
function setLogoTheme(theme) {
  const logos = document.querySelectorAll('.logo-preview svg');
  const colour = theme === 'dark' ? '#7A9E81' : '#3B533F';
  logos.forEach(svg => {
    svg.querySelectorAll('[stroke]').forEach(el => {
      el.setAttribute('stroke', colour);
    });
  });
}
```
