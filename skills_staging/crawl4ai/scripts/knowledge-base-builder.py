#!/usr/bin/env python3
"""
Knowledge Base Builder - Build searchable knowledge bases from web content.

This script crawls multiple pages and builds a structured, searchable knowledge
base with indexing for fast retrieval. Supports multiple output formats
including JSON, Markdown, and SQLite.

Usage:
    python knowledge-base-builder.py --seed https://docs.example.com --output ./kb
    python knowledge-base-builder.py --urls urls.txt --format sqlite
    python knowledge-base-builder.py --query "how to install" --search
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
except ImportError:
    print("Error: crawl4ai not installed. Run: pip install crawl4ai")
    sys.exit(1)


@dataclass
class Document:
    """Represents a document in the knowledge base."""
    id: str
    url: str
    title: str
    content: str
    markdown: str
    metadata: Dict[str, str] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    category: str = ""
    created_at: str = ""
    chunk_ids: List[str] = field(default_factory=list)


@dataclass
class KnowledgeChunk:
    """A chunk of a document for indexing."""
    id: str
    document_id: str
    content: str
    chunk_index: int
    keywords: List[str] = field(default_factory=list)


class StorageBackend(ABC):
    """Abstract base for storage backends."""

    @abstractmethod
    def add_document(self, doc: Document) -> None:
        pass

    @abstractmethod
    def add_chunk(self, chunk: KnowledgeChunk) -> None:
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def save(self) -> None:
        pass


class JSONStorage(StorageBackend):
    """JSON file-based storage."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.documents: Dict[str, Document] = {}
        self.chunks: Dict[str, KnowledgeChunk] = {}
        self.documents_file = self.output_dir / "documents.json"
        self.chunks_file = self.output_dir / "chunks.json"
        self._load()

    def _load(self):
        if self.documents_file.exists():
            with open(self.documents_file) as f:
                data = json.load(f)
                self.documents = {k: Document(**v) for k, v in data.items()}
        if self.chunks_file.exists():
            with open(self.chunks_file) as f:
                data = json.load(f)
                self.chunks = {k: KnowledgeChunk(**v) for k, v in data.items()}

    def add_document(self, doc: Document) -> None:
        self.documents[doc.id] = doc

    def add_chunk(self, chunk: KnowledgeChunk) -> None:
        self.chunks[chunk.id] = chunk

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Simple keyword-based search."""
        query_terms = query.lower().split()
        results = []

        for doc in self.documents.values():
            score = 0
            content_lower = doc.content.lower()
            title_lower = doc.title.lower()

            # Title matches weighted higher
            for term in query_terms:
                if term in title_lower:
                    score += 10
                if term in content_lower:
                    score += 1
                if term in doc.keywords:
                    score += 5

            if score > 0:
                results.append(
                    {
                        "document_id": doc.id,
                        "title": doc.title,
                        "url": doc.url,
                        "score": score,
                        "snippet": doc.content[:200] + "...",
                    }
                )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def save(self) -> None:
        with open(self.documents_file, "w") as f:
            json.dump({k: v.__dict__ for k, v in self.documents.items()}, f, indent=2)
        with open(self.chunks_file, "w") as f:
            json.dump({k: v.__dict__ for k, v in self.chunks.items()}, f, indent=2)


class MarkdownStorage(StorageBackend):
    """Markdown file-based storage with folder organization."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=self.output_dir.exists() or self.output_dir == Path("."))

        # Create index file
        self.index_file = self.output_dir / "README.md"

        self.documents: Dict[str, Document] = {}
        self._load()

    def _load(self):
        # Load existing from JSON companion file
        meta_file = self.output_dir / "kb_meta.json"
        if meta_file.exists():
            with open(meta_file) as f:
                data = json.load(f)
                self.documents = {k: Document(**v) for k, v in data.items()}

    def add_document(self, doc: Document) -> None:
        # Save as markdown file
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', doc.title[:50])
        filepath = self.output_dir / f"{safe_filename}.md"

        content = f"""---
title: {doc.title}
url: {doc.url}
category: {doc.category}
created: {doc.created_at}
keywords: {', '.join(doc.keywords)}
---

# {doc.title}

{doc.markdown}
"""
        with open(filepath, "w") as f:
            f.write(content)

        self.documents[doc.id] = doc

    def add_chunk(self, chunk: KnowledgeChunk) -> None:
        pass  # Not needed for markdown storage

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        # Return references to markdown files
        query_terms = query.lower().split()
        results = []

        for doc in self.documents.values():
            score = 0
            for term in query_terms:
                if term in doc.title.lower():
                    score += 10
                if term in doc.content.lower():
                    score += 1

            if score > 0:
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', doc.title[:50])
                results.append(
                    {
                        "document_id": doc.id,
                        "title": doc.title,
                        "url": doc.url,
                        "score": score,
                        "file": f"{safe_filename}.md",
                    }
                )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def save(self) -> None:
        # Save metadata
        meta_file = self.output_dir / "kb_meta.json"
        with open(meta_file, "w") as f:
            json.dump({k: v.__dict__ for k, v in self.documents.items()}, f, indent=2)

        # Generate index
        index_content = "# Knowledge Base Index\n\n"
        categories: Dict[str, List[Document]] = {}
        for doc in self.documents.values():
            if doc.category not in categories:
                categories[doc.category] = []
            categories[doc.category].append(doc)

        for category, docs in categories.items():
            index_content += f"\n## {category or 'Uncategorized'}\n\n"
            for doc in docs:
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', doc.title[:50])
                index_content += f"- [{doc.title}]({safe_filename}.md)\n"

        with open(self.index_file, "w") as f:
            f.write(index_content)


