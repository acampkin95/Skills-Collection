---
name: legal-matter-ops
description: Runs file operations for Australian court matters with WA court practice as the default, covering the intake-to-filing workflow, matter folder structure and versioning, chronology and affidavit templates, eDiscovery and privilege review, digital evidence admissibility, SMS and iMessage forensics, DOCX and PDF output, and internal review controls. Use when organising a legal matter, preparing a court-facing evidence bundle, running eDiscovery or privilege review, or building a versioned matter folder. Does not provide legal advice.
version: "1.0.0"
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
| Large document sets and dataset processing | `references/large-dataset-processing.md`; read when a matter has too much material to review manually |
| Interpersonal and relationship-matter hardening | `references/interpersonal-hardening.md`; read when a matter involves interpersonal conflict and extra review is needed |
| Multi-agent system design for matter operations | `references/agent-architecture.md`; read when splitting matter work across agents |
| Example prompts for this engine | `references/example-prompts.md`; read when shaping a request to this skill |

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

After changing this skill or its references, run the repository validator from the repository root (maintainers only; not needed for matter work):

```bash
python3 SkillsFramework/scripts/validate_skills.py --verbose
```

Earlier versions of this skill pointed at a Docker compose file and a `.maintenance/` reference project; neither is present in this repository.
