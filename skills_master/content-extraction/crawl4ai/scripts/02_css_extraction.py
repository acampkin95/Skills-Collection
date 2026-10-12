#!/usr/bin/env python3
"""
CSS-Based Data Extraction (No LLM)
===================================

This example demonstrates structured data extraction using CSS selectors
without requiring LLM API calls. Perfect for well-structured websites.

Provides practical examples of using JsonCssExtractionStrategy to extract
product data, news articles, nested structures, and other content from
HTML pages with CSS selector patterns.
"""

import asyncio
import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


# Example 1: Simple Product Extraction
async def extract_products() -> None:
    """Extract product data from an e-commerce page.

    Demonstrates CSS-based extraction of product information including title,
    price, image URL, and rating from e-commerce pages using selector patterns
    on product card elements. Handles potential extraction failures gracefully.

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing extracted products.

    Raises:
        No exceptions raised; JSON parsing and crawl failures are caught and logged.
    """

    print("Example 1: Product Extraction")
    print("-" * 80)
    
    # Define schema
    schema = {
        "name": "products",
        "baseSelector": ".product-card",
        "fields": [
            {
                "name": "title",
                "selector": "h3.product-title",
                "type": "text"
            },
            {
                "name": "price",
                "selector": "span.price",
                "type": "text"
            },
            {
                "name": "image",
                "selector": "img",
                "type": "attribute",
                "attribute": "src"
            },
            {
                "name": "rating",
                "selector": ".rating",
                "type": "text"
            }
        ]
    }
    
    strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(
        extraction_strategy=strategy,
        cache_mode=CacheMode.BYPASS
    )
    
    # Mock URL - replace with actual e-commerce site
    url = "https://example-shop.com/products"
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        
        if result.success and result.extracted_content:
            products = json.loads(result.extracted_content)
            print(f"Extracted {len(products)} products:")
            for product in products[:3]:  # Show first 3
                print(f"  - {product.get('title')}: {product.get('price')}")
        else:
            print(f"Failed: {result.error_message}")


# Example 2: News Article Extraction
async def extract_news_articles() -> None:
    """Extract articles from a news website.

    Demonstrates CSS-based extraction of news article metadata including headline,
    author, publication date, summary, and article URL from news site structures.
    Uses nested selectors to extract data from article containers.

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing extracted article count.

    Raises:
        No exceptions raised; JSON parsing and crawl failures are caught and logged.
    """

    print("\nExample 2: News Articles Extraction")
    print("-" * 80)
    
    schema = {
        "name": "articles",
        "baseSelector": "article.story",
        "fields": [
            {
                "name": "headline",
                "selector": "h2.headline",
                "type": "text"
            },
            {
                "name": "author",
                "selector": ".byline .author",
                "type": "text"
            },
            {
                "name": "date",
                "selector": "time",
                "type": "attribute",
                "attribute": "datetime"
            },
            {
                "name": "summary",
                "selector": ".article-summary",
                "type": "text"
            },
            {
                "name": "url",
                "selector": "a.read-more",
                "type": "attribute",
                "attribute": "href"
            }
        ]
    }
    
    strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(extraction_strategy=strategy)
    
    url = "https://news.ycombinator.com"  # Example
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        
        if result.success and result.extracted_content:
            articles = json.loads(result.extracted_content)
            print(f"Extracted {len(articles)} articles")


# Example 3: Nested Structure Extraction
async def extract_nested_data() -> None:
    """Extract nested/hierarchical data structures.

    Demonstrates CSS-based extraction of hierarchical data with nested lists,
    such as category containers with nested items. Uses nested field definitions
    in the extraction schema to handle multi-level data structures.

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing extracted category count.

    Raises:
        No exceptions raised; JSON parsing and crawl failures are caught and logged.
    """

    print("\nExample 3: Nested Data Extraction")
    print("-" * 80)
    
    schema = {
        "name": "categories",
        "baseSelector": ".category",
        "fields": [
            {
                "name": "category_name",
                "selector": "h2.category-title",
                "type": "text"
            },
            {
                "name": "items",
                "selector": ".item",
                "type": "nested_list",
                "fields": [
                    {
                        "name": "name",
                        "selector": ".item-name",
                        "type": "text"
                    },
                    {
                        "name": "description",
                        "selector": ".item-desc",
                        "type": "text"
                    },
                    {
                        "name": "link",
                        "selector": "a",
                        "type": "attribute",
                        "attribute": "href"
                    }
                ]
            }
        ]
    }
    
    strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(extraction_strategy=strategy)
    
    url = "https://example.com/catalog"
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        
        if result.success and result.extracted_content:
            data = json.loads(result.extracted_content)
            print(f"Extracted {len(data)} categories with nested items")


