---
name: wa-fvro
description: Use when handling Western Australian family violence restraining order information.
---

# WA FVRO Respondent Defence & Information Assistant

> **MANDATORY DISCLAIMER**: This skill provides **general legal information** specific to Western Australia. It is **NOT legal advice**. Users MUST obtain independent legal advice from a WA lawyer, Legal Aid WA (1300 650 579), or a community legal centre before making any decisions or court applications. Always display this disclaimer when providing FVRO information.

---

## Skill Behaviour

Identify the user's mode from context, then deliver substantive information:

| Mode | Trigger | Output |
|------|---------|--------|
| **Explain** | "What is…", "How does…", "Can I…" | Plain-language information with section references |
| **Vary** | "I want to vary…", "change conditions…" | s.45–46 process, leave test grounds, drafting guidance |
| **Cancel** | "I want to cancel…", "get rid of…" | Cancellation procedure, substantial change test, drafting |
| **Draft** | "Draft an affidavit…", "help me write…" | Structured affidavit from user facts; load `references/affidavit-templates.md` |
| **MHA Conflict** | "mental health…", "treatment conflict…" | MHA/FVRO intersection analysis; load `references/mha-intersections.md` |
| **Breach** | "charged with breach…", "she contacted me…" | Breach consequences, protected-person conduct analysis, load `references/case-law.md` |
| **Court Forms** | "what form do I need…", "how do I file…" | Load `references/court-forms.md` |

### Response Protocol

1. Open with the mandatory disclaimer
2. Identify mode and applicable provisions
3. Provide substantive information with section references and case law
4. Load reference files as needed for detail
5. Close with a referral recommendation appropriate to the user's situation

## Source Quality Protocol

Use the current Restraining Orders Act 1997 (WA) on `legislation.wa.gov.au`, official Magistrates Court WA forms/practice pages, and full judgments from AustLII/Jade/court sites. Treat unreported Magistrates Court anecdotes, forum posts, legal blogs, and AI summaries as non-authoritative. If a case cannot be retrieved from a reliable legal database, say that it needs verification before use in submissions.

---

## Respondent Rights Overview

### Initial Rights (Pre-Order)

- Right to be heard at interim FVRO application (s.31)
- Right to cross-examine applicant and witnesses
- Right to present evidence and affidavits
- Right to legal representation

### Post-Order Rights

- Right to apply for variation (s.45)
- Right to apply for cancellation (s.46)
- Right to challenge leave test requirements
- Right to defend breach charges

### Key Provisions

| Provision | Purpose |
|-----------|---------|
| s.31 | Interim FVRO application and respondent right to be heard |
| s.45–46 | Variation and cancellation applications |
| s.61 | Breach consequences and penalties |
| s.61A | Mandatory third-strike imprisonment |
| s.61B | Protected-person conduct in breach proceedings; check current text before relying on mitigation or variation consequences |

---

## Variation and Cancellation (s.45–46)

### The Leave Test

Before applying under s.45 or s.46, respondent must establish "leave" by:

1. **Change in circumstances** (substantial, material change since order made)
2. **New evidence** (could not have been available at original hearing)
3. **Injustice** (original decision was unjust in light of new facts)

### Variation Application Process

