#!/usr/bin/env python3
"""
cleanup_ai_workspace.py — Analyse 99_AI_Workspace/ for stale/duplicate content.

Two phases:
  1. Analysis (always): report old scratchpads, duplicated drafts, suggested archives
  2. Execution (only with --execute): move to 90_Archive/ per user instruction

Usage:
    python3 cleanup_ai_workspace.py <case_root>              # Analysis only
    python3 cleanup_ai_workspace.py <case_root> --execute     # Move files to archive
    python3 cleanup_ai_workspace.py <case_root> --json        # JSON output
    python3 cleanup_ai_workspace.py <case_root> --days 14     # Custom staleness threshold
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

AI_WORKSPACE = "99_AI_Workspace"
ARCHIVE_DIR = "90_Archive"
DEFAULT_STALE_DAYS = 30

# Subfolders to scan (Logs excluded — those are permanent records)
SCAN_SUBDIRS = ["AI_Drafts", "Scratchpad"]

# Always preserve these files
PRESERVE_FILES = {"README.md"}


def get_file_age_days(filepath):
    """Return age of file in days based on modification time."""
    mtime = os.path.getmtime(filepath)
    age = datetime.now() - datetime.fromtimestamp(mtime)
    return age.days


def find_duplicates(files):
    """Find files with identical sizes (potential duplicates)."""
    size_map = {}
    for f in files:
        try:
            size = f.stat().st_size
            if size > 0:  # Ignore empty files
                size_map.setdefault(size, []).append(f)
        except OSError:
            continue

    return {size: paths for size, paths in size_map.items() if len(paths) > 1}


def analyse(case_root, stale_days):
    """Analyse AI workspace and return findings."""
    ws_path = Path(case_root) / AI_WORKSPACE
    archive_path = Path(case_root) / ARCHIVE_DIR

    findings = {
        "stale_files": [],
        "potential_duplicates": [],
        "suggested_archives": [],
        "total_files": 0,
        "total_size_bytes": 0,
    }

    if not ws_path.is_dir():
        return findings

    all_files = []

    for subdir in SCAN_SUBDIRS:
        sub_path = ws_path / subdir
        if not sub_path.is_dir():
            continue

        for entry in sub_path.rglob("*"):
            if entry.is_file() and entry.name not in PRESERVE_FILES:
                all_files.append(entry)
                findings["total_files"] += 1
                findings["total_size_bytes"] += entry.stat().st_size

                age = get_file_age_days(entry)
                rel_path = str(entry.relative_to(case_root))

                if age > stale_days:
                    findings["stale_files"].append({
                        "path": rel_path,
                        "age_days": age,
                        "size_bytes": entry.stat().st_size,
                    })
                    findings["suggested_archives"].append(rel_path)

    # Check for duplicates
    dupes = find_duplicates(all_files)
    for size, paths in dupes.items():
        findings["potential_duplicates"].append({
            "size_bytes": size,
            "files": [str(p.relative_to(case_root)) for p in paths],
        })

    return findings


def execute_archive(case_root, findings):
    """Move suggested files to 90_Archive/AI_Cleanup_<date>/."""
    if not findings["suggested_archives"]:
        return {"archived": 0, "archive_dir": None}

    date_str = datetime.now().strftime("%Y%m%d")
    archive_subdir = Path(case_root) / ARCHIVE_DIR / f"AI_Cleanup_{date_str}"
    archive_subdir.mkdir(parents=True, exist_ok=True)

    archived = 0
    for rel_path in findings["suggested_archives"]:
        src = Path(case_root) / rel_path
        if src.exists():
            dest = archive_subdir / src.name
            # Avoid overwriting — add suffix if needed
            counter = 1
            while dest.exists():
                stem = src.stem
                dest = archive_subdir / f"{stem}_{counter}{src.suffix}"
                counter += 1
            shutil.move(str(src), str(dest))
            archived += 1

    return {
        "archived": archived,
        "archive_dir": str(archive_subdir.relative_to(case_root)),
    }


def main():
    parser = argparse.ArgumentParser(description="Clean up AI workspace")
    parser.add_argument("case_root", help="Path to case root directory")
    parser.add_argument("--execute", action="store_true",
                        help="Actually move files to archive (requires explicit user confirmation)")
    parser.add_argument("--days", type=int, default=DEFAULT_STALE_DAYS,
                        help=f"Staleness threshold in days (default: {DEFAULT_STALE_DAYS})")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    case_root = Path(args.case_root)
    if not case_root.is_dir():
        print(f"Error: {case_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    findings = analyse(case_root, args.days)

    if args.execute:
        archive_result = execute_archive(case_root, findings)
        findings["archive_result"] = archive_result
    else:
        findings["archive_result"] = None

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        print(f"AI Workspace Analysis ({AI_WORKSPACE})")
        print(f"  Total files: {findings['total_files']}")
        print(f"  Total size: {findings['total_size_bytes']:,} bytes")
        print()

        if findings["stale_files"]:
            print(f"Stale files (>{args.days} days old):")
            for sf in findings["stale_files"]:
                print(f"  {sf['path']} — {sf['age_days']} days old")
        else:
            print("No stale files found.")

        if findings["potential_duplicates"]:
            print(f"\nPotential duplicates (same file size):")
            for d in findings["potential_duplicates"]:
                print(f"  Size {d['size_bytes']:,} bytes:")
                for f in d["files"]:
                    print(f"    {f}")

        if not args.execute and findings["suggested_archives"]:
            print(f"\nSuggested for archive: {len(findings['suggested_archives'])} file(s)")
            print("  Run with --execute to move these to 90_Archive/")

        if args.execute and findings.get("archive_result"):
            ar = findings["archive_result"]
            print(f"\nArchived {ar['archived']} file(s) to {ar['archive_dir']}")


if __name__ == "__main__":
    main()
