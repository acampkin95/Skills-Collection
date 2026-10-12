#!/usr/bin/env python3
"""
Cost Estimator - Estimate and track AI project costs.

This module provides capabilities for:
- Token counting and pricing
- Model comparison
- Budget tracking
- Cost optimization suggestions
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of AI models."""
    TEXT = "text"
    VISION = "vision"
    EMBEDDING = "embedding"
    SPEECH = "speech"
    MULTIMODAL = "multimodal"


@dataclass
class ModelPricing:
    """Pricing information for a model."""
    model_name: str
    provider: str
    input_price_per_million: float  # per 1M tokens
    output_price_per_million: float  # per 1M tokens
    context_window: int
    max_output: int
    supports_streaming: bool = True

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Estimate cost for given token counts."""
        input_cost = (input_tokens / 1_000_000) * self.input_price_per_million
        output_cost = (output_tokens / 1_000_000) * self.output_price_per_million
        return input_cost + output_cost


@dataclass
class TokenUsage:
    """Token usage for a request."""
    model_name: str
    input_tokens: int
    output_tokens: int
    timestamp: datetime
    request_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class CostBudget:
    """Cost budget configuration."""
    max_tokens: int = 1_000_000
    max_cost: float = 100.0
    warning_threshold: float = 0.8  # Warn at 80% of budget
    period: str = "monthly"  # daily, weekly, monthly, project

    def remaining_at_warning(self) -> float:
        return self.max_cost * (1 - self.warning_threshold)


class CostEstimator:
    """
    Cost estimation and tracking for AI projects.

    Tracks token usage, calculates costs, and provides optimization suggestions.
    """

    # Default model pricing (per 1M tokens)
    DEFAULT_PRICING = {
        "MiniMax-M2": ModelPricing(
            model_name="MiniMax-M2",
            provider="MiniMax",
            input_price_per_million=0.30,
            output_price_per_million=0.90,
            context_window=196000,
            max_output=8192,
            supports_streaming=True
        ),
        "Claude-Sonnet-4": ModelPricing(
            model_name="Claude-Sonnet-4",
            provider="Anthropic",
            input_price_per_million=3.00,
            output_price_per_million=15.00,
            context_window=200000,
            max_output=8192,
            supports_streaming=True
        ),
        "Claude-Haiku-3": ModelPricing(
            model_name="Claude-Haiku-3",
            provider="Anthropic",
            input_price_per_million=0.25,
            output_price_per_million=1.25,
            context_window=200000,
            max_output=8192,
            supports_streaming=True
        ),
        "GPT-4o": ModelPricing(
            model_name="GPT-4o",
            provider="OpenAI",
            input_price_per_million=5.00,
            output_price_per_million=15.00,
            context_window=128000,
            max_output=16384,
            supports_streaming=True
        ),
        "GPT-4o-mini": ModelPricing(
            model_name="GPT-4o-mini",
            provider="OpenAI",
            input_price_per_million=0.15,
            output_price_per_million=0.60,
            context_window=128000,
            max_output=16384,
            supports_streaming=True
        ),
        "Gemini-1.5-Pro": ModelPricing(
            model_name="Gemini-1.5-Pro",
            provider="Google",
            input_price_per_million=1.25,
            output_price_per_million=5.00,
            context_window=2000000,
            max_output=8192,
            supports_streaming=True
        )
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.pricing = self.DEFAULT_PRICING.copy()
        self.usage_history: List[TokenUsage] = []
        self.budget: Optional[CostBudget] = None
        self.cost_history: List[Dict[str, Any]] = []
        self._add_custom_pricing()

    def _add_custom_pricing(self) -> None:
        """Add custom pricing from config."""
        custom = self.config.get('custom_pricing', {})
        for model_name, pricing_data in custom.items():
            self.pricing[model_name] = ModelPricing(
                model_name=model_name,
                provider=pricing_data.get('provider', 'custom'),
                input_price_per_million=pricing_data.get('input_per_million', 1.0),
                output_price_per_million=pricing_data.get('output_per_million', 1.0),
                context_window=pricing_data.get('context_window', 128000),
                max_output=pricing_data.get('max_output', 4096)
            )

    def set_budget(
        self,
        max_tokens: int = 1_000_000,
        max_cost: float = 100.0,
        warning_threshold: float = 0.8,
        period: str = "monthly"
    ) -> CostBudget:
        """Set a cost budget."""
        self.budget = CostBudget(
            max_tokens=max_tokens,
            max_cost=max_cost,
            warning_threshold=warning_threshold,
            period=period
        )
        return self.budget

    def log_usage(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TokenUsage:
        """Log token usage for a request."""
        usage = TokenUsage(
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            timestamp=datetime.now(),
            request_id=request_id or "",
            metadata=metadata or {}
        )

        self.usage_history.append(usage)

        # Calculate and log cost
        cost = self.calculate_cost(model_name, input_tokens, output_tokens)
        self.cost_history.append({
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": usage.total_tokens,
            "cost": cost
        })

        # Check budget
        if self.budget:
            self._check_budget_status()

        return usage

    def calculate_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for given model and token counts."""
        pricing = self.pricing.get(model_name)

        if not pricing:
            logger.warning(f"Unknown model {model_name}, using default pricing")
            pricing = self.pricing.get("MiniMax-M2", ModelPricing(
                model_name="unknown",
                provider="unknown",
                input_price_per_million=1.0,
                output_price_per_million=1.0,
                context_window=100000,
                max_output=4000
            ))

        return pricing.estimate_cost(input_tokens, output_tokens)

    def estimate_session_cost(
        self,
        model_name: str,
        expected_input_tokens: int,
        expected_output_tokens: int,
        request_count: int = 1
    ) -> Dict[str, Any]:
        """Estimate cost for a session with given parameters."""
        per_request = self.calculate_cost(
            model_name,
            expected_input_tokens,
            expected_output_tokens
        )
        total_cost = per_request * request_count
        total_tokens = (expected_input_tokens + expected_output_tokens) * request_count

        return {
            "model": model_name,
            "request_count": request_count,
            "input_tokens_per_request": expected_input_tokens,
            "output_tokens_per_request": expected_output_tokens,
            "total_tokens": total_tokens,
            "cost_per_request": round(per_request, 4),
            "total_estimated_cost": round(total_cost, 4)
        }

    def get_model_comparison(
        self,
        input_tokens: int,
        output_tokens: int,
        context_window_required: int
    ) -> List[Dict[str, Any]]:
        """
        Compare costs across models.

        Returns models sorted by cost-effectiveness for the task.
        """
        comparisons = []

        for name, pricing in self.pricing.items():
            # Check if model can handle the context
            if context_window_required > pricing.context_window:
                continue

            cost = pricing.estimate_cost(input_tokens, output_tokens)

            comparisons.append({
                "model": name,
                "provider": pricing.provider,
                "context_window": pricing.context_window,
                "max_output": pricing.max_output,
                "estimated_cost": round(cost, 4),
                "supports_streaming": pricing.supports_streaming,
                "cost_per_1k_input": round(pricing.input_price_per_million / 1000, 4),
                "cost_per_1k_output": round(pricing.output_price_per_million / 1000, 4)
            })

        # Sort by cost
        comparisons.sort(key=lambda x: x["estimated_cost"])

        return comparisons

    def get_current_status(self) -> Dict[str, Any]:
        """Get current cost and usage status."""
        if not self.usage_history:
            return {
                "status": "no_data",
                "message": "No usage recorded yet"
            }

        total_cost = sum(
            self.calculate_cost(u.model_name, u.input_tokens, u.output_tokens)
            for u in self.usage_history
        )
        total_tokens = sum(u.total_tokens for u in self.usage_history)

        # Group by model
        by_model = defaultdict(lambda: {"requests": 0, "input_tokens": 0, "output_tokens": 0})
        for usage in self.usage_history:
            by_model[usage.model_name]["requests"] += 1
            by_model[usage.model_name]["input_tokens"] += usage.input_tokens
            by_model[usage.model_name]["output_tokens"] += usage.output_tokens

        result = {
            "status": "active",
            "total_requests": len(self.usage_history),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "by_model": dict(by_model)
        }

        # Add budget status if set
        if self.budget:
            budget_status = self._check_budget_status()
            result["budget"] = budget_status

        return result

    def _check_budget_status(self) -> Dict[str, Any]:
        """Check current budget status."""
        if not self.budget:
            return {}

        total_cost = sum(
            self.calculate_cost(u.model_name, u.input_tokens, u.output_tokens)
            for u in self.usage_history
        )
        total_tokens = sum(u.total_tokens for u in self.usage_history)

        budget_used_percent = (total_cost / self.budget.max_cost) * 100
        tokens_used_percent = (total_tokens / self.budget.max_tokens) * 100

        status = {
            "budget_limit": self.budget.max_cost,
            "budget_used": round(total_cost, 4),
            "budget_remaining": round(self.budget.max_cost - total_cost, 4),
            "budget_used_percent": round(budget_used_percent, 1),
            "tokens_limit": self.budget.max_tokens,
            "tokens_used": total_tokens,
            "tokens_remaining": self.budget.max_tokens - total_tokens,
            "tokens_used_percent": round(tokens_used_percent, 1),
            "period": self.budget.period
        }

        # Determine alert level
        if budget_used_percent >= 100:
            status["alert_level"] = "exceeded"
            status["message"] = "Budget exceeded!"
        elif budget_used_percent >= self.budget.warning_threshold * 100:
            status["alert_level"] = "warning"
            status["message"] = f"Approaching budget limit ({budget_used_percent:.1f}% used)"
        else:
            status["alert_level"] = "ok"
            status["message"] = f"Budget healthy ({budget_used_percent:.1f}% used)"

        return status

    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Generate cost optimization suggestions."""
        suggestions = []

        if not self.usage_history:
            return [{"message": "Record usage data to get optimization suggestions"}]

        # Analyze usage patterns
        total_cost = sum(
            self.calculate_cost(u.model_name, u.input_tokens, u.output_tokens)
            for u in self.usage_history
        )

        # Check for expensive model usage
        model_costs = defaultdict(float)
        for usage in self.usage_history:
            cost = self.calculate_cost(
                usage.model_name,
                usage.input_tokens,
                usage.output_tokens
            )
            model_costs[usage.model_name] += cost

        expensive_models = [
            (model, cost) for model, cost in model_costs.items()
            if cost > total_cost * 0.3 and cost > 10.0
        ]

        if expensive_models:
            suggestions.append({
                "type": "model_selection",
                "priority": "high",
                "message": f"Consider using a cheaper model for some tasks",
                "details": f"{len(expensive_models)} model(s) account for >30% of costs",
                "models": [m for m, _ in expensive_models],
                "recommendation": "Compare with cheaper alternatives like GPT-4o-mini or Claude-Haiku-3 for simpler tasks"
            })

        # Check for high token usage
        avg_tokens = sum(u.total_tokens for u in self.usage_history) / len(self.usage_history)

        if avg_tokens > 100000:
            suggestions.append({
                "type": "context_optimization",
                "priority": "medium",
                "message": "High average token usage detected",
                "details": f"Average {avg_tokens:.0f} tokens per request",
                "recommendation": "Consider truncating context or using summarization for long inputs"
            })

        # Check for streaming usage
        streaming_models = [m for m, p in self.pricing.items() if p.supports_streaming]
        non_streaming_usage = [
            u for u in self.usage_history
            if not u.metadata.get('streaming', True) and u.model_name in streaming_models
        ]

        if len(non_streaming_usage) > len(self.usage_history) * 0.5:
            suggestions.append({
                "type": "streaming",
                "priority": "low",
                "message": "Consider using streaming for faster responses",
                "details": "Many requests could benefit from streaming",
                "recommendation": "Enable streaming to improve perceived latency"
            })

        # Check for prompt optimization opportunities
        total_output_tokens = sum(u.output_tokens for u in self.usage_history)
        if total_output_tokens > 0:
            output_ratio = sum(u.input_tokens for u in self.usage_history) / total_output_tokens

            if output_ratio < 1:  # Output heavier than input
                suggestions.append({
                    "type": "prompt_engineering",
                    "priority": "medium",
                    "message": "Output-heavy workload detected",
                    "details": f"Input/output ratio: {output_ratio:.2f}",
                    "recommendation": "Consider more specific prompts to reduce output token generation"
                })

        return suggestions

    def get_cost_forecast(
        self,
        days: int = 30,
        daily_request_estimate: Optional[int] = None
    ) -> Dict[str, Any]:
        """Forecast future costs based on historical patterns."""
        if not self.usage_history:
            return {"message": "Insufficient data for forecasting"}

        # Calculate daily averages
        now = datetime.now()
        oldest = min(u.timestamp for u in self.usage_history)
        days_of_data = max(1, (now - oldest).days)

        daily_avg_requests = len(self.usage_history) / days_of_data
        daily_avg_tokens = sum(u.total_tokens for u in self.usage_history) / days_of_data
        daily_avg_cost = sum(
            self.calculate_cost(u.model_name, u.input_tokens, u.output_tokens)
            for u in self.usage_history
        ) / days_of_data

        # Use estimate if provided
        if daily_request_estimate:
            daily_avg_requests = daily_request_estimate
            daily_avg_tokens = daily_avg_tokens * (daily_request_estimate / (len(self.usage_history) / days_of_data))
            daily_avg_cost = daily_avg_cost * (daily_request_estimate / (len(self.usage_history) / days_of_data))

        # Calculate projections
        projected_requests = int(daily_avg_requests * days)
        projected_tokens = int(daily_avg_tokens * days)
        projected_cost = daily_avg_cost * days

        return {
            "projection_days": days,
            "historical_days": days_of_data,
            "daily_averages": {
                "requests": round(daily_avg_requests, 1),
                "tokens": int(daily_avg_tokens),
                "cost": round(daily_avg_cost, 4)
            },
            "projected": {
                "requests": projected_requests,
                "tokens": projected_tokens,
                "cost": round(projected_cost, 4)
            },
            "monthly_estimate": round(projected_cost * 30 / days, 4),
            "confidence": "medium" if days_of_data >= 7 else "low"
        }

    def export_report(self, format: str = "json") -> str:
        """Export cost report."""
        status = self.get_current_status()
        forecast = self.get_cost_forecast()
        suggestions = self.get_optimization_suggestions()

        report = {
            "generated_at": datetime.now().isoformat(),
            "current_status": status,
            "forecast": forecast,
            "suggestions": suggestions
        }

        if format == "json":
            return json.dumps(report, indent=2)
        elif format == "markdown":
            return self._generate_markdown_report(report)
        else:
            return json.dumps(report, indent=2)

    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Generate markdown cost report."""
        status = report["current_status"]
        forecast = report["forecast"]
        suggestions = report["suggestions"]

        lines = [
            "# AI Cost Report",
            f"Generated: {report['generated_at']}",
            "",
            "## Current Status",
            f"- **Total Requests:** {status.get('total_requests', 0)}",
            f"- **Total Tokens:** {status.get('total_tokens', 0):,}",
            f"- **Total Cost:** ${status.get('total_cost', 0):.4f}",
            ""
        ]

        if 'budget' in status:
            budget = status['budget']
            lines.extend([
                "## Budget Status",
                f"- **Budget Limit:** ${budget['budget_limit']:.2f}",
                f"- **Used:** ${budget['budget_used']:.4f} ({budget['budget_used_percent']}%)",
                f"- **Remaining:** ${budget['budget_remaining']:.4f}",
                f"- **Status:** {budget['alert_level'].upper()}",
                ""
            ])

        lines.extend([
            "## Cost Forecast",
            f"- **Projected Cost ({forecast['projection_days']} days):** ${forecast['projected']['cost']:.4f}",
            f"- **Monthly Estimate:** ${forecast['monthly_estimate']:.4f}",
            f"- **Confidence:** {forecast['confidence']}",
            ""
        ])

        if suggestions:
            lines.extend([
                "## Optimization Suggestions",
                ""
            ])
            for suggestion in suggestions:
                lines.extend([
                    f"### [{suggestion['priority'].upper()}] {suggestion['message']}",
                    suggestion.get('details', ''),
                    f"**Recommendation:** {suggestion['recommendation']}",
                    ""
                ])

        return "\n".join(lines)


def main():
    """CLI entry point for cost estimator."""
    import argparse

    parser = argparse.ArgumentParser(description="Cost Estimator CLI")
    parser.add_argument("command", choices=[
        "status", "estimate", "compare", "forecast", "report"
    ])

    args = parser.parse_args()

    estimator = CostEstimator()

    if args.command == "status":
        print(json.dumps(estimator.get_current_status(), indent=2))

    elif args.command == "estimate":
        model = input("Model: ")
        input_tok = int(input("Input tokens: "))
        output_tok = int(input("Output tokens: "))
        cost = estimator.calculate_cost(model, input_tok, output_tok)
        print(f"Estimated cost: ${cost:.4f}")

    elif args.command == "compare":
        input_tok = int(input("Input tokens: "))
        output_tok = int(input("Output tokens: "))
        context = int(input("Context window required: "))
        comparison = estimator.get_model_comparison(input_tok, output_tok, context)
        print(json.dumps(comparison, indent=2))

    elif args.command == "forecast":
        print(json.dumps(estimator.get_cost_forecast(), indent=2))

    elif args.command == "report":
        print(estimator.export_report(format="markdown"))


if __name__ == "__main__":
    main()
