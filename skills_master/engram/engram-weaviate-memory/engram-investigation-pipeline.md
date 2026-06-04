# Engram Investigation Intelligence Pipeline

OSINT investigation module built on Weaviate for evidence collection, entity extraction, timeline reconstruction, and intelligence report generation.

## Architecture

```
Seed URLs → InvestigationCrawler → EvidenceDocument (Weaviate)
                                         ↓
                            EntityExtractionWorker → Entity (Weaviate)
                                         ↓
                           TimelineExtractionWorker → TimelineEvent (Weaviate)
                                         ↓
                         ContradictionFlaggingWorker → Flags on TimelineEvent
                                         ↓
                         IntelligenceReportWorker → IntelligenceReport (Weaviate)
```

## Source Files

```
Engram-AiMemory/packages/core/src/memory_system/investigation/
  crawler.py        # InvestigationCrawler class
  workers.py        # 4-stage worker pipeline
```

---

## InvestigationCrawler

BFS web crawler with Redis-backed URL deduplication, domain restriction, and robots.txt compliance.

### Configuration

```python
# Environment variables
CRAWL_MAX_DEPTH=2                  # Max link depth from seed URLs
CRAWL_MAX_URLS_PER_MATTER=500      # Max pages per investigation
REDIS_URL=redis://redis:6379       # URL dedup backend

# CrawlJob model
class CrawlJob:
    matter_id: str
    seed_urls: List[str]
    max_depth: int = 2
    max_pages: int = 500
    allowed_domains: Optional[List[str]] = None  # Restrict crawl scope
```

### Crawl Behavior

```python
class InvestigationCrawler:
    REDIS_KEY_PREFIX = "investigation:crawled_urls"

    async def crawl_matter(self, job: CrawlJob) -> AsyncIterator[CrawlResult]:
        """
        BFS crawl with:
        - Redis dedup (mark URL seen BEFORE crawl to prevent races)
        - Domain restriction (job.allowed_domains)
        - Depth tracking per URL
        - robots.txt compliance (check_robots_txt=True ALWAYS)
        - Content exclusions: script, style, nav, footer, aside tags
        - Min word count: 50 words per page
        - Page timeout: 30 seconds
        - Images excluded (exclude_all_images=True)
        """
```

### CrawlResult

```python
class CrawlResult:
    url: str
    matter_id: str
    content: str          # Cleaned HTML
    markdown: str         # Markdown conversion
    title: str
    links: Dict           # Discovered links for BFS queue
```

### Deduplication

```python
async def _is_seen(self, matter_id: str, url: str) -> bool:
    """Check Redis set: investigation:crawled_urls:{matter_id}"""

async def _mark_seen(self, matter_id: str, url: str) -> None:
    """Add to Redis set BEFORE crawl (prevents race conditions)"""
```

---

## Stage 1: EntityExtractionWorker

Extracts persons, organisations, and locations from evidence documents.

### Method: Regex NER + LLM Fallback

```python
class EntityExtractionWorker:
    # Regex patterns
    PERSON_PATTERNS = [
        r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b'  # "John Smith"
    ]
    ORG_PATTERNS = [
        r'\b(\w+\s+(?:Ltd|Pty|Inc|Corp|LLC))\b',              # "Acme Ltd"
        r'\b([A-Z]{2,})\b'                                     # "FBI", "CIA"
    ]

    async def process_matter(self, matter_id: str):
        # 1. Fetch all EvidenceDocument chunks for matter
        # 2. Regex extraction (fast, high recall)
        # 3. LLM fallback for low-confidence cases
        # 4. Deduplicate entities by name similarity
        # 5. Store in Entity collection with matter_id
```

### LLM Configuration

```python
# Model: liquid/lfm2.5:1.2b via Ollama
# Temperature: 0.1 (deterministic extraction)
# Max tokens: 400
# Prompt: "Extract all person names and organisation names from the following text.
#          Return JSON: {"persons": [...], "organisations": [...]}"
```

### Output

Entities stored in Weaviate `Entity` collection with:
- `name`: Extracted name
- `entity_type`: PERSON, ORGANIZATION, or LOCATION
- `description`: Context from source text
- `project_id`: Investigation matter_id
- `aliases`: Alternative name forms discovered

---

## Stage 2: TimelineExtractionWorker

Extracts dated events from evidence for chronological reconstruction.

### Date Pattern Recognition

