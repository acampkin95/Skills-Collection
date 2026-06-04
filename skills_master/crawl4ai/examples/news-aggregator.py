#!/usr/bin/env python3
"""
News Aggregator - Aggregate and extract news articles from multiple sources.

This script crawls news websites, extracts article content, and provides
summarization and categorization capabilities.

Usage:
    python news-aggregator.py --sources tech,science --output ./news
    python news-aggregator.py --search "AI technology" --days 7
    python news-aggregator.py --batch sources.txt --dedupe
"""

import argparse
import asyncio
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.content_filter_strategy import BM25ContentFilter, PruningContentFilter
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
except ImportError:
    print("Error: crawl4ai not installed. Run: pip install crawl4ai")
    sys.exit(1)


# Predefined news source configurations
NEWS_SOURCES = {
    "tech": {
        "urls": [
            "https://techcrunch.com",
            "https://www.theverge.com",
            "https://wired.com",
            "https://arstechnica.com",
        ],
        "selectors": {
            "article": "article, [class*='post'], [class*='article']",
            "title": "h1, [class*='title']",
            "content": "[class*='content'], [class*='body'], article p",
            "date": "[class*='date'], time, [class*='published']",
        },
    },
    "science": {
        "urls": [
            "https://www.sciencenews.org",
            "https://www.nature.com/news",
            "https://www.scientificamerican.com",
        ],
        "selectors": {
            "article": "article, .article, .post",
            "title": "h1, .headline",
            "content": ".article-body, .content, article",
            "date": "time, .date, .published",
        },
    },
    "business": {
        "urls": [
            "https://www.bbc.com/news/business",
            "https://www.reuters.com",
            "https://www.bloomberg.com",
        ],
        "selectors": {
            "article": "article, [class*='article']",
            "title": "h1, [class*='headline']",
            "content": "[class*='body'], article p",
            "date": "time, [class*='date']",
        },
    },
    "general": {
        "urls": [
            "https://www.bbc.com/news",
            "https://www.cnn.com",
            "https://news.google.com",
        ],
        "selectors": {
            "article": "article, [class*='story'], [class*='news']",
            "title": "h1, h2, [class*='headline']",
            "content": "[class*='body'], article",
            "date": "time, [class*='date']",
        },
    },
}


