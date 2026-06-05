---
name: csv-legal-analysis
description: Use when analysing CSV, SMS, iMessage, email exports, database extracts, or tabular evidence.
---

# CSV Legal Analysis & eDiscovery

> **CRITICAL PRINCIPLE**: Never modify original data files. All analysis works on copies or in-memory. Original file integrity must be preserved and documented from the first step.

> **DISCLAIMER**: This skill supports legal analysis workflows but does not constitute legal advice. All analysis outputs should be reviewed by qualified legal practitioners before use in proceedings.

> **AI TRANSPARENCY**: When AI/LLM classification is used, every output must include the model name, prompt hash, and linked source record IDs. AI outputs are candidates flagged for human verification, not conclusions.

## Source Quality Protocol

Use primary and standards-based sources for legal and eDiscovery propositions:

| Topic | Preferred sources |
|---|---|
| WA evidence/admissibility | `legislation.wa.gov.au`; AustLII/Jade/court judgments |
| Federal/family law evidence | `legislation.gov.au`; `fcfcoa.gov.au`; Family Court WA where applicable |
| eDiscovery/TAR | Court practice notes, EDRM materials, The Sedona Conference publications, reported cases |
| Digital forensics | ISO/IEC 27037 principles, tool audit logs, hash manifests, vendor-neutral documentation |

Do not rely on blogs, marketing material, or unverified case summaries for legal propositions. Use them only to locate primary sources. If a case or section cannot be verified, label it as unverified and omit it from court-facing outputs.

## Overview

Systematic analysis of CSV/tabular data for legal evidence, eDiscovery, structured document review, forensic investigation, and **SMS/iMessage forensic analysis**. Designed for datasets from small (hundreds of rows) to very large (1M+ rows) with appropriate tool selection at each scale.

### Workflow Summary

| Workflow | Use When | Reference File |
|----------|----------|----------------|
| **Ingest & Profile** | First contact with any dataset — understand what you have | `analysis-workflows.md` |
| **Systematic Analysis** | Pattern detection, timelines, entity extraction, statistical review | `analysis-workflows.md` |
| **eDiscovery Review** | Keyword search, responsiveness coding, privilege review, production | `ediscovery-protocols.md` |
| **Evidence Production** | Chain of custody, hashing, Bates numbering, court-ready output | `evidence-standards.md` |
| **SMS/iMessage Forensics** | Mobile messaging analysis, family law, DV evidence | `sms-imessage-analysis.md` |
| **WA Evidence Law** | Admissibility assessment, WA court requirements, Evidence Act transition and business-record checks | `wa-evidence-law.md` |
| **Large Dataset Processing** | Datasets >100K rows, DuckDB/Polars, streaming, parallel processing | `large-dataset-processing.md` |
| **Family Law Evidence** | FCFCOA requirements, affidavit annexures, family violence patterns | `family-law-evidence.md` |
| **Coercive Control Analysis** | Research-backed pattern detection, ANROWS frameworks, risk assessment | `coercive-control-frameworks.md` |

---

## Quick-Start Decision Tree

```
Dataset received
│
├─ How many rows?
│  ├─ <100K rows → Use pandas (standard workflow)
│  ├─ 100K–1M rows → Use DuckDB or Polars (see large-dataset-processing.md)
│  └─ >1M rows → Use DuckDB streaming + Polars lazy eval (MANDATORY)
│
├─ What type of data?
│  ├─ Email/communications → eDiscovery workflow (ediscovery-protocols.md)
│  ├─ SMS/iMessage/WhatsApp → SMS forensics pipeline (sms-imessage-analysis.md)
│  ├─ Financial transactions → Financial analysis (analysis-workflows.md §10, §12)
│  ├─ Access/audit logs → Access log patterns (analysis-workflows.md §11)
│  └─ Mixed/unknown → Profile first (analysis-workflows.md §2)
│
├─ What jurisdiction?
│  ├─ WA state courts → Check Evidence Act 1906 / Evidence Act 2025 transition and applicable business-record provisions (wa-evidence-law.md)
│  ├─ Federal Court → Evidence Act 1995, GPN-TECH (ediscovery-protocols.md §14)
│  ├─ Family Court (FCFCOA) → Family law evidence standards (family-law-evidence.md)
│  └─ Multiple/unknown → Apply strictest standard
│
└─ Is this family law / DV matter?
   ├─ YES → Read coercive-control-frameworks.md BEFORE analysis
   ├─ YES + children involved → Enable mandatory reporting flags
   └─ NO → Standard workflow
```

