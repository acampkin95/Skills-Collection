---
name: case-file-manager-wa
description: Use when organising Western Australian self-represented litigant case folders, evidence indexes.
---

# SRL Case File Manager — Western Australia

Organise and maintain case folders for self-represented litigants in WA courts. This skill handles folder structure, naming conventions, indexes, and dashboard documents. It does **not** provide legal advice or predict outcomes. For electronic filing, documents can be submitted via the eLodgment system on the eCourts Portal (www.ecourts.wa.gov.au) or in person at any Magistrates Court registry.

> **Mandatory disclaimer**: This skill provides organisational and administrative assistance only. It is **not** legal advice. Seek independent legal advice from a WA lawyer, Legal Aid WA (1300 650 579), or a community legal centre before making court decisions.

## Source Quality Protocol

Use primary sources first: WA legislation from `legislation.wa.gov.au`, court rules/forms/practice directions from official court sites, and full judgments from AustLII, Jade, or court-published reasons. Treat legal blogs, generic advice pages, and AI summaries as leads only. Do not present a proposition as settled law unless it is supported by legislation, rules, practice directions, or a reported decision. When a fee, form number, filing channel, or deadline matters, verify it on the official site during the current task.

## Quick Router

| Need | Go to |
|------|-------|
| Initialise a new case folder | § Operations → `init_case_structure` |
| Audit an existing folder | § Operations → `lint_case_structure` |
| Name a new document | § Operations → `suggest_filename` |
| Update dashboard/overview docs | § Operations → `update_dashboard_docs` |
| Build or update evidence index | § Operations → `update_evidence_index` |
| Build or update comms log | § Operations → `update_comms_index` |
| Log AI usage | § Operations → `record_ai_usage_event` |
| Clean up AI workspace | § Operations → `cleanup_ai_workspace` |
| WA Magistrates Court forms and procedures (civil) | `references/wa-magistrates-civil.md` |
| WA Magistrates Court criminal procedures | `references/wa-magistrates-criminal.md` |
| Affidavit and evidence bundle standards | `references/evidence-standards.md` |
| Dashboard and index templates | `references/templates.md` |

## Canonical Directory Layout

Every case folder follows this structure:

```
<CaseName> - <Court> - <FileNo>/
├── 01_Dashboard/
│   ├── Case_Overview.md
│   ├── Timeline_Short.md
│   └── Important_Dates.md
├── 02_Evidence/
│   ├── Evidence_Index.csv
│   ├── Documents/
│   ├── Photos_Videos/
│   ├── Financial/
│   ├── Witnesses/
│   ├── Expert_Reports/
│   └── Other/
├── 03_Communications/
│   ├── Comms_Index.csv
│   ├── Emails/
│   ├── Letters/
│   ├── Messages/
│   └── Call_Notes/
├── 04_Court_Documents/
│   ├── Filed/          ← IMMUTABLE: sealed/filed PDFs only
│   ├── Drafts/         ← Editable working copies
│   └── Orders_Judgments/  ← IMMUTABLE: orders and reasons
├── 05_Research_Strategy/
│   ├── Case_Law/
│   ├── Legislation/
│   └── Notes/
├── 90_Archive/
└── 99_AI_Workspace/
    ├── README.md       ← Warning: not court-ready material
    ├── AI_Drafts/
    ├── Scratchpad/
    └── Logs/
        ├── AI_Usage_Log.md
        └── AI_Usage_Log.ndjson
```

### Folder Rules

- Create missing canonical folders. Never delete or move unknown user folders without explicit instruction.
- `04_Court_Documents/Filed/` and `Orders_Judgments/` are **immutable** — never auto-edit or delete files in these folders.
- `99_AI_Workspace/` content is never treated as court-ready or authoritative.
- Idempotent: repeated operations must not duplicate folders/files or overwrite user content.

### Relationship to Other Skills' Folder Structures

This structure is designed for **SRL case management** — ongoing matters with dashboard, evidence, communications, and research. For complex litigation matters requiring full intake-to-filing lifecycle, use the `legal-matter-ops` folder structure instead. The skills share common principles (immutable filed documents, separated AI workspace, evidence traceability) but differ in focus:

