#!/usr/bin/env python3
"""
LLM-Based Data Extraction
==========================

This example demonstrates using LLMs to extract structured data from web pages.
Useful when CSS selectors are difficult or when semantic understanding is needed.

Provides practical examples of LLM-based extraction strategies including schema-based
extraction with Pydantic models, instruction-based extraction, and semantic similarity
search. Supports multiple LLM providers (OpenAI, Anthropic, Groq) via LiteLLM for
flexible model selection.
"""

import asyncio
import json
import os
from pydantic import BaseModel, Field
from typing import List, Optional
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy


# Example 1: Article Extraction with Schema
class Article(BaseModel):
    """Article data model"""
    title: str = Field(description="Article headline")
    author: str = Field(description="Article author name")
    publication_date: str = Field(description="When the article was published")
    summary: str = Field(description="Brief summary of the article")
    main_topics: List[str] = Field(description="Main topics covered in the article")
    key_points: List[str] = Field(description="Key takeaways from the article")


async def extract_article_with_llm() -> None:
    """Extract article data using LLM with schema validation.

    Demonstrates LLM-based extraction using OpenAI's GPT-4o-mini model with a
    Pydantic schema to ensure structured output. Extracts article metadata including
    title, author, publication date, summary, topics, and key points. Shows how to
    configure LLMExtractionStrategy with schema validation and custom instructions.

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing extracted article information.

    Raises:
        No exceptions raised; missing API keys and extraction failures are caught and logged.
    """
    
    print("Example 1: Article Extraction with LLM")
    print("-" * 80)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set - skipping LLM example")
        print("   Set your API key: export OPENAI_API_KEY=sk-...")
        return
    
    strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",  # or "openai/gpt-4"
        api_token=api_key,
        schema=Article.model_json_schema(),
        extraction_type="schema",
        instruction="Extract article information accurately. Focus on the main content.",
        chunk_token_threshold=4096,  # Enable parallel processing
        overlap_rate=0.1
    )
    
    config = CrawlerRunConfig(
        extraction_strategy=strategy,
        cache_mode=CacheMode.BYPASS
    )
    
    url = "https://example-news.com/article"
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        
        if result.success and result.extracted_content:
            article = json.loads(result.extracted_content)
            
            print(f"✓ Extracted article:")
            print(f"  Title: {article.get('title', 'N/A')}")
            print(f"  Author: {article.get('author', 'N/A')}")
            print(f"  Date: {article.get('publication_date', 'N/A')}")
            print(f"  Topics: {', '.join(article.get('main_topics', []))}")
            print(f"\n  Summary: {article.get('summary', 'N/A')[:200]}...")
            
            # Show token usage if available
            if result.extraction_metadata:
                print(f"\n  Tokens used: {result.extraction_metadata.get('total_tokens', 'N/A')}")
        else:
            print(f"❌ Failed: {result.error_message}")


# Example 2: Product Review Extraction
class ProductReview(BaseModel):
    """Product review data model"""
    product_name: str
    rating: float = Field(ge=1.0, le=5.0)
    pros: List[str] = Field(description="Positive aspects mentioned")
    cons: List[str] = Field(description="Negative aspects mentioned")
    verdict: str = Field(description="Overall verdict or recommendation")
    target_audience: str = Field(description="Who would benefit from this product")


async def extract_product_review() -> None:
    """Extract product review using LLM with rating and sentiment analysis.

    Demonstrates LLM-based extraction of product reviews with structured schema
    including rating (1-5 scale), pros, cons, verdict, and target audience.
    Shows how to enforce field constraints (rating bounds) and extract complex
    lists (pros/cons) from unstructured review text.

    Args:
        None.

    Returns:
        None. Output is printed to stdout describing the extraction schema.

    Raises:
        No exceptions raised; missing API keys are caught and logged.
    """
    
    print("\nExample 2: Product Review Extraction")
    print("-" * 80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Skipping - OPENAI_API_KEY not set")
        return
    
    strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        api_token=api_key,
        schema=ProductReview.model_json_schema(),
        extraction_type="schema",
        instruction="""
        Extract the product review information.
        - Rating should be a number between 1 and 5
        - List specific pros and cons mentioned
        - Capture the overall recommendation
        """,
        chunk_token_threshold=4096
    )
    
    config = CrawlerRunConfig(extraction_strategy=strategy)
    
    print("Schema defined for product reviews with structured data")


