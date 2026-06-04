# Legal Matter Operations — Multi-Agent System Architecture

**Document Version:** 1.0
**Maintenance note:** Verify this workflow against current court rules, local practice directions, and active project tooling before use.
**Scope:** Affidavit preparation, evidence management, court filing, hearing preparation
**Audience:** Practitioners, systems integrators, AI orchestration engineers

---

## Overview

This document defines a 10-agent system for managing legal matters from evidence intake through hearing preparation. Each agent owns a discrete operational domain, publishes validation outputs, escalates decision points, and hands off work via a standardised protocol. The system prioritises factual discipline, privilege protection, chain of custody integrity, and court compliance.

---

## Agent Definitions

### 1. Intake & Evidence Triage Agent

**Role:** First contact for all incoming evidence and materials.

**Responsibilities**
- Receive materials from any source format (CSV, PDF, DOCX, images, screenshots, message exports, audio transcripts, email threads)
- Compute SHA-256 hash of every file; record in registry
- Classify document type using file extension, content metadata, and manual specification
- Detect and flag duplicate files (hash match or strong content similarity)
- Create chain of custody entry for each unique file (hash, date received, source, receiver)
- Route classified files to appropriate working folders within `/working/` (messages, documents, images, other)
- Flag files with missing or incomplete metadata

**Inputs**
- Raw file submissions (any format)
- Source metadata (sender, date, context annotation)
- Classification rules (document type mapping)

**Outputs**
- `hashed-file-registry.csv`: hash, filename, class, received-date, source, receiver
- `chain-of-custody.log`: structured entries for each unique file
- `classified-file-inventory.csv`: inventory of all files by classification, with paths
- `duplicate-report.csv`: flagged duplicates with hash matches and confidence score

**Validation Checkpoints**
- [ ] All files hashed and hash recorded in registry
- [ ] All files assigned to a classification
- [ ] No files remain in intake folder after routing
- [ ] Chain of custody entry created for every unique file
- [ ] Duplicate flagging performed and documented

**Escalation Triggers**
- Unknown file format (no classification possible)
- Suspected file corruption (read errors, hash check failure)
- Missing critical metadata (no source, date unclear, submission context unknown)
- Potential privilege material detected (attorney-client communications, work product, legal advice)
- Metadata conflicts (e.g., multiple inconsistent file dates)

**Confidence & Risk Labelling**
- Risk: Mark potential privilege material as **CRITICAL** with reason
- Confidence: Mark classification as HIGH/MEDIUM/LOW based on certainty of file type

---

### 2. Legal File Management Agent

**Role:** Enforce folder structure, naming, versioning, and prevent contamination.

**Responsibilities**
- Validate folder structure compliance against defined schema (working folders, draft, final, archive)
- Enforce file naming conventions: `[AABBCCDD]_[description]_[version].[ext]` where `AABBCCDD` is 8-char code (matter ID + sequence)
- Manage version lifecycle: draft → review → final → archive
- Detect and report stale drafts (not modified in 14+ days)
- Ensure AIStore outputs are segregated in `/draft/aistore/` and never copied into `/final/` without human review
- Prevent folder sprawl: flag orphaned folders or non-standard structures
- Archive superseded versions: move to `/archive/` with timestamp prefix
- Maintain version register: track all versions of each document with author, timestamp, change summary
- Detect naming conflicts: flag duplicate or ambiguous file names

**Inputs**
- Current folder state (directory tree)
- File operation requests (create, move, rename, delete)
- Naming schema definition

**Outputs**
- Folder compliance lint report (pass/fail per structural rule)
- Rename suggestions (with before/after examples)
- Archive action log (files moved to archive with timestamp)
- Version register CSV (filename, version, author, timestamp, change summary)
- Contamination audit: confirm no AIStore files in court-facing folders

**Validation Checkpoints**
- [ ] Folder structure matches schema
- [ ] All files follow naming convention or are flagged with fix
- [ ] Versions tracked in register
- [ ] No AIStore output in `/final/` folder
- [ ] Archive retention policy respected (superseded versions > 7 days old archived)

**Escalation Triggers**
- Naming conflict (two files would have same name after normalisation)
- Version confusion (multiple versions with unclear precedence)
- Immutability violation (final file modified after archival policy date)
- Orphaned folder (folder with no current purpose or owner)
- AIStore contamination detected (draft output in court-facing location)

**Confidence & Risk Labelling**
- Risk: Mark immutability violations as **CRITICAL**
- Risk: Mark AIStore contamination as **CRITICAL**
- Confidence: Mark compliance as PASS/FAIL only (binary assessment)

---

### 3. Chronology Agent

**Role:** Extract and structure timeline from evidence.

**Responsibilities**
- Parse evidence inventory; extract dates, events, and actors from all source documents
- Build master chronology in CSV format: date, time (if available), event, source document, source page/para, confidence, evidence strength, interpretation flag
- Identify gaps: date ranges with no documented events; missing evidence between key dates
- Flag contradictions: conflicting event dates, inconsistent actor roles, disputed facts
- Separate fact from interpretation: mark subjective characterisations separately from objective event records
- Distinguish documented events from recollection: flag statements like "I recall…" vs. contemporaneous records
- Cross-reference all events to source documents (with page/paragraph)
- Assign confidence labels (HIGH, MEDIUM, LOW, UNCERTAIN) based on evidence quality

