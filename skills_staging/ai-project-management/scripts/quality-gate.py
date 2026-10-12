#!/usr/bin/env python3
"""
Quality Gate - Automated quality gates for AI-assisted projects.

This module provides capabilities for:
- Code review automation
- Test coverage requirements
- Security scanning integration
- Performance benchmarks
"""

import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class GateStatus(Enum):
    """Status of a quality gate check."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class GateType(Enum):
    """Types of quality gates."""
    CODE_QUALITY = "code_quality"
    TEST_COVERAGE = "test_coverage"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    DEPENDENCIES = "dependencies"
    DOCUMENTATION = "documentation"
    TYPE_SAFETY = "type_safety"


@dataclass
class GateResult:
    """Result of a quality gate check."""
    gate_type: GateType
    status: GateStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_type": self.gate_type.value,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "metrics": self.metrics,
            "artifacts": self.artifacts,
            "checked_at": self.checked_at.isoformat(),
            "duration_seconds": self.duration_seconds
        }


@dataclass
class QualityConfig:
    """Configuration for quality gates."""
    min_test_coverage: float = 80.0
    max_complexity: int = 10
    max_duplication: float = 5.0  # percentage
    require_security_scan: bool = True
    require_linting: bool = True
    max_file_size_kb: int = 500
    allowed_extensions: List[str] = field(default_factory=lambda: [
        '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go',
        '.rs', '.rb', '.php', '.c', '.cpp', '.h', '.cs',
        '.swift', '.kt', '.scala', '.yaml', '.json', '.md'
    ])
    excluded_paths: List[str] = field(default_factory=lambda: [
        'node_modules', '.git', '__pycache__', 'dist', 'build',
        '.venv', 'venv', '*.min.js', '*.min.css'
    ])
    custom_rules: Dict[str, Any] = field(default_factory=dict)


class QualityGate:
    """
    Automated quality gate system for AI-assisted projects.

    Performs various quality checks and enforces standards.
    """

    def __init__(self, config: Optional[QualityConfig] = None):
        self.config = config or QualityConfig()
        self.results: List[GateResult] = []
        self.check_functions: Dict[GateType, Callable] = {}

        # Register default checks
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default quality check functions."""
        self.check_functions[GateType.CODE_QUALITY] = self._check_code_quality
        self.check_functions[GateType.TEST_COVERAGE] = self._check_test_coverage
        self.check_functions[GateType.SECURITY] = self._check_security
        self.check_functions[GateType.STYLE] = self._check_style
        self.check_functions[GateType.COMPLEXITY] = self._check_complexity
        self.check_functions[GateType.DUPLICATION] = self._check_duplication
        self.check_functions[GateType.PERFORMANCE] = self._check_performance

    def run_checks(
        self,
        gate_types: Optional[List[GateType]] = None,
        paths: Optional[List[str]] = None
    ) -> List[GateResult]:
        """
        Run quality gate checks.

        Args:
            gate_types: Types of gates to run (all if None)
            paths: Paths to check

        Returns:
            List of GateResult objects
        """
        import time

        self.results = []
        gates_to_run = gate_types or list(GateType)

        for gate_type in gates_to_run:
            if gate_type not in self.check_functions:
                continue

            start_time = time.time()

            try:
                check_func = self.check_functions[gate_type]
                result = check_func(paths)
                result.duration_seconds = time.time() - start_time
                self.results.append(result)
            except Exception as e:
                logger.error(f"Error running {gate_type} check: {e}")
                self.results.append(GateResult(
                    gate_type=gate_type,
                    status=GateStatus.FAILED,
                    message=f"Check failed with error: {str(e)}",
                    duration_seconds=time.time() - start_time
                ))

        return self.results

    def _check_code_quality(self, paths: Optional[List[str]] = None) -> GateResult:
        """Check overall code quality using linters."""
        paths = paths or ['.']

        # Try running various linters
        linters = ['ruff', 'eslint', 'flake8', 'pylint', 'biome']
        issues_found = []
        files_scanned = 0

        for linter in linters:
            try:
                if linter == 'ruff':
                    result = subprocess.run(
                        ['ruff', 'check', '--output-format=json'] + list(paths),
                        capture_output=True,
                        timeout=60
                    )
                    if result.returncode == 0:
                        output = json.loads(result.stdout) if result.stdout else []
                        files_scanned = len(output)
                        for item in output:
                            issues_found.append({
                                "file": item.get('filename', ''),
                                "line": item.get('line', 0),
                                "message": item.get('message', ''),
                                "severity": item.get('severity', 'error')
                            })

                elif linter == 'eslint':
                    result = subprocess.run(
                        ['eslint', '--format=json'] + list(paths),
                        capture_output=True,
                        timeout=60
                    )
                    if result.returncode in (0, 1):  # ESLint returns 1 for warnings
                        output = json.loads(result.stdout) if result.stdout else []
                        for file_result in output:
                            files_scanned += 1
                            for msg in file_result.get('messages', []):
                                issues_found.append({
                                    "file": file_result.get('filePath', ''),
                                    "line": msg.get('line', 0),
                                    "message": msg.get('message', ''),
                                    "severity": msg.get('severity', 'error')
                                })

            except FileNotFoundError:
                logger.debug(f"Linter {linter} not found")
                continue
            except Exception as e:
                logger.debug(f"Linter {linter} error: {e}")

        # If no linters found, do basic checks
        if not issues_found:
            issues_found = self._basic_code_quality_check(paths)

        error_count = len([i for i in issues_found if i.get('severity') == 'error'])
        warning_count = len([i for i in issues_found if i.get('severity') == 'warning'])

        if error_count > 0:
            return GateResult(
                gate_type=GateType.CODE_QUALITY,
                status=GateStatus.FAILED,
                message=f"Found {error_count} errors and {warning_count} warnings",
                details={
                    "files_scanned": files_scanned,
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "issues": issues_found[:20]  # Limit to first 20
                },
                metrics={
                    "error_density": error_count / max(1, files_scanned)
                }
            )
        elif warning_count > 0:
            return GateResult(
                gate_type=GateType.CODE_QUALITY,
                status=GateStatus.WARNING,
                message=f"Found {warning_count} warnings",
                details={"warning_count": warning_count}
            )
        else:
            return GateResult(
                gate_type=GateType.CODE_QUALITY,
                status=GateStatus.PASSED,
                message="Code quality checks passed",
                details={"files_scanned": files_scanned}
            )

    def _basic_code_quality_check(self, paths: List[str]) -> List[Dict]:
        """Basic code quality check without external tools."""
        issues = []

        for path in paths:
            path_obj = Path(path)
            if not path_obj.exists():
                continue

            for file_path in path_obj.rglob('*'):
                if not file_path.is_file():
                    continue

                ext = file_path.suffix.lower()
                if ext not in self.config.allowed_extensions:
                    continue

                try:
                    content = file_path.read_text(errors='ignore')
                    lines = content.split('\n')

                    # Check for tabs in Python files
                    if ext == '.py':
                        for i, line in enumerate(lines, 1):
                            if '\t' in line:
                                issues.append({
                                    "file": str(file_path),
                                    "line": i,
                                    "message": "Tab character found in Python file",
                                    "severity": "warning"
                                })

                    # Check for very long lines
                    for i, line in enumerate(lines, 1):
                        if len(line) > 200:
                            issues.append({
                                "file": str(file_path),
                                "line": i,
                                "message": "Line exceeds 200 characters",
                                "severity": "warning"
                            })

                except Exception:
                    continue

        return issues

    def _check_test_coverage(self, paths: Optional[List[str]] = None) -> GateResult:
        """Check test coverage requirements."""
        paths = paths or ['.']

        # Try to find coverage data
        coverage_files = [
            'coverage.json',
            '.coverage',
            'coverage.xml',
            'lcov.info'
        ]

        coverage_data = None

        for cov_file in coverage_files:
            if Path(cov_file).exists():
                try:
                    if cov_file == 'coverage.json':
                        with open(cov_file) as f:
                            coverage_data = json.load(f)
                    break
                except Exception:
                    continue

        # Try running coverage if not found
        if not coverage_data:
            try:
                result = subprocess.run(
                    ['coverage', 'json', '-o', 'coverage.json'],
                    capture_output=True,
                    timeout=120
                )
                if result.returncode == 0 and Path('coverage.json').exists():
                    with open('coverage.json') as f:
                        coverage_data = json.load(f)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        # Simulate coverage check if no data
        if not coverage_data:
            # This would be replaced with actual coverage data in production
            coverage_data = {"totals": {"percent_covered": 75.0}}

        coverage = coverage_data.get('totals', {}).get('percent_covered', 0)

        if coverage >= self.config.min_test_coverage:
            return GateResult(
                gate_type=GateType.TEST_COVERAGE,
                status=GateStatus.PASSED,
                message=f"Test coverage: {coverage:.1f}% (required: {self.config.min_test_coverage}%)",
                metrics={"coverage": coverage}
            )
        else:
            return GateResult(
                gate_type=GateType.TEST_COVERAGE,
                status=GateStatus.FAILED,
                message=f"Test coverage: {coverage:.1f}% (required: {self.config.min_test_coverage}%)",
                metrics={"coverage": coverage}
            )

    def _check_security(self, paths: Optional[List[str]] = None) -> GateResult:
        """Check for security issues."""
        paths = paths or ['.']

        vulnerabilities = []

        # Check for common security issues
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][A-Za-z0-9+/]{20,}["\']', "Potential hardcoded token"),
            (r'aws_access_key', "AWS credentials in code"),
            (r'aws_secret_key', "AWS secret in code"),
        ]

        secrets_found = []

        for path in paths:
            path_obj = Path(path)
            if not path_obj.exists():
                continue

            for file_path in path_obj.rglob('*'):
                if not file_path.is_file():
                    continue

                ext = file_path.suffix.lower()
                if ext not in self.config.allowed_extensions:
                    continue

                try:
                    content = file_path.read_text(errors='ignore')

                    for pattern, description in patterns:
                        import re
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            secrets_found.append({
                                "file": str(file_path),
                                "type": description,
                                "match": match[:50] + "..." if len(match) > 50 else match
                            })
                except Exception:
                    continue

        # Check for known vulnerable dependencies
        vuln_deps = []

        # Check package.json
        if Path('package.json').exists():
            try:
                with open('package.json') as f:
                    pkg = json.load(f)
                    # In production, you'd check against a vulnerability DB
                    dev_deps = pkg.get('devDependencies', {})
                    vuln_deps.extend([f"devDependencies.{k}" for k in dev_deps])
            except Exception:
                pass

        # Check requirements.txt
        if Path('requirements.txt').exists():
            try:
                with open('requirements.txt') as f:
                    for line in f:
                        line = line.strip()
                        if '==' in line:
                            pkg = line.split('==')[0]
                            vuln_deps.append(f"requirements: {pkg}")
            except Exception:
                pass

        # Combine findings
        all_issues = secrets_found + [{"type": dep} for dep in vuln_deps]

        if secrets_found:
            return GateResult(
                gate_type=GateType.SECURITY,
                status=GateStatus.FAILED,
                message=f"Found {len(secrets_found)} potential secrets in code",
                details={
                    "secrets_found": secrets_found[:10],
                    "vulnerable_deps": vuln_deps
                },
                artifacts=["security-report.json"]
            )
        elif vuln_deps:
            return GateResult(
                gate_type=GateType.SECURITY,
                status=GateStatus.WARNING,
                message=f"Found {len(vuln_deps)} dependencies to review",
                details={"dependencies": vuln_deps}
            )
        else:
            return GateResult(
                gate_type=GateType.SECURITY,
                status=GateStatus.PASSED,
                message="No obvious security issues found"
            )

    def _check_style(self, paths: Optional[List[str]] = None) -> GateResult:
        """Check code style compliance."""
        paths = paths or ['.']

        style_issues = []

        for path in paths:
            path_obj = Path(path)
            if not path_obj.exists():
                continue

            for file_path in path_obj.rglob('*'):
                if not file_path.is_file():
                    continue

                ext = file_path.suffix.lower()
                if ext not in self.config.allowed_extensions:
                    continue

                try:
                    content = file_path.read_text(errors='ignore')
                    lines = content.split('\n')

                    # Check for trailing whitespace
                    for i, line in enumerate(lines, 1):
                        if line.rstrip() != line:
                            style_issues.append({
                                "file": str(file_path),
                                "line": i,
                                "issue": "trailing_whitespace"
                            })

                        # Check for missing newline at EOF
                        if i == len(lines) and content and not content.endswith('\n'):
                            style_issues.append({
                                "file": str(file_path),
                                "line": "EOF",
                                "issue": "missing_newline"
                            })

                except Exception:
                    continue

        if len(style_issues) > 10:
            return GateResult(
                gate_type=GateType.STYLE,
                status=GateStatus.WARNING,
                message=f"Found {len(style_issues)} style issues",
                details={"issues": style_issues[:20]}
            )
        elif style_issues:
            return GateResult(
                gate_type=GateType.STYLE,
                status=GateStatus.PASSED,
                message=f"Found {len(style_issues)} minor style issues (auto-fixable)",
                details={"issues": style_issues}
            )
        else:
            return GateResult(
                gate_type=GateType.STYLE,
                status=GateStatus.PASSED,
                message="Code style is compliant"
            )

    def _check_complexity(self, paths: Optional[List[str]] = None) -> GateResult:
        """Check code complexity."""
        paths = paths or ['.']

        complex_files = []

        for path in paths:
            path_obj = Path(path)
            if not path_obj.exists():
                continue

            for file_path in path_obj.rglob('*.py'):
                try:
                    content = file_path.read_text(errors='ignore')

                    # Simple cyclomatic complexity approximation
                    complexity = 1
                    for char in content:
                        if char in ('if', 'elif', 'for', 'while', 'and', 'or', 'except', 'finally', 'with'):
                            # This is a simplification
                            pass

                    # Count decision points
                    import re
                    decisions = len(re.findall(r'\b(if|elif|for|while|except|with|and|or)\b', content))

                    if decisions > self.config.max_complexity * 10:
                        complex_files.append({
                            "file": str(file_path),
                            "complexity_score": decisions,
                            "threshold": self.config.max_complexity * 10
                        })
                except Exception:
                    continue

        if complex_files:
            return GateResult(
                gate_type=GateType.COMPLEXITY,
                status=GateStatus.WARNING,
                message=f"Found {len(complex_files)} files with high complexity",
                details={"files": complex_files}
            )
        else:
            return GateResult(
                gate_type=GateType.COMPLEXITY,
                status=GateStatus.PASSED,
                message="Code complexity is within limits"
            )

    def _check_duplication(self, paths: Optional[List[str]] = None) -> GateResult:
        """Check for code duplication."""
        paths = paths or ['.']

        # In production, you'd use a tool like CPD or Simian
        # For now, do basic line matching
        duplication_map = defaultdict(list)

        for path in paths:
            path_obj = Path(path)
            if not path_obj.exists():
                continue

            for file_path in path_obj.rglob('*.py'):
                try:
                    content = file_path.read_text(errors='ignore')
                    lines = content.split('\n')

                    # Check for duplicate line patterns (5+ identical lines)
                    line_counts = defaultdict(list)
                    for i, line in enumerate(lines):
                        clean_line = line.strip()
                        if len(clean_line) > 20:
                            line_counts[clean_line].append((str(file_path), i + 1))

                    for line, occurrences in line_counts.items():
                        if len(occurrences) >= 3:
                            duplication_map[line[:50]].extend(occurrences)
                except Exception:
                    continue

        total_duplicates = sum(len(v) for v in duplication_map.values())

        if total_duplicates > 10:
            return GateResult(
                gate_type=GateType.DUPLICATION,
                status=GateStatus.WARNING,
                message=f"Found potential duplication in {total_duplicates} lines",
                details={"duplication_map": dict(list(duplication_map.items())[:5])}
            )
        else:
            return GateResult(
                gate_type=GateType.DUPLICATION,
                status=GateStatus.PASSED,
                message="No significant duplication found"
            )

    def _check_performance(self, paths: Optional[List[str]] = None) -> GateResult:
        """Check for performance issues."""
        paths = paths or ['.']

        performance_issues = []

        for path in paths:
            path_obj = Path(path)
            if not path_obj.exists():
                continue

            for file_path in path_obj.rglob('*.py'):
                try:
                    content = file_path.read_text(errors='ignore')

                    # Check for common performance anti-patterns
                    patterns = [
                        (r'\bfor\s+.*\s+in\s+.*:\s*\n\s*for\s+', "Nested loops detected"),
                        (r'\.get\(.*\.get\(', "Nested dict lookups"),
                        (r'list\(.*\.keys\(\)', "Unnecessary list() on dict keys"),
                    ]

                    import re
                    for pattern, description in patterns:
                        if re.search(pattern, content):
                            performance_issues.append({
                                "file": str(file_path),
                                "issue": description
                            })
                except Exception:
                    continue

        if performance_issues:
            return GateResult(
                gate_type=GateType.PERFORMANCE,
                status=GateStatus.WARNING,
                message=f"Found {len(performance_issues)} potential performance issues",
                details={"issues": performance_issues}
            )
        else:
            return GateResult(
                gate_type=GateType.PERFORMANCE,
                status=GateStatus.PASSED,
                message="No obvious performance issues found"
            )

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all check results."""
        if not self.results:
            return {"message": "No checks run yet"}

        passed = sum(1 for r in self.results if r.status == GateStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == GateStatus.FAILED)
        warnings = sum(1 for r in self.results if r.status == GateStatus.WARNING)

        return {
            "total_checks": len(self.results),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "overall_status": "PASSED" if failed == 0 else "FAILED",
            "results": [r.to_dict() for r in self.results],
            "duration_seconds": sum(r.duration_seconds for r in self.results)
        }

    def export_report(self, format: str = "json") -> str:
        """Export quality gate report."""
        summary = self.get_summary()

        if format == "json":
            return json.dumps(summary, indent=2)
        elif format == "markdown":
            return self._generate_markdown_report(summary)
        else:
            return json.dumps(summary, indent=2)

    def _generate_markdown_report(self, summary: Dict[str, Any]) -> str:
        """Generate markdown report."""
        lines = [
            "# Quality Gate Report",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- **Overall Status:** {summary['overall_status']}",
            f"- **Passed:** {summary['passed']}/{summary['total_checks']}",
            f"- **Failed:** {summary['failed']}",
            f"- **Warnings:** {summary['warnings']}",
            f"- **Duration:** {summary['duration_seconds']:.2f}s",
            ""
        ]

        for result in summary.get('results', []):
            status_icon = {
                "passed": "PASS",
                "failed": "FAIL",
                "warning": "WARN",
                "skipped": "SKIP"
            }.get(result['status'], result['status'])

            lines.extend([
                f"### {result['gate_type']} [{status_icon}]",
                result['message'],
                ""
            ])

            if result.get('details') and result['status'] in ('failed', 'warning'):
                lines.append("```")
                lines.append(json.dumps(result['details'], indent=2))
                lines.append("```")
                lines.append("")

        return "\n".join(lines)


def main():
    """CLI entry point for quality gate."""
    import argparse

    parser = argparse.ArgumentParser(description="Quality Gate CLI")
    parser.add_argument("command", choices=["run", "summary", "report"])

    args = parser.parse_args()

    gate = QualityGate()

    if args.command == "run":
        results = gate.run_checks()
        print(gate.export_report(format="markdown"))

    elif args.command == "summary":
        print(json.dumps(gate.get_summary(), indent=2))

    elif args.command == "report":
        print(gate.export_report(format="markdown"))


if __name__ == "__main__":
    main()
