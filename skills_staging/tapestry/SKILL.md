---
name: tapestry
description: Content extraction and action planning from YouTube, articles, PDFs, and web pages. Transforms content into implementation roadmaps and learning paths.
version: 2.0.0
reviewed: "2026-06-04"
---
# Tapestry - Content Extraction and Action Planning

Use this skill to **extract valuable insights from any content and create actionable implementation plans**. Supports YouTube videos, articles, PDFs, and web pages. Transforms passive learning into active building.

## Core Philosophy

**Extract → Plan → Ship → Learn → Next**

Tapestry ensures you never just consume content. Every piece of content becomes a starting point for concrete action.

---

## Content Detection and Extraction

### Supported Content Types

| Source | Detection | Extraction Method |
|--------|-----------|-------------------|
| **YouTube** | URL contains `youtube.com` or `youtu.be` | Transcript + metadata |
| **Medium/Blog** | Standard web article | Content scraping + metadata |
| **PDF** | `.pdf` extension | OCR or text extraction |
| **Web Pages** | Generic URLs | Readability extraction |
| **Twitter/X** | `x.com` or `twitter.com` | Tweet content + thread |

### Automatic Detection

```typescript
function detectContentType(url: string): ContentType {
  if (url.includes('youtube.com') || url.includes('youtu.be')) {
    return 'youtube';
  }
  if (url.includes('medium.com') || url.includes('substack.com')) {
    return 'article';
  }
  if (url.endsWith('.pdf')) {
    return 'pdf';
  }
  return 'webpage';
}
```

---


See [full-reference.md](references/full-reference.md) for complete details, code examples, and advanced patterns.