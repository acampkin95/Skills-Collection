---
name: reportlab-python
description: ReportLab Python PDF generation with Canvas drawing and Platypus document layout. Use for reports, invoices, tables, and page templates.
version: 2.0.0
reviewed: "2026-06-04"
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


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.