| This skill (`case-file-manager-wa`) | `legal-matter-ops` | `affidavit-court-preparation` |
|---|---|---|
| 01_Dashboard | 02_Evidence_Inventory | 02_Working_Evidence_Inventory |
| 02_Evidence | 01_Source_Materials | 01_Source_Materials |
| 03_Communications | (within 01_Source_Materials/Messages) | (within 01_Source_Materials) |
| 04_Court_Documents | 04_Affidavit + 08_Print_Bundle | 04_Affidavit + 08_Print_Bundle |
| 05_Research_Strategy | 03_Chronology | 03_Chronology |
| — | 05_Disclosure | 05_Disclosure |
| — | 06_Annexures_Exhibits | 06_Annexures_Exhibits |
| — | 07_Hearing_Prep | 07_Hearing_Prep |
| — | 09_Review_Reports | 09_Review_Reports |
| 90_Archive | 90_Archive | 90_Archive |
| 99_AI_Workspace | 99_AIStore | 99_AI_Workspace |

Use the structure that matches your workflow. Do not mix structures within a single matter.

## File Naming Convention

```
<YYYY-MM-DD>_<Type>_<ShortDescription>[_vN][_DRAFT|_FILED].<ext>
```

**Type vocabulary** (WA court-aligned):

| Type | Use for |
|------|---------|
| `Claim` | Statement of claim (civil — see MCWA online forms) |
| `Defence` | Statement of defence |
| `Counterclaim` | Counterclaim |
| `Reply` | Claimant's reply |
| `Affidavit` | General Form of Affidavit (MCWA Form_Affidavit) |
| `Application` | CPR Form 6, interlocutory applications, Form 12 (Vary/Cancel restraining order) |
| `Order` | Court orders received |
| `Judgment` | Judgments and reasons |
| `Subpoena` | Witness summons (CPR Form 9, Form 10, Form 11) |
| `ServiceAffidavit` | Proof of service |
| `Letter` | Formal correspondence |
| `Email` | Email evidence |
| `Message` | SMS/chat evidence |
| `CallNote` | Phone call records |
| `Evidence` | General evidence items |
| `Photo` | Photographic evidence |
| `Financial` | Bank statements, invoices, receipts |
| `CharRef` | Character reference (criminal) |
| `BailApp` | Bail application (Bail Form 5A/5B) |
| `Note` | Internal notes |

**Rules:**
- `_FILED` only on documents actually filed/served (placed in `Filed/`)
- `_DRAFT` on editable pre-filing versions (placed in `Drafts/`)
- Version suffix `_v2`, `_v3` etc. for iterative drafts
- When linting, suggest compliant names but never auto-rename

## Operations

### `init_case_structure`

Creates the canonical directory tree and populates dashboard templates. Helper script: `scripts/init_case.py`.

**Input context required:**
- `case_root` — directory name (e.g., `Smith_v_Jones - MagCourt - CIV2025_1234`)
- `court` — one of: `MagCourt_Civil`, `MagCourt_Criminal`, `FCFCOA`, `DistrictCourt`
- `file_no` — court file number
- `parties` — party names (e.g., `Smith v Jones`)

**Behaviour:**
1. Create all missing canonical folders per the layout above.
2. Populate `01_Dashboard/Case_Overview.md` from template (see `references/templates.md`).
3. Populate `01_Dashboard/Timeline_Short.md` from template.
4. Populate `01_Dashboard/Important_Dates.md` with court-specific deadlines.
5. Create `99_AI_Workspace/README.md` with warning banner.
6. Create empty `02_Evidence/Evidence_Index.csv` and `03_Communications/Comms_Index.csv` with headers.
7. If court is `MagCourt_Civil`, pre-populate Important_Dates with 14-day defence deadline.
8. If court is `MagCourt_Criminal`, pre-populate with first appearance, bail, and adjournment deadlines.

**Idempotency:** Skip existing folders/files. Never overwrite user content.

### `lint_case_structure`

Scans `case_root` and emits a structured JSON report. Helper script: `scripts/lint_case.py`.

