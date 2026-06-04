# SMS/iMessage Forensic Analysis Pipeline

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [CSV Ingestion & Source Detection](#2-csv-ingestion--source-detection)
3. [Participant Mapping & Normalisation](#3-participant-mapping--normalisation)
4. [Data Model / Schema Design](#4-data-model--schema-design)
5. [JSON Schemas for LLM Structured Outputs](#5-json-schemas-for-llm-structured-outputs)
6. [Classification Pipeline](#6-classification-pipeline)
7. [Thread Summarisation](#7-thread-summarisation)
8. [Chronology Builder](#8-chronology-builder)
9. [Agent Design & Tool Interfaces](#9-agent-design--tool-interfaces)
10. [Quality, Robustness & Process Control](#10-quality-robustness--process-control)
11. [iMessage-Specific Forensic Guidance](#11-imessage-specific-forensic-guidance)
12. [Android SMS-Specific Guidance](#12-android-sms-specific-guidance)
13. [Family Law SMS Playbook](#13-family-law-sms-playbook)

---

## 1. Architecture Overview

The SMS analysis pipeline is structured as five layers, each with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│  Evidence Store (read-only)                              │
│  Raw CSV exports, hashes, acquisition metadata           │
├─────────────────────────────────────────────────────────┤
│  Analysis DB (read/write)                                │
│  Normalised SMS tables, AI-derived labels, run logs      │
├─────────────────────────────────────────────────────────┤
│  Indexing Layer                                          │
│  Full-text search (pandas str / DuckDB FTS)              │
│  Relational filters (party, date, direction, tags)       │
├─────────────────────────────────────────────────────────┤
│  AI Orchestration Layer                                  │
│  Tools: search_messages, classify_messages,              │
│         summarise_segment, build_chronology              │
│  LLM calls with strict JSON Schema validation            │
├─────────────────────────────────────────────────────────┤
│  Review / Report Layer                                   │
│  CSV exports, PDF/DOCX reports, affidavit annexures      │
│  Everything grounded by message_id                       │
└─────────────────────────────────────────────────────────┘
```

### Core Principles

- **Evidence integrity**: Raw CSV is never modified. All transformations produce new files.
- **Deterministic search**: All search/filter operations use pure SQL or pandas — no LLM in the search path.
- **AI lineage**: Every LLM call is logged with model, parameters, prompt hash, and linked message_ids.
- **Human-in-the-loop**: AI outputs are candidates flagged for human verification, not conclusions.
- **Reproducibility**: Any analysis can be re-run from the same inputs with the same configuration.

---

## 2. CSV Ingestion & Source Detection

### 2.1 Source Tool Detection

Different forensic tools produce different CSV column layouts. Auto-detect the source by matching column header patterns:

```python
# Column signature patterns for source detection
SOURCE_SIGNATURES = {
    'ios_chat_db': {
        'required': ['ROWID', 'text', 'handle_id', 'is_from_me', 'date'],
        'optional': ['cache_roomname', 'service', 'is_read', 'is_delivered',
                     'attributedBody', 'message_summary_info', 'expire_state'],
        'platform': 'ios',
        'timestamp_format': 'apple_epoch_seconds',
    },
    'ios_chat_db_variant': {
        'required': ['rowid', 'message_text', 'handle', 'from_me', 'timestamp'],
        'platform': 'ios',
        'timestamp_format': 'apple_epoch_seconds',
    },
    'cellebrite_sms': {
        'required': ['Time Stamp', 'Parties', 'Body', 'Direction'],
        'optional': ['Status', 'Source', 'Deleted', 'Service'],
        'platform': 'mixed',
        'timestamp_format': 'iso8601',
    },
    'cellebrite_imessage': {
        'required': ['Timestamp', 'From', 'To', 'Body'],
        'optional': ['Direction', 'Status', 'Service', 'Attachment'],
        'platform': 'ios',
        'timestamp_format': 'iso8601',
    },
    'axiom_messages': {
        'required': ['Date/Time - UTC', 'From', 'To', 'Message'],
        'optional': ['Source File', 'Evidence Number', 'Artifact'],
        'platform': 'mixed',
        'timestamp_format': 'iso8601_utc',
    },
    'oxygen_sms': {
        'required': ['Timestamp', 'Date', 'From', 'To', 'Message'],
        'optional': ['From Name', 'To Name', 'Emoji', 'Attachments'],
        'platform': 'mixed',
        'timestamp_format': 'iso8601',
    },
    'imazing_export': {
        'required': ['Date', 'Type', 'Text'],
        'optional': ['Sender', 'Attachments', 'Service'],
        'platform': 'ios',
        'timestamp_format': 'iso8601',
    },
    'android_mmssms': {
        'required': ['address', 'body', 'date', 'type'],
        'optional': ['read', 'status', 'thread_id', '_id'],
        'platform': 'android',
        'timestamp_format': 'unix_milliseconds',
    },
    'android_mmssms_variant': {
        'required': ['Address', 'Body', 'Date', 'Type'],
        'optional': ['Read', 'Status', 'Thread ID'],
        'platform': 'android',
        'timestamp_format': 'unix_milliseconds',
    },
    'carrier_records': {
        'required': ['Date', 'Time', 'From Number', 'To Number'],
        'optional': ['Duration', 'Type', 'Message Content'],
        'platform': 'carrier',
        'timestamp_format': 'iso8601',
    },
}

def detect_source(df):
    """Detect CSV source tool from column headers."""
    columns_lower = {c.lower().strip() for c in df.columns}
    columns_exact = set(df.columns)

    best_match = None
    best_score = 0

    for source_id, sig in SOURCE_SIGNATURES.items():
        required = sig['required']
        # Try exact match first
        exact_matches = sum(1 for c in required if c in columns_exact)
        # Then case-insensitive
        lower_matches = sum(1 for c in required if c.lower() in columns_lower)

        score = max(exact_matches, lower_matches)
        if score == len(required) and score > best_score:
            best_match = source_id
            best_score = score

    if best_match:
        return best_match, SOURCE_SIGNATURES[best_match]

    # Heuristic fallback: check for Apple epoch timestamps
    for col in df.columns:
        sample = df[col].dropna().head(20)
        try:
            vals = sample.astype(float)
            # Apple epoch range: ~600M to ~900M (2020–2029)
            if (vals > 6e8).all() and (vals < 9e8).all():
                return 'ios_unknown', {
                    'platform': 'ios',
                    'timestamp_format': 'apple_epoch_seconds',
                    'detected_ts_column': col
                }
            # Unix milliseconds range (Android): ~1.5e12 to ~1.8e12
            if (vals > 1.4e12).all() and (vals < 1.9e12).all():
                return 'android_unknown', {
                    'platform': 'android',
                    'timestamp_format': 'unix_milliseconds',
                    'detected_ts_column': col
                }
        except (ValueError, TypeError):
            continue

    return 'unknown', {'platform': 'unknown', 'timestamp_format': 'unknown'}
```

### 2.2 Column Mapping to Canonical Schema

After detecting the source, map tool-specific columns to the canonical schema:

```python
# Canonical column names (target schema)
CANONICAL_COLUMNS = [
    'message_id',       # unique ID within dataset
    'device_id',        # source device identifier
    'conversation_id',  # thread/chat identifier
    'direction',        # 'inbound' | 'outbound' | 'unknown'
    'sender_address',   # raw phone number or handle
    'recipient_address', # raw phone number or handle
    'sent_at_local',    # original timestamp as-is
    'sent_at_utc',      # normalised to UTC
    'body_raw',         # original message text
    'body_normalized',  # lowercased, whitespace-normalised
    'service_type',     # 'iMessage' | 'SMS' | 'MMS' | 'unknown'
    'is_mms',           # boolean
    'has_attachments',   # boolean
    'is_deleted',        # boolean (if export indicates deletion)
    'is_recovered',      # boolean (recovered from artefacts)
    'is_read',           # boolean
    'is_delivered',      # boolean
    'platform',          # 'ios' | 'android' | 'carrier' | 'unknown'
    'source_tool',       # detected forensic tool
    '_source_file',      # original CSV filename
    '_source_row',       # row number in original CSV
]

COLUMN_MAPS = {
    'ios_chat_db': {
        'message_id': 'ROWID',
        'conversation_id': 'cache_roomname',
        'sender_address': lambda row: '' if str(row.get('is_from_me', '0')) == '1' else row.get('handle_id', ''),
        'recipient_address': lambda row: row.get('handle_id', '') if str(row.get('is_from_me', '0')) == '1' else '',
        'sent_at_local': 'date',
        'body_raw': 'text',
        'service_type': 'service',
        'is_read': 'is_read',
        'is_delivered': 'is_delivered',
    },
    'android_mmssms': {
        'message_id': '_id',
        'conversation_id': 'thread_id',
        'sender_address': lambda row: '' if str(row.get('type', '1')) == '2' else row.get('address', ''),
        'recipient_address': lambda row: row.get('address', '') if str(row.get('type', '1')) == '2' else '',
        'sent_at_local': 'date',
        'body_raw': 'body',
        'is_read': 'read',
    },
    'cellebrite_sms': {
        'message_id': None,  # auto-generate
        'sent_at_local': 'Time Stamp',
        'body_raw': 'Body',
        'direction': 'Direction',
    },
    'axiom_messages': {
        'message_id': None,
        'sent_at_local': 'Date/Time - UTC',
        'sender_address': 'From',
        'recipient_address': 'To',
        'body_raw': 'Message',
    },
    'oxygen_sms': {
        'message_id': None,
        'sent_at_local': 'Timestamp',
        'sender_address': 'From',
        'recipient_address': 'To',
        'body_raw': 'Message',
    },
    'imazing_export': {
        'message_id': None,
        'sent_at_local': 'Date',
        'body_raw': 'Text',
        'service_type': 'Service',
    },
}

def map_to_canonical(df, source_id, source_info):
    """Map source-specific columns to canonical schema."""
    col_map = COLUMN_MAPS.get(source_id, {})
    result = pd.DataFrame(index=df.index)

    for canonical_col in CANONICAL_COLUMNS:
        mapping = col_map.get(canonical_col)

        if mapping is None:
            # Auto-generate or leave empty
            if canonical_col == 'message_id':
                result[canonical_col] = range(1, len(df) + 1)
            else:
                result[canonical_col] = ''
        elif callable(mapping):
            result[canonical_col] = df.apply(mapping, axis=1)
        elif mapping in df.columns:
            result[canonical_col] = df[mapping]
        else:
            result[canonical_col] = ''

    # Set metadata columns
    result['platform'] = source_info.get('platform', 'unknown')
    result['source_tool'] = source_id

    # Normalise body text
    result['body_normalized'] = (
        result['body_raw']
        .fillna('')
        .str.lower()
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )

    return result
```

### 2.3 Timestamp Conversion

```python
import pandas as pd

APPLE_EPOCH_OFFSET = 978307200  # seconds between 1970-01-01 and 2001-01-01

def convert_timestamps(df, timestamp_format, ts_column='sent_at_local'):
    """Convert timestamps to UTC based on detected format."""

    df['_original_timestamp'] = df[ts_column].copy()

    if timestamp_format == 'apple_epoch_seconds':
        def convert(val):
            if pd.isna(val) or val == '':
                return pd.NaT
            ts = float(val)
            # Auto-detect nanoseconds (>1e15) or microseconds (>1e12)
            if ts > 1e15:
                ts = ts / 1e9
            elif ts > 1e12:
                ts = ts / 1e6
            return pd.Timestamp(ts + APPLE_EPOCH_OFFSET, unit='s', tz='UTC')
        df['sent_at_utc'] = df[ts_column].apply(convert)

    elif timestamp_format == 'unix_milliseconds':
        def convert(val):
            if pd.isna(val) or val == '':
                return pd.NaT
            return pd.Timestamp(float(val) / 1000, unit='s', tz='UTC')
        df['sent_at_utc'] = df[ts_column].apply(convert)

    elif timestamp_format in ('iso8601', 'iso8601_utc'):
        df['sent_at_utc'] = pd.to_datetime(df[ts_column], errors='coerce', utc=True)

    else:
        # Attempt auto-parse
        df['sent_at_utc'] = pd.to_datetime(df[ts_column], errors='coerce', utc=True)

    return df
```

### 2.4 Complete Ingestion Pipeline

```python
def ingest_sms_csv(filepath, coc, device_id='device_01'):
    """Full ingestion pipeline: detect source, map columns, convert timestamps."""

    # 1. Hash
    baseline = hash_file(filepath)
    coc.log("sms_ingest_start", f"File: {baseline['filename']}, SHA-256: {baseline['hash_value']}")

    # 2. Load
    df = pd.read_csv(filepath, encoding='utf-8-sig', low_memory=False, dtype=str)
    coc.log("sms_loaded", f"{len(df):,} rows × {len(df.columns)} cols")

    # 3. Detect source
    source_id, source_info = detect_source(df)
    coc.log("sms_source_detected", f"Source: {source_id}, Platform: {source_info.get('platform')}")

    if source_id == 'unknown':
        coc.log("sms_source_unknown", "Could not auto-detect source. Manual column mapping required.")
        return df, source_id, source_info

    # 4. Map to canonical schema
    canonical = map_to_canonical(df, source_id, source_info)
    canonical['device_id'] = device_id
    canonical['_source_file'] = os.path.basename(filepath)
    canonical['_source_row'] = range(1, len(df) + 1)
    coc.log("sms_mapped", f"Mapped to canonical schema ({len(canonical):,} messages)")

    # 5. Convert timestamps
    ts_format = source_info.get('timestamp_format', 'unknown')
    canonical = convert_timestamps(canonical, ts_format)
    coc.log("sms_timestamps", f"Converted timestamps ({ts_format})")

    # 6. Normalise direction
    if 'direction' not in canonical.columns or canonical['direction'].eq('').all():
        canonical['direction'] = canonical.apply(
            lambda row: normalise_direction(row, source_info.get('platform')),
            axis=1
        )

    # 7. Sort chronologically
    canonical = canonical.sort_values('sent_at_utc').reset_index(drop=True)

    return canonical, source_id, source_info
```

---

## 3. Participant Mapping & Normalisation

### 3.1 Phone Number Normalisation

```python
import re

def normalise_phone(raw_address, default_country_code='+61'):
    """Normalise phone number to E.164 format."""
    if not raw_address or pd.isna(raw_address):
        return ''

    # Strip whitespace and common formatting
    cleaned = re.sub(r'[\s\-\(\)\.]', '', str(raw_address).strip())

    # Already E.164
    if re.match(r'^\+\d{10,15}$', cleaned):
        return cleaned

    # Has country code without +
    if re.match(r'^0{0,2}\d{10,15}$', cleaned) and len(cleaned) > 10:
        return '+' + cleaned.lstrip('0')

    # Australian local number (starts with 0)
    if re.match(r'^0[2-9]\d{8}$', cleaned):
        return default_country_code + cleaned[1:]

    # Short number or handle (email, Apple ID)
    if '@' in cleaned:
        return cleaned  # Return as-is for email handles

    return cleaned  # Return cleaned but unnormalised
```

### 3.2 Logical Party Assignment

The logical party mapping connects raw phone numbers to meaningful role labels. This step requires user input and cannot be automated.

```python
def build_participant_map(df, known_mappings=None):
    """
    Build participant map from unique addresses in the dataset.

    known_mappings: dict of {normalised_address: logical_party}
    e.g. {'+61412345678': 'Client', '+61498765432': 'OpposingParty'}
    """
    known_mappings = known_mappings or {}

    # Collect all unique addresses
    all_addresses = set()
    for col in ['sender_address', 'recipient_address']:
        if col in df.columns:
            all_addresses.update(df[col].dropna().unique())

    all_addresses.discard('')

    # Build participant records
    participants = []
    for addr in sorted(all_addresses):
        normalised = normalise_phone(addr)
        participants.append({
            'raw_address': addr,
            'normalized_e164': normalised,
            'logical_party': known_mappings.get(normalised, 'UNMAPPED'),
            'message_count': len(df[
                (df['sender_address'] == addr) | (df['recipient_address'] == addr)
            ]),
        })

    return pd.DataFrame(participants)
```

**User interaction required**: Present the participant map and ask the user to assign logical parties. Common roles:

| Role | Description |
|------|-------------|
| `Client` | The party instructing the solicitor / the person whose device was examined |
| `OpposingParty` | The other party in the dispute |
| `Child` | Minor child (messages about or from) |
| `Solicitor` | Legal representative |
| `ThirdParty` | Other identified person |
| `Unknown` | Unidentified number |

### 3.3 Conversation Reconstruction

```python
def reconstruct_conversations(df):
    """
    Rebuild conversation threads from the normalised dataset.

    For iOS: use conversation_id (cache_roomname) if present.
    For Android: use thread_id if present.
    Fallback: group by unique sender-recipient pair.
    """
    if df['conversation_id'].notna().any() and not df['conversation_id'].eq('').all():
        # Use existing conversation IDs
        conversations = df.groupby('conversation_id').agg(
            message_count=('message_id', 'count'),
            first_message=('sent_at_utc', 'min'),
            last_message=('sent_at_utc', 'max'),
            participants=('sender_address', lambda x: list(x.unique())),
        ).reset_index()
    else:
        # Derive conversations from sender-recipient pairs
        def conversation_key(row):
            pair = sorted([
                str(row.get('sender_address', '')),
                str(row.get('recipient_address', ''))
            ])
            return '|'.join(pair)

        df['_derived_conversation'] = df.apply(conversation_key, axis=1)
        conversations = df.groupby('_derived_conversation').agg(
            message_count=('message_id', 'count'),
            first_message=('sent_at_utc', 'min'),
            last_message=('sent_at_utc', 'max'),
        ).reset_index()
        conversations.rename(columns={'_derived_conversation': 'conversation_id'}, inplace=True)

    return conversations
```

---

## 4. Data Model / Schema Design

This section defines the canonical database schema. When working in-memory with pandas DataFrames, the column names and types correspond to this schema. When using DuckDB or PostgreSQL for larger datasets, create these tables directly.

### 4.1 Core SMS Schema (PostgreSQL)

```sql
CREATE TABLE device (
  id              BIGSERIAL PRIMARY KEY,
  evidence_id     TEXT NOT NULL,
  platform        TEXT CHECK (platform IN ('ios', 'android', 'other')),
  description     TEXT,
  acquired_at     TIMESTAMPTZ,
  acquisition_tool TEXT,
  hash_sha256     TEXT,
  UNIQUE (evidence_id)
);

CREATE TABLE participant (
  id              BIGSERIAL PRIMARY KEY,
  device_id       BIGINT REFERENCES device(id),
  raw_address     TEXT NOT NULL,
  normalized_e164 TEXT,
  logical_party   TEXT,
  display_name    TEXT,
  UNIQUE (device_id, raw_address)
);

CREATE TABLE conversation (
  id              BIGSERIAL PRIMARY KEY,
  device_id       BIGINT REFERENCES device(id) NOT NULL,
  source_thread_id TEXT,
  title           TEXT,
  is_group_chat   BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ,
  metadata        JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE conversation_participant (
  conversation_id BIGINT REFERENCES conversation(id) ON DELETE CASCADE,
  participant_id  BIGINT REFERENCES participant(id) ON DELETE CASCADE,
  role            TEXT,
  PRIMARY KEY (conversation_id, participant_id)
);

CREATE TYPE message_direction AS ENUM('inbound', 'outbound', 'unknown');

CREATE TABLE message (
  id              BIGSERIAL PRIMARY KEY,
  device_id       BIGINT REFERENCES device(id) NOT NULL,
  conversation_id BIGINT REFERENCES conversation(id),
  source_message_id TEXT,
  direction       message_direction NOT NULL,
  sender_id       BIGINT REFERENCES participant(id),
  main_recipient_id BIGINT REFERENCES participant(id),
  sent_at_local   TIMESTAMPTZ,
  sent_tz_offset  INTERVAL,
  sent_at_utc     TIMESTAMPTZ,
  body_raw        TEXT,
  body_normalized TEXT,
  service_type    TEXT,
  is_mms          BOOLEAN DEFAULT FALSE,
  has_attachments BOOLEAN DEFAULT FALSE,
  is_deleted      BOOLEAN,
  is_recovered    BOOLEAN,
  is_read         BOOLEAN,
  is_delivered    BOOLEAN,
  status          TEXT,
  metadata        JSONB DEFAULT '{}'::jsonb,
  -- Multipart SMS stitching
  logical_group_id BIGINT,
  logical_part_index INT
);

CREATE TABLE attachment (
  id              BIGSERIAL PRIMARY KEY,
  message_id      BIGINT REFERENCES message(id) ON DELETE CASCADE,
  content_type    TEXT,
  file_name       TEXT,
  size_bytes      BIGINT,
  hash_sha256     TEXT,
  storage_uri     TEXT
);
```

### 4.2 AI-Derived Labels

Separate from core data to keep lineage clear:

```sql
CREATE TYPE legal_issue_tag AS ENUM (
  'threat', 'harassment', 'coercive_control', 'financial_issue',
  'parenting_issue', 'apology', 'admission', 'agreement',
  'logistics', 'other'
);

CREATE TABLE message_ml_features (
  message_id      BIGINT PRIMARY KEY REFERENCES message(id) ON DELETE CASCADE,
  lang            TEXT,
  toxicity_score  REAL,
  sentiment_score REAL,
  keyword_hits    TEXT[],
  has_threat      BOOLEAN,
  has_abuse       BOOLEAN,
  mentions_children BOOLEAN,
  mentions_money  BOOLEAN,
  mentions_violence BOOLEAN,
  mentions_selfharm BOOLEAN,
  issue_tags      legal_issue_tag[],
  last_updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source_run_id   BIGINT
);
```

### 4.3 LLM Run Tracking

```sql
CREATE TABLE llm_model (
  id              BIGSERIAL PRIMARY KEY,
  provider        TEXT NOT NULL,
  model_name      TEXT NOT NULL,
  version         TEXT,
  UNIQUE (provider, model_name, version)
);

CREATE TYPE llm_task_type AS ENUM (
  'message_classification', 'thread_summary', 'segment_summary',
  'chronology_build', 'search_explanatory', 'other'
);

CREATE TABLE llm_run (
  id              BIGSERIAL PRIMARY KEY,
  task_type       llm_task_type NOT NULL,
  model_id        BIGINT REFERENCES llm_model(id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  temperature     REAL,
  top_p           REAL,
  max_tokens      INT,
  prompt_template_hash TEXT,
  code_version_hash    TEXT,
  schema_version       TEXT,
  prompt_preview  TEXT,
  raw_request     JSONB,
  raw_response    JSONB,
  success         BOOLEAN,
  error_message   TEXT
);

CREATE TABLE llm_run_message (
  llm_run_id      BIGINT REFERENCES llm_run(id) ON DELETE CASCADE,
  message_id      BIGINT REFERENCES message(id) ON DELETE CASCADE,
  role            TEXT,
  PRIMARY KEY (llm_run_id, message_id)
);

CREATE TABLE message_segment_summary (
  id              BIGSERIAL PRIMARY KEY,
  llm_run_id      BIGINT REFERENCES llm_run(id) ON DELETE SET NULL,
  device_id       BIGINT REFERENCES device(id),
  conversation_id BIGINT REFERENCES conversation(id),
  start_time_utc  TIMESTAMPTZ,
  end_time_utc    TIMESTAMPTZ,
  message_ids     BIGINT[],
  summary_text    TEXT,
  key_points      TEXT[],
  admissions      TEXT[],
  threats         TEXT[],
  metadata        JSONB DEFAULT '{}'::jsonb
);
```

### 4.4 Indexes

```sql
CREATE INDEX idx_message_device_time ON message (device_id, sent_at_utc);
CREATE INDEX idx_message_conv_time ON message (conversation_id, sent_at_utc);
CREATE INDEX idx_message_sender_time ON message (sender_id, sent_at_utc);
CREATE INDEX idx_message_body_fts ON message
  USING GIN (to_tsvector('simple', coalesce(body_normalized, '')));
CREATE INDEX idx_ml_issue_tags ON message_ml_features USING GIN (issue_tags);
CREATE INDEX idx_llm_run_task_type ON llm_run (task_type, created_at DESC);
```

---

## 5. JSON Schemas for LLM Structured Outputs

All LLM outputs must be validated against these schemas before persisting. Use `jsonschema` in Python for validation.

### 5.1 Message Classification Schema

```json
{
  "$id": "message_classification.json",
  "type": "object",
  "required": ["message_id", "labels"],
  "properties": {
    "message_id": { "type": "integer" },
    "labels": {
      "type": "object",
      "required": [
        "has_threat", "has_abuse", "mentions_children",
        "mentions_money", "mentions_violence", "mentions_selfharm",
        "issue_tags"
      ],
      "properties": {
        "has_threat": { "type": "boolean" },
        "has_abuse": { "type": "boolean" },
        "mentions_children": { "type": "boolean" },
        "mentions_money": { "type": "boolean" },
        "mentions_violence": { "type": "boolean" },
        "mentions_selfharm": { "type": "boolean" },
        "issue_tags": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": [
              "threat", "harassment", "coercive_control", "financial_issue",
              "parenting_issue", "apology", "admission", "agreement",
              "logistics", "other"
            ]
          },
          "uniqueItems": true
        }
      }
    },
    "rationale": {
      "type": "string",
      "maxLength": 1000
    }
  },
  "additionalProperties": false
}
```

### 5.2 Classification Prompt Template

```text
You are a classification engine for SMS/iMessage evidence in a legal context.

Task:
Given ONE message, produce JSON matching the provided JSON Schema exactly.

Constraints:
- Do not invent facts not present in the message text.
- Be conservative: if unsure, set booleans to false and use "other" only as a last resort.
- Use Australian English language interpretation.
- Consider the sender's role and the conversation context when classifying.
- "coercive_control" includes patterns of isolation, surveillance, financial control,
  threats to withhold children, or systematic intimidation — even if not overtly violent.

Return ONLY a JSON object, no explanations.

<Message>
ID: {{message_id}}
From: {{sender_role}} ({{sender_address}})
To: {{recipient_role}} ({{recipient_address}})
Timestamp (UTC): {{timestamp}}
Text: """{{body}}"""
</Message>

JSON Schema:
{{schema_text}}
```

### 5.3 Thread Summary Schema

```json
{
  "$id": "thread_summary.json",
  "type": "object",
  "required": [
    "conversation_id", "start_message_id", "end_message_id",
    "summary", "key_points", "potential_admissions", "potential_threats"
  ],
  "properties": {
    "conversation_id": { "type": "integer" },
    "start_message_id": { "type": "integer" },
    "end_message_id": { "type": "integer" },
    "summary": {
      "type": "string",
      "description": "Neutral summary without speculation.",
      "maxLength": 4000
    },
    "key_points": {
      "type": "array",
      "items": { "type": "string", "maxLength": 500 },
      "maxItems": 20
    },
    "potential_admissions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["message_id", "excerpt"],
        "properties": {
          "message_id": { "type": "integer" },
          "excerpt": { "type": "string", "maxLength": 500 }
        }
      },
      "maxItems": 20
    },
    "potential_threats": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["message_id", "excerpt"],
        "properties": {
          "message_id": { "type": "integer" },
          "excerpt": { "type": "string", "maxLength": 500 }
        }
      },
      "maxItems": 20
    }
  },
  "additionalProperties": false
}
```

### 5.4 Chronology Schema

```json
{
  "$id": "chronology.json",
  "type": "object",
  "required": ["events"],
  "properties": {
    "events": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "event_id", "start_time_utc", "end_time_utc",
          "main_participants", "description", "message_ids"
        ],
        "properties": {
          "event_id": { "type": "string" },
          "start_time_utc": { "type": "string", "format": "date-time" },
          "end_time_utc": { "type": "string", "format": "date-time" },
          "main_participants": {
            "type": "array",
            "items": { "type": "string" },
            "maxItems": 10
          },
          "description": { "type": "string", "maxLength": 1000 },
          "message_ids": {
            "type": "array",
            "items": { "type": "integer" },
            "minItems": 1
          }
        }
      }
    }
  },
  "additionalProperties": false
}
```

---

## 6. Classification Pipeline

### 6.1 Batch Processing

```python
import json
import hashlib
from datetime import datetime, timezone

def classify_messages_batch(df, model_name, batch_size=15):
    """
    Classify messages in batches using LLM with JSON Schema validation.

    Returns: list of classification results, list of run records
    """
    import jsonschema

    # Load schema
    with open('schemas/message_classification.json') as f:
        schema = json.load(f)

    results = []
    runs = []

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i + batch_size]

        # Create run record
        run = {
            'id': len(runs) + 1,
            'task_type': 'message_classification',
            'model_name': model_name,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'temperature': 0.0,
            'batch_start_idx': i,
            'batch_size': len(batch),
            'prompt_template_hash': hashlib.sha256(
                CLASSIFICATION_PROMPT_TEMPLATE.encode()
            ).hexdigest()[:16],
            'message_ids': batch['message_id'].tolist(),
        }

        for _, row in batch.iterrows():
            prompt = build_classification_prompt(row, schema)
            response_json = call_llm(prompt, temperature=0.0)

            # Validate against schema
            try:
                jsonschema.validate(response_json, schema)
                results.append(response_json)
                run.setdefault('classified_count', 0)
                run['classified_count'] += 1
            except jsonschema.ValidationError as e:
                # Retry with repair prompt
                repair_response = retry_with_repair(prompt, response_json, str(e))
                try:
                    jsonschema.validate(repair_response, schema)
                    results.append(repair_response)
                    run.setdefault('classified_count', 0)
                    run['classified_count'] += 1
                except jsonschema.ValidationError:
                    run.setdefault('error_count', 0)
                    run['error_count'] += 1

        run['success'] = run.get('error_count', 0) == 0
        runs.append(run)

    return results, runs
```

### 6.2 Multi-Stage Filtering

To maximise recall while keeping LLM work focused:

**Stage 1 — Deterministic filtering** (SQL/pandas):
- Filter by parties, date range, known keywords
- No LLM involvement

**Stage 2 — Light LLM classification**:
- Tag messages for: threat, abuse, financial, parenting, admissions
- Conservative thresholds (if unsure, leave untagged)
- JSON Schema validated

**Stage 3 — Deep LLM summarisation**:
- Only on messages that passed Stage 1+2 filters
- Thread-level summaries with message_id references
- Candidate lists for human review

---

## 7. Thread Summarisation

### 7.1 Segment Splitting

Split conversations into segments using time gaps:

```python
def split_into_segments(df, gap_threshold_hours=2):
    """
    Split a conversation's messages into segments based on time gaps.

    gap_threshold_hours: minimum gap (in hours) to trigger a new segment.
    """
    if len(df) == 0:
        return []

    df = df.sort_values('sent_at_utc').reset_index(drop=True)
    segments = []
    current_segment = [df.iloc[0]]

    for i in range(1, len(df)):
        time_diff = df.iloc[i]['sent_at_utc'] - df.iloc[i-1]['sent_at_utc']
        if time_diff > pd.Timedelta(hours=gap_threshold_hours):
            segments.append(pd.DataFrame(current_segment))
            current_segment = []
        current_segment.append(df.iloc[i])

    if current_segment:
        segments.append(pd.DataFrame(current_segment))

    return segments
```

### 7.2 Summarisation Prompt Template

```text
You summarise SMS/iMessage conversations in a neutral, factual tone for legal review.

Input:
- A single conversation segment: chronological list of messages, each with id,
  timestamp, sender role, and body.

Task:
- Produce JSON matching the Thread Summary JSON Schema.
- "potential_admissions" and "potential_threats" should list only clear candidates,
  referencing specific message_ids and short verbatim excerpts.
- Do not quote or refer to any messages not in the input.
- Do not speculate about mental state or draw legal conclusions.
- Write in Australian English.

Return ONLY JSON, no commentary.

<Segment>
{{serialised_messages}}
</Segment>

JSON Schema:
{{schema_text}}
```

---

## 8. Chronology Builder

### 8.1 Event Extraction Pipeline

```python
def build_chronology(df, parties, date_from=None, date_to=None,
                     cluster_gap_hours=1):
    """
    Build a chronological event sequence from messages.

    1. Filter to specified parties and date range
    2. Cluster messages into events (time-based grouping)
    3. Summarise each event cluster via LLM
    """
    # Filter
    mask = df['logical_party'].isin(parties)
    if date_from:
        mask &= df['sent_at_utc'] >= pd.Timestamp(date_from)
    if date_to:
        mask &= df['sent_at_utc'] <= pd.Timestamp(date_to)

    filtered = df[mask].sort_values('sent_at_utc')

    # Cluster into events
    events = []
    current_cluster = [filtered.iloc[0]] if len(filtered) > 0 else []

    for i in range(1, len(filtered)):
        gap = filtered.iloc[i]['sent_at_utc'] - filtered.iloc[i-1]['sent_at_utc']
        if gap > pd.Timedelta(hours=cluster_gap_hours):
            events.append(pd.DataFrame(current_cluster))
            current_cluster = []
        current_cluster.append(filtered.iloc[i])

    if current_cluster:
        events.append(pd.DataFrame(current_cluster))

    # Summarise each event via LLM (or return raw clusters for manual review)
    return events
```

---

## 9. Agent Design & Tool Interfaces

### 9.1 Tool Abstractions

When building an interactive agent that can query the SMS dataset, define these typed tool interfaces:

```python
# Tool: search_messages (DETERMINISTIC — no LLM)
def tool_search_messages(params):
    """
    Pure SQL/pandas search. Returns message IDs and truncated excerpts.

    Params:
      device_ids: list[int]
      participants: list[str]  (logical party names)
      date_from_utc: str (ISO 8601)
      date_to_utc: str (ISO 8601)
      direction: 'inbound' | 'outbound' | None
      keywords: list[str]
      issue_tags: list[str]
      limit: int (default 50)
      offset: int (default 0)

    Returns:
      message_ids: list[int]
      truncated_messages: list[{id, timestamp_utc, sender_role, recipient_role, excerpt}]
    """
    pass

# Tool: fetch_messages_by_ids
def tool_fetch_messages(params):
    """
    Retrieve full message content by IDs.

    Params:
      message_ids: list[int]

    Returns:
      messages: list[{id, timestamp_utc, sender_role, recipient_role, body}]
    """
    pass

# Tool: classify_messages
def tool_classify_messages(params):
    """
    Run LLM classification on specified messages.

    Params:
      message_ids: list[int]

    Returns:
      classifications: list[{message_id, labels, rationale}]
    """
    pass

# Tool: summarise_segment
def tool_summarise_segment(params):
    """
    Summarise a segment of messages.

    Params:
      conversation_id: int
      start_message_id: int
      end_message_id: int

    Returns:
      summary: ThreadSummary (matching JSON Schema)
    """
    pass
```

### 9.2 Agent Planning Constraints

Hard constraints for any agent system prompt:

- Must describe a plan before invoking tools (for logging).
- Must use `search_messages` to narrow corpus before any summarisation.
- Must never quote or summarise any message not returned by tools in this session.
- Must return final answers as structured JSON with message_id references.
- Must include "All candidates must be manually reviewed in full context" in any output containing admissions or threats.

### 9.3 Example Agent Response Shape

For a query like "find potential threats regarding children around May 2023":

```json
{
  "query": "threats regarding children around 2023-05-10",
  "filters_used": {
    "participants": ["Client", "OpposingParty"],
    "date_from_utc": "2023-05-01T00:00:00Z",
    "date_to_utc": "2023-05-20T23:59:59Z",
    "issue_tags": ["threat", "parenting_issue"]
  },
  "candidate_messages": [
    {
      "message_id": 12345,
      "timestamp_utc": "2023-05-10T09:15:00Z",
      "sender_role": "OpposingParty",
      "excerpt": "If you don't let me see the kids...",
      "reason": "Contains conditional threat relating to children."
    }
  ],
  "notes": "All candidates must be manually reviewed in full context."
}
```

---

## 10. Quality, Robustness & Process Control

### 10.1 Determinism & Reproducibility

- Fix `temperature = 0` (or very low) for all classification tasks.
- Use stable prompt templates with version hashes stored in `llm_run`.
- Always record: `model_name`, `prompt_template_hash`, `code_version_hash`.
- Validate all LLM JSON output against schema before persisting.
- On invalid JSON: retry once with a repair prompt in a controlled loop. Log the failure.

### 10.2 Cross-Check & Evaluation

- Maintain a labelled sample set (manually reviewed messages) to evaluate precision/recall of `has_threat`, `has_abuse`, `mentions_children`, etc.
- Where feasible, run classification with a primary and secondary model; flag disagreements for human review.
- Track which LLM-labelled messages end up in final affidavits/reports (downstream correlation).

### 10.3 Output Formats for Legal Workflows

All exports must include:
- **CSV**: `message_id`, `timestamp_utc`, `sender`, `recipient`, `body`, `issue_tags`, `has_threat`, etc.
- **Report JSON**: Structured data consumable by document template engines.
- **Traceability**: Every AI-produced narrative references concrete `message_id`s that can be located in the original CSV.

---

## 11. iMessage-Specific Forensic Guidance

### 11.1 iOS chat.db Structure

**Database locations**:
- iOS device: `/var/mobile/Library/SMS/sms.db`
- macOS: `/Users/<username>/Library/Messages/chat.db`

**Core tables**: `message`, `chat`, `handle`, `chat_message_join`, `attachment`, `message_attachment_join`, `deleted_messages` (iOS 16+), `chat_handle_join`

**Critical join requirement**: There is no direct foreign key between `message` and `chat`. You must join through `chat_message_join` to associate messages with conversations.

### 11.2 Key Forensic Fields

| Field | Forensic Significance |
|-------|----------------------|
| `ROWID` | Sequential insertion order — gaps indicate deletions |
| `text` | May be empty for edited/unsent messages (iOS 16+) |
| `attributedBody` | Binary blob containing message text when `text` is null; protobuf format; contains tapback/reaction data |
| `is_from_me` | Definitively identifies message direction on the examined device |
| `service` | "iMessage" vs "SMS" — determines which features applied |
| `cache_roomname` | Group chat identifier (machine-readable UUID-style) |
| `expire_state` | Non-zero indicates unsent message (iOS 16+) |
| `message_summary_info` | Blob containing edit history and timestamps (iOS 16+) |
| `date_read` | When message was read (iMessage only, if read receipts enabled) |

### 11.3 Known Gotchas

**Edited messages (iOS 16+)**: The `text` column is blank for edited messages. The edit history is stored in `message_summary_info` (a binary blob). If you see messages with null `text` but valid timestamps and `expire_state = 0`, check `attributedBody` for the content.

**Unsent messages (iOS 16+)**: Both `text` and `attributedBody` are wiped. `expire_state` is set to a non-zero value. The 2-minute unsend window applies to iMessage only (not SMS). Unsent messages on the sender's device may still appear on recipient devices running older iOS versions.

**Tapback reactions**: Stored within `attributedBody` as metadata, not as separate message rows. The `text` column may be blank for reaction-only actions. iOS 18+ supports any emoji as a tapback (not just the original six).

**Deleted messages table**: The `deleted_messages` table (iOS 16+) contains only ROWID and GUID — insufficient for message reconstruction. Deleted messages remain in the main `message` table for up to 30 days (Recently Deleted folder).

**Multipart SMS**: Long SMS messages split into 160-character segments may appear as separate rows. Look for `logical_group_id` or consecutive messages with identical timestamps and the same sender.

**Timestamp precision**: Seconds-level granularity. Multiple messages within the same second require ROWID ordering as a tiebreaker.

### 11.4 Apple Epoch Reference

| Value | Meaning |
|-------|---------|
| Epoch start | 2001-01-01 00:00:00 UTC |
| Offset to Unix | +978,307,200 seconds |
| Typical range (2020–2029) | 600,000,000 – 900,000,000 |
| Detection heuristic | Float value between 6e8 and 9e8 → likely Apple epoch seconds |
| Nanosecond detection | Value > 1e15 → divide by 1e9 first |

---

## 12. Android SMS-Specific Guidance

### 12.1 mmssms.db Structure

**Database location**: `/data/data/com.android.providers.telephony/databases/mmssms.db`

**Key table: `sms`**

| Column | Type | Values |
|--------|------|--------|
| `_id` | Integer | Sequential ROWID |
| `address` | Text | Phone number (directly in row, no join needed) |
| `body` | Text | Message content |
| `date` | Integer | **Milliseconds** since 1970-01-01 UTC |
| `type` | Integer | 1=received, 2=sent, 3=draft, 4=outbox, 5=failed, 6=queued |
| `read` | Integer | 0=unread, 1=read |
| `status` | Integer | -1=failed, 0=complete, 32=pending, 64=received |
| `thread_id` | Integer | Conversation thread identifier |

### 12.2 Key Differences from iOS

- Timestamps in **milliseconds** (divide by 1000 for Unix seconds)
- `type` column uses integer enum for direction (not boolean `is_from_me`)
- Phone numbers stored directly in `address` column (no handle join needed)
- No separate `service_type` — Android SMS database is SMS-only
- Group chats identified by shared `thread_id` + multiple addresses
- No edit, unsend, or reaction features in native SMS
- Deleted SMS recoverable from `mmssms.db-journal` (WAL rollback file)

### 12.3 iOS ↔ Android Field Mapping

| Forensic Concept | iOS (chat.db) | Android (mmssms.db) | CSV Export Notes |
|------------------|---------------|---------------------|------------------|
| **Primary key** | `ROWID` (sequential) | `_id` (sequential) | Gaps indicate deletions on both platforms |
| **Message text** | `text` (or `attributedBody` blob) | `body` | iOS has two fields; check attributedBody if text is null |
| **Timestamp** | `date` (seconds since 2001-01-01) | `date` (milliseconds since 1970-01-01) | Different epochs AND granularity |
| **Direction** | `is_from_me` (boolean: 0/1) | `type` (int: 1=recv, 2=sent, 3=draft) | Boolean vs enumerated |
| **Participant** | `handle_id` → join to `handle` table | `address` (phone number directly in row) | iOS requires join; Android direct |
| **Thread/conversation** | `chat_message_join` → `chat.ROWID` | `thread_id` (direct column) | iOS requires join table; Android direct |
| **Group chat ID** | `cache_roomname` (UUID-style string) | Shared `thread_id` + multiple addresses | iOS has explicit group ID; Android infers from thread |
| **Service type** | `service` ("iMessage" / "SMS") | N/A (SMS-only database) | iMessage-exclusive features not applicable to Android |
| **Read status** | `is_read` (boolean) | `read` (0/1 integer) | Both supported; semantics differ slightly |
| **Delivery status** | `is_delivered` (iMessage only) | `status` (-1=failed, 0=complete, 32=pending) | iOS iMessage only; Android includes failure states |
| **Edit/unsend** | `expire_state`, `message_summary_info` (iOS 16+) | N/A | iOS-only features |
| **Reactions** | `attributedBody` metadata | N/A | iOS tapback stored in blob, not separate rows |

### 12.4 Multipart SMS Reconstruction

Long SMS messages (>160 chars) are split into segments by the carrier. Some forensic exports preserve these as separate rows. Reconstruct them before analysis:

```python
def reconstruct_multipart_sms(df, timestamp_tolerance_seconds=2):
    """
    Stitch multipart SMS segments back into single logical messages.

    Detection heuristic: consecutive rows with same sender, same recipient,
    timestamps within tolerance, and short body text (~160 chars or less).
    """
    df = df.sort_values(['sender_address', 'sent_at_utc']).reset_index(drop=True)
    groups = []
    current_group = [0]

    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        same_sender = prev['sender_address'] == curr['sender_address']
        same_recipient = prev['recipient_address'] == curr['recipient_address']
        time_close = abs(
            (curr['sent_at_utc'] - prev['sent_at_utc']).total_seconds()
        ) <= timestamp_tolerance_seconds
        short_body = len(str(prev.get('body_raw', ''))) <= 165

        if same_sender and same_recipient and time_close and short_body:
            current_group.append(i)
        else:
            groups.append(current_group)
            current_group = [i]

    groups.append(current_group)

    # Stitch groups with >1 segment
    logical_group_id = 1
    for group_indices in groups:
        if len(group_indices) > 1:
            combined_body = ' '.join(
                str(df.iloc[idx]['body_raw']) for idx in group_indices
            )
            # Mark all segments
            for part_idx, row_idx in enumerate(group_indices):
                df.at[row_idx, 'logical_group_id'] = logical_group_id
                df.at[row_idx, 'logical_part_index'] = part_idx
            # Store combined body on first segment
            df.at[group_indices[0], 'body_raw'] = combined_body
            df.at[group_indices[0], 'body_normalized'] = combined_body.lower().strip()
            logical_group_id += 1

    return df
```

### 12.5 Carrier Records Handling

Carrier warrant returns and CDR (Call Detail Records) differ significantly from device exports:

- **No message body**: Carrier SMS records often contain only metadata (from, to, timestamp, message length) without the actual text content.
- **No direction context**: No `is_from_me` equivalent — you must determine direction from the phone numbers (match against known parties).
- **No thread/conversation ID**: Messages are flat records with no threading.
- **Timestamps**: Usually ISO 8601 or carrier-specific formats; may be in the carrier's local timezone rather than UTC.
- **Limitations**: Cannot detect deleted/edited/unsent messages, reactions, or read receipts from carrier data alone.

When ingesting carrier records, set `platform = 'carrier'` and flag that body text may be unavailable. Carrier data is primarily useful for establishing that communication occurred (timing, frequency, parties) rather than for content analysis.

---

## 13. Family Law SMS Playbook

Family law matters are the most common use case for SMS forensic analysis. This playbook extends the general Family Law playbook (Playbook 5 in SKILL.md) with SMS-specific guidance.

### 13.1 Typical Analysis Questions

1. **Threat identification**: Did either party make threats about children, finances, or physical harm?
2. **Coercive control patterns**: Is there evidence of systematic control, isolation, or intimidation?
3. **Parenting arrangements**: What was agreed about custody, handover times, school decisions?
4. **Admissions**: Did either party acknowledge fault, violence, substance use, or other relevant conduct?
5. **Timeline of events**: When did key incidents occur? Does the messaging evidence corroborate or contradict affidavit claims?

### 13.2 Recommended Workflow

1. **Ingest** all SMS/iMessage CSV exports (one per device if multiple)
2. **Map participants**: Client, OpposingParty, Child (if messaging directly), Solicitor, ThirdParty
3. **Run deterministic search** for high-priority keywords:
   - Threats: kill, hurt, harm, destroy, "you'll be sorry", "take the kids", "never see them"
   - Coercive control: "don't go", "who were you with", "show me your phone", "I'll track you", "blocked"
   - Financial: money, pay, account, property, sell, transfer, hide
   - Children: kids, children, school, custody, access, handover, pickup, dropoff
   - Admissions: "I hit", "I'm sorry I", "I was drunk", "I shouldn't have"
4. **Run AI classification** on the full dataset (or filtered by relevant parties/dates)
5. **Generate thread summaries** for key conversations
6. **Build chronology** centred on the client and opposing party
7. **Export** candidate messages for solicitor review, with Bates-style numbering

### 13.3 Family Law Search Term Library

```python
FAMILY_LAW_TERMS = {
    'threats': [
        r'\bkill\b', r'\bhurt\b', r'\bharm\b', r'\bdestroy\b',
        r'you.ll\s+be\s+sorry', r'take\s+the\s+kids',
        r'never\s+see\s+them', r'i.ll\s+make\s+sure',
        r'watch\s+(your|ur)\s+back', r'regret',
    ],
    'coercive_control': [
        r'don.t\s+(go|leave)', r'where\s+(are|were|have)\s+you',
        r'who\s+(are|were)\s+you\s+with', r'show\s+me\s+your\s+phone',
        r'i.ll\s+track', r'blocked', r'not\s+allowed',
        r'my\s+house', r'my\s+rules', r'you\s+can.t',
        r'i\s+control', r'permission',
    ],
    'financial': [
        r'\bmoney\b', r'\bpay\b', r'\baccount\b', r'\bproperty\b',
        r'\bsell\b', r'\btransfer\b', r'\bhide\b', r'\basset',
        r'\bsuper\b', r'\bmortgage\b', r'\bdebt\b',
    ],
    'children': [
        r'\bkids?\b', r'\bchildren\b', r'\bschool\b', r'\bcustody\b',
        r'\baccess\b', r'\bhandover\b', r'\bpickup\b', r'\bdropoff\b',
        r'\bweekend\b', r'\bholiday\b', r'\bbirthday\b',
    ],
    'admissions': [
        r'i\s+hit', r'i\s+pushed', r'i\s+was\s+drunk',
        r'i\s+shouldn.t\s+have', r'i.m\s+sorry\s+i',
        r'my\s+fault', r'i\s+admit', r'i\s+was\s+wrong',
    ],
}
```

### 13.4 Output for Solicitor Review

The final output for family law SMS analysis should include:

1. **Participant summary**: Who is in the dataset, message counts, date ranges
2. **Threat register**: All messages flagged as threats, sorted chronologically, with full context (preceding and following messages)
3. **Coercive control timeline**: Chronological evidence of controlling behaviour patterns
4. **Admissions register**: Messages containing statements against interest
5. **Parenting chronology**: All messages about children, arrangements, handovers
6. **Full chronology**: Timeline of all significant events with message_id references
7. **Raw data export**: CSV of all messages with classification labels, suitable for import into eDiscovery platform

Every item in registers 2–5 must include: `message_id`, timestamp (UTC and local), sender role, recipient role, full message text, and surrounding context (2 messages before and after).

---

## §14: Relationship & Conversational Analysis

This section provides AI-assisted analysis patterns for identifying relationship dynamics and communication patterns in messaging data.

### 14.1 Escalation Detection

Detects sequences of increasing hostile behaviour within defined time windows. Critical for establishing pattern evidence in coercive control and family violence contexts.

```python
from typing import List, Dict, Tuple
import pandas as pd
import re

def detect_escalation_patterns(
    df: pd.DataFrame,
    window_hours: int = 24,
    min_sequence_length: int = 3
) -> List[Dict]:
    """
    Identify escalation patterns within conversation sequences.

    Tracks:
    - Increasing hostile language density
    - Shortening response times from aggressor
    - Lengthening messages (ranting)
    - Profanity escalation
    - ALL-CAPS usage increase

    Args:
        df: DataFrame with columns: timestamp (datetime), sender, text, message_id
        window_hours: Time window for pattern detection
        min_sequence_length: Minimum messages to constitute escalation

    Returns:
        List of escalation events with start/end timestamps, severity (0-1), and message_ids
    """

    HOSTILE_KEYWORDS = {
        'explicit': ['fuck', 'shit', 'cunt', 'bastard', 'arsehole'],
        'threatening': ['you will', 'you must', 'you better', 'or else', 'i will'],
        'contemptuous': ['pathetic', 'useless', 'stupid', 'idiot', 'loser']
    }

    def score_hostility(text: str) -> float:
        """Score text hostility 0-1."""
        if not isinstance(text, str):
            return 0.0

        text_lower = text.lower()
        score = 0.0

        # Profanity density
        profanities = sum(1 for kw in HOSTILE_KEYWORDS['explicit'] if kw in text_lower)
        score += min(profanities * 0.2, 0.3)

        # Threatening language
        if any(kw in text_lower for kw in HOSTILE_KEYWORDS['threatening']):
            score += 0.25

        # Contemptuous language
        if any(kw in text_lower for kw in HOSTILE_KEYWORDS['contemptuous']):
            score += 0.15

        # ALL-CAPS density
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.5:
            score += 0.2

        return min(score, 1.0)

    df_sorted = df.sort_values('timestamp').reset_index(drop=True)
    escalations = []

    for sender in df_sorted['sender'].unique():
        sender_msgs = df_sorted[df_sorted['sender'] == sender].reset_index(drop=True)

        for i in range(len(sender_msgs) - min_sequence_length + 1):
            window_start = sender_msgs.iloc[i]['timestamp']
            window_end = window_start + pd.Timedelta(hours=window_hours)

            window_msgs = sender_msgs[
                (sender_msgs['timestamp'] >= window_start) &
                (sender_msgs['timestamp'] <= window_end)
            ].reset_index(drop=True)

            if len(window_msgs) < min_sequence_length:
                continue

            # Score each message
            hostility_scores = [score_hostility(msg) for msg in window_msgs['text']]

            # Check for escalation trend (increasing hostility)
            if hostility_scores[-1] > hostility_scores[0]:
                severity = min(hostility_scores[-1], 1.0)

                # Check for response time shortening
                response_times = window_msgs['timestamp'].diff().dt.total_seconds() / 3600
                response_times = response_times.dropna()

                if len(response_times) > 1 and response_times.iloc[-1] < response_times.iloc[0]:
                    severity *= 1.2  # Boost severity if response times shortening

                escalations.append({
                    'sender': sender,
                    'start_timestamp': window_start,
                    'end_timestamp': window_msgs.iloc[-1]['timestamp'],
                    'severity_score': min(severity, 1.0),
                    'message_count': len(window_msgs),
                    'message_ids': window_msgs['message_id'].tolist(),
                    'hostility_progression': hostility_scores,
                    'trigger_message_id': window_msgs.iloc[0]['message_id']
                })

    return escalations
```

### 14.2 Response Time Analysis

Quantifies asymmetries in communication timing, which often signal anxiety, fear, or power imbalances.

```python
def analyse_response_times(
    df: pd.DataFrame,
    party_a: str,
    party_b: str,
    period_days: int = 30
) -> Dict:
    """
    Analyse message response patterns between two parties.

    Computes:
    - Median and mean response time per party
    - Asymmetry ratio (indicates anxiety/dependence)
    - Response time changes over date ranges
    - Silence periods (gaps > 24h after rapid exchange)

    Args:
        df: DataFrame with columns: timestamp (datetime), sender, recipient, message_id
        party_a: Name/ID of first party
        party_b: Name/ID of second party
        period_days: Days to analyse per period

    Returns:
        Dict with metrics per party and per time period
    """

    df_sorted = df.sort_values('timestamp').reset_index(drop=True)

    # Extract response times: time between one party's message and other party's next message
    response_data = []

    for i in range(len(df_sorted) - 1):
        current_msg = df_sorted.iloc[i]
        next_msg = df_sorted.iloc[i + 1]

        if current_msg['sender'] != next_msg['sender']:
            time_delta = (next_msg['timestamp'] - current_msg['timestamp']).total_seconds() / 3600

            response_data.append({
                'responder': next_msg['sender'],
                'initiator': current_msg['sender'],
                'response_hours': time_delta,
                'timestamp': next_msg['timestamp']
            })

    response_df = pd.DataFrame(response_data)

    if response_df.empty:
        return {'error': 'Insufficient messages for analysis'}

    # Per-party metrics
    metrics = {}
    for party in [party_a, party_b]:
        party_responses = response_df[response_df['responder'] == party]

        if len(party_responses) > 0:
            metrics[party] = {
                'median_response_hours': party_responses['response_hours'].median(),
                'mean_response_hours': party_responses['response_hours'].mean(),
                'std_response_hours': party_responses['response_hours'].std(),
                'response_count': len(party_responses),
                'responses_under_1h': (party_responses['response_hours'] < 1).sum(),
                'responses_over_24h': (party_responses['response_hours'] > 24).sum(),
            }

    # Asymmetry ratio
    if party_a in metrics and party_b in metrics:
        ratio_a = metrics[party_a]['median_response_hours']
        ratio_b = metrics[party_b]['median_response_hours']

        if ratio_b > 0:
            asymmetry = ratio_a / ratio_b
        else:
            asymmetry = float('inf')

        metrics['asymmetry_ratio'] = {
            'ratio': asymmetry,
            'interpretation': (
                f'{party_a} responds {asymmetry:.1f}x faster than {party_b}'
                if asymmetry > 1 else
                f'{party_b} responds {1/max(asymmetry, 0.01):.1f}x faster than {party_a}'
            )
        }

    # Silence periods (gaps > 24h after rapid exchange)
    response_df['is_rapid'] = response_df['response_hours'] < 1
    silence_periods = []

    for i in range(len(response_df) - 1):
        if response_df.iloc[i]['is_rapid'] and response_df.iloc[i + 1]['response_hours'] > 24:
            silence_periods.append({
                'after_timestamp': response_df.iloc[i]['timestamp'],
                'silence_hours': response_df.iloc[i + 1]['response_hours'],
                'responder_during_silence': response_df.iloc[i + 1]['responder']
            })

    metrics['silence_periods'] = silence_periods

    return metrics
```

### 14.3 Message Volume & Frequency Patterns

Detects patterns of message flooding, barrages, and abnormal timing that may indicate escalation or crisis.

```python
def analyse_message_flooding(
    df: pd.DataFrame,
    participant: str,
    threshold_multiplier: float = 3.0,
    baseline_period_days: int = 30
) -> List[Dict]:
    """
    Detect message flooding and volume spike patterns.

    Identifies:
    - Message flooding (volume spikes > threshold × baseline)
    - One-sided barrages (many messages with no reply)
    - Late-night messaging patterns (22:00-06:00 local time)
    - Weekend/holiday contact when previously limited

    Args:
        df: DataFrame with columns: timestamp (datetime), sender, local_timestamp (datetime)
        participant: Name/ID to analyse
        threshold_multiplier: Volume spike threshold (default 3.0 = 3x baseline)
        baseline_period_days: Days to establish baseline

    Returns:
        List of flagged periods with timestamps, counts, and baseline comparison
    """

    df_sorted = df.sort_values('timestamp').reset_index(drop=True)
    participant_msgs = df_sorted[df_sorted['sender'] == participant].reset_index(drop=True)

    if len(participant_msgs) == 0:
        return []

    flagged_periods = []

    # Establish baseline (messages per day over first baseline_period_days)
    baseline_end = participant_msgs['timestamp'].min() + pd.Timedelta(days=baseline_period_days)
    baseline_msgs = participant_msgs[participant_msgs['timestamp'] <= baseline_end]

    if len(baseline_msgs) > 0:
        baseline_daily_rate = len(baseline_msgs) / baseline_period_days
    else:
        baseline_daily_rate = 0

    threshold = baseline_daily_rate * threshold_multiplier

    # Detect daily spikes
    participant_msgs['date'] = participant_msgs['timestamp'].dt.date
    daily_counts = participant_msgs.groupby('date').size()

    for date, count in daily_counts.items():
        if count > threshold:
            flagged_periods.append({
                'type': 'volume_spike',
                'date': date,
                'message_count': count,
                'baseline_daily_rate': baseline_daily_rate,
                'spike_multiplier': count / max(baseline_daily_rate, 1),
                'message_ids': participant_msgs[participant_msgs['date'] == date]['message_id'].tolist()
            })

    # Detect one-sided barrages (3+ messages without recipient reply)
    for i in range(len(participant_msgs) - 2):
        window = participant_msgs.iloc[i:i+4]

        if len(window) >= 3 and all(msg['sender'] == participant for msg in window.to_dict('records')[:-1]):
            next_idx = i + 3
            if next_idx < len(participant_msgs):
                next_msg = participant_msgs.iloc[next_idx]
                if next_msg['sender'] != participant:
                    continue  # Replied to, not a barrage

            flagged_periods.append({
                'type': 'barrage',
                'start_timestamp': window.iloc[0]['timestamp'],
                'end_timestamp': window.iloc[-1]['timestamp'],
                'message_count': len(window),
                'message_ids': window['message_id'].tolist()
            })

    # Late-night messaging (22:00-06:00)
    late_msgs = participant_msgs[
        (participant_msgs['local_timestamp'].dt.hour >= 22) |
        (participant_msgs['local_timestamp'].dt.hour < 6)
    ]

    if len(late_msgs) > 0:
        late_night_rate = len(late_msgs) / len(participant_msgs)
        if late_night_rate > 0.3:  # More than 30% of messages at night
            flagged_periods.append({
                'type': 'late_night_pattern',
                'message_count': len(late_msgs),
                'percentage_of_total': late_night_rate * 100,
                'message_ids': late_msgs['message_id'].tolist()
            })

    return flagged_periods
```

### 14.4 Power Dynamic Indicators

Assesses communication patterns that reveal dominance, submission, control, or equality using deterministic language analysis.

```python
def assess_power_dynamics(
    df: pd.DataFrame,
    party_a: str,
    party_b: str
) -> Dict:
    """
    Analyse language patterns indicating power imbalances.

    Analyses:
    - Directive vs request language ratio
    - Question-demand asymmetry
    - Initiation vs response patterns
    - Command verbs ("do", "must", "need to", "you will")
    - Apologetic language asymmetry
    - Topic control (who sets subjects)

    Uses keyword lists and regex patterns (deterministic, not LLM).

    Args:
        df: DataFrame with columns: timestamp (datetime), sender, text, message_id
        party_a: Name/ID of first party
        party_b: Name/ID of second party

    Returns:
        Dict with power_score per party (higher = more dominant) and supporting evidence
    """

    COMMAND_VERBS = ['do', 'must', 'have to', 'need to', 'you will', 'you should', 'get', 'make']
    APOLOGETIC_WORDS = ['sorry', 'apologise', 'my fault', 'i was wrong', 'forgive me', 'pardon', 'excuse me']
    QUESTION_MARKERS = [r'\?', r'can you', r'could you', r'would you', r'will you']
    DEMAND_MARKERS = [r'you (must|will|need to|have to)', r'do (not|this|that)', r'get (out|away|lost)']

    def count_pattern_matches(text: str, patterns: List[str]) -> int:
        """Count regex/keyword matches in text."""
        if not isinstance(text, str):
            return 0
        text_lower = text.lower()
        count = 0
        for pattern in patterns:
            try:
                count += len(re.findall(pattern, text_lower, re.IGNORECASE))
            except re.error:
                count += (1 if pattern in text_lower else 0)
        return count

    df_sorted = df.sort_values('timestamp').reset_index(drop=True)

    metrics = {party_a: {}, party_b: {}}

    for party in [party_a, party_b]:
        party_msgs = df_sorted[df_sorted['sender'] == party]
        other_party = party_b if party == party_a else party_a
        other_party_msgs = df_sorted[df_sorted['sender'] == other_party]

        # Directive language
        directives = sum(
            count_pattern_matches(msg, COMMAND_VERBS)
            for msg in party_msgs['text']
        )

        # Questions
        questions = sum(
            count_pattern_matches(msg, QUESTION_MARKERS)
            for msg in party_msgs['text']
        )

        # Apologetic language
        apologies = sum(
            count_pattern_matches(msg, APOLOGETIC_WORDS)
            for msg in party_msgs['text']
        )

        # Initiation count (messages that start a conversation after > 1h silence)
        initiations = 0
        for i in range(len(party_msgs)):
            if i == 0:
                initiations += 1
            else:
                time_since_last = (party_msgs.iloc[i]['timestamp'] - party_msgs.iloc[i-1]['timestamp']).total_seconds() / 3600
                if time_since_last > 1:
                    initiations += 1

        total_msgs = len(party_msgs)

        metrics[party] = {
            'total_messages': total_msgs,
            'directive_count': directives,
            'directive_ratio': directives / max(total_msgs, 1),
            'question_count': questions,
            'question_ratio': questions / max(total_msgs, 1),
            'apologetic_count': apologies,
            'apologetic_ratio': apologies / max(total_msgs, 1),
            'initiation_count': initiations,
            'initiation_ratio': initiations / max(total_msgs, 1),
        }

    # Compute power scores
    power_a = (
        metrics[party_a]['directive_ratio'] * 0.4 +
        (1 - metrics[party_a]['question_ratio']) * 0.2 +
        (1 - metrics[party_a]['apologetic_ratio']) * 0.2 +
        metrics[party_a]['initiation_ratio'] * 0.2
    )

    power_b = (
        metrics[party_b]['directive_ratio'] * 0.4 +
        (1 - metrics[party_b]['question_ratio']) * 0.2 +
        (1 - metrics[party_b]['apologetic_ratio']) * 0.2 +
        metrics[party_b]['initiation_ratio'] * 0.2
    )

    return {
        'party_a': party_a,
        'party_b': party_b,
        'party_a_power_score': power_a,
        'party_b_power_score': power_b,
        'power_asymmetry': abs(power_a - power_b),
        'dominant_party': party_a if power_a > power_b else party_b,
        'detailed_metrics': metrics
    }
```

### 14.5 Communication Pattern Change Detection

Identifies shifts in communication style and volume around significant life events (court dates, IVO applications, separations).

```python
def detect_pattern_changes(
    df: pd.DataFrame,
    party_a: str,
    party_b: str,
    event_dates: List[Tuple[str, pd.Timestamp]] = None,
    window_days: int = 14
) -> Dict:
    """
    Detect communication pattern changes around key events.

    Compares message volume, tone markers, and response times before vs after events.

    Args:
        df: DataFrame with columns: timestamp (datetime), sender, text
        party_a: Name/ID of first party
        party_b: Name/ID of second party
        event_dates: List of tuples (event_name, timestamp)
        window_days: Days before/after event to analyse

    Returns:
        Change report per event date with statistical metrics
    """

    if not event_dates:
        return {'message': 'No event dates provided'}

    df_sorted = df.sort_values('timestamp').reset_index(drop=True)
    change_reports = []

    for event_name, event_timestamp in event_dates:
        before_start = event_timestamp - pd.Timedelta(days=window_days)
        before_end = event_timestamp
        after_start = event_timestamp
        after_end = event_timestamp + pd.Timedelta(days=window_days)

        before_msgs = df_sorted[
            (df_sorted['timestamp'] >= before_start) &
            (df_sorted['timestamp'] < before_end)
        ]

        after_msgs = df_sorted[
            (df_sorted['timestamp'] >= after_start) &
            (df_sorted['timestamp'] <= after_end)
        ]

        before_a = len(before_msgs[before_msgs['sender'] == party_a])
        before_b = len(before_msgs[before_msgs['sender'] == party_b])
        after_a = len(after_msgs[after_msgs['sender'] == party_a])
        after_b = len(after_msgs[after_msgs['sender'] == party_b])

        change_reports.append({
            'event': event_name,
            'event_timestamp': event_timestamp,
            'before_period': f'{before_start.date()} to {before_end.date()}',
            'after_period': f'{after_start.date()} to {after_end.date()}',
            'message_counts_before': {party_a: before_a, party_b: before_b},
            'message_counts_after': {party_a: after_a, party_b: after_b},
            'volume_change_a': after_a - before_a,
            'volume_change_b': after_b - before_b,
            'direction': 'increased' if (after_a + after_b) > (before_a + before_b) else 'decreased'
        })

    return {'events': change_reports}
```

### 14.6 Tone & Sentiment Markers (Deterministic)

Provides reproducible, audit-trail-friendly tone classification using regex patterns tailored to Australian English idiom.

```python
TONE_MARKERS = {
    'hostile': [
        'get stuffed', 'get fucked', 'fuck off', 'piss off', 'get lost',
        'go to hell', 'pull your head in', 'you\'re dreaming', 'bullshit',
        'arsehole', 'bastard', 'prick', 'dickhead', 'twat'
    ],
    'threatening': [
        r'you will (pay|regret|suffer)',
        r'(if you don\'t|unless you)',
        r'(i will|i\'m going to) (tell|report|take)',
        r'court order', r'police', r'lawyers',
        r'you better', r'or else', r'do as i say'
    ],
    'contemptuous': [
        'pathetic', 'useless', 'stupid', 'idiot', 'loser', 'worthless',
        'incompetent', 'weak', 'disgusting', 'abusive', 'selfish'
    ],
    'dismissive': [
        'i don\'t care', 'don\'t bother', 'forget it', 'whatever', 'yeah right',
        'sure you will', 'pull the other one', 'wake up to yourself',
        'you\'re making it up', 'that\'s a lie'
    ],
    'anxious': [
        'please', 'i\'m worried', 'i\'m scared', 'what if', 'are you okay',
        'don\'t leave', 'i can\'t cope', 'help me', 'why aren\'t you'
    ],
    'apologetic': [
        'sorry', 'apologise', 'my fault', 'i was wrong', 'forgive', 'i shouldn\'t have',
        'you\'re right', 'i understand', 'i see your point', 'i messed up'
    ],
    'controlling': [
        r'you must', r'you will', r'you (need to|have to)',
        'do this', 'don\'t', 'you\'re not', 'i\'m telling you',
        'that\'s final', 'no discussion', 'my way', 'because i said so'
    ],
    'neutral': [
        'okay', 'thanks', 'got it', 'let me know', 'see you then', 'fine'
    ]
}

def tag_tone_markers(text: str) -> List[str]:
    """
    Identify tone markers in text using deterministic patterns.

    Args:
        text: Message text to analyse

    Returns:
        List of matched tone categories
    """

    if not isinstance(text, str):
        return []

    text_lower = text.lower()
    matched_tones = []

    for tone_category, patterns in TONE_MARKERS.items():
        for pattern in patterns:
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matched_tones.append(tone_category)
                    break  # Only count each category once per message
            except re.error:
                if pattern in text_lower:
                    matched_tones.append(tone_category)
                    break

    return list(set(matched_tones))  # Deduplicate
```

---

## §15: Child Protection & Coercive Control Detection

This section provides specialised detection logic for child protection risk indicators and coercive control patterns, aligned with Australian legislation.

### 15.1 Child Protection Risk Indicators

Systematic screening for indicators of child safety risk, neglect, exposure to violence, and inappropriate parenting within messaging data.

```python
CHILD_PROTECTION_INDICATORS = {
    'neglect_signals': [
        'no food', 'hungry', 'hasn\'t eaten', 'not attending school', 'no school',
        'sick', 'ill', 'fever', 'not taken to doctor', 'needs treatment', 'can\'t afford',
        'no supervision', 'left alone', 'unsupervised', 'nobody looking after',
        'dirty', 'no clean clothes', 'no shower'
    ],
    'exposure_to_violence': [
        'heard us fighting', 'saw the fight', 'was there when',
        'children witnessed', 'kids saw', 'in front of the kids',
        'screaming', 'yelling', 'violent', 'aggressive', 'hit', 'pushed',
        'scared of', 'doesn\'t feel safe'
    ],
    'substance_abuse_around_children': [
        r'(drunk|stoned|high).*(kids|children)',
        r'(drink|drugs|alcohol).*(parenting time|their turn)',
        r'driving.*(drunk|high)',
        r'(beer|wine|whiskey|marijuana|meth|cocaine)',
        'bottle of', 'line of', 'smoked a'
    ],
    'inappropriate_parenting': [
        'left with', 'left them with', 'babysitter', 'carer',
        'inappropriate content', 'adult films', 'porn', 'explicit',
        'no rules', 'no discipline', 'anything goes', 'spoiled'
    ],
    'emotional_harm': [
        'telling them you hate me', 'telling them i\'m bad',
        'using them as a messenger', 'tell your mum', 'tell your dad',
        'you don\'t love your', 'your parent doesn\'t care',
        'belittling', 'worthless', 'stupid child', 'dumb', 'failure'
    ],
    'grooming_indicators': [
        r'(secret|don\'t tell).*(parent|mum|dad)',
        r'special (relationship|time|secret)',
        r'don\'t need to tell',
        'gifts', 'presents', 'special treatment',
        'boundary', 'inappropriate', 'private'
    ]
}

def screen_child_protection(
    df: pd.DataFrame,
    keywords_dict: Dict = CHILD_PROTECTION_INDICATORS
) -> List[Dict]:
    """
    Screen messages for child protection risk indicators.

    Args:
        df: DataFrame with columns: message_id, timestamp, sender, text
        keywords_dict: Dictionary mapping categories to keyword/pattern lists

    Returns:
        List of flagged messages with category, severity, and message_id
    """

    flagged = []
    severity_multipliers = {
        'neglect_signals': 1.0,
        'exposure_to_violence': 1.2,
        'substance_abuse_around_children': 1.3,
        'inappropriate_parenting': 1.1,
        'emotional_harm': 0.9,
        'grooming_indicators': 1.4
    }

    for idx, row in df.iterrows():
        text = row.get('text', '')
        if not isinstance(text, str):
            continue

        text_lower = text.lower()
        matched_categories = []

        for category, patterns in keywords_dict.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        matched_categories.append(category)
                        break
                except re.error:
                    if pattern in text_lower:
                        matched_categories.append(category)
                        break

        if matched_categories:
            # Severity: base 0.5 per category matched, multiplied by category weight
            severity = min(
                sum(severity_multipliers.get(cat, 1.0) for cat in matched_categories) / len(matched_categories),
                1.0
            )

            severity_level = 'critical' if severity > 0.8 else 'high' if severity > 0.6 else 'medium' if severity > 0.4 else 'low'

            flagged.append({
                'message_id': row.get('message_id'),
                'timestamp': row.get('timestamp'),
                'sender': row.get('sender'),
                'text': text[:100] + '…' if len(text) > 100 else text,
                'categories': list(set(matched_categories)),
                'severity_score': round(severity, 2),
                'severity_level': severity_level
            })

    return sorted(flagged, key=lambda x: x['severity_score'], reverse=True)
```

### 15.2 Coercive Control Pattern Detection

Detects patterns aligned with Australian coercive control legislation (Crimes Legislation Amendment (Coercive Control) Act 2022 NSW and similar QLD/TAS provisions). Coercive control is fundamentally about cumulative pattern, not single incidents.

```python
COERCIVE_CONTROL_PATTERNS = {
    'monitoring_surveillance': [
        r'(where are you|what are you doing|who are you with)',
        r'(tracking|gps|location sharing)',
        r'(check your phone|read your messages)',
        r'(who (did|are) you (texting|calling|seeing))',
        r'(call me when|text me when|let me know)',
        'spyware', 'tracking app', 'see my location', 'tracker',
        'checking up', 'following you'
    ],
    'isolation': [
        r'(don\'t (see|talk to|speak to)).*(friend|family|mum|dad|sister)',
        r'(can\'t see|can\'t talk to)',
        r'(i don\'t want you).*(friends|family)',
        r'(you can\'t go to|you shouldn\'t go to)',
        'cutting you off', 'don\'t need them', 'they don\'t care', 'i\'m all you need'
    ],
    'financial_control': [
        r'(account|credit card|money|cash)',
        r'(how much did you spend)',
        r'(you can\'t afford|i control)',
        r'(receipt|proof of purchase)',
        'no money for', 'can\'t have', 'financial', 'budget', 'accounts are frozen'
    ],
    'threats_intimidation': [
        r'(you will pay|you will regret)',
        r'(if you don\'t|or else)',
        r'(i\'ll (take|report|tell|call))',
        r'(threats|threatened)',
        'scared', 'frightened', 'afraid', 'worried for safety'
    ],
    'degradation': [
        r'(you\'re|you are) (useless|pathetic|worthless|stupid|ugly)',
        'disgusting', 'failure', 'no good', 'embarrassment', 'loser',
        'fat', 'ugly', 'bitch', 'slag', 'whore', 'slut', 'messed up'
    ],
    'regulation_of_daily_life': [
        r'(you (must|have to|will) (wear|eat|sleep|do))',
        r'(i don\'t allow|not permitted|not acceptable)',
        r'(bedtime|wake up|where you go)',
        'you\'re not allowed', 'i decide', 'my rules', 'that\'s forbidden'
    ],
    'technology_abuse': [
        r'(password|pin|access)',
        r'(facebook|instagram|twitter|snapchat).*control',
        r'(social media|posting|commenting)',
        'app monitoring', 'spyware', 'tracking software', 'can\'t have accounts'
    ]
}

def detect_coercive_control(
    df: pd.DataFrame,
    accused_party: str,
    keywords_dict: Dict = COERCIVE_CONTROL_PATTERNS,
    min_incidents_per_category: int = 2
) -> Dict:
    """
    Detect coercive control patterns aligned with Australian legislation.

    Builds cumulative timeline of incidents across categories. Coercive control is a pattern,
    not a single incident.

    Args:
        df: DataFrame with columns: message_id, timestamp, sender, text
        accused_party: Party alleged to be engaging in coercive control
        keywords_dict: Patterns dictionary (use legislative alignment)
        min_incidents_per_category: Minimum incidents to flag category as pattern

    Returns:
        Dict with timeline, density scores, and pattern assessment
    """

    df_sorted = df.sort_values('timestamp').reset_index(drop=True)
    accused_msgs = df_sorted[df_sorted['sender'] == accused_party]

    timeline = {cat: [] for cat in keywords_dict.keys()}

    for idx, row in accused_msgs.iterrows():
        text = row.get('text', '')
        if not isinstance(text, str):
            continue

        text_lower = text.lower()

        for category, patterns in keywords_dict.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        timeline[category].append({
                            'timestamp': row['timestamp'],
                            'message_id': row['message_id'],
                            'pattern_matched': pattern,
                            'text_excerpt': text[:80]
                        })
                        break
                except re.error:
                    if pattern in text_lower:
                        timeline[category].append({
                            'timestamp': row['timestamp'],
                            'message_id': row['message_id'],
                            'pattern_matched': pattern,
                            'text_excerpt': text[:80]
                        })
                        break

    # Compute density by month
    monthly_density = {}
    for category, incidents in timeline.items():
        if incidents:
            for incident in incidents:
                month_key = incident['timestamp'].strftime('%Y-%m')
                if month_key not in monthly_density:
                    monthly_density[month_key] = {}
                monthly_density[month_key][category] = monthly_density[month_key].get(category, 0) + 1

    # Pattern assessment
    flagged_categories = {
        cat: incidents for cat, incidents in timeline.items()
        if len(incidents) >= min_incidents_per_category
    }

    overall_severity = 'no_pattern'
    if len(flagged_categories) >= 3:
        total_incidents = sum(len(incidents) for incidents in flagged_categories.values())
        if total_incidents > 10:
            overall_severity = 'severe'
        elif total_incidents > 5:
            overall_severity = 'moderate'
        else:
            overall_severity = 'emerging'

    return {
        'accused_party': accused_party,
        'analysis_period': f"{df_sorted['timestamp'].min().date()} to {df_sorted['timestamp'].max().date()}",
        'timeline_by_category': {
            cat: sorted(incidents, key=lambda x: x['timestamp'])
            for cat, incidents in flagged_categories.items()
        },
        'incident_count_by_category': {cat: len(incidents) for cat, incidents in flagged_categories.items()},
        'total_incidents': sum(len(incidents) for incidents in flagged_categories.values()),
        'monthly_density': monthly_density,
        'overall_severity': overall_severity,
        'assessment_note': (
            'Coercive control is a pattern of behaviour, not individual incidents. This analysis identifies '
            'candidate patterns for human review by a qualified legal professional. A finding of coercive control '
            'requires consideration of the cumulative effect, context, impact on the victim, and the accused\'s '
            'intent. Individual messages may appear benign in isolation but form part of a controlling pattern '
            'when viewed together.'
        )
    }
```

### 15.3 Parental Alienation Markers

Identifies patterns of deliberate undermining of the other parent's relationship with children, a significant factor in parenting orders.

```python
ALIENATION_MARKERS = {
    'denigration': [
        r'your (mum|dad|mother|father) (is|\'s) (a|an)',
        r'your (parent) doesn\'t (care|love)',
        r'(mum|dad) is (selfish|cruel|bad|nasty)',
        r'(mum|dad) doesn\'t want',
        'bad parent', 'useless parent', 'you can\'t trust'
    ],
    'interference_with_contact': [
        r'(can\'t|won\'t) (have|see).*(mum|dad|other parent)',
        r'(not taking you to)',
        r'(plan.*cancel|cancel.*plan)',
        'forgot about', 'forgot the time', 'isn\'t coming',
        'doesn\'t care enough', 'too busy'
    ],
    'information_withholding': [
        r'(didn\'t tell|won\'t tell).*(mum|dad)',
        r'(school|doctor|medical).*secret',
        r'(don\'t (need to|have to) tell)',
        'don\'t need to know', 'not their business', 'none of their concern'
    ],
    'undermining_authority': [
        r'(mum|dad|other parent).*doesn\'t know (best|what\'s good)',
        r'(they|your parent) (don\'t|doesn\'t) (understand|care)',
        r'(mum|dad) (is wrong|doesn\'t know|is unfair)',
        'my rules are better', 'that\'s silly', 'don\'t listen to them'
    ],
    'loyalty_conflicts': [
        r'(you have to (choose|decide)|choose (mum|dad))',
        r'(if you love|you should help) me',
        r'(can\'t love us both|one or the other)',
        'you have to pick sides', 'you\'re on my side',
        'how could you choose them', 'you\'ve betrayed me'
    ]
}

def detect_alienation_patterns(
    df: pd.DataFrame,
    parent_a: str,
    parent_b: str,
    keywords_dict: Dict = ALIENATION_MARKERS
) -> List[Dict]:
    """
    Identify parental alienation patterns.

    Detects messages containing denigration, interference, information withholding,
    undermining, or loyalty conflicts.

    Args:
        df: DataFrame with columns: message_id, timestamp, sender, text
        parent_a: Name/ID of parent A
        parent_b: Name/ID of parent B
        keywords_dict: Alienation markers dictionary

    Returns:
        List of flagged messages with category and context
    """

    flagged = []

    for idx, row in df.iterrows():
        text = row.get('text', '')
        if not isinstance(text, str):
            continue

        text_lower = text.lower()
        matched_categories = []

        for category, patterns in keywords_dict.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        matched_categories.append(category)
                        break
                except re.error:
                    if pattern in text_lower:
                        matched_categories.append(category)
                        break

        if matched_categories:
            flagged.append({
                'message_id': row.get('message_id'),
                'timestamp': row.get('timestamp'),
                'sender': row.get('sender'),
                'text': text,
                'alienation_categories': matched_categories,
                'target_parent': parent_b if row.get('sender') == parent_a else parent_a,
            })

    return sorted(flagged, key=lambda x: x['timestamp'])
```

### 15.4 LLM Classification Extension for Family Law

Extends the LLM-based message classification (§9) with Australian family law context and child protection indicators.

```python
# Extended legal issue tags (add to base LEGAL_ISSUE_TAGS from §9)
FAMILY_LAW_LEGAL_TAGS = [
    'child_safety_concern',
    'coercive_control_pattern',
    'parental_alienation',
    'substance_abuse_incident',
    'domestic_violence_incident',
    'breach_of_orders'
]

# Extended LLM classification prompt for family law context
FAMILY_LAW_CLASSIFICATION_PROMPT = """
You are analysing SMS/iMessage messages in an Australian family law context.

Classify each message across the following dimensions:

1. **Core legal relevance** (from §9): threat, admission, impeachment, character, relational context
2. **Family law specifics** (NEW):
   - `child_safety_concern`: Does this message indicate risk to child safety (neglect, exposure, substance abuse, inappropriate care)?
   - `coercive_control_pattern`: Does this message exemplify controlling, monitoring, isolating, threatening, or denigrating behaviour?
   - `parental_alienation`: Does this attempt to undermine the other parent's relationship with children?
   - `substance_abuse_incident`: Reference to alcohol, drugs, or intoxication?
   - `domestic_violence_incident`: Reference to, threat of, or admission of violence?
   - `breach_of_orders`: Apparent breach of court orders, parenting plans, or IVOs?

For each tag present, provide:
- Severity (low/medium/high/critical)
- Specific quote or phrase that triggered the tag
- Context (is this isolated or part of a pattern?)

CRITICAL: All LLM classifications must carry a verification flag. Flag all messages as "REQUIRES_HUMAN_VERIFICATION: true" before providing to legal team.

Context: This is evidence for family law proceedings. Accuracy and consistency are essential.
"""

# JSON Schema extension for family law classification
FAMILY_LAW_MESSAGE_CLASSIFICATION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "message_id": {"type": "string"},
        "base_legal_tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Tags from §9 core classification"
        },
        "family_law_tags": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tag": {"type": "string", "enum": FAMILY_LAW_LEGAL_TAGS},
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "supporting_quote": {"type": "string"},
                    "context": {"type": "string"}
                }
            }
        },
        "requires_human_verification": {
            "type": "boolean",
            "default": True,
            "description": "All family law classifications require human review before use as evidence"
        },
        "verification_notes": {
            "type": "string",
            "description": "Flagging notes for legal review team"
        }
    },
    "required": ["message_id", "requires_human_verification"]
}