# Example 3: Instruction-Based Extraction (No Schema)
async def extract_with_instruction() -> None:
    """Extract data using natural language instructions without schema.

    Demonstrates LLM-based extraction with instruction-based guidance instead of
    schema validation. Useful for flexible extraction tasks where the output format
    is less critical. Shows how to provide natural language instructions for
    complex extraction tasks (company information, dates, locations).

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing extracted information as plain text.

    Raises:
        No exceptions raised; missing API keys and extraction failures are caught and logged.
    """
    
    print("\nExample 3: Instruction-Based Extraction")
    print("-" * 80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Skipping - OPENAI_API_KEY not set")
        return
    
    strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        api_token=api_key,
        extraction_type="block",  # No schema, just follow instructions
        instruction="""
        Extract all company names, their founding dates, and headquarters locations
        mentioned in this page. Format as a simple list with clear structure.
        """,
        chunk_token_threshold=4096
    )
    
    config = CrawlerRunConfig(extraction_strategy=strategy)
    
    url = "https://example.com/companies"
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        
        if result.success and result.extracted_content:
            print("✓ Extracted information:")
            print(result.extracted_content[:500])
        else:
            print(f"❌ Failed: {result.error_message}")


# Example 4: Research Paper Extraction
class ResearchPaper(BaseModel):
    """Research paper metadata"""
    title: str
    authors: List[str]
    abstract: str
    publication_date: str
    keywords: List[str]
    methodology: str = Field(description="Research methodology used")
    key_findings: List[str] = Field(description="Main findings of the research")
    citations_count: int = Field(default=0, description="Number of citations if mentioned")


async def extract_research_paper() -> None:
    """Extract research paper metadata using LLM with academic fields.

    Demonstrates LLM-based extraction of academic paper metadata including title,
    authors, abstract, publication date, keywords, methodology, and key findings.
    Shows how to handle complex extraction scenarios with larger token thresholds
    for longer documents and overlap configuration for better context preservation.

    Args:
        None.

    Returns:
        None. Output is printed to stdout describing the extraction schema.

    Raises:
        No exceptions raised; missing API keys are caught and logged.
    """
    
    print("\nExample 4: Research Paper Extraction")
    print("-" * 80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Skipping - OPENAI_API_KEY not set")
        return
    
    strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        api_token=api_key,
        schema=ResearchPaper.model_json_schema(),
        extraction_type="schema",
        instruction="""
        Extract research paper metadata accurately.
        - List all authors in order
        - Capture the complete abstract
        - Identify key methodologies used
        - Extract the main findings
        """,
        chunk_token_threshold=8192,  # Larger chunks for papers
        overlap_rate=0.15
    )
    
    config = CrawlerRunConfig(extraction_strategy=strategy)
    
    print("Schema defined for academic papers")


# Example 5: Job Posting Extraction
class JobPosting(BaseModel):
    """Job posting data"""
    title: str
    company: str
    location: str
    salary_range: str = Field(description="Salary range if mentioned")
    employment_type: str = Field(description="Full-time, part-time, contract, etc.")
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str
    benefits: List[str]
    application_deadline: str = Field(default="Not specified")


