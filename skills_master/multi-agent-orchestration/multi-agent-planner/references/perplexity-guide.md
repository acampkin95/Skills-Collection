# Perplexity AI Integration Guide

This guide covers the effective use of Perplexity AI for research operations within the Multi-Agent Planner system. Perplexity provides powerful search and deep research capabilities with automatic source citation.

## Table of Contents

1. [Overview](#overview)
2. [API Configuration](#api-configuration)
3. [Search Operations](#search-operations)
4. [Deep Research Workflows](#deep-research-workflows)
5. [Query Optimization](#query-optimization)
6. [Source Citation](#source-citation)
7. [Cost Optimization](#cost-optimization)
8. [Error Handling](#error-handling)
9. [Integration Examples](#integration-examples)

---

## Overview

### What is Perplexity AI?

Perplexity AI is a conversational search engine that:
- Provides direct answers with cited sources
- Supports both quick searches and deep research
- Offers an Anthropic-compatible API
- Includes source verification and attribution

### Capabilities

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Search** | Quick query with multiple sources | Fact finding, definitions |
| **Deep Research** | Comprehensive multi-source analysis | Reports, detailed research |
| **Focus Modes** | Domain-specific search | Academic, news, coding |
| **Cited Sources** | Automatic source attribution | Verification, citations |

### Use Cases in Multi-Agent Planner

```
Perplexity Integration Points:
  ├── Initial research discovery
  ├── Fact verification and cross-reference
  ├── Literature exploration
  ├── Competitive analysis
  ├── Technical documentation lookup
  └── Trend analysis and news tracking
```

---

## API Configuration

### Environment Setup

```bash
# Set Perplexity API key
export PERPLEXITY_API_KEY="your-api-key-here"

# Optional: Configure base URL (for custom endpoints)
export PERPLEXITY_BASE_URL="https://api.perplexity.ai"
```

### API Client Initialization

```python
from scripts.research_specialist import PerplexityClient, RateLimiter

# Standard initialization
client = PerplexityClient(api_key="your-api-key")

# With rate limiting
rate_limiter = RateLimiter(requests_per_minute=60, burst=10)
client = PerplexityClient(
    api_key="your-api-key",
    rate_limiter=rate_limiter
)

# Context manager usage
async with client:
    result = await client.search("your query")
```

### Configuration File

Create `config/perplexity.json`:

```json
{
  "api_key_env": "PERPLEXITY_API_KEY",
  "base_url": "https://api.perplexity.ai",
  "rate_limit": {
    "requests_per_minute": 60,
    "burst": 10
  },
  "defaults": {
    "max_results": 10,
    "timeout": 30,
    "focus_areas": ["general"]
  },
  "cost_tracking": {
    "enabled": true,
    "budget_warning_threshold": 10.00,
    "max_daily_spend": 50.00
  }
}
```

---

## Search Operations

### Basic Search

```python
async def perform_search(query: str) -> ResearchResult:
    """Perform a basic Perplexity search"""
    async with PerplexityClient() as client:
        result = await client.search(
            query=query,
            max_results=10
        )
    return result
```

### Search with Focus Areas

```python
# Search with academic focus
result = await client.search(
    query="machine learning optimization techniques",
    focus=["academic"],
    max_results=15
)

# Search with news focus
result = await client.search(
    query="latest AI developments 2024",
    focus=["news"],
    max_results=10
)

# Multiple focus areas
result = await client.search(
    query="Python async programming best practices",
    focus=["academic", "documentation", "stackoverflow"],
    max_results=20
)
```

### Focus Area Reference

| Focus Area | Description | Best For |
|------------|-------------|----------|
| **academic** | Peer-reviewed sources | Research papers, studies |
| **news** | Recent news articles | Current events, updates |
| **wikipedia** | Wikipedia sources | Overviews, background |
| **youtube** | Video content | Tutorials, demonstrations |
| **stackoverflow** | Q&A content | Technical solutions |
| **reddit** | Community discussions | Opinions, experiences |
| **finance** | Financial data | Market analysis, reports |
| **general** | All sources | Broad searches |

---

## Deep Research Workflows

### Initiating Deep Research

```python
async def deep_research_topic(
    query: str,
    focus_areas: Optional[list[str]] = None,
    max_sources: int = 20
) -> ResearchResult:
    """Perform comprehensive deep research"""
    async with PerplexityClient() as client:
        result = await client.deep_research(
            query=query,
            focus_areas=focus_areas or ["general"],
            max_sources=max_sources
        )
    return result
```

### Multi-Step Research Process

```python
async def comprehensive_research(
    topic: str,
    sub_questions: list[str]
) -> ResearchResult:
    """
    Conduct comprehensive research using iterative approach
    """
    results = []

    # Step 1: Broad overview
    overview = await client.deep_research(
        f"What is {topic}? Overview and key concepts",
        max_sources=10
    )
    results.append(overview)

    # Step 2: Historical context
    history = await client.search(
        f"History and evolution of {topic}",
        focus=["academic", "wikipedia"],
        max_results=5
    )
    results.append(history)

    # Step 3: Current state
    current = await client.search(
        f"Current developments and trends in {topic} 2024",
        focus=["news"],
        max_results=5
    )
    results.append(current)

    # Step 4: Technical details
    technical = await client.deep_research(
        f"Technical analysis of {topic}",
        focus_areas=["academic", "documentation"],
        max_sources=15
    )
    results.append(technical)

    # Step 5: Future outlook
    future = await client.search(
        f"Future predictions for {topic}",
        focus=["news", "finance"],
        max_sources=5
    )
    results.append(future)

    # Synthesize all results
    return synthesize_results(results)
```

### Research Progress Tracking

```python
class ResearchProgress:
    """Track deep research progress"""

    def __init__(self, total_queries: int):
        self.completed = 0
        self.total = total_queries
        self.sources_collected = 0
        self.start_time = datetime.now()

    def update(self, sources_count: int):
        self.completed += 1
        self.sources_collected += sources_count

    def get_status(self) -> dict:
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return {
            "completed": self.completed,
            "total": self.total,
            "progress_pct": (self.completed / self.total) * 100,
            "sources_collected": self.sources_collected,
            "elapsed_seconds": elapsed,
            "estimated_remaining": (
                (elapsed / self.completed) * (self.total - self.completed)
                if self.completed > 0 else None
            )
        }
```

---

## Query Optimization

### Query Structure Best Practices

```markdown
GOOD QUERY PATTERNS:

1. Specific Questions
   BAD:  "AI"
   GOOD: "What are the main optimization techniques for training neural networks?"

2. Context + Question
   BAD:  "Python performance"
   GOOD: "For a web application with 10k users, what Python async patterns work best?"

3. Time-Bound Queries
   BAD:  "latest iPhone features"
   GOOD: "iPhone 15 Pro major features announced in 2023"

4. Comparison Queries
   BAD:  "React vs Vue"
   GOOD: "What are the key differences between React and Vue for large-scale applications in 2024?"

5. Definition + Context
   BAD:  "What is Docker"
   GOOD: "Explain Docker containers and how they differ from virtual machines"
```

### Query Length Guidelines

| Query Type | Recommended Length | Example |
|------------|-------------------|---------|
| **Quick Fact** | 5-15 words | "Capital of France" |
| **Definition** | 10-25 words | "What is machine learning?" |
| **Analysis** | 20-50 words | Full question with context |
| **Deep Research** | 30-100 words | Comprehensive topic description |

### Query Templates

```python
QUERY_TEMPLATES = {
    "definition": "What is {topic}? Define and explain.",
    "comparison": "Compare {item_a} vs {item_b} on dimensions: {dimensions}.",
    "how_to": "How do I {action} using {tool/technology}?",
    "best_practices": "What are best practices for {task} in {context}?",
    "troubleshooting": "How to fix {error} when using {technology}?",
    "trends": "What are the latest trends in {field} {year}?",
    "pros_cons": "What are the advantages and disadvantages of {thing}?",
    "recommendations": "What are the top recommendations for {use_case}?",
}


def build_query(template: str, **params) -> str:
    """Build query from template and parameters"""
    return template.format(**params)


# Usage
query = build_query(
    "comparison",
    item_a="React",
    item_b="Vue",
    dimensions="performance, ecosystem, learning curve, community support"
)
# Result: "Compare React vs Vue on dimensions: performance, ecosystem, learning curve, community support"
```

### Query Optimization Checklist

```markdown
Before submitting a query:
  [ ] Is the query specific enough?
  [ ] Does it include necessary context?
  [ ] Are there any ambiguous terms?
  [ ] Is the time frame appropriate?
  [ ] Have I broken down complex questions?
  [ ] Am I asking for actionable recommendations?
```

---

## Source Citation

### Understanding Perplexity Citations

Perplexity provides automatic citations with each response:

```python
result = await client.search("quantum computing basics")

# Access citations
for i, citation in enumerate(result.sources):
    print(f"[{i+1}] {citation.title}")
    print(f"    URL: {citation.url}")
    print(f"    Relevance: {citation.relevance_score:.2f}")
    print(f"    Snippet: {citation.snippet[:100]}...")
```

### Citation Structure

```python
@dataclass
class Citation:
    source_id: str          # Unique identifier
    url: str               # Source URL
    title: str             # Page title
    accessed_at: str       # ISO timestamp
    content_type: str      # web, academic, etc.
    snippet: str           # Relevant excerpt
    relevance_score: float # 0.0-1.0
```

### Citation Quality Assessment

```python
def assess_citation_quality(citation: Citation) -> dict:
    """Assess the quality of a citation"""
    score = 0.0
    reasons = []

    # Check relevance score
    if citation.relevance_score >= 0.8:
        score += 0.3
        reasons.append("High relevance")
    elif citation.relevance_score >= 0.6:
        score += 0.15
        reasons.append("Moderate relevance")

    # Check content type
    if citation.content_type == "academic":
        score += 0.3
        reasons.append("Academic source")
    elif citation.content_type == "official":
        score += 0.25
        reasons.append("Official source")
    elif citation.content_type == "news":
        score += 0.15
        reasons.append("News source")

    # Check snippet length
    if len(citation.snippet) > 100:
        score += 0.2
        reasons.append("Good snippet length")
    elif len(citation.snippet) > 50:
        score += 0.1
        reasons.append("Adequate snippet")

    # Check URL validity
    if citation.url.startswith("https://"):
        score += 0.2
        reasons.append("Secure source")

    return {
        "quality_score": min(score, 1.0),
        "reasons": reasons,
        "citation": citation.to_dict()
    }
```

### Generating Citation Reports

```python
async def generate_citation_report(
    results: list[ResearchResult]
) -> dict:
    """Generate a formatted citation report"""
    citations = []
    for result in results:
        citations.extend(result.sources)

    # Sort by relevance
    citations.sort(key=lambda c: c.relevance_score, reverse=True)

    # Generate report
    report = {
        "total_citations": len(citations),
        "by_type": {},
        "top_sources": [],
        "report_generated": datetime.now().isoformat()
    }

    # Count by type
    for c in citations:
        report["by_type"][c.content_type] = (
            report["by_type"].get(c.content_type, 0) + 1
        )

    # Top 10 sources
    for c in citations[:10]:
        report["top_sources"].append({
            "id": c.source_id,
            "title": c.title,
            "url": c.url,
            "relevance": c.relevance_score,
            "type": c.content_type
        })

    return report
```

---

## Cost Optimization

### Pricing Structure

| Operation | Approximate Cost | Notes |
|-----------|------------------|-------|
| Search (standard) | ~$0.005/query | Based on tokens |
| Deep Research | ~$0.05/query | More comprehensive |
| API calls | Per-token pricing | ~$0.003/1K input tokens |

### Cost Tracking

```python
class CostTracker:
    """Track Perplexity API costs"""

    def __init__(self, daily_budget: float = 10.0):
        self.daily_budget = daily_budget
        self.session_costs = 0.0
        self.daily_costs = {}
        self.operation_counts = {}

    def record_operation(
        self,
        operation_type: str,
        tokens_used: int,
        cost: float
    ):
        """Record an API operation and its cost"""
        today = datetime.now().strftime("%Y-%m-%d")

        self.session_costs += cost
        self.daily_costs[today] = self.daily_costs.get(today, 0.0) + cost

        self.operation_counts[operation_type] = (
            self.operation_counts.get(operation_type, 0) + 1
        )

        # Warning if approaching budget
        if self.daily_costs[today] > self.daily_budget * 0.8:
            logging.warning(
                f"Approaching daily budget: "
                f"${self.daily_costs[today]:.2f}/${self.daily_budget}"
            )

    def get_summary(self) -> dict:
        return {
            "session_cost": round(self.session_costs, 4),
            "daily_cost": round(
                self.daily_costs.get(datetime.now().strftime("%Y-%m-%d"), 0.0),
                4
            ),
            "operations": self.operation_counts,
            "budget_status": (
                "OK" if self.session_costs < self.daily_budget else "EXCEEDED"
            )
        }
```

### Cost Optimization Strategies

```python
COST_OPTIMIZATION_STRATEGIES = [
    {
        "strategy": "Batch Related Queries",
        "description": "Combine multiple related questions into one query",
        "savings": "~30-50%"
    },
    {
        "strategy": "Set max_results Appropriately",
        "description": "Don't request more sources than needed",
        "savings": "~20-40%"
    },
    {
        "strategy": "Use Focus Areas",
        "description": "Narrow search to relevant domains",
        "savings": "~15-25%"
    },
    {
        "strategy": "Cache Results",
        "description": "Store and reuse results for repeated queries",
        "savings": "~100% on cache hits"
    },
    {
        "strategy": "Limit Deep Research",
        "description": "Use standard search when deep research isn't needed",
        "savings": "~90%"
    },
    {
        "strategy": "Parallelize Independent Queries",
        "description": "Run independent searches concurrently",
        "savings": "Time savings"
    }
]
```

### Budget Alert Configuration

```yaml
# config/cost_alerts.yaml
alerts:
  warning_threshold: 0.5     # Warn at 50% of budget
  critical_threshold: 0.8    # Critical at 80% of budget
  daily_budget: 10.00        # $10 per day
  monthly_budget: 200.00     # $200 per month
  notification:
    method: "log"            # log, email, slack
    channel: "default"
```

---

## Error Handling

### Error Types and Solutions

```python
ERROR_HANDLERS = {
    "rate_limit": {
        "error_code": 429,
        "message": "Too many requests",
        "solution": "Implement exponential backoff, reduce request rate",
        "retry_after": 60
    },
    "auth_error": {
        "error_code": 401,
        "message": "Invalid API key",
        "solution": "Verify API key in environment variables",
        "retry_after": None
    },
    "quota_exceeded": {
        "error_code": 402,
        "message": "API quota exceeded",
        "solution": "Check billing, wait for quota reset",
        "retry_after": 86400
    },
    "invalid_request": {
        "error_code": 400,
        "message": "Invalid request parameters",
        "solution": "Validate query format, check parameters",
        "retry_after": None
    },
    "server_error": {
        "error_code": 500,
        "message": "Internal server error",
        "solution": "Retry with backoff, contact support if persistent",
        "retry_after": 30
    }
}
```

### Retry Logic Implementation

```python
async def fetch_with_retry(
    query: str,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> ResearchResult:
    """Fetch with automatic retry and backoff"""
    for attempt in range(max_retries):
        try:
            async with PerplexityClient() as client:
                return await client.search(query)

        except Exception as e:
            error_type = type(e).__name__

            if error_type == "RateLimitError":
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
                logging.info(f"Rate limited, retrying in {delay}s...")
                continue

            elif error_type == "AuthenticationError":
                logging.error("Authentication failed. Check API key.")
                raise

            elif error_type == "TimeoutError":
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                raise

            else:
                logging.error(f"Unexpected error: {e}")
                raise

    raise Exception(f"Failed after {max_retries} retries")
```

### Circuit Breaker Pattern

```python
class PerplexityCircuitBreaker:
    """Circuit breaker for Perplexity API calls"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 300
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure = None
        self.state = "closed"  # closed, open, half_open

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == "open":
            if (datetime.now() - self.last_failure).seconds > self.recovery_timeout:
                self.state = "half_open"
            else:
                raise CircuitOpenError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failures = 0
        self.state = "closed"

    def on_failure(self):
        self.failures += 1
        self.last_failure = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = "open"
```

---

## Integration Examples

### Complete Research Workflow

```python
async def research_workflow(
    topic: str,
    budget: float = 5.0,
    min_sources: int = 10
) -> ResearchResult:
    """
    Complete research workflow with cost tracking and error handling
    """
    # Initialize components
    cost_tracker = CostTracker(daily_budget=budget)
    circuit_breaker = PerplexityCircuitBreaker()
    specialist = ResearchSpecialist()

    try:
        # Phase 1: Initial search
        result = await circuit_breaker.call(
            specialist.research,
            f"Overview of {topic}",
            ResearchType.WEB_SEARCH,
            max_results=5
        )
        cost_tracker.record_operation("search", result.tokens_used, cost_estimate(result))

        # Phase 2: Deep research if needed
        if len(result.sources) < min_sources:
            result = await circuit_breaker.call(
                specialist.research,
                f"Deep dive into {topic}",
                ResearchType.DEEP_RESEARCH,
                max_results=20
            )
            cost_tracker.record_operation("deep_research", result.tokens_used, cost_estimate(result))

        # Generate report
        report = await specialist.generate_citation_report([result])

        return ResearchOutput(
            results=result,
            citations=report,
            cost_summary=cost_tracker.get_summary()
        )

    except CircuitOpenError:
        logging.error("Circuit breaker is open, cannot proceed")
        raise
    except Exception as e:
        logging.error(f"Research workflow failed: {e}")
        raise
```

### Parallel Research Execution

```python
async def parallel_research(
    topics: list[str],
    max_concurrent: int = 3
) -> list[ResearchResult]:
    """Run research on multiple topics concurrently"""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def research_topic(topic: str):
        async with semaphore:
            async with PerplexityClient() as client:
                return await client.search(topic)

    results = await asyncio.gather(
        *[research_topic(t) for t in topics],
        return_exceptions=True
    )

    return [r for r in results if isinstance(r, ResearchResult)]
```

### Scheduled Research Job

```python
# Example: Scheduled daily research summary
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def daily_research_summary():
    topics = [
        "AI industry news today",
        "Technology trends 2024",
        "Latest software releases"
    ]

    results = await parallel_research(topics)
    report = await generate_summary_report(results)
    await send_report(report)

# Schedule daily at 9 AM
scheduler = AsyncIOScheduler()
scheduler.add_job(daily_research_summary, "cron", hour=9)
scheduler.start()
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No results | Query too broad/narrow | Adjust query specificity |
| Poor quality sources | No focus areas | Add focus parameter |
| Rate limiting | Too many requests | Implement rate limiter |
| Timeouts | Complex queries | Use simpler queries or increase timeout |
| Authentication errors | Invalid/missing API key | Verify API key configuration |
| High costs | Excessive queries | Implement caching, optimize queries |

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Perplexity client will log:
# - Request details
# - Response times
# - Token usage
# - Error details
```

---

## Summary

This guide covers the essential aspects of Perplexity AI integration for the Multi-Agent Planner:

1. **API Configuration**: Proper setup and initialization
2. **Search Operations**: Basic and focused searches
3. **Deep Research**: Comprehensive research workflows
4. **Query Optimization**: Effective query crafting
5. **Source Citation**: Understanding and using citations
6. **Cost Optimization**: Managing API costs
7. **Error Handling**: Robust error recovery
8. **Integration Examples**: Complete workflow implementations

By following these guidelines, agents can effectively leverage Perplexity AI for high-quality research while managing costs and ensuring reliability.

---

**Last Updated**: January 2025
**Version**: 1.0
**Perplexity API Docs**: https://docs.perplexity.ai
