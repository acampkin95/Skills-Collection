# Legal Workflow Skill — Templates Reference

This file contains all operational templates used by the legal matter workflow skill. Each template is ready for immediate use in case preparation, evidence management, disclosure, and hearing readiness.

**Last updated:** 2026-03-16
**Scope:** All templates use Australian English spelling and follow Australian legal practice conventions.

---

## Template 1: Evidence Inventory (CSV)

**Purpose:** Master log of all evidence collected, indexed, and referenced throughout the matter. Tracks provenance, strength assessment, and chain of custody linkage.

**Header Row:**
```csv
EvidenceID,Date,Description,Source,Category,EvidenceStrength,ConfidenceLabel,ChainOfCustodyRef,BatesRange,AnnexureRef,StoragePath,Notes,ReviewStatus
```

**Example Rows:**
```csv
EV001,2025-06-14,"Email from defendant to third party re: knowledge of defect","defendant_emails.zip","Documentary",STRONG,HIGH,CoC_2025_061_001,"BR_002-015","Annexure A","server://vault/EV001_email_chain.pdf","Demonstrates consciousness of guilt; forwarded to in-house counsel 2025-06-14","FINAL"
EV002,2025-07-20,"Photograph of product failure site; taken by claimant's engineer","site_inspection_photos/","Photographic",MODERATE,MEDIUM,CoC_2025_072_001,"BR_051-060","Annexure C","server://vault/EV002_site_photos/","Three angles provided; metadata preserved; taken before remediation work began","FINAL"
EV003,2025-08-01,"Maintenance log extract from defendant's systems (2023-2024)","discovery_batch_2.csv","Documentary",STRONG,HIGH,CoC_2025_080_001,"BR_100-125","Annexure B","server://vault/EV003_maintenance_log.pdf","Authenticated export from enterprise database; corroborates timeline of known defects","IN_REVIEW"
```

---

## Template 2: Chain of Custody Log (CSV)

**Purpose:** Auditable record of how each piece of evidence has been handled, stored, transformed, and transferred. Ensures legal admissibility and integrity.

**Header Row:**
```csv
ItemID,SourceFilename,EvidenceType,OriginalLocation,CollectionDate,CollectedBy,AcquisitionMethod,SHA256Hash,DerivativeOf,TransformationNotes,CurrentStoragePath,AccessNotes,ExhibitStatus,BatesRange,ReviewStatus
```

**Example Rows:**
```csv
CoC_2025_061_001,"defendant_emails_06-2025.zip","Digital Archive","Defendant's email server (domain: defendant.com.au)","2025-06-14","Sarah Chen (Solicitor)","Court-authorised disclosure order; extracted by defendant's IT services","a7f3e9d2c5b8e1f4a6d9c2e5f8a1b4c7d0e3f6a9b2c5d8e1f4a7b0c3d6e9","N/A","Native format preserved; no filtering or redaction applied at source","server://vault/chain_of_custody/CoC_2025_061_001/","Restricted to: legal team + counsel; access logged; 12 month retention hold","ORIGINAL","BR_002-015","FINAL"
CoC_2025_061_001_D1,"defendant_emails_06-2025_extracted.pdf","Derivative PDF","server://vault/chain_of_custody/CoC_2025_061_001/","2025-06-16","James Liu (Paralegal)","Digital extraction and PDF conversion; OCR applied","b2e4f7a9d1c3e6f8a0b4c7d9e2f5a8b1c4d7e0f3a6b9c2d5e8f1a4b7c0d3e","CoC_2025_061_001","Extracted 47 emails from thread tree; maintained folder structure in PDF bookmarks; searchable OCR layer added","server://vault/chain_of_custody/CoC_2025_061_001_D1/","Read-only; tracked in document version register; created per counsel request 2025-06-16","DERIVATIVE","BR_002-015","FINAL"
CoC_2025_072_001,"site_photos_20250720_raw.zip","Photo Library","Site inspection (GPS: -31.9505, 115.8605)","2025-07-20","Michael Torres (Expert Engineer)","In-situ photography; all metadata retained; geotagged","c9f1a3d5b7e0f2c4a6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8","N/A","Raw JPEG exports from camera; EXIF data preserved in separate CSV; no rotation or cropping applied","server://vault/chain_of_custody/CoC_2025_072_001/","Restricted to: engineering expert + counsel; photographic evidence restricted by court order","ORIGINAL","BR_051-060","IN_REVIEW"
```

---

## Template 3: Master Chronology (CSV)

**Purpose:** Timeline of all factually and legally significant events. Used to construct narrative of facts, test consistency, and support causation arguments.

**Header Row:**
```csv
EventID,Date,Time,EndDate,Description,FactType,Source,EvidenceRef,BatesRef,ConfidenceLabel,DisputedBy,Notes
```

**Example Rows:**
```csv
CHR_001,"2023-03-15","09:30","N/A","Defendant's internal email discussing known product defect","DIRECT_FACT","EV001; Email metadata","EV001","BR_002-005","HIGH","Not disputed in discovery","Sent from [defendant.email@defendant.com.au] to [ceo@defendant.com.au]; subject line: 'URGENT: QA Issue in Batch 2023-03'"
CHR_002,"2023-03-20","","2023-04-10","Defendant continues production of affected batch despite awareness of defect","INFERRED","CoC_2025_061_001; maintenance logs; production schedules","EV001, EV003","BR_010-012, BR_100-110","MEDIUM","Defendant claims defect was isolated to single unit; inconsistent with batch-wide production","Inference based on: (a) defect known 2023-03-15; (b) production continued; (c) no recall issued until 2023-06-14"
CHR_003,"2023-06-14","11:45","N/A","Claimant first became aware of defect through product failure","DOCUMENTED_EVENT","Claimant's inspection report; site photos","EV002","BR_051-055","HIGH","Defendant disputes causation of failure; accepts date","Photo evidence with timestamp 2023-06-14 11:45 AWST; corroborated by claimant's diary entry same date"
CHR_004,"2025-06-01","14:00","N/A","Defendant's legal team receives discovery obligation notice for proceedings","REPORTED_STATEMENT","Court orders; defendant's solicitor letter","N/A","N/A","HIGH","Not disputed","Email from defendant's solicitor confirms receipt; identifies 12-week document collection deadline"
```

**FactType Key:**
- `DIRECT_FACT`: Witness observation or contemporaneous document
- `DOCUMENTED_EVENT`: Formal record (court order, contract, bank statement)
- `REPORTED_STATEMENT`: Third-party account (hearsay with source noted)
- `INFERRED`: Logical conclusion from other facts; confidence label signals strength
- `BACKGROUND`: Context fact without direct legal relevance
- `ALLEGATION`: Party's claim; not independently verified

---

## Template 4: Claim Support Matrix (CSV)

**Purpose:** Maps each legal element of the claim to factual basis and evidence. Identifies gaps, weak points, and areas where counter-evidence exists.

**Header Row:**
```csv
IssueID,LegalElement,FactualBasis,EvidenceRefs,BatesRefs,Strength,CounterEvidence,Gaps,Status
```

**Example Rows:**
```csv
ISS_001,"Negligence: Duty of Care","Defendant manufactured product supplied to claimant; relationship created legal duty","CHR_001, CHR_002, Contract 2023-02-01","BR_001-010, BR_500-520","STRONG","None identified; defendant admits manufacture","None; duty clearly established by statute and common law","CLOSED"
ISS_002,"Negligence: Breach","Defendant continued production of defective batch despite knowledge (2023-03-15) and failed to recall for 3 months","EV001, EV003, CHR_002, CHR_003","BR_002-005, BR_100-110, BR_051-055","MODERATE","Defendant claims: (a) defect isolated to single unit; (b) recall delay due to batch traceability issues; (c) standard practice in industry","Defendant's manufacturing audit records for 2023-03 and 2023-04 not yet received; ISO 9001 compliance documentation needed to support 'standard practice' claim","OPEN"
ISS_003,"Causation: Defect caused failure","Site photos (2023-06-14) show failure consistent with known defect; expert engineer supports nexus","EV002, Expert Report (pending), CHR_003","BR_051-060, BR_300-320 (expert)","MODERATE","Defendant's expert will likely argue: (a) claimant mishandled product post-sale; (b) environmental factors contributed; (c) alternative defects possible","Expert-to-expert evidence exchange not yet concluded; defendant's expert report awaited; independent causation analysis needed","OPEN"
ISS_004,"Damages: Economic loss quantifiable","Claimant's cost claim supported by invoices and quotes for remediation work","Invoices EV_010-015, Repair quotes EV_016-018","BR_200-250","STRONG","Defendant challenges: (a) quantum of quotes (claims cheaper options available); (b) necessity of 'premium' materials used","Market comparison analysis not yet completed; industry standard remediation costs need independent verification","OPEN"
```

---

## Template 5: Disclosure Schedule (CSV)

**Purpose:** Record of all documents disclosed to opponent, including date disclosed, privilege status, and linkage to Bates numbering.

**Header Row:**
```csv
DisclosureID,Date,DocumentDescription,Category,Privilege,BatesRange,SourcePath,DisclosedTo,DisclosedDate,Notes
```

**Example Rows:**
```csv
DISC_001,"2025-09-01","Email chain: Defendant internal discussion re: product QA (47 emails; 2023-03-15 to 2023-06-14)","Documentary","None","BR_002-050","server://vault/disclosure_batch_1/emails_qa_2023.pdf","Claimant's solicitor (XYZ Law)","2025-09-01","Disclosed pursuant to discovery order dated 2025-06-01; produced on USB drive (SHA256: a7f3e9d2c5b8e1f4a6d9c2e5f8a1b4c7); receipt acknowledged"
DISC_002,"2025-09-08","Internal legal opinion from defendant's counsel re: product liability exposure (prepared 2023-06-15)","Documentary","Legal Professional Privilege (LPP)","N/A","server://vault/privilege_log/opinion_20230615.pdf","Not disclosed (Privilege Claim)","N/A","Included on privilege schedule dated 2025-09-08; defendant maintains privilege on basis of legal advice sought in anticipation of litigation"
DISC_003,"2025-09-15","Maintenance and service records for all units manufactured 2023-02-01 to 2023-08-31","Documentary","None","BR_100-350","server://vault/discovery_batch_2/maintenance_logs_2023.csv","Claimant's solicitor (XYZ Law)","2025-09-15","Extracted from enterprise database; CSV format with SQL query metadata; produced on USB (SHA256: b2e4f7a9d1c3e6f8a0b4c7d9e2f5a8b1c4d7e0f3a); verification report attached"
DISC_004,"2025-09-15","Site inspection photographs from claimant's engineer (20 images; 2023-06-20)","Photographic","None","BR_051-070","server://vault/claimant_evidence/site_photos_batch_1/","Claimant's solicitor (XYZ Law)","2025-09-15","Voluntarily disclosed by claimant as part of case opening; images provided in individual JPEG + contact sheet PDF; metadata preserved"
```

---