@dataclass
class Article:
    """Represents a news article."""
    url: str
    title: str = ""
    content: str = ""
    summary: str = ""
    author: str = ""
    published_date: str = ""
    source: str = ""
    category: str = ""
    keywords: List[str] = field(default_factory=list)
    hash: str = ""
    crawled_at: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.hash:
            self.hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate content hash for deduplication."""
        content = f"{self.title}{self.content}"
        return hashlib.md5(content.encode()).hexdigest()


class NewsAggregator:
    """Aggregate news articles from multiple sources."""

    def __init__(self, output_dir: str = "./news_aggregated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.seen_hashes: Set[str] = set()
        self.seen_urls: Set[str] = set()
        self.articles: List[Article] = []

    def load_existing(self):
        """Load previously crawled articles to avoid duplicates."""
        existing_file = self.output_dir / "articles.json"
        if existing_file.exists():
            with open(existing_file) as f:
                data = json.load(f)
                for art in data:
                    self.seen_hashes.add(art.get("hash", ""))
                    self.seen_urls.add(art.get("url", ""))

    async def extract_article(
        self, url: str, source: str, selectors: Dict[str, str]
    ) -> Optional[Article]:
        """Extract article content from URL."""
        content_filter = PruningContentFilter(threshold=0.5)
        md_generator = DefaultMarkdownGenerator(content_filter=content_filter)

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(
            markdown_generator=md_generator,
            page_timeout=30000,
            wait_for="networkidle",
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

        if not result.success:
            return None

        # Extract metadata
        metadata = result.metadata or {}

        # Generate article
        content = result.markdown.fit_markdown if hasattr(result.markdown, 'fit_markdown') else result.markdown
        raw_content = result.markdown.raw_markdown if hasattr(result.markdown, 'raw_markdown') else str(result.markdown)

        article = Article(
            url=url,
            title=metadata.get("title", url),
            content=content,
            summary=raw_content[:500] if raw_content else "",
            author=metadata.get("author", ""),
            published_date=metadata.get("publish_date", ""),
            source=source,
            crawled_at=datetime.now().isoformat(),
            metadata=metadata,
        )

        return article

    async def crawl_source(
        self, source_name: str, source_config: Dict, limit: int = 10
    ) -> List[Article]:
        """Crawl articles from a news source."""
        articles = []
        urls = source_config["urls"]
        selectors = source_config.get("selectors", {})

        for url in urls:
            try:
                js_find_articles = """
                async () => {
                    const links = [];
                    const selectors = [
                        'article a[href]', '[class*="post"] a[href]',
                        '[class*="article"] a[href]', 'main a[href]'
                    ];

                    selectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(a => {
                            const href = a.href;
                            if (href && href.includes('/20') && !links.includes(href)) {
                                links.push(href);
                            }
                        });
                    });

                    return [...new Set(links)].slice(0, 20);
                }
                """

                browser_config = BrowserConfig(headless=True)
                crawler_config = CrawlerRunConfig(js_code=js_find_articles)

                async with AsyncWebCrawler(config=browser_config) as crawler:
                    result = await crawler.arun(url, config=crawler_config)

                if result.success:
                    article_urls = (result.js_result or [])[:limit]

                    for article_url in article_urls:
                        if article_url in self.seen_urls:
                            continue

                        print(f"  Extracting: {article_url[:60]}...")
                        article = await self.extract_article(
                            article_url, url, selectors
                        )

                        if article and article.hash not in self.seen_hashes:
                            articles.append(article)
                            self.seen_hashes.add(article.hash)
                            self.seen_urls.add(article.url)

                        await asyncio.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"Error crawling {url}: {e}")

        return articles

    async def aggregate(
        self,
        categories: List[str] = None,
        sources: List[str] = None,
        max_articles: int = 100,
        dedupe: bool = True,
    ) -> List[Article]:
        """Aggregate news from specified categories or sources."""
        if dedupe:
            self.load_existing()

        if sources:
            # Use provided source URLs
            pass
        elif categories:
            # Use predefined category sources
            for category in categories:
                if category in NEWS_SOURCES:
                    print(f"\nCrawling {category} sources...")
                    articles = await self.crawl_source(
                        category, NEWS_SOURCES[category], limit=max_articles // len(categories)
                    )
                    self.articles.extend(articles)

        # Deduplicate
        seen = set()
        unique = []
        for art in self.articles:
            if art.url not in seen:
                seen.add(art.url)
                unique.append(art)
        self.articles = unique[:max_articles]

        return self.articles

    async def search_articles(self, query: str, limit: int = 50) -> List[Article]:
        """Search previously crawled articles."""
        query_terms = query.lower().split()
        results = []

        for art in self.articles:
            score = 0
            text = f"{art.title} {art.content} {art.keywords}".lower()

            for term in query_terms:
                if term in text:
                    score += 1

            if score > 0:
                results.append((art, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return [art for art, _ in results[:limit]]

    def save_articles(
        self, articles: List[Article] = None, format: str = "json"
    ) -> str:
        """Save articles to file."""
        if articles is None:
            articles = self.articles

        if format == "json":
            output_file = self.output_dir / "articles.json"
            data = [
                {
                    "url": art.url,
                    "title": art.title,
                    "content": art.content,
                    "summary": art.summary,
                    "author": art.author,
                    "published_date": art.published_date,
                    "source": art.source,
                    "crawled_at": art.crawled_at,
                    "keywords": art.keywords,
                }
                for art in articles
            ]
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return str(output_file)

        elif format == "markdown":
            output_file = self.output_dir / "articles.md"
            content = f"# News Articles\n\n*Generated: {datetime.now().isoformat()}*\n\n"

            for art in articles:
                content += f"""---

