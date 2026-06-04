# Example Prompts — Legal Matter Operations Engine

This document provides 25+ example invocations grouped by phase and use case. Each prompt includes a one-line note describing the skill's response.

---

## Intake & Setup

**1. Initialise a new matter**
```
Initialise a legal matter for Smith v Jones, Family Court (Western Australia), file number SYD12345/2026.
```
→ Creates folder structure, locks matter identifier, generates metadata template with court jurisdiction and parties.

**2. Intake message exports**
```
Intake these message exports (WhatsApp, SMS, email CSV) and hash all items.
```
→ Ingests message logs, generates MD5 and SHA256 hashes, creates inventory with timestamps and participant metadata.

**3. Import evidence from a source folder**
```
Import evidence from /Users/alex/Downloads/smith-v-jones-evidence/ and build the inventory.
```
→ Recursively scans folder, hashes all files, creates inventory CSV with file paths, sizes, hashes, and detected MIME types.

**4. Verify matter metadata**
```
Check the matter metadata for Smith v Jones (SYD12345/2026). What are the filing deadlines?
```
→ Reads matter metadata, displays parties, court, deadlines, and legal representatives; flags any missing critical fields.

**5. Add a new evidence source**
```
Add evidence from the defendant's WhatsApp backup (backup_20260310.zip) to the existing inventory.
```
→ Extracts archive, hashes new items, checks for duplicates against existing inventory, updates chain-of-custody log.

---

## Evidence Inventory

**6. Build the evidence inventory**
```
Build an inventory of all evidence in the matter folder and export it as CSV.
```
→ Scans evidence/ directory, hashes all files, generates inventory with columns: filename, hash (MD5/SHA256), size, date modified, MIME type.

**7. Check for duplicate evidence**
```
Scan the inventory for duplicate files (same hash).
```
→ Compares all hashes, identifies duplicates, reports storage waste and recommends consolidation.

**8. Export inventory for disclosure**
```
Export the evidence inventory in a format suitable for disclosure to the opposing party.
```
→ Generates CSV with filename, Bates number (placeholder), date, and description; redacts hash values and internal notes.

**9. Verify hash integrity**
```
Re-hash all evidence files and check against the recorded hashes.
```
→ Computes fresh hashes, compares against inventory, reports matches and mismatches (indicating tampering or corruption).

**10. Search inventory by keyword**
```
Find all documents in the inventory that mention "payment" or "agreement".
```
→ Searches metadata and extracted text, returns file list with context snippets.

---

## Chain of Custody

**11. Establish chain of custody for all evidence**
```
Document the chain of custody for all evidence. Source: client files, WhatsApp backup, recovered emails.
```
→ Creates chain-of-custody ledger with: item identifier, received from (date, person), handling log, storage location.

**12. Add a new evidence source to the chain**
```
Add evidence received from the defendant's legal representative on 2026-03-16 to the chain of custody log.
```
→ Appends new entry with receipt date, source metadata, and handler identification; updates inventory provenance.

**13. Verify chain of custody integrity**
```
Check for gaps in the chain of custody. Are all evidence items accounted for?
```
→ Audits ledger for: missing receipt dates, gaps in handling log, items with no storage location; flags anomalies.

**14. Generate chain of custody affidavit**
```
Generate a sworn statement confirming the chain of custody for all evidence in this matter.
```
→ Drafts affidavit language documenting receipt, storage, and handling of all evidence; ready for swearing.

---

## Chronology

**15. Build a master chronology from evidence**
```
Build a master chronology from the evidence inventory. Focus on events affecting [parenting arrangements / employment / property].
```
→ Extracts timestamps from all evidence, sorts chronologically, identifies key events, produces timeline document with evidence references.

**16. Add new events to chronology**
```
Add these new events to the master chronology: meeting on 2026-03-10, email dated 2026-03-12, text message 2026-03-14.
```
→ Inserts events in temporal order, updates version number, flags events for affidavit cross-referencing.

