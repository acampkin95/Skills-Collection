#!/usr/bin/env python3
"""
Next.js Project Scanner - Automated Next.js project analysis and optimization.

Usage:
    python3 nextjs-scanner.py scan <project-path>
    python3 nextjs-scanner.py config <project-path>
    python3 nextjs-scanner.py perf <project-path>
    python3 nextjs-scanner.py fix <project-path>
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any

class NextJsScanner:
    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path)
        self.issues: List[Tuple[str, str]] = []
        self.recommendations: List[Tuple[str, str]] = []

    def scan_all(self) -> None:
        """Run comprehensive scan."""
        print(f"Scanning Next.js project: {self.project_path}")
        print("=" * 60)

        self.check_version()
        self.check_config_files()
        self.check_app_router()
        self.check_server_components()
        self.check_caching()
        self.check_security()
        self.check_performance()

        self.print_report()

    def check_version(self) -> None:
        """Check Next.js version and warn about CVEs."""
        pkg_file = self.project_path / "package.json"
        if not pkg_file.exists():
            self.issues.append(("critical", "package.json not found"))
            return

        with open(pkg_file) as f:
            pkg = json.load(f)

        next_version = pkg.get("dependencies", {}).get("next", "")
        if not next_version:
            self.issues.append(("critical", "Next.js not in dependencies"))
            return

        # Check version
        version_parts = next_version.replace("^", "").replace("~", "").split(".")
        major = int(version_parts[0]) if len(version_parts) > 0 else 0
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        patch = int(version_parts[2].split("-")[0]) if len(version_parts) > 2 else 0

        if major < 16 or (major == 16 and minor == 0 and patch < 10):
            self.issues.append(("critical", f"Next.js {next_version} - vulnerable to CVE-2025. Upgrade to 16.0.10+"))
        else:
            self.recommendations.append(("info", f"Next.js {next_version} is up to date"))

    def check_config_files(self) -> None:
        """Check configuration files."""
        configs = [
            ("next.config.js", "Next.js configuration"),
            ("next.config.ts", "Next.js configuration (TypeScript)"),
            ("tsconfig.json", "TypeScript configuration"),
            ("postcss.config.mjs", "PostCSS for Tailwind v4"),
        ]

        for config, description in configs:
            config_path = self.project_path / config
            if config_path.exists():
                self.recommendations.append(("pass", f"{description} exists"))
            else:
                self.issues.append(("warning", f"{description} missing"))

    def check_app_router(self) -> None:
        """Check App Router structure."""
        app_dir = self.project_path / "src" / "app"
        if not app_dir.exists():
            app_dir = self.project_path / "app"
        if not app_dir.exists():
            self.issues.append(("warning", "App router directory not found"))
            return

        # Check for layout.tsx
        layout_file = app_dir / "layout.tsx"
        if layout_file.exists():
            with open(layout_file) as f:
                content = f.read()
            if "import './globals.css'" in content or 'import "./globals.css"' in content:
                self.recommendations.append(("pass", "globals.css imported in layout"))
            else:
                self.issues.append(("critical", "globals.css not imported in layout.tsx"))
        else:
            self.issues.append(("warning", "layout.tsx not found"))

        # Check for page.tsx
        page_file = app_dir / "page.tsx"
        if page_file.exists():
            self.recommendations.append(("pass", "page.tsx exists"))
        else:
            self.issues.append(("warning", "page.tsx not found"))

    def check_server_components(self) -> None:
        """Check Server Component patterns."""
        app_dir = self.project_path / "src" / "app"
        if not app_dir.exists():
            app_dir = self.project_path / "app"
        if not app_dir.exists():
            return

        for tsx_file in app_dir.rglob("*.tsx"):
            with open(tsx_file) as f:
                content = f.read()

            # Check for 'use client' misuse
            if content.count("'use client'") > 1:
                self.issues.append(("medium", f"{tsx_file.name}: Multiple 'use client' directives"))

            # Check for async components without proper handling
            if "'use client'" not in content and "export default async function" in content:
                self.issues.append(("critical", f"{tsx_file.name}: Async Server Component with async default export"))

    def check_caching(self) -> None:
        """Check caching configuration."""
        cfg_files = list(self.project_path.glob("next.config.*"))
        if not cfg_files:
            self.issues.append(("warning", "next.config not found"))
            return

        for cfg_file in cfg_files:
            with open(cfg_file) as f:
                content = f.read()

            # Check for image configuration
            if "images:" not in content:
                self.recommendations.append(("info", "Consider adding image optimization config"))

    def check_security(self) -> None:
        """Check security configurations."""
        # Check for hardcoded secrets
        patterns = [
            (r"['\"][A-Za-z0-9-_]{20,}['\"].*api[_-]?key", "API key"),
            (r"['\"][A-Za-z0-9-_]{30,}['\"]", "Potential secret"),
        ]

        for pattern, description in patterns:
            cmd = ["grep", "-r", "-n", "-E", pattern, str(self.project_path),
                   "--include=*.{js,ts}", "--exclude-dir=node_modules"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                self.issues.append(("high", f"Potential {description} in code"))

        # Check middleware.ts for proper auth
        middleware = self.project_path / "middleware.ts"
        if middleware.exists():
            with open(middleware) as f:
                content = f.read()
            if "clerkMiddleware" not in content and "authMiddleware" not in content:
                self.recommendations.append(("info", "Middleware found - verify authentication is configured"))

    def check_performance(self) -> None:
        """Check performance-related configs."""
        # Check for dynamic imports
        app_dir = self.project_path / "src" / "app"
        if not app_dir.exists():
            app_dir = self.project_path / "app"
        if not app_dir.exists():
            return

        lazy_imports = 0
        for tsx_file in app_dir.rglob("*.tsx"):
            with open(tsx_file) as f:
                content = f.read()
            if "next/dynamic" in content or "dynamic(()" in content:
                lazy_imports += 1

        if lazy_imports > 0:
            self.recommendations.append(("pass", f"{lazy_imports} dynamic imports for code splitting"))
        else:
            self.recommendations.append(("info", "Consider using dynamic imports for large components"))

    def print_report(self) -> None:
        """Print scan report."""
        print()
        print("=" * 60)
        print("SCAN RESULTS")
        print("=" * 60)

        # Group by severity
        by_severity = {"critical": [], "high": [], "medium": [], "warning": [], "info": [], "pass": []}

        for severity, message in self.issues:
            if severity in by_severity:
                by_severity[severity].append(message)

        for severity, message in self.recommendations:
            if severity in by_severity:
                by_severity[severity].append(message)

        # Print by severity
        for severity in ["critical", "high", "medium", "warning", "info"]:
            items = by_severity[severity]
            if items:
                print(f"\n{severity.upper()} ({len(items)}):")
                for item in items:
                    print(f"  - {item}")

        print()
        print("Summary:")
        print(f"  Critical: {len(by_severity['critical'])}")
        print(f"  High: {len(by_severity['high'])}")
        print(f"  Medium: {len(by_severity['medium'])}")
        print(f"  Warnings: {len(by_severity['warning'])}")

        if not by_severity['critical'] and not by_severity['high']:
            print("\nNo critical issues found!")
        else:
            print("\nAction required: Fix critical and high issues before deployment")

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    project_path = sys.argv[2] if len(sys.argv) > 2 else "."

    scanner = NextJsScanner(project_path)

    if command == "scan":
        scanner.scan_all()
    elif command == "config":
        scanner.check_config_files()
    elif command == "perf":
        scanner.check_performance()
    elif command == "fix":
        print("Auto-fix not implemented. Please fix issues manually.")
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
