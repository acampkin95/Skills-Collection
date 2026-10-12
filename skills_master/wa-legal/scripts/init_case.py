#!/usr/bin/env python3
"""
init_case.py — Create canonical SRL case folder structure.

Usage:
    python3 init_case.py <case_root> [--court MagCourt_Civil] [--file-no CIV2025_1234] [--parties "Smith v Jones"]

Creates all canonical folders and populates dashboard templates.
Idempotent: skips existing folders/files.
"""

import os
import sys
import argparse
from datetime import datetime, timezone, timedelta

AWST = timezone(timedelta(hours=8))

CANONICAL_DIRS = [
    "01_Dashboard",
    "02_Evidence",
    "02_Evidence/Documents",
    "02_Evidence/Photos_Videos",
    "02_Evidence/Financial",
    "02_Evidence/Witnesses",
    "02_Evidence/Expert_Reports",
    "02_Evidence/Other",
    "03_Communications",
    "03_Communications/Emails",
    "03_Communications/Letters",
    "03_Communications/Messages",
    "03_Communications/Call_Notes",
    "04_Court_Documents",
    "04_Court_Documents/Filed",
    "04_Court_Documents/Drafts",
    "04_Court_Documents/Orders_Judgments",
    "05_Research_Strategy",
    "05_Research_Strategy/Case_Law",
    "05_Research_Strategy/Legislation",
    "05_Research_Strategy/Notes",
    "90_Archive",
    "99_AI_Workspace",
    "99_AI_Workspace/AI_Drafts",
    "99_AI_Workspace/Scratchpad",
    "99_AI_Workspace/Logs",
]

def today():
    return datetime.now(AWST).strftime("%Y-%m-%d")

def create_dirs(root):
    created = []
    for d in CANONICAL_DIRS:
        path = os.path.join(root, d)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            created.append(d)
    return created

def write_if_missing(path, content):
    if os.path.exists(path):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return True

def case_overview(root_name, court, file_no, parties):
    return f"""---
case_root: "{root_name}"
court: "{court}"
file_no: "{file_no}"
parties: "{parties}"
last_updated: "{today()}"
---

# Case Overview

## Summary

[Summarise the case: what the dispute is about, who the parties are, and what stage the case is at.]

## Orders Sought

1. [Order 1]
2. [Order 2]

## Key Evidence (IDs)

- [No evidence indexed yet]

## Agreed and Disputed Issues

| Issue | Your Position | Other Party's Position | Status |
|-------|--------------|----------------------|--------|
| [Issue 1] | [Your view] | [Their view] | Disputed |

## Key Contacts

| Role | Name | Contact |
|------|------|---------|
| Self | [Your name] | [Phone/email] |
| Other party | [Name] | [Phone/email] |
| Court registry | {court} | [Phone] |

## Changelog

- {today()}: Case folder created.
"""

def timeline_short(root_name):
    return f"""---
case_root: "{root_name}"
type: "short_timeline"
last_updated: "{today()}"
---

# Short Timeline of Key Events

## {datetime.now(AWST).year}

- [YYYY-MM-DD] — [Add key events here]

## Open Questions

- [Add questions about unclear events or dates]
"""

def important_dates_civil(root_name):
    return f"""---
case_root: "{root_name}"
type: "important_dates"
last_updated: "{today()}"
---

# Important Dates

## Court Dates

| Date | Event | Location | Notes |
|------|-------|----------|-------|
| [TBD] | [Hearing type] | [Court/room] | [Preparation notes] |

## Deadlines

| Deadline | Date | Action Required | Status |
|----------|------|----------------|--------|
| Defence deadline | [calculate from served form/rules/service facts] | Defendant must lodge defence or notice of intention to defend | Pending |
| Service deadline | [5 clear days before hearing] | All documents must be served | Pending |
| Claim validity | [1 year from lodgement] | Claim expires if not served | Active |
| eCourts registration | [Allow 24 hours] | Register for eLodgment portal | Pending |

## Reminders

- [ ] Register for eCourts Portal (allow 24 hours for approval)
- [ ] Prepare evidence bundle (3 copies: court, opponent, self)
- [ ] Arrange affidavit swearing (JP, Commissioner for Oaths, or lawyer)
- [ ] File Affidavit of Service after serving documents
- [ ] Check current filing fees at magistratescourt.wa.gov.au/F/fees.aspx
"""

def important_dates_criminal(root_name):
    return f"""---
case_root: "{root_name}"
type: "important_dates"
last_updated: "{today()}"
---

# Important Dates

## Court Dates

| Date | Event | Location | Notes |
|------|-------|----------|-------|
| [TBD] | First appearance | [Court] | Plea not required; adjournment available |

## Bail Conditions (if applicable)

| Condition | Detail | Compliance Notes |
|-----------|--------|-----------------|
| [Condition 1] | [Specifics] | [How to comply] |

## Deadlines

| Deadline | Date | Action Required | Status |
|----------|------|----------------|--------|
| Adjournment application | [check current practice direction/registry instruction] | Use current filing channel and deadline | Pending |

## Preparation Checklist

- [ ] Contact duty lawyer (available at most court sittings)
- [ ] Obtain prosecution brief/disclosure
- [ ] Prepare character references (2-3, addressed to "The Presiding Magistrate")
- [ ] Prepare mitigation affidavit (CPR Form 2) if pleading guilty
- [ ] Bring photo ID to court
"""

