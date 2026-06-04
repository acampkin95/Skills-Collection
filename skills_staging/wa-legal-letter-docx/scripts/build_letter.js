/**
 * build_letter.js — WA Legal Letter Template
 * ─────────────────────────────────────────────────────────────────────────
 * Reusable scaffold for producing B&W court-ready .docx correspondence.
 * Part of the wa-legal-letter-docx skill.
 *
 * USAGE:
 *   1. Copy this file into your matter folder
 *   2. Edit the MATTER CONFIG section below
 *   3. Replace the DOCUMENT BODY section with your letter content
 *   4. Run:  npm install docx && node build_letter.js
 *   5. Output lands at OUTPUT_PATH
 *
 * All house style (fonts, colours, margins, table patterns, header/footer)
 * is defined in the CONSTANTS and HELPERS sections — do not modify those
 * unless changing the style intentionally.
 */

'use strict';

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, BorderStyle, WidthType, ShadingType,
  PageNumber, TabStopType, TabStopPosition, LevelFormat,
} = require('docx');
const fs = require('fs');
const path = require('path');

// ════════════════════════════════════════════════════════════════════════════
// MATTER CONFIG — edit these for each document
// ════════════════════════════════════════════════════════════════════════════

const MATTER = {
  // Header
  privilege:    'WITHOUT PREJUDICE SAVE AS TO COSTS',
  headerRef:    'Matter Reference — Party Name',          // right side of header

  // Cover block
  senderName1:  'Alexander Campkin',
  senderName2:  'Sophia Antonia De Caprio',               // set '' to omit
  senderAddr1:  '29 Overdene Pass, Carramar',
  senderAddr2:  'Banksia Grove WA 6031',

  recipientTo:  'Snezana Stojanovic (also known as Todorovic)',
  recipientEmail: 'snez1@y7mail.com',
  date:         '8 May 2026',

  subject:      'Tenancy at 29 Overdene Pass — Subject Matter Here',

  // Footer
  footerAddress: '29 Overdene Pass, Carramar, Banksia Grove WA 6031',
  footerDate:   '8 May 2026',

  // Output
  outputPath:   path.join(__dirname, 'output.docx'),
};

// ════════════════════════════════════════════════════════════════════════════
// CONSTANTS — house style, do not edit unless changing style
// ════════════════════════════════════════════════════════════════════════════

const BLACK = '000000';
const WHITE = 'FFFFFF';
const LGRAY = 'E8E8E8'; // table header shading
const MGRAY = 'CCCCCC'; // ruled borders
const DGRAY = '555555'; // footer / secondary text

// A4 page geometry (DXA: 1440 = 1 inch)
const PAGE_W     = 11906;
const PAGE_H     = 16838;
const MARGIN_TB  = 1080;  // 0.75 inch
const MARGIN_LR  = 1260;  // 0.875 inch
const CONTENT_W  = PAGE_W - (MARGIN_LR * 2); // 9386 DXA

// Border presets
const thinBorder = { style: BorderStyle.SINGLE, size: 4, color: MGRAY };
const noBorder   = { style: BorderStyle.NONE,   size: 0, color: WHITE };
const allBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };

// ════════════════════════════════════════════════════════════════════════════
// HELPERS — building blocks
// ════════════════════════════════════════════════════════════════════════════

/** Plain run */
function r(text, size = 20, opts = {}) {
  return new TextRun({ text, size, font: 'Arial', color: BLACK, ...opts });
}
/** Bold run */
function rb(text, size = 20) {
  return new TextRun({ text, size, font: 'Arial', bold: true, color: BLACK });
}
/** Italic run */
function ri(text, size = 18) {
  return new TextRun({ text, size, font: 'Arial', italics: true, color: BLACK });
}
/** Grey run (for metadata / secondary text) */
function rg(text, size = 16) {
  return new TextRun({ text, size, font: 'Arial', color: DGRAY });
}

/**
 * Generic paragraph.
 * opts: before, after, line, align, keepNext, keepLines, indent, bottomBorder
 */
function para(runs, opts = {}) {
  const children = Array.isArray(runs) ? runs : [runs];
  return new Paragraph({
    children,
    spacing: {
      before: opts.before ?? 0,
      after:  opts.after  ?? 100,
      line:   opts.line   ?? 276,
    },
    alignment:  opts.align    ?? AlignmentType.LEFT,
    keepNext:   opts.keepNext ?? false,
    keepLines:  opts.keepLines ?? false,
    indent: opts.indent ? { left: opts.indent } : undefined,
    border: opts.bottomBorder ? {
      bottom: { style: BorderStyle.SINGLE, size: 6, color: MGRAY, space: 4 },
    } : undefined,
  });
}

/** Empty spacer paragraph */
function spacer(pts = 6) {
  return para([r('', pts * 2)], { before: 0, after: 0 });
}