```python
DATE_PATTERNS = [
    r'\b(\d{1,2}/\d{1,2}/\d{4})\b',              # DD/MM/YYYY
    r'\b(\d{4}-\d{2}-\d{2})\b',                    # YYYY-MM-DD
    r'\b(\d{1,2}\s+(?:January|February|...)\s+\d{4})\b',  # 15 January 2024
    r'\b(?:January|February|...)\s+\d{1,2},?\s+\d{4}\b',  # January 15, 2024
]
```

### Output

Events stored in `TimelineEvent` collection:
- `event_date`: Parsed datetime
- `description`: Context surrounding the date mention
- `source_chunk_id`: Reference to EvidenceDocument chunk
- `matter_id`: Investigation identifier
- `confidence`: Extraction confidence (0-1)
- `source_url`: Origin URL

---

## Stage 3: ContradictionFlaggingWorker

Identifies conflicting claims across evidence sources.

### Algorithm

```python
async def process_matter(self, matter_id: str):
    # 1. Fetch all TimelineEvents for matter
    # 2. Group events by date (same day = potential conflict)
    # 3. For each date group with 2+ events from different sources:
    #    a. Compare descriptions semantically
    #    b. If descriptions conflict → flag for LLM verification
    # 4. LLM verification:
    #    - Model: liquid/lfm2.5:1.2b, temperature=0.1
    #    - Prompt: "Do these two statements contradict each other?"
    #    - Returns: {is_contradiction: bool, confidence: float, explanation: str}
    # 5. Update TimelineEvent.is_contradicted = True
```

---

## Stage 4: IntelligenceReportWorker

Generates aggregated intelligence reports from all collected data.

### Report Generation

```python
async def generate_report(self, matter_id: str) -> IntelligenceReport:
    # 1. Aggregate: entities, timeline, evidence, contradictions
    # 2. LLM synthesis (temperature=0.2 for factual accuracy)
    # 3. Output structure:
    return {
        "summary": {
            "total_evidence": count,
            "total_entities": count,
            "total_events": count,
            "contradictions_found": count
        },
        "persons": [{"name": "...", "mentions": N, "context": "..."}],
        "organisations": [{"name": "...", "type": "...", "context": "..."}],
        "timeline": [{"date": "...", "event": "...", "confidence": 0.9}],
        "narrative": "LLM-generated coherent summary of findings..."
    }
```

### Report Storage

Stored in `IntelligenceReport` collection:
- `report_type`: SUMMARY, TIMELINE, ENTITY_MAP
- `content`: Full report JSON
- `matter_id`: Investigation identifier
- `created_at`: Generation timestamp

---

## Running the Pipeline

### Via Docker

```bash
# Start investigation services
docker compose up -d investigation-crawler investigation-workers

# Environment
WEAVIATE_URL=http://weaviate:8080
REDIS_URL=redis://redis:6379
LLM_MODEL=liquid/lfm2.5:1.2b
OLLAMA_URL=http://ollama:11434
```

### Via API (Memory API endpoints)

```python
# Start investigation crawl
POST /investigations
{
    "matter_id": "INV-2026-001",
    "title": "Investigation Title",
    "seed_urls": ["https://example.com/page1", "https://example.com/page2"],
    "max_depth": 2,
    "allowed_domains": ["example.com"]
}

# Check investigation status
GET /investigations/INV-2026-001

# Get intelligence report
GET /investigations/INV-2026-001/report

# Get timeline
GET /investigations/INV-2026-001/timeline

# Get entities
GET /investigations/INV-2026-001/entities
```

### Pipeline Execution Order

```bash
# Manual execution (if not using API triggers)
# 1. Crawl
python -m memory_system.investigation.crawler --matter INV-2026-001

# 2. Extract entities
python -m memory_system.investigation.workers entity --matter INV-2026-001

# 3. Extract timeline
python -m memory_system.investigation.workers timeline --matter INV-2026-001

# 4. Flag contradictions
python -m memory_system.investigation.workers contradictions --matter INV-2026-001

# 5. Generate report
python -m memory_system.investigation.workers report --matter INV-2026-001
```

---

## MinIO S3 Integration

Evidence documents and reports backed up to MinIO:

```yaml
# docker-compose.yml
minio:
  image: minio/minio:latest
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin
  ports:
    - "9000:9000"   # S3 API
    - "9001:9001"   # Console

# Weaviate offload config
S3_ENDPOINT: http://minio:9000
S3_ACCESS_KEY_ID: minioadmin
S3_SECRET_ACCESS_KEY: minioadmin
S3_BUCKET: weaviate-offload
```
