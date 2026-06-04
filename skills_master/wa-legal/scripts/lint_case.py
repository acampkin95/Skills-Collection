#!/usr/bin/env python3
"""
lint_case.py — Audit an SRL case folder for compliance issues.

Usage:
    python3 lint_case.py <case_root> [--json] [--fix]

Checks: missing directories, naming issues, immutability violations,
missing indexes, stale dashboard docs, orphaned evidence, YAML integrity.
"""

import csv
import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

AWST = timezone(timedelta(hours=8))

CANONICAL_TOP_DIRS = [
    "01_Dashboard",
    "02_Evidence",
    "03_Communications",
    "04_Court_Documents",
    "05_Research_Strategy",
    "90_Archive",
    "99_AI_Workspace",
]

CANONICAL_SUB_DIRS = {
    "02_Evidence": ["Documents", "Photos_Videos", "Financial", "Witnesses", "Expert_Reports", "Other"],
    "03_Communications": ["Emails", "Letters", "Messages", "Call_Notes"],
    "04_Court_Documents": ["Filed", "Drafts", "Orders_Judgments"],
    "05_Research_Strategy": ["Case_Law", "Legislation", "Notes"],
    "99_AI_Workspace": ["AI_Drafts", "Scratchpad", "Logs"],
}

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}_")
VALID_DATE_PATTERN = re.compile(r"^(\d{4})-(\d{2})-(\d{2})_")
FILED_PATTERN = re.compile(r"_FILED\.\w+$")
DRAFT_PATTERN = re.compile(r"_DRAFT\.\w+$")
AI_INDICATORS = ["AI_", "ai_", "AI-", "ai-", "99_AI_Workspace"]

IGNORE_FILES = {".DS_Store", "Thumbs.db", ".gitkeep", "desktop.ini"}


def check_missing_dirs(root):
    """Check for missing canonical top-level and sub-level directories."""
    missing = []
    for d in CANONICAL_TOP_DIRS:
        if not os.path.isdir(os.path.join(root, d)):
            missing.append(d)

    for parent, subs in CANONICAL_SUB_DIRS.items():
        parent_path = os.path.join(root, parent)
        if not os.path.isdir(parent_path):
            continue
        for sub in subs:
            if not os.path.isdir(os.path.join(parent_path, sub)):
                missing.append(f"{parent}/{sub}")

    return missing


def check_unexpected_dirs(root):
    expected = set(CANONICAL_TOP_DIRS)
    unexpected = []
    for entry in os.listdir(root):
        if os.path.isdir(os.path.join(root, entry)) and entry not in expected:
            if not entry.startswith("."):
                unexpected.append(entry)
    return unexpected


def validate_date_prefix(filename):
    """Check if date prefix is a valid calendar date."""
    match = VALID_DATE_PATTERN.match(filename)
    if not match:
        return False, "No YYYY-MM-DD prefix"
    try:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        datetime(year, month, day)
        return True, None
    except ValueError:
        return False, f"Invalid date: {match.group(1)}-{match.group(2)}-{match.group(3)}"


def check_naming_issues(root):
    issues = []
    court_docs = os.path.join(root, "04_Court_Documents")
    if not os.path.isdir(court_docs):
        return issues

    for dirpath, _, filenames in os.walk(court_docs):
        for fn in filenames:
            if fn.startswith(".") or fn in IGNORE_FILES:
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root)

            # Check date prefix
            if not DATE_PATTERN.match(fn):
                issues.append({
                    "path": rel,
                    "reason": "Filename does not start with YYYY-MM-DD",
                    "suggested": f"{datetime.now(AWST).strftime('%Y-%m-%d')}_{fn}"
                })
            else:
                valid, err = validate_date_prefix(fn)
                if not valid:
                    issues.append({
                        "path": rel,
                        "reason": f"Invalid date prefix: {err}",
                        "suggested": None
                    })

            # Check _FILED files location
            if FILED_PATTERN.search(fn):
                rel_dir = os.path.relpath(dirpath, court_docs)
                if not rel_dir.startswith("Filed"):
                    issues.append({
                        "path": rel,
                        "reason": "_FILED suffix found outside Filed/ directory",
                        "suggested": f"Move to 04_Court_Documents/Filed/{fn}"
                    })

            # Check _DRAFT files location
            if DRAFT_PATTERN.search(fn):
                rel_dir = os.path.relpath(dirpath, court_docs)
                if not rel_dir.startswith("Drafts"):
                    issues.append({
                        "path": rel,
                        "reason": "_DRAFT suffix found outside Drafts/ directory",
                        "suggested": f"Move to 04_Court_Documents/Drafts/{fn}"
                    })

    # Also check evidence naming
    evidence_dir = os.path.join(root, "02_Evidence")
    if os.path.isdir(evidence_dir):
        for dirpath, _, filenames in os.walk(evidence_dir):
            for fn in filenames:
                if fn.startswith(".") or fn in IGNORE_FILES or fn == "Evidence_Index.csv":
                    continue
                if not DATE_PATTERN.match(fn):
                    rel = os.path.relpath(os.path.join(dirpath, fn), root)
                    issues.append({
                        "path": rel,
                        "reason": "Evidence file does not start with YYYY-MM-DD",
                        "suggested": f"{datetime.now(AWST).strftime('%Y-%m-%d')}_{fn}"
                    })

    return issues


