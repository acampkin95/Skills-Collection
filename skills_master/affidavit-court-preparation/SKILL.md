---
name: affidavit-court-preparation
description: Use when preparing Australian court affidavits, chronologies, disclosure packs, annexures.
---

# Affidavit & Court Preparation

Specialist workflow for turning fragmented evidence, notes, messages, screenshots, and court documents into restrained Australian court-facing preparation materials. It supports factual drafting, chronology reconstruction, evidence organisation, hearing preparation, and print-ready bundles. It does not provide legal advice or predict outcomes.

## Source Quality Protocol

Use primary sources for law and procedure: current legislation, court rules, practice directions, court forms, and reported judgments from official court sites, AustLII, Jade, or equivalent legal databases. Use user evidence for facts, not memory or inference. Commentary can identify issues but must not be cited as authority unless verified against primary sources. Verify current forms, fees, and practice directions before finalising any court-facing document.

## When to Use

Use this skill for:

- drafting or refining affidavits and witness statements
- reconstructing chronologies from messages, emails, notes, PDFs, photos, or recollection
- preparing disclosure schedules, evidence indexes, annexure schedules, or exhibit lists
- organising digital evidence into court-facing, private-preparation, and review buckets
- preparing hearing summaries, oral notes, response prompts, and issue lists
- checking that court material is source-backed, neutral, coherent, and print-ready

Route to another skill when the task is primarily:

- WA FVRO law, Form 12, breach, objection, or variation/cancellation: use `wa-fvro`
- full legal matter lifecycle, Bates numbering, chain of custody, bundle freeze: use `legal-matter-ops`
- WA SRL folder creation and linting: use `case-file-manager-wa`
- CSV/message forensic analysis before drafting: use `csv-legal-analysis`

## Core Rule

Chronology first. Evidence second. Drafting third. Formatting fourth. Review last.

Do not polish a narrative before the source chronology and evidence map are understood. If a fact is unsupported, inferred, ambiguous, or recollection-only, label it that way.

## Standard Workflow

1. Inspect the supplied material set.
2. Classify material types and source quality.
3. Extract key dates, parties, incidents, communications, and source references.
4. Build a working chronology.
5. Identify ambiguity, contradictions, missing context, duplicates, and weak support.
6. Decide which outputs are actually needed.
7. Draft only from the chronology and evidence map.
8. Map key statements back to source records.
9. Run evidence, formatting, and adversarial review checks.
10. Present final outputs with unresolved issues, assumptions, and human-review flags.

## Working Objects

Create only the objects needed for the task:

| Object | Required Fields |
|---|---|
| Evidence inventory | item ID, title, source type, date, people, relevance, original/derivative status, context sufficiency, duplicate status, recommended use |
| Master chronology | chronology ID, date/time, event summary, people, source references, confidence, gap/ambiguity flag |
| Claim support matrix | claim ID, paragraph reference, claim summary, supporting sources, support strength, weakness notes |
| Issues register | issue ID, type, severity, description, affected source/section, recommended action, human-review flag |
| Handoff summary | task completed, assumptions, unresolved issues, sources relied on, confidence, next action |

## Evidence Labels

Use these labels consistently:

- `Confirmed`: directly supported by clear source material or uncontested documentary evidence
- `Probable`: strongly supported but partly inferential or context-dependent
- `Uncertain`: possible but not reliably established from current material
- `Unsupported`: not presently supported by the available source material

Use severity labels in issue registers:

- `Critical`: major unsupported assertion, serious contradiction, probable source mischaracterisation, or major print/filing defect
- `High`: important missing context, weak support for a key claim, repeated argumentative drafting, or annexure mismatch
- `Medium`: wording ambiguity, incomplete source linkage, moderate formatting inconsistency, or avoidable narrative confusion
- `Low`: minor style, repetition, or formatting cleanup

## Drafting Rules

All court-facing drafting must be:

- plain, formal, and restrained
- chronological unless a court-specific structure requires another order
- paragraph-numbered where appropriate
- source-backed where possible
- explicit about uncertainty, recollection, inference, and third-party information
- free of speculation, sarcasm, motive attribution, rhetorical accusation, and emotional padding

For relationship-related matters, separate:

- relationship background
- communication history
- incident facts
- post-separation conduct
- documentary support

Only assert a behavioural pattern where it is relevant and supported by dated instances or a clearly explained evidentiary basis.

## Evidence Handling Rules

Preserve source distinctions:

- original file
- exported file
- screenshot
- extracted/processed copy
- derived table or summary
- recollection-only material

For each important source, record provenance, date/time basis, context sufficiency, hash or stable identifier where available, and whether better source material should be requested.

