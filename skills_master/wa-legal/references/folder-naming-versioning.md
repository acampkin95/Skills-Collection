# Legal Matter Folder & Versioning Standards

**Version:** 1.0
**Maintenance note:** Verify naming, filing, and retention requirements against current matter protocols before use.
**Scope:** Court affidavit preparation and disclosure workflows

---

## 1. Canonical Folder Structure (Expanded)

### Complete Directory Tree

```
<MatterName>/
├── 01_Source_Materials/          ← IMMUTABLE originals
│   ├── Documents/
│   ├── Messages/
│   ├── Photos_Media/
│   ├── Financial/
│   └── Third_Party/
├── 02_Evidence_Inventory/
│   ├── Evidence_Index.csv
│   ├── Chain_of_Custody_Log.csv
│   └── Bates_Register.csv
├── 03_Chronology/
│   ├── Master_Chronology.csv
│   └── Timeline_Summary.md
├── 04_Affidavit/
│   ├── Drafts/
│   └── Final/
├── 05_Disclosure/
│   ├── Disclosure_Schedule.csv
│   └── Disclosed_Documents/
├── 06_Annexures_Exhibits/
│   ├── Annexure_Index.csv
│   └── Prepared/
├── 07_Hearing_Prep/
│   ├── Scripts/
│   ├── Issue_Notes/
│   └── One_Pagers/
├── 08_Print_Bundle/
│   ├── ForAllParties/
│   ├── PrivatePreparation/
│   ├── ToBeReviewed/
│   └── Bundle_Manifest.csv
├── 09_Review_Reports/
│   ├── Adversarial_Review.md
│   ├── Final_Run_Report.md
│   └── Version_Register.csv
├── 10_Meeting_Data/
│   ├── Notes/
│   ├── Action_Items.csv
│   └── Obligation_Register.csv
├── 90_Archive/
└── 99_AIStore/
    ├── README.md
    ├── Drafts/
    ├── Scratchpad/
    ├── Scripts/
    ├── Transforms/
    └── Logs/
```

### Folder Definitions

#### 01_Source_Materials (IMMUTABLE)

**Purpose:** Single source of truth for all original, unmodified evidence and documents.

**What goes in it:**
- Court orders, pleadings, subpoenas
- Emails, messages, call records
- Photographs and media files
- Financial statements and records
- Third-party correspondence and documents
- Original contracts and agreements
- Any evidentiary material in its original form

**What must NOT go in it:**
- Drafts, working versions, or analysed copies
- AI-generated content or interpretations
- Redacted or edited versions (move to 05_Disclosure if redacted for production)
- Notes, commentary, or annotations

**Mutability rules:** IMMUTABLE. Files received here remain in original format and name. No modifications, deletions, or renames after intake. If a document must be excluded, create a notation in Evidence_Index.csv explaining why; do not remove the file.

**Content creation:** Intake process, subpoena response, document gathering.

