---
name: foia-requests
description: Freedom of Information Act (FOIA) and public records request workflows. Use when drafting records requests, tracking submissions, understanding exemptions, appealing denials, or managing large document productions. Essential for investigative journalists, researchers, and transparency advocates.
attribution: "Adapted from jamditis/claude-skills-journalism (journalism-core/skills/foia-requests) at 2097d218. Original author: Joe Amditis. MIT License."
---

# FOIA and public records requests

> **Jurisdiction: United States.** This skill covers US federal FOIA and state public-records law only. For EU institutions use Regulation (EC) 1049/2001; in the UK, the Freedom of Information Act 2000 (ICO guidance); elsewhere, your national access-to-information law. The request-drafting and tracking discipline transfers; the statutes, deadlines, and exemptions do not.


Workflows and templates for obtaining government records through freedom of information laws.

## Understanding FOIA landscape

### Jurisdiction overview

| Level | Law | Scope |
|-------|-----|-------|
| Federal | Freedom of Information Act (5 U.S.C. § 552) | Federal executive branch agencies |
| State | Varies by state (e.g., OPRA in NJ, FOIL in NY) | State and local agencies |
| Local | Often covered by state law | Municipal, county, school boards |

### Key federal exemptions (U.S. Federal FOIA)

```markdown
## The 9 federal FOIA exemptions

1. **National security** - Classified information
2. **Internal personnel rules** - Agency housekeeping matters
3. **Statutory exemptions** - Other laws prohibit disclosure
4. **Trade secrets** - Confidential business information
5. **Inter/intra-agency memos** - Deliberative process privilege
6. **Personal privacy** - Personnel, medical files
7. **Law enforcement** - Could interfere with proceedings
8. **Financial institutions** - Bank examination reports
9. **Geological data** - Oil and gas well information

Note: Agencies must segregate and release non-exempt portions
```

## State public records laws

All 50 states have enacted laws requiring certain government records to be open to the public. 

### State-specific resources

```markdown
### State public records resources

#### Reporters Committee for Freedom of the Press
- Open Government Guide: rcfp.org/open-government-guide
- State-by-state analysis of public records laws
- Sample request letters by state

#### National Freedom of Information Coalition
- nfoic.org/state-freedom-of-information-laws
- State FOI organization contacts
- Training and resources

#### MuckRock
- muckrock.com
- File requests through platform
- Search previous requests/responses
- Agency response time data
```

### Common state exemptions
State legislatures may be subject to different rules than the rest of their governing bodies:

1. **Exempt from public records statute** (e.g., Massachusetts, Oklahoma, Oregon, Wyoming)
2. **Excluded from definition of public body** (e.g., Georgia, Minnesota)
3. **Covered by separate statute** (e.g., California)
4. **Allowed to set own policies** (e.g., Mississippi, New York)

Court decisions and attorneys general opinions in some states have held that the separation of powers doctrine prevents courts from enforcing public records statutes against the legislature.

### State-by-state reference

The per-state statute/deadline table lives in [reference.md](reference.md) — verify against current state law before relying on any entry.

### NJ OPRA reforms (P.L. 2024, c. 16) — effective Sept. 3, 2024

Senate bill S2930 (signed June 5, 2024; effective Sept. 3, 2024) changed New Jersey's Open Public Records Act in five ways that make requesting harder:

- **Fee-shifting weakened.** Prevailing requesters now receive attorneys' fees only when a court finds the agency's denial was in bad faith or knowing and willful. Previously, prevailing requesters were entitled to fees in most successful suits.
- **Anonymous requesters lose standing.** Requesters must identify themselves by name and address; agencies may reject anonymous requests.
- **Deadline tiers introduced.** The standard 7-business-day response window remains, but agencies can extend timelines for "voluminous" or "complex" requests under defined criteria, and may treat certain commercial requests differently.
- **Special service charge presumption.** Agencies may impose extraordinary service fees more readily; requests for large data extracts, bulk records, or programmatic responses are presumed to justify a service charge above the standard copy fee.
- **Agencies can sue requesters.** Public agencies have new authority to seek injunctive relief against requesters whose requests the agency deems harassing, repeated, or filed in bad faith.