def check_immutability_violations(root):
    violations = []
    immutable_dirs = [
        os.path.join(root, "04_Court_Documents", "Filed"),
        os.path.join(root, "04_Court_Documents", "Orders_Judgments"),
    ]

    for idir in immutable_dirs:
        if not os.path.isdir(idir):
            continue
        for fn in os.listdir(idir):
            if fn.startswith(".") or fn in IGNORE_FILES:
                continue
            is_ai = any(ind in fn for ind in AI_INDICATORS)
            if is_ai:
                rel = os.path.relpath(os.path.join(idir, fn), root)
                violations.append({
                    "path": rel,
                    "reason": "AI-generated content in immutable court folder"
                })

    # Also check for AI workspace content leaking into court docs
    court_docs = os.path.join(root, "04_Court_Documents")
    if os.path.isdir(court_docs):
        for dirpath, _, filenames in os.walk(court_docs):
            for fn in filenames:
                if fn.startswith(".") or fn in IGNORE_FILES:
                    continue
                fpath = os.path.join(dirpath, fn)
                # Check file size 0 in Filed/ (possible placeholder)
                if "Filed" in dirpath and os.path.getsize(fpath) == 0:
                    rel = os.path.relpath(fpath, root)
                    violations.append({
                        "path": rel,
                        "reason": "Empty file in Filed/ folder — may be a placeholder, not a filed document"
                    })

    return violations


def check_missing_indexes(root):
    missing = []

    evidence_dir = os.path.join(root, "02_Evidence")
    if os.path.isdir(evidence_dir):
        has_evidence_files = False
        for sub in os.listdir(evidence_dir):
            sub_path = os.path.join(evidence_dir, sub)
            if os.path.isdir(sub_path) and any(
                f for f in os.listdir(sub_path)
                if not f.startswith(".") and f not in IGNORE_FILES
            ):
                has_evidence_files = True
                break

        if has_evidence_files:
            idx_path = os.path.join(evidence_dir, "Evidence_Index.csv")
            if not os.path.exists(idx_path):
                missing.append("02_Evidence/Evidence_Index.csv")

    comms_dir = os.path.join(root, "03_Communications")
    if os.path.isdir(comms_dir):
        has_comms_files = False
        for sub in os.listdir(comms_dir):
            sub_path = os.path.join(comms_dir, sub)
            if os.path.isdir(sub_path) and any(
                f for f in os.listdir(sub_path)
                if not f.startswith(".") and f not in IGNORE_FILES
            ):
                has_comms_files = True
                break

        if has_comms_files:
            idx_path = os.path.join(comms_dir, "Comms_Index.csv")
            if not os.path.exists(idx_path):
                missing.append("03_Communications/Comms_Index.csv")

    return missing


