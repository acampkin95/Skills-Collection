#!/usr/bin/env python3
"""
GitHub Repository Analyzer - Analyze and extract information from GitHub repositories.

This script crawls GitHub repositories to extract:
- Repository metadata (stars, forks, issues)
- File structure and contents
- README content
- Dependencies and packages
- Contributors
- Recent activity

Usage:
    python github-repo-analysis.py <repo-url>
    python github-repo-analysis.py https://github.com/user/repo --output ./analysis
    python github-repo-analysis.py --batch repos.txt --analyze-code
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.content_filter_strategy import PruningContentFilter
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
except ImportError:
    print("Error: crawl4ai not installed. Run: pip install crawl4ai")
    sys.exit(1)


class GitHubRepoAnalyzer:
    """Analyze GitHub repositories."""

    def __init__(self, output_dir: str = "./github_analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_repo_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL to extract owner and repo."""
        patterns = [
            r'github\.com/([^/]+)/([^/]+)/?',  # Full URL
            r'([^/]+)/([^/]+)',  # owner/repo format
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                repo = repo.rstrip('/').replace('.git', '')
                return {"owner": owner, "repo": repo, "url": f"https://github.com/{owner}/{repo}"}

        return {"owner": None, "repo": None, "url": url}

    async def extract_repo_metadata(self, url: str) -> Dict[str, Any]:
        """Extract repository metadata from GitHub page."""
        js_extraction = """
        async () => {
            const data = {
                url: window.location.href,
                metadata: {},
                social_stats: {},
                topics: [],
                description: ""
            };

            // Repository name and owner
            const repoHeader = document.querySelector('.repo-head .flex-auto');
            if (repoHeader) {
                data.full_name = repoHeader.textContent?.trim();
            }

            // Description
            const desc = document.querySelector('[itemprop="description"]');
            data.description = desc?.content || desc?.textContent?.trim();

            // Stars
            const stars = document.querySelector('[href*="/stargazers"]') ||
                        document.querySelector('.social-count[aria-label*="star"]');
            data.social_stats.stars = stars?.textContent?.trim();

            // Forks
            const forks = document.querySelector('[href*="/forks"]') ||
                         document.querySelector('.social-count[aria-label*="fork"]');
            data.social_stats.forks = forks?.textContent?.trim();

            // Watchers
            const watchers = document.querySelector('.social-count[aria-label*="watch"]');
            data.social_stats.watchers = watchers?.textContent?.trim();

            // Topics
            const topicElements = document.querySelectorAll('[class*="topic"] a');
            topicElements.forEach(t => {
                data.topics.push(t.textContent?.trim());
            });

            // Primary language
            const lang = document.querySelector('[itemprop="programmingLanguage"]');
            data.metadata.language = lang?.textContent?.trim() || lang?.content;

            // License
            const license = document.querySelector('[itemprop="license"]');
            data.metadata.license = license?.textContent?.trim();

            // Last updated
            const updated = document.querySelector('relative-time');
            data.metadata.last_updated = updated?.getAttribute('datetime');

            // Open issues
            const issues = document.querySelector('[href*="/issues"] .Counter');
            data.metadata.open_issues = issues?.textContent?.trim();

            // Pull requests count
            const prs = document.querySelector('[href*="/pulls"] .Counter');
            data.metadata.pull_requests = prs?.textContent?.trim();

            return data;
        }
        """

        browser_config = BrowserConfig(
            headless=True,
            viewport_width=1400,
            viewport_height=900,
        )
        crawler_config = CrawlerRunConfig(
            js_code=js_extraction,
            page_timeout=30000,
            wait_for="networkidle",
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return result.js_result or {}

        return {"error": "Failed to extract metadata"}

    async def extract_readme(self, url: str) -> Dict[str, Any]:
        """Extract README content."""
        content_filter = PruningContentFilter(threshold=0.4)
        md_generator = DefaultMarkdownGenerator(content_filter=content_filter)

        # Navigate to README
        readme_url = url.rstrip('/') + '/README.md'

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(
            markdown_generator=md_generator,
            page_timeout=30000,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(readme_url, config=crawler_config)

            if result.success:
                return {
                    "readme_found": True,
                    "content": result.markdown,
                    "raw": result.markdown.raw_markdown if hasattr(result.markdown, 'raw_markdown') else str(result.markdown),
                }

        # Try HTML rendered README
        readme_html_url = url.rstrip('/') + '?tab=readme'
        result = await crawler.arun(readme_html_url, config=crawler_config)

        if result.success:
            return {
                "readme_found": True,
                "content": result.markdown,
            }

        return {"readme_found": False}

    async def extract_file_structure(self, url: str) -> Dict[str, Any]:
        """Extract repository file structure."""
        js_extraction = """
        async () => {
            const data = {
                files: [],
                directories: [],
                structure: {}
            };

            // Get all file/dir rows
            const rows = document.querySelectorAll('.react-directory-row');
            rows.forEach(row => {
                const type = row.querySelector('[data-testid="file-icon"]')?.classList.contains('octicon-file')
                    ? 'file' : 'directory';

                const link = row.querySelector('a[href*="/blob/"], a[href*="/tree/"]');
                const name = link?.textContent?.trim();
                const path = link?.href;

                if (name) {
                    const entry = {
                        name,
                        type,
                        path: path?.replace('https://github.com', '')
                    };

                    if (type === 'file') {
                        // Get file info
                        const meta = row.querySelector('.octicon-file, .octicon');
                        entry.icon = meta?.className?.includes('file') ? '📄' : '📁';

                        data.files.push(entry);
                    } else {
                        data.directories.push(entry);
                    }
                }
            });

            // Get directory path
            const breadcrumb = document.querySelector('.breadcrumb');
            if (breadcrumb) {
                data.current_path = breadcrumb.textContent?.trim();
            }

            return data;
        }
        """

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(js_code=js_extraction)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=crawler_config)

            if result.success:
                return result.js_result or {}

        return {"error": "Failed to extract structure"}

    async def extract_dependencies(self, url: str) -> Dict[str, Any]:
        """Extract dependency information from package files."""
        package_files = [
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
            "Gemfile",
            "composer.json",
            "nuget.config",
        ]

        dependencies = {}
        parsed = self.parse_repo_url(url)

        for package_file in package_files:
            file_url = f"https://github.com/{parsed['owner']}/{parsed['repo']}/raw/main/{package_file}"

            browser_config = BrowserConfig(headless=True)
            crawler_config = CrawlerRunConfig(page_timeout=10000)

            try:
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    result = await crawler.arun(file_url, config=crawler_config)

                    if result.success and result.markdown:
                        dependencies[package_file] = {
                            "found": True,
                            "content": result.markdown[:5000],
                        }
            except Exception:
                pass

        return {"dependencies": dependencies}

    async def extract_contributors(self, url: str) -> Dict[str, Any]:
        """Extract contributor information."""
        js_extraction = """
        async () => {
            const contributors = [];
            const cards = document.querySelectorAll('.BorderGrid .Avatar');

            cards.forEach((card, i) => {
                if (i >= 30) return; // Limit to top 30

                const link = card.closest('a');
                contributors.push({
                    username: link?.href?.split('/').pop(),
                    avatar: card.src,
                    profile_url: link?.href
                });
            });

            return {
                count: contributors.length,
                contributors: contributors
            };
        }
        """

        contributors_url = url.rstrip('/') + '/graphs/contributors'

        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(js_code=js_extraction)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(contributors_url, config=crawler_config)

            if result.success:
                return result.js_result or {}

        return {"contributors": []}

    async def analyze_repo(self, url: str, include_code: bool = False) -> Dict[str, Any]:
        """Complete repository analysis."""
        parsed = self.parse_repo_url(url)

        print(f"Analyzing: {parsed['owner']}/{parsed['repo']}")

        analysis = {
            "repository": parsed,
            "analyzed_at": datetime.now().isoformat(),
            "sections": {},
        }

        # Extract metadata
        print("  - Extracting metadata...")
        analysis["sections"]["metadata"] = await self.extract_repo_metadata(url)

        # Extract README
        print("  - Extracting README...")
        analysis["sections"]["readme"] = await self.extract_readme(url)

        # Extract file structure
        print("  - Extracting file structure...")
        tree_url = url.rstrip('/') + '/tree/main'
        analysis["sections"]["structure"] = await self.extract_file_structure(tree_url)

        # Extract dependencies
        print("  - Extracting dependencies...")
        analysis["sections"]["dependencies"] = await self.extract_dependencies(url)

        # Extract contributors
        print("  - Extracting contributors...")
        analysis["sections"]["contributors"] = await self.extract_contributors(url)

        return analysis

    def generate_report(self, analysis: Dict[str, Any], format: str = "markdown") -> str:
        """Generate analysis report."""
        repo = analysis["repository"]
        meta = analysis["sections"].get("metadata", {})
        readme = analysis["sections"].get("readme", {})
        structure = analysis["sections"].get("structure", {})
        deps = analysis["sections"].get("dependencies", {})
        contributors = analysis["sections"].get("contributors", {})

        if format == "markdown":
            report = f"""# GitHub Repository Analysis

## {meta.get('full_name', repo['url'])}

{meta.get('description', '*No description provided*')}

### Quick Stats

| Metric | Value |
|--------|-------|
| Stars | {meta.get('social_stats', {}).get('stars', 'N/A')} |
| Forks | {meta.get('social_stats', {}).get('forks', 'N/A')} |
| Watchers | {meta.get('social_stats', {}).get('watchers', 'N/A')} |
| Open Issues | {meta.get('metadata', {}).get('open_issues', 'N/A')} |
| Language | {meta.get('metadata', {}).get('language', 'N/A')} |
| License | {meta.get('metadata', {}).get('license', 'N/A')} |

### Topics

{', '.join(meta.get('topics', [])) or '*No topics*'}

### Links

- [Repository]({repo['url']})
- [Contributors]({repo['url']}/graphs/contributors)
- [Issues]({repo['url']}/issues)

---
"""
            if readme.get("readme_found"):
                report += f"""## README

{readme.get('content', '')}

---
"""

            report += """## File Structure

"""
            for item in structure.get("files", [])[:20]:
                report += f"- 📄 {item['name']}\n"
            for item in structure.get("directories", [])[:10]:
                report += f"- 📁 {item['name']}/\n"

            report += f"""

---
## Dependencies

"""
            for file, info in deps.get("dependencies", {}).items():
                if info.get("found"):
                    report += f"### {file}\n\n```\n{info.get('content', '')[:500]}\n```\n\n"

            report += f"""---
## Contributors ({contributors.get('count', 0)})

"""
            for c in contributors.get("contributors", [])[:10]:
                report += f"- [{c.get('username', 'unknown')}]({c.get('profile_url', '')}))\n"

            report += f"""

---
*Generated on {analysis['analyzed_at']}*
"""

            return report

        elif format == "json":
            return json.dumps(analysis, indent=2)

        return str(analysis)

    def save_report(
        self, analysis: Dict[str, Any], formats: List[str] = None
    ) -> Dict[str, str]:
        """Save analysis report to files."""
        if formats is None:
            formats = ["md", "json"]

        repo = analysis["repository"]
        filename = f"{repo['owner']}_{repo['repo']}"
        output_files = {}

        for fmt in formats:
            filepath = self.output_dir / f"{filename}.{fmt}"
            content = self.generate_report(analysis, format=fmt)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            output_files[fmt] = str(filepath)

        return output_files


async def batch_analyze(urls: List[str], output_dir: str, include_code: bool):
    """Analyze multiple repositories."""
    analyzer = GitHubRepoAnalyzer(output_dir)
    results = []

    for url in urls:
        url = url.strip()
        if not url:
            continue

        print(f"\n{'='*50}")
        analysis = await analyzer.analyze_repo(url, include_code)
        results.append(analysis)

        # Save individual report
        analyzer.save_report(analysis)

        await asyncio.sleep(2)  # Rate limiting

    # Save combined report
    combined_file = Path(output_dir) / "combined_analysis.json"
    with open(combined_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*50}")
    print(f"Batch complete. Results saved to: {output_dir}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Analyze GitHub repositories")
    parser.add_argument("url", nargs="?", help="GitHub repository URL")
    parser.add_argument(
        "--output", "-o", default="./github_analysis", help="Output directory"
    )
    parser.add_argument(
        "--batch", "-b", help="File containing repository URLs"
    )
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown",
        help="Output format"
    )
    parser.add_argument(
        "--analyze-code", action="store_true", help="Include code analysis"
    )

    args = parser.parse_args()

    if not any([args.url, args.batch]):
        parser.print_help()
        print("\nExamples:")
        print("  python github-repo-analysis.py https://github.com/owner/repo")
        print("  python github-repo-analysis.py owner/repo --output ./analysis")
        print("  python github-repo-analysis.py --batch repos.txt --analyze-code")
        sys.exit(1)

    analyzer = GitHubRepoAnalyzer(args.output)

    if args.batch:
        with open(args.batch) as f:
            urls = f.readlines()
        results = asyncio.run(batch_analyze(urls, args.output, args.analyze_code))
    elif args.url:
        analysis = asyncio.run(analyzer.analyze_repo(args.url, args.analyze_code))
        output_files = analyzer.save_report(analysis, [args.format])
        print(f"Report saved: {list(output_files.values())}")


if __name__ == "__main__":
    asyncio.run(main())
