# Psychology Framework Reference

## Attachment Theory

Based on Bowlby & Ainsworth's attachment theory, adapted for text analysis.

### Attachment Styles

| Style | Core Fear | Communication Pattern |
|-------|-----------|----------------------|
| Secure | None (healthy) | Balanced, collaborative, "we" language |
| Anxious-Preoccupied | Abandonment | Excessive reassurance-seeking, apologetic |
| Dismissive-Avoidant | Intimacy | Brief, distant, deflecting |
| Fearful-Avoidant | Both | Inconsistent, hot-cold cycling |

### Detection Thresholds

| Marker | Threshold | Interpretation |
|--------|-----------|----------------|
| Anxious | >200 markers | High anxiety attachment |
| Avoidant | >150 markers | Dismissive patterns |
| Controlling | >100 markers | Potential coercive control |
| Secure | >300 markers | Healthy communication |

### Anxious-Avoidant Trap

When one partner is anxious and the other avoidant:
- Anxious pursues → Avoidant withdraws → Anxious escalates → Avoidant shuts down
- Creates pursue-withdraw cycle
- Detection: High anxious markers in one sender, high avoidant in other

## Manipulation Patterns

### Love Bombing

**Definition**: Overwhelming affection to gain control, followed by withdrawal.

**Detection Algorithm**:
```python
daily_love = SUM(has_love_words + has_affection)
rolling_avg = 3-day rolling average
spike = daily_love > (rolling_avg * 3)
```

**Thresholds**:
| Spikes | Interpretation |
|--------|----------------|
| 0-20 | Normal variation |
| 20-50 | Mild pattern |
| 50-100 | Moderate concern |
| >100 | Strong love bombing |

### Withdrawal

**Definition**: Sudden emotional distancing after bonding.

**Detection**:
```python
withdrawal = daily_love < (rolling_avg / 3) AND rolling_avg > 2
```

### Intermittent Reinforcement

**Definition**: Unpredictable rewards creating trauma bonding.

**Detection**: Count spike-withdrawal sequences within 7 days.

| Cycles | Interpretation |
|--------|----------------|
| 0-30 | Normal fluctuation |
| 30-100 | Concerning pattern |
| >100 | Strong intermittent reinforcement |

**Psychological Impact**: Creates dopamine-seeking behavior, harder to leave relationship.

## Love:Negative Ratio

Adapted from Gottman's 5:1 ratio research.

| Ratio | Phase | Health |
|-------|-------|--------|
| >5.0 | Honeymoon | Intense bonding (unsustainable) |
| 4.0-5.0 | Early stable | Healthy start |
| 3.0-4.0 | Settled | Healthy relationship |
| 2.0-3.0 | Routine | Normal, some tension |
| 1.5-2.0 | Strained | Emerging issues |
| 1.0-1.5 | Conflict | Active problems |
| <1.0 | Critical | Relationship breakdown |

**Inversion Point**: When ratio drops below 1.0, negative exceeds positive. Major red flag.

## Communication Dynamics

### Double-Texting

Sending 2 consecutive messages before response.

| Frequency | Pattern |
|-----------|---------|
| Occasional | Normal |
| Frequent (>500) | Anxiety marker |
| Asymmetric | One-sided effort |

### Message Flooding

Sending 3+ consecutive messages.

| Sender Pattern | Interpretation |
|----------------|----------------|
| Both equal | Excited communication |
| One-sided high | Desperation/anxiety |
| After conflict | Damage control |

### Response Time

| Average | Interpretation |
|---------|----------------|
| <5 min | High engagement |
| 5-30 min | Normal |
| 30-60 min | Busy/distracted |
| >60 min | Low priority/avoidant |

**Asymmetry**: If one sender consistently responds faster, indicates unequal investment.

### Initiation Ratio

Who starts conversations more often.

| Split | Pattern |
|-------|---------|
| 50/50 | Balanced |
| 60/40 | Slight asymmetry |
| 70/30 | One-sided pursuit |
| >80/20 | Severe imbalance |

## Red Flags Summary

### Communication Red Flags
1. **Message asymmetry** >60/40
2. **Response time gap** >2x difference
3. **Triple+ flooding** heavily skewed
4. **Word count gap** >50% difference

### Psychological Red Flags
1. **Love bombing** >50 spikes
2. **Intermittent reinforcement** >50 cycles
3. **Ratio inversion** <1.0
4. **Anxious-avoidant trap** detected
5. **High controlling markers** >100

### Temporal Red Flags
1. **Rapid ratio decline** (>2 points in 3 months)
2. **Increasing conflict days** trend
3. **Decreasing secure markers** trend
4. **Night-only communication** shift

## Conflict Analysis

### Severity Levels

| Conflict Msgs/Day | Severity |
|-------------------|----------|
| 3-5 | Low |
| 5-10 | Moderate |
| 10-15 | High |
| >15 | Critical |

### High-Conflict Days

Days with ≥5 conflict markers warrant review:
- What triggered the conflict?
- How was it resolved (or not)?
- Pattern across multiple high-conflict days?

## Third-Party Context

### Significant Mentions

People mentioned frequently provide relationship context:
- **Therapist**: Indicates awareness of issues
- **Ex**: May indicate unresolved past
- **Parents**: Family involvement level
- **Friends**: Support network presence

### Relationship Term Analysis

| Term Frequency | Interpretation |
|----------------|----------------|
| "ex" high | Past relationship issues |
| "therapist" present | Seeking help |
| "friends" high | Strong support network |
| "mum/dad" high | Family involvement |
