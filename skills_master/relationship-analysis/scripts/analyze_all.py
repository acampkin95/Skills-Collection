#!/usr/bin/env python3
"""
Full NLP + psychology analysis pipeline for relationship messages.
Runs all analyses and stores results back in the database.
"""

import sqlite3
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    print("Warning: textblob not installed. Sentiment analysis will be skipped.")
    print("Install in a virtual environment with: pip install textblob")

def run_sentiment_analysis(conn: sqlite3.Connection) -> Dict[str, Dict[str, Dict[str, float]]]:
    """Run TextBlob sentiment analysis on all messages."""
    if not HAS_TEXTBLOB:
        return {}

    cursor = conn.cursor()

    # Add sentiment columns if missing
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN sentiment_polarity REAL")
        cursor.execute("ALTER TABLE messages ADD COLUMN sentiment_subjectivity REAL")
        conn.commit()
    except:
        pass

    # Process messages
    cursor.execute("SELECT id, text FROM messages WHERE text IS NOT NULL AND text != ''")
    rows = cursor.fetchall()

    print(f"  Analyzing sentiment for {len(rows):,} messages...")

    for i, (msg_id, text) in enumerate(rows):
        try:
            blob = TextBlob(text)
            cursor.execute(
                "UPDATE messages SET sentiment_polarity = ?, sentiment_subjectivity = ? WHERE id = ?",
                (blob.sentiment.polarity, blob.sentiment.subjectivity, msg_id)
            )
        except:
            pass

        if (i + 1) % 5000 == 0:
            print(f"    Processed {i+1:,} messages...")
            conn.commit()

    conn.commit()

    # Aggregate by month
    cursor.execute("""
        SELECT year, month, sender,
               AVG(sentiment_polarity) as avg_polarity,
               AVG(sentiment_subjectivity) as avg_subjectivity
        FROM messages
        WHERE sentiment_polarity IS NOT NULL
        GROUP BY year, month, sender
        ORDER BY year, month
    """)

    monthly_sentiment = {}
    for row in cursor.fetchall():
        key = f"{row[0]}-{row[1]:02d}"
        if key not in monthly_sentiment:
            monthly_sentiment[key] = {}
        monthly_sentiment[key][row[2]] = {
            'polarity': round(row[3], 3),
            'subjectivity': round(row[4], 3)
        }

    return monthly_sentiment

def detect_attachment_markers(conn: sqlite3.Connection) -> Dict[str, Dict[str, int]]:
    """Detect attachment style markers in messages."""
    cursor = conn.cursor()

    patterns = {
        'anxious': [
            r'\b(please|plz)\b', r'\bsorry\b', r'\bworried\b', r'\bneed you\b',
            r'\bmiss you\b', r"don't leave\b", r'\bpromise me\b', r'\bare you mad\b',
            r'\bdo you still\b', r'\bwhy aren\'t you\b', r'\banswer me\b'
        ],
        'avoidant': [
            r'\bneed space\b', r'\bbusy\b', r'\blater\b', r'\bfine\b',
            r'\bwhatever\b', r'\bidk\b', r'\bnot now\b', r'\bleave me\b',
            r'\balone\b', r'\bback off\b', r'\bchill\b'
        ],
        'secure': [
            r'\bunderstand\b', r'\bappreciate\b', r'\btogether\b', r'\btrust\b',
            r'\bcommunicate\b', r'\bcompromise\b', r'\bsupport\b', r'\bteam\b',
            r'\bpartner\b', r'\bwe can\b'
        ],
        'controlling': [
            r'\byou should\b', r'\byou need to\b', r'\bwhy did you\b',
            r'\bwhere are you\b', r'\bwho are you with\b', r'\bwhy didn\'t you\b',
            r'\byou always\b', r'\byou never\b'
        ]
    }

    # Add marker columns
    for style in patterns.keys():
        try:
            cursor.execute(f"ALTER TABLE messages ADD COLUMN attachment_{style} INTEGER DEFAULT 0")
        except:
            pass
    conn.commit()

    results = defaultdict(lambda: defaultdict(int))

    cursor.execute("SELECT id, text, sender FROM messages WHERE text IS NOT NULL")
    rows = cursor.fetchall()

    print(f"  Detecting attachment markers in {len(rows):,} messages...")

    for msg_id, text, sender in rows:
        text_lower = text.lower()
        for style, style_patterns in patterns.items():
            for pattern in style_patterns:
                if re.search(pattern, text_lower, re.I):
                    cursor.execute(f"UPDATE messages SET attachment_{style} = 1 WHERE id = ?", (msg_id,))
                    results[sender][style] += 1
                    break

    conn.commit()
    return dict(results)

