---
name: content-extraction
description: Content extraction from any source — web scraping, OCR for documents/images, and content-to-action planning.
version: 2.0.0
reviewed: "2026-06-04"
---

# Content Extraction — Master Router

Route to the narrowest leaf that matches the source type and goal.

## Router

| Need | Route to |
| --- | --- |
| Web scraping (async, JS-rendered, LLM extraction) | `crawl4ai` |
| OCR for PDFs, scanned docs, images, handwriting | `deepinfra-ocr` |
| Extract content from URL/video/PDF and turn into an action plan | `tapestry` |
