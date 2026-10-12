#!/usr/bin/env python3
"""
macOS: Spotlight and file search.

Provides Spotlight-based search and file metadata operations.
"""

import subprocess
import os
import re
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum


class SpotlightAttribute(Enum):
    """Spotlight metadata attributes."""
    NAME = 'kMDItemFSName'
    DISPLAY_NAME = 'kMDItemDisplayName'
    KIND = 'kMDItemKind'
    CONTENT_TYPE = 'kMDItemContentType'
    CONTENT_CREATION_DATE = 'kMDItemContentCreationDate'
    CONTENT_MODIFICATION_DATE = 'kMDItemContentModificationDate'
    LAST_USED_DATE = 'kMDItemLastUsedDate'
    CREATION_DATE = 'kMDItemCreationDate'
    SIZE = 'kMDItemFSSize'
    LOGICAL_SIZE = 'kMDItemFSLogicalSize'
    LABEL = 'kMDItemLabel'
    COMMENT = 'kMDItemComment'
    AUTHOR = 'kMDItemAuthor'
    TITLE = 'kMDItemTitle'
    SUBJECT = 'kMDItemSubject'
    KEYWORDS = 'kMDItemKeywords'
    COPYRIGHT = 'kMDItemCopyright'
    APPLICATION = 'kMDItemCreator'
    GENRE = 'kMDItemGenre'


@dataclass
class SpotlightResult:
    """Result from a Spotlight search."""
    path: str
    name: str
    kind: Optional[str] = None
    size: Optional[int] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    content_type: Optional[str] = None
    attributes: Dict[str, Any] = None


class SpotlightError(Exception):
    """Exception raised for Spotlight operations."""
    pass


def _run_mdfind(args: List[str]) -> subprocess.CompletedProcess:
    """
    Run mdfind command.

    Args:
        args: Arguments to pass to mdfind

    Returns:
        CompletedProcess result
    """
    cmd = ['mdfind'] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result
    except subprocess.TimeoutExpired:
        raise SpotlightError("mdfind timed out")


def search(
    query: str,
    scope: Optional[List[str]] = None,
    only_in: Optional[str] = None,
    live: bool = False,
) -> List[str]:
    """
    Search using Spotlight.

    Args:
        query: Search query
        scope: Directories to scope search
        only_in: Limit search to specific directory
        live: Live search (continuous updates)

    Returns:
        List of matching file paths
    """
    args = []

    if scope:
        args.extend(['-scope'] + scope)

    if only_in:
        args.extend(['-onlyin', only_in])

    if live:
        args.append('-live')

    args.append(query)

    result = _run_mdfind(args)

    if result.returncode != 0:
        return []

    files = []
    for line in result.stdout.strip().split('\n'):
        if line:
            files.append(line)

    return files