## {art.title}

**Source:** {art.source} | **Date:** {art.published_date}

{art.content[:1000]}

[Read more]({art.url})

"""

            with open(output_file, "w") as f:
                f.write(content)
            return str(output_file)

        elif format == "rss":
            output_file = self.output_dir / "feed.xml"
            content = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>News Aggregator Feed</title>
<description>Aggregated news articles</description>
<link>https://news.example.com</link>
<lastBuildDate>{datetime.now().isoformat()}</lastBuildDate>
""".format(datetime=datetime)

            for art in articles[:50]:
                content += f"""
<item>
<title><![CDATA[{art.title}]]></title>
<link>{art.url}</link>
<description><![CDATA[{art.summary}]]></description>
<pubDate>{art.published_date}</pubDate>
<source>{art.source}</source>
</item>
"""

            content += "\n</channel>\n</rss>"

            with open(output_file, "w") as f:
                f.write(content)
            return str(output_file)

        return ""

    def generate_daily_brief(self, articles: List[Article] = None) -> str:
        """Generate a daily news briefing."""
        if articles is None:
            articles = self.articles

        # Group by source
        by_source: Dict[str, List[Article]] = {}
        for art in articles:
            source = urlparse(art.source).netloc
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(art)

        # Generate briefing
        lines = [
            f"# Daily News Briefing",
            f"*{datetime.now().strftime('%Y-%m-%d')}*",
            f"\n**{len(articles)} articles from {len(by_source)} sources**\n",
            "---",
        ]

        for source, arts in by_source.items():
            lines.append(f"\n## From {source}")
            lines.append("")

            for art in arts[:5]:
                lines.append(f"### {art.title}")
                lines.append(f"*{art.published_date or 'Unknown date'}*")
                lines.append("")
                lines.append(art.summary[:200] + "..." if len(art.summary) > 200 else art.summary)
                lines.append(f"[Read more]({art.url})")
                lines.append("")

        return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(description="Aggregate news articles")
    parser.add_argument(
        "--sources", "-s",
        help="Source categories: tech,science,business,general"
    )
    parser.add_argument(
        "--source-urls", help="File with source URLs (one per line)"
    )
    parser.add_argument(
        "--output", "-o", default="./news_aggregated", help="Output directory"
    )
    parser.add_argument(
        "--max-articles", "-m", type=int, default=100, help="Max articles"
    )
    parser.add_argument(
        "--format", "-f", choices=["json", "markdown", "rss"], default="json",
        help="Output format"
    )
    parser.add_argument(
        "--dedupe", action="store_true", default=True,
        help="Remove duplicate articles"
    )
    parser.add_argument(
        "--brief", action="store_true",
        help="Generate daily briefing"
    )
    parser.add_argument(
        "--search", help="Search previously crawled articles"
    )

    args = parser.parse_args()

    aggregator = NewsAggregator(args.output)

    if args.search:
        aggregator.load_existing()
        results = await aggregator.search_articles(args.search)
        print(f"Found {len(results)} articles matching '{args.search}'")
        for art in results[:10]:
            print(f"  - {art.title} ({art.source})")
        return

    # Determine sources
    categories = args.sources.split(",") if args.sources else ["tech", "science"]

    # Aggregate news
    print(f"Aggregating news from: {categories}")
    articles = await aggregator.aggregate(
        categories=categories,
        max_articles=args.max_articles,
        dedupe=args.dedupe,
    )

    print(f"\nAggregated {len(articles)} unique articles")

    # Save output
    output_file = aggregator.save_articles(format=args.format)
    print(f"Saved to: {output_file}")

    # Generate briefing
    if args.brief:
        brief_file = aggregator.output_dir / "daily_brief.md"
        brief = aggregator.generate_daily_brief()
        with open(brief_file, "w") as f:
            f.write(brief)
        print(f"Briefing saved to: {brief_file}")


if __name__ == "__main__":
    asyncio.run(main())
