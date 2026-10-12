#!/usr/bin/env python3
"""
update_evidence_index.py — Scan 02_Evidence/ and append unlisted files to Evidence_Index.csv.

Usage:
    python3 update_evidence_index.py <case_root> [--dry-run] [--json]
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

INDEX_FILE = "02_Evidence/Evidence_Index.csv"
EVIDENCE_DIR = "02_Evidence"
HEADERS = ["ID", "Date", "Description", "Relevance", "Category", "SourcePath"]

# Map subfolder names to categories
SUBFOLDER_CATEGORY = {
    "Documents": "Documents",
    "Photos_Videos": "Photos/Videos",
    "Financial": "Financial",
    "Witnesses": "Witnesses",
    "Expert_Reports": "Expert Reports",
    "Other": "Other",
}

# Files to ignore (not evidence)
IGNORE_FILES = {"Evidence_Index.csv", ".DS_Store", "Thumbs.db", ".gitkeep"}

DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def load_existing_index(index_path):
    """Load existing CSV entries and return (rows, max_id, indexed_paths)."""
    rows = []
    max_id = 0
    indexed_paths = set()

    if not index_path.exists():
        return rows, max_id, indexed_paths

    with open(index_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            # Extract numeric ID
            id_str = row.get("ID", "")
            match = re.match(r"E(\d+)", id_str)
            if match:
                max_id = max(max_id, int(match.group(1)))
            # Track source paths
            src = row.get("SourcePath", "").strip()
            if src:
                indexed_paths.add(src)

    return rows, max_id, indexed_paths


def scan_evidence_files(case_root):
    """Walk 02_Evidence/ subfolders and return list of (relative_path, subfolder, filename)."""
    evidence_root = Path(case_root) / EVIDENCE_DIR
    found = []

    for subfolder in sorted(SUBFOLDER_CATEGORY.keys()):
        sub_path = evidence_root / subfolder
        if not sub_path.is_dir():
            continue

        for entry in sorted(sub_path.iterdir()):
            if entry.is_file() and entry.name not in IGNORE_FILES:
                rel_path = f"{subfolder}/{entry.name}"
                found.append((rel_path, subfolder, entry.name))

    return found


def infer_date(filename):
    """Try to extract YYYY-MM-DD from filename prefix."""
    match = DATE_PATTERN.match(filename)
    return match.group(1) if match else ""


def build_description(filename):
    """Build a human-readable description from filename."""
    # Strip date prefix if present
    name = DATE_PATTERN.sub("", filename).lstrip("_")
    # Strip extension
    name = os.path.splitext(name)[0]
    # Replace underscores with spaces
    name = name.replace("_", " ").strip()
    return name if name else filename


def main():
    parser = argparse.ArgumentParser(description="Update Evidence_Index.csv")
    parser.add_argument("case_root", help="Path to case root directory")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show proposed changes without writing")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    args = parser.parse_args()

    case_root = Path(args.case_root)
    if not case_root.is_dir():
        print(f"Error: {case_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    index_path = case_root / INDEX_FILE
    existing_rows, max_id, indexed_paths = load_existing_index(index_path)
    evidence_files = scan_evidence_files(case_root)

    # Find unlisted files
    new_entries = []
    next_id = max_id + 1

    for rel_path, subfolder, filename in evidence_files:
        if rel_path not in indexed_paths:
            entry = {
                "ID": f"E{next_id:03d}",
                "Date": infer_date(filename),
                "Description": build_description(filename),
                "Relevance": "",
                "Category": SUBFOLDER_CATEGORY.get(subfolder, "Other"),
                "SourcePath": rel_path,
            }
            new_entries.append(entry)
            next_id += 1

    result = {
        "index_file": str(index_path),
        "existing_entries": len(existing_rows),
        "files_scanned": len(evidence_files),
        "new_entries": len(new_entries),
        "entries": [e for e in new_entries],
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if not new_entries:
            print("Evidence index is up to date — no new files found.")
        else:
            print(f"Found {len(new_entries)} unlisted file(s):")
            for e in new_entries:
                print(f"  {e['ID']}: {e['SourcePath']}")

    if not args.dry_run and new_entries:
        # Sort new entries by date (blanks last)
        new_entries.sort(key=lambda e: e["Date"] if e["Date"] else "9999-99-99")

        # Ensure index file exists with headers
        write_header = not index_path.exists() or index_path.stat().st_size == 0
        if index_path.exists():
            # Check if it only has headers
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content == ",".join(HEADERS):
                    write_header = False  # headers exist but no data

        with open(index_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            if write_header:
                writer.writeheader()
            for entry in new_entries:
                writer.writerow(entry)

        if not args.json:
            print(f"\nAppended {len(new_entries)} entries to {INDEX_FILE}")


if __name__ == "__main__":
    main()
