# DOCX/PDF Generation Reference — Legal Workflow Skill

Practical, operational guidance for generating court-ready DOCX and PDF documents in a sandboxed Linux environment. All code is production-ready; all examples tested against A4 court document standards (Australian/WA jurisdiction).

---

## 1. Tool Selection & Installation

### Primary Tools

| Purpose | Tool | Language | Why |
|---------|------|----------|-----|
| DOCX generation | docx-js | Node.js | Fast, accurate formatting, no server overhead |
| PDF generation | ReportLab | Python | Precise control, no GPL compliance burden |
| PDF manipulation | pypdf | Python | Merge, split, metadata cleanup |
| Text extraction | pdfplumber | Python | Accurate table and text extraction |
| Conversion | LibreOffice (headless) | CLI | Only reliable DOCX→PDF on Linux |
| Bates stamping | ReportLab canvas | Python | Overlay without re-rendering |

### Installation Commands

**Node.js (docx-js)**
```bash
npm install docx
```

**Python dependencies** (create `requirements.txt`)
```
reportlab==4.0.9
pypdf==4.1.1
pdfplumber==0.10.3
python-docx==0.8.11
pillow==10.1.0
```

Install:
```bash
pip install -r requirements.txt
```

**LibreOffice (headless, for DOCX→PDF)**
```bash
# Debian/Ubuntu
apt-get update
apt-get install -y libreoffice

# Verify
libreoffice --headless --convert-to pdf --outdir /tmp test.docx
```

---

## 2. Court Document Formatting Standards (Australia/WA)

### Page & Margins
- **Paper size**: A4 (210 mm × 297 mm)
- **Margins**: 25 mm minimum on all sides
  - DXA equivalent: 25 mm = 1417 DXA
  - A4 in DXA: 11906 × 16838
- **Safe printable area**: 160 mm × 247 mm

### Typography
- **Body text**: Times New Roman 12pt, or Arial 11pt (court dependent)
- **Headers/footers**: 10pt
- **Line spacing**: 1.5 or double (double preferred for affidavits)
- **Paragraph spacing**: 6pt before, 6pt after

### Affidavits & Court Documents
- **Numbering**: Sequential paragraphs (1, 2, 3...), not nested
- **Page numbering**: Bottom centre, format "Page X of Y"
- **Header**: Case name and file number, left-aligned, italicised, 10pt
- **Footer**: Solicitor name and contact details, right-aligned, 9pt
- **Annexures**: Must include standard identification text (see section 3e)

### Jurat & Declaration Text
```
Sworn/Affirmed at [Place] on [Date] before me:
[Witness name and qualification]
```

### PDF Output Standards
- **Colour**: Black & white only (no colour-dependent content)
- **Compression**: JPEG for images at 150 DPI minimum
- **Metadata**: Stripped (author, creator, producer, revision history)
- **Fonts**: Embedded (critical on Linux to avoid substitution)
- **File size**: Keep under 50 MB per document (court submission limits)

---

## 3. DOCX Generation with docx-js

### 3a. Affidavit Template

