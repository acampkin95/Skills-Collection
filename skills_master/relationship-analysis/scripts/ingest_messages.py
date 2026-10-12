#!/usr/bin/env python3
"""
Universal message ingestion script for relationship analysis.
Auto-detects format and creates optimized SQLite time-series database.
"""

import sqlite3
import csv
import re
import sys
import os
from datetime import datetime
from dateutil import parser as dateparser
from typing import Dict, Any, Optional

def detect_format(file_path: str) -> str:
    """Auto-detect input format from file structure."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return 'email_pdf'

    if ext in ['.csv', '.txt']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_lines = [f.readline() for _ in range(5)]
            content = ''.join(first_lines).lower()

            # iMessage CSV format
            if 'type' in content and 'sender' in content and 'text' in content:
                return 'imessage_csv'

            # WhatsApp format
            if re.search(r'\[\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}', content):
                return 'whatsapp'

            # Generic CSV with timestamp/sender/text
            if 'timestamp' in content or 'date' in content:
                return 'generic_csv'

    return 'unknown'

def create_database(db_path: str) -> sqlite3.Connection:
    """Create optimized SQLite database schema."""
    conn: sqlite3.Connection = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript('''
        -- Main messages table with time-series optimization
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_type TEXT,
            sender TEXT,
            sender_number TEXT,
            recipient TEXT,
            service TEXT,
            text TEXT,
            has_attachment INTEGER DEFAULT 0,
            attachment_info TEXT,

            -- Timestamp fields
            timestamp TEXT,
            unix_timestamp INTEGER,
            date_only TEXT,

            -- Time series fields for granular queries
            year INTEGER,
            month INTEGER,
            day INTEGER,
            hour INTEGER,
            minute INTEGER,
            weekday INTEGER,
            week_of_year INTEGER,
            time_of_day TEXT,
            is_weekend INTEGER,

            -- Pre-computed analysis fields
            word_count INTEGER,
            char_count INTEGER,
            has_emoji INTEGER DEFAULT 0,
            has_question INTEGER DEFAULT 0,
            has_exclamation INTEGER DEFAULT 0,
            has_love_words INTEGER DEFAULT 0,
            has_negative INTEGER DEFAULT 0,
            has_affection INTEGER DEFAULT 0,
            has_apology INTEGER DEFAULT 0,
            has_gratitude INTEGER DEFAULT 0,
            is_short INTEGER DEFAULT 0,
            is_long INTEGER DEFAULT 0,

            -- Conversation tracking
            response_time_seconds INTEGER,
            is_conversation_starter INTEGER DEFAULT 0,
            conversation_id INTEGER
        );

        -- Time-series indexes for fast range queries
        CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(unix_timestamp);
        CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date_only);
        CREATE INDEX IF NOT EXISTS idx_messages_year_month ON messages(year, month);
        CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender);
        CREATE INDEX IF NOT EXISTS idx_messages_hour ON messages(hour);
        CREATE INDEX IF NOT EXISTS idx_messages_weekday ON messages(weekday);
        CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);

        -- FTS5 full-text search
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
            text,
            content='messages',
            content_rowid='id',
            tokenize='porter unicode61'
        );

        -- Triggers to keep FTS in sync
        CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
            INSERT INTO messages_fts(rowid, text) VALUES (new.id, new.text);
        END;

        CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
            INSERT INTO messages_fts(messages_fts, rowid, text) VALUES('delete', old.id, old.text);
        END;

        CREATE TRIGGER IF NOT EXISTS messages_au AFTER UPDATE ON messages BEGIN
            INSERT INTO messages_fts(messages_fts, rowid, text) VALUES('delete', old.id, old.text);
            INSERT INTO messages_fts(rowid, text) VALUES (new.id, new.text);
        END;

        -- Aggregation views
        CREATE VIEW IF NOT EXISTS messages_by_month AS
        SELECT year, month, sender,
               COUNT(*) as message_count,
               SUM(word_count) as total_words,
               SUM(has_love_words) as love_count,
               SUM(has_negative) as negative_count,
               SUM(has_apology) as apology_count
        FROM messages
        GROUP BY year, month, sender;

        CREATE VIEW IF NOT EXISTS messages_by_day AS
        SELECT date_only, sender, COUNT(*) as message_count
        FROM messages GROUP BY date_only, sender;

        CREATE VIEW IF NOT EXISTS messages_by_hour AS
        SELECT hour, sender, COUNT(*) as message_count
        FROM messages GROUP BY hour, sender;
    ''')

    conn.commit()
    return conn

def analyze_message(text: str) -> Dict[str, int]:
    """Pre-compute analysis markers for a message."""
    if not text:
        return {}

    text_lower = text.lower()
    words = text.split()

    # Emoji detection
    emoji_pattern = re.compile(r'[\U0001F300-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U0001F600-\U0001F64F]')

    # Love/positive words
    love_pattern = re.compile(r'\b(love|adore|miss|cherish|treasure|heart|darling|sweetheart|babe|baby|honey)\b', re.I)

    # Negative words
    negative_pattern = re.compile(r'\b(hate|angry|upset|frustrated|annoyed|disappointed|hurt|sad|mad|furious|disgusted)\b', re.I)

    # Affection words
    affection_pattern = re.compile(r'\b(hug|kiss|cuddle|snuggle|hold|embrace|xoxo|mwah)\b', re.I)

    # Apology words
    apology_pattern = re.compile(r'\b(sorry|apologize|apologies|forgive|my bad|my fault)\b', re.I)

    # Gratitude words
    gratitude_pattern = re.compile(r'\b(thank|thanks|grateful|appreciate|thx)\b', re.I)

    return {
        'word_count': len(words),
        'char_count': len(text),
        'has_emoji': 1 if emoji_pattern.search(text) else 0,
        'has_question': 1 if '?' in text else 0,
        'has_exclamation': 1 if '!' in text else 0,
        'has_love_words': 1 if love_pattern.search(text) else 0,
        'has_negative': 1 if negative_pattern.search(text) else 0,
        'has_affection': 1 if affection_pattern.search(text) else 0,
        'has_apology': 1 if apology_pattern.search(text) else 0,
        'has_gratitude': 1 if gratitude_pattern.search(text) else 0,
        'is_short': 1 if len(words) <= 3 else 0,
        'is_long': 1 if len(words) > 50 else 0
    }

def parse_timestamp(date_str: str, time_str: Optional[str] = None) -> Optional[datetime]:
    """Parse various timestamp formats."""
    try:
        if time_str:
            combined = f"{date_str} {time_str}"
        else:
            combined = date_str

        dt = dateparser.parse(combined)
        if dt:
            return dt
    except:
        pass
    return None

def get_time_of_day(hour: int) -> str:
    """Categorize hour into time of day."""
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'

def process_imessage_csv(file_path: str, conn: sqlite3.Connection) -> int:
    """Process iMessage CSV export."""
    cursor = conn.cursor()

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)

        last_sender = None
        last_timestamp = None
        conversation_id = 0
        count = 0

        for row in reader:
            # Extract fields (handle various column naming)
            msg_type = row.get('Type', row.get('type', ''))
            date_str = row.get('Date', row.get('date', ''))
            time_str = row.get('Time', row.get('time', ''))
            sender = row.get('Sender Name', row.get('Sender', row.get('sender', '')))
            sender_number = row.get('Sender Number', row.get('sender_number', ''))
            recipient = row.get('Recipients', row.get('recipient', ''))
            text = row.get('Text', row.get('text', row.get('Message', '')))
            attachment = row.get('Attachment', '')
            service = row.get('Service', 'iMessage')

            # Parse timestamp
            dt = parse_timestamp(date_str, time_str)
            if not dt:
                continue

            # Calculate response time and conversation
            response_time = None
            is_starter = 0

            if last_timestamp and last_sender:
                time_diff = (dt - last_timestamp).total_seconds()
                if time_diff > 14400:  # 4 hours = new conversation
                    conversation_id += 1
                    is_starter = 1
                elif sender != last_sender:
                    response_time = int(time_diff)
            else:
                is_starter = 1

            # Analyze message
            analysis = analyze_message(text)

            # Insert
            cursor.execute('''
                INSERT INTO messages (
                    message_type, sender, sender_number, recipient, service, text,
                    has_attachment, attachment_info, timestamp, unix_timestamp, date_only,
                    year, month, day, hour, minute, weekday, week_of_year, time_of_day, is_weekend,
                    word_count, char_count, has_emoji, has_question, has_exclamation,
                    has_love_words, has_negative, has_affection, has_apology, has_gratitude,
                    is_short, is_long, response_time_seconds, is_conversation_starter, conversation_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                msg_type, sender, sender_number, recipient, service, text,
                1 if attachment else 0, attachment,
                dt.isoformat(), int(dt.timestamp()), dt.strftime('%Y-%m-%d'),
                dt.year, dt.month, dt.day, dt.hour, dt.minute,
                dt.weekday(), dt.isocalendar()[1], get_time_of_day(dt.hour),
                1 if dt.weekday() >= 5 else 0,
                analysis.get('word_count', 0), analysis.get('char_count', 0),
                analysis.get('has_emoji', 0), analysis.get('has_question', 0),
                analysis.get('has_exclamation', 0), analysis.get('has_love_words', 0),
                analysis.get('has_negative', 0), analysis.get('has_affection', 0),
                analysis.get('has_apology', 0), analysis.get('has_gratitude', 0),
                analysis.get('is_short', 0), analysis.get('is_long', 0),
                response_time, is_starter, conversation_id
            ))

            last_sender = sender
            last_timestamp = dt
            count += 1

            if count % 1000 == 0:
                print(f"  Processed {count:,} messages...")
                conn.commit()

        conn.commit()
        return count

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python ingest_messages.py <input_file> <output.db>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_db = sys.argv[2]

    print(f"Ingesting: {input_file}")
    print(f"Output: {output_db}")

    # Detect format
    fmt = detect_format(input_file)
    print(f"Detected format: {fmt}")

    # Create database
    conn = create_database(output_db)

    # Process based on format
    if fmt == 'imessage_csv':
        count = process_imessage_csv(input_file, conn)
    else:
        print(f"Format '{fmt}' not yet implemented. Using iMessage CSV parser.")
        count = process_imessage_csv(input_file, conn)

    print(f"\n✓ Ingested {count:,} messages")

    # Print summary
    cursor = conn.cursor()
    cursor.execute("SELECT sender, COUNT(*) FROM messages GROUP BY sender")
    print("\nBy sender:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,}")

    cursor.execute("SELECT MIN(date_only), MAX(date_only) FROM messages")
    row = cursor.fetchone()
    print(f"\nDate range: {row[0]} to {row[1]}")

    conn.close()

if __name__ == '__main__':
    main()