def check_orphaned_evidence(root):
    """Check for evidence files not in Evidence_Index.csv."""
    evidence_dir = os.path.join(root, "02_Evidence")
    idx_path = os.path.join(evidence_dir, "Evidence_Index.csv")
    orphaned = []

    if not os.path.isdir(evidence_dir) or not os.path.exists(idx_path):
        return orphaned

    # Load indexed paths
    indexed_paths = set()
    try:
        with open(idx_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                src = row.get("SourcePath", "").strip()
                if src:
                    indexed_paths.add(src)
    except (csv.Error, KeyError):
        return orphaned  # Can't parse — skip this check

    # Scan evidence subfolders
    for sub in os.listdir(evidence_dir):
        sub_path = os.path.join(evidence_dir, sub)
        if not os.path.isdir(sub_path):
            continue
        for fn in os.listdir(sub_path):
            if fn.startswith(".") or fn in IGNORE_FILES:
                continue
            rel_path = f"{sub}/{fn}"
            if rel_path not in indexed_paths:
                orphaned.append(f"02_Evidence/{rel_path}")

    return orphaned


def check_dashboard(root):
    stale = {}
    dashboard = os.path.join(root, "01_Dashboard")
    required = ["Case_Overview.md", "Timeline_Short.md", "Important_Dates.md"]
    missing = []

    for fname in required:
        fpath = os.path.join(dashboard, fname)
        if not os.path.exists(fpath):
            missing.append(f"01_Dashboard/{fname}")
            continue

        mtime = os.path.getmtime(fpath)
        age_days = (datetime.now().timestamp() - mtime) / 86400
        if age_days > 14:
            stale[fname] = f"Last modified {int(age_days)} days ago"

    return missing, stale


def check_yaml_integrity(root):
    """Check that dashboard markdown files have valid YAML front-matter."""
    issues = []
    dashboard = os.path.join(root, "01_Dashboard")

    for fname in ["Case_Overview.md", "Timeline_Short.md", "Important_Dates.md"]:
        fpath = os.path.join(dashboard, fname)
        if not os.path.exists(fpath):
            continue

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.startswith("---\n"):
                issues.append({
                    "file": f"01_Dashboard/{fname}",
                    "reason": "Missing YAML front-matter (should start with ---)"
                })
                continue

            end_idx = content.find("\n---\n", 4)
            if end_idx == -1:
                issues.append({
                    "file": f"01_Dashboard/{fname}",
                    "reason": "Unclosed YAML front-matter (missing closing ---)"
                })
        except UnicodeDecodeError:
            issues.append({
                "file": f"01_Dashboard/{fname}",
                "reason": "File encoding error — expected UTF-8"
            })

    return issues


def main():
    parser = argparse.ArgumentParser(description="Lint SRL case folder structure")
    parser.add_argument("case_root", help="Path to case root directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    root = args.case_root
    if not os.path.isdir(root):
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    missing_dirs = check_missing_dirs(root)
    unexpected_dirs = check_unexpected_dirs(root)
    naming_issues = check_naming_issues(root)
    immutability_violations = check_immutability_violations(root)
    missing_indexes = check_missing_indexes(root)
    orphaned_evidence = check_orphaned_evidence(root)
    missing_dashboard, stale_dashboard = check_dashboard(root)
    yaml_issues = check_yaml_integrity(root)

    total = (
        len(missing_dirs) + len(naming_issues) +
        len(immutability_violations) + len(missing_indexes) +
        len(missing_dashboard) + len(yaml_issues)
    )

    report = {
        "case_root": root,
        "missing_directories": missing_dirs,
        "unexpected_directories": unexpected_dirs,
        "naming_issues": naming_issues,
        "immutability_violations": immutability_violations,
        "missing_indexes": missing_indexes,
        "orphaned_evidence": orphaned_evidence,
        "missing_dashboard_files": missing_dashboard,
        "stale_dashboard": stale_dashboard,
        "yaml_issues": yaml_issues,
        "total_issues": total,
        "warnings": len(unexpected_dirs) + len(stale_dashboard) + len(orphaned_evidence),
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Case Folder Lint Report: {root}")
        print("=" * 60)

        if missing_dirs:
            print(f"\nMissing directories ({len(missing_dirs)}):")
            for d in missing_dirs:
                print(f"   - {d}")

        if unexpected_dirs:
            print(f"\nUnexpected directories ({len(unexpected_dirs)}):")
            for d in unexpected_dirs:
                print(f"   - {d}")

        if naming_issues:
            print(f"\nNaming issues ({len(naming_issues)}):")
            for issue in naming_issues:
                print(f"   - {issue['path']}")
                print(f"     Reason: {issue['reason']}")
                if issue.get("suggested"):
                    print(f"     Suggested: {issue['suggested']}")

        if immutability_violations:
            print(f"\nImmutability violations ({len(immutability_violations)}):")
            for v in immutability_violations:
                print(f"   - {v['path']}: {v['reason']}")

        if missing_indexes:
            print(f"\nMissing indexes ({len(missing_indexes)}):")
            for idx in missing_indexes:
                print(f"   - {idx}")

        if orphaned_evidence:
            print(f"\nOrphaned evidence (not in index) ({len(orphaned_evidence)}):")
            for o in orphaned_evidence:
                print(f"   - {o}")

        if missing_dashboard:
            print(f"\nMissing dashboard files ({len(missing_dashboard)}):")
            for f in missing_dashboard:
                print(f"   - {f}")

        if stale_dashboard:
            print(f"\nStale dashboard docs:")
            for name, info in stale_dashboard.items():
                print(f"   - {name}: {info}")

        if yaml_issues:
            print(f"\nYAML front-matter issues ({len(yaml_issues)}):")
            for yi in yaml_issues:
                print(f"   - {yi['file']}: {yi['reason']}")

        if total == 0 and not orphaned_evidence:
            print("\nNo issues found — case folder is compliant.")
        else:
            print(f"\nErrors: {total} | Warnings: {report['warnings']}")


if __name__ == "__main__":
    main()