def detect_love_bombing(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Detect love bombing patterns (>3x average affection in a day)."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date_only, sender, SUM(has_love_words + has_affection) as daily_love
        FROM messages
        GROUP BY date_only, sender
        ORDER BY date_only
    """)

    daily_data = defaultdict(lambda: defaultdict(int))
    for date, sender, love in cursor.fetchall():
        daily_data[date][sender] = love

    dates = sorted(daily_data.keys())
    spikes = []
    withdrawals = []

    for sender in set(s for d in daily_data.values() for s in d.keys()):
        sender_values = [daily_data[d].get(sender, 0) for d in dates]

        for i in range(3, len(dates)):
            rolling_avg = sum(sender_values[i-3:i]) / 3
            current = sender_values[i]

            if rolling_avg > 0:
                if current > rolling_avg * 3:
                    spikes.append({
                        'date': dates[i],
                        'sender': sender,
                        'value': current,
                        'avg': round(rolling_avg, 2)
                    })
                elif current < rolling_avg / 3 and rolling_avg > 2:
                    withdrawals.append({
                        'date': dates[i],
                        'sender': sender,
                        'value': current,
                        'avg': round(rolling_avg, 2)
                    })

    # Count intermittent reinforcement cycles
    ir_count = 0
    spike_dates = {s['date'] for s in spikes}
    for w in withdrawals:
        # Check if withdrawal within 7 days of a spike
        w_date = datetime.strptime(w['date'], '%Y-%m-%d')
        for s_date_str in spike_dates:
            s_date = datetime.strptime(s_date_str, '%Y-%m-%d')
            if 0 < (w_date - s_date).days <= 7:
                ir_count += 1
                break

    return {
        'spikes': spikes,
        'withdrawals': withdrawals,
        'intermittent_reinforcement_count': ir_count
    }

def detect_conflicts(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Detect high-conflict days and messages."""
    cursor = conn.cursor()

    conflict_patterns = [
        r'\byou always\b', r'\byou never\b', r'\bi\'m done\b', r'\bhurt\b',
        r'\bangry\b', r'\bfurious\b', r'\bhate\b', r'\bsick of\b',
        r'\btired of\b', r'\bcan\'t believe\b', r'\bwhat the\b', r'\bwtf\b'
    ]

    # Add conflict column
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN is_conflict INTEGER DEFAULT 0")
        conn.commit()
    except:
        pass

    cursor.execute("SELECT id, text, date_only FROM messages WHERE text IS NOT NULL")
    rows = cursor.fetchall()

    conflict_days = defaultdict(int)

    for msg_id, text, date in rows:
        text_lower = text.lower()
        for pattern in conflict_patterns:
            if re.search(pattern, text_lower):
                cursor.execute("UPDATE messages SET is_conflict = 1 WHERE id = ?", (msg_id,))
                conflict_days[date] += 1
                break

    conn.commit()

    # Get high-conflict days (>5 conflict messages)
    high_conflict = [{'date': d, 'count': c} for d, c in conflict_days.items() if c >= 5]
    high_conflict.sort(key=lambda x: x['count'], reverse=True)

    return {
        'high_conflict_days': high_conflict[:50],
        'total_conflict_days': len([c for c in conflict_days.values() if c >= 3])
    }

def extract_third_parties(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Extract third-party names and relationship terms."""
    cursor = conn.cursor()

    # Context patterns for extracting names
    name_patterns = [
        r'\bwith ([A-Z][a-z]{2,12})\b',
        r'\btold ([A-Z][a-z]{2,12})\b',
        r'\b([A-Z][a-z]{2,12})\'s\b',
        r'\bmy friend ([A-Z][a-z]{2,12})\b',
        r'\bsaw ([A-Z][a-z]{2,12})\b',
        r'\bfrom ([A-Z][a-z]{2,12})\b',
        r'\bto ([A-Z][a-z]{2,12})\b',
        r'\b([A-Z][a-z]{2,12}) said\b',
        r'\b([A-Z][a-z]{2,12}) and I\b'
    ]

    # Exclusion list
    exclude = {
        'But', 'The', 'That', 'This', 'What', 'When', 'Where', 'Why', 'How',
        'Just', 'Like', 'Love', 'Loved', 'Have', 'Has', 'Had', 'Was', 'Were',
        'Yes', 'Yeah', 'Yea', 'Nope', 'Sure', 'Maybe', 'Good', 'Great', 'Nice',
        'Thanks', 'Thank', 'Sorry', 'Please', 'Hello', 'Hey', 'Morning', 'Night',
        'Today', 'Tomorrow', 'Yesterday', 'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday', 'January', 'February',
        'March', 'April', 'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December', 'Also', 'Well', 'Still', 'Even',
        'Much', 'Very', 'Really', 'Actually', 'Probably', 'Definitely',
        'Going', 'Coming', 'Getting', 'Being', 'Doing', 'Having', 'Making',
        'Thinking', 'Feeling', 'Looking', 'Waiting', 'Working', 'Talking'
    }

    # Relationship terms
    rel_terms = {
        'mum': 0, 'mom': 0, 'mother': 0, 'dad': 0, 'father': 0,
        'brother': 0, 'sister': 0, 'friend': 0, 'friends': 0,
        'therapist': 0, 'counselor': 0, 'doctor': 0, 'boss': 0,
        'ex': 0, 'coworker': 0, 'colleague': 0
    }

    cursor.execute("SELECT text FROM messages WHERE text IS NOT NULL")
    rows = cursor.fetchall()

    name_counts = defaultdict(int)

    for (text,) in rows:
        text_lower = text.lower()

        # Count relationship terms
        for term in rel_terms.keys():
            if re.search(rf'\b{term}\b', text_lower):
                rel_terms[term] += 1

        # Extract names
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            for name in matches:
                if name not in exclude and len(name) >= 3:
                    name_counts[name] += 1

    # Filter to significant names (mentioned 5+ times)
    significant_names = {k: v for k, v in name_counts.items() if v >= 5}
    top_names = sorted(significant_names.items(), key=lambda x: x[1], reverse=True)[:20]

    return {
        'third_parties': [{'name': n, 'count': c} for n, c in top_names],
        'relationship_terms': {k: v for k, v in rel_terms.items() if v > 0}
    }

def analyze_communication_dynamics(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Analyze double-texting, flooding, response times."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sender, unix_timestamp, conversation_id
        FROM messages
        ORDER BY unix_timestamp
    """)
    rows = cursor.fetchall()

    double_texts = defaultdict(int)
    triple_floods = defaultdict(int)

    consecutive = defaultdict(int)
    last_sender = None

    for sender, ts, conv_id in rows:
        if sender == last_sender:
            consecutive[sender] += 1
        else:
            if consecutive.get(last_sender, 0) >= 2:
                double_texts[last_sender] += 1
            if consecutive.get(last_sender, 0) >= 3:
                triple_floods[last_sender] += 1
            consecutive = defaultdict(int)
            consecutive[sender] = 1
        last_sender = sender

    # Response time analysis
    cursor.execute("""
        SELECT sender, AVG(response_time_seconds), COUNT(*)
        FROM messages
        WHERE response_time_seconds IS NOT NULL AND response_time_seconds < 86400
        GROUP BY sender
    """)

    response_times = {}
    for sender, avg_rt, count in cursor.fetchall():
        response_times[sender] = {
            'avg_seconds': round(avg_rt, 1),
            'avg_minutes': round(avg_rt / 60, 1),
            'count': count
        }

    # Initiation analysis
    cursor.execute("""
        SELECT sender, COUNT(*)
        FROM messages
        WHERE is_conversation_starter = 1
        GROUP BY sender
    """)

    initiations = {row[0]: row[1] for row in cursor.fetchall()}

    return {
        'double_texts': dict(double_texts),
        'triple_floods': dict(triple_floods),
        'response_times': response_times,
        'conversation_initiations': initiations
    }

def create_analysis_tables(conn: sqlite3.Connection) -> None:
    """Create analysis results tables."""
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_type TEXT,
            analysis_date TEXT,
            results_json TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis_results(analysis_type);
    ''')

    conn.commit()

def save_analysis(conn: sqlite3.Connection, analysis_type: str, results: Dict[str, Any]) -> None:
    """Save analysis results to database."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO analysis_results (analysis_type, analysis_date, results_json) VALUES (?, ?, ?)",
        (analysis_type, datetime.now().isoformat(), json.dumps(results))
    )
    conn.commit()

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python analyze_all.py <database.db>")
        sys.exit(1)

    db_path: str = sys.argv[1]
    print(f"Analyzing: {db_path}")

    conn = sqlite3.connect(db_path)
    create_analysis_tables(conn)

    # Run all analyses
    print("\n1. Sentiment Analysis...")
    sentiment = run_sentiment_analysis(conn)
    save_analysis(conn, 'sentiment', sentiment)
    print(f"   ✓ Analyzed {len(sentiment)} months")

    print("\n2. Attachment Style Detection...")
    attachment = detect_attachment_markers(conn)
    save_analysis(conn, 'attachment', attachment)
    print(f"   ✓ Detected markers for {len(attachment)} senders")

    print("\n3. Love Bombing/Withdrawal Detection...")
    love_patterns = detect_love_bombing(conn)
    save_analysis(conn, 'love_patterns', love_patterns)
    print(f"   ✓ Found {len(love_patterns['spikes'])} spikes, {len(love_patterns['withdrawals'])} withdrawals")
    print(f"   ✓ Intermittent reinforcement cycles: {love_patterns['intermittent_reinforcement_count']}")

    print("\n4. Conflict Detection...")
    conflicts = detect_conflicts(conn)
    save_analysis(conn, 'conflicts', conflicts)
    print(f"   ✓ High-conflict days: {len(conflicts['high_conflict_days'])}")

    print("\n5. Third-Party Extraction...")
    third_parties = extract_third_parties(conn)
    save_analysis(conn, 'third_parties', third_parties)
    print(f"   ✓ Found {len(third_parties['third_parties'])} third parties")

    print("\n6. Communication Dynamics...")
    dynamics = analyze_communication_dynamics(conn)
    save_analysis(conn, 'dynamics', dynamics)
    print(f"   ✓ Analyzed response times and patterns")

    conn.close()
    print("\n✓ Analysis complete!")

if __name__ == '__main__':
    main()