**Inputs**
- Evidence inventory (file paths, types, hashes)
- Source documents (PDFs, message exports, transcripts, emails)
- Existing timelines (if any) for consolidation
- Matter context (parties, dispute type, relevant period)

**Outputs**
- `master-chronology.csv`: date, time, event, source-file, source-reference, actor, confidence, evidence-strength, fact-vs-interpretation
- `timeline-summary.md`: narrative summary of key events in sequence
- `gap-report.csv`: identified gaps (date range, duration, missing context)
- `contradiction-log.csv`: conflicting accounts with source documents and flag severity

**Validation Checkpoints**
- [ ] Every event sourced to at least one document
- [ ] Confidence labels assigned to every event
- [ ] Fact/interpretation flags completed
- [ ] No unsourced assertions in summary
- [ ] All contradictions logged with sources
- [ ] Gaps identified with date ranges

**Escalation Triggers**
- Major timeline gap (no documented events for > 30 days in critical period)
- Contradictory evidence (two sources with materially conflicting dates/facts)
- Disputed fact (core claim supported by only one source or recollection only)
- Credibility risk (witness recollection conflicts with contemporaneous record)
- Temporal impossibility (event dates create logical conflict)

**Confidence & Risk Labelling**
- Confidence: HIGH (contemporaneous doc, multiple corroboration), MEDIUM (single doc, clear evidence), LOW (recollection only), UNCERTAIN (conflicting sources)
- Risk: Mark contradictions as HIGH/CRITICAL
- Evidence Strength: Use DIRECT_EVIDENCE, CORROBORATIVE, CIRCUMSTANTIAL, HEARSAY, OPINION, UNCORROBORATED

---

### 4. Affidavit Drafting Agent

**Role:** Transform chronology and evidence into sworn statement.

**Responsibilities**
- Generate affidavit DOCX from master chronology, evidence inventory, and matter context
- Maintain factual discipline: every assertion sourced, no speculation, no emotional language
- Structure affidavit: header (deponent name, date, swearing formula), numbered paragraphs, annexures
- Number paragraphs sequentially; link each to source evidence via internal reference
- Create annexure reference list: para X refers to Annexure Y (exhibit identifier)
- Generate verification statement (deponent confirms truth of statements)
- Ensure proper legal language (past tense, third person where appropriate, formal style)
- Flag unsupported claims for review
- Cross-reference with claim support matrix: every material claim linked to supporting evidence

**Inputs**
- Master chronology (CSV)
- Evidence inventory (file paths, types, hashes)
- Claim support matrix (claim → supporting evidence mapping)
- Matter context (deponent role, dispute type, relief sought)
- Deponent details (name, relationship to matter, capacity)

**Outputs**
- `affidavit-draft.docx`: numbered paragraphs, annexure references, verification statement
- `annexure-reference-list.csv`: paragraph → annexure mapping, with exhibit identifiers
- `verification-statement.docx`: standard sworn statement (deponent to sign)
- `sourcing-audit.csv`: every material assertion, source document, confidence level

**Validation Checkpoints**
- [ ] Every factual assertion sourced in sourcing audit
- [ ] No speculation, hedging language, or opinion (unless expert witness)
- [ ] No emotional or argumentative language
- [ ] Paragraph numbering sequential
- [ ] Annexures referenced with correct identifiers
- [ ] Deponent capacity and authority clear
- [ ] Verification statement complete and ready for swearing

**Escalation Triggers**
- Unsupported claim (assertion with no source document or weak evidence)
- Evidence gap (claim material to dispute but no supporting evidence found)
- Contradiction between chronology and affidavit draft
- Privilege issue (affidavit references legal advice, attorney communication)
- Credibility concern (reliance on recollection only for material fact)
- Deponent capacity unclear or disputed

**Confidence & Risk Labelling**
- Confidence: Per evidence strength (HIGH for direct evidence, LOW for recollection)
- Risk: Mark unsupported claims as HIGH/CRITICAL
- Risk: Mark privilege references as CRITICAL

---

### 5. Disclosure & Bundle Agent

**Role:** Prepare court-compliant disclosure and exhibit bundles.

**Responsibilities**
- Build disclosure schedule in court-compliant format: document ID, description, date, relevance, status (produced/withheld/privileged)
- Prepare annexures and exhibits for submission: collect, order, paginate, cross-reference
- Assemble document bundles per court requirements (single PDF with book marks, or separated exhibits)
- Manage bundle segregation: confidential vs. public, separate bundles for different parties if required
- Index all disclosed items: map to affidavit paragraphs, chronology entries, Bates numbers (if Bates-stamped)
- Identify privilege documents and create privilege log (description, date, parties, privilege basis, withheld reason)
- Validate complete traceability: every disclosed item maps to originating evidence file

**Inputs**
- Evidence inventory (with hashes and classifications)
- Affidavit draft (for annexure references)
- Disclosure requirements (court rules, discovery orders)
- Privilege assessment (privileged documents and rationale)

**Outputs**
- `disclosure-schedule.csv`: doc-id, description, date, relevance, status, privilege-basis-if-applicable
- `privilege-log.csv`: description, date, parties, privilege-type, withholding-reason
- `annexure-index.csv`: annexure-id, source-file, description, pages, affidavit-reference
- `bundle-structure.md`: bundle composition, exhibit order, cross-reference map
- Prepared exhibit files (PDFs, properly ordered and indexed)