## Template 6: Annexure Index (CSV)

**Purpose:** Register of all annexures attached to affidavits or court documents. Ensures all cross-references are correct and no exhibits are orphaned.

**Header Row:**
```csv
AnnexureID,Description,EvidenceRef,BatesRange,PageCount,PreparedDate,Status,VerifiedBy
```

**Example Rows:**
```csv
Annexure A,"Email chain: Defendant's internal QA discussion (2023-03-15 to 2023-06-14; 47 emails)","EV001","BR_002-050","49","2025-10-01","FINAL","Sarah Chen (Solicitor)"
Annexure B,"Maintenance and service log extract (2023-02-01 to 2023-08-31); CSV converted to PDF with index","EV003","BR_100-350","251","2025-10-02","FINAL","James Liu (Paralegal)"
Annexure C,"Site inspection photographs and technical analysis (20 photos + 5-page analysis)","EV002","BR_051-070","25","2025-10-03","IN_REVIEW","Michael Torres (Expert)"
Annexure D,"Contract of Sale dated 2023-02-01 and Schedule of Goods (2 pages)","EV_005","BR_400-401","2","2025-10-04","FINAL","Sarah Chen (Solicitor)"
```

---

## Template 7: Bates Register (CSV)

**Purpose:** Master register of all Bates number ranges assigned. Prevents numbering conflicts, tracks assignment authority, and records any reassignments or replacements.

**Header Row:**
```csv
BatesPrefix,StartNumber,EndNumber,DocumentDescription,EvidenceRef,AnnexureRef,AssignedDate,AssignedBy,ReplacedBy,Notes
```

**Example Rows:**
```csv
BR,1,50,"Email chain: Defendant internal QA discussion","EV001","Annexure A","2025-10-01","Sarah Chen","None","Assigned to Annexure A in affidavit dated 2025-10-15"
BR,51,70,"Site inspection photographs and technical analysis","EV002","Annexure C","2025-10-03","Sarah Chen","None","Assigned to Annexure C in affidavit dated 2025-10-15; expert report integrated"
BR,100,350,"Maintenance and service logs (2023)","EV003","Annexure B","2025-10-02","Sarah Chen","None","Assigned to Annexure B; large document range due to CSV export volume"
BR,400,401,"Contract of Sale and Schedule","EV_005","Annexure D","2025-10-04","Sarah Chen","None","Assigned to Annexure D; foundational contract"
BR,500,550,"Expert engineering report (pending final version)","EV_expert_001","Annexure E","2025-10-06","Sarah Chen","BR_500-600","Preliminary range assigned; final range TBD pending report completion and page count confirmation"
```

---

## Template 8: Version Register (CSV)

**Purpose:** Tracks all drafts, reviews, and final versions of court documents. Prevents accidental filing of outdated versions and maintains audit trail.

**Header Row:**
```csv
DocumentID,Filename,Version,Status,CreatedDate,CreatedBy,SupersededDate,SupersededBy,ArchivePath,Notes
```

**Example Rows:**
```csv
DOC_AFF_001,"Affidavit_Sarah_Chen_v1.docx","v1.0","DRAFT","2025-09-20","Sarah Chen","2025-09-25","v2.0","archive://drafts/AFF_001_v1/","Initial draft; evidence references incomplete"
DOC_AFF_001,"Affidavit_Sarah_Chen_v2.docx","v2.0","REVIEW","2025-09-25","Sarah Chen","2025-10-01","v3.0","archive://drafts/AFF_001_v2/","First counsel review; amendments to pars. 12-18; cross-references to Bates numbers added"
DOC_AFF_001,"Affidavit_Sarah_Chen_v3.docx","v3.0","FINAL","2025-10-01","Counsel (Jane Smith)","2025-10-15","FILED","archive://final/AFF_001_v3/","Final version; filed with court 2025-10-15 at 14:30 AWST; court file number [2025-12345]"
DOC_BUNDLE_001,"Court_Bundle_Hearing_Prep_v1.pdf","v1.0","DRAFT","2025-10-10","James Liu","2025-10-12","v2.0","archive://drafts/BUNDLE_001_v1/","Incomplete; page numbering and cross-references not finalised"
DOC_BUNDLE_001,"Court_Bundle_Hearing_Prep_v2.pdf","v2.0","REVIEW","2025-10-12","James Liu","2025-10-14","v3.0","archive://drafts/BUNDLE_001_v2/","Counsel review; formatting amendments; manifest checked against file list"
DOC_BUNDLE_001,"Court_Bundle_Hearing_Prep_v3.pdf","v3.0","FINAL","2025-10-14","Counsel (Jane Smith)","2025-10-16","FILED","archive://final/BUNDLE_001_v3/","Ready for print; hash: e2d4f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d"
```

**Status Values:** `DRAFT` | `REVIEW` | `FINAL` | `FILED` | `SUPERSEDED` | `ARCHIVED`

---

## Template 9: Issues Register (CSV)

**Purpose:** Tracks all outstanding issues, blockers, or action items arising from document review, evidence gaps, or legal analysis.

**Header Row:**
```csv
IssueID,IssueDescription,Category,Priority,EvidenceRefs,Status,AssignedTo,DueDate,Resolution,Notes
```

**Example Rows:**
```csv
ISSUE_001,"Defendant's expert report not yet received; causation evidence incomplete","Evidence Gap","HIGH","EV002, EV_expert_001","OPEN","Sarah Chen","2025-10-20","Pending","Court order requires exchange by 2025-10-20; followup letter sent 2025-10-10"
ISSUE_002,"Manufacturing audit records for 2023-03 and 2023-04 still outstanding from discovery","Evidence Gap","HIGH","EV003","OPEN","James Liu","2025-10-18","Pending","Defendant granted extension to 2025-10-18; non-compliance escalation planned if not received"
ISSUE_003,"Affidavit para. 24 references Bates BR_123 but evidence shows range should be BR_120-128; cross-reference error identified in final review","Documentation Error","MEDIUM","DOC_AFF_001_v3","CLOSED","Sarah Chen","2025-10-14","Corrected para. 24; v4 not required as error detected pre-filing and corrected in manuscript","Error caught during final print review; notation made in version register"
ISSUE_004,"Site expert recommends independent causation analysis by second engineering firm to counter defendant's position","Legal Strategy","MEDIUM","EV002, Expert_Report_v1","OPEN","Counsel (Jane Smith)","2025-10-25","Pending client decision","Cost estimate: AUD $8,500; counsel advice: advisable given defendant's expected challenge to first expert"
ISSUE_005,"Damages quantum: market comparison analysis incomplete; three quotes obtained but industry standard verification outstanding","Evidence Gap","LOW","EV_010-018","OPEN","James Liu","2025-10-22","Pending","Instructed quantity surveyor on 2025-10-10; interim report due 2025-10-22"
```

---

## Template 10: Final Run Report (Markdown)

**Purpose:** Pre-filing checklist and risk summary. Confirms matter is ready for court, identifies remaining gaps, and flags items requiring counsel attention before filing.