## Validation Gates

Before presenting an affidavit, chronology, or bundle as refined or ready for review, check:

1. **Chronology integrity** - logical order, normalised dates, flagged contradictions and gaps.
2. **Evidence traceability** - key assertions link to source material where possible; unsupported and inferred claims are labelled.
3. **Drafting discipline** - neutral tone, concise paragraphs, no speculation or argumentative framing.
4. **Formatting and presentation** - stable numbering, A4-safe layout, consistent annexure/exhibit references, black-and-white-safe tables.
5. **Adversarial review** - overstatement, ambiguity, duplication, weak points, and likely challenge areas are identified.

If a gate fails, correct what can be corrected and report unresolved issues rather than hiding them.

## Output Types

Depending on the request, produce:

- draft affidavit or witness statement
- master chronology
- event-to-evidence table
- evidence index
- annexure or exhibit schedule
- disclosure summary
- hearing issue notes
- one-page core summary
- oral script or response prompts
- print bundle structure
- review report and human-review checklist

## Hearing Notes

For hearing preparation, create three layers where useful:

| Layer | Contents |
|---|---|
| One-page core summary | parties, issue before the court, short factual position, outcome sought |
| Issue notes | issue title, explanation, key supporting facts, evidence references, likely challenge point |
| Response prompts | short factual answer, linked evidence reference, caution note where restraint is needed |

Keep hearing notes short enough for a person to use under pressure.

## Print Bundle Defaults

Unless a court order or filing requirement says otherwise, default to:

- A4 format
- single-sided print suitability
- black text and plain headings
- stable paragraph numbering
- plain tables with black borders and white cells
- no decorative styling
- no unnecessary metadata or export clutter

Separate bundle material into:

- `ForAllParties`: final affidavit, final annexures/exhibits, disclosure schedule if appropriate, court-facing documents
- `PrivatePreparation`: annotated chronology, hearing notes, issue notes, internal response prompts
- `ToBeReviewed`: weak evidence, unresolved drafts, missing-source placeholders, legal/factual confirmation items

## Default Folder Guidance

For standalone affidavit preparation matters:

```text
/01_Source_Materials
/02_Working_Evidence_Inventory
/03_Chronology
/04_Affidavit
/05_Disclosure
/06_Annexures_Exhibits
/07_Hearing_Prep
/08_Print_Bundle
/09_Review_Reports
/90_Archive
/99_AI_Workspace
```

For active WA case folders or full matter operations, prefer the folder structures in `case-file-manager-wa` or `legal-matter-ops`.

## Reference Files

| File | Load when |
|---|---|
| `references/affidavit-templates.md` | Drafting affidavit structures and examples, especially WA Magistrates Court or FCFCOA contexts |
| `references/evidence-standards.md` | Preparing evidence indexes, annexures, chain of custody, and print-ready evidence standards |
| `references/court-formats.md` | Checking filing methods, document requirements, and form sources for MCWA, FCFCOA, and District Court |

## Common Mistakes

- Drafting from emotional narrative before building the chronology.
- Treating screenshots as equivalent to original exports without noting limits.
- Presenting recollection, inference, or third-party information as direct fact.
- Relying on isolated messages without surrounding context.
- Using legal conclusions where factual observations are needed.
- Marking material final before evidence, formatting, and adversarial review are complete.

## Validation

After editing this skill or its references, run:

```bash
docker compose -f compose.skills.yml run --rm skills-validator
```

Fallback:

```bash
uv run --project .maintenance/Skills-Framework-Reference skills-ref validate affidavit-court-preparation
```

## Cross-References

| Related Skill | Use when |
|---|---|
| `case-file-manager-wa` | Organising WA SRL case folders, naming documents, linting folder structure, evidence/comms indexes |
| `legal-matter-ops` | Full matter lifecycle, chain of custody, Bates numbering, bundle freeze, deadline registers |
| `wa-fvro` | FVRO-specific affidavit drafting, objection, variation/cancellation, Form 12, breach issues |
| `wa-law-general` | General WA court hierarchy, forms, fees, legal services, legislation research |
| `csv-legal-analysis` | Analysing CSV/message data for forensic evidence extraction and classification |
| `reportlab-python` | Generating PDF outputs from Python |
| `pdfkit-node` | Generating PDF outputs from Node.js |

## Disclaimer

This skill provides document preparation and organisational assistance only. It is not legal advice. All court-facing outputs should be reviewed by a qualified Australian legal practitioner before filing or service. Seek independent legal advice from a WA lawyer, Legal Aid WA, or a community legal centre.
