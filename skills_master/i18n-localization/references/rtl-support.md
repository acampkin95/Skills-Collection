# RTL (Right-to-Left) Support

## Setting Document Direction

### Dynamic Direction in Layout

```tsx
// app/[locale]/layout.tsx
import { routing } from '@/i18n/routing';

const rtlLocales = new Set(['ar', 'he', 'fa', 'ur']);

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const dir = rtlLocales.has(locale) ? 'rtl' : 'ltr';

  return (
    <html lang={locale} dir={dir}>
      <body>{children}</body>
    </html>
  );
}
```

### Direction-Aware Hook

```tsx
'use client';

import { useLocale } from 'next-intl';

const RTL_LOCALES = new Set(['ar', 'he', 'fa', 'ur']);

export function useDirection(): 'ltr' | 'rtl' {
  const locale = useLocale();
  return RTL_LOCALES.has(locale) ? 'rtl' : 'ltr';
}

export function useIsRTL(): boolean {
  return useDirection() === 'rtl';
}
```

---

## CSS Logical Properties

**Always use logical properties instead of physical ones.** This is the single most impactful change for RTL support.

### Property Mapping

| Physical (avoid) | Logical (use) |
|---|---|
| `margin-left` | `margin-inline-start` |
| `margin-right` | `margin-inline-end` |
| `padding-left` | `padding-inline-start` |
| `padding-right` | `padding-inline-end` |
| `border-left` | `border-inline-start` |
| `border-right` | `border-inline-end` |
| `left` | `inset-inline-start` |
| `right` | `inset-inline-end` |
| `text-align: left` | `text-align: start` |
| `text-align: right` | `text-align: end` |
| `float: left` | `float: inline-start` |
| `float: right` | `float: inline-end` |
| `width` | `inline-size` |
| `height` | `block-size` |
| `border-radius: 8px 0 0 8px` | `border-start-start-radius: 8px; border-end-start-radius: 8px` |

### Shorthand Logical Properties

```css
/* Physical — AVOID */
.card {
  margin: 16px 24px 16px 8px;
  padding: 12px 20px 12px 16px;
}

/* Logical — USE */
.card {
  margin-block: 16px;
  margin-inline: 8px 24px;  /* start end */
  padding-block: 12px;
  padding-inline: 16px 20px; /* start end */
}
```

### Tailwind CSS v4 Logical Utilities

Tailwind v4 supports logical properties natively:

```tsx
// Physical (avoid for bidirectional layouts)
<div className="ml-4 mr-8 pl-2 pr-6 text-left">

// Logical (use instead)
<div className="ms-4 me-8 ps-2 pe-6 text-start">
```

| Physical Class | Logical Class |
|---|---|
| `ml-*` | `ms-*` (margin-inline-start) |
| `mr-*` | `me-*` (margin-inline-end) |
| `pl-*` | `ps-*` (padding-inline-start) |
| `pr-*` | `pe-*` (padding-inline-end) |
| `left-*` | `start-*` (inset-inline-start) |
| `right-*` | `end-*` (inset-inline-end) |
| `text-left` | `text-start` |
| `text-right` | `text-end` |
| `rounded-l-*` | `rounded-s-*` |
| `rounded-r-*` | `rounded-e-*` |
| `border-l-*` | `border-s-*` |
| `border-r-*` | `border-e-*` |

### Flexbox and Grid

Flexbox `row` and `row-reverse` respect `dir` automatically:

```tsx
// This works correctly in both LTR and RTL
<div className="flex flex-row gap-4">
  <Sidebar />    {/* Appears on left in LTR, right in RTL */}
  <MainContent />
</div>
```

Grid column placement also follows direction. No changes needed for standard grid layouts.

---

## Bidirectional Text Handling

### Mixed-Direction Content

When content contains both LTR and RTL text (e.g., English brand names in Arabic text):

```tsx
// Isolate embedded opposite-direction text
<p dir="rtl">
  هذا المنتج من <bdi>Acme Corp</bdi> متاح الآن
</p>
```