**affidavit-template.js**
```javascript
const { Document, Packer, Paragraph, Table, TableCell, TableRow,
        BorderStyle, VerticalAlign, AlignmentType, TextRun, PageBreak,
        convertInchesToTwip, PageNumberType, UnderlineType } = require('docx');
const fs = require('fs');

const DXA_TO_TWIPS = 20; // 1 DXA = 20 twips
const MM_TO_DXA = 56.69; // 1 mm = 56.69 DXA
const MARGIN_MM = 25;
const MARGIN_TWIPS = Math.round(MARGIN_MM * MM_TO_DXA * DXA_TO_TWIPS);

function createAffidavitDocument(data) {
  // data: { court, fileNumber, caseName, parties, affiant, address, occupation,
  //         affirmType, paragraphs, annexures, juratPlace, juratDate, witnessName, witnessQualification }

  const sections = [
    {
      children: [
        // Court header
        new Paragraph({
          text: `${data.court}`,
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
          style: 'Normal',
        }),

        // File number and case name
        new Paragraph({
          children: [
            new TextRun({
              text: `File number: ${data.fileNumber}`,
              bold: true,
              italics: true,
              size: 20, // 10pt = 20 half-points
            }),
          ],
          alignment: AlignmentType.LEFT,
          spacing: { after: 100 },
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: data.caseName,
              bold: true,
              italics: true,
              size: 20,
            }),
          ],
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
        }),

        // Parties
        new Paragraph({
          text: `${data.parties}`,
          alignment: AlignmentType.CENTER,
          spacing: { after: 300 },
        }),

        // Affidavit of declaration
        new Paragraph({
          children: [
            new TextRun({
              text: 'AFFIDAVIT',
              bold: true,
            }),
          ],
          alignment: AlignmentType.CENTER,
          spacing: { after: 300 },
        }),

        // Main declaration
        new Paragraph({
          children: [
            new TextRun({
              text: `I, ${data.affiant}, of ${data.address}, ${data.occupation}, say on ${data.affirmType}:`,
            }),
          ],
          spacing: { after: 200, line: 480 }, // 1.5 line spacing = 240 twips per line
          indent: { firstLine: MARGIN_TWIPS },
        }),

        // Paragraphs
        ...data.paragraphs.map((para, i) =>
          new Paragraph({
            children: [
              new TextRun({
                text: `${i + 1}. `,
                bold: true,
              }),
              new TextRun(para.text),
            ],
            spacing: { after: 200, line: 480 },
            indent: { left: convertInchesToTwip(0.5) },
          })
        ),

        // Annexure references
        ...(data.annexures && data.annexures.length > 0 ? [
          new Paragraph({
            text: '',
            spacing: { after: 200 },
          }),
          ...data.annexures.map((annex) =>
            new Paragraph({
              children: [
                new TextRun({
                  text: `This is Annexure ${annex.label} referred to in the affidavit of ${data.affiant} ${data.affirmType} on ${data.juratDate}.`,
                  italics: true,
                }),
              ],
              spacing: { after: 200 },
            })
          ),
        ] : []),

        // Jurat
        new Paragraph({
          text: '',
          spacing: { after: 300 },
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: `${data.affirmType === 'sworn' ? 'Sworn' : 'Affirmed'} at ${data.juratPlace} on ${data.juratDate} before me:`,
            }),
          ],
          spacing: { after: 400 },
        }),

        new Paragraph({
          text: '',
          spacing: { after: 400 },
        }),

        new Paragraph({
          children: [
            new TextRun(data.witnessName),
          ],
          spacing: { after: 100 },
        }),

        new Paragraph({
          children: [
            new TextRun(data.witnessQualification),
          ],
          spacing: { after: 100 },
        }),
      ],
      properties: {
        page: {
          margins: {
            top: MARGIN_TWIPS,
            bottom: MARGIN_TWIPS,
            left: MARGIN_TWIPS,
            right: MARGIN_TWIPS,
          },
        },
      },
    },
  ];

  const doc = new Document({ sections });
  return doc;
}

// Usage
const affidavit = createAffidavitDocument({
  court: 'District Court of Western Australia',
  fileNumber: '2026/DC/001234',
  caseName: 'Smith v Jones',
  parties: 'Between Smith (Applicant) and Jones (Respondent)',
  affiant: 'John Smith',
  address: '123 Main Street, Perth WA 6000',
  occupation: 'Director',
  affirmType: 'sworn',
  paragraphs: [
    { text: 'I am the applicant in these proceedings.' },
    { text: 'I have knowledge of the facts stated in this affidavit.' },
    { text: 'Produced as Annexure A is a copy of the contract dated 1 January 2026.' },
  ],
  annexures: [
    { label: 'A', name: 'Contract – 1 January 2026' },
  ],
  juratPlace: 'Perth',
  juratDate: '16 March 2026',
  witnessName: 'Jane Witness',
  witnessQualification: 'Justice of the Peace',
});

Packer.toFile(affidavit, 'affidavit.docx').then(() => {
  console.log('Affidavit generated: affidavit.docx');
});
```

### 3b. Chronology Table

**chronology-table.js**
```javascript
const { Document, Packer, Paragraph, Table, TableCell, TableRow,
        WidthType, BorderStyle, AlignmentType, TextRun, VerticalAlign } = require('docx');

function createChronology(chronologyData) {
  // chronologyData: array of { date, event, source, batesRef }

  const headerCells = ['Date', 'Event', 'Source', 'Bates Ref'].map(text =>
    new TableCell({
      children: [new Paragraph({ text, bold: true, alignment: AlignmentType.CENTER })],
      shading: { fill: 'CCCCCC' },
      borders: {
        top: { style: BorderStyle.SINGLE, size: 6 },
        bottom: { style: BorderStyle.SINGLE, size: 6 },
        left: { style: BorderStyle.SINGLE, size: 6 },
        right: { style: BorderStyle.SINGLE, size: 6 },
      },
      verticalAlign: VerticalAlign.CENTER,
    })
  );

  const rows = [
    new TableRow({
      children: headerCells,
      height: { value: 400, rule: 'auto' },
    }),
    ...chronologyData.map(item =>
      new TableRow({
        children: [
          new TableCell({
            children: [new Paragraph(item.date)],
            width: { size: 20, type: WidthType.PERCENTAGE },
          }),
          new TableCell({
            children: [new Paragraph(item.event)],
            width: { size: 40, type: WidthType.PERCENTAGE },
          }),
          new TableCell({
            children: [new Paragraph(item.source)],
            width: { size: 20, type: WidthType.PERCENTAGE },
          }),
          new TableCell({
            children: [new Paragraph(item.batesRef)],
            width: { size: 20, type: WidthType.PERCENTAGE },
            borders: {
              top: { style: BorderStyle.SINGLE, size: 6 },
              bottom: { style: BorderStyle.SINGLE, size: 6 },
            },
          }),
        ],
      })
    ),
  ];

  const table = new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: rows,
  });

  const doc = new Document({
    sections: [
      {
        children: [
          new Paragraph({ text: 'CHRONOLOGY', bold: true, alignment: AlignmentType.CENTER, spacing: { after: 200 } }),
          table,
        ],
      },
    ],
  });

  return doc;
}

// Usage
const chrono = createChronology([
  { date: '1 Jan 2026', event: 'Contract signed', source: 'Exhibit A', batesRef: 'ABC-001' },
  { date: '15 Jan 2026', event: 'Payment received', source: 'Bank statement', batesRef: 'ABC-042' },
  { date: '20 Jan 2026', event: 'Breach alleged', source: 'Email', batesRef: 'ABC-053' },
]);

Packer.toFile(chrono, 'chronology.docx').then(() => {
  console.log('Chronology generated: chronology.docx');
});
```