---

## Step 0: Environment & Tool Selection

### Install Dependencies (Scale-Appropriate)

Use a project virtual environment or `uv`/`pipx` where possible. Do not install legal-analysis dependencies into a managed system Python.

```python
# ALWAYS needed
# pip install pandas chardet hashlib

# For datasets >100K rows (RECOMMENDED for all legal work)
# pip install duckdb>=0.10.0 polars>=0.20.0 pyarrow>=15.0.0

# For near-duplicate detection (>50K documents)
# pip install sentence-transformers faiss-cpu

# For data validation
# pip install pandera pydantic

# For PDF report generation
# pip install reportlab

# For parallel batch processing
# pip install ray
```

### Tool Selection Matrix

| Dataset Size | Primary Tool | Secondary Tool | Notes |
|-------------|-------------|---------------|-------|
| <10K rows | pandas | — | Standard workflow sufficient |
| 10K–100K rows | pandas or Polars | DuckDB for complex SQL | Polars if memory constrained |
| 100K–1M rows | DuckDB | Polars | DuckDB for SQL, Polars for transforms |
| 1M–10M rows | DuckDB streaming | Polars lazy | Never load full dataset into pandas |
| >10M rows | DuckDB + chunked | Polars sink | Streaming mandatory, chunked exports |

---

## Step 1: Ingest & Integrity

**ALWAYS start here. No exceptions.**

```python
import hashlib
import os
import json
from datetime import datetime, timezone

def establish_integrity(filepath):
    """Hash file BEFORE any processing. This is the forensic baseline."""
    h = hashlib.sha256()
    file_size = os.path.getsize(filepath)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)

    record = {
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'file_size_bytes': file_size,
        'hash_algorithm': 'SHA-256',
        'hash_value': h.hexdigest(),
        'computed_at': datetime.now(timezone.utc).isoformat(),
        'computed_by': 'csv-legal-analysis-skill',
    }

    # Write integrity record
    log_path = filepath + '.integrity.json'
    with open(log_path, 'w') as f:
        json.dump(record, f, indent=2)

    print(f"SHA-256: {record['hash_value']}")
    print(f"Size: {file_size:,} bytes")
    print(f"Integrity record: {log_path}")
    return record
```

→ See `evidence-standards.md` for full chain of custody framework
→ See `analysis-workflows.md` for CSV loading, encoding detection, profiling

---

## Step 2: Profile Dataset

```python
def quick_profile(filepath, use_duckdb=False):
    """Profile a CSV — auto-selects tool based on file size."""
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

    if file_size_mb > 100 or use_duckdb:
        return _profile_duckdb(filepath)
    else:
        return _profile_pandas(filepath)

def _profile_duckdb(filepath):
    """Profile large CSVs using DuckDB (streaming, low memory)."""
    import duckdb
    conn = duckdb.connect(':memory:')
    conn.execute(f"""
        CREATE TABLE data AS
        SELECT * FROM read_csv_auto('{filepath}', sample_size=-1)
    """)
    row_count = conn.execute("SELECT COUNT(*) FROM data").fetchone()[0]
    col_info = conn.execute("DESCRIBE data").fetchall()
    print(f"Rows: {row_count:,}")
    print(f"Columns: {len(col_info)}")
    for col in col_info:
        print(f"  {col[0]}: {col[1]}")
    return conn, row_count
```

→ See `analysis-workflows.md` §2 for comprehensive profiling
→ See `large-dataset-processing.md` for DuckDB/Polars profiling at scale

---

## Step 3: Analyse (Choose Workflow)

Based on the data type and matter context, select the appropriate workflow from the reference files. Each reference file contains complete, production-ready code.

### For eDiscovery / Document Review:
1. Boolean keyword search with KWIC → `ediscovery-protocols.md` §2
2. Responsiveness coding → `ediscovery-protocols.md` §3
3. Privilege detection → `ediscovery-protocols.md` §4
4. TAR/predictive coding suitability and validation → `ediscovery-protocols.md` §13
5. Production preparation → `ediscovery-protocols.md` §8

### For SMS/Messaging Forensics:
1. Source detection → `sms-imessage-analysis.md` §2
2. Canonical mapping → `sms-imessage-analysis.md` §2.2
3. Participant mapping → `sms-imessage-analysis.md` §3
4. Classification pipeline → `sms-imessage-analysis.md` §6
5. Thread summarisation → `sms-imessage-analysis.md` §7