def classify_message_family_law(
    text: str,
    message_id: str,
    model: str = "gpt-4",
    api_key: str = None
) -> Dict:
    """
    Classify a message using LLM with family law context.

    All classifications are flagged for human verification before use as evidence.

    Args:
        text: Message text
        message_id: Unique message identifier
        model: LLM model (default: gpt-4)
        api_key: API key for LLM service

    Returns:
        Classification dict with verification flag set
    """

    import openai

    if not api_key:
        raise ValueError("API key required for LLM classification")

    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": FAMILY_LAW_CLASSIFICATION_PROMPT
            },
            {
                "role": "user",
                "content": f"Classify this message:\n\n{text}"
            }
        ],
        temperature=0.2
    )

    # Parse response and structure into schema
    llm_output = response.choices[0].message.content

    classification = {
        "message_id": message_id,
        "base_legal_tags": [],
        "family_law_tags": [],
        "requires_human_verification": True,
        "verification_notes": (
            "LLM-generated classification. Must be reviewed by qualified legal professional "
            "before use in evidence or court proceedings."
        ),
        "raw_llm_response": llm_output
    }

    return classification
```

---

**End of §15. Child Protection & Coercive Control Detection.**

Note on usage of these sections: All functions assume pandas DataFrames with appropriately typed and validated input. All machine-generated classifications (LLM-based, in particular) must be tagged with `requires_human_verification: true` and reviewed by a qualified legal professional before being relied upon in evidence or court proceedings. The deterministic pattern matching functions are audit-trail-safe and reproducible; the LLM-based analysis is supplementary and advisory only.

---

## 16. FVRO Analysis — Western Australia

> **This section has been moved to a standalone skill.** All FVRO analysis, court document generation, and procedural guidance is now maintained in the dedicated `wa-fvro` skill.
>
> **To use FVRO analysis**: Load the `wa-fvro` skill directly. It contains the full analysis pipeline (contact initiation, invited contact detection, respondent conduct audit, changed circumstances, misuse detection, cancellation viability assessment, breach mitigation), court document generation (affidavit, annexures, Form 12 guidance), and comprehensive legislative/procedural reference.
>
> The `wa-fvro` skill assumes message data has been normalised through this pipeline's standard ingestion (§3) and participant mapping (§4). Run Stages 1–3 of the SMS pipeline here first, then hand off to `wa-fvro` for FVRO-specific analysis.

**Cross-reference**: `wa-fvro` -> workflow selection, critical legal principles, affidavit drafting, annexure guidance, evidence checklist, case-law verification, and procedure.