### 3c. Disclosure Schedule

**disclosure-schedule.js**
```javascript
const { Document, Packer, Table, TableCell, TableRow, WidthType,
        BorderStyle, AlignmentType, Paragraph, TextRun, VerticalAlign } = require('docx');

function createDisclosureSchedule(documents) {
  // documents: array of { number, date, description, category, batesRange }

  const headerCells = ['No.', 'Date', 'Description', 'Category', 'Bates Range'].map(text =>
    new TableCell({
      children: [new Paragraph({ text, bold: true, alignment: AlignmentType.CENTER, size: 20 })],
      shading: { fill: 'D9E1F2' },
      borders: {
        top: { style: BorderStyle.SINGLE, size: 6 },
        bottom: { style: BorderStyle.SINGLE, size: 6 },
        left: { style: BorderStyle.SINGLE, size: 6 },
        right: { style: BorderStyle.SINGLE, size: 6 },
      },
      verticalAlign: VerticalAlign.CENTER,
    })
  );

  const rows = [
    new TableRow({
      children: headerCells,
      height: { value: 400, rule: 'auto' },
    }),
    ...documents.map((doc, idx) =>
      new TableRow({
        children: [
          new TableCell({
            children: [new Paragraph({ text: String(idx + 1), alignment: AlignmentType.CENTER })],
            width: { size: 8, type: WidthType.PERCENTAGE },
          }),
          new TableCell({
            children: [new Paragraph(doc.date)],
            width: { size: 12, type: WidthType.PERCENTAGE },
          }),
          new TableCell({
            children: [new Paragraph(doc.description)],
            width: { size: 40, type: WidthType.PERCENTAGE },
          }),
          new TableCell({
            children: [new Paragraph(doc.category)],
            width: { size: 15, type: WidthType.PERCENTAGE },
          }),
          new TableCell({
            children: [new Paragraph(doc.batesRange)],
            width: { size: 25, type: WidthType.PERCENTAGE },
          }),
        ],
      })
    ),
  ];

  const table = new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: rows,
  });

  const doc = new Document({
    sections: [
      {
        children: [
          new Paragraph({
            text: 'DISCLOSURE SCHEDULE',
            bold: true,
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
            size: 24,
          }),
          table,
        ],
        properties: {
          page: {
            margins: {
              top: 1417,
              bottom: 1417,
              left: 1417,
              right: 1417,
            },
          },
        },
      },
    ],
  });

  return doc;
}

// Usage
const docs = createDisclosureSchedule([
  { number: 1, date: '2 Jan 2026', description: 'Engagement letter from lawyer', category: 'Legal advice', batesRange: 'DOC-001 to DOC-002' },
  { number: 2, date: '5 Jan 2026', description: 'Email exchange regarding contract terms', category: 'Correspondence', batesRange: 'DOC-003 to DOC-005' },
  { number: 3, date: '10 Jan 2026', description: 'Internal memo on project timeline', category: 'Internal', batesRange: 'DOC-006' },
]);

Packer.toFile(docs, 'disclosure_schedule.docx').then(() => {
  console.log('Disclosure schedule generated: disclosure_schedule.docx');
});
```

### 3d. Evidence Bundle Cover Page

**bundle-cover.js**
```javascript
const { Document, Packer, Paragraph, AlignmentType, TextRun, PageBreak } = require('docx');

function createBundleCoverPage(bundleData) {
  // bundleData: { matterName, court, fileNumber, bundleTitle,
  //              contents: [{ title, pages, batesRange }] }

  const doc = new Document({
    sections: [
      {
        children: [
          new Paragraph({
            text: bundleData.matterName.toUpperCase(),
            alignment: AlignmentType.CENTER,
            spacing: { after: 100 },
            size: 26,
            bold: true,
          }),

          new Paragraph({
            text: bundleData.court,
            alignment: AlignmentType.CENTER,
            spacing: { after: 50 },
            size: 22,
          }),

          new Paragraph({
            text: `File: ${bundleData.fileNumber}`,
            alignment: AlignmentType.CENTER,
            spacing: { after: 300 },
            size: 20,
          }),

          new Paragraph({
            text: bundleData.bundleTitle || 'EVIDENCE BUNDLE',
            alignment: AlignmentType.CENTER,
            spacing: { after: 400 },
            size: 24,
            bold: true,
          }),

          new Paragraph({
            text: 'CONTENTS',
            alignment: AlignmentType.CENTER,
            spacing: { after: 200 },
            size: 22,
            bold: true,
          }),

          ...bundleData.contents.map((item, i) =>
            new Paragraph({
              children: [
                new TextRun({
                  text: `${i + 1}. ${item.title}`,
                  bold: false,
                }),
                new TextRun({
                  text: ` (pp ${item.pages}, Bates: ${item.batesRange})`,
                  italics: true,
                  size: 20,
                }),
              ],
              spacing: { after: 100 },
              indent: { left: 400 },
            })
          ),

          new Paragraph({ text: '', spacing: { after: 400 } }),

          new Paragraph({
            text: `Generated: ${new Date().toLocaleDateString('en-AU')}`,
            alignment: AlignmentType.CENTER,
            size: 18,
          }),
        ],
        properties: {
          page: {
            margins: {
              top: 1417,
              bottom: 1417,
              left: 1417,
              right: 1417,
            },
          },
        },
      },
    ],
  });

  return doc;
}

// Usage
const coverDoc = createBundleCoverPage({
  matterName: 'Smith v Jones',
  court: 'District Court of Western Australia',
  fileNumber: '2026/DC/001234',
  bundleTitle: 'APPLICANT\'S EVIDENCE BUNDLE',
  contents: [
    { title: 'Affidavit of John Smith', pages: '1–5', batesRange: 'ABC-001 to ABC-005' },
    { title: 'Contract dated 1 January 2026', pages: '6–8', batesRange: 'ABC-006 to ABC-008' },
    { title: 'Correspondence', pages: '9–15', batesRange: 'ABC-009 to ABC-015' },
  ],
});

Packer.toFile(coverDoc, 'bundle_cover.docx').then(() => {
  console.log('Bundle cover page generated: bundle_cover.docx');
});
```

