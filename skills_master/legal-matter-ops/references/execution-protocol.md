# Legal Matter Operations Protocol: Execution Phases

**Full Specifications for All 15 Phases**

---

## Table of Contents

1. [INTAKE](#phase-1-intake)
2. [FILE CLASSIFICATION](#phase-2-file-classification)
3. [LEGAL FOLDER PLACEMENT](#phase-3-legal-folder-placement)
4. [CHAIN OF CUSTODY ENTRY](#phase-4-chain-of-custody-entry)
5. [EVIDENCE INVENTORY](#phase-5-evidence-inventory)
6. [CHRONOLOGY RECONSTRUCTION](#phase-6-chronology-reconstruction)
7. [CLAIM SUPPORT MAPPING](#phase-7-claim-support-mapping)
8. [DRAFTING](#phase-8-drafting)
9. [DISCLOSURE / EXHIBIT ASSEMBLY](#phase-9-disclosure--exhibit-assembly)
10. [BATES ASSIGNMENT](#phase-10-bates-assignment)
11. [FORMATTING & PRINT VALIDATION](#phase-11-formatting--print-validation)
12. [HEARING PREP](#phase-12-hearing-prep)
13. [ADVERSARIAL REVIEW](#phase-13-adversarial-review)
14. [FINAL RUN REPORT](#phase-14-final-run-report)
15. [BUNDLE FREEZE](#phase-15-bundle-freeze)

---

## Phase 1: INTAKE

**Purpose:** Receive materials, create chain of custody entries, baseline hash originals.

**Inputs:**
- Raw materials (documents, photos, messages, media, emails, spreadsheets)
- Client briefing on matter scope

**Actions:**

1. Create matter folder structure (see folder-naming-versioning.md)
2. Create chain of custody log (CSV template from templates.md)
3. Accept materials into 01_Source_Materials
4. For each file: record filename, hash (SHA-256), date received, source, custodian, file type
5. Do not modify any source file
6. Create evidence inventory skeleton

**Outputs:**
- Matter folder initialised
- Chain of custody log with baseline entries
- Hashed materials
- Hash register

**Gate (before Phase 2):**
- [ ] All source files hashed and logged
- [ ] No modifications to originals
- [ ] Matter folder structure complete
- [ ] Client confirms scope and parties

---

## Phase 2: FILE CLASSIFICATION

**Purpose:** Identify document types, assign tags, identify privileged material.

**Inputs:**
- All files from 01_Source_Materials
- Matter scope and legal issues

**Actions:**

1. Classify each file according to:
   - Document type (Affidavit, Email, SMS, Photo, Financial, Order, Legal Letter, Meeting Note, etc.)
   - Source category (Client, Respondent, Third Party, Court, Police, Medical)
   - Format
   - Privilege claim
   - Confidentiality
   - Legal relevance
   - Evidence strength

2. Flag duplicate or near-duplicate files (hash comparison, content similarity)
3. Flag missing metadata
4. Create classification register (CSV) in 02_Evidence_Inventory

**Outputs:**
- Classification register
- Privilege log (separate, confidential)
- Duplicates flagged

**Gate (before Phase 3):**
- [ ] All files classified
- [ ] Privilege claims assessed
- [ ] No privileged material in working folders
- [ ] Classification register complete

---

## Phase 3: LEGAL FOLDER PLACEMENT

**Purpose:** Route classified files to canonical working folders, maintain source originals intact.

**Inputs:**
- Classified file register
- Source materials in 01_Source_Materials

**Actions:**

1. For each classified file, copy to appropriate working folder:
   - Affidavit-related → 04_Affidavit/Drafts
   - Narrative/messages → chronology working folder
   - Financial/disclosure → 05_Disclosure or 06_Annexures_Exhibits
   - All copies are duplicates; originals remain immutable

2. Add header comment to working copies: "Source: [filename], Hash: [SHA-256], Copied: [date], DO NOT FILE THIS VERSION"
3. Create traceability links from working folders back to source
4. Do not delete or move originals

**Outputs:**
- Classified materials in working folders
- 01_Source_Materials unchanged
- Traceability links
- Working copies marked non-court-facing

**Gate (before Phase 4):**
- [ ] All materials placed
- [ ] Source originals untouched
- [ ] Traceability created
- [ ] No privileged material in working folders

---

## Phase 4: CHAIN OF CUSTODY ENTRY

**Purpose:** Log every file movement with provenance metadata.

**Inputs:**
- All files (source and working copies)
- Classification metadata

**Actions:**

1. Update chain of custody log with: original hash, filename, location, date received/created, source, custodian, format, file size, current location, handling notes, privilege claim
2. For duplicates/near-duplicates, log relationship
3. For unhashable files (live emails, voice recordings), note alternative verification
4. Create custody assignment matrix

**Outputs:**
- Comprehensive chain of custody log
- Custody assignment matrix
- Audit trail

**Gate (before Phase 5):**
- [ ] Every file has custody entry
- [ ] No gaps or undocumented movements
- [ ] Custody assignments clear
- [ ] Practitioner confirms integrity

---

## Phase 5: EVIDENCE INVENTORY

**Purpose:** Build structured evidence index with IDs, metadata, strength, and source.

**Inputs:**
- All classified and placed files (Phases 1–4)
- Matter scope and legal issues

**Actions:**

1. Create evidence inventory (CSV, template from templates.md) with fields:
   - Evidence ID (EV-001, EV-002, etc.)
   - Filename
   - Type/format
   - Date
   - Source/custodian
   - Description
   - Legal relevance
   - Evidence strength (DIRECT/CORROBORATIVE/CIRCUMSTANTIAL/HEARSAY/OPINION/UNCORROBORATED)
   - Admissibility notes
   - Privilege claim
   - Confidence label (HIGH/MEDIUM/LOW/UNCERTAIN)
   - Risk flags
   - Linked to claim support
   - Bates assigned

2. Cross-reference with chain of custody
3. Identify gaps: missing documents, unexplained absences, inconsistencies
4. Generate summary statistics

**Outputs:**
- Evidence inventory CSV
- Gap analysis
- Evidence strength distribution
- Risk flag summary

**Gate (before Phase 6):**
- [ ] All evidence catalogued with IDs
- [ ] Confidence and risk labels assigned
- [ ] Gaps identified
- [ ] Inventory reviewed

---

## Phase 6: CHRONOLOGY RECONSTRUCTION

**Purpose:** Build factual timeline from evidence, distinguish fact from inference.

**Inputs:**
- Evidence inventory
- All narrative and message evidence
- Affidavits/statements
- Photos with metadata

**Actions:**

1. Extract all dated facts from evidence (messages, emails, photos, affidavits, financial records, call/meeting notes)
2. Build master chronology CSV with columns: Date, Time, Event, Evidence ID, Confidence, Category, Source, Notes
3. For relationship/family law matters: apply Interpersonal Matter Hardening rules (see references/interpersonal-hardening.md):
   - Separate background from incident facts
   - Reduce emotional narrative
   - Distinguish fact from interpretation
   - Identify patterns only if supported by multiple instances
   - Mark memory-based statements LOW confidence
4. Identify contradictions, gaps, inconsistencies
5. Generate timeline summary (markdown narrative, 2–5 pages, readable by magistrate)

**Outputs:**
- Master chronology CSV
- Timeline summary
- Contradiction register
- Gap analysis

**Gate (before Phase 7):**
- [ ] All dated facts extracted and sequenced
- [ ] Confidence levels assigned
- [ ] Contradictions identified
- [ ] Chronology reviewed

---

## Phase 7: CLAIM SUPPORT MAPPING

**Purpose:** Map evidence to legal elements and issues, identify unsupported claims.

**Inputs:**
- Master chronology
- Evidence inventory
- Legal elements and issues (from practitioner)

**Actions:**

1. Define legal framework (elements of claim, grounds, required evidence)
2. Create claim support matrix CSV with columns: Legal element, Required evidence type, Supporting evidence (EV-IDs), Strength, Confidence, Risk flags, Weaknesses, Notes
3. For each element:
   - Identify supporting evidence
   - Identify gaps
   - Flag elements with only circumstantial/memory support
   - Flag contradictions
4. Identify unsupported or weakly supported elements
5. Recommend evidence collection or expert opinion to strengthen

**Outputs:**
- Claim support matrix
- Element strength summary
- Weakness register
- Evidence gap analysis

**Gate (before Phase 8):**
- [ ] All elements mapped
- [ ] Weaknesses identified
- [ ] Gaps documented
- [ ] Practitioner confirms assessment

---

## Phase 8: DRAFTING

**Purpose:** Generate affidavit, submissions, or response documents from chronology and claim support.

**Inputs:**
- Master chronology
- Claim support matrix
- Affidavit template
- Practitioner instructions

**Actions:**

1. Generate affidavit:
   - Convert chronology to numbered paragraphs
   - Reference evidence (EV-IDs)
   - Paragraph 1: affirm identity
   - Body: chronological narrative
   - Annexures section with exhibit list
   - Final paragraph: confirmation of truth
   - Use factual language

2. Draft submissions if required:
   - Legal framework
   - Issue-by-issue analysis
   - Counter to objections
   - Relief sought

3. For response documents: mirror applicant structure, point-by-point
4. Save to 04_Affidavit/Drafts with version control
5. Embed confidence labels and risk flags as footnotes for practitioner review (not for filing)
6. Create audit trail of draft versions

**Outputs:**
- Draft affidavit(s) (DOCX)
- Draft submissions
- Markup and comment log
- Audit trail

**Gate (before Phase 9):**
- [ ] All drafts reviewed by practitioner
- [ ] Factual accuracy confirmed
- [ ] Labels removed from final
- [ ] Practitioner sign-off

---

## Phase 9: DISCLOSURE / EXHIBIT ASSEMBLY

**Purpose:** Prepare disclosure schedule, annexures, exhibits for service.

**Inputs:**
- Evidence inventory
- Affidavit drafts
- Claim support matrix
- Disclosure obligations

**Actions:**

1. Create disclosure schedule CSV with columns: Document ID (D-001, D-002, etc.), Evidence ID, Filename, Date, Description, Category, Relevance, Privilege claim, Already produced, Notes
2. Identify exhibits for annexure, link to affidavit paragraphs, assign exhibit letters
3. Copy files to 05_Disclosure/Disclosed_Documents:
   - Maintain chain of custody
   - Redact only if legally justified with reason logged
4. Create exhibit index and annexure coversheet
5. Prepare Bates pre-registers

**Outputs:**
- Disclosure schedule
- Annexure index/coversheet
- Disclosed documents folder
- Redaction log
- Bates pre-register

**Gate (before Phase 10):**
- [ ] All exhibits identified and indexed
- [ ] Disclosure complete
- [ ] No privilege leakage
- [ ] Redactions justified
- [ ] Practitioner approves

---

## Phase 10: BATES ASSIGNMENT

**Purpose:** Assign sequential Bates numbers, update cross-references.

**Inputs:**
- Disclosure schedule
- Affidavit draft
- All documents for bundling

**Actions:**

1. Create Bates register (CSV) with columns: Bates number (00001, padded 5 digits), Evidence ID, Filename, Type/description, Date, Page count, Exhibit letter, Affidavit paragraph refs, Bundle folder, Notes
2. Assign in sequence:
   - Disclosed documents first
   - Then affidavit/submissions
   - Then procedural docs
3. Update affidavit: convert exhibit refs to Bates ranges
4. Update disclosure schedule with Bates numbers
5. Create Bates-stamped PDF versions in 06_Annexures_Exhibits and 08_Print_Bundle

**Outputs:**
- Bates register
- Bates summary chart
- Updated affidavit
- Updated disclosure schedule
- Bates-stamped PDFs

**Gate (before Phase 11):**
- [ ] All documents numbered sequentially
- [ ] No gaps or duplicates
- [ ] Cross-refs updated
- [ ] Register verified

---

## Phase 11: FORMATTING & PRINT VALIDATION

**Purpose:** Apply court-compliant formatting, validate print readiness.

**Inputs:**
- All documents from Phase 10
- Court rules
- Bates-stamped versions

**Actions:**

1. Apply formatting standards:
   - A4 single-sided
   - Margins: top 40 mm, bottom 20 mm, left 25 mm, right 20 mm
   - Times New Roman 12 pt body, 14 pt headings
   - 1.5 line spacing affidavit, 1.0 exhibits
   - Consistent heading numbering
   - Footers: "Page X of Y" + Bates
   - Header: matter name/court/year
   - Black & white safe
   - Stable pagination

2. Print-test 10-page sample (confirm readability, Bates, page breaks)
3. Court compliance check (title page, caption, verification language)
4. Create formatting report
5. Convert DOCX to PDF (searchable, embedded fonts, Bates embedded not images)
6. Save final versions to 08_Print_Bundle with FINAL status

**Outputs:**
- Formatted DOCX
- Print-ready PDFs
- Formatting report
- Print test results

**Gate (before Phase 12):**
- [ ] All docs court-formatted
- [ ] Print test passed
- [ ] PDF validated
- [ ] Bates verified
- [ ] Practitioner approves

---

## Phase 12: HEARING PREP

**Purpose:** Generate hearing scripts, issue notes, response prompts.

**Inputs:**
- Master chronology
- Claim support matrix
- Affidavit
- Weakness register
- Court rules

**Actions:**

1. Generate hearing scripts:
   - Opening (2–3 minutes)
   - Issue-by-issue narrative (5–10 minutes)
   - Evidence summary (2–3 pages)
   - Closing (2–3 minutes)

2. Create issue notes (one-pager per issue):
   - Issue statement
   - Supporting evidence (Bates refs)
   - Anticipated objection
   - Response strategy
   - Case law

3. Generate response prompts:
   - Likely magistrate questions
   - Cross-examination points
   - Response frameworks
   - Affidavit paragraphs to reference

4. Examination-in-chief checklist
5. Cross-examination brief:
   - Anticipated hostile questions
   - Concede vs defend
   - Evidence to stand on

6. Key documents summary sheet (one-page summaries of 5–10 most important docs)
7. Save to 07_Hearing_Prep

**Outputs:**
- Hearing scripts
- Issue notes
- Response prompts
- Examination checklist
- Cross-exam brief
- Key docs summary

**Gate (before Phase 13):**
- [ ] All scripts generated and reviewed
- [ ] Response prompts stress-tested
- [ ] Practitioner confident
- [ ] Hearing date confirmed

---

## Phase 13: ADVERSARIAL REVIEW

**Purpose:** Red-team all outputs, identify weaknesses, test robustness.

**Inputs:**
- Affidavit
- Claim support matrix
- Weakness register
- Hearing scripts
- Evidence inventory

**Actions:**

1. Play respondent's counsel:
   - Best argument against each element?
   - What evidence is weak/uncorroborated/memory-only?
   - What contradictions/gaps can be exploited?
   - What hearsay risks?
   - What admissibility objections?

2. Test affidavit credibility:
   - Fact vs inference distinct?
   - Emotion minimised?
   - Chain of custody intact?
   - Credible to magistrate?

3. Test claim support:
   - Direct evidence or only circumstantial?
   - Logical gap between evidence and conclusion?
   - Competing inferences?

4. Test weakness register:
   - Fatal or manageable?
   - Addressable in oral evidence?
   - Corroborating evidence available?

5. Generate adversarial review report:
   - Element-by-element strength
   - Ranked vulnerabilities (critical/significant/minor)
   - Mitigation recommendations
   - Honest winnable assessment

6. Generate counter-argument framework per issue

**Outputs:**
- Adversarial review report (3–5 pages)
- Vulnerability ranking
- Counter-argument framework
- Mitigation recommendations
- Risk assessment

**Gate (before Phase 14):**
- [ ] Review by independent reviewer (not drafter)
- [ ] Vulnerabilities acknowledged
- [ ] Practitioner reviews and agrees
- [ ] Mitigation confirmed

---

## Phase 14: FINAL RUN REPORT

**Purpose:** Completeness check, confidence summary, risk flags, readiness sign-off.

**Inputs:**
- All outputs from Phases 1–13
- Practitioner feedback

**Actions:**

1. Generate final run report with sections:
   - Executive summary (confidence HIGH/MEDIUM/LOW)
   - Phase completion checklist
   - Evidence summary
   - Chronology summary
   - Claim support summary
   - Affidavit status
   - Disclosure status
   - Hearing prep status
   - Risk flags
   - Weaknesses summary
   - Outstanding items
   - Recommended next steps
   - Practitioner approval

2. Create confidence matrix per legal element
3. Create risk register (severity and status: active/mitigated/accepted)
4. Compile appendices:
   - Evidence summary
   - Chain of custody verification
   - Bates verification
   - Document count

**Outputs:**
- Final run report (5–10 pages)
- Confidence matrix
- Risk register
- Appendices

**Gate (before Phase 15):**
- [ ] All phases complete
- [ ] No critical blockers
- [ ] Practitioner confirms readiness
- [ ] Report approved

---

## Phase 15: BUNDLE FREEZE

**Purpose:** Lock final outputs, generate manifest, stage for print and filing.

**Inputs:**
- All final documents
- Print-ready PDFs
- Bates register
- Hearing prep

**Actions:**

1. Move final outputs to 08_Print_Bundle (affidavit, submissions, exhibits, orders, manifest)
2. Create bundle manifest with:
   - Matter details
   - Date frozen
   - Document list with Bates/page count/status
   - Total pages
   - Print order
   - Distribution list

3. Create print order:
   - Affidavit first
   - Exhibits in Bates order
   - Submissions last

4. Archive working drafts to 90_Archive (tag SUPERSEDED)
5. Create 99_AIStore README warning
6. Print readiness confirmation (test print, Bates, legibility)
7. Create filing checklist:
   - Court fee
   - Forms
   - Affidavit
   - Submissions
   - Exhibits
   - Disclosure
   - Service confirmation

8. Lock bundle: rename all to FILED status, no further modifications

**Outputs:**
- Final bundle in 08_Print_Bundle
- Bundle manifest
- Print order
- Filing checklist
- Archived working drafts

**Gate (before filing/service):**
- [ ] All docs FILED status
- [ ] Manifest complete
- [ ] Print test passed
- [ ] No modifications after freeze
- [ ] Archive and AIStore segregated

---

## End of Execution Protocol

**Maintenance note:** Verify deadlines, court rules, filing channels, and source-control practices against the current matter before execution.
