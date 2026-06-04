#!/usr/bin/env python3
"""
suggest_filename.py — Generate a compliant SRL case filename.

Usage:
    python3 suggest_filename.py --category court_document --type Affidavit \
        --description "Parenting" --date 2025-03-05 --status DRAFT --ext docx

    python3 suggest_filename.py --category evidence --type Financial \
        --description "BankStatement_Joint" --date 2024-01-15 --ext pdf
"""

import argparse
import json

# Routing: category → base directory
CATEGORY_DIRS = {
    "court_document": {
        "DRAFT": "04_Court_Documents/Drafts",
        "FILED": "04_Court_Documents/Filed",
    },
    "evidence": {
        "Documents": "02_Evidence/Documents",
        "Photos_Videos": "02_Evidence/Photos_Videos",
        "Financial": "02_Evidence/Financial",
        "Witnesses": "02_Evidence/Witnesses",
        "Expert_Reports": "02_Evidence/Expert_Reports",
        "Other": "02_Evidence/Other",
    },
    "communication": {
        "Email": "03_Communications/Emails",
        "Letter": "03_Communications/Letters",
        "Message": "03_Communications/Messages",
        "CallNote": "03_Communications/Call_Notes",
    },
    "note": "05_Research_Strategy/Notes",
    "order": "04_Court_Documents/Orders_Judgments",
}

# Court document types — these route to court_document category automatically
# when no explicit category is given, the caller should set category=court_document
COURT_DOC_TYPES = {
    "Claim", "Defence", "Counterclaim", "Reply", "Affidavit",
    "Application", "Subpoena", "ServiceAffidavit", "BailApp",
}

# Evidence type → subfolder mapping
EVIDENCE_TYPE_MAP = {
    "Photo": "Photos_Videos",
    "Financial": "Financial",
    "CharRef": "Witnesses",
    "Expert": "Expert_Reports",
    "Evidence": "Documents",
}

# Communication type → subfolder mapping
COMM_TYPE_MAP = {
    "Email": "Email",
    "Letter": "Letter",
    "Message": "Message",
    "CallNote": "CallNote",
}

def suggest(category, doc_type, description, date, status, version, ext):
    # Clean description
    desc = description.replace(" ", "_").replace("/", "-")

    # Build filename parts
    parts = [date, doc_type, desc]

    if version and version > 1:
        parts.append(f"v{version}")

    if status and status.upper() in ("DRAFT", "FILED"):
        parts.append(status.upper())

    filename = "_".join(parts) + f".{ext}"

    # Determine directory
    # Orders and Judgments always go to Orders_Judgments (immutable)
    if category == "order" or doc_type in ("Order", "Judgment"):
        rel_dir = CATEGORY_DIRS["order"]
    elif category == "court_document":
        if status and status.upper() == "FILED":
            rel_dir = CATEGORY_DIRS["court_document"]["FILED"]
        else:
            rel_dir = CATEGORY_DIRS["court_document"]["DRAFT"]
    elif category == "evidence":
        subfolder = EVIDENCE_TYPE_MAP.get(doc_type, "Documents")
        rel_dir = CATEGORY_DIRS["evidence"].get(subfolder, "02_Evidence/Other")
    elif category == "communication":
        subfolder = COMM_TYPE_MAP.get(doc_type, "Email")
        rel_dir = CATEGORY_DIRS["communication"].get(subfolder, "03_Communications/Emails")
    elif category == "note":
        rel_dir = CATEGORY_DIRS["note"]
    else:
        rel_dir = "05_Research_Strategy/Notes"

    return {
        "relative_dir": rel_dir,
        "filename": filename,
        "full_path": f"{rel_dir}/{filename}"
    }

def main():
    parser = argparse.ArgumentParser(description="Suggest SRL-compliant filename")
    parser.add_argument("--category", required=True,
                       choices=["court_document", "evidence", "communication", "note", "order"],
                       help="Document category")
    parser.add_argument("--type", required=True, dest="doc_type",
                       help="Document type (Affidavit, Claim, Email, Photo, etc.)")
    parser.add_argument("--description", required=True,
                       help="Short description")
    parser.add_argument("--date", required=True,
                       help="Date (YYYY-MM-DD)")
    parser.add_argument("--status", default="",
                       help="DRAFT or FILED")
    parser.add_argument("--version", type=int, default=1,
                       help="Version number (default: 1)")
    parser.add_argument("--ext", required=True,
                       help="File extension (pdf, docx, etc.)")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON")
    args = parser.parse_args()

    result = suggest(
        args.category, args.doc_type, args.description,
        args.date, args.status, args.version, args.ext
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Directory: {result['relative_dir']}")
        print(f"Filename:  {result['filename']}")
        print(f"Full path: {result['full_path']}")

if __name__ == "__main__":
    main()
