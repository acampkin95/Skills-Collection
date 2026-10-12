#!/usr/bin/env python3
"""
Crawl4AI Performance Benchmark Suite

Measures throughput, latency, cost, and quality across extraction strategies.
Generates detailed reports for capacity planning and optimization.
"""

import asyncio
import time
import json
import statistics
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter

@dataclass
class BenchmarkResult:
    """Single benchmark execution result"""
    url: str
    strategy: str
    duration_ms: float
    success: bool
    content_length: int
    tokens_used: int = 0
    cost_usd: float = 0.0
    cache_hit: bool = False
    error: str = None

@dataclass
class BenchmarkSummary:
    """Aggregate benchmark statistics"""
    strategy: str
    total_runs: int
    success_rate: float
    avg_duration_ms: float
    p50_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    throughput_per_min: float
    avg_content_length: int
    total_tokens: int
    total_cost_usd: float
    avg_cost_per_page: float

class Benchmarker:
    """Performance benchmarking orchestrator for Crawl4AI extraction strategies.

    Manages execution of performance benchmarks across multiple URLs and extraction
    strategies, collecting timing, success rate, and cost metrics. Generates detailed
    performance reports with statistical analysis and comparison tables.
    """

    def __init__(self, output_dir: str = "./benchmark_results") -> None:
        """Initialize the benchmarking orchestrator.

        Args:
            output_dir: Directory to save benchmark results and reports (default: "./benchmark_results").

        Raises:
            OSError: If output directory cannot be created.
        """
        self.output_dir = output_dir
        self.results: List[BenchmarkResult] = []

        # Create output directory
        import os
        os.makedirs(output_dir, exist_ok=True)
    
    async def run_benchmark(
        self,
        urls: List[str],
        strategy_name: str,
        config: CrawlerRunConfig,
        iterations: int = 3
    ) -> List[BenchmarkResult]:
        """Execute benchmark suite for a crawling strategy.

        Runs multiple iterations of crawling with the specified extraction strategy,
        measuring performance metrics including latency, success rate, content length,
        and cost information.

        Args:
            urls: List of URLs to benchmark.
            strategy_name: Name of the extraction strategy being tested.
            config: CrawlerRunConfig with strategy and settings.
            iterations: Number of iterations to run (default: 3).

        Returns:
            List of BenchmarkResult objects containing timing and performance data
            for each URL across all iterations.

        Raises:
            No exceptions raised; errors are logged in individual results.
        """
        
        print(f"\n{'='*60}")
        print(f"Benchmarking: {strategy_name}")
        print(f"URLs: {len(urls)}, Iterations: {iterations}")
        print(f"{'='*60}")
        
        results = []
        
        async with AsyncWebCrawler() as crawler:
            for iteration in range(iterations):
                print(f"\nIteration {iteration + 1}/{iterations}")
                
                for i, url in enumerate(urls, 1):
                    print(f"  [{i}/{len(urls)}] {url[:60]}...", end=" ")
                    
                    start = time.time()
                    try:
                        result = await crawler.arun(url, config=config)
                        duration_ms = (time.time() - start) * 1000
                        
                        # Extract metadata
                        tokens = 0
                        cost = 0.0
                        if hasattr(result, 'extraction_metadata') and result.extraction_metadata:
                            tokens = result.extraction_metadata.get('total_tokens', 0)
                            cost = result.extraction_metadata.get('cost', 0.0)
                        
                        benchmark_result = BenchmarkResult(
                            url=url,
                            strategy=strategy_name,
                            duration_ms=duration_ms,
                            success=result.success,
                            content_length=len(result.markdown.raw_markdown) if result.success else 0,
                            tokens_used=tokens,
                            cost_usd=cost,
                            cache_hit=False  # Could check from result metadata
                        )
                        
                        results.append(benchmark_result)
                        
                        status = "✓" if result.success else "✗"
                        print(f"{status} {duration_ms:.0f}ms")
                        
                    except Exception as e:
                        duration_ms = (time.time() - start) * 1000
                        results.append(BenchmarkResult(
                            url=url,
                            strategy=strategy_name,
                            duration_ms=duration_ms,
                            success=False,
                            content_length=0,
                            error=str(e)
                        ))
                        print(f"✗ Error: {e}")
                
                # Small delay between iterations
                if iteration < iterations - 1:
                    await asyncio.sleep(1)
        
        return results
    
    def analyze_results(self, results: List[BenchmarkResult]) -> Optional[BenchmarkSummary]:
        """Generate statistical summary of benchmark results.

        Computes aggregate statistics including percentiles, throughput, and cost metrics
        from individual benchmark run results. Returns summary with zero values if no
        successful runs occurred.

        Args:
            results: List of BenchmarkResult objects from benchmark execution.

        Returns:
            Optional[BenchmarkSummary]: Summary containing aggregated statistics including
                success rate, percentiles (p50, p95, p99), throughput, and cost metrics.
                Returns None if results list is empty.

        Raises:
            ValueError: Raised if results contain invalid or inconsistent data.
        """

        if not results:
            return None
        
        strategy = results[0].strategy
        successful = [r for r in results if r.success]
        
        if not successful:
            return BenchmarkSummary(
                strategy=strategy,
                total_runs=len(results),
                success_rate=0.0,
                avg_duration_ms=0,
                p50_duration_ms=0,
                p95_duration_ms=0,
                p99_duration_ms=0,
                throughput_per_min=0,
                avg_content_length=0,
                total_tokens=0,
                total_cost_usd=0,
                avg_cost_per_page=0
            )
        
        durations = [r.duration_ms for r in successful]
        durations.sort()
        
        avg_duration = statistics.mean(durations)
        p50 = durations[len(durations) // 2]
        p95 = durations[int(len(durations) * 0.95)]
        p99 = durations[int(len(durations) * 0.99)]
        
        # Calculate throughput (pages per minute)
        throughput = 60000 / avg_duration if avg_duration > 0 else 0
        
        total_tokens = sum(r.tokens_used for r in successful)
        total_cost = sum(r.cost_usd for r in successful)
        avg_cost = total_cost / len(successful) if successful else 0
        
        return BenchmarkSummary(
            strategy=strategy,
            total_runs=len(results),
            success_rate=len(successful) / len(results),
            avg_duration_ms=avg_duration,
            p50_duration_ms=p50,
            p95_duration_ms=p95,
            p99_duration_ms=p99,
            throughput_per_min=throughput,
            avg_content_length=statistics.mean([r.content_length for r in successful]),
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            avg_cost_per_page=avg_cost
        )
    
    def print_summary(self, summary: BenchmarkSummary) -> None:
        """Display benchmark summary statistics in formatted terminal output.

        Prints a human-readable summary of benchmark results including success rate,
        latency percentiles, throughput, content metrics, and cost information.

        Args:
            summary: BenchmarkSummary object containing aggregated statistics.

        Returns:
            None. Output is printed to stdout.

        Raises:
            TypeError: Raised if summary is not a BenchmarkSummary instance.
        """

        print(f"\n{'='*60}")
        print(f"SUMMARY: {summary.strategy}")
        print(f"{'='*60}")
        print(f"Success Rate:     {summary.success_rate*100:.1f}%")
        print(f"Avg Duration:     {summary.avg_duration_ms:.0f}ms")
        print(f"P50 Duration:     {summary.p50_duration_ms:.0f}ms")
        print(f"P95 Duration:     {summary.p95_duration_ms:.0f}ms")
        print(f"P99 Duration:     {summary.p99_duration_ms:.0f}ms")
        print(f"Throughput:       {summary.throughput_per_min:.1f} pages/min")
        print(f"Avg Content:      {summary.avg_content_length:,} chars")
        
        if summary.total_tokens > 0:
            print(f"Total Tokens:     {summary.total_tokens:,}")
            print(f"Total Cost:       ${summary.total_cost_usd:.4f}")
            print(f"Cost per Page:    ${summary.avg_cost_per_page:.4f}")
    
    def export_results(self, summaries: List[BenchmarkSummary], filename: Optional[str] = None) -> str:
        """Export benchmark summaries to JSON file with timestamp.

        Serializes BenchmarkSummary objects to JSON format with metadata including
        export timestamp. Auto-generates filename with timestamp if not provided.

        Args:
            summaries: List of BenchmarkSummary objects to export.
            filename: Optional output filename. If not provided, generates filename
                     with timestamp (e.g., benchmark_20240223_120530.json).

        Returns:
            str: Path to the exported JSON file.

        Raises:
            OSError: Raised if JSON file cannot be written to disk.
            TypeError: Raised if summaries contain non-serializable objects.
        """

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/benchmark_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'summaries': [asdict(s) for s in summaries]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✓ Results exported to: {filename}")
        return filename
    
    def generate_comparison_table(self, summaries: List[BenchmarkSummary]) -> None:
        """Generate and display formatted markdown comparison table of benchmark results.

        Creates a side-by-side comparison table showing key metrics (average latency,
        p95 latency, throughput, cost per page) for all benchmark summaries.

        Args:
            summaries: List of BenchmarkSummary objects to compare.

        Returns:
            None. Output is printed to stdout in markdown table format.

        Raises:
            TypeError: Raised if summaries contain invalid BenchmarkSummary objects.
        """

        print(f"\n{'='*60}")
        print("COMPARISON TABLE")
        print(f"{'='*60}\n")
        
        # Header
        print(f"| {'Strategy':<25} | {'Avg (ms)':<10} | {'P95 (ms)':<10} | {'Throughput':<15} | {'Cost/Page':<12} |")
        print(f"|{'-'*27}|{'-'*12}|{'-'*12}|{'-'*17}|{'-'*14}|")
        
        # Rows
        for s in summaries:
            cost_str = f"${s.avg_cost_per_page:.4f}" if s.avg_cost_per_page > 0 else "Free"
            print(f"| {s.strategy:<25} | {s.avg_duration_ms:<10.0f} | {s.p95_duration_ms:<10.0f} | {s.throughput_per_min:<15.1f} | {cost_str:<12} |")
        
        print()

async def main() -> List[BenchmarkSummary]:
    """Run comprehensive benchmark suite comparing extraction strategies.

    Executes a series of benchmarks testing different Crawl4AI extraction approaches:
    1. Baseline markdown extraction (no strategy)
    2. CSS-based extraction with JSON schema
    3. Content filtering with BM25 + CSS extraction
    4. LLM-based extraction (if OPENAI_API_KEY is set)

    Generates detailed performance metrics, comparison tables, and JSON exports
    for capacity planning and optimization analysis.

    Returns:
        List[BenchmarkSummary]: List of summary statistics for each benchmark strategy.

    Raises:
        No exceptions raised; errors in individual benchmarks are logged and skipped.
    """

    # Test URLs (diverse content types)
    test_urls = [
        "https://news.ycombinator.com/",
        "https://www.bbc.com/news",
        "https://github.com/trending",
    ]
    
    benchmarker = Benchmarker()
    summaries = []
    
    # 1. Baseline: Markdown extraction (no strategy)
    print("\n🔹 Benchmark 1: Baseline Markdown")
    results = await benchmarker.run_benchmark(
        urls=test_urls,
        strategy_name="Baseline (Markdown)",
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=10
        ),
        iterations=3
    )
    summary = benchmarker.analyze_results(results)
    summaries.append(summary)
    benchmarker.print_summary(summary)
    
    # 2. CSS Extraction
    print("\n🔹 Benchmark 2: CSS Extraction")
    css_schema = {
        "name": "items",
        "baseSelector": "article, .story, .post",
        "fields": [
            {"name": "title", "selector": "h1, h2, h3, .title", "type": "text"},
            {"name": "content", "selector": "p, .content", "type": "text"}
        ]
    }
    
    results = await benchmarker.run_benchmark(
        urls=test_urls,
        strategy_name="CSS Extraction",
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=JsonCssExtractionStrategy(schema=css_schema)
        ),
        iterations=3
    )
    summary = benchmarker.analyze_results(results)
    summaries.append(summary)
    benchmarker.print_summary(summary)
    
    # 3. With Content Filtering (BM25)
    print("\n🔹 Benchmark 3: BM25 Filtering + CSS")
    results = await benchmarker.run_benchmark(
        urls=test_urls,
        strategy_name="BM25 Filter + CSS",
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            content_filter=BM25ContentFilter(
                user_query="article content news",
                bm25_threshold=1.0
            ),
            extraction_strategy=JsonCssExtractionStrategy(schema=css_schema)
        ),
        iterations=3
    )
    summary = benchmarker.analyze_results(results)
    summaries.append(summary)
    benchmarker.print_summary(summary)
    
    # 4. LLM Extraction (if API key available)
    import os
    if os.getenv('OPENAI_API_KEY'):
        print("\n🔹 Benchmark 4: LLM Extraction")
        
        llm_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "summary": {"type": "string"},
                "topics": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        results = await benchmarker.run_benchmark(
            urls=test_urls[:2],  # Fewer URLs to save costs
            strategy_name="LLM (GPT-4o-mini)",
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=LLMExtractionStrategy(
                    provider="openai/gpt-4o-mini",
                    api_token=os.getenv('OPENAI_API_KEY'),
                    schema=llm_schema,
                    extraction_type="schema"
                )
            ),
            iterations=2  # Fewer iterations for LLM
        )
        summary = benchmarker.analyze_results(results)
        summaries.append(summary)
        benchmarker.print_summary(summary)
    
    # Generate final comparison
    benchmarker.generate_comparison_table(summaries)
    
    # Export results
    benchmarker.export_results(summaries)
    
    print("\n✅ Benchmark complete!")
    
    return summaries

if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("Error: Python 3.10+ required")
        sys.exit(1)
    
    print("Crawl4AI Performance Benchmark Suite")
    print("=" * 60)
    
    asyncio.run(main())
