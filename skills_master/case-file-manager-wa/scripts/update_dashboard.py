#!/usr/bin/env python3
"""
update_dashboard.py — Update dashboard docs (Case_Overview, Timeline, Important_Dates).

Operations:
    status   — Update the last_updated field and optionally the summary/status in Case_Overview.md
    deadline — Add or update a deadline row in Important_Dates.md
    event    — Append a timeline event to Timeline_Short.md
    changelog — Append a changelog entry to Case_Overview.md

Usage:
    python3 update_dashboard.py <case_root> status --summary "Defence filed. Awaiting conciliation date."
    python3 update_dashboard.py <case_root> deadline --name "Service deadline" --date 2025-04-01 --action "Serve on defendant" --status Active
    python3 update_dashboard.py <case_root> event --date 2025-03-15 --description "Defence filed by respondent" --eid E005
    python3 update_dashboard.py <case_root> changelog --entry "Defence received; updated timeline and evidence index"
"""

import argparse
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

AWST = timezone(timedelta(hours=8))
DASHBOARD = "01_Dashboard"


def today_awst():
    return datetime.now(AWST).strftime("%Y-%m-%d")


def read_file(path):
    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def write_file(path, content):
    path.write_text(content, encoding="utf-8")


def update_last_updated(content):
    """Update YAML front-matter last_updated field."""
    return re.sub(
        r'(last_updated:\s*)"[^"]*"',
        f'\\1"{today_awst()}"',
        content
    )


def cmd_status(case_root, args):
    """Update Case_Overview.md summary and last_updated."""
    overview = case_root / DASHBOARD / "Case_Overview.md"
    content = read_file(overview)
    content = update_last_updated(content)

    if args.summary:
        # Replace the summary section content (between ## Summary and next ##)
        pattern = r'(## Summary\n\n).*?(\n\n## )'
        replacement = f'\\1{args.summary}\\2'
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        if new_content != content:
            content = new_content
            print(f"Updated summary in Case_Overview.md")
        else:
            print("Warning: Could not locate ## Summary section to update", file=sys.stderr)

    write_file(overview, content)
    print(f"Updated last_updated to {today_awst()}")


def cmd_deadline(case_root, args):
    """Add or update a deadline in Important_Dates.md."""
    dates_file = case_root / DASHBOARD / "Important_Dates.md"
    content = read_file(dates_file)
    content = update_last_updated(content)

    deadline_row = f"| {args.name} | {args.date} | {args.action} | {args.dl_status} |"

    # Check if deadline already exists (by name)
    existing_pattern = re.compile(
        r'\| ' + re.escape(args.name) + r' \|.*\|.*\|.*\|'
    )
    if existing_pattern.search(content):
        content = existing_pattern.sub(deadline_row, content)
        print(f"Updated existing deadline: {args.name}")
    else:
        # Append after the last row in Deadlines table
        # Find the Deadlines section and append
        deadline_section = re.search(
            r'(## Deadlines\n\n\|[^\n]+\|\n\|[-| ]+\|\n(?:\|[^\n]+\|\n)*)',
            content
        )
        if deadline_section:
            insert_pos = deadline_section.end()
            content = content[:insert_pos] + deadline_row + "\n" + content[insert_pos:]
            print(f"Added deadline: {args.name}")
        else:
            print("Warning: Could not locate ## Deadlines table", file=sys.stderr)

    write_file(dates_file, content)


def cmd_event(case_root, args):
    """Append a timeline event to Timeline_Short.md."""
    timeline = case_root / DASHBOARD / "Timeline_Short.md"
    content = read_file(timeline)
    content = update_last_updated(content)

    year = args.date[:4]
    eid_suffix = f" (EID: {args.eid})" if args.eid else ""
    event_line = f"- {args.date} — {args.description}{eid_suffix}"

    # Find the year section
    year_pattern = re.compile(rf'(## {year}\n\n)((?:- [^\n]+\n)*)')
    match = year_pattern.search(content)

    if match:
        # Insert in chronological order within the year section
        existing_events = match.group(2)
        events = [l for l in existing_events.strip().split("\n") if l.strip()]
        events.append(event_line)
        # Sort by date (first 12 chars: "- YYYY-MM-DD")
        events.sort(key=lambda e: e[:12])
        new_events = "\n".join(events) + "\n\n"
        content = content[:match.start(2)] + new_events + content[match.end(2):]
    else:
        # Add new year section before ## Open Questions
        new_section = f"\n## {year}\n\n{event_line}\n"
        oq_match = re.search(r'\n## Open Questions', content)
        if oq_match:
            content = content[:oq_match.start()] + new_section + content[oq_match.start():]
        else:
            content += new_section + "\n"

    write_file(timeline, content)
    print(f"Added event: {args.date} — {args.description}")


def cmd_changelog(case_root, args):
    """Append a changelog entry to Case_Overview.md."""
    overview = case_root / DASHBOARD / "Case_Overview.md"
    content = read_file(overview)
    content = update_last_updated(content)

    entry = f"- {today_awst()}: {args.entry}"

    # Find ## Changelog section and append after the last entry
    changelog_match = re.search(
        r'(## Changelog\n\n)((?:- [^\n]+\n)*)',
        content
    )
    if changelog_match:
        existing = changelog_match.group(2)
        # Prepend new entry (most recent first)
        new_entries = entry + "\n" + existing
        content = content[:changelog_match.start(2)] + new_entries + content[changelog_match.end(2):]
        print(f"Added changelog entry: {args.entry}")
    else:
        print("Warning: Could not locate ## Changelog section", file=sys.stderr)

    write_file(overview, content)


def main():
    parser = argparse.ArgumentParser(description="Update SRL case dashboard documents")
    parser.add_argument("case_root", help="Path to case root directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    sp_status = subparsers.add_parser("status", help="Update case status/summary")
    sp_status.add_argument("--summary", help="New summary text for Case_Overview.md")

    # deadline
    sp_deadline = subparsers.add_parser("deadline", help="Add/update a deadline")
    sp_deadline.add_argument("--name", required=True, help="Deadline name")
    sp_deadline.add_argument("--date", required=True, help="Deadline date (YYYY-MM-DD)")
    sp_deadline.add_argument("--action", required=True, help="Action required")
    sp_deadline.add_argument("--status", dest="dl_status", default="Pending",
                             help="Deadline status (Pending/Active/Complete)")

    # event
    sp_event = subparsers.add_parser("event", help="Add a timeline event")
    sp_event.add_argument("--date", required=True, help="Event date (YYYY-MM-DD)")
    sp_event.add_argument("--description", required=True, help="Event description")
    sp_event.add_argument("--eid", default="", help="Evidence ID (e.g., E005)")

    # changelog
    sp_changelog = subparsers.add_parser("changelog", help="Add a changelog entry")
    sp_changelog.add_argument("--entry", required=True, help="Changelog entry text")

    args = parser.parse_args()
    case_root = Path(args.case_root)

    if not case_root.is_dir():
        print(f"Error: {case_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    commands = {
        "status": cmd_status,
        "deadline": cmd_deadline,
        "event": cmd_event,
        "changelog": cmd_changelog,
    }
    commands[args.command](case_root, args)


if __name__ == "__main__":
    main()
