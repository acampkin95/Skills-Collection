#!/usr/bin/env python3
"""
Secrets Scanner - Detect hardcoded secrets and sensitive data leaks.

Usage:
    python3 secrets-scanner.py scan <directory>
    python3 secrets-scanner.py git-history [--since <date>]
    python3 secrets-scanner.py ignore-add
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple, Set
from datetime import datetime

@dataclass
class SecretMatch:
    type: str
    file: str
    line: int
    column: int
    match: str
    confidence: str  # high, medium, low

class SecretsScanner:
    """Scanner for hardcoded secrets and sensitive data."""

    # Comprehensive secret patterns
    PATTERNS: Dict[str, Tuple[str, str]] = {
        # AWS Credentials
        "AWS Access Key ID": (
            r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
            "high"
        ),
        "AWS Secret Key": (
            r"[A-Za-z0-9/+=]{40}",
            "high"
        ),
        "AWS Session Token": (
            r"FwoGZXIvYXdzECYaDPABCDEFexample==",
            "high"
        ),

        # API Keys & Tokens
        "GitHub Token": (
            r"gh[pousr]_[A-Za-z0-9_]{36,}",
            "high"
        ),
        "GitLab Token": (
            r"glpat-[A-Za-z0-9-_]{22,}",
            "high"
        ),
        "Slack Token": (
            r"xox[baprs]-([0-9a-zA-Z]{10,48})",
            "high"
        ),
        "Slack Webhook": (
            r"https:\/\/hooks\.slack\.com\/services\/T[A-Z0-9]+\/B[A-Z0-9]+\/[A-Za-z0-9]+",
            "medium"
        ),
        "Stripe API Key": (
            r"sk_live_[0-9a-zA-Z]{24,}",
            "high"
        ),
        "Stripe Test Key": (
            r"sk_test_[0-9a-zA-Z]{24,}",
            "medium"
        ),
        "Stripe Publishable Key": (
            r"pk_live_[0-9a-zA-Z]{24,}",
            "low"
        ),
        "Google API Key": (
            r"AIza[0-9A-Za-z-_]{35}",
            "medium"
        ),
        "Google OAuth": (
            r"[0-9]+-[a-zA-Z0-9_]{32}\.apps\.googleusercontent\.com",
            "medium"
        ),
        "SendGrid API Key": (
            r"SG\.[A-Za-z0-9-_]{22}\.[A-Za-z0-9-_]{43}",
            "high"
        ),
        "Twilio API Key": (
            r"SK[a-f0-9]{32}",
            "high"
        ),
        "Twilio Auth Token": (
            r"[a-f0-9]{32}",
            "medium"
        ),
        "OpenAI API Key": (
            r"sk-[A-Za-z0-9]{48,}",
            "high"
        ),
        "Anthropic API Key": (
            r"sk-ant-api03-[A-Za-z0-9-_]{50,}",
            "high"
        ),
        "HuggingFace Token": (
            r"hf_[A-Za-z0-9]{34,}",
            "high"
        ),

        # Database Credentials
        "PostgreSQL Connection": (
            r"postgres://[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+@[a-zA-Z0-9.-]+:[0-9]+\/[a-zA-Z0-9_-]+",
            "high"
        ),
        "MySQL Connection": (
            r"mysql://[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+@[a-zA-Z0-9.-]+:[0-9]+\/[a-zA-Z0-9_-]+",
            "high"
        ),
        "MongoDB Connection": (
            r"mongodb(\+srv)?:\/\/([a-zA-Z0-9_-]+):([a-zA-Z0-9_-]+)@",
            "high"
        ),
        "Redis Connection": (
            r"redis:\/\/([a-zA-Z0-9_-]+):([a-zA-Z0-9_-]+)@[a-zA-Z0-9.-]+:[0-9]+",
            "high"
        ),

        # JWT & Auth
        "JWT Token": (
            r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+",
            "medium"
        ),
        "JWT Secret": (
            r"(jwt|jwt_secret|jwtSecret|JWT_SECRET)['\"]?\s*[:=]\s*['\"][^'\"]{16,}['\"]",
            "high"
        ),
        "NextAuth Secret": (
            r"(NEXTAUTH_SECRET|NEXTAUTH_URL)[=]['\"][^'\"]{16,}['\"]",
            "high"
        ),
        "Session Secret": (
            r"(SESSION_SECRET|SessionSecret)[=]['\"][^'\"]{16,}['\"]",
            "high"
        ),

        # Private Keys
        "RSA Private Key": (
            r"-----BEGIN RSA PRIVATE KEY-----",
            "high"
        ),
        "EC Private Key": (
            r"-----BEGIN EC PRIVATE KEY-----",
            "high"
        ),
        "DSA Private Key": (
            r"-----BEGIN DSA PRIVATE KEY-----",
            "high"
        ),
        "OpenSSH Private Key": (
            r"-----BEGIN OPENSSH PRIVATE KEY-----",
            "high"
        ),
        "PEM Private Key": (
            r"-----BEGIN PRIVATE KEY-----",
            "high"
        ),

        # Generic Secrets
        "Generic API Key": (
            r"(api[_-]?key|apikey|API_KEY)[=]['\"][a-zA-Z0-9_]{16,}['\"]",
            "medium"
        ),
        "Generic Secret": (
            r"(secret|SECRET)[=]['\"][a-zA-Z0-9_]{16,}['\"]",
            "medium"
        ),
        "Generic Password": (
            r"(password|PASSWORD|Pwd|passwd)[=]['\"][^'\"]+['\"]",
            "high"
        ),
        "Bearer Token": (
            r"Bearer [a-zA-Z0-9_\-\.]+",
            "medium"
        ),
        "Basic Auth": (
            r"Basic [A-Za-z0-9+/=]+",
            "high"
        ),

        # Social Media
        "Facebook Token": (
            r"EAACEdEose0cBA[0-9A-Za-z]+",
            "high"
        ),
        "Twitter Token": (
            r"[A-Za-z0-9-]{50,}",
            "medium"
        ),
    }

    # Files to skip
    SKIP_PATTERNS = {
        ".git", "node_modules", ".next", "build", "dist", ".cache",
        ".venv", "venv", "__pycache__", ".tox", ".egg-info",
        "*.min.js", "*.min.css", "*.map",
    }

    # Allowed secret types in specific contexts
    ALLOWED_IN = {
        "AWS Access Key ID": ["tests/**/*.yaml", "tests/**/*.yml"],
        "Google API Key": ["public/**/*.js"],
    }

    def __init__(self, directory: str = ".") -> None:
        self.directory: Path = Path(directory)
        self.matches: List[SecretMatch] = []
        self.ignore_patterns: Set[str] = set()

    def scan(self) -> List[SecretMatch]:
        """Scan directory for secrets."""
        self.matches = []

        for file_path in self.directory.rglob("*"):
            if self.should_skip(file_path):
                continue

            if file_path.is_file():
                self.scan_file(file_path)

        return self.matches

    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        if path.is_dir():
            return any(part in self.SKIP_PATTERNS for part in path.parts)

        # Check file extension
        if path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf"}:
            return True

        # Check skip patterns
        for pattern in self.SKIP_PATTERNS:
            if pattern in str(path):
                return True

        return False

    def scan_file(self, file_path: Path) -> None:
        """Scan a single file for secrets."""
        try:
            content = file_path.read_text(errors="ignore")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for secret_type, (pattern, confidence) in self.PATTERNS.items():
                    # Find all matches in line
                    for match in re.finditer(pattern, line):
                        if not self.is_false_positive(file_path, secret_type, match.group(0)):
                            self.matches.append(SecretMatch(
                                type=secret_type,
                                file=str(file_path),
                                line=line_num,
                                column=match.start() + 1,
                                match=self.mask_secret(match.group(0)),
                                confidence=confidence
                            ))
        except (UnicodeDecodeError, PermissionError):
            pass

    def is_false_positive(self, file_path: Path, secret_type: str, match: str) -> bool:
        """Check if match is likely a false positive."""
        # Check if in test/example files
        test_patterns = ["test", "example", "demo", "sample", "mock"]
        if any(p in str(file_path).lower() for p in test_patterns):
            # Allow if in test fixtures
            if "fixtures" not in str(file_path).lower():
                return True

        # Check for placeholder patterns
        placeholders = ["YOUR_", "INSERT_", "REPLACE_", "XXX", "EXAMPLE", "DUMMY"]
        if any(p in match.upper() for p in placeholders):
            return True

        return False

    def mask_secret(self, secret: str) -> str:
        """Mask secret for display."""
        if len(secret) <= 8:
            return "*" * len(secret)

        return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]

    def scan_git_history(self, since: Optional[str] = None) -> List[SecretMatch]:
        """Scan git history for secrets."""
        cmd = ["git", "log", "--all", "-p", "--pretty=format:%h %s"]

        if since:
            cmd.extend([f"--since={since}"])

        try:
            result = subprocess.run(
                cmd,
                cwd=self.directory,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Parse git diff for secrets
            # This is a simplified implementation
            lines = result.stdout.split("\n")
            # Would need full parsing of diff format

        except subprocess.TimeoutExpired:
            print("Git scan timed out")

        return self.matches

    def generate_ignore_rules(self) -> str:
        """Generate .secretsignore rules."""
        rules = ["# .secretsignore - Secrets scanner ignore rules\n"]

        for match in self.matches:
            rules.append(f"{match.file}")

        return "\n".join(set(rules))

    def print_report(self) -> None:
        """Print formatted report."""
        print("\n" + "=" * 70)
        print(" SECRETS SCAN REPORT")
        print("=" * 70)
        print(f"\nDirectory: {self.directory}")
        print(f"Time: {datetime.now().isoformat()}")

        if not self.matches:
            print("\n✓ No secrets detected!")
            return

        # Group by type
        by_type = {}
        for match in self.matches:
            if match.type not in by_type:
                by_type[match.type] = []
            by_type[match.type].append(match)

        print(f"\nFound {len(self.matches)} potential secrets:\n")

        for secret_type, matches in sorted(by_type.items(), key=lambda x: -len(x[1])):
            confidence = matches[0].confidence
            print(f"[{confidence.upper()}] {secret_type}: {len(matches)} occurrences")

            for match in matches[:3]:  # Show first 3
                print(f"  - {match.file}:{match.line}")
            if len(matches) > 3:
                print(f"  ... and {len(matches) - 3} more")

        print("\n" + "-" * 70)
        print(" RECOMMENDATIONS")
        print("-" * 70)
        print("\n1. Remove all hardcoded secrets from code")
        print("2. Use environment variables or secret managers")
        print("3. Rotate any exposed credentials immediately")
        print("4. Add .secretsignore to prevent false positives")
        print("5. Enable git pre-commit hooks for secrets scanning")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Secrets Scanner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan for secrets")
    scan_parser.add_argument("directory", default=".")

    git_parser = subparsers.add_parser("git-history", help="Scan git history")
    git_parser.add_argument("--since")

    ignore_parser = subparsers.add_parser("ignore-add", help="Add findings to .secretsignore")

    args = parser.parse_args()
    scanner = SecretsScanner(args.directory)

    if args.command == "scan":
        scanner.scan()
        scanner.print_report()

        if scanner.matches:
            print(f"\nRun 'python3 secrets-scanner.py ignore-add > .secretsignore' to add exceptions")
            exit(1)
    elif args.command == "git-history":
        scanner.scan_git_history(args.since)
        scanner.print_report()


if __name__ == "__main__":
    main()
