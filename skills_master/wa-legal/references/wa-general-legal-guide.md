# WA General Legal Guide — Case Building, Data Handling & AI Guardrails

> **MANDATORY DISCLAIMER**: General legal information only. **NOT legal advice**. This guide assists with preparation and organisation. It does not replace legal representation.

---

## Contents

- Case building fundamentals
- Evidence collection and preservation
- Data handling and privacy obligations
- AI guardrails for legal work
- Self-represented litigant (SRL) guidance
- Court etiquette and procedure
- Costs and fee recovery
- Key resources and referrals

---

## Case Building Fundamentals

### The IRAC Method

Structure every legal argument using IRAC:

1. **Issue** — What is the legal question? State it precisely
2. **Rule** — What law applies? Cite the statute, case, or principle
3. **Application** — How does the law apply to the specific facts?
4. **Conclusion** — What result follows?

### Building a Chronology

A strong case starts with a **dated chronology** of every relevant event:

| Date | Event | Source | Significance |
|------|-------|--------|-------------|
| 2025-01-15 | Lease signed | Agreement copy | Establishes terms |
| 2025-03-01 | Written complaint sent | Email + screenshot | Notice of issue |
| 2025-03-15 | Landlord response | Email | Acknowledges issue |

Rules:
- Include **everything** relevant, even events that seem unhelpful — undisclosed facts destroy credibility
- Note the **source** for every entry (document, witness, recollection)
- Distinguish **facts** (what happened) from **assertions** (what someone claims)
- Update the chronology as new evidence emerges
- See `references/case-file-templates.md` for templates

### Element-Based Case Analysis

For each cause of action or defence, identify the **legal elements** and map evidence to each:

```
Cause of action: Breach of residential tenancy agreement (s 42 RTA)

Element 1: Existence of tenancy agreement
  Evidence: Signed lease (Exhibit A), bond receipt (Exhibit B)

Element 2: Landlord breached obligation to maintain in reasonable repair
  Evidence: Photos of water damage dated 15/03/2025 (Exhibit C),
            plumber's report dated 20/03/2025 (Exhibit D),
            tenant's email notification dated 01/03/2025 (Exhibit E)

Element 3: Tenant suffered loss
  Evidence: Invoice for damaged property (Exhibit F),
            rent records showing payment for unusable room (Exhibit G)

Element 4: Loss was caused by the breach
  Evidence: Chronology showing damage occurred after roof leak reported
```

### Document Bundle Structure

```
CASE-NAME/
├── 00-Case-Summary.md          # One-page case overview
├── 01-Chronology.md            # Dated timeline
├── 02-Pleadings/               # Claim, defence, reply
├── 03-Evidence-Index.md        # Master evidence list with exhibit numbers
├── 04-Correspondence/          # All letters, emails, messages (chronological)
├── 05-Documents/               # Agreements, reports, invoices
├── 06-Photos/                  # Dated and captioned photographs
├── 07-Research/                # Legislation, case law, legal research notes
├── 08-Court-Documents/         # Filed documents, orders, hearing notes
└── 09-AI-Usage-Log.md          # Record of AI assistance (see AI guardrails)
```

Use `scripts/init_case.py` to scaffold this structure automatically.

---

## Evidence Collection and Preservation

### The Rules of Evidence (Simplified)

| Principle | Meaning |
|-----------|---------|
| **Relevance** | Evidence must relate to a fact in issue |
| **Authenticity** | You must be able to prove the document/photo is what you say it is |
| **Hearsay** | Generally cannot rely on what someone else told you — exceptions apply |
| **Original documents** | Prefer originals over copies (best evidence rule) |
| **Privilege** | Some communications are protected (legal advice, without-prejudice) |

### Evidence Types Ranked by Weight

1. **Contemporaneous documents** — dated notes, diaries, receipts made at the time
2. **Official records** — police reports, medical records, government correspondence
3. **Photographs and video** — date-stamped, showing context (not close-up only)
4. **Expert reports** — qualified professionals (plumbers, doctors, valuers)
5. **Witness statements** — signed, dated, specific to what the witness personally observed
6. **Digital communications** — emails, SMS, messages with full metadata (see `references/sms-imessage-analysis.md`)
7. **Your own testimony** — credible if consistent with documents

### Preservation Checklist