def important_dates_generic(root_name):
    return f"""---
case_root: "{root_name}"
type: "important_dates"
last_updated: "{today()}"
---

# Important Dates

## Court Dates

| Date | Event | Location | Notes |
|------|-------|----------|-------|
| [TBD] | [Hearing type] | [Court/room] | [Preparation notes] |

## Deadlines

| Deadline | Date | Action Required | Status |
|----------|------|----------------|--------|
| [Deadline 1] | [Date] | [Action] | Pending |

## Reminders

- [ ] [Add preparation reminders]
"""

AI_README = """# AI Workspace — Not Official Court Documents

**WARNING: Nothing in this folder is filed with any court.**

This folder contains AI-generated drafts, summaries, and working notes.
These are tools to help you organise your thoughts — they are not court documents.

## Before Using Any AI-Generated Content

1. **Copy** the draft to `04_Court_Documents/Drafts/`
2. **Edit thoroughly** — rewrite in your own words and verify all facts
3. **Have it reviewed** — by a lawyer, Legal Aid, or community legal centre if possible
4. **Only after personal review** — save a PDF in `04_Court_Documents/Filed/` when you personally file/serve it

## AI Limitations

- AI can help organise, format, and structure documents
- AI **cannot** give legal advice or predict court outcomes
- AI may produce incorrect legal references — always verify
- AI-generated content may not reflect your actual circumstances — always check facts
- Courts may require disclosure of AI assistance — keep the AI Usage Log updated
"""

EVIDENCE_INDEX_HEADER = "ID,Date,Description,Relevance,Category,SourcePath\n"
COMMS_INDEX_HEADER = "Date,Type,From,To,ShortDescription,Important,SourcePath\n"

def main():
    parser = argparse.ArgumentParser(description="Initialise SRL case folder structure")
    parser.add_argument("case_root", help="Path to case root directory")
    parser.add_argument("--court", default="MagCourt_Civil",
                       help="Court type: MagCourt_Civil, MagCourt_Criminal, FCWA, DistrictCourt")
    parser.add_argument("--file-no", default="", help="Court file number")
    parser.add_argument("--parties", default="", help="Party names (e.g., Smith v Jones)")
    args = parser.parse_args()

    root = args.case_root
    root_name = os.path.basename(root)

    # Create directories
    created_dirs = create_dirs(root)

    # Create dashboard files
    files_created = []

    if write_if_missing(os.path.join(root, "01_Dashboard/Case_Overview.md"),
                        case_overview(root_name, args.court, args.file_no, args.parties)):
        files_created.append("01_Dashboard/Case_Overview.md")

    if write_if_missing(os.path.join(root, "01_Dashboard/Timeline_Short.md"),
                        timeline_short(root_name)):
        files_created.append("01_Dashboard/Timeline_Short.md")

    # Court-specific important dates
    if args.court == "MagCourt_Criminal":
        dates_content = important_dates_criminal(root_name)
    elif args.court == "MagCourt_Civil":
        dates_content = important_dates_civil(root_name)
    else:
        dates_content = important_dates_generic(root_name)

    if write_if_missing(os.path.join(root, "01_Dashboard/Important_Dates.md"), dates_content):
        files_created.append("01_Dashboard/Important_Dates.md")

    # AI workspace README
    if write_if_missing(os.path.join(root, "99_AI_Workspace/README.md"), AI_README):
        files_created.append("99_AI_Workspace/README.md")

    # Index files
    if write_if_missing(os.path.join(root, "02_Evidence/Evidence_Index.csv"), EVIDENCE_INDEX_HEADER):
        files_created.append("02_Evidence/Evidence_Index.csv")

    if write_if_missing(os.path.join(root, "03_Communications/Comms_Index.csv"), COMMS_INDEX_HEADER):
        files_created.append("03_Communications/Comms_Index.csv")

    # AI usage log
    log_md = f"# AI Usage Log\n\n_Created {today()}_\n"
    if write_if_missing(os.path.join(root, "99_AI_Workspace/Logs/AI_Usage_Log.md"), log_md):
        files_created.append("99_AI_Workspace/Logs/AI_Usage_Log.md")

    # Report
    print(f"Case root: {root}")
    print(f"Court: {args.court}")
    print(f"Directories created: {len(created_dirs)}")
    for d in created_dirs:
        print(f"  + {d}")
    print(f"Files created: {len(files_created)}")
    for f in files_created:
        print(f"  + {f}")
    if not created_dirs and not files_created:
        print("  (all folders and files already exist — no changes made)")

if __name__ == "__main__":
    main()