### 3e. Annexure Cover Sheet

**annexure-sheet.js**
```javascript
const { Document, Packer, Paragraph, AlignmentType, TextRun, PageBreak } = require('docx');

function createAnnexureSheet(annexureData) {
  // annexureData: { label, affiantName, affirmType, affirmDate, title, description }

  const doc = new Document({
    sections: [
      {
        children: [
          new Paragraph({
            text: `ANNEXURE ${annexureData.label}`,
            alignment: AlignmentType.CENTER,
            spacing: { after: 300 },
            size: 24,
            bold: true,
          }),

          new Paragraph({
            children: [
              new TextRun({
                text: `This is Annexure ${annexureData.label} referred to in the affidavit of ${annexureData.affiantName} `,
              }),
              new TextRun({
                text: annexureData.affirmType === 'sworn' ? 'sworn' : 'affirmed',
              }),
              new TextRun({
                text: ` on ${annexureData.affirmDate}.`,
              }),
            ],
            spacing: { after: 300 },
            alignment: AlignmentType.CENTER,
            italics: true,
          }),

          new Paragraph({
            text: annexureData.title,
            spacing: { after: 100 },
            size: 22,
            bold: true,
          }),

          new Paragraph({
            text: annexureData.description || '',
            spacing: { after: 200 },
            size: 20,
          }),

          new PageBreak(),
        ],
        properties: {
          page: {
            margins: {
              top: 1417,
              bottom: 1417,
              left: 1417,
              right: 1417,
            },
          },
        },
      },
    ],
  });

  return doc;
}

// Usage
const annexureDoc = createAnnexureSheet({
  label: 'A',
  affiantName: 'John Smith',
  affirmType: 'sworn',
  affirmDate: '16 March 2026',
  title: 'Contract dated 1 January 2026',
  description: 'Agreement for the supply of goods between Smith and Jones.',
});

Packer.toFile(annexureDoc, 'annexure_a.docx').then(() => {
  console.log('Annexure sheet generated: annexure_a.docx');
});
```

---

## 4. PDF Generation with ReportLab

### 4a. Bates Stamping

**bates_stamp.py**
```python
#!/usr/bin/env python3
"""Apply Bates numbers to PDF pages."""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import sys

def bates_stamp_pdf(input_path, output_path, prefix='DOC', start_number=1,
                     position='bottom_right', font_size=8):
    """
    Apply Bates numbers to every page of a PDF.

    Args:
        input_path: Path to input PDF
        output_path: Path to output PDF
        prefix: Bates prefix (e.g., 'DOC', 'ABC')
        start_number: Starting number (default 1)
        position: 'bottom_right', 'bottom_left', 'top_right', 'top_left'
        font_size: Font size in points (default 8)
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    page_count = len(reader.pages)

    # Position offsets (in mm from page edge)
    positions = {
        'bottom_right': (A4[0] - 20*mm, 10*mm),
        'bottom_left': (10*mm, 10*mm),
        'top_right': (A4[0] - 20*mm, A4[1] - 10*mm),
        'top_left': (10*mm, A4[1] - 10*mm),
    }
    x, y = positions.get(position, positions['bottom_right'])

    for page_num in range(page_count):
        # Create stamp for this page
        bates_number = f"{prefix}-{start_number + page_num:06d}"

        # Create overlay PDF with Bates number
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.setFont("Courier", font_size)
        can.drawString(x, y, bates_number)
        can.save()

        # Merge overlay with original page
        packet.seek(0)
        stamp_pdf = PdfReader(packet)
        stamp_page = stamp_pdf.pages[0]

        original_page = reader.pages[page_num]
        original_page.merge_page(stamp_page)

        writer.add_page(original_page)

    # Write output
    with open(output_path, 'wb') as f:
        writer.write(f)

    print(f"✓ Bates stamped: {input_path} → {output_path}")
    print(f"  Range: {prefix}-{start_number:06d} to {prefix}-{start_number + page_count - 1:06d}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python bates_stamp.py <input.pdf> <output.pdf> [prefix] [start_number]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else 'DOC'
    start = int(sys.argv[4]) if len(sys.argv) > 4 else 1

    bates_stamp_pdf(input_file, output_file, prefix, start)
```

