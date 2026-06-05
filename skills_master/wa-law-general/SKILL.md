---
name: wa-law-general
description: Use when answering Western Australian legal information questions about WA court hierarchy.
---

# Western Australian Law — General Reference

> **MANDATORY DISCLAIMER**: This skill provides **general legal information** specific to Western Australia. It is **NOT legal advice**. Users MUST obtain independent legal advice from a WA lawyer, Legal Aid WA (1300 650 579), or a community legal centre before making any decisions or court applications.

## Response Protocol

1. Always open with the mandatory disclaimer (one sentence is sufficient in conversation)
2. Identify the area of law and applicable legislation (with section references where possible)
3. Provide substantive information; cross-reference specialist skills where relevant
4. Load reference files as needed for detail (see below)
5. Close with a referral recommendation appropriate to the user's situation

## Source Quality Protocol

Use primary sources first: WA legislation from `legislation.wa.gov.au`, official court websites, official practice directions/forms, and full judgments from AustLII, Jade, or court sites. Use Legal Aid WA and community legal centre resources for plain-language assistance. Do not rely on blogs, forums, marketing pages, or AI summaries for legal propositions. Verify current fees, forms, filing channels, and deadlines during the current task.

## Reference Files (Load When Needed)

| File | When to Load |
|------|-------------|
| `references/legal-services.md` | Legal Aid contacts, community legal centres, duty lawyers, specific service details |
| `references/court-procedures.md` | Filing steps, service requirements, court forms, fees, eCourts Portal guidance |

---

## WA Court Hierarchy

### Supreme Court

- **Jurisdiction**: Appeals from District Court; constitutional matters; judicial review
- **Divisions**: Court of Appeal, Court of Criminal Appeal, Equity, Common Law
- **Location**: Perth (St Georges Terrace)
- **Contact**: (08) 9264 5111
- **Website**: supremecourt.wa.gov.au

### District Court

- **Jurisdiction**: Civil cases up to $750,000; criminal matters (indictable offences)
- **Appeal jurisdiction**: Appeals from Magistrates Court
- **Location**: Perth (State Law Building)
- **Contact**: (08) 9273 5000
- **Website**: districtcourt.wa.gov.au

### Magistrates Court

- **Civil jurisdiction**: General procedure up to $75,000; minor case procedure up to $10,000
- **Criminal jurisdiction**: Summary offences (simple offences); indictable offences heard summarily
- **Locations**: Perth, Fremantle, Joondalup, Midland, Armadale, Mandurah, Rockingham, Bunbury, Kalgoorlie, Albany, Geraldton, Broome, and other regional centres
- **Contact**: (08) 9425 2222 (Perth)
- **Website**: magistratescourt.wa.gov.au
- **eLodgment**: ctghelpdesk@justice.wa.gov.au | (08) 9425 2645

### Specialist Courts/Tribunals

| Court/Tribunal | Jurisdiction | Location |
|---|---|---|
| FCFCOA (Federal Circuit and Family Court of Australia) | Family law (parenting, property division) | Perth |
| Children's Court | Juvenile offences, child protection | Perth, regional |
| Coroner's Court | Deaths in custody, suspicious deaths | Perth |
| SAT (State Administrative Tribunal) | Appeals from administrative bodies | Perth |
| Mental Health Tribunal | Mental Health Act reviews | Perth |
| Family Violence List (Magistrates Court) | FVRO/VRO applications and variations | Perth, regional |
| Drug Court (Magistrates Court) | Drug treatment orders | Perth |
| Geraldton Family Violence Court (Barndimalgu) | FVRO matters in the Mid West | Geraldton |
| Start Court (Magistrates Court) | Mental health diversion | Perth |

---

## Specialist Skills (Cross-Reference)

When user's question involves:

- **Family Violence Restraining Orders (FVRO)**: → `wa-fvro` skill
- **Mental Health Act 2014**: → Mental Health Law skill (if available)
- **Family Law (parenting, property)**: → Family Law skill (if available)

---

## Key WA Legislation by Subject Area

### Family Law

- **Restraining Orders Act 1997** (amended): FVROs, conditions, breach offences
- **Family Court Act 1997**: Family court jurisdiction and procedure
- **Maintenance Act 1966**: Child/spouse maintenance obligations

