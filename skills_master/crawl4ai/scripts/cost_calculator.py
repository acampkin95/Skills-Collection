#!/usr/bin/env python3
"""
Crawl4AI Cost Calculator

Estimates crawling costs based on extraction strategy, content volume,
and API pricing. Helps with budget planning and ROI analysis.
"""

import sys
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class ExtractionMethod(Enum):
    """Available extraction methods"""
    BASELINE = "baseline"  # Markdown only
    CSS = "css"  # CSS extraction
    REGEX = "regex"  # Regex patterns
    LLM_MINI = "llm_mini"  # GPT-4o-mini
    LLM_STANDARD = "llm_standard"  # GPT-4o
    LLM_ADVANCED = "llm_advanced"  # GPT-4

@dataclass
class PricingModel:
    """LLM pricing per 1M tokens"""
    name: str
    input_cost: float  # USD per 1M input tokens
    output_cost: float  # USD per 1M output tokens
    avg_speed_tokens_per_sec: int

# Current pricing (as of Jan 2025)
PRICING = {
    ExtractionMethod.LLM_MINI: PricingModel(
        name="GPT-4o-mini",
        input_cost=0.15,
        output_cost=0.60,
        avg_speed_tokens_per_sec=200
    ),
    ExtractionMethod.LLM_STANDARD: PricingModel(
        name="GPT-4o",
        input_cost=2.50,
        output_cost=10.00,
        avg_speed_tokens_per_sec=100
    ),
    ExtractionMethod.LLM_ADVANCED: PricingModel(
        name="GPT-4",
        input_cost=30.00,
        output_cost=60.00,
        avg_speed_tokens_per_sec=50
    )
}

@dataclass
class CostEstimate:
    """Cost estimation result"""
    method: ExtractionMethod
    num_pages: int
    
    # Per-page metrics
    avg_page_tokens: int
    avg_extraction_tokens: int
    avg_duration_sec: float
    
    # Totals
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    total_duration_minutes: float
    
    # Optimization potential
    cache_savings_percent: float
    filter_savings_percent: float

