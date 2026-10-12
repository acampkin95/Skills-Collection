#!/usr/bin/env python3
"""
Code Audit Automation Script - Automated security and quality scanning.

Usage:
    python3 audit.py full <project-path> [--output <format>]
    python3 audit.py security <project-path>
    python3 audit.py quality <project-path>
    python3 audit.py dependencies <project-path>
    python3 audit.py fix <project-path>
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import re
from typing import List, Dict, Any, Tuple

class CodeAuditor:
    def __init__(self, project_path: str) -> None:
        self.project_path: Path = Path(project_path)
        self.issues: List[Dict[str, Any]] = []
        self.findings: List[Dict[str, Any]] = []

    def run_command(self, cmd: List[str], cwd: Path = None) -> Tuple[bool, str]:
        """Run a command and return (success, output)."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def check_security(self) -> List[Dict[str, Any]]:
        """Run security checks."""
        print("Running security checks...")
        issues: List[Dict[str, Any]] = []

        # Check for secrets in code
        secret_patterns = [
            (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
            (r'ghp_[0-9a-zA-Z]{36}', "GitHub Personal Token"),
            (r'sk_live_[0-9a-zA-Z]{24,}', "Stripe Live Key"),
            (r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*', "JWT Token"),
            (r'password["\s]*[:=]["\s]*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key["\s]*[:=]["\s]*["\'][^"\']+["\']', "Hardcoded API key"),
        ]

        for pattern, description in secret_patterns:
            cmd = ["grep", "-r", "-n", "-E", pattern, str(self.project_path), "--include=*.{js,ts,py,java}"]
            success, output = self.run_command(cmd)
            if success and output.strip():
                for line in output.strip().split("\n"):
                    if ":" in line:
                        parts = line.split(":", 2)
                        issues.append({
                            "type": "secret",
                            "severity": "critical",
                            "file": parts[0],
                            "line": parts[1] if len(parts) > 1 else "N/A",
                            "message": f"Potential {description}"
                        })

        # Check for SQL injection patterns
        sql_patterns = [
            r".*execute\s*\(\s*['\"].*['\"]\s*%\s*.*\)",
            r".*\.query\s*\(\s*f?['\"].*\{.*\}.*['\"]",
        ]

        for pattern in sql_patterns:
            cmd = ["grep", "-r", "-n", "-E", pattern, str(self.project_path), "--include=*.py"]
            success, output = self.run_command(cmd)
            if success and output.strip():
                for line in output.strip().split("\n"):
                    if ":" in line:
                        parts = line.split(":", 2)
                        issues.append({
                            "type": "sql-injection",
                            "severity": "critical",
                            "file": parts[0],
                            "line": parts[1] if len(parts) > 1 else "N/A",
                            "message": "Potential SQL injection vulnerability"
                        })

        # Check for dangerous eval usage
        cmd = ["grep", "-r", "-n", "-E", "\\beval\\s*\\(", str(self.project_path), "--include=*.{js,ts,py}"]
        success, output = self.run_command(cmd)
        if success and output.strip():
            for line in output.strip().split("\n"):
                if ":" in line:
                    parts = line.split(":", 2)
                    issues.append({
                        "type": "dangerous-eval",
                        "severity": "high",
                        "file": parts[0],
                        "line": parts[1] if len(parts) > 1 else "N/A",
                        "message": "Dangerous eval() usage"
                    })

        return issues

    def check_quality(self) -> List[Dict[str, Any]]:
        """Run code quality checks."""
        print("Running quality checks...")
        issues: List[Dict[str, Any]] = []

        # Check for console.log/print statements in production
        patterns = [
            (r"console\.(log|debug|info|warn|error)\s*\(", "console.log", [".test.", ".spec.", "node_modules/"]),
            (r"print\s*\(", "print statement", [".test.", "node_modules/"]),
        ]

        for pattern, description, exclusions in patterns:
            cmd = ["grep", "-r", "-n", "-E", pattern, str(self.project_path), "--include=*.{js,ts,py}"]
            success, output = self.run_command(cmd)
            if success and output.strip():
                for line in output.strip().split("\n"):
                    if ":" in line and not any(excl in line for excl in exclusions):
                        parts = line.split(":", 2)
                        issues.append({
                            "type": "code-quality",
                            "severity": "medium",
                            "file": parts[0],
                            "line": parts[1] if len(parts) > 1 else "N/A",
                            "message": f"Debug {description} in production code"
                        })

        # Check for TODO comments
        cmd = ["grep", "-r", "-n", "-E", "TODO|FIXME|HACK|XXX", str(self.project_path),
               "--include=*.{js,ts,py,java,go,rs}"]
        success, output = self.run_command(cmd)
        if success and output.strip():
            for line in output.strip().split("\n"):
                if ":" in line:
                    parts = line.split(":", 2)
                    issues.append({
                        "type": "technical-debt",
                        "severity": "low",
                        "file": parts[0],
                        "line": parts[1] if len(parts) > 1 else "N/A",
                        "message": "Technical debt marker"
                    })

        # Check for long lines
        cmd = ["grep", "-r", "-n", "-E", "^.{121,}$", str(self.project_path),
               "--include=*.{js,ts,py,md}", "--exclude-dir=node_modules"]
        success, output = self.run_command(cmd)
        if success and output.strip():
            count = len(output.strip().split("\n"))
            issues.append({
                "type": "formatting",
                "severity": "low",
                "file": "Multiple",
                "line": "N/A",
                "message": f"{count} lines exceed 120 characters"
            })

        return issues

    def check_dependencies(self) -> List[Dict[str, Any]]:
        """Check dependencies for vulnerabilities."""
        print("Checking dependencies...")
        issues: List[Dict[str, Any]] = []

        # Check for package.json
        pkg_file = self.project_path / "package.json"
        if pkg_file.exists():
            with open(pkg_file) as f:
                pkg = json.load(f)

            # Check for outdated packages
            cmd = ["npm", "outdated", "--json"]
            success, output = self.run_command(cmd)
            if success and output.strip():
                try:
                    outdated = json.loads(output)
                    for name, info in outdated.items():
                        issues.append({
                            "type": "dependency",
                            "severity": "medium",
                            "file": "package.json",
                            "line": "N/A",
                            "message": f"Package '{name}' is outdated (current: {info.get('current', '?')}, latest: {info.get('latest', '?')})"
                        })
                except json.JSONDecodeError:
                    pass

        # Check for known vulnerabilities
        cmd = ["npm", "audit", "--json"]
        success, output = self.run_command(cmd)
        if success and output.strip():
            try:
                audit = json.loads(output)
                vulnerabilities = audit.get("vulnerabilities", {})
                for name, info in vulnerabilities.items():
                    severity = info.get("severity", "unknown")
                    issues.append({
                        "type": "vulnerability",
                        "severity": severity.upper(),
                        "file": "package.json",
                        "line": "N/A",
                        "message": f"Vulnerability in '{name}': {info.get('via', [{}])[0].get('name', 'unknown')}"
                    })
            except json.JSONDecodeError:
                pass

        return issues

    def check_2026_cves(self) -> List[Dict[str, Any]]:
        """Check for 2026 CVE vulnerabilities."""
        print("Checking for 2026 CVEs...")
        issues: List[Dict[str, Any]] = []

        # Next.js RCE vulnerabilities
        pkg_file = self.project_path / "package.json"
        if pkg_file.exists():
            with open(pkg_file) as f:
                pkg = json.load(f)

            next_version = pkg.get("dependencies", {}).get("next", "")
            if next_version:
                # Parse version and check
                major_version = int(next_version.replace("^", "").replace("~", "").split(".")[0])
                minor_version = int(next_version.replace("^", "").replace("~", "").split(".")[1]) if "." in next_version else 0
                patch_version = int(next_version.replace("^", "").replace("~", "").split(".")[2].split("-")[0]) if len(next_version.replace("^", "").replace("~", "").split(".")) > 2 else 0

                if major_version < 16 or (major_version == 16 and minor_version == 0 and patch_version < 10):
                    issues.append({
                        "type": "cve",
                        "severity": "CRITICAL",
                        "file": "package.json",
                        "line": "N/A",
                        "message": f"Next.js {next_version} is vulnerable to CVE-2025-55182/66478. Upgrade to 16.0.10+"
                    })

        return issues

    def run_full_audit(self, output_format: str = "text") -> Dict[str, Any]:
        """Run complete audit."""
        print(f"Starting full audit: {self.project_path}")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()

        all_issues: List[Dict[str, Any]] = []

        # Run all checks
        all_issues.extend(self.check_2026_cves())
        all_issues.extend(self.check_security())
        all_issues.extend(self.check_quality())
        all_issues.extend(self.check_dependencies())

        # Group by severity
        results = {
            "critical": [i for i in all_issues if i["severity"] == "CRITICAL"],
            "high": [i for i in all_issues if i["severity"] == "high"],
            "medium": [i for i in all_issues if i["severity"] == "medium"],
            "low": [i for i in all_issues if i["severity"] == "low"],
            "total": len(all_issues)
        }

        return results

    def print_results(self, results: Dict[str, Any]) -> None:
        """Print audit results."""
        print()
        print("=" * 60)
        print("AUDIT RESULTS")
        print("=" * 60)

        for severity in ["critical", "high", "medium", "low"]:
            issues = results.get(severity, [])
            if issues:
                print(f"\n{severity.upper()} ({len(issues)} issues):")
                print("-" * 40)
                for issue in issues:
                    print(f"  [{issue['type']}] {issue['file']}:{issue['line']}")
                    print(f"    {issue['message']}")

        print()
        print(f"Total issues: {results['total']}")

        if results['total'] > 0:
            print("\nRecommendations:")
            if results['critical']:
                print("  - IMMEDIATE ACTION: Fix critical issues before deployment")
            if results['high']:
                print("  - Review high issues and fix within 1 week")
            if results['medium']:
                print("  - Address medium issues in next sprint")
            if results['low']:
                print("  - Low issues can be addressed during maintenance")

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    project_path = sys.argv[2] if len(sys.argv) > 2 else "."

    auditor = CodeAuditor(project_path)

    if command == "full":
        output = "text"
        if len(sys.argv) > 3 and sys.argv[3] == "--output":
            output = sys.argv[4] if len(sys.argv) > 4 else "text"
        results = auditor.run_full_audit(output)
        auditor.print_results(results)

    elif command == "security":
        issues = auditor.check_security()
        for issue in issues:
            print(f"[{issue['severity']}] {issue['file']}:{issue['line']} - {issue['message']}")

    elif command == "quality":
        issues = auditor.check_quality()
        for issue in issues:
            print(f"[{issue['severity']}] {issue['file']}:{issue['line']} - {issue['message']}")

    elif command == "dependencies":
        issues = auditor.check_dependencies()
        for issue in issues:
            print(f"[{issue['severity']}] {issue['file']}:{issue['line']} - {issue['message']}")

    elif command == "fix":
        print("Running auto-fix...")
        # Run npm audit fix
        success, _ = auditor.run_command(["npm", "audit", "fix"])
        if success:
            print("Auto-fix completed. Review changes before committing.")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