```json
{
  "missing_directories": ["03_Communications"],
  "unexpected_directories": ["tmp"],
  "naming_issues": [
    {
      "path": "04_Court_Documents/Drafts/my affidavit.docx",
      "reason": "Non-standard filename",
      "suggested": "2025-03-05_Affidavit_Parenting_DRAFT.docx"
    }
  ],
  "immutability_violations": [
    {
      "path": "04_Court_Documents/Filed/AI_Draft_response.docx",
      "reason": "AI content in Filed folder"
    }
  ],
  "missing_indexes": ["02_Evidence/Evidence_Index.csv"],
  "stale_dashboard": {
    "Case_Overview.md": "last_updated 45 days ago"
  }
}
```

**Lint rules:**
1. All 7 canonical top-level folders exist.
2. No `AI_` prefixed files or `99_AI_Workspace` content appears under `04_Court_Documents/Filed/` or `Orders_Judgments/`.
3. Files under `04_Court_Documents/` should begin with `YYYY-MM-DD_`.
4. `_FILED` suffix only appears in `Filed/` folder.
5. `Evidence_Index.csv` exists if `02_Evidence/` contains files.
6. `Comms_Index.csv` exists if `03_Communications/` contains files.
7. `Case_Overview.md` and `Timeline_Short.md` exist under `01_Dashboard/`.
8. Dashboard docs updated within last 14 days (warn if stale).

Never modify anything — report only.

### `suggest_filename`

Generates a compliant filename and target directory. Helper script: `scripts/suggest_filename.py`.

**Input:** category, type, description, date, status, version, extension
**Output:** `{ relative_dir, filename, full_path }`

Routing logic:
- `status=FILED` → `04_Court_Documents/Filed/`
- `status=DRAFT` → `04_Court_Documents/Drafts/`
- `category=evidence` → `02_Evidence/<appropriate_subfolder>/`
- `category=communication` → `03_Communications/<appropriate_subfolder>/`
- `category=note` → `05_Research_Strategy/Notes/`

### `update_dashboard_docs`

Updates `01_Dashboard/` files from user instructions or extracted metadata. Helper script: `scripts/update_dashboard.py`.

**Sub-commands:**
- `status` — Update `Case_Overview.md` summary and `last_updated` timestamp
- `deadline` — Add or update a deadline row in `Important_Dates.md`
- `event` — Append a chronologically sorted event to `Timeline_Short.md`
- `changelog` — Prepend an entry to the `Case_Overview.md` changelog section

**Rules:**
- Preserve user-written sections not explicitly updated.
- Keep documents concise — a magistrate should be able to quickly understand the case.
- Maintain YAML front-matter for machine parsing.
- Append to changelog in `Case_Overview.md` — never overwrite history.
- For WA Magistrates Court matters, focus on: clear statement of issues, orders sought, chronological narrative, evidence mapping.

### `update_evidence_index`

Helper script: `scripts/update_evidence_index.py`.

**Target:** `02_Evidence/Evidence_Index.csv`

**Schema:**
```
ID,Date,Description,Relevance,Category,SourcePath
E001,2024-01-15,"Bank statement joint account","Property division","Financial","Financial/E001_2024-01-15_BankStatement.pdf"
```

**Behaviour:**
1. Scan `02_Evidence/` subfolders for unlisted files.
2. Propose new entries — append only, never erase human edits.
3. Do not fabricate dates; infer from filename or leave blank.
4. Maintain sequential `E###` IDs.
5. Keep sorted by date.

### `update_comms_index`

Helper script: `scripts/update_comms_index.py`.

**Target:** `03_Communications/Comms_Index.csv`

**Schema:**
```
Date,Type,From,To,ShortDescription,Important,SourcePath
2025-02-01,Email,"Self","Opposing Party","Handover dispute","yes","Emails/2025-02-01_Email_HandoverDispute.pdf"
```

**Behaviour:** Same append-only pattern as evidence index. Maintain chronological order.

### `record_ai_usage_event`

Helper script: `scripts/record_ai_usage.py`.

**Target files:**
- `99_AI_Workspace/Logs/AI_Usage_Log.md` (human-readable)
- `99_AI_Workspace/Logs/AI_Usage_Log.ndjson` (machine-readable)

Append a dated entry for each significant AI action that creates or modifies a file. Never overwrite prior entries. Include: model used, task description, input files, output file path, user confirmation status.

### `cleanup_ai_workspace`

Helper script: `scripts/cleanup_ai_workspace.py`.

Two phases — analysis (always), then execution (only with explicit user confirmation):