/** Numbered section heading with bottom rule */
function sectionHeading(num, text) {
  return new Paragraph({
    children: [new TextRun({ text: `${num}.  ${text}`, bold: true, size: 22, font: 'Arial' })],
    spacing: { before: 260, after: 80, line: 276 },
    keepNext: true,
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 4, color: MGRAY, space: 2 },
    },
  });
}

/** Bold-italic sub-heading */
function subHeading(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, italics: true, size: 20, font: 'Arial' })],
    spacing: { before: 160, after: 60, line: 276 },
    keepNext: true,
  });
}

/** Bullet point (requires "bullets" numbering ref in Document config) */
function bullet(text) {
  return new Paragraph({
    children: [r(text)],
    numbering: { reference: 'bullets', level: 0 },
    spacing: { before: 40, after: 40, line: 276 },
  });
}

/**
 * Two-column table — demand/notice/summary tables.
 *
 * @param {Array<[string, string]>} rows   - [leftCell, rightCell] pairs
 * @param {number}  col1W                  - left column width in DXA
 * @param {number}  col2W                  - right column width in DXA (col1W + col2W = CONTENT_W)
 * @param {[string, string]|null} headerRow - header labels, or null
 * @param {boolean} col1Bold               - bold left column (default false)
 */
function twoColTable(rows, col1W, col2W, headerRow = null, col1Bold = false) {
  function makeCell(text, w, isHeader = false, bold = false) {
    return new TableCell({
      borders: allBorders,
      width: { size: w, type: WidthType.DXA },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      shading: {
        fill: isHeader ? LGRAY : WHITE,
        type: ShadingType.CLEAR,
      },
      children: [new Paragraph({
        children: [new TextRun({
          text,
          size: 18,
          font: 'Arial',
          bold: isHeader || bold,
        })],
        spacing: { before: 0, after: 0, line: 260 },
      })],
    });
  }

  const tableRows = [];

  if (headerRow) {
    tableRows.push(new TableRow({
      cantSplit: true,
      tableHeader: true,
      children: [
        makeCell(headerRow[0], col1W, true),
        makeCell(headerRow[1], col2W, true),
      ],
    }));
  }

  rows.forEach(([c1, c2]) => {
    tableRows.push(new TableRow({
      cantSplit: true,
      children: [
        makeCell(c1, col1W, false, col1Bold),
        makeCell(c2, col2W),
      ],
    }));
  });

  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [col1W, col2W],
    rows: tableRows,
  });
}

/**
 * Key-value detail table — for exclusive possession facts, notice defects, etc.
 * Left column is bold/shaded; right column is body text.
 */
function kvTable(rows) {
  const col1W = 2600;
  const col2W = CONTENT_W - col1W;
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [col1W, col2W],
    rows: rows.map(([k, v]) => new TableRow({
      cantSplit: true,
      children: [
        new TableCell({
          borders: allBorders,
          width: { size: col1W, type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          shading: { fill: LGRAY, type: ShadingType.CLEAR },
          children: [new Paragraph({
            children: [new TextRun({ text: k, bold: true, size: 18, font: 'Arial' })],
            spacing: { before: 0, after: 0 },
          })],
        }),
        new TableCell({
          borders: allBorders,
          width: { size: col2W, type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          shading: { fill: WHITE, type: ShadingType.CLEAR },
          children: [new Paragraph({
            children: [new TextRun({ text: v, size: 18, font: 'Arial' })],
            spacing: { before: 0, after: 0 },
          })],
        }),
      ],
    })),
  });
}

// ════════════════════════════════════════════════════════════════════════════
// HEADER & FOOTER
// ════════════════════════════════════════════════════════════════════════════

const docHeader = new Header({
  children: [
    new Paragraph({
      children: [
        new TextRun({ text: MATTER.privilege, bold: true, size: 18, font: 'Arial' }),
        new TextRun({ text: '\t' }),
        rg(MATTER.headerRef),
      ],
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      spacing: { before: 0, after: 60 },
      border: {
        bottom: { style: BorderStyle.SINGLE, size: 4, color: MGRAY, space: 2 },
      },
    }),
  ],
});

const docFooter = new Footer({
  children: [
    new Paragraph({
      children: [
        rg(`${MATTER.footerAddress}  |  ${MATTER.footerDate}`),
        new TextRun({ text: '\t' }),
        rg('Page '),
        new TextRun({ children: [PageNumber.CURRENT], size: 16, font: 'Arial', color: DGRAY }),
        rg(' of '),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, font: 'Arial', color: DGRAY }),
      ],
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      spacing: { before: 60, after: 0 },
      border: {
        top: { style: BorderStyle.SINGLE, size: 4, color: MGRAY, space: 2 },
      },
    }),
  ],
});

// ════════════════════════════════════════════════════════════════════════════
// COVER BLOCK — standard letter opening
// ════════════════════════════════════════════════════════════════════════════