### For Family Law / DV Matters:
1. Read `coercive-control-frameworks.md` FIRST
2. Apply coercive control indicator detection
3. Enable mandatory reporting flags
4. Follow FCFCOA affidavit annexure format → `family-law-evidence.md`

### For Financial Analysis:
1. Transaction analysis → `analysis-workflows.md` §10
2. Benford's Law screening → `analysis-workflows.md` §12
3. Currency normalisation → `analysis-workflows.md` §16

---

## Step 4: Admissibility Assessment

**Before producing any evidence output**, run the admissibility checklist:

```python
ADMISSIBILITY_CHECKLIST = {
    'wa_state_court': {
        'legislation': 'Check Evidence Act 1906 (WA) / Evidence Act 2025 (WA) transition and applicable business-record provisions',
        'checks': [
            'Source is genuine business record (ordinary course of business)',
            'Export process documented (timestamp, user, parameters, hash)',
            'Chain of custody preserved (access controls, version control)',
            'Witness can confirm source system reliability',
            'Underlying source record is a genuine business record; export/derivation process documented',
        ]
    },
    'federal_court': {
        'legislation': 'Evidence Act 1995 (Cth) ss 48, 69, 146',
        'checks': [
            's48: Copy produced by device in proper working order',
            's69: Business record created in ordinary course of business',
            's146: Computer presumed to produce accurate output',
            'Hash verification strengthens authentication',
            'Current Federal Court discovery orders/practice notes/protocol checked for eDiscovery',
        ]
    },
    'family_court': {
        'legislation': 'Family Law Act 1975, Evidence Act 1995, Family Court Rules 2021',
        'checks': [
            'Relevance to parenting/property/family violence issue',
            'Authentication: sender/recipient identity clear',
            'Completeness: full thread context (not cherry-picked)',
            'Legal acquisition (s138 balancing if obtained improperly)',
            'Affidavit annexure/exhibit format checked against current applicable family law rules',
            'If children involved: s69ZT flexibility applies',
        ]
    },
    'fvro': {
        'legislation': 'Restraining Orders Act 1997 (WA) ss 44A-44C',
        'checks': [
            'Flexible evidence standard (s44A)',
            'Pattern of behaviour demonstrable from messages',
            'Technology-facilitated abuse recognised (FVLRA 2020)',
            'Metadata preserved where available',
        ]
    }
}
```

→ See `wa-evidence-law.md` for full WA admissibility framework
→ See `family-law-evidence.md` for family court specific requirements

---

## Step 5: Produce Evidence-Grade Output

### Output Types

| Output | Format | Use Case | Reference |
|--------|--------|----------|-----------|
| **Evidence bundle** | DOCX/PDF | Court filing, affidavit annexure | `evidence-standards.md` §6, §8 |
| **Privilege log** | CSV | Discovery production | `ediscovery-protocols.md` §4 |
| **Production set** | DAT/OPT | Concordance/Relativity import | `ediscovery-protocols.md` §8 |
| **Timeline** | CSV/PDF | Chronological event reconstruction | `analysis-workflows.md` §4 |
| **Statistical report** | PDF/MD | Expert evidence, court submission | `evidence-standards.md` §8 |
| **Coercive control report** | DOCX | Family law affidavit support | `coercive-control-frameworks.md` |
| **Mandatory reporting flags** | JSON/CSV | Child safety screening | `family-law-evidence.md` |

### Load File Generation (Concordance DAT/OPT)

```python
def generate_concordance_dat(df, output_dir, bates_prefix='PROD'):
    """Generate Concordance-compatible DAT and OPT load files."""
    DELIM = '\x14'  # Concordance field delimiter (¶)
    QUOTE = '\xfe'   # Concordance text qualifier (þ)
    NEWLINE = '\x0a'  # Concordance newline within fields

    # DAT file
    dat_path = os.path.join(output_dir, 'load_file.dat')
    opt_path = os.path.join(output_dir, 'load_file.opt')

    # Standard metadata fields
    fields = ['BATES_BEG', 'BATES_END', 'CUSTODIAN', 'DATE_SENT',
              'FROM', 'TO', 'CC', 'SUBJECT', 'FILE_TYPE', 'SHA256_HASH']

    with open(dat_path, 'w', encoding='utf-8') as dat:
        # Header row
        dat.write(DELIM.join(f'{QUOTE}{f}{QUOTE}' for f in fields) + '\n')

        for i, (_, row) in enumerate(df.iterrows(), 1):
            bates = f"{bates_prefix}{str(i).zfill(7)}"
            values = [
                bates,                                    # BATES_BEG
                bates,                                    # BATES_END
                str(row.get('custodian', '')),            # CUSTODIAN
                str(row.get('date_sent', '')),            # DATE_SENT
                str(row.get('from', '')),                 # FROM
                str(row.get('to', '')),                   # TO
                str(row.get('cc', '')),                   # CC
                str(row.get('subject', '')),              # SUBJECT
                str(row.get('file_type', 'CSV')),         # FILE_TYPE
                str(row.get('_hash', '')),                # SHA256_HASH
            ]
            dat.write(DELIM.join(f'{QUOTE}{v}{QUOTE}' for v in values) + '\n')

    print(f"DAT file: {dat_path} ({i:,} records)")
    return dat_path
```