Practical effect for journalists: file under your byline and outlet (anonymous requests are now risky); narrow the scope to avoid triggering "voluminous" treatment; document the public-interest rationale up front because fee-shifting protection is weaker.

Sources: New Jersey P.L. 2024, c. 16 (S2930); New Jersey Press Association coverage; Lowenstein Sandler client advisory; HealthLaw Advisor analysis; Chasan Lamparello Mallon & Cappuzzo summary.

## Drafting effective requests

### Request template (Federal FOIA)

```markdown
[NAMES]
[ADDRESS]
[CITY],[STATE] [ZIPCODE]
[EMAIL]
[PHONE]

[DATE]

FOIA Officer
[AGENCY]
[AGENCY_ADDRESS]

[STATUTE] Request

Dear FOIA Officer:

My name is [NAME] and I am a [TITLE] for [OUTLET]. Pursuant to the [STATUTE], I am writing to request the following:

- [RECORDS_REQUESTED1] between [START_DATE] to [END_DATE] from [SPECIFIC_OFFICES] including the following words/phrases [KEYWORD1], [KEYWORD2], [KEYWORD3], [KEYWORD4] 
- [RECORDS_REQUESTED2] between [START_DATE] to [END_DATE] from [SPECIFIC_OFFICES] including the following words/phrases [KEYWORD1], [KEYWORD2], [KEYWORD3], [KEYWORD4] 
- [RECORDS_REQUESTED3] between [START_DATE] to [END_DATE] from [SPECIFIC_OFFICES] including the following words/phrases [KEYWORD1], [KEYWORD2], [KEYWORD3], [KEYWORD4] 

**INSTRUCTIONS REGARDING SEARCH:**
1. Instructions Regarding "Leads":
As required by the relevant case law, [AGENCY] should follow any leads it discovers during the conduct of its searches and perform additional searches when said leads indicate that records may be located in another system. Failure to follow clear leads is a violation of [STATUTE].

2. Request for Public Records:
Please search for any records even if they are already publicly available.

3. Request Regarding Attachments, Photographs and Other Visual Materials:
I request that any photographs or other visual materials responsive to my request be released to me in their original or comparable forms, quality and resolution. For example, if a photograph was taken digitally, or if [AGENCY] maintains a photograph digitally, I request disclosure of the original digital image file, not a reduced resolution version of that image file nor a printout and scan of that image file.

Likewise, if a photograph was originally taken as a color photograph, I request disclosure of that photograph as a color image, not a black and white image. 

For video and audio files I request that they be provided in their complete, original and unedited format. 

Please contact me at the number or email listed below for any clarification on these points.

4. Request for Duplicate Pages:
l request disclosure of any and all supposedly "duplicate" pages. Scholars analyze records not only for the information available on any given page, but also for the relationships between that information and information on pages surrounding it. As such, though certain pages may have been previously released to me, the existence of those pages within new context renders them functionally new pages. As such, the only way to properly analyze released information is to analyze that information within its proper context. Therefore, I request disclosure of all "duplicate" pages.

5. Request for Search of Records Transferred to Other Agencies:
I request that in conducting its search, [AGENCY] should disclose releasable records even if they are available publicly through other sources outside the [AGENCY] office. If [AGENCY] is unable to do so, it should disclose where specifically the relevant records are available.

6. Regarding Destroyed Records
If any records responsive or potentially responsive to my request have been destroyed, my request includes, but is not limited to, any and all records relating or referring to the destruction of those records. This includes, but is not limited to, any and all records relating or referring to the events leading to the destruction of those records.

INSTRUCTIONS REGARDING SCOPE AND BREADTH OF REQUESTS
Please interpret the scope of this request broadly. [AGENCY] is instructed to interpret the scope of this request in the most liberal manner possible short of an interpretation that would lead to a conclusion that the request does not reasonably describe the records sought.

EXEMPTIONS AND SEGREGABILITY

The FOIA Improvement Act of 2016 codified a foreseeable-harm standard at 5 U.S.C. § 552(a)(8)(A). An agency may withhold information only if it (i) reasonably foresees that disclosure would harm an interest protected by an exemption, or (ii) disclosure is prohibited by law. Embarrassment to officials, the possibility that disclosure might reveal errors or failures, and speculative or abstract fears are not legitimate grounds for withholding.

Even where an exemption properly applies to part of a record, the statute requires the agency to release all reasonably segregable non-exempt portions. If documents are denied in part or in whole, please specify which exemption(s) is (are) claimed for each passage or whole document denied. 

Please provide a complete itemized inventory and a detailed factual justification of total or partial denial of documents. Specify the number of pages in each document and the total number of pages pertaining to this request. For "classified" material denied, please include the following
information: the classification (confidential, secret or top secret); identity of the classifier; date or event for automatic declassification or classification review or downgrading; if applicable, identity of official authorizing extension of automatic declassification or review past six years; and, if applicable, the reason for extended classification beyond six years.

In excising material, please "black out" the material rather than "white out" or "cut out." I expect, as provided by FOIA, that the remaining non-exempt portions of documents will be released.

Please release all pages regardless of the extent of excising, even if all that remains are the letterhead, page numbers, or administrative markings.

In addition, I ask that your agency exercise its discretion to release records which may be technically exempt, but where withholding serves no important public interest.


**Format requested:**
I request that any releases stemming from this request be provided to me in its original digital format (soft-copy), ideally through an online file transfer or digital portal system. Should this be impossible, material may be provided on a compact disk, flash drive, hard drive or other like media.

I request that you provide records as they become available, rather than all at once.

Please produce all records with administrative markings and pagination included.

Please send a memo (copy to me) to the appropriate units in your office to assure that no records related to this request are destroyed. Please advise of any destruction of records and include the date of and authority for such destruction.


**Fee waiver request (for U.S. federal FOIA):**
I am a [JOB_TITLE] for [CURRENT_OUTLET], covering [BEAT/TOPIC]. My reporting has appeared in [PRIOR_OUTLETS].

I request a waiver of all fees pursuant to 5 U.S.C. § 552(a)(4)(A)(iii), which provides that documents shall be furnished without charge "if disclosure of the information is in the public interest because it is likely to contribute significantly to public understanding of the operations or activities of the government and is not primarily in the commercial interest of the requester."

The records I have requested meet that standard. They bear directly on [SPECIFIC_GOVERNMENT_OPERATION], a matter of public concern. I have the intent and ability to disseminate this information to a meaningful audience through [PUBLICATION_CHANNEL]. My request is non-commercial; I will not resell the records or use them primarily for private gain. *See Judicial Watch, Inc. v. Rossotti*, 326 F.3d 1309, 1312 (D.C. Cir. 2003) (Congress amended FOIA to ensure that fee-waiver provisions are "liberally construed in favor of waivers for noncommercial requesters"). I incorporate by reference the explanation in the sections above.

Should the fee waiver be denied, I request to be categorized as a representative of the news media for fee purposes pursuant to 5 U.S.C. § 552(a)(4)(A)(ii)(II). The statute defines a representative of the news media as "any person or entity that gathers information of potential interest to a segment of the public, uses its editorial skills to turn the raw materials into a distinct work, and distributes that work to an audience" — a definition derived from the holding in *Nat'l Sec. Archive v. Dep't of Def.*, 880 F.2d 1387 (D.C. Cir. 1989). I qualify under this definition because I [DESCRIBE_REPORTING_PROCESS_AND_AUDIENCE].

If both the fee waiver and the news-media classification are denied, please provide an itemized estimate of charges in writing before processing further. I am willing to pay reasonable charges up to $[AMOUNT] only if such a denial is final.

I will appeal any denial of the fee waiver administratively and, if necessary, in court.

**Expedited processing request (if applicable):**
I request expedited processing because:
- [Urgent need to inform the public about actual or alleged government activity]
- [Imminent threat to life or physical safety]

As a reminder, [TIME_LIMIT_STATUTE] requires a response within [DAYS_NUMBER] days.

**Contact information:**
Please do not hesitate to contact me at [EMAIL] or [PHONE] if you have questions or need clarification about this request.

Thank you. I appreciate your time and attention to this matter.

Sincerely,
[Your Name]

*Template Source: [Jason Leopold](https://www.dni.gov/files/documents/FOIA/DF_2023_00079_15_Oldest_Appeal_FOIA_Cases_cont.pdf)*
```

