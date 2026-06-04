---

## Parent router

This skill is a leaf of the [pdf-generation](../pdf-generation/SKILL.md) master router.
name: reportlab-python
description: Python PDF generation with ReportLab — Canvas (low-level drawing) and Platypus (high-level document layout with flowables). Use when ReportLab, SimpleDocTemplate, Paragraph, Table, canvas.drawString, platypus flowables, PDF in Python.
---

# ReportLab — Python PDF Generation Skill

ReportLab is Python's most established PDF generation library. It operates at two levels: the low-level **Canvas** for precise drawing control, and the high-level **Platypus** framework for document layout with automatic pagination.

## Installation context

ReportLab is installed via pipx (`pipx install reportlab --include-deps`). For project use, install in a virtualenv: `pip install reportlab`. The library is pure Python with optional C extensions for speed.

## Architecture: Canvas vs Platypus

Choose based on what you're building:

| Use Canvas when... | Use Platypus when... |
|----|----|
| Precise coordinate control needed | Content should flow and paginate automatically |
| Drawing charts, diagrams, labels | Reports, invoices, letters, manuals |
| Single-page outputs (certificates, cards) | Multi-page documents with consistent layout |
| Overlaying on existing coordinates | Tables, paragraphs, images that reflow |

Most real documents use **Platypus** — it handles pagination, headers/footers, and content reflow. Drop to Canvas only when you need pixel-perfect positioning.

## Platypus — high-level document creation

### Basic document

```python
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm, inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

doc = SimpleDocTemplate(
    'output.pdf',
    pagesize=A4,
    topMargin=2*cm,
    bottomMargin=2*cm,
    leftMargin=2.5*cm,
    rightMargin=2.5*cm,
    title='Document Title',
    author='Author Name',
)

styles = getSampleStyleSheet()
story = []

story.append(Paragraph('Report Title', styles['Title']))
story.append(Spacer(1, 12))
story.append(Paragraph('This is the first paragraph of the report.', styles['Normal']))

doc.build(story)
```

### Paragraph styles

The sample stylesheet gives you `Title`, `Heading1`–`Heading6`, `Normal`, `BodyText`, `Italic`, `Code`, `Bullet`, and `Definition`. Customise or create new ones:

```python
styles = getSampleStyleSheet()

# Modify existing
styles['Normal'].fontSize = 10
styles['Normal'].leading = 14  # line height in points

# Create new style
styles.add(ParagraphStyle(
    name='CustomBody',
    parent=styles['Normal'],
    fontSize=11,
    leading=16,
    textColor=HexColor('#333333'),
    alignment=TA_JUSTIFY,
    spaceAfter=8,
    spaceBefore=4,
    firstLineIndent=0,
))
```

### Rich text in paragraphs

Paragraphs accept a subset of HTML for inline formatting:

```python
Paragraph(
    'This is <b>bold</b>, <i>italic</i>, and <u>underlined</u>. '
    'Use <font color="red">colour</font> and <font size="14">size</font>. '
    'Links: <a href="https://example.com">click here</a>. '
    'Line break:<br/> New line starts here.',
    styles['Normal']
)
```

Supported tags: `<b>`, `<i>`, `<u>`, `<strike>`, `<font>` (with `color`, `size`, `face`), `<a>`, `<br/>`, `<super>`, `<sub>`, `<img>`.

### Tables

Tables are the workhorse of most ReportLab documents.

```python
data = [
    ['Name', 'Role', 'Location'],
    ['Alex', 'Architect', 'Perth'],
    ['Sam', 'Developer', 'Melbourne'],
    ['Jordan', 'Designer', 'Sydney'],
]

table = Table(data, colWidths=[5*cm, 5*cm, 5*cm])
table.setStyle(TableStyle([
    # Header row
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4A90D9')),
    ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

    # Data rows
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 1), (-1, -1), 10),
    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),

    # Alternating row colours
    ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F9F9F9')),
    ('BACKGROUND', (0, 2), (-1, 2), white),
    ('BACKGROUND', (0, 4), (-1, 4), white),  # pattern continues

    # Grid
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#DDDDDD')),
    ('LINEBELOW', (0, 0), (-1, 0), 1, HexColor('#4A90D9')),

    # Padding
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
]))

story.append(table)
```