### Criminal Law

- **Criminal Code 1913**: Offences, sentencing, defences
- **Criminal Procedure Act 2004**: Criminal procedure and evidence
- **Criminal Law (Mental Impairment) Act 2023**: Fitness to plead, supervision orders, custody orders (replaces Criminal Law (Mentally Impaired Defendants) Act 1996)
- **Victims of Crime Assistance Act 1988**: Victim support and compensation
- **Surveillance Devices Act 1998**: Recording and monitoring restrictions (one-party consent under s.5(3); publication restrictions under s.9)

### Employment & Tenancy

- **Fair Work Act 2009** (Commonwealth): National employment standards
- **Minimum Conditions of Employment Act 1993** (WA): State minimum standards
- **Residential Tenancies Act 1987**: Landlord/tenant rights and obligations

### Administrative Law

- **State Administrative Tribunal Act 2004**: SAT review jurisdiction and procedures
- **Freedom of Information Act 1992**: FOI requests and government transparency
- **Ombudsman Act 1971**: Complaint mechanisms
- **Judicial review**: Verify the current court rules, enabling Act, and common law basis for the decision being challenged

### Civil Procedure

- **Magistrates Court (Civil Proceedings) Act 2004 and Rules 2005**: Magistrates Court civil procedure
- **District Court of Western Australia Act 1969 and District Court Rules 2005**: District Court jurisdiction and procedure
- **Rules of the Supreme Court 1971**: Supreme Court procedure
- **Evidence Act 1906 / Evidence Act 2025**: Check current commencement and transitional provisions before relying on WA evidence rules
- **Defamation Act 2005**: Defamation law

---

## Statutory Interpretation Principles

### Primary Rules (WA Courts)

1. **Literal/Grammatical Rule**: Words have their ordinary meaning unless context shows otherwise
2. **Purposive Approach**: Consider the object/purpose of the legislation
3. **Golden Rule**: Avoid absurd results by adjusting meaning if literal reading produces injustice
4. **Ejusdem Generis Rule**: General words following specific words take the meaning of the specific words
5. **Noscitur a Sociis Rule**: Words must be construed by the company they keep

### WA-Specific Guidance

- **Interpretation Act 1984** (WA): Sets out general rules for reading WA legislation
- **In Pari Materia Rule**: Statutes on the same subject matter should be read together
- **Historical Context**: Courts consider legislative history and prior case law

---

## Legal Services Quick Reference

### Legal Aid WA

- **Phone**: 1300 650 579
- **Website**: legalaidwa.wa.gov.au
- **Services**: Free advice, assistance, representation for eligible persons
- **Eligibility**: Income/asset tests apply; priority for family violence, criminal matters

### Community Legal Centres

- **Perth**: Streetlaw (homelessness, tenancy, employment)
- **Regional**: Community legal centres in Fremantle, Joondalup, Mandurah, Bunbury, Kalgoorlie
- **Services**: Free legal advice, community education

### Duty Lawyer Scheme

- **Available**: Most Magistrates and District Court sittings
- **Service**: Free representation for criminal accused at first court appearance
- **Access**: Contact court on the day for availability

### Lawyers & Law Firms

- **Law Society WA Directory**: lawsocietywa.asn.au/findlawyer
- **Dispute Resolution**: Mediation, arbitration services available

---

## Court Procedures Overview

### Filing Documents

1. **Prepare document** (statement of claim, application, etc.)
2. **File at court registry** (in person or via eCourts Portal)
3. **Pay filing fee** (fee varies by court and document type)
4. **Obtain court reference number** and file stamp
5. **Serve other party** (in person, post, or electronic service)
6. **File affidavit of service** with court
7. **Wait for directions/hearing date**

### eCourts Portal

- **Access**: www.ecourts.wa.gov.au
- **Features**: Document filing, payment, case tracking
- **Courts**: Magistrates Court, District Court (rolling rollout)
- **Registration**: Free; use in conjunction with legal representative or self-represented

### Service Requirements