### Request drafting best practices

```markdown
## Effective request strategies

### Be specific but not too narrow
BAD: "All documents about climate change"
BAD: "The email from John Smith on March 15, 2024 at 2:47 PM"
GOOD: "Emails between [Office] and [External Party] regarding [Topic] from [Date Range]"

### Use agency terminology
- Research how agency categorizes information
- Use their document type names (memos, briefings, reports)
- Reference specific programs or initiatives by official name
- Include relevant file numbers if known

### Define your terms
- Specify what you mean by "communications" (emails, texts, calls?)
- Define "records" (include drafts? attachments?)
- Clarify "regarding" vs "mentioning" vs "primarily about"

### Request specific record types
- Emails and email attachments
- Text messages and messaging apps
- Printed Correspondence (letters, faxes)
- Calendar entries and meeting invites
- Memoranda, briefing papers and presentations
- Contracts, purchase orders and invoices
- Meeting minutes and notes
- Policies and procedures
- Databases and datasets; schema for databases/datasets

```

## Tracking and managing requests

### Request tracking system

A Python dataclass tracker (statuses, business-day statutory deadline, overdue flag) and the tracking-spreadsheet column list live in [reference.md](reference.md).

### Follow-up communication templates

```markdown
## Status inquiry (after 20+ business days)

Subject: Status inquiry — FOIA request [tracking number]

Dear FOIA Officer:

I am writing to inquire about the status of my Freedom of Information Act request submitted on [DATE], assigned tracking number [NUMBER].

Under FOIA, agencies must respond within 20 business days. As of today, [X] business days have elapsed.

Please provide:
1. Current status of my request
2. Estimated completion date
3. Any fee estimates
4. Name of assigned processor

I can be reached at [contact info].

Sincerely,
[Name]
```