```tsx
// React component for bidi isolation
function BidiIsolate({ children }: { children: React.ReactNode }) {
  return <span style={{ unicodeBidi: 'isolate' }}>{children}</span>;
}

// Usage in translated string with brand name
<p>{t.rich('productBy', {
  brand: () => <BidiIsolate>Acme Corp</BidiIsolate>
})}</p>
```

### Numbers in RTL Context

Numbers are always LTR, but they can cause ordering issues:

```tsx
// Use CSS to ensure proper number rendering in RTL
.price-rtl {
  unicode-bidi: isolate;
  direction: ltr;  /* Numbers always display LTR */
}
```

```tsx
function Price({ amount }: { amount: number }) {
  const format = useFormatter();
  const isRTL = useIsRTL();

  return (
    <span className={isRTL ? 'price-rtl' : ''}>
      {format.number(amount, { style: 'currency', currency: 'SAR' })}
    </span>
  );
}
```

### Phone Numbers and Technical Content

```css
/* Always force LTR for technical content */
.phone-number,
.email,
.url,
.code-snippet {
  unicode-bidi: isolate;
  direction: ltr;
}
```

---

## RTL-Specific Layouts

### Icons That Need Mirroring

Some icons are directional and must be mirrored in RTL:

```tsx
// Icons that SHOULD mirror in RTL
const MIRROR_ICONS = new Set([
  'arrow-left',      // Navigation back
  'arrow-right',     // Navigation forward
  'chevron-left',    // Previous
  'chevron-right',   // Next
  'reply',           // Reply arrow
  'external-link',   // External link indicator
  'indent',          // Text indent
  'outdent',         // Text outdent
]);

// Icons that should NOT mirror
// - Search (magnifying glass)
// - Checkmark
// - Plus / Minus
// - Play button (universal media convention)
// - Clock
// - Heart / Star

function DirectionalIcon({ name, className }: { name: string; className?: string }) {
  const isRTL = useIsRTL();
  const shouldMirror = MIRROR_ICONS.has(name) && isRTL;

  return (
    <Icon
      name={name}
      className={`${className ?? ''} ${shouldMirror ? 'scale-x-[-1]' : ''}`}
    />
  );
}
```

### Scrolling and Carousels

```tsx
function Carousel({ items }: { items: React.ReactNode[] }) {
  const isRTL = useIsRTL();
  const scrollRef = useRef<HTMLDivElement>(null);

  function scrollNext() {
    scrollRef.current?.scrollBy({
      left: isRTL ? -300 : 300,
      behavior: 'smooth'
    });
  }

  function scrollPrev() {
    scrollRef.current?.scrollBy({
      left: isRTL ? 300 : -300,
      behavior: 'smooth'
    });
  }

  return (
    <div>
      <button onClick={scrollPrev}>
        <DirectionalIcon name="chevron-left" />
      </button>
      <div ref={scrollRef} className="flex overflow-x-auto gap-4" dir={isRTL ? 'rtl' : 'ltr'}>
        {items.map((item, i) => (
          <div key={i} className="min-w-[280px]">{item}</div>
        ))}
      </div>
      <button onClick={scrollNext}>
        <DirectionalIcon name="chevron-right" />
      </button>
    </div>
  );
}
```

### Progress Bars and Sliders

```css
/* Progress bar: reversed in RTL */
.progress-bar {
  /* Uses logical property — auto-flips in RTL */
  transform-origin: inline-start center;
}

/* Or explicitly with direction */
[dir='rtl'] .progress-fill {
  transform-origin: right center;
}
[dir='ltr'] .progress-fill {
  transform-origin: left center;
}
```

---

## Arabic-Specific Considerations

### Font Selection

Arabic text needs specific font support. System fonts vary in quality:

