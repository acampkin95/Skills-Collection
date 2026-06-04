#!/usr/bin/env python3
"""
Content Planner - AI-powered content extraction and planning.

Usage:
    python3 content-planner.py analyze <url>
    python3 content-planner.py plan <url> --output <file.md>
    python3 content-planner.py batch <urls-file> --format markdown
"""

import asyncio
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, List
import aiohttp

@dataclass
class ContentPlan:
    title: str
    summary: str
    key_points: List[str]
    action_items: List[str]
    resources: List[str]
    estimated_time: str
    difficulty: str

class ContentPlanner:
    def __init__(self):
        self.session = None

    async def fetch_content(self, url: str) -> Dict:
        """Fetch and parse content from URL."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                content = await response.text()

                # Extract key information
                title = self.extract_title(content)
                headings = self.extract_headings(content)
                paragraphs = self.extract_paragraphs(content)

                return {
                    "url": url,
                    "title": title,
                    "headings": headings,
                    "paragraphs": paragraphs,
                    "word_count": len(paragraphs.split()),
                }

    def extract_title(self, html: str) -> str:
        """Extract page title."""
        title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
        return title_match.group(1) if title_match else "Untitled"

    def extract_headings(self, html: str) -> List[str]:
        """Extract all headings."""
        pattern = r'<h[1-6][^>]*>([^<]+)</h[1-6]>'
        matches = re.findall(pattern, html, re.IGNORECASE)
        return [h.strip() for h in matches if h.strip()]

    def extract_paragraphs(self, html: str) -> str:
        """Extract main text content."""
        # Remove script and style tags
        clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
        # Extract paragraphs
        paragraphs = re.findall(r'<p[^>]*>([^<]+)</p>', clean, re.IGNORECASE)
        return ' '.join([p.strip() for p in paragraphs if p.strip()])

    def generate_plan(self, content: Dict) -> ContentPlan:
        """Generate action plan from content."""
        title = content["title"]
        headings = content["headings"]
        paragraphs = content["paragraphs"]

        # Generate key points from headings
        key_points = headings[:5] if headings else ["Main topic covered"]

        # Generate action items based on content type
        action_items = self.infer_action_items(content)

        # Extract resources (links)
        resources = self.extract_resources(content.get("url", ""))

        # Estimate time and difficulty
        word_count = content.get("word_count", 0)
        estimated_time = self.estimate_time(word_count)
        difficulty = self.assess_difficulty(word_count, headings)

        return ContentPlan(
            title=title,
            summary=self.generate_summary(paragraphs),
            key_points=key_points,
            action_items=action_items,
            resources=resources,
            estimated_time=estimated_time,
            difficulty=difficulty,
        )

    def generate_summary(self, text: str) -> str:
        """Generate brief summary."""
        sentences = text.split('.')[:3]
        return '. '.join([s.strip() for s in sentences if s.strip()]) + '.'

    def infer_action_items(self, content: Dict) -> List[str]:
        """Infer action items from content."""
        headings = content.get("headings", [])
        items = []

        # Common patterns
        if any("install" in h.lower() for h in headings):
            items.append("Install required dependencies")
        if any("setup" in h.lower() or "configur" in h.lower() for h in headings):
            items.append("Set up configuration")
        if any("deploy" in h.lower() for h in headings):
            items.append("Deploy to production")
        if any("test" in h.lower() for h in headings):
            items.append("Test implementation")
        if any("api" in h.lower() or "endpoint" in h.lower() for h in headings):
            items.append("Review API integration")

        # Default items
        if not items:
            items = [
                "Review the content",
                "Identify actionable steps",
                "Implement changes",
                "Test the results"
            ]

        return items[:5]

    def extract_resources(self, url: str) -> List[str]:
        """Extract linked resources."""
        # This would typically parse the HTML for links
        return [url]  # Return the source URL as primary resource

    def estimate_time(self, word_count: int) -> str:
        """Estimate reading/implementation time."""
        minutes = word_count // 200  # ~200 words per minute

        if minutes < 15:
            return "15 min"
        elif minutes < 30:
            return "30 min"
        elif minutes < 60:
            return "1 hour"
        elif minutes < 120:
            return "2 hours"
        else:
            return f"{minutes // 60}+ hours"

    def assess_difficulty(self, word_count: int, headings: List[str]) -> str:
        """Assess content difficulty."""
        # Simple heuristic based on length and complexity
        if len(headings) < 5 or word_count < 500:
            return "Beginner"
        elif len(headings) < 10 or word_count < 2000:
            return "Intermediate"
        else:
            return "Advanced"

    def format_markdown(self, plan: ContentPlan, url: str) -> str:
        """Format plan as markdown."""
        return f"""# {plan.title}

**Source:** {url}
**Time:** {plan.estimated_time}
**Difficulty:** {plan.difficulty}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary

{plan.summary}

## Key Points

{chr(10).join(f"- {point}" for point in plan.key_points)}

## Action Items

{chr(10).join(f"1. [ ] {item}" for item in plan.action_items)}

## Resources

{chr(10).join(f"- {resource}" for resource in plan.resources)}

---

*Generated by Tapestry Content Planner*
"""

async def cmd_analyze(url: str):
    """Analyze a single URL."""
    planner = ContentPlanner()
    content = await planner.fetch_content(url)
    plan = planner.generate_plan(content)

    print(f"\n{'='*60}")
    print(f"ANALYSIS: {plan.title}")
    print(f"{'='*60}")
    print(f"\nDifficulty: {plan.difficulty}")
    print(f"Estimated Time: {plan.estimated_time}")
    print(f"Word Count: {content.get('word_count', 0)}")
    print(f"\nKey Points ({len(plan.key_points)}):")
    for point in plan.key_points:
        print(f"  - {point}")
    print(f"\nRecommended Actions:")
    for item in plan.action_items:
        print(f"  - {item}")

async def cmd_plan(url: str, output: str = None):
    """Generate plan for URL and optionally save."""
    planner = ContentPlanner()
    content = await planner.fetch_content(url)
    plan = planner.generate_plan(content)

    markdown = planner.format_markdown(plan, url)

    if output:
        with open(output, 'w') as f:
            f.write(markdown)
        print(f"Plan saved to: {output}")
    else:
        print(markdown)

async def cmd_batch(urls_file: str, format: str = "markdown"):
    """Process multiple URLs."""
    with open(urls_file) as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"Processing {len(urls)} URLs...")

    planner = ContentPlanner()
    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        try:
            content = await planner.fetch_content(url)
            plan = planner.generate_plan(content)
            results.append({"url": url, "title": plan.title, "success": True})
        except Exception as e:
            results.append({"url": url, "error": str(e), "success": False})

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    for result in results:
        if result["success"]:
            print(f"  ✓ {result['title']}")
        else:
            print(f"  ✗ {result['url']}: {result['error']}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Content Planner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a URL")
    analyze_parser.add_argument("url")

    plan_parser = subparsers.add_parser("plan", help="Generate plan for URL")
    plan_parser.add_argument("url")
    plan_parser.add_argument("--output", "-o", help="Output file")

    batch_parser = subparsers.add_parser("batch", help="Process multiple URLs")
    batch_parser.add_argument("urls_file")
    batch_parser.add_argument("--format", default="markdown")

    args = parser.parse_args()

    if args.command == "analyze":
        asyncio.run(cmd_analyze(args.url))
    elif args.command == "plan":
        asyncio.run(cmd_plan(args.url, args.output))
    elif args.command == "batch":
        asyncio.run(cmd_batch(args.urls_file, args.format))

if __name__ == "__main__":
    main()