- [ ] Screenshot all relevant digital communications with **metadata visible** (sender, recipient, date, time)
- [ ] Export SMS/iMessage to preserved format (see `references/sms-imessage-analysis.md`)
- [ ] Save emails as `.eml` files or PDF with headers visible
- [ ] Photograph physical evidence from multiple angles with **date stamps**
- [ ] Keep originals in a safe place — work from copies
- [ ] Create a **chain of custody** log for each piece of evidence
- [ ] Back up everything to at least two separate locations
- [ ] Record witness contact details immediately — memories fade, people move

### Surveillance Devices Act 1998 (WA) — Recording Conversations

- **One-party consent**: A person **can** record their own conversation without the other party's knowledge (s 5(3)) if reasonably necessary to protect their lawful interests
- **Publication restricted**: Cannot publish the recording except for legal proceedings, protecting lawful interests, or court order (s 9)
- **Third-party recording**: Recording someone else's conversation without their knowledge is an offence
- **In legal proceedings**: Recordings made under s 5(3) are generally admissible

---

## Data Handling and Privacy Obligations

### Privacy Act 1988 (Cth) — When It Applies

- Applies to organisations with annual turnover >$3 million
- **Does NOT apply to** most individuals acting in a personal capacity (including SRLs)
- **Does apply to** corporations, government agencies, and some small businesses (health, credit reporting)

### Handling Personal Information in Legal Matters

Even when the Privacy Act doesn't strictly apply, follow these principles:

1. **Collect only what you need** — don't hoard personal data
2. **Store securely** — encrypted storage, password-protected files
3. **Don't share unnecessarily** — only disclose to legal representatives, court, or as required by law
4. **Destroy when finished** — shred physical documents, securely delete digital files after matter concludes
5. **Document handling** — keep a log of who accessed what and when

### Sensitive Information

Extra care with:
- **Health records** — Confidentiality obligations under state health privacy laws
- **Children's information** — Higher duty of care in handling
- **Financial records** — Bank statements, tax returns, Centrelink records
- **Criminal history** — Spent convictions may be protected (Spent Convictions Act 1988)
- **Family violence information** — Risk assessment and safety considerations paramount

### Digital Evidence Handling

```
DO:
- Export digital evidence in original format (not retyped or reformatted)
- Preserve metadata (use screenshot tools that capture date/time/URL)
- Hash large files to prove integrity (sha256sum)
- Store on encrypted media
- Document the extraction process

DON'T:
- Edit or modify original files
- Forward evidence via unsecured channels (use encrypted email or secure file share)
- Store evidence on shared or cloud drives without access controls
- Delete originals after making copies
```

---

## AI Guardrails for Legal Work

### Mandatory AI Usage Policy

When using AI tools (including this skill) for legal matters:

1. **Never submit identifying information** to public AI services — redact names, addresses, dates of birth, financial details before input
2. **AI output is NOT legal advice** — it is a drafting and research aid only
3. **Verify everything** — check all statutory references, case citations, and procedural requirements against current primary sources at `legislation.wa.gov.au`
4. **Record AI usage** — maintain `09-AI-Usage-Log.md` noting date, tool used, query, and output used
5. **Disclose AI assistance** — if asked by the court whether AI was used in document preparation, disclose honestly

### What AI Can Help With

- Drafting chronologies and document indexes
- Organising evidence by legal element
- Explaining general legal principles
- Generating templates (letters, chronologies, evidence lists)
- Research assistance (finding legislation, case names, court forms)
- Proofreading and formatting

### What AI Must NOT Do

- Provide specific legal advice for your situation
- Predict case outcomes
- Replace a qualified legal practitioner
- Generate fabricated citations (hallucination risk)
- Access privileged communications without authority
- Make strategic decisions about your case

### Verification Protocol

Before relying on any AI-generated legal content:

1. **Statute check**: Confirm the Act and section numbers are current at `legislation.wa.gov.au`
2. **Case law check**: Verify cases exist and are not overruled at AustLII (`austlii.edu.au`) or Jade (`jade.io`)
3. **Form check**: Download current court forms from the relevant court website
4. **Fee check**: Verify current filing fees on the court website
5. **Procedure check**: Confirm current procedural requirements in the court's practice directions

### AI Usage Log Template