1. **Analysis:** Report old scratchpads (>30 days), duplicated drafts, suggested archives.
2. **Execution:** Move to `90_Archive/` or delete per user instruction. Never auto-delete.

## Guardrails

This skill is **organisational/administrative only**. It must:
- Use phrasing like "organise", "format", "index", "structure" — never "argue", "advise", "predict".
- Decline substantive legal advice requests with: *"This skill organises case files and formats documents but cannot advise on legal strategy or predict court outcomes. For legal advice, contact Legal Aid WA (1300 650 579) or a community legal centre."*
- Still help structure documents, format evidence lists, and clean folder names when asked.
- Always include the mandatory disclaimer when first responding in a session.

## Validation

After changing this skill, run the local validator. Prefer Docker when available:

```bash
docker compose -f compose.skills.yml run --rm skills-validator
```

Use the host fallback only when Docker is unavailable:

```bash
uv run --project .maintenance/Skills-Framework-Reference skills-ref validate case-file-manager-wa
```

## Common SRL Workflows

### New civil claim (Magistrates Court)
1. `init_case_structure` with `--court MagCourt_Civil`
2. Help user draft statement of claim → save to `04_Court_Documents/Drafts/`
3. Help user format supporting affidavit → see General Form of Affidavit on MCWA; load `references/evidence-standards.md`
4. Update Important_Dates with service and defence deadlines
5. File via eLodgment (eCourts Portal) or in person at any MCWA registry
6. After filing: move to `Filed/` with `_FILED` suffix, update dashboard

### Responding to a civil claim
1. `init_case_structure` — user provides file number from claim served on them
2. Import served documents to `04_Court_Documents/Filed/`
3. Calculate response/defence deadline from the current form, rules, and service facts (14 days is common for WA service; longer periods can apply for interstate/overseas service) → update Important_Dates
4. Help structure defence in `Drafts/`
5. Organise supporting evidence → update evidence index
6. File response via eLodgment or in person

### Criminal first appearance preparation
1. `init_case_structure` with `--court MagCourt_Criminal`
2. Import prosecution notice (CPR Form 3) to `04_Court_Documents/Filed/`
3. Update Important_Dates with court date
4. If bail needed: help organise character references, Bail Form 5A/5B
5. Load `references/wa-magistrates-criminal.md` for plea options and duty lawyer info

### Ongoing case maintenance
1. `lint_case_structure` — identify compliance issues
2. `update_evidence_index` — catch unlisted evidence files
3. `update_comms_index` — catch unlisted communications
4. `update_dashboard_docs` — refresh status, add events, update deadlines
5. `record_ai_usage_event` — log any AI-assisted work
6. `cleanup_ai_workspace` — archive stale AI drafts

## Context Loading Strategy

When summarising or building dashboards, prefer curated files:
1. `Case_Overview.md`, `Timeline_Short.md`, indexes, orders
2. Small relevant excerpts from evidence or communications
3. Never load large raw PDFs directly — use document chunking if needed
4. For WA Magistrates Court specifics, load the appropriate reference file

## Reference Files

| File | Load when |
|------|-----------|
| `references/wa-magistrates-civil.md` | Civil claim procedures, forms, deadlines, mediation |
| `references/wa-magistrates-criminal.md` | Criminal procedures, bail, character references, pleas |
| `references/evidence-standards.md` | Affidavit formatting, evidence bundles, pagination |
| `references/templates.md` | Dashboard templates, index schemas, README content |

## Cross-References to Other Skills

| Related Skill | Use when |
|---------------|----------|
| `legal-matter-ops` | Full 15-phase lifecycle from intake through to bundle freeze, Bates numbering, chain of custody, DOCX/PDF generation |
| `affidavit-court-preparation` | Drafting or refining affidavits, chronology reconstruction, hearing preparation, print bundle assembly |
| `wa-fvro` | FVRO-specific guidance, Form 12 for vary/cancel, FVRO conferencing, breach defences |
| `wa-law-general` | General WA court hierarchy, legislation references, legal services, filing fees |
| `csv-legal-analysis` | Analysing CSV/message data for evidence extraction and classification |
| `reportlab-python` | Generating PDF evidence bundles from Python |
| `pdfkit-node` | Generating PDF evidence bundles from Node.js |