**17. Identify chronology gaps**
```
Identify gaps in the chronology. Where are there time periods with no evidence?
```
→ Analyzes timeline, reports date ranges with no documented events, suggests follow-up questions or additional evidence sources.

**18. Verify chronology against evidence**
```
Cross-check the master chronology against the evidence inventory. Are all events properly sourced?
```
→ Compares chronology entries to inventory, reports unsourced events and missing evidence citations.

**19. Export chronology for hearing preparation**
```
Export the master chronology in a format suitable for hearing scripts.
```
→ Generates clean timeline with key dates highlighted, evidence references removed for operational use.

---

## Affidavit

**20. Draft an affidavit from chronology**
```
Draft an affidavit based on the master chronology and evidence inventory, addressing parenting arrangements and family violence concerns.
```
→ Generates sworn statement with narrative paragraphs, evidence annexures (numbered), legal structure, and placeholder for deponent signature.

**21. Add affidavit annexures**
```
Create annexures for all message evidence in the disclosure set. Link them to affidavit paragraphs.
```
→ Extracts messages, arranges chronologically, creates numbered annexures, inserts cross-references in affidavit text.

**22. Harden affidavit language**
```
Review the affidavit draft for emotional language, assumptions, and argumentative tone. Remove non-evidentiary content.
```
→ Scans affidavit for: emotive adjectives, speculation, rhetorical language, unsupported conclusions; flags and removes each item with notes.

**23. Verify affidavit against evidence**
```
Check the affidavit for accuracy against the evidence inventory. Are all factual claims properly sourced?
```
→ Compares affidavit statements to evidence, reports unsourced claims and identifies evidence that contradicts affidavit narrative.

**24. Update affidavit after new evidence**
```
Add this new evidence (email dated 2026-03-13) to the affidavit and update version numbers.
```
→ Inserts evidence into appropriate chronological position, updates annexure numbering, refreshes cross-references, increments version.

---

## Disclosure & Privileged Matter

**25. Prepare a disclosure schedule**
```
Prepare a disclosure schedule for all evidence in the matter. Identify privileged documents.
```
→ Maps all evidence to disclosure categories, applies privilege filters (legal advice, client communication, litigation strategy), generates schedule with classifications.

**26. Classify documents by disclosure status**
```
Which documents are privileged? Which must be disclosed?
```
→ Reviews all evidence against privilege criteria (legal advice privilege, litigation privilege, client confidence), produces classification matrix.

**27. Filter privileged matter from disclosure**
```
Generate a disclosure schedule excluding all privileged documents.
```
→ Removes privileged items, produces clean schedule for delivery to opposing party, maintains separate privileged register.

**28. Export disclosure schedule for service**
```
Export the disclosure schedule in a format ready for service on the opposing party.
```
→ Formats schedule with standard headings, file descriptions, and Bates numbers; produces PDF ready for delivery.

---

## Bates Numbering & Cross-References

**29. Assign Bates numbers to disclosure set**
```
Assign Bates numbers to the disclosure set, starting at SJ_001.
```
→ Assigns sequential identifiers (SJ_001, SJ_002, etc.), generates Bates register, updates all affidavit and schedule cross-references.

**30. Update cross-references after Bates assignment**
```
Update all cross-references in the affidavit and disclosure schedule to use Bates numbers.
```
→ Scans all documents, replaces file references with Bates numbers, produces cross-reference map.

**31. Verify Bates numbering integrity**
```
Check for gaps or duplicates in the Bates numbering sequence.
```
→ Audits Bates register, reports: missing numbers, duplicate assignments, unregistered documents.

**32. Generate Bates cross-reference map**
```
Generate a cross-reference map linking Bates numbers to affidavit paragraphs.
```
→ Produces table: Bates number → evidence description → affidavit paragraph(s) citing that evidence.

---

## Court Formatting

**33. Format affidavit for WA Magistrates Court**
```
Format the affidavit for filing with the Western Australia Magistrates Court.
```
→ Applies WAMC formatting standards: font (Times New Roman, 12pt), line spacing (1.5), margins, paragraph numbering, cover page, signature block.