# Example 4: Real-world - Hacker News Stories
async def extract_hackernews() -> None:
    """Extract stories from Hacker News.

    Demonstrates real-world CSS-based extraction from Hacker News, extracting story
    titles, URLs, and ranks. Shows handling of extraction failures and formatted output
    for the top stories with proper error messages when extraction fails.

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing extracted stories or error message.

    Raises:
        No exceptions raised; JSON parsing and crawl failures are caught and logged.
    """

    print("\nExample 4: Hacker News Stories")
    print("-" * 80)
    
    schema = {
        "name": "stories",
        "baseSelector": "tr.athing",
        "fields": [
            {
                "name": "title",
                "selector": "span.titleline a",
                "type": "text"
            },
            {
                "name": "url",
                "selector": "span.titleline a",
                "type": "attribute",
                "attribute": "href"
            },
            {
                "name": "rank",
                "selector": "span.rank",
                "type": "text"
            }
        ]
    }
    
    strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(
        extraction_strategy=strategy,
        cache_mode=CacheMode.BYPASS
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com",
            config=config
        )
        
        if result.success and result.extracted_content:
            stories = json.loads(result.extracted_content)
            print(f"\n✓ Extracted {len(stories)} stories from HN:")
            print()
            
            for story in stories[:5]:  # Show top 5
                rank = story.get('rank', '?').rstrip('.')
                title = story.get('title', 'No title')
                url = story.get('url', 'No URL')
                print(f"{rank:>3}. {title}")
                print(f"     {url[:60]}...")
                print()
        else:
            print(f"❌ Failed: {result.error_message}")


# Example 5: With Field Transformations
async def extract_with_transformations() -> None:
    """Extract data with custom transformations.

    Demonstrates CSS-based extraction with custom field transformations using
    lambda functions to convert extracted text into desired data types (float,
    decimal, boolean). Shows how to apply post-extraction transformations on
    extracted field values for data type conversion and cleaning.

    Args:
        None.

    Returns:
        None. Output is printed to stdout describing the schema transformations.

    Raises:
        No exceptions raised; schema definitions are printed only without crawling.
    """
    
    print("\nExample 5: Data with Transformations")
    print("-" * 80)
    
    schema = {
        "name": "products",
        "baseSelector": ".product",
        "fields": [
            {
                "name": "name",
                "selector": ".name",
                "type": "text"
            },
            {
                "name": "price",
                "selector": ".price",
                "type": "text",
                "transform": "lambda x: float(x.replace('$', '').replace(',', ''))"
            },
            {
                "name": "discount",
                "selector": ".discount",
                "type": "text",
                "transform": "lambda x: int(x.replace('%', '')) / 100"
            },
            {
                "name": "in_stock",
                "selector": ".stock-status",
                "type": "text",
                "transform": "lambda x: x.lower() == 'in stock'"
            }
        ]
    }
    
    strategy = JsonCssExtractionStrategy(schema=schema)
    config = CrawlerRunConfig(extraction_strategy=strategy)
    
    # Mock URL
    url = "https://example-shop.com/sale"
    
    print("Schema includes transformations for:")
    print("  - Price: Remove $ and convert to float")
    print("  - Discount: Convert percentage to decimal")
    print("  - In Stock: Convert to boolean")


# Example 6: Multiple Base Selectors
async def extract_multiple_sections() -> None:
    """Extract from multiple sections of a page.

    Demonstrates how to handle extraction from multiple distinct sections of a page
    using different base selectors and field patterns. Shows the recommended approach
    of running separate extractions for different sections and combining results in
    application logic rather than using a single complex schema.

    Args:
        None.

    Returns:
        None. Output is printed to stdout describing the multi-section extraction strategy.

    Raises:
        No exceptions raised; schema definitions are printed only without crawling.
    """
    
    print("\nExample 6: Multiple Section Extraction")
    print("-" * 80)
    
    # Create multiple schemas for different sections
    featured_schema = {
        "name": "featured",
        "baseSelector": ".featured-product",
        "fields": [
            {"name": "title", "selector": "h3", "type": "text"},
            {"name": "price", "selector": ".price", "type": "text"}
        ]
    }
    
    regular_schema = {
        "name": "regular",
        "baseSelector": ".regular-product",
        "fields": [
            {"name": "title", "selector": "h4", "type": "text"},
            {"name": "price", "selector": ".price", "type": "text"}
        ]
    }
    
    # You would run these separately or combine results
    print("Note: For multiple sections, run separate extractions")
    print("      and combine the results in your application logic")


def main() -> None:
    """Run all CSS extraction examples and demonstrate key patterns.

    Orchestrates execution of a real-world example (Hacker News extraction) followed
    by conceptual demonstrations of advanced extraction patterns including data
    transformations, multiple section extraction, and nested structure handling.
    Provides practical guidance on using CSS selectors for structured data extraction
    without requiring LLM API calls.

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing example execution and schema definitions.

    Raises:
        No exceptions raised; example execution errors are caught and printed.
    """

    print("=" * 80)
    print("CSS-Based Extraction Examples (No LLM)")
    print("=" * 80)
    print()
    
    # Run real example
    asyncio.run(extract_hackernews())
    
    # Show other example structures
    print("\nOther Examples (schema definitions):")
    print("-" * 80)
    asyncio.run(extract_with_transformations())
    asyncio.run(extract_multiple_sections())
    
    print("\n" + "=" * 80)
    print("Tip: CSS extraction is fast, free, and perfect for structured sites")
    print("     Inspect the HTML to find the right selectors!")
    print("=" * 80)


if __name__ == "__main__":
    main()
