# eDiscovery Protocols — CSV Review

## Table of Contents

1. [Scope Definition & Matter Setup](#1-scope-definition--matter-setup)
2. [Keyword Search & KWIC](#2-keyword-search--kwic)
3. [Responsiveness Coding](#3-responsiveness-coding)
4. [Privilege Review & Privilege Log](#4-privilege-review--privilege-log)
5. [Categorisation Framework](#5-categorisation-framework)
6. [Custodian Mapping](#6-custodian-mapping)
7. [Quality Control & Sampling](#7-quality-control--sampling)
8. [Production Preparation](#8-production-preparation)
9. [Default Search Term Libraries](#9-default-search-term-libraries)

---

## 1. Scope Definition & Matter Setup

Before any review begins, document the scope. This forms the basis for all responsiveness decisions.

### Matter Scope Template

```
MATTER SCOPE DEFINITION
════════════════════════
Matter name/reference: ______________
Date range: ______________ to ______________
Custodians in scope: [list all named custodians/data sources]
Key entities (parties, companies, individuals): [list]
Subject matter: [description of what the dispute/matter is about]
Key issues: [numbered list of legal issues to be addressed]

SEARCH STRATEGY
Search terms: [list all approved keywords]
Boolean logic: [describe how terms relate — AND/OR/NOT groupings]
Proximity operators: [e.g., "payments" within 5 words of "offshore"]
Exclusions: [what is out of scope — e.g., IT help desk emails]

PRIVILEGE CRITERIA
Attorney-client privilege markers: [legal counsel names/domains]
Litigation privilege markers: [matter names, "without prejudice", etc.]
Third-party markers: [accountants, doctors if applicable]
```

---

## 2. Keyword Search & KWIC

### Boolean Keyword Search

```python
import pandas as pd
import re

def boolean_search(df, text_columns, search_terms, operator='OR', case_sensitive=False):
    """
    Boolean keyword search across specified text columns.

    Args:
        df: DataFrame
        text_columns: list of column names to search
        search_terms: list of keyword strings or regex patterns
        operator: 'OR' (any term) or 'AND' (all terms must appear)
        case_sensitive: default False

    Returns:
        DataFrame with _keyword_hit = True for matching rows,
        _matched_terms = pipe-separated list of matched terms
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    df_result = df.copy()
    df_result['_keyword_hit'] = False
    df_result['_matched_terms'] = ''

    # Combine all text columns into a single searchable field
    df_result['_combined_text'] = df_result[text_columns].fillna('').agg(' '.join, axis=1)

    for term in search_terms:
        try:
            mask = df_result['_combined_text'].str.contains(term, flags=flags, regex=True, na=False)
            df_result.loc[mask, '_keyword_hit'] = True
            df_result.loc[mask, '_matched_terms'] += f"|{term}"
        except re.error as e:
            print(f"Invalid regex term '{term}': {e}")

    if operator == 'AND':
        # Must match ALL terms — recalculate
        all_matches = pd.Series([True] * len(df_result))
        for term in search_terms:
            try:
                mask = df_result['_combined_text'].str.contains(term, flags=flags, regex=True, na=False)
                all_matches &= mask
            except re.error:
                pass
        df_result['_keyword_hit'] = all_matches

    hits = df_result[df_result['_keyword_hit'] == True]
    print(f"Keyword hits: {len(hits):,} rows ({len(hits)/len(df)*100:.1f}% of dataset)")
    print(f"Hit breakdown by term:")
    for term in search_terms:
        count = df_result['_combined_text'].str.contains(term, flags=flags, regex=True, na=False).sum()
        print(f"  '{term}': {count:,} rows")

    return df_result, hits
```

### KWIC — Keyword in Context

```python
def kwic(df, text_column, search_term, context_chars=150, max_results=500, case_sensitive=False):
    """
    Keyword In Context (KWIC) output for a specific search term.
    Shows the keyword with surrounding text for rapid human review.

    Returns a DataFrame with columns:
        - original_row_index, [all original columns], kwic_snippet
    """
    flags = re.IGNORECASE if not case_sensitive else 0
    results = []

    for idx, text in df[text_column].dropna().items():
        text_str = str(text)
        for match in re.finditer(search_term, text_str, flags=flags):
            start = max(0, match.start() - context_chars)
            end = min(len(text_str), match.end() + context_chars)
            snippet = (
                ("..." if start > 0 else "") +
                text_str[start:match.start()] +
                f"[[ {match.group()} ]]" +  # Highlight the match
                text_str[match.end():end] +
                ("..." if end < len(text_str) else "")
            )
            row_data = df.loc[idx].to_dict()
            row_data['_kwic_snippet'] = snippet
            row_data['_kwic_match'] = match.group()
            row_data['_kwic_position'] = match.start()
            row_data['_original_row_index'] = idx
            results.append(row_data)
            if len(results) >= max_results:
                print(f"KWIC capped at {max_results} results. Refine search term to see all.")
                return pd.DataFrame(results)

    print(f"KWIC results for '{search_term}': {len(results):,} matches")
    return pd.DataFrame(results)

# Usage
kwic_results = kwic(df, 'body', r'payment[s]?\s+offshore', context_chars=200)
kwic_results[['_original_row_index', 'date', 'sender', '_kwic_snippet']].to_csv('kwic_payment_offshore.csv', index=False)
```

### Proximity Search

```python
def proximity_search(df, text_column, term1, term2, within_words=5, case_sensitive=False):
    """
    Find rows where term1 and term2 appear within N words of each other.
    """
    flags = re.IGNORECASE if not case_sensitive else 0
    # Build proximity pattern: term1 followed by up to N words then term2, or vice versa
    word_gap = r'(?:\s+\S+){0,' + str(within_words) + r'}\s+'
    pattern_fwd = re.compile(f'{term1}{word_gap}{term2}', flags=flags)
    pattern_rev = re.compile(f'{term2}{word_gap}{term1}', flags=flags)

    mask = df[text_column].str.contains(pattern_fwd, na=False) | \
           df[text_column].str.contains(pattern_rev, na=False)

    results = df[mask]
    print(f"Proximity hits ('{term1}' within {within_words} words of '{term2}'): {len(results):,}")
    return results
```

---

## 3. Responsiveness Coding

### Coding Scheme

```python
# Responsiveness codes
RESPONSIVENESS_CODES = {
    'R':   'Responsive — directly relevant to the defined matter scope',
    'NR':  'Non-Responsive — does not relate to the matter scope',
    'NR?': 'Needs Review — unclear; requires human review',
    'R-P': 'Responsive — Privileged (withhold; log in privilege log)',
    'NR-P': 'Non-Responsive — Privileged (do not produce)',
}
```

### Auto-Coding by Keyword Hit

```python
def auto_code_responsiveness(df, keyword_hit_column='_keyword_hit',
                              privilege_flag_column='_privilege_flag'):
    """Apply initial auto-coding based on keyword hits and privilege flags."""
    df = df.copy()
    df['_responsiveness_code'] = 'NR'  # Default: non-responsive

    # Keyword hit = potentially responsive
    df.loc[df[keyword_hit_column] == True, '_responsiveness_code'] = 'NR?'

    # Privilege flag overrides responsiveness
    if privilege_flag_column in df.columns:
        df.loc[
            (df[keyword_hit_column] == True) & (df[privilege_flag_column] == True),
            '_responsiveness_code'
        ] = 'R-P'

    # Report
    print("Responsiveness coding distribution:")
    print(df['_responsiveness_code'].value_counts())

    # Items requiring human review
    needs_review = df[df['_responsiveness_code'] == 'NR?']
    print(f"\nItems requiring human review: {len(needs_review):,}")

    return df, needs_review
```

### Review Batch Generation

```python
def generate_review_batches(df_needs_review, batch_size=100, output_dir='output/04_ediscovery/review_batches/'):
    """
    Split items needing review into manageable batches for human reviewer.
    Each batch gets a CSV with a review notes column pre-populated.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    df_needs_review = df_needs_review.copy()
    df_needs_review['_reviewer_code'] = ''    # Reviewer fills: R / NR / R-P / NR-P
    df_needs_review['_reviewer_notes'] = ''   # Reviewer notes
    df_needs_review['_reviewed_by'] = ''      # Reviewer name
    df_needs_review['_reviewed_date'] = ''    # Review date

    batches = [df_needs_review.iloc[i:i+batch_size] for i in range(0, len(df_needs_review), batch_size)]
    for i, batch in enumerate(batches, 1):
        batch.to_csv(f"{output_dir}batch_{i:03d}.csv", index=True, encoding='utf-8-sig')

    print(f"Generated {len(batches)} review batches of {batch_size} items each in {output_dir}")
    return batches
```

---

## 4. Privilege Review & Privilege Log

### Privilege Detection

```python
# Default privilege indicators
PRIVILEGE_INDICATORS = {
    'legal_counsel': [
        r'\battorney[-\s]client\b', r'\bprivilege[d]?\b', r'\blegal advice\b',
        r'\bsolicitor[-\s]client\b', r'\bcounsel\b', r'\bbarrist[e]?r\b',
        r'\blawyer\b', r'\blaw firm\b', r'\blegal department\b',
    ],
    'without_prejudice': [
        r'\bwithout prejudice\b', r'\bWP\b', r'\bsettlement offer\b',
        r'\bdispute resolution\b',
    ],
    'work_product': [
        r'\bwork product\b', r'\bprepared in anticipation of litigation\b',
        r'\blitigation privilege\b',
    ]
}

# Known privilege domains (legal firms, internal legal)
PRIVILEGE_EMAIL_DOMAINS = [
    # Add specific law firm domains for the matter, e.g.:
    # 'cliffordchance.com', 'allens.com.au', 'legaldept.ourcompany.com'
]

def detect_privilege(df, text_columns, sender_col=None, recipient_col=None,
                     custom_counsel_emails=None, custom_counsel_domains=None):
    """
    Apply privilege detection to a dataset.
    Flags rows potentially containing privileged communications.
    Returns df with _privilege_flag and _privilege_reason columns.
    """
    df = df.copy()
    df['_privilege_flag'] = False
    df['_privilege_reason'] = ''

    # Text-based privilege detection
    combined_text = df[text_columns].fillna('').agg(' '.join, axis=1)

    for category, patterns in PRIVILEGE_INDICATORS.items():
        for pattern in patterns:
            mask = combined_text.str.contains(pattern, case=False, regex=True, na=False)
            df.loc[mask, '_privilege_flag'] = True
            df.loc[mask, '_privilege_reason'] += f"|{category}"

    # Email domain-based privilege detection
    if sender_col and custom_counsel_domains:
        for domain in custom_counsel_domains:
            mask = df[sender_col].str.contains(domain, case=False, na=False)
            df.loc[mask, '_privilege_flag'] = True
            df.loc[mask, '_privilege_reason'] += f"|counsel_sender:{domain}"

    if recipient_col and custom_counsel_domains:
        for domain in custom_counsel_domains:
            mask = df[recipient_col].str.contains(domain, case=False, na=False)
            df.loc[mask, '_privilege_flag'] = True
            df.loc[mask, '_privilege_reason'] += f"|counsel_recipient:{domain}"

    flagged = df[df['_privilege_flag'] == True]
    print(f"Privilege-flagged rows: {len(flagged):,} ({len(flagged)/len(df)*100:.1f}%)")
    print("Privilege reason breakdown:")
    print(flagged['_privilege_reason'].value_counts().head(10))

    return df, flagged
```

### Privilege Log Generation

```python
def generate_privilege_log(df_privileged, date_col, sender_col, recipient_col,
                           subject_col=None, reason_col='_privilege_reason',
                           output_path='privilege_log.csv'):
    """
    Generate a privilege log in standard format.
    Privilege log columns match common court/discovery requirements.
    """
    priv_log = pd.DataFrame({
        'Entry_No': range(1, len(df_privileged) + 1),
        'Original_Row_Index': df_privileged.index,
        'Date': df_privileged[date_col] if date_col else '',
        'Author_Sender': df_privileged[sender_col] if sender_col else '',
        'Recipient': df_privileged[recipient_col] if recipient_col else '',
        'Subject_Description': df_privileged[subject_col] if subject_col else '[Redacted — Privileged]',
        'Privilege_Type': df_privileged[reason_col].str.replace('|', ' / ', regex=False).str.strip(' /'),
        'Basis_for_Privilege': '',  # To be completed by legal counsel
        'Withheld_or_Redacted': 'Withheld',  # Default; change if partially redacted
    })

    priv_log.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Privilege log generated: {output_path} ({len(priv_log):,} entries)")
    return priv_log
```

---

## 5. Categorisation Framework

### Default Coding Categories

```python
DEFAULT_CATEGORIES = {
    # Content type
    'COMM':   'Communication (email, message, chat)',
    'FIN':    'Financial record (invoice, transaction, account statement)',
    'CONTR':  'Contract or agreement',
    'CORP':   'Corporate record (board minutes, resolutions, registers)',
    'HR':     'Human resources record',
    'TECH':   'Technical record (logs, system data)',
    'MEDIA':  'Media, marketing, or PR materials',
    'OTHER':  'Other — describe in notes',

    # Relevance level
    'H':  'High relevance — directly addresses a key issue',
    'M':  'Medium relevance — relevant background or context',
    'L':  'Low relevance — tangentially related',

    # Action required
    'REV':    'Requires legal review',
    'PROD':   'Include in production',
    'HOLD':   'Place on litigation hold',
    'PRIV':   'Privilege — withhold',
    'REDACT': 'Redact and produce',
}

def add_coding_columns(df):
    """Add standard eDiscovery coding columns to a DataFrame."""
    coding_cols = {
        '_category_content_type': '',   # COMM, FIN, CONTR, etc.
        '_category_relevance': '',      # H, M, L
        '_category_action': '',         # REV, PROD, HOLD, PRIV, REDACT
        '_category_issues': '',         # Pipe-separated list of key issues this relates to
        '_coding_notes': '',            # Free text notes
        '_coded_by': '',                # Reviewer identifier
        '_coded_date': '',              # Date coded
        '_review_flag': False,          # Flagged for QC
    }
    for col, default in coding_cols.items():
        if col not in df.columns:
            df[col] = default
    return df
```

---

## 6. Custodian Mapping

```python
def assign_custodians(df, identifier_columns, custodian_map):
    """
    Map data rows to custodians (named individuals or data sources).

    custodian_map: dict of {identifier_value: custodian_name}
    e.g., {'john.smith@company.com': 'John Smith', 'js@company.com': 'John Smith'}

    Searches identifier_columns for any value matching the map keys.
    """
    df = df.copy()
    df['_custodian'] = 'Unknown'

    for col in identifier_columns:
        for identifier, custodian in custodian_map.items():
            mask = df[col].str.contains(re.escape(identifier), case=False, na=False)
            df.loc[mask, '_custodian'] = custodian

    print("Custodian assignment:")
    print(df['_custodian'].value_counts())

    return df

# Custodian summary for chain of custody documentation
def custodian_summary(df, custodian_col='_custodian', date_col=None):
    summary = df.groupby(custodian_col).agg(
        record_count=(custodian_col, 'count'),
        date_from=(date_col, 'min') if date_col else (custodian_col, lambda x: 'N/A'),
        date_to=(date_col, 'max') if date_col else (custodian_col, lambda x: 'N/A'),
    )
    return summary
```

---

## 7. Quality Control & Sampling

### Random Sampling for QC

```python
import numpy as np

def qc_sample(df, responsiveness_col='_responsiveness_code', sample_pct=0.05, seed=42):
    """
    Generate a QC sample from coded items for accuracy checking.
    Returns a stratified random sample (proportional by code category).
    """
    np.random.seed(seed)
    sample_size = max(50, int(len(df) * sample_pct))

    # Stratified sample by responsiveness code
    sample_parts = []
    for code in df[responsiveness_col].unique():
        group = df[df[responsiveness_col] == code]
        n = max(1, int(len(group) / len(df) * sample_size))
        sample_parts.append(group.sample(n=min(n, len(group)), random_state=seed))

    qc_sample_df = pd.concat(sample_parts).drop_duplicates()
    qc_sample_df['_qc_code'] = ''           # QC reviewer codes this
    qc_sample_df['_qc_agrees'] = ''         # 'Y' or 'N'
    qc_sample_df['_qc_notes'] = ''

    print(f"QC sample size: {len(qc_sample_df):,} rows ({len(qc_sample_df)/len(df)*100:.1f}%)")
    return qc_sample_df

# QC accuracy calculation
def qc_accuracy(qc_df, original_code_col='_responsiveness_code', qc_code_col='_qc_code'):
    """Calculate inter-rater agreement between original and QC coding."""
    both_coded = qc_df[qc_df[qc_code_col] != '']
    if len(both_coded) == 0:
        return "No completed QC codes found."
    agreement = (both_coded[original_code_col] == both_coded[qc_code_col]).sum()
    accuracy = agreement / len(both_coded) * 100
    print(f"QC agreement: {agreement}/{len(both_coded)} ({accuracy:.1f}%)")
    print(f"Discrepancies: {len(both_coded) - agreement}")
    return accuracy
```

---

## 8. Production Preparation

```python
def prepare_production_set(df, responsiveness_col='_responsiveness_code',
                           privilege_col='_privilege_flag',
                           output_path='output/05_production/responsive_set.csv',
                           bates_prefix='PROD'):
    """
    Extract the production set: responsive, non-privileged documents.
    Applies Bates-style sequential numbering.
    """
    # Production = Responsive AND NOT Privileged
    production = df[
        (df[responsiveness_col] == 'R') &
        (df.get(privilege_col, pd.Series(False, index=df.index)) == False)
    ].copy()

    # Bates numbering
    production['_bates_number'] = [
        f"{bates_prefix}{str(i).zfill(7)}"
        for i in range(1, len(production) + 1)
    ]

    production.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Production set: {len(production):,} items → {output_path}")
    print(f"Bates range: {bates_prefix}0000001 – {bates_prefix}{str(len(production)).zfill(7)}")

    return production
```

---

## 9. Default Search Term Libraries

### General Litigation Terms

```python
GENERAL_LITIGATION_TERMS = [
    r'\bfraud\b', r'\bmisrepresent', r'\bdecei[tv]', r'\bconspir',
    r'\bbreach', r'\bcontract\b', r'\bdamage[s]?\b', r'\bnegligen',
    r'\bliab[ility]+\b', r'\bsettle[ment]?\b', r'\bwithout prejudice\b',
    r'\bpayment[s]?\b', r'\binvoice[s]?\b', r'\bcover.?up\b',
    r'\bdelete\b', r'\bdestroy\b', r'\bshred\b', r'\bdo not\s+.{0,20}\brecord\b',
]

FINANCIAL_TERMS = [
    r'\bcash\b', r'\boffshore\b', r'\btransfer[s]?\b', r'\bwire\b',
    r'\baccoun[t]?\b', r'\bfund[s]?\b', r'\bpayment[s]?\b',
    r'\bdividen[d]?\b', r'\btax\b', r'\bevad',
    r'\bloan[s]?\b', r'\bdebt\b', r'\binsolvenc',
]

EMPLOYMENT_TERMS = [
    r'\btermina[t]', r'\bdismiss', r'\bredundan', r'\bbully',
    r'\bharass', r'\bdiscrimin', r'\bgrievanc', r'\bworkplace\b',
    r'\bunfair\b', r'\bwrongful\b', r'\bpayslip\b', r'\bsuperannuation\b',
]

CORPORATE_GOVERNANCE_TERMS = [
    r'\bboard\b', r'\bdirector[s]?\b', r'\bshareholder[s]?\b', r'\bdivid',
    r'\bproxy\b', r'\bresolution[s]?\b', r'\bminutes\b',
    r'\bconflict of interest\b', r'\brelated party\b', r'\bdisclosure\b',
]
```

### Using Term Libraries

```python
# Combine libraries for a matter
matter_terms = GENERAL_LITIGATION_TERMS + FINANCIAL_TERMS

# Run combined search
df_with_hits, hits = boolean_search(df, text_columns=['subject', 'body'],
                                     search_terms=matter_terms, operator='OR')

# Save all hits for KWIC review
for term in matter_terms[:5]:  # KWIC the top terms
    kwic_df = kwic(df, 'body', term, context_chars=200)
    safe_term = re.sub(r'[^\w]', '_', term)[:30]
    kwic_df.to_csv(f'kwic_{safe_term}.csv', index=False, encoding='utf-8-sig')
```

---

## 10. Australian-Specific Search Term Libraries

Search term libraries for Australian legal contexts. Use these when matter is governed by Australian law.

```python
# Australian legal context search terms

AUSTRALIAN_CORPORATIONS_ACT_TERMS = [
    r'\bCorporations Act\b', r'\bASIC\b', r'\bASX\b', r'\bdirectors?\s+duty\b',
    r'\brelated party\b', r'\bmaterial interest\b', r'\binsider\b',
    r'\bcontinuous disclosure\b', r'\bprospectus\b', r'\bplacement\b',
    r'\brightsissue\b', r'\bsolvency\b', r'\binsolven[cy]+\b',
    r'\badministrat[ion|or]\b', r'\bliquidat[ion|or]\b', r'\breceiver\b',
]

AUSTRALIAN_EMPLOYMENT_TERMS = [
    r'\bFair Work\b', r'\bFWC\b', r'\bunfair dismissal\b', r'\bgeneral protections\b',
    r'\bEnterprise Agreement\b', r'\bNational Employment Standards\b', r'\bNES\b',
    r'\bworkers.{0,5}compensation\b', r'\bWorkSafe\b', r'\bWorkCover\b',
    r'\bOH&S\b', r'\bWHS\b', r'\bbullying\b', r'\bharassment\b',
    r'\breadundancy\b', r'\blongservice\b', r'\bsuperannuation\b', r'\bsuper\b',
]

AUSTRALIAN_FINANCIAL_CRIME_TERMS = [
    r'\bAUSTRAC\b', r'\bAML\b', r'\bCTR\b',  # Cash Transaction Report
    r'\bSMR\b',  # Suspicious Matter Report
    r'\bstructuring\b', r'\bsmurfing\b', r'\bmoney laundering\b',
    r'\bproceeds of crime\b', r'\bPOCA\b',
    r'\bATO\b', r'\btax evasion\b', r'\bproject wind-?up\b',
    r'\bDivision 7A\b', r'\bfringe benefit[s]?\b',
]

WA_SPECIFIC_TERMS = [
    r'\bMagistrates Court WA\b', r'\bDistrict Court WA\b', r'\bSupreme Court WA\b',
    r'\bWA Police\b', r'\bCCC\b',  # Corruption and Crime Commission
    r'\bSAT\b',  # State Administrative Tribunal
    r'\bDPP\b',  # Director of Public Prosecutions
    r'\bLandgate\b', r'\bDOFE\b',
]
```

---

## 11. Email Threading & Conversation Reconstruction

Reconstruct email conversation threads from metadata and content patterns.

```python
def reconstruct_email_threads(df, message_id_col=None, in_reply_to_col=None,
                               subject_col=None, date_col=None, sender_col=None):
    """
    Reconstruct email conversation threads.
    Uses Message-ID/In-Reply-To if available, falls back to subject matching.
    """
    df = df.copy()

    if message_id_col and in_reply_to_col and message_id_col in df.columns and in_reply_to_col in df.columns:
        # Proper threading via Message-ID headers
        thread_map = {}
        df['_thread_root'] = df[message_id_col]

        for _, row in df.iterrows():
            msg_id = row[message_id_col]
            reply_to = row.get(in_reply_to_col, '')
            if pd.notna(reply_to) and reply_to in thread_map:
                thread_map[msg_id] = thread_map[reply_to]  # Inherit root
            else:
                thread_map[msg_id] = msg_id  # Is the root

        df['_thread_id'] = df[message_id_col].map(thread_map)

    elif subject_col and subject_col in df.columns:
        # Fallback: group by normalised subject
        df['_thread_id'] = df[subject_col].str.lower().str.replace(
            r'^(re:\s*|fwd:\s*|fw:\s*)+', '', regex=True
        ).str.strip()

    # Thread statistics
    thread_stats = df.groupby('_thread_id').agg(
        message_count=('_thread_id', 'count'),
        participants=(sender_col, lambda x: x.nunique()) if sender_col and sender_col in df.columns else ('_thread_id', 'count'),
        date_start=(date_col, 'min') if date_col and date_col in df.columns else ('_thread_id', lambda x: 'N/A'),
        date_end=(date_col, 'max') if date_col and date_col in df.columns else ('_thread_id', lambda x: 'N/A'),
    ).sort_values('message_count', ascending=False)

    print(f"Threads identified: {len(thread_stats):,}")
    print(f"Largest thread: {thread_stats['message_count'].max():,} messages")
    print(f"\nTop 10 threads by size:\n{thread_stats.head(10)}")

    return df, thread_stats

def extract_email_attachments_metadata(df, attachment_col):
    """
    Analyse attachment patterns from email data.
    Identifies documents shared, common attachment types, and unusual patterns.
    """
    if attachment_col not in df.columns:
        return None

    attachments = df[attachment_col].dropna()

    # Extension analysis
    import re
    extensions = attachments.str.extractall(r'\.([a-zA-Z0-9]{1,6})(?:\b|$)')[0]
    ext_counts = extensions.str.lower().value_counts()

    print("Attachment extension distribution:")
    print(ext_counts.head(15))

    # Suspicious extensions
    suspicious = ['exe', 'bat', 'ps1', 'vbs', 'js', 'jar', 'dll', 'zip', 'rar', '7z']
    found_suspicious = ext_counts[ext_counts.index.isin(suspicious)]
    if not found_suspicious.empty:
        print(f"\nSUSPICIOUS EXTENSIONS FOUND: {found_suspicious.to_dict()}")

    return ext_counts
```

---

## 12. Search Hit Report Generation

Generate a formal search term hit report suitable for providing to opposing counsel.

```python
def generate_search_hit_report(df, term_results_dict, output_path='output/04_ediscovery/search_hit_report.md'):
    """
    Generate a formal search term hit report suitable for providing to opposing counsel.

    term_results_dict: {term: hit_count} from boolean_search results
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    total_docs = len(df)

    with open(output_path, 'w') as f:
        f.write("# Search Term Hit Report\n\n")
        f.write(f"**Generated**: {now.isoformat()}\n")
        f.write(f"**Dataset size**: {total_docs:,} records\n\n")
        f.write("---\n\n")
        f.write("## Search Term Results\n\n")
        f.write("| Term | Hits | % of Dataset | Unique Custodians |\n")
        f.write("|------|------|-------------|-------------------|\n")

        total_hits = 0
        for term, hit_count in sorted(term_results_dict.items(), key=lambda x: -x[1]):
            pct = hit_count / total_docs * 100 if total_docs > 0 else 0
            total_hits += hit_count
            f.write(f"| `{term}` | {hit_count:,} | {pct:.2f}% | — |\n")

        f.write(f"\n**Total hits across all terms**: {total_hits:,}\n\n")
        f.write("---\n\n")
        f.write("## Notes\n\n")
        f.write("- Hits represent rows containing at least one occurrence of the search term.\n")
        f.write("- A single row may match multiple terms (counted once per term above).\n")
        f.write("- Terms are searched across all designated text columns.\n")
        f.write("- Privilege review has not been applied to hits listed above.\n")

    print(f"Search hit report written: {output_path}")
    return output_path
```

---

## 13. Technology-Assisted Review (TAR) Guidance

### What is TAR?

Technology-Assisted Review (TAR), also called predictive coding, uses machine learning to predict document responsiveness based on a human-coded seed set. TAR suitability is not triggered by a fixed document-count threshold. Assess it against the issues in dispute, volume and complexity of material, expected review burden, available validation data, proportionality, party agreement, and any court order or protocol.

### TAR Workflow

1. **Seed set**: Human reviewer codes ~500–1000 documents as Responsive (R) or Non-Responsive (NR)
2. **Model training**: ML algorithm learns patterns from seed set
3. **Prediction**: Model predicts responsiveness on entire dataset
4. **Validation**: Human review validates model predictions on sample of high-uncertainty items
5. **Iteration**: Refine model if validation shows inadequate accuracy
6. **Production**: Apply final model predictions to full dataset

### Disclosure Obligations

TAR methodology and validation should be documented before production. Disclosure to the other parties, and the level of detail disclosed, depends on the applicable court rules, practice notes, discovery orders, agreed protocol, confidentiality constraints, and privilege issues. Document:
- Training set size and selection methodology
- Model architecture and parameters
- Validation results (precision, recall, F1-score)
- Final accuracy on validation set
- Any deviations from published TAR best practices

```python
def simple_tar_model(df_seed, text_col, label_col, df_full, text_col_full):
    """
    Simple Technology-Assisted Review model.
    Train on human-coded seed set, predict responsiveness on full dataset.
    Requires: pip install scikit-learn

    label_col: column with 'R' (responsive) or 'NR' (non-responsive) human codes
    Returns: df_full with _tar_score (0–1 responsiveness probability) added
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, precision_recall_fscore_support

    # Prepare training data
    X_train = df_seed[text_col].fillna('').tolist()
    y_train = (df_seed[label_col] == 'R').astype(int).tolist()

    print(f"TAR Model Training")
    print(f"  Seed set: {len(X_train)} documents")
    print(f"  Responsive: {sum(y_train):,} | Non-responsive: {len(y_train) - sum(y_train):,}")

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2), min_df=1)
    X_train_vec = vectorizer.fit_transform(X_train)

    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    model.fit(X_train_vec, y_train)

    # Self-assessment on training set
    y_pred = model.predict(X_train_vec)
    precision, recall, f1, _ = precision_recall_fscore_support(y_train, y_pred, average='binary')

    print("\nTraining set validation:")
    print(classification_report(y_train, y_pred, target_names=['NR', 'R']))
    print(f"Summary: Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")

    # Predict on full dataset
    X_full = vectorizer.transform(df_full[text_col_full].fillna('').tolist())
    scores = model.predict_proba(X_full)[:, 1]  # Responsive probability

    df_result = df_full.copy()
    df_result['_tar_score'] = scores
    df_result['_tar_prediction'] = ['R' if s >= 0.5 else 'NR' for s in scores]

    print(f"\nFull dataset predictions:")
    print(f"  Predicted Responsive: {sum(scores >= 0.5):,}")
    print(f"  Predicted Non-responsive: {sum(scores < 0.5):,}")
    print(f"\n⚠️ IMPORTANT: TAR predictions must be validated by human review before production.")

    return df_result, model, vectorizer
```

## Section 14: EDRM Framework & Proportionality Analysis

Use EDRM and The Sedona Conference as process standards, not binding Australian law. For Australian proceedings, verify discovery obligations against the applicable court rules, practice notes, and orders. For Federal Court technology issues, check the current Technology and the Court Practice Note (GPN-TECH) and any matter-specific orders before relying on TAR, keyword protocols, load file formats, or production sampling.

### EDRM Stages

| Stage | Phase | Purpose | CSV Impact |
|-------|-------|---------|-----------|
| 1 | **Information Governance** | Data identification, retention policies | Inventory CSVs, custodian mapping |
| 2 | **Identification** | Data sources located | Source system list, backup schedules |
| 3 | **Preservation** | Legal hold, data freeze | Preservation logs, exception tracking |
| 4 | **Collection** | Extract from systems | Collection metadata, hash lists |
| 5 | **Processing** | Dedupe, OCR, metadata extraction | Load files (DAT/OPT), dedup reports |
| 6 | **Review** | Privilege, responsiveness, redaction | Coding spreadsheets, TAR predictions |
| 7 | **Analysis** | Clustering, keywords, relationships | Network CSVs, statistical summaries |
| 8 | **Production** | Bates-stamped delivery | Production manifest, load files |
| 9 | **Presentation** | Evidence in trial | Expert reports, visual timelines |

### Source hierarchy for eDiscovery propositions

1. Court rules, practice notes, and orders in the proceeding.
2. EDRM materials for lifecycle/process vocabulary and processing standards.
3. The Sedona Conference publications for TAR, proportionality, cooperation, and defensibility principles.
4. Vendor documentation only for tool-specific behaviour, not legal standards.
5. Blog posts and marketing material only as research leads.

### Proportionality Analysis (Australian Courts)

```python
def proportionality_report(total_data_volume_gb, estimated_review_hours,
                          hourly_rate_aud, case_value_aud, estimated_responsive_pct=0.05):
    """
    Generate a proportionality aid for Australian electronic discovery.
    Use as a case-management worksheet only; GPN-TECH requires early,
    proportionate consideration and court approval of discovery plans,
    not this specific formula.

    Args:
        total_data_volume_gb: Size of dataset in gigabytes
        estimated_review_hours: Expected human review hours
        hourly_rate_aud: Legal hourly rate (AUD)
        case_value_aud: Case value or claim amount (AUD)
        estimated_responsive_pct: % of data expected to be responsive

    Returns:
        Dictionary with proportionality metrics and recommendations
    """
    import math

    # Cost calculation
    review_cost = estimated_review_hours * hourly_rate_aud
    processing_cost = max(5000, total_data_volume_gb * 50)  # $50/GB minimum
    total_cost = review_cost + processing_cost

    # Proportionality metrics
    cost_to_claim_ratio = total_cost / case_value_aud if case_value_aud > 0 else float('inf')
    responsive_docs_estimated = int(total_data_volume_gb * 1e6 * (estimated_responsive_pct / 100))

    # There is no universal Australian court threshold. Flag cases where the
    # estimated cost needs extra justification and narrowing options.
    needs_narrowing_review = cost_to_claim_ratio > 0.10 or total_cost > 250000

    report = {
        'case_value_aud': case_value_aud,
        'total_data_volume_gb': total_data_volume_gb,
        'estimated_review_hours': estimated_review_hours,
        'review_cost_aud': review_cost,
        'processing_cost_aud': processing_cost,
        'total_estimated_cost_aud': total_cost,
        'cost_to_claim_ratio': round(cost_to_claim_ratio, 3),
        'estimated_responsive_count': responsive_docs_estimated,
        'proportionality_threshold': 'No fixed threshold; assess against issues, value, burden, and court orders',
        'needs_narrowing_review': needs_narrowing_review,
        'recommendation': 'DOCUMENT JUSTIFICATION' if not needs_narrowing_review else 'CONSIDER LIMITATION',
        'justification': (
            'Cost/value ratio does not itself indicate a narrowing issue; still verify against issues and orders'
            if not needs_narrowing_review
            else 'Estimated cost/burden may be high. Consider sampling, phased discovery, targeted custodians, date limits, or keyword/TAR protocol refinement'
        ),
    }

    return report


# Example usage
report = proportionality_report(
    total_data_volume_gb=500,
    estimated_review_hours=2000,
    hourly_rate_aud=350,
    case_value_aud=2500000,
    estimated_responsive_pct=0.10
)

for key, value in report.items():
    if isinstance(value, bool):
        print(f"{key}: {'✓' if value else '✗'}")
    else:
        print(f"{key}: {value}")
```

### Australian Court Practice Notes

| Court | Jurisdiction | eDiscovery Rule | Key Requirement |
|-------|--------------|-----------------|-----------------|
| **Federal Court** | National | GPN-TECH | Proportionality cost-benefit analysis |
| **NSW District** | NSW | CPA 21.1 | Early disclosure, reasonable searches |
| **Victorian** | VIC | VCR 24.05 | Proportionate discovery, privilege log |
| **WA District** | WA | DCR 24 | Standard format (EODC), agreed protocols |
| **Family Court** | National | FCR 15.13 | Child welfare priority, limitations apply |

### Pre-eDiscovery ESI Protocol Checklist

```python
def esi_protocol_checklist():
    """
    Pre-eDiscovery protocol agreement checklist for Australian litigation.
    Court orders should reference these points.
    """
    checklist = {
        'Data Scope': [
            'Custodians identified and agreed',
            'Email systems scoped (mailbox, archive, PST)',
            'Network drives included/excluded',
            'Mobile devices covered',
            'Third-party data sources identified',
        ],
        'Search Protocol': [
            'Keyword terms agreed',
            'Date ranges specified',
            'Deduplication method (hash, thread ID)',
            'Privilege log categories defined',
            'Native vs PDF production format',
        ],
        'Metadata': [
            'Required metadata fields documented',
            'Sensitive fields to exclude (SSN, credit card)',
            'Load file format agreed (DAT/OPT)',
            'Hash verification method (MD5/SHA-256)',
        ],
        'Review & Production': [
            'Coding schema finalized',
            'TAR/AI review protocols approved',
            'Redaction procedures documented',
            'Bates numbering scheme',
            'Production schedule agreed',
        ],
        'Quality Control': [
            'Sample review size (5-10%)',
            'Error rate tolerance',
            'Re-review of failed documents',
            'Privilege log sampling audit',
        ],
        'Cost & Timeline': [
            'Cost estimate and allocation',
            'Milestone dates',
            'Escalation procedures',
            'Change order process',
        ],
    }

    return checklist
```

### Cost-Benefit Decision Tree

```
Is requested discovery proportionate?
│
├─ Does the request match pleaded issues and likely probative value? → NO → Narrow scope
│
├─ Are estimated cost and time justified by the nature, size, and complexity of the case? → NO → Consider:
│  ├─ Limiting custodians
│  ├─ Narrowing keywords
│  ├─ Requesting sampling
│  └─ Phased production
│
└─ Is there an agreed/court-approved discovery plan and exchange protocol? → NO → Resolve before production
   ├─ Request narrowing
   ├─ Propose alternatives (targeted search, sampling)
   └─ Escalate to court if unresolved
```