**34. Validate print readiness**
```
Validate the affidavit and bundle for print readiness. Check formatting, fonts, page breaks.
```
→ Scans documents for: font consistency, colour management, page breaks, orphaned text, image resolution; reports issues.

**35. Convert affidavit to PDF**
```
Convert the affidavit DOCX to PDF, preserving formatting and bookmarks.
```
→ Renders DOCX as PDF, creates bookmarks for sections and annexures, verifies readability and page count.

**36. Check for compliance issues**
```
Check the affidavit for court compliance issues: font size, line spacing, margin requirements, pagination.
```
→ Audits against court rules (WAMC, District, Federal as configured), reports deviations with remediation steps.

---

## Hearing Preparation

**37. Generate a one-page hearing summary**
```
Generate a one-page hearing summary covering the key facts, evidence, and contested points.
```
→ Produces concise overview with: parties, court, key dates, factual summary, evidence summary, contested issues.

**38. Create issue notes for each contested point**
```
Create detailed issue notes for the following contested points: [parenting, residence, property division].
```
→ Generates structured notes for each issue with: factual background, evidence cited, opposing party's likely arguments, response strategy.

**39. Identify weaknesses in evidence**
```
Run a critical analysis of the evidence. What are the weakest points in our case?
```
→ Stress-tests affidavit and evidence, identifies: gaps, weak evidence, potential counter-arguments, areas requiring additional proof.

**40. Generate hearing scripts**
```
Generate a hearing script for opening remarks. Assume hostile questioning on [family violence / parenting capability].
```
→ Produces structured script: opening statement, key narrative, evidence references, anticipated objections, closing remarks.

**41. Prepare examination-in-chief notes**
```
Generate examination-in-chief notes for the deponent, structured around affidavit paragraphs.
```
→ Produces condensed notes keyed to affidavit sections, identifies: key evidence to highlight, documentary references, anticipated difficulties.

---

## Adversarial Review

**42. Run adversarial review on all outputs**
```
Run adversarial review on the affidavit. What are the strongest counter-arguments?
```
→ Stress-tests affidavit from opposing counsel perspective, identifies: weak claims, gaps in logic, unsupported conclusions, evidentiary vulnerabilities.

**43. Red-team the evidence inventory**
```
Red-team the evidence inventory. Which documents could damage our case?
```
→ Reviews all evidence from hostile perspective, flags: documents supporting opponent's case, statements that contradict affidavit, credibility issues.

**44. Challenge affidavit accuracy**
```
Challenge every factual claim in the affidavit against the evidence inventory. Which statements are unsupported?
```
→ Systematically compares affidavit paragraphs to evidence, identifies: unsupported assertions, weak sources, alternative interpretations.

**45. Identify procedural vulnerabilities**
```
Check the affidavit and bundle for procedural defects: missing signatures, improper formatting, missing exhibits.
```
→ Audits against court rules and practice notes, reports: missing elements, formatting errors, disclosure failures.

---

## Bundle Assembly & Print

**46. Assemble the print bundle**
```
Assemble the final court bundle with cover page, index, and all exhibits.
```
→ Collates documents in court order, creates index with page numbers, generates cover page with matter details, produces final PDF.

**47. Create bundle index**
```
Generate an index for the court bundle, listing all documents with Bates numbers and page references.
```
→ Produces formatted index: document description, Bates range, page numbers, keyed to bundle pages.

**48. Verify bundle completeness**
```
Check the bundle for completeness. Are all cross-referenced documents included? Are page numbers correct?
```
→ Audits bundle, verifies: all cited exhibits present, page numbers accurate, Bates numbers match, no duplicates.

**49. Freeze the bundle for filing**
```
Freeze the bundle for filing. Lock versioning and archive working drafts.
```
→ Locks final bundle version, moves working drafts to archive, generates final run report with file hashes and filing metadata.

