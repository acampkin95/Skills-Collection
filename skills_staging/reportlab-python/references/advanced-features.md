# ReportLab — Advanced Features

## Charts (ReportLab Graphics)

ReportLab includes a charting library that renders directly to PDF without external dependencies.

### Bar chart

```python
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor

drawing = Drawing(400, 200)
chart = VerticalBarChart()
chart.x = 50
chart.y = 30
chart.width = 300
chart.height = 150
chart.data = [
    (45, 52, 61, 48, 55),   # series 1
    (32, 41, 38, 45, 50),   # series 2
]
chart.categoryAxis.categoryNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
chart.bars[0].fillColor = HexColor('#4A90D9')
chart.bars[1].fillColor = HexColor('#E74C3C')
chart.valueAxis.valueMin = 0
chart.valueAxis.valueMax = 70
chart.valueAxis.valueStep = 10

drawing.add(chart)
# Add to Platypus story or render directly
story.append(drawing)
```

### Pie chart

```python
from reportlab.graphics.charts.piecharts import Pie

drawing = Drawing(300, 200)
pie = Pie()
pie.x = 50
pie.y = 20
pie.width = 150
pie.height = 150
pie.data = [35, 25, 20, 15, 5]
pie.labels = ['Product A', 'Product B', 'Product C', 'Product D', 'Other']
pie.slices[0].fillColor = HexColor('#4A90D9')
pie.slices[1].fillColor = HexColor('#E74C3C')
pie.slices[2].fillColor = HexColor('#2ECC71')
pie.slices[3].fillColor = HexColor('#F39C12')
pie.slices[4].fillColor = HexColor('#95A5A6')

drawing.add(pie)
story.append(drawing)
```

### Line chart

```python
from reportlab.graphics.charts.linecharts import HorizontalLineChart

drawing = Drawing(400, 200)
chart = HorizontalLineChart()
chart.x = 50
chart.y = 30
chart.width = 300
chart.height = 150
chart.data = [
    (12, 18, 22, 28, 35, 42),
    (8, 15, 20, 25, 30, 38),
]
chart.categoryAxis.categoryNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
chart.lines[0].strokeColor = HexColor('#4A90D9')
chart.lines[0].strokeWidth = 2
chart.lines[1].strokeColor = HexColor('#E74C3C')
chart.lines[1].strokeWidth = 2

drawing.add(chart)
story.append(drawing)
```

## Barcodes

```python
from reportlab.graphics.barcode import code128, qr

# Code 128 barcode
barcode = code128.Code128('ABC-12345', barWidth=0.5*mm, barHeight=15*mm)
story.append(barcode)

# QR code
qr_code = qr.QrCodeWidget('https://example.com')
qr_code.barWidth = 5*cm
qr_code.barHeight = 5*cm

from reportlab.graphics.shapes import Drawing
d = Drawing(5*cm, 5*cm)
d.add(qr_code)
story.append(d)
```

## Multi-column layouts

```python
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

# Two-column layout
frame_left = Frame(
    2*cm, 2*cm,
    8*cm, A4[1] - 4*cm,
    id='left',
)
frame_right = Frame(
    11*cm, 2*cm,
    8*cm, A4[1] - 4*cm,
    id='right',
)

doc = BaseDocTemplate('twocol.pdf', pagesize=A4)
doc.addPageTemplates([
    PageTemplate(id='TwoColumn', frames=[frame_left, frame_right]),
])
```

Content flows from the left frame into the right frame automatically.

## Watermarks

```python
def add_watermark(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 60)
    canvas.setFillColor(HexColor('#EEEEEE'))
    canvas.translate(A4[0] / 2, A4[1] / 2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, 'DRAFT')
    canvas.restoreState()

doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
```

## Custom flowables

Create reusable layout components by subclassing `Flowable`:

```python
from reportlab.platypus import Flowable

class HorizontalRule(Flowable):
    def __init__(self, width, thickness=0.5, color='#CCCCCC'):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = HexColor(color)
        self.height = thickness + 4  # include spacing

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 2, self.width, 2)


class InfoBox(Flowable):
    """A coloured box with a title and body text."""
    def __init__(self, title, body, width=15*cm, bg_color='#EBF5FB'):
        Flowable.__init__(self)
        self.title = title
        self.body = body
        self.box_width = width
        self.bg_color = HexColor(bg_color)
        self.height = 60  # approximate, adjust as needed

    def draw(self):
        self.canv.setFillColor(self.bg_color)
        self.canv.roundRect(0, 0, self.box_width, self.height, 4, fill=True, stroke=False)
        self.canv.setFillColor(black)
        self.canv.setFont('Helvetica-Bold', 10)
        self.canv.drawString(8, self.height - 16, self.title)
        self.canv.setFont('Helvetica', 9)
        self.canv.drawString(8, self.height - 32, self.body)
```

## Table of contents

```python
from reportlab.platypus import TableOfContents

toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle(name='TOC1', fontSize=12, leading=16,
                   leftIndent=20, spaceBefore=5),
    ParagraphStyle(name='TOC2', fontSize=10, leading=14,
                   leftIndent=40, spaceBefore=2),
]

story.append(toc)
story.append(PageBreak())

# Headings that appear in the TOC must use doc.notify()
class HeadingFlowable(Paragraph):
    """A paragraph that registers with the TOC."""
    def __init__(self, text, style, level=0):
        Paragraph.__init__(self, text, style)
        self.toc_level = level
        self.toc_text = text

    def draw(self):
        Paragraph.draw(self)

# Or use the built-in mechanism:
story.append(Paragraph('Chapter 1', styles['Heading1']))
# The doc.multiBuild() method handles TOC generation
doc.multiBuild(story)
```

## Performance for large documents

- Use `SimpleDocTemplate` for most cases — `BaseDocTemplate` adds overhead
- For >500 pages, avoid storing all flowables in memory; build in chunks
- Pre-compute table data outside the flowable loop
- Use `canvas.beginForm()` / `endForm()` for repeated graphics (logos, watermarks)
- `multiBuild()` is slower than `build()` — only use when you need TOC or cross-references