```markdown
# FINAL RUN REPORT
## [Matter Name and File Number]

**Prepared by:** [Your name and role]
**Prepared date:** [YYYY-MM-DD AWST]
**Reporting period:** [From date to date]
**Matter status:** [Hearing prep / Ready for filing / Awaiting orders]

---

## 1. Matter Summary

**Parties:** [Claimant] v [Defendant(s)]
**Court:** [Court name and jurisdiction]
**File number:** [Court file number, if assigned]
**Nature of claim:** [e.g. Product liability / Negligence / Breach of contract]
**Key issues:** [1–3 line summary of core legal elements in dispute]
**Hearing date (if fixed):** [Date and time, or "Not yet fixed"]
**Current phase:** [Discovery / Evidence exchange / Hearing prep / Trial]

---

## 2. Completeness Checklist

**Folder compliance:** ✓ PASS / ⚠ PASS WITH NOTES / ✗ FAIL
- Evidence folder fully indexed and chain of custody complete
- Disclosure schedule prepared and verified against source files
- All evidence tagged with EvidenceID and linked to Bates register
- AI working folder (99_AIStore) present and properly labelled as non-court-ready
- Court-facing folder sealed and verified for no AI material

**Notes:** [If not PASS, describe status and remedial action needed]

---

**Evidence indexed:** ✓ PASS / ⚠ PASS WITH NOTES / ✗ FAIL
- Evidence Inventory complete (all items logged with source and category)
- Chain of Custody log complete and hashes verified for digital evidence
- All evidence assigned to Bates range
- All evidence cross-referenced to annexures and affidavits

**Notes:** [If not PASS, list items outstanding]

---

**Chronology complete:** ✓ PASS / ⚠ PASS WITH NOTES / ✗ FAIL
- Master Chronology prepared with all legally significant events
- Timeline tested against evidence and marked with confidence labels
- Disputed facts identified and counter-evidence noted
- Causation chain documented and reviewed by counsel

**Notes:** [If not PASS, list gaps and expected completion date]

---

**Affidavit drafted:** ✓ PASS / ⚠ PASS WITH NOTES / ✗ FAIL
- Affidavit text complete and paragraph-numbered
- All material facts supported by evidence with Bates references
- Cross-references to Annexures verified (no orphaned exhibits)
- Witness statement or expert declaration obtained (if required)
- Signed and sworn (or ready for swearing)

**Notes:** [Version number of final affidavit; any sections pending counsel input]

---

**Disclosure prepared:** ✓ PASS / ⚠ PASS WITH NOTES / ✗ FAIL
- Disclosure Schedule complete with all discovered documents listed
- Privilege claims assessed and logged on separate privilege schedule
- Disclosure folder structure matches schedule and Bates numbering
- Documents redacted (where applicable) and redaction schedule prepared
- Delivery method and receipt acknowledgement arranged

**Notes:** [Date scheduled for disclosure; any outstanding searches or queries from opponent]

---

**Bates assigned:** ✓ PASS / ⚠ PASS WITH NOTES / ✗ FAIL
- Bates Register complete; all documents in court bundle assigned unique ranges
- No numbering gaps or overlaps
- Bates numbers appear on every page of annexures and bundled documents
- Bundle manifest matches Bates register

**Notes:** [Prefix used; any reassignments or corrections made]

---

**Formatting validated:** ✓ PASS / ⚠ PASS WITH NOTES / ✗ FAIL
- All documents in A4 format
- Black and white safe (no colour-dependent formatting)
- Page margins and heading styles consistent throughout
- Font sizes and line spacing meet court requirements
- No metadata in PDFs (author, creation date stripped)

**Notes:** [Any formatting exceptions approved by counsel; describe]

---

**Hearing prep completed:** ✓ PASS / ⚠ PASS WITH NOTES / ✗ FAIL
- Hearing Prep document drafted with case summary, key issues, and anticipated challenges
- One-page hearing summary prepared and reviewed by counsel
- Evidence map prepared linking each issue to supporting Bates range
- Oral argument outline prepared
- Witness notes completed (if applicable)
- Response prompts drafted for anticipated defence arguments

**Notes:** [Expected completion of witness preparation; any outstanding expert conferences]

---

**Adversarial review completed:** ✓ PASS / ⚠ PASS WITH NOTES / ✗ FAIL
- Critical colleague review conducted by second lawyer
- Weaknesses, gaps, and credibility risks identified and documented
- Unsupported assertions flagged and evidence checked
- Emotional framing and tone reviewed for judicial neutrality
- Recommended actions before filing completed (or scheduled)

**Notes:** [Reviewer name; key findings and responses; any items deferred to post-hearing]

---

## 3. Risk Flags Summary

**Critical risks** (must resolve before filing):
- [Risk description; impact; mitigation status]
- [Next risk]

**Significant risks** (should resolve before filing; escalate to counsel):
- [Risk description; impact; mitigation status]
- [Next risk]

**Monitor only** (low probability; manageable if occurs):
- [Risk description; contingency plan]
- [Next risk]

---

## 4. Unsupported Claims

**Claims with no supporting evidence:**
- Claim description: [e.g. "Defendant knew of defect on 2023-03-15"]
  Current status: [Evidence exists but not yet located / Reliance only on inference / Awaiting expert opinion]
  Remedial action: [Describe plan to address; completion date]

**Claims with weak supporting evidence** (confidence label LOW or MEDIUM only):
- Claim description and confidence basis
- Remedial action if needed

**Claims where counter-evidence exists:**
- Claim description
- Counter-evidence identified: [Description and source]
- Counsel assessment: [Viable defence / Requires expert response / Abandon claim]

---

## 5. Confidence Label Distribution

**Summary table:**

| Confidence Label | Count of facts | Key examples |
|---|---|---|
| HIGH | [Count] | [1–2 key facts with very strong support] |
| MEDIUM | [Count] | [1–2 facts with mixed or incomplete evidence] |
| LOW | [Count] | [1–2 inferred or weakly supported facts] |

**Analysis:** [Commentary on overall strength of factual case; any clusters of low-confidence facts that weaken specific legal elements]

---

## 6. Chain of Custody Breaks

**Breaks or gaps identified:**
- [Description of break; evidence item affected; risk assessment]
- [Next break]

**Items flagged for further investigation:**
- [Item ID and description]
- [Status: Resolved / Pending investigation / Accepted risk]

---

## 7. Missing Context Items

**Evidence still needed:**
- Item description and category [e.g. "Manufacturing audit logs for 2023-03"]
- Status: [Not yet requested / Requested on DATE / Due DATE / Outstanding]
- Impact on case if not obtained: [Moderate / High / Critical]

**Explanations still needed:**
- Description [e.g. "Defendant's reason for 3-month delay in recall"]
- Current status: [Expert report awaited / Awaiting defendant response to interrogatory / Scheduled for cross-examination]

---

## 8. Stale Drafts

**Superseded versions still in working folders:**
- [Filename and version number]
- [Status: Archived / Awaiting archival / Retained intentionally (reason)]

---

## 9. Duplicate Evidence

**Potential duplicates identified:**
- [Items compared; determination: Confirmed duplicate / Substantive differences / Derivative (intentional)]
- [Remedial action: Removed from index / Consolidated / Retained with cross-reference]

---

## 10. Human Review Items

**Items requiring counsel sign-off before next phase:**
- [Description; assigned to: [Name]]
- [Description; assigned to: [Name]]

**Items requiring client approval:**
- [Description; context and decision required]
- [Description]

---

## 11. Print Readiness Status

**Status:** ✓ PRINT READY / ⚠ CONDITIONAL (describe conditions) / ✗ NOT READY (describe blockers)

**Conditions for print readiness** (if conditional):
- [Condition 1: status and remedial action]
- [Condition 2]

**Print environment verified:**
- Printer colour/B&W capability confirmed
- Paper size confirmed (A4)
- Binding and collation method confirmed
- Delivery timeline to court confirmed

---

## 12. Bundle Manifest Summary

**Bundle composition:**
- Total documents: [Count]
- Total pages: [Count]
- Bates range: [e.g. BR_001 to BR_500]
- Annexures: [Count and list]

**Print manifest:**
- File: [Filename and location]
- Hash: [SHA256 hash of final bundle PDF]
- Date prepared: [YYYY-MM-DD]
- Print order verified: ✓ YES / ✗ NO

---

## 13. Sign-Off Section

**Prepared by:**
Name: [Your name]
Role: [Your role]
Date: [YYYY-MM-DD AWST]
Signature: ___________________________

**Reviewed by:** [If applicable]
Name: [Reviewer name]
Role: [Reviewer role]
Date: [YYYY-MM-DD AWST]
Signature: ___________________________

**Counsel approval:**
Name: [Counsel name]
Date: [YYYY-MM-DD AWST]
Approval status: ✓ APPROVED / ⚠ APPROVED WITH CONDITIONS / ✗ REQUIRES AMENDMENTS

**Conditions or amendments required:** [If applicable]

---

**Document ID:** [e.g. DOC_FINAL_RUN_REPORT_001]
**Version:** FINAL
**Archive path:** [Path to version register entry]

```

---

## Template 11: Hearing Prep (Markdown)

**Purpose:** Comprehensive brief for advocate preparing for hearing. Includes case summary, evidence map, anticipated challenges, and response strategy.

```markdown
# HEARING PREPARATION BRIEF
## [Matter Name and File Number]

**Prepared by:** [Your name]
**Prepared date:** [YYYY-MM-DD AWST]
**Hearing date:** [YYYY-MM-DD HH:MM] at [Court name and address]
**Before:** [Judge/Magistrate name, if known]

---

## 1. Case Summary (Maximum 1 Page)

**Parties:**
Claimant: [Full name and description]
Defendant(s): [Full name(s) and description(s)]

**Nature of claim:**
[One sentence; e.g. "Claim for damages arising from breach of duty of care by defendant in manufacturing and supplying a defective product that caused loss to claimant."]

**Relief sought:**
[e.g. "Damages for economic loss (remediation costs: AUD $125,000); interest and costs."]

**Key dates:**
- [Important event date and brief description]
- [Next key date]

**Critical factual matrix:**
[2–3 sentences establishing the core dispute; what defendant denies or disputes]

**Strongest point for claimant:**
[The single most compelling fact, evidence, or legal principle favoring your client]

---

## 2. Key Issues

**Issue 1: [Legal element, e.g. "Duty of Care"]**
- Legal test: [Citation to statute or principle]
- Factual argument: [Your position; how facts support it]
- Opponent's likely argument: [What defendant will contend]
- Status: [Uncontested / Disputed]

**Issue 2: [Legal element, e.g. "Breach"]**
- Legal test: [Citation]
- Factual argument: [Your position]
- Opponent's likely argument: [What defendant will contend]
- Status: [Uncontested / Disputed / Conceded]

**Issue 3: [Legal element, e.g. "Causation"]**
- Legal test: [Citation]
- Factual argument: [Your position]
- Opponent's likely argument: [What defendant will contend]
- Status: [Uncontested / Disputed]

---

## 3. Orders Sought

**Primary orders:**
1. [Order description; e.g. "Judgment for claimant in the sum of AUD $125,000"]
2. [Next order]

**Alternative orders** (if primary not granted):
1. [Fallback relief; e.g. "Damages assessed as [lower figure]"]
2. [Next alternative]

**Incidental orders:**
- [Interest: rate, period of calculation]
- [Costs: on what basis; any departure from usual order sought]

---

## 4. Evidence Map

**Issue 1: [Legal element, e.g. "Duty of Care"]**

| Evidence Item | Bates Range | Type | Strength | Relevance |
|---|---|---|---|---|
| Contract of Sale dated 2023-02-01 | BR_400-401 | Documentary | STRONG | Establishes supply relationship and implied duty |
| Email from defendant sales team | BR_020-022 | Documentary | STRONG | Acknowledges product specification and warranties |
| [Next evidence] | BR_### | [Type] | [STRONG/MODERATE/WEAK] | [Brief relevance statement] |

**Issue 2: [Legal element, e.g. "Breach"]**

| Evidence Item | Bates Range | Type | Strength | Relevance |
|---|---|---|---|---|
| Internal QA email dated 2023-03-15 | BR_002-005 | Documentary | STRONG | Demonstrates knowledge of defect; supports inference of continued risk |
| Maintenance logs (2023-03 to 2023-06) | BR_100-110 | Documentary | MODERATE | Timeline of service issues consistent with known defect |
| Expert report (causation analysis) | BR_300-320 | Expert opinion | MODERATE | Expert assessment that continued operation without recall was negligent |

**Issue 3: [Legal element, e.g. "Causation"]**

| Evidence Item | Bates Range | Type | Strength | Relevance |
|---|---|---|---|---|
| Site inspection photographs | BR_051-060 | Photographic | STRONG | Visual evidence of failure mode consistent with known defect |
| Expert engineering report | BR_300-320 | Expert opinion | STRONG | Expert confirms nexus between defect and failure |
| Claimant's inspection diary | BR_051-055 | Documentary | MODERATE | Contemporaneous record of failure discovery and initial investigation |

---

## 5. Anticipated Challenges

**Anticipated Defence Argument 1:**
[Description of defence position; e.g. "Claimant mishandled the product and caused the failure"]

**Your response:**
[How you will counter the argument; evidence to rely on; points to emphasise]

**Documents to have available:**
- [Bates range or evidence ID]
- [Next document]

---

**Anticipated Defence Argument 2:**
[Description; e.g. "The defect was isolated to a single unit and was not batch-wide"]

**Your response:**
[Counter-argument with evidence; expert opinion if available; alternative factual scenario if defendant's version accepted]

**Documents to have available:**
- [Bates range]
- [Next document]

---

**Anticipated Defence Argument 3:**
[Description]

**Your response:**
[Counter-argument]

**Documents to have available:**
- [Bates range]

---

## 6. Response Prompts (If Cross-Examined)

**If asked: "How do you know the defect existed on 2023-03-15?"**

**Response structure:**
1. Refer to evidence: [Bates range and document description]
2. Key passage: [Quote key sentence if helpful]
3. Supporting evidence: [Corroborating documents or timeline]
4. Reinforce: [Why this undermines defendant's position or supports your claim]

---

**If asked: "Why should the court accept your expert's opinion over the defendant's expert?"**

**Response structure:**
1. Qualifications: [Your expert's relevant expertise and experience]
2. Methodology: [How opinion was formed; reference to evidence examined]
3. Consistency: [How opinion aligns with documentary evidence]
4. Defendant's gaps: [Weaknesses in defendant's expert analysis]
5. Reinforce: [Why your expert's opinion is more reliable]

---

**If asked: "Isn't it possible that claimant's handling of the product caused the failure?"**

**Response structure:**
1. Acknowledge the question: [Demonstrate you understand the alternative]
2. Refute with evidence: [Documentary evidence showing claimant's proper handling; expert opinion on failure mode]
3. Timeline: [When failure occurred vs. when claimant received the product; maintenance logs showing no issues until defect manifested]
4. Inherent design: [Why the defect, not mishandling, is the proximate cause]
5. Burden: [Remind court it is defendant's burden to prove alternative causation on balance]

---

**If asked: "How do you arrive at the damages figure of AUD $125,000?"**

**Response structure:**
1. Itemisation: [Breakdown of heads of loss: remediation AUD $80,000; [next head] AUD $X]
2. Evidence: [Quotes, invoices, expert assessment; Bates ranges]
3. Reasonableness: [Comparable costs from independent sources if available]
4. Impact on claimant: [Explain why sum is necessary to put claimant back in position if not for breach]
5. Alternatives: [If court finds lower figure, indicate willingness to address]

---

## 7. Witness Notes (If Applicable)

**Witness 1: [Name and role]**
- Key evidence to be given: [E.g. "Recollection of product failure on 2023-06-14"]
- Bates references to refresh memory: [BR_051-055; site inspection diary]
- Potential weaknesses in testimony: [E.g. "Time gap between event and affidavit"]
- Cross-examination risks: [What defendant will likely challenge]
- Preparation notes: [Any areas requiring further practice or clarification]

**Witness 2: [Name and role]**
- Key evidence: [Description]
- Bates references: [Ranges]
- Weaknesses: [Description]
- Cross-examination risks: [Description]
- Preparation notes: [Description]

---

## 8. Oral Argument Outline

**Opening (2–3 minutes):**
1. Introduce parties and relief sought
2. State the case in one compelling sentence
3. Signpost the three key issues and how evidence supports you on each

**Issue 1: Duty of Care (2 minutes)**
- Legal principle: [Citation]
- Application: [How facts establish duty; reference to contract and warranties]
- Concede if uncontested: [If defendant agrees to this element, move on quickly]

**Issue 2: Breach (4–5 minutes)**
- Legal principle: [Citation; standard of care required]
- Application: [Timeline of knowledge (2023-03-15) → continued operation → failure (2023-06-14)]
- Documentary evidence: [Internal QA email (BR_002-005) proves knowledge; maintenance logs (BR_100-110) show continued problems]
- Defendant's likely response: [Isolated unit claim] → Your counter: [Batch-wide production continued; recall delayed 3 months with no justification]
- Conclusion: [Breach is clear and uncontested]

**Issue 3: Causation (3–4 minutes)**
- Legal principle: [Balance of probabilities; nexus between breach and loss]
- Documentary evidence: [Site photos (BR_051-060) show failure mode matching known defect]
- Expert evidence: [Engineering report (BR_300-320) confirms causation]
- Defendant's likely challenge: [Claimant mishandled product] → Your counter: [No evidence of mishandling; timeline inconsistent; expert rules this out]
- Conclusion: [Causation proven on balance]

**Damages (2–3 minutes)**
- Itemised claim: [AUD $80,000 remediation + AUD $45,000 consequential loss]
- Evidence: [Quotes and invoices (BR_200-250); expert assessment]
- Reasonableness: [Comparable costs; industry standards]

**Closing (1–2 minutes):**
- Recap the three issues: [Duty ✓ Breach ✓ Causation ✓]
- Ask for judgment: [Specific orders sought]
- Costs: [On what basis]

---

## 9. Documents Needed at Hearing

**Essential documents to have in hard copy:**
- Bundle of all Annexures (with Bates numbers visible on every page)
- Hearing Brief (this document)
- One-page hearing summary
- Chronology
- Claim Support Matrix
- Witness statements/affidavits

**Additional documents to have available (but not necessarily printed in volume):**
- Evidence Inventory (searchable digital copy)
- Chain of Custody log (for authenticity challenges)
- Privilege schedule (if privilege issues arise)
- Version Register (in case of document authentication questions)

**Contingency items:**
- Laptop and PDF reader for rapid document access if paper copies insufficient or lost
- USB drive with all evidence (if court accepts digital exhibits)
- Contact details for expert witnesses (in case urgent consultation needed during hearing)

---

**Document ID:** [e.g. DOC_HEARING_PREP_001]
**Version:** FINAL
**Archive path:** [Version register entry]

```

