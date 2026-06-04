# Legal Matter Operations Reference

All named operations for the `legal-matter-ops` skill. Use this guide to understand the purpose, inputs, actions, outputs, and time estimate for each operation.

---

## init_matter

**Purpose:** Initialise a new legal matter, create folder structure, set up registers.

**Inputs:**
- Matter name
- Court
- Parties
- Claim type
- Deadline

**Actions:**
1. Create matter root folder with YYYYMMDD_MatterName convention
2. Create standard subfolder structure (01_Source_Materials, 02_Evidence_Inventory, 03_Chronology, 04_Affidavit, 05_Disclosure, 06_Annexures_Exhibits, 07_Hearing_Prep, 08_Print_Bundle, 09_Review_Reports, 10_Meeting_Data, 90_Archive, 99_AIStore)
3. Create README.md with matter summary (parties, claim, deadline, practitioner)
4. Initialise registers:
   - chain_of_custody.csv (ID, Date In, Source, Custodian, File Name, Hash SHA-256, Status)
   - evidence_inventory.csv (EV-ID, Date, Description, Source, Classification, Working Copy Path)
   - classification_register.csv (EV-ID, Classification, Justification, Review Date)
5. Create project_checklist.md (phases 1–15 with checkboxes)
6. Record metadata file (matter_metadata.json with court, parties, claim type, deadline, creation date AWST)

**Outputs:**
- Matter folder created with standard structure
- Registers initialised and ready for data entry
- Project checklist ready
- Metadata file recorded

**Time estimate:** 30 minutes

---

## intake_evidence

**Purpose:** Receive materials, create chain of custody entries, hash originals.

**Inputs:**
- Raw materials (files, documents, recordings, etc.)
- Source information (how obtained, from whom)
- Custodian name and date

**Actions:**
1. Accept materials into 01_Source_Materials folder (immutable archive)
2. Hash each file using SHA-256; record hash value
3. Create chain of custody entry (ID, date, source, custodian, file name, hash, status)
4. Classify material (e.g. contemporaneous communication, medical, police, testimony-support)
5. Create working copies from originals (never modify originals)
6. Place working copies in appropriate working folder (02_Working_Files or subsection)
7. Record entry in evidence_inventory.csv with EV-ID, classification, working copy path

**Outputs:**
- Materials filed in 01_Source_Materials (immutable, read-only)
- Chain of custody updated
- Working copies placed and ready for analysis
- Evidence inventory updated with EV-IDs

**Time estimate:** 1–2 hours

---

## build_chronology

**Purpose:** Reconstruct timeline from evidence.

**Inputs:**
- Evidence inventory
- Narrative/message evidence (communications, notes, statements)
- Chronology template (master_chronology.csv)

**Actions:**
1. Extract all dated facts from evidence inventory
2. Populate master chronology CSV with: Date, Event, Source (EV-ID), Confidence (High/Medium/Low), Summary, Notes
3. Apply interpersonal hardening rules if applicable (relationship matters, DV, coercive control)
4. Identify contradictions between sources and document in contradiction_register.csv
5. Identify gaps in timeline and document in gap_analysis.md
6. Generate timeline summary (narrative form, with date range and key events highlighted)
7. Practitioner review and sign-off

**Outputs:**
- Master chronology CSV (03_Chronology/master_chronology.csv)
- Timeline summary markdown (03_Chronology/timeline_summary.md)
- Contradiction register (03_Chronology/contradiction_register.csv)
- Gap analysis (03_Chronology/gap_analysis.md)

**Time estimate:** 2–4 hours

---

## draft_affidavit

**Purpose:** Generate affidavit from chronology and claim support.

**Inputs:**
- Master chronology
- Claim support matrix (mapping claim elements to evidence)
- Affidavit template (court-standard format)
- Practitioner instructions