**50. Prepare bundle for electronic filing**
```
Prepare the bundle for electronic filing with the court. Check file size, format, and naming.
```
→ Validates PDF: file size under limit, compression optimised, filename compliant, metadata correct; generates filing checklist.

---

## File Management & Versioning

**51. Lint the matter folder for compliance**
```
Lint the matter folder. Check for: missing metadata, untracked files, version control issues, naming convention violations.
```
→ Audits folder structure, reports: missing reference files, files not matching naming convention, orphaned working materials in wrong directories.

**52. Archive superseded drafts**
```
Archive all superseded draft affidavits and chronologies. Consolidate working materials.
```
→ Moves old versions to archive/, updates file inventory, generates manifest of archived items with reasons.

**53. Generate version status report**
```
Generate a status report of all active documents in the matter. Which are current versions? Which need updating?
```
→ Scans all files, identifies: current versions, outdated drafts, files not yet updated after Bates assignment, version consistency issues.

**54. Compare versions of affidavit**
```
Generate a diff of the current affidavit and the previous version. What changed?
```
→ Produces marked-up document highlighting: additions (green), deletions (red), modifications (yellow); includes line-by-line summary.

**55. Clean up AIStore**
```
Review the AIStore for working materials that can be archived. What's still relevant?
```
→ Lists all items in AIStore with creation dates, use annotations, and recommendations for retention or archival.

---

## Meeting Data & Reporting Obligations

**56. Log meeting notes**
```
Log meeting notes from today's conference call (2026-03-16) with [opposing counsel / client / judge].
```
→ Creates dated meeting record, extracts key decisions and action items, flags any reporting obligations or disclosure issues.

**57. Extract reporting obligations**
```
Extract all reporting obligations from the meeting notes. Who must be informed of what by when?
```
→ Scans meeting notes for: compliance obligations, disclosure duties, court orders, procedural deadlines; produces obligation register.

**58. Classify meeting materials**
```
Classify the materials from today's conference as: disclosable to opponent / internal working papers / privileged.
```
→ Reviews each document, applies classification against privilege and disclosure rules, generates classification matrix.

**59. Generate meeting summary for file**
```
Generate a formal meeting summary for the matter file, documenting attendees, decisions, and next steps.
```
→ Produces structured summary with: date, time, participants, key discussion points, decisions made, action items, due dates.

**60. Track action items**
```
Extract action items from all meeting notes in the matter. Who is responsible for each? When are they due?
```
→ Compiles action item register with: description, owner, due date, status, evidence of completion.

---

## Miscellaneous & Complex Workflows

**61. Generate final run report**
```
Generate the final run report for this matter. What was completed? What remains? Are there outstanding issues?
```
→ Produces comprehensive report covering: evidence inventory (count, total size), affidavit status, disclosure completeness, Bates assignment, bundle readiness, outstanding action items.

**62. Prepare for adjournment**
```
The matter has been adjourned to [DATE]. What follow-up evidence is required? Generate an action list.
```
→ Reviews affidavit gaps, identifies evidence needed by adjournment date, generates prioritised action list with deadlines.

**63. Consolidate after new evidence**
```
New evidence has been received from the defendant. Re-run the full workflow: intake, inventory, chronology, affidavit update.
```
→ Executes in sequence: evidence intake and hashing, inventory update, chain-of-custody entry, chronology insertion, affidavit paragraph addition, version increment, cross-reference update.

**64. Prepare expert report integration**
```
An expert report has been received. Integrate it into the chronology, affidavit, and disclosure schedule.
```
→ Ingests expert report, extracts key findings, inserts into affidavit as supporting evidence, updates disclosure schedule, flags any privilege issues.

**65. Generate evidence summary for junior counsel**
```
Generate a concise evidence summary for junior counsel. Focus on: key facts, evidence supporting each fact, weaknesses.
```
→ Produces condensed brief with: factual narrative, evidence citations, assessment of evidentiary strength, identified gaps.
