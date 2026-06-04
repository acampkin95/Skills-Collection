#!/usr/bin/env python3
"""
Crawl4AI Docker REST API Client - Examples and implementation

Demonstrates using Crawl4AI's Docker REST API for:
- Remote crawling via HTTP API
- Job queue management with async jobs
- Webhook notifications for async completion
- Monitoring and health checks
- Streaming crawl results
- Bulk processing with batch optimization
"""

import requests
import json
import time
from typing import Optional, Dict, Any, Generator, List


class Crawl4AIClient:
    """Python client for Crawl4AI Docker REST API"""
    
    def __init__(self, base_url: str = "http://localhost:11235"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status.

        Returns:
            Dictionary containing API health status and version information.

        Raises:
            requests.exceptions.HTTPError: If API returns non-2xx status code.
            requests.exceptions.ConnectionError: If API is unreachable.
        """
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def crawl(
        self,
        urls: List[str],
        crawler_config: Optional[Dict[str, Any]] = None,
        browser_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Synchronous crawl request (blocking until completion).

        Args:
            urls: List of URLs to crawl.
            crawler_config: Optional CrawlerRunConfig parameters as dictionary.
            browser_config: Optional BrowserConfig parameters as dictionary.

        Returns:
            Dictionary containing crawl results with success status and markdown content.

        Raises:
            requests.exceptions.HTTPError: If API request fails.
            requests.exceptions.Timeout: If request exceeds 300 second timeout.
        """
        
        payload = {
            "urls": urls,
        }
        
        if crawler_config:
            payload["crawler_config"] = {
                "type": "CrawlerRunConfig",
                "params": crawler_config
            }
        
        if browser_config:
            payload["browser_config"] = {
                "type": "BrowserConfig",
                "params": browser_config
            }
        
        response = self.session.post(
            f"{self.base_url}/crawl",
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    
    def crawl_stream(
        self,
        urls: List[str],
        crawler_config: Optional[Dict[str, Any]] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Streaming crawl request (yields results as they arrive).

        Args:
            urls: List of URLs to crawl.
            crawler_config: Optional CrawlerRunConfig parameters as dictionary.

        Yields:
            Dictionary containing individual crawl result as data arrives from server.

        Raises:
            requests.exceptions.HTTPError: If API request fails.
            requests.exceptions.Timeout: If request exceeds 300 second timeout.
            json.JSONDecodeError: If server-sent event data is malformed.
        """
        
        crawler_config = crawler_config or {}
        crawler_config["stream"] = True
        
        payload = {
            "urls": urls,
            "crawler_config": {
                "type": "CrawlerRunConfig",
                "params": crawler_config
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/crawl/stream",
            json=payload,
            stream=True,
            timeout=300
        )
        response.raise_for_status()
        
        # Parse SSE stream
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    yield json.loads(data)
    
    def create_job(
        self,
        urls: List[str],
        crawler_config: Optional[Dict] = None,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an async job"""
        
        payload = {
            "urls": urls,
        }
        
        if crawler_config:
            payload["crawler_config"] = {
                "type": "CrawlerRunConfig",
                "params": crawler_config
            }
        
        if webhook_url:
            payload["webhook_url"] = webhook_url
        
        response = self.session.post(
            f"{self.base_url}/crawl/job",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status"""
        response = self.session.get(f"{self.base_url}/crawl/job/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_job(
        self,
        job_id: str,
        timeout: int = 300,
        poll_interval: float = 2.0
    ) -> Dict[str, Any]:
        """Wait for job completion with polling.

        Args:
            job_id: Unique identifier of the job to monitor.
            timeout: Maximum seconds to wait for job completion (default: 300).
            poll_interval: Seconds between status check requests (default: 2.0).

        Returns:
            Dictionary containing final job status and results.

        Raises:
            RuntimeError: If job status is "failed" (includes error message from server).
            TimeoutError: If job does not complete within specified timeout.
            requests.exceptions.HTTPError: If API request fails.
        """

        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)

            if status.get("status") == "completed":
                return status
            elif status.get("status") == "failed":
                raise RuntimeError(f"Job failed: {status.get('error')}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")


# Example 1: Basic Synchronous Crawl
def example_basic_crawl() -> None:
    """Run example of basic synchronous crawl with health check.

    Returns:
        None.

    Raises:
        requests.exceptions.HTTPError: If API calls fail.
        requests.exceptions.ConnectionError: If API is unreachable.
    """
    
    print("Example 1: Basic Synchronous Crawl")
    print("-" * 80)
    
    client = Crawl4AIClient()
    
    # Health check first
    health = client.health_check()
    print(f"✓ API Status: {health.get('status')}")
    
    # Crawl
    result = client.crawl(
        urls=["https://example.com"],
        crawler_config={
            "word_count_threshold": 10,
            "exclude_external_links": True
        }
    )
    
    if result.get("success"):
        markdown = result.get("result", {}).get("markdown", {}).get("raw_markdown", "")
        print(f"✓ Crawled successfully: {len(markdown)} chars")
    else:
        print(f"❌ Failed: {result.get('error')}")


# Example 2: Streaming Crawl
def example_streaming_crawl() -> None:
    """Run example of streaming crawl with multiple URLs.

    Returns:
        None.

    Raises:
        requests.exceptions.HTTPError: If API calls fail.
        requests.exceptions.ConnectionError: If API is unreachable.
    """
    
    print("\nExample 2: Streaming Crawl")
    print("-" * 80)
    
    client = Crawl4AIClient()
    
    urls = [
        "https://example.com",
        "https://docs.crawl4ai.com",
        "https://github.com/unclecode/crawl4ai"
    ]
    
    print(f"Crawling {len(urls)} URLs with streaming...")
    
    for i, result in enumerate(client.crawl_stream(urls), 1):
        if result.get("success"):
            url = result.get("url")
            length = len(result.get("result", {}).get("markdown", {}).get("raw_markdown", ""))
            print(f"  {i}. ✓ {url}: {length} chars")
        else:
            print(f"  {i}. ✗ {result.get('url')}: {result.get('error')}")


# Example 3: Job Queue with Webhook
def example_job_queue() -> None:
    """Create and monitor async crawl job with optional webhook notification.

    Demonstrates asynchronous job creation, polling for completion, and webhook
    notifications for async completion callbacks.

    Returns:
        None.

    Raises:
        requests.exceptions.HTTPError: If API calls fail.
        requests.exceptions.ConnectionError: If API is unreachable.
        RuntimeError: If job status is "failed".
        TimeoutError: If job does not complete within timeout.
    """

    print("\nExample 3: Async Job Queue")
    print("-" * 80)
    
    client = Crawl4AIClient()
    
    # Create job
    job = client.create_job(
        urls=["https://example.com"],
        crawler_config={"word_count_threshold": 10},
        webhook_url="https://your-webhook.example.com/callback"  # Optional
    )
    
    job_id = job.get("job_id")
    print(f"✓ Job created: {job_id}")
    
    # Wait for completion
    print("  Waiting for job to complete...")
    result = client.wait_for_job(job_id, timeout=60)
    
    print(f"✓ Job completed!")
    print(f"  Status: {result.get('status')}")


# Example 4: Crawl with CSS Extraction
def example_css_extraction() -> None:
    """Crawl website and extract structured data using CSS selectors.

    Demonstrates CSS-based data extraction from a page using JsonCssExtractionStrategy
    with schema-based field definitions and CSS selector patterns.

    Returns:
        None.

    Raises:
        requests.exceptions.HTTPError: If API calls fail.
        requests.exceptions.ConnectionError: If API is unreachable.
    """

    print("\nExample 4: CSS Extraction via API")
    print("-" * 80)
    
    client = Crawl4AIClient()
    
    result = client.crawl(
        urls=["https://news.ycombinator.com"],
        crawler_config={
            "extraction_strategy": {
                "type": "JsonCssExtractionStrategy",
                "params": {
                    "schema": {
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
                            }
                        ]
                    }
                }
            }
        }
    )
    
    if result.get("success"):
        extracted = result.get("result", {}).get("extracted_content")
        if extracted:
            stories = json.loads(extracted)
            print(f"✓ Extracted {len(stories)} stories")
            for story in stories[:3]:
                print(f"  - {story.get('title')}")
        else:
            print("No extracted content")


# Example 5: LLM Extraction via API
def example_llm_extraction() -> None:
    """Crawl website and extract data using LLM with schema-based extraction.

    Demonstrates LLM-based data extraction from a page using LLMExtractionStrategy
    with OpenAI GPT-4o-mini model and JSON schema definition.

    Returns:
        None.

    Raises:
        requests.exceptions.HTTPError: If API calls fail.
        requests.exceptions.ConnectionError: If API is unreachable.
    """

    print("\nExample 5: LLM Extraction via API")
    print("-" * 80)
    
    client = Crawl4AIClient()
    
    result = client.crawl(
        urls=["https://example.com/article"],
        crawler_config={
            "extraction_strategy": {
                "type": "LLMExtractionStrategy",
                "params": {
                    "provider": "openai/gpt-4o-mini",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "author": {"type": "string"},
                            "summary": {"type": "string"}
                        }
                    },
                    "extraction_type": "schema",
                    "instruction": "Extract article metadata"
                }
            }
        }
    )
    
    if result.get("success"):
        extracted = result.get("result", {}).get("extracted_content")
        if extracted:
            data = json.loads(extracted)
            print(f"✓ Extracted: {data.get('title')}")


# Example 6: Using curl commands
def show_curl_examples() -> None:
    """Display curl command examples for REST API interaction.

    Prints example curl commands for common API operations including basic crawl,
    streaming crawl, job creation, and job status checking.

    Returns:
        None.
    """

    print("\nExample 6: Using curl")
    print("-" * 80)
    print()
    
    print("Basic crawl:")
    print("""
curl -X POST http://localhost:11235/crawl \\
  -H 'Content-Type: application/json' \\
  -d '{
    "urls": ["https://example.com"],
    "crawler_config": {
      "type": "CrawlerRunConfig",
      "params": {
        "word_count_threshold": 10
      }
    }
  }'
    """)
    
    print("\nStreaming crawl:")
    print("""
curl -N -X POST http://localhost:11235/crawl/stream \\
  -H 'Content-Type: application/json' \\
  -d '{
    "urls": ["https://example.com"],
    "crawler_config": {
      "type": "CrawlerRunConfig",
      "params": {"stream": true}
    }
  }'
    """)
    
    print("\nCreate async job:")
    print("""
curl -X POST http://localhost:11235/crawl/job \\
  -H 'Content-Type: application/json' \\
  -d '{
    "urls": ["https://example.com"],
    "webhook_url": "https://your-webhook.com/callback"
  }'
    """)
    
    print("\nCheck job status:")
    print("""
curl http://localhost:11235/crawl/job/{job_id}
    """)


# Example 7: Bulk Processing
def example_bulk_processing() -> None:
    """Process multiple URLs in batches for efficient bulk crawling.

    Demonstrates batch processing of multiple URLs with configurable batch size
    and cache bypass for efficient bulk operations.

    Returns:
        None.
    """

    print("\nExample 7: Bulk Processing")
    print("-" * 80)
    
    client = Crawl4AIClient()
    
    # List of URLs to crawl
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]
    
    # Process in batches
    batch_size = 10
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}...")
        
        result = client.crawl(
            urls=batch,
            crawler_config={
                "cache_mode": "BYPASS",
                "word_count_threshold": 10
            }
        )
        
        # Process results
        # (Implementation depends on your needs)


def main() -> None:
    """Main entry point for Crawl4AI Docker REST API examples.

    Demonstrates various usage patterns for the Crawl4AI Docker REST API including
    basic synchronous crawling, streaming crawl, job queue management, CSS extraction,
    LLM extraction, and bulk processing. Includes curl command examples.

    Returns:
        None.

    Raises:
        requests.exceptions.ConnectionError: If API is unreachable.
    """

    print("=" * 80)
    print("Crawl4AI Docker REST API Examples")
    print("=" * 80)
    print()
    
    try:
        # Check if API is running
        response = requests.get("http://localhost:11235/health", timeout=5)
        if response.status_code == 200:
            print("✓ API is running\n")
            
            # Run examples
            example_basic_crawl()
            example_streaming_crawl()
            # example_job_queue()  # Uncomment if you want to test
            example_css_extraction()
            # example_llm_extraction()  # Requires API key
            
        else:
            print("⚠️  API returned unexpected status")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Crawl4AI API")
        print()
        print("Make sure the Docker container is running:")
        print("  cd docker && docker-compose up -d")
        print()
        print("Or start manually:")
        print("  docker run -p 11235:11235 unclecode/crawl4ai:latest")
    
    # Show curl examples anyway
    show_curl_examples()
    
    print("\n" + "=" * 80)
    print("Tip: Use the Playground UI at http://localhost:11235/playground")
    print("=" * 80)


if __name__ == "__main__":
    main()