def search_with_attributes(
    query: str,
    attributes: Optional[List[SpotlightAttribute]] = None,
    scope: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """
    Search and return specified metadata attributes.

    Args:
        query: Search query
        attributes: Attributes to return
        scope: Directories to scope search

    Returns:
        List of dictionaries with attributes
    """
    attrs = attributes or [
        SpotlightAttribute.NAME,
        SpotlightAttribute.KIND,
        SpotlightAttribute.SIZE,
    ]

    attr_args = ['-attr', 'kMDItemPath'] + [a.value for a in attrs]

    if scope:
        attr_args.extend(['-scope'] + scope)

    attr_args.append(query)

    result = _run_mdfind(attr_args)

    results = []
    current_result = {}

    for line in result.stdout.split('\n'):
        line = line.rstrip('\0')

        if not line:
            if current_result:
                results.append(current_result)
                current_result = {}
            continue

        if line.startswith('kMDItemPath'):
            if current_result:
                results.append(current_result)
            path = line.split(' = ', 1)[-1]
            current_result = {'path': path}
        elif ' = ' in line:
            key, value = line.split(' = ', 1)
            current_result[key] = value

    if current_result:
        results.append(current_result)

    return results


def kMDQuery(
    attribute: str,
    value: str,
    comparison: str = '==',
) -> List[str]:
    """
    Create a kMDItem query.

    Args:
        attribute: Spotlight attribute
        value: Value to match
        comparison: Comparison operator (==, !=, <, >, <=, >=)

    Returns:
        List of matching file paths
    """
    query = f'{attribute} {comparison} "{value}"'
    return search(query)


def find_by_kind(kind: str) -> List[str]:
    """
    Find files by kind.

    Args:
        kind: File kind (e.g., "PDF document", "JPEG image")

    Returns:
        List of matching file paths
    """
    return search(f'kMDItemKind == "{kind}"')


def find_by_content_type(content_type: str) -> List[str]:
    """
    Find files by content type.

    Args:
        content_type: Uniform type identifier (e.g., "public.jpeg")

    Returns:
        List of matching file paths
    """
    return search(f'kMDItemContentType == "{content_type}"')


def find_recent(
    file_type: Optional[str] = None,
    limit: int = 50,
    modification: bool = True,
) -> List[str]:
    """
    Find recently modified or used files.

    Args:
        file_type: Limit to specific file type
        limit: Maximum results
        modification: Search by modification date (vs creation)

    Returns:
        List of recent file paths
    """
    date_field = 'kMDItemContentModificationDate' if modification else \
                 'kMDItemLastUsedDate'

    query = f'{date_field} >= $now.new - 86400 * 7'  # Last 7 days

    if file_type:
        query = f'({query}) && kMDItemKind == "{file_type}"'

    results = search(query)
    return results[:limit]


def find_large_files(min_size_mb: float) -> List[str]:
    """
    Find files larger than specified size.

    Args:
        min_size_mb: Minimum size in megabytes

    Returns:
        List of large file paths
    """
    min_bytes = int(min_size_mb * 1024 * 1024)
    return search(f'kMDItemFSSize >= {min_bytes}')


def find_by_date_range(
    start_date: str,
    end_date: str,
    attribute: str = 'kMDItemContentCreationDate',
) -> List[str]:
    """
    Find files within a date range.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        attribute: Date attribute to search

    Returns:
        List of matching file paths
    """
    query = f'{attribute} >= "{start_date}" && {attribute} <= "{end_date}"'
    return search(query)


def import_metadata(plist_path: str) -> bool:
    """
    Import Spotlight metadata from a plist.

    Args:
        plist_path: Path to metadata plist

    Returns:
        True if import succeeded
    """
    try:
        result = subprocess.run(
            ['mdimport', plist_path],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        return False


def reindex_volume(volume: str = '/') -> bool:
    """
    Force reindexing of a volume.

    Args:
        volume: Volume path to reindex

    Returns:
        True if reindexing was initiated
    """
    try:
        result = subprocess.run(
            ['mdutil', '-E', volume],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        return False


def get_index_status(volume: str = '/') -> Dict[str, Any]:
    """
    Get Spotlight index status for a volume.

    Args:
        volume: Volume path

    Returns:
        Dictionary with index status
    """
    try:
        result = subprocess.run(
            ['mdutil', '-s', volume],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            output = result.stdout
            return {
                'indexed': 'Index enabled' in output or \
                          'Indexing and searching enabled' in output,
                'size': None,
                'raw': output.strip(),
            }

    except Exception as e:
        pass

    return {'indexed': False, 'size': None, 'raw': None}


def disable_index(volume: str = '/') -> bool:
    """
    Disable Spotlight indexing for a volume.

    Args:
        volume: Volume path

    Returns:
        True if disabling succeeded
    """
    try:
        result = subprocess.run(
            ['mdutil', '-i', 'off', volume],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        return False


def enable_index(volume: str = '/') -> bool:
    """
    Enable Spotlight indexing for a volume.

    Args:
        volume: Volume path

    Returns:
        True if enabling succeeded
    """
    try:
        result = subprocess.run(
            ['mdutil', '-i', 'on', volume],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        return False


if __name__ != "__main__":
    pass