class CostCalculator:
    """Calculate crawling costs across scenarios"""
    
    # Average page sizes (tokens)
    AVG_TOKENS = {
        "small": 1000,      # Landing pages
        "medium": 3000,     # Article pages
        "large": 8000,      # Documentation
        "xlarge": 15000     # Very long content
    }
    
    # Baseline performance (no LLM)
    BASELINE_DURATION_SEC = 0.5
    
    def estimate_cost(
        self,
        num_pages: int,
        page_size: str = "medium",
        method: ExtractionMethod = ExtractionMethod.CSS,
        use_cache: bool = True,
        use_filtering: bool = True,
        cache_hit_rate: float = 0.3,
        filter_reduction: float = 0.7
    ) -> CostEstimate:
        """
        Estimate crawling costs for a given scenario
        
        Args:
            num_pages: Number of pages to crawl
            page_size: Page size category (small/medium/large/xlarge)
            method: Extraction method to use
            use_cache: Whether caching is enabled
            use_filtering: Whether content filtering is enabled
            cache_hit_rate: Expected cache hit rate (0.0-1.0)
            filter_reduction: Content reduction from filtering (0.0-1.0)
        
        Returns:
            CostEstimate with detailed breakdown
        """
        
        # Get base page token count
        base_tokens = self.AVG_TOKENS.get(page_size, self.AVG_TOKENS["medium"])
        
        # Apply filtering reduction
        if use_filtering and method in [ExtractionMethod.LLM_MINI, ExtractionMethod.LLM_STANDARD, ExtractionMethod.LLM_ADVANCED]:
            page_tokens = int(base_tokens * (1 - filter_reduction))
        else:
            page_tokens = base_tokens
        
        # Calculate costs based on method
        if method in [ExtractionMethod.BASELINE, ExtractionMethod.CSS, ExtractionMethod.REGEX]:
            # Free methods
            total_cost = 0.0
            duration_per_page = self.BASELINE_DURATION_SEC
            
            # CSS/Regex add minimal overhead
            if method in [ExtractionMethod.CSS, ExtractionMethod.REGEX]:
                duration_per_page *= 1.2
            
            return CostEstimate(
                method=method,
                num_pages=num_pages,
                avg_page_tokens=page_tokens,
                avg_extraction_tokens=0,
                avg_duration_sec=duration_per_page,
                total_input_tokens=0,
                total_output_tokens=0,
                total_cost_usd=0.0,
                total_duration_minutes=(num_pages * duration_per_page) / 60,
                cache_savings_percent=0.0,
                filter_savings_percent=0.0
            )
        
        # LLM-based extraction
        pricing = PRICING[method]
        
        # Estimate output tokens (typically 20-30% of input)
        output_tokens_per_page = int(page_tokens * 0.25)
        
        # Calculate per-page cost
        input_cost_per_page = (page_tokens / 1_000_000) * pricing.input_cost
        output_cost_per_page = (output_tokens_per_page / 1_000_000) * pricing.output_cost
        cost_per_page = input_cost_per_page + output_cost_per_page
        
        # Apply cache savings
        effective_pages = num_pages
        if use_cache:
            cache_hits = int(num_pages * cache_hit_rate)
            effective_pages = num_pages - cache_hits
        
        # Total costs
        total_input_tokens = effective_pages * page_tokens
        total_output_tokens = effective_pages * output_tokens_per_page
        total_cost = effective_pages * cost_per_page
        
        # Duration estimate
        total_tokens = total_input_tokens + total_output_tokens
        llm_time = total_tokens / pricing.avg_speed_tokens_per_sec
        crawl_time = num_pages * self.BASELINE_DURATION_SEC
        total_duration_sec = crawl_time + llm_time
        
        # Calculate savings
        base_cost = num_pages * cost_per_page
        cache_savings = ((base_cost - total_cost) / base_cost * 100) if use_cache and base_cost > 0 else 0.0
        
        base_tokens_no_filter = self.AVG_TOKENS.get(page_size, self.AVG_TOKENS["medium"])
        filter_savings = (1 - page_tokens / base_tokens_no_filter) * 100 if use_filtering else 0.0
        
        return CostEstimate(
            method=method,
            num_pages=num_pages,
            avg_page_tokens=page_tokens,
            avg_extraction_tokens=output_tokens_per_page,
            avg_duration_sec=total_duration_sec / num_pages,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_cost_usd=total_cost,
            total_duration_minutes=total_duration_sec / 60,
            cache_savings_percent=cache_savings,
            filter_savings_percent=filter_savings
        )
    
    def compare_methods(
        self,
        num_pages: int,
        page_size: str = "medium"
    ) -> List[CostEstimate]:
        """Compare all extraction methods side-by-side.

        Evaluates both free methods (Baseline, CSS) and LLM-based methods
        (GPT-4o-mini, GPT-4o) with optimizations enabled for a fair comparison.

        Args:
            num_pages: Number of pages to compare across.
            page_size: Page size category (small/medium/large/xlarge, default: medium).

        Returns:
            List of CostEstimate objects, one per extraction method, allowing
            direct comparison of costs, duration, and quality metrics.
        """

        results: List[CostEstimate] = []

        # Test free methods
        for method in [ExtractionMethod.BASELINE, ExtractionMethod.CSS]:
            estimate = self.estimate_cost(num_pages, page_size, method)
            results.append(estimate)

        # Test LLM methods with optimizations
        for method in [ExtractionMethod.LLM_MINI, ExtractionMethod.LLM_STANDARD]:
            estimate = self.estimate_cost(
                num_pages,
                page_size,
                method,
                use_cache=True,
                use_filtering=True
            )
            results.append(estimate)

        return results
    
    def print_estimate(self, estimate: CostEstimate) -> None:
        """Print formatted cost estimate with detailed breakdown.

        Displays a comprehensive estimate including per-page metrics, total costs,
        optimization savings (cache and filtering), and throughput metrics.

        Args:
            estimate: CostEstimate object to display.

        Returns:
            None. Output is printed to stdout.
        """

        print(f"\n{'='*60}")
        print(f"COST ESTIMATE: {estimate.method.value.upper()}")
        print(f"{'='*60}")
        print(f"Pages:              {estimate.num_pages:,}")
        print(f"Avg tokens/page:    {estimate.avg_page_tokens:,}")

        if estimate.total_cost_usd > 0:
            print(f"\n💰 COSTS:")
            print(f"  Total input:      {estimate.total_input_tokens:,} tokens")
            print(f"  Total output:     {estimate.total_output_tokens:,} tokens")
            print(f"  Cost per page:    ${estimate.total_cost_usd/estimate.num_pages:.4f}")
            print(f"  Total cost:       ${estimate.total_cost_usd:.2f}")

            if estimate.cache_savings_percent > 0:
                print(f"\n💾 CACHE SAVINGS:   {estimate.cache_savings_percent:.1f}%")

            if estimate.filter_savings_percent > 0:
                print(f"🔍 FILTER SAVINGS:  {estimate.filter_savings_percent:.1f}%")
        else:
            print(f"\n💰 COST:            FREE")

        print(f"\n⏱️  DURATION:")
        print(f"  Per page:         {estimate.avg_duration_sec:.2f}s")
        print(f"  Total:            {estimate.total_duration_minutes:.1f} minutes")
        print(f"  Throughput:       {estimate.num_pages/estimate.total_duration_minutes:.0f} pages/min")
    
    def print_comparison(self, estimates: List[CostEstimate]) -> None:
        """Print side-by-side comparison table of extraction methods.

        Displays cost, duration, and quality metrics for all extraction methods
        in an easy-to-scan tabular format for decision-making.

        Args:
            estimates: List of CostEstimate objects to compare.

        Returns:
            None. Output is printed to stdout as formatted table.
        """

        print(f"\n{'='*80}")
        print("METHOD COMPARISON")
        print(f"{'='*80}")
        print(f"{'Method':<20} {'Cost/Page':<12} {'Total Cost':<12} {'Duration':<12} {'Quality':<10}")
        print(f"{'-'*20} {'-'*12} {'-'*12} {'-'*12} {'-'*10}")

        for est in estimates:
            if est.total_cost_usd > 0:
                cost_per_page = f"${est.total_cost_usd/est.num_pages:.4f}"
                total_cost = f"${est.total_cost_usd:.2f}"
            else:
                cost_per_page = "FREE"
                total_cost = "FREE"

            duration = f"{est.total_duration_minutes:.1f}min"

            # Rough quality scores
            quality_map: Dict[ExtractionMethod, str] = {
                ExtractionMethod.BASELINE: "Medium",
                ExtractionMethod.CSS: "High",
                ExtractionMethod.LLM_MINI: "Very High",
                ExtractionMethod.LLM_STANDARD: "Excellent",
            }
            quality = quality_map.get(est.method, "N/A")

            print(f"{est.method.value:<20} {cost_per_page:<12} {total_cost:<12} {duration:<12} {quality:<10}")
    
    def monthly_budget_plan(
        self,
        daily_pages: int,
        method: ExtractionMethod = ExtractionMethod.LLM_MINI,
        page_size: str = "medium"
    ) -> None:
        """Calculate and display monthly budget requirements with optimization tips.

        Projects daily crawl costs to monthly budgets and provides actionable
        optimization recommendations for cache, filtering, and method selection.

        Args:
            daily_pages: Number of pages to crawl per day.
            method: Extraction method to use (default: LLM_MINI).
            page_size: Page size category (small/medium/large/xlarge, default: medium).

        Returns:
            None. Output is printed to stdout with budget breakdown and tips.
        """

        daily_estimate = self.estimate_cost(
            daily_pages,
            page_size,
            method,
            use_cache=True,
            use_filtering=True,
            cache_hit_rate=0.3
        )

        monthly_pages = daily_pages * 30
        monthly_cost = daily_estimate.total_cost_usd * 30

        print(f"\n{'='*60}")
        print("MONTHLY BUDGET PLAN")
        print(f"{'='*60}")
        print(f"Method:           {method.value}")
        print(f"Daily pages:      {daily_pages:,}")
        print(f"Monthly pages:    {monthly_pages:,}")
        print(f"Daily cost:       ${daily_estimate.total_cost_usd:.2f}")
        print(f"Monthly cost:     ${monthly_cost:.2f}")
        print(f"Cost per 1000:    ${(monthly_cost/monthly_pages*1000):.2f}")

        # Break-even analysis
        print(f"\n💡 OPTIMIZATION TIPS:")

        if method in [ExtractionMethod.LLM_STANDARD, ExtractionMethod.LLM_ADVANCED]:
            savings = monthly_cost * 0.95  # 95% savings with mini
            print(f"  • Switch to GPT-4o-mini: Save ${savings:.2f}/month (95% reduction)")

        if daily_estimate.filter_savings_percent < 50:
            print(f"  • Enable aggressive filtering: Reduce costs by 50-70%")

        if daily_estimate.cache_savings_percent < 20:
            print(f"  • Increase cache hit rate: Target 30-40% for 20-30% savings")

        print(f"  • Use CSS extraction where possible: Zero LLM costs")