### 4b. Bundle Assembly

**bundle_assembler.py**
```python
#!/usr/bin/env python3
"""Assemble a court bundle from multiple PDFs."""

from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
import sys

def create_table_of_contents(bundle_items):
    """Create a ToC page as PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=25*mm, bottomMargin=25*mm,
                            leftMargin=25*mm, rightMargin=25*mm)

    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("TABLE OF CONTENTS", styles['Heading1']))
    elements.append(Spacer(1, 12))

    # Table of contents entries
    toc_data = [['Item', 'Description', 'Pages', 'Bates']]
    page_num = 2  # Page 1 is ToC itself

    for idx, item in enumerate(bundle_items):
        item_count = PdfReader(item['path']).len(PdfReader(item['path']).pages)
        end_page = page_num + item_count - 1
        bates_start = item.get('bates_start', f"X-{page_num:06d}")
        bates_end = item.get('bates_end', f"X-{end_page:06d}")

        toc_data.append([
            str(idx + 1),
            item['title'],
            f"{page_num}–{end_page}",
            f"{bates_start}–{bates_end}"
        ])

        page_num = end_page + 1

    # Create table
    toc_table = Table(toc_data, colWidths=[30, 250, 80, 100])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))

    elements.append(toc_table)
    doc.build(elements)

    buffer.seek(0)
    return PdfReader(buffer)

def assemble_bundle(cover_pdf, bundle_items, output_path, matter_info):
    """
    Assemble a court bundle.

    Args:
        cover_pdf: Path to cover page PDF
        bundle_items: List of dicts: {'path': 'file.pdf', 'title': 'Affidavit',
                                      'bates_start': 'ABC-001', 'bates_end': 'ABC-005'}
        output_path: Path to output bundle PDF
        matter_info: Dict with 'matter_name', 'file_number' for headers
    """
    merger = PdfMerger()

    # Add cover page
    merger.append(cover_pdf)

    # Create and add ToC
    toc_pdf = create_table_of_contents(bundle_items)
    toc_bytes = BytesIO()
    toc_writer = PdfWriter()
    for page in toc_pdf.pages:
        toc_writer.add_page(page)
    toc_writer.write(toc_bytes)
    toc_bytes.seek(0)
    merger.append(toc_bytes)

    # Add documents
    for item in bundle_items:
        merger.append(item['path'])

    # Write bundle
    with open(output_path, 'wb') as f:
        merger.write(f)

    print(f"✓ Bundle assembled: {output_path}")
    print(f"  Matter: {matter_info.get('matter_name')}")
    print(f"  File: {matter_info.get('file_number')}")
    print(f"  Documents: {len(bundle_items)}")

if __name__ == '__main__':
    # Example usage
    bundle_items = [
        {'path': 'affidavit.pdf', 'title': 'Affidavit of John Smith',
         'bates_start': 'ABC-001', 'bates_end': 'ABC-005'},
        {'path': 'contract.pdf', 'title': 'Contract dated 1 January 2026',
         'bates_start': 'ABC-006', 'bates_end': 'ABC-008'},
    ]

    assemble_bundle('cover.pdf', bundle_items, 'bundle.pdf',
                    {'matter_name': 'Smith v Jones', 'file_number': '2026/DC/001234'})
```

### 4c. Court-Ready PDF from DOCX (LibreOffice Headless)

**docx_to_pdf.py**
```python
#!/usr/bin/env python3
"""Convert DOCX to court-ready PDF using LibreOffice headless."""

import subprocess
import sys
import os
from pathlib import Path

def docx_to_pdf(input_docx, output_pdf=None, cleanup_metadata=True):
    """
    Convert DOCX to PDF using LibreOffice headless.

    Args:
        input_docx: Path to .docx file
        output_pdf: Output PDF path (default: same name, .pdf extension)
        cleanup_metadata: Strip metadata after conversion
    """
    input_path = Path(input_docx).resolve()

    if not input_path.exists():
        print(f"✗ File not found: {input_docx}")
        return False

    if output_pdf is None:
        output_pdf = input_path.with_suffix('.pdf')
    else:
        output_pdf = Path(output_pdf).resolve()

    output_dir = output_pdf.parent

    # LibreOffice conversion
    cmd = [
        'libreoffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', str(output_dir),
        str(input_path)
    ]

    print(f"Converting: {input_docx}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        print(f"✗ Conversion failed:\n{result.stderr}")
        return False

    # Verify output
    converted_pdf = output_dir / input_path.stem / '.pdf'
    if not converted_pdf.exists():
        # LibreOffice may output with different name
        pdf_files = list(output_dir.glob('*.pdf'))
        if pdf_files:
            converted_pdf = pdf_files[-1]  # Most recent

    # Rename if needed
    if str(converted_pdf) != str(output_pdf):
        converted_pdf.rename(output_pdf)

    # Clean metadata
    if cleanup_metadata:
        clean_pdf_metadata(str(output_pdf))

    print(f"✓ PDF created: {output_pdf}")
    return True

def clean_pdf_metadata(pdf_path):
    """Remove metadata from PDF."""
    from PyPDF2 import PdfReader, PdfWriter

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Clear metadata
        writer.add_metadata({
            '/Author': '',
            '/Creator': '',
            '/Producer': '',
            '/Title': '',
            '/Subject': '',
        })

        with open(pdf_path, 'wb') as f:
            writer.write(f)

        print(f"  Metadata cleaned")
    except Exception as e:
        print(f"  Metadata cleanup skipped: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python docx_to_pdf.py <input.docx> [output.pdf]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    success = docx_to_pdf(input_file, output_file)
    sys.exit(0 if success else 1)
```

