# WA Evidence Law — Digital Evidence Admissibility

> **Jurisdiction**: Western Australia state courts + Federal courts sitting in WA
> **Currency rule**: Verify the current Evidence Act 1906 / Evidence Act 2025 commencement and transitional position before advising on WA evidence law.
> **Key sources**: Evidence Act 1906 (WA), Evidence Act 2025 (WA), Evidence Act 1995 (Cth), Electronic Transactions Act 2011 (WA)

---

## Table of Contents

1. [WA Evidence Legislation Transition](#1-wa-evidence-legislation-transition)
2. [Evidence Act 1995 (Cth) — Federal Provisions](#2-evidence-act-1995-cth--federal-provisions)
3. [WA Electronic Transactions Act 2011](#3-wa-electronic-transactions-act-2011)
4. [WA Court Practice Directions](#4-wa-court-practice-directions)
5. [Chain of Custody Requirements](#5-chain-of-custody-requirements)
6. [Admissibility Decision Tree](#6-admissibility-decision-tree)
7. [Case Law Verification Rules](#7-case-law-verification-rules)
8. [ISO/IEC 27037:2012 Digital Forensics Standard](#8-isoiec-270372012-digital-forensics-standard)
9. [Authentication Affidavit Template](#9-authentication-affidavit-template)
10. [CSV-Specific Admissibility Checklist](#10-csv-specific-admissibility-checklist)

---

## 1. WA Evidence Legislation Transition

WA evidence law is in transition. The Evidence Act 2025 (WA) has been enacted. Official WA legislation notes indicate Part 1 commenced on assent and many substantive provisions commence by proclamation, while the Evidence Act 1906 (WA) may remain relevant depending on commencement, transitional provisions, the proceeding type, and the date evidence is tendered. Before producing court-facing advice, check `legislation.wa.gov.au` for the current Act, commencement proclamations, transitional provisions, and the court's applicable rules.

### Evidence Act 1906 — Section 79C

### Electronic Business Records

Where the Evidence Act 1906 applies, s 79C is a key provision for documentary evidence, business records, and statements derived from business records.

**Key Provision: s79C(2a)**
> "A statement in a document that has been derived from a business record" may be admitted if:
> - The underlying business record was created in the ordinary course of business
> - The derivation process is explained
> - The original record's reliability can be established

### Ordinary Course of Business Test

Courts distinguish between:
- **Admissible**: Records created as part of routine business operations (transaction logs, system-generated reports, automated exports, scheduled backups)
- **Potentially inadmissible**: One-off documents prepared specifically for legal discovery or subpoena response

**Practice point**: Do not assume a litigation-created export automatically satisfies s 79C. The safer path is to prove the underlying source database is a genuine business record and explain how the litigation export reproduces or derives from that source.

### Application to CSV Exports

A CSV export may satisfy the business-record pathway if:

```python
CSV_ADMISSIBILITY_S79C = {
    'source_is_business_record': True,       # Underlying database is genuine business record
    'created_in_ordinary_course': True,       # Not solely for litigation
    'export_process_documented': True,        # How the CSV was generated
    'witness_can_authenticate': True,         # Someone can confirm source reliability
    'integrity_preserved': True,              # Hash verification, no modifications
    'derivation_explained': True,             # SQL query, export parameters documented
}
```

### Risk Flags for CSV Evidence

```python
def assess_s79c_risks(metadata):
    """Flag business-record admissibility risks for a CSV export."""
    risks = []

    if metadata.get('created_for_litigation'):
        risks.append({
            'severity': 'HIGH',
            'issue': 'CSV created solely for litigation — may not meet ordinary course test',
            'authority': 'Check current WA evidence legislation; if Evidence Act 1906 applies, see s 79C',
            'mitigation': 'Prove the underlying system is a genuine business record and document the export/derivation process'
        })

    if not metadata.get('export_parameters_documented'):
        risks.append({
            'severity': 'MEDIUM',
            'issue': 'Export parameters not documented — derivation unclear',
            'mitigation': 'Document SQL query, filters, date range, user who ran export'
        })

    if metadata.get('contains_calculations'):
        risks.append({
            'severity': 'MEDIUM',
            'issue': 'CSV contains calculated/derived fields not in source system',
            'mitigation': 'Disclose all transformations; provide raw export alongside'
        })

    if not metadata.get('hash_verified'):
        risks.append({
            'severity': 'LOW',
            'issue': 'No hash verification — integrity not cryptographically proven',
            'mitigation': 'Compute SHA-256 at time of export; include in chain of custody'
        })

    return risks
```

---

## 2. Evidence Act 1995 (Cth) — Federal Provisions

### Section 48: Documentary Evidence — Copies

A copy produced by a device that reproduces document contents is admissible if the device was in proper working order and the copy was made in ordinary course of business.

**Application**: CSV export from a database export function qualifies as a copy produced by a device.

### Section 69: Business Records Exception

Documents prepared in the course of business are admissible as evidence of facts stated in them. Requirements:
- Business regularly records information of that type
- Recording made by person with direct knowledge (or automated system)
- Person/system acting under duty to make the record

### Section 146: Computer-Generated Evidence Presumption

**Key provision**: Where a document is produced by a process/device, the court presumes the device produced accurate output if it ordinarily does so when working properly.

**Practical effect**: No detailed expert testimony required to prove "the database works correctly." A witness may testify: "I exported using the standard function. No errors occurred."

**Strengthening authentication**: Hash verification and digital signatures defeat challenges to file integrity but are not strictly required under s146.

### Section 138: Illegally or Improperly Obtained Evidence

Evidence obtained in breach of law is NOT automatically inadmissible. Test:
> "Desirability of admitting the evidence outweighs the undesirability of the method of obtaining it."

**Factors considered** (s138(3)):
- Probative value of the evidence
- Importance of the evidence to the case
- Nature of the offence or subject matter
- Gravity of the impropriety
- Whether impropriety was deliberate or reckless
- Whether evidence obtained was within scope sought
- Difficulty in obtaining evidence lawfully

**Family law application**: Courts weigh child safety and severity of allegations heavily. Messages obtained from another party's device without consent may still be admitted if probative of harm to children.

```python
S138_ASSESSMENT = {
    'factors_favouring_admission': [
        'High probative value (direct evidence of the issue)',
        'Importance to child safety determination',
        'No other means to obtain this evidence',
        'Inadvertent or good-faith discovery',
        'Limited intrusion on privacy',
    ],
    'factors_against_admission': [
        'Deliberate privacy breach',
        'Evidence obtained through deception or coercion',
        'Could have been obtained lawfully (e.g., by subpoena)',
        'Minimal relevance to central issues',
        'Disproportionate invasion of privacy',
    ]
}
```

---

## 3. WA Electronic Transactions Act 2011

### General Principle
Evidence of a record or signature may not be excluded solely because it is in electronic form.

### Record Retention
Electronic records satisfy legal retention requirements "for evidentiary, audit, or like purposes" unless specific legislation prohibits electronic form.

**Implication**: CSV files, database exports, and electronic logs should not be rejected merely because they are electronic, but admissibility still depends on the applicable evidence law, relevance, authentication, hearsay/business-record pathway, and how the file was obtained.

---

## 4. WA Court Practice Directions

### Supreme & District Courts

Verify current practice directions and electronic evidence guides before filing or tendering digital evidence.

**Accepted document formats**:
- PDF (preferred for most documents)
- XML (transcripts)
- Excel (.xls/.xlsx) for spreadsheets and data
- CSV: Not explicitly listed — convert to Excel or provide as PDF table with metadata documentation

**Submission timeline**:
- Electronic evidence delivered at least **two days** before hearing
- Parties must **test evidence on court equipment** before hearing
- Media: PC format, DVD-Video, or USB drive (Series A plug)

### Magistrates Court (eLodgment since 23 September 2021)

**eCourts Portal**: All civil documents filed electronically.

**File format guidance**:
- Video: AVI, MP4, MOV (with codec specifications)
- Audio: MP3, WAV, AIFF
- Images: JPEG, PNG, TIFF
- Documents: PDF, Word, Excel
- CSV: Convert to Excel (.xlsx) or PDF table

### Practical Recommendations for CSV Evidence

```python
WA_COURT_SUBMISSION_CHECKLIST = [
    'Convert CSV to Excel (.xlsx) for court submission',
    'Include metadata sheet with: source system, export date, user, parameters',
    'Provide SHA-256 hash on separate cover sheet',
    'Test electronic media on court equipment at least 2 days before hearing',
    'If data is large, provide summary tables in PDF with full data on USB',
    'Include a legend/key for column names and codes',
    'Timestamps in AWST (UTC+8) unless otherwise noted',
]
```

---

## 5. Chain of Custody Requirements

### Digital Evidence Chain (WA Courts)

No specific WA statute alone supplies a complete chain-of-custody checklist for all digital evidence. Use chain-of-custody logs, hashing, audit trails, and ISO/IEC 27037-style principles as defensibility controls; do not describe ISO standards as binding law unless incorporated by order, contract, or expert evidence.

```python
CHAIN_OF_CUSTODY_RECORD = {
    'evidence_id': 'Unique identifier',
    'description': 'Description of the item',
    'source': 'Where/how the data was obtained',
    'custodian': 'Person responsible for the data',
    'actions': [
        {
            'date': 'YYYY-MM-DD HH:MM AWST',
            'action': 'What was done',
            'performed_by': 'Who did it',
            'hash_before': 'SHA-256 before action',
            'hash_after': 'SHA-256 after action (if applicable)',
            'notes': 'Any relevant notes',
        }
    ],
    'storage': 'Where/how the data is stored',
    'access_controls': 'Who has access and how it is controlled',
}
```

---

## 6. Admissibility Decision Tree

```python
def assess_admissibility(evidence_metadata, jurisdiction='wa_state'):
    """
    Structured admissibility assessment for CSV/digital evidence.

    Returns: dict with assessment results, risk flags, and recommendations.
    """
    assessment = {
        'jurisdiction': jurisdiction,
        'evidence_type': evidence_metadata.get('type', 'CSV export'),
        'checks': [],
        'risk_flags': [],
        'recommendation': '',
    }

    # Step 1: Relevance
    if evidence_metadata.get('relevance_to_issues'):
        assessment['checks'].append({'step': 'Relevance', 'status': 'PASS',
            'note': 'Content relevant to issues before the court'})
    else:
        assessment['checks'].append({'step': 'Relevance', 'status': 'FAIL',
            'note': 'Relevance not established — may be excluded'})
        assessment['risk_flags'].append('LOW_RELEVANCE')

    # Step 2: Authentication
    auth_strength = 'HIGH'
    if not evidence_metadata.get('hash_verified'):
        auth_strength = 'MEDIUM'
    if not evidence_metadata.get('witness_available'):
        auth_strength = 'LOW'
    assessment['checks'].append({'step': 'Authentication', 'status': auth_strength,
        'note': f'Authentication strength: {auth_strength}'})

    # Step 3: Business record test (s79C / s69)
    if evidence_metadata.get('ordinary_course_of_business'):
        assessment['checks'].append({'step': 'Business Record', 'status': 'PASS',
            'note': 'Created in ordinary course of business'})
    else:
        assessment['checks'].append({'step': 'Business Record', 'status': 'WARNING',
            'note': 'May not meet ordinary course test — document purpose of creation'})
        assessment['risk_flags'].append('BUSINESS_RECORD_RISK')

    # Step 4: Integrity
    if evidence_metadata.get('hash_verified') and evidence_metadata.get('chain_of_custody'):
        assessment['checks'].append({'step': 'Integrity', 'status': 'PASS',
            'note': 'Hash verified, chain of custody maintained'})
    else:
        assessment['checks'].append({'step': 'Integrity', 'status': 'WARNING',
            'note': 'Integrity not fully established — add hash verification'})

    # Step 5: Legal acquisition
    if evidence_metadata.get('legally_obtained', True):
        assessment['checks'].append({'step': 'Legal Acquisition', 'status': 'PASS'})
    else:
        assessment['checks'].append({'step': 'Legal Acquisition', 'status': 'WARNING',
            'note': 's138 balancing test applies — evidence may still be admitted'})
        assessment['risk_flags'].append('S138_REQUIRED')

    # Step 6: Completeness
    if evidence_metadata.get('complete_dataset'):
        assessment['checks'].append({'step': 'Completeness', 'status': 'PASS'})
    else:
        assessment['checks'].append({'step': 'Completeness', 'status': 'WARNING',
            'note': 'Partial dataset — document what is missing and why'})

    # Overall recommendation
    fails = sum(1 for c in assessment['checks'] if c['status'] == 'FAIL')
    warnings = sum(1 for c in assessment['checks'] if c['status'] == 'WARNING')

    if fails > 0:
        assessment['recommendation'] = 'CAUTION: One or more critical checks failed. Seek legal advice before tendering.'
    elif warnings > 1:
        assessment['recommendation'] = 'PROCEED WITH CARE: Multiple warnings. Document mitigations thoroughly.'
    else:
        assessment['recommendation'] = 'LIKELY ADMISSIBLE: Evidence appears to meet admissibility requirements.'

    return assessment
```

---

## 7. Case Law Verification Rules

Do not cite case law from memory in court-facing work. Before including any case:

1. Retrieve the full judgment from AustLII, Jade, or an official court site.
2. Confirm party names, neutral citation, court, date, and paragraph references.
3. Check whether the proposition is part of the ratio, not a headnote or secondary summary.
4. Confirm the decision has not been overturned, distinguished on the point, or superseded by statute.
5. Quote only short, necessary excerpts and keep a link or downloaded copy in the research folder.

For CSV and electronic evidence, first identify the applicable WA evidence legislation. If Evidence Act 1906 (WA) s 79C applies, a statement in a document may be admissible where it directly or indirectly reproduces, or is derived from, a genuine business record. Case law should be used to refine application only after verification.

---

## 8. ISO/IEC 27037:2012 Digital Forensics Standard

### Core Principles

The international standard for identification, collection, acquisition, and preservation of digital evidence:

1. **Relevance**: Evidence must relate to the matter
2. **Reliability**: Evidence must be trustworthy and accurate
3. **Sufficiency**: Evidence must be adequate to prove or disprove the point
4. **Auditability**: Process must be fully documented and reproducible

### Mapping to CSV Workflows

| ISO 27037 Stage | CSV Analysis Implementation |
|----------------|---------------------------|
| **Identification** | Profile dataset, identify relevant columns/rows |
| **Collection** | Hash original file, document source system |
| **Acquisition** | Create working copy, verify hash match |
| **Preservation** | Read-only original, version-controlled working copies |

---

## 9. Authentication Affidavit Template

For family law or civil proceedings where CSV evidence needs authentication:

```text
AUTHENTICATION STATEMENT

I, [FULL NAME], of [ADDRESS], state:

1. I am the [ROLE] at [ORGANISATION/POSITION].

2. I have access to [SYSTEM NAME], which is an electronic records system
   used in the ordinary course of [ORGANISATION]'s business to record
   [DESCRIPTION OF WHAT IT RECORDS].

3. On [DATE], I exported data from [SYSTEM NAME] using [EXPORT METHOD]
   covering the period [START DATE] to [END DATE].

4. The export parameters were: [DESCRIBE FILTERS, QUERIES, FIELDS].

5. The exported file is named [FILENAME] and has a SHA-256 hash value
   of [HASH VALUE], computed at the time of export.

6. I have not modified, edited, or altered the exported file since
   its creation.

7. To the best of my knowledge and belief, the exported data is a true
   and accurate representation of the records in [SYSTEM NAME] as at
   the date of export.

Sworn/affirmed at [PLACE] on [DATE].
```

---

## 10. CSV-Specific Admissibility Checklist

```python
def csv_admissibility_checklist(jurisdiction='wa_state'):
    """Generate jurisdiction-specific admissibility checklist for CSV evidence."""
    common = [
        {'item': 'SHA-256 hash computed before any processing', 'required': True},
        {'item': 'Source system identified and described', 'required': True},
        {'item': 'Export method documented (tool, parameters, user)', 'required': True},
        {'item': 'Chain of custody log maintained', 'required': True},
        {'item': 'Original file preserved unmodified', 'required': True},
        {'item': 'Working copies clearly labelled as copies', 'required': True},
        {'item': 'Column headers explained (legend/key provided)', 'required': True},
        {'item': 'Timestamps in stated timezone (AWST preferred)', 'required': True},
    ]

    if jurisdiction == 'wa_state':
        common.extend([
            {'item': 'Business record/statutory pathway checked under current WA evidence law', 'required': True},
            {'item': 'Witness available to authenticate source system', 'required': True},
            {'item': 'Court-required format checked (CSV/XLSX/PDF/native/eCourt bundle as directed)', 'required': True},
            {'item': 'Electronic presentation tested before hearing where technology will be used', 'required': True},
        ])
    elif jurisdiction == 'federal':
        common.extend([
            {'item': 'Current Federal Court discovery order/practice note/protocol checked', 'required': True},
            {'item': 'Metadata fields match agreed or court-approved protocol', 'required': True},
            {'item': 'Concordance DAT/OPT load file available', 'required': False},
            {'item': 'Proportionality analysis documented', 'required': True},
        ])
    elif jurisdiction == 'family_court':
        common.extend([
            {'item': 'Affidavit annexure/exhibit format checked against current applicable family law rules', 'required': True},
            {'item': 'Full thread context (not cherry-picked messages)', 'required': True},
            {'item': 'Deponent verification statement included', 'required': True},
            {'item': 'Child safety screening completed', 'required': True},
        ])

    return common
```
