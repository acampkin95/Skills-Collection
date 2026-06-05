---
name: pdfkit-node
description: PDFKit Node.js PDF generation with text, vector graphics, images, tables, and annotations.
---

# PDFKit — Node.js PDF Generation Skill

PDFKit is a JavaScript library for creating complex, multi-page PDF documents in Node.js and the browser. It uses a chainable API that feels natural to JS developers. All operations happen in-memory and stream to a writable destination.

## Installation context

PDFKit is installed globally (`npm i -g pdfkit`). For project-local use, `npm i pdfkit`. In browser contexts, bundle with webpack/rollup and pipe to `blob-stream` instead of `fs.createWriteStream`.

## Core workflow

Every PDFKit document follows this structure:

```javascript
const PDFDocument = require('pdfkit');
const fs = require('fs');

const doc = new PDFDocument({
  size: 'A4',           // or 'Letter', [width, height] in points
  margin: 50,           // uniform margin, or { top, bottom, left, right }
  bufferPages: true,    // enables page reordering and back-filling
});

doc.pipe(fs.createWriteStream('output.pdf'));

// ... add content ...

doc.end();  // finalise — nothing writes to disk until this is called
```

### Document options

| Option | Default | Notes |
|--------|---------|-------|
| `size` | `'Letter'` | `'A4'`, `'A3'`, `'Legal'`, or `[w, h]` in points (72pt = 1 inch) |
| `margin` | `72` | Number for uniform, or `{ top, bottom, left, right }` |
| `layout` | `'portrait'` | `'landscape'` flips width/height |
| `bufferPages` | `false` | Set `true` to access/modify pages after creation |
| `info` | `{}` | Metadata: `{ Title, Author, Subject, Keywords, CreationDate }` |
| `compress` | `true` | Compress streams in the PDF |

## Text

The text API is the most-used feature. Key things to understand: text wraps automatically within the current page margins, and the cursor advances after each call.

```javascript
// Basic text
doc.fontSize(12).text('Hello world');

// Positioned text (x, y)
doc.text('Positioned', 100, 200);

// Styled text
doc
  .font('Helvetica-Bold')
  .fontSize(24)
  .fillColor('#333333')
  .text('Large bold heading');

// Text with options
doc.text('Right-aligned paragraph with specific width', 50, 100, {
  width: 400,
  align: 'right',    // 'left', 'center', 'right', 'justify'
  lineGap: 4,        // extra space between lines
  paragraphGap: 10,  // extra space after paragraph
});

// Inline formatting (rich text)
doc
  .font('Helvetica')
  .text('This is ', { continued: true })
  .font('Helvetica-Bold')
  .text('bold', { continued: true })
  .font('Helvetica')
  .text(' and this is normal.');

// Lists
doc.list(['First item', 'Second item', 'Third item'], {
  bulletRadius: 2,
  textIndent: 20,
  bulletIndent: 10,
});

// Move cursor without printing
doc.moveDown(2);  // move down 2 lines
```

### Built-in fonts

These are always available without embedding:
`Courier`, `Courier-Bold`, `Courier-Oblique`, `Courier-BoldOblique`,
`Helvetica`, `Helvetica-Bold`, `Helvetica-Oblique`, `Helvetica-BoldOblique`,
`Times-Roman`, `Times-Bold`, `Times-Italic`, `Times-BoldItalic`,
`Symbol`, `ZapfDingbats`

### Custom fonts

```javascript
// Register a font file
doc.registerFont('CustomFont', 'path/to/font.ttf');
doc.font('CustomFont').text('Custom typography');

// Supports: .ttf, .otf, .woff, .woff2, .ttc, .dfont
```

## Images

PDFKit supports JPEG and PNG (including indexed and transparent PNGs).

```javascript
// Basic image
doc.image('path/to/image.png', 50, 50);

// From buffer
const buffer = fs.readFileSync('photo.jpg');
doc.image(buffer, 50, 50);

// Scaled to width
doc.image('chart.png', { width: 400 });

// Fit within bounds (maintains aspect ratio)
doc.image('logo.png', 50, 50, {
  fit: [200, 100],
  align: 'center',
  valign: 'center',
});

// Cover (fills area, may crop)
doc.image('background.jpg', 0, 0, { cover: [612, 792] });
```

**Image gotchas:**
- Only JPEG and PNG are supported natively — convert SVG/WebP/GIF before embedding
- Large images bloat the PDF; resize externally if the source is high-res
- Base64 data URIs work: `doc.image('data:image/png;base64,...')`

## Vector graphics

PDFKit has a Canvas-like drawing API for shapes and paths.

```javascript
// Rectangle
doc.rect(50, 50, 200, 100).fill('#4A90D9');

// Rounded rectangle
doc.roundedRect(50, 50, 200, 100, 10).stroke();

// Circle and ellipse
doc.circle(300, 200, 50).fill('#FF6B6B');
doc.ellipse(300, 200, 80, 50).stroke('#333');

// Line
doc.moveTo(50, 50).lineTo(200, 200).stroke();

// Polygon
doc
  .moveTo(100, 100)
  .lineTo(200, 100)
  .lineTo(150, 50)
  .closePath()
  .fill('#2ECC71');

// Path operations
doc
  .save()
  .lineWidth(2)
  .strokeColor('#E74C3C')
  .dash(5, { space: 3 })
  .moveTo(50, 300)
  .lineTo(550, 300)
  .stroke()
  .restore();

// SVG path
doc.path('M 0,20 L 100,160 Q 130,200 150,120 C 190,-40 200,200 300,150 L 400,90')
   .stroke('#3498DB');

// Gradients
const grad = doc.linearGradient(0, 0, 200, 0)
  .stop(0, '#667eea')
  .stop(1, '#764ba2');
doc.rect(50, 400, 200, 50).fill(grad);
```