```markdown
# AI Usage Log — [Case Name]

| Date | Tool | Query Summary | Output Used | Verified? | Notes |
|------|------|---------------|-------------|-----------|-------|
| 2025-05-07 | wa-legal skill | RTA repair obligations | Draft letter to landlord | Yes — s 42 checked | Used as template only |
```

Use `scripts/record_ai_usage.py` to automate logging.

---

## Self-Represented Litigant (SRL) Guidance

### Before You Start

1. **Seek legal advice first** — even a single consultation can identify issues you may miss
2. **Consider Legal Aid WA** — means-tested free advice: 1300 650 579
3. **Consider community legal centres** — LawAccess WA, Tenancy WA, Women's Legal Service
4. **Assess cost vs benefit** — court fees, time off work, stress, vs the amount in dispute

### Preparing for Court

1. **Know your case** — be able to state your claim in 2 minutes
2. **Know the other side's case** — anticipate their arguments
3. **Organise your evidence** — indexed, labelled, in chronological order
4. **Prepare a written outline** — summary of your argument with page references to evidence
5. **Dress appropriately** — business attire shows respect for the court
6. **Arrive early** — at least 30 minutes before your listed time
7. **Bring originals and copies** — the court and other party need copies

### In the Courtroom

- Stand when the magistrate or judge enters or exits
- Address the magistrate as "Your Honour"
- Speak clearly and slowly
- Answer questions directly — do not volunteer extra information
- Do not interrupt the other party or the magistrate
- Take notes during the hearing
- If you don't understand something, politely ask for clarification

---

## Costs and Fee Recovery

### Magistrates Court Filing Fees (Check Current Schedule)

- Application (general): ~$100–$200
- Minor civil claim (up to $10,000): lower fee
- Counter-application: additional fee
- Consent order: lower fee

### Costs Orders

- **General rule**: Each party bears their own costs in the Magistrates Court unless the court orders otherwise
- **Costs may be awarded** where a party has acted unreasonably, caused unnecessary delay, or refused reasonable settlement offers
- **SRL costs**: Self-represented litigants can sometimes claim costs for time spent, but at a lower rate than lawyer's costs
- **Offers of compromise**: Calderbank offers (without prejudice save as to costs) can protect your costs position

---

## Key Resources and Referrals

| Service | Phone | Website | Use For |
|---------|-------|---------|---------|
| Legal Aid WA | 1300 650 579 | legalaid.wa.gov.au | Free legal advice, grants of aid |
| LawAccess WA | 1300 650 579 | lawaccess.wa.gov.au | Referral to legal services |
| Tenancy WA | (08) 9221 0088 | tenancywa.org | Tenancy advice and advocacy |
| Community Legal Centres WA | — | communitylegalcentres.org.au | Local free legal help |
| Consumer Protection WA | 1300 304 054 | consumerprotection.wa.gov.au | Tenancy complaints, conciliation |
| Magistrates Court WA | — | magistratescourt.wa.gov.au | Forms, practice directions, fees |
| District Court WA | — | districtcourt.wa.gov.au | Appeals from Magistrates Court |
| State Administrative Tribunal | (08) 9219 3111 | sat.justice.wa.gov.au | Review of government decisions |
| Women's Legal Service WA | 1800 012 012 | wlswa.org.au | Women-centred legal services |
| Aboriginal Legal Service WA | 1800 019 900 | als.org.au | Aboriginal legal representation |
| Law Society of WA | (08) 9322 4577 | lawsocietywa.asn.au | Find a private lawyer |
| Relationships Australia WA | 1300 364 277 | relationshipswa.org.au | Mediation services |
| Domestic Violence Crisis Line | 1800 007 339 | — | 24/7 family violence support |

---

## Common Mistakes

- Relying on AI-generated case citations without verifying they exist (hallucination)
- Submitting evidence without proper authentication or explanation of relevance
- Failing to redact personal/identifying information before using AI tools
- Missing limitation periods (6 years for contract, 3 years for some torts, varies by cause of action)
- Not bringing copies of documents for the court and the other party
- Treating AI legal research as a substitute for qualified legal advice
- Disclosing privileged communications (legal advice, without-prejudice negotiations) to the other side or in court filings
- Not keeping an AI usage log — courts increasingly ask about AI assistance