→ See `ediscovery-protocols.md` for full production workflow including OPT files and Relativity format

---

## Step 6: Verify & Document

**Every analysis session must end with verification:**

```python
def final_verification(original_hash_record, output_files, analysis_log):
    """Final verification before delivering results."""
    checks = {
        'original_file_integrity': verify_hash(original_hash_record),
        'output_files_exist': all(os.path.exists(f) for f in output_files),
        'audit_trail_complete': len(analysis_log) > 0,
        'no_original_modification': True,  # Confirm no writes to source
    }

    passed = all(checks.values())
    print(f"Verification: {'PASSED' if passed else 'FAILED'}")
    for check, result in checks.items():
        print(f"  {'✓' if result else '✗'} {check}")

    return passed
```

## Skill Validation

After editing this skill or its references, prefer the Docker-backed validator:

```bash
docker compose -f compose.skills.yml run --rm skills-validator
```

Fallback:

```bash
uv run --project .maintenance/Skills-Framework-Reference skills-ref validate csv-legal-analysis
```

---

## Reference Files

All detailed code, workflows, and legal standards are in the `references/` directory:

| File | Contents | Size |
|------|----------|------|
| `analysis-workflows.md` | Data loading, profiling, dedup, timelines, entity extraction, statistics, anomaly detection, Benford's Law, network analysis, document clustering, currency normalisation | Core analysis |
| `ediscovery-protocols.md` | Keyword search, KWIC, responsiveness coding, privilege review, categorisation, custodian mapping, QC sampling, production, TAR, EDRM, load file generation, AI review guidance | eDiscovery |
| `evidence-standards.md` | Hashing, chain of custody, metadata preservation, audit trails, working copies, production output, privilege logs, evidence-grade reports | Evidence integrity |
| `sms-imessage-analysis.md` | Source detection, canonical mapping, participant mapping, data model, JSON schemas, classification pipeline, thread summarisation, chronology builder, family law playbook | SMS forensics |
| `wa-evidence-law.md` | WA Evidence Act 1906 / Evidence Act 2025 transition, Evidence Act 1995 (Cth), WA court practice directions, admissibility decision tree, case law verification rules, Electronic Transactions Act 2011, ISO/IEC 27037 | WA law |
| `large-dataset-processing.md` | DuckDB, Polars, PyArrow, streaming processing, parallel batch classification, data validation, memory-mapped files, vector similarity, efficient regex | Scale tools |
| `family-law-evidence.md` | FCFCOA practice directions, Family Law Rules 2021, affidavit annexure standards, s69ZT-69ZX children's evidence, s138 illegally obtained evidence, mandatory reporting, Surveillance Devices Act 1998 (WA) | Family law |
| `coercive-control-frameworks.md` | Stark framework, ANROWS technology-facilitated abuse research, DASH risk assessment, Duluth model mapping, coercive control indicators in messaging, scoring rubric, WA FVLRA 2020 | DV analysis |

## Cross-References to Other Skills

| Related Skill | Use when |
|---------------|----------|
| `legal-matter-ops` | Full 15-phase legal matter lifecycle — use chain of custody, Bates numbering, and bundle freeze from this skill |
| `affidavit-court-preparation` | Converting analysis outputs into affidavit-ready format, chronology, annexures |
| `case-file-manager-wa` | Organising case folders, evidence indexes, communications logs |
| `wa-fvro` | FVRO-specific evidence analysis, s.44A-44C flexible evidence standard |
| `wa-law-general` | WA court hierarchy, legislation, legal services |
| `reportlab-python` | Generating statistical reports and evidence bundles as PDF from Python |
| `pdfkit-node` | Generating statistical reports and evidence bundles as PDF from Node.js |