**Actions:**
1. Convert chronology into numbered paragraphs (10–15 words max per sentence)
2. Insert evidence references (EV-IDs and Bates numbers where applicable)
3. Add annexure section with exhibit list
4. Create verification clause (standard form for jurisdiction)
5. Embed confidence labels internally (High/Medium/Low) for practitioner review only
6. Save draft to 04_Affidavit/Drafts/DRAFT_v[N]_affidavit.docx
7. Generate markup/comment log for practitioner feedback
8. Practitioner review and sign-off

**Outputs:**
- Draft affidavit DOCX (04_Affidavit/Drafts/)
- Markup/comment log
- Practitioner sign-off document

**Time estimate:** 3–5 hours

---

## prepare_disclosure

**Purpose:** Build disclosure schedule, identify exhibits, prepare disclosed documents.

**Inputs:**
- Evidence inventory
- Affidavit draft
- Claim support matrix

**Actions:**
1. Create disclosure schedule CSV: Exhibit ID, Description, EV-ID, Page Count, Redacted Y/N, Redaction Reason
2. Identify all exhibits referenced in affidavit
3. Create exhibit index/coversheet (court-compliant format)
4. Copy/export documents to 05_Disclosure/Disclosed_Documents/
5. Apply redactions where justified (e.g. third-party PII, legal advice, privilege); log each redaction with reason
6. Create redaction_log.csv (Document, Page Range, Reason, Approved By, Date)
7. Create Bates pre-register (sequential numbering template, not yet applied)

**Outputs:**
- Disclosure schedule (05_Disclosure/disclosure_schedule.csv)
- Annexure index/coversheet
- Disclosed documents folder (05_Disclosure/Disclosed_Documents/)
- Redaction log
- Bates pre-register (sequential assignment ready for Phase 11)

**Time estimate:** 2–3 hours

---

## assign_bates

**Purpose:** Assign Bates numbers sequentially, update cross-references.

**Inputs:**
- Disclosure schedule
- Affidavit draft
- All documents for bundling

**Actions:**
1. Create Bates register CSV: Bates Number (format XXXXX, 5-digit padded), Document Name, Page Count, Start Page, End Page, Exhibit ID, Assigned Date
2. Assign sequential numbers starting 00001; increment by page count
3. Update affidavit with Bates references in margins/footnotes or reference list
4. Update disclosure schedule with Bates range per exhibit
5. Create Bates-stamped PDFs (stamp footer with Bates number on each page)
6. Verify no gaps, no duplicates, no page count mismatches
7. Practitioner sign-off on Bates register

**Outputs:**
- Bates register CSV (06_Exhibits/bates_register.csv)
- Updated affidavit with Bates refs (04_Affidavit/Drafts/DRAFT_v[N]_affidavit_bates.docx)
- Updated disclosure schedule with Bates ranges
- Bates-stamped PDFs (06_Exhibits/Bates_Stamped/)

**Time estimate:** 1–2 hours

---

## format_for_court

**Purpose:** Apply court-compliant formatting, validate print readiness.

**Inputs:**
- All documents from Phase 10 (affidavit, disclosure, exhibits)
- Court rules (WA, Federal, District, Local, etc.)

**Actions:**
1. Apply court formatting: A4 paper size, margins 25mm (top, bottom, left), 15mm (right), font 12pt Times New Roman or Calibri, 1.5 line spacing, 20mm header/footer for court details
2. Verify headings hierarchy (H1: Matter Name | H2: Section | H3: Subsection)
3. Ensure page numbering (bottom right)
4. Convert final DOCX to PDF (preserve hyperlinks, Bates numbers)
5. Print-test 10-page sample (check readability, Bates clarity, margin adequacy)
6. Validate Bates sequence on printout
7. Check court compliance checklist (page numbers, margins, font, spacing, signature blocks)
8. Create formatting_report.md (checklist results, any issues, sign-off)
9. Practitioner sign-off

