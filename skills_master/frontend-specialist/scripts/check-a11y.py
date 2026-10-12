#!/usr/bin/env python3
"""
Basic Accessibility Audit Script

Checks for common accessibility issues in React/Vue/Svelte components.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class Issue:
    file: str
    line: int
    rule: str
    message: str
    severity: str  # 'error' | 'warning'


RULES: Dict[str, Dict[str, str]] = {
    'img-alt': {
        'pattern': r'<img[^>]*(?<!alt=)[^>]*>|<img[^>]*alt=""[^>]*>',
        'message': 'Images must have meaningful alt text',
        'severity': 'error',
    },
    'button-type': {
        'pattern': r'<button(?![^>]*type=)[^>]*>',
        'message': 'Buttons should have explicit type attribute',
        'severity': 'warning',
    },
    'anchor-content': {
        'pattern': r'<a[^>]*>\s*</a>',
        'message': 'Links must have content or aria-label',
        'severity': 'error',
    },
    'onclick-div': {
        'pattern': r'<div[^>]*onClick[^>]*>',
        'message': 'Interactive elements should be button/a, not div',
        'severity': 'warning',
    },
    'form-label': {
        'pattern': r'<input[^>]*(?<!id=)[^>]*>',
        'message': 'Form inputs should have associated labels',
        'severity': 'warning',
    },
    'heading-order': {
        'pattern': r'<h[3-6][^>]*>.*?</h[3-6]>(?![\s\S]*<h[12])',
        'message': 'Check heading hierarchy (h1 should come before h2, etc.)',
        'severity': 'warning',
    },
    'autofocus': {
        'pattern': r'autoFocus|autofocus',
        'message': 'autoFocus can be disorienting for screen reader users',
        'severity': 'warning',
    },
    'positive-tabindex': {
        'pattern': r'tabIndex=["\']?[1-9]',
        'message': 'Avoid positive tabIndex values',
        'severity': 'error',
    },
    'role-button-click': {
        'pattern': r'role=["\']button["\'][^>]*(?!onClick)',
        'message': 'Elements with role="button" need onClick handler',
        'severity': 'warning',
    },
    'aria-hidden-focusable': {
        'pattern': r'aria-hidden=["\']true["\'][^>]*(tabIndex|onClick)',
        'message': 'aria-hidden elements should not be focusable',
        'severity': 'error',
    },
}

SKIP_DIRS: set = {'node_modules', '.next', 'dist', 'build', '.git', '.vite'}
FILE_PATTERNS: List[str] = ['**/*.tsx', '**/*.jsx', '**/*.vue', '**/*.svelte']


def should_skip(path: Path) -> bool:
    """Check if a path should be skipped based on directory exclusion list.

    Args:
        path: Path object to check against skip directories.

    Returns:
        True if path contains any skip directory, False otherwise.
    """
    return any(skip in path.parts for skip in SKIP_DIRS)


def check_file(filepath: Path) -> List[Issue]:
    """Check a single file for accessibility issues.

    Scans a file content against accessibility rules to identify WCAG violations
    and common accessibility anti-patterns.

    Args:
        filepath: Path object pointing to the file to check.

    Returns:
        List of Issue objects representing accessibility violations found in the file.
        Returns empty list if file cannot be read.

    Raises:
        No exceptions raised; errors are handled gracefully and return empty list.
    """
    issues: List[Issue] = []

    try:
        content = filepath.read_text()
    except (OSError, IOError, UnicodeDecodeError):
        return []

    for rule_name, rule in RULES.items():
        for match in re.finditer(rule['pattern'], content, re.IGNORECASE | re.MULTILINE):
            # Find line number
            line_num = content[:match.start()].count('\n') + 1

            issues.append(Issue(
                file=str(filepath),
                line=line_num,
                rule=rule_name,
                message=rule['message'],
                severity=rule['severity']
            ))

    return issues


def check_project(project_path: str) -> List[Issue]:
    """Check all files in project for accessibility issues.

    Walks the project directory tree and scans all matching file patterns
    (tsx, jsx, vue, svelte) for accessibility violations, skipping common
    directories like node_modules and build directories.

    Args:
        project_path: Root directory path to check (string or path-like).

    Returns:
        List of all Issue objects found across all scanned files.
        Returns empty list if no issues found.

    Raises:
        OSError: If project directory cannot be accessed.
    """
    root = Path(project_path).resolve()
    all_issues: List[Issue] = []

    for pattern in FILE_PATTERNS:
        for filepath in root.glob(pattern):
            if should_skip(filepath):
                continue
            issues = check_file(filepath)
            all_issues.extend(issues)

    return all_issues


def print_report(issues: List[Issue], project_path: str) -> None:
    """Print formatted accessibility audit report to console.

    Displays a summary of all accessibility issues found, grouped by file,
    with severity indicators and rule information. Provides links to WCAG
    guidelines and accessibility testing tools.

    Args:
        issues: List of Issue objects representing accessibility violations.
        project_path: Root project path for computing relative file paths.

    Returns:
        None.
    """
    print("\n" + "=" * 50)
    print("  ACCESSIBILITY AUDIT")
    print("=" * 50)

    if not issues:
        print("\n✓ No accessibility issues found")
        return

    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']

    print(f"\nFound {len(errors)} errors, {len(warnings)} warnings")

    # Group by file
    by_file: Dict[str, List[Issue]] = {}
    for issue in issues:
        rel_path = str(Path(issue.file).relative_to(project_path))
        if rel_path not in by_file:
            by_file[rel_path] = []
        by_file[rel_path].append(issue)

    for filepath, file_issues in sorted(by_file.items()):
        print(f"\n📄 {filepath}")
        for issue in file_issues:
            icon = "🔴" if issue.severity == 'error' else "🟡"
            print(f"   {icon} Line {issue.line}: {issue.message}")
            print(f"      Rule: {issue.rule}")

    print("\n" + "=" * 50)
    print("\nResources:")
    print("  • WCAG Guidelines: https://www.w3.org/WAI/WCAG21/quickref/")
    print("  • axe DevTools: https://www.deque.com/axe/devtools/")


def main() -> None:
    """CLI entry point for accessibility auditing tool.

    Parses command-line arguments, scans project for accessibility issues,
    and outputs results in human-readable or JSON format. Exits with non-zero
    code if accessibility errors are found.

    Command-line Arguments:
        path: Project directory to audit (default: current directory).
        --json: Output results as JSON instead of formatted report.

    Exit Codes:
        0: Success (no accessibility errors found, warnings may exist).
        1: Error (one or more accessibility errors detected).

    Raises:
        SystemExit: With code 0 or 1 depending on scan results.
    """
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description='Check for common accessibility issues'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project path (default: current directory)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    if not Path(args.path).is_dir():
        print(f"Error: '{args.path}' is not a valid directory")
        sys.exit(1)

    issues = check_project(args.path)

    if args.json:
        print(json.dumps([{
            'file': i.file,
            'line': i.line,
            'rule': i.rule,
            'message': i.message,
            'severity': i.severity
        } for i in issues], indent=2))
    else:
        print_report(issues, args.path)

    # Exit with error code if issues found
    errors = [i for i in issues if i.severity == 'error']
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
