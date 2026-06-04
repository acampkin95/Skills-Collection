#!/usr/bin/env python3
"""
Tailwind CSS v3 to v4 Migration Script

Automatically renames utility classes that changed between v3 and v4.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Class renames from v3 to v4
RENAMES: Dict[str, str] = {
    # Shadows
    r'\bshadow-sm\b': 'shadow-xs',
    r'\bshadow\b(?!-)': 'shadow-sm',
    
    # Blur
    r'\bblur-sm\b': 'blur-xs',
    r'\bblur\b(?!-)': 'blur-sm',
    
    # Rounded
    r'\brounded-sm\b': 'rounded-xs',
    r'\brounded\b(?!-)': 'rounded-sm',
    
    # Outline
    r'\boutline-none\b': 'outline-hidden',
    
    # Ring (default width changed)
    r'\bring\b(?!-)': 'ring-3',
}

# Files to process
FILE_PATTERNS = ['**/*.tsx', '**/*.jsx', '**/*.html', '**/*.vue', '**/*.svelte']

# Directories to skip
SKIP_DIRS = {'node_modules', '.next', 'dist', 'build', '.git', '.vite'}


def should_skip(path: Path) -> bool:
    """Check if path should be skipped based on directory exclusion list.

    Args:
        path: Path object to check against skip directories.

    Returns:
        True if path contains any skip directory, False otherwise.
    """
    for skip in SKIP_DIRS:
        if skip in path.parts:
            return True
    return False


def migrate_content(content: str, dry_run: bool = False) -> Tuple[str, List[str]]:
    """Migrate Tailwind CSS v3 classes to v4 in content string.

    Applies all regex-based class renames from RENAMES dictionary and tracks
    all replacements made.

    Args:
        content: String content (typically file content) to migrate.
        dry_run: If True, does not modify content (unused, for API consistency).

    Returns:
        Tuple of (migrated_content, list_of_changes). Changes are formatted as
        strings describing old → new replacements.
    """
    changes = []
    new_content = content

    for pattern, replacement in RENAMES.items():
        matches = list(re.finditer(pattern, new_content))
        if matches:
            for match in matches:
                old = match.group(0)
                changes.append(f"  {old} → {replacement}")
            new_content = re.sub(pattern, replacement, new_content)

    return new_content, changes


def migrate_file(filepath: Path, dry_run: bool = False) -> List[str]:
    """Migrate a single file by applying Tailwind class renames.

    Reads the file content, applies all v3→v4 class migrations, and writes
    the updated content back to the file (unless dry_run is True).

    Args:
        filepath: Path object pointing to the file to migrate.
        dry_run: If True, performs analysis without writing changes to disk.

    Returns:
        List of change descriptions (formatted as "old → new" strings).

    Raises:
        OSError: If file cannot be read or written.
    """
    try:
        content = filepath.read_text()
        new_content, changes = migrate_content(content, dry_run)

        if changes and not dry_run:
            filepath.write_text(new_content)

        return changes
    except (OSError, IOError) as e:
        print(f"Error processing {filepath}: {e}")
        return []


def migrate_project(project_path: str, dry_run: bool = False) -> Dict[str, List[str]]:
    """Migrate all matching files in a project directory.

    Walks the project directory tree, applies class migrations to all matching
    file patterns (tsx, jsx, html, vue, svelte), and skips common node modules
    and build directories.

    Args:
        project_path: Root directory path to migrate (string or path-like).
        dry_run: If True, performs analysis without writing changes to disk.

    Returns:
        Dictionary mapping relative file paths to lists of change descriptions.
        Only includes files that had at least one change.

    Raises:
        OSError: If project directory cannot be accessed.
    """
    root = Path(project_path).resolve()
    all_changes: Dict[str, List[str]] = {}

    for pattern in FILE_PATTERNS:
        for filepath in root.glob(pattern):
            if should_skip(filepath):
                continue

            changes = migrate_file(filepath, dry_run)
            if changes:
                rel_path = str(filepath.relative_to(root))
                all_changes[rel_path] = changes

    return all_changes


def print_report(changes: Dict[str, List[str]], dry_run: bool) -> None:
    """Print formatted migration report to console.

    Displays a summary of all changes made (or to be made in dry-run mode),
    including file count, total changes, and a preview of changes per file.

    Args:
        changes: Dictionary mapping relative file paths to lists of change
            descriptions (formatted as "old → new" strings).
        dry_run: If True, indicates this is a dry-run report with no actual changes.

    Returns:
        None.
    """
    print("\n" + "=" * 50)
    print("  TAILWIND v3 → v4 MIGRATION")
    if dry_run:
        print("  (DRY RUN - no files modified)")
    print("=" * 50)

    if not changes:
        print("\nNo changes needed")
        return

    total_changes = sum(len(c) for c in changes.values())
    print(f"\n{len(changes)} files, {total_changes} changes")

    for filepath, file_changes in changes.items():
        print(f"\n{filepath}")
        for change in file_changes[:5]:  # Show first 5
            print(change)
        if len(file_changes) > 5:
            print(f"  ... and {len(file_changes) - 5} more")

    print("\n" + "=" * 50)

    if dry_run:
        print("\nRun without --dry-run to apply changes")


def main() -> None:
    """CLI entry point for Tailwind CSS v3 to v4 migration tool.

    Parses command-line arguments, validates the project path, runs the
    migration on all matching files, and prints a formatted report of changes.

    Command-line Arguments:
        path: Project directory to migrate (default: current directory).
        --dry-run: Preview changes without modifying files (boolean flag).

    Exit Codes:
        0: Success (migration completed or no changes needed).
        1: Error (invalid project path or other runtime error).

    Raises:
        SystemExit: With code 0 or 1 depending on success/failure.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Migrate Tailwind CSS v3 classes to v4'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Project path (default: current directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: '{args.path}' is not a valid directory")
        sys.exit(1)

    changes = migrate_project(args.path, args.dry_run)
    print_report(changes, args.dry_run)


if __name__ == "__main__":
    main()