```css
/* Arabic-optimized font stack */
:root[lang='ar'] {
  --font-sans: 'IBM Plex Arabic', 'Noto Sans Arabic', 'Segoe UI', 'Tahoma', sans-serif;
  --font-serif: 'Noto Naskh Arabic', 'Traditional Arabic', serif;
}

body {
  font-family: var(--font-sans);
}
```

### Line Height and Spacing

Arabic script has taller ascenders/descenders than Latin. Increase line height:

```css
:root[lang='ar'] body {
  line-height: 1.8;          /* vs typical 1.5 for Latin */
  letter-spacing: 0;         /* Never add letter-spacing to Arabic */
  word-spacing: normal;
}
```

**Never use `letter-spacing` for Arabic** — it disconnects letters that must be joined.

### Arabic Numeral Systems

Arabic uses two numeral systems:
- **Western Arabic (0-9)**: Used in most digital contexts
- **Eastern Arabic (٠-٩)**: Used in some formal/traditional contexts

```tsx
function ArabicNumber({ value }: { value: number }) {
  const locale = useLocale();

  // Use standard formatting — Intl handles numeral system
  const format = useFormatter();
  return <span>{format.number(value)}</span>;

  // Force Eastern Arabic numerals if needed:
  // return <span>{value.toLocaleString('ar-SA', { numberingSystem: 'arab' })}</span>;
}
```

---

## Hebrew-Specific Considerations

### Hebrew Punctuation

Hebrew punctuation follows different rules. Periods, commas, and question marks stay in the same position, but quote marks differ:

```json
{
  "he": {
    "quoted": "הוא אמר: \u201Cשלום\u201D",
    "question": "?מה שלומך"
  }
}
```

### Hebrew Vowels (Nikud)

Most modern Hebrew text is unvocalized. If your app needs vocalized text (e.g., educational content), ensure fonts support nikud:

```css
:root[lang='he'] {
  --font-sans: 'Noto Sans Hebrew', 'Segoe UI', 'Arial', sans-serif;
  font-feature-settings: 'liga' 1;  /* Ensure ligature support */
}
```

---

## Testing RTL

### Visual Regression with Playwright

```ts
// tests/rtl.spec.ts
import { test, expect } from '@playwright/test';

const pages = ['/', '/about', '/dashboard'];
const locales = ['en', 'ar'];

for (const page of pages) {
  for (const locale of locales) {
    test(`${page} renders correctly in ${locale}`, async ({ page: pw }) => {
      await pw.goto(`http://localhost:3000/${locale}${page}`);

      // Check document direction
      const dir = await pw.getAttribute('html', 'dir');
      expect(dir).toBe(locale === 'ar' ? 'rtl' : 'ltr');

      // Visual snapshot
      await expect(pw).toHaveScreenshot(`${locale}${page.replace(/\//g, '-')}.png`, {
        fullPage: true
      });
    });
  }
}
```

### Pseudo-RTL Testing (Without Real Translations)

Test RTL layout without needing Arabic translations:

```ts
// scripts/pseudo-rtl.ts
// Converts LTR text to pseudo-RTL for layout testing
function pseudoRTL(text: string): string {
  // Reverse words but keep ICU placeholders intact
  return text
    .split(/(\{[^}]+\})/)
    .map((segment) => {
      if (segment.startsWith('{')) return segment; // Keep ICU syntax
      return segment.split(' ').reverse().join(' ');
    })
    .join('');
}
```

### Manual RTL Checklist

- [ ] Text alignment flips (start-aligned, not always left-aligned)
- [ ] Icons mirror where appropriate (arrows, chevrons)
- [ ] Padding and margins use logical properties
- [ ] Scrollbars appear on correct side
- [ ] Form labels and inputs align correctly
- [ ] Breadcrumbs read right-to-left
- [ ] Progress indicators fill from right
- [ ] Table columns order correctly
- [ ] Modals/dialogs position correctly
- [ ] Toast notifications appear on correct side
- [ ] No overlapping text or clipped content
- [ ] Numbers and technical content remain LTR
- [ ] Mixed-direction text displays correctly
