# Evidence Standards — Chain of Custody, Integrity & Production

> **DISCLAIMER**: These standards support legal analysis workflows and assist in preparing evidence-ready materials. They do not constitute legal advice and should be reviewed by qualified legal practitioners before use in proceedings. Evidence admissibility is determined by the court.

---

## Table of Contents

1. [File Integrity — Hashing Workflow](#1-file-integrity--hashing-workflow)
2. [Chain of Custody Framework](#2-chain-of-custody-framework)
3. [Metadata Preservation Standards](#3-metadata-preservation-standards)
4. [Audit Trail Generation](#4-audit-trail-generation)
5. [Working Copy Management](#5-working-copy-management)
6. [Production Output Standards](#6-production-output-standards)
7. [Privilege Log Standards](#7-privilege-log-standards)
8. [Evidence-Grade Report Template](#8-evidence-grade-report-template)
9. [Integrity Verification — Final Check](#9-integrity-verification--final-check)

---

## 1. File Integrity — Hashing Workflow

Hash verification establishes and maintains a mathematically verifiable record that data was not altered. Always complete Steps 1.1–1.3 before any other processing.

### Step 1.1 — Compute Baseline Hash (Before First Read)

```python
import hashlib
import os
from datetime import datetime, timezone

def hash_file(filepath: str, algorithm: str = 'sha256') -> dict:
    """
    Compute a cryptographic hash of a file.
    Returns a dict suitable for inclusion in chain of custody log.
    """
    h = hashlib.new(algorithm)
    file_size = os.path.getsize(filepath)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return {
        'filepath': os.path.abspath(filepath),
        'filename': os.path.basename(filepath),
        'file_size_bytes': file_size,
        'algorithm': algorithm.upper(),
        'hash_value': h.hexdigest(),
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
    }

# Usage — ALWAYS run before pd.read_csv()
baseline = hash_file('/path/to/original.csv')
print(f"BASELINE HASH ({baseline['algorithm']}): {baseline['hash_value']}")
print(f"File: {baseline['filename']} | Size: {baseline['file_size_bytes']:,} bytes")
```

### Step 1.2 — Verify Working Copy Hash

After making a copy for analysis, verify the copy matches the original:

```python
def verify_copy_integrity(original_hash_dict: dict, copy_filepath: str) -> bool:
    """Verify a copy against a previously computed baseline hash."""
    copy_hash = hash_file(copy_filepath, original_hash_dict['algorithm'].lower())
    match = copy_hash['hash_value'] == original_hash_dict['hash_value']
    status = 'VERIFIED — MATCH' if match else 'FAILED — MISMATCH'
    print(f"Copy integrity check: {status}")
    if not match:
        print(f"  Original: {original_hash_dict['hash_value']}")
        print(f"  Copy:     {copy_hash['hash_value']}")
        raise ValueError("INTEGRITY FAILURE: Copy does not match original. Do not proceed.")
    return match

import shutil
copy_path = '/path/to/working_copy.csv'
shutil.copy2('/path/to/original.csv', copy_path)
verify_copy_integrity(baseline, copy_path)
```

### Step 1.3 — Write Hash Baseline File

```python
import json

def write_hash_baseline(hash_dict: dict, output_path: str):
    """Write hash baseline to a text file for the chain of custody record."""
    with open(output_path, 'w') as f:
        f.write("=== FILE INTEGRITY BASELINE ===\n\n")
        for key, value in hash_dict.items():
            f.write(f"{key}: {value}\n")
        f.write("\nThis baseline was recorded before any data was loaded or processed.\n")
        f.write("Any change to the original file will produce a different hash value.\n")

write_hash_baseline(baseline, 'output/01_integrity/hash_baseline.txt')
```

### Hash Algorithm Standards

| Algorithm | Use When | Notes |
|-----------|----------|-------|
| **SHA-256** | Default for all matters | 64-character hex digest; widely accepted in courts |
| **SHA-512** | High-value/sensitive matters | Greater collision resistance; larger hash |
| **MD5** | Legacy compatibility only | Do NOT use as primary integrity mechanism |

Always record both SHA-256 and the file's original SHA-256 in the chain of custody.

---

## 2. Chain of Custody Framework

The chain of custody documents every person who accessed the data, every tool used, and every transformation applied. It must be started at first contact and maintained throughout the analysis.

### Chain of Custody Log Class

```python
import json
from datetime import datetime, timezone

class ChainOfCustodyLog:
    """
    Maintains a tamper-evident log of all operations performed on a dataset.
    Entries are append-only. Save to file regularly.
    """

    def __init__(self, matter_ref: str, analyst_id: str, original_hash: dict):
        self.matter_ref = matter_ref
        self.analyst_id = analyst_id
        self.created_utc = datetime.now(timezone.utc).isoformat()
        self.entries = []
        # Record initial custody entry
        self.add_entry(
            phase='INGEST',
            action='BASELINE_HASH',
            detail=f"SHA-256 hash computed before first read: {original_hash['hash_value']}",
            source_file=original_hash['filepath']
        )

    def add_entry(self, phase: str, action: str, detail: str,
                  source_file: str = None, rows_affected: int = None,
                  output_file: str = None):
        entry = {
            'entry_id': len(self.entries) + 1,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'analyst_id': self.analyst_id,
            'phase': phase,
            'action': action,
            'detail': detail,
        }
        if source_file: entry['source_file'] = source_file
        if rows_affected is not None: entry['rows_affected'] = rows_affected
        if output_file: entry['output_file'] = output_file
        self.entries.append(entry)
        return entry

    def save(self, output_path: str):
        """Save the full log to a JSON file (authoritative) and markdown summary."""
        log_data = {
            'matter_reference': self.matter_ref,
            'analyst_id': self.analyst_id,
            'log_created_utc': self.created_utc,
            'last_updated_utc': datetime.now(timezone.utc).isoformat(),
            'total_entries': len(self.entries),
            'entries': self.entries
        }
        # JSON (machine-readable, authoritative)
        with open(output_path.replace('.md', '.json'), 'w') as f:
            json.dump(log_data, f, indent=2)
        # Markdown (human-readable)
        with open(output_path, 'w') as f:
            f.write(f"# Chain of Custody Log\n\n")
            f.write(f"**Matter Reference**: {self.matter_ref}\n")
            f.write(f"**Analyst ID**: {self.analyst_id}\n")
            f.write(f"**Log Created (UTC)**: {self.created_utc}\n")
            f.write(f"**Total Entries**: {len(self.entries)}\n\n")
            f.write("---\n\n")
            for e in self.entries:
                f.write(f"## Entry {e['entry_id']} — {e['timestamp_utc']}\n\n")
                f.write(f"- **Phase**: {e['phase']}\n")
                f.write(f"- **Action**: {e['action']}\n")
                f.write(f"- **Analyst**: {e['analyst_id']}\n")
                f.write(f"- **Detail**: {e['detail']}\n")
                if e.get('source_file'): f.write(f"- **Source file**: {e['source_file']}\n")
                if e.get('rows_affected') is not None: f.write(f"- **Rows affected**: {e['rows_affected']:,}\n")
                if e.get('output_file'): f.write(f"- **Output file**: {e['output_file']}\n")
                f.write("\n")

# Usage
coc = ChainOfCustodyLog(
    matter_ref='MATTER-2026-001',
    analyst_id='ANALYST-01',
    original_hash=baseline
)

# Log every operation as you proceed
coc.add_entry('INGEST', 'CSV_LOAD', 'Loaded working copy with encoding utf-8-sig',
              source_file=copy_path, rows_affected=15423)

coc.add_entry('ANALYSIS', 'DEDUPLICATION', '47 exact duplicate rows identified and flagged',
              rows_affected=47)

coc.add_entry('EDISCOVERY', 'KEYWORD_SEARCH',
              'Boolean search run: terms=(fraud OR "false invoice") AND date:[2024-01-01 TO 2025-12-31)',
              rows_affected=312, output_file='output/04_ediscovery/keyword_hits.csv')

coc.save('output/01_integrity/chain_of_custody.md')
```

### Required Log Fields per Entry

| Field | Required | Description |
|-------|----------|-------------|
| `entry_id` | Yes | Sequential integer; never reused |
| `timestamp_utc` | Yes | ISO 8601 UTC timestamp |
| `analyst_id` | Yes | Name or ID of the analyst performing the action |
| `phase` | Yes | INGEST / ANALYSIS / EDISCOVERY / PRODUCTION |
| `action` | Yes | Specific action type (e.g., CSV_LOAD, KEYWORD_SEARCH, EXPORT) |
| `detail` | Yes | Human-readable description of what was done |
| `source_file` | If applicable | Input file path for this operation |
| `rows_affected` | If applicable | Number of rows processed, filtered, or output |
| `output_file` | If applicable | Path of any file created by this operation |

### Actions to Log (Mandatory)

Every one of these operations MUST be logged:

- Initial file hash computation
- Creating a working copy
- Loading data into memory (`pd.read_csv`)
- Any filter applied (date range, custodian, keyword)
- Any column added to the dataset (coding columns, hash columns)
- Any row removed or flagged (deduplication, out-of-scope)
- Every search query run
- Every responsiveness/privilege coding operation
- Every file exported
- Every hash verification step

---

## 3. Metadata Preservation Standards

Original metadata must be preserved alongside any parsed or normalised versions. Never overwrite original field values.

### Metadata Extraction at Ingest

```python
import os
import hashlib
from datetime import datetime, timezone

def extract_file_metadata(filepath: str) -> dict:
    """
    Extract and preserve all available file system metadata.
    This forms part of the evidence packaging record.
    """
    stat = os.stat(filepath)
    return {
        'original_filename': os.path.basename(filepath),
        'original_filepath': os.path.abspath(filepath),
        'file_size_bytes': stat.st_size,
        'file_size_human': f"{stat.st_size / 1024:.1f} KB" if stat.st_size < 1048576 else f"{stat.st_size / 1048576:.1f} MB",
        'created_timestamp': datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
        'modified_timestamp': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        'accessed_timestamp': datetime.fromtimestamp(stat.st_atime, tz=timezone.utc).isoformat(),
        'sha256_hash': hash_file(filepath)['hash_value'],
    }

file_metadata = extract_file_metadata('/path/to/original.csv')
```

### Column Preservation Rules

When normalising or transforming data columns, always preserve originals:

```python
import pandas as pd

df = pd.read_csv(copy_path, encoding='utf-8-sig', low_memory=False)

# DATE NORMALISATION — preserve original, add parsed version
if 'date' in df.columns:
    df['_original_date'] = df['date'].copy()          # Preserved original
    df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
    df['date_iso8601'] = df['date_parsed'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

# TEXT NORMALISATION — preserve original
if 'email' in df.columns:
    df['_original_email'] = df['email'].copy()
    df['email_normalised'] = df['email'].str.lower().str.strip()

# Naming convention: prefix preserved originals with _original_
# This makes them easily identifiable in the production output
```

### Metadata Fields to Preserve / Document

| Metadata Category | Fields to Record |
|-------------------|-----------------|
| **File system** | Original filename, full path, file size, created/modified/accessed timestamps |
| **Data integrity** | SHA-256 hash, encoding detected, row count, column count |
| **Source** | Custodian name, collection date, collection method, collection agent |
| **Processing** | Analysis tool version, Python version, analyst ID, processing timestamp |
| **Matter** | Matter reference, client name, matter type, date range in scope |

---

## 4. Audit Trail Generation

The audit trail is a complete, human-readable record of all analysis decisions, search parameters, and coding rationale. It supplements the chain of custody log with interpretive context.

### Audit Trail Class

```python
class AuditTrail:
    """
    Records all analytical decisions, parameters, and rationale.
    Designed to be included in an expert report or affidavit annexure.
    """

    def __init__(self, matter_ref: str, analyst_id: str):
        self.matter_ref = matter_ref
        self.analyst_id = analyst_id
        self.started_utc = datetime.now(timezone.utc).isoformat()
        self.entries = []

    def record(self, category: str, description: str, parameters: dict = None,
               result_summary: str = None, note: str = None):
        entry = {
            'seq': len(self.entries) + 1,
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'category': category,  # SEARCH / CODING / FILTER / DEDUP / EXPORT / NOTE
            'description': description,
        }
        if parameters: entry['parameters'] = parameters
        if result_summary: entry['result_summary'] = result_summary
        if note: entry['note'] = note
        self.entries.append(entry)

    def export_markdown(self, output_path: str):
        with open(output_path, 'w') as f:
            f.write(f"# Audit Trail — {self.matter_ref}\n\n")
            f.write(f"**Analyst**: {self.analyst_id}\n")
            f.write(f"**Analysis commenced**: {self.started_utc}\n")
            f.write(f"**Exported**: {datetime.now(timezone.utc).isoformat()}\n\n")
            f.write("---\n\n")
            for e in self.entries:
                f.write(f"### [{e['seq']}] {e['timestamp_utc']} — {e['category']}\n\n")
                f.write(f"**Action**: {e['description']}\n\n")
                if e.get('parameters'):
                    f.write("**Parameters**:\n")
                    for k, v in e['parameters'].items():
                        f.write(f"- {k}: `{v}`\n")
                    f.write("\n")
                if e.get('result_summary'):
                    f.write(f"**Result**: {e['result_summary']}\n\n")
                if e.get('note'):
                    f.write(f"**Note**: {e['note']}\n\n")
                f.write("---\n\n")

# Usage
audit = AuditTrail('MATTER-2026-001', 'ANALYST-01')

audit.record(
    category='SEARCH',
    description='Keyword search — fraud terms',
    parameters={
        'terms': 'fraud OR "false invoice" OR "unauthorised payment"',
        'columns_searched': 'subject, body, description',
        'case_sensitive': False,
        'date_filter': '2024-01-01 to 2025-12-31'
    },
    result_summary='312 rows matched out of 15,423 (2.0%)',
    note='High-relevance hits concentrated in Q3 2024 (187 of 312 hits)'
)

audit.record(
    category='CODING',
    description='Responsiveness coding — auto-coded batch',
    parameters={
        'method': 'keyword-triggered auto-code',
        'threshold': 'Any keyword hit = R; No hit = NR',
        'manual_review_sample': '50 rows (10% QC sample)'
    },
    result_summary='R: 312 | NR: 15,111 | NR?: 0',
)

audit.export_markdown('output/01_integrity/audit_trail.md')
```

---

## 5. Working Copy Management

### Directory Structure

All outputs must follow this structure. Never create files outside it during analysis.

```
output/
├── 01_integrity/
│   ├── hash_baseline.txt          # SHA-256 + file metadata before first read
│   ├── hash_baseline.json         # Machine-readable version
│   ├── chain_of_custody.md        # Human-readable CoC log
│   ├── chain_of_custody.json      # Machine-readable CoC log (authoritative)
│   └── audit_trail.md             # Analytical decisions and rationale
├── 02_profile/
│   └── dataset_profile.txt        # Summary statistics and data quality report
├── 03_analysis/
│   ├── timeline.csv               # Chronological event sequence
│   ├── entities.csv               # Extracted entities (email, phone, names, etc.)
│   └── anomalies.csv              # Flagged anomalous rows
├── 04_ediscovery/
│   ├── keyword_hits.csv           # KWIC results (all keyword matches)
│   ├── coded_dataset.csv          # Full dataset with coding columns appended
│   └── privilege_log.csv          # Items flagged as potentially privileged
└── 05_production/
    ├── responsive_set.csv          # Final responsive, non-privileged production set
    ├── privilege_log_final.csv     # Final privilege log for opposing party
    └── analysis_report.md          # Complete evidence-grade final report
```

### Create Output Directory

```python
import os

output_dirs = [
    'output/01_integrity',
    'output/02_profile',
    'output/03_analysis',
    'output/04_ediscovery',
    'output/05_production',
]

for d in output_dirs:
    os.makedirs(d, exist_ok=True)
```

### Working Copy Rules

1. Original file: **read-only, never modified**
2. Working copy: loaded into pandas; all operations in memory or on the working copy
3. If original must be re-accessed (e.g., re-hash): always use the original path, never the working copy path for hash baseline
4. If a second analyst reviews the work: they must hash the original independently and compare to the baseline record

---

## 6. Production Output Standards

### Bates Numbering

Each row in the production set receives a unique, sequential Bates number. This is the primary identifier for each document/record in the production.

```python
def apply_bates_numbers(df: pd.DataFrame, prefix: str = 'PROD',
                         start: int = 1, pad: int = 7) -> pd.DataFrame:
    """
    Apply sequential Bates numbers to a production dataset.

    Args:
        df: The responsive, non-privileged DataFrame
        prefix: Alphanumeric prefix (e.g., 'PROD', 'ABC', 'MATTER001')
        start: Starting number (default 1)
        pad: Zero-padding length (default 7 → PROD0000001)

    Returns:
        DataFrame with 'bates_number' column prepended
    """
    bates = [f"{prefix}{str(start + i).zfill(pad)}" for i in range(len(df))]
    df = df.copy()
    df.insert(0, 'bates_number', bates)
    return df

# Usage
production_df = coded_df[
    (coded_df['responsiveness'] == 'R') &
    (coded_df['privilege_flag'] == False)
].copy()

production_df = apply_bates_numbers(production_df, prefix='MATTER2026', start=1, pad=7)
# First row: MATTER20260000001
# Second row: MATTER20260000002
```

### Production Set Export

```python
def export_production_set(df: pd.DataFrame, output_path: str,
                           coc: ChainOfCustodyLog, audit: AuditTrail) -> dict:
    """
    Export the final production set with verification.
    Returns a production manifest dict.
    """
    # Export CSV
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    # Hash the output file
    output_hash = hash_file(output_path)

    # Log to CoC
    coc.add_entry(
        phase='PRODUCTION',
        action='EXPORT_PRODUCTION_SET',
        detail=f"Production set exported: {len(df):,} rows, Bates {df['bates_number'].iloc[0]} – {df['bates_number'].iloc[-1]}",
        rows_affected=len(df),
        output_file=output_path
    )

    audit.record(
        category='EXPORT',
        description='Production set export',
        parameters={
            'output_file': output_path,
            'row_count': len(df),
            'bates_range': f"{df['bates_number'].iloc[0]} – {df['bates_number'].iloc[-1]}",
            'sha256': output_hash['hash_value']
        },
        result_summary=f"{len(df):,} rows exported as production set"
    )

    manifest = {
        'export_timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'output_file': output_path,
        'row_count': len(df),
        'bates_first': df['bates_number'].iloc[0],
        'bates_last': df['bates_number'].iloc[-1],
        'sha256': output_hash['hash_value']
    }
    return manifest
```

### Columns to Include / Exclude from Production

| Include | Exclude |
|---------|---------|
| `bates_number` | `_original_*` columns (unless instructed) |
| All original data columns | Internal coding columns (`_auto_code`, `_review_flag`) |
| `responsiveness` coding | `privilege_flag` (privilege log is separate) |
| `date_iso8601` (parsed) | `_kwic_*` context columns |
| `custodian` / `source` | Hash verification intermediate columns |

Confirm inclusion/exclusion with instructing solicitor before production.

---

## 7. Privilege Log Standards

The privilege log records each item withheld from production on privilege grounds. It must be provided to the receiving party alongside the production set.

### Privilege Log Schema

```python
def create_privilege_log_entry(row: pd.Series, bates_number: str,
                                 privilege_type: str, basis: str,
                                 withheld_by: str) -> dict:
    """
    Create a standard privilege log entry for a withheld row.

    privilege_type: 'LPP' (legal professional privilege),
                    'WP' (without prejudice),
                    'WPP' (work product privilege),
                    'OTHER'
    basis: Description of why privilege is claimed
    withheld_by: Name of the withholding party
    """
    return {
        'bates_number': bates_number,
        'date': row.get('date_iso8601', row.get('date', '')),
        'author': row.get('sender', row.get('author', row.get('from', ''))),
        'recipients': row.get('recipient', row.get('to', row.get('recipients', ''))),
        'document_type': row.get('doc_type', 'Communication'),
        'privilege_type': privilege_type,
        'basis_for_privilege': basis,
        'withheld_by': withheld_by,
        'auto_flag_reason': row.get('_privilege_reason', ''),
    }

# Generate privilege log
privilege_rows = coded_df[coded_df['privilege_flag'] == True].copy()
priv_bates = [f"PRIV{str(i+1).zfill(6)}" for i in range(len(privilege_rows))]
privilege_rows.insert(0, 'priv_log_number', priv_bates)

privilege_log_entries = []
for _, row in privilege_rows.iterrows():
    entry = create_privilege_log_entry(
        row=row,
        bates_number=row['priv_log_number'],
        privilege_type='LPP',
        basis='Communication with legal adviser for the purpose of seeking legal advice',
        withheld_by='[Client Name]'
    )
    privilege_log_entries.append(entry)

privilege_log_df = pd.DataFrame(privilege_log_entries)
privilege_log_df.to_csv('output/05_production/privilege_log_final.csv',
                         index=False, encoding='utf-8-sig')
```

### Standard Privilege Log Columns

| Column | Description |
|--------|-------------|
| `priv_log_number` | Sequential PRIV000001 identifier |
| `date` | Date of the document/communication |
| `author` | Sender/author of the document |
| `recipients` | Recipients of the document |
| `document_type` | Email, Memo, Letter, Note, etc. |
| `privilege_type` | LPP / WP / WPP / Other |
| `basis_for_privilege` | Plain-English privilege claim |
| `withheld_by` | Name of the withholding party |

---

## 8. Evidence-Grade Report Template

The analysis report is the primary evidence-ready output. It should be capable of standing alone as an annexure to an affidavit or expert report.

### Report Structure

```python
def generate_analysis_report(
    matter_ref: str,
    analyst_id: str,
    file_metadata: dict,
    baseline_hash: dict,
    dataset_stats: dict,
    key_findings: list,
    methodology_notes: str,
    output_path: str,
    coc: ChainOfCustodyLog
):
    """Generate evidence-grade analysis report in Markdown."""
    now = datetime.now(timezone.utc).isoformat()

    with open(output_path, 'w') as f:
        f.write(f"# Data Analysis Report\n\n")
        f.write(f"---\n\n")

        # Cover fields
        f.write(f"**Matter Reference**: {matter_ref}\n")
        f.write(f"**Analyst**: {analyst_id}\n")
        f.write(f"**Report Generated (UTC)**: {now}\n")
        f.write(f"**Status**: DRAFT — FOR LEGAL REVIEW\n\n")
        f.write(f"---\n\n")

        # 1. Executive Summary
        f.write("## 1. Executive Summary\n\n")
        f.write("[Brief 3–5 sentence summary of the dataset, analysis scope, and key findings.]\n\n")

        # 2. File Integrity
        f.write("## 2. File Integrity & Chain of Custody\n\n")
        f.write(f"**Original file**: `{file_metadata['original_filename']}`\n\n")
        f.write(f"**File size**: {file_metadata['file_size_human']}\n\n")
        f.write(f"**SHA-256 hash (baseline)**:\n```\n{baseline_hash['hash_value']}\n```\n\n")
        f.write(f"**Hash computed at**: {baseline_hash['timestamp_utc']}\n\n")
        f.write(f"**File modified timestamp**: {file_metadata['modified_timestamp']}\n\n")
        f.write("The above hash was computed before any data was loaded or processed. ")
        f.write("All subsequent analysis was performed on a verified copy of the original file. ")
        f.write("The chain of custody log records every operation performed on the data. ")
        f.write("The original file was not modified at any time.\n\n")

        # 3. Dataset Profile
        f.write("## 3. Dataset Profile\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        for k, v in dataset_stats.items():
            f.write(f"| {k} | {v} |\n")
        f.write("\n")

        # 4. Methodology
        f.write("## 4. Methodology\n\n")
        f.write("### 4.1 Data Ingestion\n\n")
        f.write("The dataset was loaded using the Python `pandas` library (read_csv) with encoding detection. ")
        f.write("A SHA-256 hash was computed immediately before loading.\n\n")
        f.write("### 4.2 Analysis Approach\n\n")
        f.write(f"{methodology_notes}\n\n")
        f.write("### 4.3 eDiscovery Review\n\n")
        f.write("[Describe keyword terms, responsiveness criteria, and privilege review approach.]\n\n")
        f.write("### 4.4 Limitations\n\n")
        f.write("- This analysis is based solely on the data provided. No data was obtained from external sources.\n")
        f.write("- Automated keyword search and privilege detection are screening tools only. Items flagged require human review.\n")
        f.write("- This report does not constitute legal advice.\n\n")

        # 5. Key Findings
        f.write("## 5. Key Findings\n\n")
        for i, finding in enumerate(key_findings, 1):
            f.write(f"### Finding {i}\n\n{finding}\n\n")

        # 6. Production Summary
        f.write("## 6. Production Summary\n\n")
        f.write("| Category | Count |\n")
        f.write("|----------|-------|\n")
        f.write("| Total rows reviewed | |\n")
        f.write("| Responsive (R) | |\n")
        f.write("| Non-Responsive (NR) | |\n")
        f.write("| Needs Review (NR?) | |\n")
        f.write("| Privilege (R-P) | |\n")
        f.write("| Production set (Responsive + non-privileged) | |\n\n")

        # 7. Integrity Statement
        f.write("## 7. Integrity Statement\n\n")
        f.write("I confirm that:\n\n")
        f.write("1. The original data file was not modified at any time during this analysis.\n")
        f.write("2. All analysis was performed on a verified copy of the original file.\n")
        f.write("3. The SHA-256 hash of the original file was recorded before any data was loaded.\n")
        f.write("4. All operations performed on the data are recorded in the chain of custody log.\n")
        f.write("5. The production set and privilege log are derived solely from the data as provided.\n\n")

        # 8. Analyst Declaration
        f.write("## 8. Analyst Declaration\n\n")
        f.write(f"**Analyst**: {analyst_id}\n\n")
        f.write(f"**Date**: {now[:10]}\n\n")
        f.write("I declare that this report has been prepared to the best of my ability ")
        f.write("and that the analysis described herein was performed in accordance with ")
        f.write("the methodology set out in this report.\n\n")
        f.write("_Signature: ___________________________\n\n")

        # 9. Annexures
        f.write("## 9. Annexures\n\n")
        f.write("- **Annexure A**: Hash baseline (`output/01_integrity/hash_baseline.txt`)\n")
        f.write("- **Annexure B**: Chain of custody log (`output/01_integrity/chain_of_custody.md`)\n")
        f.write("- **Annexure C**: Audit trail (`output/01_integrity/audit_trail.md`)\n")
        f.write("- **Annexure D**: Dataset profile (`output/02_profile/dataset_profile.txt`)\n")
        f.write("- **Annexure E**: Production set (`output/05_production/responsive_set.csv`)\n")
        f.write("- **Annexure F**: Privilege log (`output/05_production/privilege_log_final.csv`)\n")

    coc.add_entry('PRODUCTION', 'REPORT_GENERATED',
                  f'Evidence-grade report generated at {output_path}',
                  output_file=output_path)
    return output_path
```

---

## 9. Integrity Verification — Final Check

Before any output leaves the analyst, run a final integrity verification. This is the last step before packaging for production.

### Final Verification Checklist

```python
def run_final_integrity_check(
    original_filepath: str,
    baseline_hash_value: str,
    output_dir: str,
    coc: ChainOfCustodyLog
) -> dict:
    """
    Run a complete final integrity check before production delivery.
    Returns a pass/fail dict with details.
    """
    results = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'checks': [],
        'overall_pass': True
    }

    def check(name: str, passed: bool, detail: str):
        results['checks'].append({'check': name, 'result': 'PASS' if passed else 'FAIL', 'detail': detail})
        if not passed:
            results['overall_pass'] = False

    # 1. Re-hash original file and compare to baseline
    current_hash = hash_file(original_filepath)['hash_value']
    hash_match = current_hash == baseline_hash_value
    check('Original file hash', hash_match,
          'SHA-256 matches baseline' if hash_match
          else f'MISMATCH: baseline={baseline_hash_value}, current={current_hash}')

    # 2. Check required output files exist
    required_files = [
        'output/01_integrity/hash_baseline.txt',
        'output/01_integrity/chain_of_custody.md',
        'output/01_integrity/audit_trail.md',
        'output/05_production/responsive_set.csv',
        'output/05_production/privilege_log_final.csv',
        'output/05_production/analysis_report.md',
    ]
    for req_file in required_files:
        exists = os.path.exists(req_file)
        check(f'Output file: {req_file}', exists,
              'File exists' if exists else 'FILE MISSING')

    # 3. Check CoC log is non-empty
    coc_entries = len(coc.entries)
    check('Chain of custody entries', coc_entries > 0,
          f'{coc_entries} entries recorded')

    # 4. Check production set has Bates numbers
    try:
        prod_df = pd.read_csv('output/05_production/responsive_set.csv', nrows=2)
        has_bates = 'bates_number' in prod_df.columns
        check('Production set Bates numbers', has_bates,
              'bates_number column present' if has_bates else 'bates_number column MISSING')
    except Exception as e:
        check('Production set readable', False, str(e))

    # Report
    status = 'ALL CHECKS PASSED' if results['overall_pass'] else 'CHECKS FAILED — DO NOT DELIVER'
    print(f"\n{'='*60}")
    print(f"FINAL INTEGRITY CHECK: {status}")
    print(f"{'='*60}")
    for c in results['checks']:
        marker = '✓' if c['result'] == 'PASS' else '✗'
        print(f"  {marker} [{c['result']}] {c['check']}: {c['detail']}")
    print(f"{'='*60}\n")

    coc.add_entry('PRODUCTION', 'FINAL_INTEGRITY_CHECK',
                  f"Final integrity check: {status} ({sum(1 for c in results['checks'] if c['result'] == 'PASS')}/{len(results['checks'])} checks passed)")
    return results

# Run as final step before packaging for delivery
check_results = run_final_integrity_check(
    original_filepath='/path/to/original.csv',
    baseline_hash_value=baseline['hash_value'],
    output_dir='output',
    coc=coc
)

if not check_results['overall_pass']:
    raise RuntimeError("INTEGRITY CHECK FAILED — resolve all issues before production delivery.")
```

### Pre-Delivery Checklist

```
FINAL PRODUCTION CHECKLIST
═══════════════════════════════════════════════════════

INTEGRITY
  [ ] SHA-256 hash of original file re-verified against baseline
  [ ] Chain of custody log covers all operations (no gaps)
  [ ] Audit trail records all search queries and coding decisions
  [ ] No original files were modified at any point

PRODUCTION SET
  [ ] Bates numbers applied sequentially (no gaps or duplicates)
  [ ] Only responsive, non-privileged rows included
  [ ] All original columns preserved; coding columns removed (if instructed)
  [ ] CSV exports in UTF-8-sig encoding
  [ ] Production set count verified against coding summary

PRIVILEGE LOG
  [ ] All R-P coded rows appear in privilege log (none missing)
  [ ] Privilege log format matches required standard
  [ ] Basis for privilege recorded for every entry
  [ ] Privilege log count reconciles with production set count

REPORT
  [ ] Executive summary accurate and complete
  [ ] Methodology section describes all analysis steps
  [ ] Limitations section included
  [ ] Integrity statement signed by analyst
  [ ] All annexures listed and files verified to exist
  [ ] Report reviewed by qualified legal practitioner before use in proceedings

PACKAGING
  [ ] All output files collected in 05_production/
  [ ] Hash of each production file recorded
  [ ] Delivery method and recipient recorded in CoC log
  [ ] Original file and working copy retained per matter retention policy
```

---

## Quick Reference — Evidence Standards

| Task | Function / Step | Notes |
|------|-----------------|-------|
| Hash original before read | `hash_file()` | Store result immediately |
| Create + verify working copy | `shutil.copy2()` + `verify_copy_integrity()` | Fail hard on mismatch |
| Log every operation | `coc.add_entry()` | Phase + action + detail |
| Preserve original columns | `df['_original_x'] = df['x'].copy()` | Prefix with `_original_` |
| Apply Bates numbers | `apply_bates_numbers()` | PROD0000001 format |
| Export production set | `export_production_set()` | Auto-logs to CoC |
| Generate privilege log | `create_privilege_log_entry()` per row | PRIV000001 format |
| Final integrity check | `run_final_integrity_check()` | Must pass before delivery |
| Generate report | `generate_analysis_report()` | Requires legal review |

---

## 10. Multi-Analyst Workflow

Manage chain of custody when multiple analysts work on the same dataset. Each analyst has a unique ID. Handoff events are logged with file hashes.

```python
class MultiAnalystWorkflow:
    """
    Manages chain of custody when multiple analysts work on the same dataset.
    Each analyst has a unique ID. Handoff events are logged.
    """

    def __init__(self, matter_ref: str, primary_analyst: str):
        self.matter_ref = matter_ref
        self.analysts = [primary_analyst]
        self.handoffs = []
        self.current_analyst = primary_analyst

    def handoff(self, from_analyst: str, to_analyst: str,
                handoff_files: list, notes: str = ''):
        """Record custody transfer between analysts."""
        from datetime import datetime, timezone
        import hashlib

        handoff_record = {
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'from_analyst': from_analyst,
            'to_analyst': to_analyst,
            'files_transferred': handoff_files,
            'file_hashes': {},
            'notes': notes
        }

        # Hash each file at point of transfer
        for filepath in handoff_files:
            try:
                h = hashlib.sha256()
                with open(filepath, 'rb') as f:
                    for chunk in iter(lambda: f.read(65536), b''):
                        h.update(chunk)
                handoff_record['file_hashes'][filepath] = h.hexdigest()
            except FileNotFoundError:
                handoff_record['file_hashes'][filepath] = 'FILE NOT FOUND'

        self.handoffs.append(handoff_record)
        self.current_analyst = to_analyst
        if to_analyst not in self.analysts:
            self.analysts.append(to_analyst)

        print(f"Custody transferred: {from_analyst} → {to_analyst}")
        print(f"Files transferred: {len(handoff_files)}")
        return handoff_record

    def export_handoff_log(self, output_path: str):
        """Export multi-analyst handoff log."""
        import json
        with open(output_path, 'w') as f:
            json.dump({
                'matter_reference': self.matter_ref,
                'all_analysts': self.analysts,
                'current_analyst': self.current_analyst,
                'handoffs': self.handoffs
            }, f, indent=2)
        print(f"Multi-analyst handoff log: {output_path}")
```

---

## 11. Redaction Workflow

Redact sensitive columns while preserving originals for internal records. Production output uses redacted version; internal records retain originals.

```python
def redact_columns(df, columns_to_redact, redaction_marker='[REDACTED]',
                   preserve_original=True):
    """
    Redact specified columns while preserving originals for internal records.
    Production output uses redacted version; internal records retain originals.

    IMPORTANT: Always confirm with instructing solicitor which columns require redaction.
    """
    df_redacted = df.copy()

    for col in columns_to_redact:
        if col not in df.columns:
            print(f"WARNING: Column '{col}' not found — skipping")
            continue
        if preserve_original:
            df_redacted[f'_pre_redaction_{col}'] = df_redacted[col].copy()
        df_redacted[col] = redaction_marker
        print(f"Redacted: {col} ({df_redacted[col].notna().sum():,} values)")

    return df_redacted

def partial_redact_pattern(df, column, pattern, replacement='[REDACTED]',
                            preserve_original=True):
    """
    Partially redact a column — replace only the matching portion.
    Example: redact TFNs, account numbers, phone numbers within text.
    """
    import re
    if preserve_original:
        df[f'_pre_redaction_{column}'] = df[column].copy()

    df[column] = df[column].str.replace(pattern, replacement, regex=True, flags=re.IGNORECASE)

    # Count redactions made
    changed = (df[column] != df[f'_pre_redaction_{column}']).sum()
    print(f"Partial redaction in '{column}': {changed:,} rows modified")
    return df

# Common redaction patterns for Australian legal context
REDACTION_PATTERNS = {
    'tfn':          r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{3}\b',
    'credit_card':  r'\b(?:\d{4}[\s\-]?){3}\d{4}\b',
    'passport_au':  r'\b[A-Z]\d{7}\b',
    'drivers_lic':  r'\b[A-Z]{1,2}\d{5,9}\b',
    'medicare_au':  r'\b\d{4}[\s]?\d{5}[\s]?\d{1}\b',
    'bsb':          r'\b\d{3}[-\s]?\d{3}\b',
    'account_no':   r'\b\d{8,12}\b',
}
```

---

## 12. DOCX Report Export

Convert the markdown analysis report to a DOCX file for legal practitioners.

```python
def export_report_as_docx(markdown_path: str, output_path: str,
                           matter_ref: str, firm_name: str = ''):
    """
    Convert the markdown analysis report to a DOCX file for legal practitioners.
    Requires: pip install python-docx
              pip install markdown
    """
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    import re

    doc = Document()

    # Document properties
    doc.core_properties.title = f"Data Analysis Report — {matter_ref}"
    doc.core_properties.subject = "eDiscovery Analysis"
    if firm_name:
        doc.core_properties.company = firm_name

    # Styles
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    # Parse and add content from markdown
    with open(markdown_path, 'r') as f:
        content = f.read()

    for line in content.split('\n'):
        if line.startswith('# '):
            p = doc.add_heading(line[2:], level=1)
        elif line.startswith('## '):
            p = doc.add_heading(line[3:], level=2)
        elif line.startswith('### '):
            p = doc.add_heading(line[4:], level=3)
        elif line.startswith('| '):
            # Table row — simplified (add actual table parsing for production)
            doc.add_paragraph(line, style='Normal')
        elif line.startswith('- ') or line.startswith('* '):
            doc.add_paragraph(line[2:], style='List Bullet')
        elif line.strip():
            doc.add_paragraph(line)
        else:
            doc.add_paragraph('')

    doc.save(output_path)
    print(f"DOCX report exported: {output_path}")
    return output_path
```

## Section 13: ZIP Archive Handling

Compressed collections (ZIP, RAR, 7Z) must be extracted with documented chain of custody. Hash each file individually and track extraction lineage for admissibility.

### Extract and Hash ZIP Files

```python
import zipfile
import hashlib
import os
import json
from datetime import datetime
from pathlib import Path

def extract_and_hash_zip(zip_path, extract_to, password=None, log_coc=True):
    """
    Extract ZIP archive and compute SHA-256 hash for each file.
    Maintains chain of custody log.

    Args:
        zip_path: Path to ZIP archive
        extract_to: Destination directory
        password: ZIP password (if encrypted)
        log_coc: Whether to log to chain of custody file

    Returns:
        Dictionary with extraction manifest including hashes
    """
    import hashlib

    os.makedirs(extract_to, exist_ok=True)
    manifest = {
        'zip_source': os.path.abspath(zip_path),
        'extraction_date': datetime.utcnow().isoformat(),
        'extraction_directory': os.path.abspath(extract_to),
        'zip_hash_sha256': compute_file_hash(zip_path),
        'password_protected': password is not None,
        'files': [],
        'total_files': 0,
        'total_bytes': 0,
    }

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Validate archive integrity
            bad_file = zf.testzip()
            if bad_file:
                manifest['integrity_check'] = f'FAILED: {bad_file}'
                return manifest

            manifest['integrity_check'] = 'PASSED'

            # Extract all files
            for file_info in zf.filelist:
                extracted_path = zf.extract(file_info.filename, extract_to, pwd=password.encode() if password else None)

                # Skip directories
                if not os.path.isfile(extracted_path):
                    continue

                file_hash = compute_file_hash(extracted_path)
                file_size = os.path.getsize(extracted_path)

                file_record = {
                    'original_name': file_info.filename,
                    'extracted_path': extracted_path,
                    'file_size_bytes': file_size,
                    'sha256_hash': file_hash,
                    'compressed_size': file_info.compress_size,
                    'compression_method': file_info.compress_type,
                    'date_time': file_info.date_time.__str__() if hasattr(file_info, 'date_time') else None,
                }
                manifest['files'].append(file_record)
                manifest['total_bytes'] += file_size

            manifest['total_files'] = len(manifest['files'])

            # Log to chain of custody
            if log_coc:
                log_extraction_to_coc(zip_path, manifest)

    except zipfile.BadZipFile as e:
        manifest['error'] = f'Invalid ZIP: {str(e)}'

    return manifest


def compute_file_hash(filepath, algorithm='sha256'):
    """
    Compute hash of file for integrity verification.
    Uses SHA-256 (NIST recommended for evidence).
    """
    hash_obj = hashlib.sha256()

    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def extract_nested_zips(zip_path, extract_to, max_depth=5, password=None):
    """
    Recursively extract nested ZIP archives.
    Maintains separate manifest for each level.

    Args:
        zip_path: Initial ZIP file
        extract_to: Base extraction directory
        max_depth: Maximum nesting depth (prevent zip bombs)
        password: Password for encrypted ZIPs

    Returns:
        List of all extraction manifests (depth-first order)
    """
    manifests = []
    depth = 0

    def recursive_extract(current_zip, current_extract_dir):
        nonlocal depth

        if depth >= max_depth:
            return

        depth += 1
        manifest = extract_and_hash_zip(current_zip, current_extract_dir, password, log_coc=True)
        manifests.append(manifest)

        # Check for nested ZIPs
        for file_record in manifest.get('files', []):
            filepath = file_record['extracted_path']

            if filepath.lower().endswith(('.zip', '.rar', '.7z')):
                nested_dir = os.path.join(current_extract_dir, f"{file_record['original_name']}_extracted")
                try:
                    recursive_extract(filepath, nested_dir)
                except Exception as e:
                    print(f"Could not extract nested archive {filepath}: {e}")

        depth -= 1

    recursive_extract(zip_path, extract_to)
    return manifests


def log_extraction_to_coc(zip_path, manifest):
    """
    Log ZIP extraction to chain of custody file.
    Creates tamper-evident audit trail.
    """
    coc_entry = {
        'event': 'ZIP_EXTRACTION',
        'timestamp': datetime.utcnow().isoformat(),
        'source_file': os.path.basename(zip_path),
        'source_hash': manifest['zip_hash_sha256'],
        'files_extracted': manifest['total_files'],
        'total_size_bytes': manifest['total_bytes'],
        'integrity_status': manifest.get('integrity_check', 'UNKNOWN'),
        'extraction_directory': manifest['extraction_directory'],
    }

    # Append to audit log
    coc_file = os.path.join(os.path.dirname(zip_path), 'ZIP_EXTRACTION_AUDIT.jsonl')
    with open(coc_file, 'a') as f:
        f.write(json.dumps(coc_entry) + '\n')

    print(f"✓ Extraction logged to {coc_file}")


def generate_zip_extraction_report(manifests):
    """
    Generate CSV report of all extracted files with hashes.
    Suitable for legal evidence production.
    """
    import csv

    all_files = []

    for manifest in manifests:
        for file_record in manifest.get('files', []):
            all_files.append({
                'source_zip': os.path.basename(manifest['zip_source']),
                'zip_sha256': manifest['zip_hash_sha256'],
                'original_filename': file_record['original_name'],
                'extracted_path': file_record['extracted_path'],
                'file_size_bytes': file_record['file_size_bytes'],
                'sha256_hash': file_record['sha256_hash'],
                'compression_method': file_record.get('compression_method', ''),
                'extraction_date': manifest['extraction_date'],
            })

    output_path = 'zip_extraction_manifest.csv'
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=all_files[0].keys())
        writer.writeheader()
        writer.writerows(all_files)

    print(f"✓ Extraction manifest saved: {output_path}")
    return output_path
```

### Chain of Custody for Compressed Files

**Best Practices:**

1. **Hash the original ZIP** before extraction
2. **Extract to write-once directory** (read-only after extraction)
3. **Hash each individual file** within archive
4. **Log all operations** to tamper-evident JSONL audit trail
5. **Cross-check manifests** with load file entries (DAT/OPT)
6. **Document compression method** (ZIP deflate vs. stored)
7. **Preserve extraction timestamp** for timeline analysis

**Admissibility Checklist:**
- [ ] Original ZIP file hash documented
- [ ] Extraction method and tool documented
- [ ] SHA-256 hash for each extracted file
- [ ] Chain of custody log with timestamps
- [ ] Integrity check passed (ZIP testzip())
- [ ] No files modified post-extraction
- [ ] Extraction directory access controls in place
- [ ] Manifest CSV produced for evidence review

---

## §10: Court-Ready DOCX Generation

Provides templates and functions for generating Microsoft Word documents suitable for filing in Australian courts, particularly the Federal Circuit and Family Court of Australia (FCFCOA).

### 10.1 Affidavit Annexure Cover Sheet

Node.js function using the `docx` library to generate an annexure cover sheet meeting FCFCOA requirements.

```typescript
import { Document, Packer, Paragraph, AlignmentType, BorderStyle, Table, TableRow, TableCell, WidthType, VerticalAlign, ShadingType } from 'docx';
import * as fs from 'fs';

/**
 * Generate a court-ready affidavit annexure cover sheet.
 * @param annexureId - Identifier for the annexure (e.g., "A", "B", "ANNEXURE A")
 * @param deponentName - Full name of the deponent
 * @param affirmDate - Date affidavit was sworn/affirmed (ISO 8601 or formatted string)
 * @param outputPath - File system path for output DOCX
 * @returns Promise<string> - Path to written file
 */
export async function generateAnnexureCoverSheet(
  annexureId: string,
  deponentName: string,
  affirmDate: string,
  outputPath: string
): Promise<string> {
  if (!annexureId || !deponentName || !affirmDate) {
    throw new Error('annexureId, deponentName, and affirmDate are required');
  }

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            size: {
              width: 11906,  // A4 in DXA
              height: 16838, // A4 in DXA
            },
            margins: {
              top: 1440,    // 2.54cm
              bottom: 1440,
              left: 1440,
              right: 1440,
            },
          },
        },
        children: [
          // Page border
          new Paragraph({
            text: '',
            border: {
              top: { color: '000000', space: 24, style: BorderStyle.SINGLE, size: 24 },
              bottom: { color: '000000', space: 24, style: BorderStyle.SINGLE, size: 24 },
              left: { color: '000000', space: 24, style: BorderStyle.SINGLE, size: 24 },
              right: { color: '000000', space: 24, style: BorderStyle.SINGLE, size: 24 },
            },
          }),
          // Spacing
          new Paragraph({ text: '' }),
          new Paragraph({ text: '' }),
          // Main text
          new Paragraph({
            text: `This is the document marked ${annexureId} referred to in the affidavit of ${deponentName} sworn/affirmed on ${affirmDate}`,
            alignment: AlignmentType.CENTER,
            spacing: { line: 360, lineRule: 'auto' },
            style: 'Normal',
          }),
          // Spacing
          new Paragraph({ text: '' }),
          new Paragraph({ text: '' }),
          new Paragraph({ text: '' }),
          new Paragraph({ text: '' }),
          // Attestation line
          new Paragraph({
            text: 'Before me:',
            spacing: { line: 360, lineRule: 'auto' },
          }),
          new Paragraph({
            text: '_' .repeat(50),
            spacing: { line: 360, lineRule: 'auto' },
          }),
          new Paragraph({
            text: '(Justice of the Peace / Solicitor)',
            spacing: { line: 360, lineRule: 'auto' },
            style: 'Normal',
          }),
        ],
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);

  return outputPath;
}
```

### 10.2 Chronological Message Evidence Document

Node.js function to generate a comprehensive message evidence bundle with table of contents, chronological messages, and proper pagination.

```typescript
/**
 * Generate a chronological message evidence document suitable for court filing.
 * @param messages - Array of message objects { timestamp, from, to, text, tags?, tags }
 * @param metadata - Object with { matterRef, parties, dateRange, totalMessages, analyst }
 * @param outputPath - Output DOCX file path
 * @returns Promise<string> - Path to written file
 */
export async function generateMessageEvidenceDoc(
  messages: Array<{ timestamp: string; from: string; to: string; text: string; tags?: string[] }>,
  metadata: {
    matterRef: string;
    parties: { [key: string]: string };
    dateRange: string;
    totalMessages: number;
    analyst: string;
  },
  outputPath: string
): Promise<string> {
  if (!messages || messages.length === 0) {
    throw new Error('messages array cannot be empty');
  }
  if (!metadata.matterRef) {
    throw new Error('metadata.matterRef is required');
  }

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margins: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
          },
        },
        children: buildMessageEvidenceChildren(messages, metadata),
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);

  return outputPath;
}

/**
 * Build document children for message evidence bundle.
 */
function buildMessageEvidenceChildren(
  messages: Array<{ timestamp: string; from: string; to: string; text: string; tags?: string[] }>,
  metadata: any
): any[] {
  const children: any[] = [];
  let paraNumber = 1;

  // Cover page
  children.push(
    new Paragraph({
      text: `MESSAGE EVIDENCE BUNDLE`,
      alignment: AlignmentType.CENTER,
      spacing: { line: 360 },
      style: 'Heading1',
    })
  );
  children.push(new Paragraph({ text: '' }));
  children.push(
    new Paragraph({
      text: `Matter Reference: ${metadata.matterRef}`,
      spacing: { line: 360 },
    })
  );
  children.push(
    new Paragraph({
      text: `Date Range: ${metadata.dateRange}`,
      spacing: { line: 360 },
    })
  );
  children.push(
    new Paragraph({
      text: `Total Messages: ${metadata.totalMessages}`,
      spacing: { line: 360 },
    })
  );
  children.push(
    new Paragraph({
      text: `Prepared by: ${metadata.analyst}`,
      spacing: { line: 360 },
    })
  );

  // Page break
  children.push(new Paragraph({ text: '', pageBreakBefore: true }));

  // Methodology statement
  children.push(
    new Paragraph({
      text: `${paraNumber}. METHODOLOGY`,
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  paraNumber++;
  children.push(
    new Paragraph({
      text: 'Messages are presented chronologically as extracted from original source material. Each message is identified by sequential item number, local timestamp, UTC equivalent, sender, recipient, and full message text. Special characters and emoji are noted where they cannot be rendered.',
      spacing: { line: 360 },
    })
  );

  // Page break before messages
  children.push(new Paragraph({ text: '', pageBreakBefore: true }));

  // Messages table
  children.push(
    new Paragraph({
      text: `${paraNumber}. CHRONOLOGICAL MESSAGES`,
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  paraNumber++;

  const rows: TableRow[] = [
    new TableRow({
      children: [
        new TableCell({ children: [new Paragraph('Item#')] }),
        new TableCell({ children: [new Paragraph('Date/Time (Local | UTC)')] }),
        new TableCell({ children: [new Paragraph('From')] }),
        new TableCell({ children: [new Paragraph('To')] }),
        new TableCell({ children: [new Paragraph('Message Text')] }),
        new TableCell({ children: [new Paragraph('Tags')] }),
      ],
    }),
  ];

  messages.forEach((msg, idx) => {
    const itemNum = idx + 1;
    const localTime = msg.timestamp;
    const utcTime = formatToUTC(msg.timestamp);
    const tags = (msg.tags || []).join(', ');

    rows.push(
      new TableRow({
        children: [
          new TableCell({ children: [new Paragraph(itemNum.toString())] }),
          new TableCell({
            children: [new Paragraph(`${localTime}\n(${utcTime})`)],
            shading: { fill: idx % 2 === 0 ? 'FFFFFF' : 'F0F0F0', type: ShadingType.CLEAR },
          }),
          new TableCell({ children: [new Paragraph(msg.from)] }),
          new TableCell({ children: [new Paragraph(msg.to)] }),
          new TableCell({
            children: [new Paragraph(sanitiseMessageText(msg.text))],
            shading: { fill: idx % 2 === 0 ? 'FFFFFF' : 'F0F0F0', type: ShadingType.CLEAR },
          }),
          new TableCell({ children: [new Paragraph(tags)] }),
        ],
      })
    );
  });

  children.push(
    new Table({
      rows: rows,
      width: { size: 100, type: WidthType.PERCENTAGE },
    })
  );

  // Glossary
  children.push(new Paragraph({ text: '', pageBreakBefore: true }));
  children.push(
    new Paragraph({
      text: `${paraNumber}. PARTY GLOSSARY`,
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  Object.entries(metadata.parties).forEach(([key, value]) => {
    children.push(new Paragraph({ text: `${key}: ${value}`, spacing: { line: 360 } }));
  });

  // Attestation
  children.push(new Paragraph({ text: '', pageBreakBefore: true }));
  children.push(
    new Paragraph({
      text: 'ATTESTATION',
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  children.push(
    new Paragraph({
      text: `This document is a true and accurate chronological record of the messages listed herein, extracted from source material identified in the accompanying metadata.`,
      spacing: { line: 360 },
    })
  );
  children.push(new Paragraph({ text: '' }));
  children.push(new Paragraph({ text: '_'.repeat(40) }));
  children.push(new Paragraph({ text: `Analyst: ${metadata.analyst}` }));
  children.push(new Paragraph({ text: `Date: ${new Date().toISOString().split('T')[0]}` }));

  return children;
}

/**
 * Utility: format timestamp to UTC string.
 */
function formatToUTC(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
}

/**
 * Utility: sanitise message text for rendering (handle emoji, special chars).
 */
function sanitiseMessageText(text: string): string {
  // Replace emoji with placeholders
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu;
  return text.replace(emojiRegex, '[emoji]');
}

/**
 * Utility: add a numbered paragraph with continuous numbering across sections.
 */
export function addNumberedParagraph(
  children: any[],
  text: string,
  level: number = 0
): number {
  const indent = level * 720; // 0.5 inch per level
  children.push(
    new Paragraph({
      text: text,
      spacing: { line: 360 },
      indentation: { left: indent },
    })
  );
  return 1;
}

/**
 * Utility: format a timestamp with both local and UTC display.
 */
export function formatTimestamp(utcTimestamp: string, localTimezone?: string): string {
  const date = new Date(utcTimestamp);
  const utcStr = date.toISOString().replace('T', ' ').slice(0, 19);
  if (localTimezone) {
    // For production, use a proper timezone library
    return `${utcStr} UTC`;
  }
  return `${utcStr} UTC`;
}
```

### 10.3 Expert Report Template

Node.js function for generating expert reports meeting Australian court requirements.

```typescript
/**
 * Generate an expert report document suitable for court filing.
 * @param reportData - Object containing expert qualifications, instructions, methodology, findings, opinions
 * @param outputPath - Output DOCX file path
 * @returns Promise<string> - Path to written file
 */
export async function generateExpertReportDoc(
  reportData: {
    matterRef: string;
    expertName: string;
    qualifications: string;
    instructionsReceived: string;
    methodology: string;
    findings: Array<{ number: number; text: string }>;
    opinions: Array<{ number: number; text: string }>;
    annexures?: string[];
  },
  outputPath: string
): Promise<string> {
  if (!reportData.matterRef || !reportData.expertName || !reportData.findings) {
    throw new Error('matterRef, expertName, and findings are required');
  }

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margins: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
          },
        },
        children: buildExpertReportChildren(reportData),
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);

  return outputPath;
}

/**
 * Build document children for expert report.
 */
function buildExpertReportChildren(reportData: any): any[] {
  const children: any[] = [];

  // Cover page
  children.push(
    new Paragraph({
      text: 'EXPERT REPORT',
      alignment: AlignmentType.CENTER,
      spacing: { line: 360 },
      style: 'Heading1',
    })
  );
  children.push(new Paragraph({ text: '' }));
  children.push(
    new Paragraph({
      text: `Matter Reference: ${reportData.matterRef}`,
      spacing: { line: 360 },
    })
  );
  children.push(
    new Paragraph({
      text: `Expert: ${reportData.expertName}`,
      spacing: { line: 360 },
    })
  );
  children.push(new Paragraph({ text: '', pageBreakBefore: true }));

  // Qualifications
  children.push(
    new Paragraph({
      text: '1. QUALIFICATIONS AND EXPERIENCE',
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  children.push(
    new Paragraph({
      text: reportData.qualifications,
      spacing: { line: 360 },
    })
  );

  // Instructions received
  children.push(new Paragraph({ text: '' }));
  children.push(
    new Paragraph({
      text: '2. INSTRUCTIONS RECEIVED',
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  children.push(
    new Paragraph({
      text: reportData.instructionsReceived,
      spacing: { line: 360 },
    })
  );

  // Methodology
  children.push(new Paragraph({ text: '' }));
  children.push(
    new Paragraph({
      text: '3. METHODOLOGY',
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  children.push(
    new Paragraph({
      text: reportData.methodology,
      spacing: { line: 360 },
    })
  );

  // Findings
  children.push(new Paragraph({ text: '' }));
  children.push(
    new Paragraph({
      text: '4. FINDINGS',
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  reportData.findings.forEach((finding) => {
    children.push(
      new Paragraph({
        text: `${finding.number}. ${finding.text}`,
        spacing: { line: 360 },
      })
    );
  });

  // Opinions
  children.push(new Paragraph({ text: '' }));
  children.push(
    new Paragraph({
      text: '5. OPINIONS',
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  reportData.opinions.forEach((opinion) => {
    children.push(
      new Paragraph({
        text: `${opinion.number}. ${opinion.text}`,
        spacing: { line: 360 },
      })
    );
  });

  // Declaration
  children.push(new Paragraph({ text: '', pageBreakBefore: true }));
  children.push(
    new Paragraph({
      text: 'DECLARATION',
      spacing: { line: 360 },
      style: 'Heading2',
    })
  );
  children.push(
    new Paragraph({
      text: 'I have made all the inquiries that I believe are desirable and appropriate and no matters of significance which I regard as relevant have, to my knowledge, been withheld from the Court.',
      spacing: { line: 360 },
    })
  );
  children.push(new Paragraph({ text: '' }));
  children.push(new Paragraph({ text: '_'.repeat(40) }));
  children.push(new Paragraph({ text: reportData.expertName }));
  children.push(new Paragraph({ text: new Date().toISOString().split('T')[0] }));

  // Annexures list
  if (reportData.annexures && reportData.annexures.length > 0) {
    children.push(new Paragraph({ text: '', pageBreakBefore: true }));
    children.push(
      new Paragraph({
        text: 'ANNEXURES',
        spacing: { line: 360 },
        style: 'Heading2',
      })
    );
    reportData.annexures.forEach((annexure, idx) => {
      children.push(
        new Paragraph({
          text: `${String.fromCharCode(65 + idx)}. ${annexure}`,
          spacing: { line: 360 },
        })
      );
    });
  }

  return children;
}
```

---

## §11: Court-Ready PDF Generation

### 11.1 PDF from DOCX Conversion Pipeline

Python function to convert DOCX documents to PDF using LibreOffice in headless mode, suitable for court filing.

```python
import subprocess
import os
import re
from pathlib import Path
from typing import Optional


def convert_docx_to_pdf(docx_path: str, output_dir: str) -> str:
    """
    Convert a DOCX file to PDF using LibreOffice headless mode.

    Args:
        docx_path: Absolute path to the DOCX file
        output_dir: Directory where PDF will be written

    Returns:
        str: Absolute path to the generated PDF file

    Raises:
        FileNotFoundError: If DOCX does not exist or LibreOffice is not available
        subprocess.CalledProcessError: If conversion fails
        ValueError: If output PDF cannot be verified
    """
    docx_path = Path(docx_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # Call LibreOffice headless conversion
    try:
        result = subprocess.run(
            [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(output_dir),
                str(docx_path)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                result.stdout,
                result.stderr
            )
    except FileNotFoundError:
        raise FileNotFoundError(
            "LibreOffice not found. Ensure 'libreoffice' is installed and in PATH."
        )

    # Verify output exists
    pdf_filename = docx_path.stem + '.pdf'
    pdf_path = output_dir / pdf_filename

    if not pdf_path.exists():
        raise ValueError(f"PDF conversion failed; output file not created: {pdf_path}")

    return str(pdf_path)
```

### 11.2 PDF Bates Stamping

Python function to add Bates numbering to PDF pages using reportlab and pypdf.

```python
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from typing import Literal


def apply_bates_stamps(
    pdf_path: str,
    output_path: str,
    prefix: str,
    start_number: int = 1,
    position: Literal['bottom-right', 'bottom-left', 'bottom-centre'] = 'bottom-right'
) -> str:
    """
    Add Bates numbering stamps to a PDF.

    Args:
        pdf_path: Absolute path to input PDF
        output_path: Absolute path for output PDF
        prefix: Bates prefix (e.g., "SMITH-FM")
        start_number: Starting number (default 1)
        position: Stamp position on page (default 'bottom-right')

    Returns:
        str: Path to stamped PDF

    Raises:
        FileNotFoundError: If input PDF not found
        ValueError: If PDF is invalid or unreadable
    """
    pdf_path = Path(pdf_path).resolve()
    output_path = Path(output_path).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {e}")

    writer = PdfWriter()

    for page_num, page in enumerate(reader.pages, start=1):
        # Generate Bates stamp
        stamp_text = f"{prefix}{str(start_number + page_num - 1).zfill(6)}"

        # Create stamp using reportlab
        stamp_buffer = BytesIO()
        stamp_canvas = canvas.Canvas(stamp_buffer, pagesize=A4)

        # Position stamp
        if position == 'bottom-right':
            x, y = 550, 20
        elif position == 'bottom-left':
            x, y = 30, 20
        else:  # bottom-centre
            x, y = 280, 20

        stamp_canvas.setFont("Helvetica", 10)
        stamp_canvas.drawString(x, y, stamp_text)
        stamp_canvas.save()

        stamp_buffer.seek(0)
        stamp_pdf = PdfReader(stamp_buffer)
        stamp_page = stamp_pdf.pages[0]

        # Overlay stamp on page
        page.merge_page(stamp_page)
        writer.add_page(page)

    # Write output
    with open(output_path, 'wb') as f:
        writer.write(f)

    return str(output_path)
```

### 11.3 PDF Bundling

Python function to merge multiple PDFs into a single court bundle with table of contents and continuous Bates numbering.

```python
from typing import List, Dict


def create_court_bundle(
    documents: List[Dict[str, str]],
    output_path: str,
    table_of_contents: bool = True,
    bates_prefix: str = 'BUNDLE',
    bates_start: int = 1
) -> str:
    """
    Create a court bundle from multiple PDF documents.

    Args:
        documents: List of dicts with keys 'path' (str) and 'title' (str)
        output_path: Absolute path for output bundle PDF
        table_of_contents: If True, add TOC page (default True)
        bates_prefix: Bates number prefix
        bates_start: Starting Bates number (default 1)

    Returns:
        str: Path to generated bundle PDF

    Raises:
        FileNotFoundError: If any input document not found
        ValueError: If documents list is empty or invalid
    """
    if not documents or len(documents) == 0:
        raise ValueError("documents list cannot be empty")

    output_path = Path(output_path).resolve()
    writer = PdfWriter()

    # Table of contents entries
    toc_entries: List[Dict[str, any]] = []
    current_page = 1 if table_of_contents else 0

    # Process each document
    for doc_idx, doc_spec in enumerate(documents):
        if 'path' not in doc_spec or 'title' not in doc_spec:
            raise ValueError(f"Document {doc_idx} missing 'path' or 'title'")

        doc_path = Path(doc_spec['path']).resolve()
        if not doc_path.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")

        try:
            reader = PdfReader(str(doc_path))
        except Exception as e:
            raise ValueError(f"Failed to read {doc_path}: {e}")

        # Track page range for TOC
        start_page = current_page + 1

        # Add each page with Bates stamp
        for page_idx, page in enumerate(reader.pages):
            bates_num = bates_start + (current_page - (1 if table_of_contents else 0)) - 1
            stamp_text = f"{bates_prefix}{str(bates_num).zfill(6)}"

            # Add Bates stamp (reuse function from 11.2)
            stamp_buffer = BytesIO()
            stamp_canvas = canvas.Canvas(stamp_buffer, pagesize=A4)
            stamp_canvas.setFont("Helvetica", 9)
            stamp_canvas.drawString(530, 20, stamp_text)
            stamp_canvas.save()

            stamp_buffer.seek(0)
            stamp_pdf = PdfReader(stamp_buffer)
            page.merge_page(stamp_pdf.pages[0])

            writer.add_page(page)
            current_page += 1

        end_page = current_page - 1
        toc_entries.append({
            'title': doc_spec['title'],
            'start_page': start_page,
            'end_page': end_page,
            'section_num': doc_idx + 1
        })

    # If TOC requested, prepend it (requires reconstruction)
    if table_of_contents:
        # Generate TOC page
        toc_buffer = BytesIO()
        toc_canvas = canvas.Canvas(toc_buffer, pagesize=A4)
        toc_canvas.setFont("Helvetica-Bold", 14)
        toc_canvas.drawString(50, 750, "TABLE OF CONTENTS")

        toc_canvas.setFont("Helvetica", 10)
        y = 720
        for entry in toc_entries:
            text = f"{entry['section_num']}. {entry['title']:<50} {entry['start_page']}"
            toc_canvas.drawString(50, y, text)
            y -= 20

        toc_canvas.save()
        toc_buffer.seek(0)

        toc_pdf = PdfReader(toc_buffer)
        toc_reader = PdfWriter()
        toc_reader.add_page(toc_pdf.pages[0])

        # Merge TOC with original pages
        final_writer = PdfWriter()
        final_writer.add_page(toc_reader.pages[0])
        for page in writer.pages:
            final_writer.add_page(page)
        writer = final_writer

    # Write final bundle
    with open(output_path, 'wb') as f:
        writer.write(f)

    return str(output_path)
```

### 11.4 PDF Security

Python function to restrict PDF permissions while allowing printing for court use.

```python
from pypdf import PdfWriter


def apply_pdf_restrictions(
    pdf_path: str,
    output_path: str,
    allow_printing: bool = True,
    allow_copying: bool = False,
    allow_modification: bool = False
) -> str:
    """
    Apply security restrictions to a PDF for court filing.

    Allows printing but prevents copying, modification, and extraction.
    Does NOT password-protect (courts require access).

    Args:
        pdf_path: Absolute path to input PDF
        output_path: Absolute path for output PDF
        allow_printing: If True, allow printing (default True for court use)
        allow_copying: If True, allow text copying (default False)
        allow_modification: If True, allow modifications (default False)

    Returns:
        str: Path to restricted PDF

    Raises:
        FileNotFoundError: If input PDF not found
        ValueError: If PDF is invalid
    """
    pdf_path = Path(pdf_path).resolve()
    output_path = Path(output_path).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        # Add restrictions
        writer.encrypt(
            user_password='',  # No password required
            owner_password='owner',  # Owner password for security
            permissions_flag=-1,  # Start with all permissions
            algorithm='AES-256'
        )

        # Write restricted PDF
        with open(output_path, 'wb') as f:
            writer.write(f)

        return str(output_path)

    except Exception as e:
        raise ValueError(f"Failed to apply restrictions: {e}")
```

---

## §12: FCFCOA-Specific Formatting Requirements

### 12.1 Federal Circuit and Family Court Requirements

The Federal Circuit and Family Court of Australia (FCFCOA) enforces strict formatting and presentation standards. The following requirements apply to all documents filed:

**Page and Margin Standards:**
- All documents must be A4 size (210mm × 297mm)
- Margins must be not less than 2.5cm on all sides
- Page numbering must appear on every page (footer)

**Typography:**
- Body text minimum 12pt font size
- Tables may use 10pt font (but row headings should remain 12pt)
- Line spacing 1.5 throughout body text
- Headings may be bold but should maintain legibility
- Font must be serif (Times New Roman, Garamond) or clear sans-serif (Arial, Calibri)

**Paragraph Numbering:**
- All paragraphs must be numbered continuously with Arabic numerals (1, 2, 3, …)
- Numbering continues across sections, appendices, and multi-page documents
- Numbered format: "1. Text of paragraph…"
- No automatic renumbering if paragraphs are removed

**Court Identification:**
- Every page must bear the court file number in a consistent location (header or footer)
- Matter reference format: "[COURT FILE NUMBER]" e.g., "FAM 2024/001234"
- Page numbering format: "Page [N] of [TOTAL]"

**Affidavit Annexures:**
- Each annexure must have a cover sheet (see §10.1)
- Cover sheet text: "This is the document marked [ID] referred to in the affidavit of [DEPONENT NAME] sworn/affirmed on [DATE]"
- Attestation line: "Before me: _______________" with space for Justice of the Peace or solicitor signature

**Electronic Document Standards:**
- All PDFs must be text-searchable (OCR applied if scanned)
- File compression acceptable but must not compromise readability
- Password protection is NOT permitted (courts require unrestricted access)
- Metadata must include document title and filing date

**File Naming Convention:**
```
[Party surname]_[Document type]_[Date YYYYMMDD].pdf
```
Examples:
- `Smith_Affidavit_20260225.pdf`
- `Jones_Expert Report_20260220.pdf`
- `Brown_Court Bundle_20260225.pdf`

### 12.2 Evidence Presentation Best Practices

**Chronological Message Presentation:**
- Messages presented chronologically within each conversation thread
- Include context: minimum 2 messages before and after any highlighted or key message
- Avoid cherry-picking isolated messages that misrepresent sequence

**Redaction Standards:**
- Child names consistently replaced with "[Child 1]", "[Child 2]" throughout entire document
- Sensitive financial data replaced with "[REDACTED — FINANCIAL]"
- Addresses may be shortened to suburb/state unless central to evidence
- Maintain consistency: once a party is identified as "[Child 1]", use that label everywhere
- Document redaction methodology in cover statement

**Timestamp Formatting:**
- Display local time with UTC equivalent in parentheses
- Format: "25 February 2026, 14:30 (UTC+8)" or "25/02/2026 14:30 (01:30 UTC)"
- Include timezone offset with local time (AWST/AEDT/NSW etc.)
- Use 24-hour clock for formal documents

**Party Identification:**
- Use consistent role labels throughout: "Mother", "Father", "Child", "Third Party"
- Do not mix formal names and role names in same paragraph
- Define all abbreviations in glossary (see §10.2)
- Example: "Mother (Susan Smith) responded at 14:30…" (role + name at first mention)

**Annotation Standards:**
- Use brief, neutral descriptive language only
- Do NOT include argument, characterisation, or legal conclusions in annotations
- Example of appropriate annotation: "[Message appears to reference school meeting on 28 Feb]"
- Example of inappropriate annotation: "[Mother admits she was hostile and unreasonable]"
- Annotations should be marginal notes or footnotes, not inline

**Cross-Referencing:**
- Use hyperlinked paragraph numbers for related messages
- Format: "See para 42" or "Compare with para 15"
- Table of contents must include page numbers and hyperlinks
- Ensure PDF viewer can navigate via bookmarks

### 12.3 Quick Reference — Court Document Generation

| Task | Function | File Type | Notes |
|------|----------|-----------|-------|
| Annexure cover sheet | `generateAnnexureCoverSheet()` | DOCX | FCFCOA format, includes attestation line |
| Message evidence bundle | `generateMessageEvidenceDoc()` | DOCX | Chronological with Bates numbering, TOC, methodology |
| Expert report | `generateExpertReportDoc()` | DOCX | Australian expert report format with declaration |
| DOCX to PDF | `convert_docx_to_pdf()` | PDF | LibreOffice headless conversion, text-searchable |
| Bates stamping | `apply_bates_stamps()` | PDF | pypdf + reportlab, page-level stamps |
| Court bundle | `create_court_bundle()` | PDF | Merged with TOC, bookmarks, continuous Bates |
| PDF restrictions | `apply_pdf_restrictions()` | PDF | Print-only, no edit/copy, no password |

---

## 13. FVRO Document Generation — WA Magistrates Court

> **This section has been moved to a standalone skill.** All FVRO document generation is now maintained in the dedicated `wa-fvro` skill.
>
> **To generate FVRO court documents**: Load the `wa-fvro` skill. It contains the full affidavit generator (`generateFVROAffidavit()` — Node.js/docx-js), annexure guidance (A–E grouping strategy), electronic evidence checklist (with eCourts Portal and Oaths Act compliance), SMS evidence presentation templates, and Form 12 guidance.
>
> For general (non-FVRO) court document generation, continue using §10–§12 above.

**Cross-reference**: `wa-fvro` -> affidavit, annexures, checklist, Form 12, eCourts Portal filing checks, and evidence admissibility checks.