```markdown
## Fee waiver appeal

Subject: Appeal of fee waiver denial — request [number]

Dear FOIA Appeals Officer:

I appeal the denial of my fee waiver request dated [DATE] for request [NUMBER].

The denial was improper because:

1. **Public interest**: [Explain how disclosure serves public interest]

2. **Ability to disseminate**: [Describe your platform/audience]
   - Publication: [name, circulation/readership]
   - Previous FOIA-based reporting: [examples]
   - Planned use of records: [specific plans]

3. **Commercial interest**: I have no commercial interest in these records. [Or: My commercial interest is minimal compared to public benefit because...]

4. **Comparison**: Similar requests have received fee waivers. See: [examples if available]

I request the fee waiver be granted or, alternatively, that fees be limited to [amount].

Sincerely,
[Name]
```

## Handling responses

### Response review checklist

```markdown
## Initial response review

### Administrative check
- [ ] Response received by deadline?
- [ ] Tracking number matches
- [ ] Request description accurate
- [ ] All requested record types addressed

### Completeness assessment
- [ ] All date ranges covered?
- [ ] All offices/divisions searched?
- [ ] Search terms used listed?
- [ ] Any referrals to other agencies?

### Exemption analysis
For each exemption claimed:
- [ ] Specific exemption cited (e.g., "Exemption 6")
- [ ] Explanation provided for each withholding
- [ ] Foreseeable harm articulated?
- [ ] Segregable portions released?

### Document review
- [ ] Page count matches stated total
- [ ] Documents legible
- [ ] Redactions clearly marked
- [ ] Index provided (Vaughn index if applicable)

### Fee assessment
- [ ] Charges match estimate?
- [ ] Itemized breakdown provided?
- [ ] Fee category correct (media, educational, commercial, other)?
```

### Redaction analysis