**Validation Checkpoints**
- [ ] All disclosed items in schedule traceable to source evidence
- [ ] No privilege material disclosed (unless waived)
- [ ] Cross-references complete and accurate (affidavit para → exhibit)
- [ ] Bundle structure matches court requirements
- [ ] Exhibit indices match actual document order
- [ ] Confidentiality markings (if required) applied consistently

**Escalation Triggers**
- Privilege uncertainty (document with arguable privilege status)
- Incomplete evidence (claim in affidavit but supporting exhibit not in inventory)
- Missing documents (referenced in affidavit or chronology but not found)
- Disclosure conflict (court orders seem to require disclosure of privileged material)
- Indexing mismatch (affidavit references exhibit that doesn't exist or is mislabelled)

**Confidence & Risk Labelling**
- Confidence: Mark privilege assessments as HIGH/MEDIUM/LOW based on clarity
- Risk: Mark privilege uncertainty as HIGH/CRITICAL
- Risk: Mark incomplete evidence as HIGH

---

### 6. Formatting & Court Compliance Agent

**Role:** Ensure documents meet court filing standards.

**Responsibilities**
- Apply court-compliant formatting to all documents (DOCX and PDF)
- Validate A4 page size, margins (default 25mm or per court rules), line spacing (1.5 or 2.0 as required)
- Enforce consistent fonts (Times New Roman 12pt standard; no sans-serif for body text)
- Validate page numbering (no blank pages, sequential numbering, footer placement)
- Confirm print readiness: no colour-dependent formatting, no embedded images affecting layout
- Clean metadata: remove tracked changes, author names, creation/modification dates before final submission
- Ensure stable layout: test print preview, confirm no widows/orphans, table rendering stable
- Generate print readiness report: margin measurements, font audit, colour usage audit, metadata audit

**Inputs**
- Draft documents (DOCX, PDF)
- Court formatting requirements (jurisdiction-specific rules)
- Print target (A4, B&W)

**Outputs**
- Formatted documents (DOCX and PDF)
- Print readiness report (margin measurements, font list, colour audit, metadata status)
- Metadata audit log (fields removed, timestamps cleared)
- Layout stability validation (page count, no rendering errors)

**Validation Checkpoints**
- [ ] A4 confirmed in document properties
- [ ] Margins within tolerance
- [ ] Fonts consistent (Times New Roman 12pt or court-specified)
- [ ] Page numbers present and sequential
- [ ] No colour-dependent content
- [ ] Metadata cleaned (no tracked changes, author, timestamps)
- [ ] Print preview successful (no layout shift)
- [ ] Header/footer consistent

**Escalation Triggers**
- Layout instability (content shifts between DOCX and PDF rendering)
- Font rendering failure (special characters not supported, font fallback created)
- Complex table rendering (multi-page or nested tables unstable in PDF)
- Metadata issues (tracked changes or author names cannot be removed)
- Colour contamination (colour used in content that must print B&W)

**Confidence & Risk Labelling**
- Risk: Mark layout instability as HIGH/CRITICAL
- Risk: Mark colour contamination as HIGH (may be rejected by court)
- Confidence: Print readiness is PASS/FAIL only (binary)

---

### 7. DOCX/PDF Generation Agent

**Role:** Produce final binary output files.

**Responsibilities**
- Generate DOCX files using docx-js library: templates, content substitution, formatting preservation
- Generate PDF files using ReportLab (Python) or equivalent: ensure faithful rendering of DOCX source
- Apply Bates stamping to PDFs: sequential numbering, page reference (e.g., "001", "002", … "145")
- Apply page numbering and footers: "Page N of M" format
- Perform file merges: concatenate multiple PDFs (e.g., main affidavit + exhibits)
- Perform file splits: extract pages or exhibits from larger PDFs
- Bundle assembly: combine cover pages, table of contents, exhibits into single submission file
- Validate binary output: files open correctly, formatting matches source, hash computed
- Generate manifest: file listing with sizes, hashes, page counts

**Inputs**
- Content templates (DOCX structure with placeholders)
- Data payloads (paragraphs, tables, metadata)
- Formatting specifications (margins, fonts, page size)
- Bates parameters (starting number, format, position)

**Outputs**
- DOCX files (generated, hashes recorded)
- PDF files (generated, hashes recorded)
- Bates-stamped PDFs (with sequential numbering verified)
- Bundled submission file (composite PDF with table of contents)
- Generation manifest (files, sizes, hashes, page counts, generation timestamp)

**Validation Checkpoints**
- [ ] Generated files open correctly in standard applications
- [ ] Formatting preserved in PDF vs. DOCX source
- [ ] Hashes computed and recorded
- [ ] Bates numbers unique and sequential (if stamped)
- [ ] Page counts accurate
- [ ] Bundle assembly complete (all exhibits included)

**Escalation Triggers**
- Rendering failure (DOCX → PDF conversion error)
- Template error (placeholder not substituted, content missing)
- Encoding issue (special characters corrupted in PDF)
- Bates numbering conflict (duplicate numbers or gaps)
- Merge/split error (pages missing or duplicated)
- File size anomaly (generated file much larger/smaller than expected)

**Confidence & Risk Labelling**
- Risk: Mark rendering failures as CRITICAL
- Confidence: File generation is PASS/FAIL only (binary)

---

### 8. Chain of Custody & Bates Agent

**Role:** Maintain provenance and reference integrity.

**Responsibilities**
- Maintain chain of custody log for every evidence file: file hash, custody events (received, transferred, used, verified)
- Assign Bates numbers to disclosed documents: track starting number, ending number, sequence
- Update cross-references as documents move between phases (e.g., Exhibit 1 becomes Bates 042-045)
- Prevent numbering conflicts: validate no duplicate Bates numbers assigned
- Track custody events: who possessed file, when, for what purpose, signature if required
- Verify hash integrity: re-compute hashes of critical files before key milestones (e.g., before court filing)
- Generate custody trail report: complete provenance chain for any document
- Flag chain breaks: missing custody event, unexplained file modification, gap in documentation

**Inputs**
- Evidence files with hashes (from Intake agent)
- Custody events (handoff records, use logs, verification records)
- Bates assignment requests (start number, document list)

**Outputs**
- Chain of custody log (CSV): file-hash, event-date, event-type, actor, signature-status, notes
- Bates register (CSV): original-doc-id, bates-start, bates-end, exhibit-description, page-count
- Cross-reference index (CSV): doc-id → bates-range mapping
- Custody trail report (per file): complete provenance chain with timestamps
- Hash verification audit (CSV): hash-recomputed, date, result (match/mismatch), certifier

**Validation Checkpoints**
- [ ] No duplicate Bates numbers assigned
- [ ] Every custody event logged with date and actor
- [ ] Hash verification completed before filing milestone
- [ ] Cross-references between doc-id and Bates complete and accurate
- [ ] No unexplained file modifications (hash change with no corresponding event)

**Escalation Triggers**
- Chain break (custody event missing or sequence unclear)
- Hash mismatch (file hash changes without documented reason)
- Numbering conflict (Bates number assigned to multiple documents)
- Missing provenance (file in use but no custody entry)
- Custody gap (unexplained time elapsed between recorded events)

**Confidence & Risk Labelling**
- Risk: Mark chain breaks as CRITICAL
- Risk: Mark hash mismatches as CRITICAL
- Confidence: Custody logging is PASS/FAIL only (either complete or incomplete)

---

### 9. Hearing Prep Agent

**Role:** Convert case materials into hearing-ready formats.

**Responsibilities**
- Generate hearing script: sequence of submissions, key facts, anticipated questions, response prompts
- Produce one-page summary (executive brief): dispute, key facts, relief sought, evidence strengths, known weaknesses
- Create issue notes (per issue): summary of legal position, supporting facts, expected opposition, counter-arguments
- Generate response prompts: anticipated questions from bench, suggested answers, evidence references
- Build documents-needed list: exhibits to cite, documents to reference, page/paragraph numbers
- Prepare oral argument outline: structure of opening, logical flow, transition points, closing
- Map affidavit paragraphs to hearing issues: para X supports issue Y
- Identify credibility risks: reliance on recollection only, contradictions, witness availability
- Flag strategic decisions: trade-offs between evidence, disclosure timing, concessions

**Inputs**
- Affidavit (final version)
- Master chronology
- Evidence map (key documents and their relevance)
- Claim support matrix
- Adversarial review findings (weaknesses, risks)
- Court rules (time limits, format requirements)
- Hearing notice (judge, date, issues on notice)

**Outputs**
- `hearing-script.md`: structured sequence of submissions with cues
- `one-pager.md`: executive brief (dispute, key facts, relief, strengths, risks)
- `issue-notes.md`: per-issue summaries with supporting facts and expected opposition
- `response-prompts.csv`: anticipated question, suggested answer, evidence reference
- `documents-needed.csv`: exhibit/document, page/para, relevance to hearing
- `oral-argument-outline.md`: opening structure, logical flow, closing

**Validation Checkpoints**
- [ ] Every issue on notice addressed in script
- [ ] Evidence references verified (documents exist, page numbers correct)
- [ ] Orders sought explicitly stated
- [ ] Credibility risks identified and addressed
- [ ] Strategic decisions documented with rationale
- [ ] Response prompts cover foreseeable cross-examination points

**Escalation Triggers**
- Unresolved issue (no sufficient evidence or legal position on issue)
- Missing evidence (key document needed for hearing not in inventory)
- Contradictory positions (affidavit vs. script differ materially)
- Credibility exposure (reliance on weak evidence for material fact)
- Strategic uncertainty (unclear whether to make concession or contest)
- Time constraint (oral argument exceeds court-permitted time)

**Confidence & Risk Labelling**
- Confidence: Per evidence strength for each issue
- Risk: Mark credibility exposures as HIGH/CRITICAL
- Risk: Mark missing evidence as HIGH/CRITICAL

---

### 10. Adversarial Review Agent

**Role:** Red-team all outputs for weaknesses, risks, and compliance.

**Responsibilities**
- Review all output documents from all other agents: affidavit, chronology, bundles, formatting, hearing prep
- Identify weaknesses: unsupported assertions, gaps in evidence, logical flaws, credibility risks
- Flag emotional or argumentative framing: language inappropriate to legal submission
- Detect formatting issues: court compliance, layout stability, metadata contamination
- Assess logical coherence: contradictions between affidavit and chronology, conflicting fact assertions
- Evaluate credibility: over-reliance on recollection, witness availability, prior inconsistent statements
- Highlight missing evidence: gaps that would allow opposing counsel to argue alternative narrative
- Review affidavit annexure references: verify exhibits exist and support assertions
- Assess privilege risks: any privileged material inadvertently disclosed or referenced
- Categorise findings by severity (CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL)

**Inputs**
- Affidavit draft (all versions)
- Master chronology
- Evidence inventory and exhibits
- Disclosure schedule and bundle
- Formatted documents (DOCX, PDF)
- Hearing prep outputs (scripts, notes, one-pager)
- Chronology and supporting documents

**Outputs**
- `adversarial-review-report.md`: structured findings by category
  - Per-document summary (affidavit, chronology, bundle, hearing prep)
  - Finding: category, severity, specific location, issue description, recommendation
- `weakness-matrix.csv`: weakness-id, document, location (para/page), category, severity, rationale, suggested fix
- `credibility-risk-summary.md`: credibility exposures with supporting facts
- `formatting-audit.csv`: formatting issues found with severity and fix required

**Validation Checkpoints**
- [ ] Every output document reviewed
- [ ] All findings categorised by severity
- [ ] Weaknesses cross-referenced to source locations
- [ ] Recommendations actionable and specific
- [ ] Credibility risks identified and ranked by exposure level

**Escalation Triggers**
- Critical weakness (affidavit assertion unsupported or contradicted)
- Potential credibility collapse (key witness unavailable or prior inconsistency)
- Irreconcilable contradictions (chronology and affidavit conflict on material fact)
- Formatting non-compliance (document would be rejected by court)
- Privilege leak (privileged material disclosed)
- Logical impossibility (facts asserted are temporally or logically inconsistent)

**Confidence & Risk Labelling**
- Risk: Mark every finding with CRITICAL/HIGH/MEDIUM/LOW/INFORMATIONAL
- Confidence: Mark severity as HIGH (definite flaw) or MEDIUM/LOW (potential issue requiring human review)

---

## Handoff Protocol

All agent-to-agent transfers follow a standardised JSON handoff object. This ensures traceability, validation, and escalation visibility.

### Handoff JSON Schema

```json
{
  "handoff_id": "string (UUID v4)",
  "source_agent": "string (sending agent name)",
  "target_agent": "string (receiving agent name)",
  "phase": "integer (1-15, see phase definitions below)",
  "matter_id": "string (unique matter identifier)",
  "status": "enum (READY | BLOCKED | ESCALATED)",
  "inputs": {
    "files": ["list of absolute file paths"],
    "data_references": ["list of external data references or keys"],
    "context": "string (brief summary of context for receiving agent)"
  },
  "outputs_expected": {
    "files": ["list of expected file outputs"],
    "data": ["list of expected data structures or reports"]
  },
  "validation_results": {
    "checks_passed": ["list of validation checks completed successfully"],
    "checks_failed": ["list of validation checks that failed"],
    "warnings": ["list of non-blocking warnings"]
  },
  "escalation": {
    "triggered": "boolean",
    "reason": "string (escalation reason if triggered)",
    "requires_human": "boolean",
    "escalation_type": "string (category from escalation matrix)"
  },
  "timestamp_utc": "ISO 8601 timestamp (UTC)",
  "timestamp_awst": "ISO 8601 timestamp (AWST, UTC+8)",
  "notes": "string (any additional context for receiving agent)"
}
```

### Handoff Status Values

- **READY**: All validation passed; target agent may proceed immediately.
- **BLOCKED**: One or more validation checks failed; target agent must not proceed until source agent resolves issues or human confirms override.
- **ESCALATED**: Escalation triggered (see Escalation Matrix); human decision required before target agent proceeds.

### Phase Definitions (1–15)

| Phase | Source Agent | Target Agent | Handoff Purpose |
|-------|--------------|--------------|-----------------|
| 1 | External | Intake & Evidence Triage | New evidence submitted |
| 2 | Intake & Evidence Triage | Legal File Management | Evidence routed and hashed; folder structure to be validated |
| 3 | Legal File Management | Chronology | File structure compliant; ready for evidence analysis |
| 4 | Chronology | Affidavit Drafting | Master chronology complete; ready for affidavit generation |
| 5 | Affidavit Drafting | Adversarial Review | Affidavit draft complete; ready for red-team review |
| 6 | Adversarial Review | Affidavit Drafting | Review findings returned; affidavit revision required |
| 7 | Affidavit Drafting | Disclosure & Bundle | Final affidavit complete; ready for exhibit preparation |
| 8 | Disclosure & Bundle | Chain of Custody & Bates | Exhibits prepared; ready for Bates stamping and custody logging |
| 9 | Chain of Custody & Bates | Formatting & Court Compliance | Documents Bates-stamped; ready for formatting and compliance check |
| 10 | Formatting & Court Compliance | DOCX/PDF Generation | Documents formatted; ready for final DOCX/PDF generation |
| 11 | DOCX/PDF Generation | Adversarial Review | Final documents generated; ready for final red-team check |
| 12 | Adversarial Review | Hearing Prep | All documents finalised; ready for hearing preparation |
| 13 | Hearing Prep | Adversarial Review | Hearing prep outputs ready; ready for final review |
| 14 | Adversarial Review | External | All documents and prep materials finalised; ready for filing/hearing |
| 15 | External | (End of Workflow) | Matter filed or hearing conducted |

---

## Validation Gates

Each phase transition requires validation. Gates must pass before handoff status = READY.

### Gate 1→2: Intake → File Management

**Trigger:** Evidence triage complete, all files hashed and classified
**Passing Criteria:**
- [ ] All files in intake folder hashed (SHA-256)
- [ ] All files assigned a classification (document type)
- [ ] Hashed file registry populated (hash, filename, class, source, receiver)
- [ ] Chain of custody entry created for every unique file
- [ ] No files remain in intake folder without routing decision

**Failure Condition:**
- Unknown file format (cannot classify)
- Suspected corruption (hash check fails or file unreadable)
- Missing source metadata (submission context unknown)

**Human Review Required:**
- Privilege determination (potential attorney-client communication)

---

### Gate 2→3: File Management → Chronology

**Trigger:** Folder structure validated and compliant
**Passing Criteria:**
- [ ] Folder structure complies with schema
- [ ] No naming conflicts
- [ ] Version register initialised for all documents
- [ ] AIStore outputs confirmed isolated (no contamination in /final/)
- [ ] Compliance lint report passed

**Failure Condition:**
- Naming convention violated (files unable to be normalised without conflict)
- Immutability violation detected
- AIStore files found in court-facing folders

**Human Review Required:**
- Naming conflicts (human decision on which version to keep)

---

### Gate 3→4: Chronology → Affidavit Drafting

**Trigger:** Master chronology complete and validated
**Passing Criteria:**
- [ ] All events sourced to at least one document
- [ ] Confidence labels assigned to every event
- [ ] Fact/interpretation flags completed
- [ ] Gaps report generated
- [ ] Contradictions logged with sources
- [ ] No material contradictions remain unresolved

**Failure Condition:**
- Major timeline gap (> 30 days with no documented events in critical period)
- Unsourced assertion (event asserted without document source)
- Unresolved contradiction (conflicting evidence without determination of which is more reliable)

**Human Review Required:**
- Disputed facts (chronology must decide credibility)
- Temporal impossibilities (event dates create logical conflict requiring human interpretation)

---

### Gate 4→5: Affidavit Drafting → Adversarial Review

**Trigger:** Affidavit draft complete with sourcing audit
**Passing Criteria:**
- [ ] Every material assertion sourced in sourcing audit
- [ ] No speculation or hedging language
- [ ] No emotional or argumentative content
- [ ] Paragraph numbering sequential
- [ ] Annexure references complete and accurate
- [ ] Verification statement drafted
- [ ] Deponent capacity and authority stated

**Failure Condition:**
- Unsupported claim (assertion with no source document)
- Contradiction with chronology
- Privilege issue (affidavit references legal advice)

**Human Review Required:**
- Credibility risk (reliance on recollection only for material fact)
- Deponent capacity disputed

---

### Gate 5→6: Adversarial Review → Affidavit Revision

**Trigger:** Red-team review completed; findings documented
**Passing Criteria:**
- [ ] All findings categorised and severity assigned
- [ ] Recommendations specific and actionable
- [ ] No CRITICAL findings remain unacknowledged

**Failure Condition:**
- CRITICAL finding (e.g., unsupported claim, privilege leak)
- Irreconcilable contradiction

**Human Review Required:**
- All CRITICAL and HIGH findings reviewed by matter handler before proceeding to revision

---

### Gate 6→7: Revised Affidavit → Disclosure & Bundle

**Trigger:** Affidavit revised and re-validated
**Passing Criteria:**
- [ ] All prior findings addressed (CRITICAL/HIGH resolved or waived with documented reason)
- [ ] Sourcing audit updated
- [ ] Revised draft passed secondary validation

**Failure Condition:**
- Unresolved CRITICAL finding

**Human Review Required:**
- Decision to proceed with HIGH-risk assertions (waiver required)

---

### Gate 7→8: Disclosure & Bundle → Chain of Custody & Bates

**Trigger:** Exhibits prepared and indexed
**Passing Criteria:**
- [ ] Disclosure schedule complete (all items accounted for)
- [ ] Privilege log complete (privileged items identified and withheld)
- [ ] Annexure index matches affidavit references
- [ ] No privilege material disclosed
- [ ] Cross-references verified

**Failure Condition:**
- Privilege uncertainty (document with arguable privilege status disclosed)
- Missing documents (referenced but not found)
- Incomplete evidence (affidavit claim unsupported by exhibit)

**Human Review Required:**
- Privilege determination (uncertain status documents)

---

### Gate 8→9: Chain of Custody & Bates → Formatting & Court Compliance

**Trigger:** Bates stamping complete and custody logged
**Passing Criteria:**
- [ ] No duplicate Bates numbers
- [ ] Bates numbering sequential and complete
- [ ] Chain of custody entries logged for all key files
- [ ] Hash verification completed
- [ ] Cross-reference index complete

**Failure Condition:**
- Chain break (missing custody event)
- Hash mismatch (file modified without documented reason)
- Numbering conflict

**Human Review Required:**
- Chain break investigation

---

### Gate 9→10: Formatting & Court Compliance → DOCX/PDF Generation

**Trigger:** Documents formatted and compliance validated
**Passing Criteria:**
- [ ] A4 confirmed
- [ ] Margins within tolerance
- [ ] Fonts consistent (Times New Roman 12pt or court-specified)
- [ ] Page numbers present and sequential
- [ ] No colour-dependent content
- [ ] Metadata cleaned
- [ ] Print preview successful

**Failure Condition:**
- Layout instability (content shifts between DOCX and PDF)
- Metadata issues (cannot remove tracked changes or author)
- Colour contamination

**Human Review Required:**
- Layout instability investigation

---

### Gate 10→11: DOCX/PDF Generation → Final Adversarial Review

**Trigger:** Final documents generated
**Passing Criteria:**
- [ ] Files open correctly
- [ ] Formatting matches source
- [ ] Hashes computed and recorded
- [ ] Bates numbers verified in PDF
- [ ] Page counts accurate
- [ ] File manifest generated

**Failure Condition:**
- Rendering failure (file corrupt or unopenable)
- Encoding issue (characters corrupted)

**Human Review Required:**
- File size anomalies (size much larger/smaller than expected, requires investigation)

---

### Gate 11→12: Final Adversarial Review → Hearing Prep

**Trigger:** Final documents passed red-team check
**Passing Criteria:**
- [ ] No CRITICAL findings in final review
- [ ] All HIGH findings documented with mitigation or acceptance

**Failure Condition:**
- CRITICAL finding (e.g., credibility collapse, irreconcilable contradiction)

**Human Review Required:**
- Decision to proceed with HIGH-risk documents (waiver required)

---

### Gate 12→13: Hearing Prep → Final Validation

**Trigger:** Hearing prep materials generated
**Passing Criteria:**
- [ ] All hearing issues addressed
- [ ] Evidence references verified
- [ ] Orders sought clearly stated
- [ ] Response prompts cover anticipated questions
- [ ] Documents-needed list complete

**Failure Condition:**
- Unresolved issue (no sufficient evidence or legal position)
- Missing evidence (key document needed not in inventory)

**Human Review Required:**
- Strategic decisions (concession trade-offs, timing)

---

### Gate 13→14: Final Adversarial Review → Filing Ready

**Trigger:** Final red-team review completed
**Passing Criteria:**
- [ ] No CRITICAL findings
- [ ] All formatting compliant
- [ ] All documents final and signed (if applicable)

**Failure Condition:**
- CRITICAL finding

**Human Review Required:**
- Approval for filing/hearing by matter handler

---

## Escalation Matrix

Escalations halt phase transition. Human decision required before proceeding.

### Escalation Types and Required Actions

| Escalation Type | Severity | Required Action | Escalation Path |
|---|---|---|---|
| EVIDENCE_INTEGRITY | CRITICAL | Halt all work. Investigate file corruption, missing evidence, or chain break. Verify original source. Do not proceed until resolved. | Matter handler + document custodian |
| PRIVILEGE_RISK | CRITICAL | Halt work. Obtain legal advice on privilege claim. Determine whether disclosure is required or material must be withheld. Document decision. | Matter handler + in-house counsel (if available) |
| UNSUPPORTED_CLAIM | CRITICAL | Halt affidavit/disclosure. Identify claim without source document. Either source the claim or remove from affidavit. Do not file with unsupported assertions. | Affidavit drafter + matter handler |
| CONTRADICTORY_EVIDENCE | HIGH | Identify conflicting accounts. Determine credibility of each source (contemporaneous record vs. recollection, corroboration, etc.). Document resolution in chronology. If unresolved, escalate for matter handler decision. | Chronology agent + matter handler |
| MISSING_CONTEXT | MEDIUM | Identify what context is missing (e.g., witness availability, prior statements, opposing party position). Determine whether matter can proceed without it or must delay for additional investigation. | Matter handler |
| FORMATTING_FAILURE | HIGH | Halt final generation. Identify formatting issue (layout shift, font failure, metadata issue). Remediate and re-test. Do not file non-compliant documents. | Formatting agent + matter handler |
| CHAIN_BREAK | CRITICAL | Halt all work. Investigate missing custody event or unexplained file modification. Determine whether chain can be reconstructed or matter compromised. | Matter handler + document custodian |
| MANDATORY_REPORTING | CRITICAL | Halt all work immediately. Identify issue requiring mandatory reporting (e.g., fraud indicators, witness tampering evidence). Obtain legal advice before proceeding. Do not file without reporting if required. | Matter handler + in-house counsel + external counsel if necessary |
| EMOTIONAL_FRAMING | HIGH | Identify emotional, argumentative, or subjective language in court-facing documents. Remove or replace with neutral, factual phrasing. Do not file documents with emotional framing. | Adversarial review agent + affidavit drafter |
| VERSION_CONFLICT | MEDIUM | Identify which version is current (e.g., multiple drafts with conflicting numbering or content). Designate authoritative version. Archive superseded versions. Restart workflow with canonical version. | Legal file management agent + matter handler |

### Escalation Workflow

1. **Detection:** Agent detects condition matching escalation trigger.
2. **Handoff Status:** Set handoff status = ESCALATED with escalation type and reason.
3. **Notification:** Flag escalation in handoff object and surface to matter handler (via Linear issue, Slack, or configured alert).
4. **Human Decision:** Matter handler reviews escalation, decides on action (resolve and retry, proceed with waiver, cancel/defer).
5. **Resolution:** Source agent applies decision (resolves issue, documents waiver, or halts work).
6. **Resume:** Upon resolution, handoff status updated to READY and workflow resumes.

---

## Confidence and Risk Labels

All agent outputs include confidence, risk, and evidence strength assessments. These enable rapid prioritisation of review effort and identification of weak points.

### Confidence Levels

| Level | Definition | Interpretation |
|-------|-----------|-----------------|
| **HIGH** | Assertion strongly supported by primary evidence, contemporaneous records, or multiple corroborating sources. | Safe to rely on for material assertions in affidavit or hearing. Low risk of successful challenge. |
| **MEDIUM** | Assertion supported by credible evidence but with some limitation (single source, some recollection, corroboration limited). | Acceptable for affidavit/hearing but flagged for cross-examination preparation. Moderate challenge risk. |
| **LOW** | Assertion supported primarily by recollection, single non-contemporaneous source, or circumstantial evidence. | Risky for material assertions. Requires corroboration or supplementary evidence to strengthen. High challenge risk. |
| **UNCERTAIN** | Assertion contradicted by other evidence, recollection conflicts with record, or evidence missing entirely. | Do not rely on for affidavit. Must resolve contradiction or source separately. Critical challenge risk. |

### Risk Levels

| Level | Definition | Trigger Action |
|-------|-----------|-----------------|
| **CRITICAL** | Issue that could result in affidavit rejection, privilege waiver, credibility collapse, or case loss. Examples: unsupported claim, privilege leak, chain break, contradictory evidence, witness unavailability. | HALT work immediately. Escalate to matter handler. Do not proceed without explicit waiver. |
| **HIGH** | Issue that creates significant challenge risk but may be managed with additional evidence, mitigation, or disclosure strategy. Examples: reliance on recollection for material fact, single source for key evidence, formatting non-compliance. | Flag for matter handler review. Proceed only with documented mitigation plan or explicit acceptance. |
| **MEDIUM** | Issue that creates some challenge risk but is not disqualifying. Examples: minor formatting issue, corroboration from secondary source only, credibility gap. | Document in review report. Proceed with awareness. Prepare response to anticipated challenges. |
| **LOW** | Minor issue or procedural note that does not affect substance or court compliance. Examples: naming inconsistency, metadata note, minor gap in evidence. | Document for reference. Proceed without delay. |
| **INFORMATIONAL** | Note or observation that provides context but does not constitute a risk or deficiency. Examples: evidence strength breakdown, observation on hearing strategy. | Log for reference. No action required. |

### Evidence Strength Classification

Evidence is classified by its nature and reliability:

| Classification | Definition | Court Weight |
|---|---|---|
| **DIRECT_EVIDENCE** | Contemporaneous document, record, or statement by direct participant describing the fact asserted (e.g., email written at time of event, contract, invoice, witness statement made immediately after). | Strongest. Preferred for material assertions. Low challenge risk. |
| **CORROBORATIVE** | Evidence supporting a fact but not directly asserting it; typically used to strengthen other evidence (e.g., multiple people describe same event; document confirms participant's recollection). | Strong. Significantly reduces challenge risk when paired with other evidence. |
| **CIRCUMSTANTIAL** | Evidence from which fact can be inferred but not directly proven (e.g., payment records infer contract performance, timestamps infer sequence). | Moderate. Acceptable as supporting evidence; risky as sole basis for material assertion. |
| **HEARSAY** | Statement by someone not present in affidavit (e.g., "X told me that…"). | Weak in court (generally inadmissible unless exception applies). Avoid for material assertions unless exception documented. |
| **OPINION** | Subjective assessment or interpretation (e.g., "I believed X intended to…", "it seemed like…"). | Weak unless from expert witness in relevant field. Avoid in affidavit unless expert status clear. |
| **UNCORROBORATED** | Evidence not supported by any other source (e.g., sole witness to event, recollection with no corroboration). | Weakest. High risk for material assertions. Must be addressed in cross-examination prep. |

### Labelling Convention

Every factual assertion in agent outputs should be tagged:

```
[Fact]: [assertion]
[Confidence]: HIGH | MEDIUM | LOW | UNCERTAIN
[Risk]: CRITICAL | HIGH | MEDIUM | LOW | INFORMATIONAL
[Evidence Strength]: DIRECT_EVIDENCE | CORROBORATIVE | CIRCUMSTANTIAL | HEARSAY | OPINION | UNCORROBORATED
[Source]: [document file, page/paragraph reference]
```

Example:

```
[Fact]: Defect occurred on 2025-08-15
[Confidence]: HIGH
[Risk]: LOW
[Evidence Strength]: DIRECT_EVIDENCE
[Source]: affidavit-draft.docx, para 14; inspection-report.pdf, p. 3
```

---

## Integration Notes

### Dependency on External Systems

- **Linear:** Reference project ID and issue tracking for matter context, decision audit trail.
- **Notion:** Master documentation and SOP reference; link to user manuals for matter handling procedures.
- **File Storage:** All file paths absolute and immutable; hashing ensures integrity verification.

### Handoff Automation

Handoff JSON objects can be stored in a structured log file (JSON Lines format, one object per line) for audit and workflow orchestration. Parsers can:
- Detect phase transitions automatically
- Identify validation gate failures
- Surface escalations to matter handler via Linear issue creation or Slack alert
- Log all phase transitions for matter audit trail

### Matter Context

Each matter is identified by a unique `matter_id` (e.g., `MAT-20260315-001`). This ID appears in:
- Folder naming convention (matter ID prefix on all documents)
- Handoff objects (all transfers reference matter_id)
- Chain of custody log
- Linear issue associations

### Workflow Orchestration

Workflow can be driven manually (matter handler triggers each phase) or semi-automated:
- Agents execute automatically on handoff receipt
- Validation gates enforced; phase transitions blocked until gate passes
- Escalations routed automatically to matter handler
- Completion notifications confirm handoff acceptance

---

## Change History

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-03-16 | Initial architecture definition (v1.0) | Establish canonical agent system for legal matter operations workflow. |

---

**Document Owner:** Legal Matter Operations System
**Last Reviewed:** 2026-03-16
**Next Review Due:** 2026-06-16
**Status:** Active