**Outputs:**
- Formatted DOCX (04_Affidavit/Final/)
- Formatted PDF (04_Affidavit/Final/)
- Print test results (photo/scan of 10-page sample)
- Formatting report

**Time estimate:** 2–3 hours

---

## prepare_hearing

**Purpose:** Generate hearing scripts, issue notes, response prompts.

**Inputs:**
- Chronology
- Claim support matrix
- Affidavit
- Weakness register

**Actions:**
1. Generate opening script (2–3 min oral summary; include key claim elements and court relief sought)
2. Generate closing script (2–3 min oral summary; address key issues, remind court of evidence, restate claim)
3. Create issue notes (one per disputed element; note evidence for, evidence against, strength assessment)
4. Generate response prompts (if-then scenarios for common respondent arguments; suggested practitioner response)
5. Create examination-in-chief checklist (affidavit paragraph numbers with exhibit cross-refs; practitioner cues)
6. Create cross-examination brief (anticipated lines of attack; weaknesses to defend; evidence to reinforce)
7. Create key documents summary (one-page cheat sheet; top 5–10 documents with Bates, purpose, impact)
8. Practitioner review and sign-off

**Outputs:**
- Opening script (07_Hearing/opening_script.md)
- Closing script (07_Hearing/closing_script.md)
- Issue notes (07_Hearing/issue_notes.md)
- Response prompts (07_Hearing/response_prompts.md)
- Examination-in-chief checklist (07_Hearing/exam_in_chief_checklist.md)
- Cross-examination brief (07_Hearing/cross_exam_brief.md)
- Key documents summary (07_Hearing/key_docs_summary.md)

**Time estimate:** 3–4 hours

---

## adversarial_review

**Purpose:** Red-team all outputs, identify weaknesses.

**Inputs:**
- Affidavit
- Claim support matrix
- Weakness register
- Hearing scripts
- Evidence inventory

**Actions:**
1. Assign independent reviewer (not affidavit author)
2. Reviewer plays respondent's counsel; challenge every claim
3. Test affidavit credibility: scrutinise confidence labels, identify memory-based statements, flag unsourced allegations
4. Test claim support: check every claim element is evidenced in matrix
5. Test weakness register: confirm all vulnerabilities are identified; assess mitigation strength
6. Test hearing scripts: check for logical gaps, unsupported jumps, rhetorical overreach
7. Generate adversarial review report (Summary, Vulnerabilities, Risk Assessment, Mitigations)
8. Rank vulnerabilities by likelihood and court impact (High/Medium/Low)
9. Generate counter-argument framework (for each vulnerability: likely respondent argument, our counter-evidence, back-up position)
10. Practitioner reviews and approves mitigation strategy

**Outputs:**
- Adversarial review report (07_Hearing/adversarial_review_report.md)
- Vulnerability ranking (spreadsheet or markdown table)
- Counter-argument framework (07_Hearing/counter_arguments.md)
- Mitigation recommendations (07_Hearing/mitigations.md)
- Risk assessment summary

**Time estimate:** 3–5 hours

---

## freeze_bundle

**Purpose:** Lock final outputs, generate manifest, stage for print.

**Inputs:**
- All final documents (affidavit, disclosure, exhibits, Bates register)
- Print-ready PDFs
- Bates register (final)
- Final run report

**Actions:**
1. Move all final documents to 08_Print_Bundle/FINAL/ (read-only flag if possible)
2. Create bundle manifest (list all documents, page ranges, Bates ranges, exhibit order)
3. Create print order (specifications: paper size, weight, binding, page count, copies)
4. Archive all working drafts and interim versions to 90_Archive/ (with ARCHIVE_ prefix on filenames)
5. Create 99_AIStore/README.md (index of all AI-generated content; includes prompts, versions, confidence markers)
6. Create filing_checklist.md (pre-court filing verification: signatures, dates, court details, page count, Bates integrity)
7. Confirm all documents in 08_Print_Bundle are FROZEN (no further edits)
8. Rename key files with FILED_ prefix (e.g. FILED_affidavit.pdf, FILED_disclosure.pdf)
9. Practitioner final sign-off (sign-off sheet with date, signature, matter name, court name)
10. Generate completion summary for matter metadata

