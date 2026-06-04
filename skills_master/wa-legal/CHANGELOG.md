# wa-legal Skill — Changelog

## [Unreleased]

### Added
- New `wa-perjury-offences.md` reference (Criminal Code ss.124–143, 169–170, researched 1 May 2026)
- `references/README.md` explaining file organization and naming convention
- `CHANGELOG.md` (this file)

### Changed
- Merged 8 standalone skills into single `wa-legal` master skill with thin router
- Consolidated 28 reference files into `references/` with deduplicated disclaimers
- Fixed file naming inconsistencies (`affidavit-templates.md` → `affidavit-court-affidavit-templates.md`, etc.)
- Updated `SKILL.md` router table with correct filenames
- Updated `CLAUDE.md` registry with new `wa-legal` structure

### Removed
- Old standalone skill directories (archived to `.omc/archive/legal-skills-pre-merge/`)
- Mirrored copies from `.config/opencode/skill/`
- Orphan files: `example-prompts.md`, `interpersonal-hardening.md`, `agent-architecture.md`
- Duplicate `evidence-standards.md` (kept `case-file-evidence-standards.md`)

### Deprecated
- `wa-fvro/`, `wa-law-general/`, `wa-teacher-misconduct/`, `case-file-manager-wa/`, `affidavit-court-preparation/`, `csv-legal-analysis/`, `legal-matter-ops/` — all archived with deprecation notices

## [Pre-Merge] - 2026-04-15 to 2026-05-04

### wa-fvro (standalone)
- Initial skill with FVRO templates, case law, court forms, MHA intersections

### wa-law-general (standalone)
- WA court hierarchy, legal services directory, court procedures

### wa-teacher-misconduct (standalone)
- Teacher Registration Act 2012 framework, WWC, TRBWA, grooming indicators

### case-file-manager-wa (standalone)
- SRL case folder structure, scripts, templates, evidence standards

### affidavit-court-preparation (standalone)
- Affidavit drafting, chronologies, disclosure packs, hearing prep

### csv-legal-analysis (standalone)
- CSV/SMS forensic analysis, DuckDB/Polars, eDiscovery protocols

### legal-matter-ops (standalone)
- 15-phase lifecycle, intake→filing, Bates numbering, DOCX/PDF generation

### wa-perjury-offences (research only)
- Researched Criminal Code ss.124–143, 169–170 from legislation.wa.gov.au (1 May 2026 consolidation)
