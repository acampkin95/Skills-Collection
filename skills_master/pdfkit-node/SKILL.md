---
name: pdfkit-node
description: PDFKit for Node.js PDF generation with text, vector graphics, images, tables, fonts, and annotations. Use for programmatic PDF creation from structured data.
version: 2.0.0
reviewed: "2026-06-04"
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


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.