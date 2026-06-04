# Database Schema Reference

## Messages Table

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Core fields
    message_type TEXT,           -- 'Incoming'/'Outgoing'
    sender TEXT,                 -- Sender name
    sender_number TEXT,          -- Phone number
    recipient TEXT,              -- Recipient name/number
    service TEXT,                -- 'iMessage'/'SMS'
    text TEXT,                   -- Message content
    has_attachment INTEGER,      -- 0/1
    attachment_info TEXT,        -- Attachment filename

    -- Timestamp fields
    timestamp TEXT,              -- ISO format
    unix_timestamp INTEGER,      -- Epoch seconds
    date_only TEXT,              -- 'YYYY-MM-DD'

    -- Time series (for granular queries)
    year INTEGER,
    month INTEGER,
    day INTEGER,
    hour INTEGER,
    minute INTEGER,
    weekday INTEGER,             -- 0=Monday, 6=Sunday
    week_of_year INTEGER,
    time_of_day TEXT,            -- 'morning'/'afternoon'/'evening'/'night'
    is_weekend INTEGER,          -- 0/1

    -- Pre-computed analysis
    word_count INTEGER,
    char_count INTEGER,
    has_emoji INTEGER,
    has_question INTEGER,
    has_exclamation INTEGER,
    has_love_words INTEGER,
    has_negative INTEGER,
    has_affection INTEGER,
    has_apology INTEGER,
    has_gratitude INTEGER,
    is_short INTEGER,            -- ≤3 words
    is_long INTEGER,             -- >50 words

    -- NLP (added by analyze_all.py)
    sentiment_polarity REAL,     -- -1.0 to 1.0
    sentiment_subjectivity REAL, -- 0.0 to 1.0

    -- Attachment markers (added by analyze_all.py)
    attachment_anxious INTEGER,
    attachment_avoidant INTEGER,
    attachment_secure INTEGER,
    attachment_controlling INTEGER,
    is_conflict INTEGER,

    -- Conversation tracking
    response_time_seconds INTEGER,
    is_conversation_starter INTEGER,
    conversation_id INTEGER
);
```

## Indexes

```sql
CREATE INDEX idx_messages_timestamp ON messages(unix_timestamp);
CREATE INDEX idx_messages_date ON messages(date_only);
CREATE INDEX idx_messages_year_month ON messages(year, month);
CREATE INDEX idx_messages_sender ON messages(sender);
CREATE INDEX idx_messages_hour ON messages(hour);
CREATE INDEX idx_messages_weekday ON messages(weekday);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
```

## Full-Text Search

```sql
CREATE VIRTUAL TABLE messages_fts USING fts5(
    text,
    content='messages',
    content_rowid='id',
    tokenize='porter unicode61'
);
```

### FTS Usage

```sql
-- Basic search
SELECT * FROM messages WHERE id IN (
    SELECT rowid FROM messages_fts WHERE messages_fts MATCH 'love'
);

-- Phrase search
SELECT * FROM messages WHERE id IN (
    SELECT rowid FROM messages_fts WHERE messages_fts MATCH '"miss you"'
);

-- Boolean search
SELECT * FROM messages WHERE id IN (
    SELECT rowid FROM messages_fts WHERE messages_fts MATCH 'love AND miss'
);
```

## Analysis Results Table

```sql
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_type TEXT,          -- 'sentiment'/'attachment'/'love_patterns'/etc
    analysis_date TEXT,          -- ISO timestamp
    results_json TEXT            -- JSON blob
);
```

## Pre-built Views

```sql
-- Monthly aggregation
CREATE VIEW messages_by_month AS
SELECT year, month, sender,
       COUNT(*) as message_count,
       SUM(word_count) as total_words,
       SUM(has_love_words) as love_count,
       SUM(has_negative) as negative_count,
       SUM(has_apology) as apology_count
FROM messages
GROUP BY year, month, sender;

-- Daily aggregation
CREATE VIEW messages_by_day AS
SELECT date_only, sender, COUNT(*) as message_count
FROM messages GROUP BY date_only, sender;

-- Hourly distribution
CREATE VIEW messages_by_hour AS
SELECT hour, sender, COUNT(*) as message_count
FROM messages GROUP BY hour, sender;
```

## Common Queries

### Monthly Statistics
```sql
SELECT year, month, sender,
       COUNT(*) as msgs,
       SUM(word_count) as words,
       AVG(sentiment_polarity) as sentiment
FROM messages
GROUP BY year, month, sender
ORDER BY year, month;
```

### Love:Negative Ratio by Month
```sql
SELECT year, month,
       SUM(has_love_words) as love,
       SUM(has_negative) as negative,
       CAST(SUM(has_love_words) AS REAL) / NULLIF(SUM(has_negative), 0) as ratio
FROM messages
GROUP BY year, month;
```

### High-Conflict Days
```sql
SELECT date_only, COUNT(*) as conflict_count
FROM messages
WHERE is_conflict = 1
GROUP BY date_only
HAVING COUNT(*) >= 5
ORDER BY conflict_count DESC;
```

### Response Time Analysis
```sql
SELECT sender,
       AVG(response_time_seconds) / 60 as avg_minutes,
       MIN(response_time_seconds) / 60 as min_minutes,
       MAX(response_time_seconds) / 60 as max_minutes
FROM messages
WHERE response_time_seconds IS NOT NULL
  AND response_time_seconds < 86400
GROUP BY sender;
```
