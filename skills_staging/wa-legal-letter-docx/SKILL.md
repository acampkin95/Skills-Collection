---
name: wa-legal-letter-docx
description: Court-ready DOCX legal correspondence for WA residential tenancy and SRL matters. Use for formal letters, statutory citations, and demand tables.
compatibility: "node (docx npm package), Python 3"
version: 2.0.0
reviewed: "2026-06-04"
---

# WA Legal Letter — .docx Production Skill

Produces professional B&W .docx legal correspondence aligned with WA court
standards and the self-represented litigant (SRL) context. Built around the
`docx` npm package and the house style established for Velocity Digital's
legal matter work.

## House Style

| Element | Specification |
|---------|--------------|
| Font | Arial throughout |
| Body text | 10pt (size: 20 in docx units) |
| Section headings | 11pt bold, bottom rule, keepNext |
| Sub-headings | 10pt bold italic, keepNext |
| Bullet points | LevelFormat.BULLET — never unicode chars |
| Colour | B&W only — LGRAY `E8E8E8` for table headers, `CCCCCC` borders |
| Page size | A4 (11906 × 16838 DXA) |
| Margins | 0.75" top/bottom (1080 DXA), 0.875" left/right (1260 DXA) |
| Content width | 9386 DXA |
| Header | Document title left, matter reference right — separated by bottom rule |
| Footer | Address/date left, "Page X of Y" right — separated by top rule |
| Tables | `cantSplit: true` on every row — no mid-row page breaks |
| Spacing | `line: 276` (≈ 1.15×), `after: 100` default body paragraphs |

---

## Workflow

### 1. Read the source content

If the user uploads an existing `.docx`, extract it first:

```bash
extract-text /mnt/user-data/uploads/filename.docx
```

Identify every section, table, bullet list, and statutory citation present.

### 2. Apply legal review changes

Before writing code, map each recommended change to the section it affects.
For WA tenancy matters, common additions include:

- **Retaliatory action** — cite ss.26A–26B *RTA 1987* (as amended by *RTAA 2024*)
- **Bond exhaustive entitlements** — cite s.81E *RTA 1987* (inserted by *RTAA 2024*)
- **Premature bond release offence** — cite s.81C(3) and (5) *RTA 1987*
- **Prescribed form penalty** — $5,000 under s.27A *RTA 1987* (as amended)
- **Property manager joint liability** — s.86A *RTA 1987* (inserted by *RTAA 2024*)
- **Rent increase frequency** — 12 months minimum under s.30 (as amended)
- **No-grounds termination notice** — 60 days for periodic tenancy under s.64

All statutory statements must be factual and cite the precise section.
Never assert a legal conclusion without a citation.

### 3. Build the document

Use the bundled script as your base — see `scripts/build_letter.js`.
Adapt it to the specific matter: update parties, date, property address,
subject line, section content, and demand table rows.

```bash
cd /home/claude/<matter-folder>
npm install docx          # only needed first time
node build_letter.js
```

### 4. Validate

```bash
python3 -c "
import zipfile
with zipfile.ZipFile('output.docx') as z:
    xml = z.read('word/document.xml')
    print('Valid —', len(xml), 'bytes in document.xml')
"
```

If the ZIP check fails, the docx-js Packer threw silently — check for
uncaught Promise rejections by wrapping `.then()` in `.catch(e => { console.error(e); process.exit(1); })`.

### 5. Copy to outputs

```bash
cp output.docx /mnt/user-data/outputs/Matter_LetterName_vN.docx
```

Then call `present_files`.

---

## Key Patterns

### Section heading with bottom rule and keepNext

```javascript
function sectionHeading(num, text) {
  return new Paragraph({
    children: [new TextRun({ text: `${num}.  ${text}`, bold: true, size: 22, font: "Arial" })],
    spacing: { before: 260, after: 80, line: 276 },
    keepNext: true,
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 2 }
    },
  });
}
```

### Header (title left, reference right, bottom rule)

```javascript
const docHeader = new Header({
  children: [
    new Paragraph({
      children: [
        new TextRun({ text: "WITHOUT PREJUDICE SAVE AS TO COSTS", bold: true, size: 18, font: "Arial" }),
        new TextRun({ text: "\t" }),
        new TextRun({ text: "Matter Reference — Party Name", size: 16, font: "Arial", color: "555555" }),
      ],
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      spacing: { before: 0, after: 60 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 2 } },
    }),
  ],
});
```

### Footer (address left, page X of Y right, top rule)

