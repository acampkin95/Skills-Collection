#!/usr/bin/env python3
"""
Schema Generator - Auto-generate extraction schemas from web page content.

This script analyzes web pages and automatically generates extraction schemas
for CSS/JSON extraction strategy. It uses LLM analysis to understand page
structure and create reusable schemas.

Usage:
    python schema-generator.py <url> "<description>" [--output <file>] [--format css|json]
    python schema-generator.py --interactive
    python schema-generator.py --batch urls.txt --save-schemas <dir>
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.extraction_strategy import LLMExtractionStrategy, JsonCssExtractionStrategy
except ImportError:
    print("Error: crawl4ai not installed. Run: pip install crawl4ai")
    sys.exit(1)


class SchemaGenerator:
    """Auto-generate extraction schemas from web content."""

    def __init__(self, output_dir: str = "./schemas") -> None:
        """Initialize schema generator with output directory.

        Creates the output directory if it doesn't exist for storing generated schemas.

        Args:
            output_dir: Directory path where generated schemas will be saved
                       (default: "./schemas").

        Returns:
            None.

        Raises:
            OSError: Raised if output directory cannot be created.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def analyze_page_structure(self, url: str) -> Dict[str, Any]:
        """Analyze the structure of a page to understand its layout and organization.

        Performs JavaScript-based structural analysis of a webpage to identify containers,
        lists, card elements, tables, forms, navigation, and semantic HTML elements.
        Returns a comprehensive structure dictionary for understanding page organization.

        Args:
            url: Target URL to analyze for structural patterns.

        Returns:
            Dict[str, Any]: Dictionary containing structural analysis with keys:
                - containers: List of main container elements with selector, tag, id, classes
                - lists: List of ul/ol elements with item counts
                - cards: Card-like elements (class*="card", "item", "product")
                - tables: Table elements with row/column counts
                - forms: Form elements detected on page
                - navigation: Navigation elements
                - semanticElements: Count of semantic HTML5 elements (header, nav, main, footer, etc.)
                Returns error dict if analysis fails.

        Raises:
            No exceptions raised; errors are returned in result dictionary with 'error' key.
        """
        js_analysis = """
        async () => {
            const structure = {
                containers: [],
                lists: [],
                cards: [],
                tables: [],
                forms: [],
                navigation: [],
                semanticElements: {}
            };

            // Find main containers
            const containerSelectors = ['main', 'article', 'section', 'aside', 'div.container', 'div.content'];
            containerSelectors.forEach(sel => {
                document.querySelectorAll(sel).forEach((el, i) => {
                    structure.containers.push({
                        selector: sel,
                        tag: el.tagName,
                        id: el.id,
                        classes: el.className,
                        childCount: el.children.length,
                        textContent: el.textContent?.substring(0, 200) || ''
                    });
                });
            });

            // Find list structures
            document.querySelectorAll('ul, ol').forEach((list, i) => {
                structure.lists.push({
                    tag: list.tagName,
                    itemCount: list.querySelectorAll('li').length,
                    classes: list.className
                });
            });

            // Find card structures (common patterns)
            document.querySelectorAll('[class*="card"], [class*="item"], [class*="product"]').forEach((el, i) => {
                if (el.children.length > 0) {
                    structure.cards.push({
                        tag: el.tagName,
                        classes: el.className,
                        childCount: el.children.length
                    });
                }
            });

            // Find tables
            document.querySelectorAll('table').forEach((table, i) => {
                structure.tables.push({
                    rows: table.querySelectorAll('tr').length,
                    columns: table.querySelectorAll('th').length,
                    classes: table.className
                });
            });

            // Semantic element counts
            const semantics = ['header', 'nav', 'main', 'footer', 'article', 'section'];
            semantics.forEach(tag => {
                structure.semanticElements[tag] = document.querySelectorAll(tag).length;
            });

            return structure;
        }
        """

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(js_code=js_analysis)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return result.js_result or {}

        return {"error": "Failed to analyze page structure"}

    async def generate_schema_with_llm(
        self,
        url: str,
        description: str,
        provider: str = "openai/gpt-4o-mini",
    ) -> Dict[str, Any]:
        """Generate extraction schema using LLM analysis of page content.

        Crawls a URL and uses LLM (Large Language Model) to analyze page structure
        and content, generating a JSON extraction schema with CSS selectors and field
        mappings. Falls back to basic schema generation if LLM extraction fails.

        Args:
            url: Target URL to analyze for schema generation.
            description: Human-readable description of what to extract from the page
                        (e.g., 'products from shop', 'blog articles').
            provider: LLM provider string in format 'provider/model'
                     (default: 'openai/gpt-4o-mini'). Examples: 'openai/gpt-4',
                     'anthropic/claude-3', 'google/gemini-pro'.

        Returns:
            Dict[str, Any]: Generated extraction schema with keys:
                - name: Normalized name derived from description
                - baseSelector: CSS selector for main container
                - fields: List of field definitions with name, selector, type, and optional attribute
                - source_url: Source URL or "auto-generated"
                - description: Original description provided
                - error: Error message if generation failed (optional)

        Raises:
            No exceptions raised; errors are returned in result dictionary with 'error' key.
        """
        # First, get page content for LLM analysis
        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(
            page_timeout=30000,
            wait_for="networkidle",
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if not result.success:
                return {"error": "Failed to crawl page"}

        # Use LLM to generate schema
        llm_prompt = f"""
        Analyze the following web page and create an extraction schema for {description}.

        Page URL: {url}
        Page Title: {result.metadata.get('title', 'Unknown') if result.metadata else 'Unknown'}

        Page Content (first 5000 chars):
        {result.markdown[:5000] if result.markdown else 'No content'}

        Based on this analysis, create a JSON extraction schema with the following structure:
        {{
            "name": "descriptive_name",
            "baseSelector": "CSS selector for main container",
            "fields": [
                {{
                    "name": "field_name",
                    "selector": "CSS selector",
                    "type": "text|html|attribute|number|date",
                    "attribute": "src|href|class etc. (optional)"
                }}
            ]
        }}

        Return ONLY the JSON schema, no other text.
        """

        extraction_strategy = LLMExtractionStrategy(
            provider=provider,
            instruction="Generate a JSON extraction schema from the provided page analysis. Output valid JSON only.",
        )

        schema_config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

        # Run LLM extraction with our prompt
        js_code = f"""
        async () => {{
            const prompt = `{llm_prompt.replace('`', '\\`')}`;
            return prompt;
        }}
        """

        crawler_config = CrawlerRunConfig(js_code=js_code)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

        # Parse the LLM response to get schema
        if result.success and hasattr(result, 'extracted_content'):
            try:
                schema = json.loads(result.extracted_content)
                return schema
            except json.JSONDecodeError:
                pass

        # Fallback: Generate basic schema from structure analysis
        structure = await self.analyze_page_structure(url)
        return self._generate_basic_schema(structure, description)

    def _generate_basic_schema(
        self, structure: Dict[str, Any], description: str
    ) -> Dict[str, Any]:
        """Generate a basic extraction schema from page structure analysis.

        Creates a fallback schema when LLM-based generation fails by analyzing the
        page structure to identify containers, cards, lists, and tables, then
        generating appropriate CSS selectors and field definitions.

        Args:
            structure: Dictionary containing page structure analysis with keys like
                      containers, cards, lists, tables from analyze_page_structure().
            description: Human-readable description of extraction intent used for
                        schema naming and metadata.

        Returns:
            Dict[str, Any]: Basic extraction schema with keys:
                - name: Normalized name from description (lowercase, underscores)
                - baseSelector: CSS selector for main container
                - fields: List of inferred field definitions with selectors and types
                - source_url: "auto-generated" marker
                - description: Original description provided

        Raises:
            No exceptions raised; always returns a valid schema dictionary.
        """
        # Try to find the best container selector
        containers = structure.get("containers", [])
        best_container = containers[0] if containers else {"selector": "article"}

        # Generate field suggestions based on structure
        fields = []

        if structure.get("cards"):
            fields.append({"name": "items", "selector": ".card, .item, [class*='card']", "type": "nested"})

        if structure.get("lists"):
            fields.append({"name": "list_items", "selector": "li", "type": "text"})

        if structure.get("tables"):
            fields.append({"name": "table_data", "selector": "tr", "type": "nested"})

        # Common fields
        common_fields = [
            {"name": "title", "selector": "h1, .title, [class*='title']", "type": "text"},
            {"name": "description", "selector": "p, .description, [class*='description']", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
        ]

        fields.extend(common_fields)

        return {
            "name": description.lower().replace(" ", "_"),
            "baseSelector": best_container.get("selector", "article"),
            "fields": fields,
            "source_url": "auto-generated",
            "description": description,
        }

    async def test_schema(
        self, url: str, schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test a generated schema on a target URL to validate extraction.

        Applies an extraction schema to a URL to validate that the CSS selectors
        and field definitions correctly extract data from the page. Useful for
        testing and refining schemas before deployment.

        Args:
            url: Target URL to test the schema extraction against.
            schema: Extraction schema dictionary with baseSelector and fields definitions.

        Returns:
            Dict[str, Any]: Test result dictionary with keys:
                - success: Boolean indicating if extraction succeeded
                - extracted_data: Extracted content from the URL (optional on success)
                - item_count: Number of items extracted (optional on success)
                - error: Error message if test failed (optional on failure)

        Raises:
            No exceptions raised; errors are returned in result dictionary with 'error' key.
        """
        extraction_strategy = JsonCssExtractionStrategy(schema=schema)

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
            page_timeout=30000,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return {
                    "success": True,
                    "extracted_data": result.extracted_content,
                    "item_count": len(result.extracted_content) if isinstance(result.extracted_content, list) else 1,
                }

        return {
            "success": False,
            "error": result.error_message if hasattr(result, 'error_message') else "Unknown error"
        }

    def save_schema(self, schema: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save extraction schema to JSON file.

        Serializes an extraction schema dictionary to a JSON file in the output directory.
        Auto-generates filename with timestamp if not provided.

        Args:
            schema: Extraction schema dictionary to save, typically containing keys like
                   name, baseSelector, and fields.
            filename: Optional output filename. If not provided, generates filename from
                     schema name and timestamp (e.g., products_schema-generator.json).

        Returns:
            str: Full file path to the saved schema JSON file.

        Raises:
            OSError: Raised if schema file cannot be written to output directory.
            TypeError: Raised if schema contains non-serializable objects.
        """
        if not filename:
            name = schema.get("name", "schema")
            timestamp = Path(__file__).stem
            filename = f"{name}_{timestamp}.json"

        filepath = self.output_dir / filename
        with open(filepath, "w") as f:
            json.dump(schema, f, indent=2)

        return str(filepath)

    def load_schema(self, filepath: str) -> Dict[str, Any]:
        """Load extraction schema from JSON file.

        Deserializes an extraction schema from a JSON file on disk.

        Args:
            filepath: Full or relative path to the schema JSON file to load.

        Returns:
            Dict[str, Any]: Extracted schema dictionary containing keys like name,
                          baseSelector, fields, source_url, and description.

        Raises:
            FileNotFoundError: Raised if the specified schema file does not exist.
            json.JSONDecodeError: Raised if the file contains invalid JSON.
            IOError: Raised if the file cannot be read due to permission or I/O errors.
        """
        with open(filepath) as f:
            return json.load(f)


async def interactive_mode() -> None:
    """Interactive schema generation mode with user prompts.

    Provides an interactive command-line interface for generating extraction schemas
    from web pages. Users can specify URLs and content descriptions, generate schemas
    using LLM analysis, save schemas to files, and test them on target URLs.

    Workflow:
    1. Prompt user for URL to analyze
    2. Prompt for description of what to extract
    3. Generate schema using LLM or fallback to basic schema
    4. Display generated schema in JSON format
    5. Optionally save schema to file
    6. Optionally test schema on the target URL
    7. Loop until user enters 'quit'

    Returns:
        None. Output is printed to stdout and schemas are saved to disk as JSON files.

    Raises:
        No exceptions raised; errors in URL analysis or schema generation are caught
        and displayed to the user for interactive handling.
    """
    print("\n=== Schema Generator Interactive Mode ===\n")

    generator = SchemaGenerator()

    while True:
        url = input("Enter URL (or 'quit' to exit): ").strip()
        if url.lower() == "quit":
            break

        description = input("Describe what to extract: ").strip()

        print("\nAnalyzing page and generating schema...")
        schema = await generator.generate_schema_with_llm(url, description)

        print("\nGenerated Schema:")
        print(json.dumps(schema, indent=2))

        save = input("\nSave schema? (y/n): ").strip().lower()
        if save == "y":
            filepath = generator.save_schema(schema)
            print(f"Schema saved to: {filepath}")

            test = input("Test schema on URL? (y/n): ").strip().lower()
            if test == "y":
                print("Testing...")
                result = await generator.test_schema(url, schema)
                if result["success"]:
                    print(f"Extracted {result.get('item_count', 0)} items")
                    print(json.dumps(result.get("extracted_data", []), indent=2)[:1000])
                else:
                    print(f"Test failed: {result.get('error')}")


def main() -> None:
    """CLI entry point for schema generation with multiple execution modes.

    Orchestrates command-line interface for auto-generating extraction schemas from web pages.
    Supports interactive mode, batch processing from file, schema testing, and single-URL
    schema generation with optional LLM-based or fallback basic schema creation.

    Command-line Arguments:
        url: Target URL to analyze for schema generation (optional if using --interactive, --test, or --batch).
        description: Human-readable description of what to extract from the page
                    (e.g., 'products from shop', 'blog articles'). Required when url is provided.
        --output, -o: Output file path for saving generated schema (optional).
        --format: Schema format choice - 'json' or 'css' (default: 'json').
        --interactive, -i: Enable interactive mode with user prompts for URL and description.
        --batch, -b: File path containing URLs to analyze (one per line) for batch processing.
        --save-schemas: Directory to save generated schemas (default: './schemas').
        --test, -t: Test extraction schema on a URL by loading schema from file path.
        --provider: LLM provider string in format 'provider/model'
                   (default: 'openai/gpt-4o-mini'). Examples: 'openai/gpt-4',
                   'anthropic/claude-3', 'google/gemini-pro'.

    Output Files:
        {name}_{timestamp}.json: Generated schema files (named by schema name + timestamp).
        Command-line output: Schema JSON displayed to stdout.

    Exit Codes:
        0: Success (schema generation completed, may have errors in output).
        1: Error (invalid arguments, missing required parameters, or no URLs found).

    Raises:
        SystemExit: With code 0 or 1 depending on argument validation and execution result.
    """
    parser = argparse.ArgumentParser(description="Auto-generate extraction schemas")
    parser.add_argument("url", nargs="?", help="URL to analyze")
    parser.add_argument(
        "description",
        nargs="?",
        help="Description of what to extract (e.g., 'products from shop')",
    )
    parser.add_argument(
        "--output", "-o", help="Output file path for schema"
    )
    parser.add_argument(
        "--format",
        choices=["json", "css"],
        default="json",
        help="Schema format",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument(
        "--batch", "-b", help="File containing URLs to analyze"
    )
    parser.add_argument(
        "--save-schemas",
        help="Directory to save generated schemas",
    )
    parser.add_argument(
        "--test", "-t", help="Test schema on URL (provide schema file path)"
    )
    parser.add_argument(
        "--provider",
        default="openai/gpt-4o-mini",
        help="LLM provider for schema generation",
    )

    args = parser.parse_args()

    if not any([args.url, args.interactive, args.test]):
        parser.print_help()
        print("\nExamples:")
        print("  python schema-generator.py https://example.com 'extract products'")
        print("  python schema-generator.py https://shop.com 'product listings' -o products.json")
        print("  python schema-generator.py --interactive")
        print("  python schema-generator.py --test schema.json -u https://example.com")
        sys.exit(1)

    generator = SchemaGenerator(args.save_schemas or "./schemas")

    if args.interactive:
        asyncio.run(interactive_mode())

    elif args.test:
        schema = generator.load_schema(args.test)
        url = getattr(args, 'url', None)
        if url:
            result = asyncio.run(generator.test_schema(url, schema))
            print(f"Test result: {result}")
        else:
            print("URL required for testing. Use: python schema-generator.py --test schema.json <url>")

    elif args.url and args.description:
        print(f"Analyzing {args.url}...")
        schema = asyncio.run(
            generator.generate_schema_with_llm(args.url, args.description, args.provider)
        )

        print("\nGenerated Schema:")
        print(json.dumps(schema, indent=2))

        if args.output:
            filepath = generator.save_schema(schema, args.output)
            print(f"\nSchema saved to: {filepath}")

    elif args.batch:
        with open(args.batch) as f:
            urls = f.readlines()

        for url in urls:
            url = url.strip()
            if not url:
                continue

            description = input(f"Describe extraction for {url}: ")
            if description:
                print(f"Generating schema for {url}...")
                schema = asyncio.run(
                    generator.generate_schema_with_llm(url, description, args.provider)
                )
                filepath = generator.save_schema(schema)
                print(f"Schema saved to: {filepath}")


if __name__ == "__main__":
    main()