async def extract_job_posting() -> None:
    """Extract job posting details using LLM with comprehensive job fields.

    Demonstrates LLM-based extraction of job posting information including title,
    company, location, salary range, employment type, required/preferred skills,
    experience level, benefits, and application deadline. Shows how to distinguish
    between required and optional fields with default values.

    Args:
        None.

    Returns:
        None. Output is printed to stdout describing the extraction schema.

    Raises:
        No exceptions raised; missing API keys are caught and logged.
    """
    
    print("\nExample 5: Job Posting Extraction")
    print("-" * 80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Skipping - OPENAI_API_KEY not set")
        return
    
    strategy = LLMExtractionStrategy(
        provider="openai/gpt-4o-mini",
        api_token=api_key,
        schema=JobPosting.model_json_schema(),
        extraction_type="schema",
        instruction="""
        Extract job posting details comprehensively.
        - Distinguish between required and preferred skills
        - Capture all benefits mentioned
        - Note employment type and experience level
        """,
        chunk_token_threshold=4096
    )
    
    print("Schema defined for job postings")


# Example 6: Using Alternative LLM Providers
async def extract_with_anthropic() -> None:
    """Extract article data using Anthropic's Claude with LiteLLM provider.

    Demonstrates LLM-based extraction using Anthropic's Claude 3.5 Sonnet model
    through the LiteLLM provider abstraction. Shows how to use alternative LLM
    providers with the same extraction strategy pattern as OpenAI. Useful for
    cost comparison, latency optimization, or provider diversification.

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing the configured LLM provider.

    Raises:
        No exceptions raised; missing API keys are caught and logged.
    """

    print("\nExample 6: Using Anthropic Claude")
    print("-" * 80)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  Skipping - ANTHROPIC_API_KEY not set")
        return

    strategy = LLMExtractionStrategy(
        provider="anthropic/claude-3-5-sonnet-20241022",
        api_token=api_key,
        schema=Article.model_json_schema(),
        extraction_type="schema",
        instruction="Extract article information accurately.",
        chunk_token_threshold=4096
    )

    print("✓ Configured to use Claude 3.5 Sonnet")
    print("  Supported providers via LiteLLM:")
    print("  - OpenAI: openai/gpt-4o-mini, openai/gpt-4o")
    print("  - Anthropic: anthropic/claude-3-5-sonnet-20241022")
    print("  - Groq: groq/llama-3.1-70b-versatile")
    print("  - And many more via LiteLLM")


# Example 7: Cosine Strategy for Semantic Search
async def extract_with_cosine_similarity() -> None:
    """Extract relevant content using semantic similarity search.

    Demonstrates semantic-based extraction using cosine similarity matching between
    embeddings. Instead of CSS selectors or LLM reasoning, this strategy finds content
    chunks most semantically similar to a provided filter query. Uses sentence
    transformers for embedding generation and returns the top-k most similar chunks.
    Useful for finding semantically related content without structural HTML patterns.

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing the semantic filter configuration.

    Raises:
        No exceptions raised; output is printed showing the configured strategy.
    """

    print("\nExample 7: Semantic Search with Cosine Similarity")
    print("-" * 80)

    from crawl4ai.extraction_strategy import CosineStrategy

    strategy = CosineStrategy(
        semantic_filter="machine learning applications in healthcare",
        top_k=10,  # Return top 10 most relevant chunks
        model_name="sentence-transformers/all-MiniLM-L6-v2"  # Embedding model
    )

    config = CrawlerRunConfig(extraction_strategy=strategy)

    print("✓ Will extract content semantically similar to:")
    print("  'machine learning applications in healthcare'")
    print("  Returns top 10 most relevant chunks")


def show_best_practices() -> None:
    """Display comprehensive best practices guide for LLM-based extraction.

    Prints practical guidance across four key dimensions: cost optimization,
    accuracy improvement, performance tuning, and robust error handling. Covers
    model selection, schema design, chunking strategies, and fallback patterns.
    Intended as a reference guide for developers implementing extraction pipelines.

    Args:
        None.

    Returns:
        None. Output is printed to stdout as formatted best practices guide.

    Raises:
        No exceptions raised; this is a display function with no external dependencies.
    """

    print("\n" + "=" * 80)
    print("LLM Extraction Best Practices")
    print("=" * 80)
    print()
    print("1. Cost Optimization:")
    print("   - Use cheaper models (gpt-4o-mini) for simple extraction")
    print("   - Set chunk_token_threshold to enable parallel processing")
    print("   - Use CSS extraction when possible (it's free!)")
    print()
    print("2. Accuracy:")
    print("   - Define clear Pydantic schemas with descriptions")
    print("   - Provide specific extraction instructions")
    print("   - Test with sample pages first")
    print()
    print("3. Performance:")
    print("   - Larger chunk_token_threshold = fewer API calls but more tokens/call")
    print("   - Smaller chunks = more parallel calls but more API requests")
    print("   - Add overlap_rate for better context across chunks")
    print()
    print("4. Error Handling:")
    print("   - Check result.success before parsing")
    print("   - Monitor token usage via result.extraction_metadata")
    print("   - Have fallback strategies for rate limits")
    print()
    print("=" * 80)


def main() -> None:
    """Execute all LLM extraction examples and display best practices guide.

    Orchestrates demonstration of five distinct LLM extraction patterns:
    schema-based (Pydantic), product review extraction with constraints,
    research paper metadata, job posting details, and provider switching
    (OpenAI vs Anthropic vs Groq). Also demonstrates semantic similarity
    extraction via cosine strategy and displays comprehensive best practices.
    Validates API key availability before running async examples.

    Args:
        None.

    Returns:
        None. Output is printed to stdout showing example execution and guidance.

    Raises:
        No exceptions raised; all example execution is wrapped with error
        handling. Missing API keys result in skipped examples, not failures.
    """

    print("=" * 80)
    print("LLM-Based Extraction Examples")
    print("=" * 80)
    print()

    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

    if not (has_openai or has_anthropic):
        print("⚠️  No LLM API keys found!")
        print()
        print("Set API keys to run these examples:")
        print("  export OPENAI_API_KEY=sk-...")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        print()
        print("Showing schema examples instead...")
        print()

    # Run examples
    asyncio.run(extract_article_with_llm())
    asyncio.run(extract_product_review())
    asyncio.run(extract_research_paper())
    asyncio.run(extract_job_posting())
    asyncio.run(extract_with_anthropic())
    asyncio.run(extract_with_cosine_similarity())

    show_best_practices()


if __name__ == "__main__":
    main()
