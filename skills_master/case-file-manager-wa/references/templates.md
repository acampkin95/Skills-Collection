# Dashboard and Index Templates

> Load this file when running `init_case_structure` or `update_dashboard_docs` operations.

## Case Overview Template

```markdown
---
case_root: "<CaseName> - <Court> - <FileNo>"
court: "<Court>"
file_no: "<FileNo>"
parties: "<Party1> v <Party2>"
last_updated: "<YYYY-MM-DD>"
---

# Case Overview

## Summary

[1–3 short paragraphs in plain English summarising the case. Include: what the dispute is about, who the parties are, and what stage the case is at.]

## Orders Sought

1. [Order 1 — what you are asking the court to do]
2. [Order 2]
3. [Order 3]

## Key Evidence (IDs)

- E001–E005: [Brief description of evidence group]
- E010–E015: [Brief description]

## Agreed and Disputed Issues

| Issue | Your Position | Other Party's Position | Status |
|-------|--------------|----------------------|--------|
| [Issue 1] | [Your view] | [Their view] | Disputed |
| [Issue 2] | [Your view] | [Their view] | Agreed |

## Key Contacts

| Role | Name | Contact |
|------|------|---------|
| Self | [Your name] | [Phone/email] |
| Other party | [Name] | [Phone/email or "via solicitor"] |
| Other party's solicitor | [Name/firm] | [Phone/email] |
| Court registry | [Court name] | [Phone] |

## Changelog

- <YYYY-MM-DD>: Case folder created. [Initial summary of matter.]
```

## Timeline Short Template

```markdown
---
case_root: "<CaseName> - <Court> - <FileNo>"
type: "short_timeline"
last_updated: "<YYYY-MM-DD>"
---

# Short Timeline of Key Events

## [Year]

- [YYYY-MM-DD] — [One-line description of event] (EID: E0xx, if linked to evidence)

## Open Questions

- [Question about unclear event or date that needs confirmation]
```

**Rules for timeline maintenance:**
- Keep entries sorted by date (oldest first within each year)
- One line per event — keep it factual, not argumentative
- Link to evidence IDs where available
- Remove open questions when resolved (move to changelog)
- Never duplicate entries

## Important Dates Template

### For MagCourt_Civil

```markdown
---
case_root: "<CaseName> - <Court> - <FileNo>"
type: "important_dates"
last_updated: "<YYYY-MM-DD>"
---

# Important Dates

## Court Dates

| Date | Event | Location | Notes |
|------|-------|----------|-------|
| [YYYY-MM-DD] | [Hearing type] | [Court/room] | [Preparation notes] |

## Deadlines

| Deadline | Date | Action Required | Status |
|----------|------|----------------|--------|
| Defence deadline | [calculate from served form/rules/service facts] | Defendant must lodge defence or notice of intention to defend | Pending |
| Service deadline | [5 days before hearing] | Documents must be served | Pending |
| Claim validity | [1 year from lodgement] | Claim expires if not served | Active |

## Reminders

- [ ] Register for eCourts Portal (allow 24 hours)
- [ ] Prepare evidence bundle (3 copies: court, opponent, self)
- [ ] Arrange affidavit swearing (JP, Commissioner for Oaths, or lawyer)
- [ ] File Affidavit of Service after serving documents
```

### For MagCourt_Criminal

```markdown
---
case_root: "<CaseName> - <Court> - <FileNo>"
type: "important_dates"
last_updated: "<YYYY-MM-DD>"
---

# Important Dates

## Court Dates

| Date | Event | Location | Notes |
|------|-------|----------|-------|
| [YYYY-MM-DD] | First appearance | [Court] | Plea not required; adjournment available |

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
- [ ] Prepare character references (2–3, addressed to "The Presiding Magistrate")
- [ ] Prepare mitigation affidavit (CPR Form 2) if pleading guilty
- [ ] Bring photo ID to court
```

## Evidence Index CSV Header

```csv
ID,Date,Description,Relevance,Category,SourcePath
```

**Category values:** Documents, Photos_Videos, Financial, Witnesses, Expert_Reports, Other

**ID format:** E001, E002, … E999 (sequential, zero-padded to 3 digits)

## Communications Index CSV Header

```csv
Date,Type,From,To,ShortDescription,Important,SourcePath
```

**Type values:** Email, Letter, Message, CallNote, CourtCorrespondence

**Important values:** yes, no

## AI Workspace README Template

```markdown
# AI Workspace — Not Official Court Documents

**WARNING: Nothing in this folder is filed with any court.**

This folder contains AI-generated drafts, summaries, and working notes. These are tools to help you organise your thoughts — they are not court documents.

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

## AI Usage Log

The `Logs/` subfolder maintains a record of all AI-assisted work on this case. This supports transparency if the court or opposing party asks about AI usage.
```

## AI Usage Log Entry Template (Markdown)

```markdown
## <YYYY-MM-DD>

- **Tool/model:** <model name>
- **Task:** <What you asked the AI to do>
- **Input files:** <List of files provided to the AI>
- **Output file:** <Path to AI-generated file>
- **User note:** "<Your note about how you used/modified the output>"
```

## AI Usage Log Entry Template (NDJSON)

```json
{"timestamp_utc":"<ISO-8601>","task":"<description>","model":"<model>","input_paths":["<path1>"],"output_path":"<path>","user_confirmation":false}
```
