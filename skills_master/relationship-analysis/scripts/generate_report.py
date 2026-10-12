#!/usr/bin/env python3
"""
Generate interactive HTML report from analyzed relationship database.
Creates comprehensive multi-section report with Chart.js and D3.js visualizations.
"""

import sqlite3
import json
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, Any, Optional

def get_base_stats(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Get basic message statistics."""
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), SUM(word_count), MIN(date_only), MAX(date_only) FROM messages")
    total, words, min_date, max_date = cursor.fetchone()

    cursor.execute("SELECT sender, COUNT(*), SUM(word_count) FROM messages GROUP BY sender")
    by_sender = {row[0]: {'messages': row[1], 'words': row[2]} for row in cursor.fetchall()}

    return {
        'total_messages': total,
        'total_words': words or 0,
        'date_range': {'start': min_date, 'end': max_date},
        'by_sender': by_sender
    }

def get_monthly_data(conn: sqlite3.Connection) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Get monthly aggregated data."""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT year, month, sender, COUNT(*), SUM(word_count),
               SUM(has_love_words), SUM(has_negative), SUM(has_apology),
               AVG(sentiment_polarity), AVG(sentiment_subjectivity)
        FROM messages
        GROUP BY year, month, sender
        ORDER BY year, month
    """)

    monthly = defaultdict(lambda: defaultdict(dict))
    for row in cursor.fetchall():
        key = f"{row[0]}-{row[1]:02d}"
        monthly[key][row[2]] = {
            'messages': row[3],
            'words': row[4],
            'love': row[5] or 0,
            'negative': row[6] or 0,
            'apology': row[7] or 0,
            'sentiment': round(row[8], 3) if row[8] else 0,
            'subjectivity': round(row[9], 3) if row[9] else 0
        }

    return dict(monthly)

def get_daily_data(conn: sqlite3.Connection) -> Dict[str, Dict[str, int]]:
    """Get daily message counts."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date_only, sender, COUNT(*)
        FROM messages
        GROUP BY date_only, sender
        ORDER BY date_only
    """)

    daily = defaultdict(dict)
    for date, sender, count in cursor.fetchall():
        daily[date][sender] = count

    return dict(daily)

def get_hourly_data(conn: sqlite3.Connection) -> Dict[int, Dict[str, int]]:
    """Get hourly distribution."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hour, sender, COUNT(*)
        FROM messages
        GROUP BY hour, sender
    """)

    hourly = defaultdict(dict)
    for hour, sender, count in cursor.fetchall():
        hourly[hour][sender] = count

    return dict(hourly)

def get_analysis_results(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Get stored analysis results."""
    cursor = conn.cursor()

    results: Dict[str, Any] = {}
    cursor.execute("SELECT analysis_type, results_json FROM analysis_results ORDER BY analysis_date DESC")
    for atype, rjson in cursor.fetchall():
        if atype not in results:
            results[atype] = json.loads(rjson)

    return results

def get_attachment_monthly(conn: sqlite3.Connection) -> Dict[str, Dict[str, Dict[str, int]]]:
    """Get attachment markers by month."""
    cursor = conn.cursor()

    styles: List[str] = ['anxious', 'avoidant', 'secure', 'controlling']
    monthly: Any = defaultdict(lambda: defaultdict(dict))

    for style in styles:
        try:
            cursor.execute(f"""
                SELECT year, month, sender, SUM(attachment_{style})
                FROM messages
                GROUP BY year, month, sender
            """)
            for row in cursor.fetchall():
                key = f"{row[0]}-{row[1]:02d}"
                if row[2] not in monthly[key]:
                    monthly[key][row[2]] = {}
                monthly[key][row[2]][style] = row[3] or 0
        except:
            pass

    return dict(monthly)

def generate_html(data: Dict[str, Any]) -> str:
    """Generate the full HTML report."""

    html: str = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relationship Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 40px 20px;
            text-align: center;
            border-bottom: 1px solid #334155;
        }
        h1 { font-size: 2.5rem; margin-bottom: 10px; color: #f8fafc; }
        .subtitle { color: #94a3b8; font-size: 1.1rem; }
        nav {
            background: #1e293b;
            padding: 15px;
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 1px solid #334155;
        }
        nav ul { display: flex; flex-wrap: wrap; gap: 10px; list-style: none; justify-content: center; }
        nav a {
            color: #94a3b8;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.2s;
            font-size: 0.9rem;
        }
        nav a:hover { background: #334155; color: #f8fafc; }
        section {
            background: #1e293b;
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0;
            border: 1px solid #334155;
        }
        h2 {
            color: #f8fafc;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3b82f6;
        }
        .grid { display: grid; gap: 20px; }
        .grid-2 { grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); }
        .grid-3 { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
        .card {
            background: #0f172a;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #334155;
        }
        .card h3 { color: #60a5fa; margin-bottom: 15px; font-size: 1.1rem; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #f8fafc; }
        .stat-label { color: #94a3b8; font-size: 0.9rem; }
        .chart-container { position: relative; height: 300px; }
        .chart-large { height: 400px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { color: #60a5fa; font-weight: 600; }
        .positive { color: #4ade80; }
        .negative { color: #f87171; }
        .warning { color: #fbbf24; }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-blue { background: #1e40af; color: #93c5fd; }
        .badge-green { background: #166534; color: #86efac; }
        .badge-red { background: #991b1b; color: #fca5a5; }
        .badge-yellow { background: #854d0e; color: #fde047; }
        #network { width: 100%; height: 500px; background: #0f172a; border-radius: 8px; }
        .finding {
            background: #0f172a;
            border-left: 4px solid #3b82f6;
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 0 8px 8px 0;
        }
        .finding.critical { border-left-color: #ef4444; }
        .finding.warning { border-left-color: #f59e0b; }
        .finding h4 { color: #f8fafc; margin-bottom: 5px; }
        .finding p { color: #94a3b8; }
    </style>
</head>
<body>
    <header>
        <h1>Relationship Communication Analysis</h1>
        <p class="subtitle">Generated ''' + datetime.now().strftime('%B %d, %Y at %H:%M') + '''</p>
    </header>

    <nav>
        <ul>
            <li><a href="#dashboard">Dashboard</a></li>
            <li><a href="#timeline">Timeline</a></li>
            <li><a href="#sentiment">Sentiment</a></li>
            <li><a href="#attachment">Attachment</a></li>
            <li><a href="#patterns">Patterns</a></li>
            <li><a href="#conflicts">Conflicts</a></li>
            <li><a href="#dynamics">Dynamics</a></li>
            <li><a href="#network">Network</a></li>
            <li><a href="#findings">Findings</a></li>
        </ul>
    </nav>

    <div class="container">
'''

    # Inject data
    html += f'''
    <script>
        const DATA = {json.dumps(data, default=str)};
    </script>
'''

    # Dashboard section
    stats = data['stats']
    html += '''
        <section id="dashboard">
            <h2>Dashboard Overview</h2>
            <div class="grid grid-3">
'''

    html += f'''
                <div class="card">
                    <h3>Total Messages</h3>
                    <div class="stat-value">{stats['total_messages']:,}</div>
                    <div class="stat-label">{stats['date_range']['start']} to {stats['date_range']['end']}</div>
                </div>
                <div class="card">
                    <h3>Total Words</h3>
                    <div class="stat-value">{stats['total_words']:,}</div>
                    <div class="stat-label">Across all messages</div>
                </div>
'''

    for sender, sdata in stats['by_sender'].items():
        pct = (sdata['messages'] / stats['total_messages']) * 100
        html += f'''
                <div class="card">
                    <h3>{sender}</h3>
                    <div class="stat-value">{sdata['messages']:,}</div>
                    <div class="stat-label">{pct:.1f}% of messages • {sdata['words']:,} words</div>
                </div>
'''

    html += '''
            </div>
            <div class="grid grid-2" style="margin-top: 20px;">
                <div class="card">
                    <h3>Monthly Message Volume</h3>
                    <div class="chart-container"><canvas id="monthlyChart"></canvas></div>
                </div>
                <div class="card">
                    <h3>Hourly Distribution</h3>
                    <div class="chart-container"><canvas id="hourlyChart"></canvas></div>
                </div>
            </div>
        </section>
'''

    # Timeline section
    html += '''
        <section id="timeline">
            <h2>Relationship Timeline</h2>
            <div class="card">
                <h3>Love:Negative Ratio Over Time</h3>
                <div class="chart-container chart-large"><canvas id="ratioChart"></canvas></div>
            </div>
            <div class="grid grid-2" style="margin-top: 20px;">
                <div class="card">
                    <h3>Monthly Love Words</h3>
                    <div class="chart-container"><canvas id="loveChart"></canvas></div>
                </div>
                <div class="card">
                    <h3>Monthly Negative Words</h3>
                    <div class="chart-container"><canvas id="negativeChart"></canvas></div>
                </div>
            </div>
        </section>
'''

    # Sentiment section
    html += '''
        <section id="sentiment">
            <h2>Sentiment Analysis</h2>
            <div class="grid grid-2">
                <div class="card">
                    <h3>Sentiment Polarity Over Time</h3>
                    <div class="chart-container"><canvas id="polarityChart"></canvas></div>
                </div>
                <div class="card">
                    <h3>Subjectivity Over Time</h3>
                    <div class="chart-container"><canvas id="subjectivityChart"></canvas></div>
                </div>
            </div>
        </section>
'''

    # Attachment section
    html += '''
        <section id="attachment">
            <h2>Attachment Style Analysis</h2>
            <div class="grid grid-2">
                <div class="card">
                    <h3>Attachment Markers by Sender</h3>
                    <div class="chart-container"><canvas id="attachmentRadar"></canvas></div>
                </div>
                <div class="card">
                    <h3>Attachment Markers Over Time</h3>
                    <div class="chart-container"><canvas id="attachmentTimeChart"></canvas></div>
                </div>
            </div>
        </section>
'''

    # Patterns section
    html += '''
        <section id="patterns">
            <h2>Love Bombing & Withdrawal Patterns</h2>
            <div class="card">
                <h3>Affection Spikes and Withdrawals</h3>
                <div class="chart-container chart-large"><canvas id="patternsChart"></canvas></div>
            </div>
'''

    if 'love_patterns' in data.get('analysis', {}):
        lp = data['analysis']['love_patterns']
        html += f'''
            <div class="grid grid-3" style="margin-top: 20px;">
                <div class="card">
                    <div class="stat-value">{len(lp.get('spikes', []))}</div>
                    <div class="stat-label">Affection Spikes (>3x avg)</div>
                </div>
                <div class="card">
                    <div class="stat-value">{len(lp.get('withdrawals', []))}</div>
                    <div class="stat-label">Withdrawal Episodes</div>
                </div>
                <div class="card">
                    <div class="stat-value">{lp.get('intermittent_reinforcement_count', 0)}</div>
                    <div class="stat-label">Intermittent Reinforcement Cycles</div>
                </div>
            </div>
'''

    html += '''
        </section>
'''

    # Conflicts section
    html += '''
        <section id="conflicts">
            <h2>Conflict Analysis</h2>
            <div class="card">
                <h3>High-Conflict Days</h3>
                <table>
                    <thead>
                        <tr><th>Date</th><th>Conflict Messages</th><th>Severity</th></tr>
                    </thead>
                    <tbody id="conflictTable"></tbody>
                </table>
            </div>
        </section>
'''

    # Dynamics section
    html += '''
        <section id="dynamics">
            <h2>Communication Dynamics</h2>
            <div class="grid grid-2">
                <div class="card">
                    <h3>Double-Texting & Flooding</h3>
                    <div class="chart-container"><canvas id="dynamicsChart"></canvas></div>
                </div>
                <div class="card">
                    <h3>Response Times</h3>
                    <div class="chart-container"><canvas id="responseChart"></canvas></div>
                </div>
            </div>
        </section>
'''

    # Network section
    html += '''
        <section id="network">
            <h2>Third-Party Network</h2>
            <div class="card">
                <h3>People Mentioned in Conversations</h3>
                <div id="networkGraph"></div>
            </div>
'''

    if 'third_parties' in data.get('analysis', {}):
        tp = data['analysis']['third_parties']
        html += '''
            <div class="grid grid-2" style="margin-top: 20px;">
                <div class="card">
                    <h3>Most Mentioned People</h3>
                    <table>
                        <thead><tr><th>Name</th><th>Mentions</th></tr></thead>
                        <tbody>
'''
        for person in tp.get('third_parties', [])[:10]:
            html += f'<tr><td>{person["name"]}</td><td>{person["count"]}</td></tr>'

        html += '''
                        </tbody>
                    </table>
                </div>
                <div class="card">
                    <h3>Relationship Terms</h3>
                    <table>
                        <thead><tr><th>Term</th><th>Mentions</th></tr></thead>
                        <tbody>
'''
        for term, count in sorted(tp.get('relationship_terms', {}).items(), key=lambda x: x[1], reverse=True):
            html += f'<tr><td>{term}</td><td>{count}</td></tr>'

        html += '''
                        </tbody>
                    </table>
                </div>
            </div>
'''

    html += '''
        </section>
'''

    # Findings section
    html += '''
        <section id="findings">
            <h2>Key Findings</h2>
            <div id="findingsContainer"></div>
        </section>
'''

    # Chart initialization script
    html += '''
    <script>
        // Color palette
        const colors = {
            blue: '#3b82f6',
            green: '#22c55e',
            red: '#ef4444',
            yellow: '#eab308',
            purple: '#a855f7',
            pink: '#ec4899',
            cyan: '#06b6d4'
        };

        // Get sender names
        const senders = Object.keys(DATA.stats.by_sender);
        const senderColors = [colors.blue, colors.pink];

        // Monthly chart
        const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
        const months = Object.keys(DATA.monthly).sort();
        new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: senders.map((sender, i) => ({
                    label: sender,
                    data: months.map(m => DATA.monthly[m]?.[sender]?.messages || 0),
                    borderColor: senderColors[i],
                    backgroundColor: senderColors[i] + '20',
                    fill: true,
                    tension: 0.3
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#e2e8f0' } } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });

        // Hourly chart
        const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
        const hours = Array.from({length: 24}, (_, i) => i);
        new Chart(hourlyCtx, {
            type: 'bar',
            data: {
                labels: hours.map(h => `${h}:00`),
                datasets: senders.map((sender, i) => ({
                    label: sender,
                    data: hours.map(h => DATA.hourly[h]?.[sender] || 0),
                    backgroundColor: senderColors[i]
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#e2e8f0' } } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });

        // Love:Negative ratio chart
        const ratioCtx = document.getElementById('ratioChart').getContext('2d');
        const ratioData = months.map(m => {
            let love = 0, neg = 0;
            Object.values(DATA.monthly[m] || {}).forEach(s => {
                love += s.love || 0;
                neg += s.negative || 0;
            });
            return neg > 0 ? (love / neg).toFixed(2) : love;
        });
        new Chart(ratioCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Love:Negative Ratio',
                    data: ratioData,
                    borderColor: colors.purple,
                    backgroundColor: colors.purple + '20',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#e2e8f0' } },
                    annotation: {
                        annotations: {
                            line1: { type: 'line', yMin: 1, yMax: 1, borderColor: colors.red, borderDash: [5, 5] }
                        }
                    }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });

        // Love chart
        const loveCtx = document.getElementById('loveChart').getContext('2d');
        new Chart(loveCtx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: senders.map((sender, i) => ({
                    label: sender,
                    data: months.map(m => DATA.monthly[m]?.[sender]?.love || 0),
                    backgroundColor: senderColors[i]
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#e2e8f0' } } },
                scales: {
                    x: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });

        // Negative chart
        const negCtx = document.getElementById('negativeChart').getContext('2d');
        new Chart(negCtx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: senders.map((sender, i) => ({
                    label: sender,
                    data: months.map(m => DATA.monthly[m]?.[sender]?.negative || 0),
                    backgroundColor: senderColors[i]
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#e2e8f0' } } },
                scales: {
                    x: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });

        // Sentiment charts
        const polarityCtx = document.getElementById('polarityChart').getContext('2d');
        new Chart(polarityCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: senders.map((sender, i) => ({
                    label: sender,
                    data: months.map(m => DATA.monthly[m]?.[sender]?.sentiment || 0),
                    borderColor: senderColors[i],
                    tension: 0.3
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#e2e8f0' } } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' }, min: -0.5, max: 0.5 }
                }
            }
        });

        const subjectivityCtx = document.getElementById('subjectivityChart').getContext('2d');
        new Chart(subjectivityCtx, {
            type: 'line',
            data: {
                labels: months,
                datasets: senders.map((sender, i) => ({
                    label: sender,
                    data: months.map(m => DATA.monthly[m]?.[sender]?.subjectivity || 0),
                    borderColor: senderColors[i],
                    tension: 0.3
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#e2e8f0' } } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });

        // Attachment radar
        if (DATA.analysis && DATA.analysis.attachment) {
            const attachmentCtx = document.getElementById('attachmentRadar').getContext('2d');
            new Chart(attachmentCtx, {
                type: 'radar',
                data: {
                    labels: ['Anxious', 'Avoidant', 'Secure', 'Controlling'],
                    datasets: Object.entries(DATA.analysis.attachment).map(([sender, styles], i) => ({
                        label: sender,
                        data: [styles.anxious || 0, styles.avoidant || 0, styles.secure || 0, styles.controlling || 0],
                        borderColor: senderColors[i],
                        backgroundColor: senderColors[i] + '30'
                    }))
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#e2e8f0' } } },
                    scales: {
                        r: {
                            angleLines: { color: '#334155' },
                            grid: { color: '#334155' },
                            pointLabels: { color: '#e2e8f0' },
                            ticks: { color: '#94a3b8', backdropColor: 'transparent' }
                        }
                    }
                }
            });
        }

        // Attachment over time
        if (DATA.attachment_monthly) {
            const attachTimeCtx = document.getElementById('attachmentTimeChart').getContext('2d');
            const styles = ['anxious', 'avoidant', 'secure', 'controlling'];
            const styleColors = [colors.yellow, colors.blue, colors.green, colors.red];

            new Chart(attachTimeCtx, {
                type: 'line',
                data: {
                    labels: months,
                    datasets: styles.map((style, i) => ({
                        label: style.charAt(0).toUpperCase() + style.slice(1),
                        data: months.map(m => {
                            let total = 0;
                            Object.values(DATA.attachment_monthly[m] || {}).forEach(s => total += s[style] || 0);
                            return total;
                        }),
                        borderColor: styleColors[i],
                        tension: 0.3
                    }))
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#e2e8f0' } } },
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                    }
                }
            });
        }

        // Patterns chart
        if (DATA.analysis && DATA.analysis.love_patterns) {
            const patternsCtx = document.getElementById('patternsChart').getContext('2d');
            const spikes = DATA.analysis.love_patterns.spikes || [];
            const withdrawals = DATA.analysis.love_patterns.withdrawals || [];

            new Chart(patternsCtx, {
                type: 'scatter',
                data: {
                    datasets: [
                        {
                            label: 'Affection Spikes',
                            data: spikes.map(s => ({ x: s.date, y: s.value })),
                            backgroundColor: colors.green,
                            pointRadius: 6
                        },
                        {
                            label: 'Withdrawals',
                            data: withdrawals.map(w => ({ x: w.date, y: w.value })),
                            backgroundColor: colors.red,
                            pointRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#e2e8f0' } } },
                    scales: {
                        x: { type: 'category', labels: months, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                    }
                }
            });
        }

        // Conflict table
        if (DATA.analysis && DATA.analysis.conflicts) {
            const tbody = document.getElementById('conflictTable');
            const conflicts = DATA.analysis.conflicts.high_conflict_days || [];
            conflicts.slice(0, 20).forEach(c => {
                const severity = c.count > 15 ? 'Critical' : c.count > 10 ? 'High' : 'Moderate';
                const badgeClass = c.count > 15 ? 'badge-red' : c.count > 10 ? 'badge-yellow' : 'badge-blue';
                tbody.innerHTML += `<tr><td>${c.date}</td><td>${c.count}</td><td><span class="badge ${badgeClass}">${severity}</span></td></tr>`;
            });
        }

        // Dynamics charts
        if (DATA.analysis && DATA.analysis.dynamics) {
            const dynamicsCtx = document.getElementById('dynamicsChart').getContext('2d');
            const dyn = DATA.analysis.dynamics;

            new Chart(dynamicsCtx, {
                type: 'bar',
                data: {
                    labels: senders,
                    datasets: [
                        {
                            label: 'Double Texts',
                            data: senders.map(s => dyn.double_texts?.[s] || 0),
                            backgroundColor: colors.blue
                        },
                        {
                            label: 'Triple+ Floods',
                            data: senders.map(s => dyn.triple_floods?.[s] || 0),
                            backgroundColor: colors.purple
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#e2e8f0' } } },
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                    }
                }
            });

            const responseCtx = document.getElementById('responseChart').getContext('2d');
            new Chart(responseCtx, {
                type: 'bar',
                data: {
                    labels: senders,
                    datasets: [{
                        label: 'Avg Response Time (minutes)',
                        data: senders.map(s => dyn.response_times?.[s]?.avg_minutes || 0),
                        backgroundColor: senders.map((_, i) => senderColors[i])
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                    }
                }
            });
        }

        // Network graph
        if (DATA.analysis && DATA.analysis.third_parties) {
            const parties = DATA.analysis.third_parties.third_parties || [];
            const nodes = [
                ...senders.map((s, i) => ({ id: s, group: 'main', radius: 25 })),
                ...parties.slice(0, 15).map(p => ({ id: p.name, group: 'third', radius: 8 + Math.min(p.count / 10, 15) }))
            ];
            const links = parties.slice(0, 15).map(p => ({
                source: senders[0],
                target: p.name,
                value: p.count
            }));

            const width = document.getElementById('networkGraph').clientWidth;
            const height = 500;

            const svg = d3.select('#networkGraph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-200))
                .force('center', d3.forceCenter(width / 2, height / 2));

            const link = svg.append('g')
                .selectAll('line')
                .data(links)
                .enter().append('line')
                .attr('stroke', '#475569')
                .attr('stroke-width', d => Math.min(d.value / 20, 3));

            const node = svg.append('g')
                .selectAll('circle')
                .data(nodes)
                .enter().append('circle')
                .attr('r', d => d.radius)
                .attr('fill', d => d.group === 'main' ? colors.blue : colors.cyan);

            const label = svg.append('g')
                .selectAll('text')
                .data(nodes)
                .enter().append('text')
                .text(d => d.id)
                .attr('fill', '#e2e8f0')
                .attr('font-size', d => d.group === 'main' ? '14px' : '10px')
                .attr('text-anchor', 'middle')
                .attr('dy', d => d.radius + 12);

            simulation.on('tick', () => {
                link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
                node.attr('cx', d => d.x).attr('cy', d => d.y);
                label.attr('x', d => d.x).attr('y', d => d.y);
            });
        }

        // Generate findings
        const findingsContainer = document.getElementById('findingsContainer');
        const findings = [];

        // Communication asymmetry
        const totalMsgs = DATA.stats.total_messages;
        Object.entries(DATA.stats.by_sender).forEach(([sender, data]) => {
            const pct = (data.messages / totalMsgs) * 100;
            if (pct > 55) {
                findings.push({
                    type: 'warning',
                    title: 'Communication Asymmetry',
                    text: `${sender} sent ${pct.toFixed(1)}% of all messages, indicating potential imbalance.`
                });
            }
        });

        // Love bombing
        if (DATA.analysis?.love_patterns?.spikes?.length > 50) {
            findings.push({
                type: 'critical',
                title: 'Love Bombing Detected',
                text: `${DATA.analysis.love_patterns.spikes.length} affection spikes detected (>3x average). This pattern is associated with manipulative behavior.`
            });
        }

        // Intermittent reinforcement
        if (DATA.analysis?.love_patterns?.intermittent_reinforcement_count > 30) {
            findings.push({
                type: 'critical',
                title: 'Intermittent Reinforcement Pattern',
                text: `${DATA.analysis.love_patterns.intermittent_reinforcement_count} spike-withdrawal cycles detected. This creates trauma bonding.`
            });
        }

        // High conflict
        if (DATA.analysis?.conflicts?.high_conflict_days?.length > 30) {
            findings.push({
                type: 'warning',
                title: 'Elevated Conflict Level',
                text: `${DATA.analysis.conflicts.high_conflict_days.length} high-conflict days identified.`
            });
        }

        findings.forEach(f => {
            findingsContainer.innerHTML += `
                <div class="finding ${f.type}">
                    <h4>${f.title}</h4>
                    <p>${f.text}</p>
                </div>
            `;
        });

        if (findings.length === 0) {
            findingsContainer.innerHTML = '<p style="color: #94a3b8;">No significant findings detected.</p>';
        }
    </script>

    </div>
</body>
</html>
'''

    return html

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python generate_report.py <database.db> <output.html>")
        sys.exit(1)

    db_path: str = sys.argv[1]
    output_path: str = sys.argv[2]

    print(f"Generating report from: {db_path}")

    conn = sqlite3.connect(db_path)

    # Gather all data
    data = {
        'stats': get_base_stats(conn),
        'monthly': get_monthly_data(conn),
        'daily': get_daily_data(conn),
        'hourly': get_hourly_data(conn),
        'analysis': get_analysis_results(conn),
        'attachment_monthly': get_attachment_monthly(conn)
    }

    conn.close()

    # Generate HTML
    html = generate_html(data)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ Report generated: {output_path}")
    print(f"  Size: {len(html):,} bytes")

if __name__ == '__main__':
    main()