1. File **Form 12** (Application to Vary or Cancel a Restraining Order) — available from any MCWA registry or [MCWA Forms page](https://magistratescourt.wa.gov.au/F/forms.aspx)
2. File affidavit with application (sworn evidence of changed circumstances)
3. File via eLodgment (eCourts Portal — www.ecourts.wa.gov.au) or in person at any MCWA registry
4. Serve applicant (person with benefit of order)
5. Attend court (magistrate or judge considers leave test)
6. If leave granted, present case for variation
7. Court orders new conditions (or cancels if appropriate)

### Cancellation Application Process

Same as variation (Form 12), but grounds must show order is no longer necessary for:
- Safety of protected person
- Prevention of family violence
- Public protection

---

## Breach Consequences

### Breach Offence (s.61)

| Strike | Penalty | Sentence Type |
|--------|---------|---------------|
| First | Up to $5,000 fine or 12 months jail | Discretionary |
| Second | Up to $10,000 fine or 24 months jail | Discretionary |
| Third+ | Mandatory 12 months imprisonment | Non-discretionary |

### Breach Examples

- Contacting protected person (direct or indirect)
- Attending protected person's home, workplace, school
- Threatening or intimidating protected person
- Breaching specific conditions listed in order

---

## FVRO Conferencing

After objecting to an interim FVRO, the respondent may be offered an **FVRO conference** — a form of mediation conducted at the Magistrates Court. Conferences are available at Perth, Joondalup, Fremantle, Bunbury, and Armadale Magistrates Courts.

- Free legal advice is available for respondents at conferences (Sussex Street Community Law Service, Northern Suburbs CLC, FASS Legal Aid WA)
- The conference is facilitated by a trained mediator
- If agreement is reached, a final order (by consent) may be made
- If no agreement, the matter proceeds to a contested hearing
- More info: [MCWA FVRO Conferencing](https://magistratescourt.wa.gov.au/F/fvro_conferencing.aspx)

---

## National Domestic Violence Order Scheme (NDVOS)

From 25 November 2017, every new FVRO is **automatically recognised nationally** across all Australian states and territories under the National Domestic Violence Order Scheme.

- FVROs/VROs made before 25 Nov 2017 can be voluntarily declared as nationally recognised
- Applications for declaration are free and lodged at any MCWA registry
- A national DVO remains in force if the protected person moves interstate

---

## Mental Health Act 2014 (WA) Intersections

### MHA/FVRO Conflicts

When respondent is subject to Mental Health Act (MHA) order AND FVRO:

- MHA compulsion may conflict with FVRO restrictions
- MHA treatment facility may be in breach area
- Respondent may need variation to attend treatment

### Resolution Strategy

1. Identify specific MHA obligation vs. FVRO condition
2. Load `references/mha-intersections.md` for detailed guidance
3. Apply for variation under s.45 with evidence of MHA necessity
4. Courts typically accommodate MHA treatment needs

---

## Breach: Protected Person Conduct and s.61B

Protected-person contact does **not** automatically excuse a bound person's breach. Start from the order's terms: the bound person must comply unless the order is varied, cancelled, or a statutory defence applies.

Under the current Restraining Orders Act 1997 (WA), s.61B deals with protected-person conduct in breach matters. The protected person does not commit an offence merely by aiding a breach, and the court may consider specified protected-person conduct in sentencing or variation/cancellation pathways. Do not describe this as a broad "encouragement defence" unless the precise statutory defence or exception has been checked against the current Act.

### Required Analysis

- Read the exact order terms and identify the alleged breach act.
- Check ss.61, 61B, 61C, and 62 in the current Act.
- Record whether the protected person initiated contact without influence from the bound person.
- Separate liability, mitigation, and variation/cancellation issues.
- Refer urgently for legal advice if there is a charge, arrest, bail condition, or risk of imprisonment.

### Evidence Required

- Affidavit from protected person (if supportive)
- Text messages, emails, recordings showing encouragement
- Witness evidence of protected person requesting contact
- Respondent's contemporaneous notes/records

---

## Candidate WA Case Law To Verify

| Case | Citation | Research Use |
|------|----------|---------------|
| Roe v D'Costa | [2014] WASCA 118 | Candidate authority for s.61A mandatory-imprisonment preconditions; verify the current legislation and full judgment before citing. |
| Gull v Barker | [2013] WASC 398 | Candidate authority for interim-order threshold/procedural fairness issues; verify the full judgment before applying. |
| Mazurak v Stein | [2019] WASC 56 | Candidate authority for variation/cancellation leave analysis; verify the full judgment and current s.45/s.46 text before relying on it. |

> **Case-law rule**: Do not present a case proposition as settled law from this table alone. Open the judgment on AustLII, Jade, LexisNexis, Westlaw, or official court sources; confirm appeal history and current statutory wording; then state the proposition narrowly with a citation.

---

## Affidavit Drafting Guidance

### Structure for Variation Application

1. **Heading**: Case name, court, application type
2. **Declaration**: "I, [name], make oath/affirmation that the following is true and correct"
3. **Introductory paragraph**: Identity, connection to order, date order made
4. **Body paragraphs**: Numbered paragraphs, each single fact or piece of evidence
5. **Statement of changed circumstances**: Detailed narrative of changes since order
6. **New evidence section**: Any evidence unavailable at original hearing
7. **Injustice section**: How original decision was unjust based on changes
8. **Prayer/conclusion**: Request for variation/cancellation
9. **Signature block**: Signature, date, witnessed by lawyer or Justice of the Peace

### Key Drafting Tips

- Use plain language, avoid legal jargon
- State facts, not opinions or conclusions
- Each paragraph should address one fact
- Include dates, names, places, and specific details
- Avoid hearsay; use personal knowledge
- Attach copies of supporting documents
- Keep tone neutral and professional

---

## Resources and Referrals

### Legal Aid and Community Services

- **Legal Aid WA**: 1300 650 579 (free legal advice for eligible persons)
- **Community Legal Centres**: Network of free legal services
- **Duty Lawyer Program**: Free representation at first court appearance

### Court Services

- **Magistrates Court of WA**: Handles FVRO applications — [magistratescourt.wa.gov.au](https://magistratescourt.wa.gov.au)
- **District Court of WA**: Appeals and complex matters
- **eCourts Portal / eLodgment**: Online filing for vary/cancel applications and other documents — [www.ecourts.wa.gov.au](https://www.ecourts.wa.gov.au)
- **FVRO Conferencing**: Mediation available post-objection — [FVRO Conferencing info](https://magistratescourt.wa.gov.au/F/fvro_conferencing.aspx)
- **Online FVRO Applications**: Legal service providers can apply online via [victimsofcrime.wa.gov.au](https://www.victimsofcrime.wa.gov.au)

### Government Resources

- **Department of Communities**: Family and domestic violence support
- **WA Police Family Violence Response Team**: Investigation and protection
- **Department of Justice**: Court procedures and forms

---

## When to Refer

Recommend legal advice when user:
- Faces breach charges
- Needs to vary complex conditions
- Has MHA/FVRO intersection issues
- Wants to challenge interim order
- Is preparing for contested court appearance
- Has safety concerns or unique circumstances

## Common Mistakes

- Treating protected-person contact as automatic permission to breach an order.
- Giving strategy on an active breach charge instead of referring urgently for legal advice.
- Citing case law without reading the full judgment and checking current statutory wording.
- Assuming filing channels, fees, or forms have not changed.
- Drafting affidavits that argue conclusions rather than set out dated facts and source material.

## Validation

After editing this skill or its references, run:

```bash
docker compose -f compose.skills.yml run --rm skills-validator
```

Fallback:

```bash
uv run --project .maintenance/Skills-Framework-Reference skills-ref validate wa-fvro
```

## Cross-References to Other Skills

| Related Skill | Use when |
|---------------|----------|
| `legal-matter-ops` | Full 15-phase lifecycle for FVRO evidence preparation, chain of custody, Bates numbering |
| `case-file-manager-wa` | Organising case folders for self-represented FVRO respondent matters |
| `affidavit-court-preparation` | Drafting and refining FVRO affidavits, chronology reconstruction, hearing prep |
| `wa-law-general` | General WA court hierarchy, legislation, legal services, filing fees |
| `csv-legal-analysis` | Analysing messaging data for s.61B/protected-person-contact evidence |
| `wa-teacher-misconduct` | When FVRO intersects with teacher misconduct or WWC issues |
