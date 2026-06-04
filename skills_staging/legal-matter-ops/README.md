# Legal Matter Operations Engine

The Legal Matter Operations Engine is a structured workflow skill for managing litigation evidence, building affidavits, and assembling court bundles. It enforces strict phase discipline, maintains continuous chain of custody over evidence, and isolates AI working materials from court-filed documents. It is not a legal adviser; it is a filing and workflow engine that works under the supervision of a qualified legal practitioner.

## What This Skill Does

- Legal matter folder structure and lifecycle management
- Evidence intake, hashing, chain of custody verification
- Chronology reconstruction from timestamped evidence
- Affidavit drafting with evidence traceability
- Disclosure schedule preparation and privileged-matter filtering
- Bates numbering and evidence cross-referencing
- DOCX and PDF generation (court-compliant formatting)
- Hearing preparation (scripts, one-pagers, issue analysis)
- Adversarial review (red-teaming all outputs)
- Print bundle assembly and document freezing
- Meeting data logging and reporting obligation extraction
- File versioning and lifecycle control
- AI working material isolation (AIStore separation)

## What This Skill Does NOT Do

- Provide legal advice or strategy
- Predict court outcomes or judicial behaviour
- Replace qualified legal practitioners or paralegals
- Guarantee admissibility of evidence
- Make litigation strategy decisions
- Assess legal merit of claims or defences
- Provide risk or cost estimates

## Mandatory Execution Protocol

The skill enforces a 15-phase sequence. Skipping or reordering phases is not permitted.

1. **Matter Setup** — create folder, establish metadata, lock matter identifier
2. **Evidence Intake** — ingest evidence (files, messages, documents), hash all items
3. **Evidence Inventory** — build and verify inventory, check for duplicates
4. **Chain of Custody** — establish provenance chain, document source and handling
5. **Chronology Build** — reconstruct timeline from dated evidence
6. **Chronology Review** — gap analysis, source verification, consolidation
7. **Affidavit Draft** — generate sworn statement with evidence annexures
8. **Affidavit Hardening** — remove emotional language, verify legal sufficiency
9. **Disclosure Schedule** — map all evidence to disclosure set, identify privileged matter
10. **Bates Numbering** — assign sequential document identifiers
11. **Cross-Reference Update** — resolve all citations to Bates numbers
12. **Adversarial Review** — stress-test outputs against hostile reading
13. **Hearing Preparation** — generate scripts, one-pagers, issue notes
14. **Bundle Assembly** — collate court documents with index and cover page
15. **Bundle Freeze & File** — lock versioning, prepare for court filing

## Folder Structure

```
matter-identifier/
├── meta/                          # Matter metadata (court, parties, deadlines)
├── evidence/                      # Source evidence (messages, documents, files)
├── inventory/                     # Evidence index and hash register
├── chain-of-custody/              # Provenance documentation
├── chronology/                    # Timeline reconstruction and consolidation
├── affidavit/                     # Sworn statement drafts and versions
├── disclosure/                    # Privileged-matter filtering and schedules
├── bates/                         # Sequential numbering and cross-references
├── hearing-prep/                  # Scripts, one-pagers, issue notes
├── bundle/                        # Court bundle assembly (final state)
├── meetings/                      # Meeting notes and reporting obligations
└── aistore/                       # AI working materials (isolated from filings)
```

## File Naming Convention

All files follow `YYYYMMDD_PHASE_DESCRIPTOR_vN.ext` format.

Examples:
- `20260315_evidence-intake_message-exports_v1.csv`
- `20260316_chronology_master-timeline_v3.docx`
- `20260316_affidavit_smith-sworn-statement_v2.docx`
- `20260316_bates_cross-reference-map_v1.xlsx`
- `20260316_bundle_final-court-bundle_v1.pdf`

## Reference Files

