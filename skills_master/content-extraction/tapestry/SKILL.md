---

## Parent router

This skill is a leaf of the [content-extraction](../content-extraction/SKILL.md) master router.
name: tapestry
description: Content extraction and actionable implementation planning from any source. Use when tapestry, content extraction, action planning, YouTube to implementation, PDF analysis, research to roadmap.
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

## YouTube Extraction

### Transcript Extraction

```typescript
import { getTranscript } from 'youtube-transcript';

async function extractYouTubeContent(url: string) {
  const videoId = extractVideoId(url);

  const transcript = await getTranscript({ videoId });

  const content = {
    title: 'Video Title',
    duration: '15:32',
    channel: 'Channel Name',
    transcript: transcript.map(t => t.text).join(' '),
    keyTimestamps: extractKeyTimestamps(transcript),
  };

  return content;
}
```

### Key Insights from Video

```typescript
function extractInsights(transcript: string): string[] {
  // Sentences starting with verbs (actionable)
  const actionable = transcript
    .split('.')
    .filter(s => /^(Use|Build|Create|Learn|Try|Test|Deploy)/i.test(s))
    .slice(0, 5);

  return actionable;
}
```

---

## Article/Blog Extraction

### Web Scraping

```typescript
import { Readability } from '@mozilla/readability';
import { JSDOM } from 'jsdom';

async function extractArticle(url: string) {
  const response = await fetch(url);
  const html = await response.text();

  const dom = new JSDOM(html, { url });
  const reader = new Readability(dom.window.document);
  const article = reader.parse();

  return {
    title: article.title,
    content: article.content,
    author: article.byline,
    publishedDate: article.publishedTime,
    excerpt: article.excerpt,
  };
}
```

### Extract Main Ideas

```typescript
function extractMainIdeas(content: string): string[] {
  // Split by paragraphs and filter for substantial ones
  return content
    .split('\n\n')
    .filter(p => p.split(' ').length > 20)
    .slice(0, 5);
}
```

---

## PDF Extraction

### Text Extraction

```typescript
import PDFParser from 'pdf-parse';
import fs from 'fs';

async function extractPDF(filePath: string) {
  const dataBuffer = fs.readFileSync(filePath);
  const data = await PDFParser(dataBuffer);

  return {
    title: filePath.split('/').pop(),
    pages: data.numpages,
    text: data.text,
    metadata: data.info,
  };
}
```

### OCR for Scanned PDFs

```typescript
import Tesseract from 'tesseract.js';

async function ocrScannedPDF(filePath: string) {
  const result = await Tesseract.recognize(
    filePath,
    'eng'
  );

  return result.data.text;
}
```

---

## Action Plan Generation

### Extract Actionable Tasks

```typescript
interface ActionItem {
  task: string;
  priority: 'high' | 'medium' | 'low';
  estimatedTime: string;
  dependencies: string[];
  resources: string[];
}

function generateActionPlan(content: string): ActionItem[] {
  const actionItems: ActionItem[] = [];

  // Extract imperative sentences (Build X, Implement Y, etc.)
  const imperatives = content
    .split('.')
    .filter(s => /^(Build|Implement|Create|Set up|Configure|Learn)/i.test(s));

  imperatives.forEach((imperative, idx) => {
    actionItems.push({
      task: imperative.trim(),
      priority: idx === 0 ? 'high' : 'medium',
      estimatedTime: '1-2 hours',
      dependencies: [],
      resources: [],
    });
  });

  return actionItems;
}
```

### Create Implementation Timeline

```typescript
interface Timeline {
  week1: ActionItem[];
  week2: ActionItem[];
  week3: ActionItem[];
  week4: ActionItem[];
}

function createTimeline(actions: ActionItem[]): Timeline {
  const timeline: Timeline = {
    week1: [],
    week2: [],
    week3: [],
    week4: [],
  };

  // High priority → Week 1
  // Medium → Week 2-3
  // Low → Week 4

  actions.forEach(action => {
    if (action.priority === 'high') {
      timeline.week1.push(action);
    } else if (action.priority === 'medium') {
      timeline.week2.push(action);
    } else {
      timeline.week4.push(action);
    }
  });

  return timeline;
}
```

---

## Full Tapestry Workflow

### Complete Pipeline

```typescript
async function tapestry(url: string) {
  // 1. Detect content type
  const contentType = detectContentType(url);

  // 2. Extract content
  let content;
  switch (contentType) {
    case 'youtube':
      content = await extractYouTubeContent(url);
      break;
    case 'article':
      content = await extractArticle(url);
      break;
    case 'pdf':
      content = await extractPDF(url);
      break;
    default:
      content = await extractArticle(url);
  }

  // 3. Extract insights
  const insights = extractInsights(content.text || content.transcript);

  // 4. Generate action plan
  const actionPlan = generateActionPlan(insights.join(' '));

  // 5. Create timeline
  const timeline = createTimeline(actionPlan);

  // 6. Return comprehensive report
  return {
    source: url,
    contentType,
    title: content.title,
    summary: insights.slice(0, 3),
    actionPlan,
    timeline,
    nextAction: actionPlan[0]?.task || 'Review content',
  };
}
```

---

## Output Formats

### Markdown Report

```markdown
# Learning Report: [Title]

## Source
- URL: [url]
- Content Type: [type]
- Date Extracted: [date]

## Key Insights
1. [Insight 1]
2. [Insight 2]
3. [Insight 3]

## Action Plan
### Week 1 (High Priority)
- [ ] Task 1 (~2 hours)
- [ ] Task 2 (~3 hours)

### Week 2-3 (Medium Priority)
- [ ] Task 3 (~4 hours)

### Week 4 (Low Priority)
- [ ] Task 4 (~1 hour)

## Next Steps
Start with: [First Task]
```

### JSON Export

```json
{
  "source": "https://example.com",
  "contentType": "article",
  "extracted_at": "2026-02-23T10:30:00Z",
  "actionPlan": [
    {
      "task": "Build authentication system",
      "priority": "high",
      "estimatedTime": "8-10 hours",
      "dependencies": ["Setup database"],
      "resources": ["NextAuth.js docs"]
    }
  ]
}
```

---

## Best Practices

1. **Start immediately**: Pick the highest-priority task and begin within 24 hours
2. **Track progress**: Use the timeline as a checklist
3. **Document learnings**: Record what worked and what didn't
4. **Iterate**: After completing action items, re-extract and update the plan
5. **Share plans**: Collaborate with teammates on action items

---

## Resources

- **Transcript APIs**: youtube-transcript, transcriber APIs
- **Web Scraping**: Readability, Cheerio, Puppeteer
- **PDF Processing**: pdf-parse, pdfjs
- **LLM Extraction**: Claude, GPT-4, Gemini
