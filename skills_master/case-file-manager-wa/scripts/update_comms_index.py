#!/usr/bin/env python3
"""
update_comms_index.py — Scan 03_Communications/ and append unlisted files to Comms_Index.csv.

Usage:
    python3 update_comms_index.py <case_root> [--dry-run] [--json]
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

INDEX_FILE = "03_Communications/Comms_Index.csv"
COMMS_DIR = "03_Communications"
HEADERS = ["Date", "Type", "From", "To", "ShortDescription", "Important", "SourcePath"]

# Map subfolder names to communication types
SUBFOLDER_TYPE = {
    "Emails": "Email",
    "Letters": "Letter",
    "Messages": "Message",
    "Call_Notes": "CallNote",
}

IGNORE_FILES = {"Comms_Index.csv", ".DS_Store", "Thumbs.db", ".gitkeep"}
DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def load_existing_index(index_path):
    """Load existing CSV entries and return (rows, indexed_paths)."""
    rows = []
    indexed_paths = set()

    if not index_path.exists():
        return rows, indexed_paths

    with open(index_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            src = row.get("SourcePath", "").strip()
            if src:
                indexed_paths.add(src)

    return rows, indexed_paths


def scan_comms_files(case_root):
    """Walk 03_Communications/ subfolders and return list of (relative_path, subfolder, filename)."""
    comms_root = Path(case_root) / COMMS_DIR
    found = []

    for subfolder in sorted(SUBFOLDER_TYPE.keys()):
        sub_path = comms_root / subfolder
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
    name = DATE_PATTERN.sub("", filename).lstrip("_")
    # Remove type prefix if it matches known types
    for t in ["Email", "Letter", "Message", "CallNote"]:
        if name.startswith(t + "_"):
            name = name[len(t) + 1:]
            break
    name = os.path.splitext(name)[0]
    name = name.replace("_", " ").strip()
    return name if name else filename


def main():
    parser = argparse.ArgumentParser(description="Update Comms_Index.csv")
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
    existing_rows, indexed_paths = load_existing_index(index_path)
    comms_files = scan_comms_files(case_root)

    new_entries = []
    for rel_path, subfolder, filename in comms_files:
        if rel_path not in indexed_paths:
            entry = {
                "Date": infer_date(filename),
                "Type": SUBFOLDER_TYPE.get(subfolder, "Email"),
                "From": "",
                "To": "",
                "ShortDescription": build_description(filename),
                "Important": "",
                "SourcePath": rel_path,
            }
            new_entries.append(entry)

    result = {
        "index_file": str(index_path),
        "existing_entries": len(existing_rows),
        "files_scanned": len(comms_files),
        "new_entries": len(new_entries),
        "entries": [e for e in new_entries],
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if not new_entries:
            print("Communications index is up to date — no new files found.")
        else:
            print(f"Found {len(new_entries)} unlisted file(s):")
            for e in new_entries:
                print(f"  [{e['Type']}] {e['SourcePath']}")

    if not args.dry_run and new_entries:
        write_header = not index_path.exists() or index_path.stat().st_size == 0
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content == ",".join(HEADERS):
                    write_header = False

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