### TableStyle coordinate system

Coordinates are `(col, row)` with `(0, 0)` at top-left. Negative indices work: `(-1, -1)` is bottom-right.

Common style commands:
- `BACKGROUND`, `TEXTCOLOR`, `FONTNAME`, `FONTSIZE`, `ALIGN`, `VALIGN`
- `GRID`, `BOX`, `LINEABOVE`, `LINEBELOW`, `LINEBEFORE`, `LINEAFTER`
- `TOPPADDING`, `BOTTOMPADDING`, `LEFTPADDING`, `RIGHTPADDING`
- `SPAN` — merge cells: `('SPAN', (0, 0), (2, 0))` merges columns 0–2 in row 0

### Paragraphs inside table cells

For text that needs to wrap within cells, use Paragraph objects instead of plain strings:

```python
data = [
    [Paragraph('<b>Description</b>', styles['Normal']),
     Paragraph('<b>Amount</b>', styles['Normal'])],
    [Paragraph('A long description that will wrap within the cell boundaries.', styles['Normal']),
     Paragraph('$1,250.00', styles['Normal'])],
]
```

### Images

```python
from reportlab.platypus import Image

# Basic image (auto-sized)
story.append(Image('logo.png'))

# Constrained dimensions
story.append(Image('chart.png', width=15*cm, height=10*cm))

# From buffer
from io import BytesIO
img_buffer = BytesIO(image_bytes)
story.append(Image(img_buffer, width=10*cm, height=8*cm))
```

### Page breaks and spacers

```python
from reportlab.platypus import PageBreak, Spacer, KeepTogether

story.append(PageBreak())                    # force new page
story.append(Spacer(1, 2*cm))               # vertical space
story.append(KeepTogether([para1, para2]))   # prevent page break between these
```

### Headers and footers

Use callback functions with `onFirstPage` and `onLaterPages`:

```python
def header_footer(canvas, doc):
    canvas.saveState()

    # Header
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(HexColor('#999999'))
    canvas.drawString(doc.leftMargin, A4[1] - 1.5*cm, 'Company Report')
    canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 1.5*cm,
                           f'Page {doc.page}')

    # Header line
    canvas.setStrokeColor(HexColor('#CCCCCC'))
    canvas.line(doc.leftMargin, A4[1] - 1.8*cm,
                A4[0] - doc.rightMargin, A4[1] - 1.8*cm)

    # Footer
    canvas.drawCentredString(A4[0] / 2, 1.5*cm, 'Confidential')

    canvas.restoreState()

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
```

### Page templates (advanced layouts)

For documents with different layouts per section (e.g. cover page vs content pages):

```python
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, NextPageTemplate

frame_cover = Frame(0, 0, A4[0], A4[1], id='cover')
frame_content = Frame(2.5*cm, 2*cm, A4[0]-5*cm, A4[1]-4*cm, id='content')

doc = BaseDocTemplate('output.pdf', pagesize=A4)
doc.addPageTemplates([
    PageTemplate(id='Cover', frames=[frame_cover], onPage=cover_page_bg),
    PageTemplate(id='Content', frames=[frame_content], onPage=header_footer),
])

story = []
story.append(Paragraph('Cover Page Title', styles['Title']))
story.append(NextPageTemplate('Content'))
story.append(PageBreak())
story.append(Paragraph('Content starts here.', styles['Normal']))

doc.build(story)
```

## Canvas — low-level drawing

For precise coordinate control. Origin is bottom-left corner.

