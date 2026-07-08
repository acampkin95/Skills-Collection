---
name: legal-check
description: Australian legal information and rights awareness. Use when user asks about legal rights, what they can/cannot do, what the law says, their options, or needs to understand a legal document or situation.
user-invocable: true
---

# Legal Awareness — Australian Rights & Options

Use this skill when the user needs to understand their legal rights, obligations, options, or what the law says about a situation. Distinguish clearly between **legal information** (educational) and **legal advice** (recommendation to act).

## When to Use

- "What are my rights?"
- "Is this legal / Can I do this?"
- "What does the law say about...?"
- Understanding a legal document, letter, or notice
- "What are my options in this situation?"
- WA/Australian law questions
- Tenant, employee, consumer rights

## The Critical Distinction

```
⚠️ LEGAL INFORMATION (this skill)          ⚠️ LEGAL ADVICE (refer out)
─────────────────────────────────────────────────────────────────────────
Explains what the law says                 Recommends a specific action
Describes rights and obligations           Predicts outcomes of a strategy
Interprets legislation and cases           Tells you what to do in court
Provides general knowledge                 Assesses your specific facts
─────────────────────────────────────────────────────────────────────────
"Under the RTA 1987 (WA), a landlord        "You should apply to SAT for
must give 60 days notice to end a          this order within 21 days."
periodic tenancy."                          ─────────────────────────────────
```

**Rule:** Always state the information/advice distinction. Never predict case outcomes or guarantee legal positions.

## Australian Legal Knowledge Base

### Western Australia — Key Frameworks

| Area | Legislation | Key Body |
|------|-------------|----------|
| Family violence | Restraining Orders Act 1997 (WA) s61B | SAT (Minor case), DC (Indictable) |
| Residential tenancy | Residential Tenancies Act 1987 (WA) | SAT |
| Employment | Fair Work Act 2009 (Cth) | Fair Work Commission |
| Consumer rights | Australian Consumer Law (Cth) | ACCC, WA Consumer Protection |
| Privacy | Privacy Act 1988 (Cth) | OAIC |
| Strata | Strata Titles Act 1985 (WA) | SAT |
| Criminal | Criminal Code Act Compilation Act 1913 (WA) | Courts |

### Common Situations — Quick Reference

#### Renting in WA

```python
tenant_rights_wa = {
    "notice_end_tenancy": "60 days (periodic) / 30 days (fixed-term ends)",
    "bond_max": "4 weeks rent",
    "landlord_entry": "48 hours notice required (generally)",
    "repairs": "Must be notified in writing, landlord has 14 days",
    "unlawful_eviction": "Landlord must get SAT order, police only for SQ",
    "rent_increase": "60 days written notice, no limit (but excessive can be challenged)",
    "break_lease": "Tenant liable for reletting costs + rent until re-let"
}
```

#### Employment in WA

```python
employee_rights = {
    "min_wage": "$24.10/hr (adult, 2025), $23.68 from 1 July 2026",
    "overtime": "150% (first 3hrs), 200% (after)",
    "casual_conversion": "After 6 months, can request permanent",
    "unfair_dismissal": "If earned <$175K, apply to FWC within 21 days",
    "leave_loading": "17.5% on annual leave",
    "parental_leave": "Govt PPL 18 weeks ($922.99/wk), employer may top up"
}
```

#### Consumer Rights (AU)

```python
consumer_rights = {
    "guarantee_services": "Acceptable quality, fitness for purpose, reasonable time",
    "refund_rights": "Faulty goods → refund/replacement/repair",
    "major_problems": "Can reject goods and get refund",
    "cooling_off": "Some contracts (door-to-door, health clubs) — 10 days",
    "misleading_conduct": "Can claim damages, rescission",
    "unconscionable": "Court can set aside contract if unfairly exploited"
}
```

## Document Analysis Pattern

When the user shares a legal document:

```python
def analyse_legal_document(text: str, doc_type: str) -> dict:
    """Standard legal document analysis."""
    
    if doc_type == "notice":
        return {
            "type": identify_notice_type(text),  # eviction, breach, termination
            "sender": extract_sender(text),
            "recipient": extract_recipient(text),
            "legal_basis": identify_legislation_cited(text),
            "key_facts": extract_key_facts(text),
            "deadline": extract_deadline(text),
            "options": list_available_options(text),
            "warnings": flag_problems(text)  # missing info, short deadlines
        }
    
    elif doc_type == "contract":
        return {
            "parties": extract_parties(text),
            "key_obligations": extract_obligations(text),
            "key_dates": extract_dates(text),
            "penalties": extract_penalties(text),
            "termination": extract_termination_clauses(text),
            "concerns": flag_unusual_terms(text),
            "questions": suggest_questions(text)
        }
    
    elif doc_type == "court_document":
        return {
            "jurisdiction": identify_court(text),
            "type": identify_document_type(text),
            "parties": extract_parties(text),
            "relief_sought": extract_claims(text),
            "legal_basis": extract_legislation_cases(text),
            "deadlines": extract_time_limits(text),
            "response_options": list_response_options(text)
        }
}
```

## Explaining Legal Concepts

### Structure for Complex Topics

```markdown
## [Topic] — Legal Information

**Short answer:** [1-2 sentences, directly]

### The Basic Rule
[What the law says in plain language]

### Key Conditions
- [Condition 1 — what must be true for this to apply]
- [Condition 2]
- [Condition 3]

### Exceptions
- [Exception 1 — when the basic rule doesn't apply]
- [Exception 2]

### Your Options
1. **[Option 1]** — [when to consider this, generally what it involves]
2. **[Option 2]** — [when to consider this]
3. **[Option 3]** — [when to consider this]

### What to Do Next
- [Practical next step]
- [Where to get more information]

### Important Caveat
[This is general legal information, not legal advice.
For your specific situation, consult a qualified Australian lawyer.]
```

## Flagging Urgency

```python
def flag_legal_urgency(text: str) -> dict:
    """Detect time-sensitive legal situations."""
    
    urgent_signals = {
        "court_deadline": ["within 21 days", "28 days", "must file", "hearing date"],
        "eviction": ["vacate", "possession", "termination notice", "SQ order"],
        "police": ["charge", "summons", "court date", "police notice"],
        "consumer": ["dispute", "refund", "contract termination"],
        "employment": ["dismissal", "termination", "notice period", "redundancy"]
    }
    
    flags = []
    for category, signals in urgent_signals.items():
        if any(sig in text.lower() for sig in signals):
            flags.append(category)
    
    return {
        "urgent": len(flags) > 0,
        "categories": flags,
        "message": "This involves time-sensitive legal matters. "
                   "Seek advice promptly." if flags else ""
    }
```

## Australian Legal Resources

| Resource | URL | Use For |
|----------|-----|---------|
| AustLII | austlii.edu.au | WA legislation, case law |
| WA State Law Publisher | slp.wa.gov.au | WA legislation official |
| Legal Aid WA | legalaid.wa.gov.au | Means-tested legal help |
| Law Society WA | lawsocietywa.asn.au | Lawyer referral |
| Fair Work Commission | fw.gov.au | Employment disputes |
| SAT | sat.uwa.edu.au | Tenancy, strata, minor civil |
| Consumer Protection WA | consumerprotection.wa.gov.au | Consumer complaints |
| OAIC | oaic.gov.au | Privacy complaints |

## Anti-Legal-Advice Failure Rules

1. **Never say "you should"** — say "you may consider" or "one option is"
2. **Never predict outcomes** — "Courts may consider... but the outcome depends on..."
3. **Always distinguish jurisdiction** — WA vs Cth matters
4. **Always cite the legislation** — "s61B of the Restraining Orders Act 1997 (WA)"
5. **Always add the disclaimer** — "This is general legal information, not legal advice"
6. **Never assess evidence quality** — "I can't assess the strength of evidence"
7. **Refer complex matters** — if beyond general information, recommend a lawyer