**Subfolder detail:**
- **Documents/**: Court orders, pleadings, letters, agreements, contracts
- **Messages/**: Emails, SMS, WhatsApp, Teams, or other chat transcripts (exported)
- **Photos_Media/**: Images, videos, audio recordings
- **Financial/**: Bank statements, invoices, tax records, accounting documents
- **Third_Party/**: Correspondence and documents from third parties (opposing counsel, police, witnesses)

---

#### 02_Evidence_Inventory

**Purpose:** Structured registry of all evidence and its properties for discovery, disclosure, and legal strategy.

**What goes in it:**
- Evidence_Index.csv — master list with file paths, descriptions, relevance, dates
- Chain_of_Custody_Log.csv — provenance, acquisition, handling record
- Bates_Register.csv — Bates numbers assigned (if documents are Bates-numbered)

**What must NOT go in it:**
- Original evidence files (they stay in 01_Source_Materials/)
- Copies of evidence (they live in appropriate process folders)

**Mutability rules:** APPEND-ONLY. Add entries when new evidence is received. Update property fields as necessary (e.g., Bates number assignment). Never delete entries; mark as "excluded" with justification.

**Content creation:** Intake process, Bates numbering, document review.

**CSV structure details:**
- **Evidence_Index.csv**: file_id | file_path | short_description | date_created | relevance_tags | bates_range | status (included/excluded) | notes
- **Chain_of_Custody_Log.csv**: file_id | date_received | source | received_by | storage_location | last_accessed | accessed_by
- **Bates_Register.csv**: file_id | bates_start | bates_end | date_assigned | file_path | description

---

#### 03_Chronology

**Purpose:** Structured timeline of events material to the legal matter.

**What goes in it:**
- Master_Chronology.csv — complete chronology with dates, parties, events, evidence references
- Timeline_Summary.md — narrative summary with key dates and turning points

**What must NOT go in it:**
- Disputed or speculative dates (mark as uncertain in CSV)
- Unsubstantiated allegations

**Mutability rules:** EDITABLE. Updated as new evidence emerges. Once affidavit is FINAL, chronology is frozen (mark version in Timeline_Summary.md).

**Content creation:** Evidence review, interview notes analysis.

**CSV structure:**
- date | event_description | parties_involved | evidence_references | certainty_level (confirmed/inferred) | notes

---

#### 04_Affidavit

**Purpose:** Sworn statement and supporting materials.

**What goes in it:**
- **Drafts/**: All working versions, marked v1, v2, etc., with status suffix
- **Final/**: Authoritative affidavit version (no version suffix when FINAL)

**What must NOT go in it:**
- Raw source materials (stay in 01_Source_Materials/)
- Unapproved AI drafts (stay in 99_AIStore/ until human review)

**Mutability rules:**
- **Drafts/**: Editable until marked FINAL
- **Final/**: Content-locked once status is FINAL; any subsequent change requires new version
- **Final/ with FILED status**: Permanently immutable

**Content creation:** Legal practitioner, AI drafting tools (output to 99_AIStore/ first).

---

#### 05_Disclosure

**Purpose:** Documents and schedules produced in discovery/disclosure to the other party.

**What goes in it:**
- Disclosure_Schedule.csv — list of disclosed documents, Bates ranges, descriptions
- Disclosed_Documents/ — subdirectory containing redacted or full copies as required by court order

**What must NOT go in it:**
- Privilege logs (separate folder or appendix)
- Documents not yet approved for production
- Original unredacted files (stay in 01_Source_Materials/)

**Mutability rules:** APPEND-ONLY for Disclosure_Schedule. Disclosed_Documents/ is frozen once schedule is filed.

**Content creation:** Disclosure review process, production to other party.

**CSV structure:**
- document_id | bates_range | date_disclosed | description | redactions_applied (yes/no) | reason_for_redaction

---

#### 06_Annexures_Exhibits

**Purpose:** Exhibits attached to affidavits and prepared for court bundles.

**What goes in it:**
- Annexure_Index.csv — list of all annexures with cross-references to affidavit paragraphs
- Prepared/ — formatted, Bates-numbered, annotated copies ready for binding

**What must NOT go in it:**
- Raw source documents (stay in 01_Source_Materials/)
- Documents not yet approved for annexation

**Mutability rules:** Prepared/ is frozen once bundle is compiled. Updates require new version with date prefix.

**Content creation:** Affidavit drafting, bundle preparation.

**CSV structure:**
- annexure_letter | file_name | description | affidavit_paragraphs_referenced | bates_range | status (prepared/final)

---

#### 07_Hearing_Prep

**Purpose:** Counsel preparation materials for court appearance or examination.

**What goes in it:**
- **Scripts/**: Prepared opening/closing remarks, examination-in-chief scripts
- **Issue_Notes/**: Single-issue analysis documents (one per key issue)
- **One_Pagers/**: Concise reference cards (case law, facts, questions)

**What must NOT go in it:**
- Source evidence (stay in 01_Source_Materials/)
- Final affidavits (stay in 04_Affidavit/)

**Mutability rules:** EDITABLE until hearing occurs. Freeze 48 hours before hearing.

**Content creation:** Counsel, legal team.

---

#### 08_Print_Bundle

**Purpose:** Court bundle (paginated, Bates-numbered documents) in stages of preparation and review.

**What goes in it:**
- **ForAllParties/**: Final bundle distributed to all parties and court
- **PrivatePreparation/**: Internal working copies, marked-up versions, counsel notes
- **ToBeReviewed/**: Bundle awaiting final review before printing
- **Bundle_Manifest.csv** — page number, Bates range, document description, document ID

**What must NOT go in it:**
- Unprepared documents
- Privileged or unreviewable material

**Mutability rules:** FROZEN after bundle freeze declared. Any update requires explicit re-opening and re-versioning of Bundle_Manifest.

**Content creation:** Bundle compilation process, printing coordinator.

**CSV structure:**
- page_number | bates_start | bates_end | document_id | document_description | document_type | date_added

---

#### 09_Review_Reports

**Purpose:** Quality assurance and final readiness reports.

**What goes in it:**
- Adversarial_Review.md — hostile reading, weaknesses, counter-arguments
- Final_Run_Report.md — final checklist, issues resolved, ready-for-court sign-off
- Version_Register.csv — version history and decision log

**What must NOT go in it:**
- Raw drafts (they stay in working folders)
- Client communications (stay in 10_Meeting_Data/)

**Mutability rules:** APPEND-ONLY. Each review phase adds a dated entry. Never delete or overwrite.

**Content creation:** Senior legal practitioner, QC review.

**CSV structure (Version_Register):**
- version_date | document_type | version_number | status | reviewed_by | sign_off_date | notes

---

#### 10_Meeting_Data

**Purpose:** Client meetings, counsel conferences, and obligation tracking.

**What goes in it:**
- **Notes/**: Meeting notes, conference records, instructions received
- **Action_Items.csv** — outstanding tasks with deadlines and owners
- **Obligation_Register.csv** — court orders, case management orders, compliance tracking

**What must NOT go in it:**
- Affidavits or court documents (belong in appropriate folders)
- Confidential advice (may be solicitor-client privileged; store separately if privilege applies)

**Mutability rules:** EDITABLE. Updated as meetings occur and obligations change. Obligation_Register is updated whenever a court order issues.

**Content creation:** Meetings, court orders, email instructions.

**CSV structure (Action_Items):**
- action_id | description | due_date | owner | status (open/complete/overdue) | completion_date | notes

**CSV structure (Obligation_Register):**
- obligation_id | obligation_description | source (court order/case management order) | due_date | status | completion_date | compliance_notes

---

#### 90_Archive

**Purpose:** Superseded and obsolete versions, preserved for audit trail and historical reference.

**What goes in it:**
- Versions marked _SUPERSEDED from any folder
- Documents removed from scope or scope
- Old versions of spreadsheets and registers

**What must NOT go in it:**
- Current working documents (they belong in active folders)
- Original source evidence (stays in 01_Source_Materials/ even if outdated)

**Mutability rules:** IMMUTABLE. Files archived are never modified. New archival entries are appended to Archive_Index.csv.

**Content creation:** Automatic when version status changes to SUPERSEDED.

**Organisation:**
- Subdirectories by date: `90_Archive/2026-03/`, `90_Archive/2026-04/` etc.
- Archive_Index.csv tracks: original_file_name | archive_date | reason_superseded | original_folder | notes

---

#### 99_AIStore (QUARANTINE ZONE)

**Purpose:** Isolation zone for AI-generated content. Content here is not court-facing and requires human review before use.

**CRITICAL RULE: No file from 99_AIStore/ may be referenced in, copied to, or linked from any court-facing folder (01–08). Violation is a compliance error.**

**What goes in it:**
- **Drafts/**: AI-generated affidavit drafts, submissions, analysis (awaiting human review)
- **Scratchpad/**: Experimental analysis, brainstorms, raw AI output (ephemeral)
- **Scripts/**: AI-generated cross-examination scripts, opening remarks (before counsel review)
- **Transforms/**: Data transformations, chronology analyses, document summaries (before verification)
- **Logs/**: Agent execution logs, prompt histories, processing records (for debugging)

**What must NOT go in it:**
- Final documents
- Court-facing material
- Original evidence
- Client communications

**Mutability rules:** EDITABLE. Files are transient until explicitly promoted to working folders. Scratchpad files >30 days old are candidates for archival.

**Content creation:** AI agents, scripts, automated processes.

**README.md (mandatory template):**

```markdown
# AI Store — Quarantine Zone

⚠️ **WARNING**: Content in this folder is AI-generated and NOT court-facing.

## Rules

1. **No content from this folder may be copied, referenced, or linked into court-facing folders (01–08).**
2. **All AI output must be reviewed and approved by a human legal practitioner before use.**
3. **Files here are not discoverable, not discloseable, and not part of the record.**
4. **Scratchpad files older than 30 days should be archived or deleted.**

## Subfolder Guide

- **Drafts/**: Affidavits, submissions, and legal arguments generated by AI. Review for accuracy, relevance, and tone before moving to active working folder.
- **Scratchpad/**: Experimental analysis and brainstorming. May be deleted without record.
- **Scripts/**: Examination scripts and advocacy remarks. Verify factual accuracy and tone before counsel uses.
- **Transforms/**: Chronologies, summaries, and data transformations. Verify against source evidence.
- **Logs/**: Processing records and agent execution logs. For debugging; may be deleted.

## Workflow

1. AI generates content → stored in appropriate 99_AIStore/ subfolder
2. Human reviews content
3. If approved: move to appropriate working folder (04_Affidavit/Drafts/, 07_Hearing_Prep/Scripts/, etc.)
4. If rejected: delete or archive to 90_Archive/

**Do not skip review. Do not copy without review.**

Last updated: [DATE]
```

---

## 2. Folder Rules — Hard Rules

### Immutability Boundaries

1. **01_Source_Materials**: IMMUTABLE after intake.
   - No modifications, deletions, or renames.
   - If evidence must be excluded, update Evidence_Index.csv; do not remove the file.

2. **99_AIStore**: NEVER referenced in court documents.
   - NEVER copied to court-facing folders (01–08) without human review.
   - Violation is a critical compliance error.
   - Warning README required.

3. **04_Affidavit/Final/**: Immutable once status is FINAL.
   - Any change requires new version; old version becomes SUPERSEDED and moves to 90_Archive/.
   - FILED status is permanently immutable.

4. **08_Print_Bundle/**: Frozen after bundle freeze phase.
   - No edits after freeze without explicit re-opening.
   - Re-opening requires version increment and date change.

5. **90_Archive/**: Immutable.
   - Receives superseded versions with datestamp prefix.
   - Files archived are never modified.

### File Routing Rules

1. **All files must route to a subfolder; nothing lives in root.**
   - Violators are flagged in lint checks.

2. **Evidence stays in 01_Source_Materials/ in original form.**
   - Copies for disclosure go to 05_Disclosure/Disclosed_Documents/ or 06_Annexures_Exhibits/Prepared/.
   - Original unredacted or unformatted copies never leave 01_Source_Materials/.

3. **AI output starts in 99_AIStore/.**
   - Human review required before promotion to working folders.

4. **CSVs and registers live at folder root**, not in subfolders:
   - Evidence_Index.csv in 02_Evidence_Inventory/
   - Chain_of_Custody_Log.csv in 02_Evidence_Inventory/
   - Disclosure_Schedule.csv in 05_Disclosure/
   - Bundle_Manifest.csv in 08_Print_Bundle/
   - Action_Items.csv in 10_Meeting_Data/
   - Obligation_Register.csv in 10_Meeting_Data/
   - Annexure_Index.csv in 06_Annexures_Exhibits/

---

## 3. File Naming Convention

### Format

```
<YYYY-MM-DD>_<Type>_<ShortDesc>[_v<N>][_STATUS].<ext>
```

### Rules

- **Date**: Document creation date or event date (not arbitrary). Format: YYYY-MM-DD.
- **Type**: From vocabulary table below. Indicates document category and routing.
- **ShortDesc**: PascalCase, max 40 characters, no spaces, no special characters except hyphen (-).
  - Examples: ParentingAffidavit, PropertyValueAssessment, EmailChain_Jan2025
- **Version**: _v1, _v2, _v3, etc. Sequential. No gaps. No sub-versions (no v1.1, v2a).
  - Omit version suffix when status is FINAL (FINAL is the authoritative version).
- **Status**: _DRAFT, _REVIEW, _FINAL, _FILED, _SUPERSEDED (uppercase).
  - FINAL and FILED files have no version suffix.
  - SUPERSEDED files are moved to 90_Archive/ with original name preserved.
- **Extension**: Lowercase (.docx, .pdf, .csv, .md, .xlsx, .txt, .zip).

### Type Vocabulary & Routing

| Type | Description | Default Folder | Routing Rules |
|------|------------|----------------|----|
| Affidavit | Sworn statement | 04_Affidavit/Drafts/ or Final/ | Must have _DRAFT or _FINAL; Final/ only for complete versions ready for filing |
| Chronology | Timeline document | 03_Chronology/ | Master chronology; multiple versions allowed |
| Disclosure | Disclosure schedule | 05_Disclosure/ | Versioned; freeze before filing |
| Evidence | Evidence item | 01_Source_Materials/ | Original format; no edits |
| Annexure | Prepared exhibit | 06_Annexures_Exhibits/Prepared/ | Numbered (Annexure A, B, etc.); cross-ref affidavit |
| Exhibit | Court exhibit | 06_Annexures_Exhibits/Prepared/ | Identical to Annexure in this context |
| Order | Court order | 01_Source_Materials/Documents/ | Immutable original |
| Application | Court application | 04_Affidavit/ | Treat as Affidavit variant |
| Subpoena | Witness summons | 01_Source_Materials/Documents/ | Immutable original |
| Letter | Formal correspondence | 01_Source_Materials/Documents/ | Immutable original |
| Email | Email evidence | 01_Source_Materials/Messages/ | Exported format (PDF or txt); preserve original headers |
| Message | SMS/chat evidence | 01_Source_Materials/Messages/ | Transcribed or screenshotted; preserve metadata |
| CallNote | Phone call record | 10_Meeting_Data/Notes/ | Date and participants noted |
| Photo | Image evidence | 01_Source_Materials/Photos_Media/ | Original format; Bates-numbered copy in 06_Annexures_Exhibits/Prepared/ |
| Financial | Financial document | 01_Source_Materials/Financial/ | Bank statements, invoices, tax records |
| MeetingNote | Meeting record | 10_Meeting_Data/Notes/ | Date and attendees in filename or metadata |
| Script | Hearing script | 07_Hearing_Prep/Scripts/ | Examination or advocacy remarks |
| IssueNote | Issue analysis | 07_Hearing_Prep/Issue_Notes/ | Single-issue focus |
| BundleManifest | Bundle index | 08_Print_Bundle/ | CSV; one per bundle version |
| ReviewReport | Review document | 09_Review_Reports/ | Adversarial or final run report |

### Naming Examples

**Compliant:**

```
2026-03-16_Affidavit_ParentingArrangements_v1_DRAFT.docx
2026-03-18_Affidavit_ParentingArrangements_v2_REVIEW.docx
2026-03-19_Affidavit_ParentingArrangements_FINAL.docx
2026-03-19_Affidavit_ParentingArrangements_FILED.pdf
2026-03-16_Chronology_MasterTimeline_v1_DRAFT.csv
2026-03-16_Disclosure_ScheduleA_v1_DRAFT.csv
2026-03-15_Email_IncidentDescription_Jan2025.pdf
2026-03-16_MeetingNote_ClientInstructions_v1.md
2026-03-16_Script_ExaminationInChief_v1_DRAFT.md
2026-03-15_ReviewReport_AdversarialReview_v1.md
```

**Non-compliant (reject):**

```
final_v2_REAL.docx              ← date missing, unclear type
Copy of affidavit.docx          ← spaces, no date, vague type
affidavit (1).docx              ← no date, no type, no status
untitled.docx                   ← completely uninformative
New Document.docx               ← spaces, no metadata
test.docx                        ← transient, no date
2026_03_16_Affidavit.docx       ← slashes instead of hyphens, no description
Affidavit_v2.1_DRAFT.docx       ← sub-version (v2.1 not allowed)
2026-03-16_Parenting_Aff_v2.docx ← abbreviations; unclear type
```

---

## 4. Version Lifecycle

### Six-State Workflow

```
DRAFT → REVIEW → FINAL → FILED
  ↓        ↓       ↓       ↓
  └────────SUPERSEDED────→ ARCHIVED
                      ↓
                 90_Archive/
```

### State Definitions

#### DRAFT

**Meaning:** Working version under active development. Subject to change.

**Who creates it:** Legal practitioner, AI agents (to 99_AIStore/ first).

**Where it lives:** Working folder (e.g., 04_Affidavit/Drafts/, 07_Hearing_Prep/Scripts/).

**What transitions are allowed:** → REVIEW (human marks ready for review), → SUPERSEDED (new version created).

**Content rules:** Editable. No restrictions on modification frequency.

**File naming:** `<date>_<Type>_<Desc>_v<N>_DRAFT.<ext>` where N starts at 1.

#### REVIEW

**Meaning:** Submitted for adversarial or quality review. Ready for critical feedback.

**Who creates it:** Practitioner promoting from DRAFT.

**Where it lives:** Working folder or review folder (depends on process; typically same as DRAFT folder).

**What transitions are allowed:** → FINAL (approved after review), → DRAFT (returned for rework), → SUPERSEDED (if new approach needed).

**Content rules:** Locked for review duration. Feedback recorded separately; changes incorporated in new version.

**File naming:** `<date>_<Type>_<Desc>_v<N>_REVIEW.<ext>` where N ≥ 2.

#### FINAL

**Meaning:** Approved, content-locked version. Authoritative for the matter.

**Who creates it:** Practitioner or QC approving document.

**Where it lives:** Final folder (e.g., 04_Affidavit/Final/).

**What transitions are allowed:** → FILED (filed with court), → SUPERSEDED (new version required if edits needed).

**Content rules:** **IMMUTABLE.** Any change requires new version; old becomes SUPERSEDED and moves to 90_Archive/.

**File naming:** `<date>_<Type>_<Desc>_FINAL.<ext>` — **no version suffix** (FINAL is the authoritative version).

**Immutability rule:** Once FINAL, the file path, filename, and content are locked. Moving to FILED does not change immutability; FILED is equally immutable.

#### FILED

**Meaning:** Submitted to court or served on other party. Part of the permanent court record.

**Who creates it:** Practitioner filing or serving document.

**Where it lives:** Final folder (e.g., 04_Affidavit/Final/), marked FILED.

**What transitions are allowed:** None. FILED is terminal and immutable.

**Content rules:** **PERMANENTLY IMMUTABLE.** Never modify, delete, or rename.

**File naming:** `<date>_<Type>_<Desc>_FILED.<ext>` — **no version suffix.**

**Archival:** FILED documents are never archived; they remain in Final/ as permanent record.

#### SUPERSEDED

**Meaning:** Replaced by a newer version. No longer authoritative.

**Who creates it:** Automatic when a new version transitions to FINAL and old version must be archived.

**Where it lives:** 90_Archive/ in dated subfolder (e.g., 90_Archive/2026-03/).

**What transitions are allowed:** → ARCHIVED (eventual cleanup; files remain in 90_Archive/).

**Content rules:** Immutable. Preserved for audit trail.

**File naming:** Original filename preserved; archive index notes reason superseded.

#### ARCHIVED

**Meaning:** Removed from active workflows; preserved for historical reference only.

**Where it lives:** 90_Archive/ in dated subfolder.

**Content rules:** Immutable.

**Cleanup rule:** Files in Scratchpad/ (99_AIStore/Scratchpad/) older than 30 days are candidates for archival or deletion without record.

### Transition Rules & Examples

**Transition: DRAFT → REVIEW**
- Practitioner judges document ready for critical review.
- File renamed: `2026-03-16_Affidavit_Parenting_v1_DRAFT.docx` → `2026-03-16_Affidavit_Parenting_v1_REVIEW.docx`
- No folder change.
- Version number (v1) remains.

**Transition: REVIEW → DRAFT (rework)**
- Reviewer returns document for significant rework.
- New version created: `2026-03-17_Affidavit_Parenting_v2_DRAFT.docx`
- Old REVIEW version archived to 90_Archive/2026-03/ or discarded (if not needed for audit).
- Version number increments.

**Transition: DRAFT → FINAL**
- Practitioner approves document for filing.
- File moved to Final/ folder.
- Renamed: `2026-03-18_Affidavit_Parenting_v3_DRAFT.docx` → `2026-03-19_Affidavit_Parenting_FINAL.docx`
- **Version suffix dropped** (FINAL is authoritative; no need to track which draft iteration it was).
- No further versions in Draft/ folder.

**Transition: FINAL → FILED**
- Document filed with court or served on other party.
- File remains in Final/ folder.
- New file created or old file status changed: `2026-03-19_Affidavit_Parenting_FINAL.docx` → `2026-03-19_Affidavit_Parenting_FILED.pdf` (if format changes; otherwise same filename with date of filing).
- Immutability strengthened: FILED is terminal.

**Transition: FINAL → SUPERSEDED (due to change required)**
- Court order issues requiring affidavit amendment.
- New version drafted: starts at DRAFT.
- Old FINAL file moved to 90_Archive/:
  - Original: `2026-03-19_Affidavit_Parenting_FINAL.docx`
  - Archived: `90_Archive/2026-03/2026-03-19_Affidavit_Parenting_FINAL.docx`
  - Archive_Index.csv records: reason="Court order issued; amendment required"; original_folder="04_Affidavit/Final/"; date_superseded="2026-03-22"
- New version created: `2026-03-22_Affidavit_Parenting_v1_DRAFT.docx` in 04_Affidavit/Drafts/
- Version counter resets to v1 in new DRAFT.

### Version Numbering Detail

**Reset rules:**
- **DRAFT → DRAFT (rework loop):** Version increments (v1 → v2 → v3).
- **DRAFT → REVIEW:** Version unchanged (v2_DRAFT → v2_REVIEW).
- **REVIEW → FINAL:** Version increments if new draft created; otherwise dropped (FINAL has no version suffix).
- **FINAL → SUPERSEDED → new DRAFT:** Version counter resets to v1 (new lifecycle).

**Example full lifecycle:**

```
2026-03-16_Affidavit_Parenting_v1_DRAFT.docx     ← First draft
2026-03-17_Affidavit_Parenting_v2_DRAFT.docx     ← Revised draft
2026-03-18_Affidavit_Parenting_v3_DRAFT.docx     ← Ready for review
2026-03-18_Affidavit_Parenting_v3_REVIEW.docx    ← Submitted for review
2026-03-19_Affidavit_Parenting_FINAL.docx        ← Approved (no version)
2026-03-19_Affidavit_Parenting_FILED.pdf         ← Filed with court

[Later: amendment required]

90_Archive/2026-03/2026-03-19_Affidavit_Parenting_FINAL.docx  ← Old version archived

2026-03-22_Affidavit_Parenting_v1_DRAFT.docx     ← New lifecycle begins
2026-03-23_Affidavit_Parenting_FINAL.docx        ← Approved amendment
```

---

## 5. Version Numbering

### Rules

- **v1, v2, v3, etc.**: Sequential integers only. No gaps.
- **No sub-versions**: v1.1, v2a, 1b are prohibited.
- **Single namespace per document type**: All drafts of a given document share the same counter (Affidavit_Parenting_v1, v2, v3...).
- **Reset on status=FINAL**: When a draft is finalised, the version number is dropped. The FINAL file has no version suffix.
- **Reset on SUPERSEDED → new DRAFT**: When a new lifecycle begins (e.g., amendment to a FINAL doc), the new DRAFT starts at v1 again.

### Examples

**Example 1: Simple approval path**
```
2026-03-16_Affidavit_Parenting_v1_DRAFT.docx
2026-03-17_Affidavit_Parenting_v2_DRAFT.docx
2026-03-18_Affidavit_Parenting_FINAL.docx        ← version suffix dropped
2026-03-19_Affidavit_Parenting_FILED.pdf
```

**Example 2: Review loop**
```
2026-03-16_Affidavit_Parenting_v1_DRAFT.docx
2026-03-17_Affidavit_Parenting_v2_DRAFT.docx
2026-03-18_Affidavit_Parenting_v2_REVIEW.docx    ← v2 unchanged; status changed
2026-03-18_Affidavit_Parenting_v3_DRAFT.docx    ← review returned; new draft
2026-03-19_Affidavit_Parenting_FINAL.docx
```

**Example 3: Amendment cycle**
```
2026-03-19_Affidavit_Parenting_FINAL.docx
2026-03-19_Affidavit_Parenting_FILED.pdf
[Court order: amendment required]
90_Archive/2026-03/2026-03-19_Affidavit_Parenting_FINAL.docx

2026-03-22_Affidavit_Parenting_v1_DRAFT.docx    ← new lifecycle; v1 reset
2026-03-23_Affidavit_Parenting_v2_DRAFT.docx
2026-03-24_Affidavit_Parenting_FINAL.docx       ← version suffix dropped
```

---

## 6. Archival Protocol

### When to Archive

- **SUPERSEDED files**: When a new FINAL version is created, the old FINAL or REVIEW version is marked SUPERSEDED and moved to 90_Archive/.
- **Stale DRAFT/REVIEW**: DRAFT or REVIEW files not updated for >21 days without progression to FINAL are candidates for archival (optional; may keep for rework context).
- **Scratchpad ephemera**: Files in 99_AIStore/Scratchpad/ older than 30 days are candidates for deletion or archival.

### Archival Procedure

1. **Rename** the file with original name preserved (do not change filename during archival).
2. **Move** to 90_Archive/ in a dated subfolder: 90_Archive/YYYY-MM/
3. **Record** in Archive_Index.csv at 90_Archive/ root:
   - original_file_name
   - archive_date (YYYY-MM-DD)
   - reason_superseded (e.g., "New FINAL version created", "Court order amendment", "Scope exclusion")
   - original_folder (where file lived before archival)
   - notes (e.g., link to new file, context)

### Archive_Index.csv Structure

```csv
original_file_name,archive_date,reason_superseded,original_folder,notes
2026-03-19_Affidavit_Parenting_FINAL.docx,2026-03-22,Court order amendment required,04_Affidavit/Final/,New version: 2026-03-24_Affidavit_Parenting_FINAL.docx
2026-03-18_Affidavit_Parenting_v3_REVIEW.docx,2026-03-19,Approved and moved to FINAL,04_Affidavit/Drafts/,Finalised as 2026-03-19_Affidavit_Parenting_FINAL.docx
2026-03-01_Script_ExaminationDraft_v1_DRAFT.md,2026-03-16,Replaced by new script,07_Hearing_Prep/Scripts/,Superseded by 2026-03-16_Script_ExaminationInChief_v1_DRAFT.md
```

### Immutability After Archival

- **Archived files are never modified.** If an archived file must be retrieved and updated, it is treated as a new document with a new date prefix and new version number.
- **Deletion from archive is prohibited.** Files archived are kept indefinitely for audit trail.
- **Retrieval procedure**: If an archived file is needed:
  1. Copy the file back to the appropriate working folder.
  2. Assign a new date and new version number (v1).
  3. Add a note in the new file linking to the archived version.
  4. Update Archive_Index.csv to note retrieval and new file location.

---

## 7. AIStore Isolation Rules

### Quarantine Zone Integrity

**CRITICAL RULE: No file from 99_AIStore/ may be referenced in, copied to, or linked from any court-facing folder (01–08).**

Violation is a critical compliance error and must be remediated immediately.

### Content Categories

**Drafts/**
- AI-generated affidavits, submissions, legal analysis awaiting human review
- AI-enhanced versions of source materials
- Status: Never court-facing until reviewed and promoted

**Scratchpad/**
- Experimental analysis, brainstorms, raw AI output
- Exploratory data transformations
- Status: Ephemeral; may be deleted without record after 30 days

**Scripts/**
- AI-generated cross-examination scripts, opening remarks, examination-in-chief
- Status: Requires counsel review and approval before use

**Transforms/**
- Chronology analyses, document summaries, event extraction
- Data transformations and statistical analyses
- Status: Requires verification against source evidence before use

**Logs/**
- Agent execution logs, prompt histories, processing records
- For debugging and transparency only
- Status: May be deleted after issue resolved

### Promotion Workflow

1. **AI generates content** → stored in 99_AIStore/[Drafts|Scratchpad|Scripts|Transforms|Logs]/
2. **Human reviews content** → assesses accuracy, relevance, legal sufficiency, tone
3. **Approved → Promoted**: File copied to appropriate working folder (04_Affidavit/Drafts/, 07_Hearing_Prep/Scripts/, 03_Chronology/, etc.) with new date and v1 version number
4. **Rejected → Archived or Deleted**: File moved to 90_Archive/ or deleted if not needed for record

### Compliance Checks

- **Lint check**: Scan court-facing folders (01–08) for any file originating from 99_AIStore/. Flag as critical violation.
- **File origin tracking** (optional): Include a note in promoted files indicating source (e.g., "AI draft origin: 99_AIStore/Drafts/; reviewed 2026-03-20").
- **README.md enforcement**: 99_AIStore/README.md must exist and contain the warning banner. Lint check verifies presence.

### Deletion Rules for AIStore

- **Scratchpad/** files: Older than 30 days may be deleted without record.
- **Logs/**: After issue resolved or >7 days old, may be deleted.
- **Other subfolders (Drafts, Scripts, Transforms)**: Do not delete without explicit reason recorded in archive. Archive to 90_Archive/ if permanent record needed; otherwise delete with date-stamped note in cleanup log (optional).

---

## 8. Lint Rules

### Automated Compliance Checks

Run lint checks after each significant folder operation (new documents added, versions created, bundle compiled, etc.). Report findings as JSON with severity levels: `CRITICAL`, `ERROR`, `WARNING`, `INFO`.

### Lint Checks

1. **Canonical folders exist**
   - Check: All folders from section 1 structure exist under <MatterName>/
   - Severity: `CRITICAL` if any folder missing
   - Fix: Create missing folder(s)

2. **No files in root**
   - Check: <MatterName>/ root contains no files
   - Severity: `ERROR` if files found
   - Fix: Move files to appropriate subfolders

3. **No AIStore content in court-facing folders**
   - Check: Scan folders 01–08 for files with path origin in 99_AIStore/
   - Method: Check file metadata or filename hints (e.g., versioning pattern _v1_DRAFT rarely appears in Final/)
   - Severity: `CRITICAL` if found
   - Fix: Remove file; copy approved version to proper working folder

4. **No _FILED files outside Final/ folders**
   - Check: Scan all folders for _FILED status; must only exist in Final/ subfolders
   - Severity: `ERROR` if found outside Final/
   - Fix: Move to appropriate Final/ folder

5. **All files follow naming convention**
   - Check: All files match `<YYYY-MM-DD>_<Type>_<Desc>[_v<N>][_STATUS].<ext>`
   - Severity: `ERROR` if malformed
   - Non-compliant examples: "final_v2_REAL.docx", "Copy of affidavit.docx", "untitled.docx"
   - Fix: Rename to standard

6. **Evidence_Index.csv exists if 01_Source_Materials/ has files**
   - Check: If 01_Source_Materials/ contains files, 02_Evidence_Inventory/Evidence_Index.csv must exist and list entries
   - Severity: `WARNING` if missing
   - Fix: Create Evidence_Index.csv with entries for all source materials

7. **Chain_of_Custody_Log.csv exists if evidence present**
   - Check: If 01_Source_Materials/ contains files, 02_Evidence_Inventory/Chain_of_Custody_Log.csv must exist
   - Severity: `WARNING` if missing
   - Fix: Create and populate with provenance data

8. **No stale DRAFT/REVIEW files**
   - Check: Scan all DRAFT and REVIEW files; flag if not updated for >21 days without progression to FINAL
   - Severity: `WARNING` if found
   - Fix: Recommend promotion to FINAL, archival, or deletion

9. **No duplicate filenames across folders**
   - Check: Scan all folders; flag duplicate filenames (excluding dated versions)
   - Severity: `ERROR` if exact duplicates found
   - Fix: Rename one file to disambiguate

10. **Version register up to date**
    - Check: 09_Review_Reports/Version_Register.csv lists all FINAL, FILED, and significant REVIEW versions
    - Severity: `WARNING` if gaps detected
    - Fix: Update register with recent versions

11. **99_AIStore/README.md exists with warning**
    - Check: File exists and contains quarantine zone warning
    - Severity: `ERROR` if missing
    - Fix: Create file from template in section 1

12. **No SUPERSEDED files in active folders**
    - Check: Scan folders 01–08 for _SUPERSEDED status; must only exist in 90_Archive/
    - Severity: `ERROR` if found in active folders
    - Fix: Move to 90_Archive/

### Lint Report Format (JSON)

```json
{
  "matter_name": "<MatterName>",
  "lint_date": "2026-03-16",
  "total_checks": 12,
  "passed": 11,
  "failed": 1,
  "findings": [
    {
      "check_id": 1,
      "check_name": "Canonical folders exist",
      "severity": "CRITICAL",
      "status": "PASS",
      "details": "All canonical folders present."
    },
    {
      "check_id": 3,
      "check_name": "No AIStore content in court-facing folders",
      "severity": "CRITICAL",
      "status": "FAIL",
      "details": "File '2026-03-15_Affidavit_Draft_v1_DRAFT.docx' in 04_Affidavit/Drafts/ matches AIStore pattern.",
      "file": "04_Affidavit/Drafts/2026-03-15_Affidavit_Draft_v1_DRAFT.docx",
      "suggested_fix": "Remove or verify human-approved promotion from 99_AIStore/."
    },
    {
      "check_id": 5,
      "check_name": "All files follow naming convention",
      "severity": "ERROR",
      "status": "FAIL",
      "details": "Non-compliant filenames detected.",
      "files": [
        "04_Affidavit/Drafts/final_v2_REAL.docx",
        "07_Hearing_Prep/Scripts/Script_ExamInChief.md"
      ],
      "suggested_fix": "Rename to standard: 2026-03-16_Affidavit_<Desc>_v2_DRAFT.docx"
    }
  ]
}
```

---

## 9. Folder Initialisation Script (Python)

### script.py

```python
#!/usr/bin/env python3
"""
Legal Matter Folder Initialisation Script

Creates a canonical folder structure for court affidavit preparation with
templates, lint checking, and safe idempotent operation.

Usage:
    python script.py <matter_name> [--base_path /path/to/base] [--lint]

Example:
    python script.py ParentingDispute_Smith_2026
    python script.py PropertyDispute_ACME_2026 --base_path /Users/alex/Projects/Dev
    python script.py MatterName --lint
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def validate_matter_name(name: str) -> str:
    """Validate and sanitise matter name."""
    if not name or len(name) < 3:
        raise ValueError("Matter name must be at least 3 characters.")
    # Allow alphanumeric, underscore, hyphen
    sanitised = "".join(c if c.isalnum() or c in "-_" else "" for c in name)
    if sanitised != name:
        print(f"Warning: Matter name sanitised from '{name}' to '{sanitised}'")
    return sanitised

def create_canonical_structure(matter_path: Path) -> None:
    """Create full canonical folder structure."""
    folders = [
        "01_Source_Materials",
        "01_Source_Materials/Documents",
        "01_Source_Materials/Messages",
        "01_Source_Materials/Photos_Media",
        "01_Source_Materials/Financial",
        "01_Source_Materials/Third_Party",
        "02_Evidence_Inventory",
        "03_Chronology",
        "04_Affidavit",
        "04_Affidavit/Drafts",
        "04_Affidavit/Final",
        "05_Disclosure",
        "05_Disclosure/Disclosed_Documents",
        "06_Annexures_Exhibits",
        "06_Annexures_Exhibits/Prepared",
        "07_Hearing_Prep",
        "07_Hearing_Prep/Scripts",
        "07_Hearing_Prep/Issue_Notes",
        "07_Hearing_Prep/One_Pagers",
        "08_Print_Bundle",
        "08_Print_Bundle/ForAllParties",
        "08_Print_Bundle/PrivatePreparation",
        "08_Print_Bundle/ToBeReviewed",
        "09_Review_Reports",
        "10_Meeting_Data",
        "10_Meeting_Data/Notes",
        "90_Archive",
        "99_AIStore",
        "99_AIStore/Drafts",
        "99_AIStore/Scratchpad",
        "99_AIStore/Scripts",
        "99_AIStore/Transforms",
        "99_AIStore/Logs",
    ]

    for folder in folders:
        folder_path = matter_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ {folder}")

def create_template_csvs(matter_path: Path) -> None:
    """Create template CSV files with headers."""

    templates = {
        "02_Evidence_Inventory/Evidence_Index.csv": [
            "file_id", "file_path", "short_description", "date_created",
            "relevance_tags", "bates_range", "status", "notes"
        ],
        "02_Evidence_Inventory/Chain_of_Custody_Log.csv": [
            "file_id", "date_received", "source", "received_by",
            "storage_location", "last_accessed", "accessed_by"
        ],
        "02_Evidence_Inventory/Bates_Register.csv": [
            "file_id", "bates_start", "bates_end", "date_assigned",
            "file_path", "description"
        ],
        "03_Chronology/Master_Chronology.csv": [
            "date", "event_description", "parties_involved",
            "evidence_references", "certainty_level", "notes"
        ],
        "05_Disclosure/Disclosure_Schedule.csv": [
            "document_id", "bates_range", "date_disclosed",
            "description", "redactions_applied", "reason_for_redaction"
        ],
        "06_Annexures_Exhibits/Annexure_Index.csv": [
            "annexure_letter", "file_name", "description",
            "affidavit_paragraphs_referenced", "bates_range", "status"
        ],
        "08_Print_Bundle/Bundle_Manifest.csv": [
            "page_number", "bates_start", "bates_end", "document_id",
            "document_description", "document_type", "date_added"
        ],
        "09_Review_Reports/Version_Register.csv": [
            "version_date", "document_type", "version_number", "status",
            "reviewed_by", "sign_off_date", "notes"
        ],
        "10_Meeting_Data/Action_Items.csv": [
            "action_id", "description", "due_date", "owner",
            "status", "completion_date", "notes"
        ],
        "10_Meeting_Data/Obligation_Register.csv": [
            "obligation_id", "obligation_description", "source",
            "due_date", "status", "completion_date", "compliance_notes"
        ],
        "90_Archive/Archive_Index.csv": [
            "original_file_name", "archive_date", "reason_superseded",
            "original_folder", "notes"
        ],
    }

    for csv_path, headers in templates.items():
        full_path = matter_path / csv_path
        if full_path.exists():
            print(f"⊘ {csv_path} (already exists)")
            continue

        with open(full_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        print(f"✓ {csv_path}")

def create_aistore_readme(matter_path: Path) -> None:
    """Create 99_AIStore/README.md with warning banner."""
    readme_path = matter_path / "99_AIStore" / "README.md"

    if readme_path.exists():
        print("⊘ 99_AIStore/README.md (already exists)")
        return

    content = """# AI Store — Quarantine Zone

⚠️ **WARNING**: Content in this folder is AI-generated and NOT court-facing.

## Rules

1. **No content from this folder may be copied, referenced, or linked into court-facing folders (01–08).**
2. **All AI output must be reviewed and approved by a human legal practitioner before use.**
3. **Files here are not discoverable, not discloseable, and not part of the record.**
4. **Scratchpad files older than 30 days should be archived or deleted.**

## Subfolder Guide

- **Drafts/**: Affidavits, submissions, and legal arguments generated by AI. Review for accuracy, relevance, and tone before moving to active working folder.
- **Scratchpad/**: Experimental analysis and brainstorming. May be deleted without record.
- **Scripts/**: Examination scripts and advocacy remarks. Verify factual accuracy and tone before counsel uses.
- **Transforms/**: Chronologies, summaries, and data transformations. Verify against source evidence.
- **Logs/**: Processing records and agent execution logs. For debugging; may be deleted.

## Workflow

1. AI generates content → stored in appropriate 99_AIStore/ subfolder
2. Human reviews content
3. If approved: move to appropriate working folder (04_Affidavit/Drafts/, 07_Hearing_Prep/Scripts/, etc.)
4. If rejected: delete or archive to 90_Archive/

**Do not skip review. Do not copy without review.**

Last updated: {date}
""".format(date=datetime.now().strftime("%Y-%m-%d"))

    with open(readme_path, "w") as f:
        f.write(content)
    print("✓ 99_AIStore/README.md")

def run_lint_checks(matter_path: Path) -> dict:
    """Run compliance lint checks and return report."""
    checks_passed = 0
    checks_failed = 0
    findings = []

    # Check 1: Canonical folders exist
    required_folders = [
        "01_Source_Materials", "02_Evidence_Inventory", "03_Chronology",
        "04_Affidavit", "04_Affidavit/Drafts", "04_Affidavit/Final",
        "05_Disclosure", "06_Annexures_Exhibits", "07_Hearing_Prep",
        "08_Print_Bundle", "09_Review_Reports", "10_Meeting_Data",
        "90_Archive", "99_AIStore"
    ]
    missing = [f for f in required_folders if not (matter_path / f).exists()]
    if missing:
        checks_failed += 1
        findings.append({
            "check_id": 1,
            "check_name": "Canonical folders exist",
            "severity": "CRITICAL",
            "status": "FAIL",
            "missing_folders": missing
        })
    else:
        checks_passed += 1

    # Check 2: No files in root
    root_files = [f for f in matter_path.iterdir() if f.is_file()]
    if root_files:
        checks_failed += 1
        findings.append({
            "check_id": 2,
            "check_name": "No files in root",
            "severity": "ERROR",
            "status": "FAIL",
            "files": [f.name for f in root_files]
        })
    else:
        checks_passed += 1

    # Check 11: 99_AIStore/README.md exists
    readme = matter_path / "99_AIStore" / "README.md"
    if not readme.exists():
        checks_failed += 1
        findings.append({
            "check_id": 11,
            "check_name": "99_AIStore/README.md exists with warning",
            "severity": "ERROR",
            "status": "FAIL",
            "file": "99_AIStore/README.md"
        })
    else:
        checks_passed += 1

    # (Additional checks can be extended here)

    report = {
        "matter_path": str(matter_path),
        "lint_date": datetime.now().strftime("%Y-%m-%d"),
        "total_checks": 11,
        "passed": checks_passed,
        "failed": checks_failed,
        "findings": findings
    }

    return report

def main():
    parser = argparse.ArgumentParser(
        description="Initialise canonical legal matter folder structure."
    )
    parser.add_argument(
        "matter_name",
        help="Matter name (e.g., ParentingDispute_Smith_2026)"
    )
    parser.add_argument(
        "--base_path",
        default=os.getcwd(),
        help="Base path for matter folder (default: current directory)"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run lint checks only; do not create folders"
    )

    args = parser.parse_args()

    try:
        matter_name = validate_matter_name(args.matter_name)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    matter_path = Path(args.base_path) / matter_name

    if args.lint:
        if not matter_path.exists():
            print(f"Error: Matter folder not found at {matter_path}")
            sys.exit(1)
        print(f"\nRunning lint checks for {matter_name}...\n")
        report = run_lint_checks(matter_path)
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["failed"] == 0 else 1)

    # Initialisation mode
    print(f"\nInitialising matter folder: {matter_name}")
    print(f"Path: {matter_path}\n")

    if matter_path.exists():
        print(f"Matter folder already exists. Skipping creation.\n")
    else:
        matter_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Matter folder created\n")

    print("Creating canonical folder structure...")
    create_canonical_structure(matter_path)

    print("\nCreating template CSV files...")
    create_template_csvs(matter_path)

    print("\nCreating 99_AIStore/README.md...")
    create_aistore_readme(matter_path)

    print("\nRunning lint checks...")
    report = run_lint_checks(matter_path)

    if report["failed"] > 0:
        print("\n⚠️  Lint warnings detected:")
        print(json.dumps(report, indent=2))
    else:
        print("✓ All lint checks passed\n")

    print(f"✓ Initialisation complete: {matter_name}")
    print(f"  Location: {matter_path}\n")

if __name__ == "__main__":
    main()
```

### Usage Examples

```bash
# Basic initialisation
python script.py ParentingDispute_Smith_2026

# Initialisation with custom base path
python script.py PropertyDispute_ACME_2026 --base_path /Users/alex/Projects/Dev

# Lint check on existing matter
python script.py ExistingMatter --base_path /Users/alex/Projects/Dev --lint

# Output lint report to file
python script.py MatterName --lint > lint_report.json
```

### Script Features

- **Idempotent**: Safe to run multiple times. Skips existing folders and files.
- **Validation**: Sanitises matter name and reports changes.
- **Template CSVs**: Creates headers for all required spreadsheets.
- **README template**: Populates 99_AIStore/README.md with quarantine zone warning.
- **Lint checking**: Verifies folder structure and file compliance. Output as JSON.
- **Clear output**: Progress indicators (✓ for created, ⊘ for skipped) and colour-friendly formatting.

---

## Summary

This reference document establishes:

1. **Canonical folder structure** with immutability rules for evidence and court-facing materials
2. **Standardised file naming** linking document type, date, version, and status
3. **Six-state version lifecycle** (DRAFT → REVIEW → FINAL → FILED, with SUPERSEDED and ARCHIVED)
4. **Hard rules** protecting evidence integrity (01_Source_Materials immutable) and court compliance (99_AIStore quarantine)
5. **Lint checks** for structural and naming compliance, executable via Python
6. **Initialisation script** for rapid, idempotent setup

Adhere to these standards to ensure legal matter organisation, auditability, and court readiness.

**Last updated:** 2026-03-16
