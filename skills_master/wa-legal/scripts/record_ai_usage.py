#!/usr/bin/env python3
"""
record_ai_usage.py — Append an AI usage event to the usage log (Markdown + NDJSON).

Usage:
    python3 record_ai_usage.py <case_root> \
        --task "Drafted affidavit outline" \
        --model "Claude Opus 4" \
        --input-files "02_Evidence/Financial/E001_BankStatement.pdf" \
        --output-file "99_AI_Workspace/AI_Drafts/affidavit_outline.md" \
        --confirmed

    python3 record_ai_usage.py <case_root> --task "Research bail conditions" --model "Claude Sonnet 4"
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

MD_LOG = "99_AI_Workspace/Logs/AI_Usage_Log.md"
NDJSON_LOG = "99_AI_Workspace/Logs/AI_Usage_Log.ndjson"

AWST = timezone(timedelta(hours=8))


def ensure_logs_exist(case_root):
    """Create log files if they don't exist."""
    md_path = Path(case_root) / MD_LOG
    ndjson_path = Path(case_root) / NDJSON_LOG

    md_path.parent.mkdir(parents=True, exist_ok=True)

    if not md_path.exists():
        md_path.write_text(
            "# AI Usage Log\n\n"
            "> Every significant AI action is recorded here for transparency and court disclosure.\n\n"
            "---\n\n",
            encoding="utf-8",
        )

    if not ndjson_path.exists():
        ndjson_path.touch()

    return md_path, ndjson_path


def main():
    parser = argparse.ArgumentParser(description="Record AI usage event")
    parser.add_argument("case_root", help="Path to case root directory")
    parser.add_argument("--task", required=True, help="Description of AI task performed")
    parser.add_argument("--model", required=True, help="AI model used (e.g., Claude Opus 4)")
    parser.add_argument("--input-files", default="",
                        help="Comma-separated input file paths (relative to case root)")
    parser.add_argument("--output-file", default="",
                        help="Output file path (relative to case root)")
    parser.add_argument("--confirmed", action="store_true",
                        help="User confirmed/reviewed the output")
    parser.add_argument("--notes", default="", help="Additional notes")
    parser.add_argument("--json", action="store_true", help="Output event as JSON")
    args = parser.parse_args()

    case_root = Path(args.case_root)
    if not case_root.is_dir():
        print(f"Error: {case_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(AWST)
    timestamp = now.strftime("%Y-%m-%d %H:%M AWST")
    date_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

    input_files = [f.strip() for f in args.input_files.split(",") if f.strip()]

    event = {
        "timestamp": date_iso,
        "model": args.model,
        "task": args.task,
        "input_files": input_files,
        "output_file": args.output_file or None,
        "user_confirmed": args.confirmed,
        "notes": args.notes or None,
    }

    md_path, ndjson_path = ensure_logs_exist(case_root)

    # Append to Markdown log
    md_entry = f"### {timestamp}\n\n"
    md_entry += f"- **Model:** {args.model}\n"
    md_entry += f"- **Task:** {args.task}\n"
    if input_files:
        md_entry += f"- **Input:** {', '.join(input_files)}\n"
    if args.output_file:
        md_entry += f"- **Output:** {args.output_file}\n"
    md_entry += f"- **User confirmed:** {'Yes' if args.confirmed else 'No — review pending'}\n"
    if args.notes:
        md_entry += f"- **Notes:** {args.notes}\n"
    md_entry += "\n---\n\n"

    with open(md_path, "a", encoding="utf-8") as f:
        f.write(md_entry)

    # Append to NDJSON log
    with open(ndjson_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    if args.json:
        print(json.dumps(event, indent=2, ensure_ascii=False))
    else:
        print(f"Logged AI usage event: {args.task}")
        print(f"  Model: {args.model}")
        print(f"  Confirmed: {'Yes' if args.confirmed else 'No'}")
        print(f"  Markdown log: {MD_LOG}")
        print(f"  NDJSON log: {NDJSON_LOG}")


if __name__ == "__main__":
    main()