---

## Template 12: One-Page Hearing Summary (Markdown)

**Purpose:** Concise, single-page brief for advocate and judge. Suitable for circulation before hearing; can be read in 2–3 minutes.

```markdown
# ONE-PAGE HEARING SUMMARY

**[Matter Name and File Number]**

---

**PARTIES**
Claimant: [Full name]
Defendant: [Full name(s)]

**JURISDICTION & DATES**
Court: [Court name and location]
Hearing date: [YYYY-MM-DD] | File number: [Court file number] | Nature: [e.g. "Product liability claim"]

---

**CORE ISSUES (In dispute)**
1. [Issue 1, e.g. "Whether defendant breached duty of care by continuing production of defective product"]
2. [Issue 2, e.g. "Whether breach caused claimant's loss"]
3. [Issue 3, e.g. "Quantum of damages"]

---

**ORDERS SOUGHT**
Judgment for claimant in the sum of AUD $125,000 plus interest and costs.

---

**KEY EVIDENCE (Strongest points)**

**Point 1: Knowledge of defect**
Email dated 2023-03-15 from defendant's QA team to senior management (Bates: BR_002-005) explicitly identifies product defect and raises liability concerns. Demonstrates conscious knowledge 3+ months before recall.

**Point 2: Failure causation**
Expert engineering report confirms failure mode on claimant's product is consistent with, and caused by, the known defect (Bates: BR_300-320). Site photographs taken 2023-06-14 (Bates: BR_051-060) corroborate expert assessment.

**Point 3: Quantifiable loss**
Quotations for remediation work (Bates: BR_200-250) total AUD $125,000. Costs represent reasonable and necessary steps to restore claimant's position.

---

**THREE BIGGEST RISKS (Defence arguments)**

**Risk 1: Isolated defect claim**
Defendant argues defect was isolated to single unit, not batch-wide. **Counter:** Production logs show batch continued in manufacture after 2023-03-15 knowledge; if truly isolated, recall would have occurred within days, not 3 months.

**Risk 2: Mishandling by claimant**
Defendant claims claimant mishandled product post-sale. **Counter:** No evidence of mishandling; timeline (received 2023 vintage, failed 2023-06) inconsistent with storage degradation; expert rules out mishandling as cause.

**Risk 3: Damages quantum challenge**
Defendant will argue quoted remediation costs are excessive. **Counter:** Quotes from two independent contractors; industry-standard methodology; no cheaper alternative available that would achieve necessary remediation.

---

**UNCONTESTED MATTERS**
- Defendant manufactured and supplied the product to claimant
- Supply created contractual relationship and duty of care
- Claimant suffered loss due to product failure

---

**STATUS**
All discovery complete. Evidence exchange closed. Adversarial review completed; no material weaknesses identified. Matter ready for hearing.

---

**Prepared by:** [Your name] | **Date:** [YYYY-MM-DD AWST] | **Version:** FINAL

```

---

## Template 13: Adversarial Review (Markdown)

**Purpose:** Critical colleague review of all court-facing documents. Identifies weaknesses, credibility risks, and areas requiring strengthening before filing.

