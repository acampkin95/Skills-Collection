# SVG Manipulation for Brand & Marketing

## SVG Fundamentals for Creatives

### Why SVG for Branding
- Infinite scalability without quality loss
- Tiny file sizes for web performance
- Animatable for motion graphics
- Editable with code or design tools
- Accessible (text remains selectable/searchable)
- Print-ready at any resolution

### SVG Anatomy
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- viewBox defines coordinate system -->
  <!-- width/height can be omitted for responsive scaling -->
  
  <defs>
    <!-- Reusable definitions: gradients, patterns, filters -->
  </defs>
  
  <g id="group-name">
    <!-- Grouped elements for organisation -->
  </g>
  
  <!-- Shape elements -->
  <rect /><circle /><ellipse /><line /><polyline /><polygon /><path />
  
  <!-- Text elements -->
  <text><tspan /></text>
</svg>
```

---

## Core Shape Elements

### Rectangle
```xml
<rect x="10" y="10" width="80" height="40" rx="5" ry="5" />
<!-- rx/ry for rounded corners -->
```

### Circle & Ellipse
```xml
<circle cx="50" cy="50" r="25" />
<ellipse cx="50" cy="50" rx="40" ry="20" />
```

### Path (The Power Element)
```xml
<path d="M10 10 L90 10 L50 90 Z" />
<!-- M=moveto, L=lineto, Z=close path -->
<!-- C=cubic bezier, Q=quadratic bezier, A=arc -->
```

**Path Commands Quick Reference:**
- `M x y` — Move to point
- `L x y` — Line to point
- `H x` — Horizontal line
- `V y` — Vertical line
- `C x1 y1 x2 y2 x y` — Cubic Bézier curve
- `S x2 y2 x y` — Smooth cubic Bézier
- `Q x1 y1 x y` — Quadratic Bézier
- `A rx ry rotation large-arc sweep x y` — Arc
- `Z` — Close path

---

## Styling SVG Elements

### Inline Styling
```xml
<rect fill="#FF6B6B" stroke="#333" stroke-width="2" opacity="0.8" />
```

### CSS Styling
```xml
<style>
  .brand-primary { fill: #FF6B6B; }
  .brand-stroke { stroke: #333; stroke-width: 2; }
</style>
<rect class="brand-primary brand-stroke" />
```

### Key Style Properties
- `fill` — Interior colour
- `stroke` — Outline colour
- `stroke-width` — Outline thickness
- `stroke-linecap` — Line endings (butt, round, square)
- `stroke-linejoin` — Corner style (miter, round, bevel)
- `stroke-dasharray` — Dashed lines
- `opacity` / `fill-opacity` / `stroke-opacity`

---

## Gradients & Patterns

### Linear Gradient
```xml
<defs>
  <linearGradient id="brand-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#FF6B6B" />
    <stop offset="100%" stop-color="#4ECDC4" />
  </linearGradient>
</defs>
<rect fill="url(#brand-gradient)" />
```

### Radial Gradient
```xml
<radialGradient id="glow" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="#FFF" stop-opacity="1" />
  <stop offset="100%" stop-color="#FFF" stop-opacity="0" />
</radialGradient>
```

### Pattern
```xml
<pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
  <circle cx="10" cy="10" r="3" fill="#333" />
</pattern>
<rect fill="url(#dots)" />
```

---

## SVG for Logo Systems

### Logo Structure Best Practices
```xml
<svg viewBox="0 0 200 60" role="img" aria-label="Brand Name">
  <title>Brand Name Logo</title>
  <g id="logo-mark">
    <!-- Icon/symbol elements -->
  </g>
  <g id="logo-wordmark">
    <!-- Text/wordmark elements -->
  </g>
</svg>
```

### Responsive Logo Variants
```xml
<!-- Full logo for large screens -->
<symbol id="logo-full">...</symbol>

<!-- Compact logo for medium screens -->
<symbol id="logo-compact">...</symbol>

<!-- Icon only for small screens -->
<symbol id="logo-icon">...</symbol>

<!-- Use with: -->
<use href="#logo-full" />
```

### Colour Variants via CSS
```css
.logo-light { --logo-primary: #FFFFFF; --logo-secondary: #CCCCCC; }
.logo-dark { --logo-primary: #1A1A1A; --logo-secondary: #333333; }
```
```xml
<path fill="var(--logo-primary, #1A1A1A)" />
```

---

## SVG Animation for Brand Motion

### CSS Animation
```xml
<style>
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }
  .animated { animation: pulse 2s ease-in-out infinite; }
</style>
```

### SMIL Animation (Native SVG)
```xml
<circle r="10">
  <animate attributeName="r" values="10;15;10" dur="1s" repeatCount="indefinite" />
</circle>
```

### Line Drawing Effect
```xml
<path stroke-dasharray="1000" stroke-dashoffset="1000">
  <animate attributeName="stroke-dashoffset" to="0" dur="2s" fill="freeze" />
</path>
```

---

## SVG Optimisation

### Optimisation Checklist
- Remove editor metadata (Illustrator, Sketch cruft)
- Simplify paths (reduce decimal precision)
- Remove hidden/unused elements
- Merge similar paths where possible
- Use symbols for repeated elements
- Compress with SVGO or similar tools

### SVGO Configuration (Common)
```json
{
  "plugins": [
    "removeDoctype",
    "removeXMLProcInst",
    "removeComments",
    "removeMetadata",
    "removeEditorsNSData",
    "cleanupAttrs",
    "convertColors",
    "convertPathData",
    "mergePaths"
  ]
}
```

### File Size Targets
- Simple icons: < 1KB
- Logo marks: 1-3KB
- Complex illustrations: 5-20KB
- Detailed graphics: 20-50KB (consider alternatives)

---

## SVG Accessibility

### Essential Accessibility
```xml
<svg role="img" aria-labelledby="title desc">
  <title id="title">Logo Name</title>
  <desc id="desc">A brief description of the image</desc>
</svg>
```

### Decorative SVG (Hide from Screen Readers)
```xml
<svg aria-hidden="true" focusable="false">
```

### Interactive SVG
```xml
<g role="button" tabindex="0" aria-label="Click to expand">
```

---

## Export Settings by Use Case

### Web (Inline)
- Optimised, minified
- CSS classes for theming
- No width/height (responsive)

### Web (Image)
- Self-contained styles
- Fixed dimensions
- Base64 encode small icons

### Print
- CMYK colour values
- Outlined text (if fonts unavailable)
- High precision paths

### Social/Sharing
- Export as PNG at 2x resolution
- Include safe area padding