def main() -> None:
    """Interactive cost calculator with scenario examples.

    Demonstrates four practical use cases for the Crawl4AI cost calculator:
    1. Single scenario estimation for a medium blog
    2. Method comparison across free and LLM-based approaches
    3. Monthly budget planning for sustained operations
    4. ROI analysis comparing manual vs automated extraction

    This is a reference implementation showing how to use CostCalculator
    for capacity planning and cost optimization decisions.

    Returns:
        None. Output is printed to stdout showing all scenarios.
    """

    print("Crawl4AI Cost Calculator")
    print("="*60)

    calc = CostCalculator()

    # Example 1: Single scenario
    print("\n📊 SCENARIO 1: Medium Blog (1000 articles)")
    estimate = calc.estimate_cost(
        num_pages=1000,
        page_size="medium",
        method=ExtractionMethod.LLM_MINI,
        use_cache=True,
        use_filtering=True
    )
    calc.print_estimate(estimate)

    # Example 2: Comparison
    print("\n\n📊 SCENARIO 2: Method Comparison (100 pages)")
    estimates = calc.compare_methods(num_pages=100, page_size="large")
    calc.print_comparison(estimates)

    # Example 3: Monthly budget
    print("\n\n📊 SCENARIO 3: Monthly Budget Planning")
    calc.monthly_budget_plan(
        daily_pages=500,
        method=ExtractionMethod.LLM_MINI,
        page_size="medium"
    )

    # Example 4: ROI analysis
    print(f"\n\n{'='*60}")
    print("💰 ROI ANALYSIS")
    print(f"{'='*60}")

    # Compare doing it manually vs automated
    manual_time_per_page = 5  # minutes
    hourly_rate = 50  # USD

    pages = 1000
    manual_cost = (pages * manual_time_per_page / 60) * hourly_rate

    automated = calc.estimate_cost(pages, "medium", ExtractionMethod.LLM_MINI)
    automated_cost = automated.total_cost_usd

    savings = manual_cost - automated_cost
    time_saved = (pages * manual_time_per_page) / 60  # hours

    print(f"Manual extraction:    ${manual_cost:,.2f} ({time_saved:.0f} hours)")
    print(f"Automated (Crawl4AI): ${automated_cost:.2f} ({automated.total_duration_minutes/60:.1f} hours)")
    print(f"Savings:              ${savings:,.2f} ({(savings/manual_cost*100):.1f}%)")
    print(f"Time saved:           {time_saved:.0f} hours")

    print(f"\n✅ Automation pays for itself after {int(automated_cost/hourly_rate*60/5)} pages")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python cost_calculator.py")
        print("\nCalculates crawling costs for various scenarios")
        print("Edit the script to customize scenarios")
        sys.exit(0)
    
    main()