```markdown
# ADVERSARIAL REVIEW REPORT

**Matter:** [Matter name and file number]
**Document(s) reviewed:** [List; e.g. "Affidavit of Sarah Chen v3.0; Court Bundle v3.0"]
**Review date:** [YYYY-MM-DD AWST]
**Reviewer:** [Name and role] — [Independent lawyer, ideally with relevant litigation experience]

---

## 1. Affidavit Review: [Document name and version]

### Weaknesses Identified

**Weakness 1: Temporal gap in knowledge**
*Description:* Affidavit asserts defendant knew of defect on 2023-03-15 (email), but claimant did not become aware until 2023-06-14. No explanation given for why defect went undetected for 3 months despite alleged batch-wide issue.
*Risk:* Defendant will argue either: (a) defect was isolated and only manifested in claimant's unit; (b) other units unaffected despite knowledge. Absence of prior complaints from other customers weakens batch-wide assertion.
*Recommendation:* Add paragraph to affidavit requesting expert opinion on expected discovery timeline for batch-wide defect. Alternatively, canvass whether claimant or defendant received other complaints in 2023-03 to 2023-06 period.

---

**Weakness 2: Causation assertion not independently verified**
*Description:* Affidavit relies heavily on expert's opinion that failure was caused by known defect, but expert report is not yet attached as annexure. Court may doubt causation in absence of independent assessment.
*Risk:* Defendant's expert will likely dispute causation, citing alternative failure modes or mishandling. Without corroborating evidence (e.g., design analysis, failure mode testing), opinion stands as expert-to-expert dispute.
*Recommendation:* (a) Ensure expert report is attached as Annexure and referenced explicitly in affidavit. (b) Consider whether second engineering opinion advisable as tiebreaker.

---

**Weakness 3: Damages claim not supported by invoice or contract evidence**
*Description:* Paragraph [X] asserts "cost to remediate is AUD $125,000" but basis is unclear. Quotes provided are dated [DATE], which is post-hearing if hearing is [HEARING DATE].
*Risk:* Court may reject damages as speculative. Defendant will argue quotes are inflated or that cheaper remediation options exist.
*Recommendation:* Attach supporting quotes as annexure; obtain dated quotes from independent contractors; add expert assessment of remediation necessity and cost reasonableness.

---

### Unsupported Assertions

**Assertion 1:** "Defendant's maintenance logs confirm the defect was widespread."
*Evidence basis:* Maintenance log extract (Bates: BR_100-110) shows 12 service requests in 2023-03-06 period, but does not explicitly state these were related to the known defect.
*Required support:* Cross-reference logs to QA email (Bates: BR_002-005) and add expert analysis linking log entries to known defect. If logs do not mention defect explicitly, add expert opinion that service codes and descriptions are consistent with defect presentation.

---

**Assertion 2:** "Claimant relied on product safety assurances from defendant."
*Evidence basis:* Not articulated in affidavit. No warranty document or sales representation quoted.
*Required support:* Add paragraph referencing Contract (Bates: BR_400-401, specifically Schedule of Goods and Warranties). Quote relevant warranty language if available.

---

### Emotional Framing & Tone

**Overall assessment:** Affidavit tone is appropriately neutral and factual. No inflammatory language detected.

**Minor observations:**
- Paragraph [X] uses phrase "egregious breach" — consider replacing with "breach" to avoid appearance of bias.
- Paragraph [Y] describes claimant's loss as "devastating" — replace with factual description of impact (e.g., "required claimant to cease operations for X weeks").

---

### Missing Evidence or Context

**Missing item 1:** Manufacturing specifications for the product and design tolerances.
*Impact:* Without understanding design parameters, court cannot assess whether defendant's defect was a design flaw or manufacturing defect. Expert opinion alone insufficient; specifications document will strengthen case.
*Action:* Request specifications from defendant in outstanding discovery request; if not forthcoming, note in affidavit that this document was sought but not produced.

---

**Missing item 2:** Correspondence between defendant's QA team and production line after 2023-03-15.
*Impact:* Gap between knowledge and action (recall not issued until 2023-06-14) is key strength, but affidavit does not explain what happened in the interim. Were there instructions to continue production? Was issue escalated? Court may find gap suspicious unless explained.
*Action:* Request internal memos, meeting minutes, or emails from 2023-03-15 to 2023-06-14 relating to product QA or recall decision-making.

---

## 2. Court Bundle Review: [Document name and version]

### Formatting Issues

**Issue 1:** Bates numbers not visible on pages BR_100-125 (Maintenance logs).
*Impact:* Court cannot verify that pages included in bundle match Bates register; potential credibility issue.
*Fix required:* Regenerate PDF with Bates numbers embedded on every page. Recompute final bundle hash.

---

**Issue 2:** Annexure index in bundle does not match Bates register.
*Example:* Register shows Annexure A as BR_001-050, but bundle index lists BR_002-050.
*Impact:* Inconsistency creates doubt about document integrity.
*Fix required:* Correct one document to match the other; verify against original affidavit cross-references.

---

### Credibility Risks

**Risk 1:** Expert report appears incomplete (final page shows "[CONTINUED ON NEXT PAGE]" but there is no next page).
*Impact:* Court may infer report was inadvertently truncated or edited post-execution, raising questions about document integrity.
*Action required:* Obtain complete executed expert report; reattach to bundle. Advise counsel if report was intentionally abbreviated.

---

**Risk 2:** Privilege schedule lists "Internal legal email dated 2023-06-15" as privileged, but same email appears in defendant's voluntary disclosure (dated 2025-09-15).
*Impact:* Privilege claim is waived by voluntary disclosure. Court will question claimant's good faith in asserting privilege now.
*Action required:* Investigate whether claimant inadvertently disclosed privileged document. If so, notify defendant and court immediately; seek advice on whether privilege is recovered or waived. If privilege was not waived, confirm with defendant that email in question was not produced by defendant and was obtained from alternative source.

---

## 3. Overall Assessment

**Viability for hearing:** ⚠ CONDITIONAL APPROVAL

**Conditions:**
1. Resolve Bates numbering issues in bundle (High priority)
2. Obtain complete expert report and attach as Annexure (High priority)
3. Address temporal gap in defect knowledge with expert or investigative evidence (Medium priority)
4. Obtain manufacturing specifications to support design/manufacturing defect analysis (Medium priority)
5. Verify privilege claim on 2023-06-15 email (Medium priority)

---

## 4. Recommended Actions Before Filing

**Action 1 — Affidavit amendment**
- Add paragraph explaining 3-month gap between knowledge and recall
- Add explicit reference to expert report (when attached)
- Replace "egregious" with neutral language
- Add contract warranty reference

**Action 2 — Evidence supplementation**
- Obtain manufacturing specs (request from defendant or access via expert)
- Canvas for other customer complaints in 2023-03-06 period
- Request QA team correspondence post-2023-03-15

**Action 3 — Bundle corrections**
- Regenerate with consistent Bates numbering throughout
- Verify expert report is complete
- Cross-check annexure index against affidavit cross-references and Bates register

**Action 4 — Privilege review**
- Clarify source of 2023-06-15 email and determine whether privilege waived

---

## 5. Critical Issues for Counsel Discussion

**Issue 1:** Second expert opinion — advisable?
*Context:* Given strength of defendant's likely challenge on causation, obtaining independent corroboration may shift balance. Cost estimate: AUD $8,500. Timeline: 3 weeks.
*Recommendation:* Discuss with client urgency of second opinion against cost/delay trade-offs.

---

**Issue 2:** Alternative settlement position
*Context:* Affidavit and bundle support strong case on liability, but causation and damages remain contested.
*Recommendation:* Prepare alternative settlement authority (e.g., AUD $95,000 if defendant offers) for negotiation before hearing.

---

## 6. Reviewer Assessment

**Overall:** Case is viable for hearing but requires amendments to affidavit, bundle corrections, and supplementary evidence collection. No fundamental credibility issues identified; weaknesses are remediable.

**Risk level:** MODERATE (down from HIGH if conditions addressed)

**Outcome note:** Do not estimate hearing success as a percentage. Summarise evidentiary strengths, unresolved risks, and legal-review questions instead.

---

**Reviewer:** [Name and signature]
**Date:** [YYYY-MM-DD AWST]
**Approved by counsel:** [Name] | [Date]

---

**Document ID:** [e.g. DOC_ADVERSARIAL_REVIEW_001]
**Version:** FINAL

```

---

## Template 14: Meeting Report (Markdown)

**Purpose:** Record of client meetings, witness interviews, or expert consultations. Identifies legally relevant facts, disclosure implications, and action items.

```markdown
# MEETING REPORT

**Matter:** [Matter name and file number]
**Meeting date:** [YYYY-MM-DD AWST]
**Meeting time:** [HH:MM start — HH:MM end]
**Location:** [Physical location or virtual platform]

---

## 1. Attendees

**Client/Witness side:**
- [Name and title, e.g. "Sarah Chen, Claimant"]
- [Next attendee]

**Legal team:**
- [Your name and role]
- [Next team member]

---

## 2. Purpose of Meeting

[Brief statement of meeting objective; e.g. "Initial client consultation to gather facts and evidence relating to product failure on 2023-06-14 and assess viability of claim for damages"]

---

## 3. Key Points Discussed

**Topic 1: [E.g. "Claimant's knowledge of product specifications and warranties"]**
- Claimant represented that: [What claimant said; direct quote if significant]
- Supporting documentary evidence produced: [If any documents were brought; e.g. "Contract of Sale dated 2023-02-01 and Warranty Card"]
- Follow-up required: [What remains unclear or needs investigation]

---

**Topic 2: [E.g. "Timeline of product failure and discovery of defect"]**
- Key dates confirmed:
  - Received product: [DATE]
  - Failure observed: [DATE at TIME]
  - Initial investigation: [DATE]
- Claimant account: [Summary of claimant's recollection]
- Documentary corroboration: [Diary entries, photos, inspection reports mentioned or provided]
- Follow-up required: [Gap or investigation needed]

---

**Topic 3: [E.g. "Details of remediation work and costs"]**
- Scope of remediation: [Description as provided by claimant]
- Quotes obtained: [Number and sources; e.g. "Two quotes from independent contractors"]
- Estimated cost: [Range or single figure given]
- Status of remediation: [Completed / In progress / Not yet commenced]
- Follow-up required: [Obtain original quotes; inspect remediated product if not yet complete]

---

## 4. Legally Relevant Facts Identified

**Fact 1:** [E.g. "Claimant was not aware of any defect in the product prior to failure on 2023-06-14; no prior complaints or performance issues"]
- Relevance: [Why this matters; e.g. "Supports inference that defect was latent and not caused by claimant's mishandling or storage"]
- Evidence basis: [Claimant testimony; supporting documents if any]
- Confidence level: [HIGH / MEDIUM / LOW]

---

**Fact 2:** [E.g. "Defendant provided express warranty on product durability and fitness for purpose"]
- Relevance: [Breach of warranty claim; supports duty of care argument]
- Evidence basis: [Warranty Card viewed at meeting; copy taken for file]
- Confidence level: [HIGH]

---

**Fact 3:** [E.g. "Remediation required shutdown of claimant's operations for 6 weeks, with consequential loss of revenue"]
- Relevance: [Damages element: consequential loss]
- Evidence basis: [Claimant's business records; invoices for lost contracts]
- Confidence level: [MEDIUM (pending corroboration from financial records)]

---

## 5. Action Items

| Action | Assigned to | Due date | Status |
|---|---|---|---|
| Obtain original quotes for remediation and supporting invoices | Client [name] | 2025-10-XX | Pending |
| Retrieve claimant's purchase invoice and warranty card | Client [name] | 2025-10-XX | Pending |
| Obtain copy of maintenance logs or service records from defendant | Your name (legal team) | 2025-10-XX | In progress |
| Arrange site inspection with engineering expert | Your name (legal team) | 2025-10-XX | Pending expert availability |
| Brief expert engineer on claimant's account for opinion formation | Your name (legal team) | 2025-10-XX | Pending expert report commission |

---

## 6. Reporting Obligations Triggered

**Obligation 1:** [E.g. "Client disclosed history of prior product failures from same manufacturer (year 2021)"]
- Relevance to disclosure: Pattern of defect; similar failure mode
- Classification: Disclosable (not protected by privilege; supports claimant's narrative)
- Action: Add to disclosure schedule as supplementary evidence supporting allegation of known defect

---

**Obligation 2:** [E.g. "Client mentioned possible settlement discussions with defendant's insurer"]
- Relevance: Settlement negotiations; admissions by defendant
- Classification: Potentially privileged under settlement negotiation rule (depends on context)
- Action: Clarify status of negotiations; confirm whether admissions made in without prejudice context

---

## 7. Disclosure Relevance Assessment

**Documents discussed that are disclosable:**
- [Document name and reason for disclosure; e.g. "Claimant's maintenance log for product (2023-02 to 2023-06) — factual foundation for claimant's account of failure timing and circumstances"]
- [Next document]

**Documents discussed that may be privileged:**
- [Document name and reason; e.g. "Draft email from claimant to solicitor seeking legal advice on rights — protected by legal professional privilege"]
- [Next document]

**Documents to be obtained from claimant:**
- [Document name; e.g. "Original invoice for product purchase"]
- [Next document]

---

## 8. Confidentiality & Internal Classification

**Classification:** ⚠ CONFIDENTIAL — CLAIMANT PRIVILEGED

**Recipient restrictions:**
- This report is intended for legal team only and is not to be disclosed to client without consent
- Information obtained is subject to legal professional privilege insofar as it relates to legal advice sought
- Factual information provided by claimant is not privileged and may need to be disclosed if requested in discovery

**Reason for restriction:** [E.g. "Meeting minutes contain legal team's initial assessment and strategic advice; factual information from claimant is separately classified"]

---

## 9. Next Steps

- [ ] Client to provide supporting documents by [DATE]
- [ ] Legal team to commission expert engineer by [DATE]
- [ ] Second meeting scheduled for [DATE] to review expert's preliminary findings
- [ ] Advise client of litigation timeline and key dates (discovery deadline, exchange, hearing)

---

**Prepared by:** [Your name] | **Date:** [YYYY-MM-DD AWST]
**Approved by:** [Supervising lawyer, if applicable] | **Date:** [YYYY-MM-DD AWST]

---

**Document ID:** [e.g. DOC_MEETING_REPORT_2025_10_15]
**Archive path:** [Folder location]

```

---

## Template 15: Obligation Register (CSV)

**Purpose:** Tracks all reporting, disclosure, and procedural obligations. Ensures no deadlines are missed.

**Header Row:**
```csv
ObligationID,Source,Description,DueDate,ResponsibleParty,Status,LinkedMeetingDate,Notes
```

