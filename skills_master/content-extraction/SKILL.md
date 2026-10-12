---
name: content-extraction
description: Routes content extraction requests to crawl4ai for web scraping, deepinfra-ocr for OCR of PDFs, scans, and images, or tapestry for turning URLs, videos, and PDFs into action plans. Use when scraping or crawling web pages, extracting text from scanned documents or images, or pulling content from a URL, video, or PDF.
version: 2.0.0
reviewed: "2026-10-12"
---

# Content Extraction — Master Router

Route to the narrowest leaf that matches the source type and goal.

## Router

| Need | Route to |
| --- | --- |
| Web scraping (async, JS-rendered, LLM extraction) | `crawl4ai` |
| OCR for PDFs, scanned docs, images, handwriting | `deepinfra-ocr` |
| Extract content from URL/video/PDF and turn into an action plan | `tapestry` |
