# Typography Mastery for Brand & Marketing

## Typography as Brand Voice

Typography speaks before words are read. The shape of letters communicates personality, era, values, and positioning before conscious comprehension kicks in.

### Type Classification & Personality

**Serif (Traditional Authority)**
- Old Style (Garamond, Caslon): Heritage, literature, timeless elegance
- Transitional (Baskerville, Times): Balanced, journalistic, trustworthy
- Modern/Didone (Bodoni, Didot): Fashion, luxury, high contrast drama
- Slab Serif (Rockwell, Clarendon): Bold, mechanical, confident

**Sans Serif (Modern Clarity)**
- Grotesque (Akzidenz, Franklin): Industrial, no-nonsense, utilitarian
- Neo-Grotesque (Helvetica, Arial): Neutral, corporate, universal
- Humanist (Gill Sans, Frutiger): Warm, approachable, readable
- Geometric (Futura, Avant Garde): Modern, progressive, architectural

**Display & Decorative**
- Script: Elegance, personal touch, celebration
- Handwritten: Authentic, human, craft
- Decorative: Specific era/mood, use sparingly
- Variable: Modern flexibility, animation-ready

---

## Type Pairing Strategies

### Contrast Principles
Successful pairings create contrast without conflict:
- **Weight contrast:** Light + Bold
- **Style contrast:** Serif + Sans
- **Proportion contrast:** Condensed + Extended
- **Era contrast:** Modern + Classical

### Pairing Frameworks

**Superfamily Approach**
Use typefaces designed to work together:
- Roboto + Roboto Slab
- Source Sans + Source Serif
- PT Sans + PT Serif

**Historical Harmony**
Pair typefaces from similar eras:
- Futura + Bodoni (1920s geometric + classical elegance)
- Gill Sans + Caslon (British heritage)

**Personality Match**
Similar character, different classification:
- Proxima Nova + Freight Text (both humanist DNA)
- Montserrat + Lora (geometric meets transitional)

### Common Pairings That Work

**Modern Professional**
- Inter + Source Serif Pro
- Instrument Sans + Instrument Serif
- Söhne + Tiempos

**Creative Contemporary**
- Clash Display + Satoshi
- Space Grotesk + Fraunces
- Cabinet Grotesk + Recoleta

**Approachable Warmth**
- Nunito + Merriweather
- Poppins + Lora
- Manrope + Literata

---

## Type Hierarchy System

### Scale Definition

**Modular Scale Approach**
Choose a ratio, apply consistently:
- 1.067 — Minor second (subtle)
- 1.200 — Minor third (common)
- 1.250 — Major third (versatile)
- 1.333 — Perfect fourth (dramatic)
- 1.618 — Golden ratio (classic)

**Example Scale (1.25 ratio, 16px base):**
```
Caption:    13px (0.8125rem)
Body:       16px (1rem)
Lead:       20px (1.25rem)
H4:         25px (1.5625rem)
H3:         31px (1.9375rem)
H2:         39px (2.4375rem)
H1:         49px (3.0625rem)
Display:    61px (3.8125rem)
```

### Line Height Guidelines

- **Display/Headlines:** 1.0–1.2 (tight)
- **Subheads:** 1.2–1.3
- **Body copy:** 1.4–1.6 (optimal reading)
- **Small text:** 1.5–1.7 (generous)

### Letter Spacing (Tracking)

- **All caps:** +0.05em to +0.1em (always add)
- **Display large:** -0.01em to -0.02em (optically tighten)
- **Body text:** 0 (default)
- **Small caps:** +0.05em

---

## Optical Adjustments

### Visual Alignment Principles
Mathematical alignment ≠ Visual alignment

**Cap height alignment:** Align to cap height, not ascender
**Baseline alignment:** Text aligns on baseline across elements
**Optical margin alignment:** Punctuation and curved letters hang slightly outside margins

### Weight Compensation
- Lighter weights need more spacing
- Heavier weights can be tighter
- Condensed faces need careful spacing
- Extended faces tolerate tighter tracking

### Size-Specific Adjustments
Same font at different sizes needs different treatment:
- Large sizes: Tighter tracking, can handle finer weights
- Small sizes: Looser tracking, heavier weights for legibility

---

## Type for Digital Screens

### Web Font Performance

**Loading Strategy:**
```css
/* Preload critical fonts */
<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>

/* Font-display options */
font-display: swap;    /* Show fallback immediately, swap when loaded */
font-display: optional; /* Only use if cached, no layout shift */
```

**Subset for Speed:**
- Latin only if no other languages needed
- Remove unused glyphs
- Variable fonts for multiple weights

### Variable Fonts
Single file containing entire weight/width spectrum:
```css
font-variation-settings: 
  'wght' 450,  /* Weight axis */
  'wdth' 100,  /* Width axis */
  'slnt' -10;  /* Slant axis */
```

**Benefits:**
- Smaller combined file size
- Smooth weight transitions
- Animation possibilities
- Responsive typography

### Responsive Type

**Fluid Typography:**
```css
/* Scales between 16px at 320px viewport to 24px at 1200px */
font-size: clamp(1rem, 0.5rem + 2vw, 1.5rem);
```

**Breakpoint Adjustments:**
- Mobile: Larger body text (17-18px), tighter line height
- Tablet: Standard sizing, comfortable line length
- Desktop: Can handle smaller body, longer lines if needed

---

## Type for Print

### Print-Specific Considerations

**Body Text Sizing:**
- Books/long-form: 10-12pt
- Brochures: 9-11pt
- Posters (distance viewing): Scale to viewing distance

**Line Length (Measure):**
- Optimal: 45-75 characters per line
- Books: 60-70 characters
- Narrow columns: 40-50 characters

**Paper and Ink:**
- Coated paper: Can handle finer details, lighter weights
- Uncoated paper: Ink spreads, use slightly heavier weights
- Small text on colour: Increase weight

### Proofing Checklist
- [ ] Widow and orphan control
- [ ] Proper hyphenation
- [ ] Consistent spacing
- [ ] Appropriate paragraph spacing
- [ ] Correct optical alignment

---

## Typography and Accessibility

### Readability Requirements

**Font Size:**
- Minimum body: 16px web, 10pt print
- Line height: At least 1.5 for body text
- Paragraph spacing: At least 1.5x font size

**Contrast:**
- Normal text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum

**Font Choice:**
- Distinct letterforms (a, o, 0, O, l, 1, I)
- Adequate x-height
- Open counters
- Avoid decorative fonts for body text

### Dyslexia Considerations
- Sans serif often preferred
- Generous spacing
- Left-aligned (not justified)
- Short line lengths
- OpenDyslexic font for specific applications

---

## Type Licensing

### License Types

**Desktop:** For design software (print, static graphics)
**Web:** For @font-face (often per-pageview tiers)
**App:** For embedding in mobile/desktop applications
**Server:** For dynamic generation (PDFs, images)
**ePub:** For electronic publications
**Broadcast:** For video/TV

### Open Source Options
Quality free fonts with permissive licenses:
- Google Fonts (SIL Open Font License)
- Font Squirrel (verified licenses)
- Adobe Fonts (with Creative Cloud)
- Variable fonts: Recursive, Inter, Fraunces, Manrope

### Commercial Foundries
Premium options when budget allows:
- Klim Type (New Zealand)
- Grilli Type (Switzerland)
- Commercial Type
- Hoefler & Co
- Colophon Foundry