**Example Rows:**
```csv
OBL_001,"Court Order dated 2025-06-01","Discovery disclosure deadline; produce all documents in response to interrogatories 1–15","2025-09-01","Sarah Chen (Solicitor)","COMPLETED","2025-08-20","Disclosure completed 2025-08-31; documents delivered to opponent 2025-09-01"
OBL_002,"Court Order dated 2025-06-01","Evidence exchange deadline; file affidavits and expert reports with court and serve on opponent","2025-10-15","Sarah Chen (Solicitor)","IN_PROGRESS","N/A","Affidavit ready for filing; expert report draft awaited from engineer (ETA 2025-10-10)"
OBL_003,"Procedural rule (Court Rules Part 8, s.12)","Privilege schedule to be filed contemporaneously with discovery disclosure if any documents are claimed to be privileged","2025-09-01","Sarah Chen (Solicitor)","COMPLETED","2025-08-20","Privilege schedule filed 2025-09-01 identifying two documents (both legal advice on settlement negotiations)"
OBL_004,"Defendant's letter dated 2025-09-10","Respond to Requests for Further and Better Particulars (RFBPs) re: dates of product manufacture and grounds for causation assertion","2025-10-01","James Liu (Paralegal)","OPEN","N/A","RFBPs received 2025-09-10; response prepared; due 2025-10-01; expert evidence scheduled to address causation RFBP by 2025-10-05"
OBL_005,"Court Order dated 2025-06-01","Pre-hearing conference; attend with counsel and appear ready to discuss settlement prospects","2025-10-20","Sarah Chen (Solicitor)","PENDING","N/A","Scheduled 2025-10-20 at 09:30 before [Judge name]; client availability confirmed; settlement parameters to be discussed with client by 2025-10-19"
```

---

## Template 16: Print Bundle Checklist (Markdown)

**Purpose:** Pre-print verification checklist. Ensures bundle is court-ready, formatted correctly, and free of errors or metadata.

```markdown
# PRINT BUNDLE CHECKLIST

**Matter:** [Matter name and file number]
**Bundle filename:** [e.g. "Court_Bundle_Hearing_Prep_v3.pdf"]
**Date prepared:** [YYYY-MM-DD AWST]
**Prepared by:** [Your name]

---

## Format & Presentation

- [ ] **A4 format confirmed**
  *Verification:* Checked document properties; all pages 210mm × 297mm
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]

- [ ] **Black & white safe (no colour-dependent content)**
  *Verification:* Converted to grayscale preview; all text and diagrams remain legible
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]
  *Notes:* [If colour present, describe what it is and whether it is essential or cosmetic]

- [ ] **Page numbers present on all pages**
  *Verification:* Spot-checked pages 1, 50, 100, final page; all have page numbers in footer
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]

- [ ] **Headings and margins consistent throughout**
  *Verification:* Sampled 5 pages across document; heading styles and margin spacing uniform
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]
  *Notes:* [If inconsistencies found, describe and note whether fixed]

---

## Content Integrity

- [ ] **Annexure references cross-checked**
  *Process:* Compared affidavit paragraphs to annexure list; verified each cross-reference exists in bundle
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]
  *Missing references found:* [If any; list and resolution]

- [ ] **Bates numbers verified on all pages**
  *Process:* Spot-checked Bates range BR_1-50 (first 10 pages), BR_200-250 (middle section), BR_400+ (end section); numbers present and sequential
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]
  *Discrepancies found:* [If any; list]

- [ ] **Bundle index matches contents**
  *Process:* Compared printed index to actual document order in PDF; verified page ranges for each section
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]
  *Discrepancies:* [If any; list and resolution]

---

## Metadata & Security

- [ ] **Metadata cleaned (author, creation date, editing history removed)**
  *Verification method:* Opened PDF properties; confirmed no author name, organisation, or edit history visible
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]
  *Notes:* [If any metadata remains, describe and note if intentional]

- [ ] **No AI-generated drafting notes or internal commentary included**
  *Verification:* Searched PDF for keywords: "AI", "draft", "TODO", "need to check", "internal only"
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]
  *Items found and removed:* [If any]

- [ ] **No internal review comments or track changes visible**
  *Verification:* Reviewed PDF for annotations, underlines, or revision marks; confirmed none present
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]

- [ ] **Final hash computed and recorded**
  *Method:* SHA256 hash generated on final PDF
  *Hash value:* `[Insert 64-character hex string]`
  *Date computed:* [YYYY-MM-DD AWST HH:MM]
  *Computed by:* [Name]
  *Storage location:* [Path to hash verification file]

---

## Court-Facing Content Only

- [ ] **No drafting notes from skill agents or LLM reasoning visible**
  *Verification:* Opened bundle and visually scanned; no visible algorithmic reasoning, agent notes, or system prompts
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]

- [ ] **No references to 99_AIStore or working folders**
  *Verification:* Searched for folder paths or file names from working directory
  *Date checked:* [YYYY-MM-DD]
  *Verified by:* [Name]

- [ ] **Affidavits signed and sworn (or "ready for swearing" noted)**
  *Status:* [All affidavits sworn by [DATE] / Affidavits ready for swearing by [DATE]]
  *Verified by:* [Name]

---

## Final Readiness

- [ ] **Print test completed**
  *Test date:* [YYYY-MM-DD]
  *Printer used:* [Printer name and model]
  *Pages printed:* [First 20 pages sampled]
  *Result:* ✓ PASS / ⚠ ACCEPTABLE WITH NOTES / ✗ FAILED
  *Notes:* [If not PASS, describe issues and remediation]

- [ ] **Binding/collation method confirmed**
  *Method:* [E.g. "Double-sided copy, stapled in top-left corner, submitted as single document"]
  *Confirmation received from:* [Court registry contact]
  *Date confirmed:* [YYYY-MM-DD]

- [ ] **Delivery timeline to court confirmed**
  *Delivery method:* [E.g. "Hand-delivery to court registry"]
  *Delivery date & time:* [YYYY-MM-DD HH:MM AWST]
  *Recipient:* [Court officer name or role]
  *Confirmation method:* [How receipt will be acknowledged; e.g. "Registry date-stamps original, copy retained with seal"]

---

## Sign-Off

**Bundle prepared by:**
Name: [Your name] | Role: [Your role]
Date: [YYYY-MM-DD AWST] | Signature: ___________________________

**Bundle verified by:** [Second person, ideally independent lawyer]
Name: [Verifier name] | Role: [Verifier role]
Date: [YYYY-MM-DD AWST] | Signature: ___________________________

**Counsel approval:**
Name: [Counsel name] | Date: [YYYY-MM-DD AWST]
Status: ✓ APPROVED FOR FILING / ⚠ APPROVED WITH CONDITIONS / ✗ REQUIRES AMENDMENTS

**Conditions or amendments:** [If applicable; describe]

---

**Document ID:** [e.g. DOC_PRINT_BUNDLE_CHECKLIST_001]
**Archive path:** [Version register entry]

```

---

## Template 17: Bundle Manifest (CSV)

**Purpose:** Index of all documents in print bundle. Matches print order to Bates numbering; used to verify bundle completeness.

**Header Row:**
```csv
BundleSection,DocumentTitle,BatesRange,PageRange,Status,PrintOrder
```

**Example Rows:**
```csv
"1. Court Documents","Cover page and Index","N/A","1-2","INCLUDED","1"
"1. Court Documents","Affidavit of Sarah Chen (Claimant)","BR_001-040","3-42","INCLUDED","2"
"2. Documentary Evidence","Email chain: Defendant QA discussion (2023-03-15 to 2023-06-14)","BR_041-090","43-92","INCLUDED","3"
"2. Documentary Evidence","Maintenance and service logs (2023-02 to 2023-08)","BR_091-250","93-252","INCLUDED","4"
"3. Photographic & Technical Evidence","Site inspection photographs (2023-06-20) and analysis","BR_251-275","253-277","INCLUDED","5"
"3. Photographic & Technical Evidence","Expert engineering report and drawings","BR_276-350","278-352","INCLUDED","6"
"4. Contracts & Warranties","Contract of Sale dated 2023-02-01","BR_351-360","353-362","INCLUDED","7"
"4. Contracts & Warranties","Product Warranty Card and specifications","BR_361-365","363-367","INCLUDED","8"
"5. Remediation Evidence","Quotations for remediation work (three quotes)","BR_366-380","368-382","INCLUDED","9"
"5. Remediation Evidence","Invoices for remediation materials and labour (2023-07 to 2025-09)","BR_381-410","383-412","INCLUDED","10"
```

---

## Template 18: Agent Handoff (JSON-like Structure)

**Purpose:** Structured handoff between workflow agents or phases. Ensures continuity and validates inputs/outputs at transition points.