```python
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor

c = Canvas('drawing.pdf', pagesize=A4)
width, height = A4

# Text
c.setFont('Helvetica-Bold', 24)
c.drawString(2*cm, height - 3*cm, 'Title Text')

# Right-aligned text
c.drawRightString(width - 2*cm, height - 3*cm, 'Right aligned')

# Centred text
c.drawCentredString(width / 2, height - 5*cm, 'Centred text')

# Shapes
c.setFillColor(HexColor('#4A90D9'))
c.rect(2*cm, height - 10*cm, 8*cm, 3*cm, fill=True, stroke=False)

c.setStrokeColor(HexColor('#E74C3C'))
c.setLineWidth(2)
c.circle(width/2, height/2, 3*cm, fill=False, stroke=True)

c.line(2*cm, 5*cm, width - 2*cm, 5*cm)

# Image
c.drawImage('logo.png', 2*cm, height - 4*cm, width=3*cm, height=3*cm,
            preserveAspectRatio=True, mask='auto')

# Save (required — nothing writes without this)
c.save()
```

### Multi-page canvas documents

```python
c = Canvas('multi.pdf', pagesize=A4)

# Page 1
c.drawString(100, 700, 'Page 1 content')
c.showPage()  # finish this page, start next

# Page 2
c.drawString(100, 700, 'Page 2 content')
c.showPage()

c.save()
```

## Common patterns

### Data-driven report

```python
def build_report(data: list[dict], output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph('Monthly Report', styles['Title']))
    story.append(Spacer(1, 1*cm))

    # Summary stats
    total = sum(d['amount'] for d in data)
    story.append(Paragraph(f'Total: ${total:,.2f}', styles['Heading2']))
    story.append(Spacer(1, 0.5*cm))

    # Data table
    table_data = [['Date', 'Description', 'Amount']]
    for row in data:
        table_data.append([
            row['date'],
            Paragraph(row['description'], styles['Normal']),
            f"${row['amount']:,.2f}",
        ])

    table = Table(table_data, colWidths=[3*cm, 10*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4A90D9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#DDD')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
    ]))

    story.append(table)
    doc.build(story)
```

### Alternating row colours (helper)

```python
def alternating_rows(table_data, color_a='#F9F9F9', color_b='#FFFFFF'):
    """Generate TableStyle commands for alternating row backgrounds."""
    styles = []
    for i in range(1, len(table_data)):
        color = color_a if i % 2 == 1 else color_b
        styles.append(('BACKGROUND', (0, i), (-1, i), HexColor(color)))
    return styles
```

## Units reference

Always use explicit units rather than raw numbers:

```python
from reportlab.lib.units import mm, cm, inch
from reportlab.lib.pagesizes import A4, letter

# A4 = (595.276, 841.89) points
# 1 inch = 72 points
# 1 cm = 28.346 points
# 1 mm = 2.835 points
```

## When NOT to use ReportLab

- **PDF from a webpage** — use Puppeteer's `page.pdf()` instead
- **Editing existing PDFs** — use `pypdf` or `pikepdf` (ReportLab creates new docs)
- **Node.js project** — use PDFKit instead
- **Simple text extraction from PDF** — use `pdfplumber` or `pymupdf`

## Fonts

ReportLab includes the standard 14 PDF fonts (Helvetica, Times, Courier families + Symbol, ZapfDingbats). For custom fonts:

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('CustomFont', 'path/to/font.ttf'))
# Then use: c.setFont('CustomFont', 12) or in paragraph styles
```

## Reference

For charts (ReportLab Graphics/charts module), barcodes, and advanced page templates with multiple frames, see `references/advanced-features.md`.

## Legal/Document Skills (Cross-Reference)

When generating court documents, evidence bundles, or legal reports, use with:

| Related Skill | Use when |
|---------------|----------|
| `legal-matter-ops` | Generating print-ready court bundles, evidence reports, DOCX/PDF output |
| `csv-legal-analysis-v2` | Generating statistical analysis reports, evidence-grade PDFs |
| `affidavit-court-preparation` | Generating affidavit bundles, annexure indexes, hearing prep documents |
| `srl-case-file-manager-wa` | Generating dashboard reports, evidence indexes as PDF |
| `wa-law-general` | Generating general legal information documents |
| `pdfkit-node` | Node.js alternative for the same PDF generation tasks |
