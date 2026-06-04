# Large Dataset Processing for Legal Analysis

> **Purpose**: Tools and patterns for processing CSV datasets from 100K to 10M+ rows efficiently within a sandboxed Linux VM environment.
> **Stack**: DuckDB, Polars, PyArrow, pandas (fallback), Python 3.10+

---

## Table of Contents

1. [Tool Selection Matrix](#1-tool-selection-matrix)
2. [DuckDB for Legal Analytics](#2-duckdb-for-legal-analytics)
3. [Polars for High-Performance Transforms](#3-polars-for-high-performance-transforms)
4. [Streaming & Chunked Processing](#4-streaming--chunked-processing)
5. [Full-Text Search at Scale](#5-full-text-search-at-scale)
6. [Parallel Batch Processing](#6-parallel-batch-processing)
7. [Vector Similarity for Near-Duplicate Detection](#7-vector-similarity-for-near-duplicate-detection)
8. [Data Validation Frameworks](#8-data-validation-frameworks)
9. [Efficient Regex at Scale](#9-efficient-regex-at-scale)
10. [Memory-Mapped File Processing](#10-memory-mapped-file-processing)
11. [Load File Generation](#11-load-file-generation)
12. [Performance Benchmarks](#12-performance-benchmarks)

---

## 1. Tool Selection Matrix

### Decision Logic

```python
def select_processing_tool(filepath):
    """Auto-select the optimal processing tool based on file characteristics."""
    import os
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

    if file_size_mb < 50:
        return 'pandas', 'Small dataset — pandas is sufficient'
    elif file_size_mb < 500:
        return 'duckdb', 'Medium dataset — DuckDB for SQL, streaming load'
    elif file_size_mb < 2000:
        return 'polars_lazy', 'Large dataset — Polars lazy evaluation recommended'
    else:
        return 'duckdb_streaming', 'Very large dataset — DuckDB streaming + chunked exports mandatory'
```

### Performance Comparison (1M rows × 50 columns)

| Operation | pandas | DuckDB | Polars | Winner |
|-----------|--------|--------|--------|--------|
| CSV load | 12.5s / 2.8GB | 3.2s / 150MB | 0.8s plan / 0.9GB | Polars |
| Filter 5% | 1.1s | 0.3s | 0.2s | Polars |
| GroupBy (100K groups) | 1.8s | 0.4s | 0.3s | Polars |
| JOIN (2×1M tables) | 3.5s | 0.8s | 1.2s | DuckDB |
| FTS keyword search | N/A | 1.2s | N/A | DuckDB |
| Regex over text cols | 3.4s | 1.1s | 0.7s | Polars |

### Installation

```bash
python -m venv .venv
source .venv/bin/activate

# Core (always install)
pip install duckdb>=0.10.0 polars>=0.20.0 pyarrow>=15.0.0

# Validation
pip install pandera>=0.18.0 pydantic>=2.0.0

# PDF reports
pip install reportlab>=4.0.0

# Vector similarity (optional — for near-duplicate detection)
pip install sentence-transformers faiss-cpu
```

---

## 2. DuckDB for Legal Analytics

### Why DuckDB for Legal Work

- **Streaming CSV load**: Process files larger than available RAM
- **SQL interface**: Familiar to legal tech professionals, defensible methodology
- **Full-text search**: Built-in FTS module for keyword searches
- **Zero-copy integration**: Direct interop with pandas/Polars DataFrames
- **In-process**: No server setup, works in sandboxed environments

### Core Patterns

```python
import duckdb
import os

def create_legal_db(csv_path, table_name='evidence'):
    """Create an in-memory DuckDB database from a CSV file with streaming load."""
    conn = duckdb.connect(':memory:')

    # Stream-load CSV (low memory — does NOT load entire file)
    conn.execute(f"""
        CREATE TABLE {table_name} AS
        SELECT *,
            ROW_NUMBER() OVER () as _row_id
        FROM read_csv_auto('{csv_path}',
            sample_size=-1,
            all_varchar=true,
            max_line_size=1048576)
    """)

    row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    col_info = conn.execute(f"DESCRIBE {table_name}").fetchall()

    print(f"Loaded: {row_count:,} rows × {len(col_info)} columns")
    return conn


def legal_keyword_search_sql(conn, table_name, text_columns, keywords, operator='OR'):
    """
    Perform keyword search using DuckDB SQL — deterministic, auditable, fast.

    Returns: DataFrame with matching rows and match metadata.
    """
    conditions = []
    for kw in keywords:
        col_conditions = [f"{col} ILIKE '%{kw}%'" for col in text_columns]
        conditions.append(f"({' OR '.join(col_conditions)})")

    joiner = ' OR ' if operator == 'OR' else ' AND '
    where_clause = joiner.join(conditions)

    query = f"""
        SELECT *,
            -- Tag which keywords matched
            {', '.join([
                f"CASE WHEN {' OR '.join([f'{col} ILIKE \'%{kw}%\'' for col in text_columns])} THEN 1 ELSE 0 END AS _hit_{kw.replace(' ', '_')}"
                for kw in keywords
            ])}
        FROM {table_name}
        WHERE {where_clause}
        ORDER BY _row_id
    """

    return conn.execute(query).fetchdf()


def custodian_analysis_sql(conn, table_name, custodian_col, date_col=None):
    """Custodian-level summary using DuckDB aggregation."""
    date_agg = f"""
        MIN(TRY_CAST({date_col} AS DATE)) as earliest_doc,
        MAX(TRY_CAST({date_col} AS DATE)) as latest_doc,
    """ if date_col else ""

    query = f"""
        SELECT
            {custodian_col} as custodian,
            COUNT(*) as doc_count,
            {date_agg}
            COUNT(DISTINCT _row_id) as unique_docs
        FROM {table_name}
        WHERE {custodian_col} IS NOT NULL
        GROUP BY {custodian_col}
        ORDER BY doc_count DESC
    """
    return conn.execute(query).fetchdf()
```

### DuckDB Full-Text Search

```python
def setup_fts(conn, table_name, text_column):
    """Set up DuckDB full-text search index."""
    conn.execute("INSTALL fts; LOAD fts;")
    conn.execute(f"""
        PRAGMA create_fts_index(
            '{table_name}',
            '_row_id',
            '{text_column}',
            stemmer='english',
            stopwords='english'
        )
    """)
    print(f"FTS index created on {table_name}.{text_column}")


def fts_search(conn, table_name, text_column, query_text, limit=1000):
    """Full-text search with relevance ranking."""
    result = conn.execute(f"""
        SELECT *, fts_main_{table_name}.match_bm25(
            _row_id, '{query_text}'
        ) AS relevance_score
        FROM {table_name}
        WHERE relevance_score IS NOT NULL
        ORDER BY relevance_score DESC
        LIMIT {limit}
    """).fetchdf()
    return result
```

### Timeline Analysis with Window Functions

```python
def timeline_analysis_sql(conn, table_name, date_col, entity_col=None):
    """Generate timeline analysis using DuckDB window functions."""
    entity_partition = f"PARTITION BY {entity_col}" if entity_col else ""

    query = f"""
        SELECT *,
            -- Gap from previous record
            TRY_CAST({date_col} AS TIMESTAMP) -
            LAG(TRY_CAST({date_col} AS TIMESTAMP))
                OVER ({entity_partition} ORDER BY TRY_CAST({date_col} AS TIMESTAMP))
                AS gap_from_previous,

            -- Running count
            ROW_NUMBER() OVER ({entity_partition}
                ORDER BY TRY_CAST({date_col} AS TIMESTAMP)) AS sequence_number,

            -- Daily volume
            COUNT(*) OVER (
                PARTITION BY DATE_TRUNC('day', TRY_CAST({date_col} AS TIMESTAMP))
            ) AS daily_volume

        FROM {table_name}
        WHERE TRY_CAST({date_col} AS TIMESTAMP) IS NOT NULL
        ORDER BY TRY_CAST({date_col} AS TIMESTAMP)
    """
    return conn.execute(query).fetchdf()
```

---

## 3. Polars for High-Performance Transforms

### When to Use Polars

- String/regex operations on large text columns (4.9× faster than pandas)
- Memory-constrained environments (uses 2–3× less RAM)
- Complex transformation pipelines (lazy evaluation optimises automatically)
- Columnar operations (aggregations, filters, joins)

### Core Patterns

```python
import polars as pl

def load_legal_csv_polars(filepath, lazy=True):
    """Load CSV with Polars — lazy by default for large files."""
    if lazy:
        return pl.scan_csv(filepath, ignore_errors=True, try_parse_dates=True)
    else:
        return pl.read_csv(filepath, ignore_errors=True, try_parse_dates=True)


def classify_documents_polars(df_lazy, classification_rules):
    """
    Apply rule-based classification using Polars expressions.

    classification_rules: dict of {label: regex_pattern}
    e.g. {'privilege': r'\b(attorney|privilege|confidential)\b',
           'financial': r'\b(payment|invoice|transaction)\b'}
    """
    expressions = []
    for label, pattern in classification_rules.items():
        expressions.append(
            pl.col('body')
            .str.contains(pattern)
            .alias(f'_flag_{label}')
        )

    return df_lazy.with_columns(expressions)


def temporal_clustering_polars(df_lazy, timestamp_col, entity_col, gap_hours=2):
    """Detect temporal clusters (bursts of activity) using Polars."""
    return (
        df_lazy
        .sort(timestamp_col)
        .with_columns([
            # Gap from previous message
            (pl.col(timestamp_col) - pl.col(timestamp_col).shift(1))
            .over(entity_col)
            .alias('_gap_duration'),
        ])
        .with_columns([
            # New cluster when gap exceeds threshold
            (pl.col('_gap_duration') > pl.duration(hours=gap_hours))
            .fill_null(True)
            .cum_sum()
            .over(entity_col)
            .alias('_cluster_id')
        ])
    )
```

### Polars → pandas Interop

```python
def polars_to_pandas_safe(df_polars):
    """Convert Polars DataFrame to pandas, handling large datasets."""
    if isinstance(df_polars, pl.LazyFrame):
        # Collect first — triggers computation
        df_polars = df_polars.collect()
    return df_polars.to_pandas()


def pandas_to_polars(df_pandas):
    """Convert pandas DataFrame to Polars for faster processing."""
    return pl.from_pandas(df_pandas)
```

---

## 4. Streaming & Chunked Processing

### For Datasets Exceeding Available Memory

```python
import duckdb
import pandas as pd

def stream_process_csv(filepath, process_fn, chunk_size=100_000):
    """
    Process a CSV file in chunks without loading the full file.

    process_fn: callable that takes a DataFrame chunk and returns processed DataFrame
    """
    results = []
    for i, chunk in enumerate(pd.read_csv(filepath, chunksize=chunk_size,
                                           encoding='utf-8-sig', dtype=str)):
        processed = process_fn(chunk)
        results.append(processed)
        if (i + 1) % 10 == 0:
            print(f"  Processed {(i + 1) * chunk_size:,} rows...")

    combined = pd.concat(results, ignore_index=True)
    print(f"Total processed: {len(combined):,} rows")
    return combined


def duckdb_chunked_export(conn, query, output_dir, chunk_size=500_000):
    """Export large DuckDB query results in chunks to avoid memory issues."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    total = conn.execute(f"SELECT COUNT(*) FROM ({query}) q").fetchone()[0]
    chunks = (total // chunk_size) + 1

    for i in range(chunks):
        offset = i * chunk_size
        chunk_query = f"{query} LIMIT {chunk_size} OFFSET {offset}"
        chunk_path = os.path.join(output_dir, f"chunk_{i:04d}.csv")
        conn.execute(f"COPY ({chunk_query}) TO '{chunk_path}' (HEADER, DELIMITER ',')")
        print(f"  Chunk {i+1}/{chunks}: {chunk_path}")

    return total
```

### Streaming Hash Computation

```python
import hashlib

def stream_hash_large_file(filepath, algorithm='sha256'):
    """Compute hash of very large files using streaming (constant memory)."""
    h = hashlib.new(algorithm)
    bytes_read = 0

    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            h.update(chunk)
            bytes_read += len(chunk)

    return {
        'algorithm': algorithm,
        'hash_value': h.hexdigest(),
        'bytes_processed': bytes_read,
    }
```

---

## 5. Full-Text Search at Scale

### Option A: DuckDB FTS (Recommended — No External Dependencies)

See §2 above for DuckDB FTS setup and search.

### Option B: Whoosh (Pure Python, Portable)

```python
def build_whoosh_index(df, text_column, id_column, index_dir='whoosh_index'):
    """Build a Whoosh full-text search index from a DataFrame."""
    # pip install whoosh
    from whoosh.index import create_in
    from whoosh.fields import Schema, TEXT, ID
    import os

    os.makedirs(index_dir, exist_ok=True)
    schema = Schema(
        doc_id=ID(stored=True, unique=True),
        content=TEXT(stored=False)
    )
    ix = create_in(index_dir, schema)

    writer = ix.writer()
    for idx, row in df.iterrows():
        writer.add_document(
            doc_id=str(row[id_column]),
            content=str(row[text_column])
        )
    writer.commit()

    return ix


def search_whoosh(ix, query_string, limit=1000):
    """Search Whoosh index with Boolean query support."""
    from whoosh.qparser import MultifieldParser
    searcher = ix.searcher()
    parser = MultifieldParser(['content'], schema=ix.schema)
    query = parser.parse(query_string)
    results = searcher.search(query, limit=limit)
    return [{'doc_id': r['doc_id'], 'score': r.score} for r in results]
```

---

## 6. Parallel Batch Processing

### For LLM Classification of Large Datasets

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd

def parallel_classify(df, classify_fn, text_column, batch_size=500, max_workers=4):
    """
    Parallel batch classification using ProcessPoolExecutor.

    classify_fn: callable that takes a list of texts and returns classifications
    """
    batches = [
        df.iloc[i:i+batch_size]
        for i in range(0, len(df), batch_size)
    ]

    all_results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(classify_fn, batch[text_column].tolist()): i
            for i, batch in enumerate(batches)
        }

        for future in as_completed(futures):
            batch_idx = futures[future]
            try:
                results = future.result()
                all_results.append((batch_idx, results))
                print(f"  Batch {batch_idx + 1}/{len(batches)} complete")
            except Exception as e:
                print(f"  Batch {batch_idx + 1} FAILED: {e}")

    # Reassemble in order
    all_results.sort(key=lambda x: x[0])
    return [r for _, batch_results in all_results for r in batch_results]
```

---

## 7. Vector Similarity for Near-Duplicate Detection

### Modern Approach (Replaces fuzzywuzzy for >10K Documents)

```python
def find_near_duplicates_vector(df, text_column, id_column,
                                 similarity_threshold=0.92, batch_size=256):
    """
    Find near-duplicate documents using sentence embeddings + FAISS.

    Much faster than fuzzywuzzy for large datasets:
    - fuzzywuzzy: O(n²) pairwise comparison — 10K docs = hours
    - This approach: O(n log n) with FAISS — 100K docs = minutes

    Requires: pip install sentence-transformers faiss-cpu
    """
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np

    model = SentenceTransformer('all-MiniLM-L6-v2')

    texts = df[text_column].fillna('').tolist()
    doc_ids = df[id_column].tolist()

    # Encode in batches
    embeddings = model.encode(texts, batch_size=batch_size,
                               show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype('float32')

    # Normalise for cosine similarity
    faiss.normalize_L2(embeddings)

    # Build FAISS index
    index = faiss.IndexFlatIP(embeddings.shape[1])  # Inner product = cosine after normalisation
    index.add(embeddings)

    # Search for near-duplicates
    k = min(10, len(embeddings))
    distances, indices = index.search(embeddings, k)

    duplicates = []
    seen_pairs = set()

    for i in range(len(embeddings)):
        for j_pos in range(1, k):
            j = indices[i][j_pos]
            sim = distances[i][j_pos]

            if sim >= similarity_threshold and i < j:
                pair = (min(i, j), max(i, j))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    duplicates.append({
                        'doc_id_1': doc_ids[i],
                        'doc_id_2': doc_ids[j],
                        'similarity': float(sim),
                        'text_1_preview': texts[i][:200],
                        'text_2_preview': texts[j][:200],
                    })

    print(f"Found {len(duplicates)} near-duplicate pairs (>{similarity_threshold*100:.0f}% similar)")
    return pd.DataFrame(duplicates)
```

---

## 8. Data Validation Frameworks

### Pandera: Schema Validation for Legal Datasets

```python
def validate_legal_csv(df, schema_type='communications'):
    """
    Validate a legal CSV dataset against expected schema.

    Requires: pip install pandera
    """
    import pandera as pa
    from pandera import Column, Check

    schemas = {
        'communications': pa.DataFrameSchema({
            'date': Column(pa.String, nullable=False,
                          checks=Check.str_matches(r'\d{4}-\d{2}-\d{2}|^\d{1,2}/\d{1,2}/\d{2,4}$')),
            'sender': Column(pa.String, nullable=False, checks=Check.str_length(min_value=1)),
            'recipient': Column(pa.String, nullable=True),
            'subject': Column(pa.String, nullable=True),
            'body': Column(pa.String, nullable=True),
        }),
        'financial': pa.DataFrameSchema({
            'date': Column(pa.String, nullable=False),
            'amount': Column(pa.String, nullable=False),
            'description': Column(pa.String, nullable=True),
        }),
        'sms': pa.DataFrameSchema({
            'timestamp': Column(pa.String, nullable=False),
            'body': Column(pa.String, nullable=True),
        }),
    }

    schema = schemas.get(schema_type)
    if not schema:
        print(f"No schema defined for type: {schema_type}")
        return df, []

    try:
        validated = schema.validate(df, lazy=True)
        print(f"Validation PASSED: {len(validated):,} rows valid")
        return validated, []
    except pa.errors.SchemaErrors as e:
        failures = e.failure_cases
        print(f"Validation FAILED: {len(failures)} issues found")
        print(failures.groupby('column').size())
        return df, failures
```

---

## 9. Efficient Regex at Scale

### Polars Regex (Recommended for >100K Rows)

```python
import polars as pl

def batch_regex_classification(filepath, patterns_dict, text_column='body'):
    """
    Apply multiple regex patterns efficiently using Polars.

    patterns_dict: {'label': 'regex_pattern', ...}
    """
    df = pl.scan_csv(filepath, ignore_errors=True)

    expressions = [
        pl.col(text_column)
        .str.contains(pattern)
        .alias(f'_flag_{label}')
        for label, pattern in patterns_dict.items()
    ]

    result = df.with_columns(expressions).collect()

    # Summary
    for label in patterns_dict:
        flag_col = f'_flag_{label}'
        hit_count = result[flag_col].sum()
        print(f"  {label}: {hit_count:,} hits ({hit_count/len(result)*100:.1f}%)")

    return result
```

### DuckDB Regex (For SQL-Based Workflows)

```python
def duckdb_regex_search(conn, table_name, text_column, patterns_dict):
    """Apply regex patterns using DuckDB — fast, SQL-auditable."""
    select_parts = [f"*"]
    for label, pattern in patterns_dict.items():
        select_parts.append(
            f"CASE WHEN regexp_matches({text_column}, '{pattern}') THEN TRUE ELSE FALSE END AS _flag_{label}"
        )

    query = f"SELECT {', '.join(select_parts)} FROM {table_name}"
    return conn.execute(query).fetchdf()
```

---

## 10. Memory-Mapped File Processing

### For Very Large Files (>2GB)

```python
import mmap
import re

def mmap_keyword_count(filepath, keyword, encoding='utf-8'):
    """Count keyword occurrences in a very large file using memory-mapped I/O."""
    keyword_bytes = keyword.encode(encoding)

    with open(filepath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            count = 0
            pos = 0
            while True:
                pos = mm.find(keyword_bytes, pos)
                if pos == -1:
                    break
                count += 1
                pos += 1

    return count
```

---

## 11. Load File Generation

### Concordance DAT Format

```python
def generate_concordance_dat(df, output_path, bates_prefix='PROD',
                              field_map=None):
    """
    Generate Concordance-compatible DAT load file.

    Standard: Pipe-delimited (þ field delimiter, ¶ newline within fields)
    """
    DELIM = '\x14'   # þ — Concordance field separator
    QUOTE = '\xfe'    # ¶ — Concordance text qualifier

    default_fields = [
        'BATES_BEG', 'BATES_END', 'CUSTODIAN', 'DATE_SENT', 'DATE_RECEIVED',
        'FROM', 'TO', 'CC', 'BCC', 'SUBJECT', 'FILE_TYPE', 'FILE_SIZE',
        'MD5_HASH', 'SHA256_HASH', 'NATIVE_FILE', 'TEXT_FILE'
    ]

    fields = field_map or {f: f.lower() for f in default_fields}

    with open(output_path, 'w', encoding='utf-8') as f:
        # Header
        f.write(DELIM.join(f'{QUOTE}{field}{QUOTE}' for field in fields.keys()) + '\n')

        for i, (_, row) in enumerate(df.iterrows(), 1):
            bates = f"{bates_prefix}{str(i).zfill(7)}"
            values = []
            for field_name, col_name in fields.items():
                if field_name == 'BATES_BEG':
                    values.append(bates)
                elif field_name == 'BATES_END':
                    values.append(bates)
                else:
                    val = str(row.get(col_name, '')).replace('\n', ' ').replace('\r', '')
                    values.append(val)

            f.write(DELIM.join(f'{QUOTE}{v}{QUOTE}' for v in values) + '\n')

    print(f"Concordance DAT: {output_path} ({i:,} records)")
    return output_path


def generate_relativity_load_file(df, output_path, bates_prefix='REL'):
    """
    Generate Relativity-compatible load file (pipe-delimited CSV).
    """
    import csv

    relativity_fields = [
        'Control Number', 'Group Identifier', 'Custodian',
        'Date Sent', 'Date Received', 'From', 'To', 'CC', 'BCC',
        'Subject', 'File Type', 'File Size', 'MD5 Hash',
        'Extracted Text', 'Native File Path'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(relativity_fields)

        for i, (_, row) in enumerate(df.iterrows(), 1):
            bates = f"{bates_prefix}{str(i).zfill(7)}"
            writer.writerow([
                bates,
                str(row.get('group_id', bates)),
                str(row.get('custodian', '')),
                str(row.get('date_sent', '')),
                str(row.get('date_received', '')),
                str(row.get('from', '')),
                str(row.get('to', '')),
                str(row.get('cc', '')),
                str(row.get('bcc', '')),
                str(row.get('subject', '')),
                str(row.get('file_type', 'CSV')),
                str(row.get('file_size', '')),
                str(row.get('md5_hash', '')),
                str(row.get('text', ''))[:50000],
                str(row.get('native_path', '')),
            ])

    print(f"Relativity load file: {output_path} ({i:,} records)")
    return output_path
```

---

## 12. Performance Benchmarks

### Quick Reference

```
DuckDB CSV load (1M rows):     3.2s, 150MB RAM
Polars lazy plan (1M rows):    0.8s, 0.9GB RAM
pandas full load (1M rows):    12.5s, 2.8GB RAM

DuckDB FTS search (1M docs):   1.2s
Whoosh search (1M docs):       2.3s

Polars regex (1M rows):        0.7s
pandas regex (1M rows):        3.4s

FAISS near-dup (100K docs):    ~2 min (including embedding)
fuzzywuzzy near-dup (10K):     ~30 min (O(n²))
```

### When NOT to Use These Tools

- **Don't use DuckDB** for: simple row-by-row iteration, scikit-learn integration
- **Don't use Polars** for: existing pandas-dependent codebases with <100K rows
- **Don't use FAISS** for: exact duplicate detection (use SHA-256 hashing instead)
- **Don't use streaming** for: datasets that fit comfortably in memory (<500MB)