```json
{
  "handoff_metadata": {
    "source_agent": "Evidence_Management_Agent",
    "target_agent": "Disclosure_&_Filing_Agent",
    "handoff_type": "phase_transition",
    "handoff_date": "2025-10-15",
    "handoff_time_awst": "14:30"
  },
  "matter_context": {
    "matter_id": "MATTER_2025_001",
    "matter_name": "[Claimant] v [Defendant] — Product Liability Claim",
    "file_number": "[Court file number, if assigned]",
    "current_phase": "Evidence assembly complete; transitioning to disclosure and court filing"
  },
  "handoff_phase": "From evidence collection → to disclosure preparation and court document filing",
  "inputs_to_target_agent": {
    "evidence_inventory": {
      "location": "server://vault/evidence_inventory_final.csv",
      "status": "FINAL",
      "record_count": 25,
      "last_updated": "2025-10-15",
      "verified_by": "Sarah Chen"
    },
    "chain_of_custody_log": {
      "location": "server://vault/chain_of_custody_final.csv",
      "status": "FINAL",
      "record_count": 32,
      "last_updated": "2025-10-15",
      "all_hashes_verified": true,
      "verified_by": "James Liu"
    },
    "bates_register": {
      "location": "server://vault/bates_register_final.csv",
      "status": "FINAL",
      "total_pages": 412,
      "prefix": "BR",
      "verified_by": "Sarah Chen"
    },
    "master_chronology": {
      "location": "server://vault/chronology_final.csv",
      "status": "FINAL",
      "event_count": 24,
      "confidence_verification_complete": true,
      "verified_by": "Counsel (Jane Smith)"
    },
    "claim_support_matrix": {
      "location": "server://vault/claim_support_matrix_final.csv",
      "status": "FINAL",
      "issues_tracked": 4,
      "gaps_identified": 2,
      "reviewed_by": "Counsel"
    }
  },
  "expected_outputs_from_target": {
    "disclosure_schedule": {
      "format": "CSV",
      "expected_location": "server://vault/disclosure/disclosure_schedule.csv",
      "expected_status": "FINAL",
      "scope": "All discovered documents with privilege claims assessed"
    },
    "privilege_schedule": {
      "format": "CSV",
      "expected_location": "server://vault/disclosure/privilege_schedule.csv",
      "expected_status": "FINAL",
      "scope": "Documents withheld on grounds of legal professional privilege"
    },
    "court_bundle": {
      "format": "PDF",
      "expected_location": "server://vault/filing/court_bundle_final.pdf",
      "expected_status": "FINAL",
      "expected_page_count": 412,
      "bates_range": "BR_001 to BR_412"
    },
    "affidavit": {
      "format": "DOCX + PDF",
      "expected_location": "server://vault/filing/affidavit_final.pdf",
      "expected_status": "FINAL / READY FOR SWEARING",
      "expected_paragraph_count": 45
    }
  },
  "validation_checks": {
    "check_1": {
      "description": "All evidence items in inventory have corresponding chain of custody records",
      "acceptance_criteria": "100% matching records with no orphaned items",
      "validation_method": "Cross-reference inventory IDs to CoC log; report any gaps"
    },
    "check_2": {
      "description": "All Bates-numbered documents appear in source evidence folder with SHA256 hashes matching chain of custody",
      "acceptance_criteria": "Hash verification 100% successful",
      "validation_method": "Automated hash comparison; spot-check 10% of documents manually"
    },
    "check_3": {
      "description": "Affidavit cross-references to evidence are valid (all Bates ranges cited exist and are accurate)",
      "acceptance_criteria": "Zero broken references; all citations match source documents",
      "validation_method": "Automated cross-reference checker; manual review of high-risk paragraphs"
    },
    "check_4": {
      "description": "No AI-generated working notes or internal commentary present in court-facing documents",
      "acceptance_criteria": "Zero instances of AI working material",
      "validation_method": "Full-text search for keywords: 'AI', 'draft', 'TODO', 'internal'; visual scan of final PDFs"
    },
    "check_5": {
      "description": "Disclosure schedule and bundle manifest match (same documents, same Bates ranges)",
      "acceptance_criteria": "100% alignment between schedules",
      "validation_method": "Automated cross-reference; spot-check 20% of entries"
    }
  },
  "escalation_triggers": [
    {
      "trigger": "Evidence inventory record count does not match bundle page count (accounting for cover pages and index)",
      "action": "Stop and notify source agent; investigate discrepancy before proceeding"
    },
    {
      "trigger": "Hash verification fails for any digital evidence item",
      "action": "Quarantine affected item; notify chain of custody custodian; do not file until resolved"
    },
    {
      "trigger": "Affidavit contains paragraph referencing evidence not in inventory or Bates register",
      "action": "Return affidavit to drafting team; do not proceed until cross-references corrected"
    },
    {
      "trigger": "Privilege claim found for document already disclosed to opponent in discovery",
      "action": "Escalate to counsel immediately; advise potential privilege waiver"
    },
    {
      "trigger": "Court bundle fails print test (illegibility, formatting issues, missing pages)",
      "action": "Halt filing; regenerate bundle and revalidate before resubmission"
    }
  ],
  "handoff_notes": {
    "note_1": "Evidence inventory is complete and verified. All source documents stored in secure vault with individual folder structure and hash integrity checks.",
    "note_2": "Chain of custody is fully auditable; no breaks or gaps identified. All digital evidence has SHA256 hash verification.",
    "note_3": "Bates register is final; no further reassignments anticipated. Print bundle reflects final Bates numbering.",
    "note_4": "Two evidence gaps identified in claim support matrix (manufacturing audit logs and defendant's expert report); disclosure schedule should flag as 'not yet received' rather than withheld or redacted.",
    "note_5": "Master chronology reviewed by counsel and endorsed; confidence label distribution is: HIGH (16 facts) / MEDIUM (6 facts) / LOW (2 facts). All disputed facts flagged.",
    "note_6": "Affidavit is ready for final counsel review and swearing; only awaiting completion of two pending evidence items (defendant's expert report; manufacturing audit logs)."
  },
  "sign_off": {
    "source_agent_confirmed_by": "Evidence_Management_Agent [System: Automated]",
    "source_agent_confirmation_date": "2025-10-15T14:30:00+08:00",
    "target_agent_acknowledgment_required": true,
    "target_agent_acknowledgment_deadline": "2025-10-15T17:00:00+08:00",
    "final_approval_by": "Counsel (Jane Smith)",
    "approval_status": "PENDING"
  }
}
```

---

## Template 19: 99_AIStore README (Markdown)

**Purpose:** Warning and governance document for AI-generated working material. Must be prominently displayed to prevent accidental filing of unverified content.

```markdown
# ⚠️ AI WORKING STORE — NOT COURT-READY

**This folder contains AI-generated working material and drafts only.**

---

## CRITICAL WARNINGS

### 🔴 DO NOT file any document from this folder without explicit human review and approval

- All content in this folder is **unverified** and **subject to error**
- AI-generated text may contain:
  - Hallucinations (invented facts, false citations, fabricated case law)
  - Logical inconsistencies or unsupported assertions
  - Formatting errors or incomplete cross-references
  - Emotional or inflammatory language inappropriate for court
  - Metadata revealing AI generation (may prejudice court perception)

### 🔴 DO NOT include documents from this folder in court bundles or affidavits

- Content is internal working material only
- No court in Australia will accept documents generated by AI without human verification
- Risk of sanctions or adverse credibility findings if AI material reaches court

### 🔴 DO NOT share or discuss contents of this folder with opponent or third parties

- Material is attorney work product and privileged
- Disclosure may waive privilege or damage your case strategy

---

## Folder Purpose

This folder (`99_AIStore/`) is a **working directory only** for:
- Initial evidence summaries and drafts
- Exploratory analysis and brainstorming
- Preliminary chronology timelines (before human verification)
- Template-generated documents (before customisation and review)
- Agent-generated research outputs (before fact-checking)

**All content must be:**
1. ✓ **Thoroughly reviewed** by a qualified lawyer
2. ✓ **Fact-checked** against primary source evidence
3. ✓ **Customised** to your specific matter (remove generic placeholders)
4. ✓ **Verified** for accuracy, completeness, and tone before use in court
5. ✓ **Moved** to the appropriate court-facing folder (not `99_AIStore/`)

---

## Folder Structure

```
99_AIStore/
├── Drafts/
│   ├── affidavit_drafts/
│   ├── evidence_summaries/
│   ├── chronology_drafts/
│   └── [other agent outputs]
├── Research/
│   ├── case_law_summaries/
│   ├── statutory_analysis/
│   └── legal_precedent_reviews/
├── Templates/
│   ├── completed_templates/
│   └── [template instances]
└── README.md [THIS FILE]
```

---

## Governance Rules

### Before moving any document to court-facing folders:

**Step 1 — Fact-check all assertions**
- [ ] Cross-reference every factual claim against primary source evidence
- [ ] Verify all dates, names, and case citations
- [ ] Confirm all cross-references (Bates numbers, annexure references) are correct
- [ ] Check for invented facts or unsupported inferences

**Step 2 — Verify legal analysis**
- [ ] Confirm all case law citations are current and correctly stated
- [ ] Verify statutory references (section numbers, act names)
- [ ] Check for legal logical consistency and validity
- [ ] Ensure conclusions follow from stated premises

**Step 3 — Review tone and language**
- [ ] Remove emotional or inflammatory language
- [ ] Ensure neutral, objective tone appropriate for court
- [ ] Check for inadvertent admissions or self-defeating statements
- [ ] Verify formatting and grammar

**Step 4 — Clean metadata and AI traces**
- [ ] Strip all document properties (author, creation date, edit history)
- [ ] Remove any AI working notes, reasoning, or "thinking" passages
- [ ] Verify no folder paths, file names, or system references remain
- [ ] Ensure no visible agent logic or templating artefacts

**Step 5 — Obtain legal sign-off**
- [ ] Have a qualified lawyer review the document
- [ ] Obtain written approval before filing
- [ ] Document reviewer name and date in version register

---

## Who Can Access This Folder?

**Permitted:**
- Your legal team (lawyers, paralegals)
- Your client (if briefed on confidentiality)
- Expert witnesses (if necessary for their work)

**NOT permitted:**
- Opponent or opponent's legal team
- Court or court personnel (unless document is formally finalised and approved)
- Third parties or public (working material is privileged)
- Any person without a need-to-know

---

## What Happens to Content After Use?

**After a document is finalised and approved:**
1. Move completed version to appropriate court-facing folder (e.g. `/matter/court_bundle/`)
2. Update version register with final version number and status
3. Optionally archive draft versions in `/archive/` subfolder for record-keeping
4. Leave a reference note in `99_AIStore/` pointing to final location (optional)

**When matter closes:**
1. Review all remaining `99_AIStore/` content
2. Delete interim drafts and exploratory work (no longer needed)
3. Archive any documents with legal, strategic, or procedural value to `/archive/`
4. Confirm deletion with matter supervisor before purging

---

## Checklist: Is This Document Ready for Court?

**Use this checklist before moving any document out of `99_AIStore/`:**

- [ ] All facts verified against primary evidence (100% accuracy)
- [ ] All legal citations current and correct
- [ ] All cross-references (Bates, annexures) verified and accurate
- [ ] No emotional language or tone issues
- [ ] No metadata or AI traces remaining
- [ ] Formatted correctly (A4, fonts, margins, page numbers)
- [ ] Reviewed and approved by qualified lawyer
- [ ] Version control entry created in version register
- [ ] Compliance check: document does not violate disclosure obligations
- [ ] Final decision: APPROVED FOR COURT / REQUIRES FURTHER AMENDMENTS

---

## Questions or Concerns?

If you're unsure whether a document is ready for court, **do not file it**. Instead:
1. Escalate to your supervising lawyer
2. Request a full review and sign-off
3. Wait for explicit written approval before proceeding

**It is better to delay filing by one day than to face sanctions or adverse credibility findings for filing unverified material.**

---

**Last updated:** 2026-03-16
**Owner:** [Your name/role]
**Review cycle:** Every matter phase transition

---

**Remember:** This folder is a working space, not a court-filing archive. Treat its contents as confidential, unverified, and internal only.

```

---

## Template 20: Matter Intake Checklist (Markdown)

**Purpose:** Initial client intake and case setup. Ensures all foundational information is gathered and systems are initialised before substantive work begins.

