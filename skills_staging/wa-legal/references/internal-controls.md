# Internal Control Systems

Controls for evidence quality, risk management, and workflow integrity in legal matter operations.

---

## Validation Gates

Each phase must pass a gate before progression. Gates are checkpoints, not suggestions.

| Phase | Gate | Block Condition |
|-------|------|-----------------|
| 1 (INTAKE) | Chain of custody complete | Any file without hash or custodian entry → block Phase 2 |
| 2 (FILE CLASSIFICATION) | All files classified | Any file unclassified → block Phase 3 |
| 3 (LEGAL FOLDER PLACEMENT) | Source materials immutable | Any modification to 01_Source_Materials → block Phase 4, audit breach |
| 4 (CHAIN OF CUSTODY) | Custody log signed off | Practitioner must review and sign chain of custody log → block Phase 5 |
| 5 (EVIDENCE INVENTORY) | Evidence IDs assigned | All evidence must have EV-ID → block Phase 6 |
| 6 (CHRONOLOGY) | Chronology reviewed | Practitioner confirms no factual errors, confidence labels assigned → block Phase 7 |
| 7 (CLAIM SUPPORT) | All elements mapped | Every legal element must have evidence linked → block Phase 8 |
| 8 (DRAFTING) | Practitioner approves draft | Counsel signs off on factual accuracy, no privilege breaches → block Phase 9 |
| 9 (DISCLOSURE) | Disclosure schedule complete | All disclosed items Bates-preregistered → block Phase 10 |
| 10 (BATES) | Bates register verified | No gaps, no duplicates, all items numbered → block Phase 11 |
| 11 (FORMATTING) | Print test passed | 10-page sample legible, Bates correct, formatting compliant → block Phase 12 |
| 12 (HEARING PREP) | Scripts reviewed | Counsel confirms scripts, issue notes, response prompts → block Phase 13 |
| 13 (ADVERSARIAL REVIEW) | Review by independent reviewer | Vulnerabilities identified and ranked → block Phase 14 |
| 14 (FINAL RUN REPORT) | Practitioner approves report | Sign-off confirms matter ready for bundle freeze → block Phase 15 |
| 15 (BUNDLE FREEZE) | Bundle locked | All documents FILED status, no further modifications | Terminal |

---

## Confidence Labels

Applied to all evidence items and factual claims. Indicate reliability and admissibility risk.

- **HIGH:** Direct documentary evidence (email, text message, photo with metadata, official record, contemporaneous note). Admissibility uncontroversial.
- **MEDIUM:** Corroborative evidence or affiant testimony supported by at least one other independent source. Admissibility likely but may face objection.
- **LOW:** Affiant memory (conversation not recorded), circumstantial evidence, or evidence supported by only one source. Admissibility may be challenged; court may reduce weight.
- **UNCERTAIN:** Evidence chain broken, source unclear, or metadata missing. Inadmissible or unreliable until clarified.

---

## Risk Flags

Assigned to evidence items and claims. Flags alert to weaknesses and vulnerabilities.

| Flag | Meaning | Action |
|------|---------|--------|
| UNSUPPORTED_CLAIM | Legal element with insufficient evidence or only memory-based support | Consider dropping, seek additional evidence, or reframe as inference |
| WEAK_SOURCE | Evidence from unreliable source (anonymous, inadmissible, prejudiced party) | Prioritise corroboration, flag in adversarial review |
| CHAIN_BREAK | Chain of custody gap or undocumented handling | Obtain clarification, document, or flag admissibility risk |
| MISSING_CONTEXT | Evidence incomplete or requires explanation (partial thread, undated photo) | Seek full version, obtain metadata, add context |
| CONTRADICTED | Evidence contradicts other evidence or affiant's own statement | Identify and resolve in chronology, address in adversarial review |
| STALE_DRAFT | Document not updated in 7+ days despite new evidence or feedback | Refresh, update, re-review |
| DUPLICATE | Same document multiple times or multiple versions | Deduplicate, retain best version, cross-reference |
| EMOTIONAL_FRAMING | Opinion, emotional escalation, or rhetoric rather than fact | Reframe using factual language only |
| HEARSAY_RISK | Hearsay statement may be inadmissible or carry reduced weight | Assess exceptions under WA Evidence Act, note in inventory |
| PRIVILEGE_AT_RISK | Privilege claimed but may not qualify | Obtain practitioner confirmation before disclosure |
| MEMORY_ONLY | No contemporaneous record; based solely on affiant recollection | Mark confidence LOW, seek corroboration |

---

## Evidence Strength Ratings

Applied to each evidence item and claim support entry. Indicates evidentiary quality and weight.

- **DIRECT_EVIDENCE:** Fact directly supported by documentary or direct testimony. Example: email stating "I paid you $500" supports payment claim.
- **CORROBORATIVE:** Evidence supporting a claim made by another source. Example: bank statement showing $500 transfer corroborates email.
- **CIRCUMSTANTIAL:** Fact inferred from evidence, not directly stated. Example: silence to repeated demands may support inference of non-payment.
- **HEARSAY:** Statement made out of court asserted for truth. May be inadmissible unless exception applies. Example: "She told me he hit her."
- **OPINION:** Statement of belief or interpretation, not fact. Admissible if by expert or lay observer on permitted topics. Example: "He seemed angry."
- **UNCORROBORATED:** Sole source supporting a claim; no independent corroboration. Higher admissibility risk.

---

## Human Review Triggers

Action stops; human input required before progression.

| Trigger | Condition | Action |
|---------|-----------|--------|
| PRIVILEGE QUERY | File marked with privilege claim but criteria unclear | Practitioner confirms privilege applies |
| ADMISSIBILITY DOUBT | Evidence flagged as likely inadmissible | Practitioner confirms admissibility decision |
| FACTUAL CONFLICT | Two pieces of evidence directly contradict | Practitioner resolves or proceeds with acknowledgment |
| MISSING LEGAL ELEMENT | Legal element has no supporting evidence | Practitioner decides: seek evidence, amend claim, or accept risk |
| EMOTIONAL ESCALATION | Document uses emotional language or rhetoric | Practitioner reviews and approves reframing |
| DISCLOSURE DOUBT | Uncertainty whether document must be disclosed | Practitioner makes disclosure decision |
| BATES CONFLICT | Bates assignment creates reference error | Practitioner confirms correct sequence |
| PRINT FORMATTING FAILURE | Print test fails | Practitioner or formatting specialist resolves |

---

## Applying Controls in Practice

When entering any phase, check the gate from the previous phase first. If the gate has not passed, do not proceed — escalate to the practitioner.

When assessing evidence during Phase 5 (Evidence Inventory):
1. Assign confidence label (HIGH/MEDIUM/LOW/UNCERTAIN)
2. Assign evidence strength (DIRECT through UNCORROBORATED)
3. Check for applicable risk flags
4. If any human review trigger fires, stop and escalate

When drafting during Phase 8:
1. Only include facts with confidence HIGH or MEDIUM in the affidavit body
2. LOW confidence facts may appear if properly qualified ("I recall, but have no contemporaneous record...")
3. UNCERTAIN evidence should not appear in the affidavit unless practitioner explicitly approves
4. All risk flags must be resolved or acknowledged before the draft gate passes

When conducting adversarial review during Phase 13:
1. Challenge every MEDIUM and LOW confidence item
2. Test every risk-flagged item against the strongest counterargument
3. Document which vulnerabilities are fatal vs manageable
4. Rank all vulnerabilities: critical (could lose the case), significant (weakens position), minor (manageable in oral evidence)