function coverBlock() {
  const lines = [
    para([ri('WITHOUT PREJUDICE SAVE AS TO COSTS', 18)], { after: 40 }),
    para([ri('Sensitive Settlement Document', 18)], { after: 200 }),
    para([rb(MATTER.senderName1, 24)], { after: 20 }),
  ];
  if (MATTER.senderName2) {
    lines.push(para([rb(MATTER.senderName2, 24)], { after: 20 }));
  }
  lines.push(
    para([r(MATTER.senderAddr1)], { after: 20 }),
    para([r(MATTER.senderAddr2)], { after: 200 }),
    para([rb(`To: ${MATTER.recipientTo}`)], { after: 20 }),
    para([r(`Delivered by email to: ${MATTER.recipientEmail}`)], { after: 20 }),
    para([r(`Date: ${MATTER.date}`)], { after: 200 }),
    para([rb('Re: '), r(MATTER.subject)], { after: 200 }),
    para([r(`Dear ${MATTER.recipientTo.split(' ')[1] || MATTER.recipientTo},`)], { after: 100 }),
  );
  return lines;
}

// ════════════════════════════════════════════════════════════════════════════
// SIGNATURE BLOCK
// ════════════════════════════════════════════════════════════════════════════

function signatureBlock() {
  const lines = [
    para([r('Yours faithfully,')], { after: 400 }),
    para([r('_________________________________')], { after: 40 }),
    para([rb(MATTER.senderName1), r('  \u2014 Tenant')], { after: 200 }),
  ];
  if (MATTER.senderName2) {
    lines.push(
      para([r('_________________________________')], { after: 40 }),
      para([rb(MATTER.senderName2), r('  \u2014 Tenant')], { after: 200 }),
    );
  }
  lines.push(
    new Paragraph({
      children: [ri(
        'This letter constitutes general legal information prepared for self-represented ' +
        'litigant purposes and does not constitute legal advice. The Tenants are strongly ' +
        'encouraged to seek independent advice from Legal Aid WA (1300 650 579) or ' +
        'Circle Green Community Legal (08 6148 3636) before taking further action.',
        16,
      )],
      spacing: { before: 160, after: 0 },
      border: {
        top: { style: BorderStyle.SINGLE, size: 4, color: MGRAY, space: 4 },
      },
    }),
  );
  return lines;
}

// ════════════════════════════════════════════════════════════════════════════
// DOCUMENT BODY — replace this section for each letter
// ════════════════════════════════════════════════════════════════════════════

const body = [
  ...coverBlock(),

  // ── Opening context ───────────────────────────────────────────────────────
  para([
    r('We write formally to notify you of our legal position. '),
    r('Copies of all correspondence are retained for potential proceedings.'),
  ], { after: 80 }),

  spacer(),

  // ── Section 1 ─────────────────────────────────────────────────────────────
  sectionHeading('1', 'Section Title Here'),

  para([r('Body text of section 1 goes here. Cite statutes with section numbers.')], { after: 80 }),

  // Example: key-value facts table
  kvTable([
    ['Fact label',  'Fact explanation.'],
    ['Second fact', 'Second explanation.'],
  ]),
  spacer(8),

  // ── Section 2 ─────────────────────────────────────────────────────────────
  sectionHeading('2', 'Second Section'),

  para([r('Introductory paragraph with statutory citation: s.64 '), ri('RTA 1987'), r('.')], { after: 80 }),

  // Example: two-column notice/status table
  twoColTable(
    [
      ['Notice or item',  'Status and reason — cite section numbers.'],
      ['Second item',     'Second explanation.'],
    ],
    3600, CONTENT_W - 3600,
    ['Item', 'Status / Reason'],
  ),
  spacer(8),

  // ── Section 3 ─────────────────────────────────────────────────────────────
  sectionHeading('3', 'Demands'),

  // Example: demands table
  twoColTable(
    [
      ['Confirmation of legal position',        'Immediately'],
      ['Written authority for payment direction', 'Within 2 business days'],
      ['Bond lodgement reference',               'Within 7 days'],
    ],
    5600, CONTENT_W - 5600,
    ['Demand', 'Deadline'],
  ),
  spacer(8),

  ...signatureBlock(),
];

// ════════════════════════════════════════════════════════════════════════════
// ASSEMBLE & WRITE
// ════════════════════════════════════════════════════════════════════════════

const doc = new Document({
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: '\u2022',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 540, hanging: 300 } } },
      }],
    }],
  },
  styles: {
    default: {
      document: { run: { font: 'Arial', size: 20, color: BLACK } },
    },
  },
  sections: [{
    properties: {
      page: {
        size:   { width: PAGE_W, height: PAGE_H },
        margin: { top: MARGIN_TB, right: MARGIN_LR, bottom: MARGIN_TB, left: MARGIN_LR },
      },
    },
    headers: { default: docHeader },
    footers: { default: docFooter },
    children: body,
  }],
});

Packer.toBuffer(doc)
  .then(buf => {
    fs.writeFileSync(MATTER.outputPath, buf);
    console.log(`\u2713 Written: ${MATTER.outputPath}`);
  })
  .catch(err => {
    console.error('Build failed:', err);
    process.exit(1);
  });