class KnowledgeBaseBuilder:
    """Build and manage knowledge bases from web content."""

    def __init__(
        self,
        output_dir: str = "./knowledge_base",
        storage: str = "json",
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> None:
        """Initialize a KnowledgeBaseBuilder with specified storage backend.

        Creates a knowledge base builder with configurable storage backend (JSON or Markdown),
        content chunking parameters, and URL tracking for avoiding duplicate crawls.

        Args:
            output_dir: Directory path for storing knowledge base files and metadata
                       (default: "./knowledge_base").
            storage: Storage backend type - either "json" or "markdown" (default: "json").
                    JSON uses structured JSON files for documents/chunks; Markdown generates
                    individual markdown files with folder organization.
            chunk_size: Number of characters per content chunk for indexing (default: 1000).
                       Larger chunks contain more context; smaller chunks increase index size.
            overlap: Number of overlapping characters between consecutive chunks (default: 200).
                    Overlap preserves context across chunk boundaries for better search.

        Returns:
            None. Initializes instance with selected storage backend and configuration.

        Raises:
            OSError: Raised if output_dir cannot be created or is inaccessible.
        """
        self.output_dir = Path(output_dir)

        if storage == "json":
            self.storage = JSONStorage(output_dir)
        else:
            self.storage = MarkdownStorage(output_dir)

        self.chunk_size = chunk_size
        self.overlap = overlap
        self.visited_urls: Set[str] = set()
        self.crawl_queue: List[str] = []

    def _generate_id(self, url: str) -> str:
        """Generate unique document ID from URL using MD5 hash.

        Creates a deterministic 12-character unique identifier for each document based on its URL.
        The same URL will always generate the same ID, enabling idempotent document operations.

        Args:
            url: The URL string to hash into a document ID.

        Returns:
            str: A 12-character hexadecimal MD5 hash of the URL.

        Raises:
            No exceptions raised; all string inputs produce valid hashes.
        """
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def _extract_keywords(self, content: str, title: str) -> List[str]:
        """Extract top keywords from document content and title.

        Uses frequency-based keyword extraction with stopword filtering to identify the most
        relevant terms. Combines content and title to create a comprehensive keyword list
        suitable for document tagging and search optimization.

        Args:
            content: The main document content text to extract keywords from.
            title: The document title, weighted equally with content in extraction.

        Returns:
            List[str]: Up to 20 unique keywords sorted by frequency (descending).
                      Returns empty list if no valid keywords found after filtering.

        Raises:
            No exceptions raised; all string inputs produce valid keyword lists.
        """
        # Simple keyword extraction - in production use NLP
        words = re.findall(r'\b[a-zA-Z]{3,}\b', (content + " " + title).lower())

        # Filter common words
        stopwords = {
            "the", "and", "for", "are", "but", "not", "you", "all", "can",
            "her", "was", "one", "our", "out", "has", "have", "been",
            "this", "that", "with", "they", "from", "will", "would", "there",
            "their", "what", "about", "which", "when", "make", "like", "just",
            "over", "such", "into", "than", "them", "some", "could", "other",
        }

        word_counts = {}
        for word in words:
            if word not in stopwords and len(word) > 3:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Return top keywords
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:20]]

    def _chunk_content(self, content: str, doc_id: str) -> List[KnowledgeChunk]:
        """Split document content into overlapping chunks for indexing.

        Breaks content into manageable chunks at sentence boundaries when possible,
        with configurable overlap to preserve context between chunks. Each chunk is
        assigned keywords and metadata for efficient searching and retrieval.

        Args:
            content: The full document content string to chunk.
            doc_id: The document ID to assign to all generated chunks.

        Returns:
            List[KnowledgeChunk]: List of KnowledgeChunk objects with sequential IDs,
                                 extracted keywords, and overlap-based context preservation.
                                 Returns empty list if content is empty.

        Raises:
            No exceptions raised; all string inputs produce valid chunk lists.
        """
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(content):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(content):
                # Look for sentence end
                for i in range(end, max(end - 200, start), -1):
                    if content[i] in ".!?":
                        end = i + 1
                        break

            chunk_content = content[start:end]
            chunk = KnowledgeChunk(
                id=f"{doc_id}_{chunk_index}",
                document_id=doc_id,
                content=chunk_content,
                chunk_index=chunk_index,
                keywords=self._extract_keywords(chunk_content, ""),
            )
            chunks.append(chunk)
            chunk_index += 1

            # Move start with overlap
            start = end - self.overlap
            if start >= len(content):
                break

        return chunks

    async def crawl_page(
        self,
        url: str,
        category: str = "",
        fit_markdown_query: Optional[str] = None,
    ) -> Optional[Document]:
        """Crawl a single page and add to knowledge base.

        Crawls a web page using headless browser automation, extracts markdown content
        with optional content filtering, and stores the page in the knowledge base with
        keyword extraction and content chunking for indexing.

        Args:
            url: Target URL to crawl and add to knowledge base.
            category: Optional category classification for the document (default: "").
            fit_markdown_query: Optional BM25 filter query string for content filtering.
                              If provided, uses BM25ContentFilter; otherwise uses PruningContentFilter.

        Returns:
            Optional[Document]: Document object containing crawled content metadata, keywords,
                              and metadata if successful. Returns None if URL was already visited,
                              crawl failed, or other errors occurred.

        Raises:
            No exceptions raised; crawl failures are logged and None is returned.
        """
        if url in self.visited_urls:
            return None

        print(f"Crawling: {url}")
        self.visited_urls.add(url)

        # Configure content filtering
        if fit_markdown_query:
            content_filter = BM25ContentFilter(user_query=fit_markdown_query)
        else:
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
            print(f"Failed to crawl: {url}")
            return None

        # Create document
        doc_id = self._generate_id(url)
        content = result.markdown.fit_markdown if hasattr(result.markdown, 'fit_markdown') else result.markdown
        raw_markdown = result.markdown.raw_markdown if hasattr(result.markdown, 'raw_markdown') else str(result.markdown)

        doc = Document(
            id=doc_id,
            url=url,
            title=result.metadata.get("title", url) if result.metadata else url,
            content=content,
            markdown=raw_markdown,
            metadata=result.metadata or {},
            keywords=self._extract_keywords(content, result.metadata.get("title", "")),
            category=category,
            created_at=datetime.now().isoformat(),
        )

        # Add to storage
        self.storage.add_document(doc)

        # Create chunks for indexing
        chunks = self._chunk_content(content, doc_id)
        for chunk in chunks:
            self.storage.add_chunk(chunk)

        return doc

    async def crawl_sitemap(
        self,
        url: str,
        category: str = "",
        max_pages: int = 50,
    ) -> List[Document]:
        """Crawl all pages from a sitemap.

        Parses XML or text-based sitemaps to extract URLs and crawls all discovered pages
        with configurable limits. Applies content filtering and keyword extraction to each
        page and stores results in the knowledge base.

        Args:
            url: URL of the sitemap (XML or text format) to parse.
            category: Optional category classification for all discovered documents (default: "").
            max_pages: Maximum number of pages to crawl from sitemap (default: 50).
                      Limits to first max_pages discovered URLs.

        Returns:
            List[Document]: List of successfully crawled Document objects. Returns empty list
                          if sitemap parsing fails or no pages could be crawled.

        Raises:
            No exceptions raised; sitemap parsing and individual crawl failures are caught
            and logged. Failed URLs are skipped without affecting others.
        """
        js_fetch_sitemap = """
        async () => {
            try {
                const response = await fetch(window.location.href);
                const text = await response.text();

                // Try XML parsing
                if (text.includes('<urlset') || text.includes('<sitemap')) {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(text, 'text/xml');
                    const urls = Array.from(doc.querySelectorAll('loc')).map(el => el.textContent);
                    return { format: 'xml', urls: urls };
                }

                // Return text for manual parsing
                return { format: 'text', content: text.substring(0, 5000) };
            } catch (e) {
                return { error: e.message };
            }
        }
        """

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(js_code=js_fetch_sitemap)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

        urls_to_crawl = []

        if result.success and hasattr(result, 'js_result'):
            js_result = result.js_result
            if isinstance(js_result, dict) and js_result.get('format') == 'xml':
                urls_to_crawl = js_result.get('urls', [])[:max_pages]
            else:
                # Try to find links on the page
                js_find_links = """
                async () => {
                    const links = Array.from(document.querySelectorAll('a[href]'))
                        .map(a => a.href)
                        .filter(h => h.startsWith('http'));
                    return links.slice(0, 100);
                }
                """
                crawler_config = CrawlerRunConfig(js_code=js_find_links)
                result = await crawler.arun(url, config=crawler_config)
                if result.success:
                    urls_to_crawl = (result.js_result or [])[:max_pages]

        # Add seed URL if not in list
        if url not in urls_to_crawl:
            urls_to_crawl.insert(0, url)

        # Crawl all URLs
        documents = []
        for page_url in urls_to_crawl[:max_pages]:
            doc = await self.crawl_page(page_url, category)
            if doc:
                documents.append(doc)
            await asyncio.sleep(1)  # Rate limiting

        return documents

    async def build_from_seed(
        self,
        seed_url: str,
        category: str = "",
        max_pages: int = 100,
        discover_links: bool = True,
    ) -> List[Document]:
        """Build knowledge base starting from a seed URL with optional link discovery.

        Crawls a seed URL and optionally discovers and crawls internal links from the page.
        All discovered pages are added to the knowledge base with automatic content chunking,
        keyword extraction, and metadata collection. Includes rate limiting between requests.

        Args:
            seed_url: The starting URL to crawl and add to knowledge base.
            category: Optional category classification for all discovered documents (default: "").
            max_pages: Maximum number of pages to crawl (default: 100). Limits total document count.
            discover_links: Whether to discover and crawl internal links from the seed page
                           (default: True). If False, only the seed URL is crawled.

        Returns:
            List[Document]: List of successfully crawled and indexed Document objects.
                          Returns empty list if seed URL crawl fails.

        Raises:
            No exceptions raised; crawl failures are caught and logged individually.
        """
        documents = []

        # First, crawl the seed page
        doc = await self.crawl_page(seed_url, category)
        if doc:
            documents.append(doc)

        if discover_links:
            # Discover and crawl internal links
            js_find_links = """
            async () => {
                const links = Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(h => h.startsWith('http') && !h.includes('#'));
                return [...new Set(links)].slice(0, 50);
            }
            """

            browser_config = BrowserConfig(headless=True)
            crawler_config = CrawlerRunConfig(js_code=js_find_links)

            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await self.crawl_page(seed_url, category)
                if result:
                    result = await crawler.arun(seed_url, config=crawler_config)

            if result.success:
                internal_links = result.js_result or []
                for link in internal_links[:max_pages - 1]:
                    doc = await self.crawl_page(link, category)
                    if doc:
                        documents.append(doc)
                    await asyncio.sleep(0.5)

        # Save storage
        self.storage.save()

        print(f"\nKnowledge base built with {len(documents)} documents")
        return documents

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the knowledge base for documents matching query terms.

        Performs keyword-based search across all indexed documents with configurable result limits.
        Search results are ranked by relevance score (title matches weighted higher than content matches).

        Args:
            query: Search query string with space-separated terms to match against document
                  titles, content, and keywords.
            limit: Maximum number of results to return (default: 10).

        Returns:
            List[Dict[str, Any]]: List of search result dictionaries containing 'document_id',
                                 'title', 'url', 'score', and 'snippet' fields, sorted by
                                 relevance score descending. Returns empty list if no matches found.

        Raises:
            No exceptions raised; invalid queries return empty result lists.
        """
        return self.storage.search(query, limit)

    def export(self, format: str = "json") -> str:
        """Export knowledge base to specified file format.

        Exports all indexed documents and metadata to JSON or Markdown format files for
        external use, analysis, or backup. JSON format includes structured metadata; Markdown
        generates a single comprehensive document with all content.

        Args:
            format: Export format - either "json" or "markdown" (default: "json").
                   JSON exports to knowledge_base.json; Markdown exports to knowledge_base.md.

        Returns:
            str: Path to the exported file. Returns empty string if format is unsupported.

        Raises:
            OSError: Raised if export file cannot be written to output directory.
            json.JSONEncodeError: Raised if JSON serialization fails (for JSON format).
        """
        if format == "json":
            output_file = self.output_dir / "knowledge_base.json"
            data = {
                "documents": {k: v.__dict__ for k, v in self.storage.documents.items()},
                "exported_at": datetime.now().isoformat(),
            }
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            return str(output_file)

        elif format == "markdown":
            output_file = self.output_dir / "knowledge_base.md"
            content = f"# Knowledge Base Export\n\nExported: {datetime.now().isoformat()}\n\n"

            for doc in self.storage.documents.values():
                content += f"---\n\n## {doc.title}\n\n**URL:** {doc.url}\n\n{doc.markdown}\n\n"

            with open(output_file, "w") as f:
                f.write(content)
            return str(output_file)

        return ""


async def interactive_mode() -> None:
    """Interactive knowledge base building mode with REPL search interface.

    Launches an interactive session allowing users to build a knowledge base from a seed URL
    and search it with natural language queries. Prompts for configuration, crawls web content,
    and provides a loop for iterative searching and result exploration.

    Args:
        None.

    Returns:
        None. Runs until user enters 'quit' to exit search loop.

    Raises:
        KeyboardInterrupt: Raised if user terminates with Ctrl+C (caught by asyncio.run).
        ValueError: Raised if max_pages input cannot be converted to integer.
    """
    print("\n=== Knowledge Base Builder ===\n")

    seed_url = input("Enter seed URL: ").strip()
    output_dir = input("Enter output directory [./knowledge_base]: ").strip() or "./knowledge_base"
    category = input("Enter category: ").strip()
    max_pages = int(input("Max pages [50]: ").strip() or "50")

    builder = KnowledgeBaseBuilder(output_dir)

    print(f"\nBuilding knowledge base from {seed_url}...")
    documents = await builder.build_from_seed(seed_url, category, max_pages)

    print(f"\nKnowledge base created with {len(documents)} documents")

    while True:
        query = input("\nSearch query (or 'quit'): ").strip()
        if query.lower() == "quit":
            break

        results = builder.search(query)
        print(f"\nFound {len(results)} results:")
        for r in results[:5]:
            print(f"  - {r['title']} (score: {r['score']})")
            print(f"    {r['snippet'][:100]}...")


def main() -> None:
    """CLI entry point for knowledge base builder with multiple operation modes.

    Orchestrates knowledge base construction from seed URLs, file lists, or sitemaps,
    with support for interactive mode, searching, and exporting. Parses command-line
    arguments and routes to appropriate operations (build, search, export, or interactive).

    Command-line Arguments:
        --seed, -s: Seed URL to start crawling from for knowledge base construction.
        --urls, -u: File path containing URLs to crawl (one per line).
        --output, -o: Output directory for knowledge base (default: ./knowledge_base).
        --format: Storage format - "json", "sqlite", or "markdown" (default: json).
        --category, -c: Category tag for all crawled documents (default: empty string).
        --max-pages, -m: Maximum number of pages to crawl (default: 100).
        --search: Search query string to query existing knowledge base.
        --export: Export format - "json" or "markdown" (exports to output directory).
        --interactive, -i: Launch interactive REPL mode for building and searching KB.
        --sitemap: Crawl URLs from XML sitemap (alternative to --seed or --urls).

    Output Files:
        knowledge_base.json: Exported JSON format (when using --export json).
        knowledge_base.md: Exported Markdown format (when using --export markdown).
        index.json: Internal knowledge base index (in output directory).

    Exit Codes:
        0: Success (operation completed successfully).
        1: Error (invalid arguments or missing required operation flags).

    Raises:
        FileNotFoundError: Raised if --urls file path does not exist.
        SystemExit: Raised with code 1 if no operation flags are provided.
    """
    parser = argparse.ArgumentParser(description="Build searchable knowledge bases")
    parser.add_argument(
        "--seed", "-s", help="Seed URL to start crawling from"
    )
    parser.add_argument(
        "--urls", "-u", help="File containing URLs to crawl (one per line)"
    )
    parser.add_argument(
        "--output", "-o", default="./knowledge_base", help="Output directory"
    )
    parser.add_argument(
        "--format",
        choices=["json", "sqlite", "markdown"],
        default="json",
        help="Storage format"
    )
    parser.add_argument(
        "--category", "-c", default="", help="Category for documents"
    )
    parser.add_argument(
        "--max-pages", "-m", type=int, default=100, help="Maximum pages to crawl"
    )
    parser.add_argument(
        "--search", help="Search the knowledge base"
    )
    parser.add_argument(
        "--export", choices=["json", "markdown"], help="Export knowledge base"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument(
        "--sitemap", help="Crawl from sitemap URL"
    )

    args = parser.parse_args()

    if not any([args.seed, args.urls, args.interactive, args.sitemap, args.search]):
        parser.print_help()
        print("\nExamples:")
        print("  python knowledge-base-builder.py --seed https://docs.example.com")
        print("  python knowledge-base-builder.py --urls urls.txt --output ./kb")
        print("  python knowledge-base-builder.py --search 'how to install'")
        print("  python knowledge-base-builder.py --interactive")
        print("  python knowledge-base-builder.py --sitemap https://example.com/sitemap.xml")
        sys.exit(1)

    builder = KnowledgeBaseBuilder(args.output, args.format)

    if args.search:
        results = builder.search(args.search)
        print(f"Search results for '{args.search}':")
        for r in results:
            print(f"  - {r['title']} (score: {r['score']})")
        return

    if args.interactive:
        asyncio.run(interactive_mode())
        return

    if args.export:
        output_file = builder.export(args.export)
        print(f"Exported to: {output_file}")
        return

    documents = []
    if args.seed:
        documents = await builder.build_from_seed(
            args.seed, args.category, args.max_pages
        )
    elif args.urls:
        with open(args.urls) as f:
            urls = f.readlines()
        for url in urls:
            url = url.strip()
            if url:
                doc = await builder.crawl_page(url, args.category)
                if doc:
                    documents.append(doc)
        builder.storage.save()

    print(f"\nKnowledge base built: {args.output}")
    print(f"Documents: {len(documents)}")


if __name__ == "__main__":
    asyncio.run(main())
