# Family Law Evidence Standards — Digital Communications

> **Jurisdiction**: Federal Circuit and Family Court of Australia (FCFCOA), Family Court of WA
> **Core sources**: Family Law Act 1975 (Cth), Evidence Act 1995 (Cth), Federal Circuit and Family Court of Australia (Family Law) Rules 2021, Family Court Act 1997 (WA), Family Court Rules 2021 (WA where applicable)
> **Currency rule**: Verify the current court, rules, practice directions, and filing portal requirements before preparing family law evidence.

---

## Table of Contents

1. [Legislative Framework](#1-legislative-framework)
2. [SMS/Messaging Evidence Admissibility](#2-smsmessaging-evidence-admissibility)
3. [Affidavit Annexure Standards](#3-affidavit-annexure-standards)
4. [Children's Cases — Flexible Evidence Rules](#4-childrens-cases--flexible-evidence-rules)
5. [Family Violence Evidence Assessment](#5-family-violence-evidence-assessment)
6. [Section 138 — Improperly Obtained Evidence](#6-section-138--improperly-obtained-evidence)
7. [Surveillance Devices Act 1998 (WA)](#7-surveillance-devices-act-1998-wa)
8. [Expert Evidence Requirements](#8-expert-evidence-requirements)
9. [Mandatory Reporting Triggers](#9-mandatory-reporting-triggers)
10. [Evidence Preparation Workflow](#10-evidence-preparation-workflow)
11. [Admissibility Roadmap for Messaging Evidence](#11-admissibility-roadmap-for-messaging-evidence)

---

## 1. Legislative Framework

### Family Law Act 1975 (Cth)

**Sections 69ZT–69ZX: Evidence in Children's Cases**

- **s69ZT**: The court is NOT bound by the Evidence Act 1995 in child-related proceedings unless it chooses to apply it. Provides flexibility for informal evidence including messages.
- **s69ZV**: Hearsay laws do not exclude representations made by a child about matters relevant to the child's welfare.
- **s69ZX**: Courts have broad discretion to manage evidence in children's interests.

**Section 67ZBA: Family Violence Allegations**
When family violence is alleged, a notice must be filed and served. The court must act expeditiously under s67ZBB to obtain evidence and assess interim protective orders.

**Section 67Z: Child Abuse Allegations**
Requires prompt court action when child abuse is alleged.

### Family Law Rules / Family Court Rules

Use the FCFCOA Family Law Rules for federal family law proceedings and the Family Court WA rules for WA Family Court matters. Do not assume the same rule number applies in both courts.

**Affidavit requirements to verify**
- Documents referred to in an affidavit must be annexed (exhibited)
- Each annexure must include a signed identification statement
- Annexures are NOT automatically admitted into evidence — they must be tendered
- Electronic filing requirements depend on the court, portal, and current practice direction

Check the current rules and practice directions for formatting, page limits, annexures, and eFiling.

---

## 2. SMS/Messaging Evidence Admissibility

### General Position

SMS, WhatsApp, Facebook Messenger, email, and similar digital communications may be admissible if relevant, authentic, lawfully obtained or admitted despite any impropriety, and presented with sufficient context. Do not claim a category of message evidence is automatically admissible or uniquely important; weight depends on authenticity, completeness, context, and the issues in dispute.

### Authentication Requirements

```python
SMS_AUTHENTICATION_CHECKLIST = {
    'provenance': {
        'description': 'Establish who sent/received the message',
        'methods': [
            'Phone number or user account linked to the party',
            'Corroboration by recipient (acknowledgment, reply)',
            'Metadata (timestamp, sender ID) where available',
            'Contextual evidence (only parties to dispute had this number)',
        ],
        'required': True,
    },
    'completeness': {
        'description': 'Full context and chronological thread',
        'methods': [
            'Full conversation threads (not isolated messages)',
            'Export entire thread with headers showing all participants',
            'Note any gaps and reasons for gaps',
        ],
        'required': True,
        'note': 'Isolated screenshots = weak evidence; cherry-picking draws adverse inference',
    },
    'authenticity': {
        'description': 'Evidence has not been altered or fabricated',
        'methods': [
            'Native file exports preferred over screenshots',
            'Metadata (timestamps, device info) preserved',
            'If screenshots: supported by metadata or witness corroboration',
        ],
        'required': True,
    },
    'legal_acquisition': {
        'description': 'Message was lawfully obtained',
        'methods': [
            'From deponent\'s own device/account',
            'Received as a party to the conversation',
            'Subpoenaed from carrier or platform',
        ],
        'required': True,
        'note': 'If unlawfully obtained, s138 balancing test applies — may still be admitted',
    },
}
```

### Native Files vs Screenshots

| Evidence Type | Strength | Metadata | Court Preference |
|--------------|----------|----------|-----------------|
| Native export (CSV/JSON) | Strong | Full timestamps, sender IDs | Preferred |
| Platform export (WhatsApp HTML) | Strong | Platform-verified timestamps | Preferred |
| Screenshot with full thread | Medium | Limited (visible timestamp only) | Acceptable |
| Isolated screenshot | Weak | Minimal | Disfavoured |
| Verbal description of messages | Very Weak | None | Usually poor evidence; seek corroboration or source records |

### Metadata Preservation Issues

- EXIF metadata in photos/MMS includes: timestamp, geolocation, device identifier
- **Critical caveat**: Messaging platforms often strip EXIF data during transmission
- Screenshots do NOT retain underlying device metadata
- For photo/MMS evidence: preserve original files before forwarding

---

## 3. Affidavit Annexure Standards

### Affidavit Annexure Cover Sheet

Verify the current rule and registry practice before filing. A common cover sheet format is:

**Annexure Cover Sheet Format**:

```text
ANNEXURE [X]

This is the document referred to as Annexure [X] in the affidavit of
[Full Name] sworn/affirmed at [Place] on [Date] before me.

[Signature of witness]
[Name and Qualification of witness]
```

### Best Practice for CSV/Messaging Annexures

```python
ANNEXURE_REQUIREMENTS = [
    'Chronological order (earliest first)',
    'Full thread context — no isolated messages',
    'Timestamps in local time (AWST if WA) with timezone noted',
    'Sender/recipient identifiers clearly visible',
    'Gaps in thread explicitly noted with reason',
    'Page numbers on every page',
    'Legible at 100% zoom (minimum 10pt font)',
    'Deponent verification statement in affidavit body',
]

DEPONENT_VERIFICATION_TEMPLATE = """
I am the owner of the mobile telephone number [XXX]. I have accessed the
[platform] message history between myself and [Party B] covering the period
[Date] to [Date]. I have exported the conversation to a [format] file on
[Date] and have since kept it secured on [storage location]. The export is
true and complete to the best of my knowledge and belief. The timestamps
shown are in [timezone].
"""
```

### CSV-to-Annexure Formatting

```python
def format_messages_for_annexure(df, sender_map, timezone='AWST (UTC+8)'):
    """
    Format a messaging DataFrame for court annexure.

    sender_map: dict mapping addresses to display names
    Returns: formatted text suitable for DOCX/PDF generation
    """
    lines = []
    lines.append(f"MESSAGE THREAD: {sender_map.get('_title', 'Communications')}")
    lines.append(f"Period: {df['timestamp'].min()} to {df['timestamp'].max()}")
    lines.append(f"Timezone: {timezone}")
    lines.append(f"Total messages: {len(df):,}")
    lines.append("=" * 60)

    prev_date = None
    for _, row in df.iterrows():
        msg_date = str(row.get('timestamp', ''))[:10]
        if msg_date != prev_date:
            lines.append(f"\n--- {msg_date} ---\n")
            prev_date = msg_date

        sender = sender_map.get(row.get('sender', ''), row.get('sender', 'Unknown'))
        timestamp = row.get('timestamp', '')
        body = row.get('body', '')
        msg_id = row.get('message_id', '')

        lines.append(f"[{timestamp}] {sender}:")
        lines.append(f"  {body}")
        lines.append(f"  (ID: {msg_id})")
        lines.append("")

    return "\n".join(lines)
```

---

## 4. Children's Cases — Flexible Evidence Rules

### Section 69ZT Application

In children's cases (Part VII proceedings), the court may:
- Accept evidence that would otherwise be inadmissible (hearsay, opinion)
- Give appropriate weight to informal evidence (including unverified messages)
- Prioritise the best interests of the child over procedural strictness

**Practical implication**: SMS evidence in children's matters has a lower admissibility threshold than in property or general civil proceedings.

### Section 69ZV: Children's Representations

Hearsay rules do NOT exclude statements made by a child about matters relevant to their welfare. Messages from or about a child (e.g., "Dad hit me" sent to a friend) may be admitted as evidence of the child's experience.

---

## 5. Family Violence Evidence Assessment

### WA Family Violence Legislation Reform Act 2020

Explicitly recognises technology-facilitated abuse:
> "Using technology to threaten, humiliate, harass, stalk, intimidate, exert undue influence over, or abuse the other party, including by engaging in cyberstalking, monitoring, surveillance, impersonation, manipulation of electronic media, or distribution of or threats to distribute actual or fabricated intimate images."

### Pattern Evidence from Messaging

Courts assess family violence as a **pattern of behaviour**, not isolated incidents. Messaging evidence is critical for establishing:

```python
PATTERN_EVIDENCE_ELEMENTS = {
    'temporal_pattern': 'Frequency, timing, and escalation of messages over time',
    'control_indicators': 'Directives, ultimatums, monitoring language',
    'threat_escalation': 'Progression from negotiation to intimidation to threats',
    'isolation_tactics': 'Demands to cut contact, surveillance of relationships',
    'response_dynamics': 'Power imbalance visible in communication patterns',
    'impact_on_children': 'Messages referencing children as leverage or targets',
}
```

→ See `coercive-control-frameworks.md` for detailed research-backed analysis framework

---

## 6. Section 138 — Improperly Obtained Evidence

### Application in Family Law

Evidence obtained in breach of law (e.g., accessing another party's phone without consent) is assessed under a balancing test:

**Factors favouring admission in family law**:
- Child safety is at stake
- Evidence reveals abuse or family violence
- No alternative means to obtain the evidence
- Probative value is high (direct evidence of the issue)

**Factors against admission**:
- Deliberate, calculated privacy breach
- Evidence could have been obtained lawfully (e.g., subpoena to carrier)
- Disproportionate invasion of privacy
- Evidence is tangential to central issues

```python
def flag_s138_issues(evidence_metadata):
    """Flag evidence that may require s138 assessment."""
    flags = []

    if evidence_metadata.get('source') == 'other_party_device':
        flags.append({
            'issue': 'Evidence obtained from other party\'s device',
            'section': 'Evidence Act 1995 s138',
            'assessment': 'Balancing test required — probative value vs. method of obtaining',
            'factors': [
                'Was consent given?',
                'Was there a lawful alternative (subpoena, discovery)?',
                'Does it relate to child safety or family violence?',
                'How was access obtained?',
            ]
        })

    if evidence_metadata.get('intercepted_communication'):
        flags.append({
            'issue': 'Intercepted communication',
            'section': 'Telecommunications (Interception) Act 1979 (Cth)',
            'note': 'Criminal offence to intercept; s138 balancing still applies to admissibility'
        })

    return flags
```

---

## 7. Surveillance Devices Act 1998 (WA)

### Key Provisions

**Sections 5–6**: Offence to record a private conversation or activity without consent.
- Penalty: up to $5,000 fine and/or imprisonment
- **Exception**: A principal party may record if "reasonably necessary for the protection of the lawful interests of that principal party"

### Application to Messaging Evidence

- **Written messages (SMS, WhatsApp, email)**: NOT covered by the Surveillance Devices Act — these are written, not audio/visual
- **Voice messages/calls**: Covered — recording without consent is an offence
- **Accessing another's phone/account**: May breach Computer Crimes Act or privacy law, but written messages themselves are not "surveillance devices" evidence

```python
def assess_surveillance_devices_act(evidence_type, acquisition_method):
    """Assess Surveillance Devices Act 1998 (WA) implications."""
    if evidence_type in ('sms', 'whatsapp_text', 'email', 'messenger_text'):
        return {
            'act_applies': False,
            'note': 'Written messages not covered by SDA 1998 (WA) — ss 5-6 apply to audio/visual only',
            'caveat': 'Access method may still raise privacy/computer crimes issues'
        }
    elif evidence_type in ('voice_message', 'recorded_call', 'video_call'):
        return {
            'act_applies': True,
            'note': 'Audio/visual recordings covered by SDA 1998 (WA)',
            'exception': 'Principal party exception if recording was reasonably necessary for protection of lawful interests',
            'criminal_liability': 'Recording without consent is an offence regardless of admissibility'
        }
    return {'act_applies': 'UNKNOWN', 'note': 'Assess on facts'}
```

---

## 8. Expert Evidence Requirements

### When Expert Analysis is Required

| Situation | Expert Required? | Type of Expert |
|-----------|-----------------|----------------|
| Provenance uncontested | No | — |
| Authenticity disputed | Yes | Digital forensics |
| Timestamp challenged | Yes | Platform/forensic specialist |
| Screenshot manipulation alleged | Yes | Image forensics |
| Coercive control pattern | Sometimes | Family violence expert |
| Deleted message recovery | Yes | Digital forensics |

### When Parties Can Present Evidence Themselves

In family law, parties should not dispute facts without a proper basis. If authenticity is contested without genuine grounds, costs or credibility consequences may arise, but the risk depends on the rules, orders, and facts.

Self-represented litigants can present messaging evidence directly if:
- Messages are from their own device/account
- Authenticity is not genuinely in dispute
- Full context is provided
- Proper affidavit verification statement included

---

## 9. Mandatory Reporting Triggers

### WA Mandatory Reporting (Children and Community Services Act 2004)

WA mandatory reporting is specific and role-dependent. Teachers and other prescribed mandatory reporters must report child sexual abuse when the statutory threshold is met. Other child protection concerns may still require reports or referrals under different policies or duties, but do not describe all abuse/neglect concerns as mandatory reports for every listed profession without checking the current Act and role.

### Messaging Content Triggers

```python
MANDATORY_REPORTING_FLAGS = {
    'direct_child_abuse_disclosure': {
        'patterns': [
            r'\b(dad|mum|father|mother|parent)\s+(hit|hurt|beat|punch|kick|burn)',
            r'\b(he|she)\s+(hit|hurt|beat)\s+(me|the\s+kid|the\s+child)',
            r'\bdon\'?t\s+tell\s+anyone',
        ],
        'severity': 'CRITICAL',
        'action': 'FLAG FOR IMMEDIATE MANDATORY REPORT REVIEW',
    },
    'child_endangerment_threat': {
        'patterns': [
            r'\b(take|keep)\s+the\s+(kids?|children)',
            r'\bnever\s+see\s+(him|her|them)\s+again',
            r'\b(drunk|high|wasted)\b.*\b(kids?|children|baby)',
        ],
        'severity': 'HIGH',
        'action': 'Flag for practitioner review — may trigger reporting obligation',
    },
    'sexual_abuse_indicators': {
        'patterns': [
            r'\b(touch|touching)\b.*\b(child|kids?|little)',
            r'\binappropriate\b.*\b(child|minor|kids?)',
        ],
        'severity': 'CRITICAL',
        'action': 'FLAG FOR IMMEDIATE MANDATORY REPORT REVIEW',
    },
    'severe_psychological_harm': {
        'patterns': [
            r'\b(worthless|useless|stupid)\b.*\b(kid|child|son|daughter)',
            r'\bsuicid',
            r'\bkill\s+(myself|yourself|himself|herself)',
        ],
        'severity': 'HIGH',
        'action': 'Flag for practitioner review',
    },
    'neglect_indicators': {
        'patterns': [
            r'\bno\s+food\b', r'\bnot\s+fed\b',
            r'\bleft\s+alone\b.*\b(child|kids?|baby)',
            r'\bno\s+(doctor|medical|medicine)',
        ],
        'severity': 'HIGH',
        'action': 'Flag for practitioner review',
    },
}


def screen_for_mandatory_reporting(df, text_column):
    """
    Screen messaging data for mandatory reporting triggers.

    WARNING: This is a screening tool, not a diagnostic tool.
    Flagged content must be reviewed by a qualified professional.
    Mandatory reporters have independent legal obligations.
    """
    import re
    flags = []

    for category, config in MANDATORY_REPORTING_FLAGS.items():
        for pattern in config['patterns']:
            mask = df[text_column].str.contains(pattern, case=False, regex=True, na=False)
            hits = df[mask]
            if len(hits) > 0:
                for idx, row in hits.iterrows():
                    flags.append({
                        'message_id': row.get('message_id', idx),
                        'category': category,
                        'severity': config['severity'],
                        'action': config['action'],
                        'text_preview': str(row[text_column])[:200],
                        'timestamp': row.get('timestamp', ''),
                        'sender': row.get('sender', ''),
                    })

    if flags:
        print(f"\n⚠️  MANDATORY REPORTING SCREENING: {len(flags)} potential flags identified")
        print("These flags require review by a qualified professional.")
        print("If you are a mandatory reporter, you may have legal obligations to report.\n")

        critical = [f for f in flags if f['severity'] == 'CRITICAL']
        if critical:
            print(f"🔴 CRITICAL flags: {len(critical)} — require immediate review")

    return flags
```

---

## 10. Evidence Preparation Workflow

### Complete Family Law Messaging Evidence Workflow

```
1. RECEIVE DATA
   ├─ Hash original file (SHA-256)
   ├─ Record chain of custody
   └─ Create working copy

2. PROFILE & VALIDATE
   ├─ Identify source tool (Cellebrite, iMazing, native export)
   ├─ Map to canonical schema
   ├─ Validate timestamps, sender IDs
   └─ Flag data quality issues

3. SCREEN & CLASSIFY
   ├─ Mandatory reporting screening (FIRST — before detailed analysis)
   ├─ Keyword search for relevant themes
   ├─ Coercive control pattern detection
   └─ Privilege detection (if solicitor communications present)

4. ANALYSE
   ├─ Timeline reconstruction
   ├─ Temporal clustering analysis
   ├─ Communication network mapping
   ├─ Threat escalation tracking
   └─ Cross-reference with other evidence

5. PREPARE OUTPUT
   ├─ Format messages for annexure (chronological, complete, legible)
   ├─ Generate deponent verification statement
   ├─ Create evidence summary report
   ├─ Verify hash integrity of all output files
   └─ Note any gaps, exclusions, or limitations

6. VERIFY
   ├─ Cross-check original hash
   ├─ Confirm completeness (no missing threads)
   ├─ Review mandatory reporting flags
   └─ Final admissibility checklist
```

---

## 11. Admissibility Roadmap for Messaging Evidence

```python
def messaging_admissibility_roadmap(evidence_metadata):
    """
    Step-by-step admissibility assessment for messaging evidence in family law.
    """
    steps = []

    # Step 1: Relevance
    steps.append({
        'step': 1,
        'name': 'Relevance',
        'question': 'Is the message content relevant to the issue before the court?',
        'issues': ['parenting', 'property', 'family violence', 'child safety'],
        'if_no': 'Exclude or flag as low probative value',
    })

    # Step 2: Authentication
    steps.append({
        'step': 2,
        'name': 'Authentication',
        'question': 'Is sender/recipient identity clear?',
        'methods': ['Phone number linked to party', 'Reply context confirms identity',
                    'Metadata present', 'Platform export with headers'],
        'if_no': 'Flag for affidavit verification or forensic authentication',
    })

    # Step 3: Completeness
    steps.append({
        'step': 3,
        'name': 'Completeness',
        'question': 'Is the message part of a full thread or isolated?',
        'if_isolated': 'Mark as potentially weak — full context required',
        'if_gaps': 'Document gaps with explanation',
    })

    # Step 4: Legal acquisition
    steps.append({
        'step': 4,
        'name': 'Legal Acquisition',
        'question': 'Was the message obtained lawfully?',
        'if_no': 'Apply s138 balancing test — may still be admitted',
        'factors': ['Child safety relevance', 'Alternative means available',
                    'Severity of alleged conduct'],
    })

    # Step 5: Proceedings type
    steps.append({
        'step': 5,
        'name': 'Proceedings Type',
        'question': 'Is this a children\'s case (Part VII)?',
        'if_yes': 's69ZT flexibility — court not bound by Evidence Act',
        'if_no': 'Standard evidence rules apply (with s138 discretion)',
    })

    # Step 6: Pattern context (for coercive control)
    steps.append({
        'step': 6,
        'name': 'Pattern Context',
        'question': 'Does this message form part of an alleged pattern of behaviour?',
        'if_yes': 'Provide temporal context, clustering analysis, escalation timeline',
        'note': 'Single messages rarely establish coercive control',
    })

    return steps
```