**Outputs:**
- Bundle in 08_Print_Bundle (read-only, FROZEN)
- Manifest (08_Print_Bundle/MANIFEST.md)
- Print order (08_Print_Bundle/PRINT_ORDER.txt)
- Archived drafts (90_Archive/)
- AIStore index (99_AIStore/README.md)
- Filing checklist (08_Print_Bundle/FILING_CHECKLIST.md)
- Practitioner sign-off sheet

**Time estimate:** 2–3 hours

---

## lint_matter

**Purpose:** Audit folder compliance, verify naming, check gates.

**Inputs:**
- Matter folder
- Naming convention standard
- Canonical folder structure
- Phase gates documentation

**Actions:**
1. Check folder structure against canonical (all 10 standard folders present: 01–08, 90, 99)
2. Verify file naming (YYYYMMDD_ prefix on time-stamped items, DRAFT_v[N], FILED_ prefix on finals)
3. Verify status tags on all files (DRAFT, IN_REVIEW, APPROVED, FILED, ARCHIVED)
4. Check 01_Source_Materials is immutable (read-only permissions, no deletions)
5. Check chain_of_custody.csv completeness (all files have entry, hash, custodian, date)
6. Check evidence_inventory.csv (all EV-IDs assigned, no gaps, all entries have classification)
7. Check Bates register (sequential numbering, no gaps, all page counts match)
8. Check privilege log if applicable (all privileged items documented with reason)
9. Check phase gates (confirm each phase is marked complete before next phase begun)
10. Check 99_AIStore segregation (all AI-generated content indexed, separate from human work)
11. Generate lint report: structure issues, naming issues, missing registrations, gate violations
12. Propose fixes for each issue

**Outputs:**
- Lint report (LINT_REPORT.md with all findings)
- Naming fixes (list of files to rename with before/after)
- Folder structure fixes (list of missing folders or misplaced files)
- Gate compliance summary (which phases are locked, which are in progress)

**Time estimate:** 1–2 hours

---

## Meeting Data Management

### Meeting Notes Creation and Storage

**Standard location:** `/02_Working_Files/meeting_notes/`

**Naming convention:** `YYYYMMDD_MeetingType_Participants.md`
- Example: `20260316_CallWithPractitioner_Alex_Counsel.md`

**Standard structure:**
```
# Meeting Notes — [Matter Name]

**Date:** YYYY-MM-DD (AWST)
**Participants:** [Names and roles]
**Purpose:** [One-line summary]

## Agenda
- [Item 1]
- [Item 2]

## Discussion Summary
[Key points, decisions, context]

## Decisions Made
- [Decision 1 — Rationale]
- [Decision 2 — Rationale]

## Action Items
[See separate action register below]

## Next Steps
[When next meeting/review scheduled]
```

**Recording and archiving:**
- All notes finalised and reviewed within 24 hours of meeting
- Shared with all participants for confirmation
- Archived to `/02_Working_Files/meeting_notes/` with APPROVED_ prefix once confirmed

---

### Action Items Register

**Standard location:** `/02_Working_Files/action_items.csv`

**Format:**
```
AI-ID,Date Assigned,Owner,Description,Due Date,Status,Evidence/Completion Notes,Assigned By
AI-001,2026-03-16,Alex,Review affidavit draft v1,2026-03-18,In Progress,Feedback due to practitioner,Counsel
AI-002,2026-03-16,Practitioner,Approve chain of custody entries,2026-03-17,Pending,Awaiting signature,Alex
```

