# CSV Legal Analysis — Analysis Workflows

## Table of Contents

1. [Data Loading & Encoding](#1-data-loading--encoding)
2. [Dataset Profiling](#2-dataset-profiling)
3. [Deduplication](#3-deduplication)
4. [Date/Time Normalisation & Timeline Analysis](#4-datetime-normalisation--timeline-analysis)
5. [Entity Extraction](#5-entity-extraction)
6. [Statistical & Frequency Analysis](#6-statistical--frequency-analysis)
7. [Anomaly Detection](#7-anomaly-detection)
8. [Cross-Reference & Join Analysis](#8-cross-reference--join-analysis)
9. [Communications Data Patterns](#9-communications-data-patterns)
10. [Financial Data Patterns](#10-financial-data-patterns)
11. [Access Log Patterns](#11-access-log-patterns)

---

## 1. Data Loading & Encoding

### Robust CSV Loading

```python
import pandas as pd
import chardet
import io

def load_csv_safely(filepath):
    """Load CSV with automatic encoding detection and fallback chain."""
    # Try UTF-8 with BOM first (most common for Windows exports)
    for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            df = pd.read_csv(
                filepath,
                encoding=encoding,
                low_memory=False,
                dtype=str          # Load all as string to prevent type coercion
            )
            print(f"Loaded with encoding: {encoding}")
            return df, encoding
        except UnicodeDecodeError:
            continue

    # Last resort: chardet detection
    with open(filepath, 'rb') as f:
        detected = chardet.detect(f.read())
    df = pd.read_csv(filepath, encoding=detected['encoding'], low_memory=False, dtype=str)
    return df, detected['encoding']

# Usage
df, encoding_used = load_csv_safely('/path/to/file.csv')
```

### Handling Malformed CSV

```python
# Skip bad lines (log them)
bad_lines = []
df = pd.read_csv(
    filepath,
    encoding='utf-8-sig',
    on_bad_lines='warn',   # or 'skip' to suppress warnings
    dtype=str
)

# For files with inconsistent delimiters
df = pd.read_csv(filepath, sep=None, engine='python', dtype=str)

# For semicolon-delimited (common in European exports)
df = pd.read_csv(filepath, sep=';', encoding='utf-8-sig', dtype=str)
```

### Large File Handling

```python
# For very large files (>500k rows), use chunked processing
chunk_size = 50_000
chunks = []
for chunk in pd.read_csv(filepath, chunksize=chunk_size, encoding='utf-8-sig', dtype=str):
    # Apply any initial filtering before accumulating
    chunks.append(chunk)
df = pd.concat(chunks, ignore_index=True)
```

---

## 2. Dataset Profiling

### Comprehensive Profile Function

```python
def profile_dataset(df, dataset_name="Dataset"):
    """Generate a comprehensive dataset profile for legal analysis."""
    report = []
    report.append(f"DATASET PROFILE: {dataset_name}")
    report.append("=" * 60)
    report.append(f"Rows: {len(df):,}")
    report.append(f"Columns: {len(df.columns)}")
    report.append(f"Total cells: {len(df) * len(df.columns):,}")
    report.append(f"Duplicate rows: {df.duplicated().sum():,} ({df.duplicated().mean()*100:.1f}%)")
    report.append("")

    report.append("COLUMNS:")
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_pct = null_count / len(df) * 100
        unique_count = df[col].nunique()
        sample = df[col].dropna().head(2).tolist()
        report.append(
            f"  {col}: {unique_count:,} unique | {null_count:,} nulls ({null_pct:.1f}%) | "
            f"sample: {sample}"
        )

    report.append("")
    report.append("POTENTIAL DATE COLUMNS:")
    date_candidates = []
    for col in df.columns:
        if any(kw in col.lower() for kw in ['date', 'time', 'created', 'modified', 'sent', 'received', 'timestamp']):
            date_candidates.append(col)
            sample_val = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else 'N/A'
            report.append(f"  {col}: sample value = {sample_val}")

    report.append("")
    report.append("POTENTIAL TEXT COLUMNS (for keyword search):")
    for col in df.columns:
        if df[col].dtype == object:
            avg_len = df[col].dropna().str.len().mean()
            if avg_len and avg_len > 20:
                report.append(f"  {col}: avg length = {avg_len:.0f} chars")

    return "\n".join(report)

# Usage
print(profile_dataset(df, "Communications Export 2024-01-01"))
```

---

## 3. Deduplication

### Exact Duplicate Detection

```python
# Find exact duplicates
duplicates = df[df.duplicated(keep=False)]
print(f"Exact duplicates: {len(duplicates):,} rows ({duplicates.duplicated().sum():,} redundant)")

# Show duplicate groups
dupe_groups = df[df.duplicated(keep='first')]

# Remove duplicates (preserving original index for audit)
df_deduped = df.drop_duplicates(keep='first')
removed_indices = set(df.index) - set(df_deduped.index)
print(f"Removed {len(removed_indices):,} duplicate rows. Original indices: {sorted(removed_indices)[:20]}...")
```

### Near-Duplicate Detection (for communications)

```python
# Requires: pip install fuzzywuzzy
from fuzzywuzzy import fuzz

def find_near_duplicates(df, text_column, threshold=90, sample_size=1000):
    """
    Find near-duplicate rows based on text similarity.
    Returns a DataFrame with original DataFrame row indices for traceability.
    Samples for performance on large datasets.
    """
    # Preserve original row indices alongside values
    sample_series = df[text_column].dropna().head(sample_size)
    sample_pairs = list(sample_series.items())  # [(original_row_index, value), ...]
    near_dupes = []

    for i in range(len(sample_pairs)):
        for j in range(i + 1, len(sample_pairs)):
            row_idx_1, text_1 = sample_pairs[i]
            row_idx_2, text_2 = sample_pairs[j]
            score = fuzz.ratio(str(text_1), str(text_2))
            if score >= threshold:
                near_dupes.append({
                    'row_index_1': row_idx_1,   # Original DataFrame index
                    'row_index_2': row_idx_2,   # Original DataFrame index
                    'similarity': score,
                    'text_1': str(text_1)[:100],
                    'text_2': str(text_2)[:100],
                })

    return pd.DataFrame(near_dupes)
```

---

## 4. Date/Time Normalisation & Timeline Analysis

### Date Column Detection and Normalisation

```python
import pandas as pd
from dateutil import parser as date_parser

def normalise_dates(df, date_columns=None):
    """Detect and normalise date columns to ISO 8601."""
    if date_columns is None:
        # Auto-detect
        date_columns = [col for col in df.columns
                       if any(kw in col.lower() for kw in
                              ['date', 'time', 'created', 'modified', 'sent',
                               'received', 'timestamp', 'dob'])]

    for col in date_columns:
        original_col = f"_original_{col}"
        df[original_col] = df[col]  # Preserve original
        df[col] = pd.to_datetime(df[col], infer_format=True, errors='coerce', utc=False)
        failed = df[col].isnull().sum()
        if failed > 0:
            print(f"WARNING: {col} — {failed:,} values could not be parsed as dates")

    return df

# Timeline summary
def timeline_summary(df, date_column):
    """Summarise the timeline of a dataset."""
    dates = pd.to_datetime(df[date_column], errors='coerce')
    valid = dates.dropna()

    print(f"Date range: {valid.min()} → {valid.max()}")
    print(f"Total span: {(valid.max() - valid.min()).days:,} days")
    print(f"Invalid/null dates: {dates.isnull().sum():,}")

    # Monthly activity
    monthly = valid.dt.to_period('M').value_counts().sort_index()
    print(f"\nMonthly activity:\n{monthly}")

    # Day of week distribution
    dow = valid.dt.day_name().value_counts()
    print(f"\nDay of week distribution:\n{dow}")
```

### Chronological Event Reconstruction

```python
def build_timeline(df, date_column, relevant_columns=None, output_path=None):
    """Build a sorted timeline of events for analysis."""
    df_timeline = df.copy()
    df_timeline['_parsed_date'] = pd.to_datetime(df_timeline[date_column], errors='coerce')
    df_timeline = df_timeline.sort_values('_parsed_date', na_position='last')
    df_timeline['_sequence_number'] = range(1, len(df_timeline) + 1)

    # Add row ID for reference back to original
    df_timeline['_original_row_index'] = df_timeline.index

    if output_path:
        df_timeline.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Timeline saved: {output_path}")

    return df_timeline

# Gap analysis: find unusual silences or gaps
def detect_temporal_gaps(df_timeline, date_column, expected_frequency_hours=24):
    """Identify unusually large gaps in a time series."""
    dates = pd.to_datetime(df_timeline[date_column], errors='coerce').sort_values().dropna()
    gaps = dates.diff()
    threshold = pd.Timedelta(hours=expected_frequency_hours * 3)  # 3x expected = unusual
    significant_gaps = gaps[gaps > threshold]

    for idx, gap in significant_gaps.items():
        gap_start = dates[idx - 1] if idx > 0 else "N/A"
        print(f"Gap of {gap} starting at {gap_start}")

    return significant_gaps
```

---

## 5. Entity Extraction

### Common Entity Patterns (Regex)

```python
import re

# Pre-compiled patterns for performance
PATTERNS = {
    'email':       re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b'),
    'phone_au':    re.compile(r'(?:\+61|0)[0-9]{1,2}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}'),
    'phone_any':   re.compile(r'(?:\+?[0-9]{1,3}[\s\-\.]?)?\(?[0-9]{2,4}\)?[\s\-\.][0-9]{3,4}[\s\-\.][0-9]{3,5}'),
    'ip_address':  re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
    'url':         re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),
    'date_iso':    re.compile(r'\b\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2})?'),
    'date_aus':    re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'),
    'dollar_aus':  re.compile(r'\$[\d,]+(?:\.\d{2})?'),
    'abn':         re.compile(r'\b\d{2}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{3}\b'),  # Australian Business Number
    'acn':         re.compile(r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{3}\b'),               # Australian Company Number
    'tfn':         re.compile(r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{3}\b'),               # Tax File Number (same pattern — context matters)
}

def extract_entities(df, text_columns, entity_types=None):
    """Extract entities from specified text columns."""
    if entity_types is None:
        entity_types = ['email', 'phone_au', 'url']

    results = {entity_type: [] for entity_type in entity_types}

    for col in text_columns:
        for entity_type in entity_types:
            if entity_type in PATTERNS:
                matches = df[col].dropna().str.extractall(PATTERNS[entity_type].pattern)
                if len(matches) > 0:
                    results[entity_type].extend(matches[0].tolist())

    # Deduplicated frequency counts
    from collections import Counter
    entity_summary = {}
    for entity_type, values in results.items():
        entity_summary[entity_type] = Counter(values).most_common(50)

    return entity_summary

def extract_emails_with_context(df, text_column):
    """Extract unique email addresses with frequency and first-seen row."""
    all_emails = {}
    for idx, text in df[text_column].dropna().items():
        found = PATTERNS['email'].findall(str(text))
        for email in found:
            email = email.lower().strip()
            if email not in all_emails:
                all_emails[email] = {'count': 0, 'first_row': idx}
            all_emails[email]['count'] += 1

    return pd.DataFrame([
        {'email': k, 'count': v['count'], 'first_row': v['first_row']}
        for k, v in sorted(all_emails.items(), key=lambda x: -x[1]['count'])
    ])
```

---

## 6. Statistical & Frequency Analysis

### Numeric Column Analysis

```python
def analyse_numeric_columns(df):
    """Perform statistical analysis on numeric columns."""
    # Convert string columns that look numeric
    numeric_df = df.apply(pd.to_numeric, errors='coerce')
    numeric_cols = numeric_df.columns[numeric_df.notna().any()]

    stats = []
    for col in numeric_cols:
        series = numeric_df[col].dropna()
        if len(series) == 0:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        outlier_low = q1 - 1.5 * iqr
        outlier_high = q3 + 1.5 * iqr
        outliers = series[(series < outlier_low) | (series > outlier_high)]

        stats.append({
            'column': col,
            'count': len(series),
            'mean': series.mean(),
            'median': series.median(),
            'std_dev': series.std(),
            'min': series.min(),
            'max': series.max(),
            'q1': q1,
            'q3': q3,
            'outlier_count': len(outliers),
            'outlier_pct': len(outliers) / len(series) * 100
        })

    return pd.DataFrame(stats)

# Frequency analysis for categorical columns
def top_values(df, column, n=20):
    """Get top N value counts for a column."""
    vc = df[column].value_counts(dropna=False)
    return vc.head(n)
```

---

## 7. Anomaly Detection

### Rule-Based Anomaly Flagging

```python
def flag_anomalies(df, rules):
    """
    Flag rows matching anomaly rules.
    rules: list of dicts with keys: name, condition (lambda), severity

    Example rules:
    rules = [
        {'name': 'Future date', 'severity': 'HIGH',
         'condition': lambda df: pd.to_datetime(df['date'], errors='coerce') > pd.Timestamp.now()},
        {'name': 'Negative amount', 'severity': 'MEDIUM',
         'condition': lambda df: pd.to_numeric(df['amount'], errors='coerce') < 0},
        {'name': 'Weekend transaction', 'severity': 'LOW',
         'condition': lambda df: pd.to_datetime(df['date'], errors='coerce').dt.dayofweek >= 5},
    ]
    """
    df_flagged = df.copy()
    df_flagged['_anomaly_flags'] = ''
    df_flagged['_anomaly_severity'] = ''

    for rule in rules:
        try:
            mask = rule['condition'](df)
            df_flagged.loc[mask, '_anomaly_flags'] += f"|{rule['name']}"
            df_flagged.loc[mask, '_anomaly_severity'] += f"|{rule['severity']}"
        except Exception as e:
            print(f"Rule '{rule['name']}' failed: {e}")

    flagged = df_flagged[df_flagged['_anomaly_flags'] != '']
    print(f"Total anomalies flagged: {len(flagged):,} rows")

    return df_flagged, flagged

# Statistical outlier detection (Z-score method)
def zscore_outliers(df, numeric_column, threshold=3.0):
    """Flag statistical outliers using Z-score."""
    series = pd.to_numeric(df[numeric_column], errors='coerce')
    mean = series.mean()
    std = series.std()
    z_scores = (series - mean) / std
    outliers = df[z_scores.abs() > threshold].copy()
    outliers['_zscore'] = z_scores[z_scores.abs() > threshold]
    return outliers.sort_values('_zscore', key=abs, ascending=False)
```

---

## 8. Cross-Reference & Join Analysis

### Comparing Two Datasets

```python
def compare_datasets(df1, df2, key_column, name1="Dataset 1", name2="Dataset 2"):
    """Compare two datasets on a common key — useful for identifying gaps or additions."""
    keys1 = set(df1[key_column].dropna().unique())
    keys2 = set(df2[key_column].dropna().unique())

    in_1_only = keys1 - keys2
    in_2_only = keys2 - keys1
    in_both = keys1 & keys2

    print(f"Keys in {name1} only: {len(in_1_only):,}")
    print(f"Keys in {name2} only: {len(in_2_only):,}")
    print(f"Keys in both: {len(in_both):,}")

    return {
        'in_1_only': df1[df1[key_column].isin(in_1_only)],
        'in_2_only': df2[df2[key_column].isin(in_2_only)],
        'in_both_from_1': df1[df1[key_column].isin(in_both)],
        'in_both_from_2': df2[df2[key_column].isin(in_both)],
    }
```

---

## 9. Communications Data Patterns

For datasets containing email/message exports (sender, recipient, subject, body, date).

### Correspondence Network Analysis

```python
def communication_network(df, sender_col, recipient_col):
    """Analyse communication patterns between parties."""
    # Normalise email addresses
    df[sender_col] = df[sender_col].str.lower().str.strip()
    df[recipient_col] = df[recipient_col].str.lower().str.strip()

    # Message counts by sender
    sender_counts = df[sender_col].value_counts()

    # Communication pairs
    df['_comm_pair'] = df.apply(
        lambda r: tuple(sorted([str(r[sender_col]), str(r[recipient_col])])), axis=1
    )
    pair_counts = df['_comm_pair'].value_counts()

    print("Top senders:")
    print(sender_counts.head(10))
    print("\nTop communication pairs:")
    print(pair_counts.head(10))

    return sender_counts, pair_counts

# Thread reconstruction
def reconstruct_threads(df, subject_col, date_col, sender_col):
    """Group messages into conversation threads by subject."""
    # Normalise subject (remove Re:, Fwd: prefixes)
    df['_clean_subject'] = df[subject_col].str.lower().str.replace(
        r'^(re:|fwd:|fw:)+\s*', '', regex=True
    ).str.strip()

    threads = df.groupby('_clean_subject').agg(
        message_count=('_clean_subject', 'count'),
        participants=(sender_col, lambda x: list(x.unique())),
        date_range_start=(date_col, 'min'),
        date_range_end=(date_col, 'max')
    ).sort_values('message_count', ascending=False)

    return threads
```

---

## 10. Financial Data Patterns

For datasets containing financial transactions.

```python
def analyse_transactions(df, amount_col, date_col, party_col=None):
    """Analyse financial transaction patterns for anomalies."""
    df['_amount_numeric'] = pd.to_numeric(df[amount_col].astype(str).str.replace(',', '').str.replace('$', ''), errors='coerce')
    df['_date_parsed'] = pd.to_datetime(df[date_col], errors='coerce')

    # Round-dollar transactions (potentially suspicious)
    round_dollar = df[df['_amount_numeric'] % 1 == 0]
    print(f"Round-dollar transactions: {len(round_dollar):,} ({len(round_dollar)/len(df)*100:.1f}%)")

    # Structuring detection (transactions just under common reporting thresholds)
    for threshold in [10000, 5000, 1000]:  # AUD reporting thresholds
        just_under = df[(df['_amount_numeric'] >= threshold * 0.9) & (df['_amount_numeric'] < threshold)]
        print(f"Transactions ${ threshold * 0.9:.0f}–${ threshold - 0.01:.2f}: {len(just_under):,}")

    # Velocity: multiple transactions same day same party
    if party_col:
        daily_velocity = df.groupby([df['_date_parsed'].dt.date, party_col]).size()
        high_velocity = daily_velocity[daily_velocity > 3]
        print(f"\nHigh-velocity party/day combinations (>3 transactions): {len(high_velocity):,}")
```

---

## 11. Access Log Patterns

For audit logs, system access records.

```python
def analyse_access_logs(df, user_col, timestamp_col, action_col=None, resource_col=None):
    """Analyse access log patterns for anomalies."""
    df['_ts'] = pd.to_datetime(df[timestamp_col], errors='coerce')
    df['_hour'] = df['_ts'].dt.hour
    df['_dow'] = df['_ts'].dt.day_name()

    # After-hours access (outside 7am–7pm)
    after_hours = df[(df['_hour'] < 7) | (df['_hour'] >= 19)]
    print(f"After-hours access events: {len(after_hours):,} ({len(after_hours)/len(df)*100:.1f}%)")

    # Access on weekends
    weekend = df[df['_dow'].isin(['Saturday', 'Sunday'])]
    print(f"Weekend access events: {len(weekend):,}")

    # Top users by activity
    print(f"\nTop 10 most active users:\n{df[user_col].value_counts().head(10)}")

    # Unique users per day (unusual spikes)
    if resource_col:
        resource_access = df.groupby(resource_col)[user_col].nunique().sort_values(ascending=False)
        print(f"\nTop accessed resources (unique users):\n{resource_access.head(10)}")

    return after_hours, weekend
```

---

## 12. Benford's Law Analysis (Financial Fraud Screening)

Apply Benford's Law to detect potential financial manipulation. Benford's Law states that in naturally occurring datasets, the first digit follows a logarithmic distribution. Significant deviations suggest potential manipulation or fraud.

```python
import numpy as np
import pandas as pd
from scipy import stats

def benfords_law_test(df, amount_column, min_value=1.0):
    """
    Apply Benford's Law to detect potential financial manipulation.

    Benford's Law: first digits in naturally occurring data follow a logarithmic distribution.
    Significant deviation suggests potential manipulation.

    Returns: chi-squared statistic, p-value, digit frequency comparison DataFrame
    """
    amounts = pd.to_numeric(df[amount_column].astype(str).str.replace('[,$]', '', regex=True), errors='coerce')
    amounts = amounts[amounts >= min_value].dropna()

    # Extract first significant digit
    first_digits = amounts.astype(str).str.lstrip('0').str[0]
    first_digits = first_digits[first_digits.str.isdigit()].astype(int)
    first_digits = first_digits[first_digits.between(1, 9)]

    # Benford expected frequencies
    expected_freq = {d: np.log10(1 + 1/d) for d in range(1, 10)}

    observed = first_digits.value_counts().sort_index()
    total = len(first_digits)

    results = []
    for digit in range(1, 10):
        obs_count = observed.get(digit, 0)
        obs_pct = obs_count / total * 100 if total > 0 else 0
        exp_pct = expected_freq[digit] * 100
        deviation = obs_pct - exp_pct
        results.append({
            'digit': digit,
            'observed_count': obs_count,
            'observed_pct': round(obs_pct, 2),
            'expected_pct': round(exp_pct, 2),
            'deviation_pct': round(deviation, 2),
            'suspicious': abs(deviation) > 5  # >5% deviation is notable
        })

    df_results = pd.DataFrame(results)

    # Chi-squared test
    observed_counts = [r['observed_count'] for r in results]
    expected_counts = [expected_freq[d] * total for d in range(1, 10)]
    chi2, p_value = stats.chisquare(observed_counts, expected_counts)

    print(f"Benford's Law Analysis — {amount_column}")
    print(f"Sample size: {total:,} values")
    print(f"Chi-squared: {chi2:.2f} | p-value: {p_value:.4f}")
    print(f"Interpretation: {'SIGNIFICANT DEVIATION (p<0.05) — warrants investigation' if p_value < 0.05 else 'No significant deviation from Benford distribution'}")
    print("\nDigit frequency comparison:")
    print(df_results.to_string(index=False))

    return df_results, chi2, p_value
```

---

## 13. Network/Graph Analysis (Communications)

Build a communication network graph to identify key nodes (connectors, isolates), clusters, and communication flow patterns.

```python
def build_communication_graph(df, sender_col, recipient_col, date_col=None):
    """
    Build a communication network graph for analysis.
    Identifies key nodes (connectors, isolates), clusters, and communication flow.
    Requires: pip install networkx
    """
    import networkx as nx

    G = nx.DiGraph()

    for _, row in df.iterrows():
        sender = str(row[sender_col]).lower().strip()
        recipient = str(row[recipient_col]).lower().strip()
        if sender and recipient and sender != 'nan' and recipient != 'nan':
            if G.has_edge(sender, recipient):
                G[sender][recipient]['weight'] += 1
            else:
                G.add_edge(sender, recipient, weight=1)

    # Key metrics
    print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Degree centrality (who communicates most)
    centrality = nx.degree_centrality(G)
    top_nodes = sorted(centrality.items(), key=lambda x: -x[1])[:10]
    print("\nTop 10 most connected nodes:")
    for node, score in top_nodes:
        in_deg = G.in_degree(node)
        out_deg = G.out_degree(node)
        print(f"  {node}: centrality={score:.3f}, received={in_deg}, sent={out_deg}")

    # Isolates (nodes with no connections in one direction — unusual)
    isolates = list(nx.isolates(G.to_undirected()))
    if isolates:
        print(f"\nIsolated nodes (no two-way communication): {isolates}")

    return G, centrality

def find_communication_clusters(G):
    """Identify tightly connected communication clusters (potential working groups or conspirators)."""
    import networkx as nx
    undirected = G.to_undirected()
    communities = list(nx.connected_components(undirected))
    print(f"Communication clusters: {len(communities)}")
    for i, community in enumerate(sorted(communities, key=len, reverse=True)[:5], 1):
        members = list(community)
        print(f"  Cluster {i}: {len(members)} members — {members[:5]}{'...' if len(members) > 5 else ''}")
    return communities
```

---

## 14. Multi-File Dataset Handling

Load and merge multiple CSV files from the same source while tracking provenance for each row.

```python
import os
import glob
import pandas as pd
import hashlib

def load_multiple_csvs(directory, pattern='*.csv', encoding='utf-8-sig'):
    """
    Load and merge multiple CSV files from a directory.
    Tracks source file provenance for each row.
    """
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' in {directory}")

    dfs = []
    file_manifest = []

    for filepath in sorted(files):
        # Hash each source file
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        file_hash = h.hexdigest()

        try:
            df = pd.read_csv(filepath, encoding=encoding, low_memory=False, dtype=str)
            df['_source_file'] = os.path.basename(filepath)
            df['_source_file_hash'] = file_hash
            df['_source_row_number'] = range(1, len(df) + 1)
            dfs.append(df)
            file_manifest.append({
                'filename': os.path.basename(filepath),
                'sha256': file_hash,
                'rows': len(df),
                'columns': list(df.columns)
            })
            print(f"  Loaded: {os.path.basename(filepath)} — {len(df):,} rows")
        except Exception as e:
            print(f"  ERROR loading {filepath}: {e}")

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\nCombined dataset: {len(combined):,} rows from {len(dfs)} files")

    return combined, file_manifest

def detect_dataset_gaps(df1, df2, key_col, date_col=None, name1='Dataset A', name2='Dataset B'):
    """
    Compare two related datasets to find records present in one but not the other.
    Useful for detecting missing records, deletions, or production set discrepancies.
    """
    keys1 = set(df1[key_col].dropna().astype(str))
    keys2 = set(df2[key_col].dropna().astype(str))

    only_in_1 = keys1 - keys2
    only_in_2 = keys2 - keys1
    in_both = keys1 & keys2

    print(f"Dataset comparison on '{key_col}':")
    print(f"  {name1}: {len(keys1):,} unique keys")
    print(f"  {name2}: {len(keys2):,} unique keys")
    print(f"  In both: {len(in_both):,}")
    print(f"  Only in {name1}: {len(only_in_1):,} ← potential deletions/omissions")
    print(f"  Only in {name2}: {len(only_in_2):,} ← potential additions/insertions")

    gaps_df = pd.DataFrame({
        'key': list(only_in_1),
        'status': f'Only in {name1}',
        'note': 'Present in first dataset but absent from second — review for deletion or omission'
    })
    return gaps_df, only_in_1, only_in_2
```

---

## 15. Text Similarity & Document Clustering

Cluster documents by text similarity using TF-IDF and K-Means. Useful for identifying document families and categorising large datasets.

```python
def cluster_documents_by_similarity(df, text_column, n_clusters=10, sample_size=5000):
    """
    Cluster documents by text similarity using TF-IDF and K-Means.
    Useful for identifying document families and categorising large datasets.
    Requires: pip install scikit-learn
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans

    texts = df[text_column].fillna('').head(sample_size).tolist()

    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', min_df=2)
    tfidf_matrix = vectorizer.fit_transform(texts)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(tfidf_matrix)

    df_sample = df.head(sample_size).copy()
    df_sample['_doc_cluster'] = clusters

    # Top terms per cluster
    feature_names = vectorizer.get_feature_names_out()
    for i in range(n_clusters):
        center = kmeans.cluster_centers_[i]
        top_terms = [feature_names[j] for j in center.argsort()[-5:][::-1]]
        cluster_size = (clusters == i).sum()
        print(f"Cluster {i} ({cluster_size} docs): {', '.join(top_terms)}")

    return df_sample, kmeans, vectorizer
```

## Section 16: Currency Normalization

Multi-currency datasets require normalization to a single currency (AUD) for legal analysis. Preserve original values while creating normalized fields for comparison and aggregation.

### Detect Multi-Currency Data

```python
import re
from typing import Dict, List, Tuple

def detect_currencies(df, currency_columns=None):
    """
    Detect multiple currencies in dataset.
    Returns mapping of column to detected currencies.
    """
    if currency_columns is None:
        # Auto-detect columns with currency indicators
        currency_columns = [col for col in df.columns
                           if any(kw in col.lower() for kw in ['amount', 'price', 'value', 'cost', 'fee'])]

    currency_pattern = r'(USD|AUD|EUR|GBP|JPY|CNY|CAD|NZD|SGD|HKD|\$|€|£|¥)'
    currencies_found = {}

    for col in currency_columns:
        if col in df.columns:
            # Check column values and name for currency indicators
            col_currencies = set()
            col_currencies.update(re.findall(currency_pattern, df[col].astype(str).str.cat(), flags=re.IGNORECASE))

            # Check column name
            if 'USD' in col.upper():
                col_currencies.add('USD')
            elif 'EUR' in col.upper():
                col_currencies.add('EUR')
            elif 'GBP' in col.upper():
                col_currencies.add('GBP')
            elif 'JPY' in col.upper():
                col_currencies.add('JPY')

            if col_currencies:
                currencies_found[col] = col_currencies

    return currencies_found


def normalize_to_aud(df, exchange_rates, source_currency_col=None, amount_col='Amount',
                    rate_date_col=None, documented_rate_source='RBA'):
    """
    Normalize amounts to AUD using documented exchange rates.

    Args:
        df: DataFrame with amount columns
        exchange_rates: Dict mapping (currency, date) -> rate, or just currency -> rate
        source_currency_col: Column containing source currency code
        amount_col: Column name with amounts
        rate_date_col: Column with rate dates for time-based conversion
        documented_rate_source: Source of exchange rates (RBA, ECB, XE.com, etc.)

    Returns:
        DataFrame with new columns: {amount_col}_original_aud, {amount_col}_normalized_aud,
        _exchange_rate_applied, _rate_date_applied, _rate_source
    """
    df = df.copy()

    # Preserve original
    df[f'{amount_col}_original'] = df[amount_col]
    df[f'{amount_col}_original_currency'] = df[source_currency_col] if source_currency_col else 'AUD'

    # Initialize normalized column
    df[f'{amount_col}_normalized_aud'] = df[amount_col]
    df['_exchange_rate_applied'] = 1.0
    df['_rate_date_applied'] = None
    df['_rate_source'] = documented_rate_source

    # Apply conversion for non-AUD
    if source_currency_col:
        mask = df[source_currency_col] != 'AUD'

        for idx in df[mask].index:
            currency = df.loc[idx, source_currency_col]
            amount = df.loc[idx, amount_col]

            # Determine exchange rate
            rate = None
            rate_applied_date = None

            if rate_date_col and rate_date_col in df.columns:
                # Time-based lookup
                rate_date = df.loc[idx, rate_date_col]
                key = (currency, rate_date)
                if key in exchange_rates:
                    rate = exchange_rates[key]
                    rate_applied_date = rate_date

            # Fallback to static rate
            if rate is None and currency in exchange_rates:
                rate = exchange_rates[currency]

            # Apply conversion
            if rate is not None and amount is not None:
                try:
                    df.loc[idx, f'{amount_col}_normalized_aud'] = float(amount) * float(rate)
                    df.loc[idx, '_exchange_rate_applied'] = float(rate)
                    df.loc[idx, '_rate_date_applied'] = rate_applied_date
                except (ValueError, TypeError):
                    pass

    return df


# Example with documented exchange rates (as of legal proceeding date)
exchange_rates_2024 = {
    'USD': 1.52,    # 1 USD = 1.52 AUD (as at 2024-02-23)
    'EUR': 1.66,    # 1 EUR = 1.66 AUD
    'GBP': 1.92,    # 1 GBP = 1.92 AUD
    'JPY': 0.0102,  # 1 JPY = 0.0102 AUD
    'CNY': 0.21,    # 1 CNY = 0.21 AUD
}

# Usage example
# df_normalized = normalize_to_aud(df, exchange_rates_2024, 'Currency', 'Amount')
```

### Legal Requirements for Currency Documentation

**Australia (Federal Court, GPN-TECH):**
- Must document exchange rate source (RBA, ECB, XE.com, banking records)
- Include conversion date for each transaction
- Preserve original amounts and currencies
- State exchange rate basis in expert report

**Admissibility Checklist:**
- [ ] Exchange rates from published, reliable source (RBA preferred)
- [ ] Conversion date disclosed
- [ ] Original and normalized amounts both shown
- [ ] Methodology documented in report
- [ ] Rate source cited in evidence
- [ ] No adjustments made without explicit documentation

### Audit Trail Example

```python
def log_currency_conversion(df, source_file, conversion_date, rate_source):
    """
    Create audit log for currency conversions.
    """
    import json
    from datetime import datetime

    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'source_file': source_file,
        'conversion_date': conversion_date,
        'rate_source': rate_source,
        'rows_processed': len(df),
        'currencies_normalized': df['_original_currency'].nunique() if '_original_currency' in df.columns else 0,
        'total_aud_value': df['Amount_normalized_aud'].sum() if 'Amount_normalized_aud' in df.columns else 0,
    }

    # Append to audit log
    with open('currency_conversion_audit.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    return log_entry
```
