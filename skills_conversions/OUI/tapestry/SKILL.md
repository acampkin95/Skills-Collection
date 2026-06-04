---
name: tapestry
description: "Content extraction and actionable implementation planning from any source. Covers content detection, YouTube/article/PDF/web extraction strategies, insight extraction, action plan generation, and timeline creation. Use when extracting knowledge from URLs, videos, or documents and converting it into actionable plans."
version: "1.0.0"
metadata:
  category: content-planning
  scope: non-cli
---

# Tapestry — Content Extraction and Action Planning

Extract valuable insights from any content source and create actionable implementation plans. Transforms passive consumption into active building.

## Core Philosophy

**Extract → Plan → Ship → Learn → Next**

Every piece of content becomes a starting point for concrete action. Never just consume — always extract, plan, and act.

---

## Content Detection

### Source Types

| Source | Detection Signal | Extraction Approach |
|--------|-----------------|---------------------|
| **YouTube** | URL contains `youtube.com` or `youtu.be` | Transcript + metadata extraction |
| **Articles/Blogs** | Standard web article URL | Readability extraction + metadata |
| **PDF** | `.pdf` extension or PDF MIME type | Text extraction or OCR |
| **Web Pages** | Generic URLs | Content scraping + metadata |
| **Social Media** | `x.com`, `twitter.com`, `threads.net` | Post content + thread context |
| **Academic Papers** | `arxiv.org`, `doi.org`, `.edu` domains | Abstract + key findings extraction |

### Detection Flow

```
Input URL or content
    │
    ├── Contains youtube.com or youtu.be?
    │   └── YES → YouTube extraction pipeline
    │
    ├── Ends with .pdf?
    │   └── YES → PDF extraction pipeline
    │
    ├── Contains arxiv.org, doi.org?
    │   └── YES → Academic extraction pipeline
    │
    ├── Contains twitter.com, x.com?
    │   └── YES → Social media extraction pipeline
    │
    └── Default → Web article extraction pipeline
```

---

## Extraction Strategies

### YouTube Videos

**What to Extract:**
- Video title, channel, duration, publish date
- Full transcript (auto-generated or manual)
- Key timestamps (chapter markers, topic transitions)
- Description links and resources mentioned

**Insight Extraction from Transcripts:**
1. Identify topic sections (chapter boundaries)
2. Extract key claims and statements
3. Find actionable imperatives ("Build X", "Use Y pattern", "Avoid Z")
4. Note tools, libraries, or resources mentioned
5. Capture quotes worth remembering

### Web Articles/Blogs

**What to Extract:**
- Title, author, publish date, source
- Main content (stripped of navigation, ads, boilerplate)
- Key headings and section structure
- Images with alt text descriptions
- Outbound links and references

**Extraction Process:**
1. Fetch HTML content
2. Apply readability algorithm (strip boilerplate)
3. Extract structured metadata (author, date, tags)
4. Identify section headings as structural outline
5. Extract main paragraphs as content blocks
6. Collect links and references for further reading

### PDFs and Documents

**What to Extract:**
- Title, author, page count, creation date
- Full text content (preserving reading order)
- Table data (structured extraction)
- Image descriptions or captions
- Key sections and headings

**Extraction Decision Tree:**
```
Is the PDF text-based?
├── YES → Direct text extraction
│   └── Clean formatting, preserve structure
└── NO (scanned/image)
    ├── Few pages → OCR processing
    └── Many pages → OCR with page segmentation
```

### Academic Papers

**What to Extract:**
- Title, authors, institution, publication date
- Abstract (always extract in full)
- Key findings and conclusions
- Methodology summary
- Data tables and figures described
- Citations and references

---

## Insight Extraction Framework

### Three-Pass Extraction

| Pass | Focus | Output |
|------|-------|--------|
| **1. Surface** | Key facts, figures, definitions | Bullet list of facts |
| **2. Structure** | Arguments, reasoning, relationships | Argument map or outline |
| **3. Action** | What can be built, applied, or tested | Actionable task list |

### Extracting Actionable Content

Look for these content patterns:

| Pattern | Signal | Example |
|---------|--------|---------|
| **Imperative verbs** | Direct instructions | "Build a caching layer using Redis" |
| **Recommendations** | Should/must statements | "You should always validate input" |
| **Comparisons** | Trade-off insights | "X is better for speed, Y for reliability" |
| **Common mistakes** | Anti-patterns to avoid | "Never store secrets in client-side code" |
| **Resources** | Tools/libraries to investigate | "Use Vitest for unit testing" |
| **Metrics** | Quantifiable benchmarks | "Reduced load time from 3s to 800ms" |