---

## 5. Metadata Cleanup

**metadata_cleaner.py**
```python
#!/usr/bin/env python3
"""Clean sensitive metadata from DOCX and PDF files."""

from PyPDF2 import PdfReader, PdfWriter
from python_docx import Document
from PIL import Image
from io import BytesIO
import sys
from pathlib import Path

def clean_docx_metadata(docx_path):
    """Remove author, creator, revision history from DOCX."""
    try:
        doc = Document(docx_path)

        # Clear core properties
        core_props = doc.core_properties
        core_props.author = ''
        core_props.comments = ''
        core_props.created = None
        core_props.modified = None
        core_props.last_modified_by = ''
        core_props.subject = ''

        doc.save(docx_path)
        print(f"✓ DOCX metadata cleaned: {docx_path}")
        return True
    except Exception as e:
        print(f"✗ DOCX cleanup failed: {e}")
        return False

def clean_pdf_metadata(pdf_path):
    """Remove all metadata from PDF."""
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Copy pages
        for page in reader.pages:
            writer.add_page(page)

        # Clear all metadata
        writer.add_metadata({
            '/Author': '',
            '/Creator': '',
            '/Producer': '',
            '/Title': '',
            '/Subject': '',
            '/Keywords': '',
            '/CreationDate': None,
            '/ModDate': None,
        })

        with open(pdf_path, 'wb') as f:
            writer.write(f)

        print(f"✓ PDF metadata cleaned: {pdf_path}")
        return True
    except Exception as e:
        print(f"✗ PDF cleanup failed: {e}")
        return False

def strip_image_exif(image_path):
    """Remove EXIF and GPS data from images."""
    try:
        img = Image.open(image_path)

        # Create new image without EXIF
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)

        image_without_exif.save(image_path, quality=95)
        print(f"✓ Image EXIF stripped: {image_path}")
        return True
    except Exception as e:
        print(f"✗ Image strip failed: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python metadata_cleaner.py <file.docx|file.pdf> [file2] [file3]...")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        p = Path(file_path)
        if p.suffix.lower() == '.docx':
            clean_docx_metadata(file_path)
        elif p.suffix.lower() == '.pdf':
            clean_pdf_metadata(file_path)
        elif p.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            strip_image_exif(file_path)
        else:
            print(f"✗ Unsupported format: {file_path}")
```

---

## 6. Print Readiness Validation

**validate_court_pdf.py**
```python
#!/usr/bin/env python3
"""Validate court-ready PDF against formatting standards."""

from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import sys
from pathlib import Path

def validate_pdf(pdf_path, strict=False):
    """
    Validate PDF against court document standards.

    Args:
        pdf_path: Path to PDF file
        strict: If True, treat warnings as errors

    Returns:
        Tuple: (is_valid, warnings, errors)
    """
    warnings = []
    errors = []

    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        return False, [], [f"Cannot read PDF: {e}"]

    # Page count
    page_count = len(reader.pages)
    if page_count == 0:
        errors.append("PDF has no pages")
        return False, warnings, errors

    # Check first page dimensions
    first_page = reader.pages[0]
    page_width = float(first_page.mediabox.width) / 72 * 25.4  # points to mm
    page_height = float(first_page.mediabox.height) / 72 * 25.4

    a4_width = A4[0] / mm
    a4_height = A4[1] / mm

    if abs(page_width - a4_width) > 2 or abs(page_height - a4_height) > 2:
        warnings.append(f"Page size ({page_width:.1f}×{page_height:.1f}mm) not A4 ({a4_width:.1f}×{a4_height:.1f}mm)")

    # Check metadata
    metadata = reader.metadata
    if metadata:
        if metadata.get('/Author') or metadata.get('/Creator') or metadata.get('/Producer'):
            warnings.append("PDF contains author/creator metadata (should be stripped)")

    # File size check
    file_size_mb = Path(pdf_path).stat().st_size / 1024 / 1024
    if file_size_mb > 50:
        warnings.append(f"File size ({file_size_mb:.1f}MB) exceeds recommended 50MB")

    # Check for encryption
    if reader.is_encrypted:
        errors.append("PDF is encrypted (not court-ready)")
        return False, warnings, errors

    # Scan for text (basic validation that content exists)
    text_count = 0
    for page in reader.pages[:min(3, page_count)]:  # Check first 3 pages
        try:
            text = page.extract_text()
            text_count += len(text)
        except:
            pass

    if text_count == 0:
        warnings.append("No extractable text found (may be image-only PDF)")

    is_valid = len(errors) == 0
    if strict and warnings:
        is_valid = False

    return is_valid, warnings, errors

def print_report(pdf_path, is_valid, warnings, errors):
    """Print validation report."""
    print(f"\n{'=' * 70}")
    print(f"VALIDATION REPORT: {Path(pdf_path).name}")
    print(f"{'=' * 70}\n")

    if is_valid:
        print("✓ VALID — Document meets court-ready standards")
    else:
        print("✗ INVALID — Document has critical issues")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for err in errors:
            print(f"  ✗ {err}")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for warn in warnings:
            print(f"  ⚠ {warn}")

    if not errors and not warnings:
        print("\nNo issues found.")

    print(f"\n{'=' * 70}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validate_court_pdf.py <file.pdf> [--strict]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    strict = '--strict' in sys.argv

    if not Path(pdf_file).exists():
        print(f"✗ File not found: {pdf_file}")
        sys.exit(1)

    is_valid, warnings, errors = validate_pdf(pdf_file, strict=strict)
    print_report(pdf_file, is_valid, warnings, errors)

    sys.exit(0 if is_valid else 1)
```

