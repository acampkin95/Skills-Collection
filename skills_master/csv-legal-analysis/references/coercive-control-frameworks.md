# Coercive Control Analysis Frameworks

> **Purpose**: Research-backed frameworks for identifying coercive control patterns in messaging data for Australian family law proceedings.
> **Sources**: Evan Stark (2007), ANROWS, DASH/DARA, Duluth Model, WA FVLRA 2020
> **Important**: This is a screening tool, not a diagnostic instrument. Flagged patterns require assessment by qualified family violence practitioners or the court.

---

## Table of Contents

1. [Legislative Context](#1-legislative-context)
2. [Evan Stark Coercive Control Framework](#2-evan-stark-coercive-control-framework)
3. [ANROWS Technology-Facilitated Abuse Research](#3-anrows-technology-facilitated-abuse-research)
4. [DASH / DARA Risk Assessment Mapping](#4-dash--dara-risk-assessment-mapping)
5. [Duluth Power & Control Model — Digital Mapping](#5-duluth-power--control-model--digital-mapping)
6. [Messaging Pattern Indicators](#6-messaging-pattern-indicators)
7. [Temporal Analysis for Coercive Control](#7-temporal-analysis-for-coercive-control)
8. [Automated Pattern Detection Pipeline](#8-automated-pattern-detection-pipeline)
9. [Scoring & Risk Rubric](#9-scoring--risk-rubric)
10. [Reporting Format for Court](#10-reporting-format-for-court)
11. [Limitations & Ethical Boundaries](#11-limitations--ethical-boundaries)

---

## 1. Legislative Context

### WA Family Violence Legislation Reform Act 2020

Explicitly recognises technology-facilitated abuse as family violence:

> "Using technology to threaten, humiliate, harass, stalk, intimidate, exert undue influence over, or abuse the other party, including by engaging in cyberstalking, monitoring, surveillance, impersonation, manipulation of electronic media, or distribution of or threats to distribute actual or fabricated intimate images."

**Key points**:
- Coercive control is recognised as a pattern of abusive behaviour (not just discrete incidents)
- Technology-based coercion is explicitly listed
- WA does not yet have a standalone coercive control criminal offence (unlike NSW from 1 July 2024 and Tasmania)
- Family violence findings influence parenting orders under Family Law Act s60CC

### Restraining Orders Act 1997 (WA)

- Sections 44A–44C provide flexible evidence standards for FVRO applications
- Pattern of behaviour can be established through messaging evidence
- Lower proof threshold than criminal proceedings

---

## 2. Evan Stark Coercive Control Framework

### Core Theory (Stark, 2007; Stark & Hester, 2019)

Coercive control is not discrete acts of violence, but a **systematic pattern of behaviour** that:
- Erodes autonomy and agency
- Creates a state of entrapment analogous to kidnapping or hostage-taking
- Functions through micro-regulation of everyday life
- May or may not include physical violence

### Pattern Elements in Messaging

```python
STARK_FRAMEWORK_INDICATORS = {
    'isolation': {
        'description': 'Restricting social connections and support networks',
        'messaging_indicators': [
            r'\bdon\'?t\s+(talk|speak|see|contact|message)\s+(to|with)\b',
            r'\bstay\s+away\s+from\b',
            r'\byour\s+(mother|father|friend|sister|brother)\s+is\b.*\b(bad|toxic|no good)',
            r'\bblock\s+(him|her|them)\b',
            r'\bwho\s+(are|were)\s+you\s+(with|talking|texting)\b',
            r'\bshow\s+me\s+your\s+(phone|messages|texts)\b',
        ],
        'weight': 'HIGH — undermines support networks',
    },
    'monitoring_surveillance': {
        'description': 'Tracking movements, communications, and activities',
        'messaging_indicators': [
            r'\bwhere\s+are\s+you\b',
            r'\bwho\s+are\s+you\s+with\b',
            r'\bI\s+(saw|know|watched|noticed)\s+you\b',
            r'\bI\s+(can|will)\s+see\s+(where|what|who)\b',
            r'\bcheck\s+your\s+(location|phone|messages)\b',
            r'\bFind\s+My\b',
            r'\bLife360\b',
            r'\btracking\b',
            r'\bI\s+know\s+(where|what|who)\b',
        ],
        'weight': 'HIGH — surveillance is a primary control mechanism',
    },
    'economic_control': {
        'description': 'Controlling access to financial resources',
        'messaging_indicators': [
            r'\byou\s+(can\'?t|won\'?t)\s+(spend|buy|use)\b',
            r'\bgive\s+me\s+(the|your)\s+(card|money|account|password)\b',
            r'\bhow\s+much\s+did\s+you\s+spend\b',
            r'\bwhat\s+did\s+you\s+buy\b',
            r'\bI\s+control\s+the\s+(money|finances|accounts)\b',
            r'\byou\s+owe\s+me\b',
        ],
        'weight': 'MEDIUM-HIGH — undermines financial independence',
    },
    'threats_intimidation': {
        'description': 'Explicit or implicit threats to coerce compliance',
        'messaging_indicators': [
            r'\bI\'?ll\s+(kill|hurt|destroy|ruin)\b',
            r'\byou\'?ll\s+(regret|pay|suffer|be\s+sorry)\b',
            r'\bI\'?ll\s+take\s+the\s+(kids|children)\b',
            r'\bnever\s+see\s+(them|him|her)\s+again\b',
            r'\bI\'?ll\s+tell\s+everyone\b',
            r'\bI\'?ll\s+(post|share|send)\s+(the\s+)?(photos?|images?|videos?)\b',
            r'\bif\s+you\s+(leave|go|don\'?t)\b.*\bI\'?ll\b',
        ],
        'weight': 'CRITICAL — immediate safety concern',
    },
    'emotional_abuse': {
        'description': 'Systematic denigration, humiliation, and psychological manipulation',
        'messaging_indicators': [
            r'\byou\'?re\s+(crazy|insane|mental|unstable|delusional|stupid|worthless|useless|pathetic)\b',
            r'\bno\s+one\s+(will|would)\s+(believe|love|want)\s+you\b',
            r'\bthat\s+never\s+happened\b',
            r'\byou\'?re\s+imagining\s+things\b',
            r'\byou\'?re\s+making\s+it\s+up\b',
            r'\byou\'?re\s+(a\s+)?bad\s+(mother|father|parent)\b',
        ],
        'weight': 'MEDIUM-HIGH if systematic',
    },
    'using_children': {
        'description': 'Using children as leverage, threats, or instruments of control',
        'messaging_indicators': [
            r'\bthe\s+(kids?|children)\s+(don\'?t|won\'?t)\s+(love|want|need)\s+you\b',
            r'\bI\'?ll\s+(take|keep|hide)\s+the\s+(kids?|children)\b',
            r'\byou\'?ll\s+never\s+see\s+(them|him|her)\b',
            r'\b(he|she|they)\s+(told|said)\s+me\s+(they|he|she)\s+(hate|don\'?t like)\s+you\b',
            r'\btell\s+(him|her|them)\s+that\s+(mum|dad|you)\b',
        ],
        'weight': 'CRITICAL — weaponising children',
    },
    'sexual_coercion': {
        'description': 'Pressure or demands regarding sexual activity or reproduction',
        'messaging_indicators': [
            r'\byou\s+(have|need|must)\s+to\b.*\b(sex|sleep\s+with)\b',
            r'\bif\s+you\s+(loved|love)\s+me\s+you\'?d\b',
            r'\bI\'?ll\s+(show|send|post)\b.*\b(nude|naked|intimate)\b',
        ],
        'weight': 'CRITICAL — fundamental autonomy breach',
    },
    'systems_abuse': {
        'description': 'Using legal/institutional systems as instruments of control',
        'messaging_indicators': [
            r'\bI\'?ll\s+(call|report|tell)\s+(the\s+)?(police|cops|DOCS|child\s+protection|DCP)\b',
            r'\bI\'?ll\s+(get|take\s+out)\s+(a|an)\s+(AVO|DVO|FVRO|restraining\s+order)\b',
            r'\bI\'?ll\s+take\s+you\s+to\s+court\b',
            r'\bmy\s+lawyer\s+will\b',
        ],
        'weight': 'MEDIUM — context-dependent; may be legitimate',
    },
}
```

---

## 3. ANROWS Technology-Facilitated Abuse Research

### Key Patterns (ANROWS 2019, 2021, 2023)

Australia's National Research Organisation for Women's Safety identifies these technology-facilitated abuse patterns:

```python
ANROWS_TFA_PATTERNS = {
    'monitoring_surveillance': {
        'description': 'Persistent tracking of location, social media, messages, device activity',
        'digital_indicators': [
            'Location sharing demanded or covertly enabled',
            'Frequent "where are you" messages without legitimate reason',
            'Knowledge of activities not directly communicated',
            'Checking/demanding access to phone, social media, email',
        ],
    },
    'harassment': {
        'description': 'Repeated, unwanted contact; flooding; rapid-fire messages',
        'digital_indicators': [
            'Message volume far exceeds reasonable communication',
            'Messages sent at antisocial hours (late night, early morning)',
            'Multiple messages demanding response with escalating urgency',
            'Contact through multiple platforms after being blocked on one',
        ],
    },
    'threats_intimidation': {
        'description': 'Threats to share intimate images, harm children, or publicise information',
        'digital_indicators': [
            'Explicit threats to distribute intimate images',
            'Threats referencing children as leverage',
            'Threats to reveal private information',
            'Threats of harm conditional on victim\'s actions',
        ],
    },
    'isolation': {
        'description': 'Monitoring who the victim communicates with; demands to stop contact',
        'digital_indicators': [
            'Demands to block or unfriend people',
            'Anger or punishment after victim contacts others',
            'Monitoring contact lists, call logs, message history',
            'Creating conflict between victim and support network',
        ],
    },
    'gaslighting': {
        'description': 'Denial of prior messages, reframing victim\'s concerns',
        'digital_indicators': [
            'Denial of sending messages that are documented',
            'Reframing victim\'s concerns as paranoia or mental illness',
            'Accusing victim of misinterpreting clear statements',
            'Alternating between hostility and affection ("lovebombing")',
        ],
    },
    'impersonation': {
        'description': 'Sending messages from victim\'s account, creating fake accounts',
        'digital_indicators': [
            'Messages sent from victim\'s account without consent',
            'Fake accounts created to contact victim or third parties',
            'Manipulated screenshots or messages presented as genuine',
        ],
    },
}
```

---

## 4. DASH / DARA Risk Assessment Mapping

### DASH (Domestic Abuse, Stalking and Honour-Based Violence)

Originally UK-based, adapted for use in Australian jurisdictions. 27-point risk checklist. Messaging evidence is relevant to scoring:

```python
DASH_MESSAGING_RELEVANT_QUESTIONS = {
    'Q3_threats_to_kill': {
        'question': 'Has the abuser ever threatened to kill you or someone else?',
        'messaging_search': r'\b(kill|murder|die|dead)\b',
        'weight': 'HIGH RISK if positive',
    },
    'Q4_strangulation': {
        'question': 'Has the abuser ever used weapons or objects to hurt you?',
        'messaging_search': r'\b(gun|knife|weapon|strangle|choke)\b',
    },
    'Q8_jealousy': {
        'question': 'Is the abuser excessively jealous or controlling?',
        'messaging_search': r'\b(who\s+were\s+you\s+with|jealous|cheating|unfaithful)\b',
    },
    'Q12_financial_control': {
        'question': 'Does the abuser control your finances?',
        'messaging_search': r'\b(give\s+me\s+(the\s+)?money|can\'?t\s+spend|account|budget)\b',
    },
    'Q14_stalking': {
        'question': 'Does the abuser follow you or watch your movements?',
        'messaging_search': r'\b(I\s+(saw|watched|followed|tracked)|where\s+(are|were)\s+you)\b',
    },
    'Q17_children': {
        'question': 'Has the abuser ever hurt or threatened the children?',
        'messaging_search': r'\b(take\s+the\s+kids?|hurt\s+the\s+child|never\s+see\s+them)\b',
    },
    'Q21_separation': {
        'question': 'Are you currently separated or trying to separate?',
        'messaging_search': r'\b(if\s+you\s+leave|divorce|separate|court)\b',
    },
}
```

---

## 5. Duluth Power & Control Model — Digital Mapping

### Control Tactics Mapped to Messaging Patterns

| Duluth Tactic | Digital Manifestation | Regex Indicators |
|--------------|----------------------|-----------------|
| **Using intimidation** | Threatening messages, expressing intent to harm | `\b(I'll|going to)\s+(hurt|kill|destroy)` |
| **Using emotional abuse** | Name-calling, denigration, gaslighting | `\byou're\s+(crazy|stupid|worthless)` |
| **Using isolation** | Controlling contacts, demanding access to messages | `\bdon't\s+talk\s+to\b`, `\bblock\s+(him|her)` |
| **Minimising/denying** | "That never happened", "You're overreacting" | `\bnever\s+happened\b`, `\boverreact` |
| **Using children** | Threatening custody, using kids as messengers | `\btake\s+the\s+kids\b`, `\btell\s+(mum|dad)` |
| **Using privilege** | "I'm the man/provider", gender-based entitlement | `\bmy\s+house\b`, `\bI\s+pay\s+for` |
| **Using economic abuse** | Controlling money, demanding financial account access | `\bgive\s+me\s+(the\s+)?card\b`, `\bhow\s+much` |
| **Using coercion/threats** | Conditional threats, ultimatums | `\bif\s+you\s+don't\b.*\bI\s+will\b` |

---

## 6. Messaging Pattern Indicators

### Quantitative Indicators

```python
def analyse_messaging_patterns(df, sender_col, timestamp_col, body_col, target_sender):
    """
    Analyse quantitative messaging patterns for coercive control indicators.

    target_sender: the party being assessed for controlling behaviour
    """
    import pandas as pd

    target_msgs = df[df[sender_col] == target_sender].copy()
    other_msgs = df[df[sender_col] != target_sender].copy()

    patterns = {}

    # 1. Volume asymmetry
    patterns['volume_ratio'] = len(target_msgs) / max(len(other_msgs), 1)
    patterns['volume_assessment'] = (
        'SIGNIFICANT ASYMMETRY' if patterns['volume_ratio'] > 3
        else 'MODERATE ASYMMETRY' if patterns['volume_ratio'] > 2
        else 'BALANCED'
    )

    # 2. Temporal patterns
    if timestamp_col in target_msgs.columns:
        target_msgs['_hour'] = pd.to_datetime(target_msgs[timestamp_col], errors='coerce').dt.hour
        antisocial = target_msgs[(target_msgs['_hour'] < 6) | (target_msgs['_hour'] >= 23)]
        patterns['antisocial_hours_pct'] = len(antisocial) / max(len(target_msgs), 1) * 100
        patterns['antisocial_assessment'] = (
            'SIGNIFICANT' if patterns['antisocial_hours_pct'] > 15
            else 'MODERATE' if patterns['antisocial_hours_pct'] > 5
            else 'NORMAL'
        )

    # 3. Response pressure (messages sent without getting a reply)
    df_sorted = df.sort_values(timestamp_col)
    consecutive_from_target = 0
    max_consecutive = 0
    for _, row in df_sorted.iterrows():
        if row[sender_col] == target_sender:
            consecutive_from_target += 1
            max_consecutive = max(max_consecutive, consecutive_from_target)
        else:
            consecutive_from_target = 0

    patterns['max_unanswered_consecutive'] = max_consecutive
    patterns['pressure_assessment'] = (
        'HIGH PRESSURE' if max_consecutive > 10
        else 'MODERATE PRESSURE' if max_consecutive > 5
        else 'NORMAL'
    )

    # 4. Message length asymmetry (controlling messages tend to be longer/more directive)
    target_avg_len = target_msgs[body_col].fillna('').str.len().mean()
    other_avg_len = other_msgs[body_col].fillna('').str.len().mean()
    patterns['length_ratio'] = target_avg_len / max(other_avg_len, 1)

    return patterns
```

### Qualitative Indicators (Regex-Based)

```python
def detect_coercive_language(df, body_col, sender_col=None, target_sender=None):
    """
    Detect coercive control language indicators in messaging data.

    Returns DataFrame with classification flags and evidence references.
    """
    import re

    if target_sender and sender_col:
        df_subset = df[df[sender_col] == target_sender].copy()
    else:
        df_subset = df.copy()

    indicators = {}

    for category, config in STARK_FRAMEWORK_INDICATORS.items():
        combined_pattern = '|'.join(config['messaging_indicators'])
        mask = df_subset[body_col].str.contains(
            combined_pattern, case=False, regex=True, na=False
        )
        hits = df_subset[mask]
        indicators[category] = {
            'count': len(hits),
            'weight': config['weight'],
            'sample_messages': hits[body_col].head(5).tolist(),
            'message_ids': hits.index.tolist()[:50],
        }

    return indicators
```

---

## 7. Temporal Analysis for Coercive Control

### Escalation Detection

```python
def detect_escalation(df, timestamp_col, body_col, sender_col, target_sender,
                       window_days=7):
    """
    Detect escalation patterns — increasing frequency, intensity, or severity
    of controlling messages over time.
    """
    import pandas as pd
    import numpy as np

    target_msgs = df[df[sender_col] == target_sender].copy()
    target_msgs['_ts'] = pd.to_datetime(target_msgs[timestamp_col], errors='coerce')
    target_msgs = target_msgs.sort_values('_ts')

    # Rolling window analysis
    target_msgs['_period'] = target_msgs['_ts'].dt.to_period(f'{window_days}D')

    period_stats = target_msgs.groupby('_period').agg(
        message_count=(body_col, 'count'),
        avg_length=(body_col, lambda x: x.fillna('').str.len().mean()),
    ).reset_index()

    # Detect upward trends
    if len(period_stats) > 2:
        count_trend = np.polyfit(range(len(period_stats)),
                                  period_stats['message_count'], 1)[0]
        length_trend = np.polyfit(range(len(period_stats)),
                                   period_stats['avg_length'], 1)[0]
    else:
        count_trend = 0
        length_trend = 0

    escalation = {
        'frequency_trend': 'INCREASING' if count_trend > 0.5 else 'STABLE' if count_trend > -0.5 else 'DECREASING',
        'intensity_trend': 'INCREASING' if length_trend > 2 else 'STABLE',
        'count_slope': round(count_trend, 2),
        'length_slope': round(length_trend, 2),
        'periods_analysed': len(period_stats),
    }

    return escalation, period_stats
```

### Demand-Response Pattern Detection

```python
def detect_demand_response(df, timestamp_col, sender_col, target_sender,
                            response_window_minutes=30):
    """
    Detect demand-response patterns: sender escalates until recipient responds.
    """
    import pandas as pd

    df_sorted = df.sort_values(timestamp_col).copy()
    df_sorted['_ts'] = pd.to_datetime(df_sorted[timestamp_col], errors='coerce')

    sequences = []
    current_demands = []

    for _, row in df_sorted.iterrows():
        if row[sender_col] == target_sender:
            current_demands.append(row)
        else:
            if len(current_demands) > 1:
                # Record the sequence: multiple demands before response
                first_demand = current_demands[0]['_ts']
                last_demand = current_demands[-1]['_ts']
                response_time = row['_ts']

                sequences.append({
                    'demand_count': len(current_demands),
                    'first_demand': first_demand,
                    'last_demand': last_demand,
                    'response_time': response_time,
                    'pressure_duration_minutes': (last_demand - first_demand).total_seconds() / 60,
                    'wait_before_response_minutes': (response_time - last_demand).total_seconds() / 60,
                })
            current_demands = []

    if sequences:
        avg_demands = sum(s['demand_count'] for s in sequences) / len(sequences)
        max_demands = max(s['demand_count'] for s in sequences)
        print(f"Demand-response sequences: {len(sequences)}")
        print(f"Average demands before response: {avg_demands:.1f}")
        print(f"Maximum demands in one sequence: {max_demands}")

    return sequences
```

---

## 8. Automated Pattern Detection Pipeline

```python
def coercive_control_analysis(df, timestamp_col, sender_col, body_col,
                                target_sender, known_parties=None):
    """
    Complete coercive control analysis pipeline.

    Returns: comprehensive analysis report with all indicators.
    """
    report = {
        'target_party': target_sender,
        'analysis_date': datetime.now(timezone.utc).isoformat(),
        'dataset_size': len(df),
        'target_messages': len(df[df[sender_col] == target_sender]),
    }

    # 1. Quantitative patterns
    report['quantitative'] = analyse_messaging_patterns(
        df, sender_col, timestamp_col, body_col, target_sender)

    # 2. Coercive language indicators (Stark framework)
    report['language_indicators'] = detect_coercive_language(
        df, body_col, sender_col, target_sender)

    # 3. Escalation analysis
    escalation, periods = detect_escalation(
        df, timestamp_col, body_col, sender_col, target_sender)
    report['escalation'] = escalation

    # 4. Demand-response patterns
    report['demand_response'] = detect_demand_response(
        df, timestamp_col, sender_col, target_sender)

    # 5. Summary scoring
    report['summary'] = summarise_indicators(report)

    return report


def summarise_indicators(report):
    """Summarise coercive control indicators into a structured assessment."""
    categories_detected = []
    critical_flags = []

    for category, data in report.get('language_indicators', {}).items():
        if data['count'] > 0:
            categories_detected.append(category)
            if 'CRITICAL' in data['weight']:
                critical_flags.append(f"{category}: {data['count']} instances")

    summary = {
        'categories_with_indicators': len(categories_detected),
        'total_categories': len(STARK_FRAMEWORK_INDICATORS),
        'categories_detected': categories_detected,
        'critical_flags': critical_flags,
        'volume_asymmetry': report['quantitative'].get('volume_assessment', 'N/A'),
        'escalation_trend': report['escalation'].get('frequency_trend', 'N/A'),
        'antisocial_hours': report['quantitative'].get('antisocial_assessment', 'N/A'),

        'overall_assessment': (
            'SIGNIFICANT INDICATORS PRESENT — Refer to family violence specialist'
            if len(categories_detected) >= 4 or len(critical_flags) > 0
            else 'MODERATE INDICATORS — Review recommended'
            if len(categories_detected) >= 2
            else 'LIMITED INDICATORS — Standard communication patterns'
        ),

        'disclaimer': (
            'This is a screening tool based on published research frameworks. '
            'It does NOT diagnose coercive control. Assessment must be made by '
            'qualified family violence practitioners or the court. '
            'Temporal patterns + isolated messages do NOT constitute proof.'
        ),
    }

    return summary
```

---

## 9. Scoring & Risk Rubric

### Pattern Scoring (Research-Informed, Not Diagnostic)

| Indicator Category | Instances | Score |
|-------------------|-----------|-------|
| Threats/intimidation | Any | +3 per instance (CRITICAL) |
| Using children as leverage | Any | +3 per instance (CRITICAL) |
| Sexual coercion | Any | +3 per instance (CRITICAL) |
| Monitoring/surveillance | 1–5 | +1; 6+ = +2 |
| Isolation tactics | 1–5 | +1; 6+ = +2 |
| Economic control | 1–5 | +1; 6+ = +2 |
| Emotional abuse/gaslighting | 1–5 | +1; 6+ = +2 |
| Systems abuse | Context-dependent | +1 |
| Volume asymmetry >3:1 | Present | +1 |
| Antisocial hours >15% | Present | +1 |
| Escalation trend | Increasing | +2 |
| Demand-response max >10 | Present | +1 |

### Risk Levels

| Total Score | Assessment | Recommended Action |
|------------|------------|-------------------|
| 0–3 | Limited indicators | Standard review |
| 4–8 | Moderate indicators | Flag for practitioner review |
| 9–15 | Significant indicators | Refer to family violence specialist |
| 16+ | Severe indicators | Urgent referral; mandatory reporting screening |

---

## 10. Reporting Format for Court

### Structure for Coercive Control Pattern Report

```python
COURT_REPORT_STRUCTURE = {
    'title': 'Analysis of Messaging Patterns: [Party A] to [Party B]',
    'sections': [
        {
            'heading': '1. Scope and Methodology',
            'content': [
                'Dataset description (date range, message count, source)',
                'Analysis methodology (frameworks applied: Stark, ANROWS)',
                'Tool and version used',
                'Limitations and disclaimers',
            ]
        },
        {
            'heading': '2. Quantitative Summary',
            'content': [
                'Message volume by party',
                'Temporal distribution (daily, hourly patterns)',
                'Response time analysis',
                'Communication asymmetry metrics',
            ]
        },
        {
            'heading': '3. Pattern Analysis',
            'content': [
                'Categories of indicators detected (with message references)',
                'Temporal escalation assessment',
                'Demand-response pattern analysis',
                'Isolation and monitoring indicators',
            ]
        },
        {
            'heading': '4. Specific Message References',
            'content': [
                'Threats/intimidation (message IDs and excerpts)',
                'Children-related controlling language',
                'Surveillance/monitoring language',
                'Other significant indicators',
            ]
        },
        {
            'heading': '5. Assessment Summary',
            'content': [
                'Overall pattern assessment (with scoring transparency)',
                'Alignment with recognised frameworks (Stark, ANROWS)',
                'Limitations of automated analysis',
                'Recommendation for further assessment',
            ]
        },
    ],
    'mandatory_disclaimers': [
        'This analysis identifies messaging patterns consistent with published coercive control research frameworks.',
        'It does NOT diagnose coercive control or make findings of family violence.',
        'All flagged patterns require assessment by qualified family violence practitioners or the court.',
        'Automated pattern detection has inherent limitations; context and nuance require human judgement.',
        'The absence of flagged indicators does NOT indicate the absence of coercive control.',
    ],
}
```

---

## 11. Limitations & Ethical Boundaries

### What This Framework Can Do

- Identify messaging patterns consistent with published coercive control research
- Quantify temporal, volumetric, and linguistic indicators
- Provide structured evidence references for court review
- Screen for mandatory reporting triggers

### What This Framework Cannot Do

- **Diagnose coercive control** — that is a judicial/clinical determination
- **Assess intent** — messaging language alone cannot prove intent
- **Account for context** — tone, relationship history, cultural factors require human assessment
- **Replace expert evidence** — qualified practitioners must interpret findings
- **Guarantee completeness** — absence of indicators ≠ absence of abuse

### Ethical Guidelines for Tool Operators

```python
ETHICAL_GUIDELINES = [
    'NEVER present automated findings as conclusions of fact',
    'ALWAYS include disclaimers in output documents',
    'Screen for mandatory reporting triggers BEFORE detailed analysis',
    'Provide full context — never cherry-pick supporting indicators',
    'Include counter-indicators and limitations in reports',
    'Flag when expert assessment is required',
    'Respect that both parties may have legitimate grievances',
    'Do not assume guilt or victimhood based on messaging alone',
    'Protect child safety above all other considerations',
]
```
