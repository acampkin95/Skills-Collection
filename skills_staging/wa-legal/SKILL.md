---
name: wa-legal
description: Master router for WA legal operations — FVRO, teacher misconduct, case files, affidavits, eDiscovery, legal matter ops, and Criminal Code offences.
version: 2.0.0
reviewed: "2026-06-04"
---

# WA Legal — Master Router

> **MANDATORY DISCLAIMER**: This skill provides **general legal information** specific to Western Australia. It is **NOT legal advice**. Users MUST obtain independent legal advice from a WA lawyer, Legal Aid WA (1300 650 579), or a community legal centre before making any decisions or court applications.

## Router

All reference files listed below are in `references/`. Case management scripts are in `scripts/`.

| Topic | Key References |
|-------|---------------|
| **FVRO** — Restraining Orders Act 1997 (WA), s.31 objection, s.45–46 variation/cancellation, s.61 breach, Form 12, MHA conflicts | `fvro-affidavit-templates.md`, `fvro-case-law.md`, `fvro-court-forms.md`, `fvro-mha-intersections.md` |
| **Teacher misconduct** — Teacher Registration Act 2012, WWC, TRBWA, grooming, professional boundaries | `teacher-regulatory-framework.md`, `teacher-wwc-framework.md`, `teacher-investigation-processes.md`, `teacher-complaints-and-evidence.md`, `teacher-conduct-scope-conflicts.md`, `teacher-case-law-legislation.md` |
| **Case file management** — SRL folder structure, evidence/comms indexes, document naming, dashboards | `case-file-evidence-standards.md`, `case-file-templates.md`, `wa-magistrates-civil.md`, `wa-magistrates-criminal.md` |
| **Affidavit & court prep** — drafting, chronologies, disclosure packs, annexures, hearing notes | `fvro-affidavit-templates.md`, `affidavit-court-formats.md`, `wa-evidence-law.md` |
| **CSV / eDiscovery** — SMS/iMessage forensics, DuckDB/Polars, Bates numbering, privilege logs | `analysis-workflows.md`, `ediscovery-protocols.md`, `sms-imessage-analysis.md`, `wa-evidence-law.md`, `large-dataset-processing.md`, `family-law-evidence.md`, `coercive-control-frameworks.md` |
| **Legal matter ops** — 15-phase lifecycle, intake to filing, DOCX/PDF generation, deadline registers | `execution-protocol.md`, `operations.md`, `folder-naming-versioning.md`, `docx-pdf-generation.md`, `internal-controls.md` |
| **WA law general** — court hierarchy, legislation, filing fees, eLodgment, SAT, legal services | `legal-services.md`, `court-procedures.md` |
| **Perjury** — Criminal Code s.124–s.143, s.169–s.170, false evidence, perverting justice | `wa-perjury-offences.md` |
| **Tenancy** — WA residential tenancy disputes, Form 1A/1B, termination, bond | `wa-tenancy-guide.md` |

## Source Quality Protocol

Use primary sources first: WA legislation from `legislation.wa.gov.au`, official court websites, practice directions/forms, and full judgments from AustLII, Jade, or court sites. Treat unreported anecdotes, forum posts, legal blogs, and AI summaries as non-authoritative. If a case cannot be retrieved from a reliable legal database, say that it needs verification before use in submissions. Verify current fees, forms, and filing channels during each task.

## Common Mistakes (All WA Legal Skills)

- Treating protected-person contact as automatic permission to breach an order.
- Giving strategy on an active charge instead of referring urgently for legal advice.
- Citing case law without reading the full judgment and checking current statutory wording.
- Assuming filing channels, fees, or forms have not changed.
- Drafting documents that argue conclusions rather than set out dated facts and source material.
- Using blogs, forums, or AI summaries as authority for legal propositions.
- Mixing WA state court procedure with Federal Court, FCFCOA, or interstate procedure.

## Validation

After editing this skill or its references, run:

```bash
docker compose -f compose.skills.yml run --rm skills-validator
```

Fallback:

```bash
uv run --project .maintenance/Skills-Framework-Reference skills-ref validate wa-legal
```
