---
name: legal-matter-ops
description: WA legal matter operations — intake, chronology, affidavits, disclosure, eDiscovery, evidence bundles, and court-ready document generation.
version: 2.0.0
reviewed: "2026-06-04"
---

# Legal Matter Operations

Run production-grade legal file operations for Australian court matters, with WA court practice as the default. This skill organises work; it does not provide legal advice, predict outcomes, or replace practitioner review.

## Operating Rules

1. Open with the legal-information disclaimer when responding to users.
2. Identify the jurisdiction, court, matter type, filing deadline, and procedural posture before drafting or organising.
3. Preserve originals: hash source evidence, work from copies, and keep source paths out of filed documents.
4. Separate facts, inferences, legal issues, and strategy. Do not convert user opinions into evidence.
5. Use primary sources for legal propositions and verify current forms, fees, practice directions, and filing channels before court-facing output.
6. Label AI-assisted material as draft until a human checks facts, citations, privileged material, annexure references, and procedural compliance.

## Quick Router

| Need | Load |
|---|---|
| Intake-to-filing workflow | `references/execution-protocol.md`, `references/operations.md` |
| Matter folder structure and versioning | `references/folder-naming-versioning.md` |
| Chronology, affidavit, and evidence traceability templates | `references/templates.md` |
| eDiscovery, TAR, privilege, production manifests | `references/ediscovery-protocols.md` |
| WA digital evidence admissibility | `references/wa-evidence-law.md` |
| Family law evidence and affidavit requirements | `references/family-law-evidence.md` |
| SMS/iMessage forensic workflows | `references/sms-imessage-analysis.md` |
| Coercive control analysis | `references/coercive-control-frameworks.md` |
| DOCX/PDF generation | `references/docx-pdf-generation.md` |
| Internal review controls | `references/internal-controls.md` |

## Source Quality Protocol

Use this source hierarchy:

| Rank | Source type | Use |
|---|---|---|
| 1 | Legislation and rules from official repositories | Acts, regulations, court rules, procedural obligations |
| 2 | Court practice directions, forms, registries, official guides | Filing, format, fees, registry practice |
| 3 | Reported judgments from AustLII, Jade, or court sites | Case law propositions |
| 4 | EDRM, The Sedona Conference, ISO/IEC standards, court technology practice notes | eDiscovery and forensic process |
| 5 | Legal commentary, vendor blogs, firm articles | Leads only; verify against ranks 1-4 |

Never present commentary, memory, or an AI-generated summary as legal authority. If a case, section, or practice note cannot be verified, mark it as unverified and keep it out of final court documents.

## Output Standards

Every court-facing deliverable should include:

- Matter name, court, file number if known, date, version, and status.
- Evidence IDs or Bates references for every factual assertion.
- Confidence labels for contested or inferred facts.
- A source/citation check for statutes, cases, rules, and practice directions.
- A final human-review checklist before filing, service, or disclosure.

## Cross-References

| Related Skill | Use when |
|---|---|
| `case-file-manager-wa` | SRL folder setup, evidence indexes, communication logs |
| `affidavit-court-preparation` | Affidavit drafting and hearing preparation |
| `csv-legal-analysis` | CSV, SMS, iMessage, and eDiscovery analysis |
| `wa-law-general` | General WA court hierarchy, legislation, filing and services |
| `wa-fvro` | WA FVRO-specific forms, objections, variations, and breach issues |

## Validation

Before treating skill or reference changes as complete, run the local framework validator. Prefer the containerized path when Docker is available so validation is not dependent on host Python state:

```bash
docker compose -f compose.skills.yml run --rm skills-validator
```

If Docker is unavailable, run:

```bash
uv run --project .maintenance/Skills-Framework-Reference skills-ref validate <skill-dir>
```
