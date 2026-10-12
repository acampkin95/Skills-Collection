#!/usr/bin/env python3
"""
Frontend Quality Checker - Automated frontend quality checks.

Usage:
    python3 quality-checker.py full <project-path>
    python3 quality-checker.py lint <project-path>
    python3 quality-checker.py types <project-path>
    python3 quality-checker.py accessibility <project-path>
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class QualityIssue:
    file: str
    line: int
    column: int
    severity: str
    message: str
    tool: str

class FrontendQualityChecker:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.issues: List[QualityIssue] = []

    def check_package_json(self):
        """Check package.json for quality tools."""
        pkg_file = self.project_path / "package.json"
        if not pkg_file.exists():
            return

        with open(pkg_file) as f:
            pkg = json.load(f)

        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

        # Check for linting tools
        has_eslint = "eslint" in deps
        has_biome = "@biomejs/biome" in deps
        has_prettier = "prettier" in deps

        if not has_eslint and not has_biome:
            self.issues.append(QualityIssue(
                file="package.json",
                line=0,
                column=0,
                severity="medium",
                message="No linter configured (ESLint or Biome recommended)",
                tool="setup"
            ))

        if not has_prettier:
            self.issues.append(QualityIssue(
                file="package.json",
                line=0,
                column=0,
                severity="low",
                message="No code formatter configured (Prettier recommended)",
                tool="setup"
            ))

    def run_biome(self):
        """Run Biome linter."""
        biome_bin = self.project_path / "node_modules" / ".bin" / "biome"
        if not biome_bin.exists():
            # Try global
            biome_bin = Path("/opt/homebrew/bin/biome")  # macOS

        if not biome_bin.exists():
            self.issues.append(QualityIssue(
                file="",
                line=0,
                column=0,
                severity="info",
                message="Biome not installed - install with: npm install @biomejs/biome",
                tool="biome"
            ))
            return

        cmd = [str(biome_bin), "lint", "--json", str(self.project_path / "src")]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            try:
                issues = json.loads(result.stdout)
                for issue in issues:
                    self.issues.append(QualityIssue(
                        file=issue.get("file", ""),
                        line=issue.get("line", 0),
                        column=issue.get("column", 0),
                        severity=issue.get("severity", "error"),
                        message=issue.get("message", ""),
                        tool="biome"
                    ))
            except json.JSONDecodeError:
                pass

    def run_eslint(self):
        """Run ESLint."""
        eslint_bin = self.project_path / "node_modules" / ".bin" / "eslint"
        if not eslint_bin.exists():
            return

        cmd = [str(eslint_bin), "--format", "json", "src"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            try:
                reports = json.loads(result.stdout)
                for report in reports:
                    for file in report.get("files", []):
                        for message in file.get("messages", []):
                            self.issues.append(QualityIssue(
                                file=file.get("filePath", "").replace(str(self.project_path) + "/", ""),
                                line=message.get("line", 0),
                                column=message.get("column", 0),
                                severity=message.get("severity", "error"),
                                message=message.get("message", ""),
                                tool="eslint"
                            ))
            except json.JSONDecodeError:
                pass

    def check_tsconfig(self):
        """Check TypeScript configuration."""
        tsconfig_file = self.project_path / "tsconfig.json"
        if not tsconfig_file.exists():
            self.issues.append(QualityIssue(
                file="tsconfig.json",
                line=0,
                column=0,
                severity="critical",
                message="tsconfig.json not found",
                tool="typescript"
            ))
            return

        with open(tsconfig_file) as f:
            tsconfig = json.load(f)

        compiler_options = tsconfig.get("compilerOptions", {})

        # Check strict mode
        if not compiler_options.get("strict", False):
            self.issues.append(QualityIssue(
                file="tsconfig.json",
                line=0,
                column=0,
                severity="high",
                message="strict mode not enabled in tsconfig.json",
                tool="typescript"
            ))

        # Check noUncheckedIndexedAccess
        if not compiler_options.get("noUncheckedIndexedAccess", False):
            self.issues.append(QualityIssue(
                file="tsconfig.json",
                line=0,
                column=0,
                severity="medium",
                message="noUncheckedIndexedAccess not enabled",
                tool="typescript"
            ))

    def check_accessibility(self):
        """Check for accessibility issues."""
        # Check for alt text on images
        for img_file in self.project_path.rglob("*.tsx"):
            with open(img_file) as f:
                content = f.read()

            # Find img tags without alt
            import re
            img_tags = re.findall(r'<img[^>]*>', content)
            for tag in img_tags:
                if 'alt=' not in tag:
                    self.issues.append(QualityIssue(
                        file=str(img_file).replace(str(self.project_path) + "/", ""),
                        line=content[:content.find(tag)].count('\n') + 1,
                        column=0,
                        severity="medium",
                        message="<img> tag without alt attribute",
                        tool="a11y"
                    ))

        # Check for button elements
        for btn_file in self.project_path.rglob("*.tsx"):
            with open(btn_file) as f:
                content = f.read()

            # Check for buttons with empty content
            empty_buttons = re.findall(r'<button[^>]*>\s*</button>', content)
            if empty_buttons:
                self.issues.append(QualityIssue(
                    file=str(btn_file).replace(str(self.project_path) + "/", ""),
                    line=content.count('\n'),
                    column=0,
                    severity="medium",
                    message="Empty button element - add text or aria-label",
                    tool="a11y"
                ))

    def check_imports(self):
        """Check for common import issues."""
        for ts_file in self.project_path.rglob("*.tsx"):
            with open(ts_file) as f:
                content = f.read()

            # Check for relative imports with too many levels
            deep_imports = re.findall(r'from\s+["\']\.{2}[./]{4,}', content)
            if deep_imports:
                self.issues.append(QualityIssue(
                    file=str(ts_file).replace(str(self.project_path) + "/", ""),
                    line=content.count('\n'),
                    column=0,
                    severity="low",
                    message="Deep relative imports - consider using alias",
                    tool="imports"
                ))

    def run_full_check(self):
        """Run all quality checks."""
        print(f"Running quality checks: {self.project_path}")
        print("=" * 60)

        self.check_package_json()
        self.check_tsconfig()
        self.run_biome()
        self.check_accessibility()
        self.check_imports()

        self.print_report()

    def print_report(self):
        """Print quality report."""
        print()
        print("=" * 60)
        print("QUALITY REPORT")
        print("=" * 60)

        # Group by severity
        by_severity = {"critical": [], "high": [], "medium": [], "low": [], "info": []}

        for issue in self.issues:
            if issue.severity in by_severity:
                by_severity[issue.severity].append(issue)

        # Print by severity
        for severity in ["critical", "high", "medium", "low", "info"]:
            issues = by_severity[severity]
            if issues:
                print(f"\n{severity.upper()} ({len(issues)}):")
                for issue in issues[:10]:  # Limit output
                    loc = f"{issue.file}:{issue.line}" if issue.line else issue.file
                    print(f"  [{issue.tool}] {loc}")
                    print(f"    {issue.message}")
                if len(issues) > 10:
                    print(f"  ... and {len(issues) - 10} more")

        print()
        print("Summary:")
        print(f"  Total issues: {len(self.issues)}")
        print(f"  Critical: {len(by_severity['critical'])}")
        print(f"  High: {len(by_severity['high'])}")

        if by_severity['critical'] or by_severity['high']:
            print("\nAction required before deployment!")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    project_path = sys.argv[2] if len(sys.argv) > 2 else "."

    checker = FrontendQualityChecker(project_path)

    if command == "full":
        checker.run_full_check()
    elif command == "lint":
        checker.run_biome()
        for issue in checker.issues:
            print(f"[{issue.severity}] {issue.file}:{issue.line} - {issue.message}")
    elif command == "types":
        checker.check_tsconfig()
    elif command == "accessibility":
        checker.check_accessibility()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
