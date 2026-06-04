#!/usr/bin/env python3
"""
Crawl4AI extraction pipeline - Three approaches:
1. Generate schema with LLM (one-time) then use CSS extraction (most efficient)
2. Manual CSS/JSON schema extraction
3. Direct LLM extraction (for complex/irregular content)

Usage examples:
  Generate schema: python extraction_pipeline.py --generate-schema <url> "<instruction>"
  Use generated schema: python extraction_pipeline.py --use-schema <url> schema.json
  Manual CSS: python extraction_pipeline.py --css <url> "<css_selector>"
  Direct LLM: python extraction_pipeline.py --llm <url> "<instruction>"
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Version check
MIN_CRAWL4AI_VERSION = "0.7.4"
try:
    from crawl4ai.__version__ import __version__
    from packaging import version
    if version.parse(__version__) < version.parse(MIN_CRAWL4AI_VERSION):
        print(f"⚠️  Warning: Crawl4AI {MIN_CRAWL4AI_VERSION}+ recommended (you have {__version__})")
except ImportError:
    print(f"ℹ️  Crawl4AI {MIN_CRAWL4AI_VERSION}+ required")

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import (
    LLMExtractionStrategy,
    JsonCssExtractionStrategy,
    CosineStrategy
)

# =============================================================================
# APPROACH 1: Generate Schema (Most Efficient for Repetitive Patterns)
# =============================================================================

async def generate_schema(url: str, instruction: str, output_file: str = "generated_schema.json") -> Optional[Dict[str, Any]]:
    """Generate a reusable extraction schema using LLM analysis.

    Analyzes webpage structure and generates CSS/JSON schema for data extraction.
    Best for repetitive patterns found in e-commerce, blogs, and news sites.

    Args:
        url: Target URL to analyze for schema generation.
        instruction: Task description for LLM to generate appropriate schema.
        output_file: Path where generated schema will be saved (default: generated_schema.json).

    Returns:
        Dictionary containing generated extraction schema with selectors and field definitions.

    Raises:
        OSError: If schema file cannot be written.
    """
    print("🔍 Generating extraction schema using LLM...")

    browser_config = BrowserConfig(headless=True)

    # Use LLM to analyze the page structure and generate schema
    extraction_strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",  # Can use any LLM provider
        instruction=f"""
        Analyze this webpage and generate a CSS/JSON extraction schema.
        Task: {instruction}

        Return a JSON schema with CSS selectors that can extract the required data.
        Format:
        {{
            "name": "items",
            "selector": "main_container_selector",
            "fields": [
                {{"name": "field1", "selector": "css_selector", "type": "text"}},
                {{"name": "field2", "selector": "css_selector", "type": "link"}},
                // more fields...
            ]
        }}

        Make selectors as specific as possible to avoid false matches.
        """
    )

    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        wait_for="css:body",
        remove_overlay_elements=True
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

        if result.success and result.extracted_content:
            try:
                # Parse and save the generated schema
                schema = json.loads(result.extracted_content)

                # Validate and enhance schema
                if "name" not in schema:
                    schema["name"] = "items"
                if "fields" not in schema:
                    print("⚠️ Generated schema missing fields, using fallback")
                    schema = {
                        "name": "items",
                        "baseSelector": "div.item, article, .product",
                        "fields": [
                            {"name": "title", "selector": "h1, h2, h3", "type": "text"},
                            {"name": "description", "selector": "p", "type": "text"},
                            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
                        ]
                    }

                # Save schema
                with open(output_file, "w") as f:
                    json.dump(schema, f, indent=2)

                print(f"✅ Schema generated and saved to: {output_file}")
                print(f"📋 Schema structure:")
                print(json.dumps(schema, indent=2))

                return schema

            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse generated schema: {e}")
                print("Raw output:", result.extracted_content[:500])
                return None
        else:
            print(f"❌ Failed to generate schema: {result.error_message if result else 'Unknown error'}")
            return None

async def use_generated_schema(url: str, schema_file: str) -> Optional[Dict[str, Any]]:
    """Use a previously generated extraction schema for fast, repeated data extraction.

    Loads a pre-generated CSS/JSON schema from file and applies it to extract data
    from a webpage without any LLM API calls. This is the most cost-efficient approach
    for repetitive extraction patterns once a schema has been generated.

    Args:
        url: Target URL to extract data from using the schema.
        schema_file: Path to the JSON file containing the extraction schema.

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing extracted data structured according
            to the schema. Returns None if schema file is not found or extraction fails.
            Extracted data is also saved to 'extracted_data.json'.

    Raises:
        FileNotFoundError: Raised if schema_file path does not exist or cannot be read.
        json.JSONDecodeError: Raised if schema file contains invalid JSON.
    """
    print(f"📂 Loading schema from: {schema_file}")

    try:
        with open(schema_file, "r") as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"❌ Schema file not found: {schema_file}")
        print("💡 Generate a schema first using: python extraction_pipeline.py --generate-schema <url> \"<instruction>\"")
        return None

    print("🚀 Extracting data using generated schema (no LLM calls)...")

    extraction_strategy = JsonCssExtractionStrategy(
        schema=schema,
        verbose=True
    )

    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        wait_for="css:body"
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

        if result.success and result.extracted_content:
            data = json.loads(result.extracted_content)
            items = data.get(schema.get("name", "items"), [])

            print(f"✅ Extracted {len(items)} items using schema")

            # Save results
            with open("extracted_data.json", "w") as f:
                json.dump(data, f, indent=2)
            print("💾 Saved to extracted_data.json")

            # Show sample
            if items:
                print("\n📋 Sample (first item):")
                print(json.dumps(items[0], indent=2))

            return data
        else:
            print(f"❌ Extraction failed: {result.error_message if result else 'Unknown error'}")
            return None

# =============================================================================
# APPROACH 2: Manual Schema Definition
# =============================================================================

async def extract_with_manual_schema(url: str, schema: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Use a manually defined CSS/JSON schema for data extraction.

    Demonstrates CSS/JSON-based extraction when the exact HTML structure of the
    website is known. Uses JsonCssExtractionStrategy with predefined selectors
    to extract structured data without requiring LLM API calls.

    Args:
        url: Target URL to extract data from using the provided schema.
        schema: Optional dictionary containing CSS/JSON schema definition. If not provided,
                uses a generic example schema extracting title, paragraphs, and links.
                Schema format: {"name": str, "baseSelector": str, "fields": List[Dict]}

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing extracted data structured according
            to the schema. Returns None if extraction fails. Data is also saved to
            'manual_extracted.json' on successful extraction.

    Raises:
        json.JSONDecodeError: Raised if extraction result cannot be parsed as JSON.
        FileNotFoundError: Raised if file writing to manual_extracted.json fails.
    """

    if not schema:
        # Example schema for general content extraction
        schema = {
            "name": "content",
            "baseSelector": "body",  # Changed from 'selector' to 'baseSelector'
            "fields": [
                {"name": "title", "selector": "h1", "type": "text"},
                {"name": "paragraphs", "selector": "p", "type": "text", "all": True},
                {"name": "links", "selector": "a", "type": "attribute", "attribute": "href", "all": True}
            ]
        }

    print("📐 Using manual CSS/JSON schema for extraction...")

    extraction_strategy = JsonCssExtractionStrategy(
        schema=schema,
        verbose=True
    )

    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

        if result.success and result.extracted_content:
            data = json.loads(result.extracted_content)
            # Handle both list and dict formats
            if isinstance(data, list):
                items = data
            else:
                items = data.get(schema["name"], [])

            print(f"✅ Extracted {len(items)} items using manual schema")

            with open("manual_extracted.json", "w") as f:
                json.dump(data, f, indent=2)
            print("💾 Saved to manual_extracted.json")

            return data
        else:
            print(f"❌ Extraction failed")
            return None