---

## Action Plan Generation

### Task Extraction Template

```
TASK EXTRACTION:
├── Task description: [what to do]
├── Priority: [high | medium | low]
├── Estimated effort: [hours/days]
├── Prerequisites: [what must be done first]
├── Resources needed: [tools, docs, libraries]
└── Success criteria: [how to know it's done]
```

### Priority Assignment

| Priority | Criteria | Timeline |
|----------|----------|----------|
| **High** | Foundational, blocks other tasks; directly from content's core thesis | Week 1 |
| **Medium** | Important but not blocking; supporting concepts | Week 2-3 |
| **Low** | Nice-to-have, exploratory, tangential | Week 4+ |

### Timeline Creation

```
WEEK 1 — Foundation (High Priority)
├── Task A: [description] (~X hours)
└── Task B: [description] (~X hours)

WEEK 2-3 — Core Implementation (Medium Priority)
├── Task C: [description] (~X hours)
├── Task D: [description] (~X hours)
└── Task E: [description] (~X hours)

WEEK 4+ — Polish and Explore (Low Priority)
├── Task F: [description] (~X hours)
└── Task G: [description] (~X hours)
```

---

## Full Tapestry Workflow

### Pipeline

```
1. DETECT content type from URL/input
      ↓
2. EXTRACT content using appropriate strategy
      ↓
3. ANALYZE with three-pass extraction (surface → structure → action)
      ↓
4. GENERATE action plan with prioritized tasks
      ↓
5. CREATE timeline with weekly milestones
      ↓
6. OUTPUT report in requested format
```

### Output Formats

**Markdown Report:**
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

**Structured Data:**
```
{
  source: URL,
  contentType: "youtube" | "article" | "pdf" | "webpage",
  extracted_at: ISO timestamp,
  insights: [string],
  actionPlan: [
    { task, priority, estimatedTime, dependencies, resources }
  ]
}
```

---

## Best Practices

1. **Start immediately**: Pick the highest-priority task and begin within 24 hours
2. **Track progress**: Use the timeline as a living checklist
3. **Document learnings**: Record what worked and what didn't for each task
4. **Iterate**: After completing action items, re-extract and update the plan
5. **Share plans**: Collaborate with teammates on action items
6. **Batch similar sources**: Extract from multiple sources on the same topic, then synthesize
7. **Validate before acting**: Cross-reference extracted insights with primary sources

---

## Extraction Quality Checklist

- [ ] Content type correctly identified
- [ ] Full content extracted (not just first section)
- [ ] Metadata captured (author, date, source)
- [ ] Key arguments and claims identified
- [ ] Actionable items separated from informational content
- [ ] Priorities assigned based on source emphasis
- [ ] Dependencies between tasks identified
- [ ] Resources and references collected for follow-up

## When to Use

- Extracting actionable insights from YouTube videos or talks
- Converting articles or blog posts into implementation roadmaps
- Processing PDFs, whitepapers, or documentation into task lists
- Creating learning plans from educational content
- Building feature roadmaps from research content
- Synthesizing multiple content sources into a unified action plan

## Limitations

- Cannot execute extractions directly — relies on agent's available tools
- Quality depends on source content accessibility (paywalls, JavaScript rendering)
- OCR quality for scanned PDFs varies by document quality
- YouTube transcript availability depends on video settings
- Action plan quality depends on content's inherent actionability — some content is purely informational
- Timeline estimates are approximate and context-dependent

## Cross-References

| Skill | Relationship |
|-------|-------------|
| [content-extraction](../content-extraction/SKILL.md) | Lower-level extraction techniques for specific content types |
| [web-crawling](../web-crawling/SKILL.md) | Crawling strategies for multi-page content extraction |
| [deep-research](../deep-research/SKILL.md) | Extended research that feeds into action plan generation |
| [summarization](../summarization/SKILL.md) | Summarize extracted content before action plan generation |
| [reporting](../reporting/SKILL.md) | Structure the Tapestry output into formal reports |
| [data-synthesis](../data-synthesis/SKILL.md) | Combine insights from multiple extracted sources |
