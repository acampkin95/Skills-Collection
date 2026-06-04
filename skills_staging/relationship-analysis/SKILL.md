---
name: relationship-analysis
description: Relationship communication analysis from SMS/iMessage/chat exports. Builds time-series metrics, response patterns, sentiment, and visual reports.
version: 2.0.0
reviewed: "2026-06-04"
---

# Relationship Communication Analysis

Use this skill to analyze relationship communication patterns from message exports. Ingest iMessage/SMS data, build time-series databases, extract metrics, and generate observations about communication dynamics.

## Source Quality Protocol

Treat outputs as pattern analysis, not psychological diagnosis, legal conclusions, or proof of misconduct. Preserve source message exports, keep row/message IDs in every derived output, and distinguish observed communication behaviour from interpretation. For court-facing or legal use, hand off to `csv-legal-analysis`, `affidavit-court-preparation`, or `legal-matter-ops` so evidence integrity, admissibility, and source-citation checks are applied.

## Output Rules

- Say "messages show" or "the dataset indicates"; do not diagnose personality, intent, abuse, alienation, or coercion from metrics alone.
- Preserve raw exports and work from copies.
- Keep participant mapping, timestamp timezone, source file, and message IDs in every derived table.
- Flag gaps such as deleted messages, partial exports, timezone uncertainty, duplicate threads, or missing attachments.
- Label sentiment/topic outputs as model-assisted indicators requiring human review.

## Workflow Overview

1. **Export messages** from phone (iMessage/SMS backup)
2. **Parse and ingest** into SQLite database
3. **Analyze patterns** (frequency, sentiment, topics)
4. **Generate reports** with visualizations and metrics

---

## Data Schema

### Messages Table

```sql
CREATE TABLE messages (
  id INTEGER PRIMARY KEY,
  timestamp DATETIME NOT NULL,
  sender TEXT NOT NULL,
  recipient TEXT NOT NULL,
  message_text TEXT,
  message_length INTEGER,
  sentiment_score REAL,
  is_emoji_only BOOLEAN,
  contains_links BOOLEAN,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_timestamp (timestamp),
  INDEX idx_sender_recipient (sender, recipient)
);
```

### Communication Metrics Table

```sql
CREATE TABLE daily_metrics (
  date DATE NOT NULL,
  sender TEXT NOT NULL,
  message_count INTEGER,
  avg_message_length REAL,
  avg_sentiment REAL,
  response_time_avg REAL,
  PRIMARY KEY (date, sender),
  FOREIGN KEY (sender) REFERENCES contacts(name)
);
```

---

## Message Ingestion Pipeline

### Parse iMessage Export

```python
import sqlite3
from datetime import datetime
import re

def ingest_imessage_export(export_file, db_path):
    """Ingest iMessage CSV/JSON export into database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    messages = parse_export(export_file)

    for msg in messages:
        cursor.execute('''
            INSERT INTO messages (
                timestamp, sender, recipient, message_text,
                message_length, is_emoji_only, contains_links
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            msg['timestamp'],
            msg['sender'],
            msg['recipient'],
            msg['text'],
            len(msg['text']),
            is_emoji_only(msg['text']),
            bool(re.search(r'http[s]?://', msg['text']))
        ))

    conn.commit()
    conn.close()

def is_emoji_only(text):
    """Check if message contains only emojis."""
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F9FF"
        "\U0001F600-\U0001F64F"
        "\U0001F900-\U0001F9FF"
        "]+", flags=re.UNICODE
    )
    return bool(emoji_pattern.match(text.strip())) and len(text.strip()) > 0
```

---

## Analysis Patterns

### Communication Frequency

```python
def analyze_frequency(db_path, days=30):
    """Analyze message frequency over time."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as message_count,
            AVG(message_length) as avg_length
        FROM messages
        WHERE timestamp >= datetime('now', ? || ' days')
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''', (-days,))

    return cursor.fetchall()
```

### Response Time Analysis

```python
def analyze_response_times(db_path):
    """Calculate average response time between participants."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            m1.sender,
            m1.recipient,
            AVG(CAST((m2.timestamp - m1.timestamp) AS REAL)) as response_time_seconds
        FROM messages m1
        JOIN messages m2 ON
            m1.sender = m2.recipient AND
            m1.recipient = m2.sender AND
            m2.timestamp > m1.timestamp AND
            m2.timestamp < datetime(m1.timestamp, '+1 hour')
        GROUP BY m1.sender, m1.recipient
    ''')

    return cursor.fetchall()
```

### Sentiment Trend Analysis

```python
from textblob import TextBlob

def add_sentiment_scores(db_path):
    """Calculate sentiment for all messages."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id, message_text FROM messages WHERE sentiment_score IS NULL')
    messages = cursor.fetchall()

    for msg_id, text in messages:
        if text:
            sentiment = TextBlob(text).sentiment.polarity
            cursor.execute('UPDATE messages SET sentiment_score = ? WHERE id = ?',
                         (sentiment, msg_id))

    conn.commit()
    conn.close()
```

---

## Report Generation

### Summary Statistics

```python
def generate_summary_report(db_path):
    """Generate comprehensive communication summary."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM messages')
    total_messages = cursor.fetchone()[0]

    cursor.execute('SELECT AVG(message_length) FROM messages')
    avg_length = cursor.fetchone()[0]

    cursor.execute('SELECT AVG(sentiment_score) FROM messages WHERE sentiment_score IS NOT NULL')
    avg_sentiment = cursor.fetchone()[0]

    return {
        'total_messages': total_messages,
        'avg_message_length': avg_length,
        'avg_sentiment': avg_sentiment,
    }
```

---

## Best Practices

1. **Privacy**: Never share raw message data externally
2. **Normalization**: Clean phone numbers, names for consistency
3. **Timezone handling**: Normalize timestamps to UTC
4. **Backup database**: Regularly backup analysis database
5. **Incremental updates**: Design ingestion for new messages only

## Common Mistakes

- Treating sentiment scores as fact rather than weak indicators.
- Ignoring timezone and daylight-saving conversions.
- Combining participants before confirming phone numbers, Apple IDs, and aliases.
- Reporting "response time" without excluding sleep, work, or no-reply periods.
- Using partial exports without warning that conclusions may be incomplete.

## Validation

After editing this skill or its references, run:

```bash
docker compose -f compose.skills.yml run --rm skills-validator
```

Fallback:

```bash
uv run --project .maintenance/Skills-Framework-Reference skills-ref validate relationship-analysis
```

---

## Resources

- **TextBlob**: Sentiment analysis library
- **SQLite**: Lightweight database for analysis
- **Pandas**: Data manipulation and aggregation
