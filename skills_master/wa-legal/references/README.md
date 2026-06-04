# WA Legal References — File Organization

All reference files for the `wa-legal` master skill live in this directory.

## Naming Convention

| Prefix | Source Skill | Example |
|--------|-------------|---------|
| `fvro-*` | wa-fvro | `fvro-affidavit-templates.md`, `fvro-case-law.md` |
| `teacher-*` | wa-teacher-misconduct | `teacher-regulatory-framework.md`, `teacher-wwc-framework.md` |
| `case-file-*` | case-file-manager-wa | `case-file-evidence-standards.md`, `case-file-templates.md` |
| `affidavit-*` | affidavit-court-preparation | `affidavit-court-affidavit-templates.md`, `affidavit-court-formats.md` |
| `court-*` | wa-law-general | `court-procedures.md` |
| `wa-*` | wa-law-general, csv-legal-analysis, legal-matter-ops | `wa-magistrates-civil.md`, `wa-evidence-law.md`, `wa-perjury-offences.md` |
| (no prefix) | csv-legal-analysis, legal-matter-ops | `analysis-workflows.md`, `ediscovery-protocols.md` |

## Key Files by Topic

### FVRO (Restraining Orders Act 1997)
- `fvro-affidavit-templates.md` — Drafting templates for s.31, s.45–46 applications
- `fvro-case-law.md` — Case law research guide
- `fvro-court-forms.md` — Forms, filing procedures, eCourts Portal
- `fvro-mha-intersections.md` — Mental Health Act conflicts with FVRO

### Teacher Misconduct (Teacher Registration Act 2012)
- `teacher-regulatory-framework.md` — TRBWA, misconduct categories, sanctions
- `teacher-wwc-framework.md` — Working with Children Check framework
- `teacher-investigation-processes.md` — Investigation procedures, mandatory reporting
- `teacher-complaints-and-evidence.md` — Complaints, evidence gathering
- `teacher-conduct-scope-conflicts.md` — Professional boundaries, conflicts of interest
- `teacher-case-law-legislation.md` — SAT decisions, key cases

### Case File Management (SRL)
- `case-file-evidence-standards.md` — Evidence standards, affidavit formatting
- `case-file-templates.md` — Dashboard, timeline, index templates
- `wa-magistrates-civil.md` — Civil procedure, forms, deadlines
- `wa-magistrates-criminal.md` — Criminal procedure, bail, sentencing

### Affidavit & Court Prep
- `affidavit-court-affidavit-templates.md` — General affidavit drafting templates
- `affidavit-court-formats.md` — Court filing formats, exhibit marking
- `evidence-standards.md` — WA Magistrates Court evidence requirements

### CSV / eDiscovery
- `analysis-workflows.md` — Data loading, profiling, analysis
- `ediscovery-protocols.md` — Keyword search, privilege review, production
- `sms-imessage-analysis.md` — SMS/iMessage forensics
- `large-dataset-processing.md` — DuckDB, Polars, scaling
- `coercive-control-frameworks.md` — DV analysis frameworks
- `family-law-evidence.md` — Family Court evidence requirements
- `wa-evidence-law.md` — WA evidence legislation

### Legal Matter Ops (15-Phase Lifecycle)
- `execution-protocol.md` — Intake to filing workflow
- `operations.md` — Matter management operations
- `folder-naming-versioning.md` — Directory structure standards
- `docx-pdf-generation.md` — Document generation
- `internal-controls.md` — Quality controls

### WA Law General
- `legal-services.md` — Legal Aid, CLCs, duty lawyers
- `court-procedures.md` — Court hierarchies, filing fees, eCourts Portal

### Perjury & False Statements
- `wa-perjury-offences.md` — Criminal Code ss.124–143, 169–170

## Scripts

All Python scripts are in `../scripts/`:
- `init_case.py` — Initialize SRL case folder structure
- `lint_case.py` — Audit case folder compliance
- `suggest_filename.py` — Generate compliant filenames
- `update_dashboard.py` — Update dashboard documents
- `update_evidence_index.py` — Update evidence indexes
- `update_comms_index.py` — Update communications indexes
- `record_ai_usage.py` — Log AI assistance
- `cleanup_ai_workspace.py` — Archive stale AI drafts

## Deprecated Skills

The 8 original skills are archived at:
`.claude/skills/.omc/archive/legal-skills-pre-merge/`

Their content is merged here. Do not use the archived skills — use this `wa-legal` master skill.