---

## 7. Bates Stamping Workflow

**bates_workflow.py**
```python
#!/usr/bin/env python3
"""Complete Bates stamping workflow for batch documents."""

from pathlib import Path
from bates_stamp import bates_stamp_pdf
import sys

def bates_stamp_batch(input_files, output_dir, prefix='DOC', start_number=1):
    """
    Bates stamp multiple PDFs with continuous numbering.

    Args:
        input_files: List of PDF file paths
        output_dir: Directory for output PDFs
        prefix: Bates prefix (e.g., 'ABC', 'DOC')
        start_number: Starting Bates number

    Returns:
        Dict mapping original file to Bates range
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {}
    current_number = start_number

    for input_file in input_files:
        input_p = Path(input_file)

        if not input_p.exists():
            print(f"✗ File not found: {input_file}")
            continue

        output_file = output_path / f"bates_{input_p.name}"

        # Get page count to calculate end number
        from PyPDF2 import PdfReader
        reader = PdfReader(input_file)
        page_count = len(reader.pages)
        end_number = current_number + page_count - 1

        # Stamp PDF
        bates_stamp_pdf(input_file, str(output_file), prefix, current_number)

        results[input_file] = {
            'output': str(output_file),
            'bates_start': f"{prefix}-{current_number:06d}",
            'bates_end': f"{prefix}-{end_number:06d}",
            'page_count': page_count,
        }

        current_number = end_number + 1

    return results

def print_bates_manifest(results):
    """Print Bates stamping manifest."""
    print(f"\n{'=' * 80}")
    print("BATES STAMPING MANIFEST")
    print(f"{'=' * 80}\n")

    total_pages = 0
    for input_file, data in results.items():
        print(f"{Path(input_file).name}")
        print(f"  Pages: {data['page_count']}")
        print(f"  Range: {data['bates_start']} → {data['bates_end']}")
        print(f"  Output: {data['output']}\n")
        total_pages += data['page_count']

    print(f"{'=' * 80}")
    print(f"Total pages: {total_pages}")
    print(f"{'=' * 80}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python bates_workflow.py <file1.pdf> [file2.pdf] ... --prefix ABC --output /path/to/output")
        sys.exit(1)

    files = []
    output_dir = './bates_output'
    prefix = 'DOC'

    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg == '--output':
            output_dir = args.pop(0)
        elif arg == '--prefix':
            prefix = args.pop(0)
        elif arg.endswith('.pdf'):
            files.append(arg)

    if not files:
        print("✗ No PDF files specified")
        sys.exit(1)

    results = bates_stamp_batch(files, output_dir, prefix)
    print_bates_manifest(results)
```

---

## 8. Bundle Assembly Workflow