| File | Purpose |
|------|---------|
| `MATTER-SETUP.md` | Matter initialisation checklist and metadata schema |
| `EVIDENCE-PROTOCOL.md` | Intake and hashing procedures |
| `CHAIN-OF-CUSTODY.md` | Provenance chain template and verification steps |
| `CHRONOLOGY-BUILD.md` | Timeline reconstruction methodology |
| `AFFIDAVIT-TEMPLATE.md` | Sworn statement structure and evidence traceability |
| `DISCLOSURE-FILTERING.md` | Privileged-matter classification and schedule format |
| `BATES-NUMBERING.md` | Sequential assignment and cross-reference management |
| `COURT-FORMATTING.md` | Jurisdiction-specific formatting rules (WAMC, District, Federal) |
| `ADVERSARIAL-REVIEW.md` | Red-teaming checklist and hostile-reading methodology |
| `HEARING-SCRIPTS.md` | Script templates and one-pager structure |
| `BUNDLE-ASSEMBLY.md` | Print bundle collation and cover page standards |
| `AISTORE-PROTOCOL.md` | AI working material isolation and lifecycle |
| `FILE-VERSIONING.md` | Version control and changelog standards |
| `REPORTING-OBLIGATIONS.md` | Meeting data classification and disclosure duty mapping |

## Quick Start

### 1. Initialise a New Matter
```
Initialise a legal matter for [CASE_NAME], [COURT], file number [FN].
```
The skill creates the folder structure, locks the matter identifier, and generates a matter metadata template.

### 2. Intake Evidence
```
Intake evidence from [SOURCE_FOLDER_PATH] and hash all items.
```
The skill ingests files, generates MD5/SHA256 hashes, creates the inventory, and documents source provenance.

### 3. Build Chronology
```
Build a master chronology from the evidence inventory.
```
The skill extracts timestamps, sorts events, identifies gaps, and generates a timeline document.

### 4. Draft Affidavit
```
Draft an affidavit based on the chronology and evidence inventory, addressing [ISSUE_LIST].
```
The skill generates a sworn statement with evidence annexures, numbered references, and legal structure.

### 5. Prepare Disclosure
```
Prepare a disclosure schedule for all evidence. Identify privileged matter.
```
The skill maps all evidence to disclosure rules, classifies privileged documents, and generates schedules.

### 6. Assign Bates Numbers
```
Assign Bates numbers to the disclosure set, starting at [PREFIX]_001.
```
The skill assigns sequential identifiers and updates all cross-references in affidavit and schedules.

### 7. Prepare Hearing
```
Generate a one-page hearing summary and issue notes for [CONTESTED_POINTS].
```
The skill produces concise, structured hearing preparation materials.

### 8. Assemble Bundle
```
Assemble the final court bundle with index and cover page.
```
The skill collates all court documents, verifies readiness, and produces the printable bundle.

### 9. Freeze and File
```
Freeze the bundle for filing and generate the final run report.
```
The skill locks versioning, archives working materials, and prepares the matter for court lodgement.

## Design Decisions

**Strict phase ordering** — The 15-phase sequence is mandatory and cannot be skipped. This prevents critical steps (chain of custody, affidavit hardening, adversarial review) from being omitted under time pressure.

**AIStore isolation** — AI working materials (drafts, explorations, annotations) are segregated from court-filed documents. This ensures AI commentary and uncertainty do not contaminate affidavits or bundles.

**Bates numbering as architecture** — Sequential document numbering is not a formatting afterthought; it is embedded in the workflow and enforced continuously. All cross-references resolve to Bates numbers.

**Mandatory adversarial review** — Before hearing preparation or bundle assembly, all outputs are stress-tested against hostile reading. This is not optional.

**Interpersonal matter hardening** — Affidavits are automatically scanned for emotional language, non-sequiturs, and argumentative tone. These are flagged and removed.

**Continuous chain of custody** — Evidence provenance is established at intake and verified at each phase. No retroactive chain-of-custody reconstruction.

## Ethical Boundaries

- The skill will not generate affidavits that misrepresent evidence or contain knowingly false statements.
- The skill will not assist in destruction, concealment, or spoliation of evidence.
- The skill will not withhold disclosable evidence or misclassify privileged matter.
- The skill will not generate legal strategy or advice; it enforces procedural discipline only.
- The skill will not override legal practitioner judgment. All outputs are supervisory review points, not autonomous filings.
- The skill will refuse invocations that contradict court orders, procedural rules, or legal obligations.

## Dependencies

- `docx-js` (npm) — DOCX generation and manipulation
- `reportlab` (pip) — PDF generation
- `pypdf` (pip) — PDF manipulation and metadata
- `pdfplumber` (pip) — PDF text extraction
- `pandas` (pip) — Inventory and chronology management
- `hashlib` (Python stdlib) — MD5/SHA256 hashing
- `json` (Python stdlib) — Metadata serialisation
- `csv` (Python stdlib) — Evidence inventory export