- **Service method**: Personal service (preferred), post, email (if permitted), or electronic
- **Timing**: Documents must be served before specified date (usually 21 days before hearing)
- **Proof**: Affidavit of service filed with court

---

## Filing Fees (Approximate - Check Court Website)

> **Current fee schedule**: Check the [MCWA Fees page](https://magistratescourt.wa.gov.au/F/fees.aspx) and any linked current PDF before giving exact amounts. MCWA currently states there is no fee to apply for an FVRO or VRO, and that MRO proceedings have fees; verify the live page because fees and filing channels change.

| Court/Document | Fee Range |
|---|---|
| Magistrates Court (statement of claim) | $50–$200 |
| District Court (statement of claim) | $100–$500 |
| Supreme Court (civil appeal) | $200–$500 |
| Application (general) | $50–$150 |
| Affidavit filing | $20–$50 |
| Certified copies | $10–$20 per page |

**Note**: Fees subject to change; always check the [MCWA Fees page](https://magistratescourt.wa.gov.au/F/fees.aspx) for current rates.

---

## Legal Terminology (Common WA Terms)

| Term | Meaning |
|------|---------|
| **Affidavit** | Sworn written evidence |
| **Application** | Court filing requesting an order (e.g., variation) |
| **Court order** | Formal decision/judgment from judge |
| **Discovery** | Exchange of relevant documents before trial |
| **Injunction** | Court order restraining or requiring an action |
| **Judgment** | Court decision on the merits |
| **Judicial review** | Challenge to administrative decision |
| **Jurisdiction** | Court's legal power to hear a matter |
| **Leave** | Permission from court to proceed with application |
| **Subpoena** | Order to attend court or produce documents |
| **Transcript** | Written record of court hearing |

---

## Key Resources

| Resource | Purpose |
|----------|---------|
| [Supreme Court WA](https://supremecourt.wa.gov.au) | Official court website, practice directions, case reports |
| [District Court WA](https://districtcourt.wa.gov.au) | Case lists, fees, procedures |
| [Magistrates Court WA](https://magistratescourt.wa.gov.au) | Local court information, regional locations |
| [eCourts Portal](https://www.ecourts.wa.gov.au) | Electronic filing and case management |
| [Legislation Online (WA)](https://legislation.wa.gov.au) | Full text of WA Acts and regulations |
| [Law Society WA](https://lawsocietywa.asn.au) | Professional standards, lawyer directory |
| [Ombudsman WA](https://www.ombudsman.wa.gov.au) | Complaint mechanism for government agencies |

---

## When to Refer

Recommend independent legal advice when user:
- Faces court proceedings
- Needs to draft formal court documents
- Has potential criminal exposure
- Is considering family law matters
- Needs urgent/time-sensitive advice
- Faces complex multi-issue legal problem

## Common Mistakes

- Answering from memory where fees, forms, deadlines, or filing channels may have changed.
- Treating plain-language guides as authority without checking legislation, rules, or practice directions.
- Mixing WA state court procedure with Federal Court, FCFCOA, or interstate procedure.
- Giving advice on merits, strategy, or prospects instead of general legal information and referral.

## Validation

After editing this skill or its references, run:

```bash
docker compose -f compose.skills.yml run --rm skills-validator
```

Fallback:

```bash
uv run --project .maintenance/Skills-Framework-Reference skills-ref validate wa-law-general
```

## Cross-References to Other Skills

| Related Skill | Use when |
|---------------|----------|
| `wa-fvro` | FVRO-specific guidance — Form 12, s.45–46, s.61 breach, FVRO conferencing, NDVOS |
| `legal-matter-ops` | Full 15-phase lifecycle for evidence preparation, chain of custody, DOCX/PDF generation |
| `case-file-manager-wa` | Organising case folders, evidence indexes, dashboard documents for SRL matters |
| `affidavit-court-preparation` | Drafting affidavits, chronology reconstruction, hearing preparation |
| `wa-teacher-misconduct` | Teacher misconduct, TRBWA, WWC checks, professional boundaries |
| `csv-legal-analysis` | CSV/message data analysis, eDiscovery, SMS forensics |
| `reportlab-python` | Generating PDF court documents from Python |
| `pdfkit-node` | Generating PDF court documents from Node.js |
