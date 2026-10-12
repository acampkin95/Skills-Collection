---
name: pdf-generation
description: "PDF generation router: sends Node.js PDF generation with PDFKit and Python PDF generation with ReportLab (Canvas or Platypus) to the matching sub-skill, for reports, invoices and printable documents. Use when creating a PDF from code, generating an invoice or report as PDF, or choosing between PDFKit and ReportLab."
version: 2.0.0
reviewed: "2026-10-12"
---

# PDF Generation — Master Router

## Router

| Need | Route to |
| --- | --- |
| Node.js — PDFKit chainable API, text, vector graphics, images, tables | `pdfkit-node` |
| Python — ReportLab Canvas (low-level) or Platypus (high-level flowables) | `reportlab-python` |