```javascript
const docFooter = new Footer({
  children: [
    new Paragraph({
      children: [
        new TextRun({ text: "Address  |  Date", size: 16, font: "Arial", color: "555555" }),
        new TextRun({ text: "\t" }),
        new TextRun({ text: "Page ", size: 16, font: "Arial", color: "555555" }),
        new TextRun({ children: [PageNumber.CURRENT], size: 16, font: "Arial", color: "555555" }),
        new TextRun({ text: " of ", size: 16, font: "Arial", color: "555555" }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, font: "Arial", color: "555555" }),
      ],
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      spacing: { before: 60, after: 0 },
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 2 } },
    }),
  ],
});
```

### Demand / two-column table (no page splits)

```javascript
function twoColTable(rows, col1W, col2W, headerRow) {
  // headerRow = ["Heading 1", "Heading 2"] or null
  // rows = [["left cell text", "right cell text"], ...]
  // All rows have cantSplit: true
  // Header row uses LGRAY shading; body rows use WHITE
  // See scripts/build_letter.js for full implementation
}
```

### Bullets (never unicode)

```javascript
// Document-level numbering config (required):
numbering: {
  config: [{
    reference: "bullets",
    levels: [{
      level: 0,
      format: LevelFormat.BULLET,
      text: "\u2022",
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 540, hanging: 300 } } },
    }],
  }],
},

// Usage:
new Paragraph({
  children: [new TextRun({ text: "Bullet content", size: 20, font: "Arial" })],
  numbering: { reference: "bullets", level: 0 },
  spacing: { before: 40, after: 40, line: 276 },
})
```

---

## WA Statutory Reference (Current Law)

Quick reference for the most commonly cited provisions in tenancy disputes.
All citations are to the *Residential Tenancies Act 1987* (WA) as amended
by the *Residential Tenancies Amendment Act 2024* (No. 11 of 2024), assented
22 April 2024. Commencement by proclamation for most provisions.

| Issue | Section | Summary |
|-------|---------|---------|
| Prescribed form (Form 1AA) | s.27A | Approved form required; $5,000 penalty |
| Rent increase frequency | s.30 | Minimum 12 months between increases |
| Bond receipt and lodgement | s.29(3),(4)(b) | Receipt immediately; lodge within 14 days; $10,000 penalty |
| Security bond — lessor entitlements | s.81E | Exhaustive list: damage, cleaning, arrears, breach costs |
| Bond release application | s.81C | Not before termination; s.81C(5) $5,000 for premature compulsion |
| Periodic tenancy termination | s.64 | 60 days notice minimum |
| Retaliatory action | ss.26A–26B | Tenant may apply for set-aside order and compensation |
| Property manager joint liability | s.86A | Manager and lessor both liable for omissions |
| Quiet enjoyment | s.46 | Entry requires 7 days written notice (s.46(2)(b)) |
| Unlawful terms | s.54(2) | Void penalty clauses |
| Pets — consent and refusal | ss.50A–50I | Lessor must respond within 14 days; silence = approval |
| Minor modifications | ss.50N–50V | Lessor must respond within 14 days; silence = approval |

For FVRO matters, also read `/mnt/skills/user/wa-fvro/SKILL.md`.
For general WA court procedure, read `/mnt/skills/user/wa-law-general/SKILL.md`.

---

## Document Naming Convention

```
NN_DocumentType_Party_vN.docx

Examples:
  01_Formal_Response_to_Stojanovic_v4.docx
  02_DMIRS_Complaint_Bond_v1.docx
  03_MC_Application_Termination_v1.docx
```

Increment `vN` on each revision. Archive superseded versions in a
`/archive/` subfolder within the matter folder.

---

## Checklist Before Presenting

- [ ] All statutory citations include section number and Act name
- [ ] No statement of legal fact without a citation
- [ ] All table rows have `cantSplit: true`
- [ ] Header and footer present on all pages
- [ ] Page numbers render (PageNumber.CURRENT / TOTAL_PAGES)
- [ ] No colour used except structural greys (E8E8E8, CCCCCC, 555555)
- [ ] Bullets use `LevelFormat.BULLET` — not unicode characters
- [ ] Document validated as valid ZIP with word/document.xml present
- [ ] File saved to `/mnt/user-data/outputs/` and presented with `present_files`

## See also

- [legal-matter-ops](../legal-matter-ops/SKILL.md) — legal file operations and court-pack workflows
- [wa-legal](../wa-legal/SKILL.md) — master router for WA legal workflows