# =============================================================================
# APPROACH 3: Direct LLM Extraction
# =============================================================================

async def extract_with_llm(url: str, instruction: str) -> Optional[Dict[str, Any]]:
    """Extract structured data using direct LLM analysis without predefined schemas.

    Uses LLM (GPT-4o-mini by default) to analyze webpage content and extract data
    according to natural language instructions. Most flexible approach but also
    most expensive; recommended for complex or irregular content patterns that
    resist CSS-based extraction.

    Args:
        url: Target URL to extract data from using LLM analysis.
        instruction: Natural language instruction describing what data to extract.
                    Examples: "Extract all product names and prices",
                    "Find contact information and business hours"

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing extracted data with 'items' array
            and optional 'summary' field. Returns None if extraction fails or if LLM
            output cannot be parsed as JSON. Successful extractions are saved to
            'llm_extracted.json'.

    Raises:
        json.JSONDecodeError: Raised if LLM output cannot be parsed as valid JSON.
        FileNotFoundError: Raised if file writing to llm_extracted.json fails.
    """
    print("🤖 Using direct LLM extraction...")

    browser_config = BrowserConfig(headless=True)

    extraction_strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",  # Can change to ollama/llama3, anthropic/claude, etc.
        instruction=instruction,
        schema={
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "object"}
                },
                "summary": {"type": "string"}
            }
        }
    )

    crawler_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        wait_for="css:body",
        remove_overlay_elements=True
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

        if result.success and result.extracted_content:
            try:
                data = json.loads(result.extracted_content)
                items = data.get('items', [])

                print(f"✅ LLM extracted {len(items)} items")
                print(f"📝 Summary: {data.get('summary', 'N/A')}")

                with open("llm_extracted.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("💾 Saved to llm_extracted.json")

                if items:
                    print("\n📋 Sample (first item):")
                    print(json.dumps(items[0], indent=2))

                return data
            except json.JSONDecodeError:
                print("⚠️ Could not parse LLM output as JSON")
                print(result.extracted_content[:500])
                return None
        else:
            print(f"❌ LLM extraction failed")
            return None

# =============================================================================
# Main CLI Interface
# =============================================================================

async def main() -> None:
    """CLI entry point for the Crawl4AI extraction pipeline.

    Orchestrates three distinct extraction approaches:
    1. Generate schema (one-time LLM cost) then use for repeated extraction
    2. Manual CSS/JSON schema when webpage structure is known
    3. Direct LLM extraction for complex or irregular content

    Command-line Arguments:
        --generate-schema <url> "<instruction>" [output_file]
            Generate a reusable extraction schema using LLM analysis.
            output_file defaults to "generated_schema.json"

        --use-schema <url> <schema.json>
            Use a previously generated schema for cost-efficient extraction.

        --manual <url>
            Extract using a manually defined schema (edit schema in code).

        --llm <url> "<instruction>"
            Direct LLM extraction with natural language instructions.

    Exit Codes:
        0: Success (extraction completed, may have errors in output)
        1: Error (invalid arguments or missing required parameters)

    Raises:
        SystemExit: With code 0 or 1 depending on argument validation.
    """
    if len(sys.argv) < 3:
        print("""
Crawl4AI Extraction Pipeline - Three Approaches

1️⃣  GENERATE & USE SCHEMA (Most Efficient for Repetitive Patterns):
    Step 1: Generate schema (one-time LLM cost)
    python extraction_pipeline.py --generate-schema <url> "<what to extract>"

    Step 2: Use schema for fast extraction (no LLM)
    python extraction_pipeline.py --use-schema <url> generated_schema.json

2️⃣  MANUAL SCHEMA (When You Know the Structure):
    python extraction_pipeline.py --manual <url>
    (Edit the schema in the script for your needs)

3️⃣  DIRECT LLM (For Complex/Irregular Content):
    python extraction_pipeline.py --llm <url> "<extraction instruction>"

Examples:
    # E-commerce products
    python extraction_pipeline.py --generate-schema https://shop.com "Extract all products with name, price, image"
    python extraction_pipeline.py --use-schema https://shop.com generated_schema.json

    # News articles
    python extraction_pipeline.py --generate-schema https://news.com "Extract headlines, dates, and summaries"

    # Complex content
    python extraction_pipeline.py --llm https://complex-site.com "Extract financial data and quarterly reports"
""")
        sys.exit(1)

    mode = sys.argv[1]
    url = sys.argv[2]

    if mode == "--generate-schema":
        if len(sys.argv) < 4:
            print("Error: Missing extraction instruction")
            print("Usage: python extraction_pipeline.py --generate-schema <url> \"<instruction>\"")
            sys.exit(1)
        instruction = sys.argv[3]
        output_file = sys.argv[4] if len(sys.argv) > 4 else "generated_schema.json"
        await generate_schema(url, instruction, output_file)

    elif mode == "--use-schema":
        if len(sys.argv) < 4:
            print("Error: Missing schema file")
            print("Usage: python extraction_pipeline.py --use-schema <url> <schema.json>")
            sys.exit(1)
        schema_file = sys.argv[3]
        await use_generated_schema(url, schema_file)

    elif mode == "--manual":
        await extract_with_manual_schema(url)

    elif mode == "--llm":
        if len(sys.argv) < 4:
            print("Error: Missing extraction instruction")
            print("Usage: python extraction_pipeline.py --llm <url> \"<instruction>\"")
            sys.exit(1)
        instruction = sys.argv[3]
        await extract_with_llm(url, instruction)

    else:
        print(f"Unknown mode: {mode}")
        print("Use --generate-schema, --use-schema, --manual, or --llm")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())