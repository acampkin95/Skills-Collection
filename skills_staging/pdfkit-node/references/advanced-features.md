# PDFKit — Advanced Features

## AcroForms (interactive forms)

```javascript
// Text input
doc.formText('fieldName', 100, 500, 200, 20, {
  value: 'Default value',
  fontSize: 12,
  borderColor: '#999',
});

// Checkbox
doc.formCheckbox('agreeTerms', 100, 470, 15, 15, {
  value: 'Yes',
});

// Radio button group
doc.formRadioButton('size', 100, 440, 15, 15, { value: 'small' });
doc.formRadioButton('size', 100, 420, 15, 15, { value: 'medium' });
doc.formRadioButton('size', 100, 400, 15, 15, { value: 'large' });

// Dropdown/combo
doc.formCombo('country', 100, 370, 200, 20, {
  select: ['Australia', 'New Zealand', 'United Kingdom'],
  value: 'Australia',
  edit: true,  // allows typing custom values
});

// Push button
doc.formPushButton('submitBtn', 100, 340, 100, 30, {
  label: 'Submit',
});
```

## PDF Security

```javascript
const doc = new PDFDocument({
  userPassword: 'user123',          // password to open
  ownerPassword: 'owner456',       // password for full access
  permissions: {
    printing: 'highResolution',     // 'lowResolution' or false
    modifying: false,
    copying: false,
    annotating: true,
    fillingForms: true,
    contentAccessibility: true,
    documentAssembly: false,
  },
});
```

## Accessibility (Tagged PDF)

```javascript
const doc = new PDFDocument({
  tagged: true,        // enable tagged PDF
  displayTitle: true,  // show title instead of filename
  lang: 'en-AU',
  info: { Title: 'Accessible Document' },
});

// Mark content structure
doc.markStructureContent('H1');
doc.fontSize(24).text('Heading');
doc.endMarkedContent();

doc.markStructureContent('P');
doc.fontSize(12).text('Paragraph content here.');
doc.endMarkedContent();
```

## Document outlines (bookmarks)

```javascript
doc.outline.addItem('Chapter 1');
doc.text('Chapter 1 content...');
doc.addPage();

const ch2 = doc.outline.addItem('Chapter 2');
doc.text('Chapter 2 content...');

// Sub-items
ch2.addItem('Section 2.1');
```

## Streaming to HTTP response

```javascript
const express = require('express');
const app = express();

app.get('/invoice/:id', (req, res) => {
  const doc = new PDFDocument();

  res.setHeader('Content-Type', 'application/pdf');
  res.setHeader('Content-Disposition', `attachment; filename=invoice-${req.params.id}.pdf`);

  doc.pipe(res);
  doc.text(`Invoice #${req.params.id}`);
  doc.end();
});
```

## Browser usage (with blob-stream)

```javascript
import PDFDocument from 'pdfkit';
import blobStream from 'blob-stream';

const doc = new PDFDocument();
const stream = doc.pipe(blobStream());

doc.text('Browser-generated PDF');
doc.end();

stream.on('finish', () => {
  const blob = stream.toBlob('application/pdf');
  const url = stream.toBlobURL('application/pdf');

  // Open in new tab
  window.open(url);

  // Or download
  const a = document.createElement('a');
  a.href = url;
  a.download = 'document.pdf';
  a.click();
});
```

## Pattern: reusable components

Build composable functions for repeated elements:

```javascript
function drawHeader(doc, { logo, title, subtitle }) {
  const y = doc.y;
  if (logo) doc.image(logo, 50, y, { width: 60 });
  doc.fontSize(18).text(title, 120, y);
  if (subtitle) doc.fontSize(10).fillColor('#666').text(subtitle, 120, y + 22);
  doc.fillColor('#000').moveDown(2);
}

function drawDivider(doc) {
  doc.save()
     .strokeColor('#E0E0E0')
     .lineWidth(0.5)
     .moveTo(50, doc.y)
     .lineTo(doc.page.width - 50, doc.y)
     .stroke()
     .restore()
     .moveDown(0.5);
}
```

## Performance tips

- Reuse font objects — don't load the same font file repeatedly
- For large documents (>100 pages), avoid `bufferPages` unless you need it
- Compress images before embedding — PDFKit doesn't optimise image data
- Use streams rather than buffering the entire PDF in memory
- For server workloads, consider pooling PDFDocument creation