**Fields:**
- **AI-ID:** Sequential identifier (AI-001, AI-002, etc.)
- **Date Assigned:** YYYY-MM-DD AWST
- **Owner:** Name of responsible person
- **Description:** Action in imperative form ("Review...", "Approve...", "Prepare...")
- **Due Date:** YYYY-MM-DD AWST
- **Status:** Pending / In Progress / Completed / On Hold / Cancelled
- **Evidence/Completion Notes:** How completion was evidenced (e.g. "Email confirmation", "File updated", "Signature obtained")
- **Assigned By:** Who tasked this action

**Update frequency:** After each meeting; reviewed at start of next meeting

---

### Reporting Obligations

**Mandatory reporting register:** `/02_Working_Files/reporting_obligations.csv`

**Format:**
```
RO-ID,Date Identified,Obligation Type,Trigger,Details,Recipient,Deadline,Status,Submitted By,Evidence
RO-001,2026-03-16,Court Document Filing,Affidavit Ready,Lodge affidavit with court,District Court WA,2026-03-25,Pending,Practitioner,Court filing receipt
RO-002,2026-03-16,Mandatory Reporting,Disclosure Reveals Child Safety Risk,Notify DFES,Department for Child Safety,2026-03-17,Completed,Alex,Report number: MR-1234
```

**Fields:**
- **RO-ID:** Sequential identifier (RO-001, RO-002, etc.)
- **Date Identified:** When obligation discovered
- **Obligation Type:** Court filing, Mandatory reporting, Privilege disclosure, Professional conduct, Other
- **Trigger:** What event/content triggered the obligation
- **Details:** Full description of the obligation
- **Recipient:** Who must receive report/notice (court, agency, counsel, etc.)
- **Deadline:** YYYY-MM-DD AWST
- **Status:** Pending / Submitted / Completed / Escalated
- **Submitted By:** Who discharged the obligation
- **Evidence:** Document/receipt number, email confirmation, or reference to proof file

**Review schedule:**
- Initial scan: at intake_evidence (Phase 2) and build_chronology (Phase 6)
- Pre-hearing: at prepare_hearing (Phase 13)
- Pre-bundle: at freeze_bundle (Phase 15)

---

### Recordings and Transcripts

**Consent requirements (Western Australia):**
- Audio and video recordings of meetings/calls require consent from all participants before recording begins
- Obtain written consent via email or meeting minutes confirmation
- Store consent evidence in `/02_Working_Files/consents/` with filename `YYYYMMDD_RecordingConsent_Participants.txt`

**Storage standard:**
- Audio files: `/02_Working_Files/recordings/audio/` (MP3 or WAV, clearly labelled)
- Video files: `/02_Working_Files/recordings/video/` (MP4, clearly labelled)
- Transcripts: `/02_Working_Files/transcripts/` (markdown or plain text, linked to source recording)

**Naming convention:**
- `YYYYMMDD_[Subject]_[Participant1]_[Participant2].ext`
- Example: `20260316_TelephoneCallWithCounsel_Alex_JSmith.mp3`

**Transcription format (if using AI transcription service):**
```
# Transcript — [Matter Name]

**Recording:** [Filename and date AWST]
**Duration:** [HH:MM]
**Participants:** [Names]
**Transcriber:** [Human/AI service]
**Confidence:** [High/Medium/Low]

## Transcript

[Timestamp] Speaker: "Quoted text..."
[Timestamp] Speaker: "Quoted text..."

## Accuracy Notes
- Any unclear passages flagged [UNCLEAR]
- Any inaudible sections marked [INAUDIBLE]
- Any names/terms requiring verification noted [VERIFY: ...]

## Action Items Extracted
- [Item 1]
- [Item 2]
```

**Archiving:**
- Transcripts reviewed and approved by original participants within 5 working days
- Recordings older than 12 months moved to 90_Archive/ (retain indefinitely for litigation support)
- Destroy recordings only with practitioner written consent and matter completion