```markdown
## Understanding redactions

### Types of redactions
- (b)(1) - National security [black bar with exemption]
- (b)(5) - Deliberative process [often overused]
- (b)(6) - Personal privacy [names, contact info]
- (b)(7)(A) - Law enforcement investigation
- (b)(7)(C) - Law enforcement privacy

### Challenging over-redaction
Questions to ask:
1. Is entire document withheld or just portions?
2. Are routine details redacted unnecessarily?
3. Is information already public elsewhere?
4. Is the exemption correctly applied?
5. Was foreseeable harm test applied?

### Building your case
- Compare with similar released documents
- Check if information is already public
- Note inconsistent redaction patterns
- Document segregability arguments
```

## Appeals process

### Federal FOIA appeal template

```markdown
[Your Name]
[Address]
[Date]

Chief FOIA Officer / FOIA Appeals Office
[Agency Name]
[Address]

RE: Administrative Appeal of FOIA Request [Tracking Number]

Dear Appeals Officer:

Pursuant to 5 U.S.C. § 552(a)(6), I appeal the [partial denial / full denial / inadequate search / fee waiver denial] of my FOIA request dated [original date], tracking number [number].

**Original request:**
[Brief description of what you requested]

**Agency response:**
On [date], the agency [describe response - denied, partially released, etc.]

**Grounds for appeal:**

[Choose applicable grounds:]

**1. Improper exemption claim**
The agency improperly invoked Exemption [X] because:
- [Specific argument about why exemption doesn't apply]
- [Legal precedent if known]
- [Foreseeable harm not demonstrated]

**2. Inadequate search**
The agency failed to conduct an adequate search because:
- [Specific offices not searched]
- [Relevant record systems overlooked]
- [Search terms too narrow]

**3. Failure to segregate**
The agency failed to release non-exempt portions as required. Specifically:
- [Identify documents where segregation possible]

**4. Fee waiver improperly denied**
[See fee waiver appeal template above]

**Relief requested:**
I request that the agency:
1. Release all improperly withheld records
2. Conduct additional searches of [specific locations]
3. Provide a detailed justification for any continued withholdings
4. Grant my fee waiver request

I expect a response within 20 business days.

Sincerely,
[Name]
```

### Appeal deadlines by jurisdiction

| Jurisdiction | Appeal deadline | Where to file |
|--------------|-----------------|---------------|
| Federal FOIA | 90 days from response | Agency appeals office |
| New Jersey OPRA | 45 days | Government Records Council |
| New York FOIL | 30 days | Agency appeals officer |
| California PRA | No admin appeal | Direct to court |

## Advanced strategies

### Multi-agency requests

```markdown
## Coordinated request strategy

When a topic spans multiple agencies:

1. **Map the agencies involved**
   - Which agencies have jurisdiction?
   - Which offices within agencies?
   - Are there inter-agency communications?

2. **Sequence requests strategically**
   - Start with agency most likely to release
   - Use released documents to refine subsequent requests
   - Reference other agencies' releases in appeals

3. **Cross-reference responses**
   - Compare what different agencies release
   - Note discrepancies in redactions
   - Use one agency's release to challenge another's withholding

4. **Track coordination**
   - Document all request/response dates
   - Note referrals between agencies
   - Build timeline of events from multiple sources
```

### Document production management

```markdown
## Large production workflow

For responses with 100+ pages:

### Organization system
/FOIA_[Agency]_[Topic]/
├── 01_Request_Materials/
│   ├── original_request.pdf
│   ├── acknowledgment.pdf
│   └── correspondence/
├── 02_Responses/
│   ├── response_2024-01-15/
│   ├── response_2024-02-20/
│   └── final_response/
├── 03_Analysis/
│   ├── document_index.xlsx
│   ├── redaction_log.xlsx
│   └── key_documents/
├── 04_Appeals/
│   └── appeal_2024-03-01.pdf
└── 05_Notes/
    └── research_notes.md

### Document indexing
For each document, track:
- Bates number (if assigned)
- Date of document
- Author/recipient
- Document type
- Subject/summary
- Exemptions applied
- Relevance rating (1-5)
- Follow-up needed?
```

## Credits

Adapted from [claude-skills-journalism](https://github.com/jamditis/claude-skills-journalism/tree/2097d218c6f38a8e7be77ce5f0ff6c2e39671f13/journalism-core/skills/foia-requests) by **Joe Amditis**, released under MIT License. Vendored at `2097d218` with localization and integration edits.