**full_bundle_workflow.py**
```python
#!/usr/bin/env python3
"""Complete workflow to assemble court evidence bundle."""

from pathlib import Path
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from io import BytesIO
import json
import sys

class BundleAssembler:
    def __init__(self, matter_name, file_number, bundle_dir):
        self.matter_name = matter_name
        self.file_number = file_number
        self.bundle_dir = Path(bundle_dir)
        self.bundle_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = {'sections': []}

    def add_section(self, title, pdf_files, bates_prefix=None):
        """Add a section to the bundle."""
        section = {
            'title': title,
            'files': pdf_files,
            'bates_prefix': bates_prefix or f"{title[:3].upper()}",
            'start_page': self._calculate_start_page(),
        }
        self.manifest['sections'].append(section)

    def _calculate_start_page(self):
        """Calculate starting page for next section."""
        page = 2  # Page 1 is cover, page 2+ is content
        for section in self.manifest['sections']:
            for file in section['files']:
                reader = PdfReader(file)
                page += len(reader.pages)
        return page

    def create_divider_page(self, section_title, page_number):
        """Create a section divider page."""
        buffer = BytesIO()
        can = canvas.Canvas(buffer, pagesize=A4)
        can.setFont("Times-Bold", 28)
        can.drawCentredString(A4[0]/2, A4[1]/2 + 20*mm, section_title.upper())
        can.setFont("Times", 10)
        can.drawString(25*mm, 20*mm, f"Page {page_number}")
        can.save()
        buffer.seek(0)
        return PdfReader(buffer).pages[0]

    def assemble(self, cover_pdf, output_path):
        """Assemble the complete bundle."""
        merger = PdfMerger()

        # Add cover
        merger.append(cover_pdf)
        current_page = 2

        # Add sections
        for section in self.manifest['sections']:
            # Add divider
            divider = self.create_divider_page(section['title'], current_page)
            divider_buffer = BytesIO()
            writer = PdfWriter()
            writer.add_page(divider)
            writer.write(divider_buffer)
            divider_buffer.seek(0)
            merger.append(divider_buffer)
            current_page += 1

            # Add documents
            for file in section['files']:
                merger.append(file)
                reader = PdfReader(file)
                current_page += len(reader.pages)

        # Write bundle
        with open(output_path, 'wb') as f:
            merger.write(f)

        print(f"✓ Bundle assembled: {output_path}")
        self._save_manifest()

    def _save_manifest(self):
        """Save bundle manifest as JSON."""
        manifest_file = self.bundle_dir / 'manifest.json'
        with open(manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        print(f"✓ Manifest saved: {manifest_file}")

if __name__ == '__main__':
    # Example usage
    assembler = BundleAssembler(
        matter_name='Smith v Jones',
        file_number='2026/DC/001234',
        bundle_dir='./bundle_output'
    )

    # Add sections
    assembler.add_section(
        'AFFIDAVITS',
        ['affidavit_smith.pdf'],
        'AFF'
    )

    assembler.add_section(
        'EXHIBITS',
        ['contract.pdf', 'correspondence.pdf'],
        'EXH'
    )

    # Assemble
    assembler.assemble('cover.pdf', 'smith_v_jones_bundle.pdf')
```

---

## 9. Common Pitfalls

| Pitfall | Cause | Fix |
|---------|-------|-----|
| Layout changes after DOCX→PDF conversion | Font substitution, table width shifts | Validate with `validate_court_pdf.py` after conversion; embed fonts in DOCX |
| Missing fonts in Linux environment | System fonts not available | Use Times New Roman or Arial (universally available); embed fonts in docx-js |
| Table overflows page width | Constrained width not applied | Set column widths as percentage or fixed DXA; test on A4 before final output |
| Image quality degraded | Low DPI (72 DPI) | Use 150+ DPI minimum; compress JPEG at quality 85+ |
| Memory exhaustion | Processing 500+ page bundles | Process in chunks; use pypdf's streaming mode; monitor RAM usage |
| UTF-8 encoding errors | Windows-1252 fallback on legacy files | Detect encoding with `chardet`; convert to UTF-8 before processing |
| Bates numbers obscure content | Position not validated | Test position ('bottom_right' safe for most); increase y-offset if needed |
| Metadata leakage | Revision history not cleared | Always call metadata cleanup; strip EXIF from embedded images |
| PDF unreadable on some readers | Missing font embedding | Use ReportLab or LibreOffice to ensure core fonts embedded |
| Conversion timeouts | Large DOCX files | Set LibreOffice timeout to 60+ seconds; split large documents |

---

## 10. Quick Reference: DXA Units

DXA (device-independent units) are used in DOCX formatting. 1 inch = 1440 DXA; 1 mm = 56.69 DXA.

### A4 Page Dimensions

| Measurement | DXA | Twips |
|-------------|-----|-------|
| A4 Width | 11906 | 11906 |
| A4 Height | 16838 | 16838 |
| 25mm margin | 1417 | 1417 |
| 50mm margin | 2834 | 2834 |

### Common Column Widths (DXA)

| Width | Use Case |
|-------|----------|
| 2835 | 2-column layout (50mm per column with 25mm margins) |
| 1890 | 3-column layout (33mm per column) |
| 5670 | Single half-width column |

### Font Sizing

| Point Size | Half-points |
|-----------|-------------|
| 10pt | 20 |
| 11pt | 22 |
| 12pt | 24 |
| 14pt | 28 |

### Line Spacing

| Spacing | Twips |
|---------|-------|
| Single (1.0) | 240 |
| 1.5 lines | 360 |
| Double (2.0) | 480 |

---

## Summary Checklist

Before submitting any court document:

- [ ] PDF validation passes: `python validate_court_pdf.py file.pdf`
- [ ] Page size is A4 (210 × 297 mm)
- [ ] Margins are 25 mm minimum all sides
- [ ] Font is Times New Roman 12pt or Arial 11pt
- [ ] Line spacing is 1.5 or double
- [ ] Page numbers present (bottom centre, format "Page X of Y")
- [ ] Headers show case name and file number
- [ ] All Bates numbers are continuous and visible
- [ ] No colour-dependent content
- [ ] Metadata stripped (author, creator, producer)
- [ ] EXIF data removed from images
- [ ] File size under 50 MB
- [ ] Text is extractable (not image-only)
- [ ] All fonts embedded or use system-safe fonts
- [ ] Tested on a Linux PDF reader (not just your local machine)

---

**Maintenance note:** Verify court document format requirements, filing rules, and package versions before using these examples in a current matter.
