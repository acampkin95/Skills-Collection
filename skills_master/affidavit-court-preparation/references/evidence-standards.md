# Evidence Standards — Court-Ready Preparation

## Chain of Custody

Every document used in court preparation must maintain a clear chain of custody:

1. **Source identification**: Where did this document come from?
2. **Original vs. copy**: Is this the original, an export, a screenshot, or a derivative?
3. **Hash verification**: SHA-256 hash of original file at intake
4. **Access log**: Who has accessed or modified the file?
5. **Working copies**: All analysis performed on copies, never originals

## Annexure / Exhibit Standards

### WA Magistrates Court

- Annexures attached to affidavits
- Each annexure marked with a sequential letter (A, B, C...)
- Cover page on each annexure:
  ```
  This is the annexure marked "[LETTER]" referred to in the
  affidavit of [NAME] sworn/affirmed at [PLACE] on [DATE]

  _________________________
  Signature of witness
  [JP / Lawyer]
  ```

### FCFCOA

- Annexures per Family Law Rules 2021
- Each annexure must be clearly identified
- Cover page mandatory
- Pagination continuous within each annexure

## Evidence Index Schema

| Field | Description |
|-------|-------------|
| ID | Sequential identifier (E001, E002...) |
| Date | Date of document/event (YYYY-MM-DD) |
| Description | Brief description |
| Relevance | Which claim/issue this supports |
| Category | Financial, Communication, Photo, Document, Expert Report |
| SourcePath | Relative path to file |
| Original/Derivative | Status of the document |
| Confidence | Confirmed / Probable / Uncertain / Unsupported |

## Print-Ready Standards

### A4 Format

- Page size: A4 (210mm × 297mm)
- Margins: minimum 25mm all sides
- Font: 12pt for body text, 14pt for headings
- Line spacing: 1.5 or double
- Paragraphs numbered sequentially
- Black text on white paper (unless colour is evidentially required)

### Pagination

- Page numbers in format "Page X of Y"
- Bottom right or bottom centre
- Continuous through document (not restarting per section)

### Bundle Organisation

1. Cover page
2. Table of contents
3. Affidavit body
4. Annexures in order (A, B, C...)
5. Each annexure on a new page

### Common Defects to Avoid

- Missing page numbers
- Annexures not matching references in affidavit
- Unclear photocopies or screenshots
- Mixed orientations (portrait/landscape) within a section
- Unstable formatting that shifts between screen and print
- Missing witness signatures on annexure cover pages
- Colour-dependent content printed in black and white