## Tables

PDFKit has a built-in table API with full styling support.

```javascript
doc.table({
  data: [
    ['Name', 'Role', 'Location'],           // header row
    ['Alex', 'Architect', 'Perth'],
    ['Sam', 'Developer', 'Melbourne'],
  ],
  defaultStyle: {
    fontSize: 10,
    font: 'Helvetica',
    border: true,
    padding: [5, 8],
  },
  columnStyles: [
    { width: 150 },
    { width: 200 },
    { width: 150 },
  ],
  rowStyles: [
    { font: 'Helvetica-Bold', backgroundColor: '#f0f0f0' },  // header row
  ],
});
```

### Table features

- **Row spans / column spans**: `{ rowSpan: 2, text: '...' }`, `{ colSpan: 3, text: '...' }`
- **Per-cell borders**: `{ border: [true, false, true, false] }` (top, right, bottom, left)
- **Background colours**: `{ backgroundColor: '#eee' }`
- **Style precedence**: defaultStyle → columnStyles → rowStyles → cell-level (most specific wins)

## Page management

```javascript
// Add a new page
doc.addPage();

// Add page with different options
doc.addPage({ size: 'A3', layout: 'landscape' });

// Page break detection — check remaining space
const bottomMargin = doc.page.height - doc.page.margins.bottom;
if (doc.y > bottomMargin - 100) {
  doc.addPage();
}

// Page numbers (with bufferPages: true)
const range = doc.bufferedPageRange();
for (let i = range.start; i < range.start + range.count; i++) {
  doc.switchToPage(i);
  doc.fontSize(8).text(
    `Page ${i + 1} of ${range.count}`,
    50, doc.page.height - 50,
    { align: 'center' }
  );
}
```

## Annotations and links

```javascript
// Web link
doc.text('Visit our site', 50, 100, { link: 'https://example.com', underline: true });

// Internal link (go to another part of the document)
doc.text('Go to section 2', 50, 100, { goTo: 'section2' });
// ... later in the doc ...
doc.text('Section 2', 50, 100, { destination: 'section2' });

// Note annotation
doc.note(100, 100, 200, 50, 'This is a note annotation');

// Highlight
doc.highlight(100, 100, 200, 20, { color: [255, 255, 0] });
```

## Common patterns

### Invoice / receipt template

```javascript
function createInvoice(doc, data) {
  // Header
  doc.image('logo.png', 50, 50, { width: 100 });
  doc.fontSize(20).text('INVOICE', 400, 50, { align: 'right' });
  doc.fontSize(10).text(`Invoice #: ${data.number}`, 400, 75, { align: 'right' });
  doc.text(`Date: ${data.date}`, 400, 90, { align: 'right' });

  // Line items table
  doc.moveDown(4);
  doc.table({
    data: [
      ['Description', 'Qty', 'Rate', 'Amount'],
      ...data.items.map(item => [
        item.description,
        String(item.qty),
        `$${item.rate.toFixed(2)}`,
        `$${(item.qty * item.rate).toFixed(2)}`,
      ]),
    ],
    // ... styling ...
  });

  // Total
  const total = data.items.reduce((sum, i) => sum + i.qty * i.rate, 0);
  doc.fontSize(14).text(`Total: $${total.toFixed(2)}`, { align: 'right' });
}
```

### Multi-page report with headers/footers

Use `bufferPages: true` and fill headers/footers in a second pass after all content is placed:

```javascript
const doc = new PDFDocument({ bufferPages: true });
// ... add all content ...

// Second pass: add headers and footers
const pages = doc.bufferedPageRange();
for (let i = pages.start; i < pages.start + pages.count; i++) {
  doc.switchToPage(i);

  // Header
  doc.fontSize(8).fillColor('#999')
     .text('Company Report — Confidential', 50, 30);

  // Footer
  doc.text(`Page ${i + 1} of ${pages.count}`, 50, doc.page.height - 40, {
    align: 'center',
  });
}
doc.end();
```

## When NOT to use PDFKit

- **PDF from a webpage** — use Puppeteer's `page.pdf()` instead
- **Filling existing PDF forms** — use `pdf-lib` (PDFKit creates new docs, it doesn't edit existing ones)
- **Complex Python pipeline** — use ReportLab instead for Python-native PDF generation
- **Simple text-to-PDF** — if you just need plain text in a PDF, Puppeteer with an HTML template is simpler

## Reference

For AcroForms, PDF security (encryption/permissions), accessibility (tagged PDF), and outlines, see `references/advanced-features.md`.

## Legal/Document Skills (Cross-Reference)

When generating court documents, evidence bundles, or legal reports, use with:

| Related Skill | Use when |
|---------------|----------|
| `legal-matter-ops` | Generating print-ready court bundles, evidence reports |
| `csv-legal-analysis-v2` | Generating statistical analysis reports, evidence-grade PDFs |
| `affidavit-court-preparation` | Generating affidavit bundles, annexure indexes, hearing prep documents |
| `srl-case-file-manager-wa` | Generating dashboard reports, evidence indexes as PDF |
| `wa-law-general` | Generating general legal information documents |
| `reportlab-python` | Python alternative for the same PDF generation tasks |