```markdown
# MATTER INTAKE CHECKLIST

**Matter name:** [Full name of matter as recorded in Linear/Notion]
**Intake date:** [YYYY-MM-DD AWST]
**Intake officer:** [Your name and role]
**File number:** [To be assigned] | **Urgency:** [Low / Normal / High / Urgent]

---

## 1. Client & Party Details

- [ ] **Client name:** [Full legal name]
  - [ ] Business name (if trading as): [Name]
  - [ ] Business structure: [Sole trader / Partnership / Proprietary company / Public company / Other]
  - [ ] ABN/ACN: [Number]

- [ ] **Client contact details:**
  - [ ] Address: [Full address]
  - [ ] Phone (primary): [Number]
  - [ ] Email: [Email address]
  - [ ] Preferred contact method: [Phone / Email / In person]

- [ ] **Opposing party/defendant:**
  - [ ] Full legal name: [Name]
  - [ ] Business name (if applicable): [Name]
  - [ ] Last known address: [Address]
  - [ ] Contact legal representative: [Name and firm]

- [ ] **Other parties:**
  - [ ] Co-claimant/co-defendants: [Names and contact details]
  - [ ] Insurer involved: [Yes / No] | [Insurer name and claim reference]

---

## 2. Court & Jurisdiction

- [ ] **Court:** [Court name; e.g. "District Court of Western Australia"]
- [ ] **Location (jurisdiction):** [State; e.g. "Western Australia"]
- [ ] **File number:** [If already assigned] | [If not yet filed: "Not yet filed — file number to be obtained post-writ"]
- [ ] **Nature of proceeding:** [E.g. "Claim for damages — product liability"; or "Defence to claim — breach of contract"]

---

## 3. Key Dates & Deadlines

- [ ] **Date of key event:** [E.g. date of alleged breach, injury, failure, etc.] | [Date: YYYY-MM-DD]
- [ ] **Date matter came to your attention:** [YYYY-MM-DD]
- [ ] **Statutory limitation date (if applicable):** [YYYY-MM-DD] | [Confirmation that within limitation: Yes / No / Borderline]
- [ ] **Court deadline (if existing order):** [Describe deadline; e.g. "Discovery by 2025-09-01"] | [Date: YYYY-MM-DD]
- [ ] **Hearing date (if fixed):** [YYYY-MM-DD and time] | [Status: Fixed / Not yet fixed / To be scheduled]
- [ ] **Settlement conference/mediation:** [Scheduled date or "Not yet scheduled"]

---

## 4. Opposing Party & Legal Representative

- [ ] **Opponent represented by:** [Firm name and contact partner]
  - [ ] Address: [Address]
  - [ ] Phone: [Number]
  - [ ] Email: [Email]

- [ ] **First communication sent:** [Date and method; e.g. "2025-08-15 Letter of demand sent via email"]
- [ ] **Opponent's response:** [Date received; summary of response; any admissions or denials noted]

---

## 5. Nature of Matter

- [ ] **Category:** [Negligence / Breach of contract / Product liability / Defamation / Other — specify]
- [ ] **Brief description:** [2–3 sentence summary of the claim or defence]
- [ ] **Quantum (if claim):** [AUD $ amount claimed or estimated]
- [ ] **Complexity rating:** [Low / Moderate / High] | [Reasons; e.g. "Expert evidence required"; "Multiple parties"; "Technical issues"]

---

## 6. Documents Received from Client

- [ ] **Key documents obtained:**
  - [ ] Contract/agreement (if applicable): [File: Intake_Evidence_001]
  - [ ] Correspondence: [File: Intake_Evidence_002]
  - [ ] Photographs/visual evidence: [File: Intake_Evidence_003]
  - [ ] Expert reports (if available): [File: Intake_Evidence_004]
  - [ ] Prior insurance/claim documents: [File: Intake_Evidence_005]
  - [ ] Other: [File names and descriptions]

- [ ] **Documents still outstanding:**
  - [ ] [Document name; expected receipt date: YYYY-MM-DD]
  - [ ] [Next document]

- [ ] **Privilege assessment completed:**
  - [ ] Communication with prior legal advisors: [Identified and logged on privilege schedule]
  - [ ] Advice sought in anticipation of litigation: [Noted as privileged]

---

## 7. Initial Evidence Hash Log

**Purpose:** Establish baseline integrity of evidence at intake (hash capture).

| Evidence Item | Format | Hash Method | Hash Value | Captured Date | Captured By |
|---|---|---|---|---|---|
| [Item 1; e.g. "Email chain from 2025-06-14"] | [Format; e.g. "Email thread (PDF)"] | [SHA256] | [Hash value] | [Date] | [Name] |
| [Item 2] | [Format] | [SHA256] | [Hash value] | [Date] | [Name] |

---

## 8. Folder Structure Created

- [ ] **Matter folder initialised at:** [Path; e.g. "server://matters/MATTER_2025_001_v_Defendant"]

- [ ] **Standard subfolders created:**
  - [ ] `/docs/` — documentation and correspondence
  - [ ] `/dev/` — working documents and drafts
  - [ ] `/archive/` — superseded versions and prior files
  - [ ] `/court_facing/` — final documents ready for court
  - [ ] `/99_AIStore/` — AI working material (with README warning)

- [ ] **File naming convention agreed:**
  - [ ] YYYYMMDD_ prefix on time-stamped files: [Confirmed]
  - [ ] Bates numbering scheme to be used: [BR_ prefix]
  - [ ] Evidence ID scheme to be used: [EV_ prefix]

---

## 9. Chain of Custody Initiated

- [ ] **Chain of Custody log created:** [Location: server://matters/MATTER_2025_001/chain_of_custody.csv]
- [ ] **First entry made:** [Date and item; e.g. "2025-08-15 — Client meeting; 5 documents received and catalogued"]
- [ ] **Custodian assigned:** [Name]
- [ ] **Custody procedure explained to client:** [Yes / No] | [Date explained: YYYY-MM-DD]
- [ ] **Client confirmed understanding:** [Yes / No]

---

## 10. Matter Setup in Case Management System

- [ ] **Matter record created in Linear:**
  - [ ] Matter ID: [e.g. VD-2025-001]
  - [ ] Project assigned: [Project name]
  - [ ] Team assigned: [Team]
  - [ ] Responsible lawyer: [Name]
  - [ ] Status: [Active / Holding / Planned]

- [ ] **Notion documentation page created (if needed):**
  - [ ] Link: [Notion page URL]
  - [ ] Content: [Matter summary, client details, key deadlines]

- [ ] **Initial issues/tasks created in Linear:**
  - [ ] [Issue 1; e.g. "Receive outstanding documents from client"]
  - [ ] [Issue 2; e.g. "Conduct conflict check and insurance review"]
  - [ ] [Issue 3; e.g. "Prepare initial correspondence/response"]

---

## 11. Risk Assessment & Conflict Check

- [ ] **Conflict of interest check completed:** [Yes / No]
  - [ ] No conflicts identified: [Confirmed]
  - [ ] Conflicts identified: [Describe and resolution; e.g. "Conflict with XYZ Corp on unrelated matter; not acting for XYZ on current matter — no issue"]

- [ ] **Insurance check completed (if applicable):** [Yes / No]
  - [ ] Professional indemnity insurance: [Adequate cover confirmed / Insufficient cover — escalate]
  - [ ] Public liability insurance: [Applicable; confirmed]

- [ ] **Litigation risk assessment:**
  - [ ] Initial viability assessment: [Strong case / Moderate case / Weak case / Unable to assess without further evidence]
  - [ ] Key risks identified: [Brief list; e.g. "Lack of contemporaneous evidence"; "Expert evidence pending"; "Limitation period at risk"]
  - [ ] Mitigation plan: [Describe; e.g. "Commission expert urgently"; "Obtain discovery order"]

---

## 12. Client Engagement & Budget

- [ ] **Retainer agreement signed:** [Yes / No] | [Date: YYYY-MM-DD]
  - [ ] Client received copy: [Yes / No]
  - [ ] Fee structure explained: [Hourly rate / Fixed fee / Contingency / Other]
  - [ ] Estimated budget provided: [Yes / No] | [Amount: AUD $]

- [ ] **Client informed of:**
  - [ ] Estimated timeline to resolution: [Date range]
  - [ ] Cost implications of discovery and expert evidence: [Discussed]
  - [ ] Litigation risks and burden of proof: [Discussed]
  - [ ] Alternative dispute resolution options: [Discussed]

- [ ] **Client authority obtained for:**
  - [ ] Taking steps in litigation: [Confirmed]
  - [ ] Engaging expert witnesses: [Confirmed / Subject to cost approval]
  - [ ] Settlement parameters: [Initial parameters established; flexible range to be refined]

---

## 13. Communication Plan

- [ ] **Reporting schedule established:**
  - [ ] Progress reports: [Monthly / Quarterly / As needed]
  - [ ] Email updates: [Only material developments / Weekly summary / As requested]
  - [ ] Meetings: [Scheduled dates; frequency]

- [ ] **Client contact person designated:** [Name and role]
- [ ] **Escalation contact (client side):** [Name and role]
- [ ] **Internal escalation contact (your firm):** [Supervising lawyer name]

---

## 14. Compliance & Next Steps

- [ ] **Initial tasks assigned and due dates set:**
  - [ ] [Task 1]: Due [YYYY-MM-DD]
  - [ ] [Task 2]: Due [YYYY-MM-DD]
  - [ ] [Task 3]: Due [YYYY-MM-DD]

- [ ] **Court filings required:**
  - [ ] Writ to be filed by: [YYYY-MM-DD] | [Status: To be prepared / Ready for filing]
  - [ ] Defence to be filed by: [YYYY-MM-DD] | [Status: In preparation / Outstanding]

- [ ] **Disclosure and procedural compliance:**
  - [ ] Discovery deadline: [YYYY-MM-DD]
  - [ ] Evidence exchange deadline: [YYYY-MM-DD]
  - [ ] Pre-hearing conference scheduled: [YYYY-MM-DD]

---

## Sign-Off

**Intake completed by:**
Name: [Your name] | Role: [Your role] | Date: [YYYY-MM-DD AWST]
Signature: ___________________________

**Reviewed by:** [Supervising lawyer]
Name: [Name] | Date: [YYYY-MM-DD AWST]
Signature: ___________________________

**Matter activation approved:**
Status: ✓ APPROVED FOR ACTIVE WORK / ⚠ APPROVED SUBJECT TO CONDITIONS / ✗ HOLD (PENDING FURTHER INFORMATION)

**Conditions or notes:** [If applicable]

---

**Document ID:** [e.g. DOC_INTAKE_CHECKLIST_MATTER_2025_001]
**Archive location:** [matter folder path]

```

---

## Reference Notes

All templates above follow Australian legal practice standards and are designed for use in court proceedings under Australian rules of civil procedure. Key design principles:

1. **Practical operational focus** — Templates are ready to use immediately with minimal adaptation
2. **Traceability** — All evidence, decisions, and versions logged with dates and responsible persons
3. **Integrity verification** — Hash logging and chain of custody throughout
4. **Court compliance** — Format and content standards match Australian court requirements
5. **AI safety** — Clear separation of AI working material from court-ready documents; explicit warnings on `99_AIStore/`
6. **Australian conventions** — English spelling (organise, finalise, analyse); AWST timezone references; Australian court hierarchy and terminology

---

**END OF TEMPLATES REFERENCE FILE**

---

**Archive:** This file serves as the definitive templates library for all legal workflow matters.
**Versioning:** Version 1.0 — 2026-03-16 AWST
**Update protocol:** New templates or revisions must be logged in the file changelog above and propagated to all active matter folders.
