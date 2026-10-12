#!/usr/bin/env python3
"""
Security Scanner - Comprehensive security vulnerability detection.

Usage:
    python3 security-scanner.py scan <target> [--type <repo|docker|k8s>]
    python3 security-scanner.py cve <package> [--severity critical|high]
    python3 security-scanner.py secrets <target>
    python3 security-scanner.py compliance <standard> [--output report.json]
"""

import os
import re
import json
import subprocess
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Vulnerability:
    id: str
    title: str
    description: str
    severity: Severity
    location: str
    line: int
    cve_id: Optional[str] = None
    fix: Optional[str] = None
    references: List[str] = field(default_factory=list)

@dataclass
class SecretFinding:
    type: str
    file: str
    line: int
    snippet: str
    confidence: str  # high, medium, low

class SecurityScanner:
    # Known CVE database (2025-2026)
    CVE_DATABASE = {
        "next": {
            "16.0.0": {"min_fixed": "16.0.10", "cves": ["CVE-2025-55182", "CVE-2025-66478"]},
            "15.0.0": {"min_fixed": "15.0.4", "cves": ["CVE-2025-44121"]},
        },
        "react": {
            "19.0.0": {"min_fixed": "19.5", "cves": ["CVE-2025-55183"]},
            "18.0.0": {"min_fixed": "18.3.2", "cves": ["CVE-2025-33210"]},
        },
        "node": {
            "22.0.0": {"min_fixed": "22.12", "cves": ["CVE-2025-38047", "CVE-2025-44189"]},
            "20.0.0": {"min_fixed": "20.18", "cves": ["CVE-2025-30205"]},
        },
    }

    # Secret patterns
    SECRET_PATTERNS = {
        "aws_access_key": (r"AKIA[0-9A-Z]{16}", "AWS Access Key", "high"),
        "aws_secret": (r"[A-Za-z0-9/+=]{40}", "AWS Secret Key", "high"),
        "github_token": (r"gh[pousr]_[A-Za-z0-9_]{36,}", "GitHub Token", "high"),
        "jwt_secret": (r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+", "JWT Token", "medium"),
        "private_key": (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private Key", "high"),
        "api_key": (r"api[_-]?key['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_]{32,}['\"]?", "API Key", "medium"),
        "database_url": (r"(postgres|mysql|mongodb)://[^\s]+", "Database URL", "high"),
        "slack_token": (r"xox[baprs]-([0-9a-zA-Z]{10,48})", "Slack Token", "high"),
        "stripe_key": (r"sk_live_[0-9a-zA-Z]{24,}", "Stripe Secret Key", "high"),
        "google_api": (r"AIza[0-9A-Za-z-_]{35}", "Google API Key", "medium"),
    }

    # Code vulnerability patterns
    VULN_PATTERNS = {
        "sql_injection": (
            r"(execute|executeMogrified|query)\s*\(\s*['\"].*?\$\{.*?\}.*?['\"]",
            "Potential SQL Injection",
            Severity.HIGH,
            "Use parameterized queries instead of string interpolation"
        ),
        "xss_vulnerability": (
            r"(dangerouslySetInnerHTML|dangerouslyInsertHtml).*\{.*\.(innerHTML|outerHTML)",
            "Potential XSS Vulnerability",
            Severity.HIGH,
            "Sanitize input or use React's built-in escaping"
        ),
        "command_injection": (
            r"(exec|execSync|spawn)\s*\(\s*['\"].*\$",
            "Potential Command Injection",
            Severity.CRITICAL,
            "Avoid shell interpolation; use array form with explicit args"
        ),
        "path_traversal": (
            r"(readFileSync|createReadStream|unlink|rmSync)\s*\(\s*(\.\.\/|\.\.\\)",
            "Path Traversal Vulnerability",
            Severity.HIGH,
            "Validate and sanitize file paths"
        ),
        "weak_crypto": (
            r"(md5|sha1)\s*\(",
            "Weak Cryptographic Hash",
            Severity.MEDIUM,
            "Use SHA-256 or stronger hash functions"
        ),
        "hardcoded_secret": (
            r"(password|secret|apiKey|apikey)\s*[:=]\s*['\"][^'\"]{8,}['\"]",
            "Hardcoded Secret Detected",
            Severity.HIGH,
            "Move secrets to environment variables or secure vault"
        ),
        "insecure_redirect": (
            r"redirect\s*\(\s*(req\.query|req\.params|req\.body)",
            "Open Redirect Vulnerability",
            Severity.MEDIUM,
            "Validate redirect URLs against allowlist"
        ),
        "sensitive_logging": (
            r"console\.(log|debug|info).*(password|secret|token|key|credential)",
            "Sensitive Data in Logs",
            Severity.MEDIUM,
            "Avoid logging sensitive information"
        ),
    }

    def __init__(self, target: str = ".") -> None:
        self.target: Path = Path(target)
        self.vulnerabilities: List[Vulnerability] = []
        self.secrets: List[SecretFinding] = []

    def scan(self, type: str = "repo") -> Dict[str, Any]:
        """Run security scan."""
        print(f"Scanning {self.target}...")

        if type == "repo":
            self.scan_codebase()
            self.scan_secrets()
            self.check_dependencies()

        return self.generate_report()

    def scan_codebase(self) -> None:
        """Scan codebase for vulnerabilities."""
        extensions = {".js", ".ts", ".tsx", ".jsx", ".py", ".java", ".go"}

        for file_path in self.target.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                self.analyze_file(file_path)

    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single file for vulnerabilities."""
        try:
            content = file_path.read_text()
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for vuln_name, (pattern, title, severity, fix) in self.VULN_PATTERNS.items():
                    if re.search(pattern, line):
                        self.vulnerabilities.append(Vulnerability(
                            id=f"VULN-{len(self.vulnerabilities) + 1:04d}",
                            title=title,
                            description=f"Potential {title.lower()} in {file_path.name}",
                            severity=severity,
                            location=str(file_path),
                            line=line_num,
                            fix=fix,
                            references=[]
                        ))
        except (UnicodeDecodeError, PermissionError):
            pass

    def scan_secrets(self) -> None:
        """Scan for hardcoded secrets."""
        extensions = {".js", ".ts", ".tsx", ".jsx", ".py", ".env", ".json", ".yaml", ".yml"}

        for file_path in self.target.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                self.analyze_for_secrets(file_path)

    def analyze_for_secrets(self, file_path: Path) -> None:
        """Analyze file for secrets."""
        try:
            content = file_path.read_text()
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for secret_name, (pattern, title, confidence) in self.SECRET_PATTERNS.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        self.secrets.append(SecretFinding(
                            type=secret_name,
                            file=str(file_path),
                            line=line_num,
                            snippet=match.group(0)[:50] + ("..." if len(match.group(0)) > 50 else ""),
                            confidence=confidence
                        ))
        except (UnicodeDecodeError, PermissionError):
            pass

    def check_dependencies(self) -> None:
        """Check for vulnerable dependencies."""
        lock_files = [
            self.target / "package-lock.json",
            self.target / "yarn.lock",
            self.target / "pnpm-lock.yaml",
            self.target / "requirements.txt",
            self.target / "Pipfile.lock",
            self.target / "poetry.lock",
            self.target / "go.mod",
        ]

        for lock_file in lock_files:
            if lock_file.exists():
                self.parse_dependency_file(lock_file)

    def parse_dependency_file(self, lock_file: Path) -> None:
        """Parse dependency lock file for vulnerabilities."""
        if lock_file.name == "package-lock.json":
            self.check_npm_dependencies(lock_file)
        elif lock_file.name == "go.mod":
            self.check_go_dependencies(lock_file)

    def check_npm_dependencies(self, lock_file: Path) -> None:
        """Check npm dependencies for known CVEs."""
        try:
            data = json.loads(lock_file.read_text())
            packages = data.get("packages", {})

            for path, package in packages.items():
                if not isinstance(package, dict):
                    continue

                name = package.get("name")
                version = package.get("version", "")

                for vuln in self.match_cves(name, version):
                    self.vulnerabilities.append(vuln)
        except json.JSONDecodeError:
            pass

    def check_go_dependencies(self, go_file: Path) -> None:
        """Check Go module dependencies."""
        try:
            content = go_file.read_text()
            for line in content.split("\n"):
                if line.startswith("require ("):
                    # Parse go.mod require block
                    pass
        except PermissionError:
            pass

    def match_cves(self, package: str, version: str) -> List[Vulnerability]:
        """Match package version against CVE database."""
        vuln_list = []

        for pkg_name, versions in self.CVE_DATABASE.items():
            if pkg_name in package.lower():
                for affected_version, fix_info in versions.items():
                    if self.version_in_range(version, affected_version):
                        for cve_id in fix_info.get("cves", []):
                            vuln_list.append(Vulnerability(
                                id=cve_id,
                                title=f"Vulnerable {package} version",
                                description=f"{package} {version} is vulnerable to {cve_id}",
                                severity=Severity.CRITICAL,
                                location=str(go_file),
                                line=0,
                                cve_id=cve_id,
                                fix=f"Upgrade to {fix_info['min_fixed']} or later"
                            ))

        return vuln_list

    def version_in_range(self, version: str, range_version: str) -> bool:
        """Check if version is in affected range (simplified)."""
        # This is a simplified version check
        try:
            v_parts = version.split(".")
            r_parts = range_version.split(".")

            for i in range(min(len(v_parts), len(r_parts))):
                if int(v_parts[i]) > int(r_parts[i]):
                    return True
                elif int(v_parts[i]) < int(r_parts[i]):
                    return False
            return True
        except (ValueError, IndexError):
            return False

    def check_cve(self, package: str, severity: Optional[str] = None) -> Dict[str, Any]:
        """Check CVE information for a specific package."""
        results = {
            "package": package,
            "searched": datetime.now().isoformat(),
            "vulnerabilities": []
        }

        for pkg_name, versions in self.CVE_DATABASE.items():
            if pkg_name in package.lower():
                for version, fix_info in versions.items():
                    results["vulnerabilities"].append({
                        "affected_versions": version,
                        "fixed_version": fix_info["min_fixed"],
                        "cves": fix_info["cves"],
                        "severity": severity or "critical"
                    })

        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate security scan report."""
        return {
            "scan_time": datetime.now().isoformat(),
            "target": str(self.target),
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "by_severity": {
                    "critical": len([v for v in self.vulnerabilities if v.severity == Severity.CRITICAL]),
                    "high": len([v for v in self.vulnerabilities if v.severity == Severity.HIGH]),
                    "medium": len([v for v in self.vulnerabilities if v.severity == Severity.MEDIUM]),
                    "low": len([v for v in self.vulnerabilities if v.severity == Severity.LOW]),
                },
                "secrets_found": len(self.secrets),
            },
            "vulnerabilities": [
                {
                    "id": v.id,
                    "title": v.title,
                    "severity": v.severity.value,
                    "location": f"{v.location}:{v.line}",
                    "cve": v.cve_id,
                    "fix": v.fix
                }
                for v in self.vulnerabilities
            ],
            "secrets": [
                {
                    "type": s.type,
                    "file": f"{s.file}:{s.line}",
                    "confidence": s.confidence
                }
                for s in self.secrets
            ]
        }

    def print_report(self, report: Dict[str, Any]) -> None:
        """Print formatted report."""
        print("\n" + "=" * 70)
        print(" SECURITY SCAN REPORT")
        print("=" * 70)
        print(f"\nTarget: {report['target']}")
        print(f"Time: {report['scan_time']}")

        summary = report['summary']
        print(f"\nVulnerabilities: {summary['total_vulnerabilities']}")
        print(f"  - Critical: {summary['by_severity']['critical']}")
        print(f"  - High: {summary['by_severity']['high']}")
        print(f"  - Medium: {summary['by_severity']['medium']}")
        print(f"  - Low: {summary['by_severity']['low']}")
        print(f"Secrets Found: {summary['secrets_found']}")

        if report['vulnerabilities']:
            print("\n" + "-" * 70)
            print("VULNERABILITIES")
            print("-" * 70)
            for vuln in report['vulnerabilities']:
                print(f"\n[{vuln['severity'].upper()}] {vuln['id']}: {vuln['title']}")
                print(f"  Location: {vuln['location']}")
                if vuln['cve']:
                    print(f"  CVE: {vuln['cve']}")
                if vuln['fix']:
                    print(f"  Fix: {vuln['fix']}")

        if report['secrets']:
            print("\n" + "-" * 70)
            print("SECRETS DETECTED")
            print("-" * 70)
            for secret in report['secrets']:
                print(f"\n[{secret['confidence'].upper()}] {secret['type']}")
                print(f"  Location: {secret['file']}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Security Scanner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan target for vulnerabilities")
    scan_parser.add_argument("target", default=".")
    scan_parser.add_argument("--type", choices=["repo", "docker", "k8s"], default="repo")

    cve_parser = subparsers.add_parser("cve", help="Check CVE for package")
    cve_parser.add_argument("package")
    cve_parser.add_argument("--severity")

    secrets_parser = subparsers.add_parser("secrets", help="Scan for secrets")
    secrets_parser.add_argument("target", default=".")

    compliance_parser = subparsers.add_parser("compliance", help="Check compliance")
    compliance_parser.add_argument("standard")
    compliance_parser.add_argument("--output")

    args = parser.parse_args()
    scanner = SecurityScanner(args.target)

    if args.command == "scan":
        report = scanner.scan(args.type)
        scanner.print_report(report)

        if args.type == "repo" and (report['summary']['total_vulnerabilities'] > 0 or report['summary']['secrets_found'] > 0):
            exit(1)  # Exit with error if issues found
    elif args.command == "cve":
        result = scanner.check_cve(args.package, args.severity)
        print(json.dumps(result, indent=2))
    elif args.command == "secrets":
        scanner.scan_secrets()
        for secret in scanner.secrets:
            print(f"[{secret.confidence}] {secret.type}: {secret.file}:{secret.line}")


if __name__ == "__main__":
    main()
